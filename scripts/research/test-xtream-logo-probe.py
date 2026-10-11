import contextlib
import io
import json
import pathlib
import runpy
import urllib.error
import urllib.parse
import urllib.request
from unittest.mock import patch

source = pathlib.Path(__file__).with_name("xtream-logo-probe.py")
login = {"server": "https://example.invalid", "username": "private&user", "password": "private#pass?"}

class Response(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()

class Opener:
    def __init__(self, body=None, error=None):
        self.body = body
        self.error = error
        self.calls = []
    def open(self, req, timeout):
        self.calls.append((req.full_url, timeout))
        assert timeout == 25
        url = urllib.parse.urlsplit(req.full_url)
        assert url.path == "/player_api.php"
        assert urllib.parse.parse_qs(url.query) == {
            "username": [login["username"]], "password": [login["password"]],
            "action": ["get_live_streams"]}
        if self.error:
            raise self.error
        return Response(self.body)

def check(body, expected, error=None, initial=None):
    output = io.StringIO()
    opener = Opener(body, error)
    def build(*handlers):
        assert len(handlers) == 1
        assert handlers[0].redirect_request(None, None, None, None, None) is None
        return opener
    with patch.object(urllib.request, "build_opener", build), contextlib.redirect_stdout(output):
        result = runpy.run_path(str(source), init_globals=initial or login)
    assert expected in output.getvalue(), output.getvalue()
    for secret in login.values():
        assert secret not in output.getvalue()
    return result, opener

fixture = [{"name": "One", "stream_icon": "https://example.invalid/a.png", "epg_channel_id": "one"},
           {"name": "Two", "stream_icon": "http://example.invalid/b.png", "epg_channel_id": "two"},
           {"name": "Three", "stream_icon": "", "epg_channel_id": ""}]
result, opener = check(json.dumps(fixture).encode(), "Channels with logo links: 2")
assert result["channels"] == fixture and len(opener.calls) == 1
check(b'{"user_info":{"auth":0}}', "Provider did not return a channel list")
check(b'not JSON', "Check failed;")
check(b'', "Provider returned HTTP 302", urllib.error.HTTPError("https://private.invalid/?password=private#pass?", 302, "private", {}, None))
check(b'', "Could not reach the provider", urllib.error.URLError("private#pass?"))
check(b'x' * 33554433, "exceeded the test size limit")
result, opener = check(b'', "Check failed;", initial={**login, "server": "https://example.invalid/?password=private"})
assert not opener.calls and not result["channels"]
print("7 offline probe checks passed; no provider contacted.")
