# A.R.M.O.R. contracts

The JSON Schemas in `src/armor_common/schemas/` are the **single source of truth**
for every message. Nothing else may add a rule the schema does not state, and
nothing may ignore one.

## Broker namespace

The nodes that read solar inverters and batteries publish on their own topic family, `armor/solar/{node_id}/{device}/state`, with the message's own
`kind` (`inverter` or `battery`) inside the payload (see *Solar messages* below). The nodes that measure the house's electrical network publish `armor/electrical/{node_id}/state` (see *Electrical messages*); a node that has switches also reads `armor/electrical/{node_id}/command` and answers on `armor/electrical/{node_id}/result` (see *Switches*). The radar family is
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

An inverter message may also carry a second PV input (`pv2_v`, `pv2_a`, `pv2_w`; `pv_w` is then the sum of both) and, for a parallel system, `units` (up to ten entries) with the totals `total_out_w`, `total_out_va`, `total_load_percent` and `total_charging_a`; all of these are optional.

Both use `additionalProperties: false` and have no nulls: a reading a node does not know is left out.

## Electrical messages

`armor/electrical/{node_id}/state` (node → server), one message per node every few seconds, `kind` `electrical` (`electrical.schema.json`). It carries `node_id`, `timestamp_ms`, `switching_enabled` (whether the node's firmware may switch anything at all; false unless it was built and set up for it) and up to sixteen `channels`. A channel has an `id` (lowercase letters, digits, `-` and `_`, unique in the message), `domain` (`ac` or `dc`), optionally a `label`, and `voltage_v`, `current_a`, `power_w` (positive when it draws from the network, negative when it feeds it), `energy_kwh`, and for AC `frequency_hz` and `power_factor`; `state` (`closed`, `open`, `unknown`) is what a switch's auxiliary contact shows, never what was asked; `alarm` is the meter's own flag. The message carries states and never a command. `additionalProperties: false` and no nulls, as for the others. See ARMOR-ELECTRICAL's `docs/ELECTRICAL_MESSAGES.md`.

## Switches: the state, the command and the answer

A node that controls a **switch** (a source transfer: two contactors, A and B, onto one line, never both) says so in the ordinary state message and takes commands on its own topic. Every command is refused by default at three independent places: the node (its firmware has to be built and set up to switch, `switching_enabled`), the server (`ARMOR_ELECTRICAL_SWITCHING=1`) and the broker (its ACL has to allow the topic, `scripts/mqtt_identity.sh electrical-switching`). Nothing that switches has been built.

* **The state** (`electrical.schema.json`, an optional `switches` array of at most four, every `id` once): for each switch `id`, `kind` (`transfer`), optionally `label`, `source_a` and `source_b` (the ids of the channels that measure each source), `a_closed` and `b_closed` (the auxiliary contacts: what the node **sees**, never what was asked), `selected` (`none`, `a` or `b`: the source confirmed closed onto the line), `wanted` (where the controller is going), `closing` (a coil is energised and the contact has not confirmed), `armed` (the next request to close is accepted) and `fault` (`none`, `did_not_close`, `did_not_open`, `both_closed`, `disabled`; a latched fault opens everything until it is acknowledged with both contactors confirmed open).
* **The command** `armor/electrical/{node_id}/command` (server → node, `electrical_command.schema.json`, never retained, at most once): `node_id`, `timestamp_ms`, `command_id` (chosen by the server, 8 to 32 lowercase letters and digits), `switch` and one `action` from the allow-list `arm`, `close_a`, `close_b`, `open`, `acknowledge`. **Closing is two steps:** `arm` (the node answers with a one-time `token`), then `close_a` or `close_b` carrying that `token`; a token is present exactly on those two actions. The token is spent by the first close that presents it, and a wrong one also withdraws the arm, so an old message that turns up again finds nothing to match and moves nothing. `open` needs no token and is always accepted.
* **The answer** `armor/electrical/{node_id}/result` (node → server, `electrical_result.schema.json`, never retained): the `command_id` it answers, `switch`, `action`, `accepted` and `refusal` (`none` exactly when accepted; otherwise `disabled`, `fault`, `not_armed`, `not_confirmed_open`, `unknown_switch`, `bad_token` or `not_supported`); the answer to an accepted `arm` carries the `token`. **An accepted command is not a switch that closed:** only the state message says that.

The schema cannot say the rules that join two fields (a token on the closing actions only, the refusal that matches `accepted`, a switch named once); `validate_electrical_command`, `validate_electrical_result` and `validate_electrical_message` do, and the conformance vectors that only those rules refuse are marked `"schema_valid": true`. See ARMOR-ELECTRICAL's `docs/SWITCHING.md` and `docs/SAFETY.md`.

## Keeping every implementation in step

1. **Python** (`armor_common`) interprets the schema files directly with a small
   validator that *refuses* a schema using a keyword it does not implement, so a
   constraint can never be quietly skipped.
2. **Conformance vectors** (`conformance/*.json`, 266 cases) list payloads that must
   be accepted and payloads that must be rejected. Every implementation runs them:
   `armor_common` in its own tests, ARMOR-SERVER in `tests/conformance.test.ts`. A
   disagreement fails a build; tightening a contract means adding a vector here.
3. **Generated types** (`generated/armor-contracts.ts`, `generated/ArmorContracts.kt`)
   come from the schemas with `python tools/generate_types.py`; `--check` fails when
   they are stale.

## HTTP

`openapi/armor-server-0.2.0.yaml` describes every route of ARMOR-SERVER, who may
call it and which schema its body follows. ARMOR-SERVER's tests fail when a
registered route is missing from it.

## Changing a contract

1. Edit the schema. 2. Add the accepted and rejected vectors. 3. Run
`python -m unittest discover -s tests` and `python tools/generate_types.py`.
4. Update every implementation until its conformance test passes. 5. Bump the
schema `$id` version when the change is not backwards compatible.
