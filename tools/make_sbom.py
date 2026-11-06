#!/usr/bin/env python3
"""The software bill of materials of a Node.js project, in CycloneDX 1.5, read from its package-lock.json.

  python tools/make_sbom.py PROJECT_DIR                   print the bill of materials
  python tools/make_sbom.py PROJECT_DIR --output FILE     write it (an existing file is never overwritten)
  python tools/make_sbom.py PROJECT_DIR --check FILE      fail when FILE does not list exactly the packages of the lock file, with the same versions and hashes

The file is the same for the same lock file and manifest: it holds no time and no machine name, and its serial number is derived from the project and from the lock file, so that a person (or
the maintenance agent) can build it again and compare it with the one published with a release. It lists what the lock file names, each package with its version, its hash and its licence;
it is not a signature and proves nothing by itself about where a build came from.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import quote

SPEC_VERSION = "1.5"
HASH_NAMES = {"sha512": "SHA-512", "sha384": "SHA-384", "sha256": "SHA-256", "sha1": "SHA-1"}


class SbomError(ValueError):
    """The project cannot be described: nothing is written."""


def _purl(name: str, version: str) -> str:
    # an npm scope keeps its "@" in the name and the rest is percent-encoded as the package URL rules say
    if name.startswith("@") and "/" in name:
        scope, _, base = name.partition("/")
        return f"pkg:npm/%40{quote(scope[1:], safe='')}/{quote(base, safe='')}@{quote(version, safe='')}"
    return f"pkg:npm/{quote(name, safe='')}@{quote(version, safe='')}"


def _hash(integrity: Any) -> list[dict[str, str]]:
    if not isinstance(integrity, str):
        return []
    found = []
    for item in integrity.split():
        algorithm, _, encoded = item.partition("-")
        if algorithm in HASH_NAMES and encoded:
            try:
                digest = base64.b64decode(encoded, validate=True).hex()
            except ValueError:
                continue
            found.append({"alg": HASH_NAMES[algorithm], "content": digest})
    return found


def _licence(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, str) or not value.strip():
        return []
    text = value.strip()
    if any(mark in text for mark in (" ", "(", ")")):
        return [{"expression": text}]
    return [{"license": {"id": text}}]


def read_lock(project: Path) -> dict[str, Any]:
    lock = project / "package-lock.json"
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except OSError as error:
        raise SbomError(f"cannot read {lock}: {error}") from error
    except ValueError as error:
        raise SbomError(f"{lock} is not JSON: {error}") from error
    if not isinstance(data, dict) or not isinstance(data.get("packages"), dict):
        raise SbomError(f"{lock} has no 'packages' table (npm lock file version 2 or 3 is needed)")
    return data


def packages(lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The installed packages of a lock file by their package URL; linked workspaces and the root are not packages of the bill."""
    found: dict[str, dict[str, Any]] = {}
    for path, entry in lock["packages"].items():
        if not path or not isinstance(entry, dict) or entry.get("link"):
            continue
        name = path.rsplit("node_modules/", 1)[-1]
        version = entry.get("version")
        if not name or not isinstance(version, str) or "node_modules/" not in path:
            continue
        found[_purl(name, version)] = {"name": name, "version": version, "integrity": entry.get("integrity"), "license": entry.get("license"), "dev": bool(entry.get("dev"))}
    return found


def build(project: Path) -> dict[str, Any]:
    manifest_path = project / "armor.project.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        name, version = str(manifest["name"]), str(manifest["version"])
    except (OSError, ValueError, KeyError) as error:
        raise SbomError(f"cannot read the name and the version from {manifest_path}: {error}") from error
    lock = read_lock(project)
    lock_digest = hashlib.sha256((project / "package-lock.json").read_bytes()).hexdigest()
    components = []
    for purl, item in sorted(packages(lock).items()):
        component: dict[str, Any] = {"type": "library", "bom-ref": purl, "name": item["name"], "version": item["version"], "purl": purl}
        hashes = _hash(item["integrity"])
        if hashes:
            component["hashes"] = hashes
        licences = _licence(item["license"])
        if licences:
            component["licenses"] = licences
        component["scope"] = "optional" if item["dev"] else "required"
        components.append(component)
    return {
        "bomFormat": "CycloneDX",
        "specVersion": SPEC_VERSION,
        "serialNumber": "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"{name}@{version}#{lock_digest}")),
        "version": 1,
        "metadata": {"component": {"type": "application", "bom-ref": f"{name}@{version}", "name": name, "version": version}},
        "components": components,
    }


def check(project: Path, published: Path) -> list[str]:
    """The differences between a published bill of materials and the lock file of the project (empty when they agree)."""
    try:
        document = json.loads(published.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"cannot read {published}: {error}"]
    if not isinstance(document, dict) or document.get("bomFormat") != "CycloneDX" or not isinstance(document.get("components"), list):
        return [f"{published.name} is not a CycloneDX bill of materials"]
    expected = {component["purl"]: component for component in build(project)["components"]}
    listed = {str(component.get("purl")): component for component in document["components"] if isinstance(component, dict)}
    problems = [f"missing from the bill: {purl}" for purl in sorted(set(expected) - set(listed))]
    problems += [f"not in the lock file: {purl}" for purl in sorted(set(listed) - set(expected))]
    for purl in sorted(set(expected) & set(listed)):
        if listed[purl].get("hashes") != expected[purl].get("hashes"):
            problems.append(f"the hash of {purl} differs from the lock file")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path, metavar="FILE")
    parser.add_argument("--check", type=Path, metavar="FILE")
    args = parser.parse_args(argv)
    try:
        if args.check:
            problems = check(args.project, args.check)
            for problem in problems:
                print("FAIL", problem)
            print(f"SBOM={'FAIL' if problems else 'PASS'}")
            return 1 if problems else 0
        text = json.dumps(build(args.project), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.output:
            try:
                with args.output.open("x", encoding="utf-8", newline="\n") as handle:
                    handle.write(text)
            except FileExistsError:
                raise SbomError(f"{args.output} already exists: give another name, nothing is overwritten") from None
            except OSError as error:
                raise SbomError(f"cannot write {args.output}: {error}") from error
        else:
            sys.stdout.write(text)
    except SbomError as error:
        print(f"make_sbom: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
