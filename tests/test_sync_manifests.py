"""The check of the manifests of the family (tools/sync_manifests.py): version comparison, the facts read from a repository (shipped versions, components, changelog, tests, simulation), the findings
they raise, the GitHub facts with a budget and a cache, the files --apply writes and the command line. Each runs on a copy of a small repository in a temporary folder.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location("sync_manifests_under_test", ROOT / "tools" / "sync_manifests.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


sm = load()
sm.PREFIX, sm.MANIFEST = "ARMOR", "armor.project.json"


def write(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def manifest(**fields) -> str:
    base = {"name": "ARMOR-X", "version": "0.1.0", "maturity": "alpha", "evidence": "none", "hardware_bound": False}
    base.update(fields)
    return json.dumps(base)


def codes(item: dict) -> set[str]:
    return {code for _, code, _ in item["findings"]}


class Versions(unittest.TestCase):
    def test_three_and_four_components_are_the_same_version(self) -> None:
        self.assertTrue(sm.same("0.4.5", "0.4.5.0"))
        self.assertFalse(sm.same("0.4.5", "0.4.5.1"))
        self.assertTrue(sm.same("0.4.5.1", "0.4.5.2", three=True))
        self.assertFalse(sm.same("0.4.6", "0.4.5", three=True))
        self.assertFalse(sm.same("latest", "0.4.5"))
        self.assertEqual(sm.odometer("1.2"), (1, 2, 0, 0))

    def test_a_pattern_is_a_string_or_a_part_per_key(self) -> None:
        text = "#define V_MAJOR 1\n#define V_MINOR 2\nv=3.4\n"
        self.assertEqual(sm.pattern_version(text, r"^v=(\d+)\.(\d+)"), "3.4")
        self.assertEqual(sm.pattern_version(text, {"major": r"V_MAJOR (\d+)", "minor": r"V_MINOR (\d+)"}), "1.2")
        self.assertIsNone(sm.pattern_version(text, {"major": r"NOPE (\d+)"}))
        self.assertIsNone(sm.pattern_version(text, r"zzz(\d)"))
        self.assertIsNone(sm.pattern_version(text, 7))


class Facts(unittest.TestCase):
    def repo(self, files: dict[str, str]):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name) / "ARMOR-X"
        root.mkdir()
        write(root, files)
        return sm.Repo(root, "WORKTREE")

    def test_the_worktree_skips_dependencies_and_reads_files(self) -> None:
        repo = self.repo({"a.txt": "x", "node_modules/b.txt": "y", "src/c.py": "z"})
        self.assertEqual(sorted(repo.files), ["a.txt", "src/c.py"])
        self.assertEqual(repo.read("a.txt"), "x")
        self.assertIsNone(repo.read("missing"))

    def test_a_git_reference_that_does_not_exist_falls_back_to_head(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            repo = sm.Repo(Path(folder), "origin/main")
        self.assertEqual(repo.ref, "HEAD")
        self.assertEqual(repo.files, [])

    def test_the_shipped_versions_are_found(self) -> None:
        repo = self.repo({"package.json": '{"version": "0.2.0"}', "pyproject.toml": 'version = "0.2.1"\n', "app/build.gradle.kts": 'versionName = "0.2.2"\n', "src/pkg/__init__.py": '__version__ = "0.2.3"\n', "src/pkg/deep/__init__.py": '__version__ = "9.9.9"\n'})
        found = dict(sm.native_candidates(repo, {}))
        self.assertEqual(found, {"package.json": "0.2.0", "pyproject.toml": "0.2.1", "app/build.gradle.kts": "0.2.2", "src/pkg/__init__.py": "0.2.3"})
        self.assertEqual(sm.native_candidates(self.repo({"package.json": "{not json"}), {}), [])

    def test_a_declared_native_file_is_read_by_pattern(self) -> None:
        repo = self.repo({"include/v.h": "#define V 1.2.3\n"})
        spec = {"native_version": {"file": "include/v.h", "pattern": r"V (\d+\.\d+\.\d+)"}}
        self.assertEqual(sm.native_candidates(repo, spec), [("include/v.h", "1.2.3")])
        spec = {"native_version": {"file": "include/none.h", "pattern": "x"}}
        self.assertEqual(sm.native_candidates(repo, spec), [("include/none.h", "UNREADABLE")])

    def test_components_are_compared_with_their_header(self) -> None:
        repo = self.repo({"v.h": "#define FW_MAJOR 1\n#define FW_MINOR 2\n#define FW_PATCH 3\n"})
        good = {"components": [{"name": "fw", "version": "1.2.3", "source": {"file": "v.h", "prefix": "FW"}}]}
        self.assertEqual(sm.component_findings(repo, good), [])
        bad = {"components": [{"name": "fw", "version": "1.2.4", "source": {"file": "v.h", "prefix": "FW"}}]}
        self.assertEqual(sm.component_findings(repo, bad)[0][1], "COMPONENT_VERSION")
        gone = {"components": [{"name": "fw", "version": "1.2.3", "source": {"file": "x.h", "prefix": "FW"}}]}
        self.assertEqual(sm.component_findings(repo, gone)[0][1], "COMPONENT_SOURCE_MISSING")
        self.assertEqual(sm.component_findings(repo, {}), [])

    def test_the_changelog(self) -> None:
        self.assertEqual(sm.changelog_facts(self.repo({})), {"present": False})
        text = "# Changelog\n\n## [Unreleased]\n\n- one\n* two\n#### sub\n- three\n\n## [0.3.0] - x\n\n- old\n## [0.2.0]\n"
        facts = sm.changelog_facts(self.repo({"CHANGELOG.md": text}))
        self.assertEqual((facts["head"], facts["unreleased"]), ("0.3.0", 3))

    def test_the_simulation_is_found_in_workflows_or_in_paths(self) -> None:
        in_flow = sm.simulation_facts(self.repo({".github/workflows/a.yml": "# simulator\nsteps:\n  - run: python simulate.py\n"}))
        self.assertTrue(in_flow["ci_simulation"])
        by_path = sm.simulation_facts(self.repo({".github/workflows/a.yml": "steps: []\n", "tests/fake_board.py": "x"}))
        self.assertTrue(by_path["ci_simulation"])
        none = sm.simulation_facts(self.repo({"tests/fake_board.py": "x"}))
        self.assertFalse(none["ci_simulation"])


class Inspect(unittest.TestCase):
    def inspect(self, files: dict[str, str], gh=None) -> dict:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "ARMOR-X"
            root.mkdir()
            write(root, files)
            return sm.inspect(sm.Repo(root, "WORKTREE"), gh)

    def test_no_manifest(self) -> None:
        self.assertEqual(codes(self.inspect({})), {"NO_MANIFEST"})

    def test_a_clean_repository_has_no_hard_finding(self) -> None:
        item = self.inspect({"armor.project.json": manifest(), "package.json": '{"version": "0.1.0"}', "CHANGELOG.md": "## [0.1.0]\n"})
        self.assertEqual([c for level, c, _ in item["findings"] if level == sm.HARD], [])

    def test_contradictions_are_hard(self) -> None:
        item = self.inspect({"armor.project.json": manifest(native_version="0.0.9", evidence="simulator"), "package.json": '{"version": "0.3.0"}', "CHANGELOG.md": "## [0.2.0]\n- x\n"})
        self.assertTrue({"NATIVE_VERSION", "NATIVE_MIRROR", "CHANGELOG_HEAD", "EVIDENCE_NO_TESTS", "SIMULATOR_NO_CI_JOB"} <= codes(item))

    def test_notes(self) -> None:
        item = self.inspect({"armor.project.json": manifest(evidence="bench"), "tests/test_a.py": "x", "CHANGELOG.md": "## [Unreleased]\n- a\n"})
        self.assertTrue({"NATIVE_UNKNOWN", "HUMAN_RECORD_MISSING", "UNRELEASED"} <= codes(item))
        item = self.inspect({"armor.project.json": manifest(hardware_bound=True), ".github/workflows/a.yml": "run: simulate\n"})
        self.assertIn("SIMULATION_NOT_CLAIMED", codes(item))

    def test_github_facts(self) -> None:
        gh = mock.Mock()
        gh.release.return_value, gh.ci.return_value = "v0.9.0", "failure"
        item = self.inspect({"armor.project.json": manifest()}, gh)
        self.assertEqual(item["facts"]["latest_release"], "v0.9.0")
        self.assertTrue({"RELEASE_AHEAD", "CI_MAIN"} <= codes(item))
        gh.release.return_value, gh.ci.return_value = "v0.0.9", "success"
        item = self.inspect({"armor.project.json": manifest()}, gh)
        self.assertIn("RELEASE_PENDING", codes(item))
        self.assertNotIn("CI_MAIN", codes(item))


class GitHubFacts(unittest.TestCase):
    def test_answers_are_cached_and_the_budget_holds(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder) / "cache.json"
            gh = sm.Gh("owner", 2, cache, 3600)
            reply = mock.Mock(returncode=0, stdout="v1.0.0\n", stderr="")
            with mock.patch.object(sm.subprocess, "run", return_value=reply) as run:
                self.assertEqual(gh.release("R"), "v1.0.0")
                self.assertEqual(gh.release("R"), "v1.0.0")   # from the cache
                self.assertEqual(run.call_count, 1)
                self.assertEqual(gh.ci("R"), "v1.0.0")
                self.assertEqual(gh.release("Other"), "budget")   # the third call is over the budget
            gh.save()
            again = sm.Gh("owner", 2, cache, 3600)
            self.assertIn("rel:R", again.cache)

    def test_failures_are_not_cached(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            gh = sm.Gh("owner", 9, Path(folder) / "c.json", 3600)
            with mock.patch.object(sm.subprocess, "run", return_value=mock.Mock(returncode=1, stdout="", stderr="HTTP 404")):
                self.assertEqual(gh.release("R"), "none")
            with mock.patch.object(sm.subprocess, "run", return_value=mock.Mock(returncode=1, stdout="", stderr="HTTP 500")):
                self.assertEqual(gh.ci("R"), "error")
            self.assertIn("rel:R", gh.cache)
            self.assertNotIn("ci:R", gh.cache)

    def test_an_old_entry_is_asked_again_and_an_unwritable_cache_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder) / "c.json"
            cache.write_text(json.dumps({"rel:R": {"at": time.time() - 99999, "value": "old"}}), encoding="utf-8")
            gh = sm.Gh("owner", 9, cache, 60)
            with mock.patch.object(sm.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="new", stderr="")):
                self.assertEqual(gh.release("R"), "new")
            gh.cache_path = Path(folder) / "nowhere" / "c.json"
            gh.save()
            self.assertEqual(sm.Gh("o", 1, Path(folder) / "broken", 1).cache, {})


class WorkspaceAndApply(unittest.TestCase):
    def workspace(self, folder: str) -> Path:
        workspace = Path(folder)
        for name, manifest_text, extra in (
            ("ARMOR-A", manifest(name="ARMOR-A", version="0.1.0", native_version="0.1.0"), {"package.json": '{"version": "0.2.0"}'}),
            ("ARMOR-B", manifest(name="ARMOR-B", version="0.1.0"), {"package.json": '{"version": "0.1.0"}'}),
        ):
            root = workspace / name
            (root / ".git").mkdir(parents=True)
            write(root, {"armor.project.json": manifest_text, **extra})
        (workspace / "OTHER").mkdir()
        (workspace / "ARMOR-NOGIT").mkdir()
        return workspace

    def test_the_family_is_the_folders_with_the_prefix_and_a_clone(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            workspace = self.workspace(folder)
            self.assertEqual([p.name for p in sm.family_repos(workspace, [])], ["ARMOR-A", "ARMOR-B"])
            self.assertEqual([p.name for p in sm.family_repos(workspace, ["B"])], ["ARMOR-B"])
            self.assertEqual([p.name for p in sm.family_repos(workspace, ["ARMOR-A"])], ["ARMOR-A"])

    def test_apply_raises_the_version_never_lowers_it(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            workspace = self.workspace(folder)
            results = [sm.inspect(sm.Repo(workspace / name, "WORKTREE"), None) for name in ("ARMOR-A", "ARMOR-B")]
            done = sm.apply_changes(results, workspace)
            self.assertEqual(done, ["ARMOR-A: version -> 0.2.0"])
            written = json.loads((workspace / "ARMOR-A" / "armor.project.json").read_text(encoding="utf-8"))
            self.assertEqual((written["version"], written["native_version"]), ("0.2.0", "0.2.0"))
            self.assertEqual(sm.apply_changes([{"name": "ARMOR-NONE"}, {"name": "ARMOR-B", "manifest": {}, "facts": {}}], workspace), [])
            behind = [{"name": "ARMOR-B", "manifest": {"version": "0.5.0"}, "facts": {"native": {"x": "0.1.0"}}}]
            self.assertEqual(sm.apply_changes(behind, workspace), [])

    def test_the_command_line(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            workspace = self.workspace(folder)
            base = ["tool", "--workspace", str(workspace), "--ref", "WORKTREE"]
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(sys, "argv", [*base, "--check", "--report", str(workspace / "r.json")]), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = sm.main()
            self.assertEqual(code, 1)   # ARMOR-A: its package.json says 0.2.0 and its manifest 0.1.0
            self.assertIn("NATIVE_VERSION", err.getvalue())
            self.assertIn("MANIFEST_FACTS=FAIL repositories=2", out.getvalue())
            self.assertEqual(len(json.loads((workspace / "r.json").read_text(encoding="utf-8"))), 2)
            out = io.StringIO()
            with mock.patch.object(sys, "argv", [*base, "--repo", "B"]), contextlib.redirect_stdout(out):
                code = sm.main()
            self.assertEqual(code, 0)
            self.assertIn("MANIFEST_FACTS=PASS repositories=1", out.getvalue())
            out = io.StringIO()
            with mock.patch.object(sys, "argv", [*base, "--apply-manifests"]), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                sm.main()
            self.assertIn("wrote ARMOR-A: version -> 0.2.0", out.getvalue())

    def test_the_command_line_online_and_waived(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            workspace = self.workspace(folder)
            base = ["tool", "--workspace", str(workspace), "--ref", "WORKTREE", "--online", "--cache", str(workspace / "cache.json"), "--max-calls", "0"]
            out = io.StringIO()
            with mock.patch.object(sys, "argv", [*base, "--repo", "B"]), contextlib.redirect_stdout(out):
                code = sm.main()
            self.assertEqual(code, 0)
            self.assertIn("api_calls=0", out.getvalue())
            with mock.patch.object(sm, "waivers", return_value={"ARMOR-A": ["NATIVE_VERSION", "NATIVE_MIRROR"]}):
                with mock.patch.object(sys, "argv", ["tool", "--workspace", str(workspace), "--ref", "WORKTREE", "--check", "--repo", "A"]), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(sm.main(), 0)

    def test_waivers_and_the_check_of_one_repository(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "ARMOR-X"
            root.mkdir()
            self.assertEqual(sm.run_in_ci(root), [])   # no manifest, nothing to say
            write(root, {"armor.project.json": manifest(), "package.json": '{"version": "0.5.0"}'})
            before = sm.MANIFEST
            try:
                problems = sm.run_in_ci(root)
                self.assertEqual(len(problems), 1)
                self.assertIn("NATIVE_VERSION", problems[0])
                write(root, {"data/manifest_waivers.json": json.dumps({"ARMOR-X": ["NATIVE_VERSION"]})})
                self.assertEqual(sm.run_in_ci(root), [])
                write(root, {"data/manifest_waivers.json": json.dumps({"*": ["NATIVE_VERSION"]})})
                self.assertEqual(sm.run_in_ci(root), [])
            finally:
                sm.MANIFEST = before
            self.assertEqual(sm.waivers(Path(folder) / "none"), {})

    def test_the_self_only_check_reads_the_docs_repository_itself(self) -> None:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["tool", "--self"]), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            sm.main()
        self.assertIn("repositories=1", out.getvalue())


if __name__ == "__main__":
    unittest.main()
