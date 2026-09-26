"""The tool that keeps the firmware the node projects share identical (tools/sync_firmware_base.py), tried on stand-in projects in a temporary folder."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "sync_firmware_base.py"
spec = importlib.util.spec_from_file_location("sync_firmware_base", TOOL)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def source(project: str, extra: str = "") -> str:
    names = tool.PROJECTS[project]
    return (f"// {names[0]} - the link to the broker of the {names[3]} node\n#include \"core/{names[3]}_config.hpp\"\nconstexpr char kTag[] = \"{names[1]}\";\n"
            f"namespace {names[2]} {{}}\n{extra}")


class Fixture:
    """Three stand-in projects in a temporary folder, and the base directory redirected there."""

    def __init__(self, test: unittest.TestCase):
        self.dir = tempfile.TemporaryDirectory()
        test.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.saved = (tool.BASE_DIR, tool.MANIFEST)
        tool.BASE_DIR = self.root / "base"
        tool.MANIFEST = tool.BASE_DIR / "manifest.json"
        test.addCleanup(lambda: setattr(tool, "BASE_DIR", self.saved[0]) or setattr(tool, "MANIFEST", self.saved[1]))
        tool.BASE_DIR.mkdir(parents=True)

    def put(self, project: str, relative: str, text: str, crlf: bool = False) -> Path:
        path = self.root / project / tool.project_path(project, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
        return path


class NamesTests(unittest.TestCase):
    def test_a_projects_name_becomes_placeholders_and_comes_back(self):
        for project in tool.PROJECTS:
            text = source(project)
            base = tool.to_base(text, project)
            self.assertNotIn(tool.PROJECTS[project][0], base)
            for placeholder in tool.PLACEHOLDERS:
                self.assertIn(placeholder, base)
            self.assertEqual(tool.from_base(base, project), text)
        # the same file of two projects is the same base
        self.assertEqual(tool.to_base(source("ARMOR-SOLAR"), "ARMOR-SOLAR"), tool.to_base(source("ARMOR-RADAR"), "ARMOR-RADAR"))

    def test_line_endings_do_not_matter(self):
        self.assertEqual(tool.to_base("ARMOR-SOLAR\r\nsolar\r\n", "ARMOR-SOLAR"), "@PROJECT@\n@kind@\n")

    def test_the_radar_keeps_its_core_inside_main(self):
        self.assertEqual(tool.project_path("ARMOR-RADAR", "core/auth.hpp"), "main/core/auth.hpp")
        self.assertEqual(tool.project_path("ARMOR-SOLAR", "core/auth.hpp"), "core/auth.hpp")
        self.assertEqual(tool.project_path("ARMOR-RADAR", "main/entropy.cpp"), "main/entropy.cpp")


class ImportTests(unittest.TestCase):
    def test_what_is_identical_is_shared_and_what_differs_is_not(self):
        fx = Fixture(self)
        for project in tool.PROJECTS:
            fx.put(project, "main/entropy.cpp", source(project))                       # identical in the three
        fx.put("ARMOR-SOLAR", "main/network.cpp", source("ARMOR-SOLAR"))
        fx.put("ARMOR-ELECTRICAL", "main/network.cpp", source("ARMOR-ELECTRICAL"))
        fx.put("ARMOR-RADAR", "main/network.cpp", source("ARMOR-RADAR", "// the radar bridges the cable\n"))   # the radar's own
        fx.put("ARMOR-SOLAR", "main/web_server.cpp", source("ARMOR-SOLAR", "a\n"))
        fx.put("ARMOR-ELECTRICAL", "main/web_server.cpp", source("ARMOR-ELECTRICAL", "b\n"))                     # all different
        fx.put("ARMOR-SOLAR", "core/auth.hpp", source("ARMOR-SOLAR"))                                              # in one project only
        fx.put("ARMOR-RADAR", "core/net_text.hpp", source("ARMOR-RADAR"), crlf=True)                              # the radar's in main/core
        fx.put("ARMOR-SOLAR", "core/net_text.hpp", source("ARMOR-SOLAR"), crlf=True)
        self.assertEqual(tool.do_import(fx.root), 0)
        manifest = json.loads(tool.MANIFEST.read_text(encoding="utf-8"))["files"]
        self.assertEqual(sorted(manifest["main/entropy.cpp"]["targets"]), sorted(tool.PROJECTS))
        self.assertEqual(sorted(manifest["main/network.cpp"]["targets"]), ["ARMOR-ELECTRICAL", "ARMOR-SOLAR"])
        self.assertNotIn("main/web_server.cpp", manifest)
        self.assertNotIn("core/auth.hpp", manifest)
        self.assertEqual(manifest["core/net_text.hpp"]["targets"]["ARMOR-RADAR"], "main/core/net_text.hpp")
        self.assertIn("@PROJECT@", (tool.BASE_DIR / "main" / "entropy.cpp").read_text(encoding="utf-8"))
        self.assertEqual(tool.do_check(fx.root), 0)


class CheckAndSyncTests(unittest.TestCase):
    def shared(self) -> Fixture:
        fx = Fixture(self)
        for project in tool.PROJECTS:
            fx.put(project, "main/entropy.cpp", source(project), crlf=True)
        tool.do_import(fx.root)
        return fx

    def test_a_fix_made_in_one_project_only_is_found_and_put_right(self):
        fx = self.shared()
        self.assertEqual(tool.drift(fx.root), [])
        path = fx.root / "ARMOR-SOLAR" / "main" / "entropy.cpp"
        path.write_bytes(path.read_bytes() + b"// a fix in one project only\r\n")
        found = tool.drift(fx.root)
        self.assertEqual(found, ["ARMOR-SOLAR: main/entropy.cpp differs from the base"])
        self.assertEqual(tool.do_check(fx.root), 1)
        self.assertEqual(tool.do_sync(fx.root), 0)
        self.assertEqual(tool.drift(fx.root), [])
        self.assertNotIn(b"a fix in one project only", path.read_bytes())

    def test_a_change_in_the_base_reaches_every_project_with_its_own_name(self):
        fx = self.shared()
        base = tool.BASE_DIR / "main" / "entropy.cpp"
        base.write_text(base.read_text(encoding="utf-8") + "// @PROJECT@ says hello from the @kind@ node\n", encoding="utf-8")
        self.assertEqual(len(tool.drift(fx.root)), 3)
        tool.do_sync(fx.root)
        self.assertEqual(tool.drift(fx.root), [])
        for project, names in tool.PROJECTS.items():
            text = (fx.root / project / "main" / "entropy.cpp").read_text(encoding="utf-8")
            self.assertIn(f"// {names[0]} says hello from the {names[3]} node", text)

    def test_the_line_endings_of_a_checkout_are_kept(self):
        fx = self.shared()
        path = fx.root / "ARMOR-RADAR" / "main" / "entropy.cpp"
        self.assertIn(b"\r\n", path.read_bytes())
        lf = fx.root / "ARMOR-SOLAR" / "main" / "entropy.cpp"
        lf.write_bytes(lf.read_bytes().replace(b"\r\n", b"\n"))          # a checkout with LF
        base = tool.BASE_DIR / "main" / "entropy.cpp"
        base.write_text(base.read_text(encoding="utf-8") + "// more\n", encoding="utf-8")
        tool.do_sync(fx.root)
        self.assertIn(b"\r\n", path.read_bytes())
        self.assertNotIn(b"\r\n", lf.read_bytes())

    def test_a_missing_copy_is_reported(self):
        fx = self.shared()
        (fx.root / "ARMOR-ELECTRICAL" / "main" / "entropy.cpp").unlink()
        self.assertEqual(tool.drift(fx.root), ["ARMOR-ELECTRICAL: main/entropy.cpp is missing"])
        tool.do_sync(fx.root)
        self.assertEqual(tool.drift(fx.root), [])


class RealProjectsTests(unittest.TestCase):
    def test_the_real_copies_match_the_base(self):
        real_base = TOOL.parent.parent / "firmware_base"
        if not (real_base / "manifest.json").exists() or not all((TOOL.parents[2] / project).is_dir() for project in tool.PROJECTS):
            self.skipTest("the node projects are not checked out next to ARMOR-COMMON")
        saved = (tool.BASE_DIR, tool.MANIFEST)
        tool.BASE_DIR, tool.MANIFEST = real_base, real_base / "manifest.json"
        try:
            self.assertEqual(tool.drift(TOOL.parents[2]), [])
        finally:
            tool.BASE_DIR, tool.MANIFEST = saved


if __name__ == "__main__":
    unittest.main()
