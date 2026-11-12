"""The seeded wire cases (conformance/wire_cases.tsv) carry, for every message that has several valid vectors, one document that holds the optional members of all of them, so that the readers of
the nested parts of a message (the boot report of a node's health, a package of diagnostics, the stages of a battery) are tried by the host tests of the nodes and not only the ones the
vectors happen to give one by one.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import make_wire_cases as cases  # noqa: E402


class Union(unittest.TestCase):
    def test_members_of_both_documents_are_kept_and_the_first_wins_a_conflict(self) -> None:
        merged = cases.union({"a": 1, "n": {"x": 1}, "l": [{"p": 1}]}, {"a": 2, "b": 3, "n": {"y": 2}, "l": [{"q": 2}, {"r": 3}]})
        self.assertEqual(merged, {"a": 1, "b": 3, "n": {"x": 1, "y": 2}, "l": [{"p": 1, "q": 2}]})
        self.assertEqual(cases.union([1, 2], [9]), [1, 2])
        self.assertEqual(cases.union("a", {"b": 1}), "a")

    def test_the_inputs_are_not_changed(self) -> None:
        first, second = {"n": {"x": 1}}, {"n": {"y": [1]}}
        cases.union(first, second)
        self.assertEqual((first, second), ({"n": {"x": 1}}, {"n": {"y": [1]}}))


class TheFile(unittest.TestCase):
    def valid_documents(self, schema: str) -> list[dict]:
        out = []
        for line in (ROOT / "conformance" / "wire_cases.tsv").read_text(encoding="utf-8").splitlines():
            name, verdict, text = line.split("\t", 2)
            if name == schema and verdict == "1":
                out.append(json.loads(text))
        return out

    def test_a_health_report_with_every_optional_part_is_among_the_valid_cases(self) -> None:
        documents = self.valid_documents("node_health")
        with_everything = [d for d in documents if all(part in d for part in ("boot", "coredump", "sensors"))]
        self.assertTrue(with_everything, "no valid node_health case carries the boot report, the core dump and the sensors together")

    def test_every_message_with_several_vectors_has_a_valid_case_with_all_the_members_any_vector_has(self) -> None:
        for path in sorted((ROOT / "conformance").glob("*.json")):
            vectors = [v["payload"] for v in json.loads(path.read_text(encoding="utf-8")).get("vectors", []) if v.get("valid") and isinstance(v.get("payload"), dict)]
            if len(vectors) < 2 or not (cases.SCHEMAS / f"{path.stem}.schema.json").is_file():
                continue
            members = {name for vector in vectors if len(json.dumps(vector)) < cases.LARGEST // 4 for name in vector}
            documents = self.valid_documents(path.stem)
            self.assertTrue(any(members <= set(document) for document in documents), f"{path.stem}: no valid case has {sorted(members)}")


class EveryMember(unittest.TestCase):
    def documents(self) -> list[tuple[str, bool, dict]]:
        out = []
        for line in (ROOT / "conformance" / "wire_full_cases.tsv").read_text(encoding="utf-8").splitlines():
            name, verdict, text = line.split("	", 2)
            out.append((name, verdict == "1", json.loads(text)))
        return out

    def test_every_message_has_valid_documents_that_hold_every_member_the_schema_declares(self) -> None:
        by_name: dict[str, list[dict]] = {}
        for name, valid, document in self.documents():
            self.assertTrue(valid, f"{name}: a document with every member is not valid")
            by_name.setdefault(name, []).append(document)
        self.assertEqual(sorted(by_name), sorted(path.name[: -len(".schema.json")] for path in cases.SCHEMAS.glob("*.schema.json")))
        for name, documents in by_name.items():
            declared = set(cases.schema_for(name).get("properties", {}))
            self.assertTrue(any(declared <= set(document) for document in documents), f"{name}: no document has every member of the schema")
            for member in declared - set(cases.schema_for(name).get("required", [])):
                self.assertTrue(any(member in document for document in documents) and any(member not in document for document in documents), f"{name}: {member} is not both present and absent")

    def test_the_variants_differ_and_the_file_is_the_same_on_every_run(self) -> None:
        self.assertEqual(cases.render_full(), cases.render_full())
        self.assertEqual((ROOT / "conformance" / "wire_full_cases.tsv").read_bytes().decode("utf-8"), cases.render_full())
        texts = [json.dumps(document, sort_keys=True) for name, _valid, document in self.documents() if name == "solar_inverter"]
        self.assertGreater(len(set(texts)), 1)

    def test_a_pair_of_documents_with_half_of_the_optional_members_has_each_one_in_exactly_one(self) -> None:
        pool = cases.string_pool()
        schema = {"type": "object", "required": ["a"], "properties": {name: {"type": "integer"} for name in "abcdefgh"}}
        first = cases.full_value(schema, 0, pool, [0, 0], 0)
        second = cases.full_value(schema, 0, pool, [0, 0], 1)
        self.assertEqual(sorted(set(first) | set(second)), list("abcdefgh"))
        self.assertEqual(sorted(set(first) & set(second)), ["a"])
        self.assertEqual(sorted(cases.full_value(schema, 0, pool, [0, 0])), list("abcdefgh"))

    def test_a_value_is_found_for_each_kind_of_member(self) -> None:
        pool = cases.string_pool()
        self.assertIsNone(cases.full_value({"type": "string", "pattern": "^q{99}$"}, 0, pool, [0, 0]))
        self.assertEqual(cases.full_value({"const": 3}, 0, pool, [0, 0]), 3)
        self.assertEqual(cases.full_value({"type": "integer", "minimum": 5}, 0, pool, [0, 0]), 5)
        self.assertEqual(cases.full_value({"type": "number", "maximum": 2.5}, 0, pool, [0, 0]), 2.5)
        self.assertIn(cases.full_value({"type": "boolean"}, 0, pool, [0, 0]), (True, False))
        self.assertEqual(len(cases.full_value({"type": "array", "items": {"type": "integer"}, "minItems": 3}, 0, pool, [0, 0])), 3)
        self.assertEqual(len(cases.full_value({"type": "array", "items": {"type": "integer"}}, 1, pool, [0, 0])), 2)
        self.assertIsNone(cases.full_value({"type": "object", "required": ["a"], "properties": {"a": {"type": "string", "pattern": "^q{99}$"}}}, 0, pool, [0, 0]))
        self.assertEqual(cases.full_value({"type": "object", "properties": {"a": {"type": "string", "pattern": "^q{99}$"}, "b": {"type": "integer"}}}, 0, pool, [0, 0]), {"b": 1})
        mapped = cases.full_value({"type": "object", "additionalProperties": {"type": "integer"}, "propertyNames": {"pattern": "^[0-9]+$"}}, 0, pool, [0, 0])
        self.assertEqual(len(mapped), 1)
        self.assertEqual(cases.full_value({"type": "string", "minLength": 12}, 0, pool, [0, 0]), "x" * 12)
        self.assertIn(cases.full_value({"enum": ["a", "b"]}, 1, pool, [0, 0]), ("a", "b"))


if __name__ == "__main__":
    unittest.main()
