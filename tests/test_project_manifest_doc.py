import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = (ROOT / "docs" / "PROJECT_MANIFEST.md").read_text(encoding="utf-8")


def required_keys() -> tuple[str, ...]:
    """The keys every repository's CI check demands, read from the vendored tool without importing it."""
    source = (ROOT / "tools" / "armor_ci_validate.py").read_text(encoding="utf-8")
    block = re.search(r"REQUIRED_MANIFEST_KEYS = \((.*?)\)", source, re.S)
    return tuple(re.findall(r'"([a-z_]+)"', block.group(1)))


class ProjectManifestDocumentation(unittest.TestCase):
    def test_every_required_key_is_described(self):
        for key in required_keys():
            self.assertIn(f"`{key}`", DOC, key)

    def test_the_optional_keys_are_described(self):
        for key in ("requires", "service", "deployment_target_note"):
            self.assertIn(f"`{key}`", DOC, key)

    def test_this_repository_manifest_is_valid_without_the_optional_requires(self):
        manifest = json.loads((ROOT / "armor.project.json").read_text(encoding="utf-8"))
        self.assertTrue(set(required_keys()) <= set(manifest))
        self.assertNotIn("requires", manifest)   # COMMON is what the others require, it requires nothing


if __name__ == "__main__":
    unittest.main()
