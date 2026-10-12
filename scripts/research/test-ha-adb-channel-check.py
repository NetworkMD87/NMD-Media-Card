"""Offline generated-HA-template checks; all service/state/clock calls mocked."""
import json
import pathlib
import re
import runpy
import shlex
import unittest

from ha_adb_channel_check import ha_check, capture_command, FIELDS, STATUSES

TrialHarness = runpy.run_path(str(pathlib.Path(__file__).with_name("test-ha-adb-capture-trial.py")))["TrialHarness"]
ENTITY = "media_player.example_adb"


def packet(status="banner", sample=1):
    return {"protocol": "NMD_ADB_FIELDS_V1", "sample": f"00000000-0000-0000-0000-{sample:012x}",
            "status": status, "elapsed_ms": 2100,
            "fields": dict(zip(FIELDS, ['Example UHD', 'Match: A & B', '16:00 — 19:30', '100 min',
                                        'A description with München and "quotes".', '19:30 — 21:15', 'Next match'])) if status == "banner" else {}}


def wrapped(value):
    return {ENTITY: {"adb_response": json.dumps(value, ensure_ascii=False)}}


class CheckHarness(TrialHarness):
    def __init__(self, response, previous=None):
        super().__init__([response], previous=previous)
        def from_json(value, default=None):
            try:
                return json.loads(value)
            except (ValueError, TypeError):
                return default
        self.env.filters["from_json"] = from_json
        self.env.filters["regex_search"] = lambda v, p: re.search(p, v) is not None

    def run(self):
        script = ha_check(ENTITY)
        # HA validates templates recursively when saving, before actions run.
        # Compile command data too; the mocked service does not execute it.
        def compile_templates(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    compile_templates(key)
                    compile_templates(item)
            elif isinstance(value, list):
                for item in value:
                    compile_templates(item)
            elif isinstance(value, str) and any(token in value for token in ['{{', '{%', '{#']):
                self.env.parse(value)
        compile_templates(script)
        self.execute(script["sequence"])
        return self


class ChannelCheckTests(unittest.TestCase):
    def run_check(self, response, previous=None):
        h = CheckHarness(response, previous=previous).run()
        self.assertEqual(h.calls, [ENTITY])
        self.assertEqual(len(h.notifications), 1)
        self.assertFalse(h.delays)
        return h

    def test_fresh_banner_decodes_exact_fields_and_reports_timing(self):
        h = self.run_check(wrapped(packet()))
        self.assertEqual(h.context["nmd_status"], "banner")
        self.assertEqual(h.context["nmd_data"]["fields"], packet()["fields"])
        message = h.notifications[0]["message"]
        for text in ['Example UHD', 'München', '16:00 — 19:30', 'HA action: 2100 ms.', 'A &amp; B']:
            self.assertIn(text, message)

    def test_guide_and_closed_banner_emit_no_programme_values(self):
        for status in ["guide", "no_banner"]:
            h = self.run_check(wrapped(packet(status)))
            self.assertEqual(h.context["nmd_status"], status)
            self.assertNotIn('Example UHD', h.notifications[0]["message"])
        self.assertIn('channel attribution rejected', self.run_check(wrapped(packet('guide'))).notifications[0]['message'])

    def test_all_context_capture_errors_emit_only_safe_status(self):
        for status in STATUSES[3:]:
            h = self.run_check(wrapped(packet(status)))
            self.assertEqual(h.context['nmd_status'], status)
            self.assertNotIn('Channel:', h.notifications[0]['message'])

    def test_stale_previous_packet_is_not_a_new_observation(self):
        h = self.run_check(wrapped(packet()), previous=json.dumps(packet()))
        self.assertEqual(h.context['nmd_status'], 'invalid_or_stale_response')
        self.assertNotIn('Example UHD', h.notifications[0]['message'])

    def test_service_error_missing_wrong_room_malformed_do_not_use_retained_data(self):
        for value in [RuntimeError('private error'), None, {}, {ENTITY: None}, {ENTITY: {'adb_response': packet()}},
                      {'media_player.other': {'adb_response': json.dumps(packet())}},
                      {ENTITY: {'adb_response': 'private password value'}}, wrapped(None), wrapped([])]:
            h = self.run_check(value, previous=json.dumps(packet()))
            self.assertEqual(h.context['nmd_status'], 'invalid_or_stale_response')
            for text in ['private', 'Example UHD', 'Channel:']:
                self.assertNotIn(text, h.notifications[0]['message'])

    def test_bad_schema_or_text_never_reports_a_channel(self):
        cases = []
        for key, value in [('protocol','wrong'), ('sample','bad'), ('sample',packet()['sample']+'\n'),
                           ('status','unknown'), ('elapsed_ms',True), ('elapsed_ms',-1), ('elapsed_ms',120001), ('fields',[])]:
            p = packet(); p[key] = value; cases.append(p)
        p = packet(); p['extra'] = 'value'; cases.append(p)
        for value in [None, 23, 'https://example.test/private', 'password value', 'token=secret', '\x01', 'a'*8193, '   ']:
            p = packet(); p['fields']['channel'] = value; cases.append(p)
        p=packet(); del p['fields']['next_title']; cases.append(p)
        p=packet('guide'); p['fields']=packet()['fields']; cases.append(p)
        for p in cases:
            h = self.run_check(wrapped(p))
            self.assertEqual(h.context['nmd_status'], 'invalid_or_stale_response', p)
            self.assertNotIn('Channel:', h.notifications[0]['message'])

    def test_empty_optional_fields_and_nonmatching_previous_type_are_safe(self):
        p = packet(); p['fields'] = {name: 'Example UHD' if name=='channel' else '' for name in FIELDS}
        for previous in ['old diagnostic', 'null', '[]', json.dumps(packet('guide', sample=2))]:
            self.assertEqual(self.run_check(wrapped(p), previous=previous).context['nmd_status'], 'banner')

    def test_generated_capture_is_one_input_free_embedded_command(self):
        s = ha_check(ENTITY)
        self.assertEqual(s['mode'], 'single')
        self.assertNotIn('triggers', s)
        calls=[x for x in s['sequence'] if x.get('action')=='androidtv.adb_command']
        self.assertEqual(len(calls), 1)
        command=CheckHarness(wrapped(packet())).render(calls[0]['data']['command'])
        self.assertEqual(command, capture_command())
        self.assertEqual(shlex.split(command)[:2], ['sh', '-c'])
        self.assertNotIn('__NMD_FIELDS_AWK__',command)
        self.assertNotIn('input keyevent',command)
        self.assertNotIn('input tap',command)
        json.loads(json.dumps(s))

    def test_literal_shell_template_marker_is_protected_during_save_and_render(self):
        from jinja2 import TemplateSyntaxError
        h = CheckHarness(wrapped(packet()))
        original = capture_command()
        self.assertIn('{%', original)
        with self.assertRaises(TemplateSyntaxError):
            h.env.parse(original)
        command = ha_check(ENTITY)['sequence'][1]['data']['command']
        h.env.parse(command)
        self.assertEqual(h.render(command), original)

    def test_invalid_targets_are_rejected(self):
        for entity in ['remote.example', 'all', 'media_player.x\nother: true']:
            with self.assertRaises(ValueError): ha_check(entity)


if __name__ == '__main__':
    unittest.main()
