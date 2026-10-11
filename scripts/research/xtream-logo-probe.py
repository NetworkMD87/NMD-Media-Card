import json
import urllib.request as request
import urllib.parse as parse
import urllib.error as errors

class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

channels = []
try:
    nmd_base = parse.urlsplit(server)
    if (nmd_base.scheme not in ("http", "https") or not nmd_base.hostname
            or nmd_base.username or nmd_base.password or nmd_base.query
            or nmd_base.fragment or not username or not password):
        raise ValueError()
    nmd_query = parse.urlencode({"username": username, "password": password,
                                 "action": "get_live_streams"})
    nmd_endpoint = server.rstrip("/") + "/player_api.php?" + nmd_query
    nmd_request = request.Request(nmd_endpoint, headers={
        "Accept": "application/json", "User-Agent": "NMD-Media-Card-Metadata-Test/0.1"})
    with request.build_opener(NoRedirect()).open(nmd_request, timeout=25) as nmd_response:
        nmd_raw = nmd_response.read(33554433)
    if len(nmd_raw) > 33554432:
        print("Channel list exceeded the test size limit.")
    else:
        nmd_data = json.loads(nmd_raw)
        if not isinstance(nmd_data, list) or not all(isinstance(c, dict) for c in nmd_data):
            print("Provider did not return a channel list; check the login details.")
        else:
            channels = nmd_data
            nmd_logos = sum(isinstance(c.get("stream_icon"), str)
                            and c["stream_icon"].strip().lower().startswith(("https://", "http://"))
                            for c in channels)
            nmd_epg = sum(bool(c.get("epg_channel_id")) for c in channels)
            print("Channels:", len(channels))
            print("Channels with logo links:", nmd_logos)
            print("Channels with guide IDs:", nmd_epg)
except errors.HTTPError as nmd_error:
    print("Provider returned HTTP", nmd_error.code)
except (errors.URLError, TimeoutError):
    print("Could not reach the provider within this check.")
except Exception:
    print("Check failed; no login details have been printed. We will inspect the input format next.")
