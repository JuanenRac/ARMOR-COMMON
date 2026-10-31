"""The HTTP contract of ARMOR-SERVER (openapi/armor-server.yaml) is a document a machine can read, and it says what the server answers.

These checks need PyYAML and openapi-spec-validator (``pip install -e .[contract-tests]``); CI installs them, and a machine without them skips the file instead of failing it.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

try:
    import yaml
    from openapi_spec_validator import validate as validate_spec
except ModuleNotFoundError:   # pragma: no cover - the optional tools are not installed
    yaml = None
try:
    import jsonschema
except ModuleNotFoundError:   # pragma: no cover - the optional tools are not installed
    jsonschema = None

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "openapi" / "armor-server.yaml"
METHODS = {"get", "put", "post", "delete", "patch", "head", "options"}

SERVER_SOURCE = ROOT.parent / "ARMOR-SERVER" / "src"


def server_routes() -> set[tuple[str, str]]:
    """The (method, path) pairs ARMOR-SERVER registers, read from its sources: app.get/post/put/patch/delete with a literal path, the routes registered in a loop over a list of names, and the panel proxy."""
    found: set[tuple[str, str]] = set()
    for source in [*sorted((SERVER_SOURCE / "routes").glob("*.ts")), SERVER_SOURCE / "node_panel_proxy.ts"]:
        text = source.read_text(encoding="utf-8")
        for match in re.finditer(r"\bapp\.(get|post|put|patch|delete)\(\s*([\"'`])([^\"'`]+)\2", text):
            method, path = match.group(1), match.group(3)
            paths = [path]
            if "${" in path:
                name = re.search(r"\$\{(\w+)\}", path).group(1)
                loop = list(re.finditer(r"for \(const \[?([^\]]*?)\]? of \[(.*?)\](?: as const)?\) \{", text[:match.start()], re.S))[-1]
                names = [item.strip() for item in loop.group(1).split(",")]
                if len(names) > 1:
                    options = re.findall(r"\[\s*\"([^\"]+)\"", loop.group(2)) if names.index(name) == 0 else []
                else:
                    options = re.findall(r"\"([^\"]+)\"", loop.group(2))
                paths = [path.replace("${" + name + "}", option) for option in options]
                if not paths:
                    raise AssertionError(f"cannot expand the route {path} in {source.name}")
            for resolved in paths:
                found.add((method, re.sub(r":(\w+)", r"{\1}", resolved)))
        for match in re.finditer(r"\bapp\.all\(\[([^\]]+)\]", text):
            for path in re.findall(r"\"([^\"]+)\"", match.group(1)):
                if path.endswith("/panel"):
                    continue   # the bare panel address is the same operation as the one with a path
                path = re.sub(r":(\w+)", r"{\1}", path).replace("*rest", "{path}")
                found.update((method, path) for method in ("get", "post", "put", "delete"))
    return found


@unittest.skipIf(yaml is None, "PyYAML and openapi-spec-validator are not installed (pip install -e .[contract-tests])")
class OpenApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))

    def test_it_is_a_valid_openapi_document(self):
        validate_spec(self.document, base_uri=OPENAPI.as_uri())

    def test_its_version_is_the_one_of_this_repository(self):
        manifest = json.loads((ROOT / "armor.project.json").read_text(encoding="utf-8"))
        self.assertEqual(self.document["info"]["version"], manifest["version"])

    def test_a_description_is_never_split_into_keys_by_a_comma(self):
        def walk(node, trail=""):
            if isinstance(node, dict):
                for key, value in node.items():
                    if value is None and isinstance(key, str) and (" " in key or len(key) > 40):
                        self.fail(f"{trail}/{key[:50]} looks like the rest of a description cut at a comma")
                    walk(value, f"{trail}/{key}")
            elif isinstance(node, list):
                for number, value in enumerate(node):
                    walk(value, f"{trail}[{number}]")
        walk(self.document)

    def test_every_operation_says_what_it_answers(self):
        for route, item in self.document["paths"].items():
            for method, operation in item.items():
                if method in METHODS:
                    self.assertTrue(operation.get("responses"), f"{method.upper()} {route} has no responses")

    def test_the_removal_of_history_is_on_the_history_and_asks_for_an_administrator(self):
        self.assertIn("delete", self.document["paths"]["/api/v1/history"])
        self.assertNotIn("delete", self.document["paths"]["/api/v1/camera-status"])
        self.assertIn("administrator", self.document["paths"]["/api/v1/history"]["delete"]["summary"])

    def test_the_messages_the_nodes_post_name_their_schema(self):
        for route, schema in (("/api/v1/telemetry", "telemetry"), ("/api/v1/health", "health"), ("/api/v1/alarm/state", "alarm"), ("/api/v1/network/state", "network")):
            body = self.document["paths"][route]["post"]["requestBody"]["content"]["application/json"]["schema"]
            self.assertTrue(body["$ref"].endswith(f"/{schema}.schema.json"), route)
            self.assertTrue((OPENAPI.parent / body["$ref"]).resolve().is_file(), route)

    def operations(self):
        for route, item in self.document["paths"].items():
            for method, operation in item.items():
                if method in METHODS:
                    yield method, route, operation

    def test_every_body_is_a_named_schema(self):
        # A message is never described as a bare object: it is a component schema (or a published contract schema), or raw bytes.
        for method, route, operation in self.operations():
            bodies = list(operation.get("requestBody", {}).get("content", {}).items())
            for _code, response in operation["responses"].items():
                bodies += list(response.get("content", {}).items())
            for media, body in bodies:
                schema = body.get("schema", {})
                named = "$ref" in schema or schema.get("format") == "binary" or (schema.get("oneOf") and all("$ref" in option for option in schema["oneOf"]))
                self.assertTrue(named, f"{method.upper()} {route} ({media}) has an unnamed body schema")

    def test_every_answer_with_a_body_says_what_the_body_is(self):
        for method, route, operation in self.operations():
            for code, response in operation["responses"].items():
                if code != "204":
                    self.assertIn("content", response, f"{method.upper()} {route} {code} has no content")

    def test_every_error_is_the_error_schema(self):
        for method, route, operation in self.operations():
            for code, response in operation["responses"].items():
                if code[0] in "45":
                    schema = response["content"]["application/json"]["schema"]
                    self.assertEqual(schema, {"$ref": "#/components/schemas/ApiError"}, f"{method.upper()} {route} {code}")

    def test_every_operation_names_who_may_call_it(self):
        schemes = self.document["components"]["securitySchemes"]
        for method, route, operation in self.operations():
            self.assertIn("security", operation, f"{method.upper()} {route} does not say who may call it (an empty list means anybody)")
            for requirement in operation["security"]:
                for name in requirement:
                    self.assertIn(name, schemes, f"{method.upper()} {route} names the unknown scheme {name}")

    def test_every_component_schema_is_used(self):
        text = OPENAPI.read_text(encoding="utf-8")
        used = set(re.findall(r"#/components/schemas/(\w+)", text))
        self.assertEqual(sorted(set(self.document["components"]["schemas"]) - used), [])

    @unittest.skipIf(jsonschema is None, "jsonschema is not installed (pip install -e .[contract-tests])")
    def test_the_examples_are_valid_against_their_schemas(self):
        seen = 0
        for name, schema in self.document["components"]["schemas"].items():
            for example in schema.get("examples", []):
                seen += 1
                wrapper = {"$ref": f"#/components/schemas/{name}", "components": self.document["components"]}
                errors = list(jsonschema.Draft202012Validator(wrapper, format_checker=jsonschema.FormatChecker()).iter_errors(example))
                self.assertEqual([error.message for error in errors], [], f"the example of {name}")
        self.assertGreater(seen, 10)

    @unittest.skipUnless(SERVER_SOURCE.is_dir(), "ARMOR-SERVER is not checked out next to this repository")
    def test_the_routes_of_the_server_are_the_routes_of_the_contract(self):
        documented = {(method, route) for method, route, _ in self.operations()}
        registered = server_routes()
        self.assertGreater(len(registered), 150, "the route table of the server was not read")
        self.assertEqual(sorted(registered - documented), [], "routes the server registers that the contract does not describe (method and path)")
        self.assertEqual(sorted(documented - registered), [], "operations the contract describes that the server does not register")


if __name__ == "__main__":
    unittest.main()
