import base64
import datetime
import time
import re
from zoneinfo import ZoneInfo

try:
    nmd_tz = ZoneInfo("Europe/London")
except Exception:
    nmd_tz = datetime.timezone.utc

nmd_now = time.time()
for nmd_entry in nmd_epg:
    try:
        nmd_start = int(nmd_entry["start_timestamp"])
        nmd_stop = int(nmd_entry["stop_timestamp"])
        if nmd_stop <= nmd_start:
            raise ValueError()
        nmd_title = str(nmd_entry.get("title", ""))
        try:
            nmd_title = base64.b64decode(nmd_title.strip(), validate=True).decode("utf-8")
        except (ValueError, UnicodeError):
            pass
        if (re.search(r"https?://|(?:password|username|token)\s*[=:]", nmd_title, re.I)
                or any(value and value in nmd_title for value in (server, username, password))):
            nmd_title = "[title withheld for privacy]"
        nmd_title = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", nmd_title)[:180]
        nmd_status = "CURRENT SCHEDULE" if nmd_start <= nmd_now < nmd_stop else "UPCOMING" if nmd_now < nmd_start else "PAST"
        nmd_from = datetime.datetime.fromtimestamp(nmd_start, nmd_tz).strftime("%d %b %H:%M %Z")
        nmd_to = datetime.datetime.fromtimestamp(nmd_stop, nmd_tz).strftime("%d %b %H:%M %Z")
        print(nmd_status, "|", nmd_from, "to", nmd_to, "|", nmd_title)
    except Exception:
        print("One guide entry could not be displayed safely.")
