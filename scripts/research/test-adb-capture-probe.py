"""Offline checks; no device or Home Assistant requests."""

import importlib.util
import json
import pathlib
import subprocess
import unittest
from unittest.mock import patch

path = pathlib.Path(__file__).with_name("adb_capture_probe.py")
spec = importlib.util.spec_from_file_location("probe", path)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

REPLY = (
    "NMD_ADB_PROBE_V1|sample=12345678-1234-1234-1234-123456789abc"
    "|status=ok|elapsed_ms=3050|nodes=31|text_nodes=0|description_nodes=0\n"
)


class ProbeTests(unittest.TestCase):
    def test_valid_response(self):
        self.assertEqual(probe.parse_response(REPLY)["elapsed_ms"], 3050)

    def test_rejects_partial_noise_duplicate_fields_and_invalid_counts(self):
        for invalid in ["", "private screen text", "noise\n" + REPLY,
                        REPLY.replace("sample=", "other="),
                        REPLY.replace("text_nodes=0", "text_nodes=32"),
                        REPLY.replace("elapsed_ms=3050", "elapsed_ms=-1"),
                        REPLY.replace("status=ok", "status=channel_confirmed"),
                        REPLY.replace("123456789abc", "not-a-sample")]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                probe.parse_response(invalid)

    def test_action_roundtrips_command(self):
        action = probe.ha_action("media_player.example_adb")
        self.assertIn("action: androidtv.adb_command\n", action)
        command = json.loads(action.split("  command: ")[1])
        self.assertEqual(command, probe.capture_command())
        self.assertNotIn("input keyevent", command)

    def test_rejects_unsafe_or_wrong_entity_type(self):
        for entity in ["remote.example", "media_player.x\nother: bad", "", "all"]:
            with self.subTest(entity=entity), self.assertRaises(ValueError):
                probe.ha_action(entity)

    def test_identity_mismatch_stops_before_capture(self):
        with patch.object(probe.subprocess, "run", return_value=type("Result", (), {"stdout": "other"})()) as run:
            with self.assertRaises(ValueError):
                probe.direct_probe("adb", "explicit:5555", "expected")
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0][:3], ["adb", "-s", "explicit:5555"])

    def test_context_transition_stops_sampling(self):
        outputs = ["expected", REPLY.replace("status=ok", "status=context_changed")]
        with patch.object(probe.subprocess, "run", side_effect=[type("Result", (), {"stdout": output})() for output in outputs]) as run:
            rows = probe.direct_probe("adb", "explicit:5555", "expected", 3)
            self.assertEqual(len(rows), 1)
            self.assertEqual(run.call_count, 2)

    def test_repeated_response_is_not_new_evidence(self):
        outputs = ["expected", REPLY, REPLY]
        with patch.object(probe.subprocess, "run", side_effect=[type("Result", (), {"stdout": output})() for output in outputs]), patch.object(probe.time, "sleep"):
            with self.assertRaises(ValueError):
                probe.direct_probe("adb", "explicit:5555", "expected", 2)

    def test_capture_timeout_propagates_without_retry(self):
        with patch.object(probe.subprocess, "run", side_effect=[type("Result", (), {"stdout": "expected"})(), subprocess.TimeoutExpired("private response", 30)]) as run:
            with self.assertRaises(subprocess.TimeoutExpired):
                probe.direct_probe("adb", "explicit:5555", "expected", 3)
            self.assertEqual(run.call_count, 2)

    def test_requires_explicit_identity_and_finite_samples(self):
        for device, serial, samples in [("", "expected", 1), ("explicit", "", 1), ("explicit", "expected", 4)]:
            with self.subTest(samples=samples), self.assertRaises(ValueError):
                probe.direct_probe("adb", device, serial, samples)


if __name__ == "__main__":
    unittest.main()
