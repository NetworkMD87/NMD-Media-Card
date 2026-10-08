# Local verification — 7 October 2026

First local implementation of the approved featured-room design. This report does not establish live Home Assistant compatibility or physical-device acceptance.

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

## Still unverified

Real HA mounting/theme behavior, real entity and universal-player routing, metadata freshness supplied by integrations, artwork quality, supported controls on either physical Shield, Silo session compatibility, TiviMate channel identity and phone/tablet physical touch interaction. No licence, minimum HA version, distribution or release acceptance is implied.
