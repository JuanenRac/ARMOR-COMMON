"""Strict validators for the A.R.M.O.R. message families.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

Every payload is checked against the published JSON Schema in ``schemas/`` (the
single source of truth) and then against the rules a schema cannot express:
the topic shape and that the topic's node id equals the payload's.
"""

from __future__ import annotations

import copy
import ipaddress
import json
from collections.abc import Mapping
from functools import lru_cache
from importlib import resources
from typing import Any

from .schema import SchemaError, check_schema, validate


class ContractError(ValueError):
    """Raised when an A.R.M.O.R. message fails its published contract."""


TOPIC_PREFIX = "armor/node/"
KINDS = ("telemetry", "health", "command", "info")
# The solar messages (gateway nodes reading inverters and batteries) live on their own topics: armor/solar/{node_id}/{device}/state.
# The kind of the message ("inverter" or "battery") is inside the payload and picks the schema.
SOLAR_TOPIC_PREFIX = "armor/solar/"
SOLAR_KINDS = ("inverter", "battery")
_SOLAR_SCHEMAS = {"inverter": "solar_inverter", "battery": "solar_battery"}
# The electrical message (ARMOR-ELECTRICAL nodes measuring the house's network) has one topic per node: armor/electrical/{node_id}/state. The switches of a node are
# commanded on armor/electrical/{node_id}/command (server -> node) and answered on armor/electrical/{node_id}/result (node -> server).
ELECTRICAL_TOPIC_PREFIX = "armor/electrical/"
ELECTRICAL_LEAVES = ("state", "command", "result")
ELECTRICAL_KINDS = ("electrical", "electrical_command", "electrical_result")
_TOKEN_ACTIONS = ("close_a", "close_b")
# The alarm message (an ARMOR-ALARM node) has one topic per node: armor/alarm/{node_id}/state; the panel is commanded on armor/alarm/{node_id}/command (server -> node)
# and answered on armor/alarm/{node_id}/result (node -> server).
ALARM_TOPIC_PREFIX = "armor/alarm/"
ALARM_LEAVES = ("state", "command", "result", "zigbee")   # "zigbee": what the server tells the panel about the Zigbee sensor of a zone (alarm_zone_feed)
ALARM_KINDS = ("alarm", "alarm_command", "alarm_result")
# The network message (an ARMOR-NETWORK node watching the local network) has one topic per node: armor/network/{node_id}/state.
NETWORK_TOPIC_PREFIX = "armor/network/"
# A relay of a node is a device of the device layer: armor/device/{node_id}/{relay}/state | availability | set. The server's alert goes out on armor/server/alert.
DEVICE_TOPIC_PREFIX = "armor/device/"
DEVICE_LEAVES = ("state", "availability", "set")
SERVER_ALERT_TOPIC = "armor/server/alert"
_RELAY_COMMANDS = ("on", "off", "true", "false", "1", "0", "toggle")
# The health report of a node of any family has one topic per node: armor/health/{node_id} (node -> server). It is not the presence message of a radar (armor/node/{node_id}/health).
NODE_HEALTH_TOPIC_PREFIX = "armor/health/"
_EXTRA_SCHEMAS = ("alarm_zone_feed", "device_state", "server_alert", "network_orders", "node_health", "arm_profile", "connection_event", "system_event", "connection_client")
_PRIVATE_RANGES = tuple(ipaddress.ip_network(text) for text in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
_DEVICE_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
_NODE_ID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")


def load_schema(kind: str) -> dict[str, Any]:
    """The published schema of a message kind (``telemetry``, ``health``, ``command`` or ``info``). A copy: the one the validators use is shared and must not be changed by a caller."""
    return copy.deepcopy(_published_schema(kind))


@lru_cache(maxsize=None)
def _published_schema(kind: str) -> dict[str, Any]:
    if kind not in KINDS and kind not in _SOLAR_SCHEMAS and kind not in ELECTRICAL_KINDS and kind not in ALARM_KINDS and kind not in _EXTRA_SCHEMAS and kind != "network":
        raise ContractError(f"unsupported topic kind {kind!r}")
    text = resources.files("armor_common").joinpath("schemas", f"{_SOLAR_SCHEMAS.get(kind, kind)}.schema.json").read_text(encoding="utf-8")
    schema = json.loads(text)
    check_schema(schema)
    return schema


def validate_payload(kind: str, payload: Mapping[str, object]) -> None:
    """Validate a payload against its schema only (no topic)."""
    try:
        validate(payload, _published_schema(kind))
    except SchemaError as error:
        raise ContractError(str(error)) from error


def _check_node_id(node_id: str) -> None:
    """The node id of a topic: lowercase letters, digits, '-' or '_', not starting with '-' or '_', at most 64 characters."""
    if not node_id or not set(node_id) <= _NODE_ID_CHARS or node_id[0] in "-_" or len(node_id) > 64:
        raise ContractError("node_id must use lowercase letters, digits, '-' or '_'")


def parse_topic(topic: str) -> tuple[str, str]:
    """Split ``armor/node/{node_id}/{kind}`` into ``(node_id, kind)``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    parts = topic.split("/")
    if len(parts) != 4 or parts[:2] != ["armor", "node"]:
        raise ContractError("topic must be armor/node/{node_id}/{kind}")
    node_id, kind = parts[2], parts[3]
    _check_node_id(node_id)
    if kind not in KINDS:
        raise ContractError("unsupported topic kind")
    return node_id, kind


def validate_topic_and_payload(topic: str, payload: Mapping[str, object]) -> None:
    """Validate a message: the topic, the payload's schema, and that their node ids agree."""
    node_id, kind = parse_topic(topic)
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    if payload.get("node_id") != node_id:
        raise ContractError("payload node_id must match the topic")
    validate_payload(kind, payload)


def parse_solar_topic(topic: str) -> tuple[str, str]:
    """Split ``armor/solar/{node_id}/{device}/state`` into ``(node_id, device)``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    parts = topic.split("/")
    if len(parts) != 5 or parts[:2] != ["armor", "solar"] or parts[4] != "state":
        raise ContractError("topic must be armor/solar/{node_id}/{device}/state")
    node_id, device = parts[2], parts[3]
    _check_node_id(node_id)
    if not device or not set(device) <= _DEVICE_CHARS or device[0] in "-_" or len(device) > 32:
        raise ContractError("device must use lowercase letters, digits, '-' or '_' (at most 32)")
    return node_id, device


def validate_solar_message(topic: str, payload: Mapping[str, object]) -> None:
    """Validate a solar message: the topic, the payload's schema (chosen by its ``kind``), and that the topic's node and device match the payload."""
    node_id, device = parse_solar_topic(topic)
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    kind = payload.get("kind")
    if kind not in SOLAR_KINDS:
        raise ContractError("kind must be inverter or battery")
    if payload.get("node_id") != node_id or payload.get("device") != device:
        raise ContractError("payload node_id and device must match the topic")
    validate_payload(str(kind), payload)


def parse_electrical_topic(topic: str, leaf: str = "state") -> str:
    """Split ``armor/electrical/{node_id}/{leaf}`` into ``node_id``; the leaf is ``state``, ``command`` or ``result``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    if leaf not in ELECTRICAL_LEAVES:
        raise ContractError("unsupported topic leaf")
    parts = topic.split("/")
    if len(parts) != 4 or parts[:2] != ["armor", "electrical"] or parts[3] != leaf:
        raise ContractError(f"topic must be armor/electrical/{{node_id}}/{leaf}")
    node_id = parts[2]
    _check_node_id(node_id)
    return node_id


def validate_electrical_message(topic: str, payload: Mapping[str, object]) -> None:
    """Validate an electrical message: the topic, the payload's schema, and that the topic's node matches the payload; a channel id appears once."""
    node_id = parse_electrical_topic(topic)
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    if payload.get("node_id") != node_id:
        raise ContractError("payload node_id must match the topic")
    validate_payload("electrical", payload)
    channels = payload.get("channels")
    if isinstance(channels, list):
        ids = [channel.get("id") for channel in channels if isinstance(channel, Mapping)]
        if len(ids) != len(set(ids)):
            raise ContractError("a channel id must appear once")
    switches = payload.get("switches")
    if isinstance(switches, list):
        ids = [item.get("id") for item in switches if isinstance(item, Mapping)]
        if len(ids) != len(set(ids)):
            raise ContractError("a switch id must appear once")


def validate_electrical_command(topic: str, payload: Mapping[str, object]) -> None:
    """Validate a command to a switch: the topic, the schema, that the node matches, and that a token is present exactly on the two actions that close."""
    node_id = parse_electrical_topic(topic, "command")
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    if payload.get("node_id") != node_id:
        raise ContractError("payload node_id must match the topic")
    validate_payload("electrical_command", payload)
    if (payload.get("action") in _TOKEN_ACTIONS) != ("token" in payload):
        raise ContractError("a token goes on close_a and close_b and on nothing else")


def validate_electrical_result(topic: str, payload: Mapping[str, object]) -> None:
    """Validate a node's answer: the topic, the schema, that the node matches, refusal none exactly when accepted, and a token only in an accepted arm."""
    node_id = parse_electrical_topic(topic, "result")
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    if payload.get("node_id") != node_id:
        raise ContractError("payload node_id must match the topic")
    validate_payload("electrical_result", payload)
    accepted = payload.get("accepted")
    if accepted != (payload.get("refusal") == "none"):
        raise ContractError("the refusal is none exactly when the request was accepted")
    if ("token" in payload) != (accepted is True and payload.get("action") == "arm"):
        raise ContractError("a token is given only in the result of an accepted arm")


def parse_alarm_topic(topic: str, leaf: str = "state") -> str:
    """Split ``armor/alarm/{node_id}/{leaf}`` into ``node_id``; the leaf is ``state``, ``command`` or ``result``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    if leaf not in ALARM_LEAVES:
        raise ContractError("unsupported topic leaf")
    parts = topic.split("/")
    if len(parts) != 4 or parts[:2] != ["armor", "alarm"] or parts[3] != leaf:
        raise ContractError(f"topic must be armor/alarm/{{node_id}}/{leaf}")
    node_id = parts[2]
    _check_node_id(node_id)
    return node_id


def _alarm_checked(topic: str, leaf: str, kind: str, payload: Mapping[str, object]) -> None:
    node_id = parse_alarm_topic(topic, leaf)
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    if payload.get("node_id") != node_id:
        raise ContractError("payload node_id must match the topic")
    validate_payload(kind, payload)


def validate_alarm_message(topic: str, payload: Mapping[str, object]) -> None:
    """Validate an alarm state: the topic, the schema, that the node matches, and the rules that join fields: a zone is named once, an open zone is a zone of the message,
    the phase and the mode agree (a disarmed panel has the mode disarmed, an armed one does not; only the alarm phase may carry both), a siren means an alarm, and an event about a zone names a zone of the message."""
    _alarm_checked(topic, "state", "alarm", payload)
    zones = payload.get("zones")
    ids = [item.get("id") for item in zones if isinstance(item, Mapping)] if isinstance(zones, list) else []
    if len(ids) != len(set(ids)):
        raise ContractError("a zone id must appear once")
    open_zones = payload.get("open_zones")
    if isinstance(open_zones, list):
        if len(open_zones) != len(set(open_zones)):
            raise ContractError("an open zone is named once")
        if any(item not in ids for item in open_zones):
            raise ContractError("an open zone must be a zone of the message")
    # A panel that is disarmed has the mode disarmed. The alarm phase may carry the mode disarmed too:
    # a 24-hour zone (smoke, gas, panic) or a tamper sounds with nobody having armed the panel.
    if payload.get("phase") == "disarmed" and payload.get("mode") != "disarmed":
        raise ContractError("a disarmed panel has the mode disarmed")
    if payload.get("phase") in ("exit_delay", "armed", "entry_delay") and payload.get("mode") == "disarmed":
        raise ContractError("an arming or armed panel has a mode other than disarmed")
    if payload.get("siren") is True and payload.get("phase") != "alarm":
        raise ContractError("the siren sounds only in the alarm phase")
    if "profile" in payload and payload.get("mode") == "disarmed":
        raise ContractError("a panel that is not armed has no arming profile")
    events = payload.get("events")
    if isinstance(events, list):
        for item in events:
            if isinstance(item, Mapping) and "zone" in item and item["zone"] not in ids:
                raise ContractError("an event about a zone names a zone of the message")


def validate_arm_profile(profile: Mapping[str, object]) -> None:
    """Validate an arming profile: the schema, and that a zone is named once and that a zone that is not guarding says nothing about its delay."""
    if not isinstance(profile, Mapping):
        raise ContractError("a profile must be an object")
    validate_payload("arm_profile", profile)
    zones = profile.get("zones")
    if isinstance(zones, list):
        ids = [item.get("id") for item in zones if isinstance(item, Mapping)]
        if len(ids) != len(set(ids)):
            raise ContractError("a zone is named once in a profile")
        for item in zones:
            if isinstance(item, Mapping) and item.get("armed") is False and "delay" in item:
                raise ContractError("a zone that is left out has no delay")


def validate_alarm_command(topic: str, payload: Mapping[str, object]) -> None:
    """Validate a command to the panel: the topic, the schema, that the node matches, a mode exactly on an arm, force and a profile only on an arm, and a profile whose base is the mode."""
    _alarm_checked(topic, "command", "alarm_command", payload)
    if (payload.get("action") == "arm") != ("mode" in payload):
        raise ContractError("a mode goes on an arm and on nothing else")
    if payload.get("action") != "arm" and payload.get("force") is True:
        raise ContractError("force goes on an arm and on nothing else")
    profile = payload.get("profile")
    if profile is not None:
        if payload.get("action") != "arm":
            raise ContractError("a profile goes on an arm and on nothing else")
        validate_arm_profile(profile)   # type: ignore[arg-type]
        if profile.get("base") != payload.get("mode"):   # type: ignore[union-attr]
            raise ContractError("the base of the profile is the mode of the arm")


def validate_alarm_result(topic: str, payload: Mapping[str, object]) -> None:
    """Validate a node's answer: the topic, the schema, that the node matches, and refusal none exactly when accepted."""
    _alarm_checked(topic, "result", "alarm_result", payload)
    if payload.get("accepted") != (payload.get("refusal") == "none"):
        raise ContractError("the refusal is none exactly when the request was accepted")


def parse_health_topic(topic: str) -> str:
    """Split ``armor/health/{node_id}`` into ``node_id``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    parts = topic.split("/")
    if len(parts) != 3 or parts[:2] != ["armor", "health"]:
        raise ContractError("topic must be armor/health/{node_id}")
    _check_node_id(parts[2])
    return parts[2]


def validate_node_health(topic: str, payload: Mapping[str, object]) -> None:
    """Validate the health report of a node: the topic, the schema, that the node matches, and the rules that join fields: the least heap is never more than the free heap,
    a signal strength only on a Wi-Fi link that is up, no link means a link that is down, and the internal memory is told whole with its least and its biggest block never above what is free."""
    node_id = parse_health_topic(topic)
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    if payload.get("node_id") != node_id:
        raise ContractError("payload node_id must match the topic")
    validate_payload("node_health", payload)
    if payload["heap_min"] > payload["heap_free"]:   # type: ignore[operator]
        raise ContractError("the least heap is never more than the heap free now")
    internal = [name for name in ("heap_internal_free", "heap_internal_min", "heap_internal_largest") if name in payload]
    if internal and len(internal) != 3:
        raise ContractError("the internal memory is told whole: heap_internal_free, heap_internal_min and heap_internal_largest together")
    if internal and (payload["heap_internal_min"] > payload["heap_internal_free"] or payload["heap_internal_largest"] > payload["heap_internal_free"]):   # type: ignore[operator]
        raise ContractError("the least internal memory and its biggest block are never more than the internal memory free now")
    if payload["link"] == "none" and payload["link_up"] is not False:
        raise ContractError("no link means a link that is down")
    if "rssi_dbm" in payload and not (payload["link"] == "wifi" and payload["link_up"] is True):
        raise ContractError("a signal strength goes only with a Wi-Fi link that is up")


def parse_network_topic(topic: str) -> str:
    """Split ``armor/network/{node_id}/state`` into ``node_id``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    parts = topic.split("/")
    if len(parts) != 4 or parts[:2] != ["armor", "network"] or parts[3] != "state":
        raise ContractError("topic must be armor/network/{node_id}/state")
    node_id = parts[2]
    _check_node_id(node_id)
    return node_id


def validate_network_message(topic: str, payload: Mapping[str, object]) -> None:
    """Validate a network message: the topic, the schema, that the node matches, and the rules that join fields: a device and an event are named once, a device with a
    MAC has it as its id, and an event is about a device (and names it) or about the internet or the gateway (and does not)."""
    node_id = parse_network_topic(topic)
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    if payload.get("node_id") != node_id:
        raise ContractError("payload node_id must match the topic")
    validate_payload("network", payload)
    interface = payload.get("interface")
    if isinstance(interface, Mapping) and isinstance(interface.get("cidr"), str):
        try:
            watched = ipaddress.ip_network(interface["cidr"], strict=False)
        except ValueError:
            raise ContractError("interface.cidr is not a network") from None
        if not any(watched.subnet_of(private) for private in _PRIVATE_RANGES):
            raise ContractError("the network a node watches is a private range (10/8, 172.16/12 or 192.168/16)")
    devices = payload.get("devices")
    if isinstance(devices, list):
        ids = [item.get("id") for item in devices if isinstance(item, Mapping)]
        if len(ids) != len(set(ids)):
            raise ContractError("a device id must appear once")
        for item in devices:
            if isinstance(item, Mapping) and isinstance(item.get("mac"), str) and item.get("id") != item["mac"] and not str(item.get("id", "")).startswith("ip-"):
                raise ContractError("a device with a MAC has the MAC as its id")
            if isinstance(item, Mapping) and item.get("first_seen_ms", 0) > item.get("last_seen_ms", 0):
                raise ContractError("a device cannot have been seen for the first time after the last time")
    events = payload.get("events")
    if isinstance(events, list):
        ids = [item.get("id") for item in events if isinstance(item, Mapping)]
        if len(ids) != len(set(ids)):
            raise ContractError("an event id must appear once")
        for item in events:
            if not isinstance(item, Mapping):
                continue
            internet = str(item.get("kind", "")).split("_")[0] in ("internet", "gateway")
            if internet and ("device_id" in item or "port" in item):
                raise ContractError("an event of the internet or the gateway is not about a device or a port")
            if not internet and "device_id" not in item:
                raise ContractError("an event about a device names the device")
            if "outage_s" in item and item.get("kind") not in ("internet_up", "gateway_up"):
                raise ContractError("only internet_up and gateway_up say how long it was down")
            if item.get("kind") in ("port_opened", "port_closed") and "port" not in item:
                raise ContractError("a port event names the port")


def validate_alarm_zone_feed(topic: str, payload: Mapping[str, object]) -> None:
    """Validate what the server tells a panel about the Zigbee sensor of one of its zones: the topic ``armor/alarm/{node_id}/zigbee`` and the schema (the node is the topic's)."""
    parse_alarm_topic(topic, "zigbee")
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    validate_payload("alarm_zone_feed", payload)


def parse_device_topic(topic: str) -> tuple[str, str, str]:
    """Split ``armor/device/{node_id}/{relay}/{leaf}`` into ``(node_id, relay, leaf)``; the leaf is ``state``, ``availability`` or ``set``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    parts = topic.split("/")
    if len(parts) != 5 or parts[:2] != ["armor", "device"] or parts[4] not in DEVICE_LEAVES:
        raise ContractError("topic must be armor/device/{node_id}/{relay}/state, availability or set")
    node_id, relay, leaf = parts[2], parts[3], parts[4]
    _check_node_id(node_id)
    if not relay or not set(relay) <= _DEVICE_CHARS or relay[0] in "-_" or len(relay) > 32:
        raise ContractError("relay must use lowercase letters, digits, '-' or '_' (at most 32)")
    return node_id, relay, leaf


def validate_device_message(topic: str, payload: object) -> None:
    """Validate a message about a relay of a node: its state ``{"on": true}`` (a JSON object), its availability (the text ``online`` or ``offline``) or the command it is given
    (``ON``, ``OFF`` or ``TOGGLE``, in any case, with ``true``, ``false``, ``1`` and ``0`` as other ways to say the first two)."""
    _node_id, _relay, leaf = parse_device_topic(topic)
    if leaf == "state":
        if not isinstance(payload, Mapping):
            raise ContractError("the state of a relay is an object")
        validate_payload("device_state", payload)
    elif leaf == "availability":
        if payload not in ("online", "offline"):
            raise ContractError("availability is online or offline")
    elif not isinstance(payload, str) or payload.strip().lower() not in _RELAY_COMMANDS:
        raise ContractError("a relay is told ON, OFF or TOGGLE")


def validate_server_alert(topic: str, payload: Mapping[str, object]) -> None:
    """Validate an alert of the server: its topic and its schema, and that what an event names is there (a node event names its node, a camera event its camera, an alarm its id and code)."""
    if topic != SERVER_ALERT_TOPIC:
        raise ContractError(f"the alert is published on {SERVER_ALERT_TOPIC}")
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    validate_payload("server_alert", payload)
    event = payload.get("event")
    if event in ("node.offline", "node.stale", "alert.raised", "alert.cleared") and "node_id" not in payload:
        raise ContractError("a node event names the node")
    if event == "camera.offline" and "camera_id" not in payload:
        raise ContractError("a camera event names the camera")
    if event in ("alarm.raised", "alarm.escalated") and not {"alarm_id", "code", "severity"} <= set(payload):
        raise ContractError("an alarm event names the alarm, its code and its severity")
    if event == "login.remote" and not {"login_user", "login_from"} <= set(payload):
        raise ContractError("a sign-in from outside names the person and the address")
    if payload.get("silent") is True and event != "alarm.raised":
        raise ContractError("only a raised alarm is silent")


def validate_network_orders(payload: Mapping[str, object]) -> None:
    """Validate the answer of the server to a message of the network node: the schema, an order about a device names it, and a sealed login goes only with an ``inspect``."""
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    validate_payload("network_orders", payload)
    for order in payload.get("commands", []):
        if order.get("type") in ("ping", "wake", "ports", "http", "inspect") and not {"device_id", "ip"} <= set(order):
            raise ContractError("an order about a device names the device and its address")
        if order.get("type") == "scan_now" and ({"device_id", "ip", "mac", "port"} & set(order)):
            raise ContractError("a sweep is about the whole network, not a device")
        if order.get("type") == "wake" and "mac" not in order:
            raise ContractError("a wake-up needs the MAC address")
        if "port" in order and order.get("type") not in ("http", "inspect"):
            raise ContractError("only a look at a web page or an inspection names a port")
        if "auth_sealed" in order and order.get("type") != "inspect":
            raise ContractError("a sealed login goes only with an inspection")
    ids = [order.get("id") for order in payload.get("commands", [])]
    if len(ids) != len(set(ids)):
        raise ContractError("an order id must appear once")
