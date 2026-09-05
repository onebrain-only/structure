#!/usr/bin/env python3
"""
One Brain — live agent flow.

Reads Claude Code session transcripts and the local agent roster, and serves a
live node graph of the company actually working: which seat was dispatched, what
it ran, what came back, and what is in flight right now.

Standard library only. No install step.

    python3 agent/scripts/flow.py            # then open http://localhost:7373
    python3 agent/scripts/flow.py --port 8080
"""
import argparse, json, os, re, sys, time, collections
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS = os.path.expanduser("~/.claude/projects")


def project_dir():
    """The transcript directory Claude Code uses for this workspace."""
    slug = ROOT.replace("/", "-")
    for cand in (slug, slug.lstrip("-")):
        p = os.path.join(PROJECTS, cand)
        if os.path.isdir(p):
            return p
    # fall back to the most recently written project dir
    if not os.path.isdir(PROJECTS):
        return None
    dirs = [os.path.join(PROJECTS, d) for d in os.listdir(PROJECTS)]
    dirs = [d for d in dirs if os.path.isdir(d)]
    return max(dirs, key=os.path.getmtime) if dirs else None


# ---------------------------------------------------------------- roster

def roster():
    """The 30 seats, their tier, and whether they have ever logged work."""
    seats = {}
    bind = os.path.join(ROOT, ".claude", "bindings")
    if not os.path.isdir(bind):
        return seats
    for fn in sorted(os.listdir(bind)):
        if not fn.endswith(".yml"):
            continue
        name = fn[:-4]
        model = effort = "—"
        for line in open(os.path.join(bind, fn), encoding="utf-8", errors="replace"):
            if line.startswith("model:"):
                model = line.split(":", 1)[1].strip()
            elif line.startswith("effort:"):
                effort = line.split(":", 1)[1].strip()
        st = os.path.join(ROOT, "agent", "status", name + ".md")
        logged = False
        if os.path.exists(st):
            logged = "_No entries yet._" not in open(st, encoding="utf-8", errors="replace").read()
        seats[name] = {"name": name, "model": model, "effort": effort, "logged": logged,
                       "level": level_of(name)}
    return seats


def level_of(n):
    if n in ("cto", "cpo", "cxo", "analyst"):
        return "company"
    if n in ("pm", "devops", "content-manager"):
        return "product"
    if n == "po" or n == "qa" or n.startswith("team-lead"):
        return "project"
    return "developer"


# ---------------------------------------------------------------- transcript

TOOL_SHORT = {"mcp__atlassian__": "jira:", "mcp__supabase__": "db:", "mcp__github-dabbler__": "gh:"}


def shorten(tool):
    for pre, rep in TOOL_SHORT.items():
        if tool.startswith(pre):
            return rep + tool[len(pre):]
    return tool


def parse(path):
    """Flatten one transcript into events, dispatches and a file-attention map."""
    events, dispatches, messages = [], [], []
    files = collections.Counter()
    tools = collections.Counter()
    use = {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0, "think": 0, "msgs": 0}
    model_seen = collections.Counter()
    turns = 0
    first = last = None

    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue

            ts = d.get("timestamp")
            if ts:
                first = first or ts
                last = ts

            typ = d.get("type")
            msg = d.get("message") or {}
            content = msg.get("content")

            u = msg.get("usage")
            if isinstance(u, dict):
                use["msgs"] += 1
                use["in"] += u.get("input_tokens", 0) or 0
                use["out"] += u.get("output_tokens", 0) or 0
                use["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
                use["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
                det = u.get("output_tokens_details") or {}
                use["think"] += det.get("thinking_tokens", 0) or 0
                if msg.get("model"):
                    model_seen[msg["model"]] += 1

            if typ == "user" and isinstance(content, str) and content.strip():
                txt = content.strip()
                m = re.search(r'teammate_id="([^"]+)"', txt)
                if m or txt.startswith("Another Claude session sent a message"):
                    who = m.group(1) if m else "agent"
                    body = re.sub(r"<[^>]+>", " ", txt)
                    body = re.sub(r'^.*?(?:summary="([^"]*)")?\s*', lambda x: x.group(1) or "", body, count=1)
                    body = re.sub(r'\{"type":"[^"]*","from":"[^"]*"[^}]*', "returned", body)
                    events.append({"kind": "return", "ts": ts, "who": who,
                                   "text": " ".join(body.split())[:220]})
                    continue
                turns += 1
                events.append({"kind": "prompt", "ts": ts, "text": txt[:400]})
                continue

            if not isinstance(content, list):
                continue

            # some agent replies arrive as structured content rather than a plain
            # string; catch those too or the run never closes
            if typ == "user":
                joined = " ".join(b.get("text", "") for b in content
                                  if isinstance(b, dict) and b.get("type") == "text")
                m = re.search(r'teammate_id="([^"]+)"', joined)
                if not m:
                    m = re.search(r'"from"\s*:\s*"([^"]+)"', joined)
                if m:
                    body = re.sub(r"<[^>]+>", " ", joined)
                    body = re.sub(r'\{"type":"[^"]*","from":"[^"]*"[^}]*', "returned", body)
                    events.append({"kind": "return", "ts": ts, "who": m.group(1),
                                   "text": " ".join(body.split())[:220]})
                    continue

            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and typ == "assistant":
                    t = (b.get("text") or "").strip()
                    if t:
                        events.append({"kind": "say", "ts": ts, "text": t[:400]})
                elif b.get("type") == "tool_use":
                    name = b.get("name", "?")
                    inp = b.get("input") or {}
                    tools[shorten(name)] += 1
                    if name == "Agent":
                        seat = inp.get("subagent_type", "?")
                        inst = inp.get("name") or seat
                        dispatches.append({"seat": seat, "instance": inst, "ts": ts,
                                           "desc": inp.get("description", ""),
                                           "model": inp.get("model", "")})
                        events.append({"kind": "dispatch", "ts": ts, "seat": seat, "instance": inst,
                                       "text": inp.get("description", "")})
                    elif name == "SendMessage":
                        messages.append({"to": inp.get("to", "?"), "ts": ts,
                                         "summary": inp.get("summary", "")})
                        events.append({"kind": "message", "ts": ts, "to": inp.get("to", "?"),
                                       "text": inp.get("summary", "")})
                    else:
                        label = ""
                        for k in ("file_path", "command", "pattern", "skill", "query", "url"):
                            if isinstance(inp.get(k), str):
                                label = inp[k]
                                break
                        fp = inp.get("file_path")
                        if isinstance(fp, str):
                            files[os.path.relpath(fp, ROOT) if fp.startswith(ROOT) else fp] += 1
                        if name == "Bash":
                            for m in re.findall(r"[\w][\w./-]{3,}\.(?:dart|md|yml|json|sql|py|ts|html)", label or ""):
                                if not m.startswith("-"):
                                    files[m.lstrip("./")] += 1
                        events.append({"kind": "tool", "ts": ts, "tool": shorten(name),
                                       "text": (label or "")[:200]})

    # pair each dispatch with the reply that came back, so a run has a real duration
    def secs(a, b):
        try:
            from datetime import datetime
            f = lambda x: datetime.fromisoformat(x.replace("Z", "+00:00"))
            return max(0, int((f(b) - f(a)).total_seconds()))
        except Exception:
            return None

    runs, open_by = [], {}
    order = 0
    for e in events:
        if e["kind"] == "dispatch":
            order += 1
            r = {"seat": e["seat"], "instance": e["instance"], "start": e["ts"], "end": None,
                 "desc": e.get("text", ""), "secs": None, "order": order, "tools": 0}
            runs.append(r); open_by[e["instance"]] = r
        elif e["kind"] == "return":
            r = open_by.get(e["who"])
            if r and not r["end"]:
                r["end"] = e["ts"]; r["secs"] = secs(r["start"], e["ts"])
        elif e["kind"] == "tool":
            for r in runs:
                if r["end"] is None:
                    r["tools"] += 1

    # Claude Opus 5 list price, verified: $5.00 / MTok in, $25.00 / MTok out.
    # Cache read and write are deliberately NOT priced here — the rate depends on
    # the cache TTL in use and guessing it would put a wrong number on screen.
    model = model_seen.most_common(1)[0][0] if model_seen else "—"
    RATE = {"claude-opus-5": (5.0, 25.0)}.get(model)
    use["model"] = model
    use["priced"] = bool(RATE)
    use["cost"] = round(use["in"] / 1e6 * RATE[0] + use["out"] / 1e6 * RATE[1], 2) if RATE else None

    return {"events": events, "dispatches": dispatches, "messages": messages, "runs": runs,
            "usage": use,
            "tools": tools.most_common(14), "files": files.most_common(16),
            "turns": turns, "first": first, "last": last}


_CACHE = {}


def parse_cached(path):
    """Re-parse only when the transcript actually changed."""
    try:
        sig = (os.path.getmtime(path), os.path.getsize(path))
    except OSError:
        return parse(path)
    hit = _CACHE.get(path)
    if hit and hit[0] == sig:
        return hit[1]
    out = parse(path)
    _CACHE[path] = (sig, out)
    return out


def sessions():
    d = project_dir()
    if not d:
        return []
    out = []
    for fn in os.listdir(d):
        if not fn.endswith(".jsonl"):
            continue
        p = os.path.join(d, fn)
        try:
            sz = os.path.getsize(p)
            if sz < 2000:
                continue
            out.append({"id": fn[:-6], "path": p, "size": sz, "mtime": os.path.getmtime(p)})
        except OSError:
            continue
    return sorted(out, key=lambda s: s["mtime"], reverse=True)


def state(session_id=None):
    ses = sessions()
    if not ses:
        return {"error": "No session transcripts found under ~/.claude/projects.", "sessions": []}
    pick = next((s for s in ses if s["id"] == session_id), ses[0])
    data = parse_cached(pick["path"])
    seats = roster()
    used = collections.Counter(d["seat"] for d in data["dispatches"])
    for name, s in seats.items():
        s["dispatched"] = used.get(name, 0)
    return {
        "sessions": [{"id": s["id"], "size": s["size"], "mtime": s["mtime"],
                      "live": (time.time() - s["mtime"]) < 120} for s in ses],
        "active": pick["id"],
        "live": (time.time() - pick["mtime"]) < 120,
        "seats": sorted(seats.values(), key=lambda x: x["name"]),
        "generated": time.time(),
        **data,
    }


# ---------------------------------------------------------------- page

PAGE = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>One Brain — Agent Flow</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{--paper:#F3F4F1;--raise:#FFF;--ink:#171C1A;--ink2:#3D4744;--muted:#6B7671;
--rule:#CBD2CE;--soft:#E1E6E2;--struct:#3E5F63;--structsoft:#DCE6E6;
--signal:#B4560B;--signalsoft:#F6E4D2;--live:#1F6F4A;--livesoft:#DCEDE3;--grid:#E4E8E4}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--paper:#111513;--raise:#181E1B;
--ink:#E7ECE7;--ink2:#B4BDB8;--muted:#828E88;--rule:#2B332F;--soft:#212824;--struct:#7FAAAE;
--structsoft:#1C2626;--signal:#E5883C;--signalsoft:#2B1E11;--live:#5FBE8C;--livesoft:#14241B;--grid:#1B211D}}
:root[data-theme=dark]{--paper:#111513;--raise:#181E1B;--ink:#E7ECE7;--ink2:#B4BDB8;--muted:#828E88;
--rule:#2B332F;--soft:#212824;--struct:#7FAAAE;--structsoft:#1C2626;--signal:#E5883C;
--signalsoft:#2B1E11;--live:#5FBE8C;--livesoft:#14241B;--grid:#1B211D}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 "IBM Plex Sans",system-ui,sans-serif;
-webkit-font-smoothing:antialiased;overflow:hidden}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
h1{font-family:"Bricolage Grotesque",system-ui,sans-serif;font-size:19px;font-weight:800;letter-spacing:-.02em;margin:0}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}

.bar{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:11px 18px;
border-bottom:1px solid var(--rule);background:var(--raise);height:52px}
.dot{width:8px;height:8px;border-radius:50%;background:var(--muted);display:inline-block;margin-right:6px}
.dot.on{background:var(--live);box-shadow:0 0 0 3px var(--livesoft)}
@media(prefers-reduced-motion:no-preference){.dot.on{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}
.counts{display:flex;margin-left:auto;border:1px solid var(--rule);border-radius:2px;overflow:hidden}
.counts div{padding:4px 12px;border-right:1px solid var(--rule)}
.counts div:last-child{border-right:0}
.counts b{font-family:"IBM Plex Mono",monospace;font-size:14px;font-variant-numeric:tabular-nums;display:block;line-height:1.2}
.counts span{font-size:9.5px;color:var(--muted)}
select,button{font-family:"IBM Plex Mono",monospace;font-size:11px;padding:5px 9px;background:var(--paper);
color:var(--ink);border:1px solid var(--rule);border-radius:2px;cursor:pointer}
button:hover{border-color:var(--struct)}
button:focus-visible,select:focus-visible{outline:2px solid var(--struct);outline-offset:1px}

.grid{display:grid;grid-template-columns:216px minmax(0,1fr) 300px;height:calc(100vh - 52px)}
.rail{overflow-y:auto;padding:14px 15px;border-right:1px solid var(--rule)}
.insp{overflow-y:auto;padding:14px 16px;border-left:1px solid var(--rule);background:var(--raise)}
.rail h2,.insp h2{font-family:"Bricolage Grotesque",sans-serif;font-size:12px;font-weight:600;margin:0 0 9px;letter-spacing:-.01em}
.canvas{position:relative;overflow:hidden;background:var(--paper);cursor:grab}
.canvas.drag{cursor:grabbing}
svg{display:block;width:100%;height:100%;touch-action:none}

.lvl{margin-bottom:12px}
.lvl>.eyebrow{display:block;margin-bottom:5px;color:var(--struct)}
.seat{display:flex;justify-content:space-between;align-items:center;gap:6px;padding:3px 7px;
border:1px solid transparent;border-radius:2px;font-family:"IBM Plex Mono",monospace;font-size:10.5px}
.seat.logged{color:var(--ink2)}
.seat:not(.logged){color:var(--muted)}
.seat.hot{background:var(--signalsoft);border-color:var(--signal);color:var(--signal);font-weight:600}
.seat .tier{font-size:9px;opacity:.65}
.seat .n{background:var(--signal);color:#fff;border-radius:8px;padding:0 5px;font-size:9px;font-weight:600}

.hint{position:absolute;left:14px;bottom:12px;font-family:"IBM Plex Mono",monospace;font-size:10px;
color:var(--muted);background:var(--raise);border:1px solid var(--rule);padding:4px 9px;border-radius:2px}
.zoom{position:absolute;right:14px;bottom:12px;display:flex;gap:5px}

.kv{font-family:"IBM Plex Mono",monospace;font-size:11px;display:flex;justify-content:space-between;
gap:8px;padding:4px 0;border-bottom:1px solid var(--soft)}
.kv span{color:var(--muted)}
.kv b{font-weight:500;text-align:right}
.insp .desc{font-size:13px;color:var(--ink2);margin:8px 0 12px}
.tag{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:10px;padding:1px 7px;
border-radius:2px;margin-bottom:9px}
.tag.company{background:var(--structsoft);color:var(--struct)}
.tag.product{background:var(--livesoft);color:var(--live)}
.tag.project{background:var(--signalsoft);color:var(--signal)}
.tag.developer{background:var(--soft);color:var(--ink2)}
.empty{color:var(--muted);font-size:12.5px;padding:14px 0}
.chip{font-family:"IBM Plex Mono",monospace;font-size:10px;padding:1px 6px;border:1px solid var(--rule);
border-radius:2px;color:var(--muted);display:inline-block;margin:0 3px 3px 0}
</style></head><body>

<div class="bar">
  <h1>One Brain</h1>
  <span class="eyebrow" id="livelabel"><span class="dot"></span>connecting</span>
  <select id="sess"></select>
  <button id="fit">fit</button>
  <div class="counts">
    <div><b id="cTurns">0</b><span>turns</span></div>
    <div><b id="cRuns">0</b><span>runs</span></div>
    <div><b id="cTools">0</b><span>tool calls</span></div>
    <div><b id="cSeats">0</b><span>seats woken</span></div>
  </div>
</div>

<div class="grid">
  <div class="rail"><h2>The roster</h2><div id="roster"></div></div>
  <div class="canvas" id="canvas">
    <svg id="svg"><g id="scene"></g></svg>
    <div class="hint">drag to pan · scroll to zoom · click a node</div>
    <div class="zoom"><button id="zout">−</button><button id="zin">+</button></div>
  </div>
  <div class="insp"><h2>Inspector</h2><div id="insp"><p class="empty">Click a node in the graph.</p></div></div>
</div>

<script>
var LEVELS=[["company","Company"],["product","Product"],["project","Project"],["developer","Developers"]];
var NS="http://www.w3.org/2000/svg";
var picked=null,misses=0,sel=null,S=null,view={x:0,y:0,k:1},didFit=false;

function esc(s){return (s||"").replace(/[<>&"]/g,function(c){
  return {"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c]})}
function t2ms(t){var d=new Date(t);return isNaN(d)?0:d.getTime()}
function clock(t){var d=new Date(t);return isNaN(d)?"":d.toTimeString().slice(0,5)}
function el(n,a){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);return e}
function levelOf(n){
  if(["cto","cpo","cxo","analyst"].indexOf(n)>=0)return "company";
  if(["pm","devops","content-manager"].indexOf(n)>=0)return "product";
  if(n==="po"||n==="qa"||n.indexOf("team-lead")===0)return "project";
  return "developer"}

function apply(){document.getElementById("scene").setAttribute("transform",
  "translate("+view.x+","+view.y+") scale("+view.k+")")}

/* ---- graph ---------------------------------------------------------- */
var LANE_Y=150, LANE_H=74, LEFT=120, SPAN=1180;

function draw(s){
  var scene=document.getElementById("scene");
  while(scene.firstChild) scene.removeChild(scene.firstChild);
  var runs=s.runs||[]; if(!runs.length){ return }

  var stamps=[]; runs.forEach(function(r){stamps.push(t2ms(r.start)); if(r.end)stamps.push(t2ms(r.end))});
  (s.events||[]).forEach(function(e){if(e.kind==="prompt")stamps.push(t2ms(e.ts))});
  var t0=Math.min.apply(null,stamps), t1=Math.max.apply(null,stamps);
  var X=function(t){ return t1===t0 ? LEFT : LEFT + (t2ms(t)-t0)/(t1-t0)*SPAN };

  // one lane per seat, ordered by first dispatch
  var lanes=[],laneOf={};
  runs.forEach(function(r){ if(!(r.seat in laneOf)){ laneOf[r.seat]=lanes.length; lanes.push(r.seat) } });

  // lane backgrounds + labels
  lanes.forEach(function(seat,i){
    var y=LANE_Y+60+i*LANE_H;
    scene.appendChild(el("line",{x1:LEFT-60,y1:y,x2:LEFT+SPAN+70,y2:y,
      stroke:"var(--grid)","stroke-width":1}));
    var lb=el("text",{x:LEFT-70,y:y+4,"text-anchor":"end",fill:"var(--muted)",
      "font-family":"IBM Plex Mono, monospace","font-size":11});
    lb.textContent=seat; scene.appendChild(lb);
  });

  // the Listener spine
  scene.appendChild(el("line",{x1:LEFT-60,y1:LANE_Y,x2:LEFT+SPAN+70,y2:LANE_Y,
    stroke:"var(--rule)","stroke-width":2}));
  var sl=el("text",{x:LEFT-70,y:LANE_Y+4,"text-anchor":"end",fill:"var(--ink)",
    "font-family":"IBM Plex Mono, monospace","font-size":11.5,"font-weight":600});
  sl.textContent="listener"; scene.appendChild(sl);

  // CEO prompts above the spine
  (s.events||[]).filter(function(e){return e.kind==="prompt"}).forEach(function(e){
    var x=X(e.ts);
    scene.appendChild(el("line",{x1:x,y1:LANE_Y-42,x2:x,y2:LANE_Y,stroke:"var(--rule)","stroke-width":1}));
    var d=el("rect",{x:x-5,y:LANE_Y-47,width:10,height:10,fill:"var(--ink)",
      transform:"rotate(45 "+x+" "+(LANE_Y-42)+")"});
    d.style.cursor="pointer";
    d.addEventListener("click",function(ev){ev.stopPropagation();
      inspect({kind:"prompt",ts:e.ts,text:e.text})});
    scene.appendChild(d);
  });
  var cl=el("text",{x:LEFT-70,y:LANE_Y-38,"text-anchor":"end",fill:"var(--muted)",
    "font-family":"IBM Plex Mono, monospace","font-size":11});
  cl.textContent="CEO"; scene.appendChild(cl);

  // runs
  runs.forEach(function(r){
    var y=LANE_Y+60+laneOf[r.seat]*LANE_H;
    var x0=X(r.start), open=!r.end;
    // an open run gets a fixed stub, not a bar stretched to now — one unmatched
    // reply should not swamp the whole canvas
    var w=open?118:Math.max(96,X(r.end)-x0);
    var lv=levelOf(r.seat);
    var stroke=lv==="company"?"var(--struct)":lv==="product"?"var(--live)":
               lv==="project"?"var(--signal)":"var(--ink2)";

    // dispatch edge out, return edge back
    scene.appendChild(el("path",{d:"M"+x0+","+LANE_Y+" C"+x0+","+(LANE_Y+34)+" "+x0+","+(y-30)+" "+x0+","+(y-13),
      fill:"none",stroke:"var(--signal)","stroke-width":1.5}));
    if(!open) scene.appendChild(el("path",{
      d:"M"+(x0+w)+","+(y-13)+" C"+(x0+w)+","+(y-34)+" "+(x0+w)+","+(LANE_Y+30)+" "+(x0+w)+","+LANE_Y,
      fill:"none",stroke:"var(--live)","stroke-width":1.5,"stroke-dasharray":"3 3"}));

    var g=el("g",{}); g.style.cursor="pointer";
    g.appendChild(el("rect",{x:x0,y:y-13,width:w,height:26,rx:2,
      fill:"var(--raise)",stroke:stroke,"stroke-width":sel===r.instance?2.5:1.2}));
    g.appendChild(el("rect",{x:x0,y:y-13,width:3,height:26,fill:stroke}));
    var room=Math.floor((w-(w>150?52:30))/6.6);
    var tx=el("text",{x:x0+10,y:y+4,fill:"var(--ink)","font-family":"IBM Plex Mono, monospace",
      "font-size":11,"font-weight":500});
    tx.textContent=r.seat.length>room?r.seat.slice(0,Math.max(3,room-1))+"…":r.seat;
    g.appendChild(tx);
    if(r.secs!=null && w>150){
      var dt=el("text",{x:x0+w-8,y:y+4,"text-anchor":"end",fill:"var(--muted)",
        "font-family":"IBM Plex Mono, monospace","font-size":9.5});
      dt.textContent=r.secs+"s"; g.appendChild(dt);
    }
    if(open){
      g.appendChild(el("circle",{cx:x0+w-10,cy:y,r:3.5,fill:"var(--signal)"}));
      var op=el("text",{x:x0+w-20,y:y+3.5,"text-anchor":"end",fill:"var(--signal)",
        "font-family":"IBM Plex Mono, monospace","font-size":9});
      op.textContent="open"; g.appendChild(op);
    }
    g.addEventListener("click",function(ev){ev.stopPropagation(); sel=r.instance; inspect(r); draw(S)});
    scene.appendChild(g);
  });

  // messages sent to running agents
  (s.events||[]).filter(function(e){return e.kind==="message"}).forEach(function(e){
    var x=X(e.ts), ln=laneOf[ (e.to||"").replace(/-[^-]*$/,"") ];
    var y = ln!=null ? LANE_Y+60+ln*LANE_H : LANE_Y;
    scene.appendChild(el("path",{d:"M"+x+","+LANE_Y+" L"+x+","+(y-13),
      fill:"none",stroke:"var(--struct)","stroke-width":1,"stroke-dasharray":"2 4"}));
    scene.appendChild(el("circle",{cx:x,cy:LANE_Y,r:3,fill:"var(--struct)"}));
  });

  if(!didFit){ fit(); didFit=true }
}

function fit(){
  var c=document.getElementById("canvas");
  var w=c.clientWidth-40, need=SPAN+LEFT+120;
  view.k=Math.min(1, w/need); view.x=20; view.y=20; apply();
}

/* ---- inspector ------------------------------------------------------ */
function inspect(o){
  var h="";
  if(o.kind==="prompt"){
    h='<span class="tag developer">CEO prompt</span>'+
      '<div class="desc">'+esc(o.text)+'</div>'+
      '<div class="kv"><span>at</span><b>'+clock(o.ts)+'</b></div>';
  } else {
    var lv=levelOf(o.seat);
    h='<span class="tag '+lv+'">'+lv+'</span>'+
      '<div class="mono" style="font-size:14px;font-weight:600">'+esc(o.seat)+'</div>'+
      '<div class="desc">'+esc(o.desc||"—")+'</div>'+
      '<div class="kv"><span>instance</span><b>'+esc(o.instance)+'</b></div>'+
      '<div class="kv"><span>started</span><b>'+clock(o.start)+'</b></div>'+
      '<div class="kv"><span>returned</span><b>'+(o.end?clock(o.end):"— running")+'</b></div>'+
      '<div class="kv"><span>duration</span><b>'+(o.secs!=null?o.secs+"s":"—")+'</b></div>'+
      '<div class="kv"><span>listener tool calls<br>while it ran</span><b>'+o.tools+'</b></div>'+
      '<p class="empty" style="font-size:11.5px;line-height:1.5">Its own tool calls are not in this'+
      ' transcript — subagents run in their own context. Enabling Claude Code hooks would stream them.</p>';
  }
  document.getElementById("insp").innerHTML=h;
}

/* ---- data ----------------------------------------------------------- */
function render(s){
  S=s;
  if(s.error){document.getElementById("insp").innerHTML='<p class="empty">'+esc(s.error)+'</p>';return}
  document.getElementById("livelabel").innerHTML='<span class="dot'+(s.live?" on":"")+'"></span>'+(s.live?"live":"idle");
  var se=document.getElementById("sess");
  if(se.options.length!==s.sessions.length){
    se.innerHTML=s.sessions.map(function(x){return '<option value="'+x.id+'">'+(x.live?"● ":"")+
      x.id.slice(0,8)+"  ·  "+(x.size/1048576).toFixed(1)+"MB</option>"}).join("");
    se.value=s.active;
  }
  document.getElementById("cTurns").textContent=s.turns;
  document.getElementById("cRuns").textContent=(s.runs||[]).length;
  document.getElementById("cTools").textContent=s.tools.reduce(function(a,t){return a+t[1]},0);
  document.getElementById("cSeats").textContent=s.seats.filter(function(x){return x.dispatched>0}).length;

  document.getElementById("roster").innerHTML=LEVELS.map(function(L){
    return '<div class="lvl"><span class="eyebrow">'+L[1]+'</span>'+
      s.seats.filter(function(x){return x.level===L[0]}).map(function(x){
        return '<div class="seat'+(x.logged?" logged":"")+(x.dispatched>0?" hot":"")+'">'+
          '<span>'+esc(x.name)+'</span>'+(x.dispatched>0?'<span class="n">'+x.dispatched+'</span>':
          '<span class="tier">'+esc(x.model)+'·'+esc(x.effort)+'</span>')+'</div>'}).join("")+'</div>'
  }).join("");
  draw(s);
}

function tick(){
  fetch("/api/state"+(picked?"?s="+picked:""))
    .then(function(r){return r.json()}).then(function(s){misses=0;render(s)})
    .catch(function(){if(++misses>=2)document.getElementById("livelabel").innerHTML=
      '<span class="dot"></span>server stopped'});
}

/* ---- pan + zoom ----------------------------------------------------- */
var cv=document.getElementById("canvas"),down=false,sx=0,sy=0;
cv.addEventListener("mousedown",function(e){down=true;sx=e.clientX-view.x;sy=e.clientY-view.y;cv.classList.add("drag")});
window.addEventListener("mouseup",function(){down=false;cv.classList.remove("drag")});
window.addEventListener("mousemove",function(e){if(down){view.x=e.clientX-sx;view.y=e.clientY-sy;apply()}});
cv.addEventListener("wheel",function(e){e.preventDefault();
  var f=e.deltaY<0?1.12:1/1.12,k=Math.min(3,Math.max(.2,view.k*f));
  var r=cv.getBoundingClientRect(),mx=e.clientX-r.left,my=e.clientY-r.top;
  view.x=mx-(mx-view.x)*(k/view.k); view.y=my-(my-view.y)*(k/view.k); view.k=k; apply()},{passive:false});
document.getElementById("zin").onclick=function(){view.k=Math.min(3,view.k*1.2);apply()};
document.getElementById("zout").onclick=function(){view.k=Math.max(.2,view.k/1.2);apply()};
document.getElementById("fit").onclick=fit;
document.getElementById("sess").addEventListener("change",function(e){
  picked=e.target.value;didFit=false;sel=null;tick()});

tick(); setInterval(tick,2000);
</script></body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, ctype):
        b = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/api/state"):
            sid = None
            if "?s=" in self.path:
                sid = self.path.split("?s=", 1)[1].split("&")[0]
            try:
                self._send(json.dumps(state(sid)), "application/json")
            except Exception as e:
                self._send(json.dumps({"error": str(e), "sessions": []}), "application/json")
        else:
            self._send(PAGE, "text/html; charset=utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=7373)
    a = ap.parse_args()
    d = project_dir()
    print("One Brain — agent flow")
    print("  workspace   :", ROOT)
    print("  transcripts :", d or "NOT FOUND")
    print("  seats       :", len(roster()))
    print("  open        : http://localhost:%d" % a.port)
    print("  stop        : Ctrl-C")
    try:
        ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
