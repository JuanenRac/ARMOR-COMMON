"""Hiding the secrets of an environment file, and giving them back when the file is saved (the rules and the vectors are in ``env_masking.json``).

The reference of the program that holds the file (the maintenance agent), of the server that shows it and of the editor that saves it.
Copyright (C) 2026 JuanenRac (Electro Hobby 3D). GPL-3.0-or-later.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib import resources
from typing import Any

_LINE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)=(.*?)(\r?)$")
_LOGIN = re.compile(r"(://[^/\s:@]+:)[^@/\s]+@")
_LOGIN_EDITED = re.compile(r"(://[^/\s:@]+:)\*\*\*@")
_LOGIN_PASSWORD = re.compile(r"://[^/\s:@]+:([^@/\s]+)@")
_QUERY = re.compile(r"([?&](?:token|key|secret|password|pass)=)[^&\s]+", re.IGNORECASE)
_QUERY_EDITED = re.compile(r"([?&])(token|key|secret|password|pass)=\*\*\*", re.IGNORECASE)


@lru_cache(maxsize=None)
def rules() -> dict[str, Any]:
    """The rules and vectors (``env_masking.json``)."""
    return json.loads(resources.files("armor_common").joinpath("env_masking.json").read_text(encoding="utf-8"))


def _secret_key() -> re.Pattern[str]:
    return re.compile(rules()["secret_key_pattern"], re.IGNORECASE)


def hide_login(value: str) -> str:
    """An address that carries a login without the secret; any other value as it is."""
    return _QUERY.sub(lambda m: m.group(1) + "***", _LOGIN.sub(lambda m: m.group(1) + "***@", value, count=1))


def _restore_login(edited: str, before: str) -> str:
    found = _LOGIN_PASSWORD.search(before)
    out = edited
    if found is not None:
        password = found.group(1)
        out = _LOGIN_EDITED.sub(lambda m: m.group(1) + password + "@", out, count=1)

    def query(match: re.Match[str]) -> str:
        original = re.search(r"[?&]" + re.escape(match.group(2)) + r"=([^&\s]+)", before, re.IGNORECASE)
        return match.group(0) if original is None else match.group(1) + match.group(2) + "=" + original.group(1)

    return _QUERY_EDITED.sub(query, out)


def mask_env(content: str) -> str:
    """The text of an environment file with the value of every secret replaced by the mask."""
    mask, secret = rules()["mask"], _secret_key()
    out = []
    for line in content.split("\n"):
        match = _LINE.match(line)
        if match is None or match.group(3) == "":
            out.append(line)
        elif secret.search(match.group(2)):
            out.append(f"{match.group(1)}{match.group(2)}={mask}{match.group(4)}")
        else:
            hidden = hide_login(match.group(3))
            out.append(line if hidden == match.group(3) else f"{match.group(1)}{match.group(2)}={hidden}{match.group(4)}")
    return "\n".join(out)


def unmask_env(edited: str, current: str) -> dict[str, str]:
    """What was edited with every hidden value given back the value it had: ``{"content": ...}``, or ``{"missing": KEY}`` for a mask whose key is not in the file any more."""
    mask = rules()["mask"]
    known: dict[str, str] = {}
    for line in current.split("\n"):
        match = _LINE.match(line)
        if match:
            known[match.group(2)] = match.group(3)
    missing = ""
    out = []
    for line in edited.split("\n"):
        match = _LINE.match(line)
        if match is None:
            out.append(line)
            continue
        lead, key, value, ending = match.groups()
        before = known.get(key)
        if value != mask and before is not None and hide_login(before) != before and "***" in value:
            out.append(f"{lead}{key}={_restore_login(value, before)}{ending}")
        elif value != mask:
            out.append(line)
        elif before is None:
            missing = key
            out.append(line)
        else:
            out.append(f"{lead}{key}={before}{ending}")
    return {"missing": missing} if missing else {"content": "\n".join(out)}
