"""The cases of the binary voice turn that every reader (Python here, TypeScript in ARMOR-SERVER) must agree on: the bytes of a request or an answer and what the reader makes of them.

Written to ``conformance/voice/turn_multipart.json`` by ``tools/make_conformance.py``. A case is ``{name, direction, content_type, body (base64), max_audio_bytes?, expect}``; ``expect`` is
``{"error": {"status": 400, "code": "bad_multipart"}}`` or, for a request, ``{"meta": {...} | null, "audio": <base64>}`` and, for an answer, ``{"result": {...}, "audio": <base64> | null}``.
"""
from __future__ import annotations

import base64
import json
from typing import Any

CRLF = b"\r\n"
B = "XB"
PCM = bytes(range(200))          # 100 samples
PCM_B64 = base64.b64encode(PCM).decode()
META = {"language": "es", "encoding": "pcm_s16le", "sample_rate": 16000, "channels": 1, "reply_audio": "binary"}
META_TEXT = json.dumps(META, separators=(",", ":")).encode()


def part(name: str, data: bytes, content_type: str | None = None, disposition: str | None = None, boundary: str = B) -> bytes:
    head = [f"--{boundary}".encode(), (disposition or f'Content-Disposition: form-data; name="{name}"').encode()]
    if content_type is not None:
        head.append(f"Content-Type: {content_type}".encode())
    return CRLF.join(head + [b"", data]) + CRLF


def close(boundary: str = B) -> bytes:
    return f"--{boundary}--".encode() + CRLF


def ct(boundary: str = B, kind: str = "form-data") -> str:
    return f"multipart/{kind}; boundary={boundary}"


def _case(name: str, direction: str, content_type: str, body: bytes, expect: dict, max_audio_bytes: int | None = None) -> dict:
    case: dict[str, Any] = {"name": name, "direction": direction, "content_type": content_type, "body": base64.b64encode(body).decode(), "expect": expect}
    if max_audio_bytes is not None:
        case["max_audio_bytes"] = max_audio_bytes
    return case


def _error(status: int, code: str) -> dict:
    return {"error": {"status": status, "code": code}}


def cases() -> list[dict]:
    audio = part("audio", PCM, "audio/L16;rate=16000")
    meta = part("meta", META_TEXT, "application/json")
    ok = {"meta": META, "audio": PCM_B64}
    out = [
        _case("meta and audio", "request", ct(), meta + audio + close(), ok),
        _case("audio first, meta second", "request", ct(), audio + meta + close(), ok),
        _case("audio alone", "request", ct(), audio + close(), {"meta": None, "audio": PCM_B64}),
        _case("audio of octet-stream type", "request", ct(), part("audio", PCM, "application/octet-stream") + close(), {"meta": None, "audio": PCM_B64}),
        _case("audio without a type", "request", ct(), part("audio", PCM) + close(), {"meta": None, "audio": PCM_B64}),
        _case("a file name is tolerated", "request", ct(), part("audio", PCM, "audio/L16;rate=16000", 'Content-Disposition: form-data; name="audio"; filename="turn.pcm"') + close(), {"meta": None, "audio": PCM_B64}),
        _case("the boundary in quotes", "request", f'multipart/form-data; boundary="{B}"', audio + close(), {"meta": None, "audio": PCM_B64}),
        _case("audio that holds a line end and dashes", "request", ct(), part("audio", b"\x00\x00\r\n--\r\n--X\x01", "audio/L16;rate=16000") + close(), {"meta": None, "audio": base64.b64encode(b"\x00\x00\r\n--\r\n--X\x01").decode()}),
        _case("nothing after the closing delimiter but a line end", "request", ct(), audio + f"--{B}--".encode(), {"meta": None, "audio": PCM_B64}),
        _case("not multipart", "request", "audio/L16;rate=16000", PCM, _error(400, "bad_multipart")),
        _case("no boundary", "request", "multipart/form-data", audio + close(), _error(400, "bad_multipart")),
        _case("a boundary of 71 characters", "request", ct("b" * 71), audio.replace(B.encode(), b"b" * 71) + close("b" * 71), _error(400, "bad_multipart")),
        _case("two boundaries", "request", ct() + "; boundary=other", audio + close(), _error(400, "bad_multipart")),
        _case("text before the first delimiter", "request", ct(), b"hello" + CRLF + audio + close(), _error(400, "bad_multipart")),
        _case("no closing delimiter", "request", ct(), audio, _error(400, "bad_multipart")),
        _case("text after the closing delimiter", "request", ct(), audio + close() + b"more", _error(400, "bad_multipart")),
        _case("a part without a name", "request", ct(), part("audio", PCM, None, "Content-Disposition: form-data") + close(), _error(400, "bad_multipart")),
        _case("a header the contract does not have", "request", ct(), f"--{B}".encode() + CRLF + b'Content-Disposition: form-data; name="audio"' + CRLF + b"X-Other: 1" + CRLF + CRLF + PCM + CRLF + close(), _error(400, "bad_multipart")),
        _case("line feeds instead of CRLF", "request", ct(), (audio + close()).replace(CRLF, b"\n"), _error(400, "bad_multipart")),
        _case("a part with headers over 512 bytes", "request", ct(), part("audio", PCM, "audio/L16;rate=16000;" + "x" * 600) + close(), _error(400, "bad_multipart")),
        _case("an unknown part", "request", ct(), audio + part("token", b"x") + close(), _error(422, "unknown_part")),
        _case("audio twice", "request", ct(), audio + audio + close(), _error(422, "duplicate_part")),
        _case("meta twice", "request", ct(), meta + meta + audio + close(), _error(422, "duplicate_part")),
        _case("no audio", "request", ct(), meta + close(), _error(422, "missing_audio")),
        _case("a meta that is not JSON", "request", ct(), part("meta", b"{nope", "application/json") + audio + close(), _error(422, "bad_meta")),
        _case("a meta with another sample rate", "request", ct(), part("meta", json.dumps(dict(META, sample_rate=8000)).encode(), "application/json") + audio + close(), _error(422, "bad_meta")),
        _case("a meta with an unknown field", "request", ct(), part("meta", json.dumps(dict(META, token="x")).encode(), "application/json") + audio + close(), _error(422, "bad_meta")),
        _case("a meta that is not JSON by type", "request", ct(), part("meta", META_TEXT, "text/plain") + audio + close(), _error(422, "bad_meta")),
        _case("a meta of 1025 bytes", "request", ct(), part("meta", b" " * 1025, "application/json") + audio + close(), _error(422, "bad_meta")),
        _case("audio of another type", "request", ct(), part("audio", PCM, "audio/wav") + close(), _error(415, "unsupported_audio_type")),
        _case("audio of another rate", "request", ct(), part("audio", PCM, "audio/L16;rate=44100") + close(), _error(415, "unsupported_audio_type")),
        _case("empty audio", "request", ct(), part("audio", b"", "audio/L16;rate=16000") + close(), _error(411, "bad audio length")),
        _case("audio of an odd number of bytes", "request", ct(), part("audio", PCM + b"\x01", "audio/L16;rate=16000") + close(), _error(411, "bad audio length")),
        _case("audio over the limit", "request", ct(), part("audio", b"\x00" * 3202, "audio/L16;rate=16000") + close(), _error(413, "audio_too_large"), 3200),
        _case("audio of exactly the limit", "request", ct(), part("audio", b"\x00" * 3200, "audio/L16;rate=16000") + close(), {"meta": None, "audio": base64.b64encode(b"\x00" * 3200).decode()}, 3200),
    ]
    result = {"heard": "arm the system", "reply": "Arm the system? Say yes to confirm."}
    result_text = json.dumps(result, separators=(",", ":")).encode()
    inline_result = part("result", result_text, "application/json", 'Content-Disposition: inline; name="result"')
    inline_audio = part("audio", PCM, "audio/L16;rate=16000", 'Content-Disposition: inline; name="audio"')
    omitted = {"heard": "x", "reply": "y", "audio_omitted": "too_large"}
    out += [
        _case("an answer with audio", "reply", ct(kind="mixed"), inline_result + inline_audio + close(), {"result": result, "audio": PCM_B64}),
        _case("an answer without audio", "reply", ct(kind="mixed"), inline_result + close(), {"result": result, "audio": None}),
        _case("an answer with the audio left out", "reply", ct(kind="mixed"), part("result", json.dumps(omitted, separators=(",", ":")).encode(), "application/json", 'Content-Disposition: inline; name="result"') + close(), {"result": omitted, "audio": None}),
        _case("an answer in the form-data type", "reply", ct(), inline_result + close(), _error(400, "bad_multipart")),
        _case("an answer without a result", "reply", ct(kind="mixed"), inline_audio + close(), _error(422, "bad_meta")),
        _case("an answer whose result holds the audio", "reply", ct(kind="mixed"), part("result", json.dumps(dict(result, audio="AAAA")).encode(), "application/json", 'Content-Disposition: inline; name="result"') + close(), _error(422, "bad_meta")),
        _case("an answer with an unknown part", "reply", ct(kind="mixed"), inline_result + part("extra", b"x", None, 'Content-Disposition: inline; name="extra"') + close(), _error(422, "unknown_part")),
        _case("an answer with audio over the limit", "reply", ct(kind="mixed"), inline_result + part("audio", b"\x00" * 3202, "audio/L16;rate=16000", 'Content-Disposition: inline; name="audio"') + close(), _error(413, "audio_too_large"), 3200),
    ]
    return out


def render() -> str:
    return json.dumps({"description": "Cases of the binary voice turn (docs/CONTRACTS.md, Voice turn): the bytes and what a reader must make of them. Written by tools/make_conformance.py.", "cases": cases()}, indent=1) + "\n"
