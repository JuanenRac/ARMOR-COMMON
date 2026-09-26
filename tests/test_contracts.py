import json
import unittest
from pathlib import Path

from armor_common import ContractError, decode, encode, validate_electrical_message, validate_solar_message, validate_topic_and_payload
from armor_common.contracts import load_schema, parse_electrical_topic, parse_solar_topic, parse_topic, validate_payload
from armor_common.schema import SchemaError, UnsupportedSchema, check_schema, validate

CONFORMANCE = Path(__file__).resolve().parent.parent / "conformance"


class ConformanceTests(unittest.TestCase):
    """The shared vectors every implementation must agree on."""

    def test_every_vector_is_accepted_or_rejected_as_published(self):
        checked = 0
        for file in sorted(CONFORMANCE.glob("*.json")):
            document = json.loads(file.read_text(encoding="utf-8"))
            kind = document["kind"]
            for vector in document["vectors"]:
                with self.subTest(kind=kind, case=vector["name"]):
                    if vector["valid"]:
                        validate_payload(kind, vector["payload"])
                    else:
                        with self.assertRaises(ContractError):
                            validate_payload(kind, vector["payload"])
                checked += 1
        self.assertGreaterEqual(checked, 40)


class SchemaValidatorTests(unittest.TestCase):
    def test_types_are_strict_and_a_boolean_is_never_a_number(self):
        for value, schema_type, ok in [(1, "integer", True), (1.0, "integer", True), (1.5, "integer", False), (True, "integer", False),
                                       (True, "number", False), (1.5, "number", True), ("1", "number", False), (None, "null", True),
                                       ([], "array", True), ({}, "object", True), ("x", "string", True)]:
            with self.subTest(value=value, type=schema_type):
                if ok:
                    validate(value, {"type": schema_type})
                else:
                    with self.assertRaises(SchemaError):
                        validate(value, {"type": schema_type})

    def test_errors_locate_the_offending_value(self):
        schema = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "integer"}}}}
        with self.assertRaises(SchemaError) as caught:
            validate({"items": [1, 2, "x"]}, schema)
        self.assertEqual(caught.exception.path, "/items/2")

    def test_required_additional_properties_and_bounds(self):
        schema = {"type": "object", "required": ["a"], "additionalProperties": False, "properties": {"a": {"type": "integer", "minimum": 1, "maximum": 3}}}
        validate({"a": 2}, schema)
        for bad in ({}, {"a": 0}, {"a": 4}, {"a": 2, "b": 1}):
            with self.assertRaises(SchemaError):
                validate(bad, schema)

    def test_string_and_array_limits(self):
        validate("abc", {"type": "string", "pattern": "^a", "minLength": 2, "maxLength": 3})
        for bad in ("bcd", "a", "abcd"):
            with self.assertRaises(SchemaError):
                validate(bad, {"type": "string", "pattern": "^a", "minLength": 2, "maxLength": 3})
        with self.assertRaises(SchemaError):
            validate([1, 2, 3], {"type": "array", "maxItems": 2})
        with self.assertRaises(SchemaError):
            validate([], {"type": "array", "minItems": 1})

    def test_enum_and_const(self):
        validate("a", {"enum": ["a", "b"]})
        with self.assertRaises(SchemaError):
            validate("c", {"enum": ["a", "b"]})
        with self.assertRaises(SchemaError):
            validate(2, {"const": 1})

    def test_a_schema_with_an_unimplemented_keyword_is_refused_not_ignored(self):
        with self.assertRaises(UnsupportedSchema):
            check_schema({"type": "object", "oneOf": []})
        with self.assertRaises(UnsupportedSchema):
            check_schema({"properties": {"a": {"format": "email"}}})

    def test_every_published_schema_uses_only_supported_keywords(self):
        for kind in ("telemetry", "health", "command"):
            check_schema(load_schema(kind))


class TopicTests(unittest.TestCase):
    def test_topics_are_parsed_strictly(self):
        self.assertEqual(parse_topic("armor/node/north-1/telemetry"), ("north-1", "telemetry"))
        for bad in ["armor/node/north-1", "armor/nodo/x/telemetry", "armor/node/X/telemetry", "armor/node//health", "armor/node/a/b/health",
                    "armor/node/a/reboot", "", "armor/node/a b/health"]:
            with self.subTest(topic=bad), self.assertRaises(ContractError):
                parse_topic(bad)
        with self.assertRaises(ContractError):
            parse_topic(None)  # type: ignore[arg-type]

    def test_valid_telemetry(self):
        validate_topic_and_payload("armor/node/north-1/telemetry", {
            "node_id": "north-1", "timestamp_ms": 1, "lux": 42.0,
            "targets": [{"sensor_id": 1, "track_id": 9, "x_mm": 10, "y_mm": 20, "speed_mm_s": 30}],
        })

    def test_rejects_topic_node_mismatch(self):
        with self.assertRaises(ContractError):
            validate_topic_and_payload("armor/node/north-1/health", {"node_id": "south-1", "online": True, "timestamp_ms": 1})

    def test_commands_are_an_allow_list(self):
        validate_topic_and_payload("armor/node/n1/command", {"node_id": "n1", "timestamp_ms": 1, "command": "restart"})
        with self.assertRaises(ContractError):
            validate_topic_and_payload("armor/node/n1/command", {"node_id": "n1", "timestamp_ms": 1, "command": "rm -rf"})

    def test_a_non_object_payload_is_refused(self):
        with self.assertRaises(ContractError):
            validate_topic_and_payload("armor/node/n1/health", [1])  # type: ignore[arg-type]


class EnvelopeTests(unittest.TestCase):
    def test_round_trip_envelope(self):
        line = encode("armor/node/north-1/health", {"node_id": "north-1", "online": True, "timestamp_ms": 1})
        self.assertEqual(decode(line)[0], "armor/node/north-1/health")

    def test_encoding_is_deterministic(self):
        payload = {"timestamp_ms": 1, "online": True, "node_id": "n1"}
        self.assertEqual(encode("armor/node/n1/health", payload), encode("armor/node/n1/health", dict(reversed(list(payload.items())))))

    def test_untrusted_lines_are_refused(self):
        for bad in ["not json", "[]", "{}", '{"topic":"armor/node/n1/health"}', '{"topic":5,"payload":{}}',
                    '{"topic":"armor/node/n1/health","payload":{"node_id":"n1","timestamp_ms":1,"online":"yes"}}',
                    '{"topic":"armor/node/n1/health","payload":{"node_id":"n1","timestamp_ms":1,"online":true},"extra":1}']:
            with self.subTest(line=bad), self.assertRaises((ValueError, ContractError)):
                decode(bad)


class InfoMessageTests(unittest.TestCase):
    def test_info_is_a_published_kind_with_its_own_topic(self):
        payload = {"node_id": "north-1", "timestamp_ms": 5, "name": "North gate", "firmware": "0.2.3", "ip": "192.168.0.181", "port": 80}
        validate_topic_and_payload("armor/node/north-1/info", payload)
        with self.assertRaises(ContractError):
            validate_topic_and_payload("armor/node/other/info", payload)  # the node id must match the topic
        self.assertEqual(parse_topic("armor/node/north-1/info"), ("north-1", "info"))


if __name__ == "__main__":
    unittest.main()


class SolarMessageTests(unittest.TestCase):
    """The messages of the gateway nodes that read inverters and batteries."""

    inverter = json.loads((CONFORMANCE / "solar_inverter.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]
    battery = json.loads((CONFORMANCE / "solar_battery.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]

    def test_the_topic_carries_the_node_and_the_device(self):
        self.assertEqual(parse_solar_topic("armor/solar/solar-1/axpert-1/state"), ("solar-1", "axpert-1"))
        for topic in ["armor/solar/solar-1/state", "armor/solar/solar-1/axpert-1/set", "armor/node/solar-1/axpert-1/state", "armor/solar/Solar/axpert-1/state",
                      "armor/solar/solar-1/AXPERT/state", "armor/solar/-solar/axpert-1/state", "armor/solar/solar-1/-axpert/state", "armor/solar/solar-1/" + "d" * 33 + "/state",
                      "armor/solar/solar-1/axpert-1/state/extra", "armor/solar//axpert-1/state"]:
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                parse_solar_topic(topic)

    def test_a_message_must_agree_with_its_topic(self):
        validate_solar_message("armor/solar/solar-1/axpert-1/state", self.inverter)
        validate_solar_message("armor/solar/solar-1/us3000-1/state", self.battery)
        with self.assertRaises(ContractError):
            validate_solar_message("armor/solar/solar-2/axpert-1/state", self.inverter)     # another node
        with self.assertRaises(ContractError):
            validate_solar_message("armor/solar/solar-1/axpert-2/state", self.inverter)     # another device
        with self.assertRaises(ContractError):
            validate_solar_message("armor/solar/solar-1/axpert-1/state", {**self.inverter, "kind": "toaster"})
        with self.assertRaises(ContractError):
            validate_solar_message("armor/solar/solar-1/axpert-1/state", [self.inverter])
        with self.assertRaises(ContractError):
            validate_solar_message("armor/solar/solar-1/axpert-1/state", {**self.inverter, "kind": "battery"})   # the schema of a battery refuses an inverter's fields


class ElectricalMessageTests(unittest.TestCase):
    """The messages of the nodes that measure the house's electrical network."""

    electrical = json.loads((CONFORMANCE / "electrical.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]

    def test_the_topic_carries_the_node(self):
        self.assertEqual(parse_electrical_topic("armor/electrical/electrical-1/state"), "electrical-1")
        for topic in ["armor/electrical/state", "armor/electrical/electrical-1/set", "armor/solar/electrical-1/state", "armor/electrical/Node/state",
                      "armor/electrical/-node/state", "armor/electrical/" + "n" * 65 + "/state", "armor/electrical/electrical-1/state/extra", "armor/electrical//state"]:
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                parse_electrical_topic(topic)

    def test_a_message_must_agree_with_its_topic_and_name_each_channel_once(self):
        validate_electrical_message("armor/electrical/electrical-1/state", self.electrical)
        with self.assertRaises(ContractError):
            validate_electrical_message("armor/electrical/other/state", self.electrical)
        with self.assertRaises(ContractError):
            validate_electrical_message("armor/electrical/electrical-1/state", [self.electrical])
        twice = {**self.electrical, "channels": [{"id": "grid", "domain": "ac"}, {"id": "grid", "domain": "dc"}]}
        with self.assertRaises(ContractError):
            validate_electrical_message("armor/electrical/electrical-1/state", twice)
