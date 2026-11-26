"""The catalogue of the solar equipment protocols: every entry is whole, the ids are unique and the line settings are ones a gateway node accepts."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = json.loads((ROOT / "src" / "armor_common" / "solar_protocols.json").read_text(encoding="utf-8"))
KEYS = {"id", "label", "message", "port_kind", "dialect", "baud", "framing", "physical", "commands", "fields", "status", "note"}


class SolarProtocols(unittest.TestCase):
    def test_every_protocol_is_whole_and_unique(self):
        ids = [p["id"] for p in CATALOGUE["protocols"]] + [p["id"] for p in CATALOGUE["not_implemented"]]
        self.assertEqual(len(ids), len(set(ids)))
        for protocol in CATALOGUE["protocols"]:
            self.assertEqual(set(protocol), KEYS, protocol["id"])
            self.assertRegex(protocol["id"], r"^[a-z0-9][a-z0-9-]{0,31}$")
            self.assertIn(protocol["message"], ("inverter", "battery"))
            self.assertIn(protocol["status"], ("decoded", "partial"))
            self.assertIn(protocol["baud"], (2400, 9600, 19200, 115200))
            self.assertEqual(protocol["framing"], "8N1")
        for missing in CATALOGUE["not_implemented"]:
            self.assertTrue(missing["reason"], missing["id"])

    def test_the_fields_are_ones_the_messages_have(self):
        schemas = ROOT / "src" / "armor_common" / "schemas"
        inverter = set(json.loads((schemas / "solar_inverter.schema.json").read_text(encoding="utf-8"))["properties"])
        battery_schema = json.loads((schemas / "solar_battery.schema.json").read_text(encoding="utf-8"))["properties"]
        battery = set(battery_schema) | set(battery_schema["stack"]["items"]["properties"])
        for protocol in CATALOGUE["protocols"]:
            known = inverter if protocol["message"] == "inverter" else battery
            self.assertEqual(sorted(set(protocol["fields"]) - known), [], protocol["id"])


if __name__ == "__main__":
    unittest.main()
