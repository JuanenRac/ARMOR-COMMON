"""The one numbering of the network ports of an installation (ports.json)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_FILE = Path(__file__).with_name("ports.json")


@lru_cache(maxsize=1)
def registry() -> dict:
    return json.loads(_FILE.read_text(encoding="utf-8"))


def port(name: str) -> int:
    """The port registered under a name (``server``, ``studio``, ``mqtt``, ``voice``, ``mqtt_tls``, ``https``, ``acme_http``)."""
    return int(registry()["ports"][name]["port"])


def legacy_ports() -> dict[int, str]:
    """The numbers the Docker stack used before the numbering was unified, with the service each one was for."""
    return {int(old): name for name, entry in registry()["ports"].items() for old in entry.get("legacy", [])}


def check_registry(data: dict) -> list[str]:
    """What is wrong with a registry: a port out of range, two services on one port, a legacy number that is also in use."""
    problems: list[str] = []
    seen: dict[int, str] = {}
    entries = data.get("ports")
    if not isinstance(entries, dict) or not entries:
        return ["ports is empty"]
    for name, entry in entries.items():
        value = entry.get("port") if isinstance(entry, dict) else None
        if not isinstance(value, int) or isinstance(value, bool) or not 1024 <= value <= 65535:
            problems.append(f"{name}: the port must be a number between 1024 and 65535")
            continue
        if value in seen:
            problems.append(f"{name} and {seen[value]} share the port {value}")
        seen[value] = name
    for name, entry in entries.items():
        for old in entry.get("legacy", []):
            if old in seen:
                problems.append(f"{name}: the old number {old} is the current port of {seen[old]}")
    return problems
