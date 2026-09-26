# Changelog

All notable changes to this project are documented here.

## [0.2.2] - The health of a battery

- **`health_percent`** (an integer from 0 to 100, optional) on the battery message and on each module of its stack: the capacity the battery has learned against its rated one. A node that cannot tell leaves it out. Five new conformance vectors (147 in all); the generated TypeScript and Kotlin types carry it.
- OpenAPI: `GET` and `PUT /api/v1/electrical` (the electrical design of the house, kept apart from the site design).

## [0.2.1] - The project tool runs the tests of both boards

- `armor_project_tool.py` also builds and runs the board-profile tests of ARMOR-RADAR (`test_board_wifi`) and ARMOR-SOLAR (`test_board_eth`). No change to the messages, the schemas or the vectors.

## [0.2.0] - Declaring solar equipment

- **OpenAPI 0.2.0:** `POST /api/v1/solar/devices` (declare an inverter or a battery stack: name, model, connection, gateway node), `DELETE /api/v1/solar/devices/{node}/{device}` and `POST /api/v1/solar/devices/{node}/{device}/example` (one made-up reading, marked as an example); `GET /api/v1/solar` also lists the declared devices that have not reported yet and the catalogue of models and connections. The file is renamed `armor-server-0.2.0.yaml`. No schema changed.
- `armor_project_tool.py` also tests ARMOR-SOLAR's node (settings, network plan, emulated UART, the exchange with stand-in equipment) and checks the messages its ports make against the contract. No change to the messages, the schemas or the vectors.

## [0.1.9] - The solar messages

- **Two new messages**, on their own topics `armor/solar/{node_id}/{device}/state`: `inverter` (a solar inverter of the Voltronic / MPP Solar family) and `battery` (a battery stack as Pylontech's console reports it, with each module's cell voltages and temperature sensors when the node reads them). Schemas, `validate_solar_message` and `parse_solar_topic` in Python, **74 new conformance vectors** (142 in all), TypeScript and Kotlin types, and the description in `docs/CONTRACTS.md`. No change to the radar messages.
- **OpenAPI 0.1.9**: `POST /api/v1/solar` (an ingest token), `GET /api/v1/solar` and `GET /api/v1/solar/history` (an operator); the file is renamed `armor-server-0.1.9.yaml`.
- The generator writes the types of an array of plain values (the list of warning names). Tests: 19.

## [0.1.8] - The shared project tool knows ARMOR-SOLAR

- `armor_project_tool.py` tests ARMOR-SOLAR (its protocol library and the messages its serialiser prints) and runs all three host tests of ARMOR-RADAR (it ran only one). No change to the messages, the schemas or the vectors.

## [0.1.7] - The node information message

- **`info`** (`armor/node/{node_id}/info`, node to server): the node's name, its firmware version, its IPv4 address and the port of its web panel, so a console can offer a link to it. `info.schema.json` follows the same rules as the others (`additionalProperties: false`, the node id equal in topic and body); the address is a dotted quad without leading zeros, the firmware is `x.y.z`, the name 1 to 48 characters.
- 18 new conformance vectors (68 in all), the generated TypeScript and Kotlin types, and a test of the topic.
- `armor-server-0.1.7.yaml`: the state of a node carries `panel` (the address the node said, or null).

## [0.1.6] - OpenAPI 0.1.6

- `armor-server-0.1.6.yaml`: `/api/v1/devices` (and the state, command and test routes), `/api/v1/alarms`, `/api/v1/automations`, `POST /api/v1/mode`, `/api/v1/site`, `/api/v1/system` and `/api/v1/audit`, with their schemas.

## [0.1.5] - OpenAPI 0.1.5

- `armor-server-0.1.5.yaml`: `/api/v1/users`, `/api/v1/users/{id}`, `/api/v1/account`, the signed-in user in the Studio session answer, and the targets of a node in the status.

## [0.1.4] - OpenAPI 0.1.4

- `armor-server-0.1.4.yaml`: `/api/v1/history/summary`, `DELETE /api/v1/history`, the new history filters, and the PTZ semantics (auto-stop, honest errors).

## [0.1.3] - OpenAPI 0.1.3

- `armor-server-0.1.3.yaml`: `/api/v1/camera-status`, `DELETE /api/v1/nodes/{id}`, the `camera` event type, and `/api/v1/status` now needing an operator.

## [0.1.2] - OpenAPI 0.1.2

- `openapi/armor-server-0.1.2.yaml` (replaces 0.1.1) adds `GET /api/v1/history` and `GET`/`PUT /api/v1/rules` with the `Rules` schema.

## [0.1.1] - Schemas as the single source of truth

- The JSON Schemas are now packaged with the library and interpreted directly by a small validator that refuses any schema keyword it does not implement, so a constraint can never be silently skipped.
- The Python validator used to be weaker than the published schemas (it did not check lux range, integer timestamps, sensor 1-3, the node-id pattern or unknown fields); it now enforces all of them.
- Added `command.schema.json` (allow-listed commands, optional sensitivity 1-10).
- Added 50 shared conformance vectors. ARMOR-SERVER runs them too, which found and fixed a real drift: the server used to ignore unknown fields.
- Added generated TypeScript and Kotlin types (`tools/generate_types.py`, `--check` for CI).
- Replaced the 0.1.0 OpenAPI file with `armor-server-0.1.1.yaml`, covering every route and access rule of ARMOR-SERVER.
- 16 tests (previously 3).

## [0.1.0]

- First functional baseline: topic parsing, telemetry/health validation and deterministic envelopes.
