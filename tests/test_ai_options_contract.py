"""The two options of the observation service (both off by default), the options it follows in the context and the proposals of areas to ignore, as the server contract describes them."""
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
class AiOptionsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
        cls.schemas = cls.spec["components"]["schemas"]

    def validator(self, name: str):
        return jsonschema.Draft202012Validator({"components": {"schemas": self.schemas}, **self.schemas[name]})

    def test_both_options_start_off(self) -> None:
        for schema in self.schemas.values():
            props = schema.get("properties", {}) if isinstance(schema, dict) else {}
            if "ai.learn" in props:
                self.assertIs(props["ai.learn"]["default"], False)
                self.assertIs(props["ai.spatial"]["default"], False)
                return
        self.fail("the security settings do not list ai.learn")

    def test_the_context_may_carry_the_options_and_nothing_else_in_them(self) -> None:
        context = {"mode": "armed", "nodes": [], "cameras": []}
        self.validator("AiContext").validate(context)
        self.validator("AiContext").validate({**context, "options": {"spatial": False, "learn": True}})
        with self.assertRaises(jsonschema.ValidationError):
            self.validator("AiContext").validate({**context, "options": {"anything": True}})

    def test_a_proposal_is_rectangles_inside_the_picture_and_at_most_sixteen(self) -> None:
        validator = self.validator("PostAiIgnoreProposalsRequest")
        zone = {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.2}
        validator.validate({"camera_id": "c1", "zones": [zone]})
        with self.assertRaises(jsonschema.ValidationError):
            validator.validate({"camera_id": "c1", "zones": [zone] * 17})
        with self.assertRaises(jsonschema.ValidationError):
            validator.validate({"camera_id": "c1", "zones": [{**zone, "w": 0}]})

    def test_the_decision_is_accept_or_reject(self) -> None:
        validator = self.validator("IgnoreProposalDecision")
        validator.validate({"decision": "accept"})
        validator.validate({"decision": "reject"})
        with self.assertRaises(jsonschema.ValidationError):
            validator.validate({"decision": "apply"})

    def test_the_routes_are_in_the_contract_and_the_decision_is_for_administrators(self) -> None:
        paths = self.spec["paths"]
        self.assertEqual(paths["/api/v1/ai/ignore-proposals"]["post"]["security"], [{"aiBearer": []}])
        self.assertEqual(paths["/api/v1/ignore-proposals"]["get"]["security"], [{"operator": []}])
        self.assertEqual(paths["/api/v1/ignore-proposals/{camera_id}"]["post"]["security"], [{"admin": []}])


if __name__ == "__main__":
    unittest.main()
