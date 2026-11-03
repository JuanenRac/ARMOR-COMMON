"""The text of the provisioning QR code holds a node id and a server address and can never hold a secret."""
import json
import unittest

from armor_common.contracts import ContractError
from armor_common.provisioning import PREFIX, build_provisioning, parse_provisioning


class ProvisioningTests(unittest.TestCase):
    def test_round_trip(self):
        text = build_provisioning("radar-1", "https://armor.local:8443/")
        self.assertTrue(text.startswith(PREFIX + ":"))
        self.assertEqual(parse_provisioning(text), {"v": 1, "node_id": "radar-1", "server": "https://armor.local:8443"})

    def test_plain_http_on_a_lan_address_is_allowed(self):
        self.assertEqual(parse_provisioning(build_provisioning("a1", "http://192.168.0.180:18080"))["server"], "http://192.168.0.180:18080")

    def test_bad_node_ids_are_refused(self):
        for node_id in ("", "-x", "Radar", "a b", "x" * 65):
            with self.assertRaises(ContractError, msg=node_id):
                build_provisioning(node_id, "https://armor.local")

    def test_addresses_that_could_hold_a_secret_are_refused(self):
        for server in ("https://user:pw@armor.local", "https://user@armor.local", "https://armor.local/?token=x", "https://armor.local/#x",
                       "https://armor.local/api", "ftp://armor.local", "armor.local", "https://", "https://armor.local:99999", "https://armor .local", ""):
            with self.assertRaises(ContractError, msg=server):
                build_provisioning("radar-1", server)

    def test_the_reader_refuses_extra_or_missing_fields_and_other_versions(self):
        good = {"v": 1, "node_id": "radar-1", "server": "https://armor.local"}
        for bad in (dict(good, token="x"), {k: v for k, v in good.items() if k != "server"}, dict(good, v=2), dict(good, v=True), dict(good, node_id=5)):
            with self.assertRaises(ContractError, msg=str(bad)):
                parse_provisioning(PREFIX + ":" + json.dumps(bad))

    def test_the_reader_refuses_other_text(self):
        for bad in (None, 5, "", "armor-provision:", "armor-provision:{", "armor-provision:[]", "other:{}", PREFIX + ":" + "x" * 600):
            with self.assertRaises(ContractError, msg=str(bad)):
                parse_provisioning(bad)


if __name__ == "__main__":
    unittest.main()
