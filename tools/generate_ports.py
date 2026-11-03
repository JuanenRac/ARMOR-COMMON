#!/usr/bin/env python3
"""Generate the port constants of the other languages from the one registry of ports.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

src/armor_common/ports.json is the single source of truth; the generated files must never be
edited by hand. ``--check`` fails when a generated file is out of date, which is how CI keeps
the clients honest.

    python tools/generate_ports.py           # write generated/
    python tools/generate_ports.py --check   # verify generated/ is current
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "armor_common" / "ports.json"
OUT = ROOT / "generated"
sys.path.insert(0, str(ROOT / "src"))
from armor_common.ports import check_registry  # noqa: E402

HEADER = "Generated from src/armor_common/ports.json by tools/generate_ports.py. Do not edit."


def _words(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def render(data: dict) -> dict[str, str]:
    ports = {name: int(entry["port"]) for name, entry in data["ports"].items()}
    ts = [f"/** {HEADER} */", "", "export const ARMOR_PORTS = {"] + [f"  {name}: {value}," for name, value in ports.items()] + ["} as const;", "",
          "export type ArmorPortName = keyof typeof ARMOR_PORTS;", ""]
    kt = [f"// {HEADER}", "package es.electrohobby3d.armor.contracts", "", "object ArmorPorts {"] + [f"    const val {name.upper()}: Int = {value}" for name, value in ports.items()] + ["}", ""]
    hpp = [f"// {HEADER}", "#pragma once", "", "namespace armor::ports {", ""] + [f"inline constexpr int k{_words(name)} = {value};" for name, value in ports.items()] + ["", "}  // namespace armor::ports", ""]
    env = [f"# {HEADER}"] + [f"ARMOR_PORT_{name.upper()}={value}" for name, value in ports.items()] + [""]
    return {"armor-ports.ts": "\n".join(ts), "ArmorPorts.kt": "\n".join(kt), "armor_ports.hpp": "\n".join(hpp), "armor-ports.env": "\n".join(env)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail when a generated file is out of date")
    args = parser.parse_args()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    problems = check_registry(data)
    if problems:
        print("ports.json is wrong: " + "; ".join(problems), file=sys.stderr)
        return 1
    stale = []
    for name, text in render(data).items():
        target = OUT / name
        if args.check:
            if not target.exists() or target.read_bytes() != text.encode("utf-8"):
                stale.append(name)
        else:
            target.write_bytes(text.encode("utf-8"))
    if stale:
        print("out of date (run tools/generate_ports.py): " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
