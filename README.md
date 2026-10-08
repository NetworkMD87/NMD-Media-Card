# NMD Media Card

A compact Home Assistant custom card combining configured media players into one featured-room view. This is an **early development version**, not a stable release or a live-verified Home Assistant installation.

The owner-approved design uses faded full-width artwork, app logos, a separate dark strip for other active rooms, and an idle view that remains visible. See [design decisions](DESIGN-DECISIONS.md). It adapts to the container rather than fixing the card to a desktop width.

## Local preview and checks

Requires Node.js 20 or later for the local tools. No npm dependencies or build step are required.

```powershell
node --test tests/media-model.test.js
node scripts/preview.mjs
```

Open `http://127.0.0.1:8767/`. The preview has fictional data, original sample artwork, selectable widths and light/dark themes. Play/pause calls a sample service only. Browser checks are at `http://127.0.0.1:8767/tests/browser.html`; their summary and `window.browserResults` report results. Stop the preview with Ctrl+C.

The preview serves only local demo, source, asset and browser-test files on loopback. It does not expose the private handoff or connect to Home Assistant, Plex, Emby, Silo or a Shield.

## Configuration

Configure the exact media-player entity for each device. Never list two entities for the same physical player as separate rooms merely because different integrations expose them.

```yaml
type: custom:nmd-media-card
devices:
  - entity: media_player.example_lounge
    name: Living room
  - entity: media_player.example_den
    name: Snug
```

These entity IDs are placeholders. String entries such as `- media_player.example_lounge` also work; the friendly name is used unless `name` is provided. Add more entries for additional devices. Each other active device contributes one compact preview row; inactive statuses wrap together. The first local version has no separate visual configuration editor.

The selected room stays featured while it is active. When it stops, selection falls back in configuration order, preferring playing, then paused, buffering, app-open and on states. Clicking an other-room preview changes the featured room only; it does not change device playback.

### App-open versus real playback

The default `state_source: entity` uses the configured entity's reported state. It is appropriate only when that entity actually reports playback. An open Android TV app does not by itself prove anything is playing.

For an Android TV Remote entity, an unverified universal player aggregating an assumed source, or another source with app identification only:

```yaml
type: custom:nmd-media-card
devices:
  - entity: media_player.example_android_tv
    name: Living room
    state_source: app
```

App-only mode shows the app, explicitly marks playback as unconfirmed and omits programme artwork, progress and playback controls. The card also detects `assumed_state: true` and `androidtv_remote` when its platform is supplied in HA's entity registry; explicit configuration remains necessary when that information is absent or hidden behind a universal entity. Idle, off, unknown and unavailable remain distinct.

An optional `app_name` provides a display fallback for an app-specific integration that omits its app name. Do not use a fixed app name for a device that changes applications.

### Logos and artwork

Plex and Emby logo PNGs are bundled locally. Other app names remain as readable text until a matching logo is configured. Missing or failed images fall back cleanly.

```yaml
type: custom:nmd-media-card
devices:
  - media_player.example_lounge
app_logos:
  tivimate: /local/media-logos/tivimate.png
  silo: /local/media-logos/silo.png
```

Logo keys are lowercase application names. Root-relative image paths and HTTP(S) image URLs are accepted; credentials embedded in URLs, executable URLs and inline data URLs are rejected. Keep credentials out of card configuration. See [asset provenance and third-party terms](assets/NOTICE.md).

The card uses the entity's `entity_picture`, displayed as a cover image behind a readability gradient. Artwork quality and crop depend on what the integration supplies; a poster may be cropped. It does not fetch extra posters, invent channel identity, or create a new media proxy. Local HA artwork URLs supplied by existing integrations remain usable. There is no video player or stream routing.

### Playback controls

Pause is shown only for a reported playing entity with HA's pause feature. Resume is shown only for a reported paused entity with its play feature. Requests target that configured entity; controls are rechecked when clicked. The card waits for HA state updates rather than pretending that a request succeeded.

Progress is read-only. It requires valid duration and position; elapsed time advances only for playing media with a valid position timestamp. Unknown progress is not displayed as zero. A stale integration can still report stale source data: the card clears media when playback ends and suppresses unchanged metadata across detected app switches, but cannot prove the freshness of every backend field.

## Later installation — not performed

After entity mapping and local review, the runtime files can be copied together into HA's `www/nmd-media-card/` directory:

- `nmd-media-card.js`
- `src/` (all three JavaScript modules)
- `assets/` (logos and provenance)

Register `/local/nmd-media-card/nmd-media-card.js` as a dashboard JavaScript module, then add the YAML card. Keeping the folder layout matters because the module imports and logo paths are relative. Do not copy the private project handoff, local screenshots, test logs or development files into a public package.

No stable release or HACS registration is provided. Live Home Assistant and physical-device validation remain pending.

## Verification boundary and remaining work

Local model/browser checks exercise sample state and service responses, not a real Home Assistant frontend or physical media player. The minimum supported HA release and owner/device acceptance remain unverified.

- Verify both real room entities and any universal-player children/routing.
- Inspect actual Plex/Emby metadata, progress, app identity and supported actions per device.
- Investigate Silo's server/client session reporting independently; compatibility is not established by its API claims.
- Establish whether TiviMate exposes reliable current-channel/programme data. Until then its limited-information state is intentional. Silo and TiviMate remain target apps.
- Confirm real artwork, touch/keyboard use and phone/tablet/desktop layout in the owner's dashboard.
- Decide the configuration editor, packaged releases and HACS distribution separately.

Implementation references: [HA custom cards](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/), [media-player states and features](https://developers.home-assistant.io/docs/core/entity/media-player/), and [Android TV Remote limitations](https://www.home-assistant.io/integrations/androidtv_remote/).

## Licence

Free for personal, non-commercial use under the custom [NMD Media Card licence](LICENSE). Supported configuration is allowed. Code modifications, derivative versions and commercial use require prior written permission. Unmodified copies may be shared free with the licence and notices retained. This is source-available software, not open source. Third-party assets retain their own terms in [assets/NOTICE.md](assets/NOTICE.md).
