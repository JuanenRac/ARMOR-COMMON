"""Strict validators for the A.R.M.O.R. message families.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

Every payload is checked against the published JSON Schema in ``schemas/`` (the
single source of truth) and then against the rules a schema cannot express:
the topic shape and that the topic's node id equals the payload's.
"""

from __future__ import annotations

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
_DEVICE_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
_NODE_ID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")


@lru_cache(maxsize=None)
def load_schema(kind: str) -> dict[str, Any]:
    """The published schema of a message kind (``telemetry``, ``health``, ``command`` or ``info``)."""
    if kind not in KINDS and kind not in _SOLAR_SCHEMAS and kind not in ELECTRICAL_KINDS:
        raise ContractError(f"unsupported topic kind {kind!r}")
    text = resources.files("armor_common").joinpath("schemas", f"{_SOLAR_SCHEMAS.get(kind, kind)}.schema.json").read_text(encoding="utf-8")
    schema = json.loads(text)
    check_schema(schema)
    return schema


def validate_payload(kind: str, payload: Mapping[str, object]) -> None:
    """Validate a payload against its schema only (no topic)."""
    try:
        validate(payload, load_schema(kind))
    except SchemaError as error:
        raise ContractError(str(error)) from error


def parse_topic(topic: str) -> tuple[str, str]:
    """Split ``armor/node/{node_id}/{kind}`` into ``(node_id, kind)``."""
    if not isinstance(topic, str):
        raise ContractError("topic must be a string")
    parts = topic.split("/")
    if len(parts) != 4 or parts[:2] != ["armor", "node"]:
        raise ContractError("topic must be armor/node/{node_id}/{kind}")
    node_id, kind = parts[2], parts[3]
    if not node_id or not set(node_id) <= _NODE_ID_CHARS:
        raise ContractError("node_id must use lowercase letters, digits, '-' or '_'")
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
    if not node_id or not set(node_id) <= _NODE_ID_CHARS or node_id[0] in "-_" or len(node_id) > 64:
        raise ContractError("node_id must use lowercase letters, digits, '-' or '_'")
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
    if not node_id or not set(node_id) <= _NODE_ID_CHARS or node_id[0] in "-_" or len(node_id) > 64:
        raise ContractError("node_id must use lowercase letters, digits, '-' or '_'")
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
