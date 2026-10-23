"""The generated TypeScript and Kotlin types: fixed values are literals, no object is left as an anonymous map, and Kotlin does not meet a reserved word."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KOTLIN = (ROOT / "generated" / "ArmorContracts.kt").read_text(encoding="utf-8")
TYPESCRIPT = (ROOT / "generated" / "armor-contracts.ts").read_text(encoding="utf-8")
HARD_KEYWORDS = {"as", "break", "class", "continue", "do", "else", "false", "for", "fun", "if", "in", "interface", "is", "null", "object", "package", "return", "super", "this", "throw", "true", "try",
                 "typealias", "typeof", "val", "var", "when", "while"}


class GeneratedTypesTests(unittest.TestCase):
    def test_kotlin_does_not_use_a_reserved_word_as_a_name(self):
        for name in re.findall(r"^\s+val (`?)([A-Za-z_][A-Za-z0-9_]*)\1:", KOTLIN, flags=re.M):
            quoted, word = name
            if word in HARD_KEYWORDS:
                self.assertEqual(quoted, "`", f"{word} must be written between backticks")
        self.assertIn("val `interface`: NetworkInterface", KOTLIN)

    def test_kotlin_keeps_the_names_of_the_json_fields(self):
        self.assertIn("val node_id: String", KOTLIN)
        self.assertIn("val timestamp_ms: Long", KOTLIN)
        self.assertNotIn("nodeId", KOTLIN)

    def test_a_message_that_always_has_one_kind_says_which(self):
        self.assertIn('kind: "inverter";', TYPESCRIPT)
        self.assertIn('val kind: String = "network",', KOTLIN)

    def test_no_object_of_a_message_is_left_as_an_unnamed_map(self):
        self.assertNotIn("Record<string, unknown>", TYPESCRIPT)
        self.assertNotIn("Map<String, Any>", KOTLIN)
        self.assertNotIn("List<Any>", KOTLIN)


try:
    import yaml   # noqa: F401 - the generator of the types of the HTTP contract reads the OpenAPI document with it
except ImportError:      # a machine without the contract tests skips this class
    yaml = None


@unittest.skipIf(yaml is None, "PyYAML is not installed (pip install -e .[contract-tests])")
class RestTypesTests(unittest.TestCase):
    def setUp(self):
        import sys
        sys.path.insert(0, str(ROOT / "tools"))
        import generate_rest_types
        self.generated = generate_rest_types.render()
        self.rest = (ROOT / "generated" / "armor-rest.ts").read_text(encoding="utf-8").replace("\r\n", "\n")

    def test_the_types_of_the_http_contract_are_current(self):
        self.assertEqual(self.generated, self.rest, "run python tools/generate_rest_types.py")

    def test_every_component_of_the_contract_has_its_type_and_the_messages_of_the_nodes_are_not_repeated(self):
        import generate_rest_types
        document = yaml.load(generate_rest_types.OPENAPI.read_text(encoding="utf-8"), Loader=generate_rest_types.Loader)
        for name in document["components"]["schemas"]:
            self.assertIn(f"export type {name} = ", self.rest, name)
        self.assertIn("export type ConnectionClient = Contracts.ConnectionClient;", self.rest)

    def test_a_property_called_on_keeps_its_name(self):
        self.assertRegex(self.rest, r"\bon\??: ")


if __name__ == "__main__":
    unittest.main()
