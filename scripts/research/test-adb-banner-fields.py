"""Synthetic regression checks for the research-only banner AWK filter."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
AWK_PROGRAM = HERE / "adb-banner-fields.awk"
AWK = os.environ.get("NMD_AWK") or shutil.which("awk") or r"C:\Program Files\Git\usr\bin\awk.exe"
SAMPLE = "f3346010-60e8-464a-a1ca-92cee1bde619"


def node(resource_id, text="", package="ar.tvplayer.tv", cls="android.widget.TextView"):
    def attr(value):
        return (value.replace("&", "&amp;").replace('"', "&quot;")
                .replace("<", "&lt;").replace(">", "&gt;"))
    return (f'<node resource-id="{attr(resource_id)}" text="{attr(text)}" '
            f'class="{attr(cls)}" package="{attr(package)}"/>')


FIELDS = [
    ("b7", "Example Sports UHD"),
    ("152", "Match: Team A v Team B"),
    ("315", "14:00 — 16:30"),
    ("3lj", "25 min"),
    ("m2", "Sample venue — café & football"),
    ("9v", "16:30 — 17:00"),
    ("37v", "Next programme"),
]


def document(children=None):
    if children is None:
        children = [node("ar.tvplayer.tv:id/" + suffix, value) for suffix, value in FIELDS]
    banner = node("ar.tvplayer.tv:id/49p", cls="android.view.ViewGroup")
    # Banner is a container, so emit an explicit opening tag.
    banner = banner[:-2] + ">" + "".join(children) + "</node>"
    return ("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><hierarchy rotation=\"0\">"
            + node("ar.tvplayer.tv:id/root", cls="android.widget.FrameLayout")[:-2]
            + ">" + banner + "</node></hierarchy>")


def run(xml, version="5.3.3"):
    proc = subprocess.run(
        [AWK, "-v", f"sample={SAMPLE}", "-v", "elapsed_ms=17", "-v",
         f"app_version={version}", "-f", str(AWK_PROGRAM)],
        input=xml, text=True, encoding="utf-8", capture_output=True, check=False,
    )
    if proc.returncode:
        raise AssertionError(f"awk failed ({proc.returncode}): {proc.stderr}")
    return json.loads(proc.stdout)


class BannerFilterTests(unittest.TestCase):
    def assert_status(self, xml, status):
        result = run(xml)
        self.assertEqual(result["status"], status)
        self.assertEqual(result["protocol"], "NMD_ADB_FIELDS_V1")
        self.assertEqual(result["sample"], SAMPLE)
        self.assertEqual(result["elapsed_ms"], 17)
        if status != "banner":
            self.assertEqual(result["fields"], {})
        return result

    def test_extracts_only_banner_fields_and_preserves_utf8(self):
        result = self.assert_status(document(), "banner")
        self.assertEqual(result["fields"]["channel"], "Example Sports UHD")
        self.assertEqual(result["fields"]["schedule"], "14:00 — 16:30")
        self.assertEqual(result["fields"]["description"], "Sample venue — café & football")
        self.assertEqual(set(result["fields"]), {"channel", "title", "schedule", "remaining", "description", "next_schedule", "next_title"})

    def test_guide_wins_even_when_banner_and_fields_are_present(self):
        guide = node("ar.tvplayer.tv:id/4ig", cls="android.widget.FrameLayout")
        self.assert_status(document([guide] + [node("ar.tvplayer.tv:id/" + a, b) for a, b in FIELDS]), "guide")

    def test_guide_marker_is_recognized_anywhere_in_tivimate_tree(self):
        xml = document()[:-len("</hierarchy>")] + node("ar.tvplayer.tv:id/2im", cls="androidx.recyclerview.widget.RecyclerView") + "</hierarchy>"
        self.assert_status(xml, "guide")

    def test_duplicate_banner_field_is_rejected(self):
        kids = [node("ar.tvplayer.tv:id/" + suffix, text) for suffix, text in FIELDS]
        kids.append(node("ar.tvplayer.tv:id/b7", "Other channel"))
        self.assert_status(document(kids), "invalid_layout")

    def test_field_outside_banner_is_never_used(self):
        outside = node("ar.tvplayer.tv:id/b7", "Wrong channel")
        xml = document()[:-len("</hierarchy>")] + outside + "</hierarchy>"
        self.assert_status(xml, "banner")
        self.assertEqual(run(xml)["fields"]["channel"], "Example Sports UHD")

    def test_missing_required_field_and_empty_channel_are_rejected(self):
        self.assert_status(document([node("ar.tvplayer.tv:id/" + a, b) for a, b in FIELDS[:-1]]), "invalid_layout")
        fields = [(a, "" if a == "b7" else b) for a, b in FIELDS]
        self.assert_status(document([node("ar.tvplayer.tv:id/" + a, b) for a, b in fields]), "invalid_layout")

    def test_required_field_must_be_textview_and_have_text_attribute(self):
        kids = [node("ar.tvplayer.tv:id/" + a, b) for a, b in FIELDS]
        kids[1] = node("ar.tvplayer.tv:id/152", "Title", cls="android.widget.EditText")
        self.assert_status(document(kids), "invalid_layout")
        xml = document().replace(' text="Match: Team A v Team B"', "", 1)
        self.assert_status(xml, "invalid_layout")

    def test_foreign_package_descendant_is_rejected(self):
        kids = [node("ar.tvplayer.tv:id/" + a, b) for a, b in FIELDS]
        kids.append(node("foreign:id/text", "private", package="other.package"))
        self.assert_status(document(kids), "invalid_layout")

    def test_malformed_truncated_and_unknown_xml_fail_closed(self):
        self.assert_status(document()[:-7], "incomplete")
        self.assert_status(document().replace("<node", "<view", 1), "invalid_layout")
        self.assert_status(document().replace(" text=\"Example Sports", " text=\"Example &bogus; Sports"), "unsafe_text")

    def test_private_or_unsafe_text_suppresses_all_fields(self):
        for unsafe_text in ("https://example.invalid/x", "Username: guest", "token=secret", "line\x01break"):
            kids = [node("ar.tvplayer.tv:id/" + a, unsafe_text if a == "m2" else b) for a, b in FIELDS]
            self.assert_status(document(kids), "unsafe_text")

    def test_json_escapes_quotes_backslashes_and_normal_newlines(self):
        title = 'A "quoted" \\ title\nsecond line'
        kids = [node("ar.tvplayer.tv:id/" + a, title if a == "152" else b) for a, b in FIELDS]
        result = self.assert_status(document(kids), "banner")
        self.assertEqual(result["fields"]["title"], title)

    def test_decimal_and_hex_tab_lf_cr_entities_decode(self):
        text = "before&#9;tab&#10;line&#13;return"
        xml = document().replace("Sample venue — café &amp; football", text)
        result = self.assert_status(xml, "banner")
        self.assertEqual(result["fields"]["description"], "before\ttab\nline\rreturn")
        xml = document().replace("Sample venue — café &amp; football", "A&#x9;B&#xA;C&#xD;D")
        result = self.assert_status(xml, "banner")
        self.assertEqual(result["fields"]["description"], "A\tB\nC\rD")

    def test_unsupported_numeric_entity_is_rejected(self):
        xml = document().replace("Sample venue — café &amp; football", "A&#65;B")
        self.assert_status(xml, "unsafe_text")

    def test_unsupported_version_returns_no_fields(self):
        result = run(document(), version="5.4.0")
        self.assertEqual(result["status"], "unsupported_version")
        self.assertEqual(result["fields"], {})

    def test_nested_banner_rejected(self):
        kids = [node("ar.tvplayer.tv:id/" + a, b) for a, b in FIELDS]
        kids.append(node("ar.tvplayer.tv:id/49p", cls="android.view.ViewGroup"))
        self.assert_status(document(kids), "invalid_layout")

    def test_self_closing_banner_is_rejected(self):
        fields = "".join(node("ar.tvplayer.tv:id/" + a, b) for a, b in FIELDS)
        root = node("ar.tvplayer.tv:id/root", cls="android.widget.FrameLayout")[:-2]
        xml = ("<hierarchy rotation=\"0\">" + root + "><node resource-id=\"ar.tvplayer.tv:id/49p\" "
               "class=\"android.view.ViewGroup\" package=\"ar.tvplayer.tv\"/>" + fields + "</node></hierarchy>")
        self.assert_status(xml, "invalid_layout")

    def test_invalid_sample_exits_before_any_device_capture(self):
        capture = (HERE / "adb-banner-capture.sh").read_text(encoding="utf-8")
        guard = capture.index("if ! nmd_uuid_valid; then")
        context = capture.index("if ! nmd_awake", guard)
        temp = capture.index("nmd_file=$(mktemp", guard)
        error_branch = capture[guard:context]
        self.assertLess(guard, context)
        self.assertLess(context, temp)
        self.assertIn("nmd_sample=00000000-0000-4000-8000-000000000000", error_branch)
        self.assertIn("nmd_emit incomplete", error_branch)
        self.assertIn("exit 0", error_branch)
        self.assertIn("[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}", capture)


if __name__ == "__main__":
    unittest.main()
