"""The live panel of the build and test scripts (tools/pretty_run.py), run in this process so that its lines are measured: one line per step with its time, the output folded away until a step
fails, the tests counted, a script drawn as steps (by the markers [n/m] or by lines that start with + or $) and the summary with its exit code. The drawing is checked in the plain form (a pipe)
and in the one of a terminal.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location("pretty_run_under_test", ROOT / "tools" / "pretty_run.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules["pretty_run_under_test"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


pr = load()


def drawn(function, *args, tty: bool = False, **kwargs):
    out = io.StringIO()
    with mock.patch.object(pr, "_TTY", tty), contextlib.redirect_stdout(out):
        result = function(*args, **kwargs)
    return result, out.getvalue()


def python(code: str) -> list[str]:
    return [sys.executable, "-c", code]


class Small(unittest.TestCase):
    def test_times(self) -> None:
        self.assertEqual(pr._seconds(0.04), "0.0 s")
        self.assertEqual(pr._seconds(12.34), "12.3 s")
        self.assertEqual(pr._seconds(75), "1 min 15 s")

    def test_colour_only_on_a_terminal(self) -> None:
        with mock.patch.object(pr, "_TTY", False):
            self.assertEqual(pr._c("31", "x"), "x")
        with mock.patch.object(pr, "_TTY", True):
            self.assertEqual(pr._c("31", "x"), "\033[31mx\033[0m")

    def test_the_log_name_is_safe(self) -> None:
        panel = pr.Panel("A B/C", "build-test")
        self.assertRegex(panel.log_path.name, r"^pretty_run-A_B_C-build-test\.log$")


class Steps(unittest.TestCase):
    def panel(self) -> "pr.Panel":
        panel = pr.Panel("DEMO", "build-test", "1.2.3")
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        panel.log_path = Path(folder.name) / "log.txt"
        return panel

    def test_the_banner_names_the_project_and_the_mode(self) -> None:
        _, text = drawn(self.panel().banner)
        self.assertIn("DEMO", text)
        self.assertIn("BUILD-TEST", text)
        self.assertIn("v1.2.3", text)
        _, text = drawn(self.panel().banner, tty=True)
        self.assertIn("╔", text)

    def test_a_good_step_counts_its_tests(self) -> None:
        panel = self.panel()
        ok, text = drawn(panel.step, "Unit", python("print('Ran 7 tests in 0.1s'); print('OK')"))
        self.assertTrue(ok)
        self.assertIn("ok   Unit", text)
        self.assertIn("7 tests", text)
        self.assertEqual((panel.passed, panel.failed), (7, 0))
        self.assertEqual(panel.steps[0][:2], ("Unit", "ok"))

    def test_a_failing_step_shows_its_output(self) -> None:
        panel = self.panel()
        ok, text = drawn(panel.step, "Broken", python("print('line one'); print('boom'); raise SystemExit(2)"))
        self.assertFalse(ok)
        self.assertIn("FAIL Broken", text)
        self.assertIn("boom", text)
        self.assertEqual(panel.steps[0][1], "fail")

    def test_a_missing_executable_is_a_failed_step(self) -> None:
        panel = self.panel()
        ok, text = drawn(panel.step, "Nothing", ["armor-no-such-executable-xyz"])
        self.assertFalse(ok)
        self.assertIn("required executable was not found", text)

    def test_the_terminal_form_draws_a_symbol_and_the_time(self) -> None:
        panel = self.panel()
        ok, text = drawn(panel.step, "Slow", python("import time; print('working'); time.sleep(0.35)"), tty=True)
        self.assertTrue(ok)
        self.assertIn("✔", text)
        self.assertIn("Slow", text)
        _, text = drawn(panel.step, "Bad", python("raise SystemExit(1)"), tty=True)
        self.assertIn("✘", text)

    def test_skip_fail_and_note(self) -> None:
        panel = self.panel()
        _, text = drawn(panel.skip, "Browser", "no browser")
        self.assertIn("skip Browser  (no browser)", text)
        _, text = drawn(panel.skip, "Browser", "no browser", tty=True)
        self.assertIn("skipped", text)
        _, text = drawn(panel.skip, "Plain")
        self.assertIn("skip Plain", text)
        _, text = drawn(panel.fail, "Check", "it did not hold")
        self.assertIn("FAIL Check", text)
        self.assertIn("it did not hold", text)
        _, text = drawn(panel.fail, "Check", "again", tty=True)
        self.assertIn("failed", text)
        _, text = drawn(panel.note, "a note")
        self.assertIn("a note", text)

    def test_the_summary_and_the_exit_code(self) -> None:
        panel = self.panel()
        drawn(panel.step, "A", python("print('Ran 3 tests in 0.1s')"))
        drawn(panel.skip, "B", "why")
        code, text = drawn(panel.finish, "extra words")
        self.assertEqual(code, 0)
        self.assertIn("PASS", text)
        self.assertIn("1/1 steps", text)
        self.assertIn("1 skipped", text)
        self.assertIn("3 tests passed", text)
        self.assertIn("extra words", text)
        self.assertTrue(panel.log_path.is_file())
        drawn(panel.fail, "C", "no")
        code, text = drawn(panel.finish)
        self.assertEqual(code, 1)
        self.assertIn("FAIL", text)
        self.assertIn("failed: C", text)
        code, text = drawn(panel.finish, tty=True)
        self.assertIn("✘", text)

    def test_failed_tests_fail_the_run_even_when_the_commands_succeeded(self) -> None:
        panel = self.panel()
        drawn(panel.step, "A", python("print('Ran 3 tests in 0.1s'); print('FAILED (failures=1)')"))
        code, text = drawn(panel.finish)
        self.assertEqual(code, 1)
        self.assertIn("1 failed", text)

    def test_an_unwritable_log_does_not_stop_the_summary(self) -> None:
        panel = self.panel()
        panel.log_path = panel.log_path.parent / "nowhere" / "log.txt"
        code, _ = drawn(panel.finish)
        self.assertEqual(code, 0)


class Wrap(unittest.TestCase):
    def script(self, text: str) -> list[str]:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "run.py"
        path.write_text(text, encoding="utf-8")
        return [sys.executable, str(path)]

    def wrap(self, text: str, tty: bool = False):
        panel = pr.Panel("DEMO", "build", "1.0")
        panel.log_path = Path(tempfile.gettempdir()) / "pretty_panel_test.log"
        code, out = drawn(panel.wrap, self.script(text), tty=tty)
        return panel, code, out

    def test_markers_make_steps_and_the_preamble_is_left_out(self) -> None:
        panel, code, out = self.wrap("print('own banner')\nprint('[1/2] First')\nprint('hello')\nprint('[2/2] Second')\nprint('Ran 4 tests in 0.1s')\n")
        self.assertEqual(code, 0)
        self.assertEqual([s[0] for s in panel.steps], ["First", "Second"])
        self.assertNotIn("own banner", out)
        self.assertEqual(panel.passed, 4)
        self.assertIn("PASS", out)

    def test_command_lines_make_steps_when_there_are_no_markers(self) -> None:
        panel, code, _ = self.wrap("print('+ cmake build')\nprint('x')\nprint('$ ctest')\nprint('100% tests passed, 0 tests failed out of 5')\n")
        self.assertEqual([s[0] for s in panel.steps], ["cmake build", "ctest"])
        self.assertEqual((code, panel.passed), (0, 5))

    def test_a_script_without_steps_is_one_step(self) -> None:
        panel, code, _ = self.wrap("print('just output')\n")
        self.assertEqual(code, 0)
        self.assertEqual(panel.steps[0][0], "run")

    def test_the_exit_code_of_the_script_is_kept_and_the_running_step_fails(self) -> None:
        panel, code, out = self.wrap("print('[1/2] Fine')\nprint('[2/2] Breaks')\nprint('the reason')\nraise SystemExit(3)\n")
        self.assertEqual(code, 3)
        self.assertEqual([(s[0], s[1]) for s in panel.steps], [("Fine", "ok"), ("Breaks", "fail")])
        self.assertIn("the reason", out)

    def test_a_failure_before_any_step_is_named(self) -> None:
        panel, code, _ = self.wrap("raise SystemExit(4)\n")
        self.assertEqual(code, 4)
        self.assertEqual(panel.steps[-1][1], "fail")

    def test_the_terminal_form(self) -> None:
        _, code, out = self.wrap("import time\nprint('[1/1] Slow')\ntime.sleep(0.4)\nprint('done')\n", tty=True)
        self.assertEqual(code, 0)
        self.assertIn("Slow", out)

    def test_a_missing_script_is_a_failed_start(self) -> None:
        panel = pr.Panel("DEMO", "build")
        panel.log_path = Path(tempfile.gettempdir()) / "pretty_panel_test.log"
        code, out = drawn(panel.wrap, ["armor-no-such-executable-xyz"])
        self.assertEqual(code, 1)
        self.assertIn("required executable was not found", out)


class WrapCommandLine(unittest.TestCase):
    def test_no_command_is_a_usage_error(self) -> None:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(pr._wrap_main(["--wrap"]), 2)
        self.assertIn("usage", err.getvalue())

    def test_the_name_and_version_come_from_the_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "x.project.json").write_text('{"name": "ARMOR-X", "version": "9.8.7", "ecosystem": "A.R.M.O.R."}', encoding="utf-8")
            (root / "run.py").write_text("print('[1/1] Only step')\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"CI": "1"}):
                code, out = drawn(pr._wrap_main, ["--wrap", "--mode", "test", "--", sys.executable, str(root / "run.py")])
        self.assertEqual(code, 0)
        self.assertIn("ARMOR-X", out)
        self.assertIn("v9.8.7", out)
        self.assertIn("TEST", out)

    def test_a_broken_manifest_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "x.project.json").write_text("{broken", encoding="utf-8")
            (root / "run.py").write_text("print('hi')\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"CI": "1"}):
                code, out = drawn(pr._wrap_main, ["--wrap", "--", sys.executable, str(root / "run.py")])
        self.assertEqual(code, 0)
        self.assertIn(root.name, out)


if __name__ == "__main__":
    unittest.main()
