"""The validator can say all the faults of a message at once, and its first fault is the one it has always raised."""
from __future__ import annotations

import unittest

from armor_common import ContractError, collect_payload_errors
from armor_common.contracts import load_schema, validate_payload
from armor_common.schema import iter_errors, validate

POLICY = {"config_hash": True, "zone_feed": True, "zone_feed_signature": False}


class CollectErrorsTests(unittest.TestCase):
    def test_a_good_message_has_no_faults(self):
        self.assertEqual(collect_payload_errors("alarm_policy", POLICY), [])

    def test_every_fault_is_reported_and_the_first_is_the_one_validation_raises(self):
        bad = {"config_hash": "yes", "zone_feed": 1, "extra": True}
        errors = collect_payload_errors("alarm_policy", bad)
        self.assertGreaterEqual(len(errors), 4, errors)                    # two wrong types, a missing option, an option that does not exist
        self.assertTrue(any("zone_feed_signature" in text and "required" in text for text in errors))
        self.assertTrue(any("extra" in text and "not allowed" in text for text in errors))
        with self.assertRaises(ContractError) as raised:
            validate_payload("alarm_policy", bad)
        self.assertEqual(str(raised.exception), errors[0])

    def test_a_value_of_the_wrong_type_is_reported_once_and_not_looked_into(self):
        self.assertEqual(len(collect_payload_errors("alarm_policy", [1, 2])), 1)
        self.assertEqual(len(collect_payload_errors("alarm_policy", "text")), 1)

    def test_the_published_schema_is_a_copy_nobody_can_change_for_the_others(self):
        copy_one = load_schema("alarm_policy")
        copy_one["properties"]["zone_feed"]["type"] = "string"
        copy_one["required"].clear()
        self.assertEqual(load_schema("alarm_policy")["properties"]["zone_feed"]["type"], "boolean")
        self.assertEqual(collect_payload_errors("alarm_policy", POLICY), [])
        with self.assertRaises(ContractError):
            validate_payload("alarm_policy", {"config_hash": True})

    def test_a_message_that_repeats_a_name_is_refused_by_the_decoder(self):
        from armor_common import decode
        with self.assertRaisesRegex(ValueError, "repeats the field"):
            decode('{"topic":"armor/alarm/alarm-1/policy","payload":{"config_hash":true,"config_hash":false,"zone_feed":true,"zone_feed_signature":false}}')

    def test_iter_errors_is_lazy(self):
        schema = load_schema("alarm_policy")
        walker = iter_errors({"config_hash": 1, "zone_feed": 2, "zone_feed_signature": 3}, schema)
        first = next(walker)
        self.assertIn("config_hash", str(first))
        with self.assertRaises(Exception):
            validate({"config_hash": 1, "zone_feed": 2, "zone_feed_signature": 3}, schema)


if __name__ == "__main__":
    unittest.main()
