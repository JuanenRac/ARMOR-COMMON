"""The shared path of a spoken order to silence the alarm (conformance/voice/silence_path.json) is well formed and says what the two ends rely on."""
import json
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "conformance" / "voice" / "silence_path.json"
MODES = {"off", "double_turn", "pin", "challenge"}
ANSWERS = {"accepted", "token", "needs_confirmation"}
CONFIRMATIONS = {"none", "server_token", "issued"}


class SilencePath(unittest.TestCase):
    def setUp(self):
        self.vector = json.loads(PATH.read_text(encoding="utf-8"))

    def test_every_mode_has_a_path_and_every_path_is_well_formed(self):
        self.assertEqual({path["mode"] for path in self.vector["paths"]}, MODES)
        for path in self.vector["paths"]:
            with self.subTest(path["name"]):
                self.assertIn(path["first_answer"], ANSWERS)
                self.assertEqual(path["asks"][0], {"text": "original", "confirmation": "none"})
                for ask in path["asks"]:
                    self.assertEqual(ask["text"], "original", "the order that is asked is always the one first said, never the proof")
                    self.assertIn(ask["confirmation"], CONFIRMATIONS)
                    self.assertEqual("subject" in ask, ask["confirmation"] == "issued")

    def test_the_subject_of_an_issued_confirmation_is_the_panel_or_the_operator(self):
        subject = self.vector["subject"]
        for path in self.vector["paths"]:
            for ask in path["asks"]:
                if ask["confirmation"] == "issued":
                    expected = subject["panel_prefix"] + path["panel"] if path["panel"] else subject["operator"]
                    self.assertEqual(ask["subject"], expected, path["name"])
                    self.assertLessEqual(len(ask["subject"]), subject["max_length"])

    def test_the_validities_are_the_ones_in_force(self):
        self.assertEqual(self.vector["validity_s"], {"double_turn": 15, "pin": 20, "challenge": 20, "pending": 30})


if __name__ == "__main__":
    unittest.main()
