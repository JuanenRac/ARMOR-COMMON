import os
import subprocess
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import pretty_run  # noqa: E402


class CountTests(unittest.TestCase):
    def test_reads_what_each_runner_says(self):
        self.assertEqual(pretty_run.count_tests("ℹ tests 700\nℹ pass 698\nℹ fail 2\n"), (698, 2))
        self.assertEqual(pretty_run.count_tests(" Test Files  3 passed (3)\n      Tests  2 failed | 986 passed (988)\n"), (986, 2))
        self.assertEqual(pretty_run.count_tests("Ran 22 tests in 0.5s\n\nOK\n"), (22, 0))
        self.assertEqual(pretty_run.count_tests("Ran 22 tests in 0.5s\n\nFAILED (failures=2, errors=1)\n"), (19, 3))
        self.assertEqual(pretty_run.count_tests("============ 1 failed, 40 passed in 3.2s ============"), (40, 1))
        self.assertEqual(pretty_run.count_tests("100% tests passed, 0 tests failed out of 14"), (14, 0))
        self.assertEqual(pretty_run.count_tests("test result: ok. 115 passed; 0 failed; 0 ignored"), (115, 0))
        self.assertEqual(pretty_run.count_tests("nothing about tests here"), (0, 0))


class PanelRun(unittest.TestCase):
    def run_demo(self, code: str) -> subprocess.CompletedProcess[str]:
        script = (
            "import sys; sys.path.insert(0, %r)\nfrom pretty_run import Panel\n"
            "p = Panel('DEMO', 'build-test', '1.0')\np.banner()\n%s\nraise SystemExit(p.finish())\n" % (str(TOOLS), code)
        )
        return subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PRETTY_PLAIN": "1"}, check=False)

    def test_passing_steps_make_a_passing_panel_with_the_number_of_tests(self):
        done = self.run_demo("p.step('tests', [sys.executable, '-c', \"print('Ran 5 tests in 0.1s'); print('OK')\"], tests=True)\np.skip('browser', 'none here')")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("PASS", done.stdout)
        self.assertIn("5 tests passed", done.stdout)
        self.assertIn("skip browser", done.stdout)

    def test_a_failing_step_shows_its_output_and_fails_the_panel(self):
        done = self.run_demo("p.step('boom', [sys.executable, '-c', \"print('the reason'); raise SystemExit(3)\"])")
        self.assertEqual(done.returncode, 1)
        self.assertIn("FAIL", done.stdout)
        self.assertIn("the reason", done.stdout)

    def test_a_failure_that_is_not_a_command_counts_too(self):
        done = self.run_demo("p.fail('Workflow', 'a tool is missing')")
        self.assertEqual(done.returncode, 1)
        self.assertIn("a tool is missing", done.stdout)

    def test_a_missing_program_is_a_failed_step_not_a_crash(self):
        done = self.run_demo("p.step('missing', ['no-such-program-armor'])")
        self.assertEqual(done.returncode, 1)
        self.assertIn("was not found", done.stdout)


class WrapScript(unittest.TestCase):
    def wrapped(self, body: str) -> subprocess.CompletedProcess[str]:
        script = Path(__import__("tempfile").mkdtemp()) / "build.py"
        script.write_text(body, encoding="utf-8")
        return subprocess.run([sys.executable, str(TOOLS / "pretty_run.py"), "--wrap", "--mode", "build", "--", sys.executable, str(script)], capture_output=True, text=True, encoding="utf-8",
                              env={**os.environ, "PRETTY_PLAIN": "1", "PRETTY_PAUSE": "0"}, check=False)

    def test_the_marked_lines_of_a_script_become_its_steps(self):
        done = self.wrapped("print('banner'); print('[1/2] Reading the version'); print('[2/2] Running the tests'); print('Ran 7 tests in 0.1s'); print('OK')")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("Reading the version", done.stdout)
        self.assertIn("Running the tests", done.stdout)
        self.assertIn("7 tests passed", done.stdout)
        self.assertNotIn("banner", done.stdout)

    def test_the_step_that_was_running_when_the_script_failed_is_the_failed_one(self):
        done = self.wrapped("print('[1/2] First'); print('[2/2] Second'); print('the reason'); raise SystemExit(4)")
        self.assertEqual(done.returncode, 4)
        self.assertIn("FAIL Second", done.stdout)
        self.assertIn("the reason", done.stdout)

    def test_command_lines_are_the_steps_of_a_script_without_marks(self):
        done = self.wrapped("print('+ npm run typecheck'); print('fine'); print('+ npm test'); print('Tests  3 passed (3)')")
        self.assertEqual(done.returncode, 0)
        self.assertIn("npm run typecheck", done.stdout)
        self.assertIn("3 tests passed", done.stdout)


if __name__ == "__main__":
    unittest.main()
