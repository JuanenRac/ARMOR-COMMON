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
_DEVICE_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
_NODE_ID_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-_")


@lru_cache(maxsize=None)
def load_schema(kind: str) -> dict[str, Any]:
    """The published schema of a message kind (``telemetry``, ``health``, ``command`` or ``info``)."""
    if kind not in KINDS and kind not in _SOLAR_SCHEMAS:
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
