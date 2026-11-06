#!/usr/bin/env python3
"""Generate the AsyncAPI description of the MQTT topics of A.R.M.O.R.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

``asyncapi/armor-mqtt.asyncapi.json`` (AsyncAPI 3.0, written as JSON, which is YAML too) is made from ``mqtt_topics.json`` (who publishes each topic, who reads it, which schema, the QoS and
whether it is retained) and ``node_roles.json`` (the access lines of each role of the broker): one channel per topic, one operation per role and channel (``send`` for what the role
publishes, ``receive`` for what it reads) with the MQTT binding ``qos`` and ``retain``, the message of each channel pointing at its JSON Schema, and ``x-acl`` with the access lines of
every role. The file is never edited by hand; ``--check`` fails when it is out of date.

    python tools/generate_asyncapi.py           # write asyncapi/armor-mqtt.asyncapi.json
    python tools/generate_asyncapi.py --check   # verify it is current
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from armor_common import mqtt_topics, node_roles   # noqa: E402

OUT = ROOT / "asyncapi" / "armor-mqtt.asyncapi.json"
BINDING = "0.2.0"


def camel(text: str) -> str:
    head, *rest = text.split("_")
    return head + "".join(part.capitalize() for part in rest)


def render() -> str:
    channels: dict = {}
    operations: dict = {}
    messages: dict = {}
    for item in mqtt_topics.channels():
        parameters = {name: {"description": "the name of the node" if name == "node_id" else "the device the message is about"} for name in ("node_id", "device") if "{" + name + "}" in item["address"]}
        names = []
        for schema in mqtt_topics.schemas_of(item):
            messages.setdefault(schema, {"name": schema, "title": schema, "contentType": "application/json", "payload": {"$ref": f"../src/armor_common/schemas/{schema}.schema.json"}})
            names.append(schema)
        channels[item["id"]] = {
            "address": item["address"],
            "description": item["about"],
            **({"parameters": parameters} if parameters else {}),
            "messages": {name: {"$ref": f"#/components/messages/{name}"} for name in names},
            "bindings": {"mqtt": {"bindingVersion": BINDING}},
        }
        binding = {"qos": item["qos"], "retain": item["retain"], "bindingVersion": BINDING}
        for action, key in (("send", "publishers"), ("receive", "readers")):
            for role in item[key]:
                operations[f"{role}.{action}.{item['id']}"] = {
                    "action": action,
                    "channel": {"$ref": f"#/channels/{item['id']}"},
                    "summary": f"the `{role}` role {'publishes' if action == 'send' else 'reads'} {item['address']}",
                    "bindings": {"mqtt": binding},
                    "x-role": role,
                    **({"x-opt-in": item["opt_in"]} if "opt_in" in item and role != mqtt_topics.SERVER else {}),
                    **({"x-lifecycle": item["lifecycle"]} if "lifecycle" in item and action == "send" else {}),
                }
    acl = {role: {"user": entry["user"], "lines": entry["topics"]} for role, entry in node_roles.table().items()}
    document = {
        "asyncapi": "3.0.0",
        "info": {
            "title": "A.R.M.O.R. MQTT topics",
            "version": "0.1.0",
            "description": "Who publishes and who reads each topic of the broker, with the QoS, whether the broker keeps it, the schema of its messages and the access lines of each role. Generated: do not edit.",
        },
        "servers": {"broker": {"host": "armor.local:8883", "protocol": "mqtts", "description": "the broker of the installation (Mosquitto on the CM5)"}},
        "channels": channels,
        "operations": operations,
        "components": {"messages": dict(sorted(messages.items()))},
        "x-acl": acl,
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    current = OUT.read_bytes().decode("utf-8").replace("\r\n", "\n") if OUT.exists() else None
    if current == content:
        print("AsyncAPI is current")
        return 0
    if args.check:
        print("asyncapi/armor-mqtt.asyncapi.json is out of date: run python tools/generate_asyncapi.py", file=sys.stderr)
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(content.encode("utf-8"))
    print("AsyncAPI written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
