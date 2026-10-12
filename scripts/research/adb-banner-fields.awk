# Research-only, narrow parser for the TiviMate 5.3.3 uiautomator hierarchy.
# This intentionally accepts only hierarchy/node tags and double-quoted attrs.
BEGIN {
    protocol = "NMD_ADB_FIELDS_V1"
    if (app_version != "5.3.3") { emit("unsupported_version", ""); exit }
    xml = ""
    bytes = 0
    while ((getline line) > 0) {
        bytes += length(line) + 1
        if (bytes > 262144) { emit("incomplete", ""); exit }
        xml = xml line "\n"
    }
    if (xml == "") { emit("incomplete", ""); exit }
    parse_xml(xml)
}

function emit(status, fields,    body) {
    body = ""
    if (status == "banner") body = fields
    printf "{\"protocol\":\"%s\",\"sample\":\"%s\",\"status\":\"%s\",\"elapsed_ms\":%s,\"fields\":{%s}}\n", protocol, sample, status, elapsed_ms, body
}

function fail(status) { if (!done) { done = 1; emit(status, "") } }

function json(s,    i,c,n,out) {
    out = ""
    for (i = 1; i <= length(s); i++) {
        c = substr(s, i, 1)
        if (c == "\\") out = out "\\\\"
        else if (c == "\"") out = out "\\\""
        else if (c == "\n") out = out "\\n"
        else if (c == "\r") out = out "\\r"
        else if (c == "\t") out = out "\\t"
        else {
            for (n = 1; n < 32; n++) if (c == sprintf("%c", n)) { c = "\\u" sprintf("%04x", n); break }
            out = out c
        }
    }
    return out
}

function decode_entities(s,    out,i,c,tail,code,hex,n,ref,j) {
    out = ""
    for (i = 1; i <= length(s); i++) {
        c = substr(s, i, 1)
        if (c != "&") { out = out c; continue }
        tail = substr(s, i)
        if (tail ~ /^&amp;/) { out = out "&"; i += 4 }
        else if (tail ~ /^&quot;/) { out = out "\""; i += 5 }
        else if (tail ~ /^&apos;/) { out = out "'"; i += 5 }
        else if (tail ~ /^&lt;/) { out = out "<"; i += 3 }
        else if (tail ~ /^&gt;/) { out = out ">"; i += 3 }
        else if (match(tail, /^&#(x[0-9A-Fa-f]+|[0-9]+);/)) {
            ref = substr(tail, 1, RLENGTH)
            code = substr(ref, 3, length(ref) - 3)
            n = -1
            if (substr(ref, 3, 1) == "x") {
                hex = substr(ref, 4, length(ref) - 4)
                if (hex ~ /^(9|09|0A|0a|A|a|0D|0d|D|d)$/) {
                    if (hex ~ /^(9|09)$/) n = 9
                    else if (hex ~ /^(0A|0a|A|a)$/) n = 10
                    else n = 13
                }
            } else if (code ~ /^[0-9]+$/ && (code + 0 == 9 || code + 0 == 10 || code + 0 == 13)) n = code + 0
            if (n == 9) out = out "\t"
            else if (n == 10) out = out "\n"
            else if (n == 13) out = out "\r"
            else { fail("unsafe_text"); return "" }
            i += length(ref) - 1
        } else { fail("unsafe_text"); return "" }
    }
    return out
}

function unsafe(s,    t) {
    t = tolower(s)
    if (t ~ /https?:\/\// || t ~ /password/ || t ~ /username/ || t ~ /token=/) return 1
    if (s ~ /[[:cntrl:]]/) {
        gsub(/[\t\n\r]/, "", s)
        if (s ~ /[[:cntrl:]]/) return 1
    }
    return 0
}

function attr_value(attrs, key,    pattern,rest,value) {
    pattern = "(^|[[:space:]])" key "=\"[^\"]*\""
    if (!match(attrs, pattern)) return ""
    rest = substr(attrs, RSTART, RLENGTH)
    sub("^[[:space:]]*" key "=\"", "", rest)
    sub("\"$", "", rest)
    return rest
}

function parse_attrs(attrs,    rest,key,value,eq,q,pos) {
    for (key in a) delete a[key]
    rest = attrs
    while (rest != "") {
        sub(/^[[:space:]]+/, "", rest)
        if (rest == "") break
        if (rest !~ /^[A-Za-z_:][A-Za-z0-9_.:-]*="/) return 0
        key = rest
        sub(/=.*/, "", key)
        sub(/^[A-Za-z_:][A-Za-z0-9_.:-]*="/, "", rest)
        if (!match(rest, /"/)) return 0
        value = substr(rest, 1, RSTART - 1)
        rest = substr(rest, RSTART + 1)
        if (key in a) return 0
        if (value ~ /[<>]/) return 0
        a[key] = decode_entities(value)
        if (done) return 0
    }
    return 1
}

function note_node(attrs, depth,    pkg,rid,cls,field,idx,k,v) {
    if (!parse_attrs(attrs)) { fail("invalid_layout"); return }
    pkg = a["package"]
    rid = a["resource-id"]
    cls = a["class"]
    if (pkg == "ar.tvplayer.tv" && (rid == "ar.tvplayer.tv:id/4ig" || rid == "ar.tvplayer.tv:id/4h3" || rid == "ar.tvplayer.tv:id/2im" || rid == "ar.tvplayer.tv:id/1oe")) guide = 1
    if (rid == "ar.tvplayer.tv:id/49p" && pkg == "ar.tvplayer.tv") {
        if (cls != "android.view.ViewGroup" || banner_count) { fail("invalid_layout"); return }
        banner_count = 1
        banner_depth = depth
    }
    if (banner_depth && depth > banner_depth && pkg != "ar.tvplayer.tv") { fail("invalid_layout"); return }
    if (banner_depth && depth > banner_depth && pkg == "ar.tvplayer.tv") {
        field = ""
        if (rid == "ar.tvplayer.tv:id/b7") field = "channel"
        else if (rid == "ar.tvplayer.tv:id/152") field = "title"
        else if (rid == "ar.tvplayer.tv:id/315") field = "schedule"
        else if (rid == "ar.tvplayer.tv:id/3lj") field = "remaining"
        else if (rid == "ar.tvplayer.tv:id/m2") field = "description"
        else if (rid == "ar.tvplayer.tv:id/9v") field = "next_schedule"
        else if (rid == "ar.tvplayer.tv:id/37v") field = "next_title"
        if (field != "") {
            if (field in seen) { fail("invalid_layout"); return }
            if (cls != "android.widget.TextView" || !("text" in a)) { fail("invalid_layout"); return }
            seen[field] = 1
            value = a["text"]
            if (length(value) > 512) { fail("unsafe_text"); return }
            if (unsafe(value)) { fail("unsafe_text"); return }
            values[field] = value
        }
    }
}

function parse_xml(src,    i,n,tag,body,closing,selfclose,name,attrs,depth,decl,stack) {
    i = 1; n = length(src); depth = 0
    while (i <= n && !done) {
        if (substr(src, i, 1) != "<") {
            j = index(substr(src, i), "<")
            if (!j) j = n - i + 2
            body = substr(src, i, j - 1)
            if (body ~ /[^[:space:]]/) { fail("invalid_layout"); return }
            i += j - 1
            continue
        }
        if (substr(src, i, 2) == "<?") {
            if (substr(src, i, 5) != "<?xml" || hierarchy_seen || declaration_seen) { fail("invalid_layout"); return }
            j = index(substr(src, i), "?>")
            if (!j) { fail("incomplete"); return }
            decl = substr(src, i, j + 1)
            if (decl !~ /^<\?xml version='1\.0' encoding='UTF-8' standalone='yes' \?>$/) { fail("invalid_layout"); return }
            declaration_seen = 1
            i += j + 1; continue
        }
        if (substr(src, i, 4) == "<!--" || substr(src, i, 2) == "<!") { fail("invalid_layout"); return }
        j = index(substr(src, i), ">")
        if (!j) { fail("incomplete"); return }
        tag = substr(src, i + 1, j - 2)
        i += j
        if (tag ~ /^\//) {
            name = substr(tag, 2)
            if (name !~ /^(hierarchy|node)$/ || depth < 1 || stack[depth] != name) { fail("invalid_layout"); return }
            if (name == "hierarchy") hierarchy_closed = 1
            if (name == "node" && depth == banner_depth) banner_depth = 0
            delete stack[depth--]
            continue
        }
        selfclose = (tag ~ /\/$/)
        if (selfclose) sub(/\/$/, "", tag)
        if (tag !~ /^(hierarchy|node)([[:space:]]|$)/) { fail("invalid_layout"); return }
        name = tag; sub(/[[:space:]].*$/, "", name)
        attrs = substr(tag, length(name) + 1)
        if (name == "hierarchy") {
            if (hierarchy_seen || depth != 0 || !parse_attrs(attrs)) { fail("invalid_layout"); return }
            hierarchy_seen = 1
        } else {
            if (!hierarchy_seen || hierarchy_closed || depth < 1) { fail("invalid_layout"); return }
            note_node(attrs, depth + 1)
            if (selfclose && banner_depth == depth + 1) { fail("invalid_layout"); return }
        }
        if (!selfclose) stack[++depth] = name
    }
    if (done) return
    if (depth != 0 || !hierarchy_seen || !hierarchy_closed) { emit("incomplete", ""); return }
    if (guide) { emit("guide", ""); return }
    if (banner_count != 1) { emit("no_banner", ""); return }
    fields = ""
    split("channel title schedule remaining description next_schedule next_title", required, " ")
    for (i = 1; i <= 7; i++) if (!(required[i] in seen)) { emit("invalid_layout", ""); return }
    if (values["channel"] == "") { emit("invalid_layout", ""); return }
    for (i = 1; i <= 7; i++) {
        k = required[i]
        if (fields != "") fields = fields ","
        fields = fields "\"" k "\":\"" json(values[k]) "\""
    }
    emit("banner", fields)
}
