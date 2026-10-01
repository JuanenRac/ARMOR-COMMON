# Changelog

All notable changes to this project are documented here.

## [0.3.1] - The network node can look at a device's web login

- The network message's order types gain `inspect` (look at a device's web administration with a login given for that one order); a conformance vector covers it.
- OpenAPI: `PUT/DELETE /api/v1/network/devices/{id}/login`.
- `docs/CONTRACTS.md` describes the `inspect` order and its `auth`.

## [0.3.0] - The touch panel joins the shared firmware

- **`firmware_base` serves ARMOR-HMI too:** the sync tool and the manifest list the new project (27 shared files), whose settings are its own.
- **The certificate no longer overflows the stack:** the 4 KB buffer that mbedTLS writes the certificate into lives on the heap, and the main task has 16 KB of stack (`CONFIG_ESP_MAIN_TASK_STACK_SIZE=16384`), after the first board reset in a loop right there ("A stack overflow in task main").
- OpenAPI: `GET /api/v1/panel/summary`, `GET /api/v1/system/metrics` and `GET/PUT /api/v1/system/connection`.
- The shared project tool builds and tests ARMOR-HMI (`test_hmi`).
- The conformance vectors of the network message use documentation addresses instead of a real one.

## [0.2.9] - The network message carries the public address and the results of manual orders

- `network.schema.json`: an optional `public` block (the public address of the connection and what a public service says of it) and an optional `results` array (what the node did with the manual orders the server handed it: `scan_now`, `ping`, `traceroute`, `wake`, `ports`, `http`). 13 new conformance vectors (the network message has 77); the TypeScript and Kotlin types are regenerated. `docs/CONTRACTS.md` tells that the orders travel in the answer to `POST /api/v1/network/state`, never over MQTT.
- OpenAPI: `POST/GET /api/v1/network/commands` and `GET /api/v1/network/commands/{id}`.

## [0.2.8] - The contract of the design versions and of deleting alarms

- OpenAPI: `GET /api/v1/{site,electrical/design,network/design}/versions` and `.../versions/{id}` (the versions the server keeps of each design, newest first, to take one back by saving it as the current one) and `DELETE /api/v1/alarms/{id}` (take one alarm off the list); `DELETE /api/v1/alarms` now clears every alarm somebody has acknowledged, ended or not, and is the operator's to use (it was an administrator's, and did nothing at all when the role was missing).

## [0.2.7] - ARMOR-HARDWARE's enclosure was renamed

- `armor_project_tool.py` and the CI template (`tools/ci.yml.template`, `.github/workflows/ci.yml`) now look for ARMOR-HARDWARE's enclosure at `scad/node_enclosure_radar.scad` (rendered to `build/node_enclosure_radar.stl`) instead of the old placeholder `scad/node_enclosure.scad`, which no longer exists: its real design moved there from `CAD/`. The other repositories' vendored copies carry the same line, which only matters to ARMOR-HARDWARE, and pick it up the next time they are synced.

## [0.2.6] - Canonical CI tooling for the whole ecosystem

- `tools/armor_ci_validate.py`, `tools/_armor_readme_parity.py` and `tools/ci.yml.template`, the canonical CI baseline every other A.R.M.O.R. repository vendors (via ARMOR-DOCS' new `tools/sync_ci_tools.py`): the manifest, its version, CHANGELOG.md's heading, the seven README translations' structure and its local Markdown links are checked before the project's own real build/test runs.
- `armor_project_tool.py`: `bump()`'s version odometer now rolls PATCH past 9 into MINOR (`0.2.9` -> `0.3.0`) instead of continuing to `0.2.10` - the same real mistake found and corrected on ARMOR-SERVER's own version once already, now fixed at the source; ARMOR-DEVOPS's own build-test step now runs `scripts/generate_secrets.sh` first when no local `.env` exists, so `docker compose config` has real (disposable) values to interpolate; ARMOR-UPDATER's pytest-based suite is now a recognized project.
- Found while writing the validator and running it once against every repository: four real manifest/build drifts (ARMOR-RADAR, ARMOR-SOLAR, ARMOR-ELECTRICAL, ARMOR-SIMULATOR each had `native_version` behind `version`, and ARMOR-ELECTRICAL's manifest was missing the field outright) - all four fixed.

## [0.2.5] - The state of the local network

- **`network.schema.json`**, the message of the new ARMOR-NETWORK nodes on `armor/network/{node_id}/state`: the interface a node watches, the state of the internet (and whose side an outage is on: `down` is the provider's, `lan_down` this side's), every device found with what is known about it (MAC, maker, name, kind, system, open ports with what each says, announced services, first and last seen) and the latest events (a device that appeared, went or returned, changed its address, two machines for one address, a port that opened or closed, the internet lost and back with how long). Up to 512 devices and 64 events; nothing is a command.
- `validate_network_message` and `parse_network_topic` (the rules that join two fields), 64 new conformance vectors (330 in all; those only a message-level rule refuses are marked `schema_valid`), 3 new tests (39), the generated types are current (the generator now follows objects and arrays of objects inside objects, and the types it made before are byte for byte the same), and the OpenAPI file describes the routes of the network: `POST /api/v1/network/state`, `GET /api/v1/network`, `GET /api/v1/network/history`, `PUT` and `DELETE /api/v1/network/devices/{id}`, `GET` and `PUT /api/v1/network/design`.

## [0.2.4] - The commands to a switch and the node's answer

- **The contract for switching, not activated.** `electrical.schema.json` gains an **optional** `switches` array (up to four: the auxiliary contacts of each contactor, what is selected and wanted, closing, armed, and a latched fault); two new schemas, `electrical_command.schema.json` (`arm`, then `close_a` or `close_b` with the one-time token the node gave, `open`, `acknowledge`) and `electrical_result.schema.json` (accepted, and the refusal when not), on the new topics `armor/electrical/{node_id}/command` and `.../result`. Every command is an allow-list; nothing that switches has been built.
- `validate_electrical_command` and `validate_electrical_result` (and, in `validate_electrical_message`, a switch named once) check the rules that join two fields, which a schema cannot state: a token on the closing actions only, a refusal that is `none` exactly when accepted, a token only in an accepted arm. `parse_electrical_topic` takes the leaf (`state`, `command`, `result`).
- 73 new conformance vectors (266 in all; those only a message-level rule refuses are marked `schema_valid`), 6 new tests (36), the generated types are current, and the OpenAPI file describes `POST /api/v1/electrical/switch` and `GET /api/v1/electrical/switching`.

## [0.2.3] - A second PV input and parallel units in the inverter message

- `solar_inverter.schema.json` gains **optional** fields: `pv2_v`, `pv2_a`, `pv2_w` (a second PV input; `pv_w` is then the sum of both), `units` (up to ten units of a parallel system, each with its number, mode and, when known, serial, fault code and figures) and the totals `total_out_w`, `total_out_va`, `total_load_percent` and `total_charging_a`. Nothing that was valid stops being valid.
- 16 new conformance vectors (193 in all); the generated types are current.
- **The firmware the node projects share, once** (`firmware_base/`, `tools/sync_firmware_base.py`, `docs/FIRMWARE_BASE.md`): 35 files (the network, the settings store, the certificate, the log, the Bluetooth channel and its framing, the login and the address rules, the panel's page and its build...) that ARMOR-RADAR, ARMOR-SOLAR and ARMOR-ELECTRICAL used to keep as three copies now have one master with the project's name as placeholders; `sync` writes it into each project (keeping its line endings), `check` fails when a copy has drifted (it is part of `check_all.sh`) and `import` takes the projects' files as they are. Nothing is shared at build time: each project builds from its own tree as before. 9 tests (30 in all).


## [0.2.2] - The health of a battery

- **`health_percent`** (an integer from 0 to 100, optional) on the battery message and on each module of its stack: the capacity the battery has learned against its rated one. A node that cannot tell leaves it out. Five new conformance vectors (147 in all); the generated TypeScript and Kotlin types carry it.
- OpenAPI: `GET` and `PUT /api/v1/electrical/design` (the electrical design of the house, kept apart from the site design).
- **The `electrical` message** (kind `electrical`, topic `armor/electrical/{node_id}/state`): what an ARMOR-ELECTRICAL node measures on the house's network, one entry per channel (up to 16: a circuit, a line, the grid input, a DC bus) with AC or DC, voltage, current, power (positive when it draws from the network), energy, frequency, power factor, the state of a switch it sees (`closed`, `open`, `unknown`), an alarm and its code, and whether the node is allowed to switch at all. It carries a state, never a command. Schema, 30 conformance vectors (177 in all), the generated TypeScript and Kotlin types, the Python validator (`validate_electrical_message`: the topic, the schema and a channel id once) and OpenAPI for `POST` and `GET /api/v1/electrical/readings` and `GET /api/v1/electrical/history`.

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
