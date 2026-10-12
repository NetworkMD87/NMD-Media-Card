"""Prepare a one-shot HA action or run a bounded laptop-side diagnostic.

The direct mode is comparative evidence only, not proof of the HA connection.
It requires an explicit endpoint and expected serial, never selects a device
automatically, and prints only validated counts and timing.
"""

import argparse
import json
import pathlib
import re
import shlex
import subprocess
import time

SOURCE = pathlib.Path(__file__).with_name("adb-passive-capture.sh")
STATUSES = {
    "ok", "skipped_context", "temp_failed", "capture_failed",
    "context_changed", "incomplete",
}


def capture_command():
    return "sh -c " + shlex.quote(SOURCE.read_text(encoding="utf-8"))


def ha_action(entity):
    if not re.fullmatch(r"media_player\.[a-z0-9_]+", entity):
        raise ValueError("Use a single Android Debug Bridge media-player entity.")
    # JSON scalar quoting is valid YAML and preserves every shell newline/quote.
    return (
        "action: androidtv.adb_command\n"
        "target:\n"
        f"  entity_id: {entity}\n"
        "data:\n"
        f"  command: {json.dumps(capture_command())}\n"
    )


def parse_response(response):
    # Reject noise/partial responses instead of reusing a previous observation.
    parts = response.strip().split("|")
    names = ["sample", "status", "elapsed_ms", "nodes", "text_nodes", "description_nodes"]
    if len(parts) != 7 or parts[0] != "NMD_ADB_PROBE_V1":
        raise ValueError("No valid fresh diagnostic response.")
    values = {}
    for name, part in zip(names, parts[1:]):
        if not part.startswith(name + "="):
            raise ValueError("Invalid diagnostic fields.")
        values[name] = part[len(name) + 1:]
    if not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", values["sample"]):
        raise ValueError("Invalid sample marker.")
    if values["status"] not in STATUSES:
        raise ValueError("Invalid diagnostic status.")
    for name in names[2:]:
        if not re.fullmatch(r"[0-9]{1,8}", values[name]):
            raise ValueError("Invalid diagnostic count.")
        values[name] = int(values[name])
    if any(values[name] > values["nodes"] for name in ["text_nodes", "description_nodes"]):
        raise ValueError("Inconsistent diagnostic counts.")
    return values


def direct_probe(adb, device, expected_serial, samples=1):
    if not device or not expected_serial or not 1 <= samples <= 3:
        raise ValueError("Explicit device/serial and 1 to 3 samples are required.")
    def shell(command):
        result = subprocess.run(
            [adb, "-s", device, "shell", command],
            capture_output=True, text=True, timeout=30, check=True,
        )
        return result.stdout
    if shell("getprop ro.serialno").strip() != expected_serial:
        raise ValueError("Device identity mismatch; no capture performed.")
    responses = []
    for index in range(samples):
        if index:
            time.sleep(3)
        started = time.monotonic()
        response = parse_response(shell(capture_command()))
        if any(old["sample"] == response["sample"] for old in responses):
            raise ValueError("Repeated sample marker; observation is not fresh.")
        response["round_trip_ms"] = round((time.monotonic() - started) * 1000)
        responses.append(response)
        # Do not retry failures or an app/sleep transition in this finite test.
        if response["status"] != "ok":
            break
    return responses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--ha-entity", help="Print YAML for one existing ADB media player")
    mode.add_argument("--device", help="Explicit endpoint for laptop-side timing only")
    parser.add_argument("--serial", help="Previously verified expected device serial")
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--samples", type=int, default=1, choices=[1, 2, 3])
    args = parser.parse_args()
    try:
        if args.ha_entity:
            print(ha_action(args.ha_entity), end="")
        else:
            print(json.dumps(direct_probe(args.adb, args.device, args.serial, args.samples), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError):
        # ADB exceptions can contain the entire response/command. Never print them.
        parser.exit(1, "Diagnostic failed; no current-channel claim can be made.\n")


if __name__ == "__main__":
    main()
