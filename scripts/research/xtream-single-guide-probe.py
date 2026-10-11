nmd_epg = []
try:
    nmd_stream_id = str(nmd_matches[0].get("stream_id", ""))
    if not nmd_stream_id.isascii() or not nmd_stream_id.isdigit():
        raise ValueError()
    nmd_epg_query = parse.urlencode({"username": username, "password": password,
                                   "action": "get_short_epg", "stream_id": nmd_stream_id, "limit": 4})
    nmd_epg_request = request.Request(server.rstrip("/") + "/player_api.php?" + nmd_epg_query,
                                     headers={"Accept": "application/json",
                                              "User-Agent": "NMD-Media-Card-Metadata-Test/0.1"})
    with request.build_opener(NoRedirect()).open(nmd_epg_request, timeout=25) as nmd_response:
        nmd_epg_raw = nmd_response.read(1048577)
    if len(nmd_epg_raw) > 1048576:
        print("Guide response exceeded the test size limit.")
    else:
        nmd_epg_data = json.loads(nmd_epg_raw)
        nmd_listings = nmd_epg_data.get("epg_listings") if isinstance(nmd_epg_data, dict) else None
        if not isinstance(nmd_listings, list) or not all(isinstance(e, dict) for e in nmd_listings):
            print("Provider did not return a programme-guide list.")
        else:
            nmd_epg = nmd_listings
            print("Guide entries:", len(nmd_epg))
            print("Entries with titles:", sum(bool(e.get("title")) for e in nmd_epg))
            print("Entries with descriptions:", sum(bool(e.get("description")) for e in nmd_epg))
            print("Entries with timestamp pairs:", sum(bool(e.get("start_timestamp")) and bool(e.get("stop_timestamp")) for e in nmd_epg))
except errors.HTTPError as nmd_error:
    print("Provider returned HTTP", nmd_error.code)
except (errors.URLError, TimeoutError):
    print("Could not reach the provider within this guide check.")
except Exception:
    print("Guide check failed; no login details have been printed.")
