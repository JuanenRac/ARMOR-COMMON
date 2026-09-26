# The firmware the node projects share

ARMOR-RADAR, ARMOR-SOLAR and ARMOR-ELECTRICAL grew from one base: the network (Ethernet and Wi-Fi), the settings and users kept in flash, the web panel's server and its
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
2. Run `sync`: the file is written into ARMOR-RADAR, ARMOR-SOLAR and ARMOR-ELECTRICAL (or the two or one that use it), each with its own name, keeping the line endings of the
   checkout.
3. Build and test each project as usual.

If a change was made in a project's copy by mistake, `check` says so and `sync` puts the base back. If it was meant (a fix found in one project), copy it into the base and
`sync`, or run `import`, which takes what is identical in two or more projects as the base.

## What is shared and what is not

`status` lists it. A file is shared by exactly the projects whose copies are identical once the name is turned into placeholders: the Ethernet driver, the entropy, the log, the
certificate, the settings store, the network, the Bluetooth channel and its framing, the login and the URL and address rules, the panel's page and the panel's build are shared;
what a project says in its own words is not: its settings, its panel's routes and pages (`web_server.cpp`, `api_shared`), its pins and its build profile, and, in ARMOR-RADAR, the
parts of the network and the broker link that only a radar node has (`mqtt_link` is shared by ARMOR-SOLAR and ARMOR-ELECTRICAL only).

## Limits

* The base is only as good as the projects' tests: a change to a shared file is tested by each project's host tests and built in each project's container, as any change.
* The tool never builds anything and never touches a file that is not in the base.
* The three projects have to be checked out next to ARMOR-COMMON (they are, for every other check of the family).
