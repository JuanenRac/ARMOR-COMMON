"""The HTTP contract of ARMOR-SERVER (openapi/armor-server.yaml) is a document a machine can read, and it says what the server answers.

These checks need PyYAML and openapi-spec-validator (``pip install -e .[contract-tests]``); CI installs them, and a machine without them skips the file instead of failing it.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import yaml
    from openapi_spec_validator import validate as validate_spec
except ModuleNotFoundError:   # pragma: no cover - the optional tools are not installed
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "openapi" / "armor-server.yaml"
METHODS = {"get", "put", "post", "delete", "patch", "head", "options"}


@unittest.skipIf(yaml is None, "PyYAML and openapi-spec-validator are not installed (pip install -e .[contract-tests])")
class OpenApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))

    def test_it_is_a_valid_openapi_document(self):
        validate_spec(self.document)

    def test_its_version_is_the_one_of_this_repository(self):
        manifest = json.loads((ROOT / "armor.project.json").read_text(encoding="utf-8"))
        self.assertEqual(self.document["info"]["version"], manifest["version"])

    def test_a_description_is_never_split_into_keys_by_a_comma(self):
        def walk(node, trail=""):
            if isinstance(node, dict):
                for key, value in node.items():
                    if value is None and isinstance(key, str) and (" " in key or len(key) > 40):
                        self.fail(f"{trail}/{key[:50]} looks like the rest of a description cut at a comma")
                    walk(value, f"{trail}/{key}")
            elif isinstance(node, list):
                for number, value in enumerate(node):
                    walk(value, f"{trail}[{number}]")
        walk(self.document)

    def test_every_operation_says_what_it_answers(self):
        for route, item in self.document["paths"].items():
            for method, operation in item.items():
                if method in METHODS:
                    self.assertTrue(operation.get("responses"), f"{method.upper()} {route} has no responses")

    def test_the_removal_of_history_is_on_the_history_and_asks_for_an_administrator(self):
        self.assertIn("delete", self.document["paths"]["/api/v1/history"])
        self.assertNotIn("delete", self.document["paths"]["/api/v1/camera-status"])
        self.assertIn("administrator", self.document["paths"]["/api/v1/history"]["delete"]["summary"])

    def test_the_messages_the_nodes_post_name_their_schema(self):
        for route, schema in (("/api/v1/telemetry", "telemetry"), ("/api/v1/health", "health"), ("/api/v1/alarm/state", "alarm"), ("/api/v1/network/state", "network")):
            body = self.document["paths"][route]["post"]["requestBody"]["content"]["application/json"]["schema"]
            self.assertTrue(body["$ref"].endswith(f"/{schema}.schema.json"), route)
            self.assertTrue((OPENAPI.parent / body["$ref"]).resolve().is_file(), route)


if __name__ == "__main__":
    unittest.main()
