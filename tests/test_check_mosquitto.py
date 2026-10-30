"""The check that plays a node's MQTT client against a real Mosquitto (firmware_base/tests/check_mosquitto.py), tried against a small stand-in broker so that it is exercised even where
Mosquitto is not installed: the codec, the order of events, the skip when there is no broker and the failure when one is required."""
from __future__ import annotations

import importlib.util
import io
import os
import socket
import struct
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "firmware_base" / "tests" / "check_mosquitto.py"
spec = importlib.util.spec_from_file_location("check_mosquitto", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def _read(sock: socket.socket) -> tuple[int, bytes]:
    first = sock.recv(1)
    if not first:
        raise ConnectionError
    size = shift = 0
    while True:
        byte = sock.recv(1)[0]
        size |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            break
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError
        data += chunk
    return first[0], data


def _text(data: bytes, at: int) -> tuple[str, int]:
    size = struct.unpack(">H", data[at:at + 2])[0]
    return data[at + 2:at + 2 + size].decode(), at + 2 + size


def _matches(topic_filter: str, topic: str) -> bool:
    wanted, got = topic_filter.split("/"), topic.split("/")
    for index, part in enumerate(wanted):
        if part == "#":
            return True
        if index >= len(got) or part not in ("+", got[index]):
            return False
    return len(wanted) == len(got)


class StandInBroker:
    """MQTT 3.1.1 with what the check needs: will, retained messages, QoS 1, wildcards, and a node that may only publish on topics that carry its client id."""

    def __init__(self, lose_wills: bool = False) -> None:
        self.lose_wills = lose_wills
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen()
        self.port = self.listener.getsockname()[1]
        self.subscriptions: list[tuple[socket.socket, str]] = []
        self.retained: dict[str, bytes] = {}
        self.lock = threading.Lock()
        threading.Thread(target=self._accept, daemon=True).start()

    def _accept(self) -> None:
        while True:
            try:
                connection, _ = self.listener.accept()
            except OSError:
                return
            threading.Thread(target=self._serve, args=(connection,), daemon=True).start()

    def _push(self, sock: socket.socket, topic: str, payload: bytes, retained: bool = False) -> None:
        body = check._text(topic) + b"\x00\x01" + payload
        try:
            sock.sendall(bytes([0x33 if retained else 0x32]) + check._length(len(body)) + body)
        except OSError:
            pass

    def _deliver(self, topic: str, payload: bytes, retain: bool) -> None:
        with self.lock:
            if retain:
                self.retained[topic] = payload
            for sock, topic_filter in list(self.subscriptions):
                if _matches(topic_filter, topic):
                    self._push(sock, topic, payload)

    def _serve(self, sock: socket.socket) -> None:
        will = None
        try:
            _, data = _read(sock)
            _, at = _text(data, 0)
            flags = data[at + 1]
            at += 4
            client_id, at = _text(data, at)
            if flags & 0x04:
                topic, at = _text(data, at)
                size = struct.unpack(">H", data[at:at + 2])[0]
                will = (topic, data[at + 2:at + 2 + size])
                at += 2 + size
            user, at = _text(data, at)
            sock.sendall(b"\x20\x02\x00\x00")
            while True:
                first, data = _read(sock)
                kind = first >> 4
                if kind == 8:
                    topic_filter, _ = _text(data, 2)
                    sock.sendall(b"\x90\x03" + data[:2] + b"\x01")
                    with self.lock:
                        self.subscriptions.append((sock, topic_filter))
                        for topic, payload in self.retained.items():
                            if _matches(topic_filter, topic):
                                self._push(sock, topic, payload, retained=True)
                elif kind == 3:
                    topic, at = _text(data, 0)
                    sock.sendall(b"\x40\x02" + data[at:at + 2])
                    if user == "armor-server" or client_id in topic:
                        self._deliver(topic, data[at + 2:], bool(first & 1))
                elif kind == 14:
                    will = None
                    return
        except (ConnectionError, OSError, IndexError):
            pass
        finally:
            with self.lock:
                self.subscriptions = [item for item in self.subscriptions if item[0] is not sock]
            if will and not self.lose_wills:
                self._deliver(will[0], will[1], True)
            sock.close()

    def close(self) -> None:
        self.listener.close()


class CheckMosquittoTest(unittest.TestCase):
    def test_a_node_through_a_broker(self) -> None:
        broker = StandInBroker()
        self.addCleanup(broker.close)
        samples = [
            ("armor/electrical/n-1/state", {"kind": "electrical", "node_id": "n-1", "timestamp_ms": 1, "channels": []}),
            ("armor/electrical/n-1/command", {"node_id": "n-1", "command_id": "abcd1234"}),
            ("node_health", {"node_id": "n-1", "timestamp_ms": 9, "online": True}),
            ("telemetry", {"node_id": "another"}),
        ]
        with mock.patch.object(check, "start_broker", return_value=(mock.Mock(), broker.port)), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(check.run(samples), 0)
        self.assertIn("MOSQUITTO=OK 2 messages", out.getvalue())

    def test_a_broker_that_loses_the_last_will_fails(self) -> None:
        broker = StandInBroker(lose_wills=True)
        self.addCleanup(broker.close)
        with mock.patch.object(check, "start_broker", return_value=(mock.Mock(), broker.port)):
            with self.assertRaises(AssertionError) as caught:
                check.run([("node_health", {"node_id": "n-1", "timestamp_ms": 9, "online": True})])
        self.assertIn("last will", str(caught.exception))

    def test_without_a_broker_it_skips_unless_one_is_required(self) -> None:
        with mock.patch.object(check, "find", return_value=None), mock.patch.object(check.sys, "argv", ["check_mosquitto.py"]):
            with mock.patch.dict(os.environ):
                os.environ.pop("ARMOR_REQUIRE_MOSQUITTO", None)
                with redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(check.main(), 0)
                self.assertIn("MOSQUITTO=SKIPPED", out.getvalue())
            with mock.patch.dict(os.environ, {"ARMOR_REQUIRE_MOSQUITTO": "1"}), redirect_stderr(io.StringIO()) as err:
                self.assertEqual(check.main(), 1)
            self.assertIn("MOSQUITTO=MISSING", err.getvalue())

    def test_the_lines_a_node_prints_are_told_apart(self) -> None:
        self.assertEqual(check.classify("armor/solar/s1/inverter", {}, "x"), ("armor/solar/s1/inverter", "s1", True))
        self.assertEqual(check.classify("armor/alarm/a1/command", {}, "x"), ("armor/alarm/a1/command", "a1", False))
        self.assertEqual(check.classify("node_health", {"node_id": "r1"}, "x"), ("armor/health/r1", "r1", True))
        self.assertEqual(check.classify("telemetry", {"node_id": "r1"}, "x"), ("armor/node/r1/telemetry", "r1", True))
        self.assertIsNone(check.classify("device_state", {"node_id": "r1"}, "x"))
        self.assertIsNone(check.classify("armor/x", {}, "x"))


if __name__ == "__main__":
    unittest.main()
