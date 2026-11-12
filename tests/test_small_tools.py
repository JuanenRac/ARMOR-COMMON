"""The small tools of ARMOR-COMMON that no other test ran: the generator of the port constants, the check of the pins of the consumers (its commands, not only its verdict) and
the comparison of what a node writes back with what the contract keeps. Each runs on copies, in a temporary folder.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


ports = load("generate_ports")
pins = load("contract_pins")
rewrites = load("check_wire_rewrites")


def captured(function, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = function(*args)
    return code, out.getvalue(), err.getvalue()


class GeneratedPorts(unittest.TestCase):
    DATA = {"ports": {"server_http": {"port": 18080}, "mqtt_broker": {"port": 1883}}}

    def test_the_four_files_carry_every_port_in_the_syntax_of_their_language(self):
        files = ports.render(self.DATA)
        self.assertEqual(set(files), {"armor-ports.ts", "ArmorPorts.kt", "armor_ports.hpp", "armor-ports.env"})
        self.assertIn("  server_http: 18080,", files["armor-ports.ts"])
        self.assertIn("const val MQTT_BROKER: Int = 1883", files["ArmorPorts.kt"])
        self.assertIn("inline constexpr int kServerHttp = 18080;", files["armor_ports.hpp"])
        self.assertIn("ARMOR_PORT_SERVER_HTTP=18080", files["armor-ports.env"])
        for text in files.values():
            self.assertIn("Do not edit", text)

    def test_words_are_capitalised_per_part(self):
        self.assertEqual(ports._words("server_http_tls"), "ServerHttpTls")
        self.assertEqual(ports._words("x"), "X")

    def test_the_generated_files_of_the_repository_are_current(self):
        with mock.patch.object(sys, "argv", ["generate_ports.py", "--check"]):
            self.assertEqual(captured(ports.main)[0], 0)

    def test_check_names_a_file_that_is_out_of_date_and_write_makes_it_current(self):
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(ports, "OUT", Path(folder)):
            with mock.patch.object(sys, "argv", ["generate_ports.py", "--check"]):
                code, _, err = captured(ports.main)
            self.assertEqual(code, 1)
            self.assertIn("armor-ports.ts", err)
            with mock.patch.object(sys, "argv", ["generate_ports.py"]):
                self.assertEqual(captured(ports.main)[0], 0)
            with mock.patch.object(sys, "argv", ["generate_ports.py", "--check"]):
                self.assertEqual(captured(ports.main)[0], 0)
            (Path(folder) / "ArmorPorts.kt").write_text("tampered", encoding="utf-8")
            with mock.patch.object(sys, "argv", ["generate_ports.py", "--check"]):
                code, _, err = captured(ports.main)
            self.assertEqual((code, "ArmorPorts.kt" in err), (1, True))

    def test_a_registry_that_is_wrong_is_refused_before_anything_is_written(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "ports.json"
            source.write_text(json.dumps({"ports": {"a": {"port": 80}, "b": {"port": 80}}}), encoding="utf-8")
            with mock.patch.object(ports, "SOURCE", source), mock.patch.object(ports, "OUT", Path(folder) / "out"), mock.patch.object(sys, "argv", ["generate_ports.py"]):
                code, _, err = captured(ports.main)
            self.assertEqual(code, 1)
            self.assertIn("ports.json is wrong", err)
            self.assertFalse((Path(folder) / "out").exists())


class ContractPins(unittest.TestCase):
    def fixture(self, folder: str, consumers: dict, version: str = "0.8.1.0", known: tuple[str, ...] = ("ARMOR-A", "ARMOR-B")) -> None:
        root = Path(folder)
        (root / "registry").mkdir()
        (root / "registry" / "contract_pins.json").write_text(json.dumps({"consumers": consumers}), encoding="utf-8")
        (root / "registry" / "repositories.json").write_text(json.dumps({"repositories": [{"name": "ARMOR-COMMON"}, *({"name": n} for n in known)]}), encoding="utf-8")
        (root / "armor.project.json").write_text(json.dumps({"version": version}), encoding="utf-8")

    def patched(self, folder: str):
        root = Path(folder)
        return mock.patch.multiple(pins, ROOT=root, PINS=root / "registry" / "contract_pins.json")

    def test_every_kind_of_problem_is_named(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder, {"ARMOR-A": "0.8.9.0", "ARMOR-Z": "0.8.0.0", "ARMOR-B": "x.y"}, known=("ARMOR-A", "ARMOR-B", "ARMOR-C"))
            with self.patched(folder):
                found = pins.problems()
        self.assertIn("ARMOR-A: pinned to 0.8.9.0, above the current 0.8.1.0", found)
        self.assertIn("ARMOR-Z is not a consumer of the registry", found)
        self.assertIn("ARMOR-B: 'x.y' is not a version", found)
        self.assertIn("ARMOR-C has no pin", found)

    def test_a_clean_table_passes_and_the_command_says_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder, {"ARMOR-A": "0.8.1.0", "ARMOR-B": "0.8.0.9"})
            with self.patched(folder):
                self.assertEqual(captured(pins.main, [])[0], 0)

    def test_the_command_fails_and_prints_each_problem(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder, {"ARMOR-A": "0.8.1.0"})
            with self.patched(folder):
                code, _, err = captured(pins.main, [])
        self.assertEqual(code, 1)
        self.assertIn("ARMOR-B has no pin", err)

    def test_behind_lists_the_consumers_pinned_below_the_current_version(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder, {"ARMOR-A": "0.8.1.0", "ARMOR-B": "0.8.0.9"})
            with self.patched(folder):
                code, out, _ = captured(pins.main, ["--behind"])
        self.assertEqual((code, out.strip()), (0, "ARMOR-B 0.8.0.9 < 0.8.1.0"))

    def test_set_pins_the_named_repositories_to_the_current_version_and_refuses_an_unknown_one(self):
        with tempfile.TemporaryDirectory() as folder:
            self.fixture(folder, {"ARMOR-A": "0.8.0.0", "ARMOR-B": "0.8.0.0"})
            fake_compat = mock.Mock()
            with self.patched(folder), mock.patch.dict(sys.modules, {"make_compat": fake_compat}):
                code, _, err = captured(pins.main, ["--set", "ARMOR-Q"])
                self.assertEqual((code, "ARMOR-Q is not a consumer" in err), (2, True))
                self.assertEqual(captured(pins.main, ["--set", "ARMOR-A"])[0], 0)
                written = json.loads((Path(folder) / "registry" / "contract_pins.json").read_text(encoding="utf-8"))["consumers"]
            self.assertEqual(written, {"ARMOR-A": "0.8.1.0", "ARMOR-B": "0.8.0.0"})
            fake_compat.main.assert_called_once_with([])


class KnownOnly(unittest.TestCase):
    SCHEMA = {"properties": {"a": {"type": "integer"}, "obj": {"properties": {"x": {}}}, "list": {"items": {"properties": {"k": {}}}}}, "additionalProperties": {"properties": {"z": {}}}}

    def test_what_the_schema_does_not_know_is_dropped_at_every_level(self):
        value = {"a": 1, "obj": {"x": 1, "y": 2}, "list": [{"k": 1, "q": 2}, {"k": 3}], "other": {"z": 1, "w": 2}}
        self.assertEqual(rewrites.known_only(value, self.SCHEMA), {"a": 1, "obj": {"x": 1}, "list": [{"k": 1}, {"k": 3}], "other": {"z": 1}})

    def test_a_schema_without_extra_properties_drops_the_unknown_names(self):
        self.assertEqual(rewrites.known_only({"a": 1, "b": 2}, {"properties": {"a": {}}}), {"a": 1})

    def test_a_scalar_or_a_list_without_items_goes_through_unchanged(self):
        self.assertEqual(rewrites.known_only(5, {"type": "integer"}), 5)
        self.assertEqual(rewrites.known_only([1, 2], {}), [1, 2])
        self.assertEqual(rewrites.known_only("text", None), "text")

    def test_numbers_agree_to_twelve_digits_and_nothing_else_is_loosened(self):
        self.assertTrue(rewrites.same_value({"v": [3.3249999999999997, 25]}, {"v": [3.325, 25.0]}))
        self.assertFalse(rewrites.same_value({"v": 3.325}, {"v": 3.326}))
        self.assertFalse(rewrites.same_value({"a": 1}, {"a": 1, "b": 2}))
        self.assertFalse(rewrites.same_value([1, 2], [1]))
        self.assertFalse(rewrites.same_value(True, 1))
        self.assertFalse(rewrites.same_value("1", 1))


class WireRewrites(unittest.TestCase):
    def test_without_the_file_to_compare_the_command_says_how_it_is_used(self):
        code, out, _ = captured(rewrites.main, ["check_wire_rewrites.py"])
        self.assertEqual(code, 2)
        self.assertIn("rewrites", (rewrites.__doc__ or "") + out)

    def test_a_file_with_few_cases_or_a_different_rewrite_fails(self):
        cases = ROOT / "conformance" / "wire_cases.tsv"
        first = cases.read_bytes().decode("utf-8").splitlines()[0]
        key, number, text = first.split("\t", 2)
        self.assertTrue(number.isdigit())
        with tempfile.TemporaryDirectory() as folder:
            wrong = Path(folder) / "rewrites.tsv"
            wrong.write_text(f"{key}\t1\t{json.dumps({'not': 'what the contract keeps'})}\n", encoding="utf-8")
            code, out, err = captured(rewrites.main, ["check_wire_rewrites.py", str(wrong)])
        self.assertEqual(code, 1)
        self.assertIn("written back differently", err)
        self.assertIn("1 rewrites compared, 1 differ", out)


if __name__ == "__main__":
    unittest.main()
