#!/usr/bin/env python3
"""Records which version of the contracts each consumer repository was last checked against (registry/contract_pins.json).

  python tools/contract_pins.py --check                 fail when a pin is malformed, unknown or above the version of this repository
  python tools/contract_pins.py --set ARMOR-SERVER ...  pin the named repositories to the current version (after a green reverse-dependency run)
  python tools/contract_pins.py --behind                list the consumers pinned below the current version
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = ROOT / "registry" / "contract_pins.json"
VERSION = re.compile(r"^\d+\.\d+\.\d+(\.\d+)?$")


def current() -> str:
    return json.loads((ROOT / "armor.project.json").read_text(encoding="utf-8"))["version"]


def key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def problems() -> list[str]:
    data = json.loads(PINS.read_text(encoding="utf-8"))
    known = {entry["name"] for entry in json.loads((ROOT / "registry" / "repositories.json").read_text(encoding="utf-8"))["repositories"]} - {"ARMOR-COMMON"}
    now = current()
    found = []
    for name, version in data["consumers"].items():
        if name not in known:
            found.append(f"{name} is not a consumer of the registry")
        elif not isinstance(version, str) or not VERSION.match(version):
            found.append(f"{name}: '{version}' is not a version")
        elif key(version) > key(now):
            found.append(f"{name}: pinned to {version}, above the current {now}")
    found += [f"{name} has no pin" for name in sorted(known - set(data["consumers"]))]
    return found


def main(argv: list[str]) -> int:
    if "--set" in argv:
        names = argv[argv.index("--set") + 1:]
        data = json.loads(PINS.read_text(encoding="utf-8"))
        for name in names:
            if name not in data["consumers"]:
                print(f"{name} is not a consumer", file=sys.stderr)
                return 2
            data["consumers"][name] = current()
        PINS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
        return 0
    if "--behind" in argv:
        data = json.loads(PINS.read_text(encoding="utf-8"))["consumers"]
        for name, version in sorted(data.items()):
            if key(version) < key(current()):
                print(f"{name} {version} < {current()}")
        return 0
    found = problems()
    for line in found:
        print(line, file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
