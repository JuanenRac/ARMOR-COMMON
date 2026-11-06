#!/usr/bin/env python3
"""Generate the TypeScript parsers of the messages from the published JSON Schemas.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``generated/armor-parsers.ts`` holds the schemas as data (without their prose), one small interpreter that applies them the way ``armor_common.schema`` does (same keywords, same ASCII
meaning of the patterns, the same order of the checks), and ``parseMessage(name, value)``, which returns the value typed as the message of ``armor-contracts.ts`` or throws a
``ContractError`` that says where the document is wrong. Servers and apps that read what a node or the server publishes use it instead of writing the checks again by hand; the seeded
cases of ``conformance/wire_cases.tsv`` (verdict from the Python validator) keep it equal to the others.

    python tools/generate_parsers.py           # write generated/armor-parsers.ts
    python tools/generate_parsers.py --check   # verify it is current
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_types as gt   # noqa: E402

ROOT = gt.ROOT
OUT = ROOT / "generated" / "armor-parsers.ts"
KEEP = {"type", "enum", "const", "pattern", "minimum", "maximum", "minLength", "maxLength", "minItems", "maxItems", "items", "properties", "required", "additionalProperties", "propertyNames", "maxProperties"}

HEAD = r'''/** Generated from the A.R.M.O.R. JSON Schemas by tools/generate_parsers.py. Do not edit. */
import type * as T from "./armor-contracts.js";

/** What a document gets wrong: where (`/zones/0/id`) and what. */
export class ContractError extends Error {
  readonly path: string;
  readonly detail: string;
  constructor(path: string, detail: string) {
    super(`${path || "$"}: ${detail}`);
    this.name = "ContractError";
    this.path = path;
    this.detail = detail;
  }
}

type Schema = {
  type?: string; enum?: readonly (string | number | boolean)[]; const?: string | number | boolean; pattern?: string; minimum?: number; maximum?: number;
  minLength?: number; maxLength?: number; minItems?: number; maxItems?: number; items?: Schema; properties?: Record<string, Schema>; required?: readonly string[];
  additionalProperties?: boolean | Schema; propertyNames?: { pattern: string }; maxProperties?: number;
};

const compiled = new Map<string, RegExp>();
/** The pattern of a schema, with `$` meaning the end of the text and nothing else (the same as everywhere else in A.R.M.O.R.). */
const matcher = (pattern: string): RegExp => {
  let regex = compiled.get(pattern);
  if (regex === undefined) {
    regex = new RegExp(pattern, "u");
    compiled.set(pattern, regex);
  }
  return regex;
};

const isObject = (value: unknown): value is Record<string, unknown> => typeof value === "object" && value !== null && !Array.isArray(value);
const length = (text: string): number => Array.from(text).length;

const typeMatches = (value: unknown, type: string): boolean => {
  switch (type) {
    case "object": return isObject(value);
    case "array": return Array.isArray(value);
    case "string": return typeof value === "string";
    case "boolean": return typeof value === "boolean";
    case "integer": return typeof value === "number" && Number.isFinite(value) && Number.isInteger(value);
    case "number": return typeof value === "number" && Number.isFinite(value);
    default: return false;
  }
};

/** The first way in which `value` does not satisfy `schema`, in the order Python's validator finds it, or undefined. */
function firstError(value: unknown, schema: Schema, path: string): ContractError | undefined {
  if (schema.type !== undefined && !typeMatches(value, schema.type)) return new ContractError(path, `must be of type ${schema.type}`);
  if (schema.const !== undefined && value !== schema.const) return new ContractError(path, `must equal ${JSON.stringify(schema.const)}`);
  if (schema.enum !== undefined && !schema.enum.includes(value as string)) return new ContractError(path, `must be one of ${JSON.stringify(schema.enum)}`);
  if (typeof value === "string") {
    if (schema.minLength !== undefined && length(value) < schema.minLength) return new ContractError(path, `must have at least ${schema.minLength} characters`);
    if (schema.maxLength !== undefined && length(value) > schema.maxLength) return new ContractError(path, `must have at most ${schema.maxLength} characters`);
    if (schema.pattern !== undefined && !matcher(schema.pattern).test(value)) return new ContractError(path, `must match ${schema.pattern}`);
  }
  if (typeof value === "number") {
    if (schema.minimum !== undefined && value < schema.minimum) return new ContractError(path, `must be at least ${schema.minimum}`);
    if (schema.maximum !== undefined && value > schema.maximum) return new ContractError(path, `must be at most ${schema.maximum}`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) return new ContractError(path, `must have at least ${schema.minItems} items`);
    if (schema.maxItems !== undefined && value.length > schema.maxItems) return new ContractError(path, `must have at most ${schema.maxItems} items`);
    if (schema.items !== undefined) {
      for (let index = 0; index < value.length; index += 1) {
        const error = firstError(value[index], schema.items, `${path}/${index}`);
        if (error) return error;
      }
    }
  }
  if (isObject(value)) {
    const properties = schema.properties ?? {};
    for (const name of schema.required ?? []) if (!Object.prototype.hasOwnProperty.call(value, name)) return new ContractError(`${path}/${name}`, "is required");
    const names = Object.keys(value);
    if (schema.maxProperties !== undefined && names.length > schema.maxProperties) return new ContractError(path, `must have at most ${schema.maxProperties} properties`);
    if (schema.propertyNames !== undefined) {
      for (const name of names) if (!matcher(schema.propertyNames.pattern).test(name)) return new ContractError(`${path}/${name}`, `the name must match ${schema.propertyNames.pattern}`);
    }
    const declared = (name: string): boolean => Object.prototype.hasOwnProperty.call(properties, name);
    if (schema.additionalProperties === false) {
      for (const name of names) if (!declared(name)) return new ContractError(`${path}/${name}`, "is not allowed");
    } else if (typeof schema.additionalProperties === "object") {
      for (const name of names) {
        if (declared(name)) continue;
        const error = firstError(value[name], schema.additionalProperties, `${path}/${name}`);
        if (error) return error;
      }
    }
    for (const name of Object.keys(properties)) {
      if (!Object.prototype.hasOwnProperty.call(value, name)) continue;
      const error = firstError(value[name], properties[name], `${path}/${name}`);
      if (error) return error;
    }
  }
  return undefined;
}
'''


def to_js(pattern: str) -> str:
    """A schema pattern with the meaning of ``armor_common.schema`` (ASCII classes, ``$`` is the end of the text, ``.`` is any character but the line feed) as a JavaScript pattern."""
    out, in_class, index = [], False, 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            nxt = pattern[index + 1]
            out.append({"S": "[^ \\t\\n\\r\\f\\x0b]", "d": "[0-9]"}.get(nxt, "\\" + nxt) if not in_class else "\\" + nxt)
            index += 2
            continue
        if in_class:
            in_class = char != "]"
            out.append(char)
        elif char == "[":
            in_class = True
            out.append(char)
        elif char == "$":
            out.append("(?![\\s\\S])")
        elif char == ".":
            out.append("[^\\n]")
        else:
            out.append(char)
        index += 1
    return "".join(out)


def trim(node):
    """The schema without its prose, keeping the keywords that decide whether a document is valid."""
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key == "properties":
                out[key] = {name: trim(child) for name, child in value.items()}
            elif key == "pattern":
                out[key] = to_js(value)
            elif key == "propertyNames":
                out[key] = {"pattern": to_js(value["pattern"])}
            elif key in KEEP:
                out[key] = trim(value) if key in ("items", "additionalProperties") else value
        return out
    return node


def render() -> str:
    docs = {}
    for path in sorted(gt.SCHEMAS.glob("*.schema.json")):
        docs[path.name[: -len(".schema.json")]] = json.loads(path.read_text(encoding="utf-8"))
    names = gt.discover()
    types = {key: names[key][0] for key in docs if key in names}
    types["arm_profile"] = gt.pascal("arm_profile")
    out = [HEAD.rstrip("\n"), "", "const SCHEMAS: Record<string, Schema> = {"]
    for key in sorted(docs):
        out.append(f"  {json.dumps(key)}: {json.dumps(trim(docs[key]), separators=(',', ':'))},")
    out += ["};", "", "/** The messages, by the name of their schema file, and the type each one is. */", "export interface MessageTypes {"]
    out += [f"  {json.dumps(key)}: T.{types[key]};" for key in sorted(types)]
    out += [
        "}",
        "",
        "export type MessageName = keyof MessageTypes;",
        "export const MESSAGE_NAMES = Object.keys(SCHEMAS) as MessageName[];",
        "",
        "/** The first thing wrong with the document as the message called `name`, or undefined when it is valid. */",
        "export const checkMessage = (name: MessageName, value: unknown): ContractError | undefined => firstError(value, SCHEMAS[name], \"\");",
        "",
        "/** The document typed as the message called `name`; throws a ContractError when it is not valid. */",
        "export function parseMessage<K extends MessageName>(name: K, value: unknown): MessageTypes[K] {",
        "  const error = checkMessage(name, value);",
        "  if (error) throw error;",
        "  return value as MessageTypes[K];",
        "}",
        "",
    ]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if current == content:
        print("generated parsers are current")
        return 0
    if args.check:
        print("generated/armor-parsers.ts is out of date", file=sys.stderr)
        return 1
    OUT.write_text(content, encoding="utf-8", newline="\n")
    print("generated parsers written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
