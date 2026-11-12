#!/usr/bin/env python3
"""Generate the Kotlin readers of the messages from the published JSON Schemas.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``generated/ArmorParsers.kt`` (package ``es.electrohobby3d.armor.contracts``, next to ``ArmorContracts.kt``) reads a message from an ``org.json`` object into the data class of
``ArmorContracts.kt``: ``checkMessage(name, value)`` applies the schema (the same keywords, the same ASCII meaning of the patterns and the same order of checks as
``armor_common.schema``) and says what is wrong and where; ``read<Message>`` builds the data class from a document that has passed; ``parse<Message>`` does both and gives null when
the document is not valid. The app uses them instead of reading each field by hand, so it refuses what the other readers of the contract refuse.

    python tools/generate_kotlin_parsers.py           # write generated/ArmorParsers.kt
    python tools/generate_kotlin_parsers.py --check   # verify it is current
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_parsers as gp   # noqa: E402
import generate_types as gt   # noqa: E402

ROOT = gt.ROOT
OUT = ROOT / "generated" / "ArmorParsers.kt"

HEAD = r'''// Generated from the A.R.M.O.R. JSON Schemas by tools/generate_kotlin_parsers.py. Do not edit.
package es.electrohobby3d.armor.contracts

import org.json.JSONArray
import org.json.JSONObject
import java.math.BigInteger

/** What a document gets wrong: where (`/zones/0/id`) and what. */
class ContractError(val path: String, val detail: String) : Exception("${path.ifEmpty { "$" }}: $detail")

private fun isWhole(number: Number): Boolean = when (number) {
    is Int, is Long, is Short, is Byte, is BigInteger -> true
    else -> number.toDouble().let { it.isFinite() && it == Math.floor(it) }
}

private val compiled = HashMap<String, Regex>()
private fun matcher(pattern: String): Regex = synchronized(compiled) { compiled.getOrPut(pattern) { Regex(pattern) } }

private fun typeMatches(value: Any?, type: String): Boolean = when (type) {
    "object" -> value is JSONObject
    "array" -> value is JSONArray
    "string" -> value is String
    "boolean" -> value is Boolean
    "integer" -> value is Number && value.toDouble().isFinite() && isWhole(value)
    "number" -> value is Number && value.toDouble().isFinite()
    else -> false
}

private fun same(a: Any?, b: Any?): Boolean = if (a is Number && b is Number) a.toDouble() == b.toDouble() else a == b

/** The first way in which `value` does not satisfy `schema`, in the order Python's validator finds it, or null. */
private fun firstError(value: Any?, schema: JSONObject, path: String): ContractError? {
    schema.optString("type", "").takeIf { it.isNotEmpty() }?.let { if (!typeMatches(value, it)) return ContractError(path, "must be of type $it") }
    if (schema.has("const") && !same(value, schema.get("const"))) return ContractError(path, "must equal ${schema.get("const")}")
    schema.optJSONArray("enum")?.let { options ->
        if ((0 until options.length()).none { same(value, options.get(it)) }) return ContractError(path, "must be one of $options")
    }
    if (value is String) {
        val length = value.codePointCount(0, value.length)
        if (schema.has("minLength") && length < schema.getInt("minLength")) return ContractError(path, "must have at least ${schema.getInt("minLength")} characters")
        if (schema.has("maxLength") && length > schema.getInt("maxLength")) return ContractError(path, "must have at most ${schema.getInt("maxLength")} characters")
        if (schema.has("pattern") && !matcher(schema.getString("pattern")).containsMatchIn(value)) return ContractError(path, "must match ${schema.getString("pattern")}")
    }
    if (value is Number) {
        val number = value.toDouble()
        if (schema.has("minimum") && number < schema.getDouble("minimum")) return ContractError(path, "must be at least ${schema.get("minimum")}")
        if (schema.has("maximum") && number > schema.getDouble("maximum")) return ContractError(path, "must be at most ${schema.get("maximum")}")
    }
    if (value is JSONArray) {
        if (schema.has("minItems") && value.length() < schema.getInt("minItems")) return ContractError(path, "must have at least ${schema.getInt("minItems")} items")
        if (schema.has("maxItems") && value.length() > schema.getInt("maxItems")) return ContractError(path, "must have at most ${schema.getInt("maxItems")} items")
        schema.optJSONObject("items")?.let { items ->
            for (index in 0 until value.length()) firstError(value.get(index), items, "$path/$index")?.let { return it }
        }
    }
    if (value is JSONObject) {
        val properties = schema.optJSONObject("properties") ?: JSONObject()
        schema.optJSONArray("required")?.let { required ->
            for (index in 0 until required.length()) if (!value.has(required.getString(index))) return ContractError("$path/${required.getString(index)}", "is required")
        }
        val names = value.keys().asSequence().toList()
        if (schema.has("maxProperties") && names.size > schema.getInt("maxProperties")) return ContractError(path, "must have at most ${schema.getInt("maxProperties")} properties")
        schema.optJSONObject("propertyNames")?.let { rule ->
            for (name in names) if (!matcher(rule.getString("pattern")).containsMatchIn(name)) return ContractError("$path/$name", "the name must match ${rule.getString("pattern")}")
        }
        val extra = schema.opt("additionalProperties")
        if (extra == false) {
            for (name in names) if (!properties.has(name)) return ContractError("$path/$name", "is not allowed")
        } else if (extra is JSONObject) {
            for (name in names) if (!properties.has(name)) firstError(value.get(name), extra, "$path/$name")?.let { return it }
        }
        for (name in properties.keys()) if (value.has(name)) firstError(value.get(name), properties.getJSONObject(name), "$path/$name")?.let { return it }
    }
    return null
}
'''


def kotlin_string(text: str) -> str:
    assert text.isascii()
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$") + '"'


def reading(f: gt.Field, source: str = "o") -> str:
    """The Kotlin expression that reads the field `f` of the JSON object `source`, once the document has passed the schema."""
    name = json.dumps(f.name)
    schema = f.schema
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        if items == "array" and not f.nested:
            inner = schema["items"]["items"]["type"]
            getter = {"string": "getString", "integer": "getLong", "number": "getDouble", "boolean": "getBoolean"}[inner]
            return f"{source}.getJSONArray({name}).let {{ rows -> (0 until rows.length()).map {{ r -> rows.getJSONArray(r).let {{ row -> (0 until row.length()).map {{ row.{getter}(it) }} }} }} }}"
        if f.nested:
            return f"{source}.getJSONArray({name}).let {{ a -> (0 until a.length()).map {{ read{f.nested}(a.getJSONObject(it)) }} }}"
        getter = {"string": "getString", "integer": "getLong", "number": "getDouble", "boolean": "getBoolean"}[items]
        return f"{source}.getJSONArray({name}).let {{ a -> (0 until a.length()).map {{ a.{getter}(it) }} }}"
    if kind == "object":
        values = schema.get("additionalProperties")
        if not f.nested and isinstance(values, dict):
            getter = {"string": "getString", "integer": "getLong", "number": "getDouble", "boolean": "getBoolean"}[values["type"]]
            return f"{source}.getJSONObject({name}).let {{ m -> m.keys().asSequence().associateWith {{ m.{getter}(it) }} }}"
        return f"read{f.nested}({source}.getJSONObject({name}))"
    getter = {"string": "getString", "integer": "getLong", "number": "getDouble", "boolean": "getBoolean"}[kind]
    return f"{source}.{getter}({name})"


def render() -> str:
    docs = {}
    for path in sorted(gt.SCHEMAS.glob("*.schema.json")):
        docs[path.name[: -len(".schema.json")]] = json.loads(path.read_text(encoding="utf-8"))
    names = gt.discover()
    out = [HEAD.rstrip("\n"), ""]
    # the schemas as text, one constant each (a constant of the JVM may not be longer than 65535 bytes)
    for key in sorted(docs):
        out.append(f"private const val SCHEMA_{key.upper()} = {kotlin_string(json.dumps(gp.trim(docs[key]), separators=(',', ':')))}")
    out += ["", "private val SCHEMAS: Map<String, JSONObject> by lazy {", "    mapOf("]
    out += [f"        {json.dumps(key)} to JSONObject(SCHEMA_{key.upper()})," for key in sorted(docs)]
    out += [
        "    )",
        "}",
        "",
        "val MESSAGE_NAMES: List<String> get() = SCHEMAS.keys.sorted()",
        "",
        "/** The JSON Schema of the message called `name`, or null: what a reader needs to leave out the members a closed object does not name. */",
        "fun messageSchema(name: String): JSONObject? = SCHEMAS[name]",
        "",
        "/** The first thing wrong with the document as the message called `name` (a JSONObject, a JSONArray, a String, a Number or a Boolean), or null when it is valid. */",
        "fun checkMessage(name: String, value: Any?): ContractError? = firstError(value, SCHEMAS.getValue(name), \"\")",
        "",
    ]
    emitted: set[str] = set()
    roots: dict[str, str] = {}
    for key, (name, declared) in names.items():
        schema = docs[key]
        nested = gt.complete(schema, declared, name)
        for type_name, item in gt.nested_types(schema, nested, emitted):
            fields = gt.fields_of(item, nested)
            out.append(f"fun read{type_name}(o: JSONObject): {type_name} = {type_name}(")
            out += [f"    {gt.kt_name(f.name)} = " + (reading(f) if f.required else f"if (o.has({json.dumps(f.name)})) {reading(f)} else null") + "," for f in fields]
            out += [")", ""]
        fields = gt.fields_of(schema, nested)
        out.append(f"fun read{name}(o: JSONObject): {name} = {name}(")
        out += [f"    {gt.kt_name(f.name)} = " + (reading(f) if f.required else f"if (o.has({json.dumps(f.name)})) {reading(f)} else null") + "," for f in fields]
        out += [")", ""]
        roots[key] = name
    roots["arm_profile"] = "ArmProfile"
    out.append("/** Every message, by the name of its schema: the document read as its data class, or null when it does not satisfy the schema. */")
    for key in sorted(roots):
        out.append(f"fun parse{roots[key]}(o: JSONObject): {roots[key]}? = if (checkMessage({json.dumps(key)}, o) == null) read{roots[key]}(o) else null")
    out.append("")
    out.append("/** The document as the message called `name` (the name of its schema file): its data class, or null when it does not satisfy the schema or the name is not known. */")
    out.append("fun parseMessage(name: String, o: JSONObject): Any? = when (name) {")
    out += [f"    {json.dumps(key)} -> parse{roots[key]}(o)" for key in sorted(roots)]
    out += ["    else -> null", "}", ""]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if current == content:
        print("generated Kotlin parsers are current")
        return 0
    if args.check:
        print("generated/ArmorParsers.kt is out of date", file=sys.stderr)
        return 1
    OUT.write_text(content, encoding="utf-8", newline="\n")
    print("generated Kotlin parsers written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
