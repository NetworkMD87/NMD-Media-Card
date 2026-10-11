# Approved design

Owner approved the featured-room design and subsequent artwork/logo revisions on 7 October 2026. This records approval, not live device acceptance.

- One unified card; device and room names come from configuration.
- Compact, attractive idle presentation that remains visible.
- A featured room, with selectable previews for other active rooms in a separate darker strip.
- Movie/episode artwork fills the featured area, with a strong readability fade. No duplicate poster when a backdrop is present.
- A restrained fallback when artwork or reliable programme information is absent. An open app is not proof of playback.
- App logos at the top right, with an accessible name and text fallback. On 11 October the owner selected TiviMate's blue website `tv` symbol with rounded corners, requested the best fitting official Silo asset and the existing Emby logo, and requested removal of the repeated app-name heading. Silo uses its square project icon, which its brand guide specifies for compact integration placements. Genuine programme titles remain visible. The TiviMate asset is for local testing pending redistribution rights confirmation.
- Supported play/pause, slim read-only progress, and retained paused content.
- Responsive to the card container. The 520px preview was explored; it is not a fixed production width.

## First local implementation boundaries

Standard Home Assistant media-player entities, configured explicitly per room. No guessed child players or server session association. Repeated preview rows support additional devices; each active room adds one compact row. No new menus, remote-control panel or editor have been added.

The featured room remains selected while active. Otherwise the first playing, paused, buffering, or app/on device in configuration order is selected. Inactive devices appear as concise status text. A missing or unknown device is not described as idle.

## Still proposals or unresolved

- Visual configuration editor, extra controls, expansion and alternative layouts for many simultaneous devices.
- Live channel identification and now/next support for TiviMate; Silo session/API compatibility.
- Owner entity mapping, real metadata quality, universal-player assumptions and device acceptance.
- App-specific/backend integrations, minimum supported HA version, HACS and packaged releases.

No stream proxying/transcoding or VPN features. No live dashboard edits, device setup, Git repository creation or publication are authorized by design approval.

## Repository and licence decision — 8 October 2026

The owner separately approved a public NetworkMD87/NMD-Media-Card repository with an initial source commit. Original project material uses the custom free non-commercial use licence in LICENSE; supported configuration is allowed, but code modifications and commercial use require permission. This approval does not establish live compatibility or approve a stable release.
