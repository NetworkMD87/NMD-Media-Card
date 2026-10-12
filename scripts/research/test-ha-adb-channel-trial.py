"""Offline tests for the generated finite HA channel trial."""
import json
import pathlib
import re
import runpy
import shlex
import unittest

from ha_adb_channel_check import FIELDS, PROTOCOL, STATUSES, capture_command
from ha_adb_channel_trial import ha_trial

TrialHarness = runpy.run_path(str(pathlib.Path(__file__).with_name("test-ha-adb-capture-trial.py")))["TrialHarness"]
ENTITY = "media_player.example_adb"


def packet(sample, status="banner", fields=None, elapsed_ms=2140):
    if fields is None:
        fields = dict(zip(FIELDS, [
            "Example Sports UHD", "Match: Home & Away", "16:00 — 19:30", "90 min",
            "Description", "19:30 — 21:15", "Next match",
        ])) if status == "banner" else {}
    return {"protocol": PROTOCOL, "sample": f"00000000-0000-0000-0000-{sample:012x}",
            "status": status, "elapsed_ms": elapsed_ms, "fields": fields}


def wrapped(value):
    return {ENTITY: {"adb_response": json.dumps(value, ensure_ascii=False)}}


class ChannelTrialHarness(TrialHarness):
    def __init__(self, responses, previous=None, action_seconds=2.1):
        super().__init__(responses, previous=previous, action_seconds=action_seconds)

        def from_json(value, default=None):
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return default

        self.env.filters["from_json"] = from_json
        self.env.filters["regex_search"] = lambda value, pattern: re.search(pattern, value) is not None

    def run(self):
        script = ha_trial(ENTITY)

        def compile_templates(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    compile_templates(key)
                    compile_templates(item)
            elif isinstance(value, list):
                for item in value:
                    compile_templates(item)
            elif isinstance(value, str) and any(token in value for token in ["{{", "{%", "{#"]):
                self.env.parse(value)

        compile_templates(script)
        self.execute(script["sequence"])
        return self


class ChannelTrialTests(unittest.TestCase):
    def run_trial(self, responses, previous=None, action_seconds=2.1):
        trial = ChannelTrialHarness(responses, previous, action_seconds).run()
        self.assertEqual(trial.calls, [ENTITY] * len(trial.calls))
        self.assertEqual(len(trial.notifications), 1)
        return trial

    def test_collects_actual_banner_fields_and_keeps_closed_and_guide_rows(self):
        responses = [wrapped(packet(i, status, fields)) for i, status, fields in [
            (1, "no_banner", {}), (2, "banner", None), (3, "guide", {}),
            (4, "no_banner", {}), (5, "banner", dict(zip(FIELDS, [
                "Second Channel", "Second programme", "18:00 — 20:00", "60 min",
                "Description", "20:00 — 21:00", "Next programme",
            ]))), (6, "no_banner", {}), (7, "guide", {}), (8, "no_banner", {}),
        ]]
        trial = self.run_trial(responses)
        rows = trial.context["nmd_rows"]
        self.assertEqual([row["status"] for row in rows], [
            "no_banner", "banner", "guide", "no_banner", "banner", "no_banner", "guide", "no_banner",
        ])
        self.assertEqual([row["sample"] for row in rows], [row["sample"] for row in map(lambda i: packet(i), range(1, 9))])
        self.assertEqual(rows[1]["channel"], "Example Sports UHD")
        self.assertEqual(rows[4]["title"], "Second programme")
        self.assertEqual(rows[2]["channel"], "")
        self.assertEqual(trial.delays, [1] * 7)
        message = trial.notifications[0]["message"]
        self.assertIn("Playback banner samples: 2", message)
        self.assertIn("Banner samples are not switch counts", message)
        self.assertIn("Current: Match: Home &amp; Away", message)
        self.assertNotIn("guide channel", message.lower())

    def test_any_repeated_uuid_in_run_stops_and_does_not_report_duplicate_fields(self):
        a, b = wrapped(packet(1)), wrapped(packet(2, fields=dict(zip(FIELDS, [
            "B Channel", "B programme", "17:00", "30 min", "desc", "18:00", "next",
        ]))))
        trial = self.run_trial([a, b, a])
        rows = trial.context["nmd_rows"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[0]["fresh"])
        self.assertTrue(rows[1]["fresh"])
        self.assertFalse(rows[2]["fresh"])
        self.assertEqual(rows[2]["status"], "invalid_or_repeated_response")
        self.assertEqual(rows[2]["sample"], "")
        self.assertEqual(rows[2]["channel"], "")
        self.assertIn("invalid_or_repeated_response", trial.notifications[0]["message"])
        self.assertNotIn("A Channel", trial.notifications[0]["message"])

    def test_retained_marker_service_error_wrong_room_and_bad_packets_stop_safely(self):
        valid = packet(1)
        cases = [
            ([wrapped(valid)], json.dumps(valid)),
            ([RuntimeError("private device error")], None),
            ([{"media_player.other": {"adb_response": json.dumps(valid)}}], None),
            ([wrapped({**valid, "extra": "private"})], None),
            ([wrapped({**valid, "status": "unknown"})], None),
            ([wrapped({**valid, "elapsed_ms": True})], None),
            ([wrapped(packet(1, "unsupported_version"))], None),
            ([wrapped(packet(1, "capture_failed"))], None),
        ]
        for responses, previous in cases:
            with self.subTest(responses=type(responses[0]).__name__, previous=bool(previous)):
                trial = self.run_trial(responses, previous=previous)
                self.assertEqual(len(trial.calls), 1)
                self.assertEqual(len(trial.context["nmd_rows"]), 1)
                self.assertNotIn("Example Sports UHD", trial.notifications[0]["message"])
                self.assertNotIn("private", trial.notifications[0]["message"])

    def test_unsafe_banner_text_is_rejected_without_echo(self):
        unsafe = packet(1)
        unsafe["fields"]["title"] = "token=private-value"
        trial = self.run_trial([wrapped(unsafe)])
        self.assertEqual(trial.context["nmd_rows"][0]["status"], "invalid_or_repeated_response")
        self.assertNotIn("private-value", trial.notifications[0]["message"])

    def test_failure_after_success_cannot_reuse_previous_response(self):
        for failure in [RuntimeError('private failure'), {}, wrapped(packet(2, 'context_changed'))]:
            with self.subTest(failure=type(failure).__name__):
                trial = self.run_trial([wrapped(packet(1)), failure])
                rows = trial.context['nmd_rows']
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]['channel'], 'Example Sports UHD')
                self.assertEqual(rows[1]['channel'], '')
                self.assertNotIn('private failure', trial.notifications[0]['message'])
                self.assertEqual(trial.delays, [1])

    def test_guide_with_banner_fields_is_invalid_and_suppresses_all_fields(self):
        value = packet(1, 'guide', fields=packet(1)['fields'])
        trial = self.run_trial([wrapped(value)])
        self.assertEqual(trial.context['nmd_rows'][0]['status'], 'invalid_or_repeated_response')
        self.assertNotIn('Example Sports UHD', trial.notifications[0]['message'])
        self.assertEqual(trial.context['nmd_rows'][0]['sample'], '')

    def test_malformed_retained_marker_cannot_break_trial_initialisation(self):
        for previous in ['null', '[]', 'old diagnostic', json.dumps({**packet(9), 'sample': []})]:
            with self.subTest(previous=previous):
                trial = self.run_trial([wrapped(packet(i, 'no_banner')) for i in range(1, 9)], previous=previous)
                self.assertEqual(len(trial.calls), 8)
                self.assertTrue(all(row['fresh'] for row in trial.context['nmd_rows']))

    def test_start_threshold_and_eight_attempt_cap(self):
        slow = self.run_trial([wrapped(packet(i)) for i in range(1, 9)], action_seconds=9)
        self.assertEqual(len(slow.calls), 3)
        self.assertEqual([row["at_s"] for row in slow.context["nmd_rows"]], [0.0, 10.0, 20.0])
        self.assertIn("Time limit reached", slow.notifications[0]["message"])

        overrun = self.run_trial([wrapped(packet(i)) for i in range(1, 9)], action_seconds=9.5)
        self.assertEqual([row['at_s'] for row in overrun.context['nmd_rows']], [0.0, 10.5, 21.0])
        self.assertGreater(overrun.clock, 30)
        self.assertEqual(len(overrun.calls), 3)

        normal = self.run_trial([wrapped(packet(i)) for i in range(1, 9)])
        self.assertEqual(len(normal.calls), 8)
        self.assertEqual(len(normal.context["nmd_rows"]), 8)
        self.assertEqual(normal.delays, [1] * 7)
        self.assertIn("Completed", normal.notifications[0]["message"])

    def test_generated_action_is_raw_protected_and_renders_to_existing_capture(self):
        script = ha_trial(ENTITY)
        self.assertEqual(script["mode"], "single")
        self.assertNotIn("triggers", script)
        repeat = script["sequence"][1]["repeat"]
        self.assertEqual(repeat["count"], 8)
        action = next(step for step in repeat["sequence"] if step.get("action") == "androidtv.adb_command")
        harness = ChannelTrialHarness([wrapped(packet(1))])
        command_template = action["data"]["command"]
        self.assertTrue(command_template.startswith("{% raw %}"))
        self.assertTrue(command_template.endswith("{% endraw %}"))
        self.assertEqual(harness.render(command_template), capture_command())
        self.assertEqual(shlex.split(capture_command())[:2], ["sh", "-c"])
        self.assertNotIn("input keyevent", capture_command())
        self.assertNotIn("input tap", capture_command())
        self.assertEqual(json.loads(json.dumps(script, ensure_ascii=False))["mode"], "single")

    def test_invalid_entity_rejected(self):
        for entity in ["remote.example", "all", "media_player.x\nother: true"]:
            with self.subTest(entity=entity), self.assertRaises(ValueError):
                ha_trial(entity)


if __name__ == "__main__":
    unittest.main()
