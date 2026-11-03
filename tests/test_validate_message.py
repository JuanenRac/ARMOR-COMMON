"""validate_message: the topic alone chooses the validator, for every family of messages."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from armor_common import ContractError, decode, encode, validate_message

CONFORMANCE = Path(__file__).resolve().parent.parent / "conformance"


def first_valid(name: str) -> dict:
    document = json.loads((CONFORMANCE / f"{name}.json").read_text(encoding="utf-8"))
    return next(vector["payload"] for vector in document["vectors"] if vector["valid"])


class ValidateMessageTests(unittest.TestCase):
    def test_zigbee_feed_and_server_alert_are_routed(self) -> None:
        feed = first_valid("alarm_zone_feed")
        validate_message("armor/alarm/panel-1/zigbee", feed)
        with self.assertRaises(ContractError):
            validate_message("armor/alarm/panel-1/zigbee", {**feed, "state": "not-a-state"})
        validate_message("armor/server/alert", first_valid("server_alert"))

    def test_the_leaves_of_the_alarm_family_are_routed_and_others_refused(self) -> None:
        for leaf in ("state", "command", "result", "policy", "bogus"):
            with self.subTest(leaf=leaf), self.assertRaises(ContractError):
                validate_message(f"armor/alarm/panel-1/{leaf}", {})

    def test_unknown_topics_are_refused(self) -> None:
        for topic in ("", "node/a/telemetry", "armor/x", "armor/unknown/a/state", "armor/control/a/other"):
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                validate_message(topic, {})
        with self.assertRaises(ContractError):
            validate_message(None, {})  # type: ignore[arg-type]

    def test_the_envelope_reads_messages_of_the_other_families(self) -> None:
        feed = first_valid("alarm_zone_feed")
        topic, payload = decode(encode("armor/alarm/panel-1/zigbee", feed))
        self.assertEqual((topic, payload), ("armor/alarm/panel-1/zigbee", feed))


if __name__ == "__main__":
    unittest.main()
