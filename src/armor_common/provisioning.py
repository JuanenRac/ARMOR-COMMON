"""The text of the provisioning QR code: the id of a node and the address of the server, nothing else.

The code carries no password, no token and no certificate: a phone or the Studio that reads it learns which node is being added and where its server is, and the
node is then adopted with the credentials the server already issues. ``parse_provisioning`` refuses anything that could hold a secret (a user name or password
in the address, a query, a fragment, a field that is not one of the three).
"""
from __future__ import annotations

import json
from urllib.parse import urlsplit

from .contracts import ContractError, _check_node_id

PREFIX = "armor-provision"
VERSION = 1
_FIELDS = {"v", "node_id", "server"}
MAX_TEXT = 256


def _check_server(server: object) -> str:
    if not isinstance(server, str) or not server or len(server) > MAX_TEXT:
        raise ContractError("server must be a text of 1 to 256 characters")
    if any(ord(c) < 33 or ord(c) == 127 for c in server):
        raise ContractError("server must not hold spaces or control characters")
    try:
        parts = urlsplit(server)
        port = parts.port
    except ValueError as err:
        raise ContractError("server is not a valid address") from err
    if parts.scheme not in ("http", "https"):
        raise ContractError("server must start with http:// or https://")
    if not parts.hostname:
        raise ContractError("server has no host")
    if parts.username is not None or parts.password is not None or "@" in parts.netloc:
        raise ContractError("server must not carry a user name or a password")
    if parts.query or parts.fragment or "?" in server or "#" in server:
        raise ContractError("server must not carry a query or a fragment")
    if parts.path not in ("", "/"):
        raise ContractError("server must be the address of the server without a path")
    if port is not None and not 1 <= port <= 65535:
        raise ContractError("server port is out of range")
    return server.rstrip("/")


def build_provisioning(node_id: str, server: str) -> str:
    """The text to turn into a QR code: ``armor-provision:`` followed by the compact JSON of version, node id and server."""
    _check_node_id(node_id)
    body = json.dumps({"v": VERSION, "node_id": node_id, "server": _check_server(server)}, separators=(",", ":"), sort_keys=True)
    return f"{PREFIX}:{body}"


def parse_provisioning(text: object) -> dict[str, object]:
    """Read the text of a provisioning QR code; raises ``ContractError`` when it is not exactly what ``build_provisioning`` writes."""
    if not isinstance(text, str) or not text.startswith(PREFIX + ":") or len(text) > 2 * MAX_TEXT:
        raise ContractError("not a provisioning code")
    try:
        body = json.loads(text[len(PREFIX) + 1:])
    except ValueError as err:
        raise ContractError("the provisioning code is not valid JSON") from err
    if not isinstance(body, dict) or set(body) != _FIELDS:
        raise ContractError("the provisioning code must hold exactly v, node_id and server")
    if body["v"] != VERSION or isinstance(body["v"], bool):
        raise ContractError("unsupported provisioning version")
    node_id = body["node_id"]
    if not isinstance(node_id, str):
        raise ContractError("node_id must be a text")
    _check_node_id(node_id)
    return {"v": VERSION, "node_id": node_id, "server": _check_server(body["server"])}
