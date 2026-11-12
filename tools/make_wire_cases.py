#!/usr/bin/env python3
"""Write the seeded cases that the C++ readers of the messages are tested with, each with the verdict of the Python validator (the oracle).

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``conformance/wire_cases.tsv`` has one case per line: ``schema <TAB> 1 or 0 <TAB> the document as compact JSON``. The documents are the valid vectors of ``conformance/`` and, for each of
them, mutations that a seeded random generator makes: a member taken away, an unknown member added, a value of another type, a number on and just beyond its limits, a text of the longest
length and one longer, a value outside an enumeration, a list longer than allowed. The verdict is what ``armor_common.schema`` says, never what the C++ says, and the file is the same on
every run (``--check`` compares).

    python tools/make_wire_cases.py           # write conformance/wire_cases.tsv
    python tools/make_wire_cases.py --check   # fail when it is out of date
"""
from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from armor_common import schema as sc   # noqa: E402

SCHEMAS = ROOT / "src" / "armor_common" / "schemas"
OUT = ROOT / "conformance" / "wire_cases.tsv"
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
    content = render()
    current = OUT.read_bytes().decode("utf-8") if OUT.exists() else None
    if current == content:
        print("wire cases are current")
        return 0
    if args.check:
        print("conformance/wire_cases.tsv is out of date", file=sys.stderr)
        return 1
    OUT.write_bytes(content.encode("utf-8"))
    print(f"wrote {content.count(chr(10))} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
