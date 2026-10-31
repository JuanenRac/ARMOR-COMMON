"""The labels of the facts an alarm carries: every fact has its label in the eight languages, and the facts the alarm codes name are all there."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "armor_common"
LANGUAGES = ["en", "es", "de", "fr", "it", "ja", "zh", "pt"]


class AlarmFacts(unittest.TestCase):
    def setUp(self):
        self.table = json.loads((ROOT / "alarm_facts.json").read_text(encoding="utf-8"))

    def test_the_eight_languages_are_declared(self):
        self.assertEqual(self.table["languages"], LANGUAGES)

    def test_every_fact_is_labelled_in_every_language(self):
        self.assertGreaterEqual(len(self.table["facts"]), 50)
        for key, words in self.table["facts"].items():
            with self.subTest(key):
                self.assertRegex(key, r"^[a-z][a-z0-9_]{0,47}$")
                self.assertEqual(sorted(words), sorted(LANGUAGES))
                for language, label in words.items():
                    self.assertTrue(label.strip(), language)
                    self.assertLessEqual(len(label), 60, language)

    def test_the_facts_of_a_panel_that_does_not_confirm_the_arming_mode_are_there(self):
        for key in ("arming_mode", "panel_profile", "panels", "panel_answers", "by", "what_happened", "device", "ip", "mac", "port"):
            self.assertIn(key, self.table["facts"])

    def test_portuguese_is_the_european_one(self):
        words = " ".join(row["pt"] for row in self.table["facts"].values()).lower()
        for brazilian in ("arquivo", "tela", "celular", "usuário"):
            self.assertNotIn(brazilian, words)


if __name__ == "__main__":
    unittest.main()
