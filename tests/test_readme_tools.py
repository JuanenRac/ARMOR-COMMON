"""Tests of the shared README pictures: tools/make_architecture.py, tools/make_structure.py and the kit they share.

They use the fixture under tests/fixtures/readme_tools/voice_ai (a copy of the specifications of a small repository),
copied into a temporary directory together with stand-ins for the files the specifications point to.
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import _readme_svg as K  # noqa: E402
import make_architecture as A  # noqa: E402
import make_structure as S  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "readme_tools" / "voice_ai"
STRUCTURE_FILES = [
    "src/armor_voice_ai/phrases.py", "src/armor_voice_ai/intent.py", "src/armor_voice_ai/confirmation.py",
    "src/armor_voice_ai/silence_policy.py", "src/armor_voice_ai/session.py", "src/armor_voice_ai/gateway.py",
    "src/armor_voice_ai/service.py", "src/armor_voice_ai/turn.py", "tests/test_a.py", "docs/SAFETY.md", "docs/SERVICE.md",
    "docs/SILENCE_POLICY.md", "tools/x.py", "images/a.svg", ".github/workflows/ci.yml", "armor.project.json", "pyproject.toml",
    "CHANGELOG.md", "run.sh", "run.bat", "build.sh", "build.bat", "SECURITY.md", "SUPPORT.md", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md", "LICENSE", "README.md", ".gitignore",
]


def make_repo() -> Path:
    base = Path(tempfile.mkdtemp(prefix="readme_tools_test_"))
    shutil.copytree(FIXTURE / "docs", base / "docs")
    for rel in STRUCTURE_FILES:
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text("x\n", encoding="utf-8")
    code = base / "src" / "armor_voice_ai"
    (code / "turn.py").write_text("BUDGET = 9\n", encoding="utf-8")
    return base


class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(shutil.rmtree, self.repo, True)
        self.spec = A.load_spec(self.repo / "docs" / "architecture.json")

    def test_builds_a_valid_svg_of_the_promised_size(self):
        svg = A.build_svg(self.spec)
        root = K.validate_xml(svg)
        self.assertEqual(root.get("viewBox"), "0 0 1200 640")
        self.assertIn("ARMOR-VOICE-AI architecture", svg)
        self.assertEqual(svg, A.build_svg(self.spec), "the same JSON always gives the same picture")

    def test_motion_is_smil_and_there_are_no_icons_or_images(self):
        svg = A.build_svg(self.spec)
        self.assertIn("<animate ", svg)
        self.assertIn("<animateMotion", svg)
        for forbidden in ("<image", "<use", "<script", "foreignObject"):
            self.assertNotIn(forbidden, svg)

    def test_write_then_check_passes_and_changes_are_caught(self):
        self.assertEqual(A.run(self.repo, False, None), 0)
        self.assertEqual(A.run(self.repo, True, None), 0)
        spec_file = self.repo / "docs" / "architecture.json"
        changed = copy.deepcopy(self.spec)
        changed["nodes"][2]["lines"][0] = "something else entirely"
        spec_file.write_text(json.dumps(changed), encoding="utf-8")
        self.assertEqual(A.run(self.repo, True, None), 1, "a changed JSON makes the picture stale")

    def test_check_fails_when_the_code_the_box_points_to_changes(self):
        self.assertEqual(A.run(self.repo, False, None), 0)
        changed = copy.deepcopy(self.spec)
        changed["nodes"][2]["code"] = ["src/armor_voice_ai/turn.py::BUDGET = 9"]
        (self.repo / "docs" / "architecture.json").write_text(json.dumps(changed), encoding="utf-8")
        self.assertEqual(A.run(self.repo, False, None), 0)
        self.assertEqual(A.run(self.repo, True, None), 0)
        (self.repo / "src" / "armor_voice_ai" / "turn.py").write_text("BUDGET = 12\n", encoding="utf-8")
        self.assertEqual(A.run(self.repo, True, None), 1, "the text the box states is gone from the code")
        (self.repo / "src" / "armor_voice_ai" / "turn.py").unlink()
        self.assertEqual(A.run(self.repo, True, None), 1, "the file is gone")

    def test_too_many_boxes_or_bad_edges_or_text_that_does_not_fit_are_refused(self):
        many = copy.deepcopy(self.spec)
        many["nodes"] += [{"id": f"x{i}", "column": 2, "title": "x"} for i in range(8)]
        with self.assertRaises(A.SpecError):
            A.validate_spec(many)
        across = copy.deepcopy(self.spec)
        across["edges"].append({"from": "panel", "to": "engines"})
        with self.assertRaises(A.SpecError):
            A.validate_spec(across)
        long_line = copy.deepcopy(self.spec)
        long_line["nodes"][2]["lines"][0] = "a very long sentence that cannot possibly fit inside a box of this size at all"
        with self.assertRaises(ValueError):
            A.build_svg(long_line)
        no_repo = copy.deepcopy(self.spec)
        for n in no_repo["nodes"]:
            n["column"] = 0 if n["column"] == 1 else n["column"]
        with self.assertRaises(A.SpecError):
            A.validate_spec(no_repo)

    def test_every_ecosystem_has_a_palette(self):
        for name in K.PALETTES:
            spec = copy.deepcopy(self.spec)
            spec["ecosystem"] = name
            K.validate_xml(A.build_svg(spec))
        spec = copy.deepcopy(self.spec)
        spec["ecosystem"] = "other"
        with self.assertRaises(ValueError):
            A.validate_spec(spec)


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        self.addCleanup(shutil.rmtree, self.repo, True)
        self.spec = S.load_spec(self.repo / "docs" / "structure.json")

    def test_tree_is_aligned_and_the_same_names_in_every_language(self):
        trees = {lang: S.render_tree(self.spec, lang) for lang in K.LANGUAGES}
        names = {lang: [line.split("  ")[0] for line in tree.splitlines()] for lang, tree in trees.items()}
        self.assertEqual(len({tuple(v) for v in names.values()}), 1)
        lines = trees["en"].splitlines()
        self.assertEqual(lines[0], "ARMOR-VOICE-AI/")
        self.assertTrue(lines[1].startswith("├── src/armor_voice_ai/"))
        self.assertTrue(lines[-1].startswith("└── SECURITY.md"))
        columns = {len(line) - len(line.split("   ", 1)[1].lstrip()) for line in lines[2:10]}
        self.assertEqual(len(columns), 1, "the descriptions start in one column")

    def test_a_language_without_a_description_is_refused(self):
        broken = copy.deepcopy(self.spec)
        broken["cards"][1]["sub"].pop("fr")
        with self.assertRaises(S.SpecError):
            S.build_svg(broken, "fr")

    def test_svg_is_valid_and_deterministic_in_every_language(self):
        for lang in K.LANGUAGES:
            svg = S.build_svg(self.spec, lang)
            K.validate_xml(svg)
            self.assertEqual(svg, S.build_svg(self.spec, lang))
        self.assertIn("リポジトリ構造", S.build_svg(self.spec, "ja"))

    def test_write_then_check_and_the_disk_is_compared(self):
        self.assertEqual(S.run(self.repo, False, False, None, None, None), 0)
        self.assertEqual(S.run(self.repo, True, False, None, None, None), 0)
        (self.repo / "NEWFOLDER").mkdir()
        (self.repo / "NEWFOLDER" / "a.txt").write_text("x", encoding="utf-8")
        self.assertEqual(S.run(self.repo, True, False, None, None, None), 1, "an entry the tree does not list")
        shutil.rmtree(self.repo / "NEWFOLDER")
        self.assertEqual(S.run(self.repo, True, False, None, None, None), 0)
        (self.repo / "src" / "armor_voice_ai" / "turn.py").unlink()
        self.assertEqual(S.run(self.repo, True, False, None, None, None), 1, "a file the tree lists is gone")

    def test_readmes_must_carry_the_tree_of_their_language(self):
        S.run(self.repo, False, False, None, None, None)
        for lang in K.LANGUAGES:
            (self.repo / K.README_NAME[lang]).write_text("## Structure\n\n```text\n" + S.render_tree(self.spec, lang) + "\n```\n", encoding="utf-8")
        self.assertEqual(S.run(self.repo, True, True, None, None, None), 0)
        (self.repo / "README_spa.md").write_text("## Estructura\n", encoding="utf-8")
        self.assertEqual(S.run(self.repo, True, True, None, None, None), 1)

    def test_a_text_that_does_not_fit_stops_the_build(self):
        long_row = copy.deepcopy(self.spec)
        long_row["cards"][0]["rows"][0]["desc"] = "x" * 200
        with self.assertRaises(ValueError):
            S.build_svg(long_row, "en")


class KitTests(unittest.TestCase):
    def test_overlapping_texts_and_texts_outside_their_card_are_reported(self):
        canvas = K.Canvas(400, 200)
        canvas.text(40, 50, "first line of text", 14, "#fff")
        canvas.text(45, 52, "overlaps the first", 14, "#fff")
        canvas.text(100, 120, "out of its card", 14, "#fff", bound=(90, 100, 60, 40))
        problems = canvas.problems()
        self.assertTrue(any("overlap" in p for p in problems))
        self.assertTrue(any("leaves its card" in p for p in problems))

    def test_cjk_is_measured_wider_than_latin(self):
        self.assertGreater(K.text_width("リポジトリ", 12), K.text_width("abcde", 12) * 1.5)

    def test_wrap_refuses_what_cannot_fit(self):
        self.assertEqual(K.wrap("stdin / stdout", 10.5, 60), ["stdin /", "stdout"])
        with self.assertRaises(ValueError):
            K.wrap("a b c d e f g h i j k l m n o p", 10.5, 30)


@unittest.skipUnless(K.find_edge(), "Edge is not installed here")
class RenderTests(unittest.TestCase):
    def test_both_pictures_render_to_a_real_screenshot(self):
        repo = make_repo()
        self.addCleanup(shutil.rmtree, repo, True)
        A.run(repo, False, None)
        S.run(repo, False, False, None, None, None)
        for svg, height in ((repo / "images" / "architecture.svg", 640), (repo / "images" / "repository-structure.svg", 984)):
            png = repo / (svg.stem + ".png")
            self.assertTrue(K.render_png(svg, png, 1200, height))
            self.assertGreater(png.stat().st_size, 20000, "a blank page would be far smaller")


if __name__ == "__main__":
    unittest.main()
