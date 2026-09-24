"""A small, dependency-free JSON Schema validator for the A.R.M.O.R. contracts.

Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.

The published schemas are the single source of truth for every message. This
module interprets them directly, so the Python validators can never drift from
what the schemas say. It implements only the keywords the contracts use and
**refuses a schema that uses any other keyword**, instead of silently ignoring
it: a keyword this code does not understand would otherwise be an unchecked
constraint.

Supported keywords: type, enum, const, pattern, minimum, maximum, minLength,
maxLength, minItems, maxItems, items, properties, required,
additionalProperties (boolean), plus the annotations $schema, $id, title,
description.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

ANNOTATIONS = {"$schema", "$id", "title", "description"}
KEYWORDS = ANNOTATIONS | {
    "type", "enum", "const", "pattern", "minimum", "maximum", "minLength", "maxLength",
    "minItems", "maxItems", "items", "properties", "required", "additionalProperties",
}


class SchemaError(ValueError):
    """An instance does not satisfy its schema. `path` locates the offending value."""

    def __init__(self, path: str, message: str) -> None:
        super().__init__(f"{path or '$'}: {message}")
        self.path = path or "$"
        self.detail = message


class UnsupportedSchema(ValueError):
    """The schema uses a keyword this validator does not implement."""


def _type_matches(value: Any, name: str) -> bool:
    if name == "object":
        return isinstance(value, Mapping)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    # bool is an int in Python, but is never a JSON number.
    if isinstance(value, bool):
        return False
    if name == "integer":
        return isinstance(value, int) or (isinstance(value, float) and value.is_integer())
    if name == "number":
        return isinstance(value, (int, float)) and value == value and value not in (float("inf"), float("-inf"))
    raise UnsupportedSchema(f"unknown type {name!r}")


def check_schema(schema: Mapping[str, Any], path: str = "") -> None:
    """Raise UnsupportedSchema when the schema uses a keyword that is not implemented."""
    unknown = sorted(set(schema) - KEYWORDS)
    if unknown:
        raise UnsupportedSchema(f"{path or '$'}: unsupported keyword(s) {unknown}")
    for name, child in (schema.get("properties") or {}).items():
        check_schema(child, f"{path}/properties/{name}")
    if isinstance(schema.get("items"), Mapping):
        check_schema(schema["items"], f"{path}/items")
    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise UnsupportedSchema(f"{path or '$'}: additionalProperties must be a boolean")


def validate(instance: Any, schema: Mapping[str, Any], path: str = "") -> None:
    """Raise SchemaError if `instance` does not satisfy `schema`."""
    expected = schema.get("type")
    if expected is not None:
        names = expected if isinstance(expected, list) else [expected]
        if not any(_type_matches(instance, name) for name in names):
            raise SchemaError(path, f"must be of type {' or '.join(names)}")
    if "const" in schema and instance != schema["const"]:
        raise SchemaError(path, f"must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(path, f"must be one of {schema['enum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise SchemaError(path, f"must have at least {schema['minLength']} characters")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            raise SchemaError(path, f"must have at most {schema['maxLength']} characters")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            raise SchemaError(path, f"must match {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaError(path, f"must be at least {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            raise SchemaError(path, f"must be at most {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise SchemaError(path, f"must have at least {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise SchemaError(path, f"must have at most {schema['maxItems']} items")
        if isinstance(schema.get("items"), Mapping):
            for index, item in enumerate(instance):
                validate(item, schema["items"], f"{path}/{index}")

    if isinstance(instance, Mapping):
        properties = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in instance:
                raise SchemaError(f"{path}/{name}", "is required")
        if schema.get("additionalProperties") is False:
            for name in instance:
                if name not in properties:
                    raise SchemaError(f"{path}/{name}", "is not allowed")
        for name, child in properties.items():
            if name in instance:
                validate(instance[name], child, f"{path}/{name}")
