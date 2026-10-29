# The pictures of the READMEs

Two pictures of every README are drawn by tools, not by hand, so they cannot say what the code no longer does:

| Picture | Source file | Tool | Output |
|---|---|---|---|
| Architecture | `docs/architecture.json` | `tools/make_architecture.py` | `images/architecture.svg` |
| Repository Structure | `docs/structure.json` | `tools/make_structure.py` | the text tree for the README and `images/repository-structure.svg` |

The canonical copy of the tools is here, in ARMOR-COMMON (`tools/_readme_svg.py`, `tools/make_architecture.py`, `tools/make_structure.py`). The other repositories of the family carry a byte-for-byte copy in their own `tools/`, written by `tools/sync_ci_tools.py` of ARMOR-DOCS (`python tools/sync_ci_tools.py --check` fails when a copy has drifted). Change the tools here, then run the sync.

Both pictures are 1200 pixels wide, have no icons and no drawings (type, lines and curves) and move discreetly (SMIL: dashes flowing along the arrows, a pulse that visits the boxes). The colours come from the family of the repository (`armor`, `hydra`, `urtc` or `eh3d`). Every text is measured before the file is written: a text that would leave its box, or lie on another text, stops the build, so a picture that is written has no overflow.

## Architecture

```text
python tools/make_architecture.py            # writes images/architecture.svg
python tools/make_architecture.py --check    # exit 1 when the picture, the JSON or the code it points to disagree
python tools/make_architecture.py --png out.png   # also a screenshot made with Edge, to look at it
```

`docs/architecture.json` has at most twelve boxes in three columns (who calls the repository, the repository, what it depends on), the arrows between them with a short label, and a level for every box:

| Level | Meaning | Look |
|---|---|---|
| `tested` | covered by tests | the family's first colour |
| `contract` | the source of the rest, or a security layer | the family's second colour |
| `config` | chosen by the installation, or never tried for real | amber, dashed |
| `untested` | has not run on real hardware | red bar |
| `external` | another repository or a device | grey |

Each box may list `code`: paths of the repository, optionally `path::text` when a text has to be in the file. `--check` fails when the file is gone or no longer holds the text, and when `images/architecture.svg` is not what the JSON draws now.

## Repository Structure

```text
python tools/make_structure.py               # writes images/repository-structure.svg ("svg": "all" writes one per language)
python tools/make_structure.py --tree es     # prints the text tree of a language
python tools/make_structure.py --check       # tree, disk and pictures agree
python tools/make_structure.py --check --readmes   # ... and every README carries the tree of its language
```

`docs/structure.json` lists the cards of the picture; each row has its description in the eight languages (`en`, `es`, `de`, `fr`, `it`, `ja`, `zh`, `pt`), and the same file gives the text tree, so the names are identical everywhere. `--check` compares the tree with the files Git versions: an entry that is versioned but not listed, or listed but not there, fails. A language without its description is an error.

## Tests

`tests/test_readme_tools.py` builds both pictures from a fixture, checks that the XML is valid and the output is deterministic, that a changed JSON or a changed code reference fails `--check`, that overflow and overlap are caught, and, where Edge is installed, that both pictures render to a real screenshot.
