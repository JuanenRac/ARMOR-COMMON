"""The shared build, test and version workflow (tools/armor_project_tool.py): the odometer of the versions, the bump of a manifest and of the files that mirror it, the plan of the lint step, the
check of the Markdown links, the local development secrets and the steps each kind of repository runs (the commands are recorded, never executed). Each runs on copies in a temporary folder.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later."""
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
    spec = importlib.util.spec_from_file_location("armor_project_tool_under_test", ROOT / "tools" / "armor_project_tool.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


tool = load()


def quiet(function, *args, **kwargs):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        result = function(*args, **kwargs)
    return result, out.getvalue()


class Odometer(unittest.TestCase):
    def test_no_component_reaches_ten(self) -> None:
        for before, after in (("0.2.9", "0.3.0"), ("0.0.1", "0.0.2"), ("0.4.9", "0.5.0"), ("0.7.8", "0.7.9")):
            self.assertEqual(tool.next_version(before), after)

    def test_the_fourth_component_starts_at_0_8_0(self) -> None:
        self.assertEqual(tool.next_version("0.7.9"), "0.8.0.0")
        self.assertEqual(tool.next_version("0.8.0"), "0.8.0.0")
        self.assertEqual(tool.next_version("0.8.0.9"), "0.8.1.0")
        self.assertEqual(tool.next_version("0.8.9.9"), "0.9.0.0")
        self.assertEqual(tool.next_version("0.9.9.9"), "1.0.0.0")

    def test_the_step_title_is_short_and_without_flags(self) -> None:
        self.assertEqual(tool.step_title(["npm", "run", "typecheck"]), "npm run typecheck")
        self.assertEqual(tool.step_title(["python", "-m", "pytest", "-q", "tests"]), "python -m pytest tests")
        self.assertEqual(tool.step_title(["C:/x/python.exe", "-m", "unittest"]), "python -m unittest")
        self.assertLessEqual(len(tool.step_title(["tool", "a" * 80])), 52)


class Bump(unittest.TestCase):
    def make(self, root: Path, name: str, version: str) -> dict:
        manifest = {"ecosystem": "A.R.M.O.R.", "name": name, "version": version, "native_version": version}
        (root / "armor.project.json").write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_bump_writes_the_manifest_and_a_changelog_entry(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.make(root, "ARMOR-DOCS", "0.1.9")
            (root / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.9] - 2026-01-01\n\n- old\n", encoding="utf-8")
            before, after = tool.bump(root, manifest)
            self.assertEqual((before, after), ("0.1.9", "0.2.0"))
            written = json.loads((root / "armor.project.json").read_text(encoding="utf-8"))
            self.assertEqual((written["version"], written["native_version"]), ("0.2.0", "0.2.0"))
            text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
            self.assertLess(text.index("[0.2.0]"), text.index("[0.1.9]"))
            self.assertTrue(text.endswith("\n"))

    def test_a_missing_changelog_is_made(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tool.bump(root, self.make(root, "ARMOR-DOCS", "0.0.1"))
            self.assertIn("[0.0.2]", (root / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_a_version_that_is_not_numeric_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for bad in ("1.0", "1.0.x", "1.2.3.4.5"):
                with self.assertRaises(RuntimeError):
                    tool.bump(root, self.make(root, "ARMOR-DOCS", bad))

    def test_a_python_project_keeps_pyproject_and_init_in_step(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.make(root, "ARMOR-NETWORK", "0.0.1")
            (root / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "0.0.1"\n', encoding="utf-8")
            (root / "src" / "pkg").mkdir(parents=True)
            (root / "src" / "pkg" / "__init__.py").write_text('__version__ = "0.0.1"\n', encoding="utf-8")
            tool.bump(root, manifest)
            self.assertIn('version = "0.0.2"', (root / "pyproject.toml").read_text(encoding="utf-8"))
            self.assertIn('__version__ = "0.0.2"', (root / "src" / "pkg" / "__init__.py").read_text(encoding="utf-8"))

    def test_the_android_client_moves_its_version_code(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.make(root, "ARMOR-ANDROID-CONTROL", "0.3.1")
            (root / "app").mkdir()
            gradle = root / "app" / "build.gradle.kts"
            gradle.write_text('android { defaultConfig { versionCode = 41\n versionName = "0.3.1" } }\n', encoding="utf-8")
            tool.bump(root, manifest)
            text = gradle.read_text(encoding="utf-8")
            self.assertIn("versionCode = 42", text)
            self.assertIn('versionName = "0.3.2"', text)

    def test_the_android_client_without_its_gradle_file_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.make(root, "ARMOR-ANDROID-CONTROL", "0.3.1")
            with self.assertRaises(RuntimeError):
                tool.bump(root, manifest)
            (root / "app").mkdir()
            (root / "app" / "build.gradle.kts").write_text("android {}\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                tool.bump(root, manifest)


class LintPlan(unittest.TestCase):
    def plan(self, files: dict[str, str]):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, text in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            return tool.lint_plan(root, {}), tool.uses_pyside(root), tool.tool_dirs(root)

    def test_the_flags_of_pyproject(self) -> None:
        self.assertTrue(tool._pyproject_flag("[tool.armor]\nci_lint = false\n", "ci_lint"))
        self.assertFalse(tool._pyproject_flag("[tool.armor]\nci_lint = true\n", "ci_lint"))
        self.assertFalse(tool._pyproject_flag("[other]\nci_lint = false\n", "ci_lint"))
        self.assertFalse(tool._pyproject_flag("[tool.armor]\n[other]\nci_lint = false\n", "ci_lint"))

    def test_switched_off_wins(self) -> None:
        (run, reason), _, _ = self.plan({"pyproject.toml": "[tool.armor]\nci_lint = false\n", "tools/a.py": "x = 1\n"})
        self.assertFalse(run)
        self.assertIn("ci_lint", reason)

    def test_tools_with_python_are_typed(self) -> None:
        (run, reason), _, dirs = self.plan({"tools/a.py": "x = 1\n"})
        self.assertTrue(run)
        self.assertEqual(dirs, ["tools"])

    def test_tools_left_out_and_no_typed_source(self) -> None:
        (run, reason), _, _ = self.plan({"pyproject.toml": "[tool.armor]\nlint_tools = false\n", "scripts/a.py": "x = 1\n"})
        self.assertFalse(run)
        self.assertIn("lint_tools", reason)

    def test_source_with_a_mypy_configuration_is_typed(self) -> None:
        (run, _), _, _ = self.plan({"pyproject.toml": "[tool.mypy]\nstrict = true\n", "src/p/a.py": "x = 1\n"})
        self.assertTrue(run)
        (run, _), _, _ = self.plan({"mypy.ini": "[mypy]\n", "src/p/a.py": "x = 1\n"})
        self.assertTrue(run)
        (run, _), _, _ = self.plan({"setup.cfg": "[mypy]\n", "src/p/a.py": "x = 1\n"})
        self.assertTrue(run)

    def test_nothing_to_check(self) -> None:
        (run, reason), _, _ = self.plan({"README.md": "x"})
        self.assertFalse(run)
        self.assertIn("no mypy", reason)
        (run, _), _, _ = self.plan({"src/p/a.py": "x = 1\n"})
        self.assertFalse(run)

    def test_pyside_is_found_in_the_source(self) -> None:
        _, pyside, _ = self.plan({"src/p/a.py": "from PySide6 import QtCore\n"})
        self.assertTrue(pyside)
        _, pyside, _ = self.plan({"src/p/a.py": "import os\n"})
        self.assertFalse(pyside)

    def test_lint_skips_and_runs_the_right_commands(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "pyproject.toml").write_text("[tool.armor]\nci_lint = false\n", encoding="utf-8")
            with mock.patch.object(tool, "command") as command:
                _, text = quiet(tool.lint, root, {})
            command.assert_not_called()
            self.assertIn("ARMOR_LINT=SKIP", text)
            (root / "pyproject.toml").write_text("[tool.mypy]\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("from PySide6 import QtCore\n", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools" / "t.py").write_text("x = 1\n", encoding="utf-8")
            with mock.patch.object(tool, "command") as command:
                _, text = quiet(tool.lint, root, {})
            words = [" ".join(call.args[1]) for call in command.call_args_list]
            self.assertTrue(any("pip install" in w and "PySide6-Essentials" in w for w in words))
            self.assertTrue(any("ruff check" in w for w in words))
            self.assertTrue(any(w.endswith("-m mypy") for w in words))
            self.assertTrue(any("--platform linux" in w and w.endswith("tools") for w in words))
            self.assertIn("ARMOR_LINT=PASS", text)


class MarkdownLinks(unittest.TestCase):
    def test_a_broken_link_is_named_and_the_good_ones_pass(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "docs").mkdir()
            (root / "docs" / "a.md").write_text("x", encoding="utf-8")
            (root / "README.md").write_text(
                "[ok](docs/a.md) [anchor](docs/a.md#top) [web](https://example.org/x) [mail](mailto:a@b.c) [only anchor](#top) [bad](docs/missing.md)",
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError) as caught:
                quiet(tool.validate_markdown_links, root)
            self.assertIn("docs/missing.md", str(caught.exception).replace("\\", "/"))
            self.assertNotIn("a.md ->", str(caught.exception))
            (root / "README.md").write_text("[ok](docs/a.md)", encoding="utf-8")
            _, text = quiet(tool.validate_markdown_links, root)
            self.assertIn("ARMOR_DOCS_LINKS=PASS", text)


class LocalSecrets(unittest.TestCase):
    def test_a_first_run_makes_distinct_secrets_and_keeps_the_real_environment(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            environment = {"ARMOR_PORT": "9999", "ARMOR_CONTROL_TOKEN": "replace-with-something"}
            result, text = quiet(tool.load_server_environment, root, environment)
            self.assertIn("ARMOR_LOCAL_SECRETS=CREATED", text)
            self.assertTrue((root / ".env").is_file())
            self.assertEqual(result["ARMOR_PORT"], "9999")   # what the system supplies wins
            tokens = {result[key] for key in ("ARMOR_INGEST_TOKEN", "ARMOR_CONTROL_TOKEN", "ARMOR_OPERATOR_TOKEN")}
            self.assertEqual(len(tokens), 3)
            self.assertTrue(all(len(token) >= 32 for token in tokens))
            self.assertFalse(result["ARMOR_CONTROL_TOKEN"].startswith("replace-with-"))
            again, text = quiet(tool.load_server_environment, root, {})
            self.assertNotIn("CREATED", text)
            self.assertEqual(again["ARMOR_INGEST_TOKEN"], result["ARMOR_INGEST_TOKEN"])

    def test_comments_blanks_and_empty_variables_do_not_shadow(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".env").write_text("# c\n\nnot a pair\nA=1\nB = two \n", encoding="utf-8")
            result, _ = quiet(tool.load_server_environment, root, {"A": ""})
            self.assertEqual((result["A"], result["B"]), ("1", "two"))


class Steps(unittest.TestCase):
    def run_steps(self, name: str, files: dict[str, str] | None = None, tools: set[str] | None = None, **env):
        """The commands test_project asks for, recorded; `tools` are the executables that exist."""
        recorded: list[list[str]] = []
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / name
            root.mkdir()
            for rel, text in (files or {}).items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            present = tools if tools is not None else {"npm", "cmake", "ctest", "openscad", "docker", "bash", "gradle", "swift"}
            with mock.patch.object(tool, "command", side_effect=lambda project, args, environment=None: recorded.append([str(a) for a in args])), mock.patch.object(
                tool.shutil, "which", side_effect=lambda exe: f"/bin/{exe}" if exe in present else None
            ), mock.patch.dict(os.environ, env, clear=False), mock.patch.object(tool, "project_python", return_value="python-venv"), mock.patch.object(tool, "check_broker"), mock.patch.object(
                tool.subprocess, "run", side_effect=AssertionError("a step ran a real process")
            ):
                try:
                    _, text = quiet(tool.test_project, root, {"name": name})
                    error = None
                except RuntimeError as caught:
                    text, error = "", str(caught)
        return recorded, text, error

    def joined(self, recorded) -> list[str]:
        return [" ".join(args) for args in recorded]

    def test_the_python_projects_run_unittest(self) -> None:
        recorded, _, _ = self.run_steps("ARMOR-NETWORK")
        self.assertEqual(len(recorded), 1)
        self.assertIn("-m unittest discover -s tests", self.joined(recorded)[0])

    def test_the_updater_runs_pytest_from_its_own_environment(self) -> None:
        recorded, _, _ = self.run_steps("ARMOR-UPDATER")
        self.assertEqual(recorded, [["python-venv", "-m", "pytest", "tests", "-q"]])

    def test_a_node_project_installs_only_when_modules_are_missing(self) -> None:
        recorded, _, _ = self.run_steps("ARMOR-STUDIO")
        names = [args[-1] if args[-2:-1] != ["run"] else args[-1] for args in recorded]
        self.assertEqual([r[1] for r in recorded], ["ci", "run", "test", "run"])
        self.assertEqual(names[1:], ["typecheck", "test", "build"])
        recorded, _, _ = self.run_steps("ARMOR-SERVER", files={"node_modules/.keep": ""})
        self.assertEqual([r[1] for r in recorded], ["run", "test", "run"])

    def test_a_node_project_without_npm_is_refused(self) -> None:
        _, _, error = self.run_steps("ARMOR-STUDIO", tools=set())
        self.assertIn("npm is required", error)

    def test_the_documentation_repository_checks_links_then_tests(self) -> None:
        recorded, text, _ = self.run_steps("ARMOR-DOCS", files={"tests/test_a.py": "x"})
        self.assertIn("ARMOR_DOCS_LINKS=PASS", text)
        self.assertIn("unittest discover -s tests -p test_*.py", self.joined(recorded)[0])
        _, text, _ = self.run_steps("ARMOR-DOCS")
        self.assertIn("UNIT_TESTS=SKIPPED", text)

    def test_the_hardware_repository_renders_every_piece(self) -> None:
        recorded, _, _ = self.run_steps("ARMOR-HARDWARE", files={"tests/test_a.py": "x"})
        stl = [args for args in recorded if args[0].endswith("openscad")]
        self.assertEqual(len(stl), 1 + 2 + 6)
        self.assertTrue(any('preset="alarm"' in " ".join(a) and 'part="lid"' in " ".join(a) for a in stl))
        _, _, error = self.run_steps("ARMOR-HARDWARE", tools=set())
        self.assertIn("OpenSCAD is required", error)

    def test_the_host_nodes_configure_build_and_run_ctest(self) -> None:
        recorded, _, _ = self.run_steps("ARMOR-NODE-HMI")
        steps = self.joined(recorded)
        self.assertIn("-S tests -B", steps[0])
        self.assertIn("--build", steps[1])
        self.assertIn("--test-dir", steps[2])
        _, _, error = self.run_steps("ARMOR-NODE-HMI", tools=set())
        self.assertIn("CMake", error)
        _, _, error = self.run_steps("ARMOR-NODE-HMI", tools={"cmake"})
        self.assertIn("CTest", error)

    def test_the_android_client_prefers_its_wrapper(self) -> None:
        recorded, _, _ = self.run_steps("ARMOR-ANDROID-CONTROL", files={"gradlew": ""}, tools=set())
        self.assertEqual(recorded[0][0], "./gradlew")
        _, _, error = self.run_steps("ARMOR-ANDROID-CONTROL", tools=set())
        self.assertIn("Gradle", error)

    def test_the_ios_client_needs_swift_only_when_asked(self) -> None:
        recorded, text, _ = self.run_steps("ARMOR-IOS-CONTROL", tools=set())
        self.assertIn("SWIFT_TESTS=SKIPPED", text)
        self.assertEqual(len(recorded), 1)
        _, _, error = self.run_steps("ARMOR-IOS-CONTROL", tools=set(), ARMOR_REQUIRE_SWIFT="1")
        self.assertIn("Swift is required", error)
        recorded, _, _ = self.run_steps("ARMOR-IOS-CONTROL")
        self.assertEqual(len(recorded), 2)

    def test_an_unknown_repository_is_refused(self) -> None:
        _, _, error = self.run_steps("ARMOR-SOMETHING")
        self.assertIn("no build rule registered", error)

    def test_the_siblings_flag(self) -> None:
        with mock.patch.dict(os.environ, {"ARMOR_REQUIRE_SIBLINGS": "1"}):
            self.assertTrue(tool.siblings_required())
        with mock.patch.dict(os.environ, {"ARMOR_REQUIRE_SIBLINGS": "0"}):
            self.assertFalse(tool.siblings_required())
        with mock.patch.dict(os.environ, {"ARMOR_REQUIRE_SIBLINGS": ""}):
            self.assertFalse(tool.siblings_required())

    def test_common_demands_its_siblings_in_ci_and_skips_them_on_a_machine(self) -> None:
        recorded, text, error = self.run_steps("ARMOR-COMMON", ARMOR_REQUIRE_SIBLINGS="")
        self.assertIsNone(error)
        self.assertIn("FIRMWARE_BASE=SKIPPED", text)
        self.assertEqual(len(recorded), 3)
        _, _, error = self.run_steps("ARMOR-COMMON", ARMOR_REQUIRE_SIBLINGS="1")
        self.assertIn("not next to ARMOR-COMMON", error)


class RunAndCommand(unittest.TestCase):
    def test_a_library_has_nothing_to_run(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            _, text = quiet(tool.run_project, Path(folder), {"name": "ARMOR-COMMON"})
        self.assertIn("is a library", text)

    def test_hardware_and_native_projects_have_no_generic_runtime(self) -> None:
        for name in ("ARMOR-NODE-RADAR", "ARMOR-HARDWARE", "ARMOR-DOCS", "ARMOR-IOS-CONTROL"):
            _, text = quiet(tool.run_project, Path("."), {"name": name})
            self.assertIn("no safe generic runtime command", text)
        with self.assertRaises(RuntimeError):
            tool.run_project(Path("."), {"name": "ARMOR-NOTHING"})

    def test_a_python_project_runs_its_module_with_src_on_the_path(self) -> None:
        with mock.patch.object(tool, "command") as command:
            tool.run_project(Path("/p"), {"name": "ARMOR-NETWORK"})
        args, environment = command.call_args.args[1], command.call_args.args[2]
        self.assertEqual(args[-1], "armor_network")
        self.assertTrue(environment["PYTHONPATH"].startswith(str(Path("/p") / "src")))

    def test_devops_brings_the_stack_up(self) -> None:
        with mock.patch.object(tool, "command") as command:
            tool.run_project(Path("/p"), {"name": "ARMOR-DEVOPS"})
        self.assertEqual(command.call_args.args[1], ["docker", "compose", "up", "--build"])

    def test_the_server_creates_its_local_secrets_before_dev(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            with mock.patch.object(tool, "command") as command:
                quiet(tool.run_project, Path(folder), {"name": "ARMOR-SERVER"})
            self.assertTrue((Path(folder) / ".env").is_file())
            self.assertEqual(command.call_args.args[1][1:], ["run", "dev"])

    def test_command_reports_a_failure_and_a_missing_executable(self) -> None:
        with mock.patch.object(tool, "PANEL", None):
            _, text = quiet(tool.command, Path("."), [sys.executable, "-c", "pass"])
            self.assertIn("$ ", text)
            with self.assertRaises(RuntimeError) as caught:
                quiet(tool.command, Path("."), [sys.executable, "-c", "raise SystemExit(3)"])
            self.assertIn("exit code 3", str(caught.exception))
            with self.assertRaises(RuntimeError) as caught:
                quiet(tool.command, Path("."), ["armor-no-such-executable-xyz"])
            self.assertIn("not found", str(caught.exception))

    def test_a_panel_step_that_fails_raises(self) -> None:
        panel = mock.Mock()
        panel.step.return_value = False
        with mock.patch.object(tool, "PANEL", panel):
            with self.assertRaises(RuntimeError):
                tool.command(Path("."), ["x", "y"])
            panel.step.return_value = True
            tool.command(Path("."), ["x", "y"])

    def test_report_sends_skipped_steps_to_the_panel(self) -> None:
        panel = mock.Mock()
        with mock.patch.object(tool, "PANEL", panel):
            tool.report("SWIFT_TESTS=SKIPPED no Swift")
            tool.report("ARMOR_LINT=PASS")
        panel.skip.assert_called_once()
        panel.note.assert_called_once_with("ARMOR_LINT=PASS")

    def test_main_refuses_a_foreign_manifest_and_a_missing_one(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with mock.patch.object(sys, "argv", ["tool", "test", str(root)]):
                with self.assertRaises(RuntimeError):
                    tool.main()
                (root / "armor.project.json").write_text(json.dumps({"ecosystem": "other", "name": "x", "version": "1.0.0"}), encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    tool.main()

    def test_main_test_and_build_report_the_result(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "armor.project.json").write_text(json.dumps({"ecosystem": "A.R.M.O.R.", "name": "ARMOR-DOCS", "version": "0.1.0"}), encoding="utf-8")
            with mock.patch.dict(os.environ, {"ARMOR_PRETTY": "0"}), mock.patch.object(tool, "test_project"):
                with mock.patch.object(sys, "argv", ["tool", "build-test", str(root)]):
                    code, text = quiet(tool.main)
                self.assertEqual(code, 0)
                self.assertIn("BUILD_TEST=PASS", text)
                with mock.patch.object(sys, "argv", ["tool", "build", str(root)]):
                    code, text = quiet(tool.main)
                self.assertIn("VERSION_BUMP=PASS v0.1.0 -> v0.1.1", text)
                self.assertEqual(json.loads((root / "armor.project.json").read_text(encoding="utf-8"))["version"], "0.1.1")
                with mock.patch.object(sys, "argv", ["tool", "run", str(root)]):
                    code, _ = quiet(tool.main)
                self.assertEqual(code, 0)
                with mock.patch.object(sys, "argv", ["tool", "lint", str(root)]), mock.patch.object(tool, "lint") as lint:
                    code, _ = quiet(tool.main)
                lint.assert_called_once()
            with mock.patch.dict(os.environ, {"ARMOR_PRETTY": "0"}), mock.patch.object(tool, "test_project", side_effect=RuntimeError("boom")):
                with mock.patch.object(sys, "argv", ["tool", "test", str(root)]):
                    with self.assertRaises(RuntimeError):
                        quiet(tool.main)


if __name__ == "__main__":
    unittest.main()
