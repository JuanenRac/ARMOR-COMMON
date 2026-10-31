<p align="center">
  <img src="images/ARMOR_BANNER.svg" alt="ARMOR-COMMON banner" width="100%">
</p>

# 🧾 ARMOR-COMMON

<p align="center">
  🇺🇸 <b>English</b> |
  <a href="README_spa.md">🇪🇸 Español</a> |
  <a href="README_fra.md">🇫🇷 Français</a> |
  <a href="README_ita.md">🇮🇹 Italiano</a> |
  <a href="README_deu.md">🇩🇪 Deutsch</a> |
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a> |
  <a href="README_por.md">🇵🇹 Português</a>
</p>

### Message contracts, validation, the firmware base that the nodes share and the shared project launcher

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.11%2B-3776ab.svg" alt="Language">
  <img src="https://img.shields.io/badge/Dependencies-none-2ea44f.svg" alt="Dependencies">
  <img src="https://img.shields.io/badge/Vectors-1270-00E5FF.svg" alt="Vectors">
  <img src="https://img.shields.io/badge/Tests-237%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.7.9-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

**Honesty check - what runs today:** The schemas (telemetry, health, command, node information, solar inverter and battery, electrical, alarm with its command and result, and network), the Python validator, the 1270 conformance vectors, the generated TypeScript and Kotlin types, the OpenAPI file of the server (195 paths), the firmware base shared by the five nodes and the shared project launcher are real and tested (237 tests). The Kotlin file is generated but **not yet consumed** by ARMOR-ANDROID-CONTROL (which keeps its own parsing), and the `set_thresholds` command carries a single `sensitivity` field because the real radar parameters are not defined until firmware exists.

---

## 📋 At a glance

| | |
|---|---|
| Version | `0.7.9` |
| Maturity | Established |
| Role | Shared contracts, validator and firmware base of the family |
| Stack | Python 3.11+, JSON Schema, OpenAPI; C++ firmware base (ESP-IDF) |
| Tests | 237 (`python -m unittest discover -s tests`), 1270 conformance vectors |
| Contract | 35 JSON Schemas, 196 HTTP paths (255 operations) |
| Runs on | Any computer (library and tools); the firmware base runs inside the five nodes |
| On real hardware | Only the radar node has run the shared firmware on a board; the other four have not |
| License | GPL-3.0-or-later |

**Jump to:** [Overview](#-overview) · [Architecture](#-architecture) · [Features](#-features) · [Security](#-security--safety) · [Interfaces](#-interfaces) · [Configuration](#-configuration) · [Quick start](#-quick-start) · [Testing](#-testing) · [Troubleshooting](#-troubleshooting) · [Structure](#-repository-structure) · [Related](#-related-projects)

## 🚦 Project status

Each line is one part of this repository and the light says how far it is today. It is written from what the repository can show (tests, builds, runs), not from what is planned.

🟢 Done and verified · 🟡 Works, with known limits · 🟠 Partly done or not verified yet · 🔴 Not done or not working

| Area | State | What it means here |
|---|---|---|
| Software | 🟢 | The schemas, the Python validator, the generated TypeScript and Kotlin types, the OpenAPI file of the server and the firmware base shared by the five nodes are in place. |
| Tests | 🟢 | 237 tests and 1270 conformance vectors pass; the JSON, Bluetooth and Improv parsers of the firmware are also fuzzed with libFuzzer. |
| Protocols and data | 🟡 | Only the radar node's messages are used every day with a real board and the server; those of the other nodes are checked against stand-ins. |
| Integration | 🟡 | The firmware base is checked to be identical in every node; the Kotlin types are generated but not yet used by the Android app, which keeps its own parsing. |
| Hardware | 🟠 | Only the radar node has run this shared firmware on a board; the other four nodes have not. |
| Security | 🟡 | The firmware signature check and the derivation of the Bluetooth PIN are tested on the host; there has been no independent review. |
| Documentation | 🟢 | Eight languages, the OpenAPI file, the conformance guide and the changelog are up to date. |

## 🎯 Overview

**ARMOR-COMMON** owns what every A.R.M.O.R. message means. Radar nodes, solar gateway nodes and the simulator produce these messages; the server, the visual AI and the voice service consume them. If two projects disagree about a field, this repository decides.

* **One source of truth:** JSON Schemas in `src/armor_common/schemas/` for telemetry, health, command, node information, the two solar messages (inverter, battery with cells and capacities), the electrical messages (readings, command, result), the alarm messages (state, command, result) and the network message. Unknown fields and impossible combinations are refused.
* **A validator that cannot skip a rule:** it interprets the schema directly and refuses a schema that uses a keyword it does not implement.
* **Conformance vectors:** 1270 accepted and rejected payloads run by every implementation (Python here, TypeScript in ARMOR-SERVER, the checks of the firmware repositories), so drift fails a build.
* **Generated clients:** TypeScript and Kotlin types come from the schemas (`tools/generate_types.py --check` keeps them current).
* **HTTP contract:** `openapi/armor-server.yaml` describes every server route (195 paths, 253 operations), its access rule, and a named schema for every request body, answer and error, and a test checks that the routes the server registers are exactly the ones it describes (method and path).
* **Firmware base:** `firmware_base/` keeps each file the five nodes share (network, settings and users, web panel server and login, HTTPS certificate, log, Bluetooth with PIN pairing, signed-update check; relays and Zigbee for the nodes that have them) once; `tools/sync_firmware_base.py` writes it into every node and checks that no copy drifted ([the guide](docs/FIRMWARE_BASE.md), [signed firmware](docs/SIGNED_FIRMWARE.md)).
* **Shared launcher:** `tools/armor_project_tool.py` gives every repository of the family the same `build`, `build-test` and `run` workflow, and `tools/armor_ci_validate.py` the same CI checks.
* **Optional TLS link to the broker in the shared node base:** `firmware_base` carries the `mqtt.tls` switch and the `mqtt.ca_pem` text (one PEM certificate, at most 2 KB, validated), the connection that trusts that authority only and checks the broker's name, and the host tests shared by the five nodes; off by default.
* **Node health and arming profiles:** the `node_health` message (the same report from a radar, a solar, an electrical, an alarm or a wall-panel node) and the `arm_profile` (a named way of arming: which zones guard, the delays, the siren and how loudly the server tells people, carried inside the arm command) have their schemas, conformance vectors, generated TypeScript and Kotlin types, OpenAPI routes and the shared firmware code that builds the report.
* **Arming modes:** the schema `arming_modes` (away, home and night: what each defends, the exit and entry delays and an optional timetable), its 42 conformance vectors, the rule validator, the generated TypeScript and Kotlin types and the OpenAPI routes `GET` and `PUT /api/v1/alarm/modes`, the modes of `POST /api/v1/mode` and the four settings that switch it all on (off by default).
* **Connection and system events of the history:** the schemas `connection_event`, `system_event` and `connection_client` (what the server's history says about the clients that connect and about the system itself, with a fixed vocabulary and no field where a secret could go), their conformance vectors, the generated TypeScript and Kotlin types and the OpenAPI route that lists the clients.
* **Diagnostics and reading quality in the contract:** the dirty-boot report, the core dump, the settings safety check, the diagnostic package, the radar events and the read-only diagnostic token messages have their schemas, conformance vectors and generated types; a meter channel may carry the age of its reading and its error count, and an inverter message may name the values the node held at a limit.

## 🧩 Role in A.R.M.O.R.

ARMOR-COMMON is what keeps the family speaking the same language. Every message between a node and [ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER) is defined here once, with the vectors that every implementation must pass; the server's HTTP contract lives here too; and the firmware that the five nodes share ([ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR), [ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR), [ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL), [ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM), [ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)) is kept once and copied into them by a tool. It holds no secret and runs nothing in production.

| It talks to | How | What for |
|---|---|---|
| ARMOR-SERVER | runs the vectors; implements every OpenAPI route | vectors, OpenAPI |
| ARMOR-STUDIO | keeps a copy of the generated types; a test fails on drift | generated TypeScript |
| ARMOR-ANDROID-CONTROL | has its own parsing; the Kotlin types are generated, not used | generated Kotlin |
| ARMOR-NODE-RADAR, SOLAR, ELECTRICAL, ALARM, HMI | receive firmware_base by `tools/sync_firmware_base.py` | copied firmware |
| ARMOR-DOCS, ARMOR-DEVOPS, ARMOR-UPDATER | read `registry/repositories.json`, the one list of repositories | the registry |

## 🏛️ Architecture

<p align="center">
  <img src="images/architecture.svg" alt="ARMOR-COMMON architecture: who uses it, what the repository owns (schemas, vectors, validator, generated types, OpenAPI, firmware base) and who receives it" width="100%">
</p>

<details>
<summary>Text version of the diagram (Mermaid)</summary>

```mermaid
flowchart LR
    S["JSON Schemas (source of truth)"] --> P["armor_common (Python validator)"]
    S --> G["generated TS + Kotlin types"]
    S --> V["conformance vectors"]
    V --> P
    V --> T["ARMOR-SERVER tests"]
    V --> X["ARMOR-NODE-SOLAR and ARMOR-NODE-ELECTRICAL checks"]
    S --> O["OpenAPI (HTTP contract)"]
```

</details>

## ✨ Features

### Adding or changing a message

1. Edit the schema in `src/armor_common/schemas/` (and `docs/CONTRACTS.md` if the meaning changes).
2. Add the cases to the list and run `python tools/make_conformance.py`.
3. Run `python tools/generate_types.py` and `python tools/generate_rest_types.py` to refresh the TypeScript and Kotlin types.
4. Update `openapi/armor-server.yaml` when a route is involved; `tests/test_openapi.py` compares it with the routes of the server.
5. The server and the nodes then run the same vectors, so a disagreement fails a build.

### The firmware base

`firmware_base/` keeps once every file the five nodes share: network, settings and users, the web panel server and its login, the HTTPS certificate, the log, Bluetooth with PIN pairing, the check of a signed update, the report of node health, the guard that restarts a node in trouble, the typed orders of the server and, for the nodes that have them, relays and Zigbee. `tools/sync_firmware_base.py` writes it into every node and checks that no copy drifted (see [docs/FIRMWARE_BASE.md](docs/FIRMWARE_BASE.md) and [docs/SIGNED_FIRMWARE.md](docs/SIGNED_FIRMWARE.md)). Its decisions that need no hardware live in `core/` and are tested on a computer; `main/` reads the real values.

## 🔒 Security & Safety

| Threat | Defence |
|---|---|
| An unknown field or an impossible combination | `additionalProperties: false`; the validator interprets the schema and refuses to load one that uses a keyword it does not implement |
| Telemetry without a limit to exhaust a node | At most 15 tracks (5 for each of 3 sensors) and lux 0 to 200 000 |
| A command outside the list | Allow-list: `calibrate`, `set_thresholds` (sensitivity 1 to 10), `restart`; the subscriber rejects the rest before the hardware |
| A topic that does not match the node id of the body | The consumer rejects the mismatch |
| A fake firmware on GitHub | The image must match its `.sha256` and carry an Ed25519 signature of that hash, checked with the public key built into `firmware_base/core/fw_trust.hpp`; without it nothing changes |
| The private release key leaks | It lives outside every repository, CI and release (PKCS#8, mode 0600); `release_firmware.py` refuses to publish when the key is not the one the firmware trusts |
| Node passwords and the Bluetooth PIN | Passwords: PBKDF2-HMAC-SHA256, 10 000 rounds. PIN: derived from the MAC and the fleet secret (`CONFIG_ARMOR_FLEET_SECRET`, empty in public firmware) |
| Exposed parsers (JSON, Bluetooth frames, Improv) | Fuzzed with libFuzzer, AddressSanitizer and UndefinedBehaviorSanitizer (`fuzz/run_fuzz.sh`, Linux with clang) |
| A node copy drifts from the shared one | `tools/sync_firmware_base.py check` fails if the five nodes are not identical |

**What it does not cover.** A firmware uploaded by hand by an administrator is not checked. A node with a firmware older than this check installs the first signed release by its hash alone. The key protects releases, not boards: with physical access anyone can flash anything. If the key is lost, the GitHub updater is blocked until the public key is replaced by a manual upload or by cable. The signature check and the PIN are tested on the host; there has been no independent review. More in [docs/SIGNED_FIRMWARE.md](docs/SIGNED_FIRMWARE.md).

## 🔌 Interfaces

### Broker topics

| Topic | What it carries |
|---|---|
| `armor/node/{node_id}/telemetry`  `health`  `command`  `info` | a radar node: tracks, health, commands and information |
| `armor/solar/{node_id}/{device}/state` | an inverter or a battery of a solar node |
| `armor/electrical/{node_id}/state`  `command`  `result` | the electrical node: readings, command, result |
| `armor/alarm/{node_id}/state`  `command`  `result` | the alarm node (also `zigbee` and `policy` from the server) |
| `armor/network/{node_id}/state` | what a node sees on the network |
| `armor/health/{node_id}` | the health report of any node, and its last will |
| `armor/control/{node_id}/command`  `result`  `maintenance`  and `armor/control/all/command` | typed orders to one node or to all, their result and the planned-maintenance signal |
| `armor/device/{node_id}/{relay}/set`  `state`  `availability` | a relay of a node |
| `armor/radar/{node_id}/events`  and  `armor/server/alert` | radar events; alerts the server sends to the panels |

### Schemas, vectors and OpenAPI

* **35 JSON Schemas** in `src/armor_common/schemas/`: telemetry, health, command, node information, node health, node control (command and result), node maintenance, solar inverter and battery (with their commands and results), electrical (with command and result), alarm (state, command, result, policy and zone feed), network (with its orders), connection and system events, radar events, server alert, arming profile, arming modes, device state, diagnostic tokens, and the voice turn.
* **1270 conformance vectors** in `conformance/` (35 files, one per message), run by this repository, by ARMOR-SERVER and by the checks of the firmware repositories.
* **OpenAPI** `openapi/armor-server.yaml`: 196 paths and 255 operations, each with its access rule and a named schema for every body, answer and error. A test checks that the routes the server registers are exactly the ones described. The voice turn travels as bytes (see [docs/CONTRACTS.md](docs/CONTRACTS.md)).

### Command-line tools

| Tool | What it does |
|---|---|
| `tools/armor_project_tool.py` | the shared `build`, `build-test` and `run` workflow |
| `tools/generate_types.py [--check]`  `generate_rest_types.py [--check]` | TypeScript and Kotlin types, and the types of the HTTP contract |
| `tools/make_conformance.py [--check]` | writes the conformance vectors from the case list |
| `tools/sync_firmware_base.py` (`check`, `sync`, `import`) | writes `firmware_base` into the five nodes, or checks they have not drifted |
| `tools/release_firmware.py`  `tools/firmware_sign.mjs` | signs and publishes a firmware release |
| `tools/voice_cases.py` | the voice cases shared with ARMOR-VOICE-AI |
| `tools/make_architecture.py`  `tools/make_structure.py`  `tools/universal_readme_check.py` | the pictures and the layout check of the READMEs |

## ⚙️ Configuration

### Firmware build options (Kconfig)

| Setting | Default | What it does |
|---|---|---|
| `CONFIG_ARMOR_NODE_ID` | "" | the node's name on the broker |
| `CONFIG_ARMOR_SETUP_CODE` | "" | the code that opens set-up |
| `CONFIG_ARMOR_FLEET_SECRET` | "" | fleet secret for the Bluetooth PIN; empty in public firmware |
| `CONFIG_ARMOR_BLE_SETUP_MINUTES` | 10 (1 to 120) | how long Bluetooth set-up stays open |
| `CONFIG_ARMOR_ETH_SPI_HOST` | 1 (1 to 2) | SPI host of the Ethernet chip |
| `CONFIG_ARMOR_ETH_MOSI` `MISO` `SCLK` `CS` `INT` `RST` | 11, 12, 13, 14, 10, 9 | pins of the Ethernet board (profile `s3-eth`) |
| `CONFIG_ARMOR_ETH_SPI_MHZ` | 20 (1 to 40) | SPI clock of the Ethernet chip |
| `CONFIG_ARMOR_MQTT_URI` `USERNAME` `PASSWORD` | "" | first broker address and credentials |
| `CONFIG_ARMOR_BOOT_FACTORY_RESET` | y | allows the factory reset at boot |
| `CONFIG_ARMOR_NTP_SERVER` | pool.ntp.org | time server |
| `CONFIG_ARMOR_HEARTBEAT_S` | 10 (2 to 300) | seconds between heartbeats |
| `CONFIG_ARMOR_BOARD_S3_WIFI`  `CONFIG_ARMOR_BOARD_S3_ETH` | S3_WIFI | the board profile of the image (`tools/build_node.sh NODE BOARD`) |

The node's own TLS link to the broker is a setting of the node (not of the build): `mqtt.tls` (off by default) and `mqtt.ca_pem` (one PEM certificate, at most 2 KB, validated); the connection trusts that authority only and checks the broker's name. The Python library has no environment variables of its own; the shared launcher creates an ignored `.env` on the first ARMOR-SERVER run with random secrets and a random administrator password, and prints and commits nothing.

## 🚀 Quick start

**Requirements:** Python 3.11+ (no other package). To check the firmware base the five node repositories must be next to this one.

```powershell
python -m pip install -e .                   # install the library
python -m unittest discover -s tests         # 237 tests, 1270 conformance vectors
python tools/generate_types.py --check       # the generated types are current
python tools/generate_rest_types.py --check  # the types of the HTTP contract are current
python tools/make_conformance.py             # regenerate the vectors after editing the case list (--check: they are current)
python tools/sync_firmware_base.py check     # the firmware the nodes share has not drifted
```

## 🧪 Testing

```powershell
python -m unittest discover -s tests  # 237 tests
python -I tools/armor_ci_validate.py
```

| Test file | Tests | What it covers |
|---|---|---|
| `test_contracts.py` | 68 | every message, topic and splitter, with the conformance vectors |
| `test_task_safety_check.py` | 23 | the scan that finds the tasks a node cannot do without |
| `test_universal_readme_check.py`, `test_readme_tools.py` | 36 | the layout check and the pictures of the READMEs |
| `test_firmware_base.py` | 13 | the shared firmware base and its sync |
| `test_openapi.py` | 13 | the OpenAPI file against the routes of the server |
| `test_release_firmware.py` | 12 | the signing and publication of firmware |
| `test_pretty_run.py`, `test_build_scripts.py` | 11 | the live panel of the scripts |
| `test_generated_types.py`, `test_repository_registry.py`, `test_voice_turn.py` | 21 | the generated types, the repository list and the voice turn |
| `test_alarm_codes.py`, `test_collect_errors.py`, `test_project_manifest_doc.py`, `test_firmware_fuzz.py`, `test_fuzz_validator.py` | 17 | alarm code words, error collection, the manifest guide and the fuzz harness |

The host tests of the shared firmware are in `firmware_base/tests/` (C++, no ESP-IDF needed) and run from the node repositories' own checks. `python tools/sync_firmware_base.py check` needs the five node repositories next to this one. GitHub Actions runs the A.R.M.O.R. baseline on every push and pull request: the validation of the manifest, version, changelog and README parity, then the project's own build and tests.

## 🏗️ Build & Release

It is plain Python and a set of tools: nothing to compile. The version lives in `pyproject.toml`, in `armor.project.json` and in the README badge (read from the manifest); each version has its entry in [CHANGELOG.md](CHANGELOG.md). Releases are published on GitHub. The firmware release tool (`tools/release_firmware.py`) signs and publishes the images of the nodes; the key it needs is never in a repository.

## 🩺 Troubleshooting

| You see | Because | Do |
|---|---|---|
| `FIRMWARE_BASE=FAIL ... copies drifted` | a node changed a shared file by hand | make the change in `firmware_base/` and run `sync`; or `import` to take the nodes' files as they are |
| `ARMOR-NODE-HMI: main/secret_vault.cpp is missing` | the node repositories are not next to ARMOR-COMMON | clone them side by side |
| `generated types are out of date` | a schema or the OpenAPI file changed | run `generate_types.py` and `generate_rest_types.py` without `--check` |
| `TASK_SAFETY=FAIL no task found: the scan is broken` | the scan of the node sources found nothing | check that the node repositories are next to this one |
| `no_signature`, `bad_signature`, `checksum_mismatch`, `wrong_firmware` | the node refused a release: missing or wrong signature, hash or board | publish with `tools/release_firmware.py` and the release key the firmware trusts |

## 📂 Repository Structure

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of ARMOR-COMMON" width="100%">
</p>

<details>
<summary>Text version of the tree</summary>

```text
ARMOR-COMMON/
├── src/armor_common/
│   ├── contracts.py               topics and validators
│   ├── schema.py                  the schema interpreter
│   ├── envelope.py                the common envelope
│   ├── voice.py                   the voice turn contract
│   ├── schemas/                   35 JSON Schemas
│   ├── alarm_codes.json           words of each alarm code
│   └── battery_ops.json           battery operations
├── firmware_base/                 the firmware that the five nodes share, once
├── conformance/                   1270 accepted and rejected payloads
├── generated/                     TypeScript and Kotlin types (generated, do not edit)
├── openapi/                       armor-server.yaml, HTTP contract
├── registry/                      repositories.json, the family list
├── fuzz/                          libFuzzer targets
├── scripts/                       armor-project launcher
├── tools/                         generators, firmware sync and release, launcher, CI checks
├── tests/                         237 tests
├── docs/                          contracts, firmware, fuzzing
├── images/                        banner, icon and the pictures of the README
├── .github/                       CI workflow, dashboard notice, issue and pull-request templates
├── armor.project.json             manifest: version, role, maturity
├── pyproject.toml                 package metadata, entry points
├── CHANGELOG.md                   what changed in each version
├── run.sh run.bat                 start, shared workflow
├── build.sh build.bat             build and test, shared workflow
├── build-test.sh build-test.bat   build, test and package
├── test.sh test.bat               only the tests, never the version
└── SECURITY.md SUPPORT.md CONTRIBUTING.md CODE_OF_CONDUCT.md LICENSE
```

</details>

## 🗺️ Roadmap & Known limits

**Known limits today**

* The Kotlin types are generated but **not yet used** by ARMOR-ANDROID-CONTROL, which keeps its own parsing.
* The `set_thresholds` command carries a single `sensitivity` field: the real radar parameters are not defined until the firmware exists.
* Only the radar node has run the shared firmware on a board; the other four nodes have not.
* No independent security review.

**Next**

* Let the Android app use the generated Kotlin types.
* Define the real radar parameters of `set_thresholds`.
* Run the shared firmware on the boards of the other four nodes.

## 🌍 Languages

README and texts exist in English, Spanish, French, Italian, German, Chinese, Japanese and European Portuguese.

## 🔗 Related Projects

**A.R.M.O.R.** (Autonomous Radar & Multimodal Observation Range) is a perimeter-security system made of independent repositories. Each one has its own version, its own tests and its own README; this is the family:

* **ARMOR-COMMON** (this repository) - Message contracts, validators, conformance vectors and generated types
* **[ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR)** - Field-node firmware for ESP32-S3 with three radars and its own web panel
* **[ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR)** - Solar inverter and battery protocols and the messages of a gateway node
* **[ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL)** - Electrical node: meters, the message of the network's readings and the rules for switching
* **[ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM)** - Alarm node and panel: zones, arming, delays, siren and PIN, with the server or without it
* **[ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)** - Touch panel: the state of the system on a wall screen, arming and acknowledging, and the home of the voice assistant
* **[ARMOR-NETWORK](https://github.com/JuanenRac/ARMOR-NETWORK)** - The local network: its devices, the internet and what changes
* **[ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER)** - Central coordinator: telemetry, alarms, devices, solar readings and cameras
* **[ARMOR-STUDIO](https://github.com/JuanenRac/ARMOR-STUDIO)** - Web console: cameras, radar, alarms, solar energy and the 2D/3D site designer
* **[ARMOR-ANDROID-CONTROL](https://github.com/JuanenRac/ARMOR-ANDROID-CONTROL)** - Android operator client with a live 2D/3D radar
* **[ARMOR-IOS-CONTROL](https://github.com/JuanenRac/ARMOR-IOS-CONTROL)** - iPhone operator client
* **[ARMOR-SERVER-AI](https://github.com/JuanenRac/ARMOR-SERVER-AI)** - Visual inference policy that explains its decisions and never actuates
* **[ARMOR-VISION](https://github.com/JuanenRac/ARMOR-VISION)** - Camera zones, masks and detection rules for the Jetson Orin NX
* **[ARMOR-VOICE-AI](https://github.com/JuanenRac/ARMOR-VOICE-AI)** - Offline voice intents with a confirmation that cannot be forged
* **[ARMOR-HARDWARE](https://github.com/JuanenRac/ARMOR-HARDWARE)** - Enclosures, electronics and the bench acceptance matrix
* **[ARMOR-DEVOPS](https://github.com/JuanenRac/ARMOR-DEVOPS)** - Deployment, the CM5 test bench, backup and TLS
* **[ARMOR-SIMULATOR](https://github.com/JuanenRac/ARMOR-SIMULATOR)** - Offline telemetry simulator with repeatable faults
* **[ARMOR-UPDATER](https://github.com/JuanenRac/ARMOR-UPDATER)** - Detects, installs and updates the ecosystem's own repositories
* **[ARMOR-DOCS](https://github.com/JuanenRac/ARMOR-DOCS)** - Architecture, security baseline and the capability matrix

## 📚 Documentation

* [Contracts](docs/CONTRACTS.md): every message, topic and the way to change a contract
* [Firmware base](docs/FIRMWARE_BASE.md): what the five nodes share and how it is synced
* [Signed firmware](docs/SIGNED_FIRMWARE.md): the signature of releases and what it does not cover
* [Fuzzing](docs/FUZZING.md): the three parser targets and how to run them
* [Project manifest](docs/PROJECT_MANIFEST.md): the `armor.project.json` every repository carries
* [The pictures of the READMEs](docs/README_PICTURES.md): how Architecture and Repository Structure are drawn
* [Capability matrix: what is proven and what is not](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/CAPABILITY_MATRIX.md)
* [Project catalogue: versions and how the repositories depend on each other](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/PROJECT_CATALOG.md)
* [Changelog of this repository](CHANGELOG.md)

## 🤝 Contributing & Community

* Before a pull request run `python -I tools/armor_ci_validate.py` and the tests: both must pass. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [code of conduct](CODE_OF_CONDUCT.md).
* The README exists in eight languages and is generated from the sources in ARMOR-DOCS: a change to the text is made there.
* A change to a message between components starts in ARMOR-COMMON.
* Do not describe as working on a board what has only been built.
* Report a vulnerability privately: [SECURITY.md](SECURITY.md). Questions, ideas and reports: electrohobby3d@gmail.com ([SUPPORT.md](SUPPORT.md)).

## 👤 AUTHOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENSE

GPL-3.0-or-later - see [LICENSE](LICENSE).
