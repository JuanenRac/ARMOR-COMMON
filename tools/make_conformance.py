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


def info(**changes):
    base = {"node_id": "north-1", "timestamp_ms": 1000, "name": "North gate", "firmware": "0.2.3", "ip": "192.168.0.181", "port": 80}
    base.update(changes)
    return base


def inverter(**changes):
    base = {"kind": "inverter", "node_id": "solar-1", "device": "axpert-1", "timestamp_ms": 1000, "mode": "line", "grid_v": 232.0, "grid_hz": 50.0, "out_v": 230.0,
            "out_hz": 50.0, "out_va": 161, "out_w": 119, "load_percent": 3, "battery_v": 57.5, "battery_a": 12.0, "battery_percent": 100, "pv_v": 103.8, "pv_a": 14.0,
            "pv_w": 856, "heatsink_c": 69, "ac_charging": False, "pv_charging": True, "load_on": True, "warnings": []}
    base.update(changes)
    return base


def battery(**changes):
    base = {"kind": "battery", "node_id": "solar-1", "device": "us3000-1", "timestamp_ms": 3000, "modules": 2, "state": "discharging", "voltage_v": 49.87, "current_a": -2.59,
            "temperature_min_c": 19.5, "temperature_max_c": 25.0, "cell_min_v": 3.328, "cell_max_v": 3.349, "soc_percent": 88, "alarm": False,
            "stack": [{"n": 1, "present": True, "voltage_v": 49.872, "current_a": -1.28, "temperature_c": 22.0, "soc_percent": 88, "state": "Dischg"}, {"n": 2, "present": False}]}
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
    "info": [
        ("a node on the LAN", True, info()),
        ("port at the top of the range", True, info(port=65535)),
        ("name of 48 characters", True, info(name="n" * 48)),
        ("name with accents", True, info(name="Perímetro norte")),
        ("uppercase node id", False, info(node_id="North-1")),
        ("empty name", False, info(name="")),
        ("name of 49 characters", False, info(name="n" * 49)),
        ("firmware with a v", False, info(firmware="v0.2.3")),
        ("firmware with two parts", False, info(firmware="0.2")),
        ("address with three parts", False, info(ip="192.168.0")),
        ("address above 255", False, info(ip="192.168.0.256")),
        ("address with a leading zero", False, info(ip="192.168.0.01")),
        ("host name instead of an address", False, info(ip="node.local")),
        ("port 0", False, info(port=0)),
        ("port above 65535", False, info(port=65536)),
        ("string port", False, info(port="80")),
        ("missing address", False, without(info(), "ip")),
        ("unknown field", False, info(mac="34:85:18:00:00:01")),
    ],
    "solar_inverter": [
        ("a typical reading", True, inverter()),
        ("running on the battery with two warnings", True, inverter(mode="battery", warnings=["line_fail", "battery_low"], battery_a=-8.5)),
        ("unknown mode", True, inverter(mode="unknown")),
        ("everything at zero", True, inverter(grid_v=0, grid_hz=0, out_v=0, out_hz=0, out_va=0, out_w=0, load_percent=0, battery_v=0, battery_a=0, battery_percent=0, pv_v=0, pv_a=0, pv_w=0, heatsink_c=0)),
        ("a device name of 32 characters", True, inverter(device="d" * 32)),
        ("thirty-two warnings, the limit", True, inverter(warnings=["w%d" % i for i in range(32)])),
        ("a mode the contract does not know", False, inverter(mode="sleeping")),
        ("uppercase device", False, inverter(device="Axpert-1")),
        ("device of 33 characters", False, inverter(device="d" * 33)),
        ("empty device", False, inverter(device="")),
        ("device starting with a dash", False, inverter(device="-axpert")),
        ("uppercase node id", False, inverter(node_id="Solar-1")),
        ("negative timestamp", False, inverter(timestamp_ms=-1)),
        ("the kind of a battery", False, inverter(kind="battery")),
        ("missing kind", False, without(inverter(), "kind")),
        ("missing mode", False, without(inverter(), "mode")),
        ("missing battery current", False, without(inverter(), "battery_a")),
        ("grid voltage above the limit", False, inverter(grid_v=601)),
        ("negative output power", False, inverter(out_w=-1)),
        ("battery percentage above 100", False, inverter(battery_percent=101)),
        ("battery current beyond the limit", False, inverter(battery_a=-1001)),
        ("heat-sink temperature below the limit", False, inverter(heatsink_c=-51)),
        ("string voltage", False, inverter(grid_v="230")),
        ("boolean voltage", False, inverter(grid_v=True)),
        ("numeric charging flag", False, inverter(ac_charging=1)),
        ("warnings is not a list", False, inverter(warnings="line_fail")),
        ("warning that is not a name", False, inverter(warnings=["Line fail"])),
        ("thirty-three warnings", False, inverter(warnings=["w%d" % i for i in range(33)])),
        ("unknown field", False, inverter(serial="92931903102538")),
        ("not an object", False, [1, 2]),
    ],
    "solar_battery": [
        ("a stack of two modules, one not there", True, battery()),
        ("charging", True, battery(state="charging", current_a=12.4)),
        ("idle", True, battery(state="idle", current_a=0.1)),
        ("state of charge left out", True, without(battery(), "soc_percent")),
        ("no module present", True, {"kind": "battery", "node_id": "solar-1", "device": "us3000-2", "timestamp_ms": 4000, "modules": 0, "stack": []}),
        ("sixteen modules, the limit", True, battery(modules=16, stack=[{"n": i + 1, "present": True} for i in range(16)])),
        ("an alarm", True, battery(alarm=True)),
        ("a module with its fifteen cells and temperatures", True, battery(stack=[{"n": 1, "present": True, "voltage_v": 49.872, "soc_percent": 88, "cells_v": [3.324 + 0.001 * i for i in range(15)], "temperatures_c": [22.0, 21.5, 22.5, 23.0, 21.0]}])),
        ("a module with thirty-two cells, the limit", True, battery(stack=[{"n": 1, "present": True, "cells_v": [3.3] * 32}])),
        ("a module with no cells listed", True, battery(stack=[{"n": 1, "present": True, "cells_v": []}])),
        ("thirty-three cells", False, battery(stack=[{"n": 1, "present": True, "cells_v": [3.3] * 33}])),
        ("a cell above ten volts", False, battery(stack=[{"n": 1, "present": True, "cells_v": [10.5]}])),
        ("a negative cell voltage", False, battery(stack=[{"n": 1, "present": True, "cells_v": [-0.1]}])),
        ("a cell voltage as a string", False, battery(stack=[{"n": 1, "present": True, "cells_v": ["3.3"]}])),
        ("cells that are not a list", False, battery(stack=[{"n": 1, "present": True, "cells_v": 3.3}])),
        ("nine temperature sensors", False, battery(stack=[{"n": 1, "present": True, "temperatures_c": [20.0] * 9}])),
        ("a temperature beyond the limit", False, battery(stack=[{"n": 1, "present": True, "temperatures_c": [201.0]}])),
        ("capacities, model and cycles", True, battery(model="US3000C", capacity_ah=140.5, full_capacity_ah=148.0, energy_kwh=7.0, cycles=312,
                                                       stack=[{"n": 1, "present": True, "capacity_ah": 70.2, "full_capacity_ah": 74.0, "cycles": 312}])),
        ("a model of 24 characters", True, battery(model="m" * 24)),
        ("an empty model", False, battery(model="")),
        ("a model of 25 characters", False, battery(model="m" * 25)),
        ("a negative capacity", False, battery(capacity_ah=-1)),
        ("a capacity above the limit", False, battery(full_capacity_ah=100001)),
        ("negative energy", False, battery(energy_kwh=-0.1)),
        ("fractional cycles", False, battery(cycles=1.5)),
        ("a module with a negative capacity", False, battery(stack=[{"n": 1, "present": True, "capacity_ah": -5}])),
        ("a module with fractional cycles", False, battery(stack=[{"n": 1, "present": True, "cycles": 2.5}])),
        ("seventeen modules", False, battery(modules=17)),
        ("seventeen entries in the stack", False, battery(stack=[{"n": (i % 16) + 1, "present": True} for i in range(17)])),
        ("a state that is not one of the three", False, battery(state="full")),
        ("state of charge above 100", False, battery(soc_percent=101)),
        ("state of charge as a null", False, battery(soc_percent=None)),
        ("fractional state of charge", False, battery(soc_percent=88.5)),
        ("cell voltage above the limit", False, battery(cell_max_v=10.1)),
        ("missing stack", False, without(battery(), "stack")),
        ("missing modules", False, without(battery(), "modules")),
        ("modules as a string", False, battery(modules="2")),
        ("module number 0", False, battery(stack=[{"n": 0, "present": True}])),
        ("module without its presence", False, battery(stack=[{"n": 1}])),
        ("module with an unknown field", False, battery(stack=[{"n": 1, "present": True, "cells": 15}])),
        ("module state of 17 characters", False, battery(stack=[{"n": 1, "present": True, "state": "s" * 17}])),
        ("the kind of an inverter", False, battery(kind="inverter")),
        ("uppercase device", False, battery(device="US3000")),
        ("unknown field", False, battery(serial="PPTBH01")),
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
    schema_kind = {"solar_inverter": "inverter", "solar_battery": "battery"}.get(kind, kind)   # the solar files are named after their schema, and carry the payload's kind
    (ROOT / f"{kind}.json").write_text(json.dumps({"kind": schema_kind, "vectors": vectors}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(kind, len(vectors), "vectors")
