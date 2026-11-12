"""The generator of the conformance vectors (tools/make_conformance.py) run in its --check mode inside the test process: every file it writes (the vectors of each message kind, the multipart
voice turns and the signed alarm states) must be what is committed, and the run must say so. Before this, only the workflow of the repository ran the check, so the unit tests (and their measure of
coverage) never reached the generator.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later."""
from __future__ import annotations

import contextlib
import io
import runpy
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class ConformanceFilesAreCurrent(unittest.TestCase):
    def test_the_committed_vectors_are_what_the_generator_writes(self) -> None:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["make_conformance.py", "--check"]), mock.patch.object(sys, "path", [str(ROOT / "tools"), *sys.path]), contextlib.redirect_stdout(out):
            try:
                runpy.run_path(str(ROOT / "tools" / "make_conformance.py"), run_name="make_conformance_under_test")
            except SystemExit as stop:
                self.fail(f"the committed vectors are stale: {out.getvalue()} (exit {stop.code})")
        self.assertRegex(out.getvalue(), r"CONFORMANCE=PASS \d+ files are current")


if __name__ == "__main__":
    unittest.main()
