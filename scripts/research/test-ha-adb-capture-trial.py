"""Offline Jinja/sequence checks with mocked HA services and clock.

Requires Jinja2 in the test environment, or the ignored task-local test-deps
folder. These checks do not run HA itself or contact a device/provider.
"""
import datetime
import json
import pathlib
import re
import sys
import unittest

try:
    from jinja2.nativetypes import NativeEnvironment
except ImportError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "output/research/trial-test-deps"))
    from jinja2.nativetypes import NativeEnvironment

from ha_adb_capture_trial import ha_trial
from adb_capture_probe import capture_command

ENTITY = "media_player.example_adb"


def reply(index, status="ok", text=0, descriptions=0, nodes=31):
    return (
        f"NMD_ADB_PROBE_V1|sample=00000000-0000-0000-0000-{index:012x}"
        f"|status={status}|elapsed_ms=2100|nodes={nodes}"
        f"|text_nodes={text}|description_nodes={descriptions}"
    )


class TrialHarness:
    """Evaluate the generated templates and finite sequence; services are fake."""
    def __init__(self, responses, previous=None, action_seconds=2.1):
        self.responses = iter(responses)
        self.previous = previous
        self.action_seconds = action_seconds
        self.clock = 0.0
        self.context = {}
        self.calls = []
        self.notifications = []
        self.delays = []
        self.stopped = False
        self.env = NativeEnvironment()
        self.env.filters["regex_match"] = lambda value, pattern: bool(re.match(pattern, str(value)))
        self.env.filters["regex_findall"] = lambda value, pattern: re.findall(pattern, str(value))
        self.env.globals["now"] = lambda: datetime.datetime.fromtimestamp(self.clock, datetime.timezone.utc)
        self.env.globals["as_timestamp"] = lambda value: value.timestamp()
        self.env.globals["state_attr"] = lambda entity, field: self.previous

    def render(self, value):
        if isinstance(value, str) and ("{{" in value or "{%" in value):
            return self.env.from_string(value).render(**self.context)
        if isinstance(value, dict):
            return {key: self.render(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.render(item) for item in value]
        return value

    def execute(self, sequence):
        for step in sequence:
            if self.stopped:
                return
            if "variables" in step:
                for name, value in step["variables"].items():
                    self.context[name] = self.render(value)
            elif "repeat" in step:
                count = step["repeat"]["count"]
                for index in range(1, count + 1):
                    self.context["repeat"] = {"index": index, "last": index == count}
                    self.execute(step["repeat"]["sequence"])
                    if self.stopped:
                        return
            elif "if" in step:
                if self.render(step["if"]):
                    self.execute(step["then"])
            elif "action" in step:
                if step["action"] == "androidtv.adb_command":
                    self.calls.append(self.render(step["target"])["entity_id"])
                    self.clock += self.action_seconds
                    response = next(self.responses)
                    if isinstance(response, Exception):
                        # continue_on_error leaves the reset response empty.
                        if not step.get("continue_on_error"):
                            raise response
                    else:
                        self.context[step["response_variable"]] = response
                elif step["action"] == "persistent_notification.create":
                    self.notifications.append(self.render(step["data"]))
                else:
                    raise AssertionError("Unexpected service: " + step["action"])
            elif "delay" in step:
                self.delays.append(step["delay"]["seconds"])
                self.clock += self.delays[-1]
            elif "stop" in step:
                self.stopped = True
            else:
                raise AssertionError("Unexpected action")

    def run(self):
        self.execute(ha_trial(ENTITY)["sequence"])
        return self


def wrapped(raw):
    return {ENTITY: {"adb_response": raw}}


class TrialTests(unittest.TestCase):
    def test_closed_visible_closed_sequence_collects_all_eight(self):
        responses = [wrapped(reply(i, text=12 if i in [3, 4] else 0,
                                  descriptions=1 if i in [3, 4] else 0,
                                  nodes=55 if i in [3, 4] else 31)) for i in range(1, 9)]
        trial = TrialHarness(responses).run()
        rows = trial.context["nmd_rows"]
        self.assertEqual(len(rows), 8)
        self.assertEqual([r["text_nodes"] for r in rows], [0, 0, 12, 12, 0, 0, 0, 0])
        self.assertEqual(rows[2]["description_nodes"], 1)
        self.assertEqual(rows[2]["capture_ms"], 2100)
        self.assertEqual(rows[2]["action_ms"], 2100)
        self.assertEqual(trial.calls, [ENTITY] * 8)
        self.assertEqual(trial.delays, [1] * 7)
        self.assertEqual(len(trial.notifications), 1)
        self.assertIn("Text-positive samples: 2", trial.notifications[0]["message"])
        self.assertAlmostEqual(trial.clock, 23.8)

    def test_repeat_or_previous_marker_stops_with_no_second_capture(self):
        for responses, previous, count in [([wrapped(reply(1))], reply(1), 1),
                                           ([wrapped(reply(1)), wrapped(reply(1))], None, 2)]:
            with self.subTest(count=count):
                trial = TrialHarness(responses, previous=previous).run()
                self.assertEqual(len(trial.calls), count)
                self.assertFalse(trial.context["nmd_rows"][-1]["fresh"])
                self.assertEqual(len(trial.notifications), 1)

    def test_all_capture_error_and_context_statuses_stop(self):
        for status in ["skipped_context", "temp_failed", "capture_failed", "context_changed", "incomplete"]:
            with self.subTest(status=status):
                trial = TrialHarness([wrapped(reply(1, status=status))]).run()
                self.assertEqual(len(trial.calls), 1)
                self.assertEqual(trial.context["nmd_rows"][0]["status"], status)
                self.assertFalse(trial.delays)

    def test_missing_malformed_wrong_room_and_inconsistent_responses_stop(self):
        for response in [None, {}, {ENTITY: None}, {"media_player.other": {"adb_response": reply(1)}},
                         wrapped("private password or screen text"), wrapped(reply(1, text=99))]:
            with self.subTest(response=response):
                trial = TrialHarness([response]).run()
                self.assertEqual(len(trial.calls), 1)
                self.assertFalse(trial.context["nmd_rows"][0]["fresh"])
                self.assertNotIn("private password", trial.notifications[0]["message"])

    def test_service_failure_does_not_reuse_previous_reply_or_retry(self):
        trial = TrialHarness([wrapped(reply(1)), RuntimeError("private device error")]).run()
        self.assertEqual(len(trial.calls), 2)
        self.assertFalse(trial.context["nmd_rows"][1]["fresh"])
        self.assertNotIn("private device error", trial.notifications[0]["message"])

    def test_time_limit_stops_before_starting_another_capture(self):
        trial = TrialHarness([wrapped(reply(i)) for i in range(1, 9)], action_seconds=8).run()
        self.assertEqual(len(trial.calls), 4)
        self.assertIn("Time limit reached", trial.notifications[0]["message"])

    def test_json_is_valid_yaml_and_command_is_the_existing_input_free_capture(self):
        script = json.loads(json.dumps(ha_trial(ENTITY)))
        self.assertEqual(script["mode"], "single")
        repeat = script["sequence"][1]["repeat"]
        capture = next(step for step in repeat["sequence"] if step.get("action") == "androidtv.adb_command")
        self.assertEqual(capture["data"]["command"], capture_command())
        self.assertNotIn("input keyevent", capture["data"]["command"])
        self.assertNotIn("triggers", script)

    def test_invalid_targets_are_rejected(self):
        for entity in ["remote.example", "all", "media_player.x\nother: true"]:
            with self.subTest(entity=entity), self.assertRaises(ValueError):
                ha_trial(entity)


if __name__ == "__main__":
    unittest.main()
