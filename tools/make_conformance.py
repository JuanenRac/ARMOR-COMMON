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


def electrical(**changes):
    base = {"kind": "electrical", "node_id": "electrical-1", "timestamp_ms": 5000, "channels": [
        {"id": "grid", "domain": "ac", "label": "Grid input", "voltage_v": 231.4, "current_a": 12.6, "power_w": 2810.5, "energy_kwh": 5230.4, "frequency_hz": 49.98, "power_factor": 0.97, "state": "closed", "alarm": False}]}
    base.update(changes)
    return base


def channel(**changes):
    return electrical(channels=[dict({"id": "ch1", "domain": "ac"}, **changes)])


def switch(**changes):
    base = {"id": "transfer", "kind": "transfer", "label": "Grid or inverter", "source_a": "grid", "source_b": "inverter", "a_closed": True, "b_closed": False,
            "selected": "a", "wanted": "a", "closing": False, "armed": False, "fault": "none"}
    base.update(changes)
    return base


def with_switch(**changes):
    return electrical(switching_enabled=True, switches=[switch(**changes)])


def command(**changes):
    base = {"kind": "electrical_command", "node_id": "electrical-1", "timestamp_ms": 7000, "command_id": "c0ffee0123456789", "switch": "transfer", "action": "arm"}
    base.update(changes)
    return base


def result(**changes):
    base = {"kind": "electrical_result", "node_id": "electrical-1", "timestamp_ms": 7100, "command_id": "c0ffee0123456789", "switch": "transfer", "action": "open",
            "accepted": True, "refusal": "none"}
    base.update(changes)
    return base


def net_device(**changes):
    base = {"id": "14:2e:5e:86:d9:62", "ip": "192.168.0.1", "mac": "14:2e:5e:86:d9:62", "vendor": "Sagemcom Broadband SAS", "hostname": "router", "kind": "router", "os": "network gear",
            "online": True, "first_seen_ms": 1790000000000, "last_seen_ms": 1790000060000, "latency_ms": 1.4,
            "ports": [{"port": 80, "proto": "tcp", "service": "http", "banner": "Router login"}, {"port": 443, "proto": "tcp", "service": "https"}], "services": ["_http._tcp"]}
    base.update(changes)
    return base


def net_event(**changes):
    base = {"id": "e1", "kind": "new_device", "at_ms": 1790000030000, "device_id": "96:b3:ed:0b:1c:18", "detail": "A device that was never seen has joined the network"}
    base.update(changes)
    return base


def network(**changes):
    base = {"kind": "network", "node_id": "network-1", "timestamp_ms": 1790000060000,
            "interface": {"name": "Ethernet", "ip": "192.168.0.10", "cidr": "192.168.0.0/24", "gateway": "192.168.0.1", "rx_bps": 1200000, "tx_bps": 340000},
            "internet": {"state": "up", "since_ms": 1789990000000, "gateway_ok": True, "latency_ms": 12.5, "loss_percent": 0.0,
                         "probes": [{"target": "1.1.1.1", "kind": "tcp", "ok": True, "latency_ms": 11.2}, {"target": "8.8.8.8", "kind": "dns", "ok": True, "latency_ms": 13.8}],
                         "last_outage": {"started_ms": 1789900000000, "ended_ms": 1789900300000, "duration_s": 300}, "outages_24h": 1, "downtime_24h_s": 300},
            "devices": [net_device()], "events": [net_event()], "scan": {"last_ms": 1790000050000, "hosts": 254, "duration_ms": 9000}}
    base.update(changes)
    return base


def internet(**changes):
    return network(internet=dict(network()["internet"], **changes))


def dev(**changes):
    return network(devices=[net_device(**changes)])


def without(payload, key):
    return {name: value for name, value in payload.items() if name != key}


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
        ("a second PV input", True, inverter(pv2_v=327.3, pv2_a=3.1, pv2_w=1026, pv_w=1882)),
        ("the second PV input at zero", True, inverter(pv2_v=0, pv2_a=0, pv2_w=0)),
        ("a second PV voltage above the limit", False, inverter(pv2_v=1501)),
        ("a negative second PV power", False, inverter(pv2_w=-1)),
        ("a second PV current as a string", False, inverter(pv2_a="3.1")),
        ("two units of a parallel system", True, inverter(units=[{"unit": 0, "serial": "92931701100510", "mode": "line", "fault_code": "00", "grid_v": 230.6, "out_v": 230.6, "out_va": 275, "out_w": 141, "load_percent": 5, "battery_v": 51.4, "battery_percent": 100, "pv_v": 83.3, "charging_a": 1}, {"unit": 1, "mode": "battery"}], total_out_w=312, total_out_va=574, total_load_percent=3, total_charging_a=2)),
        ("ten units, the limit", True, inverter(units=[{"unit": i, "mode": "line"} for i in range(10)])),
        ("eleven units", False, inverter(units=[{"unit": i % 10, "mode": "line"} for i in range(11)])),
        ("units that are not a list", False, inverter(units={"unit": 0, "mode": "line"})),
        ("a unit without its number", False, inverter(units=[{"mode": "line"}])),
        ("a unit without its mode", False, inverter(units=[{"unit": 0}])),
        ("a unit number of 10", False, inverter(units=[{"unit": 10, "mode": "line"}])),
        ("a unit with a mode the contract does not know", False, inverter(units=[{"unit": 0, "mode": "sleeping"}])),
        ("a unit with a one-digit fault code", False, inverter(units=[{"unit": 0, "mode": "fault", "fault_code": "7"}])),
        ("a unit with an unknown field", False, inverter(units=[{"unit": 0, "mode": "line", "colour": "red"}])),
        ("a negative total output power", False, inverter(total_out_w=-1)),
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
        ("health of the stack and of a module", True, battery(health_percent=78, stack=[{"n": 1, "present": True, "health_percent": 100}, {"n": 2, "present": True, "health_percent": 56}])),
        ("health of zero", True, battery(health_percent=0)),
        ("health above 100", False, battery(health_percent=101)),
        ("fractional health", False, battery(health_percent=55.5)),
        ("a module with negative health", False, battery(stack=[{"n": 1, "present": True, "health_percent": -1}])),
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
    "electrical": [
        ("a whole channel", True, electrical()),
        ("no channels yet", True, electrical(channels=[])),
        ("sixteen channels, the limit", True, electrical(channels=[{"id": f"c{i}", "domain": "ac"} for i in range(16)])),
        ("a DC channel", True, channel(domain="dc", voltage_v=52.1, current_a=-14.2, power_w=-740.0)),
        ("a node that says it may switch", True, electrical(switching_enabled=True)),
        ("an open switch and an alarm", True, channel(state="open", alarm=True, alarm_code="over_current")),
        ("power fed to the network", True, channel(power_w=-1500.0)),
        ("seventeen channels", False, electrical(channels=[{"id": f"c{i}", "domain": "ac"} for i in range(17)])),
        ("a channel with no domain", False, electrical(channels=[{"id": "ch1"}])),
        ("a channel with no id", False, electrical(channels=[{"domain": "ac"}])),
        ("a domain that is neither AC nor DC", False, channel(domain="hv")),
        ("uppercase channel id", False, channel(id="Grid")),
        ("a channel id of 33 characters", False, electrical(channels=[{"id": "c" * 33, "domain": "ac"}])),
        ("voltage above the limit", False, channel(voltage_v=1000.5)),
        ("negative voltage", False, channel(voltage_v=-1)),
        ("current beyond the limit", False, channel(current_a=1000.5)),
        ("negative energy", False, channel(energy_kwh=-0.1)),
        ("power factor above 1", False, channel(power_factor=1.01)),
        ("frequency above 100", False, channel(frequency_hz=100.1)),
        ("a state that is a command", False, channel(state="close")),
        ("an alarm code with capitals", False, channel(alarm_code="OverCurrent")),
        ("an empty label", False, channel(label="")),
        ("a string where a number should be", False, channel(voltage_v="231")),
        ("an unknown field in a channel", False, channel(relay_pin=4)),
        ("an unknown field in the message", False, electrical(command="close")),
        ("a message of another kind", False, electrical(kind="inverter")),
        ("missing channels", False, {"kind": "electrical", "node_id": "electrical-1", "timestamp_ms": 5000}),
        ("a node id with a space", False, electrical(node_id="my node")),
        ("negative timestamp", False, electrical(timestamp_ms=-1)),
        ("channels that are not a list", False, electrical(channels={"id": "grid"})),
        ("a transfer switch in a state message", True, with_switch()),
        ("a switch that is closing", True, with_switch(a_closed=False, selected="none", wanted="b", closing=True, armed=False)),
        ("an armed switch with nothing closed", True, with_switch(a_closed=False, selected="none", wanted="none", armed=True)),
        ("a latched fault, everything open", True, with_switch(a_closed=False, selected="none", wanted="none", fault="did_not_close")),
        ("both contacts closed, a fault", True, with_switch(b_closed=True, selected="none", wanted="none", fault="both_closed")),
        ("a switch with no label or sources", True, electrical(switches=[{k: v for k, v in switch().items() if k not in ("label", "source_a", "source_b")}])),
        ("no switches at all", True, electrical(switches=[])),
        ("four switches, the limit", True, electrical(switches=[switch(id=f"t{i}") for i in range(4)])),
        ("five switches", False, electrical(switches=[switch(id=f"t{i}") for i in range(5)])),
        ("a switch id twice", False, electrical(switches=[switch(), switch()]), True),
        ("a switch without its contacts", False, electrical(switches=[{k: v for k, v in switch().items() if k != "a_closed"}])),
        ("a switch without its fault", False, electrical(switches=[{k: v for k, v in switch().items() if k != "fault"}])),
        ("a switch of a kind that does not exist", False, with_switch(kind="breaker")),
        ("a source that is not a source", False, with_switch(selected="c")),
        ("a wanted state that is a command", False, with_switch(wanted="close_a")),
        ("a fault outside the list", False, with_switch(fault="welded")),
        ("a contact that is a string", False, with_switch(a_closed="true")),
        ("a switch with an unknown field", False, with_switch(coil_pin=4)),
        ("a switch id with capitals", False, with_switch(id="Transfer")),
        ("an empty switch label", False, with_switch(label="")),
        ("switches that are not a list", False, electrical(switches={"id": "transfer"})),
    ],
    "electrical_command": [
        ("arm a switch", True, command()),
        ("open a switch", True, command(action="open")),
        ("acknowledge a fault", True, command(action="acknowledge")),
        ("close onto source A with its token", True, command(action="close_a", token="ab12cd34ef56ab12")),
        ("close onto source B with its token", True, command(action="close_b", token="ab12cd34ef56ab12")),
        ("a token of eight characters, the shortest", True, command(action="close_a", token="ab12cd34")),
        ("close with no token", False, command(action="close_a"), True),
        ("an arm that carries a token", False, command(token="ab12cd34ef56ab12"), True),
        ("an open that carries a token", False, command(action="open", token="ab12cd34ef56ab12"), True),
        ("an action outside the list", False, command(action="toggle")),
        ("an action that is a source", False, command(action="a")),
        ("uppercase action", False, command(action="ARM")),
        ("a token of seven characters", False, command(action="close_a", token="ab12cd3")),
        ("a token of 33 characters", False, command(action="close_a", token="a" * 33)),
        ("a token with capitals", False, command(action="close_a", token="AB12CD34EF56AB12")),
        ("a command id of seven characters", False, command(command_id="c0ffee0")),
        ("a command id with a dash", False, command(command_id="c0ffee01-2345")),
        ("no command id", False, {k: v for k, v in command().items() if k != "command_id"}),
        ("no switch", False, {k: v for k, v in command().items() if k != "switch"}),
        ("no action", False, {k: v for k, v in command().items() if k != "action"}),
        ("a switch id with a space", False, command(switch="my switch")),
        ("a node id with a space", False, command(node_id="my node")),
        ("negative timestamp", False, command(timestamp_ms=-1)),
        ("the kind of a state message", False, command(kind="electrical")),
        ("an unknown field", False, command(force=True)),
        ("a coil to drive directly", False, command(coil="a")),
    ],
    "electrical_result": [
        ("an open, accepted", True, result()),
        ("an arm, accepted, with its token", True, result(action="arm", token="ab12cd34ef56ab12")),
        ("a close, accepted", True, result(action="close_a")),
        ("a close refused: not armed", True, result(action="close_a", accepted=False, refusal="not_armed")),
        ("a close refused: switching is off", True, result(action="close_b", accepted=False, refusal="disabled")),
        ("an arm refused: a fault is latched", True, result(action="arm", accepted=False, refusal="fault")),
        ("an acknowledge refused: contacts not open", True, result(action="acknowledge", accepted=False, refusal="not_confirmed_open")),
        ("a command to a switch it does not have", True, result(switch="nothing", accepted=False, refusal="unknown_switch")),
        ("a wrong token", True, result(action="close_a", accepted=False, refusal="bad_token")),
        ("a node that cannot do it", True, result(action="close_a", accepted=False, refusal="not_supported")),
        ("accepted with a refusal", False, result(refusal="disabled"), True),
        ("refused with refusal none", False, result(accepted=False), True),
        ("a token in the result of an open", False, result(token="ab12cd34ef56ab12"), True),
        ("a token in the result of a refused arm", False, result(action="arm", accepted=False, refusal="disabled", token="ab12cd34ef56ab12"), True),
        ("an accepted arm without a token", False, result(action="arm"), True),
        ("a refusal outside the list", False, result(accepted=False, refusal="welded")),
        ("an action outside the list", False, result(action="toggle")),
        ("accepted as a string", False, result(accepted="true")),
        ("no command id", False, {k: v for k, v in result().items() if k != "command_id"}),
        ("no refusal", False, {k: v for k, v in result().items() if k != "refusal"}),
        ("no accepted", False, {k: v for k, v in result().items() if k != "accepted"}),
        ("a command id of seven characters", False, result(command_id="c0ffee0")),
        ("a token with capitals", False, result(action="arm", token="AB12CD34EF56AB12")),
        ("the kind of a command", False, result(kind="electrical_command")),
        ("a node id with a space", False, result(node_id="my node")),
        ("an unknown field", False, result(detail="welded")),
    ],
    "network": [
        ("a whole network state", True, network()),
        ("the public address of the connection", True, network(public={"ip": "203.0.113.9", "hostname": "host-203-0-113-9.example.net", "city": "Madrid", "region": "Madrid", "country": "ES", "org": "AS64496 EXAMPLE TELECOM", "timezone": "Europe/Madrid", "checked_ms": 1790000050000, "changed_ms": 1789990000000})),
        ("only the public address", True, network(public={"ip": "203.0.113.9", "checked_ms": 5})),
        ("a public address that is not an address of text", False, network(public={"ip": 12, "checked_ms": 5})),
        ("a public address with no time", False, network(public={"ip": "203.0.113.9"})),
        ("an unknown field in the public block", False, network(public={"ip": "203.0.113.9", "checked_ms": 5, "isp_login": "x"})),
        ("the result of a ping", True, network(results=[{"id": "c1a2b3", "type": "ping", "ok": True, "finished_ms": 5, "device_id": "14:2e:5e:86:d9:62", "latency_ms": 1.3, "output": "1 packet, 1 received"}])),
        ("the result of a traceroute", True, network(results=[{"id": "c1a2b4", "type": "traceroute", "ok": True, "finished_ms": 5, "output": " 1  192.168.0.1  1.2 ms\n 2  10.10.0.1  5.1 ms"}])),
        ("the result of a look at the ports", True, network(results=[{"id": "c1a2b5", "type": "ports", "ok": True, "finished_ms": 5, "device_id": "14:2e:5e:86:d9:62", "ports": [{"port": 80, "proto": "tcp", "service": "http", "banner": "Router login"}]}])),
        ("a result that failed", True, network(results=[{"id": "c1a2b6", "type": "wake", "ok": False, "finished_ms": 5, "output": "the device has no MAC address"}])),
        ("a result of a kind that is not one", False, network(results=[{"id": "c1a2b7", "type": "reboot", "ok": True, "finished_ms": 5}])),
        ("a result with no id", False, network(results=[{"type": "ping", "ok": True, "finished_ms": 5}])),
        ("17 results", False, network(results=[{"id": f"c{i:05d}", "type": "ping", "ok": True, "finished_ms": 5} for i in range(17)])),
        ("an output of 2001 characters", False, network(results=[{"id": "c1a2b8", "type": "traceroute", "ok": True, "finished_ms": 5, "output": "x" * 2001}])),
        ("nothing found yet", True, network(devices=[], events=[])),
        ("the smallest state", True, {"kind": "network", "node_id": "network-1", "timestamp_ms": 1, "interface": {"name": "eth0", "ip": "10.0.0.2", "cidr": "10.0.0.0/24"},
                                      "internet": {"state": "unknown"}, "devices": []}),
        ("the internet is down and the router answers", True, internet(state="down", gateway_ok=True, loss_percent=100.0)),
        ("the local network is down", True, internet(state="lan_down", gateway_ok=False)),
        ("degraded internet", True, internet(state="degraded", latency_ms=480.0, loss_percent=35.5)),
        ("a device known only by its address", True, network(devices=[{"id": "ip-192-168-0-77", "ip": "192.168.0.77", "online": True, "first_seen_ms": 5, "last_seen_ms": 5}])),
        ("a phone with a randomised MAC", True, dev(id="96:b3:ed:0b:1c:18", mac="96:b3:ed:0b:1c:18", ip="192.168.0.12", randomized_mac=True, kind="phone")),
        ("a device that went offline", True, dev(online=False)),
        ("an internet outage that ended", True, network(events=[{"id": "e2", "kind": "internet_up", "at_ms": 5, "outage_s": 420}])),
        ("an internet outage that began", True, network(events=[{"id": "e3", "kind": "internet_down", "at_ms": 5}])),
        ("a port that opened", True, network(events=[net_event(id="e4", kind="port_opened", port=23)])),
        ("an ARP conflict", True, network(events=[net_event(id="e5", kind="arp_conflict", detail="192.168.0.1 answers from two addresses")])),
        ("512 devices, the limit", True, network(devices=[{"id": f"ip-10-0-{i // 250}-{i % 250 + 1}", "ip": f"10.0.{i // 250}.{i % 250 + 1}", "online": True, "first_seen_ms": 1, "last_seen_ms": 2} for i in range(512)])),
        ("513 devices", False, network(devices=[{"id": f"ip-10-0-{i // 250}-{i % 250 + 1}", "ip": f"10.0.{i // 250}.{i % 250 + 1}", "online": True, "first_seen_ms": 1, "last_seen_ms": 2} for i in range(513)])),
        ("65 ports on a device", False, dev(ports=[{"port": i + 1, "proto": "tcp"} for i in range(65)])),
        ("17 services on a device", False, dev(services=[f"_s{i}._tcp" for i in range(17)])),
        ("65 events", False, network(events=[{"id": f"e{i}", "kind": "internet_down", "at_ms": 1} for i in range(65)])),
        ("nine probes", False, internet(probes=[{"target": f"h{i}", "kind": "tcp", "ok": True} for i in range(9)])),
        ("no interface", False, without(network(), "interface")),
        ("no internet", False, without(network(), "internet")),
        ("no devices", False, without(network(), "devices")),
        ("an internet state that is not one", False, internet(state="offline")),
        ("an address with an octet of 256", False, network(interface={"name": "eth0", "ip": "192.168.0.256", "cidr": "192.168.0.0/24"})),
        ("a prefix of 33", False, network(interface={"name": "eth0", "ip": "192.168.0.10", "cidr": "192.168.0.0/33"})),
        ("an address with a leading zero", False, dev(ip="192.168.000.1")),
        ("a MAC in capitals", False, dev(mac="14:2E:5E:86:D9:62")),
        ("a MAC with dashes", False, dev(mac="14-2e-5e-86-d9-62")),
        ("a device id with a space", False, dev(id="my device")),
        ("a device with no address", False, network(devices=[{k: v for k, v in net_device().items() if k != "ip"}])),
        ("a device with no online flag", False, network(devices=[{k: v for k, v in net_device().items() if k != "online"}])),
        ("a device kind that is not one", False, dev(kind="toaster")),
        ("a port of 0", False, dev(ports=[{"port": 0, "proto": "tcp"}])),
        ("a port of 65536", False, dev(ports=[{"port": 65536, "proto": "tcp"}])),
        ("a protocol that is not one", False, dev(ports=[{"port": 80, "proto": "icmp"}])),
        ("a banner of 81 characters", False, dev(ports=[{"port": 80, "proto": "tcp", "banner": "b" * 81}])),
        ("an empty hostname", False, dev(hostname="")),
        ("a negative latency", False, dev(latency_ms=-1)),
        ("loss above 100", False, internet(loss_percent=100.5)),
        ("a probe of a kind that is not one", False, internet(probes=[{"target": "1.1.1.1", "kind": "ping", "ok": True}])),
        ("a probe with no result", False, internet(probes=[{"target": "1.1.1.1", "kind": "tcp"}])),
        ("an outage without its duration", False, internet(last_outage={"started_ms": 1, "ended_ms": 2})),
        ("more than a day of downtime in a day", False, internet(downtime_24h_s=86401)),
        ("an event of a kind that is not one", False, network(events=[net_event(kind="attack")])),
        ("an event with no time", False, network(events=[{k: v for k, v in net_event().items() if k != "at_ms"}])),
        ("an event id with capitals", False, network(events=[net_event(id="E1")])),
        ("a string where a number should be", False, network(timestamp_ms="1790000060000")),
        ("a negative timestamp", False, network(timestamp_ms=-1)),
        ("a node id with a space", False, network(node_id="my node")),
        ("the kind of another message", False, network(kind="electrical")),
        ("an unknown field in the message", False, network(command="scan")),
        ("an unknown field in a device", False, dev(password="admin")),
        ("an unknown field in a port", False, dev(ports=[{"port": 80, "proto": "tcp", "exploit": "x"}])),
        ("an unknown field in the internet block", False, internet(dns_server="1.1.1.1")),
        ("an unknown field in the interface", False, network(interface={"name": "eth0", "ip": "10.0.0.2", "cidr": "10.0.0.0/24", "password": "x"})),
        ("a device named twice", False, network(devices=[net_device(), net_device()]), True),
        ("a MAC that is not the id", False, dev(id="aa:bb:cc:dd:ee:ff"), True),
        ("first seen after last seen", False, dev(first_seen_ms=10, last_seen_ms=5), True),
        ("an event named twice", False, network(events=[net_event(), net_event()]), True),
        ("an internet event about a device", False, network(events=[{"id": "e6", "kind": "internet_down", "at_ms": 1, "device_id": "14:2e:5e:86:d9:62"}]), True),
        ("an internet event about a port", False, network(events=[{"id": "e7", "kind": "gateway_down", "at_ms": 1, "port": 80}]), True),
        ("a device event that names no device", False, network(events=[{"id": "e8", "kind": "new_device", "at_ms": 1}]), True),
        ("a duration on an event that is not an end", False, network(events=[net_event(id="e9", outage_s=5)]), True),
        ("a port event that names no port", False, network(events=[net_event(id="e10", kind="port_opened")]), True),
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
    # A fourth item, True, marks a payload the schema accepts and the message-level rule refuses (a token where none belongs, a switch named twice).
    vectors = [{"name": name, "valid": valid, "payload": payload, **({"schema_valid": True} if extra else {})} for name, valid, payload, *extra in entries]
    schema_kind = {"solar_inverter": "inverter", "solar_battery": "battery"}.get(kind, kind)   # the solar files are named after their schema, and carry the payload's kind
    (ROOT / f"{kind}.json").write_text(json.dumps({"kind": schema_kind, "vectors": vectors}, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(kind, len(vectors), "vectors")
