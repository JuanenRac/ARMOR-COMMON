#!/usr/bin/env python3
"""Write the shared conformance vectors.

Every implementation of the contracts (Python here, TypeScript in ARMOR-SERVER,
Kotlin in ARMOR-ANDROID-CONTROL) must accept every ``valid`` vector and reject
every other one. Adding a case here is how a contract gets tightened.
"""
import json
import sys
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


def bat_command(**changes):
    base = {"kind": "solar_battery_command", "node_id": "solar-1", "timestamp_ms": 9000, "command_id": "b0b0b0b012345678", "port": 2, "action": "arm", "op": "output_set",
            "params": {"output": "cfet", "state": "off"}, "serial": "PPTBH02200409223"}
    base.update(changes)
    return base


def bat_execute(**changes):
    return bat_command(action="execute", token="0123456789abcdef0123456789abcdef", **changes)


def bat_stage(**changes):
    base = {"id": "ab12cd34ef56ab12", "index": 0, "total": 782, "size": 200000, "crc32": 305419896, "data": "QUJDRA=="}
    base.update(changes)
    return {"kind": "solar_battery_command", "node_id": "solar-1", "timestamp_ms": 9000, "command_id": "b0b0b0b012345679", "port": 2, "action": "stage", "stage": base}


def bat_without(payload, *names):
    return {k: v for k, v in payload.items() if k not in names}


MODULE_VOLTAGE = {"pov": 58000, "povr": 55000, "phv": 57600, "phvr": 55500, "plv": 47000, "plvr": 48000, "puv": 44000, "puvr": 45000, "pslp": 42000}
TEMPERATURE = {"cot": 60000, "cotr": 55000, "cht": 50000, "chtr": 45000, "clt": 5000, "cltr": 8000, "cut": -5000, "cutr": -2000}
BATTERY = {"model": "US3000C", "serial": "PPTBH02200409223", "soft_version": "V3.0", "board": ""}
ARMED_ONLY = ("token", "battery", "canonical", "summary", "risk", "atomic")


def bat_result(**changes):
    base = {"kind": "solar_battery_result", "node_id": "solar-1", "timestamp_ms": 9100, "command_id": "b0b0b0b012345678", "port": 2, "action": "arm", "op": "output_set", "stage": "armed",
            "accepted": True, "refusal": "none", "token": "0123456789abcdef0123456789abcdef", "canonical": "output_set cfet off", "summary": "switch cfet off", "risk": "medium", "atomic": False,
            "battery": dict(BATTERY)}
    base.update(changes)
    return base


def bat_plain(**changes):
    """An answer that is not an armed one: no token, no battery, no description of the operation."""
    return bat_without(bat_result(**changes), *ARMED_ONLY)


def bat_final(**changes):
    base = {"kind": "solar_battery_result", "node_id": "solar-1", "timestamp_ms": 9200, "command_id": "b0b0b0b012345680", "port": 2, "action": "execute", "op": "output_set", "stage": "final",
            "accepted": True, "refusal": "none", "outcome": "ok", "steps_done": 9, "steps_total": 9, "writes_done": 1, "before": "## info\nDevice name : US3000C\n", "after": "## output\ncfet : OFF\n",
            "transcript": "> ctrl cfet off\n"}
    base.update(changes)
    return base


def alarm(**changes):
    base = {"kind": "alarm", "node_id": "alarm-1", "timestamp_ms": 1000, "phase": "armed", "mode": "away", "siren": False, "locked_out": False, "commands_enabled": True,
            "zones": [{"id": "front-door", "name": "Front door", "kind": "entry", "state": "normal", "bypassed": False},
                      {"id": "window", "kind": "instant", "state": "normal", "bypassed": False}],
            "open_zones": [], "events": [{"ago_s": 12, "kind": "armed"}]}
    base.update(changes)
    return base


def zone(**changes):
    return alarm(zones=[dict({"id": "front-door", "kind": "entry", "state": "normal", "bypassed": False}, **changes)], open_zones=[], events=[])


def alarm_command(**changes):
    base = {"kind": "alarm_command", "node_id": "alarm-1", "timestamp_ms": 7000, "command_id": "c0ffee0123456789", "action": "arm", "mode": "away"}
    base.update(changes)
    return base


def alarm_result(**changes):
    base = {"kind": "alarm_result", "node_id": "alarm-1", "timestamp_ms": 7100, "command_id": "c0ffee0123456789", "action": "arm", "accepted": True, "refusal": "none", "phase": "exit_delay"}
    base.update(changes)
    return base


def node_health(**changes):
    base = {"kind": "node_health", "node_id": "alarm-1", "timestamp_ms": 9000, "family": "alarm", "firmware": "0.3.6", "board": "s3-eth", "uptime_s": 86400, "reset_reason": "power_on",
            "heap_free": 142000, "heap_min": 98000, "link": "ethernet", "link_up": True, "broker_reconnects": 1, "low_stack_tasks": 0}
    base.update(changes)
    return base


def wifi_health(**changes):
    return node_health(**dict({"link": "wifi", "rssi_dbm": -61}, **changes))


def profile(**changes):
    base = {"id": "night", "name": "Night", "base": "stay", "entry_delay_s": 45, "siren": True, "notify": "urgent",
            "zones": [{"id": "hall-motion", "armed": True}, {"id": "front-door", "delay": "entry"}, {"id": "garage", "armed": False}]}
    base.update(changes)
    return base


def alarm_profile_command(**changes):
    return alarm_command(**dict({"mode": "stay", "profile": profile()}, **changes))


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


def zone_feed(**changes):
    base = {"zone": "front-door", "state": "triggered", "battery_low": False}
    base.update(changes)
    return base


def server_alert(**changes):
    base = {"service": "armor-server", "event": "alarm.raised", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "alarm_id": "a1", "severity": "critical", "code": "smoke", "device_id": "smoke-1"}
    base.update(changes)
    return base


def orders(**changes):
    base = {"accepted": True, "commands": [{"id": "c0123456789", "type": "ping", "device_id": "14:2e:5e:86:d9:62", "ip": "192.168.0.1"}]}
    base.update(changes)
    return base


def order(**changes):
    return orders(commands=[dict({"id": "c0123456789", "type": "ping", "device_id": "14:2e:5e:86:d9:62", "ip": "192.168.0.1"}, **changes)])


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


def connection_event(**changes):
    base = {"id": 7, "at": "2026-01-01T10:00:00.000Z", "type": "connection", "action": "login", "client_kind": "studio", "client_id": "0123456789abcdef", "user": "ana", "origin": "local", "two_factor": False}
    base.update(changes)
    return base


def system_event(**changes):
    base = {"id": 8, "at": "2026-01-01T10:00:00.000Z", "type": "system", "category": "node", "action": "appeared", "subject": "alarm-1", "version": "0.3.7"}
    base.update(changes)
    return base


def connection_client(**changes):
    base = {"id": "0123456789abcdef", "kind": "android", "user": "ana", "app_version": "0.6.6", "first_seen": "2026-01-01T10:00:00.000Z", "last_seen": "2026-01-02T10:00:00.000Z", "active_sessions": 1, "logins_ok": 3, "logins_failed": 0}
    base.update(changes)
    return base


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
        ("node id with a line feed at the end", False, telemetry(node_id="north-1\n")),
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
        ("a wall panel", True, {"node_id": "hall-panel", "timestamp_ms": 5, "online": True, "kind": "panel"}),
        ("a radar that says it is one", True, {"node_id": "north-1", "timestamp_ms": 5, "online": True, "kind": "radar"}),
        ("a kind that does not exist", False, {"node_id": "north-1", "timestamp_ms": 5, "online": True, "kind": "toaster"}),
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
        ("firmware with four parts, from 0.8.0 on", True, info(firmware="0.8.0.1")),
        ("firmware with a v", False, info(firmware="v0.2.3")),
        ("firmware with two parts", False, info(firmware="0.2")),
        ("firmware with five parts", False, info(firmware="0.8.0.1.2")),
        ("firmware with a line feed at the end", False, info(firmware="0.2.3\n")),
        ("address with a line feed at the end", False, info(ip="192.168.0.181\n")),
        ("node id with a line feed at the end", False, info(node_id="north-1\n")),
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
        ("an inverter whose dialect cannot ask for its warnings", True, inverter(warnings_known=False)),
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
        ("warnings_known that is not a boolean", False, inverter(warnings_known="no")),
        ("warning that is not a name", False, inverter(warnings=["Line fail"])),
        ("thirty-three warnings", False, inverter(warnings=["w%d" % i for i in range(33)])),
        ("unknown field", False, inverter(model="Axpert King")),
        ("the serial number the unit says", True, inverter(serial="92931903102538")),
        ("a serial number with a space", False, inverter(serial="9293 1903")),
        ("a serial number that is too short", False, inverter(serial="1234567")),
        ("a serial number that is a number", False, inverter(serial=92931903102538)),
        ("the firmware the unit says", True, inverter(firmware="00041.54")),
        ("a firmware with a space", False, inverter(firmware="00041 54")),
        ("an empty firmware", False, inverter(firmware="")),
        ("the energy the panels have made in all", True, inverter(pv_energy_total_wh=1234567)),
        ("a negative total energy", False, inverter(pv_energy_total_wh=-1)),
        ("a total energy as text", False, inverter(pv_energy_total_wh="12345")),
        ("the ratings of a 5 kVA unit", True, inverter(ratings={"grid_rating_v": 230.0, "out_rating_v": 230.0, "out_rating_hz": 50.0, "out_rating_va": 5000, "out_rating_w": 5000, "battery_rating_v": 48.0, "battery_recharge_v": 46.0, "battery_under_v": 42.0, "battery_bulk_v": 56.4, "battery_float_v": 54.0, "max_charge_a": 60, "max_ac_charge_a": 60, "battery_type": "agm", "input_range": "appliance", "output_priority": "solar_first", "charger_priority": "solar_and_utility"})),
        ("ratings with only what the unit said", True, inverter(ratings={"out_rating_va": 3000})),
        ("empty ratings", True, inverter(ratings={})),
        ("a battery type the contract does not know", False, inverter(ratings={"battery_type": "gel"})),
        ("an output priority the contract does not know", False, inverter(ratings={"output_priority": "grid"})),
        ("a charger priority the contract does not know", False, inverter(ratings={"charger_priority": "none"})),
        ("an input range the contract does not know", False, inverter(ratings={"input_range": "wide"})),
        ("a rated voltage above the limit", False, inverter(ratings={"battery_rating_v": 601})),
        ("a negative rated power", False, inverter(ratings={"out_rating_w": -1})),
        ("an unknown field in the ratings", False, inverter(ratings={"fuel": 1})),
        ("ratings that are not an object", False, inverter(ratings=[5000])),
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
        ("the bus voltage", True, inverter(bus_v=381.5)),
        ("a bus voltage above 1500", False, inverter(bus_v=1501)),
        ("a negative bus voltage", False, inverter(bus_v=-1)),
        ("not an object", False, [1, 2]),
    ],
    "solar_battery": [
        ("a stack of two modules, one not there", True, battery()),
        ("what a battery management system adds", True, battery(power_w=-129.2, balancing=3, protecting=False, charge_mos=1, discharge_mos=1)),
        ("a protection active", True, battery(protecting=True, charge_mos=5, discharge_mos=1, balancing=0)),
        ("power as a string", False, battery(power_w="12")),
        ("balancing a fractional number of cells", False, battery(balancing=2.5)),
        ("balancing a negative number of cells", False, battery(balancing=-1)),
        ("a mosfet code above 255", False, battery(charge_mos=256)),
        ("protecting as a number", False, battery(protecting=1)),
        ("charging", True, battery(state="charging", current_a=12.4)),
        ("idle", True, battery(state="idle", current_a=0.1)),
        ("state of charge left out", True, without(battery(), "soc_percent")),
        ("no module present", True, {"kind": "battery", "node_id": "solar-1", "device": "us3000-2", "timestamp_ms": 4000, "modules": 0, "stack": []}),
        ("sixteen modules, the limit", True, battery(modules=16, stack=[{"n": i + 1, "present": True} for i in range(16)])),
        ("an alarm", True, battery(alarm=True)),
        ("a module with its fifteen cells and temperatures", True, battery(stack=[{"n": 1, "present": True, "voltage_v": 49.872, "soc_percent": 88, "cells_v": [3.324 + 0.001 * i for i in range(15)], "temperatures_c": [22.0, 21.5, 22.5, 23.0, 21.0]}])),
        ("a module with the counters of its history", True, battery(stack=[{"n": 1, "present": True, "counters": {"bat_ov_times": 755, "bat_hv_times": 0, "coc_times": 1, "data_items": 2411, "dsg_cap": 149287073}}])),
        ("a module with no counters", True, battery(stack=[{"n": 1, "present": True, "counters": {}}])),
        ("a counter name in capitals", False, battery(stack=[{"n": 1, "present": True, "counters": {"Bat_OV": 1}}])),
        ("a counter name with a space", False, battery(stack=[{"n": 1, "present": True, "counters": {"bat ov": 1}}])),
        ("a negative counter", False, battery(stack=[{"n": 1, "present": True, "counters": {"bat_ov_times": -1}}])),
        ("a counter with a fraction", False, battery(stack=[{"n": 1, "present": True, "counters": {"bat_ov_times": 1.5}}])),
        ("a counter as a string", False, battery(stack=[{"n": 1, "present": True, "counters": {"bat_ov_times": "5"}}])),
        ("a counter above the limit", False, battery(stack=[{"n": 1, "present": True, "counters": {"bat_ov_times": 10000000000}}])),
        ("counters that are a list", False, battery(stack=[{"n": 1, "present": True, "counters": [1, 2]}])),
        ("a module with its model and limits", True, battery(stack=[{"n": 1, "present": True, "model": "US2000", "cell_count": 15, "max_charge_a": 53.0, "max_discharge_a": 55.0, "console_baud": 19200, "board_version": "V10R04", "main_soft_version": "B68.2.0.0", "soft_version": "V2.6"}])),
        ("a software version that is too long", False, battery(stack=[{"n": 1, "present": True, "soft_version": "x" * 25}])),
        ("an empty model", False, battery(stack=[{"n": 1, "present": True, "model": ""}])),
        ("a model that is too long", False, battery(stack=[{"n": 1, "present": True, "model": "x" * 25}])),
        ("a negative current limit", False, battery(stack=[{"n": 1, "present": True, "max_charge_a": -1}])),
        ("the health of the cells", True, battery(stack=[{"n": 1, "present": True, "soh_counts": [0] * 6 + [13] + [0] * 8, "soh_abnormal": [6]}])),
        ("a health count that is negative", False, battery(stack=[{"n": 1, "present": True, "soh_counts": [-1], "soh_abnormal": []}])),
        ("a cell index above the limit", False, battery(stack=[{"n": 1, "present": True, "soh_counts": [0], "soh_abnormal": [32]}])),
        ("the newest entry of the event log", True, battery(stack=[{"n": 1, "present": True, "last_event": {"index": 754, "time": "25-03-09 19:01:42", "voltage_v": 51.753, "current_a": 0, "temperature_c": 36, "percent": 52, "base_state": "Charge", "voltage_state": "OV", "power_events": "0x2 PHV", "battery_events": "0x4 BVNOR", "system_fault": "0x0"}}])),
        ("an event with only its index and time", True, battery(stack=[{"n": 1, "present": True, "last_event": {"index": 1, "time": "17-05-13 20:52:58"}}])),
        ("an event with no time", False, battery(stack=[{"n": 1, "present": True, "last_event": {"index": 1}}])),
        ("an event with a field of its own", False, battery(stack=[{"n": 1, "present": True, "last_event": {"index": 1, "time": "17-05-13 20:52:58", "decoded": "overvoltage"}}])),
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
        ("a power that the node only estimated", True, channel(power_estimated=True)),
        ("power_estimated that is not a boolean", False, channel(power_estimated="yes")),
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
    "solar_battery_command": [
        ("arm an output", True, bat_command()),
        ("execute with its token", True, bat_execute()),
        ("cancel", True, bat_without(bat_command(action="cancel"), "op", "params", "serial")),
        ("a piece of an image", True, bat_stage()),
        ("a piece of 344 characters", True, bat_stage(data="A" * 344)),
        ("arm the clock", True, bat_command(op="set_clock", params={})),
        ("arm the clock without params", True, bat_without(bat_command(op="set_clock"), "params")),
        ("a battery with no serial yet", True, bat_command(op="set_clock", params={}, serial="NOSERIAL")),
        ("write the barcode", True, bat_command(op="write_barcode", params={"serial": "H221014C32213244"})),
        ("set the module voltages", True, bat_command(op="limits_set", params={"group": "module_voltage", "values": dict(MODULE_VOLTAGE)})),
        ("set the temperatures", True, bat_command(op="limits_set", params={"group": "temperature", "values": dict(TEMPERATURE)})),
        ("enable two protections", True, bat_command(op="protections_set", params={"items": {"bov": "en", "coc": "en"}})),
        ("disable a protection, risk accepted", True, bat_command(op="protections_set", params={"items": {"bov": "dis"}, "accept_risk": True})),
        ("clear the event records", True, bat_command(op="clear_data", params={"which": "event"})),
        ("send a firmware image", True, bat_command(op="firmware_update", params={"image_size": 200000, "image_crc32": 305419896, "image_version": "2.4"})),
        ("send a firmware image and erase the memory", True, bat_command(op="firmware_update", params={"image_size": 200000, "image_crc32": 305419896, "image_version": "2.4", "clear_eeprom": True})),
        ("an expert line that only reads", True, bat_command(op="expert_command", params={"line": "pwr"})),
        ("an action outside the list", False, bat_command(action="run")),
        ("an operation outside the list", False, bat_command(op="format")),
        ("a free command as an operation", False, bat_command(op="ctrl cfet on")),
        ("port 0", False, bat_command(port=0)),
        ("port 11", False, bat_command(port=11)),
        ("port as a string", False, bat_command(port="2")),
        ("a command id of seven characters", False, bat_command(command_id="b0b0b0b")),
        ("a token with capitals", False, dict(bat_execute(), token="0123456789ABCDEF0123456789ABCDEF")),
        ("a token of 31 characters", False, dict(bat_execute(), token="0123456789abcdef0123456789abcde")),
        ("a serial with a space", False, bat_command(serial="PPTBH0220 409223")),
        ("a serial of seven characters", False, bat_command(serial="PPTBH02")),
        ("a node id with a space", False, bat_command(node_id="my node")),
        ("negative timestamp", False, bat_command(timestamp_ms=-1)),
        ("the kind of a result", False, bat_command(kind="solar_battery_result")),
        ("an unknown field", False, bat_command(password="x")),
        ("the service password as a field", False, bat_command(service_password="x")),
        ("params that are a list", False, bat_command(params=[1])),
        ("a piece with a data of 345 characters", False, bat_stage(data="A" * 345)),
        ("a piece with data that is not base64", False, bat_stage(data="@@@@")),
        ("a piece below the smallest image", False, bat_stage(size=100)),
        ("a piece above the largest image", False, bat_stage(size=524289)),
        ("a piece with an index past the end", False, bat_stage(index=2048)),
        ("a piece with an unknown field", False, bat_stage(path="x")),
        ("an arm with no operation", False, bat_without(bat_command(), "op"), True),
        ("an arm with no serial", False, bat_without(bat_command(), "serial"), True),
        ("an arm that carries a token", False, bat_command(token="0123456789abcdef0123456789abcdef"), True),
        ("an execute with no token", False, bat_without(bat_execute(), "token"), True),
        ("an execute with no serial", False, bat_without(bat_execute(), "serial"), True),
        ("a cancel that carries an operation", False, bat_without(bat_command(action="cancel"), "params", "serial"), True),
        ("a stage with no piece", False, bat_without(bat_stage(), "stage"), True),
        ("a stage that also names an operation", False, dict(bat_stage(), op="set_clock"), True),
        ("a value the operation does not have", False, bat_command(op="set_clock", params={"hour": 3})),
        ("an output that does not exist", False, bat_command(params={"output": "mostest", "state": "on"})),
        ("a state that is not on or off", False, bat_command(params={"output": "cfet", "state": "toggle"})),
        ("an output without its state", False, bat_command(params={"output": "cfet"}), True),
        ("clear data of something else", False, bat_command(op="clear_data", params={"which": "all"})),
        ("a serial to write that is too short", False, bat_command(op="write_barcode", params={"serial": "SHORT"})),
        ("the module voltages with one missing", False, bat_command(op="limits_set", params={"group": "module_voltage", "values": {k: v for k, v in MODULE_VOLTAGE.items() if k != "pslp"}}), True),
        ("the module voltages with one too many", False, bat_command(op="limits_set", params={"group": "module_voltage", "values": dict(MODULE_VOLTAGE, extra=1)})),
        ("a module voltage above the range the maker's tool states", False, bat_command(op="limits_set", params={"group": "module_voltage", "values": dict(MODULE_VOLTAGE, pov=65001)}), True),
        ("a module voltage below that range", False, bat_command(op="limits_set", params={"group": "module_voltage", "values": dict(MODULE_VOLTAGE, pslp=19999)}), True),
        ("an over-voltage below the high alarm", False, bat_command(op="limits_set", params={"group": "module_voltage", "values": dict(MODULE_VOLTAGE, pov=50000)}), True),
        ("an under-voltage above the low alarm", False, bat_command(op="limits_set", params={"group": "module_voltage", "values": dict(MODULE_VOLTAGE, puv=50000)}), True),
        ("a limit that is a fraction", False, bat_command(op="limits_set", params={"group": "module_voltage", "values": dict(MODULE_VOLTAGE, pov=58000.5)})),
        ("a limit group that does not exist", False, bat_command(op="limits_set", params={"group": "current", "values": {}})),
        ("a temperature above the range", False, bat_command(op="limits_set", params={"group": "temperature", "values": dict(TEMPERATURE, cot=100001)})),
        ("a temperature below the range", False, bat_command(op="limits_set", params={"group": "temperature", "values": dict(TEMPERATURE, cut=-40001)})),
        ("a protection that does not exist", False, bat_command(op="protections_set", params={"items": {"nope": "en"}})),
        ("a protection set to something else", False, bat_command(op="protections_set", params={"items": {"bov": "off"}})),
        ("a protection switched off without the risk accepted", False, bat_command(op="protections_set", params={"items": {"bov": "dis"}}), True),
        ("no protection at all", False, bat_command(op="protections_set", params={"items": {}}), True),
        ("a firmware image below the smallest", False, bat_command(op="firmware_update", params={"image_size": 1000, "image_crc32": 1, "image_version": "2.4"})),
        ("a firmware image without its CRC", False, bat_command(op="firmware_update", params={"image_size": 200000, "image_version": "2.4"}), True),
        ("a firmware image with a CRC above 32 bits", False, bat_command(op="firmware_update", params={"image_size": 200000, "image_crc32": 4294967296, "image_version": "2.4"})),
        ("an expert line with a blocked word", False, bat_command(op="expert_command", params={"line": "tbar H221014C32213244"}), True),
        ("an expert line that starts the update", False, bat_command(op="expert_command", params={"line": "updata"}), True),
        ("an expert line that erases the memory", False, bat_command(op="expert_command", params={"line": "eepe 0"}), True),
        ("an expert line of two commands", False, bat_command(op="expert_command", params={"line": "pwr;shut"}), True),
        ("an expert line of 49 characters", False, bat_command(op="expert_command", params={"line": "a" * 49})),
        ("an expert line with the blocked word later", False, bat_command(op="expert_command", params={"line": "help eepw"}), True),
    ],
    "solar_battery_result": [
        ("an arm, accepted, with its token", True, bat_result()),
        ("an execute, started", True, bat_plain(action="execute", stage="started")),
        ("progress", True, bat_plain(action="execute", stage="progress", outcome="running", steps_done=3, steps_total=9)),
        ("a firmware transfer in progress", True, bat_plain(action="execute", stage="progress", outcome="running", steps_done=1, steps_total=8, packets_sent=40, packets_total=196)),
        ("a cancel, accepted", True, bat_without(bat_plain(action="cancel", stage="cancel_requested"), "op")),
        ("a cancel, refused", True, bat_without(bat_plain(action="cancel", stage="rejected", accepted=False, refusal="not_cancellable"), "op")),
        ("an operation that worked", True, bat_final()),
        ("an operation that failed on its read-back", True, bat_final(outcome="failed", code="verify:clock_differs:25-03-09")),
        ("a sequence that stopped midway", True, bat_final(outcome="partial", code="step_failed:barcode", steps_done=4, steps_total=9, writes_done=3)),
        ("a battery that did not answer", True, bat_final(outcome="retry", code="timeout", writes_done=0)),
        ("a transfer that was cut", True, bat_final(outcome="partial", code="firmware:receiver_cancelled", packets_sent=12, packets_total=196)),
        ("a final answer that was shortened", True, bat_final(truncated=True)),
        ("a piece kept", True, bat_without(bat_plain(action="stage", stage="staged", received=256), "op")),
        ("an arm refused: serial does not match", True, bat_plain(accepted=False, stage="rejected", refusal="serial_mismatch")),
        ("an arm refused: not idle", True, bat_plain(accepted=False, stage="rejected", refusal="not_idle")),
        ("an arm refused: the chip cannot be told", True, bat_plain(accepted=False, stage="rejected", refusal="chip_unknown")),
        ("an execute refused: wrong token", True, bat_plain(action="execute", accepted=False, stage="rejected", refusal="bad_token")),
        ("everything refused: the node's setting is off", True, bat_plain(accepted=False, stage="rejected", refusal="disabled")),
        ("a refusal outside the list", False, bat_plain(accepted=False, stage="rejected", refusal="welded")),
        ("a stage outside the list", False, bat_result(stage="done")),
        ("an outcome outside the list", False, bat_final(outcome="mostly")),
        ("a risk outside the list", False, bat_result(risk="none")),
        ("no stage", False, bat_without(bat_result(), "stage")),
        ("no refusal", False, bat_without(bat_result(), "refusal")),
        ("no accepted", False, bat_without(bat_result(), "accepted")),
        ("accepted as a string", False, bat_result(accepted="true")),
        ("a token with capitals", False, bat_result(token="0123456789ABCDEF0123456789ABCDEF")),
        ("a node id with a space", False, bat_result(node_id="my node")),
        ("the kind of a command", False, bat_result(kind="solar_battery_command")),
        ("an unknown field", False, bat_result(password="x")),
        ("the service password as a field", False, bat_final(service_password="x")),
        ("an unknown field in the battery", False, bat_result(battery=dict(BATTERY, password="x"))),
        ("a battery without its serial", False, bat_result(battery={k: v for k, v in BATTERY.items() if k != "serial"})),
        ("a transcript above the limit", False, bat_final(transcript="t" * 8001)),
        ("more steps than the limit", False, bat_final(steps_total=201, steps_done=201)),
        ("accepted with a refusal", False, bat_result(refusal="busy"), True),
        ("refused with refusal none", False, bat_plain(accepted=False, stage="rejected"), True),
        ("rejected but accepted", False, bat_plain(stage="rejected"), True),
        ("a token in a final answer", False, bat_final(token="0123456789abcdef0123456789abcdef"), True),
        ("an armed answer without a token", False, bat_without(bat_result(), "token"), True),
        ("an armed answer without the operation", False, bat_without(bat_result(), "canonical"), True),
        ("an armed answer without the battery", False, bat_without(bat_result(), "battery"), True),
        ("a final answer without how it ended", False, bat_without(bat_final(), "outcome"), True),
        ("a final answer that is still running", False, bat_final(outcome="running"), True),
        ("progress that says ok", False, bat_plain(action="execute", stage="progress", outcome="ok"), True),
        ("an outcome in an armed answer", False, bat_result(outcome="ok"), True),
        ("a staged answer without the bytes", False, bat_without(bat_plain(action="stage", stage="staged"), "op"), True),
        ("more steps done than steps", False, bat_final(steps_done=10, steps_total=9), True),
    ],
    "alarm": [
        ("an armed alarm", True, alarm()),
        ("a disarmed panel", True, alarm(phase="disarmed", mode="disarmed", events=[])),
        ("an exit delay in stay mode", True, alarm(phase="exit_delay", mode="stay")),
        ("an alarm with the siren sounding", True, alarm(phase="alarm", siren=True, zones=[{"id": "window", "kind": "instant", "state": "triggered", "bypassed": False}],
                                                       open_zones=["window"], events=[{"ago_s": 3, "kind": "alarm", "zone": "window"}])),
        ("an alarm whose siren was silenced with the PIN", True, alarm(phase="alarm", mode="away", siren=False, events=[{"ago_s": 9, "kind": "alarm", "zone": "window"}, {"ago_s": 2, "kind": "siren_silenced"}])),
        ("a locked-out panel", True, alarm(locked_out=True, events=[{"ago_s": 1, "kind": "locked_out"}])),
        ("a node that takes no commands", True, alarm(commands_enabled=False)),
        ("a zone that is bypassed", True, alarm(zones=[{"id": "window", "kind": "instant", "state": "triggered", "bypassed": True}], open_zones=[])),
        ("a tamper", True, zone(state="tamper")),
        ("a zone that cannot be read", True, zone(state="trouble")),
        ("a zone state that is not one of the four", False, zone(state="broken")),
        ("an always zone", True, zone(kind="always")),
        ("an interior zone", True, zone(kind="interior")),
        ("no zones at all", True, alarm(zones=[], open_zones=[], events=[])),
        ("ten events, the limit", True, alarm(events=[{"ago_s": i, "kind": "armed"} for i in range(10)])),
        ("sixteen zones, the limit", True, alarm(zones=[{"id": f"z{i}", "kind": "instant", "state": "normal", "bypassed": False} for i in range(16)], open_zones=[])),
        ("eleven events", False, alarm(events=[{"ago_s": i, "kind": "armed"} for i in range(11)])),
        ("seventeen zones", False, alarm(zones=[{"id": f"z{i}", "kind": "instant", "state": "normal", "bypassed": False} for i in range(17)], open_zones=[])),
        ("a phase outside the list", False, alarm(phase="sleeping")),
        ("a mode outside the list", False, alarm(mode="night")),
        ("a zone kind outside the list", False, zone(kind="glass")),
        ("a zone state outside the list", False, zone(state="open")),
        ("an event kind outside the list", False, alarm(events=[{"ago_s": 1, "kind": "reboot"}])),
        ("an event told in the future", False, alarm(events=[{"ago_s": -1, "kind": "armed"}])),
        ("a zone id with a space", False, zone(id="front door")),
        ("an empty zone name", False, zone(name="")),
        ("a zone without its bypass", False, alarm(zones=[{"id": "window", "kind": "instant", "state": "normal"}])),
        ("no events", False, {k: v for k, v in alarm().items() if k != "events"}),
        ("no open zones", False, {k: v for k, v in alarm().items() if k != "open_zones"}),
        ("a siren as a string", False, alarm(siren="true")),
        ("a node id with a space", False, alarm(node_id="my node")),
        ("negative timestamp", False, alarm(timestamp_ms=-1)),
        ("the kind of a command", False, alarm(kind="alarm_command")),
        ("an unknown field", False, alarm(pin="1234")),
        ("a zone id twice", False, alarm(zones=[{"id": "window", "kind": "instant", "state": "normal", "bypassed": False}, {"id": "window", "kind": "entry", "state": "normal", "bypassed": False}]), True),
        ("an open zone that is not a zone", False, alarm(open_zones=["garage"]), True),
        ("an open zone named twice", False, alarm(zones=[{"id": "window", "kind": "instant", "state": "triggered", "bypassed": False}], open_zones=["window", "window"]), True),
        ("disarmed with a mode", False, alarm(phase="disarmed", mode="away"), True),
        ("armed with no mode", False, alarm(phase="armed", mode="disarmed"), True),
        ("an exit delay with no mode", False, alarm(phase="exit_delay", mode="disarmed"), True),
        ("an alarm while disarmed (smoke, panic or tamper)", True, alarm(phase="alarm", mode="disarmed", siren=True)),
        ("an alarm while armed", True, alarm(phase="alarm", mode="away", siren=True)),
        ("a node that understands arming profiles", True, alarm(arm_profiles=True)),
        ("armed with a profile", True, alarm(mode="stay", arm_profiles=True, profile="night")),
        ("a profile id with capitals", False, alarm(profile="Night")),
        ("a profile id of seventeen characters", False, alarm(profile="a" * 17)),
        ("arm_profiles as a string", False, alarm(arm_profiles="yes")),
        ("a profile on a panel that is not armed", False, alarm(phase="disarmed", mode="disarmed", profile="night"), True),
        ("a siren outside the alarm phase", False, alarm(siren=True), True),
        ("an event about a zone that is not there", False, alarm(events=[{"ago_s": 1, "kind": "alarm", "zone": "garage"}]), True),
    ],
    "alarm_command": [
        ("arm in away", True, alarm_command()),
        ("arm in stay", True, alarm_command(mode="stay")),
        ("arm and force", True, alarm_command(force=True)),
        ("arm without forcing, said so", True, alarm_command(force=False)),
        ("disarm", True, alarm_command(action="disarm", mode=None) if False else {k: v for k, v in alarm_command(action="disarm").items() if k != "mode"}),
        ("an arm with no mode", False, {k: v for k, v in alarm_command().items() if k != "mode"}, True),
        ("a disarm that carries a mode", False, alarm_command(action="disarm"), True),
        ("a disarm that forces", False, {k: v for k, v in alarm_command(action="disarm", force=True).items() if k != "mode"}, True),
        ("a mode outside the list", False, alarm_command(mode="night")),
        ("silence the siren", True, {k: v for k, v in alarm_command(action="silence").items() if k != "mode"}),
        ("a silence that carries a mode", False, alarm_command(action="silence"), True),
        ("a silence that forces", False, {k: v for k, v in alarm_command(action="silence", force=True).items() if k != "mode"}, True),
        ("an action outside the list", False, alarm_command(action="mute")),
        ("uppercase action", False, alarm_command(action="ARM")),
        ("a PIN in the command", False, alarm_command(pin="1234")),
        ("a command id of fifteen digits", False, alarm_command(command_id="c0ffee012345678")),
        ("a command id with capitals", False, alarm_command(command_id="C0FFEE0123456789")),
        ("a command id that is not hexadecimal", False, alarm_command(command_id="c0ffeezzzzzzzzzz")),
        ("no command id", False, {k: v for k, v in alarm_command().items() if k != "command_id"}),
        ("no action", False, {k: v for k, v in alarm_command().items() if k != "action"}),
        ("force as a string", False, alarm_command(force="yes")),
        ("a node id with a space", False, alarm_command(node_id="my node")),
        ("negative timestamp", False, alarm_command(timestamp_ms=-1)),
        ("the kind of a state message", False, alarm_command(kind="alarm")),
        ("a zone to bypass", False, alarm_command(zone="window")),
        ("arm in stay with a profile", True, alarm_profile_command()),
        ("a profile with the base only", True, alarm_command(mode="away", profile={"id": "away", "name": "Away", "base": "away"})),
        ("a profile with every field", True, alarm_profile_command(profile=profile(exit_delay_s=0, entry_delay_s=300, siren=False, notify="normal"))),
        ("a profile with sixteen zones", True, alarm_profile_command(profile=profile(zones=[{"id": f"z{i}", "armed": True} for i in range(16)]))),
        ("a profile with no zones", True, alarm_profile_command(profile=profile(zones=[]))),
        ("a forced arm with a profile", True, alarm_profile_command(force=True)),
        ("a profile with seventeen zones", False, alarm_profile_command(profile=profile(zones=[{"id": f"z{i}", "armed": True} for i in range(17)]))),
        ("a profile without a name", False, alarm_profile_command(profile={k: v for k, v in profile().items() if k != "name"})),
        ("a profile without a base", False, alarm_profile_command(profile={k: v for k, v in profile().items() if k != "base"})),
        ("a profile with an empty name", False, alarm_profile_command(profile=profile(name=""))),
        ("a profile name of thirty-three characters", False, alarm_profile_command(profile=profile(name="n" * 33))),
        ("a base outside the list", False, alarm_profile_command(profile=profile(base="night"))),
        ("an entry delay of 301 seconds", False, alarm_profile_command(profile=profile(entry_delay_s=301))),
        ("a negative exit delay", False, alarm_profile_command(profile=profile(exit_delay_s=-1))),
        ("a siren as a string", False, alarm_profile_command(profile=profile(siren="off"))),
        ("a notify level outside the list", False, alarm_profile_command(profile=profile(notify="silent"))),
        ("a zone delay outside the list", False, alarm_profile_command(profile=profile(zones=[{"id": "garage", "delay": "later"}]))),
        ("a zone override with no zone", False, alarm_profile_command(profile=profile(zones=[{"armed": True}]))),
        ("an unknown field in a profile", False, alarm_profile_command(profile=profile(pin="1234"))),
        ("an unknown field in a zone override", False, alarm_profile_command(profile=profile(zones=[{"id": "garage", "armed": True, "name": "x"}]))),
        ("a profile whose base is not the mode", False, alarm_command(mode="away", profile=profile()), True),
        ("a profile on a disarm", False, {k: v for k, v in alarm_profile_command(action="disarm").items() if k != "mode"}, True),
        ("a zone named twice in a profile", False, alarm_profile_command(profile=profile(zones=[{"id": "garage", "armed": False}, {"id": "garage", "armed": True}])), True),
        ("a zone left out that has a delay", False, alarm_profile_command(profile=profile(zones=[{"id": "garage", "armed": False, "delay": "entry"}])), True),
    ],
    "alarm_result": [
        ("an arm, accepted", True, alarm_result()),
        ("a disarm, accepted", True, alarm_result(action="disarm", phase="disarmed")),
        ("an arm refused: a zone is open", True, alarm_result(accepted=False, refusal="zones_open", phase="disarmed")),
        ("an arm refused: already armed", True, alarm_result(accepted=False, refusal="not_disarmed", phase="armed")),
        ("a disarm refused: not armed", True, alarm_result(action="disarm", accepted=False, refusal="not_armed", phase="disarmed")),
        ("a disarm refused: wrong PIN", True, alarm_result(action="disarm", accepted=False, refusal="bad_pin", phase="armed")),
        ("a silence, accepted", True, alarm_result(action="silence", phase="alarm")),
        ("a silence refused: wrong PIN", True, alarm_result(action="silence", accepted=False, refusal="bad_pin", phase="alarm")),
        ("a disarm refused: locked out", True, alarm_result(action="disarm", accepted=False, refusal="locked_out", phase="alarm")),
        ("accepted with a refusal", False, alarm_result(refusal="zones_open"), True),
        ("refused with refusal none", False, alarm_result(accepted=False), True),
        ("a refusal outside the list", False, alarm_result(accepted=False, refusal="welded")),
        ("an action outside the list", False, alarm_result(action="mute")),
        ("a phase outside the list", False, alarm_result(phase="sleeping")),
        ("accepted as a string", False, alarm_result(accepted="true")),
        ("no phase", False, {k: v for k, v in alarm_result().items() if k != "phase"}),
        ("no refusal", False, {k: v for k, v in alarm_result().items() if k != "refusal"}),
        ("no accepted", False, {k: v for k, v in alarm_result().items() if k != "accepted"}),
        ("no command id", False, {k: v for k, v in alarm_result().items() if k != "command_id"}),
        ("a command id of fifteen digits", False, alarm_result(command_id="c0ffee012345678")),
        ("the kind of a command", False, alarm_result(kind="alarm_command")),
        ("a node id with a space", False, alarm_result(node_id="my node")),
        ("an unknown field", False, alarm_result(detail="x")),
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
        ("the result of a look at a web administration", True, network(results=[{"id": "c1a2b5", "type": "inspect", "ok": True, "finished_ms": 5, "device_id": "14:2e:5e:86:d9:62", "output": "http://192.168.0.1:80/ -> HTTP 200\nlogin: accepted (Digest)\ntitle: Home Router\nmodel: HR-5000"}])),
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
        ("a network that is not a private range", False, network(interface=dict(network()["interface"], cidr="8.8.8.0/24")), True),
        ("a network wider than a private range", False, network(interface=dict(network()["interface"], cidr="0.0.0.0/0")), True),
        ("a private range of 172.16", True, network(interface=dict(network()["interface"], cidr="172.16.4.0/24"))),
    ],
    "alarm_zone_feed": [
        ("a closed door", True, zone_feed(state="normal")),
        ("a triggered sensor with a low battery", True, zone_feed(battery_low=True)),
        ("a tampered sensor", True, zone_feed(state="tamper")),
        ("a zone name of 32 characters", True, zone_feed(zone="z" * 32)),
        ("a zone name of 33 characters", False, zone_feed(zone="z" * 33)),
        ("an uppercase zone", False, zone_feed(zone="Front")),
        ("a line feed at the end of the zone", False, zone_feed(zone="front\n")),
        ("a state that is not one", False, zone_feed(state="open")),
        ("a battery that is not a flag", False, zone_feed(battery_low="no")),
        ("the node repeated inside", False, zone_feed(node_id="alarm-1")),
        ("a missing battery flag", False, without(zone_feed(), "battery_low")),
        ("not an object", False, [1]),
    ],
    "device_state": [
        ("a relay that is on", True, {"on": True}),
        ("a relay that is off", True, {"on": False}),
        ("the word instead of the flag", False, {"on": "ON"}),
        ("a number instead of the flag", False, {"on": 1}),
        ("an unknown field", False, {"on": True, "level": 3}),
        ("no field", False, {}),
        ("not an object", False, [True]),
    ],
    "server_alert": [
        ("a device alarm", True, server_alert()),
        ("a node that went high", True, {"service": "armor-server", "event": "alert.raised", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "node_id": "north-1", "targets": 2}),
        ("a camera that went offline", True, {"service": "armor-server", "event": "camera.offline", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "camera_id": "cam-01"}),
        ("a test", True, {"service": "armor-server", "event": "alert.test", "at": "1970-01-01T00:00:00.000Z", "mode": "disarmed"}),
        ("a silent alarm", True, {"service": "armor-server", "event": "alarm.raised", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "alarm_id": "a2", "severity": "critical", "code": "duress_disarm", "alarm_node_id": "alarm-1", "silent": True}),
        ("a sign-in from outside the house", True, {"service": "armor-server", "event": "login.remote", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "login_user": "admin", "login_from": "203.0.113.9"}),
        ("a sign-in from outside that names no one", False, {"service": "armor-server", "event": "login.remote", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "login_from": "203.0.113.9"}, True),
        ("another service", False, server_alert(service="someone-else")),
        ("an event that does not exist", False, server_alert(event="alarm.imagined")),
        ("a mode that does not exist", False, server_alert(mode="armed-away")),
        ("a severity that does not exist", False, server_alert(severity="urgent")),
        ("silent set to false", False, server_alert(silent=False)),
        ("an unknown field", False, server_alert(extra=1)),
        ("a missing time", False, without(server_alert(), "at")),
        ("a node event that names no node", False, {"service": "armor-server", "event": "node.offline", "at": "1970-01-01T00:00:00.000Z", "mode": "armed"}, True),
        ("a camera event that names no camera", False, {"service": "armor-server", "event": "camera.offline", "at": "1970-01-01T00:00:00.000Z", "mode": "armed"}, True),
        ("an alarm that does not say which", False, {"service": "armor-server", "event": "alarm.raised", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "device_id": "smoke-1"}, True),
        ("a silent test", False, {"service": "armor-server", "event": "alert.test", "at": "1970-01-01T00:00:00.000Z", "mode": "armed", "silent": True}, True),
    ],
    "network_orders": [
        ("one order about a device", True, orders()),
        ("no order waiting", True, orders(commands=[])),
        ("a sweep", True, orders(commands=[{"id": "c1", "type": "scan_now"}])),
        ("an inspection with a sealed login", True, order(type="inspect", port=80, auth_sealed="A" * 64)),
        ("a wake-up with the MAC", True, order(type="wake", mac="14:2e:5e:86:d9:62")),
        ("four orders, the most at once", True, orders(commands=[{"id": f"c{i}", "type": "scan_now"} for i in range(4)])),
        ("five orders", False, orders(commands=[{"id": f"c{i}", "type": "scan_now"} for i in range(5)])),
        ("not accepted", False, orders(accepted=False)),
        ("an unknown order", False, order(type="format")),
        ("an address with a leading zero", False, order(ip="192.168.0.01")),
        ("a port of 0", False, order(type="http", port=0)),
        ("a sealed login in clear text", False, order(type="inspect", auth="admin:1234")),
        ("a sealed login that is too short", False, order(type="inspect", auth_sealed="AAAA")),
        ("an unknown field", False, orders(extra=True)),
        ("an order about a device that names none", False, orders(commands=[{"id": "c1", "type": "ping"}]), True),
        ("a sweep about a device", False, order(type="scan_now"), True),
        ("a wake-up without a MAC", False, order(type="wake"), True),
        ("a port on a ping", False, order(port=80), True),
        ("a sealed login on a ping", False, order(auth_sealed="A" * 64), True),
        ("an order twice", False, orders(commands=[{"id": "c1", "type": "scan_now"}, {"id": "c1", "type": "scan_now"}]), True),
    ],
    "node_health": [
        ("an alarm node on a cable", True, node_health()),
        ("a radar on Wi-Fi", True, wifi_health(family="radar", node_id="north-1", board="s3-wifi")),
        ("a solar node", True, node_health(family="solar", node_id="solar-1")),
        ("an electrical node", True, node_health(family="electrical", node_id="electrical-1")),
        ("a wall panel", True, wifi_health(family="hmi", node_id="hall-panel", board="lcd7box")),
        ("a four part firmware version", True, node_health(firmware="0.8.0.1")),
        ("the minimum a node must say", True, {k: v for k, v in node_health().items() if k not in ("board", "low_stack_tasks")}),
        ("a node that has logged an error", True, node_health(last_error="mqtt: the broker refused the identity")),
        ("a node that restarted after a crash", True, node_health(reset_reason="panic", uptime_s=12)),
        ("a node with no link", True, node_health(link="none", link_up=False)),
        ("a Wi-Fi link that is down", True, node_health(link="wifi", link_up=False)),
        ("a node that reconnected nine times", True, node_health(broker_reconnects=9)),
        ("the least heap equals the heap free", True, node_health(heap_min=142000)),
        ("a radar that tells its internal memory and its external RAM", True, wifi_health(family="radar", node_id="north-1", board="s3-wifi", heap_free=7900000, heap_min=7800000, heap_internal_free=72704, heap_internal_min=60112, heap_internal_largest=36864, psram_free=7700000)),
        ("a board with no external RAM that tells its internal memory", True, node_health(heap_internal_free=90112, heap_internal_min=71000, heap_internal_largest=65536)),
        ("the internal figures equal to what is free", True, node_health(heap_internal_free=50000, heap_internal_min=50000, heap_internal_largest=50000)),
        ("a reset reason outside the list", False, node_health(reset_reason="cosmic_ray")),
        ("a family outside the list", False, node_health(family="toaster")),
        ("the kind of another message", False, node_health(kind="health")),
        ("a firmware that is not a version", False, node_health(firmware="latest")),
        ("a firmware of five parts", False, node_health(firmware="0.8.0.1.2")),
        ("a negative uptime", False, node_health(uptime_s=-1)),
        ("an uptime as a string", False, node_health(uptime_s="1d")),
        ("a negative heap", False, node_health(heap_free=-1)),
        ("a link outside the list", False, node_health(link="lte")),
        ("a link flag as a number", False, node_health(link_up=1)),
        ("a signal stronger than zero", False, wifi_health(rssi_dbm=5)),
        ("a signal weaker than -120", False, wifi_health(rssi_dbm=-121)),
        ("an empty board", False, node_health(board="")),
        ("a board of thirty-three characters", False, node_health(board="b" * 33)),
        ("an empty error", False, node_health(last_error="")),
        ("an error of 97 characters", False, node_health(last_error="e" * 97)),
        ("sixty-five tasks short of stack", False, node_health(low_stack_tasks=65)),
        ("no firmware", False, {k: v for k, v in node_health().items() if k != "firmware"}),
        ("no reset reason", False, {k: v for k, v in node_health().items() if k != "reset_reason"}),
        ("no reconnect count", False, {k: v for k, v in node_health().items() if k != "broker_reconnects"}),
        ("a node id with a space", False, node_health(node_id="my node")),
        ("a negative timestamp", False, node_health(timestamp_ms=-1)),
        ("an unknown field", False, node_health(temp_c=41)),
        ("a command in a report", False, node_health(command="restart")),
        ("a negative internal memory", False, node_health(heap_internal_free=-1, heap_internal_min=0, heap_internal_largest=0)),
        ("a negative external RAM", False, node_health(psram_free=-1)),
        ("an internal memory as a string", False, node_health(heap_internal_free="72 KB", heap_internal_min=1, heap_internal_largest=1)),
        ("the least internal memory above what is free", False, node_health(heap_internal_free=50000, heap_internal_min=60000, heap_internal_largest=40000), True),
        ("a biggest block above what is free", False, node_health(heap_internal_free=50000, heap_internal_min=40000, heap_internal_largest=60000), True),
        ("the internal memory told in part", False, node_health(heap_internal_free=50000), True),
        ("the least heap above the heap free", False, node_health(heap_min=150000), True),
        ("a signal on a cable", False, node_health(rssi_dbm=-50), True),
        ("a signal on a Wi-Fi link that is down", False, node_health(link="wifi", link_up=False, rssi_dbm=-50), True),
        ("no link but the link is up", False, node_health(link="none", link_up=True), True),
    ],
    "arm_profile": [
        ("a night profile", True, profile()),
        ("the base only", True, {"id": "away", "name": "Away", "base": "away"}),
        ("a silent profile", True, profile(siren=False, notify="normal")),
        ("a zone switched on in stay", True, {"id": "home", "name": "Home", "base": "stay", "zones": [{"id": "hall", "armed": True}]}),
        ("a zone with a delay", True, profile(zones=[{"id": "back-door", "delay": "instant"}])),
        ("a zone with nothing to say", True, profile(zones=[{"id": "hall"}])),
        ("a custom id with an underscore and a dash", True, profile(id="custom_1-b")),
        ("an id of sixteen characters", True, profile(id="a" * 16)),
        ("an id of seventeen characters", False, profile(id="a" * 17)),
        ("an id starting with a dash", False, profile(id="-night")),
        ("an id with capitals", False, profile(id="Night")),
        ("a name of thirty-two characters", True, profile(name="n" * 32)),
        ("a name of thirty-three characters", False, profile(name="n" * 33)),
        ("no id", False, {k: v for k, v in profile().items() if k != "id"}),
        ("a base of disarmed", False, profile(base="disarmed")),
        ("a delay of 300 seconds", True, profile(entry_delay_s=300, exit_delay_s=300)),
        ("a delay of 301 seconds", False, profile(exit_delay_s=301)),
        ("a fractional delay", False, profile(entry_delay_s=1.5)),
        ("notify as a boolean", False, profile(notify=True)),
        ("an unknown field", False, profile(armed=True)),
        ("zones that are not a list", False, profile(zones={"id": "x"})),
        ("a zone named twice", False, profile(zones=[{"id": "x", "armed": True}, {"id": "x", "armed": False}]), True),
        ("a zone left out that has a delay", False, profile(zones=[{"id": "x", "armed": False, "delay": "instant"}]), True),
    ],
    "connection_event": [
        ("a sign-in to Studio", True, connection_event()),
        ("a sign-in with the second factor", True, connection_event(two_factor=True, origin="remote")),
        ("a sign-in the administrator sees with its address", True, connection_event(ip="192.168.0.20", agent="Mozilla/5.0")),
        ("a refused sign-in", True, connection_event(action="login_failed")),
        ("a wrong code of the second factor", True, connection_event(action="second_factor_failed")),
        ("an app seen for the first time", True, connection_event(action="first_seen", client_kind="android", app_version="0.6.6")),
        ("the panel of a node opened", True, connection_event(action="panel_opened", client_kind="node", subject="radar-1")),
        ("a client with no user", True, {k: v for k, v in connection_event(client_kind="voice").items() if k != "user"}),
        ("a session that expired", True, connection_event(action="session_expired")),
        ("an action outside the list", False, connection_event(action="hijacked")),
        ("a client kind outside the list", False, connection_event(client_kind="toaster")),
        ("a client id that is not a hash", False, connection_event(client_id="ana")),
        ("another type", False, connection_event(type="system")),
        ("a password in the event", False, connection_event(password="secret")),
        ("a token in the event", False, connection_event(token="abc")),
        ("a user of 61 characters", False, connection_event(user="u" * 61)),
        ("an application version with a space", False, connection_event(app_version="0.6 6")),
        ("an id of zero", False, connection_event(id=0)),
        ("no action", False, {k: v for k, v in connection_event().items() if k != "action"}),
        ("the second factor as a number", False, connection_event(two_factor=1)),
    ],
    "system_event": [
        ("a node that appeared", True, system_event()),
        ("a node that went away", True, system_event(action="disappeared")),
        ("a node whose firmware changed", True, system_event(action="firmware_changed", version="0.3.8", previous_version="0.3.7")),
        ("the broker lost", True, system_event(category="broker", action="disconnected", subject="mqtt")),
        ("a setting changed by somebody", True, system_event(category="settings", action="changed", subject="rules", by="ana")),
        ("a service restarted", True, system_event(category="service", action="restarted", subject="armor-server", by="ana")),
        ("an update installed", True, system_event(category="update", action="installed", subject="armor-server", version="0.7.2")),
        ("the alarm armed with a profile", True, system_event(category="alarm", action="arm_requested", subject="alarm-1", profile="night", by="ana")),
        ("a battery operation ordered", True, system_event(category="batteries", action="battery_requested", subject="solar-1:2", by="ana", outcome="allowed")),
        ("a battery operation that ended badly", True, system_event(category="batteries", action="battery_operation", subject="solar-1:2", by="ana", outcome="failed")),
        ("the siren silenced", True, system_event(category="alarm", action="silence_requested", subject="alarm-1")),
        ("a backup made", True, system_event(category="backup", action="backup_made")),
        ("a refused change", True, system_event(category="settings", action="changed", outcome="denied")),
        ("a category outside the list", False, system_event(category="weather")),
        ("an action outside the list", False, system_event(action="exploded")),
        ("a free text", False, system_event(detail="password=hunter2")),
        ("a value of the setting", False, system_event(value="1234")),
        ("a version that is not a version", False, system_event(version="latest")),
        ("a profile with capitals", False, system_event(profile="Night")),
        ("a subject of 81 characters", False, system_event(subject="s" * 81)),
        ("another type", False, system_event(type="connection")),
        ("no category", False, {k: v for k, v in system_event().items() if k != "category"}),
    ],
    "connection_client": [
        ("the Android app of a person", True, connection_client()),
        ("a Studio with its address, for an administrator", True, connection_client(kind="studio", ip="10.0.0.5", agent="Mozilla/5.0", origin="local")),
        ("a client that was refused once", True, connection_client(logins_failed=1, last_failure="2026-01-02T09:00:00.000Z")),
        ("the voice service with no user", True, {k: v for k, v in connection_client(kind="voice").items() if k not in ("user", "app_version")}),
        ("the panel of a node", True, connection_client(kind="node", label="radar-1")),
        ("a negative count of sessions", False, connection_client(active_sessions=-1)),
        ("a count as text", False, connection_client(logins_ok="3")),
        ("a kind outside the list", False, connection_client(kind="fridge")),
        ("an id that is not a hash", False, connection_client(id="123")),
        ("a cookie in the client", False, connection_client(cookie="abc")),
        ("no last seen", False, {k: v for k, v in connection_client().items() if k != "last_seen"}),
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

CHECK = "--check" in sys.argv[1:]
stale: list[str] = []
if not CHECK:
    ROOT.mkdir(exist_ok=True)
for kind, entries in cases.items():
    # A fourth item, True, marks a payload the schema accepts and the message-level rule refuses (a token where none belongs, a switch named twice).
    vectors = [{"name": name, "valid": valid, "payload": payload, **({"schema_valid": True} if extra else {})} for name, valid, payload, *extra in entries]
    schema_kind = {"solar_inverter": "inverter", "solar_battery": "battery"}.get(kind, kind)   # the solar files are named after their schema, and carry the payload's kind
    text = json.dumps({"kind": schema_kind, "vectors": vectors}, indent=1) + "\n"
    if CHECK:
        path = ROOT / f"{kind}.json"
        if not path.is_file() or path.read_text(encoding="utf-8").replace("\r\n", "\n") != text:
            stale.append(f"{kind}.json")
    else:
        (ROOT / f"{kind}.json").write_text(text, encoding="utf-8", newline="\n")
        print(kind, len(vectors), "vectors")
if CHECK:
    if stale:
        print("CONFORMANCE=FAIL these files are not what tools/make_conformance.py writes (run it): " + ", ".join(stale))
        sys.exit(1)
    print(f"CONFORMANCE=PASS {len(cases)} files are current")
