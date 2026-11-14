"""armor-contract-check: the command that an emitter repository runs to check its messages and vectors without a ../ path."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from armor_common import contract_check

ROOT = Path(__file__).resolve().parents[1]


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = contract_check.main(argv)
    return code, out.getvalue(), err.getvalue()


class ContractCheckTests(unittest.TestCase):
    def test_the_shared_vectors_pass_their_own_check(self):
        code, out, err = run(["vectors", str(ROOT / "conformance")])
        self.assertEqual(code, 0, err)
        self.assertIn("VECTORS=PASS", out)

    def test_a_vector_file_that_lies_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "health.json"
            file.write_text(json.dumps({"kind": "health", "vectors": [
                {"name": "accepted but marked refused", "valid": False, "payload": {"node_id": "north-1", "timestamp_ms": 5, "online": True}},
                {"name": "refused but marked accepted", "valid": True, "payload": {"node_id": "north-1"}},
            ]}), encoding="utf-8")
            code, out, err = run(["vectors", str(file)])
        self.assertEqual(code, 1)
        self.assertIn("must be refused", err)
        self.assertIn("must be accepted", err)
        self.assertIn("VECTORS=FAIL", out)

    def test_a_file_that_is_not_a_vector_file_is_a_problem_not_a_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "x.json"
            file.write_text("[1, 2", encoding="utf-8")
            code, _, err = run(["vectors", str(file)])
        self.assertEqual(code, 1)
        self.assertIn("not a vector file", err)

    def test_a_message_is_accepted_or_refused_by_its_topic(self):
        with tempfile.TemporaryDirectory() as folder:
            good = Path(folder) / "good.json"
            good.write_text(json.dumps({"node_id": "north-1", "timestamp_ms": 5, "online": True}), encoding="utf-8")
            bad = Path(folder) / "bad.json"
            bad.write_text(json.dumps({"node_id": "other", "timestamp_ms": 5, "online": True}), encoding="utf-8")
            self.assertEqual(run(["message", "armor/node/north-1/health", str(good)])[0], 0)
            code, _, err = run(["message", "armor/node/north-1/health", str(bad)])
            self.assertEqual(code, 1)
            self.assertIn("REFUSED", err)
            self.assertEqual(run(["message", "armor/node/x/health", str(Path(folder) / "missing.json")])[0], 2)

    def test_the_kinds_are_the_schemas_that_exist(self):
        code, out, _ = run(["kinds"])
        self.assertEqual(code, 0)
        self.assertEqual(out.split(), sorted(path.name[: -len(".schema.json")] for path in (ROOT / "src" / "armor_common" / "schemas").glob("*.schema.json")))

    def test_the_matrix_counts_the_shared_vectors_and_marks_a_pin_that_is_behind(self):
        rows = contract_check.matrix_rows(ROOT / "conformance")
        health = next(row for row in rows if row["kind"] == "health")
        self.assertGreater(health["accepted_vectors"], 0)
        self.assertGreater(health["refused_vectors"], 0)
        text = contract_check.render_markdown(rows, [{"name": "A", "checked_against": "0.8.0.6"}, {"name": "B", "checked_against": "0.8.0.7"}], "0.8.0.7")
        self.assertIn("| A | 0.8.0.6 | behind |", text)
        self.assertIn("| B | 0.8.0.7 | current |", text)

    def test_the_matrix_file_is_what_the_command_writes(self):
        code, _, err = run(["matrix", "--check", str(ROOT / "docs" / "CONTRACT_MATRIX.md")])
        self.assertEqual(code, 0, err)

    def test_a_usage_error_exits_with_two(self):
        self.assertEqual(run([])[0], 2)


if __name__ == "__main__":
    unittest.main()
