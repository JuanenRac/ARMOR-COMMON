"""tools/universal_readme_check.py: the 22-section layout of the README, in the eight languages."""
from __future__ import annotations

import importlib.util
import io
import os
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "universal_readme_check.py"
spec = importlib.util.spec_from_file_location("universal_readme_check", TOOL)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

LIGHT_ROW = "| Software | 🟢 | Works. |"


def readme(language: str, file: str, omit=(), swap=None, rename=None, extra="", tests="12") -> str:
    """A small README that follows the layout, in one language."""
    names = tool.NAMES[language]
    bar = " | ".join(f"[{name}]({name})" if name != file else f"**{name}**" for _, name in tool.LANGUAGE_FILES)
    out = [f'<p align="center">\n  <img src="images/BANNER.svg" alt="banner">\n</p>\n\n# Demo\n\n{bar}\n\n### One line.\n\n'
           f'<img src="https://img.shields.io/badge/Tests-{tests}%20passing-green.svg" alt="Tests">\n\n---\n\nHonest.\n\n---\n']
    order = [s for s in tool.ORDER if s not in omit and s != "screenshots"]
    if swap:
        a, b = order.index(swap[0]), order.index(swap[1])
        order[a], order[b] = order[b], order[a]
    for section in order:
        title = (rename or {}).get(section, names[section])
        if section == "role":
            title = "Role in A.R.M.O.R." if language == "en" else names["role"]
        icon = dict(tool.SECTIONS)[section]
        body = {
            "glance": f"| | |\n|---|---|\n| Tests | {tests} |\n\n**Jump to:** [Overview](#overview) · [Testing](#testing)",
            "status": f"| Area | State | Note |\n|---|---|---|\n{LIGHT_ROW}",
            "architecture": '<img src="images/architecture.svg" alt="architecture">',
        }.get(section, "text")
        out.append(f"## {icon} {title}\n\n{body}\n")
    if extra:
        out.insert(2, extra + "\n")
    return "\n".join(out)


def write_repo(directory: Path, **options) -> Path:
    for language, file in tool.LANGUAGE_FILES:
        (directory / file).write_text(readme(language, file, **options), encoding="utf-8")
    return directory


class LayoutTests(unittest.TestCase):
    def check(self, **options) -> list[str]:
        with tempfile.TemporaryDirectory() as folder:
            return tool.check_repository(write_repo(Path(folder), **options))

    def test_a_readme_in_the_layout_passes_in_all_eight_languages(self):
        self.assertEqual(self.check(), [])

    def test_the_layout_has_22_sections_and_14_are_required(self):
        self.assertEqual(len(tool.SECTIONS), 22)
        self.assertEqual(len(tool.REQUIRED), 14)
        for language in tool.NAMES:
            self.assertEqual(list(tool.NAMES[language]), tool.ORDER)

    def test_a_missing_required_section_is_reported_in_every_language(self):
        problems = self.check(omit=("roadmap",))
        self.assertEqual(len([p for p in problems if "required section missing: Roadmap" in p]), 8)

    def test_an_optional_section_may_be_left_out(self):
        self.assertEqual(self.check(omit=("security", "interfaces", "build")), [])

    def test_sections_out_of_order_are_reported(self):
        self.assertTrue(any("out of order" in p for p in self.check(swap=("overview", "role"))))

    def test_a_wrong_name_is_reported(self):
        problems = self.check(rename={"overview": "Introduction"})
        self.assertTrue(any("'Introduction', it must be 'Overview'" in p for p in problems))

    def test_status_must_be_second_and_author_license_last(self):
        problems = self.check(swap=("status", "overview"))
        self.assertTrue(any("Project status must be the second" in p for p in problems))
        self.assertTrue(any("out of order" in p for p in problems))

    def test_a_date_the_version_rule_and_a_private_reference_are_reported(self):
        problems = self.check(extra="Built on 2026-10-29. The ecosystem odo" + "meter. See SON" + "NET notes. Report H-1 UBAS-MEJ-001.")
        text = "\n".join(problems)
        self.assertIn("it has a date", text)
        self.assertIn("mentions the version rule", text)
        self.assertIn("private document", text)

    def test_ordinary_technical_words_are_not_private(self):
        self.assertEqual(self.check(extra="Signed with HMAC-SHA-256 and AES-GCM-128; sections 1.2.3."), [])

    def test_a_missing_translation_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            write_repo(Path(folder))
            (Path(folder) / "README_por.md").unlink()
            self.assertIn("README_por.md: missing", tool.check_repository(Path(folder)))

    def test_a_translation_with_another_sequence_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            root = write_repo(Path(folder))
            (root / "README_deu.md").write_text(readme("de", "README_deu.md", omit=("security",)), encoding="utf-8")
            self.assertTrue(any("README_deu.md: the sequence of sections differs" in p for p in tool.check_repository(root)))

    def test_the_badge_and_the_glance_table_must_agree_on_the_tests(self):
        with tempfile.TemporaryDirectory() as folder:
            root = write_repo(Path(folder), tests="12")
            text = (root / "README.md").read_text(encoding="utf-8").replace("| Tests | 12 |", "| Tests | 13 |")
            (root / "README.md").write_text(text, encoding="utf-8")
            self.assertTrue(any("number of tests differs" in p for p in tool.check_repository(root)))

    def test_a_heading_inside_a_code_block_is_not_a_section(self):
        parsed = tool.Readme("# T\n\n## 📋 At a glance\n\n```\n## 🎯 not a section\n```\n")
        self.assertEqual([s["id"] for s in parsed.sections], ["glance"])

    def test_no_architecture_diagram_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            root = write_repo(Path(folder))
            for _, file in tool.LANGUAGE_FILES:
                text = (root / file).read_text(encoding="utf-8").replace('<img src="images/architecture.svg" alt="architecture">', "text")
                (root / file).write_text(text, encoding="utf-8")
            self.assertTrue(any("no diagram image" in p for p in tool.check_repository(root)))

    def test_run_compares_the_tests_that_really_run_with_the_readme(self):
        with tempfile.TemporaryDirectory() as folder:
            root = write_repo(Path(folder), tests="2")
            (root / "tests").mkdir()
            (root / "tests" / "test_a.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n    def test_b(self): pass\n", encoding="utf-8")
            self.assertEqual(tool.check_repository(root, run=True), [])
            wrong = write_repo(root, tests="9")
            self.assertTrue(any("states [9] tests and the suite ran 2" in p for p in tool.check_repository(wrong, run=True)))


class VerdictTests(unittest.TestCase):
    def test_warn_mode_never_fails_and_strict_mode_does(self):
        stream = io.StringIO()
        self.assertEqual(tool.report(["a: wrong"], strict=False, stream=stream), 0)
        self.assertIn("UNIVERSAL_README=WARN 1", stream.getvalue())
        stream = io.StringIO()
        self.assertEqual(tool.report(["a: wrong"], strict=True, stream=stream), 1)
        self.assertIn("UNIVERSAL_README=FAIL 1", stream.getvalue())
        stream = io.StringIO()
        self.assertEqual(tool.report([], strict=True, stream=stream), 0)
        self.assertIn("UNIVERSAL_README=PASS", stream.getvalue())

    def test_the_environment_can_switch_the_mode_for_one_run(self):
        saved = os.environ.get("UNIVERSAL_README_STRICT")
        try:
            os.environ["UNIVERSAL_README_STRICT"] = "1"
            self.assertTrue(tool.strict_requested(False))
            os.environ["UNIVERSAL_README_STRICT"] = "0"
            self.assertFalse(tool.strict_requested(True))
            del os.environ["UNIVERSAL_README_STRICT"]
            self.assertTrue(tool.strict_requested(True))
        finally:
            if saved is not None:
                os.environ["UNIVERSAL_README_STRICT"] = saved

    def test_the_family_comes_from_the_name_of_the_repository(self):
        for name, family in (("ARMOR-SERVER", "ARMOR"), ("URTC-FLASHER", "URTC"), ("HYDRA-UMC-SDK", "HYDRA"), ("EH3D-DOCS", "EH3D"),
                             ("ELECTRO-HOBBY-3D-UPDATER", "EH3D"), ("other", "")):
            self.assertEqual(tool.family_of(Path(name)), family)

    def test_the_ci_hook_fails_only_for_a_strict_family_and_never_crashes(self):
        saved = dict(tool.FAMILY_STRICT)
        tool.FAMILY_STRICT["ARMOR"] = False
        try:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder) / "ARMOR-DEMO"
                root.mkdir()
                write_repo(root, omit=("roadmap",))
                self.assertEqual(tool.run_in_ci(root), [])
                tool.FAMILY_STRICT["ARMOR"] = True
                self.assertEqual(len(tool.run_in_ci(root)), 1)
                write_repo(root)
                self.assertEqual(tool.run_in_ci(root), [])
                self.assertEqual(tool.run_in_ci(Path(folder) / "missing"), [] if not tool.FAMILY_STRICT["ARMOR"] else tool.run_in_ci(Path(folder) / "missing"))
        finally:
            tool.FAMILY_STRICT.update(saved)

    def test_a_long_list_is_cut_but_counted(self):
        stream = io.StringIO()
        tool.report([f"x{i}" for i in range(30)], limit=5, stream=stream)
        self.assertIn("WARN 30", stream.getvalue())
        self.assertIn("and 25 more", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
