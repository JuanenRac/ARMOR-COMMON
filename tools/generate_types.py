#!/usr/bin/env python3
"""Generate the TypeScript and Kotlin types from the published JSON Schemas.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

The schemas are the single source of truth; the generated files must never be
edited by hand. ``--check`` fails when a generated file is out of date, which
is how CI keeps the clients honest.

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
}
HEADER = "Generated from the A.R.M.O.R. JSON Schemas by tools/generate_types.py. Do not edit."


class Field:
    def __init__(self, name: str, schema: dict, required: bool, nested: str | None) -> None:
        self.name, self.schema, self.required, self.nested = name, schema, required, nested


def fields_of(schema: dict, nested: dict[str, str]) -> list[Field]:
    required = set(schema.get("required", []))
    return [Field(name, child, name in required, nested.get(name)) for name, child in schema["properties"].items()]


def ts_type(field: Field) -> str:
    schema = field.schema
    if "enum" in schema:
        return " | ".join(json.dumps(value) for value in schema["enum"])
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        return f"{field.nested or {'string': 'string', 'integer': 'number', 'number': 'number', 'boolean': 'boolean'}.get(items, 'unknown')}[]"
    return {"string": "string", "integer": "number", "number": "number", "boolean": "boolean"}[kind]


def kt_type(field: Field) -> str:
    schema = field.schema
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        return f"List<{field.nested or {'string': 'String', 'integer': 'Long', 'number': 'Double', 'boolean': 'Boolean'}.get(items, 'Any')}>"
    return {"string": "String", "integer": "Long", "number": "Double", "boolean": "Boolean"}[kind]


def camel(name: str) -> str:
    head, *rest = name.split("_")
    return head + "".join(part.capitalize() for part in rest)


def render_typescript(docs: dict[str, dict]) -> str:
    out = [f"/** {HEADER} */", ""]
    emitted: set[str] = set()
    for key, (name, nested) in MESSAGES.items():
        schema = docs[key]
        for prop, type_name in nested.items():
            if type_name in emitted:
                continue
            emitted.add(type_name)
            item = schema["properties"][prop]["items"]
            out.append(f"export type {type_name} = {{")
            out += [f"  {f.name}{'' if f.required else '?'}: {ts_type(f)};" for f in fields_of(item, {})]
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
    for key, (name, nested) in MESSAGES.items():
        schema = docs[key]
        for prop, type_name in nested.items():
            if type_name in emitted:
                continue
            emitted.add(type_name)
            item = schema["properties"][prop]["items"]
            body = ",\n".join(f"    val {camel(f.name)}: {kt_type(f)}{'' if f.required else '? = null'}" for f in fields_of(item, {}))
            out += [f"data class {type_name}(", body, ")", ""]
        body = ",\n".join(f"    val {camel(f.name)}: {kt_type(f)}{'' if f.required else '? = null'}" for f in fields_of(schema, nested))
        out += [f"data class {name}(", body, ")", ""]
    limits = docs["telemetry"]["properties"]
    commands = ", ".join(json.dumps(value) for value in docs["command"]["properties"]["command"]["enum"])
    out += [
        "object ContractLimits {",
        f"    const val MAX_TARGETS = {limits['targets']['maxItems']}",
        f"    const val MAX_LUX = {limits['lux']['maximum']}.0",
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
