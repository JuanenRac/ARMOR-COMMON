"""The binary voice turn: the reader and the writer of armor_common.voice agree with the shared cases (conformance/voice/turn_multipart.json) and with each other."""
import base64
import json
import unittest
from pathlib import Path

from armor_common import ContractError
from armor_common.voice import (MAX_AUDIO_BYTES, MAX_AUDIO_BYTES_LIMIT, MAX_REPLY_AUDIO_BYTES, VoiceTurnError, build_voice_turn_reply, build_voice_turn_request, is_multipart_form,
                                parse_voice_turn_reply, parse_voice_turn_request)

CASES = Path(__file__).resolve().parents[1] / "conformance" / "voice" / "turn_multipart.json"
META = {"language": "es", "encoding": "pcm_s16le", "sample_rate": 16000, "channels": 1}


class SharedCases(unittest.TestCase):
    def test_the_file_is_what_the_tool_writes(self):
        import sys
        sys.path.insert(0, str(CASES.parents[2] / "tools"))
        import voice_cases
        self.assertEqual(CASES.read_text(encoding="utf-8").replace("\r\n", "\n"), voice_cases.render())

    def test_every_case(self):
        cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
        self.assertGreaterEqual(len(cases), 40)
        for case in cases:
            body = base64.b64decode(case["body"])
            expect = case["expect"]
            limit = case.get("max_audio_bytes")
            with self.subTest(case["name"]):
                if "error" in expect:
                    with self.assertRaises(VoiceTurnError) as caught:
                        if case["direction"] == "request":
                            parse_voice_turn_request(case["content_type"], body, limit or MAX_AUDIO_BYTES)
                        else:
                            parse_voice_turn_reply(case["content_type"], body, limit or MAX_REPLY_AUDIO_BYTES)
                    self.assertEqual((caught.exception.status, caught.exception.code), (expect["error"]["status"], expect["error"]["code"]))
                elif case["direction"] == "request":
                    meta, audio = parse_voice_turn_request(case["content_type"], body, limit or MAX_AUDIO_BYTES)
                    self.assertEqual(meta, expect["meta"])
                    self.assertEqual(base64.b64encode(audio).decode(), expect["audio"])
                else:
                    result, audio = parse_voice_turn_reply(case["content_type"], body, limit or MAX_REPLY_AUDIO_BYTES)
                    self.assertEqual(result, expect["result"])
                    self.assertEqual(None if audio is None else base64.b64encode(audio).decode(), expect["audio"])


class RoundTrip(unittest.TestCase):
    def test_a_request_goes_through(self):
        audio = bytes(range(256)) * 10
        content_type, body = build_voice_turn_request(audio, dict(META, reply_audio="binary"))
        self.assertTrue(is_multipart_form(content_type))
        self.assertFalse(is_multipart_form("audio/L16;rate=16000"))
        meta, back = parse_voice_turn_request(content_type, body)
        self.assertEqual(back, audio)
        self.assertEqual(meta["reply_audio"], "binary")
        self.assertEqual(parse_voice_turn_request(*build_voice_turn_request(audio))[0], None)

    def test_a_meta_that_breaks_its_schema_is_not_built(self):
        with self.assertRaises(ContractError):
            build_voice_turn_request(b"\x00\x00", dict(META, sample_rate=8000))

    def test_an_answer_goes_through(self):
        result = {"heard": "arm the system", "reply": "Arm the system? Say yes to confirm."}
        content_type, body = build_voice_turn_reply(result, b"\x01\x02" * 50)
        self.assertEqual(parse_voice_turn_reply(content_type, body), (result, b"\x01\x02" * 50))
        content_type, body = build_voice_turn_reply(result)
        self.assertEqual(parse_voice_turn_reply(content_type, body), (result, None))
        with self.assertRaises(VoiceTurnError):
            build_voice_turn_reply(dict(result, audio="AAAA"))

    def test_a_boundary_inside_the_audio_is_refused_to_the_writer(self):
        with self.assertRaises(VoiceTurnError):
            build_voice_turn_request(b"--abc\x00", None, "abc")

    def test_the_limits(self):
        self.assertEqual((MAX_AUDIO_BYTES, MAX_AUDIO_BYTES_LIMIT, MAX_REPLY_AUDIO_BYTES), (480_000, 1_920_000, 200_000))
        audio = b"\x00" * MAX_AUDIO_BYTES
        parse_voice_turn_request(*build_voice_turn_request(audio))                 # exactly the limit
        content_type, body = build_voice_turn_request(audio + b"\x00\x00")
        with self.assertRaises(VoiceTurnError) as caught:
            parse_voice_turn_request(content_type, body)
        self.assertEqual((caught.exception.status, caught.exception.code), (413, "audio_too_large"))
        parse_voice_turn_request(content_type, body, MAX_AUDIO_BYTES + 2)          # the server may be set higher


if __name__ == "__main__":
    unittest.main()
