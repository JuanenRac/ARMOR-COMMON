"""The one list of the repositories of the family (registry/repositories.json) and the lists that other tools still keep for themselves: a repository named in one and forgotten in another is found here."""
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT.parent
REGISTRY = json.loads((ROOT / "registry" / "repositories.json").read_text(encoding="utf-8"))
REPOSITORIES = REGISTRY["repositories"]
NAMES = [entry["name"] for entry in REPOSITORIES]
NODES = {entry["name"] for entry in REPOSITORIES if entry["node"]}
KINDS = {"LIBRARY", "FIRMWARE", "SERVICE", "APP", "PROJECT", "TOOL", "HARDWARE", "DOCS"}
FIELDS = {"name", "kind", "group", "technologies", "node", "shared_tools", "studio_e2e", "contract_link", "map", "feeds", "component"}


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegistryShapeTests(unittest.TestCase):
    def test_every_entry_is_complete_and_names_are_unique(self):
        self.assertEqual(REGISTRY["schema_version"], "1.0")
        self.assertEqual(len(NAMES), len(set(NAMES)), "a repository twice in the registry")
        for entry in REPOSITORIES:
            with self.subTest(entry["name"]):
                self.assertTrue(re.fullmatch(r"ARMOR-[A-Z0-9]+(-[A-Z0-9]+)*", entry["name"]))
                self.assertLessEqual(set(entry), FIELDS)
                self.assertGreaterEqual(set(entry), FIELDS - {"component"})
                self.assertIn(entry["kind"], KINDS)
                self.assertTrue(entry["group"] and entry["group"] == entry["group"].upper())
                self.assertTrue(entry["technologies"] and all(isinstance(item, str) and item.strip() for item in entry["technologies"]))
                self.assertEqual(entry["map"].keys(), {"column", "row"})
                self.assertIn(entry["map"]["column"], range(len(REGISTRY["columns"])))
                for target in entry["feeds"]:
                    self.assertIn(target, NAMES, f"{entry['name']} feeds a repository that is not in the registry")

    def test_the_nodes_are_the_five_firmware_projects_and_no_two_repositories_share_a_place_on_the_map(self):
        self.assertEqual(NODES, {"ARMOR-NODE-ALARM", "ARMOR-NODE-ELECTRICAL", "ARMOR-NODE-HMI", "ARMOR-NODE-RADAR", "ARMOR-NODE-SOLAR"})
        self.assertTrue(all(entry["kind"] == "FIRMWARE" for entry in REPOSITORIES if entry["node"]))
        places = [(entry["map"]["column"], entry["map"]["row"]) for entry in REPOSITORIES]
        self.assertEqual(len(places), len(set(places)))

    def test_the_components_of_the_deployment_are_named_once(self):
        keys = [entry["component"] for entry in REPOSITORIES if "component" in entry]
        self.assertEqual(len(keys), len(set(keys)))


class ListsThatFollowTheRegistryTests(unittest.TestCase):
    def test_the_shared_project_tool_knows_the_same_nodes(self):
        tool = (ROOT / "tools" / "armor_project_tool.py").read_text(encoding="utf-8")
        listed = re.search(r"NODE_REPOSITORIES = \(([^)]*)\)", tool)
        self.assertEqual(set(re.findall(r'"(ARMOR-[A-Z-]+)"', listed.group(1))), NODES)

    def test_the_tool_that_shares_the_firmware_serves_the_same_nodes(self):
        self.assertEqual(set(load(ROOT / "tools" / "sync_firmware_base.py").PROJECTS), NODES)

    def test_the_workflow_template_fetches_the_same_nodes_to_compare_the_shared_firmware(self):
        template = (ROOT / "tools" / "ci.yml.template").read_text(encoding="utf-8")
        loop = re.search(r"for repository in ([A-Z -]+); do", template)
        self.assertIsNotNone(loop, "the template no longer fetches the nodes in a loop")
        self.assertEqual(set(loop.group(1).split()), NODES)

    def test_the_repositories_beside_this_one_say_the_same_thing_about_themselves(self):
        seen = 0
        for entry in REPOSITORIES:
            manifest = FAMILY / entry["name"] / "armor.project.json"
            if not manifest.is_file():
                continue
            seen += 1
            data = json.loads(manifest.read_text(encoding="utf-8"))
            with self.subTest(entry["name"]):
                self.assertEqual(data["name"], entry["name"])
                self.assertEqual(data["family"].upper(), entry["group"])
        if not seen:
            self.skipTest("no other repository is next to this one")


if __name__ == "__main__":
    unittest.main()
