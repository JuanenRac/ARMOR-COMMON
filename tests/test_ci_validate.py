"""The baseline check every repository of the family runs (tools/armor_ci_validate.py): the manifest, the changelog order, the version stated in the README prose, the local Markdown links and the
files that mirror the version. Each case builds a small repository in a temporary folder and points the tool at it; the checks of the README layout and of the lights, which have their own tests,
are replaced by empty ones.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def load():
    spec = importlib.util.spec_from_file_location("armor_ci_validate_under_test", ROOT / "tools" / "armor_ci_validate.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


validate = load()

MANIFEST = {
    "schema_version": 1, "ecosystem": "A.R.M.O.R.", "name": "ARMOR-X", "version": "0.1.0", "role": "r", "stack": "s", "technologies": ["python"],
    "deployment_target": "d", "maturity": "functional", "family": "f", "parent": "p", "build": "b", "notes": "n", "native_version": "0.1.0",
}


class Repository:
    """A repository on disk the tool is pointed at; `fails` runs a check and returns the message it failed with (None when it passed)."""

    def __init__(self, test: unittest.TestCase, **manifest) -> None:
        folder = tempfile.TemporaryDirectory()
        test.addCleanup(folder.cleanup)
        self.root = Path(folder.name) / "ARMOR-X"
        self.root.mkdir()
        self.manifest = {**MANIFEST, **manifest}
        self.put("armor.project.json", json.dumps(self.manifest))
        for name in validate.REQUIRED_DOCUMENTS:
            self.put(name, "x\n")
        self.put("CHANGELOG.md", "# Changelog\n\n## [0.1.0] - x\n\n- first\n")

    def put(self, name: str, text: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def fails(self, function, *args) -> str | None:
        err = io.StringIO()
        with mock.patch.object(validate, "ROOT", self.root), mock.patch.object(validate, "MANIFEST_PATH", self.root / "armor.project.json"), \
                mock.patch.object(validate, "check_readme_section_parity", return_value=[]), mock.patch.object(validate, "check_readme_tree", return_value=[]), \
                mock.patch.object(validate, "universal_readme_check", None), mock.patch.object(validate, "status_lights", None), mock.patch.object(validate, "sync_manifests", None), \
                mock.patch.dict(os.environ, {"GITHUB_ACTIONS": ""}), contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            try:
                function(*args)
            except SystemExit as stop:
                self.code = stop.code
                return err.getvalue()
        return None


class ChangelogOrder(unittest.TestCase):
    def check(self, text: str) -> str | None:
        repo = Repository(self)
        repo.put("CHANGELOG.md", text)
        return repo.fails(validate.validate_changelog_order)

    def test_newest_first_with_unreleased_on_top_passes(self) -> None:
        self.assertIsNone(self.check("# C\n\n## [Unreleased]\n\n- a\n\n## [0.2.0]\n\n## [0.1.9]\n\n## 0.1.0\n"))
        self.assertIsNone(self.check("## [0.8.0.1]\n## [0.8.0]\n"))   # 0.8.0 is 0.8.0.0: older than 0.8.0.1

    def test_unreleased_in_the_middle_fails(self) -> None:
        self.assertIn("'Unreleased' must be at the top", self.check("## [0.2.0]\n\n## [Unreleased]\n"))

    def test_a_version_twice_fails(self) -> None:
        self.assertIn("has two entries", self.check("## [0.2.0]\n## [0.2.0]\n"))
        self.assertIn("has two entries", self.check("## [0.2.0]\n## [0.2.0.0]\n"))

    def test_an_older_version_on_top_fails(self) -> None:
        self.assertIn("newest first", self.check("## [0.1.0]\n## [0.2.0]\n"))

    def test_no_changelog_is_not_this_checks_business(self) -> None:
        repo = Repository(self)
        (repo.root / "CHANGELOG.md").unlink()
        self.assertIsNone(repo.fails(validate.validate_changelog_order))


class VersionProse(unittest.TestCase):
    def check(self, line: str, manifest: dict | None = None) -> str | None:
        repo = Repository(self)
        repo.put("README.md", line + "\n")
        return repo.fails(validate.validate_readme_version_prose, manifest or repo.manifest)

    def test_a_label_next_to_the_wrong_version_fails(self) -> None:
        self.assertIn("README.md:1: states 0.0.9, manifest says 0.1.0", self.check("Version: 0.0.9"))
        self.assertIn("states 0.3.0", self.check("Real today - ARMOR-X v0.3.0 works"))
        self.assertIn("states 0.1.1", self.check("| Estado: 0.1.1 |"))

    def test_the_right_version_and_free_prose_pass(self) -> None:
        self.assertIsNone(self.check("Version: 0.1.0"))
        self.assertIsNone(self.check("Needs Python 3.11.2 or newer"))
        self.assertIsNone(self.check("Version: 0.0.9 -> 0.1.0"))   # the odometer scheme itself
        self.assertIsNone(self.check("Version: 0.0.9 → 0.1.0"))
        self.assertIsNone(self.check("ARMOR-X v0.1.0 is current"))

    def test_the_preview_is_cut_after_ten(self) -> None:
        repo = Repository(self)
        repo.put("README.md", "".join(f"Version: 0.0.{n}\n" for n in range(12)))
        message = repo.fails(validate.validate_readme_version_prose, repo.manifest)
        self.assertIn("(+2 more)", message)

    def test_a_missing_translation_is_skipped(self) -> None:
        repo = Repository(self)
        (repo.root / "README_jpn.md").unlink()
        self.assertIsNone(repo.fails(validate.validate_readme_version_prose, repo.manifest))


class Links(unittest.TestCase):
    def test_broken_links_are_named_and_the_rest_pass(self) -> None:
        repo = Repository(self)
        repo.put("docs/a.md", "x")
        repo.put("README.md", "[ok](docs/a.md#top) [w](https://e.org) [m](mailto:a@b.c) [root](/x) [anchor](#a) ![img](images/none.png) [bad](docs/none.md?x=1)\n")
        message = repo.fails(validate.validate_local_markdown_links)
        self.assertIn("README.md:1 -> docs/none.md?x=1", message.replace("\\", "/"))
        self.assertNotIn("images/none.png", message)
        repo.put("README.md", "[ok](docs/a.md)\n")
        self.assertIsNone(repo.fails(validate.validate_local_markdown_links))

    def test_dependency_folders_are_not_searched(self) -> None:
        repo = Repository(self)
        repo.put("node_modules/p/README.md", "[bad](nowhere.md)\n")
        self.assertIsNone(repo.fails(validate.validate_local_markdown_links))

    def test_the_preview_is_cut_after_ten(self) -> None:
        repo = Repository(self)
        repo.put("README.md", "".join(f"[b](none{n}.md)\n" for n in range(11)))
        self.assertIn("(+1 more)", repo.fails(validate.validate_local_markdown_links))


class WholeCheck(unittest.TestCase):
    def run_main(self, repo: Repository):
        message = repo.fails(validate.main)
        return message

    def test_a_good_repository_passes(self) -> None:
        repo = Repository(self)
        out = io.StringIO()
        with mock.patch.object(validate, "ROOT", repo.root), mock.patch.object(validate, "MANIFEST_PATH", repo.root / "armor.project.json"), \
                mock.patch.object(validate, "check_readme_section_parity", return_value=[]), mock.patch.object(validate, "check_readme_tree", return_value=[]), \
                mock.patch.object(validate, "universal_readme_check", None), mock.patch.object(validate, "status_lights", None), mock.patch.object(validate, "sync_manifests", None), \
                contextlib.redirect_stdout(out):
            self.assertEqual(validate.main(), 0)
        self.assertIn("CI_VALIDATION=PASS project=ARMOR-X version=0.1.0", out.getvalue())

    def test_each_manifest_mistake_is_named(self) -> None:
        cases = (
            ({"ecosystem": "other"}, "ecosystem must be"),
            ({"version": "1.0"}, "manifest version must be"),
            ({"version": 3}, "manifest version must be"),
            ({"maturity": "nope"}, "unsupported maturity"),
            ({"technologies": []}, "technologies must be a non-empty list"),
            ({"native_version": "x"}, "native_version must be"),
            ({"native_version": "0.1.1"}, "differs from version"),
        )
        for change, expected in cases:
            repo = Repository(self, **change)
            self.assertIn(expected, self.run_main(repo), change)

    def test_a_missing_key_a_broken_manifest_and_missing_documents(self) -> None:
        repo = Repository(self)
        repo.put("armor.project.json", json.dumps({k: v for k, v in MANIFEST.items() if k != "role"}))
        self.assertIn("missing required keys: role", self.run_main(repo))
        repo.put("armor.project.json", "{broken")
        self.assertIn("cannot read manifest", self.run_main(repo))
        repo = Repository(self)
        (repo.root / "README_por.md").unlink()
        self.assertIn("required documentation missing: README_por.md", self.run_main(repo))

    def test_the_changelog_head_must_be_the_manifest_version(self) -> None:
        repo = Repository(self)
        repo.put("CHANGELOG.md", "## [0.0.9]\n")
        self.assertIn("latest changelog version 0.0.9 differs", self.run_main(repo))
        repo.put("CHANGELOG.md", "nothing\n")
        self.assertIn("<none>", self.run_main(repo))

    def test_the_mirrors_of_the_version_must_agree(self) -> None:
        repo = Repository(self)
        repo.put("pyproject.toml", '[project]\nversion = "0.0.9"\n')
        self.assertIn("pyproject.toml version 0.0.9 differs", self.run_main(repo))
        repo.put("pyproject.toml", "[project]\n")
        self.assertIn("missing its own [project].version", self.run_main(repo))
        repo = Repository(self)
        repo.put("src/pkg/__init__.py", '__version__ = "0.0.9"\n')
        self.assertIn("__version__ 0.0.9 differs", self.run_main(repo))

    def test_the_name_of_the_folder_is_a_warning_locally_and_an_error_in_actions(self) -> None:
        repo = Repository(self, name="ARMOR-OTHER")
        self.assertIsNone(self.run_main(repo))
        with mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": "o/ARMOR-X"}), mock.patch.object(validate, "ROOT", repo.root), \
                mock.patch.object(validate, "MANIFEST_PATH", repo.root / "armor.project.json"), contextlib.redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit):
                validate.main()
        self.assertIn("must match the repository", err.getvalue())

    def test_an_env_file_must_be_ignored(self) -> None:
        repo = Repository(self)
        repo.put(".env", "A=1\n")
        self.assertIn(".env exists locally", self.run_main(repo))
        repo.put(".gitignore", "node_modules\n.env\n")
        self.assertIsNone(self.run_main(repo))

    def test_the_problems_of_the_other_checks_fail_the_run(self) -> None:
        repo = Repository(self)
        for target in ("check_readme_section_parity", "check_readme_tree"):
            with mock.patch.object(validate, "ROOT", repo.root), mock.patch.object(validate, "MANIFEST_PATH", repo.root / "armor.project.json"), \
                    mock.patch.object(validate, target, return_value=["problem of " + target]), mock.patch.object(validate, "check_readme_section_parity" if target == "check_readme_tree" else "check_readme_tree", return_value=[]), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                with self.assertRaises(SystemExit):
                    validate.main()
            self.assertIn("problem of " + target, err.getvalue())
        fake = mock.Mock()
        fake.run_in_ci.return_value = ["layout problem"]
        for name in ("universal_readme_check", "status_lights", "sync_manifests"):
            with mock.patch.object(validate, "ROOT", repo.root), mock.patch.object(validate, "MANIFEST_PATH", repo.root / "armor.project.json"), \
                    mock.patch.object(validate, "check_readme_section_parity", return_value=[]), mock.patch.object(validate, "check_readme_tree", return_value=[]), \
                    mock.patch.object(validate, "universal_readme_check", None), mock.patch.object(validate, "status_lights", None), mock.patch.object(validate, "sync_manifests", None), \
                    mock.patch.object(validate, name, fake), contextlib.redirect_stderr(io.StringIO()) as err:
                with self.assertRaises(SystemExit):
                    validate.main()
            self.assertIn("layout problem", err.getvalue())


if __name__ == "__main__":
    unittest.main()
