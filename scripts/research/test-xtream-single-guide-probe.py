import contextlib
import io
import json
import pathlib
import runpy
import urllib.request as request
import urllib.parse as parse
import urllib.error as errors
from unittest.mock import patch

source = pathlib.Path(__file__).with_name("xtream-single-guide-probe.py")
class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None
class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

def check(expected, body=b"{}", error=None, stream_id="123"):
    output, calls = io.StringIO(), []
    class Opener:
        def open(self, req, timeout):
            calls.append(req.full_url)
            parsed = parse.urlsplit(req.full_url)
            assert parsed.path == "/player_api.php"
            assert parse.parse_qs(parsed.query) == {"username": ["private&user"], "password": ["private#pass"],
                "action": ["get_short_epg"], "stream_id": ["123"], "limit": ["4"]}
            assert timeout == 25
            if error: raise error
            return Response(body)
    def build(*handlers):
        assert len(handlers) == 1 and handlers[0].redirect_request(None) is None
        return Opener()
    context = {"request": request, "parse": parse, "errors": errors, "json": json, "NoRedirect": NoRedirect,
               "server": "https://example.invalid", "username": "private&user", "password": "private#pass",
               "nmd_matches": [{"stream_id": stream_id}]}
    with patch.object(request, "build_opener", build), contextlib.redirect_stdout(output):
        result = runpy.run_path(str(source), init_globals=context)
    assert expected in output.getvalue(), output.getvalue()
    assert "private" not in output.getvalue() and "example.invalid" not in output.getvalue()
    return result, calls

fixture = {"epg_listings": [{"title": "VGVzdA==", "description": "RGVzYw==", "start_timestamp": 1, "stop_timestamp": 2}]}
result, calls = check("Entries with timestamp pairs: 1", json.dumps(fixture).encode())
assert len(calls) == 1 and result["nmd_epg"] == fixture["epg_listings"]
check("Guide entries: 0", b'{"epg_listings":[]}')
check("did not return a programme-guide list", b'{"epg_listings":"private"}')
check("Guide check failed", b'invalid JSON')
check("Provider returned HTTP 302", error=errors.HTTPError("private", 302, "private", {}, None))
check("Could not reach", error=errors.URLError("private"))
check("exceeded the test size limit", b'x' * 1048577)
result, calls = check("Guide check failed", stream_id="")
assert not calls and not result["nmd_epg"]
print("8 offline guide-request checks passed; no provider contacted.")
