"""tools/release_firmware.py: what a release is made of, and what stops one from being published."""
from __future__ import annotations

import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "release_firmware.py"
spec = importlib.util.spec_from_file_location("release_firmware", TOOL)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

KEY = tool.public_key_in_firmware()


def image(project: str, version: str) -> bytes:
    """The start of an application image: the header, the first segment's header and the application description."""
    description = struct.pack("<I", tool.APP_DESCRIPTION_MAGIC) + b"\0" * 12 + version.encode().ljust(32, b"\0") + project.encode().ljust(32, b"\0")
    return bytes([0xE9]) + b"\0" * 23 + b"\0" * 8 + description + b"\0" * 400


def stub_signer(arguments: list[str]) -> str:
    if arguments == ["--public"]:
        return KEY
    return ("%02x" % (len(" ".join(arguments)) % 256)) * 64


class Project:
    def __init__(self, test: unittest.TestCase, name="ARMOR-RADAR", version="0.6.7"):
        self.dir = tempfile.TemporaryDirectory()
        test.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name) / name
        self.dist = self.root / "dist"
        self.dist.mkdir(parents=True)
        (self.root / "armor.project.json").write_text(json.dumps({"name": name, "version": version}), encoding="utf-8")
        self.kind, self.version = name.removeprefix("ARMOR-").lower(), version

    def build(self, board="s3-eth", mode="publica", project=None, version=None):
        (self.dist / f"armor-{self.kind}-{self.version}-{board}-{mode}-app.bin").write_bytes(image(project or f"armor_{self.kind}", version or self.version))
        (self.dist / f"armor-{self.kind}-{self.version}-{board}-{mode}-complete.bin").write_bytes(b"complete" * 50)


class PublicKeyTests(unittest.TestCase):
    def test_the_key_the_firmware_trusts_is_the_one_in_the_header(self):
        self.assertRegex(KEY, r"^[0-9a-f]{64}$")
        self.assertEqual(KEY, "664478b12a8799ab18970f58e974f14a6d0bf5623f0a22c65c3aaa32997054d2")


class ReleaseTests(unittest.TestCase):
    def test_every_board_gets_its_hash_and_both_signatures(self):
        project = Project(self)
        project.build("s3-eth")
        project.build("s3-wifi")
        out = project.root / "out"
        files = tool.build_release(project.root, project.dist, out, stub_signer)
        names = sorted(path.name for path in files)
        for board in ("s3-eth", "s3-wifi"):
            for suffix in ("", ".sha256", ".sig", ".sig2"):
                self.assertIn(f"armor_radar-{board}.bin{suffix}", names)
            self.assertIn(f"armor-radar-0.6.7-{board}-complete.bin", names)
        sums = (out / "armor_radar-s3-eth.bin.sha256").read_text(encoding="ascii")
        self.assertRegex(sums, r"^[0-9a-f]{64}  armor_radar-s3-eth\.bin\n$")
        self.assertRegex((out / "armor_radar-s3-eth.bin.sig2").read_text(encoding="ascii"), r"^[0-9a-f]{128}\n$")

    def test_the_manifest_that_is_signed_names_the_project_the_board_the_version_and_the_hash(self):
        project = Project(self)
        project.build("s3-wifi")
        asked: list[list[str]] = []

        def recording(arguments: list[str]) -> str:
            asked.append(arguments)
            return stub_signer(arguments)

        tool.build_release(project.root, project.dist, project.root / "out", recording)
        manifest = next(arguments for arguments in asked if arguments[0] == "--manifest")
        digest = tool.sha256_of(project.dist / "armor-radar-0.6.7-s3-wifi-publica-app.bin")
        self.assertEqual(manifest, ["--manifest", "armor_radar", "s3-wifi", "0.6.7", digest])
        self.assertIn(["--digest", digest], asked)

    def test_an_image_built_with_the_secret_of_a_fleet_is_never_published(self):
        project = Project(self)
        project.build("s3-eth")
        project.build("s3-eth", mode="local")
        with self.assertRaisesRegex(tool.ReleaseError, "secret of a fleet"):
            tool.build_release(project.root, project.dist, project.root / "out", stub_signer)

    def test_a_build_that_kept_the_secret_in_its_configuration_is_refused(self):
        project = Project(self)
        project.build("s3-eth")
        folder = project.root / ".compile" / "publica-s3-eth"
        folder.mkdir(parents=True)
        (folder / "sdkconfig").write_text('CONFIG_ARMOR_FLEET_SECRET="abc"\n', encoding="utf-8")
        with self.assertRaisesRegex(tool.ReleaseError, "CONFIG_ARMOR_FLEET_SECRET"):
            tool.build_release(project.root, project.dist, project.root / "out", stub_signer)

    def test_an_image_of_another_project_or_version_is_refused(self):
        project = Project(self)
        project.build("s3-eth", project="armor_solar")
        with self.assertRaisesRegex(tool.ReleaseError, "armor_solar"):
            tool.build_release(project.root, project.dist, project.root / "out", stub_signer)
        project.build("s3-eth", version="0.6.6")
        with self.assertRaisesRegex(tool.ReleaseError, "0.6.6"):
            tool.build_release(project.root, project.dist, project.root / "out", stub_signer)

    def test_a_key_that_is_not_the_one_the_firmware_trusts_is_refused(self):
        project = Project(self)
        project.build("s3-eth")
        with self.assertRaisesRegex(tool.ReleaseError, "not the one the firmware trusts"):
            tool.build_release(project.root, project.dist, project.root / "out", lambda arguments: "00" * 32 if arguments == ["--public"] else "aa" * 64)

    def test_a_signature_that_is_not_one_is_refused(self):
        project = Project(self)
        project.build("s3-eth")
        with self.assertRaisesRegex(tool.ReleaseError, "did not give a signature"):
            tool.build_release(project.root, project.dist, project.root / "out", lambda arguments: KEY if arguments == ["--public"] else "oops")

    def test_nothing_to_publish_is_said(self):
        project = Project(self)
        with self.assertRaisesRegex(tool.ReleaseError, "no public build"):
            tool.build_release(project.root, project.dist, project.root / "out", stub_signer)

    def test_a_file_that_is_not_an_image_is_refused(self):
        project = Project(self)
        (project.dist / "armor-radar-0.6.7-s3-eth-publica-app.bin").write_bytes(b"not firmware" * 40)
        with self.assertRaisesRegex(tool.ReleaseError, "not an ESP32 application image"):
            tool.build_release(project.root, project.dist, project.root / "out", stub_signer)


if __name__ == "__main__":
    unittest.main()
