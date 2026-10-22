#!/usr/bin/env python3
"""Generate the TypeScript and Kotlin types from the published JSON Schemas.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

The schemas are the single source of truth; the generated files must never be
edited by hand. ``--check`` fails when a generated file is out of date, which
is how CI keeps the clients honest.

The Kotlin properties keep the exact names of the JSON fields (``node_id``), so any
library that maps by name reads the messages as they are, with a backtick around the
few names that Kotlin reserves (``interface``). A field that always has one value (the
``kind`` of a message) is that literal in TypeScript and the default in Kotlin; every
object inside a message gets a type of its own, named after the field that holds it.

    python tools/generate_types.py           # write generated/
    python tools/generate_types.py --check   # verify generated/ is current
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "src" / "armor_common" / "schemas"
OUT = ROOT / "generated"

# schema file -> (type name, {nested property name -> nested type name})
MESSAGES = {
    "telemetry": ("Telemetry", {"targets": "RadarTrack"}),
    "health": ("Health", {}),
    "command": ("Command", {}),
    "info": ("Info", {}),
    "solar_inverter": ("SolarInverter", {}),
    "solar_battery": ("SolarBattery", {"stack": "SolarModule"}),
    "electrical": ("Electrical", {"channels": "ElectricalChannel", "switches": "ElectricalSwitch"}),
    "electrical_command": ("ElectricalCommand", {}),
    "electrical_result": ("ElectricalResult", {}),
    "solar_battery_command": ("SolarBatteryCommand", {"stage": "SolarBatteryStage"}),
    "solar_battery_result": ("SolarBatteryResult", {"battery": "SolarBatteryIdentity"}),
    "node_control_command": ("NodeControlCommand", {}),
    "node_control_result": ("NodeControlResult", {}),
    "node_maintenance": ("NodeMaintenance", {}),
    "radar_event": ("RadarEvent", {}),
    "diagnostic_token_request": ("DiagnosticTokenRequest", {}),
    "diagnostic_token_created": ("DiagnosticTokenCreated", {}),
    "diagnostic_token_info": ("DiagnosticTokenInfo", {}),
    "alarm": ("Alarm", {"zones": "AlarmZone", "events": "AlarmEvent"}),
    "alarm_command": ("AlarmCommand", {"profile": "ArmProfile", "zones": "ArmProfileZone"}),
    "alarm_result": ("AlarmResult", {}),
    "node_health": ("NodeHealth", {}),
    "connection_event": ("ConnectionEvent", {}),
    "system_event": ("SystemEvent", {}),
    "connection_client": ("ConnectionClient", {}),
    "network": ("Network", {"interface": "NetworkInterface", "internet": "NetworkInternet", "probes": "NetworkProbe", "last_outage": "NetworkOutage", "devices": "NetworkDevice",
                            "ports": "NetworkPort", "events": "NetworkEvent", "scan": "NetworkScan"}),
}
HEADER = "Generated from the A.R.M.O.R. JSON Schemas by tools/generate_types.py. Do not edit."


class Field:
    def __init__(self, name: str, schema: dict, required: bool, nested: str | None) -> None:
        self.name, self.schema, self.required, self.nested = name, schema, required, nested


KOTLIN_HARD_KEYWORDS = {"as", "break", "class", "continue", "do", "else", "false", "for", "fun", "if", "in", "interface", "is", "null", "object", "package", "return", "super", "this", "throw",
                        "true", "try", "typealias", "typeof", "val", "var", "when", "while"}


def pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def complete(schema: dict, nested: dict[str, str], parent: str) -> dict[str, str]:
    """`nested` plus a type name for every object (or list of objects) inside the schema that has no name yet: the parent's name and the field's."""
    full = dict(nested)

    def walk(node: dict, owner: str) -> None:
        for prop, child in node.get("properties", {}).items():
            item = child.get("items", child) if child.get("type") == "array" else child
            if isinstance(item, dict) and item.get("type") == "object" and item.get("properties"):
                full.setdefault(prop, owner + pascal(prop))
                walk(item, full[prop])

    walk(schema, parent)
    return full


def kt_name(name: str) -> str:
    return f"`{name}`" if name in KOTLIN_HARD_KEYWORDS else name


def fields_of(schema: dict, nested: dict[str, str]) -> list[Field]:
    required = set(schema.get("required", []))
    return [Field(name, child, name in required, nested.get(name)) for name, child in schema["properties"].items()]


def ts_type(field: Field) -> str:
    schema = field.schema
    if "const" in schema:
        return json.dumps(schema["const"])
    if "enum" in schema:
        return " | ".join(json.dumps(value) for value in schema["enum"])
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        return f"{field.nested or {'string': 'string', 'integer': 'number', 'number': 'number', 'boolean': 'boolean'}.get(items, 'unknown')}[]"
    if kind == "object":
        values = schema.get("additionalProperties")
        if not field.nested and isinstance(values, dict) and values.get("type") in ("integer", "number", "string", "boolean"):
            return "Record<string, " + {"string": "string", "integer": "number", "number": "number", "boolean": "boolean"}[values["type"]] + ">"   # a map of one kind of value
        return field.nested or "Record<string, unknown>"
    return {"string": "string", "integer": "number", "number": "number", "boolean": "boolean"}[kind]


def kt_type(field: Field) -> str:
    schema = field.schema
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        return f"List<{field.nested or {'string': 'String', 'integer': 'Long', 'number': 'Double', 'boolean': 'Boolean'}.get(items, 'Any')}>"
    if kind == "object":
        values = schema.get("additionalProperties")
        if not field.nested and isinstance(values, dict) and values.get("type") in ("integer", "number", "string", "boolean"):
            return "Map<String, " + {"string": "String", "integer": "Long", "number": "Double", "boolean": "Boolean"}[values["type"]] + ">"   # a map of one kind of value
        return field.nested or "Map<String, Any>"
    return {"string": "String", "integer": "Long", "number": "Double", "boolean": "Boolean"}[kind]


def kt_property(field: Field) -> str:
    """One Kotlin property: its JSON name, its type, and its default (a fixed value for a field that always has the same one; null for an optional field)."""
    default = f" = {json.dumps(field.schema['const'])}" if "const" in field.schema and field.required else ("" if field.required else "? = null")
    return f"    val {kt_name(field.name)}: {kt_type(field)}{default}"


def nested_types(schema: dict, nested: dict[str, str], emitted: set[str]):
    """The named types inside a schema, the deepest first: (type name, its schema). A property named in `nested` is an object or an array of objects."""
    for prop, type_name in nested.items():
        child = schema.get("properties", {}).get(prop)
        if child is None or type_name in emitted:
            continue
        item = child.get("items", child)
        if not (isinstance(item, dict) and item.get("type") == "object" and item.get("properties")):
            continue   # the same name in another place may be a plain field (a flag called like an object elsewhere)
        emitted.add(type_name)
        yield from nested_types(item, nested, emitted)
        yield type_name, item


def render_typescript(docs: dict[str, dict]) -> str:
    out = [f"/** {HEADER} */", ""]
    emitted: set[str] = set()
    for key, (name, declared) in MESSAGES.items():
        schema = docs[key]
        nested = complete(schema, declared, name)
        for type_name, item in nested_types(schema, nested, emitted):
            out.append(f"export type {type_name} = {{")
            out += [f"  {f.name}{'' if f.required else '?'}: {ts_type(f)};" for f in fields_of(item, nested)]
            out += ["};", ""]
        out.append(f"export type {name} = {{")
        out += [f"  {f.name}{'' if f.required else '?'}: {ts_type(f)};" for f in fields_of(schema, nested)]
        out += ["};", ""]
    limits = docs["telemetry"]["properties"]
    out += [
        f"export const MAX_TARGETS = {limits['targets']['maxItems']};",
        f"export const MAX_LUX = {limits['lux']['maximum']};",
        f"export const NODE_ID_PATTERN = /{docs['telemetry']['properties']['node_id']['pattern']}/;",
        f"export const COMMANDS = {json.dumps(docs['command']['properties']['command']['enum'])} as const;",
        "",
    ]
    return "\n".join(out)


def render_kotlin(docs: dict[str, dict]) -> str:
    out = ["// " + HEADER, "package es.electrohobby3d.armor.contracts", ""]
    emitted: set[str] = set()
    for key, (name, declared) in MESSAGES.items():
        schema = docs[key]
        nested = complete(schema, declared, name)
        for type_name, item in nested_types(schema, nested, emitted):
            body = ",\n".join(kt_property(f) for f in fields_of(item, nested))
            out += [f"data class {type_name}(", body, ")", ""]
        body = ",\n".join(kt_property(f) for f in fields_of(schema, nested))
        out += [f"data class {name}(", body, ")", ""]
    limits = docs["telemetry"]["properties"]
    commands = ", ".join(json.dumps(value) for value in docs["command"]["properties"]["command"]["enum"])
    out += [
        "object ContractLimits {",
        f"    const val MAX_TARGETS = {limits['targets']['maxItems']}",
        f"    const val MAX_LUX = {float(limits['lux']['maximum'])!r}",
        f"    val COMMANDS = listOf({commands})",
        "}",
        "",
    ]
    return "\n".join(out)


def outputs() -> dict[Path, str]:
    docs = {key: json.loads((SCHEMAS / f"{key}.schema.json").read_text(encoding="utf-8")) for key in MESSAGES}
    return {OUT / "armor-contracts.ts": render_typescript(docs), OUT / "ArmorContracts.kt": render_kotlin(docs)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, content in outputs().items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        stale.append(path.name)
        if not args.check:
            OUT.mkdir(exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if args.check and stale:
        print("generated files are out of date:", ", ".join(stale), file=sys.stderr)
        return 1
    print("generated types are current" if args.check else "generated types written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
