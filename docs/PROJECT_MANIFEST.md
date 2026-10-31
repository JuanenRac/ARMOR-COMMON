# The project manifest: `armor.project.json`

Every A.R.M.O.R. repository carries one `armor.project.json` at its root. It is plain JSON, public metadata only (never a secret, a machine path or a credential), and it is what a
tool reads to discover a project: the updater, the dashboard and the CI checks of each repository all start from it.

The checks that every repository runs (`tools/armor_ci_validate.py`) require the keys below and compare the version with the changelog, the README files and the package files. A
key that is not listed here is ignored by those checks, but the updater rejects a manifest with a key it does not know, so a new key is added to this page and to the updater at the
same time.

## Required keys

| Key | Type | Meaning |
|---|---|---|
| `schema_version` | string | Always `"1.0"`. |
| `ecosystem` | string | Always `"A.R.M.O.R."`. A repository that does not say so is not part of the family. |
| `name` | string | The name of the repository. |
| `version` | string | The version of the project: `MAJOR.MINOR.PATCH` up to `0.7.9`, `MAJOR.MINOR.PATCH.BUILD` from `0.8.0`. |
| `native_version` | string | The version the build files carry. Always equal to `version`. |
| `role` | string | What the project is, in a sentence. |
| `stack` | string | The languages and platforms it is written for. |
| `technologies` | array of strings | Non-empty, no repeated item. |
| `deployment_target` | string | Where it runs, in words. |
| `maturity` | string | `scaffolding`, `functional`, `established` or `production`. |
| `family` | string | The group the project is listed with. |
| `parent` | string or `null` | The project this one is a part of, or `null`. |
| `build` | string | The command that builds and tests it. |
| `notes` | string | What really works and what does not. |

## Optional keys

### `requires`

```json
"requires": ["ARMOR-COMMON", "ARMOR-SERVER"]
```

An array of project names (repository names) that must be **installed, and built, before this project**. Leave it out when there is nothing to list: a manifest without `requires`
means exactly what it meant before the field existed.

* The names are unique, written like a repository name (letters, digits, `.`, `_`, `-`), and never the project itself.
* It is about installing, not about a version: it does not say which version of the other project is needed.
* `parent` is a different thing (it groups a project under another in the lists). The updater already puts `ARMOR-COMMON` first in every batch, because every build calls its script,
  and a parent before its children; write a requirement in `requires` only when it is not already one of those two, so nothing is declared twice.
* The updater orders a batch so that each required project comes first, and it refuses to install or update a project whose requirement is not installed, with a message in the
  language of the window. A tool that does not know the field ignores it.

### `service`

An object for a project that runs as a network service: `port` (1 to 65535), `health_path` (a path that starts with `/`, only together with `port`) and `systemd_unit` (a name that
ends in `.service`). At least one of `port` or `systemd_unit` must be present.

### `deployment_target_note`

A sentence that explains a `deployment_target` whose meaning is not clear from the words alone.

### `evidence`

How far the repository has been shown to work: `none`, `host-test` (tests on a computer only), `simulator` (run against a simulated or fake board or bus), `bench` (run on a real board on the bench) or `field` (used in the field). It is the ceiling of the lights of the Project status table together with `maturity`: the hardware and integration rows are orange at most for `none`, `host-test` and `simulator`, yellow at most for `bench` and green only for `field`. `tools/status_lights.py` (canonical here, copied to every repository by `sync_ci_tools.py`) fails the validator when a light is above its ceiling; `--suggest` lists what could be better and `--apply` lowers the lights in the eight READMEs and in the source of the generator, never a sentence.

### `hardware_bound`

`false` for a repository that has no hardware (a document, a service, a client): its hardware and integration rows are then not limited by `evidence`. Leave it out when the repository does run on hardware.