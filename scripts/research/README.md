# One-off Xtream metadata research

These Python snippets preserve the bounded owner-assisted checks from 11 October 2026. They are research material, not an installed Home Assistant integration, background collector or supported setup workflow. They do not play video or run a polling loop.

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
