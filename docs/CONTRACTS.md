# A.R.M.O.R. contracts

The JSON Schemas in `src/armor_common/schemas/` are the **single source of truth**
for every message. Nothing else may add a rule the schema does not state, and
nothing may ignore one.

## Broker namespace

`armor/node/{node_id}/{kind}` where `kind` is `telemetry`, `health` or `command`.
Topic names are lower-case and part of the compatibility contract. A producer
keeps its `node_id` identical in the topic and in the JSON body; consumers reject
a mismatch.

| Kind | Direction | Schema |
|---|---|---|
| `telemetry` | node → server | `telemetry.schema.json`: node id, millisecond timestamp, ambient lux (0–200 000) and at most 15 tracks (5 per each of the 3 radar sensors). The limit stops an unbounded payload from exhausting a field node. |
| `health` | node → server | `health.schema.json`: node id, timestamp, `online` flag |
| `command` | server → node | `command.schema.json`: `calibrate`, `set_thresholds` (optional `sensitivity` 1–10) or `restart`. Commands are an allow-list: a subscriber rejects everything else before it reaches hardware control logic. |

All three use `additionalProperties: false`: an unknown field is an error, never
silently ignored.

## Keeping every implementation in step

1. **Python** (`armor_common`) interprets the schema files directly with a small
   validator that *refuses* a schema using a keyword it does not implement, so a
   constraint can never be quietly skipped.
2. **Conformance vectors** (`conformance/*.json`, 50 cases) list payloads that must
   be accepted and payloads that must be rejected. Every implementation runs them:
   `armor_common` in its own tests, ARMOR-SERVER in `tests/conformance.test.ts`. A
   disagreement fails a build; tightening a contract means adding a vector here.
3. **Generated types** (`generated/armor-contracts.ts`, `generated/ArmorContracts.kt`)
   come from the schemas with `python tools/generate_types.py`; `--check` fails when
   they are stale.

## HTTP

`openapi/armor-server-0.3.0.yaml` describes every route of ARMOR-SERVER, who may
call it and which schema its body follows. ARMOR-SERVER's tests fail when a
registered route is missing from it.

## Changing a contract

1. Edit the schema. 2. Add the accepted and rejected vectors. 3. Run
`python -m unittest discover -s tests` and `python tools/generate_types.py`.
4. Update every implementation until its conformance test passes. 5. Bump the
schema `$id` version when the change is not backwards compatible.
