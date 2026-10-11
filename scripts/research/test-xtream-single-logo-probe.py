import contextlib
import email.message
import io
import pathlib
import runpy
import urllib.request as request
import urllib.parse as parse
import urllib.error as errors
from unittest.mock import patch

source = pathlib.Path(__file__).with_name("xtream-single-logo-probe.py")
class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None
class Response(io.BytesIO):
    def __init__(self, body, mime):
        super().__init__(body)
        self.headers = email.message.Message()
        self.headers["Content-Type"] = mime
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()

def check(expected, body=b"image bytes", mime="image/png", url="https://example.invalid/logo.png?token=private", error=None):
    output, calls = io.StringIO(), []
    class Opener:
        def open(self, req, timeout):
            assert req.full_url == url
            assert timeout == 25
            assert "password=" not in req.full_url
            calls.append(req.full_url)
            if error:
                raise error
            return Response(body, mime)
    def build(*handlers):
        assert len(handlers) == 1
        assert handlers[0].redirect_request(None) is None
        return Opener()
    context = {"request": request, "parse": parse, "errors": errors,
               "NoRedirect": NoRedirect, "nmd_matches": [{"stream_icon": url}]}
    with patch.object(request, "build_opener", build), contextlib.redirect_stdout(output):
        result = runpy.run_path(str(source), init_globals=context)
    assert expected in output.getvalue(), output.getvalue()
    assert "private" not in output.getvalue().replace("no private links", "")
    assert "example.invalid" not in output.getvalue()
    return result, calls

result, calls = check("Logo bytes received: 11")
assert result["nmd_logo_bytes"] == b"image bytes" and len(calls) == 1
result, _ = check("did not return a supported image", mime="text/html")
assert not result["nmd_logo_bytes"]
check("empty or exceeded", body=b"")
check("empty or exceeded", body=b"x" * 2097153)
check("Logo server returned HTTP 302", error=errors.HTTPError("private", 302, "private", {}, None))
check("Could not reach", error=errors.URLError("private"))
result, calls = check("Logo check failed", url="https://example.invalid/live/test.ts")
assert not calls and not result["nmd_logo_bytes"]
result, calls = check("Logo check failed", url="https://user:private@example.invalid/logo.png")
assert not calls
print("8 offline image-request checks passed; no server contacted. Image decoding is untested.")
