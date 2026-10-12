# NMD Media Card

A custom Home Assistant card for seeing what's playing around the house in one place.

One room takes the main spot, with artwork, programme details and playback controls. Other active rooms appear underneath; tap one to bring it into view. When nothing is playing, the card stays visible so you can still see the status of your devices.

**This is an early development version.** It has been tested locally with sample data. Initial live Home Assistant checks on one Shield showed the card's idle view, Plex playback status, artwork and progress, and TiviMate playback status with working pause/resume controls. TiviMate programme metadata and broader compatibility remain unverified. There is no stable release or HACS installation yet.

## Manual installation

If you'd like to try the development version, copy these files and folders into `config/www/nmd-media-card/` in Home Assistant:

- `nmd-media-card.js`
- `src/`
- `assets/`

Keep the folder structure intact. Add `/local/nmd-media-card/nmd-media-card.js` as a **JavaScript module** in your dashboard resources, then add a manual card using the example below.

## Set up your rooms

Replace the example entities with your own media players:

```yaml
type: custom:nmd-media-card
devices:
  - entity: media_player.example_lounge
    name: Living room
  - entity: media_player.example_den
    name: Snug
```

Add as many devices as you need, using one entity per physical player. If several integrations expose the same device, choose the entity that provides the playback information you want to use.

The `name` is optional. Leave it out to use the entity's friendly name, or use the shorter form:

```yaml
type: custom:nmd-media-card
devices:
  - media_player.example_lounge
  - media_player.example_den
```

Tap another room to see its details. This changes the card's view without interrupting playback. Your chosen room stays selected while it's active. After that, the card picks another active room, giving priority to anything playing; ties follow the order in your configuration.

Configuration is currently YAML only.

### When Home Assistant only knows which app is open

Some entities can tell you that an app is open without knowing whether it's playing anything. For those, use `state_source: app`:

```yaml
type: custom:nmd-media-card
devices:
  - entity: media_player.example_android_tv
    name: Living room
    state_source: app
```

The card will show the app name and mark playback as unconfirmed. Artwork, progress and play/pause controls are hidden in this mode.

This is useful for Android TV Remote entities and universal players that rely on an assumed playback state. The card detects some of these cases automatically, but use the setting explicitly if your entity doesn't provide that information.

The default, `state_source: entity`, uses the playback state reported by your media player. If an integration dedicated to a single app leaves out its name, you can add `app_name` to that device's configuration. Avoid setting a fixed app name on a device that switches between apps.

### Logos and artwork

Plex, Emby and Silo logos are included. The current local test also includes the owner's selected TiviMate website symbol (see its separate asset notice). You can supply or override logos through `app_logos`:

```yaml
type: custom:nmd-media-card
devices:
  - media_player.example_lounge
app_logos:
  tivimate: /local/media-logos/tivimate.png
  silo: /local/media-logos/silo.png
```

Use lowercase app names as the keys. Image paths starting with `/` and HTTP(S) URLs are supported. URLs containing a username or password, executable URLs and inline data URLs are rejected. Keep credentials out of your configuration.

If a logo is missing or won't load, the app name is shown as text. Artwork comes from the media player's `entity_picture`; its quality and crop depend on what the integration provides.

An app name is shown once in the corner. The programme heading is omitted when only an app name is available; genuine programme titles remain visible. Android Debug Bridge supplies periodic screen captures for `entity_picture`, rather than programme artwork.

See [the asset notices](assets/NOTICE.md) for logo sources and third-party terms.

### Playback controls

Play and pause appear when the selected entity reports a suitable playback state and supports the action. The display updates when Home Assistant reports the new state.

The progress bar is for display only; you can't use it to seek. It appears when the entity supplies a valid position and duration. Missing progress information is left out.

## What to expect

The card displays information supplied by Home Assistant. It doesn't play or relay video, and it can't fill in titles, artwork or channel details that an integration doesn't provide.

Further real-device testing is still needed for Plex and Emby. Silo compatibility and TiviMate channel information are also unconfirmed. If an integration reports old information, the card may still show it, although it clears details when playback ends and handles detected app changes.

The minimum supported Home Assistant version hasn't been established yet. Further live dashboard testing, phone and tablet testing, a visual configuration editor and HACS distribution are still ahead. The [roadmap](ROADMAP.md) tracks remaining work and the next decision; the [verification notes](VERIFICATION.md) record the local checks and initial live results.

## Run the demo locally

You'll need Node.js 20 or later. There are no npm dependencies to install and no build step.

```sh
node scripts/preview.mjs
```

Open `http://127.0.0.1:8767/` to try the card with sample rooms and artwork. You can switch between light and dark themes and different card widths. The demo doesn't connect to your devices, and its playback buttons only affect the sample data. Stop the server with Ctrl+C.

Run the model tests with:

```sh
node --test tests/media-model.test.js
```

With the preview server running, browser checks are available at `http://127.0.0.1:8767/tests/browser.html`.

## Licence

You're welcome to use NMD Media Card free for personal, non-commercial use and configure it for your own setup. You can also share unmodified copies for free, keeping the licence and notices included.

Changing the code, creating derivative versions or using it commercially requires prior written permission. The source is public, but this is **not an open-source licence**. Read the [full licence](LICENSE) for the terms; third-party assets keep their [own terms](assets/NOTICE.md).
