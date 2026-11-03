"""The table of broker identities: sound, and a node never gets a line that lets it command another."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from armor_common import node_roles  # noqa: E402


class NodeRolesTests(unittest.TestCase):
    def test_every_role_has_a_user_and_valid_lines(self):
        self.assertEqual(sorted(node_roles.roles()), sorted(["node", "hmi-node", "solar-node", "electrical-node", "alarm-node", "network-node", "device", "bridge", "consumer"]))
        for role in node_roles.roles():
            self.assertTrue(node_roles.user_for(role, "x1").endswith("x1"))
            for line in node_roles.acl_lines(role, "x1"):
                kind, access, topic = line.split(" ", 2)
                self.assertEqual(kind, "topic")
                self.assertIn(access, ("read", "write", "readwrite"))
                self.assertTrue(topic.startswith("armor/"))

    def test_no_node_can_write_an_order_topic(self):
        for role in ("node", "hmi-node", "solar-node", "electrical-node", "alarm-node", "network-node"):
            for line in node_roles.acl_lines(role, "x1"):
                if " write " in line or " readwrite " in line:
                    self.assertNotIn("/command", line, f"{role}: {line}")

    def test_a_node_writes_only_under_its_own_name(self):
        for role in ("node", "hmi-node", "solar-node", "electrical-node", "alarm-node", "network-node"):
            for line in node_roles.acl_lines(role, "x1"):
                if " write " in line or " readwrite " in line:
                    self.assertTrue("/x1" in line or line.endswith("armor/control/x1/maintenance"), f"{role}: {line}")

    def test_a_bad_name_is_refused(self):
        with self.assertRaises(ValueError):
            node_roles.acl_lines("node", "../x")


if __name__ == "__main__":
    unittest.main()
