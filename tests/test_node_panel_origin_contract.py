"""The second origin of the node panels, as the server contract describes it (additive, off by default)."""
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
TICKET_PATH = "/api/v1/admin/node-panels/{id}/ticket"


@unittest.skipIf(yaml is None or jsonschema is None, "PyYAML and jsonschema are not installed")
class NodePanelOriginContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
        cls.schemas = cls.spec["components"]["schemas"]

    def test_the_option_starts_off_and_says_what_it_closes(self) -> None:
        option = self.schemas["SecuritySettings"]["properties"]["panel.separate_origin"]
        self.assertEqual(option["type"], "boolean")
        self.assertIs(option["default"], False)
        for word in ("ticket of one use", "panel_origin_required", "panel_origin_forbidden"):
            self.assertIn(word, option["description"])

    def test_only_an_administrator_asks_for_a_ticket_and_every_answer_is_typed(self) -> None:
        operation = self.spec["paths"][TICKET_PATH]["post"]
        self.assertEqual(operation["security"], [{"admin": []}])
        self.assertEqual(set(operation["responses"]), {"201", "403", "404", "409", "503"})
        for status, response in operation["responses"].items():
            self.assertIn("application/json", response["content"], status)
        self.assertEqual(operation["responses"]["201"]["content"]["application/json"]["schema"], {"$ref": "#/components/schemas/NodePanelTicket"})
        self.assertIn("panel_origin_off", operation["responses"]["409"]["description"])

    def test_a_ticket_answer_has_an_address_an_origin_and_a_lifetime_in_seconds(self) -> None:
        schema = self.schemas["NodePanelTicket"]
        validator = jsonschema.Draft202012Validator(schema)
        good = {"url": "http://192.168.0.180:18081/enter/abc", "origin": "http://192.168.0.180:18081", "expires_in_s": 30}
        self.assertEqual(list(validator.iter_errors(good)), [])
        for missing in ("url", "origin", "expires_in_s"):
            bad = {key: value for key, value in good.items() if key != missing}
            self.assertNotEqual(list(validator.iter_errors(bad)), [], missing)
        self.assertNotEqual(list(validator.iter_errors({**good, "expires_in_s": "30"})), [])

    def test_the_old_route_says_it_may_close(self) -> None:
        panel = self.spec["paths"]["/api/v1/nodes/{nodeId}/panel/{path}"]["get"]["responses"]["403"]["description"]
        self.assertIn("panel_origin_required", panel)


if __name__ == "__main__":
    unittest.main()
