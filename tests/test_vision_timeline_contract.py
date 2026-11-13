"""The review timeline of the vision service and the photo in the notification, as the server contract describes them (additive, both off by default)."""
from __future__ import annotations

import unittest
from pathlib import Path

try:
    import yaml
    import jsonschema
except ModuleNotFoundError:   # pragma: no cover - the optional tools are not installed
    yaml = None
    jsonschema = None

OPENAPI = Path(__file__).resolve().parents[1] / "openapi" / "armor-server.yaml"


@unittest.skipIf(yaml is None or jsonschema is None, "PyYAML and jsonschema are not installed")
class VisionTimelineContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
        cls.schemas = cls.spec["components"]["schemas"]

    def settings(self) -> dict:
        for schema in self.schemas.values():
            props = schema.get("properties", {}) if isinstance(schema, dict) else {}
            if "vision.timeline" in props:
                return props
        self.fail("the security settings do not list vision.timeline")

    def validator(self, name: str):
        resolver_spec = {"components": {"schemas": self.schemas}, **self.schemas[name]}
        return jsonschema.Draft202012Validator(resolver_spec)

    def test_the_new_options_start_off_and_the_retention_is_thirty_days(self) -> None:
        props = self.settings()
        self.assertIs(props["vision.timeline"]["default"], False)
        self.assertIs(props["push.photo"]["default"], False)
        self.assertIs(props["push.photo_ack"]["default"], False)
        self.assertEqual(props["vision.timeline_days"]["default"], 30)
        self.assertEqual((props["vision.timeline_days"]["minimum"], props["vision.timeline_days"]["maximum"]), (1, 3650))
        self.assertIn("Google", props["push.photo"]["description"])

    def test_who_may_read_and_who_may_delete(self) -> None:
        paths = self.spec["paths"]
        self.assertEqual(paths["/api/v1/vision/timeline"]["get"]["security"], [{"operator": []}])
        self.assertEqual(paths["/api/v1/vision/timeline"]["delete"]["security"], [{"admin": []}])
        self.assertEqual(paths["/api/v1/vision/timeline/{id}"]["delete"]["security"], [{"admin": []}])
        names = {p["name"] for p in paths["/api/v1/vision/timeline"]["get"]["parameters"]}
        self.assertEqual(names, {"since", "level", "camera_id", "limit"})

    def test_an_entry_needs_its_identity_and_refuses_a_wrong_level_or_id(self) -> None:
        entry = {"id": "vt-0123abcd", "at": "2026-01-01T00:00:00Z", "camera_id": "cam-1", "level": "alert", "zone_id": "z", "zone_name": "Drive", "label": "person"}
        item = self.validator("VisionTimelineItem")
        self.assertEqual(list(item.iter_errors(entry)), [])
        self.assertEqual(list(item.iter_errors({**entry, "snapshot_id": None, "clip_id": "cam-1/recording/a.mp4", "confidence": 0.5})), [])
        self.assertTrue(list(item.iter_errors({**entry, "level": "info"})))
        self.assertTrue(list(item.iter_errors({**entry, "id": "x"})))
        self.assertTrue(list(item.iter_errors({k: v for k, v in entry.items() if k != "label"})))
        self.assertTrue(list(item.iter_errors({**entry, "confidence": 1.5})))

    def test_the_list_and_the_deleted_count(self) -> None:
        self.assertEqual(list(self.validator("VisionTimeline").iter_errors({"enabled": False, "days": 30, "items": []})), [])
        self.assertTrue(list(self.validator("VisionTimeline").iter_errors({"enabled": True, "days": 30})))
        self.assertTrue(list(self.validator("VisionTimelineDeleted").iter_errors({"deleted": -1})))


if __name__ == "__main__":
    unittest.main()
