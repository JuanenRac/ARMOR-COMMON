"""armor-contract-check, the cases a normal run never reaches: a vector without its fields, a conformance folder with a broken file, a matrix that is out of date, a folder with no vectors."""
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


class VectorFileGaps(unittest.TestCase):
    def test_a_vector_without_its_fields_is_named_and_the_others_are_still_checked(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "health.json"
            file.write_text(json.dumps({"kind": "health", "vectors": [
                {"name": "no payload", "valid": True},
                {"payload": {"node_id": "north-1", "timestamp_ms": 5, "online": True}},
                "not even an object",
                {"name": "fine", "valid": True, "payload": {"node_id": "north-1", "timestamp_ms": 5, "online": True}},
            ]}), encoding="utf-8")
            checked, problems = contract_check.check_vector_file(file)
        self.assertEqual(checked, 4)
        self.assertEqual(len(problems), 3)
        self.assertIn("'no payload' needs 'valid' and 'payload'", problems[0])
        self.assertIn("'#1' needs", problems[1])
        self.assertIn("'#2' needs", problems[2])

    def test_a_file_without_a_kind_or_a_vector_list_is_not_a_vector_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            for index, body in enumerate(['{"vectors": []}', '{"kind": "health"}', "[]", "null"]):
                file = Path(folder) / f"{index}.json"
                file.write_text(body, encoding="utf-8")
                checked, problems = contract_check.check_vector_file(file)
                self.assertEqual(checked, 0, body)
                self.assertIn("not a vector file", problems[0], body)
            checked, problems = contract_check.check_vector_file(Path(folder) / "missing.json")
            self.assertEqual((checked, len(problems)), (0, 1))

    def test_a_folder_with_no_vector_files_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            code, _, err = run(["vectors", folder])
        self.assertEqual(code, 2)
        self.assertIn("no vector files found", err)

    def test_a_folder_is_read_in_the_order_of_its_names(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            for name in ("b.json", "a.json", "c.txt"):
                (Path(folder) / name).write_text("{}", encoding="utf-8")
            files = contract_check.collect_vector_files([folder])
        self.assertEqual([file.name for file in files], ["a.json", "b.json"])

    def test_a_message_that_is_not_json_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "m.json"
            file.write_text("{not json", encoding="utf-8")
            code, _, err = run(["message", "armor/node/north-1/health", str(file)])
        self.assertEqual(code, 2)
        self.assertIn("cannot read the message", err)


class MatrixGaps(unittest.TestCase):
    def test_without_a_conformance_folder_every_kind_has_no_vectors(self) -> None:
        rows = contract_check.matrix_rows(None)
        self.assertEqual([row["kind"] for row in rows], contract_check.kinds())
        for row in rows:
            self.assertEqual((row["accepted_vectors"], row["refused_vectors"]), (0, 0), row["kind"])

    def test_a_broken_file_in_the_conformance_folder_is_skipped_not_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "broken.json").write_text("{", encoding="utf-8")
            (root / "list.json").write_text("[]", encoding="utf-8")
            (root / "bad_vectors.json").write_text(json.dumps({"kind": "health", "vectors": [1, 2]}), encoding="utf-8")
            (root / "good.json").write_text(json.dumps({"kind": "health", "vectors": [{"valid": True}, {"valid": True}, {"valid": False}]}), encoding="utf-8")
            rows = contract_check.matrix_rows(root)
        health = next(row for row in rows if row["kind"] == "health")
        self.assertEqual((health["accepted_vectors"], health["refused_vectors"]), (2, 1))

    def test_a_matrix_file_that_is_out_of_date_or_missing_fails_the_check(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder) / "old.md"
            old.write_text("# old\n", encoding="utf-8")
            code, out, err = run(["matrix", "--check", str(old)])
            self.assertEqual((code, out), (1, ""))
            self.assertIn("is out of date", err)
            code, _, err = run(["matrix", "--check", str(Path(folder) / "missing.md")])
            self.assertEqual(code, 1)
            self.assertIn("is out of date", err)

    def test_the_matrix_is_written_as_markdown_or_as_json(self) -> None:
        code, out, _ = run(["matrix", "--markdown"])
        self.assertEqual(code, 0)
        self.assertIn("health", out)
        self.assertGreater(len(out.splitlines()), len(contract_check.kinds()))
        code, out, _ = run(["matrix"])
        document = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual([row["kind"] for row in document["kinds"]], contract_check.kinds())
        self.assertEqual(document["consumers"], [])

    def test_with_the_consumers_the_matrix_also_says_which_pin_is_behind(self) -> None:
        code, out, err = run(["matrix", "--consumers"])
        self.assertEqual(code, 0, err)
        consumers = json.loads(out)["consumers"]
        self.assertEqual(consumers, json.loads((ROOT / "registry" / "compat.json").read_text(encoding="utf-8"))["consumers"])


if __name__ == "__main__":
    unittest.main()
