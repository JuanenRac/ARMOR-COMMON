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
from functools import lru_cache
from typing import Any

ANNOTATIONS = {"$schema", "$id", "title", "description"}
TYPES = {"object", "array", "string", "boolean", "null", "integer", "number"}
KEYWORDS = ANNOTATIONS | {
    "type", "enum", "const", "pattern", "minimum", "maximum", "minLength", "maxLength",
    "minItems", "maxItems", "items", "properties", "required", "additionalProperties",
}


@lru_cache(maxsize=None)
def _ecma_pattern(pattern: str) -> re.Pattern[str]:
    r"""A schema pattern with the meaning JSON Schema gives it (ECMA-262), which is what the server and the firmware apply.

    Python's ``$`` also matches before a final line feed (so ``"abc\n"`` satisfied ``^[a-z]+$``), and its ``\d``, ``\w`` and ``\s`` take in other scripts' digits and spaces. Here
    ``$`` is the end of the text and nothing else, and the classes are ASCII, so all implementations accept exactly the same texts.
    """
    out: list[str] = []
    in_class = False
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            out.append(pattern[index:index + 2])
            index += 2
            continue
        if in_class:
            if char == "]":
                in_class = False
            out.append(char)
        elif char == "[":
            in_class = True
            out.append(char)
        elif char == "$":
            out.append(r"\Z")
        else:
            out.append(char)
        index += 1
    return re.compile("".join(out), re.ASCII)


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
    where = path or "$"
    # The values of the keywords are checked too: "required": "x" or "minimum": "1" would otherwise be taken for something it is not.
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not names or any(not isinstance(name, str) or name not in TYPES for name in names):
            raise UnsupportedSchema(f"{where}: type must be one of {sorted(TYPES)} (or a list of them)")
    if "enum" in schema and (not isinstance(schema["enum"], list) or not schema["enum"]):
        raise UnsupportedSchema(f"{where}: enum must be a non-empty list")
    if "required" in schema and (not isinstance(schema["required"], list) or any(not isinstance(name, str) for name in schema["required"])):
        raise UnsupportedSchema(f"{where}: required must be a list of names")
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            raise UnsupportedSchema(f"{where}: pattern must be a string")
        _ecma_pattern(schema["pattern"])
    for name in ("minimum", "maximum"):
        if name in schema and (isinstance(schema[name], bool) or not isinstance(schema[name], (int, float))):
            raise UnsupportedSchema(f"{where}: {name} must be a number")
    for name in ("minLength", "maxLength", "minItems", "maxItems"):
        if name in schema and (isinstance(schema[name], bool) or not isinstance(schema[name], int) or schema[name] < 0):
            raise UnsupportedSchema(f"{where}: {name} must be a non-negative integer")
    if "properties" in schema and not isinstance(schema["properties"], Mapping):
        raise UnsupportedSchema(f"{where}: properties must be an object")
    for name, child in (schema.get("properties") or {}).items():
        if not isinstance(child, Mapping):
            raise UnsupportedSchema(f"{path}/properties/{name}: a property schema must be an object")
        check_schema(child, f"{path}/properties/{name}")
    if "items" in schema:
        if not isinstance(schema["items"], Mapping):
            raise UnsupportedSchema(f"{where}: items must be a single schema (a list of schemas, prefixItems, is not implemented)")
        check_schema(schema["items"], f"{path}/items")
    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise UnsupportedSchema(f"{where}: additionalProperties must be a boolean")


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
        if "pattern" in schema and _ecma_pattern(schema["pattern"]).search(instance) is None:
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
