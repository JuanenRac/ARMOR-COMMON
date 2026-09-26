#!/usr/bin/env python3
"""
*****************************************************************************
* A.R.M.O.R. - sync_firmware_base.py
* Keeps the part of the field-node firmware that the node projects share (the
* network, the settings store, the panel's server, the Bluetooth channel, the
* log, the certificate, the JSON reader...) identical in every one of them.
* Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
* GPL-3.0-or-later - see LICENSE
*****************************************************************************

The three node projects (ARMOR-RADAR, ARMOR-SOLAR, ARMOR-ELECTRICAL) grew from one base, and a fix made in one used to have to be made three times. The files
they share are kept here, once, in `firmware_base/`, with the name of the project written as placeholders; this tool writes them into every project that uses
them, and `check` says when a copy has drifted (a fix made in one project only). A project keeps its own copy in its own tree, so each builds on its own, exactly as
before: nothing is shared at build time.

    python tools/sync_firmware_base.py check     # exit 1 when a copy differs from the base (used by ARMOR-DOCS/tools/check_all.sh)
    python tools/sync_firmware_base.py sync      # write the base into every project that uses each file
    python tools/sync_firmware_base.py import    # (re)make the base from the projects' current files: what is identical in two or more of them becomes shared
    python tools/sync_firmware_base.py status    # which file goes where

The project's name appears in a shared file in four forms, each with a placeholder: ARMOR-SOLAR (@PROJECT@), armor-solar (@project-@), armor_solar (@project_@) and solar
(@kind@). A file that says something else in one project than in the others (a route of the panel, a topic of the broker) is not shared: it stays the project's own.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_DIR = HERE.parent / "firmware_base"
MANIFEST = BASE_DIR / "manifest.json"
ROOT = HERE.parent.parent                 # the folder that holds the ARMOR repositories

# project -> (ARMOR-X, armor-x, armor_x, x); the forms in this order become the placeholders below
PROJECTS = {
    "ARMOR-SOLAR": ("ARMOR-SOLAR", "armor-solar", "armor_solar", "solar"),
    "ARMOR-ELECTRICAL": ("ARMOR-ELECTRICAL", "armor-electrical", "armor_electrical", "electrical"),
    "ARMOR-RADAR": ("ARMOR-RADAR", "armor-radar", "armor_radar", "radar"),
}
PLACEHOLDERS = ("@PROJECT@", "@project-@", "@project_@", "@kind@")

# The files worth trying to share, by their place in ARMOR-SOLAR (a project keeps its `core/` under `main/core/` in ARMOR-RADAR).
CANDIDATES = [
    "main/board_ethernet.cpp", "main/board_ethernet.hpp", "main/entropy.cpp", "main/entropy.hpp", "main/log_buffer.cpp", "main/log_buffer.hpp",
    "main/mqtt_link.cpp", "main/mqtt_link.hpp", "main/network.cpp", "main/network.hpp", "main/node_store.cpp", "main/node_store.hpp",
    "main/tls_cert.cpp", "main/tls_cert.hpp", "main/web_server.cpp", "main/web_server.hpp", "main/ble_provision.cpp", "main/ble_provision.hpp",
    "main/api_shared.cpp", "main/api_shared.hpp", "main/Kconfig.projbuild",
    "core/auth.hpp", "core/net_text.hpp", "core/netplan.hpp", "core/node_id.hpp", "core/web_policy.hpp", "core/json.hpp", "core/ble_frame.hpp", "core/ble_dispatch.hpp",
    "core/board_s3.hpp",
    "panel/index.html", "panel/style.css", "tools/pack_panel.py", "tools/build_node.sh",
    "partitions.csv", "sdkconfig.defaults", "sdkconfig.board.s3-wifi", "sdkconfig.board.s3-eth",
]


def project_path(project: str, candidate: str) -> str:
    """Where a project keeps a candidate file: ARMOR-RADAR has its `core/` inside `main/`."""
    if project == "ARMOR-RADAR" and candidate.startswith("core/"):
        return "main/" + candidate
    return candidate


def to_base(text: str, project: str) -> str:
    """A project's file with its name turned into placeholders (line endings as LF)."""
    text = text.replace("\r\n", "\n")
    for form, placeholder in zip(PROJECTS[project], PLACEHOLDERS):
        text = text.replace(form, placeholder)
    return text


def from_base(text: str, project: str) -> str:
    for form, placeholder in zip(PROJECTS[project], PLACEHOLDERS):
        text = text.replace(placeholder, form)
    return text


def read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def write_like(path: Path, text: str) -> None:
    """Write `text` (LF) to `path`, keeping the file's own line endings (a Windows checkout has CRLF)."""
    crlf = path.exists() and b"\r\n" in path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"files": {}}


def do_import(root: Path) -> int:
    """Makes the base: a candidate that is identical (once the name is turned into placeholders) in two or more projects is shared by exactly those."""
    files: dict[str, dict[str, str]] = {}
    for candidate in CANDIDATES:
        found: dict[str, str] = {}
        for project in PROJECTS:
            path = root / project / project_path(project, candidate)
            if path.is_file():
                found[project] = to_base(read_text(path), project)
        groups: dict[str, list[str]] = {}
        for project, content in found.items():
            groups.setdefault(content, []).append(project)
        best = max(groups.items(), key=lambda item: (len(item[1]), "ARMOR-SOLAR" in item[1]), default=None)
        if best is None or len(best[1]) < 2:
            continue
        content, projects = best
        target = BASE_DIR / candidate
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode("utf-8"))
        files[candidate] = {"targets": {project: project_path(project, candidate) for project in PROJECTS if project in projects}}
    MANIFEST.write_text(json.dumps({"files": files}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for stale in sorted(p for p in BASE_DIR.rglob("*") if p.is_file() and p != MANIFEST and str(p.relative_to(BASE_DIR)).replace("\\", "/") not in files):
        print(f"not shared any more, left in place: {stale.relative_to(BASE_DIR)}")
    print(f"{len(files)} files shared ({sum(len(v['targets']) for v in files.values())} copies)")
    return 0


def drift(root: Path) -> list[str]:
    """The copies that differ from the base, as 'project: path'."""
    out: list[str] = []
    for candidate, entry in load_manifest()["files"].items():
        base = read_text(BASE_DIR / candidate).replace("\r\n", "\n")   # the base is LF whatever the editor did
        for project, relative in entry["targets"].items():
            path = root / project / relative
            if not path.is_file():
                out.append(f"{project}: {relative} is missing")
            elif read_text(path).replace("\r\n", "\n") != from_base(base, project):
                out.append(f"{project}: {relative} differs from the base")
    return out


def do_check(root: Path) -> int:
    problems = drift(root)
    for line in problems:
        print(line)
    manifest = load_manifest()["files"]
    if problems:
        print(f"FIRMWARE_BASE=FAIL {len(problems)} copies drifted (make the change in ARMOR-COMMON/firmware_base and run `sync`, or `import` to take the projects' files as they are)")
        return 1
    print(f"FIRMWARE_BASE=PASS {len(manifest)} shared files, {sum(len(v['targets']) for v in manifest.values())} copies identical to the base")
    return 0


def do_sync(root: Path) -> int:
    written = 0
    for candidate, entry in load_manifest()["files"].items():
        base = read_text(BASE_DIR / candidate).replace("\r\n", "\n")   # the base is LF whatever the editor did
        for project, relative in entry["targets"].items():
            path = root / project / relative
            wanted = from_base(base, project)
            if not path.is_file() or read_text(path).replace("\r\n", "\n") != wanted:
                write_like(path, wanted)
                written += 1
                print(f"written: {project}/{relative}")
    print(f"{written} copies written")
    return 0


def do_status() -> int:
    for candidate, entry in load_manifest()["files"].items():
        print(f"{candidate:32} {', '.join(p.removeprefix('ARMOR-') for p in entry['targets'])}")
    own = [c for c in CANDIDATES if c not in load_manifest()["files"]]
    print("\nnot shared (each project's own): " + ", ".join(own))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["check", "sync", "import", "status"])
    parser.add_argument("--root", type=Path, default=ROOT, help="the folder that holds the ARMOR repositories (default: the parent of ARMOR-COMMON)")
    args = parser.parse_args(argv)
    return {"check": lambda: do_check(args.root), "sync": lambda: do_sync(args.root), "import": lambda: do_import(args.root), "status": do_status}[args.command]()


if __name__ == "__main__":
    sys.exit(main())
