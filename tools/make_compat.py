#!/usr/bin/env python3
"""Writes registry/compat.json: the one file a page about compatibility reads (the dashboard of the organisation reads it from the repository, nothing is served).

For each repository that consumes the contracts it says what kind of repository it is, whether it is a field node, who it feeds and the version of the contracts it was last checked against
(registry/contract_pins.json, moved only after a green reverse-dependency run). The version of the contracts that is current is the one in armor.project.json, which the page reads next to this
file; it is not copied here so that cutting a version never makes this file out of date. Sorted, no time, no machine: the same inputs give the same bytes.

  python tools/make_compat.py            write registry/compat.json
  python tools/make_compat.py --check    fail when the file is not what the registry and the pins give today
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "repositories.json"
PINS = ROOT / "registry" / "contract_pins.json"
OUT = ROOT / "registry" / "compat.json"


def build() -> dict[str, object]:
    repositories = {entry["name"]: entry for entry in json.loads(REGISTRY.read_text(encoding="utf-8"))["repositories"]}
    pins = json.loads(PINS.read_text(encoding="utf-8"))["consumers"]
    consumers = []
    for name in sorted(pins):
        entry = repositories.get(name, {})
        consumers.append({
            "name": name,
            "kind": entry.get("kind", ""),
            "node": bool(entry.get("node", False)),
            "feeds": sorted(entry.get("feeds", [])),
            "checked_against": pins[name],
        })
    return {
        "schema_version": "1.0",
        "about": "The version of the contracts (ARMOR-COMMON) each consumer was last checked against. The current version of the contracts is the version of armor.project.json of this repository. Written by tools/make_compat.py.",
        "contracts_manifest": "armor.project.json",
        "consumers": consumers,
    }


def render() -> str:
    return json.dumps(build(), indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            print("registry/compat.json is not what the registry and the pins give: run tools/make_compat.py", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
