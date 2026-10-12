"""Offline rendered-output regressions for both generated notifications.

Requires the existing Jinja2 test environment and Marked (test-only).
Set NMD_MARKED_MODULE to the absolute path to marked/lib/marked.esm.js.
No HA, ADB, provider or network calls are made.
"""
import html.parser
import json
import os
import pathlib
import runpy
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).parent
CHECK = runpy.run_path(str(ROOT / "test-ha-adb-channel-check.py"))
TRIAL = runpy.run_path(str(ROOT / "test-ha-adb-channel-trial.py"))
LABELS = dict(zip(CHECK["FIELDS"], [
    "Channel", "Current", "Schedule", "Remaining", "Description", "Next schedule", "Next",
]))
PAYLOADS = [
    'Match: Home & Away — München "quotes"',
    "![image](//notification.invalid/image.png) [link](//notification.invalid/page)",
    "[reference][target]\n\n[target]: //notification.invalid/reference",
    "www.notification.invalid user@notification.invalid <//notification.invalid/auto>",
    "first line\n\n![image](//notification.invalid/multiline.png)\n# heading\n> quote",
    "```\n![image](//notification.invalid/backtick.png)\n```\n~~~\n[link](//notification.invalid/tilde)\n~~~",
    '</pre><img src="//notification.invalid/html.png"><a href="//notification.invalid/html">link</a>',
    '&lt;/pre&gt; &#60;img src="//notification.invalid/entity.png"&#62; &amp; München "quotes"',
    "backslash \\ `inline` **bold** _italic_ ~~strike~~ {{ 7 * 7 }} {% endraw %}",
    "first\r\n![image](//notification.invalid/crlf.png)\r[link](//notification.invalid/cr)",
    "",
    "`" * 4096 + "~" * 4096,
]


def cases():
    for index, payload in enumerate(PAYLOADS):
        packet = CHECK["packet"]()
        packet["fields"] = {name: (payload or "Example UHD") if name == "channel" else payload
                            for name in CHECK["FIELDS"]}
        check = CHECK["CheckHarness"](CHECK["wrapped"](packet)).run()
        trial = TRIAL["ChannelTrialHarness"]([
            TRIAL["wrapped"](TRIAL["packet"](1, fields=packet["fields"])),
            *[TRIAL["wrapped"](TRIAL["packet"](i, "no_banner")) for i in range(2, 9)],
        ]).run()
        for kind, harness, names in [
            ("check", check, ["channel", "title", "schedule", "remaining", "description", "next_title", "next_schedule"]),
            ("trial", trial, ["channel", "title", "schedule"]),
        ]:
            yield {
                "name": f"{kind}-{index}", "message": harness.notifications[0]["message"],
                "expected": [f"{LABELS[name]}: {packet['fields'][name]}".replace("\r\n", "\n").replace("\r", "\n")
                             for name in names],
            }


class OutputParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.in_pre = False
        self.forbidden = []

    def handle_starttag(self, tag, attrs):
        if tag in {"a", "img", "iframe", "video", "audio", "source", "script", "link", "object", "embed"}:
            self.forbidden.append(tag)
        if self.in_pre:
            self.forbidden.append(tag)
        if tag == "pre":
            self.in_pre = True
            self.blocks.append("")

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False

    def handle_data(self, data):
        if self.in_pre:
            self.blocks[-1] += data


class NotificationReportsTests(unittest.TestCase):
    def test_both_reports_render_all_fields_literally(self):
        fixtures = list(cases())
        module = pathlib.Path(os.environ["NMD_MARKED_MODULE"]).resolve().as_uri()
        # Match HA's gfm/breaks options and token-by-token parsing. Inspect
        # BEFORE its XSS filter: safe output must not depend on sanitization.
        code = """const { marked } = await import(process.env.NMD_MARKED_URI);
let input = ''; for await (const chunk of process.stdin) input += chunk;
marked.setOptions({gfm: true, breaks: true});
console.log(JSON.stringify(JSON.parse(input).map(c => ({name: c.name,
  html: marked.lexer(c.message).map(t => marked.parser([t])).join('')}))));"""
        result = subprocess.run(["node", "--input-type=module", "-e", code],
                                input=json.dumps(fixtures), text=True, encoding="utf-8",
                                capture_output=True, check=True, timeout=30,
                                env={**os.environ, "NMD_MARKED_URI": module})
        outputs = json.loads(result.stdout)
        self.assertEqual(len(outputs), len(fixtures))
        for fixture, output in zip(fixtures, outputs):
            with self.subTest(case=fixture["name"]):
                parser = OutputParser()
                parser.feed(output["html"])
                self.assertFalse(parser.forbidden)
                self.assertEqual(parser.blocks, fixture["expected"])


if __name__ == "__main__":
    if "--fixtures" in sys.argv:
        print(json.dumps(list(cases()), ensure_ascii=False))
    else:
        if not os.environ.get("NMD_MARKED_MODULE"):
            sys.exit("Set NMD_MARKED_MODULE to the absolute path to marked/lib/marked.esm.js (test-only).")
        unittest.main()
