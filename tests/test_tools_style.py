"""tools/*.py: the shared tools are copied into every repository, so a style finding there would be copied too. Two rules are held without the linter."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"


def sources():
    for path in sorted(TOOLS.glob("*.py")):
        yield path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


class ToolsStyleTests(unittest.TestCase):
    def test_every_zip_says_whether_its_lengths_must_match(self):
        bad = []
        for path, tree in sources():
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "zip":
                    if not any(keyword.arg == "strict" for keyword in node.keywords):
                        bad.append(f"{path.name}:{node.lineno}")
        self.assertEqual(bad, [])

    def test_a_raise_inside_except_names_its_cause(self):
        bad = []
        for path, tree in sources():
            for handler in (n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)):
                for node in ast.walk(handler):
                    if isinstance(node, ast.Raise) and node.exc is not None and node.cause is None:
                        # re-raising the caught name itself (`raise error`) and SystemExit chains are the only accepted bare forms
                        if isinstance(node.exc, ast.Name) and node.exc.id == handler.name:
                            continue
                        bad.append(f"{path.name}:{node.lineno}")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
