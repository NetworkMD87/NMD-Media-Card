"""Generate a short, manually started HA channel-banner trial; no live calls.

The trial uses the existing one-shot TiviMate field capture. It never sends
remote input or writes channel metadata. Output is JSON, which is valid YAML.
"""
import argparse
import json
from ha_adb_channel_check import LITERAL_FIELD, ha_check

NORMAL_STATUSES = ["banner", "guide", "no_banner"]

REPORT = LITERAL_FIELD + """NMD finite ADB channel trial — {{ nmd_reason }}
{{ nmd_rows | length }} of 8 attempts; {{ (as_timestamp(now()) - nmd_started) | round(1) }} seconds total.
Playback banner samples: {{ nmd_rows | selectattr('fresh') | selectattr('status', 'equalto', 'banner') | list | length }}.
Banner samples are not switch counts; continuous current-channel tracking is unconfirmed.
{% for row in nmd_rows %}
Attempt {{ row.attempt }} at +{{ row.at_s }}s: {{ row.status }}; fresh={{ row.fresh }}; sample={{ row.sample or 'none' }}; device={{ row.device_ms }}ms; HA action={{ row.action_ms }}ms.{% if row.status == 'banner' and row.fresh %}

{{ literal_field('Channel', row.channel) }}

{{ literal_field('Current', row.title) }}

{{ literal_field('Schedule', row.schedule) }}

{% endif %}
{% endfor %}Banner fields are guide values. A banner sample is not proof of a channel switch or continuous current channel.
No remote input or metadata-state update."""


def report_action():
    return {
        "action": "persistent_notification.create",
        "data": {
            "title": "NMD finite ADB channel trial",
            "notification_id": "{{ 'nmd_adb_channel_trial_' ~ nmd_entity }}",
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
    # Reuse the owner-verified command, schema, decoding and template protection.
    single = ha_check(entity)
    initial = dict(single['sequence'][0]['variables'])
    initial.update({
        "nmd_normal_statuses": NORMAL_STATUSES,
        "nmd_rows": [],
        "nmd_seen": "{{ [nmd_previous_sample] if nmd_previous_sample is string and (nmd_previous_sample | regex_match(nmd_uuid)) else [] }}",
    })
    decode = dict(single['sequence'][2]['variables'])
    decode['nmd_action_ms'] = "{{ ((as_timestamp(now()) - nmd_action_started) * 1000) | round | int }}"
    return {
        "alias": "NMD finite ADB channel trial",
        "description": "Up to eight sequential input-free captures; one-second gaps; no capture starts at or after 30 seconds.",
        "mode": "single",
        "sequence": [
            {"variables": initial},
            {"repeat": {"count": 8, "sequence": [
                {"if": "{{ as_timestamp(now()) - nmd_started >= 30 }}",
                 "then": end_trial("Time limit reached; no further capture started")},
                {"variables": {
                    "nmd_reply": {},
                    "nmd_action_started": "{{ as_timestamp(now()) }}",
                }},
                single['sequence'][1],
                {"variables": decode},
                single['sequence'][3],
                {"variables": {
                    "nmd_fresh": "{{ nmd_valid and nmd_data.sample not in nmd_seen }}",
                    "nmd_accepted_sample": "{{ nmd_data.sample if nmd_valid and nmd_data.sample not in nmd_seen else '' }}",
                    "nmd_status": "{{ nmd_data.status if nmd_valid and nmd_data.sample not in nmd_seen else 'invalid_or_repeated_response' }}",
                }},
                {"variables": {
                    "nmd_row": "{{ {'attempt': repeat.index, 'at_s': (nmd_action_started - nmd_started) | round(1), 'status': nmd_status, 'fresh': nmd_fresh, 'sample': nmd_accepted_sample, 'device_ms': nmd_data.elapsed_ms if nmd_fresh else 0, 'action_ms': nmd_action_ms, 'channel': nmd_data.fields.channel if nmd_fresh and nmd_status == 'banner' else '', 'title': nmd_data.fields.title if nmd_fresh and nmd_status == 'banner' else '', 'schedule': nmd_data.fields.schedule if nmd_fresh and nmd_status == 'banner' else ''} }}",
                }},
                {"variables": {
                    "nmd_rows": "{{ nmd_rows + [nmd_row] }}",
                    "nmd_seen": "{{ nmd_seen + [nmd_accepted_sample] if nmd_accepted_sample else nmd_seen }}",
                }},
                {"if": "{{ not nmd_fresh or nmd_status not in nmd_normal_statuses }}",
                 "then": end_trial("Stopped on invalid, repeated or failed capture")},
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
        print(json.dumps(ha_trial(args.entity), indent=2, ensure_ascii=False))
    except ValueError as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
