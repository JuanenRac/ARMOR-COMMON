"""The one table of the broker access of each kind of identity (node_roles.json)."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_FILE = Path(__file__).with_name("node_roles.json")
_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


@lru_cache(maxsize=1)
def table() -> dict:
    return json.loads(_FILE.read_text(encoding="utf-8"))["roles"]


def roles() -> list[str]:
    return list(table())


def user_for(role: str, name: str) -> str:
    """The broker user name of an identity of this role."""
    return table()[role]["user"].replace("{name}", _checked(name))


def acl_lines(role: str, name: str) -> list[str]:
    """The access lines of an identity of this role, in the order mqtt_identity.sh writes them."""
    return [line.replace("{name}", _checked(name)) for line in table()[role]["topics"]]


def acl_block(role: str, name: str) -> str:
    """The whole block (``user`` line and access lines) a broker access list holds for the identity."""
    return "\n".join([f"user {user_for(role, name)}", *acl_lines(role, name)]) + "\n"


def _checked(name: str) -> str:
    if not _NAME.match(name):
        raise ValueError("the name must match ^[a-z0-9][a-z0-9_-]{0,63}$")
    return name
