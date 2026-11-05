#!/usr/bin/env python3
"""
*****************************************************************************
* A.R.M.O.R. - sync_motion_core.py
* Keeps the movement model of the observation services (src/armor_common/
* motion_core.py) identical in ARMOR-SERVER-AI and ARMOR-VISION.
* Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
* GPL-3.0-or-later - see LICENSE
*****************************************************************************

The two services decide movement with the same code. It is written once, here, and copied into each service (a service builds on its own and fetches nothing at run time):

    python tools/sync_motion_core.py check     # exit 1 when a copy that is next to this repository differs from the original
    python tools/sync_motion_core.py sync      # write the original into every service that is next to this repository

A service that is not checked out next to this repository is skipped with a note.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "src" / "armor_common" / "motion_core.py"
ROOT = HERE.parent.parent
TARGETS = {
    "ARMOR-SERVER-AI": "src/armor_server_ai/motion_core.py",
    "ARMOR-VISION": "src/armor_vision/motion_core.py",
}


def normalised(path: Path) -> str:
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def drift(root: Path = ROOT) -> tuple[list[str], list[str]]:
    """(the copies that differ or are missing, the services that are not next to this repository)."""
    wanted = normalised(SOURCE)
    problems: list[str] = []
    absent: list[str] = []
    for project, relative in TARGETS.items():
        if not (root / project).is_dir():
            absent.append(project)
        elif not (root / project / relative).is_file():
            problems.append(f"{project}: {relative} is missing")
        elif normalised(root / project / relative) != wanted:
            problems.append(f"{project}: {relative} differs from the original")
    return problems, absent


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else "check"
    if command == "sync":
        wanted = normalised(SOURCE)
        for project, relative in TARGETS.items():
            if (ROOT / project).is_dir():
                path = ROOT / project / relative
                crlf = path.exists() and b"\r\n" in path.read_bytes()
                path.write_bytes((wanted.replace("\n", "\r\n") if crlf else wanted).encode("utf-8"))
                print(f"written: {project}/{relative}")
        return 0
    if command != "check":
        print("usage: sync_motion_core.py check|sync")
        return 2
    problems, absent = drift()
    for line in problems:
        print(line)
    for project in absent:
        print(f"skipped, not next to this repository: {project}")
    if problems:
        print(f"MOTION_CORE=FAIL {len(problems)} copies drifted (change src/armor_common/motion_core.py and run `sync`)")
        return 1
    print(f"MOTION_CORE=PASS {len(TARGETS) - len(absent)} copies identical to the original")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
