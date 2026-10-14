import json, re, sys, html
from collections import OrderedDict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from origin import ORIGIN
d = Path(sys.argv[1]); out_md = Path(sys.argv[2]); out_html_frag = Path(sys.argv[3]); out_html_full = Path(sys.argv[4])
PFX = "2026-10-14_hybrid_vss"
pos = json.load(open(d/f"{PFX}_positive_tools_spec.json"))
neg = json.load(open(d/f"{PFX}_negative_tools_spec.json"))
inv = json.load(open(d/f"{PFX}_state_inventory.json"))
vmap = json.load(open(d/f"{PFX}_signal_mapping.json"))
VSSM = vmap["signals"]
NSTD = sum(m["standard"] for m in VSSM.values()); NEXTN = len(VSSM) - NSTD
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

# ---------- vehicle state
STATE=inv["state"]
WRITERS={p:[] for p in STATE}; READERS={p:[] for p in STATE}
for tn,ts in inv["tools"].items():
    for p in ts.get("writes",[]): WRITERS[p].append(tn)
    for p in ts.get("reads",[]): READERS[p].append(tn)
GROUPS=[("Doors and windows","Door locks, child locks, window positions",["Vehicle.Cabin.Door.","Vehicle.Cabin.IsWindowChildLockEngaged"]),
        ("Sunroof and shades","Sunroof, sunroof shade, rear window shade",["Vehicle.Cabin.Sunroof.","Vehicle.Cabin.RearShade."]),
        ("Interior lights","Reading lights and ambient light zones",["Vehicle.Cabin.Light."]),
        ("Climate","HVAC zones, air conditioning, defrosters, measured temperatures",["Vehicle.Cabin.HVAC.","Vehicle.Exterior."]),
        ("Seats and steering wheel","Occupancy, heating and cooling, massage, position",["Vehicle.Cabin.Seat.","Vehicle.Chassis.SteeringWheel."]),
        ("Media","Source, playback, volume, radio",["Vehicle.Cabin.Infotainment.Media."]),
        ("Navigation","Guidance, destination, stops, route options, voice",["Vehicle.Cabin.Infotainment.Navigation."]),
        ("Exterior lights","Headlights, fog lights, hazard lights",["Vehicle.Body.Lights."]),
        ("Wipers and mirrors","Wiper modes, exterior mirrors",["Vehicle.Body.Windshield.Front.Wiping.","Vehicle.Body.Windshield.Rear.Wiping.","Vehicle.Body.Mirrors."]),
        ("Trunk","Trunk lid and lock",["Vehicle.Body.Trunk."]),
        ("Driving, tires, and service","Speed, gear, odometer, trip, tire pressure, service, fluids, 12 V battery",
         ["Vehicle.Speed","Vehicle.Powertrain.Transmission.SelectedGear","Vehicle.TraveledDistance","Vehicle.Trip","Vehicle.AverageSpeed","Vehicle.Chassis.Axle.","Vehicle.Service.","Vehicle.LowVoltageBattery.","Vehicle.Body.Windshield.Front.WasherFluid.","Vehicle.Powertrain.CombustionEngine.EngineOil."]),
        ("Charging","Charge port, cable, charge limit, timer, charging power",["Vehicle.Powertrain.TractionBattery.Charging."]),
        ("Battery, fuel, and hybrid","Levels, capacities, consumption, hybrid and drive modes",["Vehicle.Powertrain."]),
        ("Vehicle identity","Fixed facts about the car",["Vehicle.VehicleIdentification."])]
def group_of(p):
    return next(i for i,(_,_,pre) in enumerate(GROUPS) if any(p.startswith(x) for x in pre))
for p in STATE: group_of(p)
def clean_desc(t): return re.sub(r" VSS [^.]*\.$", "", t)
def values_text(v):
    if "enum" in v: return ", ".join(json.dumps(x) if isinstance(x,str) else str(x) for x in v["enum"])
    if v["type"]=="bool": return "true, false"
    if "minimum" in v:
        st=f", step {v['step']}" if "step" in v else ""
        return f"{v['minimum']} to {v['maximum']}{st}"
    return "location or route ID, empty when unset"
def start_text(v):
    if v["initial"]=="fixed": return "fixed: "+json.dumps(v["default"])
    if v["initial"]=="from_weather": return "from weather"
    return "random"
state_data=[{"p":p,"g":group_of(p),"t":v["type"],"v":values_text(v),"s":start_text(v),"d":clean_desc(v["description"]),"w":WRITERS[p],"r":READERS[p],
             "std":VSSM[p]["standard"],"vk":VSSM[p]["type"],"vd":VSSM[p]["datatype"],"vu":VSSM[p].get("unit","")} for p,v in STATE.items()]
state_data.sort(key=lambda x: x["g"])
STYPE={p:v["type"] for p,v in STATE.items()}

# ---------- markdown
md=["# Tools VSS", "",
    f"**{len(pos)+len(neg)} tools** in total: **{len(pos)} positive** and **{len(neg)} negative**, over **{len(STATE)} vehicle state values** named after [COVESA VSS](https://github.com/COVESA/vehicle_signal_specification) signals ({NSTD} standard, {NEXTN} extensions). The spec files are the `{PFX}_*` files in this folder.", "",
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
    md.append("| Tool | Parameters | Kind | Origin | CAR-bench source | What it does |"); md.append("|---|---|---|---|---|---|")
    for n,t in pos.items():
        if t["domain"]==dom:
            o,src,note=ORIGIN.get(n,("new",[],""))
            srcs=", ".join(f"`{x}`" for x in src) or "–"
            what=first_sentence(t["description"]) + (f" {note}" if note else "")
            sig=", ".join(f"`{pn}{'' if pp['required'] else '?'}: {pp['type']}`" for pn,pp in t["parameters"].items()) or "–"
            md.append(f"| `{n}` | {sig} | {t['kind']} | {TAG[o]} | {srcs} | {what} |")
    md.append("")
md += ["## Negative tools", "",
       f"These {len(neg)} tools cover smart-home, phone, and other requests that do not belong in the car. The model should recognize them and decline or pick the right in-car tool. All of them are new.", "",
       "| Tool | Domain | What it does |","|---|---|---|"]
for n,t in neg.items():
    md.append(f"| `{n}` | {t['domain']} | {first_sentence(t['description'])} |")
md += ["", "## Vehicle state", "",
       f"The {len(STATE)} state values the tools change and read, named by their [COVESA VSS](https://github.com/COVESA/vehicle_signal_specification) path. {NSTD} are standard VSS signals and {NEXTN} are extensions declared in `{PFX}_overlay.vspec`. Each conversation starts from a random but valid state, and every successful action updates it.", ""]
for g,(label,desc,_) in enumerate(GROUPS):
    md += [f"### {label}", "", desc+".", "", "| VSS signal | VSS kind | VSS type | Simulator type | Values | Start | Changed by | Read by |", "|---|---|---|---|---|---|---|---|"]
    for x in state_data:
        if x["g"]==g:
            w=", ".join(f"`{n}`" for n in x["w"]) or "read-only"
            r=", ".join(f"`{n}`" for n in x["r"])
            vt=x["vd"]+(f" ({x['vu']})" if x["vu"] else "")
            md.append(f"| `{x['p']}`{'' if x['std'] else ' *(extension)*'} | {x['vk']} | {vt} | {x['t']} | {x['v']} | {x['s']} | {w} | {r} |")
    md.append("")
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
    return {"n":n,"dom":t["domain"],"k":t["kind"],"d":t["description"],"p":params,"s":state,"neg":negative,"o":o,"src":src,"note":note,
            "w":st.get("writes",[]) if not negative else [],"r":st.get("reads",[]) if not negative else [],"ext":bool(st.get("external"))}
data={"pos":[tool_entry(n,t) for n,t in pos.items()],"neg":[tool_entry(n,t,True) for n,t in neg.items()],"state":state_data,"stype":STYPE,
      "groups":[[i,l,d] for i,(l,d,_) in enumerate(GROUPS)]}
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
// Collapse seat, door, zone, and wheel instances so one line shows what a tool touches.
function compress(paths) {
  const groups = new Map();
  for (const p of paths) {
    const pat = p.replace(/\.Row\d\./g, ".Row*.").replace(/\.(DriverSide|PassengerSide)\./g, ".*Side.").replace(/\.Row\*\.(Driver|Passenger)\./g, ".Row*.*.").replace(/\.Wheel\.(Left|Right)\./g, ".Wheel.*.").replace(/\.Stop\d\./g, ".Stop*.");
    if (!groups.has(pat)) groups.set(pat, [pat, 0, p]);
    groups.get(pat)[1]++;
  }
  return [...groups.values()];
}
function item(t) {
  const cls = t.neg ? "k-neg" : "k-" + t.k;
  const label = t.neg ? "negative" : t.k;
  const params = t.p.length ? '<ul class="params">' + t.p.map(p => `<li><span><span class="pn">${esc(p.n)}</span><span class="pt">${p.t}${p.req ? "" : " · optional"}</span></span><span class="pd">${fmt(p.d)}</span></li>`).join("") + "</ul>" : '<p class="state">No parameters</p>';
  const otag = `<span class="otag o-${t.o}">${TAG[t.o]}</span>`;
  const sig = `<span class="sig">(${t.p.map(p => `${esc(p.n)}${p.req ? "" : "?"}: <b>${p.t}</b>`).join(", ")})</span>`;
  const plist = (label, paths) => `<div class="slist"><span class="slabel">${label}</span><ul>${paths.map(x => `<li><a href="#s-${x}" data-state="${x}"><code>${esc(x)}</code></a> <span class="pt">${DATA.stype[x]}</span></li>`).join("")}</ul></div>`;
  const glance = t.neg ? "" : t.ext ? `<span class="tstate"><span class="glabel">No vehicle state</span></span>` :
    `<span class="tstate"><span class="glabel">${t.w.length ? "Changes" : "Reads"}</span>${compress(t.w.length ? t.w : t.r).map(([pat, n, first]) => `<a class="gpath" href="#s-${first}" data-state="${first}"><code>${esc(pat).replace(/\./g, ".<wbr>")}</code>${n > 1 ? `<span class="gn">×${n}</span>` : ""} <span class="pt">${DATA.stype[first]}</span></a>`).join("")}</span>`;
  const stateBlock = t.neg ? "" : t.ext ? `<p class="state">Uses outside data only. It changes and reads no vehicle state.</p>` : (t.w.length ? plist("All vehicle state it changes", t.w) : plist("All vehicle state it reads", t.r));
  const src = t.src.length ? `<p class="state">CAR-bench source: ${t.src.map(x => `<code>${esc(x)}</code>`).join(", ")}.${t.note ? " " + esc(t.note) : ""}</p>` : "";
  return `<details id="t-${t.n}"><summary><span class="chip ${cls}">${label}</span><span class="tline"><span class="tname">${t.n}</span>${sig}${otag}</span><span class="tdesc">${fmt(first(t.d))}</span>${glance}</summary><div class="body"><p>${fmt(t.d)}</p>${params}${stateBlock}${src}</div></details>`;
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
document.querySelectorAll(".seg button[data-k], .seg button[data-o]").forEach(b => b.addEventListener("click", () => {
  if ("k" in b.dataset) kind = b.dataset.k; else origin = b.dataset.o;
  b.parentElement.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b));
  render();
}));
document.querySelectorAll('tbody th a').forEach(a => a.addEventListener("click", () => {
  document.getElementById("dom").value = ""; document.getElementById("q").value = ""; kind = ""; origin = "";
  document.querySelectorAll(".seg button[data-k], .seg button[data-o]").forEach(x => x.setAttribute("aria-pressed", (x.dataset.k ?? x.dataset.o) === "")); render();
}));
function toolLink(n) { return `<a href="#t-${n}" data-tool="${n}"><code>${n.replace(/_/g, "_<wbr>")}</code></a>`; }
let vfilter = "";
function renderState() {
  const q = document.getElementById("sq").value.trim().toLowerCase();
  let out = "", n = 0;
  for (const [g, label, desc] of DATA.groups) {
    const rows = DATA.state.filter(x => x.g === g && (!q || (x.p + " " + x.d + " " + x.vk + " " + (x.std ? "standard" : "extension") + " " + x.w.join(" ") + " " + x.r.join(" ")).toLowerCase().includes(q)) && (!vfilter || (vfilter === "ext") !== x.std));
    if (!rows.length) continue;
    n += rows.length;
    out += `<div class="sgroup"><h3>${label} <small>${desc} · ${rows.length}</small></h3><div class="tablebox"><table class="stable"><thead><tr><th scope="col">VSS signal</th><th scope="col">Type</th><th scope="col">Values</th><th scope="col">Start</th><th scope="col">Changed by</th><th scope="col">Read by</th></tr></thead><tbody>` +
      rows.map(x => `<tr id="s-${x.p}"><td><code class="spath">${esc(x.p).replace(/\./g, ".<wbr>")}</code><span class="vtags"><span class="vk vk-${x.vk}">${x.vk}</span>${x.std ? '<span class="vstd">VSS standard</span>' : '<span class="vext">extension</span>'}</span><span class="sdesc">${esc(x.d)}</span></td><td><span class="ttype">${x.t}</span><span class="vtype">VSS ${esc(x.vd)}${x.vu ? " · " + esc(x.vu) : ""}</span></td><td class="vals${x.t === "bool" ? " nw" : ""}">${esc(x.v)}</td><td class="start">${esc(x.s)}</td><td class="tools">${x.w.length ? x.w.map(toolLink).join(" ") : '<span class="ro">read-only</span>'}</td><td class="tools">${x.r.map(toolLink).join(" ")}</td></tr>`).join("") +
      `</tbody></table></div></div>`;
  }
  document.getElementById("slist").innerHTML = out || '<p class="empty">No state values match. Try another word.</p>';
  document.getElementById("scount").textContent = `${n} shown`;
}
document.getElementById("sq").addEventListener("input", renderState);
document.querySelectorAll(".seg button[data-v]").forEach(b => b.addEventListener("click", () => {
  vfilter = b.dataset.v;
  b.parentElement.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", x === b));
  renderState();
}));
document.addEventListener("click", e => {
  const a = e.target.closest("a[data-tool], a[data-state]");
  if (!a) return;
  e.preventDefault();
  let el;
  if (a.dataset.tool) {
    document.getElementById("dom").value = ""; document.getElementById("q").value = ""; kind = ""; origin = "";
    document.querySelectorAll(".seg button[data-k], .seg button[data-o]").forEach(x => x.setAttribute("aria-pressed", (x.dataset.k ?? x.dataset.o) === ""));
    render();
    el = document.getElementById("t-" + a.dataset.tool); if (el) el.open = true;
  } else {
    document.getElementById("sq").value = ""; renderState();
    el = document.getElementById("s-" + a.dataset.state);
    if (el) { el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash"); }
  }
  if (el) el.scrollIntoView({block: "center"});
});
render();
renderState();
</script>
'''
frag=f'''<title>Tools VSS</title>
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
.eyebrow {{ font-size:12px; color:var(--muted); font-weight:500; }}
.totals {{ display:flex; flex-wrap:wrap; gap:8px 28px; font-variant-numeric:tabular-nums; }}
.totals div {{ display:grid; }}
.totals b {{ font-size:32px; font-weight:600; line-height:1.1; }}
.totals span {{ color:var(--muted); font-size:13px; }}
.totals .pos b {{ color:var(--fg); }} .totlink {{ color:inherit; text-decoration:none; }} .totals .neg b {{ color:var(--neg); }}
section {{ display:grid; gap:14px; min-width:0; }}
.tablebox {{ position:relative; overflow-x:auto; background:var(--surface); border:1px solid var(--line); border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; min-width:680px; font-variant-numeric:tabular-nums; }}
th,td {{ padding:10px 14px; text-align:left; border-bottom:1px solid var(--line); vertical-align:middle; }}
thead th {{ font-size:12px; color:var(--muted); font-weight:500; }}
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
.chip {{ font-size:12px; font-weight:500; padding:2px 7px; border-radius:4px; grid-row:span 3; align-self:start; margin-top:3px; min-width:68px; text-align:center; }}
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
.params .pt {{ margin-left:6px; }}
.params .pd {{ color:var(--muted); min-width:0; }}
.state {{ font-size:13px; color:var(--muted); }}
.empty {{ color:var(--muted); padding:20px 0; }}
.sig {{ font-family:var(--font-mono); font-size:13px; color:var(--muted); overflow-wrap:anywhere; }}
.sig b {{ font-weight:500; color:var(--retrieve); }}
.slist {{ display:grid; gap:4px; }}
.slabel {{ font-size:13px; color:var(--muted); font-weight:500; }}
.tstate {{ display:flex; flex-wrap:wrap; gap:4px 8px; align-items:baseline; font-size:13px; min-width:0; }}
.glabel {{ color:var(--muted); }}
.gpath {{ color:var(--fg); text-decoration:none; background:var(--bg); border:1px solid var(--line); border-radius:4px; padding:0 6px; overflow-wrap:anywhere; }}
.gpath:hover {{ border-color:var(--muted); }}
.gpath code {{ font-size:12px; }}
.gn {{ color:var(--muted); font-size:12px; margin-left:3px; }}
.slist ul {{ margin:0; padding:0; list-style:none; display:flex; flex-wrap:wrap; gap:4px 16px; font-size:13px; }}
.slist a, td.tools a {{ color:var(--fg); text-decoration:none; border-bottom:1px dotted var(--muted); }}
.slist a:hover, td.tools a:hover {{ border-bottom-style:solid; }}
.pt {{ color:var(--muted); font-size:12px; font-family:var(--font-mono); }}
.sgroup {{ display:grid; gap:8px; }}
.sgroup h3 {{ display:flex; flex-wrap:wrap; gap:4px 10px; align-items:baseline; padding-top:8px; }}
.sgroup h3 small {{ font-weight:400; color:var(--muted); font-size:13px; }}
table.stable {{ min-width:900px; font-size:13px; }}
table.stable td {{ vertical-align:top; }}
.spath {{ font-weight:500; display:block; overflow-wrap:normal; }}
.sdesc {{ display:block; color:var(--muted); max-width:40ch; }}
.ttype {{ font-family:var(--font-mono); color:var(--retrieve); }}
td.vals {{ font-family:var(--font-mono); font-size:12px; min-width:14ch; max-width:22ch; overflow-wrap:anywhere; }}
td.start {{ color:var(--muted); white-space:nowrap; }}
td.tools {{ font-size:12px; line-height:1.9; min-width:16ch; }}
td.tools a {{ margin-right:6px; }}
.ro {{ color:var(--muted); font-style:italic; }}
.facts {{ margin:0; padding-left:20px; display:grid; gap:6px; max-width:75ch; }}
.facts li {{ padding-left:2px; }}
.vtags {{ display:flex; flex-wrap:wrap; gap:4px; margin:3px 0; }}
.vk, .vstd, .vext {{ font-size:11px; padding:0 6px; border-radius:4px; border:1px solid var(--line); color:var(--muted); }}
.vk-actuator {{ color:var(--action); border-color:var(--action); }}
.vk-sensor {{ color:var(--retrieve); border-color:var(--retrieve); }}
.vk-attribute {{ color:var(--muted); }}
.vext {{ background:var(--fg); border-color:var(--fg); color:var(--bg); }}
.vtype {{ display:block; color:var(--muted); font-size:11px; font-family:var(--font-mono); white-space:nowrap; }}
header a, #h-vss ~ * a, section p a {{ color:var(--retrieve); }}
td.nw {{ white-space:nowrap; }}
tr.flash td {{ animation:flash 1.6s ease-out; }}
@keyframes flash {{ from {{ background:var(--retrieve-soft); }} to {{ background:transparent; }} }}
@media (prefers-reduced-motion: reduce) {{ tr.flash td {{ animation:none; background:var(--retrieve-soft); }} }}
@media (max-width:560px) {{ .params li {{ grid-template-columns:1fr; }} .totals b {{ font-size:26px; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ scroll-behavior:auto !important; }} }}
</style>
<div class="wrap">
<header>
  <h1>Tools VSS</h1>
  <p>Tool specs and vehicle state for a plug-in hybrid in-car assistant, with every state value named after a COVESA Vehicle Signal Specification signal. They keep every CAR-bench capability and add hybrid energy, media, access, seats, visibility, and read-only vehicle status.</p>
  <div class="totals">
    <div><b>{len(pos)+len(neg)}</b><span>tools in total</span></div>
    <div class="pos"><b>{len(pos)}</b><span>positive ({TA} action · {TR} retrieve)</span></div>
    <div class="neg"><b>{len(neg)}</b><span>negative (to decline)</span></div>
    <div><b><a class="totlink" href="#h-state">{len(inv["state"])}</a></b><span>state values ({NSTD} VSS · {NEXTN} extension)</span></div>
  </div>
</header>
<section aria-labelledby="h-vss">
  <h2 id="h-vss">Built on VSS</h2>
  <p>The <a href="https://github.com/COVESA/vehicle_signal_specification">Vehicle Signal Specification</a> (VSS) from COVESA is an open catalog of vehicle data, not a programming framework. It names every signal a car can expose with a dot path such as <code>Vehicle.Body.Lights.Fog.Front.IsOn</code> and gives it a kind, a datatype, a unit, and allowed values. BMW, Volvo, JLR, Bosch, and others contribute to it, and servers such as KUKSA expose a car's live data under these names.</p>
  <ul class="facts">
    <li><b>sensor</b> is read from the car, like <code>Vehicle.Speed</code>. <b>actuator</b> can be requested, like <code>Vehicle.Cabin.HVAC.IsAirConditioningActive</code>. <b>attribute</b> is a fixed fact, like the tank capacity.</li>
    <li>This tool set names every vehicle state value after its VSS signal and keeps VSS's types, units, and allowed values. Tools follow them too: fan speed is stored in percent, the sunroof can tilt, and seat heating and ventilation share one heating-cooling value, so a seat cannot heat and cool at once.</li>
    <li>What VSS lacks, such as the hybrid mode, navigation stops, and media mute, is added as an overlay in VSS's own format. COVESA's vss-tools accepts the overlay in strict mode, so every path here resolves to a real or declared signal.</li>
  </ul>
</section>
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
<section aria-labelledby="h-state">
  <h2 id="h-state">Vehicle state</h2>
  <p class="note">The {len(STATE)} values the tools change and read, each named by its VSS path. {NSTD} are standard VSS signals; {NEXTN} are extensions this car needs that VSS does not define, declared in <code>{PFX}_overlay.vspec</code>. Each conversation starts from a random but valid state, and every successful action updates it. Tool names link to the tool above.</p>
  <div class="controls">
    <input id="sq" type="search" placeholder="Search VSS paths, descriptions, or tools" aria-label="Search vehicle state">
    <div class="seg" role="group" aria-label="Filter by VSS status">
      <button type="button" data-v="" aria-pressed="true">All signals</button><button type="button" data-v="std" aria-pressed="false">VSS standard</button><button type="button" data-v="ext" aria-pressed="false">Extensions</button>
    </div>
    <span class="count" id="scount"></span>
  </div>
  <div id="slist"></div>
</section>
</div>
__SCRIPT__
'''
frag = frag.replace("__SCRIPT__", SCRIPT.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__ORDER__", json.dumps([[r[0], r[1]] for r in rows], ensure_ascii=False)))
frag = frag.replace('<span class="sr">Share</span>', '<span style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Share</span>')
out_html_frag.write_text(frag)
out_html_full.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + frag.replace("</style>","</style>\n</head>\n<body>",1) + "</body>\n</html>\n")
print(TA,TR,len(pos),len(neg))
