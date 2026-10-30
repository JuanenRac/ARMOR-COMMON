# The firmware the node projects share

ARMOR-NODE-RADAR, ARMOR-NODE-SOLAR and ARMOR-NODE-ELECTRICAL grew from one base: the network (Ethernet and Wi-Fi), the settings and users kept in flash, the web panel's server and its
login, the certificate of the HTTPS panel, the log, the source of randomness, the Bluetooth channel, the small JSON reader, the panel's page and its build. A fix made in
one project used to have to be made in the other two by hand, and the copies drifted.

`firmware_base/` keeps **each shared file once**, with the name of the project written as placeholders, and `tools/sync_firmware_base.py` writes it into every project that
uses it. Nothing is shared at build time: each project keeps its own copy in its own tree and builds exactly as before (ESP-IDF, in its own container, from its own
folder). The tool only keeps the copies equal.

## The four commands

```bash
python tools/sync_firmware_base.py status    # which file goes to which project, and which files are each project's own
python tools/sync_firmware_base.py check     # exit 1 when a copy differs from the base (ARMOR-DOCS/tools/check_all.sh runs it)
python tools/sync_firmware_base.py sync      # write the base into every project that uses each file
python tools/sync_firmware_base.py import    # (re)make the base from the projects' files as they are now
```

## How to change a shared file

1. Edit it in `firmware_base/` (write the project's name as `@PROJECT@`, `@project-@`, `@project_@` or `@kind@`: see the top of the tool).
2. Run `sync`: the file is written into ARMOR-NODE-RADAR, ARMOR-NODE-SOLAR and ARMOR-NODE-ELECTRICAL (or the two or one that use it), each with its own name, keeping the line endings of the
   checkout.
3. Build and test each project as usual.

If a change was made in a project's copy by mistake, `check` says so and `sync` puts the base back. If it was meant (a fix found in one project), copy it into the base and
`sync`, or run `import`, which takes what is identical in two or more projects as the base.

## What is shared and what is not

`status` lists it. A file is shared by exactly the projects whose copies are identical once the name is turned into placeholders: the Ethernet driver, the entropy, the log, the
certificate, the settings store, the network, the Bluetooth channel and its framing, the login and the URL and address rules, the panel's page and the panel's build are shared;
what a project says in its own words is not: its settings, its panel's routes and pages (`web_server.cpp`, `api_shared`), its pins and its build profile, and, in ARMOR-NODE-RADAR, the
parts of the network and the broker link that only a radar node has (`mqtt_link` is shared by ARMOR-NODE-SOLAR and ARMOR-NODE-ELECTRICAL only).

## The test against a real broker

`tests/check_mosquitto.py` is shared with the five projects. It starts Mosquitto on a free port of the loopback address with the account rules of a node, plays the MQTT client of the node
(esp-mqtt: client id, retained birth and last will, QoS 1, its own order topic) with a small codec, and checks that what the node's serialiser prints (`emit_samples`) reaches the server
on the right topic, that an order reaches the node, that the node cannot write on another node's topics and that the retained last will arrives when the connection dies. Where Mosquitto is
not installed it says so and passes; the shared workflow installs it in the node repositories and sets `ARMOR_REQUIRE_MOSQUITTO`, so there a missing broker is a failure. `tests/test_check_mosquitto.py`
of this repository tries the script against a stand-in broker.

## Limits

* The base is only as good as the projects' tests: a change to a shared file is tested by each project's host tests and built in each project's container, as any change.
* The tool never builds anything and never touches a file that is not in the base.
* The three projects have to be checked out next to ARMOR-COMMON (they are, for every other check of the family).

## Files that are not shared with every node

`main/zigbee_bridge.cpp` and `main/zigbee_bridge.hpp` are listed for ARMOR-NODE-ELECTRICAL only: ARMOR-NODE-ALARM keeps its own copy, which takes a hook for the node itself to speak Zigbee while the radio is its own (see ARMOR-NODE-ALARM's `docs/FAILOVER.md`). `core/zigbee_bridge.hpp` (who may connect, the arbiter, the reset sequence) is still shared by both.

## The health report

`core/node_health.hpp`, `main/node_health.hpp` and `main/node_health.cpp` are shared by the five nodes: the report every node publishes to `armor/health/<node>` (the `node_health` contract). `core/node_health.hpp` holds what is decided without hardware - the words of the ESP-IDF reset reasons, which link the node is on, the last error of the log, the JSON of the report - and is tested in `tests/test_base.cpp`; `main/node_health.cpp` reads the real values (heap, uptime, reset reason, the network status, the log) and sends the message about once a minute. `mqtt_link.cpp` counts the connections to the broker for it (ARMOR-NODE-RADAR's own `mqtt_link.cpp` too). Each node calls `node_health::start` from its `app_main.cpp` and lists `node_health.cpp` in its `main/CMakeLists.txt`. It has not run on a board.

`core/memory_budget.hpp`, `main/psram_mem.hpp` and `main/psram_mem.cpp` are shared by the five nodes: where the memory goes. A node has two kinds, the internal one (about 300 KB, shared by the radio, the drivers and every task stack) and 8 MB of external RAM (PSRAM) that nothing may touch while the flash is being written. `core/memory_budget.hpp` decides without hardware - when the internal memory is low (under 40 KB, back to normal over 48 KB, or no free block of 8 KB), where a big buffer or a task stack goes and whether that was a fallback, when the log says it (every minute, and at once when the state changes) - and is tested in `tests/test_base.cpp`. `main/psram_mem.cpp` reads the real heap and acts: `install_tls_allocator` (first thing in `app_main`: mbedTLS takes the external RAM and falls back to the internal memory where a board has none, which the stock "external" mode of ESP-IDF does not), `snapshot`, `allocate`/`release` for a long-lived buffer that only the CPU touches, `start_task` for a task whose stack may live in the external RAM, and `start_monitor`, the task that writes the line `memory: internal ... KB free (least ..., biggest block ...), PSRAM ...` in the log every minute. A task may use `start_task` only if it runs for ever and touches no flash at all (no NVS - not even a read -, no partition, no update, no restart of its own) and owns no DMA buffer on its stack; the update check, the broker link's sender and watchdog, the health report and the radar map qualify, the radio, the network, the settings, the update itself and the equipment's own tasks do not. The sdkconfig sends a request of up to 4096 bytes to the internal memory first and a bigger one to the external RAM first (`CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL`), and keeps 32 KB of the internal memory for what must be there. The health report carries the internal memory on its own (`heap_internal_*`, `psram_free`), because `heap_free` adds the external RAM and so never looks short. None of it has run on a board.

## Self-protection (memory, Bluetooth window, guard, gate)

`core/node_guard.hpp` and `core/ble_window.hpp` hold, as pure functions tested in `tests/test_base.cpp`, the rules by which a node protects itself: the watchdog over the tasks it needs and its internal memory (one clean restart after a minute of trouble, never more than three an hour of running time, the count kept in memory that survives a software reset), the gate that refuses new panel connections while the internal memory is short, the handler of a failed allocation (restart with a record, abort during a firmware write or when repeated within a minute), the dead-man switch (ten minutes without a message to a connected broker), and the window that closes Bluetooth set-up. `main/node_guard.cpp` reads the real values; `main/psram_mem.cpp` starts it first thing. `tools/check_sdkconfig.py` compares a build's generated `sdkconfig` with `sdkconfig.defaults` (a cached build directory keeps the old value of a line added later: delete it and build again). Every node registers the tasks it cannot do without with `nodeguard::expect_task` right before it makes them, and the web servers of the five nodes use `nodeguard::http_open_gate` as their `open_fn`. See `docs/NODE_FIRMWARE.md` of any node for what each rule does and its starting values. It has not run on a board.

## Diagnostics

`core/boot_report.hpp`, `core/config_snapshot.hpp`, `core/diag_package.hpp`, `main/node_diag.hpp`, `main/node_diag.cpp` and `tests/test_diag.cpp` are shared by the five nodes: the report of a dirty start (`boot` of the health report, from the reset reason of the chip, what the guard writes in memory that survives a software reset every two seconds and the record of an out-of-memory), the copy of the settings made right before an update and the check fifteen seconds after a start, the core dump in flash (the check, the summary, the download for an administrator of the panel and the erase) and the diagnostic package (the allow-list of settings, the washing of secrets, the bound on its size) that a `diagnostics` order with `detail` asks for. A node adds `node_diag.cpp` to its `main/CMakeLists.txt` and `espcoredump` to its `REQUIRES`, and its `sdkconfig.defaults` carries `CONFIG_ESP_COREDUMP_ENABLE_TO_FLASH=y`, `CONFIG_ESP_COREDUMP_DATA_FORMAT_ELF=y`, `CONFIG_ESP_COREDUMP_CHECKSUM_CRC32=y` and `CONFIG_ESP_COREDUMP_MAX_TASKS_NUM=32` (`tools/check_sdkconfig.py` checks the generated file). The `coredump` partition is 128 KB in the shared `partitions.csv` (and in the radar's and the touch panel's own tables; the touch panel's storage partition moved up by 64 KB); a board flashed by cable with the older 64 KB table keeps it, because an update over the air does not rewrite the partition table. A node with its own copy of `main/node_store.cpp` (the radar) carries the same changes by hand. The test builds a package from settings full of passwords, keys and names of the house and looks for each one in the answer. None of it has run on a board.

## Control from the server

`core/control_gate.hpp`, `main/node_control.hpp`, `main/node_control.cpp` and `tests/test_control.cpp` are shared by the five nodes: the typed orders the server can give a node (the `node_control_command` and `node_control_result` contracts). `core/control_gate.hpp` holds what is decided without hardware - the strict reading of an order, the one-time token bound to its operation (thirty seconds, one use, replay and a wrong operation refused), the refusals (busy installing, uploading, copying a slot or running a battery operation; too soon; already in that state), the state machine (running, paused with its timer, standby kept across restarts, the maintenance flag, the identify window), the rolling schedule of restarts and the JSON of every answer - and is tested in `tests/test_control.cpp` against the shared vectors. `main/node_control.cpp` subscribes to the node's own topic and to the topic of every node, keeps the standby in flash (loaded before the node's work starts), runs a one-second task for the timers and calls the node's hooks (`busy`, `on_state`, `identify`, `diagnostics_extra`); `node_control::working()` is what a node asks before it does its work. `main/node_health.cpp` adds the state to the health report. `main/relay_outputs.cpp` has `hold_open`, which opens every relay and keeps them still while the work is off (the electrical and the alarm node). There is no order that erases the settings, none for deep sleep and none that sets a wake timer. It has not run on a board. The planned-maintenance signal (`MaintenanceSignal`, `maintenance_json`, `follow_order`, `follow_tick`) is there too: the node publishes `armor/control/<node>/maintenance` retained (through `mqtt_link::publish_retained`) before it goes quiet and clears it when it is back, and the firmware update, the slot copy and the panel upload call `node_control::announce_maintenance` / `announce_maintenance_done` (a no-op when the server does not control the node). The guard of the previous section and this module work together: the guard does not count a missing task while the node is paused, in standby or on its way to a restart that was ordered (`node_control::working()`, `node_control::restart_pending()`; the memory rules stay in force), an ordered restart marks the memory that survives a software reset (`nodeguard::note_deliberate_restart`) so that the next start says it was not the guard's and it is not in the guard's ledger, and the standby kept in flash is loaded before the node's work starts, so it survives a restart of the guard.
