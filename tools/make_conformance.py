#!/usr/bin/env python3
"""Write the shared conformance vectors.

Every implementation of the contracts (Python here, TypeScript in ARMOR-SERVER,
Kotlin in ARMOR-ANDROID-CONTROL) must accept every ``valid`` vector and reject
every other one. Adding a case here is how a contract gets tightened.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "conformance"
track = {"sensor_id": 1, "track_id": 1, "x_mm": 1200.5, "y_mm": -300, "speed_mm_s": 0}


def telemetry(**changes):
    base = {"node_id": "north-1", "timestamp_ms": 1000, "lux": 250.5, "targets": [dict(track)]}
    base.update(changes)
    return base


def without(payload, key):
    return {name: value for name, value in payload.items() if name != key}


cases = {
    "telemetry": [
        ("minimal, no targets", True, telemetry(targets=[])),
        ("one target", True, telemetry()),
        ("fifteen targets, the limit", True, telemetry(targets=[dict(track, track_id=i + 1, sensor_id=(i % 3) + 1) for i in range(15)])),
        ("zero lux", True, telemetry(lux=0)),
        ("lux at the sensor limit", True, telemetry(lux=200000)),
        ("negative coordinates and speed", True, telemetry(targets=[dict(track, x_mm=-5000, y_mm=-1, speed_mm_s=-785.4)])),
        ("node id with digits, dash and underscore", True, telemetry(node_id="node_2-b")),
        ("sixteen targets", False, telemetry(targets=[dict(track) for _ in range(16)])),
        ("uppercase node id", False, telemetry(node_id="North-1")),
        ("node id starting with a dash", False, telemetry(node_id="-north")),
        ("node id too long", False, telemetry(node_id="a" * 65)),
        ("empty node id", False, telemetry(node_id="")),
        ("negative timestamp", False, telemetry(timestamp_ms=-1)),
        ("fractional timestamp", False, telemetry(timestamp_ms=1.5)),
        ("string timestamp", False, telemetry(timestamp_ms="1000")),
        ("boolean timestamp", False, telemetry(timestamp_ms=True)),
        ("negative lux", False, telemetry(lux=-0.1)),
        ("lux above the limit", False, telemetry(lux=200001)),
        ("boolean lux", False, telemetry(lux=True)),
        ("string lux", False, telemetry(lux="12")),
        ("missing lux", False, without(telemetry(), "lux")),
        ("missing targets", False, without(telemetry(), "targets")),
        ("targets is not a list", False, telemetry(targets={})),
        ("unknown top-level field", False, telemetry(extra=1)),
        ("target sensor 0", False, telemetry(targets=[dict(track, sensor_id=0)])),
        ("target sensor 4", False, telemetry(targets=[dict(track, sensor_id=4)])),
        ("target track 0", False, telemetry(targets=[dict(track, track_id=0)])),
        ("fractional track id", False, telemetry(targets=[dict(track, track_id=1.5)])),
        ("target with a missing field", False, telemetry(targets=[without(track, "speed_mm_s")])),
        ("target with an unknown field", False, telemetry(targets=[dict(track, z_mm=1)])),
        ("boolean coordinate", False, telemetry(targets=[dict(track, x_mm=True)])),
        ("target is not an object", False, telemetry(targets=[7])),
        ("not an object", False, [1, 2]),
    ],
    "health": [
        ("online node", True, {"node_id": "north-1", "timestamp_ms": 5, "online": True}),
        ("offline node", True, {"node_id": "north-1", "timestamp_ms": 0, "online": False}),
        ("string online flag", False, {"node_id": "north-1", "timestamp_ms": 5, "online": "yes"}),
        ("numeric online flag", False, {"node_id": "north-1", "timestamp_ms": 5, "online": 1}),
        ("missing online", False, {"node_id": "north-1", "timestamp_ms": 5}),
        ("negative timestamp", False, {"node_id": "north-1", "timestamp_ms": -5, "online": True}),
        ("unknown field", False, {"node_id": "north-1", "timestamp_ms": 5, "online": True, "temp_c": 20}),
        ("uppercase node id", False, {"node_id": "NORTH", "timestamp_ms": 5, "online": True}),
    ],
    "command": [
        ("calibrate", True, {"node_id": "north-1", "timestamp_ms": 9, "command": "calibrate"}),
        ("restart", True, {"node_id": "north-1", "timestamp_ms": 9, "command": "restart"}),
        ("thresholds with a sensitivity", True, {"node_id": "north-1", "timestamp_ms": 9, "command": "set_thresholds", "sensitivity": 7}),
        ("command outside the allow-list", False, {"node_id": "north-1", "timestamp_ms": 9, "command": "format_flash"}),
        ("uppercase command", False, {"node_id": "north-1", "timestamp_ms": 9, "command": "RESTART"}),
        ("sensitivity above 10", False, {"node_id": "north-1", "timestamp_ms": 9, "command": "set_thresholds", "sensitivity": 11}),
        ("sensitivity 0", False, {"node_id": "north-1", "timestamp_ms": 9, "command": "set_thresholds", "sensitivity": 0}),
        ("missing command", False, {"node_id": "north-1", "timestamp_ms": 9}),
        ("unknown field", False, {"node_id": "north-1", "timestamp_ms": 9, "command": "restart", "shell": "rm -rf /"}),
    ],
}

ROOT.mkdir(exist_ok=True)
for kind, entries in cases.items():
    vectors = [{"name": name, "valid": valid, "payload": payload} for name, valid, payload in entries]
    (ROOT / f"{kind}.json").write_text(json.dumps({"kind": kind, "vectors": vectors}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(kind, len(vectors), "vectors")
