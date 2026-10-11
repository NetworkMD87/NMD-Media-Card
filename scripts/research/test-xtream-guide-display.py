import base64
import contextlib
import datetime
import io
import pathlib
import runpy
import time
from unittest.mock import patch

source = pathlib.Path(__file__).with_name("xtream-guide-display.py")
start = int(datetime.datetime(2026, 10, 11, 12, tzinfo=datetime.timezone.utc).timestamp())
private = {"server": "https://private.invalid", "username": "private-user", "password": "private-pass"}
def entry(title, offset=0, duration=3600):
    return {"title": title, "start_timestamp": str(start + offset), "stop_timestamp": str(start + offset + duration)}
def check(entries):
    output = io.StringIO()
    with patch.object(time, "time", return_value=start + 1800), contextlib.redirect_stdout(output):
        runpy.run_path(str(source), init_globals={**private, "nmd_epg": entries})
    text = output.getvalue()
    assert all(value not in text for value in private.values())
    return text

title = "Programme with Unicode — Live"
text = check([entry(base64.b64encode(title.encode()).decode()), entry("Next programme", 3600), entry("Earlier programme", -3600)])
assert title in text and "CURRENT SCHEDULE" in text and "UPCOMING" in text and "PAST" in text
assert "11 Oct 13:00 BST" in text or "11 Oct 12:00 UTC" in text
assert "[title withheld for privacy]" in check([entry("https://private.invalid/?token=private-pass")])
assert "[title withheld for privacy]" in check([entry(base64.b64encode(b'private-user').decode())])
assert "\x1b" not in check([entry("Title\x1b[31m")])
assert "could not be displayed safely" in check([entry("Invalid range", duration=-1)])
assert "could not be displayed safely" in check([{"title": "No timestamps"}])
print("6 offline guide-display checks passed; no provider contacted.")
