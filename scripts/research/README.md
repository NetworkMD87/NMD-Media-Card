# One-off Xtream and ADB research

These scripts preserve bounded research from 11 October 2026. They are research material, not an installed Home Assistant integration, background collector or supported setup workflow. The Xtream snippets do not play video or run a polling loop; the ADB diagnostic makes only explicitly requested finite captures and sends no remote input.

The snippets expect an existing interactive Python session and deliberately contain no real provider address or credentials. Do not run the live snippets merely to verify this repository. Do not print their raw responses, request URLs or session variables: provider data can include credential-bearing links.

- `xtream-logo-probe.py` expects privately entered `server`, `username` and `password`; it fetches the channel catalogue once and prints counts. It also establishes the imports and redirect-refusing handler used by the following request snippets.
- `xtream-single-logo-probe.py` expects a reviewed `nmd_matches` list; it fetches the original image for the first entry and retains its bytes in memory. A supported response type is not proof that an image decodes.
- `xtream-single-guide-probe.py` expects the same reviewed first channel entry and private login variables; it requests at most four guide listings and prints field counts.
- `xtream-guide-display.py` reads the retained guide entries and private login variables to display redacted titles and scheduled times without a network request. These schedule intervals are not the live playback position.

Channel selection/filtering is not automated here. The live test used the single Main Event UHD/4K-labelled entry. Two F1 UHD entries remain ambiguous; never assume the first result identifies the watched channel. All request snippets refuse redirects, bound response size and omit exception URLs from their output.

The accompanying test scripts use synthetic values and mocked network access. Run only these tests for offline validation:

```text
python scripts/research/test-xtream-logo-probe.py
python scripts/research/test-xtream-single-logo-probe.py
python scripts/research/test-xtream-single-guide-probe.py
python scripts/research/test-xtream-guide-display.py
```

The owner-assisted results and remaining limitations are recorded in [VERIFICATION.md](../../VERIFICATION.md).

## Finite ADB capture diagnostic

`adb-passive-capture.sh` is an input-free, one-shot Android shell command for the existing HA `androidtv.adb_command` action. It captures only while TiviMate is foreground and the device is awake, bounds the dump to eight seconds (with a two-second termination grace), checks context again, and removes its unique temporary file. It outputs timing and TiviMate node/text counts, never screen labels or programme details. A fresh sample UUID distinguishes each actual reply; a previous `adb_response` value is not new evidence.

Prepare a single action for your **Android Debug Bridge media-player entity**, rather than a universal player or Android TV Remote entity:

```text
python scripts/research/adb_capture_probe.py --ha-entity media_player.example_adb
```

Paste the generated YAML into HA's Developer Tools / Actions and run it once. Inspect its action response or that entity's `adb_response`. The sample marker must change on each run. `ok` with zero text nodes is expected when the banner is closed; it does not identify a channel. `skipped_context` means the device was asleep or TiviMate was not foreground. Any failed/incomplete/context-changed capture supplies no valid current-channel observation. The diagnostic does not open a banner, change channels, wake the TV, install anything or keep polling after the action finishes.

HA can retain and log ADB action output ([official action reference](https://www.home-assistant.io/actions/androidtv.adb_command/)); keep diagnostic output limited to counts. Do not substitute a full UI dump into this action: another screen can contain private text. Do not run captures concurrently, and avoid a permanent polling automation until latency, resource use and banner capture rate have been measured.

Optional laptop-side comparison requires an explicit endpoint and its independently verified hardware serial:

```text
python scripts/research/adb_capture_probe.py --device DEVICE_ENDPOINT --serial EXPECTED_SERIAL --samples 1
```

This mode uses the laptop's existing ADB, not HA's connection; it cannot qualify HA-path performance. At most three sequential samples are allowed, with a three-second gap, and any context change or capture error stops the run. It contacts no provider and emits no screen text. Other HA users would not need Python or this research CLI for the eventual collector; its packaging remains to be decided after the trial.

Run the diagnostic's offline checks with:

```text
python scripts/research/test-adb-capture-probe.py
```

The full reliability trial still needs ordinary/rapid/guide tuning, guide-focus rejection, observation gaps, app exit/sleep, programme changes and pause. A successful one-shot capture does not establish that every short banner will be caught. No new metadata is connected to the card yet.

## Finite automatic HA trial

`ha_adb_capture_trial.py` generates a manually started HA script for one existing ADB media-player entity:

```text
python scripts/research/ha_adb_capture_trial.py --entity media_player.example_adb
```

The output is JSON, a valid YAML subset. Paste it into the YAML editor of a new script under HA Settings / Automations & scenes / Scripts and save it. This generator is a maintainer tool; running the resulting script needs no Python, device app, API token, shell-command integration or separate ADB server. The owner-specific prepared file is ignored and not part of a release.

Run once with TiviMate playing. During the run, expose the **playback information banner** twice and let it close normally; avoid opening the guide or changing channels for this first check. Afterward, copy the local **NMD finite ADB trial** notification and note any lag in remote response. This temporary script has no triggers and does not start again unless manually run. Do not run other UI captures concurrently; only this script's own duplicate starts are prevented by `mode: single`.

The script attempts eight captures, one at a time, with one-second gaps. Based on observed timing, a normal run should take about 25 seconds. No new capture starts after 30 seconds, although an outstanding action may finish later. A failed/context-changed/incomplete/missing/malformed/repeated response stops the run early and leaves a summary. If HA rejects the script or cannot execute its action, inspect its trace; offline checks do not replace the owner HA run. No remote key input, playback control or device-setting command is sent. Stop the script from HA if viewing or remote responsiveness is affected; a capture already running on-device remains bounded by its existing timeout.

Results show attempt offsets, capture diagnostic time, HA action duration, node/text/description counts and fresh-response status. Text-positive samples are not confirmed banners or channels. A closed/visible/closed transition gives initial automatic-capture evidence; guide-focus rejection, actual field parsing, missed switches and metadata retention require later tests. The summary contains only counts/timings/status, not raw UI text.

The script uses [HA's documented repeat/variables/stop behavior](https://www.home-assistant.io/docs/scripts/) and [local persistent notifications](https://www.home-assistant.io/integrations/persistent_notification/). The automatic trial has eight offline template/sequence checks:

```text
python -B scripts/research/test-ha-adb-capture-trial.py
```

Those tests require Jinja2 in the maintainer's test environment (or the ignored task-local test-deps folder); they mock HA services and make no live requests. No Jinja2 dependency is added to the card or HA setup. Delete or retain the saved trial script through HA after reviewing its results; it is not the eventual supported collector setup.

## One-shot HA channel and guide check

`ha_adb_channel_check.py` prepares a manually run script that makes one input-free capture and reports either playback-banner fields or a rejection status:

```text
python scripts/research/ha_adb_channel_check.py --entity media_player.example_adb
```

Paste the complete generated JSON/YAML into a new HA script's YAML editor and save. This research check uses the existing ADB media-player action and a local persistent notification; HA needs no Python package, helper app, new token or extra ADB connection. Do not run another UI capture concurrently. The saved script has `mode: single`, no triggers, repeats or remote input; it does not update the card or retain channel state.

For the positive check, show the playback information banner with the TV remote and immediately run the script once. The `banner` notification should contain channel, current title/description/schedule, remaining minutes and next title/schedule. For the negative check, open the guide, highlight another channel **without selecting it**, run the same script once, then return normally to playback. The expected `guide` notification states that channel attribution was rejected, with no guide channel/programme values. Notifications for banner and guide have separate IDs, allowing comparison. If the banner closes before capture, `no_banner` accepts no channel; that is not a positive field test. A failure or invalid/stale reply likewise accepts nothing. Supply both notifications before treating actual HA transport/guide rejection as verified.

The filter is limited to the observed **TiviMate 5.3.3** layout. It checks awake/foreground context before and after a bounded dump, gates the exact app version, and removes its unique temporary XML file. It accepts one TiviMate-owned `id/49p` ViewGroup with seven unique TextView fields. Observed guide markers (`4ig`, `4h3`, `2im`, `1oe`) prevent attribution even if banner-like fields coexist. It rejects malformed/unknown markup, missing or duplicate fields, mixed-package banner contents, input over 256 KiB, fields over 512 characters and unsafe text. The narrow parser supports standard XML entities and numeric tab/newline/carriage-return entities; other numeric entities are conservatively rejected. It is not a general XML parser or a claim of compatibility with all TiviMate screens/versions.

Only the seven allowed banner values leave the device; no raw hierarchy, playlist/group labels or arbitrary screen text is returned. Credential-like/URL/control text causes all fields to be suppressed. Successful programme details will be present in the HA response, attribute, trace/notification and potentially info logs, as documented by the [ADB action reference](https://www.home-assistant.io/actions/androidtv.adb_command/). Invalid replies are not echoed in the notification. Each capture carries a fresh UUID; the script consumes the action response and rejects a marker retained from the preceding action.

Run the focused offline checks with:

```text
python -B scripts/research/test-adb-banner-fields.py
python -B scripts/research/test-ha-adb-channel-check.py
```

The parser checks use synthetic XML and an available AWK runtime (`NMD_AWK` can select one); the HA checks use Jinja2 and mocked services/state/clock, compiling every generated template before execution. Source components are `adb-banner-capture.sh` and `adb-banner-fields.awk`; the generator embeds them in the saved action and protects the command with a Jinja raw block so shell literals cannot be interpreted as HA template tags. Rendering preserves the exact original command; no upload/install step is needed. Passing local/device parser checks does not establish actual HA execution, every guide layout, capture rate or continuous current-channel confirmation. No permanent collector is installed.

Both channel-report generators now put programme values in escaped preformatted blocks. Markdown links/images, HTML tags, fence delimiters and multiline content remain literal text. The existing credential-like/URL rejection still applies. Previously saved HA scripts retain their old templates: regenerate and replace the relevant saved script before further notification trials; editing the local generators does not update HA.

The additional offline report regression uses Node.js and test-only Marked alongside the existing Jinja2 harness. Set `NMD_MARKED_MODULE` to an absolute `marked/lib/marked.esm.js` path in the maintainer environment, then run:

```powershell
$env:NMD_MARKED_MODULE = 'C:\path\to\marked\lib\marked.esm.js'
python -B scripts/research/test-ha-adb-notification-reports.py
```

It checks both generated reports with HA's GFM/line-break options and token-by-token parsing, before sanitization. No runtime dependency, HA service, device or provider call is involved. [RM-017 local evidence](../../VERIFICATION.md#literal-research-notification-fields--12-october-2026) records the tested parser version and browser limits.

## Finite automatic HA channel trial

`ha_adb_channel_trial.py` prepares a manually started trial using the same capture command and field validation as the owner-verified one-shot check:

```text
python -B scripts/research/ha_adb_channel_trial.py --entity media_player.example_adb
```

Save the generated JSON/YAML as a **new** HA script. The owner-specific prepared YAML is kept under ignored `output/research/`. The saved script needs only the existing ADB media-player connection and a local notification; it installs nothing and sends no TV inputs or metadata-state updates. Run no other capture script at the same time. `mode: single` prevents duplicate starts of this script, not concurrent captures from other scripts.

For the first natural-banner trial:

1. With the match playing normally and the banner closed, start **NMD finite ADB channel trial**.
2. At roughly five seconds, use your normal remote controls to switch to another known working channel. At roughly ten seconds, switch back to the match. Let both banners close naturally; do not open the guide or press OK to show an extra banner.
3. Let the script finish, then copy its notification and supply the channel you briefly selected, approximate switch times and any remote lag. There is only one brief away/return pair.

The script attempts at most eight sequential captures with one-second gaps. It starts no further capture once 30 seconds have elapsed; an action already running may finish later, so this is not a hard 30-second completion timeout. `guide` and `no_banner` samples continue without any channel fields. Capture/context/version/schema/stale-response failures stop early and leave a partial summary. Stop it in HA if viewing or remote responsiveness is affected; an outstanding device capture retains the existing bounded dump timeout.

The summary gives every attempt's start offset, status, device-check and HA-action duration, plus a valid fresh sample marker. Accepted banners include channel name, current title and schedule, escaped for display. Invalid or guide replies supply no programme fields or raw response text. Previous and repeated markers are rejected, including a repeat of an earlier non-adjacent sample. Banner samples can include repeated sightings of the same banner; their count is not a count of switches. Comparing these names with the owner's actual tuning is necessary to identify misses. The trial records observations without confirming a continuously current channel, provider association or playback position.

Focused offline template/sequence checks use synthetic fields and mocked HA services/state/clock:

```text
python -B scripts/research/test-ha-adb-channel-trial.py
```

These do not execute HA itself or send device/provider requests. The trial reuses the unchanged parser and raw-protected command; actual HA save/runtime and capture-rate evidence require the owner run. This finite diagnostic is not a permanent collector or supported end-user setup.
