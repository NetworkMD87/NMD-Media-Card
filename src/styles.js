export const styles = `
:host { display:block; min-width:0; container-type:inline-size; font-family:var(--primary-font-family,Roboto,Arial,sans-serif); }
* { box-sizing:border-box; }
[hidden] { display:none !important; }
ha-card { display:block; overflow:hidden; border-radius:var(--ha-card-border-radius,14px); border:1px solid var(--ha-card-border-color,var(--divider-color,#3b424a)); background:var(--ha-card-background,var(--card-background-color,#20262d)); color:var(--primary-text-color,#f4f6f8); box-shadow:var(--ha-card-box-shadow,none); }
button { font:inherit; cursor:pointer; touch-action:manipulation; }
button:focus-visible { outline:3px solid var(--primary-color,#80cbed); outline-offset:-3px; }
button:disabled, button[aria-disabled="true"] { cursor:wait; opacity:.6; }
.idle { padding:16px; background:radial-gradient(ellipse at 100% 0%,rgba(100,170,190,.16),transparent 72%); }
.idle-top { display:flex; align-items:center; gap:12px; }
.tv { width:36px; height:36px; display:grid; place-items:center; color:var(--secondary-text-color,#b9c9d8); flex:none; }
.tv svg { width:27px; height:27px; }
.brand { font-size:10px; line-height:15px; letter-spacing:.15em; color:var(--secondary-text-color,#bdcbd6); }
h2 { font-size:17px; font-weight:500; line-height:24px; margin:0; overflow-wrap:anywhere; }
.statuses { display:flex; flex-wrap:wrap; gap:6px 20px; margin-top:13px; font-size:12px; line-height:18px; }
.status-name { color:var(--secondary-text-color,#bdcbd6); margin-right:5px; }
.feature { position:relative; isolation:isolate; padding:14px 16px 10px; color:#f4f6f8; background:radial-gradient(ellipse at 100% 15%,#31596d,transparent 80%),#202d3c; }
.backdrop { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:-2; }
.feature::after { content:''; position:absolute; inset:0; z-index:-1; background:linear-gradient(90deg,rgba(12,20,29,.88),rgba(12,20,29,.58) 52%,rgba(12,20,29,.06)),linear-gradient(0deg,rgba(12,20,29,.78),transparent 55%); }
.topline { display:flex; align-items:center; gap:7px; min-height:24px; font-size:12px; line-height:18px; color:#d1dfe8; }
.room { color:#f4f6f8; font-weight:500; min-width:0; overflow-wrap:anywhere; }
.state { flex:none; }
.app { display:grid; place-items:center; flex:none; margin-left:auto; min-width:24px; max-width:34%; min-height:24px; font-size:10px; letter-spacing:.04em; overflow-wrap:anywhere; text-align:right; }
.app img { width:24px; height:24px; object-fit:contain; }
.app-tivimate img { border-radius:4px; }
.content { display:flex; align-items:center; gap:12px; min-height:61px; margin-top:10px; }
.title-group { flex:1; min-width:0; }
.title { font-family:'NMD Satoshi',var(--primary-font-family,Roboto,Arial,sans-serif); font-size:24px; font-weight:700; line-height:29px; letter-spacing:-.02em; text-shadow:0 2px 6px rgba(0,0,0,.5); margin:0; overflow-wrap:anywhere; }
.detail { color:#d1dfe8; font-size:12px; line-height:17px; margin-top:4px; overflow-wrap:anywhere; }
.control { display:grid; place-items:center; width:48px; height:48px; flex:none; border:1px solid rgba(255,255,255,.32); border-radius:50%; color:#fff; background:rgba(16,24,32,.48); box-shadow:0 2px 8px rgba(0,0,0,.15); backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px); transition:background-color 140ms ease,transform 140ms ease,border-color 140ms ease; }
@media (hover:hover) { .control:not([aria-disabled="true"]):not(:disabled):hover { background:rgba(40,54,66,.68); border-color:rgba(255,255,255,.55); } }
.control:not([aria-disabled="true"]):not(:disabled):active { transform:scale(.95); }
.control:focus-visible { outline:3px solid #fff; outline-offset:3px; box-shadow:0 0 0 7px #0c141d; }
.control svg { display:block; width:22px; height:22px; }
@media (prefers-reduced-motion:reduce) { .control { transition:none; } .control:not([aria-disabled="true"]):not(:disabled):active { transform:none; } }
.timing { display:flex; align-items:center; gap:10px; min-height:15px; margin-top:9px; color:#d1dfe8; font-size:11px; line-height:15px; font-variant-numeric:tabular-nums; }
.track { flex:1; height:3px; overflow:hidden; background:rgba(220,237,247,.25); border-radius:3px; }
.fill { height:100%; background:#b7dae2; }
.limited { min-height:15px; margin-top:9px; font-size:11px; line-height:15px; color:#d1dfe8; }
.others { color:#f4f6f8; background:#181e26; }
.other { display:flex; width:100%; align-items:center; gap:10px; min-height:57px; padding:9px 16px; color:inherit; background:transparent; border:0; border-top:1px solid #3b4652; text-align:left; }
.other:hover { background:#242e3a; }
.thumb { width:28px; height:38px; flex:none; object-fit:cover; border-radius:4px; background:#2d4554; }
.other-text { flex:1; min-width:0; }
.other-meta { font-size:11px; line-height:17px; color:#c9d3dd; overflow-wrap:anywhere; }
.other-title { font-size:12px; line-height:18px; overflow-wrap:anywhere; }
.chevron { flex:none; width:16px; height:16px; }
.rest { display:flex; flex-wrap:wrap; gap:6px 18px; padding:9px 16px; font-size:12px; line-height:18px; color:#c9d3dd; border-top:1px solid #3b4652; }
.error { margin:0; padding:10px 16px; font-size:12px; line-height:18px; color:var(--error-color,#dc6666); overflow-wrap:anywhere; }
.sr-only { position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap; }
@container (max-width:350px) { .feature { padding-inline:12px; } .topline { gap:5px; } .content { gap:9px; } .app { max-width:28%; } }
`;
