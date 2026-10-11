# Local verification — 7 October 2026

First local implementation of the approved featured-room design. The 7 October results below cover local verification only; the later live-test section records separate, bounded evidence.

## Passed

- `node --test tests/media-model.test.js`: **18/18**.
- Native browser checks at `/tests/browser.html`: **21/21** in isolated Chrome through Playwright CLI. Rerun after model fixes and use of the real `type: custom:nmd-media-card` configuration shape: **21/21**.
- Browser scenarios: idle/off/unknown/unavailable; app-only and assumed playback; feature-gated service targets; room switching and selection retention; 3 active devices; image errors; literal untrusted titles; service failures and duplicate requests; focus during pending controls; reconfiguration with an old request in flight; disconnect/reconnect timer cleanup.
- Browser overflow/touch-target checks at card widths 320, 400, 455 and 520 px, including long titles and room names.
- Visual review: 455px card on desktop in dark theme and 320px card in a 390px browser viewport with light theme. The featured artwork stays dark for readability in both themes. Screenshots: `output/playwright/desktop-dark.png` and `output/playwright/phone-light.png`.
- `node --check` for card, styles and local preview server; no trailing-whitespace matches in source/tests/demo/scripts/documentation.
- Independent reviewer: no unresolved findings after corrections. Review independently reran the 18 model tests; browser evidence was collected by the primary agent.

## Findings corrected

- Accept HA's `type` and standard card layout/visibility fields.
- Never render programme metadata from a mere `on` state.
- Retain app provenance through idle/off/missing-entity gaps so unchanged previous-app metadata remains suppressed.
- Prevent inherited object properties from being mistaken for app logo URLs.
- Keep the playback control keyboard-focusable during pending requests while rejecting duplicate actions.
- Do not show failures from a request made under an obsolete card configuration.

## Failed or limited attempts retained

The initial sandboxed browser launch failed in Chrome's crash reporter. Running the browser outside that sandbox then timed out against the sandboxed loopback server. Both were moved to the host's loopback environment, with scoped execution approval, and the browser checks passed. No protection settings were disabled and no HA/device connections were made.

No Git repository exists, so `git diff --check` is not a valid verification result here. An early worker statement saying it passed was corrected; this report uses the actual file checks above.

## Source hashes for the final checks

SHA-256:

```text
src/card.js                 24891D3941E347B54D3440DB1758AE605B9D04FC8722DC78B54EA72CBE849AA9
src/media-model.js          DF2B4C1EA57381FF4C8C0701990C6EEB0D07507A6070C1F73FE171B91295C38A
src/styles.js              D8AC4DC3E9D2F40A7516A246DDDA2B6C1E3DBBF6CE4A8979CEE606EF5634ECD5
tests/media-model.test.js  C2EB2F8EC746FAB54D328F2D22E16E8802F39AEC84A8F32E03857F7ED996BA1E
tests/browser.html         05235DA6E479AA03816B4770DC343E681A7E427119C773BDEBFA70F2823257A3
```

## Still unverified as of 7 October

Real HA mounting/theme behavior, real entity and universal-player routing, metadata freshness supplied by integrations, artwork quality, supported controls on either physical Shield, Silo session compatibility, TiviMate channel identity and phone/tablet physical touch interaction. No licence, minimum HA version, distribution or release acceptance is implied.

## Owner-assisted live checks — 11 October 2026 (in progress)

Evidence: owner-supplied Home Assistant screenshots and serial-verified, read-only ADB checks on the Living Room Shield. Private screenshots, image URLs and device identifiers are not copied into this report. Snug testing is deferred because that device is occupied.

- Manual installation and JavaScript-module resource registration succeeded. Owner screenshots show the card mounted in the real desktop dashboard, including its idle view.
- During Plex playback, the configured Living Room player supplied playing state, artwork, duration and position; the card displayed these and a pause button. The entity's `media_title` was empty, so the card used its existing programme-information fallback. Playback controls have not yet been exercised.
- During owner-confirmed TiviMate playback, the configured player reported off. The separate Android TV Remote entry reported on with `assumed_state: true`, but its app fields were empty during both TiviMate and Plex checks. Neither entry supplied TiviMate channel details in the captured states.
- Direct ADB identified TiviMate 5.3.3 (`ar.tvplayer.tv`) as the foreground app. Its audio player reported `started` during playback and `paused` after the owner paused the channel while leaving the app open. This establishes two observed device states, not a validated Home Assistant detection rule.
- The Android media-session report contained no TiviMate session; only a leftover Plex session with null state and metadata. Channel/programme names and artwork remain unresolved through this route.
- The initial integration-list screenshot showed Android TV Remote configured and no Android Debug Bridge integration listed. The owner subsequently added the built-in Android Debug Bridge connection for the verified Living Room Shield and approved its device prompt. The ADB entity was identified from its attributes and used in the existing test card. Owner screenshots show TiviMate's app identity, Playing status, periodic screen capture and pause control; programme and progress metadata are absent. No custom state rule was added. Card pause/resume was subsequently owner-verified below; app-exit transitions remain unverified.
- Read-only inspection found no advertised channel/programme interface in TiviMate's registered components. This does not rule out undocumented mechanisms. An initial UI hierarchy had 31 nodes with no text or descriptions. While the owner repeatedly opened the programme banner, four samples had 55 nodes and exposed a playlist-group label, time and programme-title text. After the banner closed, the follow-up sample again exposed no text. This supports further UI-metadata investigation, not automatic channel identity or a reliable integration. Temporary device XML files were removed; no private application data was read.

## Requested local card update — 11 October 2026

- Added the genuine TiviMate Google Play icon for the owner's local test, with separate provenance and a redistribution-rights limitation in the asset notice.
- Removed repeated app-name programme headings and duplicate app names in room previews. Real programme titles remain visible, including a title identical to the application name. Text remains available if a corner logo fails to load.
- `node --test tests/media-model.test.js`: 19/19 passed, including title-provenance regression coverage.
- Existing browser harness: 24/24 passed, including local TiviMate icon loading, heading omission, genuine-title preservation and preview text. Existing controls, stale-metadata, accessibility and container-width checks passed. Browser console contained only an expected missing preview favicon (404).
- Visually checked sample TiviMate cards at 320px and 455px. Local evidence: `output/playwright/nmd-tivimate-local.png` (ignored, sample data only).
- Prepared `output/install/nmd-media-card-tivimate-test-2026-10-11.zip` with exactly ten runtime/asset/licence entries. Every archived file's SHA-256 matched its current source file. The earlier install archive was preserved. No Git/GitHub mutations occurred.
- Owner-supplied terminal output confirms all ten update files extracted into the existing HA card folder with `unzip -o`, including the new logo. The subsequent refreshed screenshot still shows the previous text app label and repeated heading. Extraction succeeded, but the browser is still displaying old behavior; cached modules are the working explanation, not a confirmed server diagnosis. Live visual acceptance remains pending.
- Following the fresh-folder/resource change, the next owner screenshot shows the corner icon and no duplicate heading. The owner requested replacing that Google Play icon with TiviMate's blue website symbol and rounded corners; the first icon choice was not accepted.

## Official logo revision — 11 October 2026

- Replaced TiviMate's local PNG with the owner's selected official website symbol, unchanged on disk, and applied 4px corner rounding in the card's CSS.
- Added Silo's unmodified official square project icon and supplied brand notice. The official guide identifies this asset for compact integration placements. The existing Emby logo remains included.
- Final browser harness: 25/25 passed, including Silo image loading, accessible app name and text fallback. All three requested logos loaded at 24 × 24px in the local sample preview; computed TiviMate corner radius was 4px. No playback/model changes were made for this revision.
- Local sample visual evidence: `output/playwright/nmd-three-logos-local.png`. All three logos are verified locally; live Silo/Emby playback remains pending.
- Prepared `output/install/nmd-media-card-logos-v3.zip` with exactly twelve runtime/asset/licence entries under the fresh `nmd-media-card-logos-v3/` prefix. Every archived file's SHA-256 matched its current source. Previous install archives were preserved; no Git/GitHub mutations occurred.
- Owner terminal output confirms all twelve files extracted under the fresh folder. The subsequent live dashboard screenshot shows the selected blue TiviMate website symbol with rounded corners, no repeated app heading, Playing status and screen capture. This verifies live rendering of the requested TiviMate appearance; explicit owner acceptance and live control behavior are separate from this screenshot evidence.
- The owner reports that pausing TiviMate through the Living Room card worked, then pressing play through the card also worked. Playback was resumed because people were watching TV. This is owner-assisted live confirmation of both control actions on that Shield, not independent observation of raw HA attributes or verification of other apps/devices. Further interactive tests should wait until viewing can be interrupted.

## Passive TiviMate metadata check — 11 October 2026

- Reverified the Living Room Shield identity and TiviMate foreground process without sending input or changing playback.
- Read a bounded, current-TiviMate-process diagnostic-log sample (450 retained lines). There were no matches for programme/title, channel-name, EPG, metadata, now-playing or current-channel keywords. Raw logs were not saved. This rules out a useful metadata match in this sample, not all possible logging or undocumented interfaces.
- At this stage, evidence was limited to programme text exposed while the short information banner was visible. No automatic channel identity or full metadata feed had been established. A background helper remained a proposal, not implemented work.

## Visible TiviMate guide and description check — 11 October 2026

- The owner confirmed the Living Room TV was free and opened the guide's programme context menu. Reverified the intended Shield before sending bounded input.
- The visible UI hierarchy exposed the complete selected programme title, a start/end time range, programme description and channel names in the guide/context menu. Located the actual `Program description` option from the device's UI rather than assuming a remote shortcut.
- Selected `Program description`. Its panel exposed the complete title, time range and description as Android-readable text. The underlying guide also retained channel names. The description panel itself did not provide a separate channel-name field in this capture.
- This proves that these visible views expose useful text. It does not establish that guide selection always matches the playing channel, that text remains available with the guide closed, or that an automatic background collection method works. A two-channel association/freshness comparison remains pending. Temporary device XML files were removed; no private application data was read. No channel-switch, recording or playback-control command was sent in this check.

## Channel association, banner freshness and logos — 11 October 2026

- The owner explicitly authorised channel changes because the Living Room TV was free. Reverified the intended Shield; all commands were pinned to that device. Starting playback was Sky Sports Main Event UHD.
- In the guide, moving focus to Sky Sports F1 UHD changed the title, description and schedule header while the playing-channel marker remained on Main Event. Guide focus therefore cannot be treated as the currently playing channel. Selecting F1 moved the playing marker to that row; a screenshot also confirmed F1 video in the preview. Returning to Main Event restored its title, description, schedule and playing marker.
- The full-screen playback banner exposed a channel name, complete current title, description, start/end times, remaining minutes and next-programme title/times for both channels (55 nodes). The F1 banner identified its race programme and 12:55–15:00 schedule; the restored Main Event banner identified its football programme and 13:00–16:00 schedule. These are guide schedule values, not proof of the precise live-stream position.
- With the banner closed, normal playback again exposed 31 nodes and zero nonempty text/description fields. Reading the hierarchy alone therefore does not provide a continuous metadata feed.
- A normal full-screen channel-down action switched to RTL 4K and automatically exposed its NFL programme, channel name, description and 14:00–17:45 schedule (51 nodes). The inverse channel-up action restored Main Event and its original programme details (55 nodes). This demonstrates fresh automatically displayed banner data for these two normal changes; it does not establish that a collector catches every change or handles programme rollover, guide tuning, pause, app exit or missing guide data.
- Channel logos were visible in the guide and playback banner screenshots. Their Android `ImageView` nodes (`id/1kb`) expose bounds, but no image URL, file path or description in these captures. No clean standalone logo file was obtained. A provider guide/playlist logo source remains to be checked. XMLTV supports optional channel icon URLs ([upstream format definition](https://github.com/XMLTV/xmltv/blob/master/xmltv.dtd)); this does not establish that the owner's feed contains them.
- Local, ignored screen evidence: `output/research/tivimate-f1-guide-20261011.png` and `output/research/tivimate-main-event-banner-20261011.png`. Temporary device XML/PNG files were removed. No credentials, private application data, recordings, settings or other apps were accessed or changed. No card/backend implementation or Git/GitHub mutation occurred in this test.

## Xtream metadata probe preparation — 11 October 2026

- The owner confirmed an Xtream Codes connection and requested step-by-step, read-only provider checking in the HA terminal. Python 3.14.8 is available there. The owner entered server, username and password through hidden prompts; their values were not supplied to this chat or written into project files.
- Prepared an ignored, one-off probe for `get_live_streams`. It makes one bounded metadata request, refuses redirects, keeps the response in memory and prints only channel/logo-link/guide-ID counts or a short error without exception URLs. It does not open a stream or install an integration.
- Seven offline cases passed locally: successful counts and credential encoding, non-list response, malformed JSON, refused redirect, connection error, response-size limit and invalid server input. All network access was mocked; no provider was contacted locally. Live HA execution, actual logo retrieval and provider guide compatibility remain pending.
- The first owner-run request reported an unreachable provider. After the owner privately corrected the server address and reran the probe, it returned 4,475 channels, 4,459 with HTTP(S) logo-link values and 3,982 with nonempty guide IDs. This is owner-assisted live catalogue evidence, not proof that each image URL loads or that guide listings match the watched channel. Login values remain private to the owner's Python session; no raw provider response was supplied to this chat.
- Filtering that in-memory catalogue returned five Main Event/F1 variants, all with nonempty logo links and guide IDs. One Main Event variant and two F1 variants carry UHD/4K labels. No network request was made by the filter; duplicate F1 UHD variants still require association checks.
- Prepared a one-image request probe for the single Main Event UHD/4K-labelled entry. It refuses redirects and embedded URL-userinfo, rejects common stream-file extensions, checks the image content type and limits its response to 2 MiB without printing private URLs or adding provider login parameters. Eight offline request/error/bounds cases passed with mocked network access. Actual image retrieval and decoding remain pending.
- The owner-run image probe returned `image/png` and 24,427 bytes for that entry. This establishes an accessible original logo response rather than a screenshot crop. Image decoding, visual identity and card rendering remain unverified; its bytes remain in the owner's Python session.
- Prepared a one-channel `get_short_epg` request with a limit of four entries and a 1 MiB response cap. It prints only entry/field counts and retains data in memory. Eight offline response/error/bounds cases passed with mocked network access; actual guide response and programme association remain pending.
- The owner-run Main Event guide request returned four entries, all with titles, descriptions and start/stop timestamp pairs. Actual title/time agreement with TiviMate still requires comparison; a populated guide is not evidence of the channel being watched.
- Prepared an in-memory display step to decode guide titles, label current/upcoming/past schedule intervals and show Europe/London times (explicit UTC fallback if timezone data is missing). It suppresses credential-like text and terminal control characters. Six offline decoding/status/privacy/error cases passed; no provider request is made by this step.
- The owner-run display decoded all four titles and their BST schedules. The current Crystal Palace/Nottingham Forest entry (13:00–16:00) and next Liverpool/Manchester City entry (16:00–19:30) exactly match the earlier serial-verified TiviMate Main Event playback banner. The two later NFL entries were also displayed but were not compared with the device. This verifies bounded provider/device guide agreement for Main Event, not automatic current-channel identification, live-stream position or wider provider compatibility.

- The owner saved the already-downloaded PNG to a new, non-overwriting HA preview file, then supplied a browser screenshot showing the Sky Sports UHD Main Event logo served through HA's `/local/` path. This confirms browser decoding, visual channel identity and HA image serving for this one logo, with no additional provider request. Automatic channel association and rendering inside the media card remain unverified.

## Follow-up architecture investigation — 11 October 2026

- A separate, read-only Astra investigation reverified the Living Room Shield and TiviMate foreground state. Additional passive TV-input and TiviMate-filtered notification snapshots yielded no TiviMate TV-input reference or matching notification records. This is bounded negative evidence, not proof that no interface exists. No files, installations, settings, playback controls or provider requests were changed by that investigation.
- No continuously available current-channel signal was established. Astra recommends evaluating a separate, event-driven accessibility helper for naturally appearing playback banners instead of permanent ADB hierarchy polling. Android supports UI-event callbacks and window-content retrieval ([primary API documentation](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService)); sufficient TiviMate events, capture reliability, device overhead and interaction with other accessibility services remain untested.
- Retaining a banner observation does not prove it remains current: an unchanged channel and an unobserved channel change can both leave an empty hierarchy. The prototype must distinguish last-observed information from confirmed-current information, reject guide-focus metadata, start unknown after observation gaps, handle app exit/sleep and keep devices separate. Provider schedules must not be presented as paused or time-shifted playback position.
- The owner favours downloading a channel logo when first needed and retaining it locally, avoiding downloads for unwatched channels. Catalogue/image refresh and banner retention were discussed; no cache or helper has been implemented. Helper installation/accessibility permission, channel-logo placement and a physical validation plan remain decisions for the next phase.
- Preserved the four credential-free research snippets and their mocked-network checks under [scripts/research](scripts/research/README.md). Private responses, downloaded provider images, screenshots and installation archives remain outside version control.
- Checkpoint validation: 19/19 media-model tests and all 29 offline research checks passed. Research checks mocked every network request; no provider or device was contacted. The earlier 25/25 browser result covers the unchanged card source and was not repeated for this documentation/script-preservation checkpoint. `git diff --check` passed.

Next: decide whether to implement a bounded Living Room accessibility-observer prototype, then validate normal/rapid/guide-based tuning, guide browsing, recovery, pause, app exit and device impact before connecting it to the card. Disambiguate the two F1 UHD variants before relying on that association. Channel-logo placement and Plex artwork alongside an ADB fallback still need owner decisions. Snug, live Silo/Emby display, Plex/Silo/Emby controls, phone/tablet interaction and broader live compatibility remain unverified.
