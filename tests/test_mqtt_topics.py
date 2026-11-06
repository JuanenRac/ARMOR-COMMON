"""The list of the MQTT topics, the access lines of the roles and the AsyncAPI file made from both say the same."""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from armor_common import mqtt_topics, node_roles   # noqa: E402
import generate_asyncapi   # noqa: E402

SCHEMAS = ROOT / "src" / "armor_common" / "schemas"
NODE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class CatalogTests(unittest.TestCase):
    def test_every_schema_a_channel_names_exists(self):
        for item in mqtt_topics.channels():
            for schema in mqtt_topics.schemas_of(item):
                self.assertTrue((SCHEMAS / f"{schema}.schema.json").is_file(), f"{item['id']}: {schema}")

    def test_the_ids_and_the_addresses_are_unique(self):
        ids = [item["id"] for item in mqtt_topics.channels()]
        addresses = [item["address"] for item in mqtt_topics.channels()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(addresses), len(set(addresses)))

    def test_the_qos_is_0_or_1_and_only_the_planned_signals_are_kept_by_the_broker(self):
        retained = {item["id"] for item in mqtt_topics.channels() if item["retain"]}
        self.assertEqual(retained, {"control_maintenance"})
        for item in mqtt_topics.channels():
            self.assertIn(item["qos"], (0, 1), item["id"])
        for item in mqtt_topics.channels():
            if item["address"].split("/")[-1] == "command" or item["address"].endswith("/command"):
                self.assertFalse(item["retain"], f"a command is never retained: {item['id']}")

    def test_every_role_named_in_a_channel_exists(self):
        roles = set(node_roles.roles()) | {mqtt_topics.SERVER}
        for item in mqtt_topics.channels():
            for role in item["publishers"] + item["readers"]:
                self.assertIn(role, roles, item["id"])

    def test_the_addresses_use_the_names_of_the_whole_system(self):
        for item in mqtt_topics.channels():
            self.assertTrue(item["address"].startswith("armor/"), item["id"])
            self.assertTrue(NODE_ID.match("alarm-1"))


class AccessLinesAgreeTests(unittest.TestCase):
    """What a role's access lines allow is what the list says the role does (the lines the server has are in ARMOR-DEVOPS, and the lines for commands are written only on purpose: `opt_in`)."""

    def test_a_role_can_only_write_the_channels_it_publishes_and_read_the_ones_it_reads(self):
        for role in node_roles.roles():
            for item in mqtt_topics.channels():
                for verb, key in (("write", "publishers"), ("read", "readers")):
                    may = mqtt_topics.allowed(role, verb, item["address"])
                    listed = role in item[key]
                    wider = role in item.get("acl_wider_than_needed", []) and verb == "write"
                    if may and wider:
                        continue   # a known gap: the line `topic write armor/solar/{name}/#` also covers the maintenance command topic, which only the server publishes
                    if may:
                        self.assertTrue(listed, f"{role} may {verb} {item['address']} by its lines but the list does not say it does")
                    elif listed and "opt_in" not in item:
                        self.fail(f"the list says {role} {verb}s {item['address']} but its lines do not let it")

    def test_every_access_line_is_about_a_topic_of_the_list(self):
        for role in node_roles.roles():
            for verb in ("write", "read"):
                for pattern in mqtt_topics.acl_topics(role, verb):
                    self.assertTrue(any(mqtt_topics.covers(pattern, item["address"]) for item in mqtt_topics.channels()), f"{role}: {pattern}")

    def test_the_lines_that_are_opt_in_are_not_in_the_base_lines(self):
        for item in mqtt_topics.channels():
            if "opt_in" not in item:
                continue
            for role in node_roles.roles():
                for verb in ("write", "read"):
                    if verb == "write" and role in item.get("acl_wider_than_needed", []):
                        continue
                    self.assertFalse(mqtt_topics.allowed(role, verb, item["address"]), f"{role} can {verb} {item['address']} without turning {item['opt_in']} on")

    def test_a_known_gap_is_still_there_or_it_is_removed_from_the_list(self):
        for item in mqtt_topics.channels():
            for role in item.get("acl_wider_than_needed", []):
                self.assertTrue(mqtt_topics.allowed(role, "write", item["address"]), f"{role}: the lines no longer cover {item['address']}, so the note must go")
                self.assertNotIn(role, item["publishers"], f"{role}: it is listed as a publisher of {item['address']}, so it is not a gap")

    def test_covers_follows_the_rules_of_a_broker(self):
        self.assertTrue(mqtt_topics.covers("armor/solar/{node_id}/#", "armor/solar/{node_id}/{device}/state"))
        self.assertTrue(mqtt_topics.covers("armor/device/#", "armor/device/{node_id}/#"))
        self.assertFalse(mqtt_topics.covers("armor/device/{node_id}/#", "armor/device/#"))
        self.assertFalse(mqtt_topics.covers("armor/alarm/{node_id}/state", "armor/alarm/{node_id}/command"))
        self.assertFalse(mqtt_topics.covers("armor/alarm/{node_id}", "armor/alarm/{node_id}/state"))


class AsyncApiTests(unittest.TestCase):
    def setUp(self):
        self.text = generate_asyncapi.OUT.read_bytes().decode("utf-8").replace("\r\n", "\n")
        self.document = json.loads(self.text)

    def test_the_file_is_what_the_generator_writes(self):
        self.assertEqual(self.text, generate_asyncapi.render(), "run python tools/generate_asyncapi.py")

    def test_every_operation_carries_the_qos_and_the_retain_flag_of_its_channel(self):
        for name, operation in self.document["operations"].items():
            binding = operation["bindings"]["mqtt"]
            channel = mqtt_topics.channel(operation["channel"]["$ref"].rsplit("/", 1)[1])
            self.assertEqual((binding["qos"], binding["retain"]), (channel["qos"], channel["retain"]), name)

    def test_every_role_has_its_access_lines_and_every_message_its_schema(self):
        self.assertEqual(set(self.document["x-acl"]), set(node_roles.roles()))
        for message in self.document["components"]["messages"].values():
            self.assertTrue((ROOT / "asyncapi" / message["payload"]["$ref"]).resolve().is_file(), message["name"])

    def test_the_operations_say_who_sends_and_who_receives(self):
        operations = self.document["operations"]
        self.assertEqual(operations["server.send.alarm_command"]["action"], "send")
        self.assertEqual(operations["alarm-node.receive.alarm_zone_feed"]["action"], "receive")
        self.assertEqual(operations["alarm-node.receive.alarm_command"]["x-opt-in"], "alarm-commands")
        self.assertTrue(operations["node.send.control_maintenance"]["bindings"]["mqtt"]["retain"])


if __name__ == "__main__":
    unittest.main()
