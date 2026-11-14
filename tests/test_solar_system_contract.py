"""The summary a solar gateway publishes about everything it reads, on armor/solar/{node_id}/system."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from armor_common.contracts import ContractError, parse_solar_system_topic, validate_solar_system  # noqa: E402

CONFORMANCE = ROOT / "conformance"


def vectors():
    return json.loads((CONFORMANCE / "solar_system.json").read_text(encoding="utf-8"))["vectors"]


class SolarSystemTests(unittest.TestCase):
    def test_the_topic_carries_the_node(self):
        self.assertEqual(parse_solar_system_topic("armor/solar/solar-1/system"), "solar-1")
        for topic in ["armor/solar/solar-1/state", "armor/solar/solar-1/axpert-1/system", "armor/node/solar-1/system", "armor/solar/Solar/system", "armor/solar//system",
                      "armor/solar/solar-1/system/extra"]:
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                parse_solar_system_topic(topic)

    def test_the_vectors_are_judged_as_the_contract_says(self):
        for vector in vectors():
            with self.subTest(vector["name"]):
                payload = vector["payload"]
                if vector["valid"]:
                    validate_solar_system("armor/solar/solar-1/system", payload)
                else:
                    with self.assertRaises(ContractError):
                        validate_solar_system("armor/solar/solar-1/system", payload)

    def test_the_node_in_the_topic_must_be_the_node_in_the_payload(self):
        payload = next(v["payload"] for v in vectors() if v["valid"])
        with self.assertRaises(ContractError):
            validate_solar_system("armor/solar/solar-2/system", payload)

    def test_every_alert_code_is_a_fixed_word(self):
        schema = json.loads((ROOT / "src" / "armor_common" / "schemas" / "solar_system.schema.json").read_text(encoding="utf-8"))
        codes = schema["properties"]["alerts"]["items"]["properties"]["code"]["enum"]
        self.assertEqual(codes, ["soc_low", "cell_over_voltage", "temperature_high", "temperature_low"])


if __name__ == "__main__":
    unittest.main()
