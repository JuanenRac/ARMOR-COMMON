# The ports of an installation

One numbering for every way of running A.R.M.O.R. (the CM5 installer and the Docker stack alike), written once in `src/armor_common/ports.json`:

| Service | Port | Used for |
|---|---|---|
| server | 18080 | the API and the ingest of ARMOR-SERVER |
| studio | 18081 | the web console (its proxy reaches the server) |
| mqtt | 18883 | the plain listener of the broker (never the standard 1883) |
| voice | 18090 | the gateway of the wall panel |
| mqtt_tls | 8883 | the optional encrypted door of the broker |
| https | 8443 | the optional TLS proxy of the Docker stack |
| acme_http | 8081 | the plain port of that proxy, for the check of a public certificate |

The Docker stack used 8080 (server), 8088 (Studio) and 1883 (broker) before. An installation that still has them keeps working until it is updated; `armor_doctor.py` names an old number it finds in the configuration, and the address that clients and nodes use has to follow (`http://<host>:18080`, `mqtt://<host>:18883`).

## What is generated from the registry

`python tools/generate_ports.py` writes `generated/armor-ports.ts`, `generated/ArmorPorts.kt`, `generated/armor_ports.hpp` and `generated/armor-ports.env`; `--check` (run by the tests) fails when one is out of date. `armor_common.ports` reads the same file from Python. The copy of the registry that the installer scripts carry (`ARMOR-DEVOPS/scripts/ports.json`) must equal it, and `tests/test_ports.py` fails when a file of any repository next to this one still uses an old number outside the list `scan.allowed` of the registry (each entry says why).
