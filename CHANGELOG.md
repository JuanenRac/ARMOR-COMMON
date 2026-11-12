# Changelog

All notable changes to this project are documented here.

## [Unreleased]

- **The text of the pairing code is pinned byte for byte:** a test asserts the exact text that the Studio, Android and iPhone tests also assert, so a code made by one reads in every other.
- **The activity events of the vision service have a route in the server contract, behind a security option:** the setting `vision.activity_events` (off by default) decides whether `POST /api/v1/ai/activity-events` takes anything (off: `{ raised: false, reason: feature_off }`); the route `POST /api/v1/ai/activity-events` (the token of the observation service) and its named body `PostAiActivityEventsRequest` describe the event `armor.vision.activity/v1`, including the optional `notify` flag that is false when the profile of the arming mode does not tell the people the alarms go to; the server still records the event.

- **The waits before a lost network or broker is tried again, and Improv over the cable, are settings of the node:** `retry` (`wifi_first_ms`, `wifi_max_ms`, `mqtt_first_ms`, `mqtt_max_ms` and `scatter_percent`; the defaults are the waits the firmware always used, 1 s growing to 30 s for the Wi-Fi and to 60 s for the broker, 20 % scatter) and `improv.mode` (`setup`, the default, listens for a Wi-Fi network from an ESP Web Tools page only while the node has none stored; `always`; `off`). A start that owes the page an answer listens whatever the mode. The shared node settings read, check (a ceiling below the first wait is refused) and write both, and the diagnostic package carries the new numbers. Host tests of both.

- **The health report names the task with the least stack:** the optional `stack_min_free` and `stack_min_task` (told together) say which task has had the least stack free at its worst, so the console can show it and not only how many tasks are short. The schema, the generated types, readers and writers, the conformance vectors (eight new) and the wire cases follow; a node of an older firmware simply does not say it.

- **The event of the vision service is part of the contract:** `vision_event.schema.json` describes `armor.vision.event/v1` and `v2` (the zone, the followed object, the box, `authorizes_action` always false) and adds the optional `vectors` (where each followed object was heading: a unit direction and a speed, at most 16); `POST /api/v1/ai/vision-events` is in the OpenAPI document, the types and parsers of every language are generated from it and `conformance/vision_event.json` holds 22 cases.

- **Swift readers and writers of the messages:** `tools/generate_swift_parsers.py` writes `generated/ArmorContract.swift` from the schemas, the way `generate_kotlin_parsers.py` does for the Android app: inside the namespace `Contract`, a struct for every message with `init(reading:)` and `toJSON()` (the members the schema names and no other), `Contract.check(name, document)` (the same keywords, order of checks and ASCII meaning of the patterns as the other readers), `Contract.parse<Message>`, `Contract.parse(name, document)` and `Contract.rewrite(name, document)`. The iPhone app keeps a copy next to its sources and a test runs `conformance/wire_cases.tsv` and `conformance/wire_full_cases.tsv` through it: the same verdict as the Python validator, every valid case read, written back equal to the document without the members the schema does not name, and stable when written twice.

- **Messages that hold every member of their contract, for the host tests of the nodes:** `conformance/wire_full_cases.tsv` (made by `tools/make_wire_cases.py`, which now writes and checks both files) has, for every message, four documents with every member the schema declares (the choices of the enumerations and of the numbers turn from one to the next) and four more that leave out about half of the optional members, the half that a checksum of the place of the member picks, so that each optional member is present in some and absent in others; the verdict is the Python validator's. `firmware_base/tests/test_wire_full.cpp` (copied to the five nodes) requires each one to be valid for the generated validator, to be read and written back to a valid, stable document with the same number of members, and feeds the decoder of the text patterns text that is not UTF-8. The branch coverage of the generated reader and writer of the nodes goes from 79 % to 88 %.

- **Tests of the branches the nodes shared and nobody tried:** `firmware_base/tests/test_shared_more.cpp` (copied to the five nodes) now runs the diagnostic package through every branch that decides what leaves a node (the address of a broker without its login, the leaves that are carried and the words that mark a secret, nesting and list limits, a value of each kind, every way a credential is washed from the log, the bounds of the package and of the log), the text of a release signature and of the manifest it signs, the matching of an MQTT topic with its wildcards and the will and birth messages, the frame, reassembly and request of the Bluetooth channel, and the wait between tries. The branch coverage of `diag_package` goes from 77 % to 94 % in every node.

- **The contract describes `GET /api/v1/contract`:** the version of the contracts the server speaks and the state of every node that reported (`ContractStatus`: `server`, `nodes` with `node_id`, `family`, `contract` and `status` current, older, newer or unknown, and `totals`), with its types generated.

- **The error of the order of the changelog names the right line:** when a version is listed after an older one, `tools/armor_ci_validate.py` said `line` followed by the text of the last line of the file instead of the number of the misplaced heading; a test fixes the message. The tool is copied to every repository by the sync of the shared CI tools.

## [0.8.1.2] - The floor of the test coverage goes up: measured by the workflow `coverage-floor.yml`, lines 86.0 % and branches 81.7 % (before: 65.4 and 66.3); the floor is 85.5 and 81.0

- **The floor of the test coverage goes up:** measured by the workflow `coverage-floor.yml`, lines 86.0 % and branches 81.7 % (before: 65.4 and 66.3); the floor is 85.5 and 81.0.

- **Tests for the shared tools that had none:** `armor_project_tool.py` (the odometer of the versions, the bump of the manifest and of the files that mirror it, the lint plan, the Markdown links, the local development secrets, the steps of each kind of repository and the command line), `sync_manifests.py` (versions, facts of a repository, findings, the GitHub facts with budget and cache, `--apply`), `armor_ci_validate.py` (every failure it names), `pretty_run.py` (the panel and the wrapped scripts) and `make_conformance.py` (the committed vectors are what it writes).

- **One more case per message in the seeded wire cases:** for every message with several valid vectors, `conformance/wire_cases.tsv` now holds a document with the optional members of all of them (and a few mutations of it), so the host tests of the nodes also read and write the nested parts of a message (the boot report and the core dump of a health report, a package of diagnostics, the stages of a battery).

- **Shared host tests for the nodes:** `firmware_base/tests/test_shared_more.cpp` (health report words and its optional parts, the report of a dirty start, the settings kept in flash and the operations of the Bluetooth channel).

- **A floor for the test coverage:** the workflow `coverage-floor.yml` runs the Python tests under coverage and fails when the lines or the branches fall below `docs/coverage_threshold.json`. Floor of src/armor_common and tools/: lines 64.5, branches 65.5 (measured 65.35 and 66.31). Raising it is a change of that file, made with a figure measured by the workflow.

- **More tests for the small tools:** the generator of the port constants (the four files, the check of a file out of date, a registry that is wrong), the check of the pins of the consumers (every kind of problem, `--behind`, `--set`) and the comparison of what a node writes back with what the contract keeps now have tests of their own, on copies in temporary folders.

- **The voice turn result can carry `challenge`, and the silence option can be `challenge`:** `voice_turn_result` has an optional `challenge` (two to six digits, shown on the screen of the panel and never said aloud) with accepted and rejected vectors, and the binary answer of the voice turn has two more shared cases; `voice.silence_confirmation` in the HTTP contract now lists `challenge` (off by default). The generated types, parsers, the wire header of the nodes and the vectors were regenerated, and the five nodes follow the new header.

- **The wake word in the shared contract:** `POST /api/v1/voice/wake` (audio up to two seconds, answer `VoiceWake`) and the security option `voice.wake_word` (off by default), with the REST types regenerated.

- **An administrator allows who may have a silent panic phrase:** `PublicUser.panicPhraseAllowed` and `UserChange.panicPhraseAllowed` in the HTTP contract, and the code `panic_not_allowed` (403) of the account's panic phrase route. The user still sets the phrase and the administrator never sees it.

- **The name and the addresses of `network_public.dns` may not be empty strings:** `minLength: 1` on `name` and on the items of `addresses` (the server's reader already refused them by hand; the contract now says so, and every generated reader and writer, the Kotlin parsers, the firmware header and the seeded cases follow).

- **The log hook no longer takes 224 bytes of the stack of every task that logs:** the line is formatted into one static buffer shared by all the tasks (tried, never waited for, with a small buffer on the stack as the way out), so the tasks with 3 KiB of stack have room and the lines of the panel's log are cut at 383 characters instead of 223. The rule of what is kept is `core/log_line.hpp`, host-tested.

- **The board mark of a firmware image is shared with the solar and radar nodes:** `core/image_board.hpp` and its host test now go to four nodes (the alarm and electrical nodes already had them), so an upload for the other board is refused by all of them.
- **A sign-in hashes the password outside the lock of the settings, and the shared store has `with_settings()`:** a node with a screen read the settings through the lock of the store every half second, so the 10 000 rounds of a sign-in froze it; the hash is now computed on a copy of the users, and a task that needs a part of the settings can read it under the lock without copying all of them.

- **The shared firmware can watch the Wi-Fi link by ping (off by default):** `firmware_base/core/link_watch.hpp` holds the rule (a round of pings to the gateway counts as answered with one reply; three silent rounds in a row force a fresh association), `main/network.cpp` runs it when the build option `ARMOR_NET_LINK_WATCH` is on, and the new `tests/test_link_watch.cpp` covers it on a computer (lost packets, the limit, the count cleared by an answer, a seeded long run). The radar node, which already had the watch of its own, now uses the same rule.

- **The shared CI workflow checks a coverage floor where a repository keeps one:** a Node repository with `docs/coverage_threshold.json` (a number per measure) and a package script `coverage` runs it after the build and tests, and a repository without the file runs nothing more. The numbers live in that file, not in the workflow.

## [0.8.1.1] - The contract describes updating the machine's programs from Studio and the phone: GET /api/v1/admin/machine-update, POST /api/v1/admin/machine-update/preview, POST /api/v1/admin/machine-update/apply and GET... (and 3 more changes)

- **The contract describes updating the machine's programs from Studio and the phone:** `GET /api/v1/admin/machine-update`, `POST /api/v1/admin/machine-update/preview`, `POST /api/v1/admin/machine-update/apply` and `GET /api/v1/admin/machine-update/jobs/{id}` in the HTTP contract, with named request and answer schemas (the state, the preview with its one-use plan, the apply with the project typed again) and the generated types that follow from them.
- **The crossings of the counting lines in the contract of the server:** `GET /api/v1/vision/counts` (the counts of each counting line of each camera, whole numbers only, behind the same option as the heat map) with its schemas `VisionCounts` and `LineCount`, and the state of the copy of the node traffic now says how many messages were taken and refused and lists its files; the download of a file of that copy is described too.
- **One file for a page about compatibility:** `registry/compat.json`, written by `tools/make_compat.py` from the registry and the pins of the contracts, lists each consumer with its kind, whether it is a field node, who it feeds and the version of the contracts it was last checked against; a test fails when it is not what those two files give, `tools/contract_pins.py --set` rewrites it with the pins, and it holds no current version (that one is read from `armor.project.json`) so cutting a version never leaves it out of date.
- **A solar or field node can no longer publish the order topic of the batteries:** in the table of the roles (`node_roles.json`) the wide line `topic write armor/solar/{name}/#` of the `node` and `solar-node` roles is now two narrow ones, `topic write armor/solar/{name}/+/state` (the readings of the inverters and batteries) and `topic write armor/solar/{name}/maintenance/result` (the answers of a maintenance step). `armor/solar/{node_id}/maintenance/command` stays the server's alone. The old line is kept in the table only as `relaxed_extra`, which `mqtt_identity.sh` of ARMOR-DEVOPS writes when it runs with `ARMOR_ACL_STRICT_MAINTENANCE_COMMAND=0` (the default is strict). The list of the topics lost its note of a known gap (`acl_wider_than_needed`) and the AsyncAPI file its `x-acl-wider-than-needed`; `covers()` now understands `+` in an access line; new tests check that no node role covers any command topic and that the readings and the answers still pass.

## [0.8.1.0] - The messages have readers and writers generated from the schemas, in C++ and in TypeScript: generated/armorwire.hpp (a struct, a validator, a reader and a writer for each of the 38 schemas, the schema itself run as a table by... (and 4 more changes)

- **The messages have readers and writers generated from the schemas, in C++ and in TypeScript:** `generated/armor_wire.hpp` (a struct, a validator, a reader and a writer for each of the 38 schemas, the schema itself run as a table by a few lines of C++, with the patterns compiled to a small automaton by `tools/wire_regex.py`) and `generated/armor-parsers.ts` (`parseMessage(name, value)` returns the typed message or throws a `ContractError` that says where the document is wrong). `tools/generate_wire.py` and `tools/generate_parsers.py` write them and `--check` fails when they are out of date.
- **The Kotlin readers of the messages are generated too:** `generated/ArmorParsers.kt` (`checkMessage`, `read<Message>` and `parse<Message>` over `org.json`, next to `ArmorContracts.kt`) with `tools/generate_kotlin_parsers.py`, so an app reads the data classes with the checks of the schema instead of field by field.
- **The MQTT topics are described once, and an AsyncAPI file is made from them:** `src/armor_common/mqtt_topics.json` lists every topic (who publishes it, who reads it, the schema of its messages, the QoS and whether the broker keeps it; the commands that only exist when an option is turned on say which), `tools/generate_asyncapi.py` writes `asyncapi/armor-mqtt.asyncapi.json` (AsyncAPI 3.0: one operation per role and topic with its QoS and retain flag, the message pointing at its schema, and the access lines of every role), and `tests/test_mqtt_topics.py` compares the list with the access lines of `node_roles.json`: a role can publish exactly the topics it is listed for. It found that the line that lets a solar node (and a radar node that reads solar equipment) write below `armor/solar/{name}/` also covers the topic of the maintenance commands, which only the server publishes; the list says so until the lines are narrowed.
- **The shared firmware carries the generated readers and a test that runs them:** `core/armor_wire.hpp` and `tests/test_wire.cpp` reach the five nodes with the rest of the base (`tools/sync_firmware_base.py`). The test reads the seeded cases and checks the generated validator, reader and writer on the compiler and flags of each node, and runs the parsers the node has written by hand for the messages it receives against the same verdicts: none may accept what the contract refuses.
- **A seeded oracle for the parsers:** `tools/make_wire_cases.py` writes `conformance/wire_cases.tsv` (the valid vectors and seeded mutations of them: a member taken away or added, another type, the limits, the longest text, a value outside an enumeration), each with the verdict of the Python validator; `host_tests/test_wire_oracle.cpp` (CMake and `ctest`, workflow `wire-host.yml`) checks that the C++ readers agree on every case and that what the writers write back is valid, stable and equal to the document read (`tools/check_wire_rewrites.py`).

## [0.8.0.9] - The copy of the node traffic is in the HTTP contract: GET and PUT /api/v1/system/ingest/recording (an administrator) with the schemas IngestRecording and IngestRecordingChange, and the security option ingest.recording (off by... (and 1 more changes)

- **The copy of the node traffic is in the HTTP contract:** `GET` and `PUT /api/v1/system/ingest/recording` (an administrator) with the schemas `IngestRecording` and `IngestRecordingChange`, and the security option `ingest.recording` (off by default); the generated REST types are current.
- **`tools/make_sbom.py` writes the software bill of materials of a Node.js project:** CycloneDX 1.5 read from its `package-lock.json`, with the version, the hash and the licence of every package, the same file for the same lock file (no time, no machine name), and `--check FILE` compares a published one with the lock file so that a person or the maintenance agent can verify it. It is not a signature of the build.

## [0.8.0.8] - The health report of a node can say which contracts its firmware was checked against: optional contract in nodehealth (schema 0.2.0, the same three or four numbers as the information message), with 7 vectors (four parts, three... (and 5 more changes)

- **The health report of a node can say which contracts its firmware was checked against:** optional `contract` in `node_health` (schema 0.2.0, the same three or four numbers as the information message), with 7 vectors (four parts, three parts, a leading v, two parts, a trailing line feed, a number, empty), the generated types and the document of the contracts updated. The shared firmware writes it into every report from the constant of the node (`main/contract_version.hpp`), only when it looks like a version, with host tests of the rule; so the alarm, electrical and solar nodes, which send no information message, say it too, and the radar and the wall panel say it in both.
- **The contract of the two switches of the broker rules that Studio can ask for:** `GET /api/v1/admin/mqtt/relays` and `POST /api/v1/admin/mqtt/relays/{kind}` (`battery-write` for one solar node, `alarm-state-relay`) in the OpenAPI document, with the schemas `AdminRelays`, `AdminRelayChanged` and `PostAdminMqttRelaysKindRequest`, the security option `admin.acl_relays` (off by default) and the REST types regenerated; the answers `403 acl_relays_disabled`, `totp_not_enrolled`, `totp_required` and `totp_invalid` are described (an agent's 401 reaches the console as a 403 so that it is not taken for a session that ended), as are the two confirmations (`confirm` and `confirm_text`) of the request.
- **One set of rules to hide the secrets of an environment file, with its vectors:** `src/armor_common/env_masking.json` holds the mask, the pattern of the secret keys, the way a login or a token of an address is hidden and 19 vectors (12 for hiding, 7 for giving the hidden values back when the file is saved, among them Windows line ends, an address whose host was edited and a mask for a key that is not in the file any more); `env_masking.py` is the reference and `tests/test_env_masking.py` runs every vector and checks that hiding twice changes nothing. The maintenance agent hides the secrets in what it returns and puts them back from its own file when it is saved, and the server follows the same vectors.
- **One movement model for the observation services:** `src/armor_common/motion_core.py` decides movement per pixel after the change of the whole picture is taken away, cuts the picture into a grid only to say where, and gives the regions as rectangles `{x, y, w, h}`; `tools/sync_motion_core.py` copies it into ARMOR-SERVER-AI and ARMOR-VISION and `check` fails when a copy differs. The observation of a camera takes an optional `regions` (at most 16 rectangles, the schema moves to 0.2.0, ten new conformance vectors, generated types and the HTTP description follow).
- **A node and the server say which contracts they were checked against:** the information message of a node takes an optional `contract` (a version of this repository, three or four numbers; the schema moves to 0.3.0 and the conformance vectors cover the good and bad shapes), `/api/v1/info` and the panel of each node in the system state carry the same field, and the generated types follow. The number is the pin of the reverse-dependency run; `tests/test_contract_declared.py` compares the constant of the server (`src/contract_version.ts`) and of every node (`main/contract_version.hpp`) with `registry/contract_pins.json`.
- **The contract pins of all the consumers of the reverse-dependency run are at the current version** after its green runs: the eighteen of the matrix, among them the server, Studio, the two phone apps, the observation service, the vision service and the voice gateway.

## [0.8.0.7] - The figures of the README are current: the conformance vectors, the JSON Schemas, the HTTP paths and operations, the files of conformance/ and the tests now say what the repository holds. (and 16 more changes)

- **The figures of the README are current:** the conformance vectors, the JSON Schemas, the HTTP paths and operations, the files of `conformance/` and the tests now say what the repository holds.
- **The contract describes the trusted phones:** `/api/v1/devices/trust` (list, register), `/api/v1/devices/trust/{id}` (end), `/api/v1/devices/trust/challenge` and `/api/v1/devices/trust/session` (renew a session by signing a one-time challenge) with the schemas `TrustedDevice`, `TrustedDeviceList`, `TrustedChallenge` and the three request bodies, and the options `client.trusted_devices` (off by default) and `client.trusted_session_h` (1 to 720 hours, 72) in the security settings.
- **Each consumer has a pin of the contracts and a manual reverse-dependency run:** `registry/contract_pins.json` records the version of the contracts every repository was last checked against, `tools/contract_pins.py` checks it (`--check`, never above the current version), moves a pin (`--set`) and lists the consumers that are behind (`--behind`), and the workflow `reverse-deps.yml` (started by hand) runs the checks of eighteen consumers against the checkout of the contracts before a version is published. The tests of the pin are in `tests/test_contract_pins.py`.
- **The contract describes the counting lines of a camera:** `/api/v1/cameras/{id}/count-lines` (read, and set by an administrator) with the schemas `CountLine`, `CountLines` and `CountLinesInput`, and their generated types.
- **One table of the broker access of each kind of identity (`src/armor_common/node_roles.json`, `armor_common.node_roles`):** the user name and the access lines of a field node, panel, solar, electrical, alarm and network node, a device, a bridge and a consumer, with tests that no node can write an order topic or write outside its own name; the identity script of the deployment repository is compared with it by its own test (see `docs/NODE_ROLES.md`).
- **One format for the id of a command in the whole family:** `command_id` is sixteen lowercase hexadecimal digits in the electrical, solar-battery and node-control messages too (the alarm messages already said so, and the server has always issued ids of that form), in the schemas, the OpenAPI path parameters, the vectors (new refusals of eight characters, capitals and letters that are not hexadecimal) and the shared firmware (`firmware_base/core/control_gate.hpp` with its tests). The token of a two-step order keeps its own rule.
- **The refusal codes are one list for every client:** the OpenAPI file has `ApiErrorCode` (the codes a client branches on), `PinErrorCode` (`wrong_pin`, `pin_locked`, `pin_not_set`) and `PinRefusal` (the body of a refusal about the PIN of the acknowledge order); the generator also writes them as C++ constants (`generated/armor_error_codes.hpp`) and a test keeps the list, the generated files and the OpenAPI file equal, so a wall panel keeps no copy of the words.
- **The observation of a camera has its schema (`ai_observation.schema.json`) and vectors:** the body of `POST /api/v1/ai/observations` (camera, severity, up to five reasons, light profile, `motion`, `motion_ratio`, radar tracks) is described once for the service that watches the camera and for the server; the generated TypeScript and Kotlin types follow.
- **The text of the provisioning QR code has its writer and reader (`armor_common.provisioning`):** `armor-provision:` plus the compact JSON of the node id and the server address, with no field where a secret could go; the reader refuses extra fields, other versions, addresses with a user name, a query, a fragment or a path, and node ids the contract does not accept, with tests and a section in `docs/CONTRACTS.md`. The screens that show and scan it are for the Studio, the Android app and the nodes.
- **The contract describes the automatic security update routes:** `/api/v1/admin/system/auto-updates` (read and change the switch, the reboot policy and its window) and `/api/v1/maintenance/armed` (asked by the maintenance helper with its own token before it reboots), with their schemas; the generated REST types follow.
- **The table of alarm codes has `alarm_siren_fault`, the notice that the siren of a panel may not sound:** the words of the code in the eight languages, what it means and what to check, and a conformance vector of the alert (severity `warning`). The server raises it while a panel reports that the wiring of its siren is open, shorted or unreadable and the new option `alarm.siren_fault_notice` (on by default) allows it; the OpenAPI file and the generated REST types describe the option.
- **One numbering for the ports (`src/armor_common/ports.json`):** server 18080, Studio 18081, MQTT 18883, voice 18090 (and the optional TLS ports 8883, 8443 and 8081) for the CM5 installer and for Docker alike; `tools/generate_ports.py` writes the TypeScript, Kotlin, C++ and shell constants (`generated/armor-ports.*`, `ArmorPorts.kt`, `armor_ports.hpp`), `armor_common.ports` reads it from Python and `tests/test_ports.py` fails when a file of any sibling repository still uses an old number (see `docs/PORTS.md`). The OpenAPI server URL follows.
- **The OpenAPI file describes `POST /api/v1/voice/panic-check`:** the route where the voice gateway shows the text it has just transcribed, before interpreting it, so that the server can look for a panic phrase; the answer is always `{ ok: true }` and never says whether the text matched (schemas `PostVoicePanicCheckRequest` and `VoicePanicCheckReply`); the generated REST types follow.
- **One validator for every family:** `validate_message(topic, payload)` reads a message of any family (node, solar, electrical, alarm with its zigbee feed and policy, network, health, radar events, control, devices, server alert) by choosing the validator from the topic, so a consumer no longer repeats the routing; `encode` and `decode` use it and now accept the messages of the other families, with tests.
- **Documents:** the firmware base page names the five node projects it is copied into, and the signed firmware page names the release tool that exists in this repository.
- **Property-based tests of the validators of the contract:** `tests/test_property_validators.py` checks, with seeded generated cases, that a topic is accepted exactly when it has the shape and a valid node id (the length limit of 64 included), that `sensitivity` is accepted only on `set_thresholds` and only from 1 to 10, that only the three commands exist, that the duration of a control operation stays inside its range, that no value outside a range or an enum that any schema states is accepted (and the limits themselves are), that a boolean or a text is never taken for a number, and that a damaged or truncated line gives a `ValueError`, never another kind of error. A mutation run of `parse_topic`, `validate_topic_and_payload` and the node id check killed 35 of 44 mutants the first time and 43 after the tests it pointed to were added (the refusal texts and the character set of a node id); the method and the figures are in `docs/TESTING_STRATEGY.md`. The mutation run is not part of the CI.
- **`decode` answers a `ValueError` to a document nested thousands of levels deep:** the JSON parser raised a `RecursionError`, which a reader that catches only `ValueError` (as the documentation says) did not expect; it is now reported as "envelope is not valid JSON", with a test.

## [0.8.0.6] - The telemetry, info and command messages may say their own kind, the type generator reads every schema and the limits of the contract are generated as C++ constants, sensitivity belongs only to set_thresholds and the state of an alarm node can be signed

- **`telemetry`, `info` and `command` may say their own kind:** the schemas accept an optional `kind` equal to the message kind (their versions go to 0.2.0, 0.2.0 and 0.3.0), so a generic dispatcher can read the payload alone; a message without it is still valid, one with another value is refused. `health` already uses `kind` for the sort of node and is left as it is. Six conformance vectors and a test.
- **The type generator reads every schema of the folder:** a new `*.schema.json` gets its TypeScript and Kotlin types without editing the generator (the three that were missing, `device_state`, `network_orders` and `server_alert`, are now generated), and a test requires a type in both languages for every schema file.
- **The limits of the contract are also generated as C++ constants** (`generated/armor_contracts.hpp`: the node id pattern, the most targets, the largest lux, the range of `sensitivity` and the list of commands), kept current by `tools/generate_types.py --check`, and a test requires the node id rule of the shared firmware to say what the schema says.
- **`sensitivity` belongs only to the command `set_thresholds`:** `validate_topic_and_payload` refuses it on any other command, with three new conformance vectors.
- **The state of an alarm node can be signed:** `alarm.schema.json` gains the optional `seq` and `sig` (HMAC-SHA256 with the key of the installation over `armor-alarm-state|node_id|timestamp_ms|phase|mode|siren|locked_out|commands_enabled|open_zones|zones|seq`), `validate_alarm_message` requires the pair together, `alarm_state_canonical` and `alarm_state_signature` compute the bytes and the value, seven conformance vectors and `conformance/signatures/alarm_state.json` (the key, the canonical text and the signature of five states and four altered copies) are shared with the readers, and the guide describes the format.
- **The OpenAPI file describes the setting `server.alarm_state_signature`** (off by default): the server publishes a signed copy of each alarm state it hears; the generated types follow.

## [0.8.0.5] - A route for the Prometheus numbers, the dead-man ping, the incident record and the dry run of an installation import, with named schemas and the counts of routes and operations brought up to date

- **The OpenAPI file describes the incident record** (`GET /api/v1/admin/incident` and `POST /api/v1/admin/incident/verify`, with the schemas `IncidentExport` and `IncidentVerdict`); the generated REST types follow.
- **The OpenAPI file describes `GET /metrics`** (the Prometheus text page, with its own bearer scheme), the two new settings `metrics.prometheus` and `heartbeat.enabled` (both off by default), the `dry_run` of the installation import and the `dry_run` mark of its report; the generated REST types follow.
- **The state of an alarm node can carry the wiring of its siren:** `alarm.schema.json` gains the optional `siren_loop` (`unknown`, `ok`, `open`, `short`, `unreadable`) and `siren_fault`, sent together and only by a node that supervises its siren; `validate_alarm_message` requires the pair and that the fault is true exactly for `open`, `short` and `unreadable`; twelve conformance vectors; the generated types follow.
- **The firmware the nodes share can tell which board an image was built for** (`core/image_board.hpp` and its tests, with the two settings `security.ota_check_board` and `security.ota_require_board_mark` in `core/node_settings.hpp`, for the electrical and alarm nodes); the shared copy of `tools/check_sdkconfig.py` is brought to what the nodes hold, so the check of the shared files passes again.

## [0.8.0.4] - The help text of every alarm code lives in the table every client shares

- **The shared alarm table holds the help of every alarm code** (59 codes, in the eight languages, European Portuguese; two lines: what it means and what to check), not only the eleven solar ones. A test requires a help text for every code of `alarm_codes.json` and the same two-line shape in every language, and that the alarms that threaten life say to get safe first.

## [0.8.0.3] - The modes of arming carry the map of profiles and panels of each mode, the false-alarm mark of an alarm, the token of the live vision service and the help of the alarm codes in the table every client shares

- **The arming modes say how they reach the alarm panels:** `arming_modes.schema.json` gains the optional `panel_map` (`profiles`: the profile each mode arms, `only`: the panels that are asked), with conformance vectors; defaults are the mapping and the panels it always had.
- **The shared alarm table also holds the help of each alarm code, and the vision service can have a token:** `alarm_facts.json` gains `help` (what an alarm code means and what to check, in the eight languages) next to the labels of the facts, kept whole by `tests/test_alarm_facts.py`; `SecuritySettings` gains the read-only `vision.service_token_set`.
- **An alarm can be marked as a false alarm by a person:** `POST /api/v1/alarms/{id}/false-alarm` (administrators and operators, audited) with `false_alarm` true, false or null; the `Alarm` carries `false_alarm` and `false_alarm_by`, and the summary of a day counts the mark before it infers anything from a disarm.

## [0.8.0.2] - The contract describes the summary of a day and the activity heat map, the settings of both and the labels of the facts of an alarm for the mobile clients

- **The summary of a day has more sources, with four tuning settings:** `SecuritySettings` gains `summary.log_days`, `summary.reading_every_s`, `summary.power_every_s` and `summary.false_alarm_s`; the guide says the summary now also covers lost links, false alarms, the readings of the sensors and the power of the house, with only plain facts reaching it.
- **The heat map is asked of a live ARMOR-VISION service:** the contract of `GET /api/v1/vision/heatmap` keeps its shape; its `503` now means the live service is not set up or is not this machine while the new setting `vision.service_remote` (`false` by default) is off, and a service that cannot be reached is a `502`. `SecuritySettings` gains `vision.service_url` (the address of the service, empty when not set up) and `vision.service_remote`.
- **The entry delay of an arming mode also holds back a node and a camera listed in `entry`, and the limits of the two reports are settings:** the descriptions of `entry` and `entry_delay_s` in `arming_modes.schema.json` and the contracts guide now say that a node (its intrusion and its silence) or a camera (its silence) waits like a device; `SecuritySettings` has `reports.timeout_s` (5 to 120, default 20), `reports.queue_max` (1 to 10, default 3) and `reports.requests_per_minute` (1 to 300, default 30), the values the report routes always used.
- **The contract describes the summary of a day and the activity heat map:** `GET /api/v1/summary/daily` and `GET /api/v1/vision/heatmap` (administrators and operators only, each behind its own security option that is off by default), the options `summary.daily` and `vision.heatmap`, the schemas `daily_summary` and `heatmap` with 24 conformance vectors (the summary has no field for the free text of an event, a setting or a secret, and the map says `contains_images: false`), their generated types, and grids of numbers in the generated TypeScript and Kotlin types.
- **The labels of the facts of an alarm are one table in the eight languages** (`src/armor_common/alarm_facts.json`, described in the contracts guide and kept whole by `tests/test_alarm_facts.py`), so the consoles can show what an alarm carries (which device, which panel, what each panel answered) with the same words.

## [0.8.0.1] - The server tells the panel of each node the profile of the arming mode, with an alarm when a panel does not answer, the voice and control arming as the away mode and the alarm codes in the eight languages

- **A panel that does not confirm the arming mode is an alarm:** the code `mode_panel_sync_failed` (severity `high`, source `alarm` / `mode_panel`) with its words in the eight languages in `alarm_codes.json`, described next to `panel_sync` in the guide and the OpenAPI file; arming by the control API and by voice is arming the mode `away` while the modes are on.
- **The contract describes the panel sync of the arming modes:** the setting `alarm.mode_panel_sync` (off by default), the object `panel_sync` in the system state and in `GET /api/v1/alarm/modes` (`PanelSync`: the mode, the profile it asks for, the status `none`, `pending`, `confirmed` or `failed` and one entry per panel with its reason), `panel_sync_enabled` in the modes state, and the guide says how a mode and a profile join (away arms the profile away, home arms stay, night arms night); the generated types and a test of the schema are updated.

## [0.8.0.0] - The contract describes the arming modes (away, home, night), the shared workflow lints and type-checks and the documentation covers the manifest evidence

- **The contract describes the arming modes (away, home, night):** the schema `arming_modes.schema.json` with its shared vectors (`conformance/arming_modes.json`, 42 of them) and `validate_arming_modes`, the routes `GET` and `PUT /api/v1/alarm/modes`, the modes `away`, `home` and `night` and `confirm_unassigned` in `POST /api/v1/mode`, `arming_mode` in the system state, the answers `modes_disabled` and `no_zones_assigned`, and the four settings `alarm.arming_modes`, `alarm.mode_downgrade_pin`, `alarm.mode_schedule` and `alarm.mode_schedule_lowers` (all off or conservative by default: the system only arms and disarms until an administrator turns the modes on). The generated types are regenerated; `docs/CONTRACTS.md` has the model.
- **The shared workflow lints and type-checks:** `tools/ci.yml.template` has a "Lint and type-check" step and `armor_project_tool.py` a `lint` action that installs ruff 0.17.1 and mypy 2.4.0 and runs `ruff check --select F,E9,B` and `mypy`. ruff looks at the whole checkout and mypy type-checks `src/` where the repository has a mypy configuration and `tools/` and `scripts/` wherever they hold Python, with the same settings in every repository (the Qt stubs are installed only where the code imports Qt); `ci_lint = false` under `[tool.armor]` in `pyproject.toml` skips the step and `lint_tools = false` leaves out only `tools/` and `scripts/`. The shared tools and generators are annotated so that they pass.
- **The documentation covers the manifest evidence, the shared panel page and the old readings:** the manifest guide describes `evidence` and `hardware_bound`, the firmware base guide the green frames of the Overview and the failed-login limit of every node, and the contracts guide how a channel with an old reading is set aside; the figures follow the contract (195 paths, 253 operations, 1228 conformance vectors, 237 tests).

## [0.7.9] - The sign-in limit of a node and the stale-readings option in the contract, the green frames of the Overview fit their text, status lights kept inside what the manifest allows and clean type check and lint

- **The Ed25519 generator of the firmware base has no unused import:** `firmware_base/tools/gen_ed25519.py` no longer imports `isqrt`; what it writes is the same.
- **The type check and the lint of the Python code come out clean:** the type comments of the validators name the codes that the current checker reports, a duplicated helper of the conformance generator and an unused import are gone; the behaviour and the generated vectors are the same.
- **The green frames of the Overview fit their text:** in the Overview cards (Hardware, Flash memory and the rest) each green frame is as wide as its content, stays on the right and grows to the left, so long texts in any of the eight languages are no longer squeezed; on a narrow screen the label goes above its frame.
- **The lights of the Project status table are kept inside what the manifest allows:** `tools/status_lights.py` (canonical here, copied to the other repositories by `sync_ci_tools.py`) reads `maturity` and the new `evidence` field of the manifest (`host-test`, `simulator`, `bench` or `field`; `hardware_bound: false` for a repository with no hardware). `--check`, run by the validator, fails when a light is above its ceiling; `--suggest` lists what could be better; `--apply` lowers the lights in the eight READMEs and in the generator and never touches a sentence. It has 17 tests; the README states 235.
- **The contract has the route to set a node's sign-in limit and the option to set old readings aside:** `POST /api/v1/admin/nodes/settings`, `stale_channels` and `totals.stale_readings` in the electrical readings, and `electrical.set_aside_old_readings` in the security settings; the generated types follow.
- **The tests of the field nodes play the node's MQTT client against a real Mosquitto:** the shared `tests/check_mosquitto.py` starts a broker with the account rules of a node, connects as the node does (retained last will, retained birth, QoS 1, its own order topic) and checks that what the node prints reaches the server on the right topic, that an order reaches the node, that the node cannot write on another node's topic and that the last will arrives when the connection dies; the shared workflow installs Mosquitto in the node repositories and makes its absence a failure. A stand-in broker tries the check in the tests of this repository.

## [0.7.8] - The contract of the sign-in country, the language of a phone and the alarm audio, and the shared tools of the pictures and the live panel

- **The contract knows the country of a sign-in and the language of a phone:** the alert `login.remote` may carry `login_country` (two capital letters) and `login_country_new` (always true when present), only on a sign-in from outside and never the second without the first, with three new conformance vectors; the security option `login.country_alert` (on by default) is in the HTTP contract; `POST /api/v1/push/register` accepts `language`, one of the eight, so the notice of an alarm is told in the language of the phone.
- **The contract describes the sound of an alarm for the wall panel:** `GET /api/v1/alarm-audio`, `GET /api/v1/alarm-audio/spoken` and `GET`, `PUT` and `DELETE /api/v1/alarm-audio/sounds/{source}` with their schemas, the two security options `alarm_audio.spoken` and `alarm_audio.custom_sounds` (both off by default), the feature `alarm_audio` and the generated types; the section *The sound of an alarm* of the contracts document says how the audio is asked for and checked.
- **The README follows the universal layout in the eight languages:** the sections of the layout with the figures taken from the code (34 schemas, 1225 vectors, 191 paths and 247 operations of the HTTP contract, 214 tests), the broker topics, the build options of the firmware base, a threat and defence table, troubleshooting, and the Repository Structure drawn from `docs/structure.json` next to the architecture picture; the Mermaid diagram stays inside a collapsible block.
- **Every project has `test.bat` and `test.sh`:** they run the tests and the checks with the same live panel, a line per step and the number of tests, and never change the version. The launchers of `build`, `build-test` and `test` no longer print their own banner, because the panel has one; and the panel can also draw any script as steps (`pretty_run.py --wrap`), taking the lines `[2/5] ...` or `+ command` of the script as its steps.
- **The build and test scripts show a live panel:** `build`, `build-test` and `run` of every project print a banner, one line per step with its time and the number of tests that ran, hide the output of the steps that pass (it shows only when one fails, and it is kept in a log file) and end with a summary box. `pretty_run.py` is standard library only and is copied to every project; with `NO_COLOR` or `PRETTY_PLAIN=1` it prints plain lines for logs and CI.
- **The Architecture and Repository Structure pictures of the READMEs are drawn by shared tools:** `tools/make_architecture.py` (from `docs/architecture.json`, at most twelve boxes in three columns, discreet SMIL motion, `--check` that fails when the picture, the JSON or the code a box points to disagree) and `tools/make_structure.py` (from `docs/structure.json`, the text tree in eight languages and the animated picture, checked against the files Git versions), with their shared kit `tools/_readme_svg.py` that measures every text and refuses overflow and overlap. They are vendored into the other repositories by the sync tool of ARMOR-DOCS; `docs/README_PICTURES.md` explains them and `tests/test_readme_tools.py` tries them, screenshots included.
- **A check for the layout of the README:** `tools/universal_readme_check.py` verifies the 22 sections of the README (fixed names, icons and order in the eight languages, the 14 required ones, the header, the traffic lights of Project status, no dates, no mention of the version rule, no private references) and, with `--run`, that the number of tests in the README is the one the tests report. `armor_ci_validate.py` runs it as a warning (`UNIVERSAL_README=WARN n`) and the family can turn it into a failure in one line (`FAMILY_STRICT`).
- **The architecture of ARMOR-COMMON is a picture:** `docs/architecture.json` and the generated `images/architecture.svg` (the Mermaid diagram stays in the README as text).

## [0.7.7] - The contract describes the traits of a camera and the PIN of the written voice command

- **The OpenAPI describes `silence_pin` of the written voice command:** the PIN that silencing by voice asks for in the `pin` mode, apart from the PIN of the signed-in user. The REST types are regenerated.
- **The inter-processor call tasks of every node have more stack:** `CONFIG_ESP_IPC_TASK_STACK_SIZE` is 2048 (the default left 532 bytes free in `ipc0` on a running node), in the shared firmware base and in the two nodes that keep their own configuration.
- **The framed values of the Overview page have the same width:** each value fills the column next to its label, so the boxes of a card line up instead of having the width of their text.
- **The OpenAPI describes the traits of a camera:** the camera and camera-view schemas carry the optional layout (one stream or two lenses split), group and lens name, type of camera, whether it pans, tilts and zooms, the address of its own configurator page, its field of view and ranges, and the new `CameraParams` schema for its internal parameters. The REST types are regenerated.
- **The OpenAPI describes the removal of the example readings of the solar equipment:** `DELETE /api/v1/solar/devices/{node}/{device}/example` and `DELETE /api/v1/solar/examples`.
- **The HTTP contract describes the still picture of a camera:** `POST /api/v1/cameras/{id}/preview-ticket` and `GET /api/v1/cameras/{id}/preview` (and the schema `PreviewTicket`), with the generated types.
- **The parsers of the firmware are fuzzed:** `fuzz/` holds libFuzzer targets for the JSON parser, the Bluetooth set-up framing and the Improv serial parser (AddressSanitizer and UndefinedBehaviorSanitizer), seeds, `fuzz/run_fuzz.sh`, a workflow that runs them when the shared code changes, and a test; see `docs/FUZZING.md`.

## [0.7.6] - One list of the repositories of the family and the types of the HTTP contract are generated too

- **The answers of the HTTP contract say what they hold, and the generator knows the parts of the messages:** the arming profiles, the diagnostic package of a node, the interface, the internet, the scan, the public address and the devices of a network node, and the boot report of a node health message are now types of their own where the contract points at them. The automations, the battery operations, the connection settings (and the state of the MQTT encryption), the history summary, the report of an installation import, the preferences (the weather place is an object), the preflight issues (kind, level and code), the remote check, the system summary, the registrations and totals of the solar overview, the health of every node (with the restarts, the control state and the levels) and the proof of custody (with its signature as the server writes it) are described field by field, and each field the server always sends is required. The generator stops when the contract points at a type that the generated messages do not have.
- **One list of the repositories of the family:** `registry/repositories.json` names every repository once, with its kind, its group, the technologies of its banner, its place on the map of the family, who it feeds, whether it is a node, whether it carries the shared tools and the workflow of Studio and the server, and which deployable component it is. The READMEs, the brand pictures, the catalogue and the copy of the shared tools of ARMOR-DOCS read it, and a test fails when the shared project tool, the firmware sync or the workflow template name other nodes than it does.
- **The types of the HTTP contract are generated too:** `tools/generate_rest_types.py` writes `generated/armor-rest.ts` from every component of `openapi/armor-server.yaml` (the messages of the nodes are not repeated: they use the types of `armor-contracts.ts`), `--check` and a test fail when it is stale, and ARMOR-STUDIO compares the types it reads the server's answers with against them at compile time.
- **A node says which version of the network contract it speaks:** the network message takes an optional whole `contract` (1 today; a node that says nothing speaks the first), with vectors for a good one, zero and a text, and the overview of the server says it and whether the node is older than the server.
- **More of the HTTP contract is typed:** the switching and alarm-command statuses (what is pending and what became of the latest commands), the orders for a network node and the fields of an event that every client reads.
- **The workflow that tries Studio and the server together has its template here** (`tools/e2e.yml.template`), vendored into ARMOR-STUDIO and ARMOR-SERVER by the sync tool of ARMOR-DOCS.

## [0.7.5] - Security options as settings, new guards and a validator that reports every fault

- **The pairing text of the installation's HTTPS is in the contract:** `GET /api/v1/admin/remote/tls` gives the pin of the authority that signs it (SHA-256 of its public key, base64) and the text `armor-pin:<host>:<pin>` that a phone takes to trust it the first time.
- **The validators are tried against damaged messages:** `tests/test_fuzz_validator.py` changes, adds and removes values of every valid conformance vector (seeded, so a failure repeats) and requires "accepted" or a `ContractError` and nothing else.
- **The HTTP contract types more of what the server answers:** the sums of the solar, electrical, alarm, network and health pages, the node views of the electrical, alarm and network pages (with the message each node sent), the samples of the electrical and network histories, the metrics of the machine, the audit trail, the services, files and broker accounts of the administration, the cameras found and the energy of the panel summary are objects with their fields and no longer open ones (65 open objects before, 28 now), the devices and the automations have their sources, commands, triggers and actions described, and the detail of an issue of the preflight check is the text it always was and not an object. The four places of the notification page (`webhook`, `mqtt`, `telegram`, `homeassistant`) are flags, as the server has always sent them, not objects.
- **A wall panel can acknowledge with its PIN:** `POST /api/v1/alarms/acknowledge` takes an optional `pin` (the PIN of the panel's account), with the refusals 403 and 429 described in the OpenAPI file.
- **The live picture has a lighter profile in the contract:** the stream ticket takes `quality` (`auto`, `normal`, `low`) and says the one it granted, and the live address accepts `?quality=low` for an operator without a ticket, described in the OpenAPI file.
- **The voice turn may say which panel spoke:** the header `X-Armor-Panel` (the node id of the panel) is described in the contracts guide, for the commands the voice gateway carries out to be written as that panel's.
- **The name the house is reached by is checked against the public address:** the network message may carry `public.dns` (`name`, `addresses`, `matches`) with its schema, vectors and types, and the alarm table has `network_dns_stale` for the day the address changed and the dynamic DNS did not follow.
- **The notification channels report their counters:** `GET /api/v1/admin/notifications` may carry `metrics` by place (delivered, failed, dropped, queued, and when and why the last one failed) and `ntfy`, described in the OpenAPI file.
- **Keeping the stored secrets encrypted is an option of the contract:** the security option `nodes.nvs_encryption` (`off` by default, `secrets`) in the OpenAPI file and the optional `nvs_encryption` of the policy message (`alarm_policy`), with the schema, vectors and generated types; it asks a node to encrypt only the secrets it stores, with no eFuse burned.
- **The words of every alarm code are one table in the eight languages** (`src/armor_common/alarm_codes.json`, described in the contracts guide and kept whole by `tests/test_alarm_codes.py`), so the server tells a person what happened instead of the internal code.
- **Fixed: a node with stored settings no longer restarts in a loop at power-up.** The start-up code read the stored settings and the copy made before the last update on the stack of the main task (about 3 KB each, plus the reader's own copy); with settings stored the 16 KB stack overflowed and the node restarted again and again before it could start the network. They now live on the heap.
- **The lock of the phone app is a security option of the contract:** `client.device_lock` (`user`, `sensitive`, `always`) in the security options of the session and of `/api/v1/security/settings`, described in the OpenAPI file and in `docs/CONTRACTS.md`.
- **The two sizes of a spoken turn are options of the contract:** `voice.turn_max_bytes` and `voice.reply_audio_max_bytes` (whole numbers, 3200 to 1920000 and 3200 to 1000000) in `SecuritySettings`, so a client edits them with the rest.
- **The PIN to disarm reaches the alarm node:** the policy message (`alarm_policy`) may carry `disarm_pin` (`never`, `if_set` or `always`, the server's `alarm.disarm_pin`); it is left out while it is `if_set`, so a message of the older form means the same and a panel that does not know the field simply ignores the whole message. Schema, validator, vectors (the three words, a word that is not one, capitals, a flag) and the contracts guide describe it.
- **The live channel of the wall panel is a contract:** `docs/CONTRACTS.md` describes the WebSocket `/api/v1/panel/events` (the frame, the heartbeat, the close codes 4401 and 4403, what a client does when it is missing), and `SecuritySettings` has `panel.live_events` (on by default) in the OpenAPI file. The contract of the binary voice turn now says that ARMOR-NODE-HMI sends it, with the fall back to the raw request on `415`.
- **The limit on wrong passwords per minute is a setting of the node** in the shared firmware: `system.login_limit_per_minute` (30 as always, 0 for none, at most 120), read by the five panels.
- **A relay can be interlocked with another** (`interlock` in the relay settings, empty by default): a request to close one while the other is closed is refused from the panel, the broker and the central alike, the node never opens the partner by itself, and the alarm's siren is not held back.
- **The universal image holds no fleet secret unless asked for:** `tools/build_node.sh generic` adds `secrets/generic.conf` only with `ARMOR_WITH_FLEET_SECRET=1`, names that image `*-local` and says it is never to be published, and a public build is refused when the configuration it ended with holds a secret or a set-up code; the option's help says the same.
- **The release tool refuses a build whose configuration it cannot read,** because an image that cannot be checked for a fleet secret or a set-up code is not published (`--unchecked` is the owner saying so on purpose); a build that holds either is refused as before.
- **New checks shared by the five nodes:** the Bluetooth session under its lock (`check_ble_session.py`) and the routes, the panels and the stand-in nodes (`check_routes.py`); the guard on the paths of a save also keeps the tolerant read of the settings, the serial set-up and the update check.
- **The binary voice turn is a contract:** a wall panel can send the audio of a spoken turn as `multipart/form-data` (the audio as raw bytes and an optional `meta` part, `voice_turn_meta`) and ask for the spoken answer as a second part of a `multipart/mixed` answer (`voice_turn_result`) instead of base64; the raw request keeps working. The rules (parts, framing, limits, errors, the option `voice.multipart_turn`) are in `docs/CONTRACTS.md`, in the OpenAPI document and in the new `armor_common.voice` (reader and writer), with 43 shared byte-level cases in `conformance/voice/turn_multipart.json` and the two schemas with their vectors and generated types.
- **The validator can say every fault of a message at once** (`collect_payload_errors`, built on `iter_errors`); the first one is the one `validate_payload` has always raised, and a published schema is still a copy nobody can change for the others.
- **The contract:** `SecuritySettings` has `network.login_secure_only` (off by default) in the OpenAPI file, and the contracts guide says that ARMOR-NODE-ALARM now applies the policy of the server and checks the signed zone feed.
- **Board names in the shared text:** the touch panel is one board (`lcd7box`), and the shared Kconfig and network comments say so.

## [0.7.4] - Node diagnostics, reading quality and held values in the contract

- The repository has a security policy, a code of conduct, a contributing guide and a support file.
- The banner follows the animated style of the ecosystem banners, with the name, the kind and the technologies of the project.
- **The zone messages of the server can be signed:** `alarm_zone_feed` may carry `seq` and `sig` (together), `zone_feed_signature` computes the HMAC-SHA256 over `node_id|zone|state|battery_low|seq`, and the vectors cover a signed message and every malformed one; the generated TypeScript and Kotlin gain `AlarmZoneFeed`.
- **The policy of the server reaches the panels:** a new message, `alarm_policy` (`armor/alarm/{node_id}/policy`: `config_hash`, `zone_feed`, `zone_feed_signature`), with its schema, validator (`validate_alarm_policy`), vectors and generated types. Panel side pending: the alarm firmware does not read it yet.
- **The session announces its capabilities:** the HTTP contract describes `capabilities` in `GET /api/v1/studio/session` (what the person may do, the parts of the server that exist and the security options in force), `GET` and `PUT /api/v1/security/settings` and `GET /api/v1/alarm/zone-feed/key/{node}`; an older server has no such field.
- **ESP-IDF 5.5.5 is the one version:** `tools/build_node.sh` uses the 5.5.5 container, and the firmware guide, the requirements of the READMEs and the manifest name it (it said 5.4 in places).
- **Node diagnostics in the shared contract:** the dirty-boot report, the core dump, the settings safety check, the diagnostic package, the radar events and the read-only diagnostic token messages, with their schemas, conformance vectors and generated types.
- **An electrical meter channel may carry `reading_age_ms` and `errors`,** how old its reading is and how many requests to it failed since boot, so a consumer tells a real 0 W from no data.
- **The inverter message may carry `clamped`,** the names of the numbers the node held at a limit because the inverter sent them beyond what is possible.

## [0.7.3] - The contract and the shared base to control the nodes from the server

- **Controlling a node from the server:** two new messages, `node_control_command` (server to node, `armor/control/{node_id}/command`, or `armor/control/all/command` for an arm) and `node_control_result` (node to server, `armor/control/{node_id}/result`), with their schemas, validators (`validate_node_control_command`, `validate_node_control_result`, `parse_control_topic`) and conformance vectors for every operation and every refusal: restart (now or rolling), pause, resume, standby, identify, diagnostics, maintenance on and off. The token is bound to the operation; there is no factory reset, no erase and no deep sleep.
- **The health report says what the node is doing:** optional `control_state`, `control_since_ms`, `control_by`, `control_until_s`, `maintenance` and `maintenance_until_s`.
- **The history has words for it:** `control_requested`, `control_acknowledged`, `control_applied`, `control_refused`, `control_back` and `control_lost`.
- **The HTTP contract:** `/api/v1/nodes/{id}/control`, `/api/v1/nodes/control` and `/api/v1/nodes/control/operations`, documented and typed, and the generated TypeScript and Kotlin types.
- **Planned maintenance:** a new retained message, `node_maintenance` (node to server, `armor/control/{node_id}/maintenance`), with its schema, validator (`validate_node_maintenance`), conformance vectors and generated types: a node says why and for how long it expects to be quiet (restart, pause, standby, update, upload, operator) before it goes quiet, and clears it when it is back, so the server can hold back the node-offline alert for a bounded time. The history gets `maintenance_started`, `maintenance_ended` and `maintenance_expired`; the HTTP contract describes the `NodeMaintenanceWindow`.
- **The node base:** a pure state machine (`control_gate.hpp`: running, paused, standby, the maintenance flag, one-time operation-bound tokens, busy refusals, a rate limit and the rolling schedule) and the shared module that applies it (`node_control`), with host tests; the host test of the GitHub request now builds its request with the right escapes.
- **The node base sends the planned-maintenance signal:** `control_gate.hpp` gets `MaintenanceSignal` (what to publish and when: a restart, a pause, a standby, an update, an upload or an operator window raises it, the end of each clears it, a boot clears what the last run left and a boot into standby keeps `standby`, every window with a time ends by itself unless the work it announced is still going) with its message builder, `node_control` publishes it retained through the new `mqtt_link::publish_retained` (QoS 1) and offers `announce_maintenance` / `announce_maintenance_done` to the firmware update, the slot copy and the panel upload; host tests cover it against the shared vectors.
- **The guard and the server's orders work together:** a node the server paused or put in standby is not restarted by the guard for a task it stopped on purpose (nor one with a restart order on its way; the memory rules stay in force), a restart that was ordered leaves a mark so the next start tells it from a restart of the guard and does not count it against the three an hour, the standby kept in flash survives a restart of the guard, and the planned-maintenance signal goes out before an ordered restart, an install and an upload.
- **Fixed:** the log line that closes the Bluetooth set-up window passed a text chosen at run time as the format of the message, which the logging macro does not accept at build time.
- **Shared files:** `main/node_guard.*` (`note_deliberate_restart`), `main/node_control.*` (`restart_pending`) and the pure rules `counted_missing_tasks` and `deliberate_boot` in `core/node_guard.hpp`, with host tests.

## [0.7.2] - The memory of the nodes: the shared rules of the guard, the Bluetooth window, the gate, and the internal-memory fields of the health report

- **The shared firmware base protects the internal memory:** `core/node_guard.hpp` and `core/ble_window.hpp` (the guard that restarts once and never in a loop, the gate at the panel's door, the controlled restart on a failed allocation, the dead-man switch and the Bluetooth set-up window), `main/node_guard.cpp`, the Bluetooth memory settings and `tools/check_sdkconfig.py`; the web servers, the broker link and the Bluetooth module of the five nodes use them.
- **The health report tells the internal memory on its own:** `heap_internal_free`, `heap_internal_min`, `heap_internal_largest` (together) and `psram_free` are optional fields of `node_health` (schema, validator, vectors and the generated types), and the shared memory module puts the TLS buffers, the large requests and the stacks of safe tasks in the external RAM.
- **Last will and birth, retained:** the contract documents the life state of a node on `armor/health/{node_id}` (`online` false as the will and true at each connection, both retained).
- **Fixed:** the host test of the request buffer of the GitHub update had text that did not compile; the Improv page says `provisioned` only after the Wi-Fi network was joined.

## [0.7.1] - The GitHub update fits the redirect address

- The HTTP client of the GitHub update gets a 4 KB request buffer (the default of 512 bytes made it say "Out of buffer" on the request that follows GitHub's long redirect, so the checksum could not be read), with a host test and a static guard that every client sets it.

## [0.7.0] - Orders and answers for writing to Pylontech batteries

- **Orders and answers for writing to a Pylontech battery:** two new messages, `solar_battery_command` (server to node, `armor/solar/{node_id}/maintenance/command`) and `solar_battery_result` (node to server, `.../result`), with their JSON Schemas, validators (`validate_solar_battery_command`, `validate_solar_battery_result`) and 125 conformance vectors. Writing is two steps (`arm`, then `execute` with the one-time token the node gave), `cancel` stops an operation that may still be stopped and `stage` carries a firmware image to the node in pieces.
- **One table of the operations (`battery_ops.json`):** the twenty typed operations with their risk, whether they need the battery at rest, whether they can be cut halfway, the values each takes and the ranges and the order between values that the maker's tool states, the models with the capacity the maker gives, the protections, the words the expert console blocks, the limits and every refusal a node can give. The node, the server and the screens are all tested against it.
- **The rules that join fields:** what each action carries, the values of the operation against the table, the refusal that matches `accepted`, a token only in an armed answer and the fields each stage needs; the service password of the battery has no field in either message, and a test looks for one.
- **HTTP contract:** the routes `/api/v1/solar/battery-ops` (catalog, list, arm, execute, cancel, restore and the firmware image), documented and typed, and a `batteries` category (with `battery_requested` and `battery_operation`) in the system events of the history.
- **Generated types:** the new messages in the TypeScript and Kotlin types.

## [0.6.9] - Update from GitHub through long redirects, real update errors, the green frames of the Summary and richer battery readings

- **Update from GitHub through long redirects:** the node's header buffer is 20 KB (in the external RAM, 6 KB where a board has none) and the log tells the free internal memory before and after the client is opened.
- **The real reason of a failed update:** `fetch_error` names a checksum or signature that could not be read (connection, size or HTTP status) and keeps "no checksum" for a release that carries none; tested.
- **The Summary of every node panel draws its values in green frames:** one shared style rule (`.kv.framed`).
- **A battery module tells more:** `solar_battery` accepts, per module, the model, the versions of its board and software, the number of cells, the current it allows each way, the speed of its console, the life counters, the health of each cell and the newest entry of its event log; conformance vectors for every field, and the generated types.
- **The contracts can say more:** the schema checker accepts a schema as `additionalProperties`, `propertyNames` and `maxProperties`.
- **The node base:** a last will on the connection to the broker, a lock around the task report, and the failed initialisations of the network, the settings and the Ethernet degrade with a log line instead of aborting.
- **The API description:** the cells of the day, the alarm settings of the energy and the event log of a battery are described.

## [0.6.8] - Node firmware base: tolerant settings, login limit, Bluetooth race, missing board image

- Shared node firmware: settings kept in flash are read as far as they can be after an update (unknown members ignored, a value that cannot be accepted falls back alone instead of resetting the node), with tests.
- Shared node firmware: the login of the node panels also limits the wrong passwords of all sources together to thirty per minute, with tests.
- Shared node firmware: a Bluetooth answer is sent only to the phone that asked, and the requests waiting for the worker are discarded when a phone connects or disconnects.
- Shared node firmware: a newer release without an image for the node's board is reported as no_asset_for_board instead of passing for up to date.

## [0.6.7] - Wider login table and stricter text in the shared node base

- The shared login throttle keeps thirty-two sources (it kept eight), so a handful of busy addresses, or the people counted next to them, no longer crowd out the rest; a blocked source is still never pushed out.
- The over-the-air download limit is the size of an application slot (3 MiB), so an image that cannot fit is refused as a bad size before the slot is erased instead of failing inside the write.
- The shared JSON reader refuses malformed UTF-8 (a lead byte without its continuation, overlong forms, raw surrogates, anything above U+10FFFF) and documents of more than 4096 values; a number of a billion or more keeps its digits when it is written.
- A set-up code compiled in with letters in lower case is stored in capitals, the form the panel's page sends, so it can be used to set the node up.
- The comment of the relay command topics says what the code does: the broker may send ON or OFF, and TOGGLE exists only on the node's own HTTP API.
- Shared tests for the new limits (the table of sources, the UTF-8 forms, the number of values, large numbers).
- The shared base is written into the five node projects again, so all copies stay identical.

## [0.6.6] - Stored passwords follow their host

- The shared node settings tie the stored broker password, and the password of each backup broker, to the host it was typed for: pointing them at another host without a new password clears it. Same-host edits keep it.
- The shared settings refuse an access point bandwidth other than 20 or 40 MHz, and the list of networks that may use the panel refuses parts with a leading zero.
- The shared tests check both rules, and the known-gap checks of the shared node tests are ordinary checks now.

## [0.6.5] - Connection and system events of the history

- New schemas `connection_event` (a client of a kind - Studio, the Android app, the panel of a node, the voice service or another - that was first seen, signed in, was refused, signed out or whose session ended or expired), `system_event` (a node that appears, returns, changes firmware or disappears; the broker link; settings; services; updates; arming, disarming and silencing with the profile; backups) and `connection_client` (one entry of the list of clients, with its last sign of life and its open sessions). The words are a fixed list and no field can hold a secret; the address and the user agent are for administrators only.
- Conformance vectors for the three (51 more, accepted and refused), the generated TypeScript and Kotlin types, and the OpenAPI description of `GET /api/v1/history/connections` and of the new filters of `GET /api/v1/history` (`category`, `kind`, `client`, `user`, `all` and the types `connection` and `system`).
- The contract lists the types of event that were missing in the filter of the history (`device` and `alarm`) and says that the totals of the summary count the events shown by default.

## [0.6.4] - The HTTP contract types every message

- openapi/armor-server.yaml: every request body, answer and error names a component schema (no bare object bodies); one error schema for all refusals, a status-text schema for the routes that answer with the bare status, and an explicit access rule on every operation (including the public ones and the stream ticket).
- The GET of /api/v1/admin/updates was hidden by a duplicated path key and is described again; the voice command lists the Portuguese language; the console state matches what the server answers.
- Examples in the schemas are checked against their schemas, and the file is validated with its relative references resolved.
- tests/test_openapi.py reads the route table of ARMOR-SERVER when it is checked out next to this repository and fails when a route (method and path) is registered but not described, or described but not registered.
- CI installs jsonschema with the other contract-test tools.

## [0.6.3] - Node health and arming profiles

- node_health.schema.json (new): the same health report for a radar, a solar, an electrical, an alarm and a wall-panel node, published to armor/health/{node_id}; validate_node_health also checks the rules that join fields (the least heap is never above the free heap, a signal only on a Wi-Fi link that is up, no link is a link that is down).
- arm_profile.schema.json (new): a named way of arming a panel (base away or stay, per-zone armed and delay, exit and entry delays, siren, notification level), and alarm_command.schema.json accepts it as the optional profile of an arm, whose base must be the mode. The alarm state gains the optional arm_profiles and profile.
- Conformance vectors for both (41 and 23, plus 26 for the command and 6 for the state), generated TypeScript and Kotlin types, the OpenAPI routes of node health and of the profiles, and CONTRACTS.md describe them. Everything is additive: a message without the new fields is read as before.
- Firmware base: core/node_health.hpp, main/node_health.hpp and main/node_health.cpp are shared by the five nodes, mqtt_link.cpp counts the connections to the broker, and tests/test_base.cpp tests the reset reasons, the link choice, the last error of a log and the JSON of the report.

## [0.6.2] - An optional encrypted link to the broker in the shared node base

- firmware_base carries mqtt_tls.hpp (what a stored authority may look like: exactly one certificate in PEM, at most 2 KB, and what the settings must say when TLS is on), the mqtt.tls and mqtt.ca_pem settings of the nodes that share node_settings.hpp, the connection in mqtt_link.cpp that trusts only that authority and checks the broker's name, and the textarea style of the panel.
- tests/test_mqtt_tls.cpp is shared by the five nodes and checks the settings of each. sync_firmware_base.py keeps every copy identical.

## [0.6.1] - The contracts know the silence of a siren

- alarm_command.schema.json and alarm_result.schema.json accept the action silence (no mode, no force, no PIN, like a disarm); alarm.schema.json lists the event kind siren_silenced.
- Conformance vectors for a silence, its refusals and the new event; generated TypeScript and Kotlin types refreshed; CONTRACTS.md and the server OpenAPI file describe the new action.

## [0.6.0] - A zone can be in trouble, a channel can be an estimate and a wall panel says what it is

- The alarm zone state has a fourth value, trouble: the node cannot read the zone, so it is not guarding.
- An electrical channel may carry power_estimated: true when its power and energy are an estimate from a current and a nominal voltage, not a measurement.
- The health message has an optional kind (radar or panel): a wall panel says it is one, so the server keeps it apart from the radars.
- Conformance vectors: 534 in all. The contract page describes the three changes.

## [0.5.9] - An inverter can say that its warnings are unknown

- The solar inverter message has an optional boolean warnings_known: false says that the inverter dialect cannot ask for its warnings (REVO), so an empty list means unknown and not none; absent means true. Two conformance vectors (527 in all), the generated types and the contract page describe it.

## [0.5.8] - The project manifest is documented, with the optional requires field

- docs/PROJECT_MANIFEST.md (new) describes every key of armor.project.json, including the optional requires field: the projects that must be installed, and built, before this one. The field is optional, a manifest without it is unchanged, and the shared CI checks ignore it.
- A test keeps the page in step with the keys the CI checks require.

## [0.5.7] - The firmware base: the networks that may use a node's panel, wrong passwords counted per person, and the panels with relative paths

- `core/admin_sources.hpp` (new, shared by the five nodes): the list of networks that may use a node's panel - empty means the private ranges of a house, otherwise addresses and networks separated by commas - with the parser, the rules and 74 new host checks (the default ranges, the edges of each range, a stray comma, too many entries, a list that cannot be read never lets everybody in).
- `core/auth.hpp`: `user_key()`, the key under which the wrong passwords of one person are counted, so a guess against an account is slowed down from any address; checked in the base tests.
- `panel/index.html` uses relative paths, so the panel of a node opens both directly and behind the server's proxy; the five panels do the same in their own files.
- The settings of ELECTRICAL and ALARM (`core/node_settings.hpp`) carry `web.admin_sources`; SOLAR, HMI and RADAR have it in their own configuration with the same rules.

## [0.5.6] - A sign-in from outside is an alert of the server, and the routes of the node panels, the VPN and the dynamic DNS name are in the contract

- The alert of the server has a new event, `login.remote`, with the person (`login_user`) and the address (`login_from`); the validator demands both, and there are two more conformance vectors (a sign-in from outside, and one that names no one).
- The OpenAPI file describes the panel of a node through the server (`/api/v1/nodes/{nodeId}/panel/{path}`), the list of node panels and the look at a node's certificate, and the routes that set up the VPN and the dynamic DNS name.

## [0.5.5] - Strict patterns, a valid HTTP contract, signed manifests and firmware that agrees with itself

- **Patterns mean what JSON Schema says.** The Python validator used to accept a text with a line feed at the end where the server and the firmware refuse it, and to read `\d` as any digit of any script; `$` is now the end of the text and the classes are ASCII. A schema that holds a keyword with a value this validator does not understand (`"required": "x"`, a list in `items`) is refused, the schema a caller gets is its own copy, and an envelope that repeats a field name is refused.
- **Firmware versions of four numbers** (`0.8.0.1`) are accepted by the node information schema, by the version comparison of the nodes, by the changelog and README checks, and by the manifest tools.
- **New contracts for what had none:** the state, availability and commands of a relay as a device, the Zigbee feed the server gives a panel, the alert the server publishes, and the answer of the network endpoint with its orders (a login only sealed). A network a node watches must be a private range. 523 conformance vectors.
- **The HTTP contract is valid.** `openapi/armor-server.yaml` (the version left its name) is real YAML and a valid OpenAPI 3.1 document; its descriptions were split at their commas, the removal of history sat under the wrong path and said operator where the server asks for an administrator, and the media routes lacked their parameters. A test keeps it valid and its version equal to this repository's.
- **The generated types compile.** Kotlin keeps the names of the JSON fields and writes reserved words between backticks, fixed values are literals, and every object inside a message has a type of its own.
- **Signed releases bind the image to what it is.** The signature of a node's update covers the project, the board, the version and the hash (`<image>.sig2`); a node refuses an image that is not newer than the one it runs, one whose version differs from the release's, and any file that is not one of its own repository's releases. A signature whose S is not below the order of the group is refused. `tools/release_firmware.py` and `tools/firmware_sign.mjs` make the release files and keep a fleet secret out of them.
- **The shared firmware** no longer lets the random generator's noise source run while the radio does, restarts the node over a broker address that cannot be used, or leaves a reconnect to a client that is being destroyed; it probes the first broker before going back to it, copies a 32-byte network name whole, keeps relays free of a pull-up between reset and direction, writes users to flash all-or-nothing, refuses a repeated name in a JSON document, writes whole numbers whole, blocks a phone that fails its Bluetooth login on its own and the channel only after twenty failures together, and closes the Bluetooth door for five minutes after five failed pairings.
- **The tool that shares the firmware** (`sync_firmware_base.py`) tries each file with and without the plain node name turned into a placeholder, keeps a base file with a hand-written one, and lists files that are almost the same; five files that had dropped out of the base are shared again, and the ones that really differ are kept apart in `firmware_base/_unshared/`.
- **The continuous integration compares for real.** It fetches ARMOR-COMMON (and the simulator, for the server) next to the repository under test, fails when a comparison cannot be made, runs every host test the nodes register, and checks here the generated types, the vectors, the OpenAPI file and the firmware of the five nodes.
- **Also in the shared firmware:** a TOGGLE from the broker is refused (a message can be delivered twice; the node's own API can still toggle), a relay can be reserved for one owner (the alarm's siren) so that the panel, the broker and the central cannot move it and it does not fall back to open, Improv over USB on a board with a cable also tells the node to use the Wi-Fi it was given, the upload by hand takes the same lock as an installation from GitHub and the copy of a slot, and a build option turns off the reset of the settings by the BOOT button.
- Documentation: the guides of the contracts, the shared firmware and the signed firmware are brought up to date, and the READMEs in the eight languages state what is shared, how many tests and vectors there are, and that only the radar node has run on a board.

## [0.5.4] - The ignore zones routes in the OpenAPI file

- The shared firmware base verifies Ed25519 signatures (`core/ed25519_verify.hpp`, generated by `firmware_base/tools/gen_ed25519.py`) and holds the public key of the releases (`core/fw_trust.hpp`): the GitHub updater of the five nodes installs only signed firmware. Tests check SHA-512 and Ed25519 against another implementation and the real key.
- The OpenAPI file documents GET and PUT /api/v1/cameras/{id}/ignore-zones.

## [0.5.3] - The capture settings in the OpenAPI file

- The OpenAPI file documents GET and PUT /api/v1/capture-settings.

## [0.5.2] - Bluetooth pairing with a PIN in the shared firmware base and the new routes in the OpenAPI file

- The shared firmware base pairs over Bluetooth with a 6-digit PIN derived from the node's setup code (display only, authenticated link), and a test holds its range and spread; the five firmware projects take it from here.
- The OpenAPI file documents the Zigbee zone links route and that a login of the network inspection arrives sealed for the node.

## [0.5.1] - The check before arming, the proof of custody and the daily electrical energy in the contract

- The OpenAPI file describes `GET /api/v1/preflight`, the signed proof of custody of an evidence file and its verification, and the energy of each electrical channel per day.

## [0.5.0] - Firmware base: slot copy, background update check, serialised settings and a longer station pause cap

- A firmware slot can be copied to the other one from the panel, and the update of a node waits for the image to be confirmed only after the node has an address or its own access point is reachable, rolling back after five minutes otherwise.
- The station connection that was paused to leave the access point free retries after ten minutes at most instead of waiting forever.
- The firmware check against GitHub runs in the background and the panel asks for its result, so a slow search no longer freezes the panel.
- Saving the settings is serialised, so two browsers saving at once cannot mix their changes.
- Logging out needs the page's own token, which stops another page from logging the panel out.
- A session table can say whether a session is still alive, so the nodes drop the dead ones instead of keeping them until the table is full.

## [0.4.9] - Maintenance routes in the contract, a changelog order check and the copy-log style of the node panels

- The OpenAPI contract describes the maintenance routes (programs, updates, history, jobs, console).
- `armor_ci_validate.py` checks that the versions of a CHANGELOG are in order and not repeated.
- The firmware base panel has the style of the copy-log icon button.
- The firmware base copies the firmware that runs into the other slot (`start_copy`, `copy_progress`, `slot_generation` in github_update) so that a node can keep both slots at the same version.

## [0.4.8] - Version scheme of four components from 0.8.0

- The shared project tool and the validator know the numbering of the family: three components up to 0.7.9 and four from 0.8.0 (0.7.9 -> 0.8.0.0 -> 0.8.0.9 -> 0.8.1.0 ...), with no component ever reaching 10.

## [0.4.7] - Shared firmware base and project tool

- The shared firmware base carries the session, broker and web-server fixes of the round, and the project tool knows ARMOR-VISION.

## [0.4.6] - An alarm with the central disarmed is a valid message

- **`validate_alarm_message` accepts the alarm phase with the mode `disarmed`:** a smoke, gas or panic zone, or a tamper, sounds with nobody having armed the central, and the node says so. A disarmed panel still has the mode `disarmed`, and an arming or armed one still never has it. New conformance vectors: an alarm while disarmed (valid), an alarm while armed (valid), an exit delay with no mode (invalid).
- `openapi/armor-server-0.4.3.yaml` describes the PIN of the mode, of the command to an alarm node and of the voice, the routes of the PIN of a user and of the account, and the answers 403 (`wrong_pin`, `pin_not_set`) and 429 (`pin_locked`).
- `firmware_base/` carries the publish queue of `mqtt_link.cpp`, the watchdog settings and the relay task's watchdog subscription, so that the copies in the node projects stay identical.

## [0.4.5] - What an inverter says about itself, and more for the nodes' shared firmware

- **`solar_inverter.schema.json` gains optional fields:** `serial` (8 to 20 letters and digits), `firmware` (up to 24 characters), `pv_energy_total_wh` (the energy the panels have made in all) and `ratings` (what the unit is rated for and how it is set: the rated output and voltages, the battery's bulk, float, low and recharge voltages, the charging currents, and four names: the type of battery, the input range, the priority of the output source and of the charger). Twenty-three new conformance vectors (the unknown-field vector now uses another field); the generated types are current.
- **`firmware_base/`:** `core/backoff.hpp` (waits that grow between tries, used by the Wi-Fi and the broker links), `core/improv.hpp` and `main/improv_serial.*` (Improv Wi-Fi over the USB cable), `core/task_health.hpp` and `main/task_health.*` (the stack each task has left), `core/central_link.hpp` (the direct HTTP API for a central: the token and the relay request, for the electrical and alarm nodes), `remote.http` and `remote.token` in `core/io_config.hpp`, a direct way to move a relay by name in `main/relay_outputs.*`, and shared host tests (`tests/test_base.cpp`, `tests/test_central.cpp`).

## [0.4.4] - The Zigbee bridge is the alarm node's own

- **`main/zigbee_bridge.cpp` and `.hpp` are shared with ARMOR-NODE-ELECTRICAL only**; ARMOR-NODE-ALARM has its own copy with a hook for the node to hold the radio itself. `core/zigbee_bridge.hpp` stays shared. `sync_firmware_base.py check` passes for 52 files in 197 copies.

## [0.4.3] - The alarm messages, and a firmware base that every node shares

- **Alarm contract (version 0):** `alarm.schema.json`, `alarm_command.schema.json` and `alarm_result.schema.json` for `armor/alarm/{node_id}/state | command | result`, the validators `validate_alarm_message`, `validate_alarm_command` and `validate_alarm_result`, 81 conformance vectors (the ones only the message rules refuse are marked), the generated TypeScript and Kotlin types, and a section in `docs/CONTRACTS.md`. A disarm carries no PIN.
- **`firmware_base` carries the files every node shares:** the update from GitHub (`github_update`, `semver`, `release_assets`: a node picks the image of its own board, `armor_<kind>-<board>.bin`, and checks its SHA-256), the broker topic rule, the node-wide settings (`node_settings`, `config_common`), the base board's pins, relays and Zigbee radio bridge (`io_config`, `base_board`, `relay_bank`, `relay_remote`, `zigbee_bridge`, `relay_outputs`). `sync_firmware_base.py check` passes for 52 shared files in 199 copies.
- **OpenAPI:** the file is now `openapi/armor-server-0.4.3.yaml`; it describes `POST /api/v1/alarm/state`, `GET /api/v1/alarm/nodes`, `GET /api/v1/alarm/commands` and `POST /api/v1/alarm/command`, and the firmware kinds include `alarm`.

## [0.4.2] - Battery management and inverter fields in the solar contract, and the new server routes

- **OpenAPI: `GET /api/v1/electrical/devices`.**
- **OpenAPI: the levels of the energy alarms** (`GET` and `PUT /api/v1/solar/alarms`).
- **Solar contract: what a battery management system and an inverter can add.** The battery stack takes `power_w`, `balancing` (cells being balanced), `protecting`, `charge_mos` and `discharge_mos`; the inverter takes `bus_v` (the DC bus). All optional, with new conformance vectors (valid and refused) and the regenerated types.
- `openapi/armor-server-0.4.2.yaml`: the service administration route accepts `pause` and `resume` besides start, stop, restart and reload.

## [0.4.1] - The voice command in the OpenAPI file lists its commands

- `openapi/armor-server-0.4.2.yaml` says which commands `/api/v1/voice/command` understands: arm, disarm, status, silence, alarms, nodes, cameras, radar, solar, electrical, network, time, help, lights on and lights off.

## [0.4.0] - The observation routes in the OpenAPI file

- `openapi/armor-server-0.4.2.yaml` describes `/api/v1/ai/context`, `/api/v1/ai/cameras/{id}/frame` and `/api/v1/ai/observations` of ARMOR-SERVER 0.4.9, and the `aiBearer` security scheme.

## [0.3.9] - The notification routes in the OpenAPI file

- `openapi/armor-server-0.4.2.yaml` describes `/api/v1/admin/notifications` and `/api/v1/admin/notifications/test` of ARMOR-SERVER 0.4.8.

## [0.3.8] - The voice routes in the OpenAPI file

- `openapi/armor-server-0.4.2.yaml` describes `/api/v1/voice/status` and `/api/v1/voice/command` of ARMOR-SERVER 0.4.6.


## [0.3.7] - The firmware routes in the OpenAPI file

- `openapi/armor-server-0.4.2.yaml` describes `/api/v1/admin/firmware/uploads`, `releases/{kind}`, `probe`, `jobs` and `jobs/{id}` of ARMOR-SERVER 0.4.4.

## [0.3.6] - One rule for the node id of every topic, and the OpenAPI file with the version of the server

- **Node id:** `parse_topic` (the node topics) now applies the same rule as the solar, electrical and network topics - at most 64 characters, not starting with `-` or `_` - through one shared check, so a long or odd id is refused the same way everywhere.
- **`openapi/armor-server-0.4.2.yaml`** (it was `armor-server-0.4.0.yaml`, with version 0.4.0 inside) carries the version of the server it describes; the documents that name it say so.


## [0.3.5] - The shared firmware catches up, and the administration routes in the OpenAPI file

- **`firmware_base` re-made from the four node projects:** it now carries the clock (time zone and time server), the flash overview, the persistent set-up code, the Wi-Fi reason shown for a secured network joined with an empty password, the pause of the station's attempts while someone is using the rescue network, and the style rules for the buttons that are file pickers. `sync_firmware_base.py check` passes again for the 35 shared files.
- **`openapi/armor-server-0.4.0.yaml`:** the `/api/v1/admin/...` routes of ARMOR-SERVER 0.4.2 (services, settings files, broker accounts, adopting a node).

## [0.3.4] - The OpenAPI file was not actually valid YAML

- **`openapi/armor-server-0.4.0.yaml`: two summaries had an unquoted "word: word" inside parentheses** (the network and services routes), which a real YAML parser reads as a second mapping key, not plain text - this repo's own conformance test only ever did a substring check, so it never caught it. Both quoted now; the file parses cleanly.
- Added `GET`/`PUT /api/v1/preferences` to the same file, for ARMOR-SERVER 0.4.1's new per-account language/theme/weather-place storage.

## [0.3.3] - ARMOR-NODE-HMI was missing from the shared firmware's checks

- **`firmware_base/manifest.json` reconciled with what the four node projects actually run:** the fixes made to `ble_provision.cpp` (the Bluetooth stack size and the advertise-while-in-setup condition) and to the panel's titled `<title>`, among others, had been written straight into ARMOR-NODE-RADAR/-SOLAR/-ELECTRICAL's own copies without ever updating this project's shared base - `sync_firmware_base.py check` had nothing current to compare ARMOR-NODE-HMI against, so its own copies (never fixed) went unnoticed. The base now reflects the fixed content, and ARMOR-NODE-HMI has been synced to it (see its own 0.0.4).
- **`openapi/armor-server-0.2.0.yaml` renamed to `armor-server-0.4.0.yaml`, its own `info.version` bumped from 0.1.7 to match**, catching the file's name and its own declared version up to ARMOR-SERVER's real current one; its content (76 routes) was already reasonably current, only the name and the version field had stopped following it.

## [0.3.2] - The services route

- OpenAPI: `GET /api/v1/system/services` (every service of the system, running or not).

## [0.3.1] - The network node can look at a device's web login

- The network message's order types gain `inspect` (look at a device's web administration with a login given for that one order); a conformance vector covers it.
- OpenAPI: `PUT/DELETE /api/v1/network/devices/{id}/login`.
- `docs/CONTRACTS.md` describes the `inspect` order and its `auth`.

## [0.3.0] - The touch panel joins the shared firmware

- **`firmware_base` serves ARMOR-NODE-HMI too:** the sync tool and the manifest list the new project (27 shared files), whose settings are its own.
- **The certificate no longer overflows the stack:** the 4 KB buffer that mbedTLS writes the certificate into lives on the heap, and the main task has 16 KB of stack (`CONFIG_ESP_MAIN_TASK_STACK_SIZE=16384`), after the first board reset in a loop right there ("A stack overflow in task main").
- OpenAPI: `GET /api/v1/panel/summary`, `GET /api/v1/system/metrics` and `GET/PUT /api/v1/system/connection`.
- The shared project tool builds and tests ARMOR-NODE-HMI (`test_hmi`).
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
- Found while writing the validator and running it once against every repository: four real manifest/build drifts (ARMOR-NODE-RADAR, ARMOR-NODE-SOLAR, ARMOR-NODE-ELECTRICAL, ARMOR-SIMULATOR each had `native_version` behind `version`, and ARMOR-NODE-ELECTRICAL's manifest was missing the field outright) - all four fixed.

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
- **The firmware the node projects share, once** (`firmware_base/`, `tools/sync_firmware_base.py`, `docs/FIRMWARE_BASE.md`): 35 files (the network, the settings store, the certificate, the log, the Bluetooth channel and its framing, the login and the address rules, the panel's page and its build...) that ARMOR-NODE-RADAR, ARMOR-NODE-SOLAR and ARMOR-NODE-ELECTRICAL used to keep as three copies now have one master with the project's name as placeholders; `sync` writes it into each project (keeping its line endings), `check` fails when a copy has drifted (it is part of `check_all.sh`) and `import` takes the projects' files as they are. Nothing is shared at build time: each project builds from its own tree as before. 9 tests (30 in all).


## [0.2.2] - The health of a battery

- **`health_percent`** (an integer from 0 to 100, optional) on the battery message and on each module of its stack: the capacity the battery has learned against its rated one. A node that cannot tell leaves it out. Five new conformance vectors (147 in all); the generated TypeScript and Kotlin types carry it.
- OpenAPI: `GET` and `PUT /api/v1/electrical/design` (the electrical design of the house, kept apart from the site design).
- **The `electrical` message** (kind `electrical`, topic `armor/electrical/{node_id}/state`): what an ARMOR-NODE-ELECTRICAL node measures on the house's network, one entry per channel (up to 16: a circuit, a line, the grid input, a DC bus) with AC or DC, voltage, current, power (positive when it draws from the network), energy, frequency, power factor, the state of a switch it sees (`closed`, `open`, `unknown`), an alarm and its code, and whether the node is allowed to switch at all. It carries a state, never a command. Schema, 30 conformance vectors (177 in all), the generated TypeScript and Kotlin types, the Python validator (`validate_electrical_message`: the topic, the schema and a channel id once) and OpenAPI for `POST` and `GET /api/v1/electrical/readings` and `GET /api/v1/electrical/history`.

## [0.2.1] - The project tool runs the tests of both boards

- `armor_project_tool.py` also builds and runs the board-profile tests of ARMOR-NODE-RADAR (`test_board_wifi`) and ARMOR-NODE-SOLAR (`test_board_eth`). No change to the messages, the schemas or the vectors.

## [0.2.0] - Declaring solar equipment

- **OpenAPI 0.2.0:** `POST /api/v1/solar/devices` (declare an inverter or a battery stack: name, model, connection, gateway node), `DELETE /api/v1/solar/devices/{node}/{device}` and `POST /api/v1/solar/devices/{node}/{device}/example` (one made-up reading, marked as an example); `GET /api/v1/solar` also lists the declared devices that have not reported yet and the catalogue of models and connections. The file is renamed `armor-server-0.2.0.yaml`. No schema changed.
- `armor_project_tool.py` also tests ARMOR-NODE-SOLAR's node (settings, network plan, emulated UART, the exchange with stand-in equipment) and checks the messages its ports make against the contract. No change to the messages, the schemas or the vectors.

## [0.1.9] - The solar messages

- **Two new messages**, on their own topics `armor/solar/{node_id}/{device}/state`: `inverter` (a solar inverter of the Voltronic / MPP Solar family) and `battery` (a battery stack as Pylontech's console reports it, with each module's cell voltages and temperature sensors when the node reads them). Schemas, `validate_solar_message` and `parse_solar_topic` in Python, **74 new conformance vectors** (142 in all), TypeScript and Kotlin types, and the description in `docs/CONTRACTS.md`. No change to the radar messages.
- **OpenAPI 0.1.9**: `POST /api/v1/solar` (an ingest token), `GET /api/v1/solar` and `GET /api/v1/solar/history` (an operator); the file is renamed `armor-server-0.1.9.yaml`.
- The generator writes the types of an array of plain values (the list of warning names). Tests: 19.

## [0.1.8] - The shared project tool knows ARMOR-NODE-SOLAR

- `armor_project_tool.py` tests ARMOR-NODE-SOLAR (its protocol library and the messages its serialiser prints) and runs all three host tests of ARMOR-NODE-RADAR (it ran only one). No change to the messages, the schemas or the vectors.

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
