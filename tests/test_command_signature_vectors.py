"""The signed critical commands, as the shared vectors fix them: the key of a node, the bytes that are signed and the signature, checked here with the standard library so that a node (or the server) that computes them differently is told apart."""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import unittest
from pathlib import Path

VECTORS = json.loads((Path(__file__).resolve().parents[1] / "conformance" / "signatures" / "command.json").read_text(encoding="utf-8"))
ENDING = re.compile(r'^(.*),"sig":"([0-9a-f]{64})"\}$', re.S)


def verifies(payload: str, node_key: str) -> bool:
    """What a node does: cut the ending, put the brace back, HMAC the prefix and the body, compare."""
    match = ENDING.match(payload)
    if not match:
        return False
    body = match.group(1) + "}"
    expected = hmac.new(bytes.fromhex(node_key), ("armor-command-v2|" + body).encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, match.group(2))


class CommandSignatureVectors(unittest.TestCase):
    def test_the_key_of_a_node_comes_from_the_master_key_and_its_id(self) -> None:
        for case in VECTORS["cases"]:
            expected = hmac.new(bytes.fromhex(VECTORS["master_key"]), f"node|{case['node_id']}".encode(), hashlib.sha256).hexdigest()
            self.assertEqual(case["node_key"], expected, case["name"])
        self.assertEqual(len({case["node_key"] for case in VECTORS["cases"]}), 2, "two nodes, two keys; the same node, the same key")

    def test_every_signed_payload_verifies_with_the_key_of_its_node_and_has_the_nonce_last_before_the_signature(self) -> None:
        for case in VECTORS["cases"]:
            self.assertTrue(verifies(case["payload"], case["node_key"]), case["name"])
            self.assertEqual(case["payload"], case["body"][:-1] + ',"sig":"' + case["sig"] + '"}')
            self.assertRegex(case["body"], r'"nonce":"[0-9a-f]{16}"\}$')
            self.assertEqual(json.loads(case["payload"])["node_id"], case["node_id"])

    def test_a_payload_signed_for_another_node_or_changed_in_any_byte_does_not_verify(self) -> None:
        for refused in VECTORS["refused"]:
            self.assertFalse(verifies(refused["payload"], refused["node_key"]), refused["name"])
        case = VECTORS["cases"][0]
        for index in range(len(case["body"]) - 1):
            changed = case["payload"][:index] + chr(ord(case["payload"][index]) ^ 1) + case["payload"][index + 1:]
            self.assertFalse(verifies(changed, case["node_key"]), index)
        self.assertFalse(verifies(case["payload"], VECTORS["cases"][2]["node_key"]), "the key of another node")


if __name__ == "__main__":
    unittest.main()
