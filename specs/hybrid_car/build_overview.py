import json, re, sys, html
from collections import OrderedDict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from origin import ORIGIN
d = Path(sys.argv[1]); out_md = Path(sys.argv[2]); out_html_frag = Path(sys.argv[3]); out_html_full = Path(sys.argv[4])
pos = json.load(open(d/"2026-10-11_hybrid_positive_tools_spec.json"))
neg = json.load(open(d/"2026-10-11_hybrid_negative_tools_spec.json"))
inv = json.load(open(d/"2026-10-11_hybrid_state_inventory.json"))
ORDER = [("Vehicle","Body, lights, climate, seats, vehicle status"),("Navigation","Routes, stops, places"),("Energy","Hybrid powertrain, charging, fuel"),("Media","Audio and radio"),("Communication","Calls, texts, email, calendar"),("Utility","Math and time"),("Weather","Conditions at a place today"),("Preferences","Saved driver preferences")]
orig = lambda n: ORIGIN.get(n, ("new", [], ""))[0]
rows=[]
for dom,label in ORDER:
    a=sum(1 for t in pos.values() if t["domain"]==dom and t["kind"]=="action")
    r=sum(1 for t in pos.values() if t["domain"]==dom and t["kind"]=="retrieve")
    cb=sum(1 for n,t in pos.items() if t["domain"]==dom and orig(n)!="new")
    rows.append((dom,label,a,r,cb))
assert sum(x[2]+x[3] for x in rows)==len(pos)
TA=sum(x[2] for x in rows); TR=sum(x[3] for x in rows); TCB=sum(x[4] for x in rows)
NSAME=sum(1 for n in pos if orig(n)=="same"); NEXT=sum(1 for n in pos if orig(n)=="extended"); NNEW=len(pos)-TCB
TAG={"same":"CAR-bench","extended":"CAR-bench, extended","new":"New"}
dash=lambda n: str(n) if n else "–"

def first_sentence(s):
    m=re.match(r"(.+?\.)(\s|$)", s)
    return m.group(1) if m else s

# ---------- markdown
md=["# Hybrid Assistant Tools", "",
    f"**{len(pos)+len(neg)} tools** in total: **{len(pos)} positive** and **{len(neg)} negative**. The spec files are the `2026-10-11_hybrid_*.json` files in this folder.", "",
    f"Of the {len(pos)} positive tools, **{TCB} come from CAR-bench** ({NSAME} with the same capability, {NEXT} extended) and **{NNEW} are new**.", "",
    "## Positive tools by domain", "",
    "| Domain | Action | Retrieve | Total | From CAR-bench | New |","|---|---|---|---|---|---|"]
for dom,label,a,r,cb in rows:
    md.append(f"| {dom} ({label}) | {dash(a)} | {dash(r)} | {a+r} | {dash(cb)} | {dash(a+r-cb)} |")
md.append(f"| **Total** | **{TA}** | **{TR}** | **{len(pos)}** | **{TCB}** | **{NNEW}** |")
md += ["", "CAR-bench has 57 tools. All of them are covered except `think` and `planning_tool`, which are reasoning scaffolds for the agent rather than features for the driver.", "",
       "Origin tags used below:", "",
       "- **CAR-bench**: the same capability as a CAR-bench tool, sometimes renamed or merged from several getters.",
       "- **CAR-bench, extended**: built on a CAR-bench tool, with added parameters, values, or state.",
       "- **New**: not in CAR-bench.", "",
       "## Positive tools", ""]
for dom,label,a,r,cb in rows:
    md.append(f"### {dom} ({a+r})"); md.append("")
    md.append("| Tool | Kind | Origin | CAR-bench source | What it does |"); md.append("|---|---|---|---|---|")
    for n,t in pos.items():
        if t["domain"]==dom:
            o,src,note=ORIGIN.get(n,("new",[],""))
            srcs=", ".join(f"`{x}`" for x in src) or "–"
            what=first_sentence(t["description"]) + (f" {note}" if note else "")
            md.append(f"| `{n}` | {t['kind']} | {TAG[o]} | {srcs} | {what} |")
    md.append("")
md += ["## Negative tools", "",
       f"These {len(neg)} tools cover smart-home, phone, and other requests that do not belong in the car. The model should recognize them and decline or pick the right in-car tool. All of them are new.", "",
       "| Tool | Domain | What it does |","|---|---|---|"]
for n,t in neg.items():
    md.append(f"| `{n}` | {t['domain']} | {first_sentence(t['description'])} |")
out_md.write_text("\n".join(md).rstrip()+"\n")

# ---------- html
def tool_entry(n,t,negative=False):
    st=inv["tools"].get(n,{})
    if negative: state=None
    elif st.get("external"): state="Uses outside data only; reads or writes no vehicle state."
    else:
        key="writes" if "writes" in st else "reads"
        state=("Writes " if key=="writes" else "Reads ")+f"{len(st[key])} vehicle state value"+("s" if len(st[key])!=1 else "")+"."
    params=[]
    for pn,p in t["parameters"].items():
        params.append({"n":pn,"t":p["type"],"req":p["required"],"d":p["description"]})
    o,src,note=("new",[],"") if negative else ORIGIN.get(n,("new",[],""))
    return {"n":n,"dom":t["domain"],"k":t["kind"],"d":t["description"],"p":params,"s":state,"neg":negative,"o":o,"src":src,"note":note}
data={"pos":[tool_entry(n,t) for n,t in pos.items()],"neg":[tool_entry(n,t,True) for n,t in neg.items()]}
maxn=max(x[2]+x[3] for x in rows)
table_rows="".join(
  f'<tr><th scope="row"><a href="#d-{dom.lower()}">{dom}</a><span class="sub">{html.escape(label)}</span></th>'
  f'<td class="num">{dash(a)}</td><td class="num">{dash(r)}</td><td class="num tot">{a+r}</td><td class="num">{dash(cb)}</td><td class="num">{dash(a+r-cb)}</td>'
  f'<td class="barcell"><div class="bar" role="img" aria-label="{a} action, {r} retrieve">'
  f'<span class="ba" style="width:{a/maxn*100:.2f}%"></span><span class="br" style="width:{r/maxn*100:.2f}%"></span></div></td></tr>'
  for dom,label,a,r,cb in rows)
domain_opts="".join(f'<option value="{dom}">{dom}</option>' for dom,*_ in rows)
SCRIPT = r'''<script>
const DATA = __DATA__;
const ORDER = __ORDER__;
const NEG_GROUP = ["__neg", "Requests outside the car that the model should decline"];
const esc = s => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const fmt = s => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");
const first = s => (s.match(/^(.+?\.)(\s|$)/) || [null, s])[1];
let kind = "", origin = "";
const TAG = {same: "CAR-bench", extended: "CAR-bench, extended", "new": "New"};
function item(t) {
  const cls = t.neg ? "k-neg" : "k-" + t.k;
  const label = t.neg ? "negative" : t.k;
  const params = t.p.length ? '<ul class="params">' + t.p.map(p => `<li><span><span class="pn">${esc(p.n)}</span><span class="pt">${p.t}${p.req ? "" : " · optional"}</span></span><span class="pd">${fmt(p.d)}</span></li>`).join("") + "</ul>" : '<p class="state">No parameters</p>';
  const otag = `<span class="otag o-${t.o}">${TAG[t.o]}</span>`;
  const src = t.src.length ? `<p class="state">CAR-bench source: ${t.src.map(x => `<code>${esc(x)}</code>`).join(", ")}.${t.note ? " " + esc(t.note) : ""}</p>` : "";
  return `<details><summary><span class="chip ${cls}">${label}</span><span class="tline"><span class="tname">${t.n}</span>${otag}</span><span class="tdesc">${fmt(first(t.d))}</span></summary><div class="body"><p>${fmt(t.d)}</p>${params}${src}${t.s ? `<p class="state">${t.s}</p>` : ""}</div></details>`;
}
function render() {
  const q = document.getElementById("q").value.trim().toLowerCase();
  const dom = document.getElementById("dom").value;
  const match = t => (!q || (t.n + " " + t.d).toLowerCase().includes(q)) && (!kind || t.k === kind) && (!origin || (origin === "new" ? t.o === "new" : t.o !== "new"));
  let html = "", n = 0;
  for (const [d, l] of [...ORDER, NEG_GROUP]) {
    if (dom && dom !== d) continue;
    const items = (d === "__neg" ? DATA.neg : DATA.pos.filter(t => t.dom === d)).filter(match);
    if (!items.length) continue;
    n += items.length;
    const title = d === "__neg" ? "Negative tools" : d;
    const sub = l;
    html += `<div class="group" id="d-${d === "__neg" ? "negative" : d.toLowerCase()}"><h3>${title} <small>${sub} · ${items.length}</small></h3>${items.map(item).join("")}</div>`;
  }
  document.getElementById("list").innerHTML = html || '<p class="empty">No tools match. Try another word or clear the filters.</p>';
  document.getElementById("count").textContent = `${n} shown`;
}
document.getElementById("q").addEventListener("input", render);
document.getElementById("dom").addEventListener("change", render);
document.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => {
  if ("k" in b.dataset) kind = b.dataset.k; else origin = b.dataset.o;
  b.parentElement.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b));
  render();
}));
document.querySelectorAll('tbody th a').forEach(a => a.addEventListener("click", () => {
  document.getElementById("dom").value = ""; document.getElementById("q").value = ""; kind = ""; origin = "";
  document.querySelectorAll(".seg button").forEach(x => x.setAttribute("aria-pressed", (x.dataset.k ?? x.dataset.o) === "")); render();
}));
render();
</script>
'''
frag=f'''<title>Hybrid Assistant Tools</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: single readable column; summary table first, then filterable tool catalogue grouped by domain. */
:root {{
  --bg:#f6f7f5; --surface:#ffffff; --fg:#1d2321; --muted:#5d6763; --line:#dde2df;
  --action:#2f7d5b; --action-soft:#e2f0e8; --retrieve:#3a6ea5; --retrieve-soft:#e3ecf6; --neg:#a5533a; --neg-soft:#f6e6df; --cb:#7a5a1e;
  --font-body:"IBM Plex Sans",system-ui,sans-serif; --font-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#141917; --surface:#1c2220; --fg:#e4e9e6; --muted:#9aa5a0; --line:#2f3734;
  --action:#6cc59a; --action-soft:#1f3a2d; --retrieve:#7fb0e6; --retrieve-soft:#1e2f42; --neg:#e3957b; --neg-soft:#3d2620; --cb:#d9b46a; color-scheme:dark; }} }}
:root[data-theme="dark"] {{
  --bg:#141917; --surface:#1c2220; --fg:#e4e9e6; --muted:#9aa5a0; --line:#2f3734;
  --action:#6cc59a; --action-soft:#1f3a2d; --retrieve:#7fb0e6; --retrieve-soft:#1e2f42; --neg:#e3957b; --neg-soft:#3d2620; --cb:#d9b46a; color-scheme:dark; }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--font-body); font-size:15px; line-height:1.6; }}
.wrap {{ max-width:960px; margin:0 auto; padding-inline:16px; padding-block:40px 64px; display:grid; gap:40px; }}
h1,h2,h3 {{ text-wrap:balance; line-height:1.25; margin:0; }}
h1 {{ font-size:28px; font-weight:600; }}
h2 {{ font-size:20px; font-weight:600; }}
h3 {{ font-size:16px; font-weight:600; }}
p {{ margin:0; max-width:65ch; }}
code, .mono {{ font-family:var(--font-mono); font-size:.92em; }}
header {{ display:grid; gap:16px; }}
.eyebrow {{ font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); font-weight:500; }}
.totals {{ display:flex; flex-wrap:wrap; gap:8px 28px; font-variant-numeric:tabular-nums; }}
.totals div {{ display:grid; }}
.totals b {{ font-size:32px; font-weight:600; line-height:1.1; }}
.totals span {{ color:var(--muted); font-size:13px; }}
.totals .pos b {{ color:var(--fg); }} .totals .neg b {{ color:var(--neg); }}
section {{ display:grid; gap:14px; min-width:0; }}
.tablebox {{ position:relative; overflow-x:auto; background:var(--surface); border:1px solid var(--line); border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; min-width:680px; font-variant-numeric:tabular-nums; }}
th,td {{ padding:10px 14px; text-align:left; border-bottom:1px solid var(--line); vertical-align:middle; }}
thead th {{ font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); font-weight:500; }}
tbody th {{ font-weight:600; }}
tbody th a {{ color:var(--fg); text-decoration:none; }} tbody th a:hover {{ text-decoration:underline; }}
.sub {{ display:block; font-weight:400; font-size:13px; color:var(--muted); }}
.num {{ text-align:right; width:72px; }}
.tot {{ font-weight:600; }}
tfoot td, tfoot th {{ border-bottom:0; font-weight:600; }}
.barcell {{ width:20%; min-width:90px; }}
.bar {{ display:flex; height:10px; border-radius:5px; background:var(--bg); overflow:hidden; }}
.ba {{ background:var(--action); }} .br {{ background:var(--retrieve); }}
.legend {{ display:flex; gap:18px; flex-wrap:wrap; font-size:13px; color:var(--muted); }}
.legend i {{ display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; vertical-align:-1px; }}
.note {{ color:var(--muted); font-size:14px; }}
.controls {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; position:sticky; top:env(safe-area-inset-top,0px); background:var(--bg); padding-block:10px; z-index:2; }}
.controls input, .controls select {{ font:inherit; color:var(--fg); background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:7px 10px; }}
.controls input {{ flex:1 1 220px; min-width:0; }}
.seg {{ display:inline-flex; border:1px solid var(--line); border-radius:8px; overflow:hidden; background:var(--surface); }}
.seg button {{ font:inherit; font-size:14px; border:0; background:transparent; color:var(--muted); padding:7px 12px; cursor:pointer; }}
.seg button[aria-pressed="true"] {{ background:var(--fg); color:var(--bg); }}
.count {{ color:var(--muted); font-size:13px; font-variant-numeric:tabular-nums; }}
:focus-visible {{ outline:2px solid var(--retrieve); outline-offset:2px; }}
.group {{ display:grid; gap:8px; scroll-margin-top:72px; }}
.group h3 {{ display:flex; gap:10px; align-items:baseline; padding-top:8px; }}
.group h3 small {{ font-weight:400; color:var(--muted); font-size:13px; }}
details {{ background:var(--surface); border:1px solid var(--line); border-radius:8px; }}
summary {{ list-style:none; cursor:pointer; padding:10px 14px; display:grid; grid-template-columns:auto 1fr; gap:4px 12px; align-items:baseline; }}
summary::-webkit-details-marker {{ display:none; }}
.chip {{ font-size:11px; letter-spacing:.05em; text-transform:uppercase; font-weight:500; padding:2px 7px; border-radius:4px; grid-row:span 2; align-self:start; margin-top:3px; min-width:68px; text-align:center; }}
.k-action {{ background:var(--action-soft); color:var(--action); }}
.k-retrieve {{ background:var(--retrieve-soft); color:var(--retrieve); }}
.k-neg {{ background:var(--neg-soft); color:var(--neg); }}
.tline {{ display:flex; flex-wrap:wrap; gap:4px 10px; align-items:baseline; min-width:0; }}
.tname {{ font-family:var(--font-mono); font-weight:500; overflow-wrap:anywhere; }}
.otag {{ font-size:12px; padding:0 8px; border-radius:999px; border:1px solid var(--line); color:var(--muted); white-space:nowrap; }}
.otag.o-same, .otag.o-extended {{ border-color:var(--cb); color:var(--cb); }}
.otag.o-new {{ background:var(--fg); border-color:var(--fg); color:var(--bg); }}
.tdesc {{ color:var(--muted); font-size:14px; min-width:0; }}
.body {{ padding:0 14px 14px; display:grid; gap:10px; border-top:1px solid var(--line); padding-top:12px; }}
.body p {{ font-size:14px; }}
.params {{ display:grid; gap:6px; margin:0; padding:0; list-style:none; }}
.params li {{ font-size:14px; display:grid; grid-template-columns:minmax(0,max-content) 1fr; gap:2px 10px; }}
.params .pn {{ font-family:var(--font-mono); }}
.params .pt {{ color:var(--muted); font-size:12px; margin-left:6px; font-family:var(--font-mono); }}
.params .pd {{ color:var(--muted); min-width:0; }}
.state {{ font-size:13px; color:var(--muted); }}
.empty {{ color:var(--muted); padding:20px 0; }}
@media (max-width:560px) {{ .params li {{ grid-template-columns:1fr; }} .totals b {{ font-size:26px; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior:auto !important; }} }}
</style>
<div class="wrap">
<header>
  <div class="eyebrow">Plug-in hybrid · in-car assistant · tool spec</div>
  <h1>Hybrid Assistant Tools</h1>
  <p>Tool specs for a plug-in hybrid in-car assistant. They keep every CAR-bench capability and add hybrid energy, media, door access, seats, visibility, and read-only vehicle status.</p>
  <div class="totals">
    <div><b>{len(pos)+len(neg)}</b><span>tools in total</span></div>
    <div class="pos"><b>{len(pos)}</b><span>positive ({TA} action · {TR} retrieve)</span></div>
    <div class="neg"><b>{len(neg)}</b><span>negative (to decline)</span></div>
    <div><b>{len(inv["state"])}</b><span>vehicle state values</span></div>
  </div>
</header>
<section aria-labelledby="h-sum">
  <h2 id="h-sum">Positive tools by domain</h2>
  <div class="legend"><span><i style="background:var(--action)"></i>action: changes something</span><span><i style="background:var(--retrieve)"></i>retrieve: only reads</span></div>
  <div class="tablebox"><table>
    <thead><tr><th scope="col">Domain</th><th scope="col" class="num">Action</th><th scope="col" class="num">Retrieve</th><th scope="col" class="num">Total</th><th scope="col" class="num">CAR-bench</th><th scope="col" class="num">New</th><th scope="col"><span class="sr">Share</span></th></tr></thead>
    <tbody>{table_rows}</tbody>
    <tfoot><tr><th scope="row">Total</th><td class="num">{TA}</td><td class="num">{TR}</td><td class="num">{len(pos)}</td><td class="num">{TCB}</td><td class="num">{NNEW}</td><td></td></tr></tfoot>
  </table></div>
  <p class="note">{TCB} of the {len(pos)} positive tools come from CAR-bench ({NSAME} with the same capability, {NEXT} extended) and {NNEW} are new. CAR-bench has 57 tools; all are covered except <code>think</code> and <code>planning_tool</code>, which are reasoning scaffolds for the agent rather than features for the driver.</p>
</section>
<section aria-labelledby="h-list">
  <h2 id="h-list">All tools</h2>
  <div class="controls">
    <input id="q" type="search" placeholder="Search tool names and descriptions" aria-label="Search tools">
    <select id="dom" aria-label="Filter by domain"><option value="">All domains</option>{domain_opts}<option value="__neg">Negative tools</option></select>
    <div class="seg" role="group" aria-label="Filter by kind">
      <button type="button" data-k="" aria-pressed="true">All kinds</button><button type="button" data-k="action" aria-pressed="false">action</button><button type="button" data-k="retrieve" aria-pressed="false">retrieve</button>
    </div>
    <div class="seg" role="group" aria-label="Filter by origin">
      <button type="button" data-o="" aria-pressed="true">Any origin</button><button type="button" data-o="cb" aria-pressed="false">From CAR-bench</button><button type="button" data-o="new" aria-pressed="false">New</button>
    </div>
    <span class="count" id="count"></span>
  </div>
  <div id="list"></div>
</section>
</div>
__SCRIPT__
'''
frag = frag.replace("__SCRIPT__", SCRIPT.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__ORDER__", json.dumps([[r[0], r[1]] for r in rows], ensure_ascii=False)))
frag = frag.replace('<span class="sr">Share</span>', '<span style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Share</span>')
out_html_frag.write_text(frag)
out_html_full.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + frag.replace("</style>","</style>\n</head>\n<body>",1) + "</body>\n</html>\n")
print(TA,TR,len(pos),len(neg))
