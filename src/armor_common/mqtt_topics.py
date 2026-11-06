"""The one list of the MQTT topics (mqtt_topics.json) and what the access lines of each role (node_roles.json) allow on them."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import node_roles

_FILE = Path(__file__).with_name("mqtt_topics.json")
SERVER = "server"


@lru_cache(maxsize=1)
def channels() -> list[dict]:
    return json.loads(_FILE.read_text(encoding="utf-8"))["channels"]


def channel(channel_id: str) -> dict:
    for item in channels():
        if item["id"] == channel_id:
            return item
    raise KeyError(channel_id)


def schemas_of(item: dict) -> list[str]:
    """The schemas a channel carries, as a list (empty when its messages have none)."""
    schema = item["schema"]
    return [] if schema is None else [schema] if isinstance(schema, str) else list(schema)


def segments(topic: str) -> list[str]:
    return topic.split("/")


def covers(pattern: str, address: str) -> bool:
    """Does an access line's topic (``armor/node/x/telemetry``, ``armor/solar/x/#``, ``armor/device/#``) cover the address of a channel (``{node_id}`` and ``{device}`` stand for one segment)?
    A ``#`` covers everything below it; a name in the pattern covers the channel only where the channel says the same name or a placeholder for it."""
    wanted = segments(address)
    given = segments(pattern)
    for index, part in enumerate(given):
        if part == "#":
            return True
        if index >= len(wanted):
            return False
        here = wanted[index]
        if here == "#":
            return False   # the channel is wider than the line
        if part != here and not (here.startswith("{") and here.endswith("}")):
            return False
    return len(given) == len(wanted)


def acl_topics(role: str, verb: str) -> list[str]:
    """The topics (with the node's name as {node_id}) that a role's lines let it ``write`` or ``read`` (a ``readwrite`` line counts for both)."""
    out = []
    for line in node_roles.table()[role]["topics"]:
        _topic, mode, address = line.split(" ", 2)
        if mode == verb or mode == "readwrite":
            out.append(address.replace("{name}", "{node_id}"))
    return out


def allowed(role: str, verb: str, address: str) -> bool:
    """May this role ``write`` / ``read`` the channel with this address, going by its access lines? (The server is not in the table: its lines are in ARMOR-DEVOPS.)"""
    return any(covers(pattern, address) for pattern in acl_topics(role, verb))
