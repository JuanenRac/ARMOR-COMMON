"""The fuzz targets of the firmware parsers exist, have seeds and a workflow, and (where clang with libFuzzer is installed) survive a few seconds of fuzzing."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ("fuzz_json", "fuzz_ble_frame", "fuzz_improv")


class FuzzTargets(unittest.TestCase):
    def test_every_target_has_source_and_seeds(self):
        for target in TARGETS:
            self.assertTrue((ROOT / "fuzz" / f"{target}.cpp").is_file(), target)
            self.assertTrue(any((ROOT / "fuzz" / "corpus" / target).iterdir()), f"no seeds for {target}")

    def test_workflow_runs_the_script(self):
        text = (ROOT / ".github" / "workflows" / "fuzz.yml").read_text(encoding="utf-8")
        self.assertIn("fuzz/run_fuzz.sh", text)

    @unittest.skipUnless(sys.platform.startswith("linux") and shutil.which("clang++") and shutil.which("bash"), "needs clang with libFuzzer on Linux")
    def test_a_few_seconds_of_fuzzing_find_nothing(self):
        with tempfile.TemporaryDirectory() as build:
            result = subprocess.run(["bash", str(ROOT / "fuzz" / "run_fuzz.sh"), "3"], env={**os.environ, "FUZZ_BUILD_DIR": build}, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
