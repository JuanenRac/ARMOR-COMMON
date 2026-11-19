"""tools/status_lights.py: the ceiling of every light of the Project status table, from the manifest and the files of the repository."""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOL = Path(__file__).resolve().parents[1] / "tools" / "status_lights.py"
spec = importlib.util.spec_from_file_location("status_lights", TOOL)
status_lights = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status_lights)

G, Y, O, R = status_lights.GREEN, status_lights.YELLOW, status_lights.ORANGE, status_lights.RED
NAMES = ("README.md", "README_spa.md", "README_fra.md", "README_ita.md", "README_deu.md", "README_zho.md", "README_jpn.md", "README_por.md")


def readme(lights, word="Hardware") -> str:
    rows = [("Software", lights[0]), ("Tests", lights[1]), (word, lights[2]), ("Integration", lights[3]), ("Documentation", lights[4])]
    body = "\n".join(f"| {label} | {light} | A sentence that stays, with a | not at the end. |" for label, light in rows)
    return f"# X\n\n## \U0001F6A6 Project status\n\nlegend\n\n| Area | State | What it means |\n|---|---|---|\n{body}\n\n## Overview\n\ntext\n"


def make_repo(root: Path, lights, maturity="established", evidence="bench", extra=None, tests=True, ci=True) -> Path:
    repo = root / "ARMOR-TEST"
    repo.mkdir()
    manifest = {"name": "ARMOR-TEST", "maturity": maturity, "evidence": evidence}
    manifest.update(extra or {})
    (repo / "armor.project.json").write_text(json.dumps(manifest), encoding="utf-8")
    for name in NAMES:
        (repo / name).write_bytes(readme(lights).encode("utf-8"))
    if tests:
        (repo / "tests").mkdir()
        (repo / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
    if ci:
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")
    return repo


class Kinds(unittest.TestCase):
    def test_kind_of_a_label(self):
        self.assertEqual(status_lights.kind_of("Real hardware"), "hardware")
        self.assertEqual(status_lights.kind_of("Hardware"), "hardware")
        self.assertEqual(status_lights.kind_of("Integration"), "integration")
        self.assertEqual(status_lights.kind_of("Tests"), "tests")
        self.assertEqual(status_lights.kind_of("Documentation"), "docs")
        self.assertEqual(status_lights.kind_of("Software"), "software")
        self.assertEqual(status_lights.kind_of("Security"), "security")
        self.assertEqual(status_lights.kind_of("Updates"), "updates")
        self.assertEqual(status_lights.kind_of("Writing to equipment"), "writing")
        self.assertEqual(status_lights.kind_of("Deployment"), "other")


class Ceilings(unittest.TestCase):
    def test_evidence_limits_hardware_and_integration(self):
        for evidence, top in (("none", O), ("host-test", O), ("simulator", O), ("bench", Y), ("field", G)):
            self.assertEqual(status_lights.ceiling("hardware", {"evidence": evidence}, True, True, "unknown")[0], top, evidence)
            self.assertEqual(status_lights.ceiling("integration", {"evidence": evidence}, True, True, "unknown")[0], top, evidence)

    def test_security_updates_writing_share_the_hardware_ceiling_when_bound(self):
        for kind in ("security", "updates", "writing"):
            for evidence, top in (("none", O), ("host-test", O), ("simulator", O), ("bench", Y)):
                self.assertEqual(status_lights.ceiling(kind, {"evidence": evidence}, True, True, "green")[0], top, (kind, evidence))
            self.assertEqual(status_lights.ceiling(kind, {}, True, True, "green")[0], O, kind)
        for kind in ("updates", "writing"):
            self.assertEqual(status_lights.ceiling(kind, {"evidence": "field"}, True, True, "green")[0], G)

    def test_security_is_never_green_even_with_field_evidence_or_no_hardware(self):
        self.assertEqual(status_lights.ceiling("security", {"evidence": "field"}, True, True, "green")[0], Y)
        self.assertEqual(status_lights.ceiling("security", {"evidence": "field", "hardware_bound": False}, True, True, "green")[0], Y)
        self.assertEqual(status_lights.ceiling("security", {"evidence": "none", "hardware_bound": False}, True, True, "green")[0], Y)

    def test_updates_and_writing_without_hardware_are_not_limited_by_evidence(self):
        for kind in ("updates", "writing"):
            self.assertEqual(status_lights.ceiling(kind, {"evidence": "none", "hardware_bound": False}, True, True, "green")[0], G)

    def test_a_simulator_manifest_lowers_security_to_orange_in_the_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, O, O, G], evidence="simulator")
            for name in NAMES:
                path = repo / name
                text = path.read_text(encoding="utf-8").replace("| Integration |", "| Security | " + Y + " | s |\n| Updates | " + G + " | u |\n| Integration |", 1)
                path.write_text(text.replace("\\n", "\n"), encoding="utf-8")
            problems = status_lights.run_in_ci(repo)
            self.assertEqual(len(problems), 2)
            self.assertTrue(any("Security" in p for p in problems) and any("Updates" in p for p in problems))
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            self.assertEqual(status_lights.run_in_ci(repo), [])
            self.assertIn("| Security | " + O + " |", (repo / "README_por.md").read_text(encoding="utf-8"))

    def test_evidence_does_not_limit_software(self):
        self.assertEqual(status_lights.ceiling("software", {"evidence": "none"}, True, True, "green")[0], G)

    def test_a_repository_without_hardware_is_not_limited_by_evidence(self):
        self.assertEqual(status_lights.ceiling("integration", {"evidence": "host-test", "hardware_bound": False}, True, True, "unknown")[0], G)

    def test_software_tests_docs_need_tests_and_a_ci(self):
        for kind in ("software", "tests", "docs"):
            self.assertEqual(status_lights.ceiling(kind, {}, False, True, "green")[0], Y)
            self.assertEqual(status_lights.ceiling(kind, {}, True, False, "green")[0], Y)
            self.assertEqual(status_lights.ceiling(kind, {}, True, True, "red")[0], Y)
            self.assertEqual(status_lights.ceiling(kind, {}, True, True, "green")[0], G)

    def test_low_maturity_limits_everything_to_yellow(self):
        for maturity in ("scaffolding", "experimental", "alpha"):
            for kind in ("software", "tests", "docs", "hardware", "other"):
                self.assertEqual(status_lights.ceiling(kind, {"maturity": maturity, "evidence": "field"}, True, True, "green")[0], Y)


class Check(unittest.TestCase):
    def test_a_false_green_fails_the_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            problems = status_lights.run_in_ci(repo)
            self.assertEqual(len(problems), 2)
            self.assertTrue(any("Hardware" in p for p in problems) and any("Integration" in p for p in problems))

    def test_lights_within_the_ceilings_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, Y, Y, G], evidence="bench")
            self.assertEqual(status_lights.run_in_ci(repo), [])

    def test_a_missing_or_unknown_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, O, O, G])
            manifest = repo / "armor.project.json"
            manifest.write_text(json.dumps({"name": "x", "maturity": "established"}), encoding="utf-8")
            self.assertTrue(any("no 'evidence'" in p for p in status_lights.run_in_ci(repo)))
            manifest.write_text(json.dumps({"name": "x", "maturity": "established", "evidence": "magic"}), encoding="utf-8")
            self.assertTrue(any("magic" in p for p in status_lights.run_in_ci(repo)))

    def test_translations_with_other_lights_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, O, O, G])
            (repo / "README_por.md").write_bytes(readme([G, G, R, O, G]).encode("utf-8"))
            self.assertTrue(any("README_por.md" in p for p in status_lights.run_in_ci(repo)))

    def test_no_tests_caps_the_software_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, O, O, G], tests=False)
            self.assertEqual(len(status_lights.run_in_ci(repo)), 3)


class Apply(unittest.TestCase):
    def test_apply_lowers_only_the_light_in_the_eight_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="simulator")
            before = (repo / "README.md").read_text(encoding="utf-8")
            self.assertEqual(status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"]), 0)
            for name in NAMES:
                after = (repo / name).read_text(encoding="utf-8")
                self.assertEqual(after, readme([G, G, O, O, G]))
            self.assertEqual(before.replace(G, "").replace(O, ""), (repo / "README.md").read_text(encoding="utf-8").replace(G, "").replace(O, ""))
            self.assertEqual(status_lights.run_in_ci(repo), [])

    def test_apply_never_raises_without_the_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [Y, Y, R, R, Y], evidence="field")
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            self.assertEqual((repo / "README.md").read_text(encoding="utf-8"), readme([Y, Y, R, R, Y]))
            status_lights.main(["--apply", "--raise", "--repo", str(repo), "--ci", "off"])
            self.assertEqual((repo / "README.md").read_text(encoding="utf-8"), readme([Y, Y, O, O, Y]))

    def test_apply_keeps_line_endings(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            for name in NAMES:
                path = repo / name
                path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            data = (repo / "README.md").read_bytes()
            self.assertEqual(data.count(b"\r\n"), data.count(b"\n"))

    def test_apply_patches_the_source_of_the_armor_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            source = Path(tmp) / "ARMOR-DOCS" / "tools" / "readme_src" / "repos"
            source.mkdir(parents=True)
            text = 'FACTS = {\n  "status": [\n    [\n      "software",\n      "green",\n    ],\n    [\n      "tests",\n      "green",\n    ],\n    [\n      "hardware",\n      "green",\n    ],\n    [\n      "integration",\n      "green",\n    ],\n    [\n      "docs",\n      "green",\n    ],\n  ],\n}\n'
            (source / "ARMOR_TEST.py").write_text(text, encoding="utf-8")
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            self.assertEqual((source / "ARMOR_TEST.py").read_text(encoding="utf-8"), text.replace('"hardware",\n      "green"', '"hardware",\n      "orange"').replace('"integration",\n      "green"', '"integration",\n      "orange"'))

    def test_apply_patches_a_source_written_with_single_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            source = Path(tmp) / "ARMOR-DOCS" / "tools" / "readme_src" / "repos"
            source.mkdir(parents=True)
            text = "FACTS = {\n 'status': [['software', 'green'],\n            ['tests', 'green'],\n            ['hardware', 'green'],\n            ['integration', 'green'],\n            ['docs', 'green']],\n 'other': {'status': {'software': 'green words'}},\n}\n"
            (source / "ARMOR_TEST.py").write_text(text, encoding="utf-8")
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            self.assertEqual((source / "ARMOR_TEST.py").read_text(encoding="utf-8"), text.replace("['hardware', 'green']", "['hardware', 'orange']").replace("['integration', 'green']", "['integration', 'orange']"))

    def test_apply_patches_the_sections_of_the_urtc_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, G, G, G], evidence="host-test")
            repo = repo.rename(Path(tmp) / "URTC-TEST")
            spec = Path(tmp) / "URTC-COMMON" / "spec" / "readme"
            spec.mkdir(parents=True)
            body = readme([G, G, G, G, G]).split("\n## Overview")[0].split("legend\n\n", 1)[1]
            data = {"sections": [{"id": "status_test", "repos": ["URTC-TEST"], "body": {"english": body, "spanish": body}}]}
            (spec / "sections.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            status_lights.main(["--apply", "--repo", str(repo), "--ci", "off"])
            after = json.loads((spec / "sections.json").read_text(encoding="utf-8"))
            for text in after["sections"][0]["body"].values():
                self.assertEqual(text, body.replace("| Hardware | " + G, "| Hardware | " + O).replace("| Integration | " + G, "| Integration | " + O))

    def test_suggest_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [Y, Y, R, R, Y], evidence="field")
            before = (repo / "README.md").read_bytes()
            self.assertEqual(status_lights.main(["--suggest", "--repo", str(repo), "--ci", "off"]), 0)
            self.assertEqual(before, (repo / "README.md").read_bytes())


class WhiteLightTests(unittest.TestCase):
    """A line that does not apply is white, and white is never a step of the scale; green on the hardware line of a repository with no hardware is refused."""

    def problems(self, manifest, light):
        state = {"manifest": manifest, "items": [{"index": 0, "label": "Hardware", "kind": "hardware", "light": light, "ceiling": status_lights.GREEN, "why": "no limit"}]}
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            return status_lights.problems_of(Path(tmp) / "ARMOR-DEMO", state)

    def test_white_has_a_name_and_is_not_on_the_scale(self):
        self.assertEqual(status_lights.NAMES["white"], status_lights.WHITE)
        self.assertNotIn(status_lights.WHITE, status_lights.ORDER)

    def test_no_hardware_may_be_white_and_never_green(self):
        unbound = {"maturity": "functional", "evidence": "none", "hardware_bound": False}
        self.assertEqual(self.problems(unbound, status_lights.WHITE), [])
        self.assertTrue(any("never green" in line for line in self.problems(unbound, status_lights.GREEN)))

    def test_white_is_refused_where_hardware_applies(self):
        bound = {"maturity": "functional", "evidence": "field"}
        self.assertTrue(any("hardware_bound" in line for line in self.problems(bound, status_lights.WHITE)))


class StrictEvidenceTests(unittest.TestCase):
    """--strict-evidence: a manifest that claims bench or field evidence cannot keep a red Hardware row."""

    def run_check(self, lights, strict, **fields):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), lights, **fields)
            return status_lights.run_in_ci(repo, strict)

    def test_it_is_off_by_default(self):
        self.assertEqual(self.run_check([G, G, R, O, G], None, evidence="bench"), [])
        self.assertEqual(self.run_check([G, G, R, O, G], False, evidence="bench"), [])

    def test_bench_with_a_red_hardware_row_fails_when_strict(self):
        problems = self.run_check([G, G, R, O, G], True, evidence="bench")
        self.assertEqual(len(problems), 1)
        self.assertIn("evidence is bench", problems[0])
        self.assertTrue(self.run_check([G, G, R, O, G], True, evidence="field"))

    def test_lower_evidence_or_a_row_that_is_not_red_passes_when_strict(self):
        self.assertEqual(self.run_check([G, G, R, O, G], True, evidence="simulator"), [])
        self.assertEqual(self.run_check([G, G, O, O, G], True, evidence="bench"), [])
        self.assertEqual(self.run_check([G, G, R, O, G], True, evidence="bench", extra={"hardware_bound": False}), [])

    def test_the_environment_switches_it_on(self):
        with mock.patch.dict(os.environ, {"ARMOR_STRICT_EVIDENCE": "1"}):
            self.assertTrue(self.run_check([G, G, R, O, G], None, evidence="bench"))
        with mock.patch.dict(os.environ, {"ARMOR_STRICT_EVIDENCE": "0"}):
            self.assertEqual(self.run_check([G, G, R, O, G], None, evidence="bench"), [])

    def test_a_state_without_a_manifest_has_no_contradiction(self):
        self.assertEqual(status_lights.evidence_contradictions(Path("ARMOR-X"), {"items": []}), [])

    def test_the_command_line_flag_and_the_suggestion(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(Path(tmp), [G, G, R, O, G], evidence="bench")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(status_lights.main(["--check", "--repo", str(repo)]), 0)
                self.assertEqual(status_lights.main(["--check", "--strict-evidence", "--repo", str(repo)]), 1)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                status_lights.main(["--suggest", "--repo", str(repo)])
            self.assertIn("evidence is bench", out.getvalue())


if __name__ == "__main__":
    unittest.main()
