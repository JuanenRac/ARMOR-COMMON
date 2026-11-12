"""The generated readers of the messages (C++ and TypeScript) are current, the pattern automaton agrees with Python's ``re``, and the seeded cases cover every schema with both verdicts."""
from __future__ import annotations

import json
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))
import generate_parsers   # noqa: E402
import generate_wire   # noqa: E402
import make_wire_cases   # noqa: E402
import wire_regex   # noqa: E402
from armor_common.schema import _ecma_pattern   # noqa: E402


def every_pattern() -> set[str]:
    found: set[str] = set()

    def walk(node) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "pattern" and isinstance(value, str):
                    found.add(value)
                elif key == "properties":
                    for child in value.values():
                        walk(child)
                else:
                    walk(value)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    for path in (ROOT / "src" / "armor_common" / "schemas").glob("*.schema.json"):
        walk(json.loads(path.read_text(encoding="utf-8")))
    return found


def sample(auto: wire_regex.Automaton, rnd: random.Random, limit: int = 90) -> str | None:
    """A text the automaton accepts, by a random walk (None when the walk runs out of steps)."""
    state, out = auto.start, []
    for _ in range(limit * 4):
        op, a, b = auto.states[state]
        if op == 2:
            return "".join(out)
        if op == 1:
            state = rnd.choice((a, b))
            continue
        negated, ranges = auto.sets[a]
        if negated:
            pool = [c for c in "aZ09-_.:@/ é\n\t" if not any(low <= ord(c) <= high for low, high in ranges)]
        else:
            pool = [chr(code) for low, high in ranges for code in range(low, min(high, low + 40) + 1)]
        if not pool:
            return None
        out.append(rnd.choice(pool))
        state = b
    return None


class GeneratedFilesAreCurrentTests(unittest.TestCase):
    def test_the_cpp_header_is_what_the_schemas_produce(self):
        for path in generate_wire.OUTPUTS:
            self.assertEqual(path.read_text(encoding="utf-8"), generate_wire.render_cpp(), "run python tools/generate_wire.py")

    def test_the_typescript_parsers_are_what_the_schemas_produce(self):
        self.assertEqual(generate_parsers.OUT.read_text(encoding="utf-8"), generate_parsers.render(), "run python tools/generate_parsers.py")

    def test_the_kotlin_parsers_are_what_the_schemas_produce(self):
        import generate_kotlin_parsers
        self.assertEqual(generate_kotlin_parsers.OUT.read_text(encoding="utf-8"), generate_kotlin_parsers.render(), "run python tools/generate_kotlin_parsers.py")

    def test_the_swift_readers_are_what_the_schemas_produce(self):
        import generate_swift_parsers
        self.assertEqual(generate_swift_parsers.OUT.read_text(encoding="utf-8"), generate_swift_parsers.render(), "run python tools/generate_swift_parsers.py")

    def test_every_schema_has_a_swift_reader_and_writer(self):
        import generate_swift_parsers
        import generate_types
        swift = generate_swift_parsers.OUT.read_text(encoding="utf-8")
        for path in (ROOT / "src" / "armor_common" / "schemas").glob("*.schema.json"):
            key = path.name[: -len(".schema.json")]
            self.assertIn(f'"{key}": #"', swift, key)
            self.assertIn(f'case "{key}": return parse', swift, key)
        for _key, (name, _declared) in generate_types.discover().items():
            self.assertIn(f"public static func parse{name}(", swift, name)
            self.assertIn(f"extension Contract.{name} {{", swift, name)

    def test_every_schema_has_a_reader_in_each_language(self):
        import generate_types
        kotlin = (ROOT / "generated" / "ArmorParsers.kt").read_text(encoding="utf-8")
        typescript = (ROOT / "generated" / "armor-parsers.ts").read_text(encoding="utf-8")
        cpp = (ROOT / "generated" / "armor_wire.hpp").read_text(encoding="utf-8")
        for path in (ROOT / "src" / "armor_common" / "schemas").glob("*.schema.json"):
            key = path.name[: -len(".schema.json")]
            self.assertIn(f'"{key}" to JSONObject(', kotlin, key)
            self.assertIn(f'"{key}": ', typescript, key)
            self.assertIn(f"inline bool validate_{key}(", cpp, key)
        for _key, (name, _declared) in generate_types.discover().items():
            self.assertIn(f"fun parse{name}(", kotlin, name)

    def test_the_cases_are_what_the_generator_writes(self):
        self.assertEqual(make_wire_cases.OUT.read_bytes().decode("utf-8"), make_wire_cases.render(), "run python tools/make_wire_cases.py")

    def test_the_generated_files_are_never_written_by_hand(self):
        for path in (ROOT / "generated" / "armor_wire.hpp", ROOT / "generated" / "armor-parsers.ts", ROOT / "generated" / "ArmorParsers.kt", ROOT / "generated" / "ArmorContract.swift"):
            self.assertIn("Do not edit", path.read_text(encoding="utf-8").splitlines()[0] + path.read_text(encoding="utf-8").splitlines()[1])


class PatternAutomatonTests(unittest.TestCase):
    def test_every_pattern_of_the_schemas_compiles(self):
        patterns = every_pattern()
        self.assertGreater(len(patterns), 30)
        for pattern in patterns:
            wire_regex.compile_pattern(pattern)

    def test_the_automaton_and_re_agree_on_texts_it_accepts_and_on_mutations_of_them(self):
        rnd = random.Random(7)
        for pattern in sorted(every_pattern()):
            auto = wire_regex.compile_pattern(pattern)
            expected = _ecma_pattern(pattern)
            accepted = 0
            for _ in range(200):
                text = sample(auto, rnd)
                if text is None:
                    continue
                accepted += 1
                self.assertIsNotNone(expected.search(text), (pattern, text))
                for mutated in (text[:-1], text + "a", text.upper(), text[1:] + text[:1], text + "\n", text.replace("-", "–")):
                    self.assertEqual(wire_regex.run(auto, mutated), expected.search(mutated) is not None, (pattern, mutated))
            self.assertGreater(accepted, 0, pattern)

    def test_a_pattern_the_firmware_could_not_honour_is_refused(self):
        for bad in ("abc", "^a(?=b)$", "^\\w+$", "^a++$", "^[a-z]{2,1}$", "^(a$"):
            with self.assertRaises(wire_regex.UnsupportedPattern, msg=bad):
                wire_regex.compile_pattern(bad)


class CasesTests(unittest.TestCase):
    def setUp(self):
        self.cases = [line.split("\t", 2) for line in make_wire_cases.OUT.read_bytes().decode("utf-8").splitlines()]

    def test_every_schema_with_conformance_vectors_has_valid_and_invalid_cases(self):
        verdicts: dict[str, set[str]] = {}
        for key, verdict, _text in self.cases:
            verdicts.setdefault(key, set()).add(verdict)
        for path in sorted((ROOT / "src" / "armor_common" / "schemas").glob("*.schema.json")):
            key = path.name[: -len(".schema.json")]
            if make_wire_cases.seeds_of(key):
                self.assertEqual(verdicts.get(key), {"0", "1"}, f"{key} needs valid and invalid cases")

    def test_no_case_has_a_raw_tab_or_line_break_in_its_document(self):
        for _key, _verdict, text in self.cases:
            json.loads(text)
            self.assertNotRegex(text, r"[\t\n\r]")

    def test_the_verdict_is_the_one_of_the_python_validator(self):
        from armor_common import schema as sc
        for key, verdict, text in self.cases[::17]:
            rule = json.loads((ROOT / "src" / "armor_common" / "schemas" / f"{key}.schema.json").read_text(encoding="utf-8"))
            try:
                sc.validate(json.loads(text), rule)
                ok = True
            except sc.SchemaError:
                ok = False
            self.assertEqual("1" if ok else "0", verdict, text[:120])


class RewriteComparisonTests(unittest.TestCase):
    def test_known_only_drops_what_the_schema_does_not_name(self):
        import check_wire_rewrites
        rule = {"properties": {"a": {"type": "integer"}, "b": {"type": "object", "properties": {"c": {"type": "string"}}}}}
        self.assertEqual(check_wire_rewrites.known_only({"a": 1, "x": 2, "b": {"c": "z", "d": 1}}, rule), {"a": 1, "b": {"c": "z"}})


if __name__ == "__main__":
    unittest.main()
