"""The version of the contracts a repository says it was checked against (in its information message and, for the server, in /api/v1/info) is the pin of the reverse-dependency run.

The repositories that declare it hold one constant: ARMOR-SERVER in src/contract_version.ts and every field node in main/contract_version.hpp. This test reads the constant of each
sibling checkout that has it and compares it with registry/contract_pins.json, so a pin cannot move (after a green run) without the repository saying so, and a repository cannot
claim a version nobody checked. A sibling that is not there is skipped unless ARMOR_REQUIRE_SIBLINGS is set; one that has no constant yet is not declaring anything.
"""
import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINS = json.loads((ROOT / "registry" / "contract_pins.json").read_text(encoding="utf-8"))["consumers"]
DECLARATIONS = {
    "ARMOR-SERVER": ("src/contract_version.ts", re.compile(r'CONTRACT_VERSION\s*=\s*"([0-9.]+)"')),
    **{f"ARMOR-NODE-{kind}": ("main/contract_version.hpp", re.compile(r'kContractVersion\s*=\s*"([0-9.]+)"')) for kind in ("RADAR", "SOLAR", "ELECTRICAL", "ALARM", "HMI")},
}
VERSION = re.compile(r"^\d+\.\d+\.\d+(\.\d+)?$")


class DeclaredContracts(unittest.TestCase):
    def test_every_declaration_is_the_pin_of_its_repository(self):
        required = os.environ.get("ARMOR_REQUIRE_SIBLINGS") == "1"
        found = 0
        for name, (relative, pattern) in sorted(DECLARATIONS.items()):
            sibling = ROOT.parent / name
            if not sibling.is_dir():
                self.assertFalse(required, f"{name} must be next to this repository when ARMOR_REQUIRE_SIBLINGS is set")
                continue
            file = sibling / relative
            if not file.is_file():
                continue
            match = pattern.search(file.read_text(encoding="utf-8"))
            self.assertIsNotNone(match, f"{name}/{relative} holds no version")
            declared = match.group(1)  # type: ignore[union-attr]
            self.assertRegex(declared, VERSION, name)
            self.assertEqual(declared, PINS[name], f"{name} declares {declared} but its pin is {PINS[name]}: move the pin or the declaration")
            found += 1
        self.assertGreaterEqual(found, 0)

    def test_the_declaring_repositories_are_consumers_with_a_pin(self):
        for name in DECLARATIONS:
            self.assertIn(name, PINS)


if __name__ == "__main__":
    unittest.main()
