nmd_logo_bytes = b""
try:
    nmd_logo_url = nmd_matches[0].get("stream_icon", "")
    nmd_logo_parts = parse.urlsplit(nmd_logo_url)
    if (nmd_logo_parts.scheme not in ("http", "https") or not nmd_logo_parts.hostname
            or nmd_logo_parts.username or nmd_logo_parts.password
            or nmd_logo_parts.path.lower().endswith((".ts", ".m3u", ".m3u8", ".mp4", ".mkv"))):
        raise ValueError()
    nmd_logo_request = request.Request(nmd_logo_url, headers={
        "Accept": "image/*", "User-Agent": "NMD-Media-Card-Metadata-Test/0.1"})
    with request.build_opener(NoRedirect()).open(nmd_logo_request, timeout=25) as nmd_logo_response:
        nmd_logo_type = nmd_logo_response.headers.get_content_type()
        if nmd_logo_type not in ("image/png", "image/jpeg", "image/webp", "image/gif", "image/svg+xml"):
            print("The logo link did not return a supported image.")
        else:
            nmd_logo_data = nmd_logo_response.read(2097153)
            if not nmd_logo_data or len(nmd_logo_data) > 2097152:
                print("The logo was empty or exceeded the test size limit.")
            else:
                nmd_logo_bytes = nmd_logo_data
                print("Logo response type:", nmd_logo_type)
                print("Logo bytes received:", len(nmd_logo_bytes))
except errors.HTTPError as nmd_error:
    print("Logo server returned HTTP", nmd_error.code)
except (errors.URLError, TimeoutError):
    print("Could not reach the logo server within this check.")
except Exception:
    print("Logo check failed; no private links or login details have been printed.")
