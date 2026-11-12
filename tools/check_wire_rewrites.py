#!/usr/bin/env python3
"""Compare what the C++ writers wrote back with the documents they read.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``host_tests/test_wire_oracle`` reads each valid case into its struct and writes it again (``rewrites.tsv``). A reader keeps only the members the schema names, so the text it writes
must equal the original document without the members the schema does not name, value by value.

    python tools/check_wire_rewrites.py <rewrites.tsv>
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "src" / "armor_common" / "schemas"
CASES = ROOT / "conformance" / "wire_cases.tsv"


def known_only(value, schema):
    """The document without the members its schema does not name (those the schema leaves free are dropped by a reader)."""
    if isinstance(value, dict) and isinstance(schema, dict):
        properties = schema.get("properties", {})
        extra = schema.get("additionalProperties")
        out = {}
        for name, child in value.items():
            if name in properties:
                out[name] = known_only(child, properties[name])
            elif isinstance(extra, dict):
                out[name] = known_only(child, extra)
        return out
    if isinstance(value, list) and isinstance(schema, dict) and isinstance(schema.get("items"), dict):
        return [known_only(child, schema["items"]) for child in value]
    return value


def same_value(left, right) -> bool:
    """Equal documents; two numbers are equal when they agree to 12 digits (the writer of a node prints a number with fewer digits than a double can carry: 3.3249999999999997 comes back as 3.325)."""
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(same_value(left[name], right[name]) for name in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(same_value(a, b) for a, b in zip(left, right, strict=True))
    if isinstance(left, (int, float)) and isinstance(right, (int, float)) and not isinstance(left, bool) and not isinstance(right, bool):
        return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)
    return left == right and type(left) is type(right)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    cases = CASES.read_bytes().decode("utf-8").splitlines()
    problems = 0
    checked = 0
    for line in Path(argv[1]).read_bytes().decode("utf-8").splitlines():
        key, number, text = line.split("\t", 2)
        original = json.loads(cases[int(number) - 1].split("\t", 2)[2])
        schema = json.loads((SCHEMAS / f"{key}.schema.json").read_text(encoding="utf-8"))
        wanted = known_only(original, schema)
        got = json.loads(text)
        checked += 1
        if not same_value(got, wanted):
            problems += 1
            if problems <= 10:
                print(f"case {number} ({key}): written back differently\n  wanted {json.dumps(wanted)[:300]}\n  got    {text[:300]}", file=sys.stderr)
    print(f"{checked} rewrites compared, {problems} differ")
    return 1 if problems or checked < 100 else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
