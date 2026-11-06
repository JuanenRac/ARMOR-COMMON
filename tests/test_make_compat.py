"""The compatibility feed (registry/compat.json) is what the registry and the pins give, is the same every time and holds nothing that changes when a version is cut."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("make_compat", ROOT / "tools" / "make_compat.py")
make_compat = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(make_compat)  # type: ignore[union-attr]


class CompatFeedTests(unittest.TestCase):
    def test_the_file_is_what_the_registry_and_the_pins_give(self):
        self.assertEqual((ROOT / "registry" / "compat.json").read_text(encoding="utf-8"), make_compat.render())
        self.assertEqual(make_compat.main(["--check"]), 0)

    def test_every_pinned_consumer_is_listed_once_with_its_pin(self):
        feed = json.loads(make_compat.render())
        pins = json.loads((ROOT / "registry" / "contract_pins.json").read_text(encoding="utf-8"))["consumers"]
        names = [item["name"] for item in feed["consumers"]]
        self.assertEqual(names, sorted(pins))
        for item in feed["consumers"]:
            self.assertEqual(item["checked_against"], pins[item["name"]])

    def test_the_field_nodes_are_marked_and_the_current_version_is_not_copied(self):
        feed = json.loads(make_compat.render())
        nodes = {item["name"] for item in feed["consumers"] if item["node"]}
        self.assertTrue({"ARMOR-NODE-RADAR", "ARMOR-NODE-SOLAR", "ARMOR-NODE-ELECTRICAL", "ARMOR-NODE-ALARM", "ARMOR-NODE-HMI"} <= nodes)
        self.assertNotIn("version", feed, "the current version of the contracts is read from the manifest: a version cut must not leave this file out of date")
        self.assertEqual(feed["contracts_manifest"], "armor.project.json")


if __name__ == "__main__":
    unittest.main()
