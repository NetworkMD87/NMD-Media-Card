# One finite, input-free capture for androidtv.adb_command. No raw UI text output.
# This is a diagnostic, not a background collector or channel identification rule.
nmd_sample=$(cat /proc/sys/kernel/random/uuid)
nmd_started=$(awk '{printf "%.0f", $1 * 1000}' /proc/uptime)
nmd_nodes=0
nmd_text_nodes=0
nmd_description_nodes=0
nmd_file=

nmd_foreground() {
  dumpsys activity activities 2>/dev/null |
    sed -n '/mResumedActivity:/ {s/.* u[0-9]* //;s/\/.*//;p;}'
}
nmd_awake() {
  dumpsys power 2>/dev/null | grep -q 'mWakefulness=Awake'
}
nmd_finish() {
  nmd_ended=$(awk '{printf "%.0f", $1 * 1000}' /proc/uptime)
  printf 'NMD_ADB_PROBE_V1|sample=%s|status=%s|elapsed_ms=%s|nodes=%s|text_nodes=%s|description_nodes=%s\n' \
    "$nmd_sample" "$1" "$((nmd_ended - nmd_started))" \
    "$nmd_nodes" "$nmd_text_nodes" "$nmd_description_nodes"
}

if ! nmd_awake || [ "$(nmd_foreground)" != ar.tvplayer.tv ]; then
  nmd_finish skipped_context
  exit 0
fi
nmd_file=$(mktemp /data/local/tmp/nmd-adb-probe-XXXXXXXX) || {
  nmd_finish temp_failed
  exit 0
}
trap 'rm -f -- "$nmd_file"' EXIT
trap 'exit 1' HUP INT TERM

if ! timeout -k 2 8 uiautomator dump "$nmd_file" >/dev/null 2>&1; then
  nmd_finish capture_failed
  exit 0
fi
if ! nmd_awake || [ "$(nmd_foreground)" != ar.tvplayer.tv ]; then
  nmd_finish context_changed
  exit 0
fi
if ! grep -q '</hierarchy>' "$nmd_file"; then
  nmd_finish incomplete
  exit 0
fi
# Only count TiviMate nodes. Labels, programme names and other app text stay on-device.
nmd_counts=$(awk 'BEGIN {RS="<node "; n=0; t=0; d=0}
  /package="ar[.]tvplayer[.]tv"/ {
    n++; if ($0 ~ /text="[^"]+"/) t++;
    if ($0 ~ /content-desc="[^"]+"/) d++
  }
  END {printf "%d %d %d", n, t, d}' "$nmd_file")
set -- $nmd_counts
nmd_nodes=$1
nmd_text_nodes=$2
nmd_description_nodes=$3
nmd_finish ok
