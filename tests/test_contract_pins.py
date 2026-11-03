"""The pin of each consumer repository: complete, well formed, and never ahead of the contracts."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contract_pins", ROOT / "tools" / "contract_pins.py")
pins = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(pins)  # type: ignore[union-attr]


class ContractPinTests(unittest.TestCase):
    def test_the_pins_are_sound(self):
        self.assertEqual(pins.problems(), [])

    def test_versions_compare_as_numbers(self):
        self.assertGreater(pins.key("0.8.0.10"), pins.key("0.8.0.9"))
        self.assertGreater(pins.key("0.8.1.0"), pins.key("0.8.0.9"))


if __name__ == "__main__":
    unittest.main()
