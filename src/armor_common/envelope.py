"""Canonical JSON envelopes; deterministic output is useful for logs and tests."""
from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .contracts import validate_topic_and_payload


def encode(topic: str, payload: Mapping[str, object]) -> str:
    """Validate and encode an MQTT-ready envelope with stable key ordering."""
    validate_topic_and_payload(topic, payload)
    return json.dumps({"topic": topic, "payload": payload}, sort_keys=True, separators=(",", ":"))


def _no_duplicate_names(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """JSON.parse keeps the LAST of a repeated name and the nodes' parser the first: a document that repeats one is refused, so no two readers can take different values from it."""
    found: dict[str, Any] = {}
    for name, value in pairs:
        if name in found:
            raise ValueError(f"envelope repeats the field {name!r}")
        found[name] = value
    return found


def decode(line: str) -> tuple[str, dict[str, Any]]:
    """Decode and validate one untrusted JSONL envelope."""
    try:
        envelope = json.loads(line, object_pairs_hook=_no_duplicate_names)
    except json.JSONDecodeError as error:
        raise ValueError("envelope is not valid JSON") from error
    if not isinstance(envelope, dict) or set(envelope) != {"topic", "payload"}:
        raise ValueError("envelope must contain only topic and payload")
    if not isinstance(envelope["topic"], str) or not isinstance(envelope["payload"], dict):
        raise ValueError("envelope fields have invalid types")
    validate_topic_and_payload(envelope["topic"], envelope["payload"])
    return envelope["topic"], envelope["payload"]
