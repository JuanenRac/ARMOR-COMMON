"""The one numbering of the ports: the registry is sound, the generated constants say what it says, and no file of the family still uses the old numbers of the Docker stack."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from armor_common import ports  # noqa: E402

FAMILY = Path(os.environ.get("ARMOR_FAMILY_DIR") or ROOT.parent)
TEXT = re.compile(r"\.(py|sh|bat|ps1|ts|tsx|mjs|js|json|yml|yaml|md|conf|example|env|kt|swift|hpp|cpp|h|txt|toml|cfg|xml|html|svg|acl)$|(^|/)(Dockerfile|\.env\.example)$")


def family_files():
    for repo in sorted(FAMILY.glob("ARMOR-*")):
        if not (repo / ".git").exists():
            continue
        listing = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, encoding="utf-8")
        if listing.returncode != 0:
            continue
        for name in listing.stdout.splitlines():
            if TEXT.search(name) and not name.endswith(("package-lock.json", ".lock")):
                yield repo, name


class RegistryTests(unittest.TestCase):
    def test_the_registry_is_sound(self):
        self.assertEqual(ports.check_registry(ports.registry()), [])

    def test_the_numbering_is_the_one_of_the_cm5(self):
        self.assertEqual([ports.port(n) for n in ("server", "studio", "mqtt", "voice")], [18080, 18081, 18883, 18090])

    def test_a_clash_and_an_old_number_in_use_are_found(self):
        self.assertTrue(ports.check_registry({"ports": {"a": {"port": 18080}, "b": {"port": 18080}}}))
        self.assertTrue(ports.check_registry({"ports": {"a": {"port": 18080, "legacy": [18081]}, "b": {"port": 18081}}}))
        self.assertTrue(ports.check_registry({"ports": {"a": {"port": 80}}}))
        self.assertTrue(ports.check_registry({"ports": {}}))

    def test_the_generated_constants_are_current(self):
        done = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "generate_ports.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_the_generated_constants_carry_every_port(self):
        ts = (ROOT / "generated" / "armor-ports.ts").read_text(encoding="utf-8")
        kt = (ROOT / "generated" / "ArmorPorts.kt").read_text(encoding="utf-8")
        hpp = (ROOT / "generated" / "armor_ports.hpp").read_text(encoding="utf-8")
        for name in ports.registry()["ports"]:
            value = ports.port(name)
            self.assertIn(f"{name}: {value},", ts)
            self.assertIn(f"const val {name.upper()}: Int = {value}", kt)
            self.assertIn(f"= {value};", hpp)


class FamilyTests(unittest.TestCase):
    def test_no_file_of_the_family_uses_an_old_port(self):
        legacy = ports.legacy_ports()
        scan = ports.registry()["scan"]
        only_as_address = set(scan["context_only"]["numbers"])
        plain = [n for n in legacy if n not in only_as_address]
        # (?<![\w.]) so that 18080 and 1.8080 are not 8080
        parts = [r"(?<![\w.])(" + "|".join(map(str, plain)) + r")(?!\w)"] + [r"(?:[:=]|listener )(" + str(n) + r")(?!\w)" for n in sorted(only_as_address)]
        pattern = re.compile("|".join(parts))
        allowed = ports.registry()["scan"]["allowed"]
        seen = 0
        found = []
        for repo, name in family_files():
            seen += 1
            path = f"{repo.name}/{name}"
            whole = [rule for rule in allowed if rule["match"] in path and "line_contains" not in rule]
            if whole:
                continue
            partial = [rule["line_contains"] for rule in allowed if rule["match"] in path and "line_contains" in rule]
            try:
                if (repo / name).stat().st_size > 400_000:
                    continue
                text = (repo / name).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for number, line in enumerate(text.splitlines(), 1):
                hit = pattern.search(line)
                if hit and not any(word in line for word in partial):
                    found.append(f"{path}:{number}: {hit.group(hit.lastindex)} (now {ports.port(legacy[int(hit.group(hit.lastindex))])})")
        if seen == 0:
            self.skipTest("no sibling repository next to this one")
        self.assertEqual(found, [], "an old port is still in use")


if __name__ == "__main__":
    unittest.main()
