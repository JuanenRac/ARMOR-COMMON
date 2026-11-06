#!/usr/bin/env python3
"""Generate the C++ readers and writers of the messages from the published JSON Schemas.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``generated/armor_wire.hpp`` holds, for every schema: the C++ struct of the message, ``validate_<schema>`` (the schema itself as a table that a few lines of C++ interpret, so the node
refuses exactly what the Python and TypeScript validators refuse), ``parse_<schema>`` (validate, then fill the struct) and ``write_<schema>`` (the struct as JSON, member by member in
the order of the schema). A copy lives in ``firmware_base/core/`` and reaches every node project with the rest of the shared firmware (``tools/sync_firmware_base.py``), where ``tests/test_wire.cpp`` runs it against the oracle.

The header is never edited by hand: ``--check`` fails when it is out of date, which is how CI keeps the nodes honest. ``tools/make_wire_cases.py`` writes the seeded cases with the
verdict of the Python validator that the host tests of the nodes run against this header.

    python tools/generate_wire.py           # write generated/ and firmware_base/core/
    python tools/generate_wire.py --check   # verify it is current
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import generate_types as gt   # noqa: E402
import wire_regex   # noqa: E402

ROOT = gt.ROOT
OUTPUTS = (ROOT / "generated" / "armor_wire.hpp", ROOT / "firmware_base" / "core" / "armor_wire.hpp")
CPP_KEYWORDS = {"alignas", "and", "auto", "bool", "break", "case", "catch", "char", "class", "const", "continue", "default", "delete", "do", "double", "else", "enum", "explicit", "export", "extern", "false",
                "float", "for", "friend", "goto", "if", "inline", "int", "long", "mutable", "namespace", "new", "not", "operator", "or", "private", "protected", "public", "register", "return", "short",
                "signed", "sizeof", "static", "struct", "switch", "template", "this", "throw", "true", "try", "typedef", "typename", "union", "unsigned", "using", "virtual", "void", "volatile", "while", "xor"}
TYPE_CODES = {None: 0, "object": 1, "array": 2, "string": 3, "boolean": 4, "integer": 5, "number": 6}


def snake(name: str) -> str:
    return name


def member(name: str) -> str:
    return name + "_" if name in CPP_KEYWORDS else name


def literal(text: str) -> str:
    assert text.isascii() and all(ord(c) >= 32 for c in text), text
    return json.dumps(text)


def number(value: float) -> str:
    return repr(float(value))


# ---- the schema as a table ----------------------------------------------------------------------------------------------------------------------------------------------------------

class Tables:
    def __init__(self) -> None:
        self.nodes: list[dict] = []
        self.props: list[tuple[str, int, bool]] = []
        self.lits: list[tuple[int, str, float, bool]] = []
        self.patterns: list[wire_regex.Automaton] = []
        self._pattern_index: dict[str, int] = {}
        self.sets: list[tuple[bool, tuple[tuple[int, int], ...]]] = []
        self.ranges: list[tuple[int, int]] = []

    def pattern(self, text: str) -> int:
        if text not in self._pattern_index:
            self._pattern_index[text] = len(self.patterns)
            self.patterns.append(wire_regex.compile_pattern(text))
        return self._pattern_index[text]

    def lit(self, value) -> int:
        if isinstance(value, bool):
            entry = (2, "", 0.0, value)
        elif isinstance(value, (int, float)):
            entry = (1, "", float(value), False)
        elif isinstance(value, str):
            entry = (0, value, 0.0, False)
        else:
            raise AssertionError(value)
        self.lits.append(entry)
        return len(self.lits) - 1

    def add(self, schema: dict) -> int:
        index = len(self.nodes)
        node: dict = {"type": TYPE_CODES[schema.get("type")]}
        self.nodes.append(node)
        node["min"] = schema.get("minimum")
        node["max"] = schema.get("maximum")
        node["minlen"] = schema.get("minLength", -1)
        node["maxlen"] = schema.get("maxLength", -1)
        node["pattern"] = self.pattern(schema["pattern"]) if "pattern" in schema else -1
        node["enum"] = (len(self.lits), len(schema["enum"])) if "enum" in schema else (0, 0)
        for value in schema.get("enum", []):
            self.lit(value)
        node["const"] = self.lit(schema["const"]) if "const" in schema else -1
        node["minitems"] = schema.get("minItems", -1)
        node["maxitems"] = schema.get("maxItems", -1)
        node["items"] = self.add(schema["items"]) if isinstance(schema.get("items"), dict) else -1
        props = schema.get("properties", {})
        required = list(schema.get("required", []))
        children = [(name, self.add(child)) for name, child in props.items()]   # the children add their own members first
        first = len(self.props)
        for name, child in children:
            self.props.append((name, child, name in required))
        for name in required:
            if name not in props:
                self.props.append((name, -1, True))
        node["props"] = (first, len(self.props) - first)
        extra = schema.get("additionalProperties")
        node["extra"] = 1 if extra is False else (2 if isinstance(extra, dict) else 0)
        node["extra_node"] = self.add(extra) if isinstance(extra, dict) else -1
        node["name_pattern"] = self.pattern(schema["propertyNames"]["pattern"]) if "propertyNames" in schema else -1
        node["max_props"] = schema.get("maxProperties", -1)
        return index

    def render(self) -> list[str]:
        out = []
        # sets and ranges, global
        set_rows: list[tuple[int, int, bool]] = []
        pattern_rows: list[tuple[int, int, int]] = []
        state_rows: list[tuple[int, int, int]] = []
        for auto in self.patterns:
            base_set = len(set_rows)
            for negated, ranges in auto.sets:
                set_rows.append((len(self.ranges), len(ranges), negated))
                self.ranges.extend(ranges)
            base_state = len(state_rows)
            for op, a, b in auto.states:
                if op == 0:
                    state_rows.append((0, a + base_set, b + base_state))
                elif op == 1:
                    state_rows.append((1, a + base_state, b + base_state))
                else:
                    state_rows.append((2, -1, -1))
            pattern_rows.append((base_state, auto.start + base_state, len(auto.states)))
        out.append("inline constexpr Range kRanges[] = {" + ", ".join(f"{{{a}u, {b}u}}" for a, b in self.ranges) + ", {0u, 0u}};")
        out.append("inline constexpr CharSet kSets[] = {" + ", ".join(f"{{{a}, {b}, {'true' if n else 'false'}}}" for a, b, n in set_rows) + "};")
        out.append("inline constexpr State kStates[] = {" + ", ".join(f"{{{op}, {a}, {b}}}" for op, a, b in state_rows) + "};")
        out.append("inline constexpr Pattern kPatterns[] = {" + ", ".join(f"{{{first}, {start}, {count}}}" for first, start, count in pattern_rows) + "};")
        lits = ", ".join(f"{{{k}, {literal(s)}, {number(n)}, {'true' if b else 'false'}}}" for k, s, n, b in self.lits)
        out.append(f"inline constexpr Lit kLits[] = {{{lits}, {{0, \"\", 0.0, false}}}};")
        props = ", ".join(f"{{{literal(n)}, {c}, {'true' if r else 'false'}}}" for n, c, r in self.props)
        out.append(f"inline constexpr Prop kProps[] = {{{props}, {{\"\", -1, false}}}};")
        rows = []
        for node in self.nodes:
            lo = "true, " + number(node["min"]) if node["min"] is not None else "false, 0.0"
            hi = "true, " + number(node["max"]) if node["max"] is not None else "false, 0.0"
            rows.append(f"{{{node['type']}, {lo}, {hi}, {node['minlen']}, {node['maxlen']}, {node['pattern']}, {node['enum'][0]}, {node['enum'][1]}, {node['const']}, {node['minitems']}, "
                        f"{node['maxitems']}, {node['items']}, {node['props'][0]}, {node['props'][1]}, {node['extra']}, {node['extra_node']}, {node['name_pattern']}, {node['max_props']}}}")
        out.append("inline constexpr Node kNodes[] = {\n    " + ",\n    ".join(rows) + "};")
        return out


# ---- the structs ---------------------------------------------------------------------------------------------------------------------------------------------------------------

SCALAR_CPP = {"string": "std::string", "integer": "long long", "number": "double", "boolean": "bool"}


def cpp_type(field: gt.Field) -> str:
    schema = field.schema
    kind = schema["type"]
    if kind == "array":
        items = schema.get("items", {}).get("type")
        if items == "array" and not field.nested:
            return f"std::vector<std::vector<{SCALAR_CPP[schema['items']['items']['type']]}>>"
        return f"std::vector<{field.nested or SCALAR_CPP[items]}>"
    if kind == "object":
        values = schema.get("additionalProperties")
        if not field.nested and isinstance(values, dict):
            return f"Map<{SCALAR_CPP[values['type']]}>"
        assert field.nested, field.name
        return field.nested
    return SCALAR_CPP[kind]


def default_of(field: gt.Field) -> str:
    schema = field.schema
    if "const" in schema and field.required:
        value = schema["const"]
        return f' = {literal(value)}' if isinstance(value, str) else f" = {json.dumps(value)}"
    if field.required and schema["type"] == "integer":
        return " = 0"
    if field.required and schema["type"] == "number":
        return " = 0.0"
    if field.required and schema["type"] == "boolean":
        return " = false"
    return ""


def render_structs(docs: dict[str, dict]) -> tuple[list[str], list[str], list[str], list[tuple[str, str, dict, dict]]]:
    structs, forwards, bodies = [], [], []
    emitted: set[str] = set()
    roots = []

    def emit(type_name: str, item: dict, nested: dict[str, str]) -> None:
        fields = gt.fields_of(item, nested)
        lines = [f"struct {type_name} {{"]
        for f in fields:
            t = cpp_type(f)
            lines.append(f"  {('std::optional<' + t + '>') if not f.required else t} {member(f.name)}{default_of(f)};")
        lines += ["};", ""]
        structs.extend(lines)
        forwards.append(f"inline void take(const json::Value& value, {type_name}& out);")
        forwards.append(f"inline void put(json::Writer& w, const {type_name}& value);")
        read = [f"inline void take(const json::Value& value, {type_name}& out) {{"]
        write = [f"inline void put(json::Writer& w, const {type_name}& value) {{", "  w.begin_object();"]
        for f in fields:
            name, mem = literal(f.name), member(f.name)
            if f.required:
                read.append(f"  if (const json::Value* m = value.get({name})) take(*m, out.{mem});")
                write.append(f"  w.key({name}); put(w, value.{mem});")
            else:
                read.append(f"  if (const json::Value* m = value.get({name})) {{ typename std::decay<decltype(*out.{mem})>::type t{{}}; take(*m, t); out.{mem} = std::move(t); }}")
                write.append(f"  if (value.{mem}) {{ w.key({name}); put(w, *value.{mem}); }}")
        read.append("}")
        write += ["  w.end_object();", "}"]
        bodies.extend(read + write + [""])

    for key, (name, declared) in gt.discover().items():
        schema = docs[key]
        nested = gt.complete(schema, declared, name)
        for type_name, item in gt.nested_types(schema, nested, emitted):
            emit(type_name, item, nested)
        emit(name, schema, nested)
        roots.append((key, name, schema, nested))
    return structs, forwards, bodies, roots


PRELUDE = r'''
// Generated from the A.R.M.O.R. JSON Schemas by tools/generate_wire.py. Do not edit.
// The messages of the contract as C++: a struct, a validator, a reader and a writer for each schema. The validators run the schema itself (a table), so they refuse what the
// Python and TypeScript validators refuse; tests/test_wire_oracle.cpp of ARMOR-COMMON checks that with seeded cases whose verdict comes from the Python validator.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

#include "json.hpp"

namespace armor::wire {

// A map of one kind of value (the object of a message whose names are not fixed).
template <class T>
struct Map {
  std::vector<std::pair<std::string, T>> items;
};

namespace table {
struct Range { std::uint32_t low, high; };
struct CharSet { int first, count; bool negated; };
struct State { int op, a, b; };               // op 0: take one code point of set a, go to b; 1: split into a and b; 2: accept
struct Pattern { int first, start, count; };
struct Lit { int kind; std::string_view text; double number; bool boolean; };   // kind 0 text, 1 number, 2 boolean
struct Prop { std::string_view name; int node; bool required; };
struct Node {
  int type;   // 0 any, 1 object, 2 array, 3 string, 4 boolean, 5 integer, 6 number
  bool has_min; double min; bool has_max; double max;
  int min_length, max_length, pattern, enum_first, enum_count, constant, min_items, max_items, items, props_first, props_count;
  int extra;   // 0 free, 1 forbidden, 2 every other value follows extra_node
  int extra_node, name_pattern, max_props;
};
'''

RUNTIME = r'''
}  // namespace table

namespace detail {
inline bool next_code_point(std::string_view text, std::size_t& at, std::uint32_t& out) {
  const unsigned char c = static_cast<unsigned char>(text[at]);
  std::size_t extra = 0;
  if (c >= 0x80) {
    if ((c >> 5) == 6) extra = 1;
    else if ((c >> 4) == 14) extra = 2;
    else if ((c >> 3) == 30) extra = 3;
    else return false;
  }
  if (at + extra >= text.size()) return false;
  out = extra == 0 ? c : extra == 1 ? (c & 0x1fu) : extra == 2 ? (c & 0x0fu) : (c & 0x07u);
  for (std::size_t i = 1; i <= extra; ++i) out = (out << 6) | (static_cast<unsigned char>(text[at + i]) & 0x3fu);
  at += extra + 1;
  return true;
}

inline std::size_t code_points(std::string_view text) {
  std::size_t count = 0;
  for (char c : text) if ((static_cast<unsigned char>(c) & 0xc0u) != 0x80u) ++count;
  return count;
}

inline bool in_set(const table::CharSet& set, std::uint32_t code) {
  bool inside = false;
  for (int i = 0; i < set.count && !inside; ++i) {
    const table::Range& r = table::kRanges[set.first + i];
    inside = code >= r.low && code <= r.high;
  }
  return inside != set.negated;
}

// Runs the automaton of a pattern over the whole text. One flag per state, no recursion.
inline bool matches(int pattern, std::string_view text) {
  const table::Pattern& p = table::kPatterns[pattern];
  std::vector<unsigned char> now(static_cast<std::size_t>(p.count), 0), next(static_cast<std::size_t>(p.count), 0);
  std::vector<int> stack;
  auto close = [&](std::vector<unsigned char>& flags, std::vector<int>& seeds) {
    while (!seeds.empty()) {
      const int s = seeds.back();
      seeds.pop_back();
      if (flags[static_cast<std::size_t>(s - p.first)]) continue;
      flags[static_cast<std::size_t>(s - p.first)] = 1;
      if (table::kStates[s].op == 1) { seeds.push_back(table::kStates[s].a); seeds.push_back(table::kStates[s].b); }
    }
  };
  stack.push_back(p.start);
  close(now, stack);
  std::size_t at = 0;
  while (at < text.size()) {
    std::uint32_t code = 0;
    if (!next_code_point(text, at, code)) return false;
    std::fill(next.begin(), next.end(), static_cast<unsigned char>(0));
    for (int i = 0; i < p.count; ++i) {
      if (!now[static_cast<std::size_t>(i)]) continue;
      const table::State& s = table::kStates[p.first + i];
      if (s.op == 0 && in_set(table::kSets[s.a], code)) stack.push_back(s.b);
    }
    close(next, stack);
    now.swap(next);
  }
  for (int i = 0; i < p.count; ++i) if (now[static_cast<std::size_t>(i)] && table::kStates[p.first + i].op == 2) return true;
  return false;
}

inline bool literal_equals(const table::Lit& lit, const json::Value& v) {
  return lit.kind == 0 ? v.is_string() && v.text == lit.text : lit.kind == 1 ? v.is_number() && v.number == lit.number : v.is_bool() && v.boolean == lit.boolean;
}

inline bool check(int index, const json::Value& v) {
  const table::Node& n = table::kNodes[index];
  switch (n.type) {
    case 1: if (!v.is_object()) return false; break;
    case 2: if (!v.is_array()) return false; break;
    case 3: if (!v.is_string()) return false; break;
    case 4: if (!v.is_bool()) return false; break;
    case 5: if (!v.is_number() || !std::isfinite(v.number) || v.number != std::floor(v.number)) return false; break;
    case 6: if (!v.is_number() || !std::isfinite(v.number)) return false; break;
    default: break;
  }
  if (n.constant >= 0 && !literal_equals(table::kLits[n.constant], v)) return false;
  if (n.enum_count > 0) {
    bool found = false;
    for (int i = 0; i < n.enum_count && !found; ++i) found = literal_equals(table::kLits[n.enum_first + i], v);
    if (!found) return false;
  }
  if (v.is_string()) {
    if (n.min_length >= 0 || n.max_length >= 0) {
      const std::size_t length = code_points(v.text);
      if (n.min_length >= 0 && length < static_cast<std::size_t>(n.min_length)) return false;
      if (n.max_length >= 0 && length > static_cast<std::size_t>(n.max_length)) return false;
    }
    if (n.pattern >= 0 && !matches(n.pattern, v.text)) return false;
  }
  if (v.is_number()) {
    if (n.has_min && v.number < n.min) return false;
    if (n.has_max && v.number > n.max) return false;
  }
  if (v.is_array()) {
    if (n.min_items >= 0 && v.items.size() < static_cast<std::size_t>(n.min_items)) return false;
    if (n.max_items >= 0 && v.items.size() > static_cast<std::size_t>(n.max_items)) return false;
    if (n.items >= 0) for (const json::Value& item : v.items) if (!check(n.items, item)) return false;
  }
  if (v.is_object()) {
    if (n.max_props >= 0 && v.items.size() > static_cast<std::size_t>(n.max_props)) return false;
    for (int i = 0; i < n.props_count; ++i) {
      const table::Prop& p = table::kProps[n.props_first + i];
      if (p.required && v.get(p.name) == nullptr) return false;
    }
    for (const std::string& name : v.names) if (n.name_pattern >= 0 && !matches(n.name_pattern, name)) return false;
    for (std::size_t i = 0; i < v.names.size(); ++i) {
      int declared = -2;
      for (int j = 0; j < n.props_count; ++j) {
        const table::Prop& p = table::kProps[n.props_first + j];
        if (p.name == v.names[i]) { declared = p.node; break; }
      }
      if (declared == -2) {
        if (n.extra == 1) return false;
        if (n.extra == 2 && !check(n.extra_node, v.items[i])) return false;
      } else if (declared >= 0 && !check(declared, v.items[i])) return false;
    }
  }
  return true;
}
}  // namespace detail

// ---- reading and writing the pieces ------------------------------------------------------------------------------------------------------------------------------------------
'''

HELPERS = r'''
inline void take(const json::Value& value, std::string& out) { out = value.text; }
inline void take(const json::Value& value, long long& out) { out = static_cast<long long>(value.number); }
inline void take(const json::Value& value, double& out) { out = value.number; }
inline void take(const json::Value& value, bool& out) { out = value.boolean; }
template <class T> void take(const json::Value& value, std::vector<T>& out) {
  out.clear();
  for (const json::Value& item : value.items) { T element{}; take(item, element); out.push_back(std::move(element)); }
}
template <class T> void take(const json::Value& value, Map<T>& out) {
  out.items.clear();
  for (std::size_t i = 0; i < value.names.size(); ++i) { T element{}; take(value.items[i], element); out.items.emplace_back(value.names[i], std::move(element)); }
}
inline void put(json::Writer& w, const std::string& value) { w.string(value); }
inline void put(json::Writer& w, long long value) { w.integer(value); }
inline void put(json::Writer& w, double value) { w.number(value); }
inline void put(json::Writer& w, bool value) { w.boolean(value); }
template <class T> void put(json::Writer& w, const std::vector<T>& values) {
  w.begin_array();
  for (const T& element : values) put(w, element);
  w.end_array();
}
template <class T> void put(json::Writer& w, const Map<T>& values) {
  w.begin_object();
  for (const auto& entry : values.items) { w.key(entry.first); put(w, entry.second); }
  w.end_object();
}
'''


def render_cpp() -> str:
    docs = {key: json.loads((gt.SCHEMAS / f"{key}.schema.json").read_text(encoding="utf-8")) for key in gt.discover()}
    for path in sorted(gt.SCHEMAS.glob("*.schema.json")):
        key = path.name[: -len(".schema.json")]
        docs.setdefault(key, json.loads(path.read_text(encoding="utf-8")))
    tables = Tables()
    roots = {key: tables.add(docs[key]) for key in sorted(docs)}
    structs, forwards, bodies, struct_roots = render_structs(docs)

    out = [PRELUDE.strip("\n")]
    out += tables.render()
    out.append("")
    out.append("inline constexpr struct { std::string_view name; int root; } kSchemas[] = {" + ", ".join(f"{{{literal(k)}, {roots[k]}}}" for k in sorted(roots)) + "};")
    out.append(RUNTIME.strip("\n"))
    out.append("")
    out += structs
    out += forwards
    out.append(HELPERS.strip("\n"))
    out.append("")
    out += bodies
    out.append("// ---- one validator, reader and writer for each schema ---------------------------------------------------------------------------------------------------------")
    out.append("")
    out.append("/// Does the document satisfy the schema called `name` (the file name without `.schema.json`)? An unknown name is refused.")
    out.append("inline bool validate_message(std::string_view name, const json::Value& value) {")
    out.append("  for (const auto& schema : table::kSchemas) if (schema.name == name) return detail::check(schema.root, value);")
    out.append("  return false;")
    out.append("}")
    out.append("")
    out.append("inline constexpr std::string_view kSchemaNames[] = {" + ", ".join(literal(k) for k in sorted(roots)) + "};")
    out.append("")
    for key in sorted(roots):
        out.append(f"inline bool validate_{key}(const json::Value& value) {{ return detail::check({roots[key]}, value); }}")
    out.append("")
    struct_by_key = {key: name for key, name, _s, _n in struct_roots}
    for key in gt.EMBEDDED:
        struct_by_key[key] = gt.pascal(key)
    for key in sorted(struct_by_key):
        name = struct_by_key[key]
        out.append(f"/// The `{key}` message as a struct; false (and `out` untouched) when the document does not satisfy the schema.")
        out.append(f"inline bool parse_{key}(const json::Value& value, {name}& out) {{")
        out.append(f"  if (!validate_{key}(value)) return false;")
        out.append(f"  {name} result{{}};")
        out.append("  take(value, result);")
        out.append("  out = std::move(result);")
        out.append("  return true;")
        out.append("}")
        out.append(f"inline std::string write_{key}(const {name}& value) {{")
        out.append("  json::Writer w;")
        out.append("  put(w, value);")
        out.append("  return w.str();")
        out.append("}")
        out.append("")
    out.append("/// Reads the document as the struct of the schema called `name` and writes it back (what the nodes do with a message they receive and one they send); false when it is not valid.")
    out.append("inline bool rewrite_message(std::string_view name, const json::Value& value, std::string& out) {")
    for key in sorted(struct_by_key):
        out.append(f"  if (name == {literal(key)}) {{ {struct_by_key[key]} message{{}}; if (!parse_{key}(value, message)) return false; out = write_{key}(message); return true; }}")
    out.append("  return false;")
    out.append("}")
    out.append("")
    out.append("}  // namespace armor::wire")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render_cpp()
    stale = []
    for path in OUTPUTS:
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        stale.append(str(path.relative_to(ROOT)))
        if not args.check:
            path.parent.mkdir(exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if args.check and stale:
        print("generated files are out of date:", ", ".join(stale), file=sys.stderr)
        return 1
    print("generated wire header is current" if args.check else "generated wire header written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
