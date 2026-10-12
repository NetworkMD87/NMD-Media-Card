# NMD Media Card roadmap

Last updated: 2026-10-12

## 🎯 Next up

[RM-016 — Correct stale metadata across app changes](#rm-016-correct-stale-metadata-across-app-changes).

Next action: reproduce the two confirmed metadata defects with focused regression tests, then correct metadata provenance without changing the approved compact presentation. Follow with [literal research notifications](#rm-017-render-research-notification-fields-as-literal-text), [Plex source qualification](#rm-011-finish-plex-silo-and-emby-validation), and [TiviMate guide-tuning evidence](#rm-007-build-and-qualify-the-banner-observer). Qualify real HA behaviour before [supported distribution](#rm-014-prepare-a-supported-distribution); [capture safeguards](#rm-018-qualify-capture-safety-and-viewing-data-handling) gate any sustained capture.

The shared [ADB/companion feasibility investigation](#rm-020-establish-what-adb-and-a-device-companion-can-observe) supports the Plex and TiviMate items. On 12 October the owner requested recording it for later, explicitly stopping immediate device investigation; do not resume testing or installation until requested.

The [11 October audit](codex://threads/01a12c22-2438-7e90-a190-68fa3ff85f2e) is the source for the findings added on 12 October. It reported 19 model, 25 browser and 83 offline research checks passing, plus syntax/whitespace checks and a 320px layout check with 44px controls. Those historical local checks missed the confirmed defects and do not establish live HA/device acceptance. The audit accessed no live HA, devices or private servers. This update records the work and its order; it does not approve new interfaces, helpers, backend/authentication setup, live changes or publication.

## 🔧 Confirmed audit defects

### RM-016: Correct stale metadata across app changes

- [ ] **P2 — Preserve meaningful metadata provenance through empty inactive gaps.** Plex playing → empty `off`/`idle`/`unavailable` → Emby with inherited attributes can display the old Plex title, artwork and progress as current. Keep the last meaningful source identity independently of empty snapshots. [Affected model](src/media-model.js).
- [ ] **P2 — Stop artwork-only refreshes validating unrelated programme fields.** After cross-app suppression, changing only `entity_picture` can restore the old title and progress. Track artwork freshness separately from programme/item identity.
  Done when: focused regressions cover both sequences, old fields remain suppressed, legitimate same-app resume works, and one room cannot affect another. Run relevant model/browser checks; real installed app-transition acceptance remains under RM-011/RM-013.
- [ ] Reconcile the earlier provenance-fix claim in [VERIFICATION.md](VERIFICATION.md#findings-corrected) with the reproduced gaps and subsequent fix evidence; preserve the historical result and distinguish local from live checks.

### RM-017: Render research notification fields as literal text

- [ ] **P2 — Prevent provider programme text becoming Markdown links or images.** HTML escaping in the [one-shot report](scripts/research/ha_adb_channel_check.py) and [finite trial report](scripts/research/ha_adb_channel_trial.py) leaves Markdown syntax active. Correct both before further report-based trials.
  Done when: hostile image/link syntax, protocol-relative URLs, multiline fields and fence delimiters render literally without injected links/images or network requests. Add focused regressions and inspect rendered output; distinguish local rendering from installed HA verification. The audit reproduced template/parser acceptance, not a live HA network effect, credential theft or code execution.

---

## ✅ Approved direction

### RM-006: Decide on the Living Room banner-observer prototype

- [x] ADB-first trial approved 11 October 2026.
  Capture natural banners through the existing ADB route before considering a helper app. Keep eventual setup manageable for other HA users. [Trial evidence and limits](VERIFICATION.md#adb-first-capture-trial--11-october-2026).

## 🔎 Shared metadata-source investigation

### RM-020: Establish what ADB and a device companion can observe

- [ ] **Deferred by owner on 12 October — investigate before choosing a solution.** The owner is open to either ADB or an installed diagnostic app to establish exactly what information is obtainable. This is willingness to revisit the approach, not approval to continue testing now or build a permanent helper. Only the ADB connection inventory was read before stopping; no target identity/playback verification, media-session/UI capture, app installation or playback change occurred in that attempt.
- [ ] Start with bounded ADB checks on the identity-verified intended Shield: available media-session metadata, playback state/actions, package/context, and relevant interface nodes or markers. Inspect safe fields without printing raw dumps, credentials or private URLs. Establish what the shell actually exposes; an ADB dump's summary may omit fields available through Android APIs, while shell privileges may exceed those of an ordinary installed app.
- [ ] If ADB leaves material questions unanswered, scope a minimal diagnostic companion to compare full published media-session fields/callbacks and relevant accessibility events/nodes. Determine whether an installed app is necessary to observe those events and whether the same information is available with ordinary user-granted access. Measure event-driven observation against periodic captures; faster delivery or lower overhead is a hypothesis until measured.
  The companion would observe permitted data locally and report to HA; no AI is required. Installation does not grant access to another app's private database, credentials or unpublished playback internals. It cannot manufacture a missing channel identifier or title. [Android app sandbox](https://source.android.com/docs/security/app-sandbox) · [Media-session access](https://developer.android.com/reference/android/media/session/MediaSessionManager) · [Metadata/playback callbacks](https://developer.android.com/reference/android/media/session/MediaController.Callback) · [Accessibility observations](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService).
- [ ] For TiviMate, determine whether events expose a committed playing-channel identity after guide tuning without an extra OK press. Compare actual successful playback with guide browsing, unchanged return and failed/cancelled tuning using RM-007's acceptance cases. Catching more short banners is useful but does not itself solve bannerless tuning; focus/selection alone is insufficient.
- [ ] For Plex, inspect the full published metadata rather than only its description: title/series/episode, artwork availability, duration/position, playback state and usable item identity where supplied. Test a movie, an episode and item/app transitions. If native data suffices, establish whether it avoids a separate server login; otherwise retain RM-011's authenticated known-item lookup and shared-user limitations. A companion does not bypass Plex permissions. Central protected HA-side enrichment is a design candidate, not an approved backend.
- [ ] Qualify ordinary-user setup and lifecycle before recommending the helper: installation/pairing, necessary notification/accessibility access, restricted-settings differences across Android TV versions, permission loss, reboot, sleep/wake and reconnection. Distinguish ADB-assisted grants from setup an ordinary user can complete. Check coexistence with screen readers/button remappers, resource use and remote/playback responsiveness under RM-018; do not promise reliable background operation before testing. [Restricted settings](https://support.google.com/android/answer/12623953) · [Background-service restrictions](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start).
- [ ] Produce a capability matrix per tested app/device/version: obtainable field/event, ADB versus ordinary-app access, required permission, update timing, reliability, missing cases and setup burden. Separate confirmed-current information from last observed/unknown, reject obsolete results, and retain RM-012 device isolation. Record unsupported sources explicitly rather than presenting a small passing sample as general compatibility.
  Decision gate: demonstrate the value for TiviMate and/or Plex, then compare that value with installation and maintenance cost. Recommend ADB only, a narrowly scoped companion, a hybrid, or no viable source. Any permanent service, HA pairing/authentication workflow or new card behaviour requires a concrete owner decision; research success is not product approval.

## 📋 TiviMate work remaining

The ADB-first trial is approved. Proceed to a persistent collector only if measured results justify it; a permanent helper and new card presentation still need separate owner approval. The owner is open to companion feasibility research under RM-020, deferred for now.

### RM-007: Build and qualify the banner observer

- [ ] HA field transport, guide rejection and one natural-banner channel-up/down pair confirmed; guide-based tuning without a banner, wider capture rate and qualification remain unresolved.
  First owner-run R2 banner result: fresh sample, all seven populated fields, 2,120 ms device check and 2,325 ms HA action. Two guide-browsing methods returned no channel fields (`no_banner` and explicit `guide` rejection). This confirms the tested one-shot cases, not continuous tracking or every guide layout. [HA field capture](VERIFICATION.md#first-ha-channel-field-capture--11-october-2026) · [Guide checks](VERIFICATION.md#owner-ha-guide-browsing-checks--11-october-2026).
  First run: seven captures in 33.4 seconds with one text-positive sample despite two tuning banners. Controlled repeat: eight in 28.5 seconds with two text-positive samples and immediate owner-observed banner response. Sample timing still needs care; no channel-tracking reliability claim. [First result](VERIFICATION.md#first-automatic-ha-trial--11-october-2026) · [Repeat](VERIFICATION.md#controlled-automatic-ha-repeat--11-october-2026).
  The manually started script is finite, uses the existing ADB connection and leaves a count/timing summary. Eight trial and nine diagnostic checks passed offline with independent review. [Trial setup](scripts/research/README.md#finite-automatic-ha-trial).
  Owner-run HA captures reported 2,120 ms with zero text when closed, then 2,100 ms with 12 text fields and one description field when visible. Laptop ADB separately captured both natural banners in one brief adjacent-channel/return pair. These establish neither reusable channel parsing nor missed-switch rates. [Details](VERIFICATION.md#adb-first-capture-trial--11-october-2026).
  A further authorised direct-ADB check read channel, current title/description/schedule, remaining minutes and next title/schedule from one common banner container in TiviMate 5.3.3. RTL 4K was captured and Main Event restored; all seven fields were checked offline in three private samples. This is a version-specific field map, not an implemented HA collector or accepted guide classifier. [Field evidence](VERIFICATION.md#actual-playback-banner-fields--11-october-2026).
  The new input-free filter rejects observed guide containers, scopes unique fields to one playback-banner container and rejects stale/malformed/context-changed responses. Eight saved-screen comparisons and Android parser checks passed. A guide navigation test exceeded the intended short interruption and unexpectedly tuned RTL; Main Event was restored and verified. Further guide checks use owner controls. [Preparation and limits](VERIFICATION.md#ha-channel-and-guide-check-preparation--11-october-2026) · [One-shot setup](scripts/research/README.md#one-shot-ha-channel-and-guide-check).
  The finite field trial completed through HA: eight fresh captures in 31.2 seconds, two guide rejections and one F1 UHD banner. The owner used the guide and reports pressing OK to expose the banner. This verifies finite execution and field parsing, not automatic detection of guide-based switches or an away/return capture rate. The owner cannot recall exact switch/OK/return timings; remote lag remains unreported. [Trial result](VERIFICATION.md#first-finite-ha-channel-trial-result--11-october-2026) · [Preparation](VERIFICATION.md#finite-ha-channel-trial-preparation--11-october-2026) · [Instructions](scripts/research/README.md#finite-automatic-ha-channel-trial).
  Direct channel-up/down repeat: eight fresh captures in 31.5 seconds; F1 UHD then Main Event accepted, with natural banners reported for both switches. This passes the bounded owner-run away/return case; switch times are approximate and remote lag remains unreported. Guide tuning and broader reliability are still open. [Direct-tuning result](VERIFICATION.md#direct-channel-tuning-ha-trial--11-october-2026).
  Next for this item: investigate reliable playback evidence for guide-based tuning through existing ADB, without requiring extra owner input, before implementing a persistent collector. Preserve earlier unknown timings and missed-banner concerns.
  Test ordinary, rapid and guide-based tuning; reject guide browsing as playback evidence. Measure missed captures, delay, resource use and remote responsiveness before claiming reliability. Use a finite trial with no overlapping dumps; avoid permanent polling until those results support it.
  Validate startup/reconnection, lost observations, app exit/sleep and pause across a programme boundary. Distinguish last-observed channel from confirmed-current information; do not assume a connection proves every switch was captured.

- [ ] Resolve the bannerless guide-tuning feasibility gate before choosing a collector. Compare successful guide tuning, browsing/return without a change, and failed/cancelled tuning in a synchronized finite trial. Record actual playback, event times, natural-banner visibility and candidate app/device signals; investigate whether the observed playing-channel marker is machine-readable and means successful playback.
  Done when: the bounded cases produce zero false confirmed-current claims, with misses and latency reported; then extend to rapid tuning, startup and reconnect. Guide focus/closure, foreground app and audio restart alone are insufficient. If accessible signals cannot distinguish the cases, record the existing-access limitation rather than increasing polling speed.
- [ ] Define attribution and compatibility limits for any proposed observer. Start unknown on startup/reconnect; treat retained data only as last observed. Invalidate confirmation after missed changes/capture failure, app exit, sleep or disconnection; reject delayed results from obsolete observations. A fresh UUID proves a new response, not correct playback attribution. Keep scheduled guide information distinct from actual paused/time-shifted playback at programme boundaries.
  Rank existing app/device playback evidence first, banner-only last-observed information second, an unapproved accessibility/session helper third, and provider playback-session evidence fourth. A helper needs proof that a useful event/node exists; provider catalogue/logo/guide endpoints do not identify the playing device/channel. Record supported TiviMate/device/layout versions; 5.3.3 samples do not qualify other versions. Sustained capture also depends on RM-018; no satisfactory bannerless method is established.
  Use RM-020 for the shared ADB-versus-companion access comparison; this item owns channel-attribution acceptance rather than duplicating that investigation.

### RM-018: Qualify capture safety and viewing-data handling

- [ ] Bound the entire capture operation, not only the UI dump. The existing eight-second dump timeout plus termination grace does not cover every diagnostic call; the 30-second trial threshold stops new starts, not an in-flight action. Check timeout, cancellation, failure and temporary-file cleanup across the full sequence.
- [ ] Prevent overlap across scripts/ADB clients for the same device; HA `mode: single` only protects its own script. Before sustained polling, demonstrate one capture at a time, scheduling from completion, failure backoff and bounded stopping. Agree acceptable resource use and remote/playback responsiveness, then measure them; historical 3.8–4.7-second start gaps are not CPU measurements or reliability proof.
- [ ] Check accessibility-service compatibility on the supported device/version. Android UI automation may suppress services such as screen readers/button remappers; input-free capture alone does not establish non-interference. This is an unverified risk, not an observed Shield failure.
- [ ] Agree minimal viewing-data retention and diagnostic output before a permanent collector. Accepted programme fields may enter HA responses, notifications and logs; filtering credential strings does not remove viewing-history privacy concerns. Keep credentials/private raw replies out of saved evidence and verify the chosen retention behaviour.
  Gate: finish RM-017 before further notification trials and establish RM-007 feasibility before commissioning persistent collection. New collector/workflow decisions remain separate from this roadmap update.

### RM-008: Match observed channels to provider entries

- [ ] Association still incomplete.
  Establish explicit mappings that keep channel variants separate and leave ambiguous matches unresolved. Disambiguate the two F1 UHD entries; matching names or identical schedules alone are insufficient. [Existing provider evidence](VERIFICATION.md#xtream-metadata-probe-preparation--11-october-2026).
  Dependency: RM-007 must establish observation semantics before any mapping is presented as the currently playing channel; a catalogue match cannot repair missing playback evidence.

### RM-009: Add local catalogue, logo and guide caching

- [ ] Approach favoured; not implemented.
  Download a logo only when its channel is first needed, then retain it locally. Agree catalogue/image refresh intervals and request limits; reuse shared logo images and keep cached images when refresh fails.
  Keep credentials outside public card configuration/logs, protect metadata collection and handle request failures without repeated rapid retries. Cache guide listings for the identified channel and update scheduled now/next at programme boundaries without claiming live playback position.
- [ ] Resolve research-provider transport and image-fetch trust before reusing probes in a supported backend. The [catalogue probe](scripts/research/xtream-logo-probe.py) and [logo probe](scripts/research/xtream-single-logo-probe.py) permit HTTP and credentials in request queries. HTTP exposes those values in transit; HTTPS does not remove provider-side URL logging. Provider-supplied logo URLs may target localhost/LAN services. These are conditional risks, not evidence of a leak or an existing backend vulnerability.
  Done when: an approved credential/transport and destination-validation approach covers redirects, sensitive local destinations, failure paths and redacted errors/logs, with focused checks before authenticated live use. Preserve intentional owner-configured private-server access; agree backend/setup choices first. Apply RM-018's viewing-data requirements to stored guide/observation data.

### RM-010: Connect confirmed observations and cached metadata to the card

- [ ] Presentation decision pending.
  Agree channel-logo placement, programme/description/next-programme presentation and how uncertainty is shown. Retain observations after the banner closes; replace them on a new validated banner and invalidate current attribution after observation gaps or app exit.
  Preserve working play/pause and the app logo. Verify missing logos/guide entries, duplicate mappings, reconnects, paused/time-shifted content and cross-app changes with honest fallbacks.
  Dependencies: RM-016 metadata fixes, qualified observation semantics in RM-007, explicit mappings in RM-008 and the agreed cache approach in RM-009. No retained banner may silently become a claim of continuous current playback; owner approval is still needed for how uncertainty appears.

## 🧪 Remaining live compatibility checks

### RM-011: Finish Plex, Silo and Emby validation

- [ ] Awaiting further investigation/testing.
  Owner comparison restored Plex artwork/progress through `media_player.master_nvidia_shield`. Parent and active child titles are empty; no Plex-integration entities were returned, the passive Android session description was empty and normal playback UI had no text/description nodes. The owner administers the server but wants ordinary-user routes investigated first; the standard admin integration is a last fallback. Library-item metadata lookup is documented, but shared-user access and a suitable setup/credential flow are not qualified or implemented. The proposed non-admin account test is unavailable and on hold by owner instruction; continue investigating existing-access sources without requiring account creation. Real titles, app transitions and controls remain open; live Silo/Emby compatibility is unverified. [Plex source comparison](VERIFICATION.md#plex-entity-comparison--11-october-2026) · [Title-source availability](VERIFICATION.md#plex-title-source-availability--11-october-2026) · [Ordinary-user route investigation](VERIFICATION.md#plex-ordinary-user-source-investigation--11-october-2026).

- [ ] Complete a bounded comparison of existing HA/Cast fields and underlying Cast data, using whitelisted output. Empty standard fields explain the current fallback; no Plex title-rendering bug was demonstrated. Null Android metadata descriptions do not rule out every metadata key. No overlay-dependent source should be treated as continuous title delivery.
  Coordinate full Android metadata and callback feasibility through RM-020; an installed diagnostic app is an option to investigate, not proof that additional Plex fields exist.
- [ ] If existing sources are insufficient, decide on a protected known-item lookup proof using deliberately authorised credentials, server discovery and explicit server/item association. An approved HA-side location is preferred; never place tokens in dashboard configuration or extract them from artwork URLs. Setup/backend approval remains required; shared-user access stays unverified without suitable evidence and no separate account is required.
  Done when: one movie and one episode resolve correctly; inaccessible items, server mismatches and results arriving after device/app/session/item changes are rejected. Failures preserve working artwork/progress and controls. Bind each request to device, app/session generation, server and item; titles, pictures, duration and friendly names are not sufficient identifiers.
  Ranked alternatives after existing HA/Cast data and known-item lookup: qualify Plex Companion timeline discovery/binding/authentication against the current Shield before relying on the legacy protocol; investigate fuller Android session metadata only if needed, with helper/permission requirements explicit; retain the standard admin-only HA Plex integration as the last fallback. None is established as a supported title source by the audit. [Audit and primary-source references](codex://threads/01a12c22-2438-7e90-a190-68fa3ff85f2e).
- [ ] After RM-016, exercise actual Plex/Silo/Emby app transitions, missing titles, playback controls and failure fallbacks in installed HA. Record app/device versions and results separately from synthetic browser coverage.

### RM-012: Qualify Snug and two-device isolation

- [ ] Deferred; Snug has not been tested for this card.
  Arrange a viewing-free test, verify the intended device and qualify playback, logos, controls and metadata separately. Keep observations and connection histories independent; delayed or duplicate observations must not move data between rooms.
  Done when: two simultaneous players, room selection changes and delayed/stale responses preserve correct metadata and explicit control targets. Include any subsequently approved enrichment source; its results must remain tied to the originating device/session. Preserve the deferred status until testing is arranged.

### RM-013: Complete real dashboard and touch-device acceptance

- [ ] Only initial desktop HA checks completed.
  Check real phone/tablet interaction, light/dark themes, room switching and multiple active rooms with realistic metadata. Include missing/unavailable entities and controls failing; local sample tests do not establish physical acceptance.
- [ ] Qualify keyboard and screen-reader use, focus retention, touch targets, narrow layouts and long/missing metadata in installed HA. The audit's 320px/44px sample is useful local evidence, not phone/tablet or assistive-technology acceptance.
- [ ] Cover actual HA lifecycle/reconfiguration and reconnect behaviour, pending/failed service calls, malformed/missing progress values and timestamps, and app transitions after RM-016. Retain existing duplicate-action protection, explicit entity targeting, image fallbacks and disconnect timer cleanup; no timer leak was found in the audit. Add focused coverage for newly reproduced gaps rather than duplicating passing tests.

## 💭 Later / proposed

### RM-014: Prepare a supported distribution

- [ ] No stable release or HACS package yet.
  Establish supported HA versions, installation/update and cache-refresh instructions, compatibility limits and third-party asset redistribution terms before wider distribution. Any release/publication requires a separate owner request; the source checkpoint is not a stable release.
- [ ] Verify a complete install/update package includes the entry module, imported `src/` modules and assets together; test module/cache refresh and document supported versions and known device/app limits. HACS packaging is not yet implemented.
- [ ] Resolve TiviMate asset redistribution permission in [asset notices](assets/NOTICE.md), and include required third-party notices and the existing restrictive custom [licence](LICENSE) in distribution instructions. Local logo acceptance does not establish redistribution rights.
- [ ] Document reproducible maintainer checks and tool prerequisites, including offline research tooling; separate local/synthetic checks from native HA and physical-device results. Reconcile documentation claims with RM-016/RM-017 evidence before distribution. No npm runtime dependencies were found; do not introduce a framework simply for packaging.
  Gate: close the confirmed defects and document real compatibility under RM-011–RM-013, with unresolved metadata/research capabilities clearly labelled. Release/publication still requires its own request.

### RM-019: Measure update cost before considering optimisation

- [ ] Proposed, lower priority: profile realistic multi-room HA update traffic. The card rebuilds and hashes each configured room on every HA update, but the audit found no demonstrated performance problem.
  Done when: record update/render cost and responsiveness under representative loads; propose a bounded optimisation only if measurements justify it. Preserve lifecycle cleanup, room isolation and metadata correctness; no speculative refactor.

### RM-015: Decide on optional product improvements

- [ ] Unapproved proposals.
  Visual configuration editor, extra controls, expansion and alternative layouts for many simultaneous devices. Keep YAML setup and the approved compact card as the current baseline. [Design boundaries](DESIGN-DECISIONS.md#still-proposals-or-unresolved).
- [ ] After RM-020, assess optional companion capabilities separately: faster playback/progress updates, other supported apps' programme metadata, per-device pairing, connection/permission/freshness health, privacy-conscious diagnostics, supported play/pause/seek/next/previous actions and HA automation signals based on confirmed playback. These are candidate benefits, not promised features; each depends on the source app and tested access.
  Prefer a small optional companion feeding the existing compact card if evidence supports it. Broader controls, interfaces and automation workflows require their own scope/experience decision; keep stream proxying/transcoding and VPN features out of scope.

---

## ✅ Completed checkpoints

### RM-001: Implement the approved compact multi-room card locally

- [x] Completed 7 October 2026.
  Featured room, active-room previews, honest playback fallbacks and supported controls implemented; initial automated/browser checks passed. This was local sample evidence. [Details](VERIFICATION.md#passed).

### RM-002: Install and mount the card in Living Room Home Assistant

- [x] Completed 11 October 2026.
  Owner confirmed resource registration and live idle/Plex/TiviMate rendering. TiviMate card pause/resume worked; broader device/app compatibility remains open. [Live checks](VERIFICATION.md#owner-assisted-live-checks--11-october-2026-in-progress).

### RM-003: Add the requested app logos and remove duplicate app headings

- [x] Completed 11 October 2026.
  Selected TiviMate symbol with rounded corners, Silo icon and existing Plex/Emby assets included. 19 model and 25 browser checks passed; owner confirmed TiviMate live appearance. [Logo evidence](VERIFICATION.md#official-logo-revision--11-october-2026).

### RM-004: Establish bounded TiviMate/provider metadata feasibility

- [x] Completed 11 October 2026.
  Playback-banner text is readable; guide focus is not playback identity. Provider catalogue, Main Event logo and matching guide were owner-verified; automatic channel tracking is not established. [Device evidence](VERIFICATION.md#channel-association-banner-freshness-and-logos--11-october-2026) · [Provider evidence](VERIFICATION.md#xtream-metadata-probe-preparation--11-october-2026).

### RM-005: Commit and push the source/research checkpoint

- [x] Completed 11 October 2026.
  [Commit 473deff](https://github.com/NetworkMD87/NMD-Media-Card/commit/473deff4d849a962737ce74b12d5d15e2b41d86d) reached `main`; 19 source and 29 mocked-network research checks passed. Credentials/private captures were excluded; no helper was delivered.

## 🗂️ Supporting records

[Verification evidence](VERIFICATION.md) · [11 October audit report](codex://threads/01a12c22-2438-7e90-a190-68fa3ff85f2e) · [Approved design](DESIGN-DECISIONS.md) · [Current setup](README.md) · [One-off research scripts](scripts/research/README.md) · [Asset notices](assets/NOTICE.md).

This roadmap tracks outcomes and next actions; detailed historical checks remain in VERIFICATION.md. Update affected entries after authorised work, retaining the distinction between local tests, live checks, implementation and release. No stream proxying/transcoding, VPN features or unrelated device changes are in scope.
