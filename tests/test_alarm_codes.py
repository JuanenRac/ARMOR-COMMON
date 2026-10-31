"""The table of alarm codes: every code has its words in the eight languages, and the codes the contract names are all there."""
import json
import unittest
from pathlib import Path

TABLE = Path(__file__).resolve().parents[1] / "src" / "armor_common" / "alarm_codes.json"
LANGUAGES = ["en", "es", "de", "fr", "it", "ja", "zh", "pt"]


class AlarmCodes(unittest.TestCase):
    def setUp(self):
        self.table = json.loads(TABLE.read_text(encoding="utf-8"))

    def test_the_eight_languages_are_declared(self):
        self.assertEqual(self.table["languages"], LANGUAGES)

    def test_every_code_is_said_in_every_language(self):
        self.assertGreaterEqual(len(self.table["codes"]), 55)
        for code, words in self.table["codes"].items():
            with self.subTest(code):
                self.assertRegex(code, r"^[a-z][a-z0-9_]{1,47}$")
                self.assertEqual(sorted(words), sorted(LANGUAGES))
                for language, sentence in words.items():
                    self.assertTrue(sentence.strip(), language)
                    self.assertLessEqual(len(sentence), 160, language)
                    self.assertNotIn("{", sentence, language)

    def test_a_language_is_not_the_english_one_left_in_place(self):
        for code, words in self.table["codes"].items():
            others = [words[language] for language in LANGUAGES if language not in ("en", "pt")]
            with self.subTest(code):
                self.assertTrue(any(sentence != words["en"] for sentence in others))

    def test_the_codes_the_alarm_centre_raises_are_in_the_table(self):
        # the ones a person is told about: the device kinds, the nodes, the network, the solar gateways and the electrical nodes
        for code in ("intrusion", "node_down", "camera_down", "tamper", "low_battery", "device_offline", "duress_disarm", "solar_fault", "electrical_grid_lost",
                     "network_new_device", "alarm_sounding", "node_wifi_jam"):
            self.assertIn(code, self.table["codes"])


if __name__ == "__main__":
    unittest.main()
