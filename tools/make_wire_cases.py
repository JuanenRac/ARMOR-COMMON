#!/usr/bin/env python3
"""Write the seeded cases that the C++ readers of the messages are tested with, each with the verdict of the Python validator (the oracle).

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``conformance/wire_cases.tsv`` has one case per line: ``schema <TAB> 1 or 0 <TAB> the document as compact JSON``. The documents are the valid vectors of ``conformance/`` and, for each of
them, mutations that a seeded random generator makes: a member taken away, an unknown member added, a value of another type, a number on and just beyond its limits, a text of the longest
length and one longer, a value outside an enumeration, a list longer than allowed. The verdict is what ``armor_common.schema`` says, never what the C++ says, and the file is the same on
every run (``--check`` compares).

    python tools/make_wire_cases.py           # write conformance/wire_cases.tsv and conformance/wire_full_cases.tsv
    python tools/make_wire_cases.py --check   # fail when it is out of date
"""
from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from armor_common import schema as sc   # noqa: E402

SCHEMAS = ROOT / "src" / "armor_common" / "schemas"
OUT = ROOT / "conformance" / "wire_cases.tsv"
OUT_FULL = ROOT / "conformance" / "wire_full_cases.tsv"
FULL_VARIANTS = 4   # documents per message that hold every member the schema declares (the choices of an enumeration and of a number turn from one to the next)
SEED = 20261106
SEEDS_PER_SCHEMA = 5
MUTATIONS_PER_SCHEMA = 40
UNION_MUTATIONS = 12
LARGEST = 30000   # characters: the reader of a node bounds a document, so the cases stay inside the bound
ODD_TEXTS = ["", " ", "A", "é", "日本語", "\U0001F600", "x\n", "zone:", "-", "0", "a" * 200]


def schema_for(key: str) -> dict:
    return json.loads((SCHEMAS / f"{key}.schema.json").read_text(encoding="utf-8"))


def seeds_of(key: str) -> list[dict]:
    path = ROOT / "conformance" / f"{key}.json"
    if not path.exists():
        return []
    vectors = json.loads(path.read_text(encoding="utf-8")).get("vectors", [])
    out = []
    for vector in vectors:
        payload = vector.get("payload")
        if isinstance(payload, dict) and vector.get("valid") and len(json.dumps(payload)) < LARGEST // 4:
            out.append(payload)
    return out


def paths(node, prefix=()):
    """Every place inside the document: a tuple of keys and indexes."""
    yield prefix
    if isinstance(node, dict):
        for name, child in node.items():
            yield from paths(child, prefix + (name,))
    elif isinstance(node, list):
        for index, child in enumerate(node):
            yield from paths(child, prefix + (index,))


def get(node, path):
    for step in path:
        node = node[step]
    return node


def schema_at(root_schema: dict, path):
    node: dict | None = root_schema
    for step in path:
        if node is None:
            return None
        if isinstance(step, int):
            node = node.get("items") if isinstance(node.get("items"), dict) else None
        else:
            properties = node.get("properties", {})
            extra = node.get("additionalProperties")
            node = properties.get(step) if step in properties else (extra if isinstance(extra, dict) else None)
    return node


def mutate(doc: dict, root_schema: dict, rnd: random.Random) -> dict:
    out = copy.deepcopy(doc)
    where = rnd.choice(list(paths(out)))
    here = get(out, where)
    rule = schema_at(root_schema, where) or {}
    choice = rnd.randrange(9)
    if where and choice == 0:   # take a member away
        parent = get(out, where[:-1])
        if isinstance(parent, dict):
            del parent[where[-1]]
        elif isinstance(parent, list):
            del parent[where[-1]]
        return out
    if choice == 1 and isinstance(here, dict):   # an unknown member
        here[rnd.choice(["extra", "kind2", "x-y", "A"])] = rnd.choice([1, "s", True, None, [], {}])
        return out
    if choice == 2 and where:   # another type
        replacement: object = rnd.choice([None, True, 0, 1.5, "7", [], {}, "x"])
        parent = get(out, where[:-1])
        parent[where[-1]] = replacement
        return out
    if choice == 3 and isinstance(here, (int, float)) and not isinstance(here, bool) and where:   # on and beyond the limits
        options = [x for x in (rule.get("minimum"), rule.get("maximum")) if x is not None]
        options += [(rule["minimum"] - 1) if "minimum" in rule else -1, (rule["maximum"] + 1) if "maximum" in rule else 2 ** 40, 0.5, here + 1, here - 1]
        get(out, where[:-1])[where[-1]] = rnd.choice(options)
        return out
    if choice == 4 and isinstance(here, str) and where:   # lengths
        length = rule.get("maxLength")
        options = list(ODD_TEXTS)
        if length is not None:
            options += ["a" * length, "a" * (length + 1), "0" * length]
        minimum = rule.get("minLength")
        if minimum is not None:
            options += ["a" * minimum, "a" * max(minimum - 1, 0)]
        get(out, where[:-1])[where[-1]] = rnd.choice(options)
        return out
    if choice == 5 and isinstance(here, str) and where:   # a changed character
        position = rnd.randrange(len(here) + 1)
        get(out, where[:-1])[where[-1]] = here[:position] + rnd.choice("aZ0-_:./ \n") + here[position:]
        return out
    if choice == 6 and where and "enum" in rule:
        get(out, where[:-1])[where[-1]] = rnd.choice(["", "unknown", "ARM", 0, 1])
        return out
    if choice == 7 and isinstance(here, list) and here:   # too many items
        limit = rule.get("maxItems")
        copies = (limit + 1 - len(here)) if limit is not None else 1
        here.extend(copy.deepcopy(here[-1]) for _ in range(max(copies, 1)))
        return out
    if choice == 8 and isinstance(here, list) and where:   # an empty list
        get(out, where[:-1])[where[-1]] = []
        return out
    if choice == 8 and isinstance(here, bool) and where:
        get(out, where[:-1])[where[-1]] = not here
        return out
    return out


def union(first, second):
    """The two documents in one: every member that either of them has (a list is merged item by item, as far as both reach). The result carries the optional members that no single vector has
    all at once, so that the readers of the nested parts of a message are tried too; whether it is valid is the oracle's to say, as for every other case."""
    if isinstance(first, dict) and isinstance(second, dict):
        out = copy.deepcopy(first)
        for name, value in second.items():
            out[name] = union(out[name], value) if name in out else copy.deepcopy(value)
        return out
    if isinstance(first, list) and isinstance(second, list):
        merged = [union(a, b) for a, b in zip(first, second, strict=False)]
        return merged + copy.deepcopy(first[len(second):])
    return first


def verdict(key: str, root_schema: dict, doc) -> bool:
    try:
        sc.validate(doc, root_schema)
    except sc.SchemaError:
        return False
    return True


STRING_POOL = ["a", "ab", "node-1", "electrical-1", "0123456789abcdef", "abcdefgh", "12345678", "1.2.3", "0.8.0.7", "aa:bb:cc:dd:ee:ff", "192.168.0.10", "zone-1", "front-door", "https://example.org",
               "a/b", "00", "47", "5", "grid", "inverter", "hello world", "x1", "0", "-", "key", "1", "ab12", "a_b"]


def string_pool() -> list[str]:
    """The texts that a member may be given: a fixed list and every text the valid vectors of any message hold, so that a pattern of the contract finds one that fits."""
    found = set(STRING_POOL)
    for path in sorted((ROOT / "conformance").glob("*.json")):
        for vector in json.loads(path.read_text(encoding="utf-8")).get("vectors", []):
            stack = [vector.get("payload")]
            while stack:
                node = stack.pop()
                if isinstance(node, str) and 0 < len(node) <= 80:
                    found.add(node)
                elif isinstance(node, dict):
                    stack.extend(node.values())
                    found.update(name for name in node if 0 < len(name) <= 80)
                elif isinstance(node, list):
                    stack.extend(node)
    return list(STRING_POOL) + sorted(found - set(STRING_POOL))


def fits(value, node: dict) -> bool:
    try:
        sc.validate(value, node)
    except sc.SchemaError:
        return False
    return True


def full_value(node: dict, variant: int, pool: list[str], turn: list[int], parity: int | None = None, trail: str = ""):
    """A value that holds every member that the schema declares (and the first allowed value of what has no member), or None when none was found. ``variant`` and ``turn`` rotate the
    choices (an enumeration, a number, a text) so that the documents of the different variants reach the different branches of the readers. With a ``parity`` (0 or 1) about half of the optional
    members are left out, the half that the checksum of the place of the member in the document (``trail``) picks, so that the pair of documents of the two parities has each optional
    member present in one and absent in the other."""
    if "const" in node:
        return node["const"]
    if "enum" in node:
        turn[0] += 1
        values = node["enum"]
        for k in range(len(values)):
            candidate = values[(variant + turn[0] + k) % len(values)]
            if fits(candidate, node):
                return candidate
        return None
    kind = node.get("type")
    if kind == "boolean":
        return (variant + turn[0]) % 2 == 0
    if kind in ("integer", "number"):
        low, high = node.get("minimum"), node.get("maximum")
        options = []
        if low is not None and high is not None:
            options = [low, high, (low + high) // 2 if kind == "integer" else (low + high) / 2, low + 1 if low + 1 <= high else low]
        elif low is not None:
            options = [low, low + 1, low + 7, low + 100]
        elif high is not None:
            options = [high, high - 1, high - 7, 0 if high >= 0 else high]
        else:
            options = [1, 0, 7, 100]
        turn[0] += 1
        for k in range(len(options)):
            candidate = options[(variant + k) % len(options)]
            if kind == "integer":
                candidate = int(candidate)
            if fits(candidate, node):
                return candidate
        return None
    if kind == "string":
        turn[0] += 1
        shift = (variant * 7 + turn[0] * 3) % max(1, len(pool))
        order = pool[shift:] + pool[:shift]
        extra = ["x" * node["minLength"]] if node.get("minLength", 0) > 1 else []
        for candidate in extra + order:
            if fits(candidate, node):
                return candidate
        return None
    if kind == "array":
        count = max(node.get("minItems", 0), 1)
        if variant % 2 == 1 and node.get("maxItems", 2) >= 2:
            count = max(count, 2)
        items = node.get("items")
        out = []
        for _ in range(count):
            value = full_value(items, variant, pool, turn, parity, trail + "[]") if isinstance(items, dict) else None
            if value is None:
                return None
            out.append(value)
        return out if fits(out, node) else None
    if kind == "object":
        out = {}
        required = set(node.get("required", []))
        for name, child in node.get("properties", {}).items():
            if name not in required and parity is not None and zlib.crc32(f"{trail}/{name}".encode()) % 2 == parity:
                continue
            value = full_value(child, variant, pool, turn, parity, f"{trail}/{name}")
            if value is None:
                if name in required:
                    return None
                continue
            out[name] = value
        extra = node.get("additionalProperties")
        if isinstance(extra, dict):
            for key in pool:
                value = full_value(extra, variant, pool, turn, parity, trail + "/*")
                if value is None:
                    break
                if fits({key: value}, node):
                    out[key] = value
                    break
        return out if fits(out, node) else None
    return None


def render_full() -> str:
    """One document per variant for every message, each with every member of the schema (the members that no valid vector has among them): the host tests of the nodes read and write them back,
    which tries the readers and writers of the nested parts that the vectors never reach. The verdict is the oracle's as for every other case."""
    pool = string_pool()
    lines = []
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        key = path.name[: -len(".schema.json")]
        root_schema = schema_for(key)
        seen = set()
        for variant, parity in [(v, None) for v in range(FULL_VARIANTS)] + [(v, p) for v in (0, 1) for p in (0, 1)]:
            doc = full_value(root_schema, variant, pool, [0, 0], parity)
            if doc is None:
                continue
            text = json.dumps(doc, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
            if len(text) > LARGEST or text in seen or "\t" in text or "\n" in text:
                continue
            seen.add(text)
            lines.append(f"{key}\t{1 if verdict(key, root_schema, doc) else 0}\t{text}")
    return "\n".join(lines) + "\n"


def render() -> str:
    rnd = random.Random(SEED)
    lines = []
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        key = path.name[: -len(".schema.json")]
        root_schema = schema_for(key)
        seeds = seeds_of(key)
        everyone = list(seeds)
        rnd.shuffle(seeds)
        seeds = sorted(seeds[:SEEDS_PER_SCHEMA], key=lambda d: len(json.dumps(d)))
        documents = list(seeds)
        if seeds:
            for _ in range(MUTATIONS_PER_SCHEMA):
                documents.append(mutate(rnd.choice(seeds), root_schema, rnd))
        documents.append({})   # nothing at all is never a message
        if len(everyone) > 1:   # the vectors all in one document, and a few mutations of it: made apart from the random stream above, so that the older cases do not move
            everything = everyone[0]
            for other in everyone[1:]:
                everything = union(everything, other)
            documents.append(everything)
            apart = random.Random(f"{SEED}:{key}:union")
            documents.extend(mutate(everything, root_schema, apart) for _ in range(UNION_MUTATIONS))
        seen = set()
        for doc in documents:
            text = json.dumps(doc, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
            if len(text) > LARGEST or text in seen or "\t" in text or "\n" in text:
                continue
            seen.add(text)
            lines.append(f"{key}\t{1 if verdict(key, root_schema, doc) else 0}\t{text}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = False
    for target, content in ((OUT, render()), (OUT_FULL, render_full())):
        current = target.read_bytes().decode("utf-8") if target.exists() else None
        if current == content:
            print(f"{target.name} is current")
            continue
        if args.check:
            print(f"conformance/{target.name} is out of date", file=sys.stderr)
            stale = True
            continue
        target.write_bytes(content.encode("utf-8"))
        print(f"wrote {content.count(chr(10))} cases to {target.name}")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
