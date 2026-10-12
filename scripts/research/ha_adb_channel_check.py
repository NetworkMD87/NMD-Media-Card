"""Prepare a one-shot, input-free HA banner/guide check; no live calls.

Uses only the existing ADB media-player action and a local notification.
This version-specific research check does not update card/channel state.
"""
import argparse
import json
import pathlib
import re
import shlex

ROOT = pathlib.Path(__file__).parent
PROTOCOL = "NMD_ADB_FIELDS_V1"
UUID = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z"
FIELDS = ["channel", "title", "schedule", "remaining", "description", "next_schedule", "next_title"]
STATUSES = ["banner", "guide", "no_banner", "invalid_layout", "unsafe_text", "unsupported_version",
            "skipped_context", "temp_failed", "capture_failed", "context_changed", "incomplete"]


def capture_command():
    shell = (ROOT / "adb-banner-capture.sh").read_text(encoding="utf-8")
    parser = (ROOT / "adb-banner-fields.awk").read_text(encoding="utf-8")
    if shell.count("__NMD_FIELDS_AWK__") != 1:
        raise ValueError("Missing/duplicate parser placeholder")
    shell = shell.replace("__NMD_FIELDS_AWK__", shlex.quote(parser))
    return "sh -c " + shlex.quote(shell)


VALIDATE = """{% set ns = namespace(valid=false) %}
{% if nmd_data is mapping
      and (nmd_data | list | sort) == ['elapsed_ms', 'fields', 'protocol', 'sample', 'status']
      and nmd_data.protocol == nmd_protocol
      and nmd_data.sample is string and (nmd_data.sample | regex_match(nmd_uuid))
      and nmd_data.status is string and nmd_data.status in nmd_statuses
      and nmd_data.elapsed_ms is integer and 0 <= nmd_data.elapsed_ms <= 120000
      and nmd_data.fields is mapping %}
  {% set ns.valid = true %}
  {% if nmd_data.status == 'banner' %}
    {% if (nmd_data.fields | list | sort) != (nmd_field_names | sort) %}
      {% set ns.valid = false %}
    {% else %}
      {% for name in nmd_field_names %}
        {% set value = nmd_data.fields[name] %}
        {% if value is not string or value | length > 8192 %}
          {% set ns.valid = false %}
        {% elif value | regex_search(nmd_unsafe) %}
          {% set ns.valid = false %}
        {% endif %}
      {% endfor %}
      {% if nmd_data.fields.channel is not string or not nmd_data.fields.channel | trim %}
        {% set ns.valid = false %}
      {% endif %}
    {% endif %}
  {% elif nmd_data.fields | length != 0 %}
    {% set ns.valid = false %}
  {% endif %}
{% endif %}
{{ ns.valid }}"""

# Preformatted HTML disables Markdown parsing/autolinking. Escape ampersands
# first so entity-looking text and attempted closing tags stay literal too.
# Unlike Markdown fences, provider backticks/tildes cannot end this block.
LITERAL_FIELD = """{% macro literal_field(label, value) -%}
<pre>{{ label }}: {{ value | replace('&', '&amp;') | replace('<', '&lt;') | replace('>', '&gt;') }}</pre>
{%- endmacro %}"""

REPORT = LITERAL_FIELD + """{% if nmd_status == 'banner' %}
Playback banner captured — fresh=True.
{% for label, name in [('Channel', 'channel'), ('Current', 'title'), ('Schedule', 'schedule'), ('Remaining', 'remaining'), ('Description', 'description'), ('Next', 'next_title'), ('Next schedule', 'next_schedule')] %}
{{ literal_field(label, nmd_data.fields[name]) }}

{% endfor %}
These are banner guide values, not playback position or continuous channel confirmation.
{% elif nmd_status == 'guide' %}
Guide detected — channel attribution rejected.
No guide channel or programme fields were returned.
{% elif nmd_status == 'no_banner' %}
No playback banner detected. No channel observation accepted.
{% else %}
No channel observation accepted: {{ nmd_status }}.
{% endif %}
{% if nmd_fresh %}
Sample: {{ nmd_data.sample }}
Device check: {{ nmd_data.elapsed_ms }} ms.
{% endif %}
HA action: {{ nmd_action_ms }} ms.
One capture only; no remote input or metadata-state update."""


def ha_check(entity):
    if not re.fullmatch(r"media_player\.[a-z0-9_]+", entity):
        raise ValueError("Use one Android Debug Bridge media-player entity")
    return {
        "alias": "NMD ADB channel check",
        "description": "One input-free capture: show playback fields or reject guide text. TiviMate 5.3.3 research only.",
        "mode": "single",
        "sequence": [
            {"variables": {
                "nmd_entity": entity,
                "nmd_protocol": PROTOCOL,
                "nmd_uuid": "^" + UUID,
                "nmd_field_names": FIELDS,
                "nmd_statuses": STATUSES,
                "nmd_unsafe": r"(?i)https?://|password|username|token=|[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]",
                "nmd_previous": "{{ (state_attr(nmd_entity, 'adb_response') | default('', true) | string) | from_json(default={}) }}",
                "nmd_previous_sample": "{{ nmd_previous.get('sample', '') if nmd_previous is mapping and nmd_previous.get('protocol') == nmd_protocol else '' }}",
                "nmd_reply": {},
                "nmd_started": "{{ as_timestamp(now()) }}",
            }},
            {"action": "androidtv.adb_command",
             "target": {"entity_id": "{{ nmd_entity }}"},
             # The shell's JSON printf contains a literal "{%s}". Protect the
             # entire command from HA's recursive Jinja template validation.
             "data": {"command": "{% raw %}" + capture_command() + "{% endraw %}"},
             "response_variable": "nmd_reply",
             "continue_on_error": True},
            {"variables": {
                # Decode in the same template: HA may convert a JSON-looking
                # intermediate template result to a native dictionary.
                "nmd_data": """{% set raw = nmd_reply.get(nmd_entity, {}).get('adb_response', '') if nmd_reply is mapping and nmd_reply.get(nmd_entity) is mapping else '' %}
{{ raw | from_json(default={}) if raw is string and raw | length <= 65536 else {} }}""",
                "nmd_action_ms": "{{ ((as_timestamp(now()) - nmd_started) * 1000) | round | int }}",
            }},
            {"variables": {"nmd_valid": VALIDATE}},
            {"variables": {"nmd_fresh": "{{ nmd_valid and nmd_data.sample != nmd_previous_sample }}"}},
            {"variables": {"nmd_status": "{{ nmd_data.status if nmd_fresh else 'invalid_or_stale_response' }}"}},
            {"action": "persistent_notification.create", "data": {
                "title": "NMD ADB channel check — {{ nmd_status }}",
                "notification_id": "{{ 'nmd_adb_fields_' ~ nmd_entity ~ '_' ~ nmd_status }}",
                "message": REPORT,
            }},
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entity", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(ha_check(args.entity), indent=2, ensure_ascii=False))
    except (ValueError, OSError):
        parser.exit(1, "Unable to prepare check; no live call made.\n")


if __name__ == "__main__":
    main()
