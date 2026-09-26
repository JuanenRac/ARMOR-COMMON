# A.R.M.O.R. contracts

The JSON Schemas in `src/armor_common/schemas/` are the **single source of truth**
for every message. Nothing else may add a rule the schema does not state, and
nothing may ignore one.

## Broker namespace

The nodes that read solar inverters and batteries publish on their own topic family, `armor/solar/{node_id}/{device}/state`, with the message's own
`kind` (`inverter` or `battery`) inside the payload (see *Solar messages* below). The radar family is
`armor/node/{node_id}/{kind}` where `kind` is `telemetry`, `health`, `info` or `command`.
Topic names are lower-case and part of the compatibility contract. A producer
keeps its `node_id` identical in the topic and in the JSON body; consumers reject
a mismatch.

| Kind | Direction | Schema |
|---|---|---|
| `telemetry` | node → server | `telemetry.schema.json`: node id, millisecond timestamp, ambient lux (0–200 000) and at most 15 tracks (5 per each of the 3 radar sensors). The limit stops an unbounded payload from exhausting a field node. |
| `health` | node → server | `health.schema.json`: node id, timestamp, `online` flag |
| `info` | node → server | `info.schema.json`: node id, timestamp, the operator's name for the node, its firmware version, its IPv4 address and the port of its web panel. It lets a console offer a link to the panel; it is sent when the node connects and now and then. |
| `command` | server → node | `command.schema.json`: `calibrate`, `set_thresholds` (optional `sensitivity` 1–10) or `restart`. Commands are an allow-list: a subscriber rejects everything else before it reaches hardware control logic. |

All four use `additionalProperties: false`: an unknown field is an error, never
silently ignored.

## Solar messages

`armor/solar/{node_id}/{device}/state` (node → server), `device` being lowercase letters, digits, `-` and `_` (at most 32 characters, not starting with `-` or `_`). The
payload repeats `node_id` and `device`; a mismatch is refused. The payload's `kind` picks the schema:

| Kind | Schema |
|---|---|
| `inverter` | `solar_inverter.schema.json`: the mode, the grid and output figures, the battery side (voltage, signed current, percentage), the panels' voltage, current and power, the temperature, three flags and the names of the active warnings |
| `battery` | `solar_battery.schema.json`: how many modules are present (0 to 16) and, when there are, the state, voltage, current, temperature range, cell range, mean state of charge and alarm, and one entry per module (with, when the node reads them, the voltage of each cell and the module's temperature sensors). With no module present the message carries no other reading |

Both use `additionalProperties: false` and have no nulls: a reading a node does not know is left out.

## Keeping every implementation in step

1. **Python** (`armor_common`) interprets the schema files directly with a small
   validator that *refuses* a schema using a keyword it does not implement, so a
   constraint can never be quietly skipped.
2. **Conformance vectors** (`conformance/*.json`, 142 cases) list payloads that must
   be accepted and payloads that must be rejected. Every implementation runs them:
   `armor_common` in its own tests, ARMOR-SERVER in `tests/conformance.test.ts`. A
   disagreement fails a build; tightening a contract means adding a vector here.
3. **Generated types** (`generated/armor-contracts.ts`, `generated/ArmorContracts.kt`)
   come from the schemas with `python tools/generate_types.py`; `--check` fails when
   they are stale.

## HTTP

`openapi/armor-server-0.1.9.yaml` describes every route of ARMOR-SERVER, who may
call it and which schema its body follows. ARMOR-SERVER's tests fail when a
registered route is missing from it.

## Changing a contract

1. Edit the schema. 2. Add the accepted and rejected vectors. 3. Run
`python -m unittest discover -s tests` and `python tools/generate_types.py`.
4. Update every implementation until its conformance test passes. 5. Bump the
schema `$id` version when the change is not backwards compatible.
