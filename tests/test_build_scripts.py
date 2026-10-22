"""The build scripts of the nodes never produce a public image that holds the secret of a fleet: the universal image is built without it unless it is asked for, and then it is named *-local."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES = ("ARMOR-RADAR", "ARMOR-SOLAR", "ARMOR-ELECTRICAL", "ARMOR-ALARM", "ARMOR-HMI")


def scripts() -> dict[str, str]:
    found = {"firmware_base": (ROOT / "firmware_base" / "tools" / "build_node.sh").read_text(encoding="utf-8")}
    for node in NODES:
        path = ROOT.parent / node / "tools" / "build_node.sh"
        if path.is_file():
            found[node] = path.read_text(encoding="utf-8")
    return found


class BuildScriptTests(unittest.TestCase):
    def test_the_fleet_secret_goes_in_only_when_asked_for_and_the_image_is_then_a_local_one(self):
        for name, text in scripts().items():
            with self.subTest(script=name):
                self.assertNotRegex(text, r'\[\[ -f "\$ROOT/secrets/generic\.conf" \]\] && DEFAULTS=', "the secret must not be added just because the file exists")
                self.assertIn('ARMOR_WITH_FLEET_SECRET:-0}" == "1"', text)
                self.assertIn('IMAGE="$NODE-$BOARD-local"', text)
                self.assertIn("never publish it", text)

    def test_the_result_of_a_public_build_is_read_for_a_secret_before_it_is_accepted(self):
        for name, text in scripts().items():
            with self.subTest(script=name):
                self.assertRegex(text, r"CONFIG_ARMOR_\(FLEET_SECRET\|SETUP_CODE\)=")
                self.assertIn("REFUSED:", text)
                self.assertLess(text.index("REFUSED:"), text.index('ls -l "$ROOT/dist/$IMAGE.bin"'), "the check comes before the image is reported as ready")

    def test_the_option_that_puts_a_secret_in_an_image_says_it_must_not_be_published(self):
        kconfig = (ROOT / "firmware_base" / "main" / "Kconfig.projbuild").read_text(encoding="utf-8")
        self.assertIn("Never publish such an image", kconfig)


if __name__ == "__main__":
    unittest.main()
