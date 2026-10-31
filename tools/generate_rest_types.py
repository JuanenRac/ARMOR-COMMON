#!/usr/bin/env python3
"""Generate the TypeScript types of the HTTP contract (the components of openapi/armor-server.yaml).

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

The OpenAPI document is the single source of truth for what ARMOR-SERVER answers and accepts; the types written here are what a client (ARMOR-STUDIO) compares its own with, so
that a field renamed in the contract is a failure to compile and not a surprise at run time. The messages of the nodes are not repeated: a schema that points at one of the JSON
Schemas of the nodes uses the type of generated/armor-contracts.ts. ``--check`` fails when the generated file is out of date.

    python tools/generate_rest_types.py           # write generated/armor-rest.ts
    python tools/generate_rest_types.py --check   # verify it is current
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "openapi" / "armor-server.yaml"
OUT = ROOT / "generated" / "armor-rest.ts"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_types import MESSAGES  # noqa: E402

HEADER = "Generated from openapi/armor-server.yaml by tools/generate_rest_types.py. Do not edit."
SCALARS = {"string": "string", "integer": "number", "number": "number", "boolean": "boolean", "null": "null"}
IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
CONTRACTS = ROOT / "generated" / "armor-contracts.ts"
# The parts of a message that have a type of their own in generated/armor-contracts.ts, by the end of the reference that points at them.
NESTED = {
    "arm_profile.schema.json": "ArmProfile",
    "arming_modes.schema.json#/properties/modes": "ArmingModesModes",
    "arming_modes.schema.json#/properties/schedule/items": "ArmingModesSchedule",
    "node_control_result.schema.json#/properties/diagnostics/properties/package": "NodeControlResultDiagnosticsPackage",
    "node_health.schema.json#/properties/boot": "NodeHealthBoot",
    "network.schema.json#/properties/interface": "NetworkInterface",
    "network.schema.json#/properties/internet": "NetworkInternet",
    "network.schema.json#/properties/scan": "NetworkScan",
    "network.schema.json#/properties/public": "NetworkPublic",
    "network.schema.json#/properties/devices/items": "NetworkDevice",
}


class Loader(yaml.SafeLoader):
    """YAML 1.2 booleans: only true and false are booleans, so a property called `on` or `no` keeps its name."""


Loader.yaml_implicit_resolvers = {first: [(tag, pattern) for tag, pattern in resolvers if tag != "tag:yaml.org,2002:bool"] for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()}
Loader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$"), list("tf"))


class Context:
    """The types of the node messages that a schema may point at, found by the name of the JSON Schema file."""

    def __init__(self, document: dict) -> None:
        self.document = document
        self.messages = {f"{name}.schema.json": type_name for name, (type_name, _nested) in MESSAGES.items()}
        self.used_messages: set[str] = set()


def key(name: str) -> str:
    return name if IDENTIFIER.match(name) else json.dumps(name)


def union(parts: list[str]) -> str:
    seen: list[str] = []
    for part in parts:
        if part not in seen:
            seen.append(part)
    return " | ".join(seen) if seen else "never"


def grouped(text: str) -> str:
    """`text` as the element of an array: a union or an intersection needs parentheses."""
    return f"({text})" if re.search(r"[|&]", text) and not text.startswith("{") else text


def ref(target: str, context: Context, indent: int) -> str:
    if target.startswith("#/components/schemas/"):
        pieces = target[len("#/components/schemas/"):].split("/")
        if len(pieces) == 1:
            return pieces[0]
        node = context.document["components"]["schemas"]   # a property of another schema: its own type, written out
        for piece in pieces:
            node = node[piece]
        return convert(node, context, indent)
    nested = NESTED.get(target.rsplit("/schemas/", 1)[-1])
    if nested:
        context.used_messages.add(nested)
        return "Contracts." + nested
    name = target.rsplit("/", 1)[-1]
    if name in context.messages:
        context.used_messages.add(context.messages[name])
        return "Contracts." + context.messages[name]
    return "unknown"


def convert(schema, context: Context, indent: int = 0) -> str:
    if schema is True or schema == {} or schema is None:
        return "unknown"
    if "$ref" in schema:
        return ref(schema["$ref"], context, indent)
    if "const" in schema:
        return json.dumps(schema["const"])
    for word, joiner in (("oneOf", " | "), ("anyOf", " | "), ("allOf", " & ")):
        if word in schema:
            return joiner.join(grouped(convert(part, context, indent)) for part in schema[word])
    if "enum" in schema:
        base = union([json.dumps(value) for value in schema["enum"]])
    else:
        base = None
    kind = schema.get("type")
    kinds = kind if isinstance(kind, list) else ([kind] if kind else [])
    if not kinds and ("properties" in schema or "additionalProperties" in schema):
        kinds = ["object"]
    parts: list[str] = []
    for one in kinds:
        if one == "array":
            parts.append(grouped(convert(schema.get("items"), context, indent)) + "[]")
        elif one == "object":
            parts.append(convert_object(schema, context, indent))
        elif one in SCALARS:
            parts.append(base if (base and one != "null") else SCALARS[one])
        else:
            parts.append("unknown")
    if not parts:
        parts.append(base or "unknown")
    if schema.get("nullable") is True:
        parts.append("null")
    return union(parts)


def convert_object(schema: dict, context: Context, indent: int) -> str:
    properties = schema.get("properties", {})
    extra = schema.get("additionalProperties", False if properties else True)
    pad = "  " * (indent + 1)
    lines = []
    required = set(schema.get("required", []))
    for name, child in properties.items():
        description = child.get("description") if isinstance(child, dict) else None
        if description:
            lines.append(f"{pad}/** {' '.join(str(description).split()).replace('*/', '* /')} */")
        lines.append(f"{pad}{key(name)}{'' if name in required else '?'}: {convert(child, context, indent + 1)};")
    if extra is True:
        lines.append(f"{pad}[key: string]: unknown;")
    elif isinstance(extra, dict):
        lines.append(f"{pad}[key: string]: {convert(extra, context, indent + 1)};")
    if not lines:
        return "Record<string, never>" if extra is False else "Record<string, unknown>"
    return "{\n" + "\n".join(lines) + "\n" + "  " * indent + "}"


def render(document: dict | None = None) -> str:
    document = document or yaml.load(OPENAPI.read_text(encoding="utf-8"), Loader=Loader)
    context = Context(document)
    body: list[str] = []
    for name in sorted(document["components"]["schemas"]):
        schema = document["components"]["schemas"][name]
        description = schema.get("description") if isinstance(schema, dict) else None
        if description:
            body.append(f"/** {' '.join(str(description).split()).replace('*/', '* /')} */")
        body.append(f"export type {name} = {convert(schema, context)};\n")
    if CONTRACTS.is_file():
        known = set(re.findall(r"^export type (\w+)", CONTRACTS.read_text(encoding="utf-8"), re.M))
        missing = sorted(context.used_messages - known)
        if missing:
            raise SystemExit("the contract points at types that generated/armor-contracts.ts does not have: " + ", ".join(missing))
    imports = 'import type * as Contracts from "./armor-contracts";\n\n' if context.used_messages else ""
    return f"// {HEADER}\n{imports}" + "\n".join(body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    current = OUT.read_text(encoding="utf-8").replace("\r\n", "\n") if OUT.is_file() else None
    if args.check:
        if current != text:
            print("generated/armor-rest.ts is out of date: run python tools/generate_rest_types.py", file=sys.stderr)
            return 1
        print("rest types current")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("rest types written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
