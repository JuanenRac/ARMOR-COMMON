"""The live notices, the capture on alarm, the vacation schedule, the signed commands, the backups, the load shedding and the energy balance, as the server contract describes them (all additive, all off by default except the notices)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import yaml
    import jsonschema
except ModuleNotFoundError:   # pragma: no cover - the optional tools are not installed
    yaml = None
    jsonschema = None

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "openapi" / "armor-server.yaml"
CODES = ROOT / "src" / "armor_common" / "alarm_codes.json"
NEW_CODES = ["grid_export_unexpected", "meter_mismatch", "consumption_appliance_stopped", "consumption_standby_high", "consumption_phase_down"]


@unittest.skipIf(yaml is None or jsonschema is None, "PyYAML and jsonschema are not installed")
class TandaAContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
        cls.schemas = cls.spec["components"]["schemas"]

    def validator(self, name: str):
        return jsonschema.Draft202012Validator({"components": {"schemas": self.schemas}, **self.schemas[name]})

    def options(self) -> dict:
        return next(schema["properties"] for schema in self.schemas.values() if isinstance(schema, dict) and "capture.on_alarm" in schema.get("properties", {}))

    def test_the_options_default_to_the_conservative_value(self) -> None:
        props = self.options()
        for key in ("capture.on_alarm", "vacation.mode", "commands.require_sig", "admin.backup", "electrical.load_shedding", "electrical.balance"):
            self.assertIs(props[key]["default"], False, key)
        self.assertIs(props["live.events"]["default"], True)
        self.assertEqual(props["capture.on_alarm_per_min"]["default"], 6)

    def test_the_routes_are_there_with_their_guards(self) -> None:
        paths = self.spec["paths"]
        expected = {
            ("/api/v1/admin/backup", "get"): "admin", ("/api/v1/admin/backup", "put"): "admin", ("/api/v1/admin/backup/run", "post"): "admin", ("/api/v1/admin/backup/verify", "post"): "admin",
            ("/api/v1/electrical/load-shedding", "get"): "operator", ("/api/v1/electrical/load-shedding", "put"): "admin",
            ("/api/v1/electrical/balance", "get"): "operator", ("/api/v1/electrical/balance", "put"): "admin",
        }
        for (route, method), guard in expected.items():
            self.assertIn(guard, paths[route][method]["security"][0], f"{method} {route}")

    def test_a_schedule_trigger_is_valid_only_with_a_time_of_day(self) -> None:
        validator = self.validator("AutomationTrigger")
        self.assertTrue(validator.is_valid({"type": "schedule", "at": "20:30", "days": [0, 6], "jitter_min": 25, "seed": "casa"}))
        self.assertTrue(validator.is_valid({"type": "schedule", "at": "00:00"}))
        for bad in ({"type": "schedule"}, {"type": "schedule", "at": "24:00"}, {"type": "schedule", "at": "9:00"}, {"type": "schedule", "at": "20:00", "jitter_min": 121},
                    {"type": "schedule", "at": "20:00", "days": [7]}, {"type": "schedule", "at": "20:00", "extra": 1}):
            self.assertFalse(validator.is_valid(bad), bad)

    def test_the_backup_requests_keep_the_passphrase_out_of_the_answers(self) -> None:
        request = self.validator("BackupSettingsRequest")
        self.assertTrue(request.is_valid({"schedule": True, "every_h": 24, "keep": 7, "destination": "/media/usb", "passphrase": "twelve chars!"}))
        self.assertFalse(request.is_valid({"passphrase": "short"}))
        self.assertFalse(request.is_valid({"every_h": 0}))
        self.assertNotIn("passphrase", self.schemas["BackupSettings"]["properties"])
        self.assertNotIn("passphrase", json.dumps(self.schemas["BackupState"]))
        verify = self.validator("BackupVerifyRequest")
        self.assertTrue(verify.is_valid({"name": "armor-backup-20260102T030405Z.armorbk"}))
        self.assertFalse(verify.is_valid({"name": "../../etc/passwd"}))

    def test_the_shedding_and_balance_settings_have_the_ranges_of_the_server(self) -> None:
        shedding = self.validator("LoadSheddingSettings")
        self.assertTrue(shedding.is_valid({"limit_w": 4000, "restore_w": 3000, "loads": ["heater", "boiler"]}))
        for bad in ({"limit_w": 100}, {"hold_s": 1}, {"loads": ["a", "a"]}, {"loads": ["has space"]}, {"surprise": 1}):
            self.assertFalse(shedding.is_valid(bad), bad)
        balance = self.validator("EnergyBalanceSettings")
        self.assertTrue(balance.is_valid({"allow_export": False, "watch_channels": ["electrical-1/fridge"]}))
        for bad in ({"watch_channels": ["fridge"]}, {"stopped_h": 49}, {"mismatch_pct": 5}):
            self.assertFalse(balance.is_valid(bad), bad)

    def test_the_new_alarm_codes_have_words_in_every_language(self) -> None:
        shared = json.loads(CODES.read_text(encoding="utf-8"))
        for code in NEW_CODES:
            self.assertEqual(sorted(shared["codes"][code]), sorted(shared["languages"]), code)
            for language, text in shared["codes"][code].items():
                self.assertGreater(len(text), 8, f"{code} {language}")
        self.assertEqual(self.schemas["EnergyBalanceFinding"]["properties"]["code"]["enum"], NEW_CODES)


if __name__ == "__main__":
    unittest.main()
