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


if __name__ == "__main__":
    unittest.main()
