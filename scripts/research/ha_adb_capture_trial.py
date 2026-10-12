"""Generate a finite, manually started HA diagnostic; no live calls here.

Output is JSON, a valid YAML subset accepted by HA's script YAML editor.
Only the maintainer needs this generator. Running the saved script needs no
Python, additional ADB connection, helper app, or permanent automation.
"""

import argparse
import json
import re

from adb_capture_probe import capture_command

UUID = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"
NUMBER = r"[0-9]{1,8}"
RESPONSE_PATTERN = (
    rf"^NMD_ADB_PROBE_V1\|sample={UUID}"
    r"\|status=(?:ok|skipped_context|temp_failed|capture_failed|context_changed|incomplete)"
    + "".join(rf"\|{field}={NUMBER}" for field in
              ["elapsed_ms", "nodes", "text_nodes", "description_nodes"])
    + "$"
)

REPORT = """NMD finite ADB trial — {{ nmd_reason }}
{{ nmd_rows | length }} of 8 attempts; {{ (as_timestamp(now()) - nmd_started) | round(1) }} seconds total.
Text-positive samples: {{ nmd_rows | selectattr('fresh') | selectattr('status', 'equalto', 'ok') | selectattr('text_nodes', 'gt', 0) | list | length }}.
Text counts are observations, not confirmed channel identities.
{% for row in nmd_rows %}
Attempt {{ row.attempt }} at +{{ row.at_s }}s: {{ row.status }}; fresh={{ row.fresh }}; capture={{ row.capture_ms }}ms; HA action={{ row.action_ms }}ms; nodes={{ row.nodes }}; text={{ row.text_nodes }}; descriptions={{ row.description_nodes }}.
{% endfor %}"""


def report_action():
    return {
        "action": "persistent_notification.create",
        "data": {
            "title": "NMD finite ADB trial",
            "notification_id": "{{ 'nmd_adb_trial_' ~ nmd_entity }}",
            "message": REPORT,
        },
    }


def end_trial(reason):
    return [
        {"variables": {"nmd_reason": reason}},
        report_action(),
        {"stop": reason},
    ]


def ha_trial(entity):
    if not re.fullmatch(r"media_player\.[a-z0-9_]+", entity):
        raise ValueError("Use one Android Debug Bridge media-player entity.")
    return {
        "alias": "NMD finite ADB trial",
        "description": "Eight input-free sequential captures; no automatic trigger. Stop on failed/stale/context-changed capture.",
        "mode": "single",
        "sequence": [
            {"variables": {
                "nmd_entity": entity,
                "nmd_started": "{{ as_timestamp(now()) }}",
                "nmd_rows": [],
                # Only retain a valid marker, never arbitrary previous ADB output.
                "nmd_seen": "{{ (state_attr(nmd_entity, 'adb_response') | default('', true) | string) | regex_findall(" + json.dumps(rf"^NMD_ADB_PROBE_V1\|sample=({UUID})\|") + ") }}",
                "nmd_pattern": RESPONSE_PATTERN,
            }},
            {"repeat": {"count": 8, "sequence": [
                {"if": "{{ as_timestamp(now()) - nmd_started >= 30 }}",
                 "then": end_trial("Time limit reached; no further capture started")},
                {"variables": {
                    "nmd_reply": {},
                    "nmd_action_started": "{{ as_timestamp(now()) }}",
                }},
                {"action": "androidtv.adb_command",
                 "target": {"entity_id": "{{ nmd_entity }}"},
                 "data": {"command": capture_command()},
                 "continue_on_error": True,
                 "response_variable": "nmd_reply"},
                {"variables": {
                    "nmd_raw": "{{ nmd_reply.get(nmd_entity, {}).get('adb_response', '') | string | trim if nmd_reply is mapping and nmd_reply.get(nmd_entity) is mapping else '' }}",
                    "nmd_action_ms": "{{ ((as_timestamp(now()) - nmd_action_started) * 1000) | round | int }}",
                }},
                {"variables": {"nmd_valid": "{{ nmd_raw | regex_match(nmd_pattern) }}"}},
                {"variables": {"nmd_parts": "{{ nmd_raw.split('|') if nmd_valid else [] }}"}},
                {"variables": {
                    "nmd_sample": "{{ nmd_parts[1][7:] if nmd_valid else '' }}",
                    "nmd_status": "{{ nmd_parts[2][7:] if nmd_valid else 'invalid_response' }}",
                    "nmd_nodes": "{{ nmd_parts[4][6:] | int if nmd_valid else 0 }}",
                    "nmd_text": "{{ nmd_parts[5][11:] | int if nmd_valid else 0 }}",
                    "nmd_descriptions": "{{ nmd_parts[6][18:] | int if nmd_valid else 0 }}",
                }},
                {"variables": {
                    "nmd_fresh": "{{ nmd_valid and nmd_sample not in nmd_seen and nmd_text <= nmd_nodes and nmd_descriptions <= nmd_nodes }}",
                }},
                {"variables": {
                    "nmd_row": "{{ {'attempt': repeat.index, 'at_s': (nmd_action_started - nmd_started) | round(1), 'fresh': nmd_fresh, 'status': nmd_status if nmd_fresh else 'invalid_or_repeated_response', 'capture_ms': nmd_parts[3][11:] | int if nmd_fresh else 0, 'action_ms': nmd_action_ms, 'nodes': nmd_nodes if nmd_fresh else 0, 'text_nodes': nmd_text if nmd_fresh else 0, 'description_nodes': nmd_descriptions if nmd_fresh else 0} }}",
                }},
                {"variables": {
                    "nmd_rows": "{{ nmd_rows + [nmd_row] }}",
                    "nmd_seen": "{{ nmd_seen + [nmd_sample] if nmd_fresh else nmd_seen }}",
                }},
                {"if": "{{ not nmd_fresh or nmd_status != 'ok' }}",
                 "then": end_trial("Stopped on failed, stale or changed-context capture")},
                {"if": "{{ not repeat.last }}", "then": [{"delay": {"seconds": 1}}]},
            ]}},
            *end_trial("Completed"),
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entity", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(ha_trial(args.entity), indent=2))
    except ValueError as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
