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

    def test_every_help_text_is_in_every_language_and_names_a_code(self):
        helps = self.table["help"]
        self.assertGreaterEqual(len(helps), 11)
        for code, words in helps.items():
            with self.subTest(code):
                self.assertRegex(code, r"^[a-z][a-z0-9_]{0,47}$")
                self.assertEqual(sorted(words), sorted(LANGUAGES))
                for language, text in words.items():
                    self.assertTrue(text.strip(), language)
                    self.assertLessEqual(len(text), 600, language)

    def test_every_alarm_code_has_its_help_text(self):
        codes = json.loads((ROOT / "alarm_codes.json").read_text(encoding="utf-8"))["codes"]
        missing = sorted(code for code in codes if code not in self.table["help"])
        self.assertEqual(missing, [], "an alarm code without a help text: add it to alarm_facts.json (what it means and what to check, in the eight languages)")
        self.assertEqual(sorted(set(self.table["help"]) - set(codes)), [], "a help text for a code that does not exist")

    def test_every_help_text_says_what_it_means_and_what_to_check_in_two_lines(self):
        starts = {"en": ("Means:", "Check:"), "es": ("Significa:", "Revisa:"), "de": ("Bedeutung:", "Prüfen:"), "fr": ("Signification:", "À vérifier:"), "it": ("Significato:", "Controlla:"),
                  "ja": ("意味:", "確認:"), "zh": ("含义:", "检查:"), "pt": ("Significa:", "Verifique:")}
        for code, words in self.table["help"].items():
            for language, text in words.items():
                with self.subTest(f"{code} {language}"):
                    lines = text.split("\n")
                    self.assertEqual(len(lines), 2)
                    self.assertTrue(lines[0].startswith(starts[language][0]), lines[0][:30])
                    self.assertTrue(lines[1].startswith(starts[language][1]), lines[1][:30])

    def test_the_help_of_the_alarms_that_threaten_life_tells_to_get_safe_first(self):
        for code in ("smoke", "co", "gas"):
            check = self.table["help"][code]["en"].split("\n")[1].lower()
            self.assertTrue("leave" in check or "call" in check, code)
        self.assertIn("police", self.table["help"]["panic"]["en"].lower())
        self.assertIn("police", self.table["help"]["duress_disarm"]["en"].lower())

    def test_portuguese_help_is_the_european_one(self):
        words = " ".join(row["pt"] for row in self.table["help"].values()).lower()
        for brazilian in ("arquivo", "tela", "celular", "usuário", "você"):
            self.assertNotIn(brazilian, words)

    def test_portuguese_is_the_european_one(self):
        words = " ".join(row["pt"] for row in self.table["facts"].values()).lower()
        for brazilian in ("arquivo", "tela", "celular", "usuário"):
            self.assertNotIn(brazilian, words)


if __name__ == "__main__":
    unittest.main()
