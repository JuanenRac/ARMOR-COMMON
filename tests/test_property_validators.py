"""Property-based tests of the critical validators: topic and node id, the command rules, the ranges and enums every schema states, and the decoder of untrusted lines.

The cases come from a small generator with a FIXED seed (``random.Random``), so a run is the same everywhere and no test dependency is needed; the number of cases per
property is bounded to keep the whole file in a few seconds.
"""
import copy
import json
import random
import unittest
from pathlib import Path

from armor_common import ContractError, decode, encode, validate_node_control_command, validate_topic_and_payload
from armor_common.contracts import CONTROL_DURATIONS, load_schema, parse_topic, validate_payload

CONFORMANCE = Path(__file__).resolve().parent.parent / "conformance"
SEED = 7001
NODE_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789-_"
ALPHABET = NODE_CHARS + "ABC /.é\u0000\n+#"


def rng(name):
    return random.Random(f"{SEED}:{name}")


def is_valid_node_id(text):
    return 0 < len(text) <= 64 and text[0] not in "-_" and set(text) <= set(NODE_CHARS)


def command(node="north-1", name="restart", **extra):
    return {"node_id": node, "timestamp_ms": 5, "command": name, **extra}


class TopicAndNodeId(unittest.TestCase):
    def test_a_topic_is_accepted_exactly_when_it_has_the_shape_and_a_valid_node_id(self):
        r = rng("topic")
        for _ in range(1500):
            node = "".join(r.choice(ALPHABET) for _ in range(r.choice([0, 1, 2, 5, 63, 64, 65, 80])))
            kind = r.choice(["command", "telemetry", "health", "info", "other", ""])
            topic = r.choice([f"armor/node/{node}/{kind}", f"armor/nodes/{node}/{kind}", f"armor/node/{node}/{kind}/x", f"Armor/node/{node}/{kind}"])
            expected = topic == f"armor/node/{node}/{kind}" and is_valid_node_id(node) and kind in ("telemetry", "health", "command", "info") and "/" not in node
            try:
                parsed = parse_topic(topic)
            except ContractError:
                self.assertFalse(expected, topic)
            else:
                self.assertTrue(expected, topic)
                self.assertEqual(parsed, (node, kind))

    def test_node_id_length_boundary(self):
        for length in (1, 63, 64, 65, 100):
            topic = "armor/node/" + "a" * length + "/command"
            if length <= 64:
                self.assertEqual(parse_topic(topic)[0], "a" * length)
            else:
                with self.assertRaises(ContractError):
                    parse_topic(topic)
        for bad in ("-a", "_a", "", "A", "a b", "a/b", "a\n", "á"):
            with self.assertRaises(ContractError):
                parse_topic(f"armor/node/{bad}/command")

    def test_the_payload_node_id_must_equal_the_topic_one(self):
        r = rng("mismatch")
        for _ in range(300):
            a = "".join(r.choice(NODE_CHARS[:26]) for _ in range(r.randrange(1, 8)))
            b = "".join(r.choice(NODE_CHARS[:26]) for _ in range(r.randrange(1, 8)))
            if a != b:
                with self.assertRaises(ContractError):
                    validate_topic_and_payload(f"armor/node/{a}/command", command(b))
            validate_topic_and_payload(f"armor/node/{a}/command", command(a))


class CommandRules(unittest.TestCase):
    def test_sensitivity_is_accepted_only_on_set_thresholds_and_only_from_one_to_ten(self):
        r = rng("sensitivity")
        for _ in range(600):
            name = r.choice(["calibrate", "set_thresholds", "restart", "reboot", "", "SET_THRESHOLDS"])
            value = r.choice([r.randrange(-5, 20), 0, 1, 10, 11, 1.0, 5.5, True, False, "5", None, 2 ** 70])
            topic = "armor/node/north-1/command"
            # JSON Schema counts 1.0 as the integer 1 (the schema says "integer"), so a whole float is accepted; a boolean never is
            valid = name == "set_thresholds" and type(value) in (int, float) and value == int(value) and 1 <= value <= 10
            try:
                validate_topic_and_payload(topic, command(name=name, sensitivity=value))
            except ContractError:
                self.assertFalse(valid, (name, value))
            else:
                self.assertTrue(valid, (name, value))

    def test_only_the_three_commands_exist(self):
        r = rng("commands")
        for _ in range(300):
            name = "".join(r.choice(ALPHABET) for _ in range(r.randrange(0, 14)))
            valid = name in ("calibrate", "set_thresholds", "restart")
            try:
                validate_topic_and_payload("armor/node/north-1/command", command(name=name))
            except ContractError:
                self.assertFalse(valid, name)
            else:
                self.assertTrue(valid, name)

    def test_a_control_duration_is_inside_the_range_of_its_operation(self):
        base = next(v["payload"] for v in json.loads((CONFORMANCE / "node_control_command.json").read_text(encoding="utf-8"))["vectors"]
                    if v["valid"] and v["payload"].get("action") == "execute" and "token" in v["payload"])
        r = rng("duration")
        topic = f"armor/control/{base['node_id']}/command"
        for _ in range(600):
            operation = r.choice(sorted(CONTROL_DURATIONS) + ["restart", "resume", "standby"])
            payload = dict(base, operation=operation, duration_s=r.choice([r.randrange(-10, 40000), 4, 5, 60, 300, 301, 3600, 3601, 28800, 28801]))
            for key in ("delay_s", "slot", "detail"):
                payload.pop(key, None)
            span = CONTROL_DURATIONS.get(operation)
            valid = span is not None and span[0] <= payload["duration_s"] <= span[1]
            try:
                validate_node_control_command(topic, payload)
            except ContractError:
                self.assertFalse(valid, payload)
            else:
                self.assertTrue(valid, payload)


def number_rules(schema):
    for name, rule in schema.get("properties", {}).items():
        kind = rule.get("type")
        if kind in ("integer", "number") and ("minimum" in rule or "maximum" in rule):
            yield name, rule


class SchemaRanges(unittest.TestCase):
    def test_no_value_outside_a_stated_range_or_enum_is_accepted_and_the_limits_are(self):
        checked = 0
        for file in sorted(CONFORMANCE.glob("*.json")):
            document = json.loads(file.read_text(encoding="utf-8"))
            kind = document.get("kind")
            if not kind or "vectors" not in document:
                continue
            schema = load_schema(kind)
            valid = [v["payload"] for v in document["vectors"] if v["valid"]]
            if not valid:
                continue
            for name, rule in number_rules(schema):
                for source in valid:
                    if name not in source:
                        continue
                    for outside in ([rule["minimum"] - 1] if "minimum" in rule else []) + ([rule["maximum"] + 1] if "maximum" in rule else []):
                        if rule["type"] == "integer" and outside != int(outside):
                            continue
                        with self.assertRaises(ContractError, msg=f"{kind}.{name}={outside}"):
                            validate_payload(kind, dict(copy.deepcopy(source), **{name: outside}))
                        checked += 1
                    for inside in [rule[key] for key in ("minimum", "maximum") if key in rule]:
                        validate_payload(kind, dict(copy.deepcopy(source), **{name: inside}))
                        checked += 1
                    break
            for name, rule in schema.get("properties", {}).items():
                if "enum" in rule and all(isinstance(item, str) for item in rule["enum"]):
                    for source in valid:
                        if name in source:
                            with self.assertRaises(ContractError, msg=f"{kind}.{name}"):
                                validate_payload(kind, dict(copy.deepcopy(source), **{name: "not-in-the-list"}))
                            checked += 1
                            break
        self.assertGreater(checked, 150)

    def test_a_boolean_or_text_is_never_taken_for_a_number(self):
        for file in sorted(CONFORMANCE.glob("*.json")):
            document = json.loads(file.read_text(encoding="utf-8"))
            kind = document.get("kind")
            if not kind or "vectors" not in document:
                continue
            schema = load_schema(kind)
            valid = [v["payload"] for v in document["vectors"] if v["valid"]]
            for name, _rule in number_rules(schema):
                for source in valid:
                    if name in source:
                        for odd in (True, False, "5", None, [], {}):
                            with self.assertRaises(ContractError, msg=f"{kind}.{name}={odd!r}"):
                                validate_payload(kind, dict(copy.deepcopy(source), **{name: odd}))
                        break


class UntrustedLines(unittest.TestCase):
    def test_decode_answers_with_a_value_error_for_any_text(self):
        r = rng("decode")
        good = encode("armor/node/north-1/command", command())
        pieces = ['{"topic":', '"armor/node/north-1/command"', ',"payload":', '{"node_id":"north-1","timestamp_ms":5,"command":"restart"}', "}", "[", "]", "{", "null", "1e999", "NaN", '"\\ud800"', "\u0000", " "]
        for _ in range(2000):
            if r.random() < 0.5:
                text = "".join(r.choice(pieces) for _ in range(r.randrange(0, 9)))
            else:
                chars = list(good)
                for _ in range(r.randrange(1, 4)):
                    chars[r.randrange(len(chars))] = chr(r.choice([r.randrange(32, 127), 0, 0xD800, 0x20AC, 10]))
                text = "".join(chars[: r.choice([len(chars), r.randrange(0, len(chars))])])
            try:
                topic, payload = decode(text)
            except ValueError:
                continue                       # ContractError is a ValueError: the foreseen answer
            validate_topic_and_payload(topic, payload)   # whatever it accepts is a valid message

    def test_a_deeply_nested_line_is_a_value_error_not_a_recursion_error(self):
        for depth in (500, 5000, 200000):
            for line in ('{"topic":"a","payload":' + "[" * depth + "]" * depth + "}", "[" * depth, '{"topic":"a","payload":{"x":' + '{"y":' * depth + "1" + "}" * depth + "}}"):
                with self.assertRaises(ValueError):
                    decode(line)

    def test_a_repeated_name_is_refused(self):
        with self.assertRaises(ValueError):
            decode('{"topic":"armor/node/a/command","topic":"armor/node/b/command","payload":{}}')
        with self.assertRaises(ValueError):
            decode('{"topic":"armor/node/a/command","payload":{"node_id":"a","node_id":"b","timestamp_ms":1,"command":"restart"}}')

    def test_a_structured_fuzz_of_a_valid_command_is_accepted_or_a_contract_error(self):
        r = rng("structured")
        odd = [None, True, 0, -1, 2 ** 70, 1.5, "", "x" * 3000, "\u0000", [], {}, [[]], {"a": None}]
        for _ in range(1500):
            payload = command(name=r.choice(["restart", "set_thresholds"]), sensitivity=r.randrange(1, 11))
            for _ in range(r.randrange(1, 4)):
                key = r.choice(list(payload) + ["extra", "kind"])
                action = r.choice(["set", "set", "drop"])
                if action == "drop":
                    payload.pop(key, None)
                else:
                    payload[key] = r.choice(odd)
            topic = r.choice(["armor/node/north-1/command", "armor/node/north-1/command", "armor/node//command", "", None, 5])
            try:
                validate_topic_and_payload(topic, payload)
            except ContractError:
                continue
            self.assertEqual(topic, "armor/node/north-1/command")
            self.assertEqual(payload["node_id"], "north-1")
            self.assertTrue(type(payload["timestamp_ms"]) is int and payload["timestamp_ms"] >= 0)
            self.assertIn(payload["command"], ("calibrate", "set_thresholds", "restart"))
            self.assertTrue("sensitivity" not in payload or (payload["command"] == "set_thresholds" and 1 <= payload["sensitivity"] <= 10))
            self.assertLessEqual(set(payload), {"kind", "node_id", "timestamp_ms", "command", "sensitivity"})


class ReasonsAndLimits(unittest.TestCase):
    """Added after a mutation run: the reason a message is refused is part of the contract (the readers show it), and the character set is used up to its last member."""

    def refusal(self, topic, payload=None):
        with self.assertRaises(ContractError) as caught:
            validate_topic_and_payload(topic, payload if payload is not None else command())
        return str(caught.exception)

    def test_each_refusal_says_why(self):
        self.assertEqual(self.refusal(5), "topic must be a string")
        self.assertEqual(self.refusal("armor/node/x"), "topic must be armor/node/{node_id}/{kind}")
        self.assertEqual(self.refusal("armor/node/-x/command"), "node_id must use lowercase letters, digits, '-' or '_'")
        self.assertEqual(self.refusal("armor/node/north-1/other"), "unsupported topic kind")
        self.assertEqual(self.refusal("armor/node/north-1/command", [1]), "payload must be an object")
        self.assertEqual(self.refusal("armor/node/north-1/command", command("south")), "payload node_id must match the topic")
        self.assertEqual(self.refusal("armor/node/north-1/command", command(name="restart", sensitivity=5)), "sensitivity belongs only to the command set_thresholds")

    def test_a_node_id_may_use_every_character_of_the_set_at_once(self):
        every = "a" + NODE_CHARS
        self.assertEqual(parse_topic(f"armor/node/{every}/command")[0], every)
        for lead in "-_":
            with self.assertRaises(ContractError):
                parse_topic(f"armor/node/{lead}{every}/command")


if __name__ == "__main__":
    unittest.main()
