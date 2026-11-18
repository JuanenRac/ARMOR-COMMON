"""Small refusals of the shared package that no other test reached: a name that is not an identity, a channel that does not exist, a port 0, a frame of the wrong size."""
from __future__ import annotations

import unittest

from armor_common import mqtt_topics, node_roles
from armor_common.contracts import ContractError
from armor_common.motion_core import check_frame
from armor_common.provisioning import _check_server
from armor_common.voice import VoiceTurnError, _check_boundary


class NodeRoleNames(unittest.TestCase):
    def test_a_name_that_is_not_an_identity_is_refused_by_every_way_to_use_it(self) -> None:
        role = node_roles.roles()[0]
        for bad in ("", "Upper", "-start", "with space", "a/b", "a" * 65, "x\n", "../etc"):
            with self.assertRaises(ValueError, msg=repr(bad)):
                node_roles.user_for(role, bad)
            with self.assertRaises(ValueError, msg=repr(bad)):
                node_roles.acl_lines(role, bad)
            with self.assertRaises(ValueError, msg=repr(bad)):
                node_roles.acl_block(role, bad)

    def test_an_access_block_is_the_user_line_and_then_its_access_lines(self) -> None:
        role = node_roles.roles()[0]
        block = node_roles.acl_block(role, "north-1")
        lines = block.splitlines()
        self.assertTrue(block.endswith("\n"))
        self.assertEqual(lines[0], f"user {node_roles.user_for(role, 'north-1')}")
        self.assertEqual(lines[1:], node_roles.acl_lines(role, "north-1"))
        self.assertTrue(all("{name}" not in line for line in lines))

    def test_the_longest_name_is_accepted_and_one_more_character_is_not(self) -> None:
        role = node_roles.roles()[0]
        self.assertTrue(node_roles.user_for(role, "a" * 64))
        with self.assertRaises(ValueError):
            node_roles.user_for(role, "a" * 65)


class ChannelLookup(unittest.TestCase):
    def test_every_channel_is_found_by_its_id_and_an_unknown_one_is_a_key_error(self) -> None:
        for item in mqtt_topics.channels():
            self.assertIs(mqtt_topics.channel(item["id"]), item)
        with self.assertRaises(KeyError):
            mqtt_topics.channel("no-such-channel")


class ProvisioningServerAddress(unittest.TestCase):
    def test_port_zero_is_out_of_range_and_a_real_port_is_kept(self) -> None:
        with self.assertRaisesRegex(ContractError, "out of range"):
            _check_server("http://192.168.0.180:0")
        self.assertEqual(_check_server("http://192.168.0.180:8080/"), "http://192.168.0.180:8080")
        self.assertEqual(_check_server("https://casa.example.org"), "https://casa.example.org")

    def test_a_port_above_the_last_one_is_not_an_address_at_all(self) -> None:
        with self.assertRaisesRegex(ContractError, "not a valid address"):
            _check_server("http://192.168.0.180:70000")


class MotionFrameSize(unittest.TestCase):
    def test_a_frame_must_have_a_positive_size_and_exactly_one_byte_per_cell(self) -> None:
        check_frame(bytes(6), 3, 2)
        check_frame(bytearray(6), 3, 2)
        for width, height in ((0, 2), (3, 0), (-1, 2)):
            with self.assertRaisesRegex(ValueError, "positive size"):
                check_frame(bytes(6), width, height)
        for frame in (bytes(5), bytes(7), b"", "abcdef", None, [0] * 6):
            with self.assertRaisesRegex(ValueError, "grey frame of 3 x 2 is 6 bytes"):
                check_frame(frame, 3, 2)   # type: ignore[arg-type]


class MultipartBoundary(unittest.TestCase):
    def test_a_boundary_that_ends_in_a_line_break_is_refused_like_any_other_bad_one(self) -> None:
        _check_boundary("armor0123456789abcdef")
        for bad in ("", "x" * 71, "ends.", "with space", "line" + chr(10), "armor0123" + chr(10), "a" + chr(13) + chr(10) + "b", "tab" + chr(9)):
            with self.assertRaises(VoiceTurnError, msg=repr(bad)) as raised:
                _check_boundary(bad)
            self.assertEqual((raised.exception.status, raised.exception.code), (400, "bad_multipart"))


if __name__ == "__main__":
    unittest.main()
