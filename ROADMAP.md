# NMD Media Card roadmap

Last updated: 2026-10-19

## 🎯 Next up

[RM-011 — Finish Plex, Silo and Emby validation](#rm-011-finish-plex-silo-and-emby-validation).

The approved Satoshi title, brighter artwork and translucent playback control are locally verified; the title-only fallback now applies across apps. Next acceptance step: inspect the updated card in installed HA after a separately authorised installation/update. [Polish evidence and font packaging limit](VERIFICATION.md#title-and-playback-polish--19-october-2026) · [RM-013](#rm-013-complete-real-dashboard-and-touch-device-acceptance).

Plex movie/episode HA and direct raw Cast checks are complete: titles are empty in the receiver replies, with artwork/progress and a library metadata reference present. Recommended next action, awaiting owner selection: scope protected known-item lookup, agreeing credential handling and explicit server/item association before any requests or setup changes. Shared-user access remains unverified. [Entity comparison](VERIFICATION.md#plex-movie-and-episode-ha-field-check--12-october-2026) · [Raw Cast evidence](VERIFICATION.md#plex-raw-cast-status-check--12-october-2026).

RM-016 and RM-017 are locally verified; installed HA acceptance remains open under RM-011 and [RM-013](#rm-013-complete-real-dashboard-and-touch-device-acceptance). Previously saved notification scripts need regeneration before reuse.

Retain the remaining order: Plex source qualification, then TiviMate guide-tuning evidence. Shared device/companion investigation remains [deferred under RM-020](#rm-020-establish-what-adb-and-a-device-companion-can-observe). Roadmap maintenance does not approve new interfaces, helpers, authentication/backend setup, live changes or publication.

---

## 🔎 Deferred source investigation

### RM-020: Establish what ADB and a device companion can observe

- [ ] **Deferred by owner on 12 October:** resume only when requested. The owner is open to ADB or an installed diagnostic app, but no permanent helper is approved.
  Only the ADB connection inventory was read before stopping; no target/playback verification, media-session/UI capture, installation or playback change occurred.
- [ ] Compare bounded ADB observations on the identity-verified intended Shield: full published media-session metadata, playback state/actions, app/context and interface nodes/markers. Print only safe fields; exclude raw dumps, credentials and private URLs.
  A dump summary may omit Android API fields; shell privileges may exceed ordinary-app access.
- [ ] If material questions remain, scope a minimal diagnostic companion to compare media-session callbacks and accessibility events/nodes with ordinary user-granted access. Measure event-driven delivery against periodic capture before claiming better speed or lower overhead.
  It would observe permitted data locally and report to HA without AI; installation cannot expose another app's private data, manufacture missing metadata or bypass Plex permissions.
- [ ] For TiviMate, test committed playing-channel identity after guide tuning without extra OK presses against RM-007's successful, unchanged and failed/cancelled cases. Catching short banners does not resolve bannerless tuning; focus alone is insufficient.
- [ ] For Plex, inspect title/series/episode, artwork, duration/position, playback state and usable item identity for a movie, episode and item/app transitions. Establish whether native data avoids separate server login; otherwise retain RM-011's lookup and shared-user limits.
- [ ] Qualify ordinary-user installation/pairing, notification/accessibility access, Android TV restricted settings, permission loss, reboot, sleep/wake and reconnect. Separate ADB-assisted grants from ordinary setup; check screen-reader/button-remapper coexistence, resource use and remote responsiveness under RM-018.
- [ ] Produce a capability matrix per app/device/version: fields/events, ADB versus ordinary-app access, permissions, timing, reliability, missing cases and setup cost. Keep current, last-observed and unknown data distinct; reject obsolete results and preserve RM-012 isolation.
  Decision gate: compare demonstrated value with installation/maintenance cost; recommend ADB only, a narrow companion, a hybrid or no viable source. Permanent services, HA pairing/authentication, central protected enrichment and new card behaviour need separate owner decisions.

---

## 📋 TiviMate delivery gates

The finite ADB-first trial was approved under [RM-006](#rm-006-decide-on-the-living-room-banner-observer-prototype). Further shared investigation is deferred under RM-020. Persistent collection depends on measured feasibility and safety; permanent helpers and new presentation require separate approval.

### RM-007: Build and qualify the banner observer

- [ ] **Partially evidenced; feasibility unresolved:** HA field transport, sampled guide rejection and one natural-banner away/return pair passed. Bannerless guide tuning, missed-switch rate, precise latency and remote responsiveness remain unqualified; a persistent collector is not implemented.
  [Field/parser evidence](VERIFICATION.md#actual-playback-banner-fields--11-october-2026) · [Guide checks and interruption limits](VERIFICATION.md#ha-channel-and-guide-check-preparation--11-october-2026) · [Manual-OK trial](VERIFICATION.md#first-finite-ha-channel-trial-result--11-october-2026) · [Natural-banner trial](VERIFICATION.md#direct-channel-tuning-ha-trial--11-october-2026).
- [ ] Resolve bannerless tuning before choosing a collector: compare successful guide tuning, browsing/unchanged return and failed/cancelled tuning in a synchronized finite trial using owner controls. Record actual playback, event times, banner visibility and candidate signals; establish whether the playing-channel marker is machine-readable and means successful playback.
  Done when: bounded cases produce zero false confirmed-current claims, with misses and latency reported; then extend to ordinary/rapid tuning, startup/reconnect, lost observations, app exit/sleep and pause across programme boundaries. Guide focus/closure, foreground app, audio restart and fresh UUIDs alone are insufficient. Record an access limitation if signals cannot distinguish the cases.
- [ ] Define attribution and compatibility: start unknown on startup/reconnect; retain observations as last observed; invalidate confirmation after missed changes, failed capture, app exit, sleep or disconnection; reject obsolete delayed results. Keep scheduled guide information separate from paused/time-shifted playback.
  Rank existing app/device playback evidence, banner-only last-observed information, an unapproved session/accessibility helper, then provider playback-session evidence. Catalogue/logo/guide endpoints do not identify the playing device/channel; helpers need a proven useful event/node. Record supported app/device/layout versions; TiviMate 5.3.3 samples do not qualify other versions.
  Dependencies: RM-020 owns access comparison; RM-018 gates sustained capture. Earlier unknown timings, missed-banner concerns and unexpected guide-test tuning remain in [verification history](VERIFICATION.md).

### RM-018: Qualify capture safety and viewing-data handling

- [ ] **Required before sustained capture:** bound the whole operation, including diagnostic calls, cancellation, failure and temporary-file cleanup. The eight-second dump timeout plus termination grace does not cover every call; the 30-second trial threshold only stops new starts.
- [ ] Prevent overlapping capture across scripts/ADB clients for one device; HA `mode: single` protects only its own script. Demonstrate scheduling from completion, failure backoff and bounded stopping. Agree and measure resource use and remote/playback responsiveness; capture spacing is not a CPU measurement or reliability result.
- [ ] Check screen-reader/button-remapper compatibility on supported versions. UI automation may suppress accessibility services; this is an unverified risk, not an observed Shield failure.
- [ ] Agree and verify minimal viewing-data retention and diagnostic output. Programme fields can enter HA responses, notifications and logs; credential filtering does not eliminate viewing-history concerns. Exclude credentials/private raw replies from saved evidence.
  Gates: RM-017 before notification trials; RM-007 feasibility before commissioning persistent collection. New collector/workflow decisions remain separate.

### RM-008: Match observed channels to provider entries

- [ ] **Awaiting RM-007 observation semantics:** establish explicit mappings, keep channel variants distinct and leave ambiguous matches unresolved. Disambiguate the two F1 UHD entries; matching names or schedules alone are insufficient.
  Done when: identified observations map unambiguously without claiming a catalogue match proves current playback. [Provider evidence](VERIFICATION.md#xtream-metadata-probe-preparation--11-october-2026).

### RM-009: Add local catalogue, logo and guide caching

- [ ] **Approach favoured; setup/backend decisions pending:** download a logo on first need, reuse shared images, retain cached images after refresh failure and agree catalogue/image refresh intervals and request limits.
  Cache guide listings for identified channels and scheduled now/next boundaries without claiming playback position; protect credentials outside public card configuration/logs and avoid rapid retries.
- [ ] Resolve transport and image-destination trust before authenticated live reuse of the [catalogue](scripts/research/xtream-logo-probe.py) and [logo](scripts/research/xtream-single-logo-probe.py) probes. HTTP/query credentials and provider logo URLs targeting local services are conditional risks, not observed leaks or backend vulnerabilities.
  Done when: an approved approach covers credentials, HTTPS/URL logging, redirects, sensitive local destinations, redacted failures/logs and focused checks; preserve intentional owner-configured private-server access and apply RM-018 retention requirements.

### RM-010: Connect confirmed observations and cached metadata to the card

- [ ] **Awaiting presentation approval:** agree channel-logo placement, programme/description/next-programme content and uncertainty handling while preserving the app logo and working play/pause.
  Done when: validated observations replace retained data correctly, gaps/app exit invalidate current attribution, and missing logos/guide entries, duplicate mappings, reconnects, paused/time-shifted content and cross-app changes have honest fallbacks.
  Dependencies: locally corrected RM-016, qualified RM-007 semantics, RM-008 mappings and agreed RM-009 caching. A retained banner cannot silently imply continuous current playback.

---

## 🧪 Remaining live acceptance

### RM-011: Finish Plex, Silo and Emby validation

- **Silo update — 13 October:** owner screenshot shows a paused title and progress with no artwork. Locally removed the missing-programme-details fallback when Silo has a current title; real details and stale/missing-title fallbacks remain. Installed acceptance of this change and broader Silo testing remain open. [Local evidence](VERIFICATION.md#silo-title-only-detail--13-october-2026).
- [ ] **Investigate Silo metadata — partial evidence, 19 October:** the owner screenshot confirms title/artwork/progress in the installed card. Two serial-verified, read-only Cast samples for Haunt supplied title, one HTTPS image address and advancing progress/duration; Android also exposed the title. No description/episode details were supplied in this movie's Cast metadata. Episode playback, item/app changes and broader freshness remain untested. [Evidence](VERIFICATION.md#silo-playback-source-check--19-october-2026).
- [ ] **Investigate Emby metadata:** perform the same field/source comparison for movie and episode playback; record what the card can already use, what needs a bounded mapping change and what would require additional setup.
  Done when, for each app: record available/missing fields, source and app/device versions, freshness across item/app changes, and practical card uses with setup/access limitations. Prefer existing ordinary-user sources; document gaps without assuming unavailable data or approving new integrations, credentials, helpers or UI changes. Full Android/companion investigation remains deferred under RM-020.
- [ ] **Plex title source unresolved; Emby untested:** three owner-run HA readings and two serial-verified direct raw Cast checks on 12 October found empty titles and no recognised series/episode details. Movie and episode receiver replies both had movie metadata type, artwork/progress and a library metadata reference; no recognised title fields were found in custom data. This does not qualify every possible vendor field or other Android source. Existing standard Cast fields cannot supply titles in these samples; a lookup/setup decision remains separate. [Entity comparison](VERIFICATION.md#plex-movie-and-episode-ha-field-check--12-october-2026) · [Raw Cast evidence and limits](VERIFICATION.md#plex-raw-cast-status-check--12-october-2026).
  Earlier passive session-description/playback-UI sources were empty. Use RM-020 for full Android metadata/callback access; it remains deferred. Empty observations do not rule out every metadata key, and an overlay is not continuous delivery. [Earlier Plex evidence](VERIFICATION.md#plex-entity-comparison--11-october-2026) · [Source limits](VERIFICATION.md#plex-title-source-availability--11-october-2026).
- [ ] If existing sources are insufficient, seek a decision on protected known-item lookup using deliberately authorised credentials, explicit server/item association and server discovery; prefer an approved HA-side location. Never place tokens in dashboard configuration or extract artwork tokens.
  Done when: a movie and episode resolve correctly; inaccessible items, wrong servers and delayed results after device/app/session/item changes are rejected; failures preserve working artwork/progress/controls. Bind requests to device, app/session generation, server and item; titles, images, duration and friendly names are insufficient identifiers.
  Ordinary-user access is the priority. The separate non-admin account test is on hold; no account creation is required and shared-user compatibility remains unknown. Rank existing HA/Cast, known-item lookup, qualified Plex Companion timeline discovery/binding/authentication, fuller Android metadata where needed, then the admin-only HA integration as last fallback. No candidate is qualified. [Investigation and owner decisions](VERIFICATION.md#plex-ordinary-user-source-investigation--11-october-2026).
- [ ] **Awaiting installed HA testing:** exercise the RM-016 fix through actual Plex/Silo/Emby transitions, missing titles, playback controls and failure fallbacks; record app/device versions separately from synthetic checks.

### RM-012: Qualify Snug and two-device isolation

- [ ] **Deferred until a viewing-free test is arranged:** verify Snug identity and qualify playback, logos, controls and metadata separately; keep room observations and connection histories independent.
  Done when: simultaneous players, selection changes and delayed/duplicate/stale responses preserve metadata and explicit control targets, including any approved enrichment bound to its originating device/session. Snug has not been tested for this card.

### RM-013: Complete real dashboard and touch-device acceptance

- **Locally verified — 19 October:** approved title/artwork/control polish passed 27 model tests, 30 existing browser checks, focused font-failure/motion/control checks and independent code review. Installed HA and phone/tablet acceptance remain open. [Evidence](VERIFICATION.md#title-and-playback-polish--19-october-2026).
- [ ] **Awaiting installed phone/tablet testing:** qualify light/dark themes, room switching, multiple active rooms, realistic/long/missing metadata, unavailable entities and failing controls. Only initial desktop HA evidence exists.
- [ ] Qualify keyboard/screen-reader use, focus retention, touch targets and narrow layouts in installed HA; local 320px/44px checks do not establish physical or assistive-technology acceptance.
- [ ] Qualify HA lifecycle/reconfiguration/reconnect, pending/failed service calls, malformed/missing progress and timestamps, and actual app transitions with RM-016. Retain duplicate-action protection, explicit entity targets, image fallbacks and disconnect cleanup; add coverage only for newly reproduced gaps. No timer leak was found in the audit.

---

## 💭 Later / proposed

### RM-014: Prepare a supported distribution

- [ ] **Awaiting defect closure and live compatibility:** establish supported HA versions, installation/update/cache-refresh instructions and explicit metadata/research/device limitations. No stable release or HACS package exists.
- [ ] Verify a complete package includes the entry module, imported `src/` modules and assets; qualify updates and cache refresh.
  Satoshi is available locally but excluded from Git under its redistribution restrictions. Resolve font distribution rights or document each user's own download before packaging; preserve the dashboard-font fallback. [Font notice](assets/NOTICE.md#local-title-font).
- [ ] Resolve TiviMate redistribution permission and include [asset notices](assets/NOTICE.md) and the restrictive custom [licence](LICENSE); local logo acceptance is not redistribution approval.
- [ ] Document reproducible maintainer/offline-research checks and prerequisites; reconcile claims with RM-016/RM-017 and separate local, native HA and physical-device evidence. No npm runtime dependencies were found; packaging does not justify a framework.
  Gates: close confirmed defects and qualify RM-011–RM-013. Publication requires a separate owner request; the source checkpoint is not a stable release.

### RM-019: Measure update cost before considering optimisation

- [ ] **Lower-priority proposal:** profile realistic multi-room HA update traffic; the card rebuilds/hashes rooms on each update, but no performance problem was demonstrated.
  Done when: measured update/render cost and responsiveness justify any bounded optimisation while preserving lifecycle cleanup, room isolation and correctness. No speculative refactor.

### RM-015: Decide on optional product improvements

- [ ] **Unapproved:** assess a visual editor, extra controls, expansion and alternative layouts for many active devices; YAML setup and the approved compact card remain the baseline. [Design boundaries](DESIGN-DECISIONS.md#still-proposals-or-unresolved).
- [ ] After RM-020, assess optional companion benefits: faster playback/progress, other-app metadata, device pairing, connection/permission/freshness health, privacy-conscious diagnostics, supported playback/seek/next/previous actions and automation signals tied to confirmed playback.
  Prefer a small optional companion feeding the existing card only if evidence supports it; these are candidates, not promises. Broader interfaces, controls and workflows need separate scope/experience approval.

---

## ✅ Completed checkpoints

### RM-017: Render research notification fields as literal text

- [x] **Locally verified — 12 October 2026.** Both notification generators render provider fields literally; 20 existing template/sequence tests, 24 rendered report cases, local Chrome checks and independent review passed.
  No injected links/images or browser requests; saved HA scripts remain unchanged and need regeneration before reuse. [Fix evidence and installed-HA limits](VERIFICATION.md#literal-research-notification-fields--12-october-2026).

### RM-016: Correct stale metadata across app changes

- [x] **Locally verified — 12 October 2026.** Corrected empty-gap provenance and independent artwork freshness; historical claims were reconciled.
  26 model and 30 browser checks plus independent model review passed; source is committed as `4c1bab6`. Installed HA acceptance remains under RM-011/RM-013. [Fix evidence](VERIFICATION.md#stale-metadata-correction--12-october-2026).

### RM-006: Decide on the Living Room banner-observer prototype

- [x] **ADB-first finite trial approved — 11 October 2026.** Existing ADB access comes before helpers; measured benefit and manageable ordinary-user setup gate further choices.
  This approves the bounded trial direction, not a permanent helper or new presentation. [Trial evidence and limits](VERIFICATION.md#adb-first-capture-trial--11-october-2026).

### RM-001: Implement the approved compact multi-room card locally

- [x] **Completed locally — 7 October 2026.** Featured room, active-room previews, honest fallbacks and supported controls passed initial automated/browser checks.
  Local sample evidence only. [Details](VERIFICATION.md#passed).

### RM-002: Install and mount the card in Living Room Home Assistant

- [x] **Completed — 11 October 2026.** Owner confirmed registration and live idle/Plex/TiviMate rendering; TiviMate pause/resume worked.
  Broader device/app acceptance remains open. [Live evidence](VERIFICATION.md#owner-assisted-live-checks--11-october-2026-in-progress).

### RM-003: Add the requested app logos and remove duplicate app headings

- [x] **Completed — 11 October 2026.** Selected rounded TiviMate symbol, Silo icon and existing Plex/Emby assets were included; 19 model and 25 browser checks passed.
  Owner confirmed TiviMate's live appearance; Silo/Emby live compatibility remains open. [Logo evidence](VERIFICATION.md#official-logo-revision--11-october-2026).

### RM-004: Establish bounded TiviMate/provider metadata feasibility

- [x] **Bounded investigation completed — 11 October 2026.** Playback-banner text is readable; guide focus is not playback identity. Provider catalogue/logo/guide were owner-verified.
  Automatic tracking is unresolved. [Device evidence](VERIFICATION.md#channel-association-banner-freshness-and-logos--11-october-2026) · [Provider evidence](VERIFICATION.md#xtream-metadata-probe-preparation--11-october-2026).

### RM-005: Commit and push the source/research checkpoint

- [x] **Completed — 11 October 2026.** [Commit 473deff](https://github.com/NetworkMD87/NMD-Media-Card/commit/473deff4d849a962737ce74b12d5d15e2b41d86d) reached `main`; 19 source and 29 mocked-network research checks passed.
  Credentials/private captures were excluded; no helper or stable release was delivered. [Checkpoint evidence](VERIFICATION.md#follow-up-architecture-investigation--11-october-2026).

---

## 🗂️ Supporting records

[Verification and historical trial results](VERIFICATION.md) · [11 October audit](codex://threads/01a12c22-2438-7e90-a190-68fa3ff85f2e) · [Approved design](DESIGN-DECISIONS.md) · [Current setup](README.md) · [Research scripts and finite-trial instructions](scripts/research/README.md) · [Asset notices](assets/NOTICE.md).

Research references: [Android sandbox](https://source.android.com/docs/security/app-sandbox), [media-session access](https://developer.android.com/reference/android/media/session/MediaSessionManager), [metadata callbacks](https://developer.android.com/reference/android/media/session/MediaController.Callback), [accessibility observations](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService), [restricted settings](https://support.google.com/android/answer/12623953), [background-service restrictions](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start).

Historical local checks missed RM-016/RM-017 and never established live acceptance. Detailed counts, timing uncertainties and failed/limited attempts remain in VERIFICATION.md and the audit. Keep dates, evidence, blockers and next actions current after authorised work; roadmap updates grant no implementation or publication authority. Stream proxying/transcoding, VPN features and unrelated device changes remain out of scope.
