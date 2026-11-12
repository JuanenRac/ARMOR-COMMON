#!/usr/bin/env python3
"""Generate the Swift readers and writers of the messages from the published JSON Schemas.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``generated/ArmorContract.swift`` holds, inside the namespace ``Contract``, a struct for every message (the same names and members as ``ArmorContracts.kt``), the schemas as text, one
small interpreter that applies them the way ``armor_common.schema`` does (the same keywords, the same ASCII meaning of the patterns and the same order of checks), and for each
message:

* ``Contract.check(name, document)`` says what is wrong with a document and where, or gives nil when it is valid;
* ``Contract.parse<Message>(document)`` gives the struct, or nil when the document is not valid;
* ``Contract.<Message>(reading:)`` builds the struct from a document that has passed, and ``toJSON()`` writes it back with the members the schema names and nothing else;
* ``Contract.rewrite(name, document)`` validates, reads and writes in one step.

The document is what ``JSONSerialization`` gives (``[String: Any]``). The iPhone app uses it as the other clients use their own generated readers, and the vectors of ``conformance/``
keep it equal to them.

    python tools/generate_swift_parsers.py           # write generated/ArmorContract.swift
    python tools/generate_swift_parsers.py --check   # verify it is current
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
OUT = ROOT / "generated" / "ArmorContract.swift"

SWIFT_KEYWORDS = {"associatedtype", "class", "deinit", "enum", "extension", "fileprivate", "func", "import", "init", "inout", "internal", "let", "open", "operator", "private", "precedencegroup",
                  "protocol", "public", "rethrows", "static", "struct", "subscript", "typealias", "var", "break", "case", "catch", "continue", "default", "defer", "do", "else", "fallthrough",
                  "for", "guard", "if", "in", "repeat", "return", "throw", "switch", "where", "while", "Any", "as", "await", "false", "is", "nil", "self", "Self", "super", "throws", "true",
                  "try", "Type", "Protocol"}
RESERVED_LOCALS = {"document", "out"}
SCALAR = {"string": "String", "integer": "Int64", "number": "Double", "boolean": "Bool"}
AS = {"string": "asStr", "integer": "asInt", "number": "asNum", "boolean": "asFlag"}
AT = {"string": "str", "integer": "int", "number": "num", "boolean": "flag"}

HEAD = r'''// Generated from the A.R.M.O.R. JSON Schemas by tools/generate_swift_parsers.py. Do not edit.
import Foundation

public enum Contract {
    /// What a document gets wrong: where (`/zones/0/id`) and what.
    public struct ContractError: Error, Equatable, CustomStringConvertible {
        public let path: String
        public let detail: String
        public init(path: String, detail: String) {
            self.path = path
            self.detail = detail
        }
        public var description: String { "\(path.isEmpty ? "$" : path): \(detail)" }
    }

    // MARK: reading values of a document (a value of the wrong kind never crashes: it takes a harmless default)

    static func isBool(_ value: Any) -> Bool {
        guard let number = value as? NSNumber else { return false }
        return String(cString: number.objCType) == "c"
    }

    static func numberOf(_ value: Any) -> Double? {
        if isBool(value) { return nil }
        guard let number = value as? NSNumber else { return nil }
        return number.doubleValue
    }

    static func asStr(_ value: Any) -> String { value as? String ?? "" }
    static func asInt(_ value: Any) -> Int64 { numberOf(value).map { ($0.isFinite && abs($0) < 9.2e18) ? Int64($0) : 0 } ?? 0 }
    static func asNum(_ value: Any) -> Double { numberOf(value) ?? 0 }
    static func asFlag(_ value: Any) -> Bool { isBool(value) ? ((value as? NSNumber)?.boolValue ?? false) : false }
    static func objOf(_ value: Any) -> [String: Any] { value as? [String: Any] ?? [:] }
    static func listOf(_ value: Any) -> [Any] { value as? [Any] ?? [] }

    static func str(_ o: [String: Any], _ key: String) -> String { o[key].map(asStr) ?? "" }
    static func int(_ o: [String: Any], _ key: String) -> Int64 { o[key].map(asInt) ?? 0 }
    static func num(_ o: [String: Any], _ key: String) -> Double { o[key].map(asNum) ?? 0 }
    static func flag(_ o: [String: Any], _ key: String) -> Bool { o[key].map(asFlag) ?? false }
    static func objAt(_ o: [String: Any], _ key: String) -> [String: Any] { o[key].map(objOf) ?? [:] }
    static func listAt(_ o: [String: Any], _ key: String) -> [Any] { o[key].map(listOf) ?? [] }

    // MARK: the interpreter of the schemas

    private static let regexLock = NSLock()
    private static var compiled: [String: NSRegularExpression] = [:]

    private static func matches(_ pattern: String, _ text: String) -> Bool {
        regexLock.lock()
        var regex = compiled[pattern]
        if regex == nil {
            regex = try? NSRegularExpression(pattern: pattern, options: [])
            compiled[pattern] = regex
        }
        regexLock.unlock()
        guard let found = regex else { return false }
        return found.firstMatch(in: text, options: [], range: NSRange(location: 0, length: (text as NSString).length)) != nil
    }

    private static func typeMatches(_ value: Any, _ type: String) -> Bool {
        switch type {
        case "object": return value is [String: Any]
        case "array": return value is [Any]
        case "string": return value is String
        case "boolean": return isBool(value)
        case "integer":
            guard let number = numberOf(value), number.isFinite else { return false }
            return number == number.rounded(.towardZero)
        case "number":
            guard let number = numberOf(value) else { return false }
            return number.isFinite
        default: return false
        }
    }

    private static func same(_ a: Any, _ b: Any) -> Bool {
        if isBool(a) || isBool(b) { return isBool(a) && isBool(b) && asFlag(a) == asFlag(b) }
        if let x = numberOf(a), let y = numberOf(b) { return x == y }
        if let x = a as? String, let y = b as? String { return x == y }
        return false
    }

    private static func show(_ value: Any?) -> String {
        guard let value = value else { return "" }
        if let data = try? JSONSerialization.data(withJSONObject: value, options: [.fragmentsAllowed, .sortedKeys]), let text = String(data: data, encoding: .utf8) { return text }
        return "\(value)"
    }

    /// The first way in which `value` does not satisfy `schema`, in the order Python's validator finds it, or nil.
    private static func firstError(_ value: Any, _ schema: [String: Any], _ path: String) -> ContractError? {
        if let type = schema["type"] as? String, !typeMatches(value, type) { return ContractError(path: path, detail: "must be of type \(type)") }
        if let fixed = schema["const"], !same(value, fixed) { return ContractError(path: path, detail: "must equal \(show(fixed))") }
        if let options = schema["enum"] as? [Any], !options.contains(where: { same(value, $0) }) { return ContractError(path: path, detail: "must be one of \(show(options))") }
        if let text = value as? String, !isBool(value) {
            let length = text.unicodeScalars.count
            if let least = schema["minLength"] as? Int, length < least { return ContractError(path: path, detail: "must have at least \(least) characters") }
            if let most = schema["maxLength"] as? Int, length > most { return ContractError(path: path, detail: "must have at most \(most) characters") }
            if let pattern = schema["pattern"] as? String, !matches(pattern, text) { return ContractError(path: path, detail: "must match \(pattern)") }
        }
        if let number = numberOf(value) {
            if let least = schema["minimum"], let limit = numberOf(least), number < limit { return ContractError(path: path, detail: "must be at least \(show(least))") }
            if let most = schema["maximum"], let limit = numberOf(most), number > limit { return ContractError(path: path, detail: "must be at most \(show(most))") }
        }
        if let list = value as? [Any] {
            if let least = schema["minItems"] as? Int, list.count < least { return ContractError(path: path, detail: "must have at least \(least) items") }
            if let most = schema["maxItems"] as? Int, list.count > most { return ContractError(path: path, detail: "must have at most \(most) items") }
            if let items = schema["items"] as? [String: Any] {
                for (index, element) in list.enumerated() {
                    if let found = firstError(element, items, "\(path)/\(index)") { return found }
                }
            }
        }
        if let object = value as? [String: Any] {
            let properties = schema["properties"] as? [String: Any] ?? [:]
            if let required = schema["required"] as? [String] {
                for name in required where object[name] == nil { return ContractError(path: "\(path)/\(name)", detail: "is required") }
            }
            let names = object.keys.sorted()
            if let most = schema["maxProperties"] as? Int, names.count > most { return ContractError(path: path, detail: "must have at most \(most) properties") }
            if let rule = schema["propertyNames"] as? [String: Any], let pattern = rule["pattern"] as? String {
                for name in names where !matches(pattern, name) { return ContractError(path: "\(path)/\(name)", detail: "the name must match \(pattern)") }
            }
            let extra = schema["additionalProperties"]
            if let allowed = extra as? [String: Any] {
                for name in names where properties[name] == nil {
                    if let found = firstError(object[name] as Any, allowed, "\(path)/\(name)") { return found }
                }
            } else if let allowed = extra, isBool(allowed), !asFlag(allowed) {
                for name in names where properties[name] == nil { return ContractError(path: "\(path)/\(name)", detail: "is not allowed") }
            }
            for name in properties.keys.sorted() {
                guard let member = object[name], let rule = properties[name] as? [String: Any] else { continue }
                if let found = firstError(member, rule, "\(path)/\(name)") { return found }
            }
        }
        return nil
    }

    private static func read(_ text: String) -> [String: Any] {
        guard let data = text.data(using: .utf8), let value = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return [:] }
        return value
    }

    /// The schema of each message, by the name of its file.
    public static let schemas: [String: [String: Any]] = {
        var found: [String: [String: Any]] = [:]
        for (name, text) in schemaTexts { found[name] = read(text) }
        return found
    }()

    /// The names of the messages.
    public static var messageNames: [String] { schemaTexts.keys.sorted() }

    /// The first thing wrong with the document as the message called `name`, or nil when it is valid. An unknown name is an error.
    public static func check(_ name: String, _ value: Any) -> ContractError? {
        guard let schema = schemas[name] else { return ContractError(path: "", detail: "unknown message \(name)") }
        return firstError(value, schema, "")
    }
'''


def swift_string(text: str) -> str:
    """A raw string literal that holds `text` as it is."""
    assert text.isascii() and '"#' not in text and "\n" not in text
    return '#"' + text + '"#'


def prop(name: str) -> str:
    return f"`{name}`" if name in SWIFT_KEYWORDS else name


def swift_type(f: gt.Field) -> str:
    schema = f.schema
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        if items == "array" and not f.nested:
            return f"[[{SCALAR[schema['items']['items']['type']]}]]"
        return f"[{f.nested or SCALAR.get(items, 'Any')}]"
    if kind == "object":
        values = schema.get("additionalProperties")
        if not f.nested and isinstance(values, dict) and values.get("type") in SCALAR:
            return f"[String: {SCALAR[values['type']]}]"
        return f.nested or "[String: Any]"
    return SCALAR[kind]


def default_of(f: gt.Field) -> str:
    if "const" in f.schema and f.required:
        value = f.schema["const"]
        if isinstance(value, bool):
            return " = " + ("true" if value else "false")
        if isinstance(value, str):
            assert value.isascii() and "\\" not in value and '"' not in value
            return f' = "{value}"'
        return f" = {value!r}"
    return "" if f.required else " = nil"


def reading(f: gt.Field) -> str:
    """The Swift expression that reads the field `f` from `document`, once the document has passed the schema."""
    key = json.dumps(f.name)
    schema = f.schema
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        if items == "array" and not f.nested:
            inner = schema["items"]["items"]["type"]
            return f"Contract.listAt(document, {key}).map {{ Contract.listOf($0).map(Contract.{AS[inner]}) }}"
        if f.nested:
            return f"Contract.listAt(document, {key}).map {{ Contract.{f.nested}(reading: Contract.objOf($0)) }}"
        if items in AS:
            return f"Contract.listAt(document, {key}).map(Contract.{AS[items]})"
        return f"Contract.listAt(document, {key})"
    if kind == "object":
        values = schema.get("additionalProperties")
        if not f.nested and isinstance(values, dict) and values.get("type") in AS:
            return f"Contract.objAt(document, {key}).mapValues(Contract.{AS[values['type']]})"
        if f.nested:
            return f"Contract.{f.nested}(reading: Contract.objAt(document, {key}))"
        return f"Contract.objAt(document, {key})"
    return f"Contract.{AT[kind]}(document, {key})"


def writing(f: gt.Field, source: str) -> str:
    schema = f.schema
    if schema["type"] == "array" and f.nested:
        return f"{source}.map {{ $0.toJSON() }}"
    if schema["type"] == "object" and f.nested:
        return f"{source}.toJSON()"
    return source


def struct(type_name: str, fields: list[gt.Field]) -> list[str]:
    for f in fields:
        assert f.name not in RESERVED_LOCALS, f.name
    out = [f"    public struct {type_name} {{"]
    out += [f"        public var {prop(f.name)}: {swift_type(f)}{'' if f.required else '?'}" for f in fields]
    arguments = ", ".join(f"{prop(f.name)}: {swift_type(f)}{'' if f.required else '?'}{default_of(f)}" for f in fields)
    out.append(f"        public init({arguments}) {{")
    out += [f"            self.{prop(f.name)} = {prop(f.name)}" for f in fields]
    out += ["        }", "    }", ""]
    return out


def extension(type_name: str, fields: list[gt.Field]) -> list[str]:
    out = [f"extension Contract.{type_name} {{", "    /// The message from a document that has passed its schema."]
    out.append("    public init(reading document: [String: Any]) {")
    for f in fields:
        if f.required:
            out.append(f"        self.{prop(f.name)} = {reading(f)}")
        else:
            out.append(f"        if document[{json.dumps(f.name)}] != nil {{ self.{prop(f.name)} = {reading(f)} }} else {{ self.{prop(f.name)} = nil }}")
    out += ["    }", "", "    /// The document the message was read from, with the members the schema names and no other."]
    out.append("    public func toJSON() -> [String: Any] {")
    out.append("        var out: [String: Any] = [:]")
    for f in fields:
        if f.required:
            out.append(f"        out[{json.dumps(f.name)}] = {writing(f, 'self.' + prop(f.name))}")
        else:
            out.append(f"        if let value = self.{prop(f.name)} {{ out[{json.dumps(f.name)}] = {writing(f, 'value')} }}")
    out += ["        return out", "    }", "}", ""]
    return out


def render() -> str:
    docs = {}
    for path in sorted(gt.SCHEMAS.glob("*.schema.json")):
        docs[path.name[: -len(".schema.json")]] = json.loads(path.read_text(encoding="utf-8"))
    names = gt.discover()
    out = [HEAD.rstrip("\n"), ""]
    out.append("    private static let schemaTexts: [String: String] = [")
    out += [f"        {json.dumps(key)}: {swift_string(json.dumps(gp.trim(docs[key]), separators=(',', ':')))}," for key in sorted(docs)]
    out += ["    ]", ""]
    emitted: set[str] = set()
    roots: dict[str, str] = {}
    structs: list[str] = []
    extensions: list[str] = []
    for key, (name, declared) in names.items():
        schema = docs[key]
        nested = gt.complete(schema, declared, name)
        for type_name, item in gt.nested_types(schema, nested, emitted):
            fields = gt.fields_of(item, nested)
            structs += struct(type_name, fields)
            extensions += extension(type_name, fields)
        fields = gt.fields_of(schema, nested)
        structs += struct(name, fields)
        extensions += extension(name, fields)
        roots[key] = name
    roots["arm_profile"] = "ArmProfile"
    out += ["    // MARK: the messages", ""] + structs
    out.append("    // MARK: reading by name")
    out.append("")
    for key in sorted(roots):
        out.append(f"    /// The `{key}` message, or nil when the document does not satisfy its schema.")
        body = "check(" + json.dumps(key) + ", document) == nil ? " + roots[key] + "(reading: document) : nil"
        out.append(f"    public static func parse{roots[key]}(_ document: [String: Any]) -> {roots[key]}? {{ {body} }}")
    out += ["", "    /// The document as the message called `name`: its struct, or nil when it does not satisfy the schema or the name is not known.",
            "    public static func parse(_ name: String, _ document: [String: Any]) -> Any? {", "        switch name {"]
    out += [f"        case {json.dumps(key)}: return parse{roots[key]}(document)" for key in sorted(roots)]
    out += ["        default: return nil", "        }", "    }", "",
            "    /// A valid document read and written again: the members the schema names, as the struct holds them; nil when the document is not valid.",
            "    public static func rewrite(_ name: String, _ document: [String: Any]) -> [String: Any]? {", "        switch name {"]
    out += [f"        case {json.dumps(key)}: return parse{roots[key]}(document)?.toJSON()" for key in sorted(roots)]
    out += ["        default: return nil", "        }", "    }", "}", ""]
    return "\n".join(out + extensions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if current == content:
        print("generated Swift parsers are current")
        return 0
    if args.check:
        print("generated/ArmorContract.swift is out of date", file=sys.stderr)
        return 1
    OUT.write_text(content, encoding="utf-8", newline="\n")
    print("generated Swift parsers written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
