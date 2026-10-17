#!/usr/bin/env python3
"""
*****************************************************************************
* A.R.M.O.R. - release_firmware.py
* Turns the images a node project has built into the files of a GitHub
* release: the application image of each board with its SHA-256 and its two
* signatures, and the complete image for flashing by cable.
* Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
* GPL-3.0-or-later - see LICENSE
*****************************************************************************

    python tools/release_firmware.py ARMOR-RADAR                 # reads ../ARMOR-RADAR/dist, writes ../ARMOR-RADAR/dist/release-<version>/
    python tools/release_firmware.py ARMOR-RADAR --dist DIR --out DIR --signer "node tools/firmware_sign.mjs"

For each board it finds ``armor-<kind>-<version>-<board>-publica-app.bin`` (the image built WITHOUT the secret of a fleet; the one built with it, ``-local-``, is refused) and writes

    armor_<kind>-<board>.bin          the application image (what the nodes download and install)
    armor_<kind>-<board>.bin.sha256   its SHA-256
    armor_<kind>-<board>.bin.sig      the signature of the hash alone (for the nodes from before the manifest check)
    armor_<kind>-<board>.bin.sig2     the signature of ``armor-fw/1|<project>|<board>|<version>|<sha256>`` (what the nodes check now)
    armor-<kind>-<version>-<board>-complete.bin(.sha256)   the whole flash image (bootloader, partition table, application), for a cable

Before it writes anything it checks that the image says it is the project and the version it is asked for (it reads them from the image itself), that the build had no fleet secret, that the
version is the one in the project's manifest, and that the key that signs is the one the firmware trusts (``firmware_base/core/fw_trust.hpp``). The key itself is never read here: the
signer (``tools/firmware_sign.mjs``) reads it from ARMOR_FIRMWARE_KEY or ~/.armor/firmware_ed25519.pem, and it is never copied into a repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # ARMOR-COMMON
REPOSITORIES = ROOT.parent              # the folder that holds the ARMOR repositories
TRUST = ROOT / "firmware_base" / "core" / "fw_trust.hpp"
BOARDS = ("s3-eth", "s3-wifi", "lcd7box")
KINDS = ("radar", "solar", "electrical", "alarm", "hmi")
APP_DESCRIPTION_AT = 32                 # after the image header (24 bytes) and the header of the first segment (8)
APP_DESCRIPTION_MAGIC = 0xABCD5432


class ReleaseError(RuntimeError):
    """Something that must be right before an image is published is not."""


def public_key_in_firmware(text: str | None = None) -> str:
    """The public key the firmware trusts, as 64 hexadecimal digits, read from fw_trust.hpp."""
    source = text if text is not None else TRUST.read_text(encoding="utf-8")
    match = re.search(r"kPublicKey\[32\]\s*=\s*\{([^}]*)\}", source)
    if not match:
        raise ReleaseError("fw_trust.hpp has no kPublicKey")
    values = [int(item, 16) for item in re.findall(r"0x([0-9a-fA-F]{2})", match.group(1))]
    if len(values) != 32:
        raise ReleaseError("the public key in fw_trust.hpp is not 32 bytes")
    return bytes(values).hex()


def describe_image(path: Path) -> tuple[str, str]:
    """The project name and the version an application image says about itself (its ``esp_app_desc_t``)."""
    data = path.read_bytes()[: APP_DESCRIPTION_AT + 96]
    if len(data) < APP_DESCRIPTION_AT + 80 or data[0] != 0xE9:
        raise ReleaseError(f"{path.name} is not an ESP32 application image")
    magic = struct.unpack_from("<I", data, APP_DESCRIPTION_AT)[0]
    if magic != APP_DESCRIPTION_MAGIC:
        raise ReleaseError(f"{path.name} has no application description")
    version = data[APP_DESCRIPTION_AT + 16: APP_DESCRIPTION_AT + 48].split(b"\0", 1)[0].decode("ascii", "replace")
    project = data[APP_DESCRIPTION_AT + 48: APP_DESCRIPTION_AT + 80].split(b"\0", 1)[0].decode("ascii", "replace")
    return project, version


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def default_signer(arguments: list[str]) -> str:
    command = ["node", str(HERE / "firmware_sign.mjs"), *arguments]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ReleaseError("the signer failed: " + (result.stderr.strip() or result.stdout.strip())[:300])
    return result.stdout.strip()


def make_signer(command: str | None) -> Callable[[list[str]], str]:
    if not command:
        return default_signer
    base = shlex.split(command)

    def signer(arguments: list[str]) -> str:
        result = subprocess.run([*base, *arguments], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise ReleaseError("the signer failed: " + (result.stderr.strip() or result.stdout.strip())[:300])
        return result.stdout.strip()

    return signer


def check_signature_text(text: str, what: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{128}", text):
        raise ReleaseError(f"the signer did not give a signature for {what}")
    return text


def check_build_had_no_secret(project: Path, mode: str, board: str) -> None:
    """The build folder keeps the configuration the image was built with: a fleet secret or a setup code in it means the image holds them."""
    sdkconfig = project / ".compile" / f"{mode}-{board}" / "sdkconfig"
    if not sdkconfig.is_file():
        return
    for name in ("CONFIG_ARMOR_FLEET_SECRET", "CONFIG_ARMOR_SETUP_CODE"):
        match = re.search(rf'^{name}="([^"]*)"', sdkconfig.read_text(encoding="utf-8", errors="replace"), flags=re.M)
        if match and match.group(1):
            raise ReleaseError(f"the build of {board} was made with {name}: an image like that would give the secret to whoever downloads it")


def build_release(project: Path, dist: Path, out: Path, signer: Callable[[list[str]], str], trusted_key: str | None = None) -> list[Path]:
    """Write the release files of every board that has a public build of the project's current version. Returns the files written."""
    manifest = json.loads((project / "armor.project.json").read_text(encoding="utf-8"))
    name, version = str(manifest["name"]), str(manifest["version"])
    kind = name.removeprefix("ARMOR-").lower()
    if kind not in KINDS:
        raise ReleaseError(f"{name} is not a node project")
    expected_project = f"armor_{kind}"
    key = trusted_key if trusted_key is not None else public_key_in_firmware()
    if signer(["--public"]).lower() != key:
        raise ReleaseError("the key that would sign is not the one the firmware trusts (fw_trust.hpp): a node would refuse every file")
    if not dist.is_dir():
        raise ReleaseError(f"{dist} does not exist")
    local = sorted(path.name for path in dist.glob(f"armor-{kind}-{version}-*-local-*"))
    if local:
        raise ReleaseError("a build made with the secret of a fleet is in the folder and is not published: " + ", ".join(local))
    boards = [board for board in BOARDS if (dist / f"armor-{kind}-{version}-{board}-publica-app.bin").is_file()]
    if not boards:
        raise ReleaseError(f"there is no public build of {name} {version} in {dist} (armor-{kind}-{version}-<board>-publica-app.bin)")
    written: list[Path] = []
    out.mkdir(parents=True, exist_ok=True)
    for board in boards:
        image = dist / f"armor-{kind}-{version}-{board}-publica-app.bin"
        check_build_had_no_secret(project, "publica", board)
        described_project, described_version = describe_image(image)
        if described_project != expected_project:
            raise ReleaseError(f"{image.name} says it is {described_project}, not {expected_project}")
        if described_version != version:
            raise ReleaseError(f"{image.name} says it is version {described_version}; the manifest says {version}: build again after the bump")
        digest = sha256_of(image)
        asset = out / f"{expected_project}-{board}.bin"
        shutil.copyfile(image, asset)
        (out / (asset.name + ".sha256")).write_text(f"{digest}  {asset.name}\n", encoding="ascii", newline="\n")
        (out / (asset.name + ".sig")).write_text(check_signature_text(signer(["--digest", digest]), "the hash") + "\n", encoding="ascii", newline="\n")
        (out / (asset.name + ".sig2")).write_text(check_signature_text(signer(["--manifest", expected_project, board, version, digest]), "the manifest") + "\n", encoding="ascii", newline="\n")
        written += [asset, out / (asset.name + ".sha256"), out / (asset.name + ".sig"), out / (asset.name + ".sig2")]
        complete = dist / f"armor-{kind}-{version}-{board}-publica-complete.bin"
        if complete.is_file():
            target = out / f"armor-{kind}-{version}-{board}-complete.bin"
            shutil.copyfile(complete, target)
            (out / (target.name + ".sha256")).write_text(f"{sha256_of(target)}  {target.name}\n", encoding="ascii", newline="\n")
            written += [target, out / (target.name + ".sha256")]
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", help="the node project, e.g. ARMOR-RADAR")
    parser.add_argument("--dist", type=Path, help="the folder with the built images (default: <project>/dist)")
    parser.add_argument("--out", type=Path, help="where the release files are written (default: <dist>/release-<version>)")
    parser.add_argument("--signer", help='the command that signs (default: node tools/firmware_sign.mjs); it is given "--public", "--digest <hash>" or "--manifest <project> <board> <version> <hash>"')
    args = parser.parse_args(argv)
    project = REPOSITORIES / args.project
    if not (project / "armor.project.json").is_file():
        print(f"RELEASE_FIRMWARE=FAIL {project} is not a project", file=sys.stderr)
        return 2
    version = json.loads((project / "armor.project.json").read_text(encoding="utf-8"))["version"]
    dist = args.dist or project / "dist"
    out = args.out or dist / f"release-{version}"
    try:
        files = build_release(project, dist, out, make_signer(args.signer))
    except ReleaseError as error:
        print(f"RELEASE_FIRMWARE=FAIL {error}", file=sys.stderr)
        return 1
    for path in files:
        print(path)
    print(f"RELEASE_FIRMWARE=PASS {args.project} {version}: {len(files)} files in {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
