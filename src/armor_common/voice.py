"""The binary voice turn: a ``multipart/form-data`` request with the audio as raw bytes, and the ``multipart/mixed`` answer, as the contract describes them (docs/CONTRACTS.md, *Voice turn*).

The older request (the audio as the whole body, ``Content-Type: audio/L16;rate=16000``) keeps working; this is the way to send the audio without the 33 percent of base64 in the answer and with
the language and the wish for the answer in a checked JSON part (``voice_turn_meta``). The reader here is strict on purpose: exactly the parts of the contract, each once, the headers it needs and
nothing else, and sizes that are checked before anything is copied. It is the reference the server's reader (TypeScript) and the voice gateway's (Python) are compared with.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Mapping

from .contracts import ContractError, validate_payload

AUDIO_TYPE = "audio/L16;rate=16000"
MAX_AUDIO_BYTES = 480_000          # 15 seconds of 16 kHz 16-bit mono PCM; the server may be set lower or higher (up to MAX_AUDIO_BYTES_LIMIT)
MAX_AUDIO_BYTES_LIMIT = 1_920_000  # 60 seconds: no setting goes above it
MAX_REPLY_AUDIO_BYTES = 200_000    # the spoken answer the server hands on in binary or base64; above it the answer is text only (audio_omitted)
MAX_META_BYTES = 1024
MAX_PART_HEADER_BYTES = 512
MAX_BOUNDARY_CHARS = 70
FRAMING_OVERHEAD = 4096            # what the boundaries and the headers may add to the audio and the meta
REQUEST_PARTS = ("meta", "audio")
REPLY_PARTS = ("result", "audio")
_BOUNDARY_CHARS = re.compile(r"^[0-9A-Za-z'()+_,\-./:=?]{1,70}$")   # RFC 2046 without the space, which a header would have to quote
_CRLF = b"\r\n"


class VoiceTurnError(ContractError):
    """A voice turn that breaks the contract: ``code`` is the short word the server answers with and ``status`` its HTTP status."""

    def __init__(self, status: int, code: str) -> None:
        super().__init__(code)
        self.status, self.code = status, code


def new_boundary() -> str:
    return "armor" + os.urandom(12).hex()


def _check_boundary(boundary: str) -> None:
    if not _BOUNDARY_CHARS.match(boundary) or boundary.endswith("."):
        raise VoiceTurnError(400, "bad_multipart")


def boundary_of(content_type: str, kind: str) -> str:
    """The boundary of a ``Content-Type`` that must be ``multipart/<kind>``; ``bad_multipart`` for anything else."""
    parts = [p.strip() for p in content_type.split(";")]
    if not parts or parts[0].lower() != f"multipart/{kind}":
        raise VoiceTurnError(400, "bad_multipart")
    boundary = ""
    for item in parts[1:]:
        name, _, value = item.partition("=")
        if name.strip().lower() != "boundary":
            continue
        if boundary:
            raise VoiceTurnError(400, "bad_multipart")
        boundary = value.strip()
        if len(boundary) >= 2 and boundary[0] == boundary[-1] == '"':
            boundary = boundary[1:-1]
    _check_boundary(boundary)
    return boundary


def is_multipart_form(content_type: str) -> bool:
    """Whether a request is the binary voice turn (and not the older raw one)."""
    return content_type.split(";", 1)[0].strip().lower() == "multipart/form-data"


@dataclass(frozen=True)
class Part:
    name: str
    content_type: str
    data: bytes


def _split(body: bytes, boundary: str, kind: str, allowed: tuple[str, ...], max_part_bytes: Mapping[str, int]) -> list[Part]:
    opening = b"--" + boundary.encode("ascii")
    delimiter = _CRLF + opening
    if not body.startswith(opening + _CRLF):
        raise VoiceTurnError(400, "bad_multipart")
    position = len(opening) + 2
    parts: list[Part] = []
    while True:
        header_end = body.find(_CRLF + _CRLF, position - 2)
        if header_end < 0 or header_end - position > MAX_PART_HEADER_BYTES:
            raise VoiceTurnError(400, "bad_multipart")
        header_block = body[position:header_end] if header_end >= position else b""
        data_start = header_end + 4
        end = body.find(delimiter, data_start)
        if end < 0:
            raise VoiceTurnError(400, "bad_multipart")
        name = content_type = ""
        for line in header_block.split(_CRLF) if header_block else []:
            try:
                text = line.decode("ascii")
            except UnicodeDecodeError:
                raise VoiceTurnError(400, "bad_multipart") from None
            key, sep, value = text.partition(":")
            key = key.strip().lower()
            if not sep or key not in ("content-disposition", "content-type"):
                raise VoiceTurnError(400, "bad_multipart")
            if key == "content-type":
                if content_type:
                    raise VoiceTurnError(400, "bad_multipart")
                content_type = value.strip()
            else:
                if name:
                    raise VoiceTurnError(400, "bad_multipart")
                match = re.fullmatch(r'\s*form-data\s*;\s*name="([a-z]{1,16})"\s*(;\s*filename="[^"\r\n]{0,64}")?\s*', value) if kind == "form-data" else re.fullmatch(r'\s*(?:inline|attachment)\s*;\s*name="([a-z]{1,16})"\s*', value)
                if not match:
                    raise VoiceTurnError(400, "bad_multipart")
                name = match.group(1)
        if not name:
            raise VoiceTurnError(400, "bad_multipart")
        if name not in allowed:
            raise VoiceTurnError(422, "unknown_part")
        if any(p.name == name for p in parts):
            raise VoiceTurnError(422, "duplicate_part")
        data = body[data_start:end]
        if len(data) > max_part_bytes.get(name, MAX_META_BYTES):
            raise VoiceTurnError(413, "audio_too_large") if name == "audio" else VoiceTurnError(422, "bad_meta")
        parts.append(Part(name, content_type, data))
        position = end + len(delimiter)
        tail = body[position:position + 2]
        if tail == b"--":
            if body[position + 2:] not in (b"", _CRLF):
                raise VoiceTurnError(400, "bad_multipart")
            return parts
        if tail != _CRLF:
            raise VoiceTurnError(400, "bad_multipart")
        position += 2


def _audio_type_ok(content_type: str) -> bool:
    normal = content_type.replace(" ", "").lower()
    return normal in ("audio/l16;rate=16000", "application/octet-stream")


def parse_voice_turn_request(content_type: str, body: bytes, max_audio_bytes: int = MAX_AUDIO_BYTES) -> tuple[dict[str, object] | None, bytes]:
    """The ``meta`` (``None`` when the part is absent) and the audio of a binary voice request. Raises ``VoiceTurnError`` with the status and code of the contract."""
    boundary = boundary_of(content_type, "form-data")
    if len(body) > max_audio_bytes + MAX_META_BYTES + FRAMING_OVERHEAD:
        raise VoiceTurnError(413, "audio_too_large")
    parts = {p.name: p for p in _split(body, boundary, "form-data", REQUEST_PARTS, {"audio": max_audio_bytes, "meta": MAX_META_BYTES})}
    audio = parts.get("audio")
    if audio is None:
        raise VoiceTurnError(422, "missing_audio")
    if audio.content_type and not _audio_type_ok(audio.content_type):
        raise VoiceTurnError(415, "unsupported_audio_type")
    if len(audio.data) == 0 or len(audio.data) % 2:
        raise VoiceTurnError(411, "bad audio length")
    meta: dict[str, object] | None = None
    if "meta" in parts:
        if parts["meta"].content_type and parts["meta"].content_type.split(";", 1)[0].strip().lower() != "application/json":
            raise VoiceTurnError(422, "bad_meta")
        try:
            loaded = json.loads(parts["meta"].data.decode("utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError
            validate_payload("voice_turn_meta", loaded)
        except (ValueError, ContractError):
            raise VoiceTurnError(422, "bad_meta") from None
        meta = loaded
    return meta, audio.data


def build_voice_turn_request(audio: bytes, meta: Mapping[str, object] | None = None, boundary: str | None = None) -> tuple[str, bytes]:
    """The ``Content-Type`` and the body of a binary voice request."""
    boundary = boundary or new_boundary()
    _check_boundary(boundary)
    chunks: list[bytes] = []
    marker = b"--" + boundary.encode("ascii")
    if meta is not None:
        validate_payload("voice_turn_meta", dict(meta))
        chunks += [marker, b'Content-Disposition: form-data; name="meta"', b"Content-Type: application/json", b"", json.dumps(meta, separators=(",", ":")).encode("utf-8")]
    chunks += [marker, b'Content-Disposition: form-data; name="audio"', b"Content-Type: " + AUDIO_TYPE.encode("ascii"), b"", audio]
    if marker in audio:
        raise VoiceTurnError(400, "bad_multipart")
    return f"multipart/form-data; boundary={boundary}", _CRLF.join(chunks) + _CRLF + marker + b"--" + _CRLF


def build_voice_turn_reply(result: Mapping[str, object], audio: bytes | None = None, boundary: str | None = None) -> tuple[str, bytes]:
    """The ``Content-Type`` and the body of the ``multipart/mixed`` answer: the JSON ``result`` (without an ``audio`` field) and, when there is one, the ``audio`` part."""
    if "audio" in result:
        raise VoiceTurnError(400, "bad_multipart")
    validate_payload("voice_turn_result", dict(result))
    boundary = boundary or new_boundary()
    _check_boundary(boundary)
    marker = b"--" + boundary.encode("ascii")
    chunks = [marker, b'Content-Disposition: inline; name="result"', b"Content-Type: application/json", b"", json.dumps(result, separators=(",", ":"), ensure_ascii=False).encode("utf-8")]
    if audio:
        if marker in audio:
            raise VoiceTurnError(400, "bad_multipart")
        chunks += [marker, b'Content-Disposition: inline; name="audio"', b"Content-Type: " + AUDIO_TYPE.encode("ascii"), b"", audio]
    return f"multipart/mixed; boundary={boundary}", _CRLF.join(chunks) + _CRLF + marker + b"--" + _CRLF


def parse_voice_turn_reply(content_type: str, body: bytes, max_audio_bytes: int = MAX_REPLY_AUDIO_BYTES) -> tuple[dict[str, object], bytes | None]:
    """The ``result`` and the audio (``None`` when the answer is text only) of a binary answer."""
    boundary = boundary_of(content_type, "mixed")
    parts = {p.name: p for p in _split(body, boundary, "mixed", REPLY_PARTS, {"audio": max_audio_bytes, "result": 8192})}
    if "result" not in parts:
        raise VoiceTurnError(422, "bad_meta")
    try:
        loaded = json.loads(parts["result"].data.decode("utf-8"))
        if not isinstance(loaded, dict) or "audio" in loaded:
            raise ValueError
        validate_payload("voice_turn_result", loaded)
    except (ValueError, ContractError):
        raise VoiceTurnError(422, "bad_meta") from None
    audio = parts["audio"].data if "audio" in parts else None
    if audio is not None and (len(audio) == 0 or len(audio) % 2):
        raise VoiceTurnError(411, "bad audio length")
    return loaded, audio
