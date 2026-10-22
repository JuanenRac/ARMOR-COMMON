import json
import unittest
from pathlib import Path

from armor_common import ContractError, validate_radar_event, validate_diagnostic_token_request, validate_diagnostic_token_created, validate_diagnostic_token_info, decode, encode, validate_arm_profile, validate_node_health, validate_alarm_command, validate_alarm_message, validate_alarm_result, validate_alarm_zone_feed, validate_device_message, validate_network_orders, validate_server_alert, validate_electrical_command, validate_electrical_message, validate_electrical_result, validate_network_message, validate_node_control_command, validate_node_control_result, validate_node_maintenance, validate_solar_battery_command, validate_solar_battery_result, validate_solar_message, validate_topic_and_payload
from armor_common.contracts import battery_catalog, battery_expert_line, parse_battery_topic, validate_battery_params
from armor_common.contracts import parse_control_topic
from armor_common.contracts import load_schema, parse_alarm_topic, parse_device_topic, parse_electrical_topic, parse_network_topic, parse_solar_topic, parse_topic, validate_payload
from armor_common.schema import SchemaError, UnsupportedSchema, check_schema, validate

CONFORMANCE = Path(__file__).resolve().parent.parent / "conformance"
# The kinds whose messages also have a rule a schema cannot state (a token where none belongs, a switch named twice): the check of the whole message.
MESSAGE_RULES = {
    "electrical": lambda payload: validate_electrical_message(f"armor/electrical/{payload['node_id']}/state", payload),
    "electrical_command": lambda payload: validate_electrical_command(f"armor/electrical/{payload['node_id']}/command", payload),
    "electrical_result": lambda payload: validate_electrical_result(f"armor/electrical/{payload['node_id']}/result", payload),
    "solar_battery_command": lambda payload: validate_solar_battery_command(f"armor/solar/{payload['node_id']}/maintenance/command", payload),
    "solar_battery_result": lambda payload: validate_solar_battery_result(f"armor/solar/{payload['node_id']}/maintenance/result", payload),
    "node_control_command": lambda payload: validate_node_control_command(f"armor/control/{payload['node_id']}/command", payload),
    "node_control_result": lambda payload: validate_node_control_result(f"armor/control/{payload['node_id']}/result", payload),
    "node_maintenance": lambda payload: validate_node_maintenance(f"armor/control/{payload['node_id']}/maintenance", payload),
    "alarm": lambda payload: validate_alarm_message(f"armor/alarm/{payload['node_id']}/state", payload),
    "alarm_command": lambda payload: validate_alarm_command(f"armor/alarm/{payload['node_id']}/command", payload),
    "alarm_result": lambda payload: validate_alarm_result(f"armor/alarm/{payload['node_id']}/result", payload),
    "network": lambda payload: validate_network_message(f"armor/network/{payload['node_id']}/state", payload),
    "alarm_zone_feed": lambda payload: validate_alarm_zone_feed("armor/alarm/alarm-1/zigbee", payload),
    "device_state": lambda payload: validate_device_message("armor/device/electrical-1/lights/state", payload),
    "server_alert": lambda payload: validate_server_alert("armor/server/alert", payload),
    "network_orders": validate_network_orders,
    "node_health": lambda payload: validate_node_health(f"armor/health/{payload['node_id']}", payload),
    "radar_event": lambda payload: validate_radar_event(f"armor/radar/{payload['node_id']}/events", payload),
    "diagnostic_token_request": validate_diagnostic_token_request,
    "diagnostic_token_created": validate_diagnostic_token_created,
    "diagnostic_token_info": validate_diagnostic_token_info,
    "arm_profile": validate_arm_profile,
}


class ConformanceTests(unittest.TestCase):
    """The shared vectors every implementation must agree on."""

    def test_every_vector_is_accepted_or_rejected_as_published(self):
        checked = 0
        for file in sorted(CONFORMANCE.glob("*.json")):
            document = json.loads(file.read_text(encoding="utf-8"))
            kind = document["kind"]
            for vector in document["vectors"]:
                with self.subTest(kind=kind, case=vector["name"]):
                    rule = MESSAGE_RULES.get(kind)
                    if vector["valid"]:
                        validate_payload(kind, vector["payload"])
                        if rule:
                            rule(vector["payload"])
                    elif vector.get("schema_valid"):
                        validate_payload(kind, vector["payload"])   # the schema alone accepts it...
                        with self.assertRaises(ContractError):
                            rule(vector["payload"])                 # ...and the rule of the whole message refuses it
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


class AlarmMessageTests(unittest.TestCase):
    """The messages of an alarm node: their topics and that each one agrees with its topic."""

    state = json.loads((CONFORMANCE / "alarm.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]
    command = json.loads((CONFORMANCE / "alarm_command.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]
    result = json.loads((CONFORMANCE / "alarm_result.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]

    def test_the_topic_of_each_leaf_carries_the_node(self):
        for leaf in ("state", "command", "result"):
            self.assertEqual(parse_alarm_topic(f"armor/alarm/alarm-1/{leaf}", leaf), "alarm-1")
        for topic, leaf in [("armor/alarm/alarm-1/command", "state"), ("armor/alarm/alarm-1/state", "command"), ("armor/alarm/alarm-1/set", "state"), ("armor/alarm/Node/state", "state"),
                            ("armor/alarm/-x/result", "result"), ("armor/alarm/a/b/state", "state"), ("armor/alarm/alarm-1/state/extra", "state"), ("armor/electrical/alarm-1/state", "state"),
                            ("armor/alarm//state", "state")]:
            with self.subTest(topic=topic, leaf=leaf), self.assertRaises(ContractError):
                parse_alarm_topic(topic, leaf)
        with self.assertRaises(ContractError):
            parse_alarm_topic("armor/alarm/alarm-1/set", "set")

    def test_each_message_must_agree_with_its_topic(self):
        validate_alarm_message("armor/alarm/alarm-1/state", self.state)
        validate_alarm_command("armor/alarm/alarm-1/command", self.command)
        validate_alarm_result("armor/alarm/alarm-1/result", self.result)
        for check, topic, payload in [(validate_alarm_message, "armor/alarm/other/state", self.state), (validate_alarm_command, "armor/alarm/other/command", self.command),
                                      (validate_alarm_result, "armor/alarm/other/result", self.result), (validate_alarm_message, "armor/alarm/alarm-1/result", self.state),
                                      (validate_alarm_command, "armor/alarm/alarm-1/state", self.command), (validate_alarm_result, "armor/alarm/alarm-1/command", self.result),
                                      (validate_alarm_message, "armor/alarm/alarm-1/state", [self.state])]:
            with self.subTest(check=check.__name__, topic=topic), self.assertRaises(ContractError):
                check(topic, payload)

    def test_a_command_carries_a_mode_only_on_an_arm(self):
        disarm = {k: v for k, v in self.command.items() if k not in ("mode", "force")} | {"action": "disarm"}
        validate_alarm_command("armor/alarm/alarm-1/command", disarm)
        with self.assertRaises(ContractError):
            validate_alarm_command("armor/alarm/alarm-1/command", {**disarm, "mode": "away"})
        with self.assertRaises(ContractError):
            validate_alarm_command("armor/alarm/alarm-1/command", {**disarm, "force": True})
        with self.assertRaises(ContractError):
            validate_alarm_command("armor/alarm/alarm-1/command", {k: v for k, v in self.command.items() if k != "mode"})


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


class ElectricalSwitchMessageTests(unittest.TestCase):
    """The command to a switch and the node's answer: their topics, and the rules of the whole message."""

    command = json.loads((CONFORMANCE / "electrical_command.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]
    result = json.loads((CONFORMANCE / "electrical_result.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]

    def test_the_topic_of_each_leaf_carries_the_node(self):
        for leaf in ("state", "command", "result"):
            self.assertEqual(parse_electrical_topic(f"armor/electrical/electrical-1/{leaf}", leaf), "electrical-1")
        for topic, leaf in [("armor/electrical/electrical-1/command", "state"), ("armor/electrical/electrical-1/state", "command"), ("armor/electrical/electrical-1/result", "command"),
                            ("armor/electrical/electrical-1/set", "command"), ("armor/electrical/Node/command", "command"), ("armor/electrical/-x/result", "result"),
                            ("armor/electrical/a/b/command", "command"), ("armor/electrical/electrical-1/command/extra", "command")]:
            with self.subTest(topic=topic, leaf=leaf), self.assertRaises(ContractError):
                parse_electrical_topic(topic, leaf)
        with self.assertRaises(ContractError):
            parse_electrical_topic("armor/electrical/electrical-1/set", "set")

    def test_a_command_must_agree_with_its_topic(self):
        validate_electrical_command("armor/electrical/electrical-1/command", self.command)
        for topic in ("armor/electrical/other/command", "armor/electrical/electrical-1/state", "armor/electrical/electrical-1/result"):
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                validate_electrical_command(topic, self.command)
        with self.assertRaises(ContractError):
            validate_electrical_command("armor/electrical/electrical-1/command", [self.command])

    def test_only_a_close_carries_a_token(self):
        token = "ab12cd34ef56ab12"
        for action in ("close_a", "close_b"):
            validate_electrical_command("armor/electrical/electrical-1/command", {**self.command, "action": action, "token": token})
            with self.assertRaises(ContractError):
                validate_electrical_command("armor/electrical/electrical-1/command", {**self.command, "action": action})
        for action in ("arm", "open", "acknowledge"):
            validate_electrical_command("armor/electrical/electrical-1/command", {**self.command, "action": action})
            with self.assertRaises(ContractError):
                validate_electrical_command("armor/electrical/electrical-1/command", {**self.command, "action": action, "token": token})

    def test_a_result_must_agree_with_its_topic_and_say_why_it_refused(self):
        validate_electrical_result("armor/electrical/electrical-1/result", self.result)
        with self.assertRaises(ContractError):
            validate_electrical_result("armor/electrical/other/result", self.result)
        with self.assertRaises(ContractError):
            validate_electrical_result("armor/electrical/electrical-1/command", self.result)
        refused = {**self.result, "action": "close_a", "accepted": False, "refusal": "not_armed"}
        validate_electrical_result("armor/electrical/electrical-1/result", refused)
        for bad in ({**refused, "refusal": "none"}, {**self.result, "refusal": "fault"}):
            with self.assertRaises(ContractError):
                validate_electrical_result("armor/electrical/electrical-1/result", bad)

    def test_only_an_accepted_arm_gives_a_token(self):
        token = "ab12cd34ef56ab12"
        arm = {**self.result, "action": "arm"}
        validate_electrical_result("armor/electrical/electrical-1/result", {**arm, "token": token})
        for bad in (arm, {**self.result, "token": token}, {**arm, "accepted": False, "refusal": "fault", "token": token}):
            with self.assertRaises(ContractError):
                validate_electrical_result("armor/electrical/electrical-1/result", bad)

    def test_a_switch_is_named_once_in_a_state_message(self):
        switch = {"id": "transfer", "kind": "transfer", "a_closed": True, "b_closed": False, "selected": "a", "wanted": "a", "closing": False, "armed": False, "fault": "none"}
        state = {"kind": "electrical", "node_id": "electrical-1", "timestamp_ms": 1, "channels": [], "switches": [switch]}
        validate_electrical_message("armor/electrical/electrical-1/state", state)
        with self.assertRaises(ContractError):
            validate_electrical_message("armor/electrical/electrical-1/state", {**state, "switches": [switch, dict(switch)]})


class NetworkMessageTests(unittest.TestCase):
    """The state of the local network as one ARMOR-NETWORK node sees it."""

    network = json.loads((CONFORMANCE / "network.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]
    topic = "armor/network/network-1/state"

    def test_the_topic_carries_the_node(self):
        self.assertEqual(parse_network_topic(self.topic), "network-1")
        for topic in ["armor/network/state", "armor/network/network-1/set", "armor/electrical/network-1/state", "armor/network/Node/state", "armor/network/-x/state",
                      "armor/network/" + "n" * 65 + "/state", "armor/network/network-1/state/extra", "armor/network//state"]:
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                parse_network_topic(topic)

    def test_a_message_must_agree_with_its_topic(self):
        validate_network_message(self.topic, self.network)
        with self.assertRaises(ContractError):
            validate_network_message("armor/network/other/state", self.network)
        with self.assertRaises(ContractError):
            validate_network_message(self.topic, [self.network])

    def test_the_rules_that_join_two_fields(self):
        device = self.network["devices"][0]
        event = self.network["events"][0]
        cases = {
            "a device named twice": {**self.network, "devices": [device, dict(device)]},
            "a MAC that is not the id": {**self.network, "devices": [{**device, "id": "aa:bb:cc:dd:ee:ff"}]},
            "first seen after last seen": {**self.network, "devices": [{**device, "first_seen_ms": 9, "last_seen_ms": 1}]},
            "an event named twice": {**self.network, "events": [event, dict(event)]},
            "an internet event about a device": {**self.network, "events": [{"id": "x1", "kind": "internet_down", "at_ms": 1, "device_id": device["id"]}]},
            "a device event with no device": {**self.network, "events": [{"id": "x2", "kind": "device_offline", "at_ms": 1}]},
            "a duration where there is no end": {**self.network, "events": [{**event, "id": "x3", "outage_s": 3}]},
            "a port event with no port": {**self.network, "events": [{**event, "id": "x4", "kind": "port_closed"}]},
        }
        for name, payload in cases.items():
            with self.subTest(name), self.assertRaises(ContractError):
                validate_network_message(self.topic, payload)
        # and the ones that look alike and are fine
        validate_network_message(self.topic, {**self.network, "events": [{"id": "x5", "kind": "internet_up", "at_ms": 1, "outage_s": 3}]})
        validate_network_message(self.topic, {**self.network, "devices": [{"id": "ip-192-168-0-9", "ip": "192.168.0.9", "online": True, "first_seen_ms": 1, "last_seen_ms": 1}]})


class TopicsWithoutAJsonObjectTests(unittest.TestCase):
    """The topics of a relay and of the panel's Zigbee feed, and what is published on armor/server/alert."""

    def test_the_topics_of_a_relay(self):
        for leaf in ("state", "availability", "set"):
            self.assertEqual(parse_device_topic(f"armor/device/electrical-1/lights/{leaf}"), ("electrical-1", "lights", leaf))
        for bad in ("armor/device/electrical-1/lights", "armor/device/electrical-1/lights/other", "armor/device/Upper/lights/state", "armor/device/electrical-1/Lights/state", "armor/device/electrical-1/lights/state/x", "armor/node/electrical-1/lights/state", "armor/device/electrical-1/" + "r" * 33 + "/state", "armor/device/electrical-1/lights\n/state"):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                parse_device_topic(bad)

    def test_what_a_relay_is_told_and_says(self):
        validate_device_message("armor/device/electrical-1/lights/state", {"on": True})
        for word in ("ON", "off", " Toggle ", "true", "False", "1", "0"):
            validate_device_message("armor/device/electrical-1/lights/set", word)
        for word in ("", "2", "dim", "ON\x00", "pulse 5", 1, True, None, {"on": True}):
            with self.subTest(word=word), self.assertRaises(ContractError):
                validate_device_message("armor/device/electrical-1/lights/set", word)
        validate_device_message("armor/device/electrical-1/lights/availability", "online")
        validate_device_message("armor/device/electrical-1/lights/availability", "offline")
        for word in ("Online", "up", "", None):
            with self.subTest(availability=word), self.assertRaises(ContractError):
                validate_device_message("armor/device/electrical-1/lights/availability", word)
        with self.assertRaises(ContractError):
            validate_device_message("armor/device/electrical-1/lights/state", "ON")

    def test_the_zigbee_feed_belongs_to_the_topic_of_a_panel(self):
        validate_alarm_zone_feed("armor/alarm/alarm-1/zigbee", {"zone": "front-door", "state": "normal", "battery_low": False})
        for bad_topic in ("armor/alarm/alarm-1/state", "armor/alarm/Alarm/zigbee", "armor/alarm/alarm-1/zigbee/x"):
            with self.subTest(topic=bad_topic), self.assertRaises(ContractError):
                validate_alarm_zone_feed(bad_topic, {"zone": "z", "state": "normal", "battery_low": False})
        # the leaf "zigbee" is not a leaf of the other alarm messages
        with self.assertRaises(ContractError):
            validate_alarm_message("armor/alarm/alarm-1/zigbee", {})

    def test_the_alert_goes_on_one_topic(self):
        message = {"service": "armor-server", "event": "alert.test", "at": "1970-01-01T00:00:00.000Z", "mode": "armed"}
        validate_server_alert("armor/server/alert", message)
        with self.assertRaises(ContractError):
            validate_server_alert("armor/server/other", message)

    def test_the_answer_of_the_network_orders_never_carries_a_login_in_clear(self):
        validate_network_orders({"accepted": True, "commands": []})
        with self.assertRaises(ContractError):
            validate_network_orders({"accepted": True, "commands": [{"id": "c1", "type": "inspect", "device_id": "d", "ip": "192.168.0.2", "auth": {"user": "admin", "password": "x"}}]})
        with self.assertRaises(ContractError):
            validate_network_orders([])


class NodeIdTests(unittest.TestCase):
    def test_a_node_id_is_limited_the_same_way_in_every_topic(self):
        self.assertEqual(parse_topic("armor/node/" + "a" * 64 + "/telemetry")[0], "a" * 64)
        for bad in ("a" * 65, "-lead", "_lead", "Upper", "line\n"):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                parse_topic(f"armor/node/{bad}/telemetry")


class PatternTests(unittest.TestCase):
    """A pattern means what JSON Schema (ECMA-262) says, which is what the server and the firmware apply."""

    def test_a_line_feed_at_the_end_is_not_the_end_of_the_text(self):
        schema = {"type": "string", "pattern": "^[a-z0-9]+$"}
        validate("abc", schema)
        for text in ("abc\n", "abc\r\n"):
            with self.subTest(text=text), self.assertRaises(SchemaError):
                validate(text, schema)

    def test_the_classes_are_ascii(self):
        schema = {"type": "string", "pattern": "^\\d+$"}
        validate("123", schema)
        with self.assertRaises(SchemaError):
            validate("\u0663\u0662", schema)   # Arabic-Indic digits

    def test_the_messages_that_carry_a_text_refuse_a_line_feed(self):
        with self.assertRaises(ContractError):
            validate_topic_and_payload("armor/node/north-1/info", {"node_id": "north-1", "timestamp_ms": 1, "name": "N", "firmware": "1.2.3\n", "ip": "10.0.0.1", "port": 80})
        with self.assertRaises(ContractError):
            validate_topic_and_payload("armor/node/north-1/info", {"node_id": "north-1", "timestamp_ms": 1, "name": "N", "firmware": "1.2.3", "ip": "10.0.0.1\n", "port": 80})
        with self.assertRaises(ContractError):
            validate_alarm_command("armor/alarm/alarm-1/command", {"kind": "alarm_command", "node_id": "alarm-1", "timestamp_ms": 1, "command_id": "0123456789abcdef\n", "action": "arm", "mode": "away"})

    def test_a_firmware_version_has_three_numbers_or_four(self):
        info = {"node_id": "north-1", "timestamp_ms": 1, "name": "N", "ip": "10.0.0.1", "port": 80}
        for good in ("0.7.9", "0.8.0.0", "0.8.1.3"):
            validate_topic_and_payload("armor/node/north-1/info", {**info, "firmware": good})
        for bad in ("0.8", "0.8.0.0.1", "v0.8.0", "0.8.0."):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                validate_topic_and_payload("armor/node/north-1/info", {**info, "firmware": bad})


class SchemaCheckTests(unittest.TestCase):
    """A schema that says something this validator would not check is refused, not ignored."""

    def test_the_forms_of_a_keyword_that_are_not_implemented_are_refused(self):
        for bad in ({"items": [{"type": "string"}]}, {"required": "x"}, {"enum": []}, {"type": "text"}, {"minimum": "1"}, {"maxItems": -1}, {"pattern": 5}, {"properties": []}, {"properties": {"a": 3}}):
            with self.subTest(bad=bad), self.assertRaises(UnsupportedSchema):
                check_schema(bad)
        check_schema({"type": ["string", "null"], "properties": {"a": {"type": "integer", "minimum": 0}}, "required": ["a"], "items": {"type": "string"}})

    def test_the_published_schema_a_caller_gets_is_its_own_copy(self):
        load_schema("health")["required"].append("tampered")
        self.assertNotIn("tampered", load_schema("health")["required"])
        validate_payload("health", {"node_id": "north-1", "timestamp_ms": 5, "online": True})

    def test_a_document_that_repeats_a_name_is_refused(self):
        with self.assertRaises(ValueError):
            decode('{"topic":"armor/node/a/health","payload":{"node_id":"a","timestamp_ms":1,"online":true,"online":false}}')
        topic, payload = decode(encode("armor/node/a/health", {"node_id": "a", "timestamp_ms": 1, "online": True}))
        self.assertEqual((topic, payload["online"]), ("armor/node/a/health", True))


class BatteryWriteTests(unittest.TestCase):
    """Writing to a Pylontech battery: the table of the operations, the topics and the rules that join fields."""

    def test_the_table_is_consistent(self):
        catalog = battery_catalog()
        ids = [item["id"] for item in catalog["ops"]]
        self.assertEqual(len(ids), len(set(ids)))
        schema_ops = load_schema("solar_battery_command")["properties"]["op"]["enum"]
        self.assertEqual(sorted(ids), sorted(schema_ops))
        schema_refusals = load_schema("solar_battery_result")["properties"]["refusal"]["enum"]
        self.assertEqual(sorted(catalog["refusals"]), sorted(schema_refusals))
        for item in catalog["ops"]:
            self.assertIn(item["risk"], ("low", "medium", "high", "irreversible"))
            if item["atomic"]:
                self.assertTrue(item["needs_idle"], item["id"])
            if item["risk"] == "irreversible":
                self.assertTrue(item["atomic"], item["id"])
        for group in catalog["limit_groups"]:
            keys = {key for key, _wire in group["keys"]}
            self.assertEqual(len(keys), len(group["keys"]))
            for low, high in group["orders"]:
                self.assertIn(low, keys)
                self.assertIn(high, keys)
            self.assertLess(group["lowest"], group["highest"])
        self.assertEqual({m["name"]: m["official_ah"] for m in catalog["models"] if m["official_ah"]}, {"US2000C": 50, "US3000C": 74, "UP5000": 100})
        self.assertNotIn("preflight", ids)

    def test_the_topics(self):
        self.assertEqual(parse_battery_topic("armor/solar/solar-1/maintenance/command", "command"), "solar-1")
        self.assertEqual(parse_battery_topic("armor/solar/solar-1/maintenance/result", "result"), "solar-1")
        for bad in ("armor/solar/solar-1/maintenance/state", "armor/solar/solar-1/inverter/command", "armor/solar/Solar 1/maintenance/command", "armor/solar/solar-1/maintenance", "armor/electrical/solar-1/maintenance/command"):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                parse_battery_topic(bad, "command")
        with self.assertRaises(ContractError):
            parse_battery_topic("armor/solar/solar-1/maintenance/command", "state")

    def test_a_command_must_match_its_topic(self):
        command = json.loads((CONFORMANCE / "solar_battery_command.json").read_text(encoding="utf-8"))["vectors"][0]["payload"]
        validate_solar_battery_command("armor/solar/solar-1/maintenance/command", command)
        with self.assertRaises(ContractError):
            validate_solar_battery_command("armor/solar/other/maintenance/command", command)
        with self.assertRaises(ContractError):
            validate_solar_battery_command("armor/solar/solar-1/maintenance/result", command)
        with self.assertRaises(ContractError):
            validate_solar_battery_command("armor/solar/solar-1/maintenance/command", [command])

    def test_params_are_checked_against_the_table(self):
        validate_battery_params("set_clock", {})
        validate_battery_params("output_set", {"output": "heat", "state": "on"})
        for op, params in (("set_clock", {"x": 1}), ("output_set", {}), ("nothing", {}), ("set_clock", [])):
            with self.subTest(op=op, params=params), self.assertRaises(ContractError):
                validate_battery_params(op, params)

    def test_the_expert_line(self):
        self.assertEqual(battery_expert_line("  bat   3 "), "bat 3")
        for bad in ("", "tbar x", "UPDATA", "eepe 0", "pwr;shut", "pwr\nshut", "help eepw", "a" * 49, 5, "café"):
            with self.subTest(bad=bad):
                self.assertEqual(battery_expert_line(bad), "")

    def test_the_service_password_has_no_field_anywhere(self):
        def names(node):
            if isinstance(node, dict):
                for key, child in node.get("properties", {}).items():
                    yield key
                    yield from names(child)
        for kind in ("solar_battery_command", "solar_battery_result"):
            self.assertEqual([name for name in names(load_schema(kind)) if "pass" in name.lower() or "secret" in name.lower() or "pin" == name.lower()], [], kind)


class NodeMaintenanceTests(unittest.TestCase):
    """The planned-maintenance signal: retained, one node's own topic, a window that ends carries no expected time."""

    signal = next(item["payload"] for item in json.loads((CONFORMANCE / "node_maintenance.json").read_text(encoding="utf-8"))["vectors"] if item["valid"])
    topic = "armor/control/radar-1/maintenance"

    def test_the_signal_is_whole_and_on_its_own_topic(self):
        validate_node_maintenance(self.topic, self.signal)
        for topic in ("armor/control/radar-2/maintenance", "armor/control/all/maintenance", "armor/control/radar-1/result", "armor/control/radar-1/maintenance/x"):
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                validate_node_maintenance(topic, self.signal)

    def test_a_window_that_ends_has_no_expected_time(self):
        validate_node_maintenance(self.topic, {k: v for k, v in self.signal.items() if k != "expected_s"} | {"active": False})
        with self.assertRaises(ContractError):
            validate_node_maintenance(self.topic, {**self.signal, "active": False})

    def test_every_reason_is_a_word_of_the_list(self):
        for reason in ("restart", "pause", "standby", "update", "upload", "operator"):
            validate_node_maintenance(self.topic, {**self.signal, "reason": reason})
        for reason in ("deep_sleep", "factory_reset", ""):
            with self.subTest(reason=reason), self.assertRaises(ContractError):
                validate_node_maintenance(self.topic, {**self.signal, "reason": reason})


class NodeControlTests(unittest.TestCase):
    """Controlling a node: two steps, a token that belongs to one node and one operation, a broadcast that only arms, ranges per operation, and an answer that says what it is."""

    commands = json.loads((CONFORMANCE / "node_control_command.json").read_text(encoding="utf-8"))["vectors"]
    results = json.loads((CONFORMANCE / "node_control_result.json").read_text(encoding="utf-8"))["vectors"]
    arm = commands[0]["payload"]
    armed = results[0]["payload"]
    token = "0123456789abcdef0123456789abcdef"
    operations = ("restart", "pause", "resume", "standby", "identify", "diagnostics", "maintenance_on", "maintenance_off")

    def command(self, **changes):
        return {**self.arm, **changes}

    def execute(self, **changes):
        return {**self.arm, "action": "execute", "token": self.token, **changes}

    def test_the_topics_name_the_node_and_the_direction(self):
        self.assertEqual(parse_control_topic("armor/control/radar-1/command", "command"), "radar-1")
        self.assertEqual(parse_control_topic("armor/control/all/command", "command"), "all")
        for topic, leaf in [("armor/control/radar-1/result", "command"), ("armor/control/radar-1/command", "result"), ("armor/control/all/result", "result"), ("armor/control/Radar/command", "command"),
                            ("armor/control/radar-1", "command"), ("armor/control/radar-1/command/x", "command"), ("armor/node/radar-1/command", "command"), ("armor/restart/radar-1/command", "command")]:
            with self.subTest(topic=topic), self.assertRaises(ContractError):
                parse_control_topic(topic, leaf)
        with self.assertRaises(ContractError):
            parse_control_topic("armor/control/radar-1/command", "state")

    def test_the_node_must_be_the_one_of_the_topic(self):
        validate_node_control_command("armor/control/radar-1/command", self.arm)
        validate_node_control_result("armor/control/radar-1/result", self.armed)
        with self.assertRaises(ContractError):
            validate_node_control_command("armor/control/radar-2/command", self.arm)
        with self.assertRaises(ContractError):
            validate_node_control_result("armor/control/radar-2/result", self.armed)
        with self.assertRaises(ContractError):
            validate_node_control_command("armor/control/radar-1/result", self.arm)

    def test_a_broadcast_arms_and_never_executes(self):
        for operation in self.operations:
            with self.subTest(operation=operation):
                validate_node_control_command("armor/control/all/command", self.command(node_id="all", operation=operation))
                with self.assertRaises(ContractError):
                    validate_node_control_command("armor/control/all/command", self.execute(node_id="all", operation=operation))

    def test_every_operation_can_be_armed_and_executed(self):
        for operation in self.operations:
            with self.subTest(operation=operation):
                validate_node_control_command("armor/control/radar-1/command", self.command(operation=operation))
                validate_node_control_command("armor/control/radar-1/command", self.execute(operation=operation))

    def test_there_is_no_operation_that_erases_or_sleeps(self):
        for operation in ("factory_reset", "erase", "reset", "wipe", "format", "wipe_wifi", "deep_sleep", "radio_sleep", "sleep", "wake"):
            with self.subTest(operation=operation), self.assertRaises(ContractError):
                validate_node_control_command("armor/control/radar-1/command", self.command(operation=operation))
        for action in ("factory_reset", "erase", "wipe"):
            with self.subTest(action=action), self.assertRaises(ContractError):
                validate_node_control_command("armor/control/radar-1/command", self.command(action=action))
        for name in ("wake_after_s", "wake_timer_s", "sleep_s", "wake_s"):
            with self.subTest(field=name), self.assertRaises(ContractError):
                validate_node_control_command("armor/control/radar-1/command", self.execute(operation="standby", **{name: 600}))
        schema = load_schema("node_control_command")
        self.assertEqual(schema["properties"]["action"]["enum"], ["arm", "execute"])
        self.assertEqual(list(schema["properties"]["operation"]["enum"]), list(self.operations))
        self.assertIs(schema["additionalProperties"], False)
        for kind in ("node_control_command", "node_control_result"):
            names = list(load_schema(kind)["properties"]) + list(load_schema(kind)["properties"].get("operation", {}).get("enum", []))
            self.assertEqual([name for name in names if any(word in name for word in ("sleep", "wake", "erase", "wipe", "factory", "format"))], [], kind)

    def test_the_rolling_mode_is_for_a_restart_only(self):
        validate_node_control_command("armor/control/radar-1/command", self.execute(mode="rolling", slot=3, delay_s=10))
        for operation in self.operations[1:]:
            with self.subTest(operation=operation), self.assertRaises(ContractError):
                validate_node_control_command("armor/control/radar-1/command", self.command(operation=operation, mode="rolling"))
        with self.assertRaises(ContractError):
            validate_node_control_command("armor/control/radar-1/command", self.execute(slot=1))
        for operation in self.operations[1:]:
            with self.subTest(delay=operation), self.assertRaises(ContractError):
                validate_node_control_command("armor/control/radar-1/command", self.execute(operation=operation, delay_s=5))

    def test_durations_are_those_of_their_operation(self):
        ranges = {"pause": (60, 3600), "identify": (5, 300), "maintenance_on": (60, 28800)}
        for operation, (low, high) in ranges.items():
            for value in (low, (low + high) // 2, high):
                with self.subTest(operation=operation, value=value):
                    validate_node_control_command("armor/control/radar-1/command", self.execute(operation=operation, duration_s=value))
            for value in (low - 1, high + 1):
                with self.subTest(operation=operation, wrong=value), self.assertRaises(ContractError):
                    validate_node_control_command("armor/control/radar-1/command", self.execute(operation=operation, duration_s=value))
            with self.subTest(arm=operation), self.assertRaises(ContractError):
                validate_node_control_command("armor/control/radar-1/command", self.command(operation=operation, duration_s=low))
        for operation in ("restart", "resume", "standby", "diagnostics", "maintenance_off"):
            with self.subTest(none=operation), self.assertRaises(ContractError):
                validate_node_control_command("armor/control/radar-1/command", self.execute(operation=operation, duration_s=60))

    def test_a_token_goes_on_an_execute_only(self):
        with self.assertRaises(ContractError):
            validate_node_control_command("armor/control/radar-1/command", self.command(token=self.token))
        with self.assertRaises(ContractError):
            validate_node_control_command("armor/control/radar-1/command", {k: v for k, v in self.execute().items() if k != "token"})

    def answer(self, name):
        return next(item["payload"] for item in self.results if item["name"] == name)

    def test_each_answer_is_whole(self):
        for item in self.results:
            if item["valid"]:
                with self.subTest(item["name"]):
                    validate_node_control_result("armor/control/radar-1/result", item["payload"])
        going = self.answer("the node is restarting now")
        for name in ("uptime_s", "firmware", "reason", "restart_in_s", "mode", "requested_by"):
            with self.subTest(missing=name), self.assertRaises(ContractError):
                validate_node_control_result("armor/control/radar-1/result", {k: v for k, v in going.items() if k != name})
        applied = self.answer("a pause applied")
        for name in ("state", "maintenance", "requested_by"):
            with self.subTest(missing=name), self.assertRaises(ContractError):
                validate_node_control_result("armor/control/radar-1/result", {k: v for k, v in applied.items() if k != name})

    def test_a_snapshot_has_no_room_for_a_secret(self):
        snapshot = load_schema("node_control_result")["properties"]["diagnostics"]
        self.assertIs(snapshot["additionalProperties"], False)
        self.assertEqual([name for name in snapshot["properties"] if any(word in name for word in ("pass", "secret", "token", "key", "psk"))], [])

    def test_the_health_report_says_what_the_node_is_doing(self):
        health = {"kind": "node_health", "node_id": "radar-1", "timestamp_ms": 9, "family": "radar", "firmware": "0.7.7", "uptime_s": 5, "reset_reason": "power_on", "heap_free": 9, "heap_min": 9,
                  "link": "ethernet", "link_up": True, "broker_reconnects": 1}
        validate_node_health("armor/health/radar-1", health)
        validate_node_health("armor/health/radar-1", {**health, "control_state": "standby", "control_since_ms": 1, "control_by": "ana", "maintenance": True, "maintenance_until_s": 60})
        validate_node_health("armor/health/radar-1", {**health, "control_state": "paused", "control_since_ms": 1, "control_by": "ana", "control_until_s": 60})
        for extra in ({"control_state": "running", "control_by": "ana"}, {"control_state": "standby", "control_until_s": 60}, {"maintenance_until_s": 60}, {"control_state": "asleep"}):
            with self.subTest(extra=extra), self.assertRaises(ContractError):
                validate_node_health("armor/health/radar-1", {**health, **extra})
