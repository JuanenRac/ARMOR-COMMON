"""The rules that hide the secrets of an environment file: every vector holds, and what is hidden is never given away."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from armor_common import env_masking  # noqa: E402


class EnvMaskingTests(unittest.TestCase):
    def test_mask_vectors(self):
        for case in env_masking.rules()["mask_vectors"]:
            with self.subTest(case["name"]):
                self.assertEqual(env_masking.mask_env(case["input"]), case["output"])

    def test_unmask_vectors(self):
        for case in env_masking.rules()["unmask_vectors"]:
            with self.subTest(case["name"]):
                got = env_masking.unmask_env(case["edited"], case["current"])
                if "missing" in case:
                    self.assertEqual(got, {"missing": case["missing"]})
                else:
                    self.assertEqual(got, {"content": case["content"]})

    def test_masking_twice_changes_nothing(self):
        for case in env_masking.rules()["mask_vectors"]:
            once = env_masking.mask_env(case["input"])
            self.assertEqual(env_masking.mask_env(once), once, case["name"])

    def test_the_masked_text_never_holds_a_secret(self):
        text = "A_TOKEN=s1\nB_PASSWORD=s2\nU=mqtt://u:s3@h:1\nH=https://h/x?key=s4&z=1\nPORT=5\n"
        masked = env_masking.mask_env(text)
        for secret in ("s1", "s2", "s3", "s4"):
            self.assertNotIn(secret, masked)
        self.assertEqual(env_masking.unmask_env(masked, text), {"content": text})

    def test_the_rules_are_the_ones_the_code_uses(self):
        self.assertEqual(env_masking.rules()["login_hidden"], "***")
        self.assertEqual(env_masking.rules()["query_names"], ["token", "key", "secret", "password", "pass"])


if __name__ == "__main__":
    unittest.main()
