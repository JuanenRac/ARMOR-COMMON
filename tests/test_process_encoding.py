# =============================================================================
# ARMOR-COMMON - tests/test_process_encoding.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D)
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The shared tools read what a child process writes as UTF-8: text mode without an encoding reads with the code page of Windows."""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {name: ROOT / "tools" / (name + ".py") for name in ("status_lights", "sync_manifests", "universal_readme_check")}


def load(name: str):
    spec = importlib.util.spec_from_file_location("encoding_" + name, SOURCES[name])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def text_calls_without_encoding(source: str) -> list[int]:
    """The lines where a process is started in text mode without saying which encoding."""
    lines = []
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "Popen", "check_output"}):
            continue
        keywords = {k.arg: k.value for k in node.keywords}
        given = [keywords.get(name) for name in ("text", "universal_newlines")]
        text_mode = any(isinstance(value, ast.Constant) and value.value is True for value in given)
        if text_mode and not {"encoding", "errors"} <= set(keywords):
            lines.append(node.lineno)
    return lines


class ProcessEncodingTests(unittest.TestCase):
    def test_the_scan_finds_a_call_without_encoding(self):
        self.assertEqual(text_calls_without_encoding("import subprocess\nsubprocess.run(['x'], text=True)\n"), [2])

    def test_the_shared_tools_name_the_encoding_of_what_they_read(self):
        found = {name: text_calls_without_encoding(path.read_text(encoding="utf-8")) for name, path in SOURCES.items()}
        self.assertEqual({name: lines for name, lines in found.items() if lines}, {})


class SharedRowsTests(unittest.TestCase):
    """The Security, Updates and Writing rows have their own ceiling only in an A.R.M.O.R. repository."""

    def kinds(self, manifest_name: str) -> list[str]:
        status_lights = load("status_lights")
        rows = "| Security | x | s |\n| Updates | x | u |\n| Writing | x | w |\n"
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / manifest_name).write_text(json.dumps({"evidence": "none"}), encoding="utf-8")
            (repo / "README.md").write_text("## \U0001F6A6 Project status\n\n| Area | State | Note |\n|---|---|---|\n" + rows, encoding="utf-8")
            return [item["kind"] for item in status_lights.evaluate(repo, "off")["items"]]

    def test_an_armor_repository_reads_them(self):
        self.assertEqual(self.kinds("armor.project.json"), ["security", "updates", "writing"])

    def test_the_other_families_leave_them_as_other(self):
        for name in ("urtc.project.json", "hydra-umc.project.json"):
            self.assertEqual(self.kinds(name), ["other", "other", "other"], name)


class StrictEvidenceTests(unittest.TestCase):
    def test_strict_evidence_is_off_unless_asked_for(self):
        sync_manifests = load("sync_manifests")
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(sync_manifests.strict_evidence_default())
        with mock.patch.dict(os.environ, {"ARMOR_STRICT_EVIDENCE": "1"}):
            self.assertTrue(sync_manifests.strict_evidence_default())


if __name__ == "__main__":
    unittest.main()
