#!/system/bin/sh
# Input-free research capture. The coordinator replaces the AWK marker with
# adb-banner-fields.awk when assembling a one-shot HA androidtv.adb_command.
nmd_sample=$(cat /proc/sys/kernel/random/uuid 2>/dev/null)
nmd_started=$(awk '{print $1}' /proc/uptime 2>/dev/null)
nmd_elapsed() {
  nmd_now=$(awk '{print $1}' /proc/uptime 2>/dev/null)
  awk -v s="$nmd_started" -v n="$nmd_now" 'BEGIN { if (s == "" || n == "") print 0; else printf "%d", (n-s)*1000 }'
}
nmd_emit() {
  printf '{"protocol":"NMD_ADB_FIELDS_V1","sample":"%s","status":"%s","elapsed_ms":%s,"fields":{}}\n' "$nmd_sample" "$1" "$(nmd_elapsed)"
}
nmd_uuid_valid() {
  printf '%s\n' "$nmd_sample" | grep -Eq '^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$'
}
nmd_awake() { dumpsys power 2>/dev/null | grep -q 'mWakefulness=Awake'; }
nmd_foreground() {
  dumpsys activity activities 2>/dev/null |
    sed -n '/mResumedActivity:/ {s/.* u[0-9]* //;s/\/.*//;p;}'
}

if ! nmd_uuid_valid; then
  nmd_sample=00000000-0000-4000-8000-000000000000
  nmd_emit incomplete
  exit 0
fi
if ! nmd_awake || [ "$(nmd_foreground)" != ar.tvplayer.tv ]; then nmd_emit skipped_context; exit 0; fi
if ! dumpsys package ar.tvplayer.tv 2>/dev/null | grep -Eq '^[[:space:]]*versionName=5\.3\.3[[:space:]]*$'; then nmd_emit unsupported_version; exit 0; fi

nmd_file=$(mktemp /data/local/tmp/nmd-adb-fields-XXXXXXXX 2>/dev/null) || { nmd_emit temp_failed; exit 0; }
trap 'rm -f "$nmd_file"' EXIT
trap 'rm -f "$nmd_file"; exit 1' HUP INT TERM
if ! timeout -k 2 8 uiautomator dump "$nmd_file" >/dev/null 2>&1; then nmd_emit capture_failed; exit 0; fi
nmd_size=$(wc -c < "$nmd_file" 2>/dev/null)
case "$nmd_size" in ''|*[!0-9]*) nmd_emit incomplete; exit 0;; esac
if [ "$nmd_size" -gt 262144 ]; then nmd_emit incomplete; exit 0; fi
if ! nmd_awake || [ "$(nmd_foreground)" != ar.tvplayer.tv ]; then nmd_emit context_changed; exit 0; fi
nmd_duration=$(nmd_elapsed)
awk -v sample="$nmd_sample" -v elapsed_ms="$nmd_duration" -v app_version=5.3.3 __NMD_FIELDS_AWK__ "$nmd_file"
