"""The generators of the types and of the AsyncAPI document, and the check of the shared motion core, tried on small fixed inputs and in a throwaway folder: the type of each kind of field in
TypeScript and Kotlin, the three ways the command of each generator can end, and every way the copies of the motion core can differ. Nothing in the repository is written.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

import generate_asyncapi  # noqa: E402
import generate_types  # noqa: E402
import sync_motion_core  # noqa: E402


def field(name, schema, required=True, nested=None):
    return generate_types.Field(name, schema, required, nested)


class FieldTypeTests(unittest.TestCase):
    def test_typescript_types_of_every_kind_of_field(self):
        cases = [
            (field("a", {"const": "kind-x"}), '"kind-x"'),
            (field("a", {"enum": ["on", "off"]}), '"on" | "off"'),
            (field("a", {"type": "string"}), "string"),
            (field("a", {"type": "integer"}), "number"),
            (field("a", {"type": "number"}), "number"),
            (field("a", {"type": "boolean"}), "boolean"),
            (field("a", {"type": "array", "items": {"type": "string"}}), "string[]"),
            (field("a", {"type": "array", "items": {"type": "object"}}, nested="Item"), "Item[]"),
            (field("a", {"type": "array", "items": {"type": "array", "items": {"type": "integer"}}}), "number[][]"),
            (field("a", {"type": "array", "items": {"type": "wat"}}), "unknown[]"),
            (field("a", {"type": "object"}), "Record<string, unknown>"),
            (field("a", {"type": "object"}, nested="Box"), "Box"),
            (field("a", {"type": "object", "additionalProperties": {"type": "number"}}), "Record<string, number>"),
        ]
        for item, wanted in cases:
            with self.subTest(wanted=wanted):
                self.assertEqual(generate_types.ts_type(item), wanted)

    def test_kotlin_types_of_every_kind_of_field(self):
        cases = [
            (field("a", {"type": "string"}), "String"),
            (field("a", {"type": "integer"}), "Long"),
            (field("a", {"type": "number"}), "Double"),
            (field("a", {"type": "boolean"}), "Boolean"),
            (field("a", {"type": "array", "items": {"type": "string"}}), "List<String>"),
            (field("a", {"type": "array", "items": {"type": "object"}}, nested="Item"), "List<Item>"),
            (field("a", {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}), "List<List<Double>>"),
            (field("a", {"type": "array", "items": {"type": "wat"}}), "List<Any>"),
            (field("a", {"type": "object"}), "Map<String, Any>"),
            (field("a", {"type": "object"}, nested="Box"), "Box"),
            (field("a", {"type": "object", "additionalProperties": {"type": "integer"}}), "Map<String, Long>"),
        ]
        for item, wanted in cases:
            with self.subTest(wanted=wanted):
                self.assertEqual(generate_types.kt_type(item), wanted)

    def test_a_kotlin_property_has_a_default_only_when_it_is_fixed_or_optional(self):
        self.assertEqual(generate_types.kt_property(field("kind", {"type": "string", "const": "alarm"})), '    val kind: String = "alarm"')
        self.assertEqual(generate_types.kt_property(field("count", {"type": "integer"})), "    val count: Long")
        self.assertEqual(generate_types.kt_property(field("note", {"type": "string"}, required=False)), "    val note: String? = null")
        self.assertEqual(generate_types.kt_property(field("fixed", {"type": "string", "const": "x"}, required=False)), "    val fixed: String? = null")

    def test_a_name_that_is_a_kotlin_keyword_is_quoted_and_names_are_pascal_case(self):
        self.assertEqual(generate_types.kt_name("when"), "`when`")
        self.assertEqual(generate_types.kt_name("plain"), "plain")
        self.assertEqual(generate_types.pascal("node_health"), "NodeHealth")

    def test_the_fields_of_a_schema_know_which_are_required_and_which_are_nested(self):
        schema = {"required": ["a"], "properties": {"a": {"type": "string"}, "b": {"type": "object"}}}
        fields = generate_types.fields_of(schema, {"b": "BBox"})
        self.assertEqual([(item.name, item.required, item.nested) for item in fields], [("a", True, None), ("b", False, "BBox")])


class GeneratorCommandTests(unittest.TestCase):
    def run_main(self, module, *args, **patches):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), mock.patch.object(sys, "argv", [module.__name__, *args]):
            code = module.main()
        return code, out.getvalue(), err.getvalue()

    def test_types_are_written_then_found_current_then_found_stale_after_a_change(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "generated"
            with mock.patch.object(generate_types, "OUT", target):
                code, out, _err = self.run_main(generate_types, "--check")
                self.assertEqual(code, 1, "nothing written yet: stale")
                self.assertEqual(self.run_main(generate_types)[1].strip(), "generated types written")
                self.assertEqual(sorted(path.name for path in target.iterdir()), ["ArmorContracts.kt", "armor-contracts.ts", "armor_contracts.hpp"])
                code, out, _err = self.run_main(generate_types, "--check")
                self.assertEqual((code, out.strip()), (0, "generated types are current"))
                (target / "armor-contracts.ts").write_text("// edited by hand\n", encoding="utf-8")
                code, _out, err = self.run_main(generate_types, "--check")
                self.assertEqual(code, 1)
                self.assertIn("armor-contracts.ts", err)

    def test_the_asyncapi_document_is_written_then_current_then_stale(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "asyncapi" / "armor-mqtt.asyncapi.json"
            with mock.patch.object(generate_asyncapi, "OUT", target):
                self.assertEqual(self.run_main(generate_asyncapi, "--check")[0], 1, "a missing file is stale")
                self.assertEqual(self.run_main(generate_asyncapi)[1].strip(), "AsyncAPI written")
                self.assertEqual(self.run_main(generate_asyncapi)[1].strip(), "AsyncAPI is current")
                target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
                self.assertEqual(self.run_main(generate_asyncapi, "--check")[0], 0, "a checkout with another line ending is still current")
                target.write_text("{}", encoding="utf-8")
                code, _out, err = self.run_main(generate_asyncapi, "--check")
                self.assertEqual(code, 1)
                self.assertIn("out of date", err)

    def test_the_asyncapi_document_is_the_same_every_time_it_is_made(self):
        self.assertEqual(generate_asyncapi.render(), generate_asyncapi.render())
        self.assertEqual(generate_asyncapi.camel("node_health_report"), generate_asyncapi.camel("node_health_report"))


class MotionCoreTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.source = self.root / "ARMOR-COMMON" / "motion_core.py"
        self.source.parent.mkdir()
        self.source.write_text("MOTION = 1\nOTHER = 2\n", encoding="utf-8", newline="\n")
        self.targets = {"ARMOR-VISION": "src/motion_core.py", "ARMOR-SERVER-AI": "src/ai_motion.py"}
        original = sync_motion_core.drift   # its default folder was fixed when the module was read, so the command is pointed at the throwaway one
        patches = [mock.patch.object(sync_motion_core, "drift", lambda root=self.root: original(root)), mock.patch.object(sync_motion_core, "ROOT", self.root), mock.patch.object(sync_motion_core, "SOURCE", self.source), mock.patch.object(sync_motion_core, "TARGETS", self.targets)]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def copy(self, project, text="MOTION = 1\nOTHER = 2\n", newline="\n"):
        path = self.root / project / self.targets[project]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline=newline)

    def main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = sync_motion_core.main(["sync_motion_core.py", *args])
        return code, out.getvalue()

    def test_a_project_that_is_not_next_to_the_repository_is_skipped_not_failed(self):
        problems, absent = sync_motion_core.drift(self.root)
        self.assertEqual((problems, sorted(absent)), ([], ["ARMOR-SERVER-AI", "ARMOR-VISION"]))
        code, out = self.main()
        self.assertEqual(code, 0)
        self.assertIn("MOTION_CORE=PASS 0 copies identical", out)
        self.assertIn("skipped, not next to this repository: ARMOR-VISION", out)

    def test_a_missing_copy_and_a_copy_that_differs_are_both_reported(self):
        (self.root / "ARMOR-VISION").mkdir()
        self.copy("ARMOR-SERVER-AI", "MOTION = 99\n")
        problems, absent = sync_motion_core.drift(self.root)
        self.assertEqual(absent, [])
        self.assertEqual(problems, ["ARMOR-VISION: src/motion_core.py is missing", "ARMOR-SERVER-AI: src/ai_motion.py differs from the original"])
        code, out = self.main("check")
        self.assertEqual(code, 1)
        self.assertIn("MOTION_CORE=FAIL 2 copies drifted", out)

    def test_a_copy_with_windows_line_endings_is_the_same_copy(self):
        self.copy("ARMOR-VISION", newline="\r\n")
        self.copy("ARMOR-SERVER-AI")
        self.assertEqual(sync_motion_core.drift(self.root), ([], []))
        self.assertIn("MOTION_CORE=PASS 2 copies identical", self.main()[1])

    def test_sync_writes_the_original_into_each_copy_and_keeps_its_line_endings(self):
        self.copy("ARMOR-VISION", "OLD = 1\r\n", newline="")
        self.copy("ARMOR-SERVER-AI", "OLD = 1\n")
        code, out = self.main("sync")
        self.assertEqual(code, 0)
        self.assertIn("written: ARMOR-VISION/src/motion_core.py", out)
        self.assertEqual((self.root / "ARMOR-VISION" / "src" / "motion_core.py").read_bytes(), b"MOTION = 1\r\nOTHER = 2\r\n")
        self.assertEqual((self.root / "ARMOR-SERVER-AI" / "src" / "ai_motion.py").read_bytes(), b"MOTION = 1\nOTHER = 2\n")
        self.assertEqual(self.main("check")[0], 0)

    def test_an_unknown_command_prints_the_usage_and_changes_nothing(self):
        code, out = self.main("remove")
        self.assertEqual(code, 2)
        self.assertIn("usage:", out)


if __name__ == "__main__":
    unittest.main()
