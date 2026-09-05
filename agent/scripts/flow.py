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


def subagent_runs(session_id):
    """What each dispatched seat actually did, from its own transcript.

    Every subagent writes a full transcript under
      ~/.claude/projects/<project>/<session>/subagents/agent-a<instance>-<hash>.jsonl
    These were there all along. An earlier version of this file claimed a
    dispatched seat's tool calls were unrecorded, on the strength of finding no
    `isSidechain` rows in the parent transcript. That was a wrong inference from
    the wrong file.
    """
    d = project_dir()
    if not d:
        return {}
    sub = os.path.join(d, session_id, "subagents")
    if not os.path.isdir(sub):
        return {}
    out = {}
    for fn in os.listdir(sub):
        if not fn.endswith(".jsonl") or not fn.startswith("agent-a"):
            continue
        inst = fn[len("agent-a"):-len(".jsonl")]
        inst = inst.rsplit("-", 1)[0]          # drop the trailing hash
        path = os.path.join(sub, fn)
        tools = collections.Counter()
        files = collections.Counter()
        rows = 0
        tok = {"out": 0, "think": 0, "cache_read": 0}
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        x = json.loads(line)
                    except Exception:
                        continue
                    rows += 1
                    m = x.get("message") or {}
                    u = m.get("usage") or {}
                    tok["out"] += u.get("output_tokens", 0) or 0
                    tok["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
                    tok["think"] += (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
                    c = m.get("content")
                    if not isinstance(c, list):
                        continue
                    for b in c:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            tools[shorten(b.get("name", "?"))] += 1
                            i = b.get("input") or {}
                            fp = i.get("file_path")
                            if isinstance(fp, str):
                                files[os.path.relpath(fp, ROOT) if fp.startswith(ROOT) else fp] += 1
        except OSError:
            continue
        out[inst] = {"rows": rows, "tools": tools.most_common(10),
                     "tool_total": sum(tools.values()),
                     "files": files.most_common(6),
                     "out": tok["out"], "think": tok["think"],
                     "cache_read": tok["cache_read"],
                     "cost": round(tok["out"] / 1e6 * 25.0, 2)}
    return out


def hook_events():
    """Events written by agent/scripts/flow-hook.sh, if hooks are configured.

    Absent until the CEO reloads settings once (/hooks). Until then the graph
    shows dispatch and reply and says plainly that the inside is not recorded.
    """
    p = os.path.join(ROOT, "agent", ".flow", "events.jsonl")
    if not os.path.exists(p):
        return {"live": False, "count": 0, "by_event": [], "by_session": []}
    ev = collections.Counter()
    ses = collections.Counter()
    n = 0
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                n += 1
                ev[d.get("event", "?")] += 1
                sid = d.get("session_id")
                if sid:
                    ses[sid] += 1
    except OSError:
        pass
    return {"live": n > 0, "count": n,
            "by_event": ev.most_common(), "by_session": ses.most_common(12)}


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
    inner = subagent_runs(pick["id"])
    for r in data.get("runs", []):
        r["inner"] = inner.get(r["instance"])
    data["inner_found"] = sum(1 for r in data.get("runs", []) if r.get("inner"))
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
        "hooks": hook_events(),
        **data,
    }


# ---------------------------------------------------------------- page

PAGE = r"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>One Brain — Agent Flow</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>
:root{
  --void:#0B0F0E; --deep:#101614; --panel:#141B19; --edge:#232D2A;
  --ink:#E8EDE9; --ink2:#9DA9A3; --dim:#5F6B66;
  --teal:#5FA8AE; --teal-dim:#2A4448;
  --amber:#E5883C; --amber-dim:#3A2716;
  --green:#5FBE8C; --green-dim:#17301F;
  --violet:#9A8FD8;
}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--void);color:var(--ink);overflow:hidden;
  font:14px/1.5 "IBM Plex Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}

/* ---------- chrome ---------- */
.top{position:fixed;inset:0 0 auto 0;height:50px;z-index:5;display:flex;align-items:center;gap:16px;
  padding:0 18px;background:linear-gradient(var(--void),rgba(11,15,14,.72));backdrop-filter:blur(6px)}
.brand{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:17px;letter-spacing:-.02em}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--dim);display:inline-block;margin-right:6px}
.pulse.on{background:var(--green);box-shadow:0 0 9px var(--green)}
@media(prefers-reduced-motion:no-preference){.pulse.on{animation:bp 2.4s ease-in-out infinite}}
@keyframes bp{0%,100%{opacity:1}50%{opacity:.35}}
.meta{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink2);letter-spacing:.02em}
.meta b{color:var(--ink);font-weight:600}
select{font-family:"IBM Plex Mono",monospace;font-size:11px;padding:4px 8px;background:var(--panel);
  color:var(--ink);border:1px solid var(--edge);border-radius:3px}
.spacer{margin-left:auto}

/* ---------- ledger ---------- */
.ledger{position:fixed;right:16px;top:62px;width:242px;z-index:4;background:var(--panel);
  border:1px solid var(--edge);border-radius:4px;padding:12px 13px}
.ledger .big{font-family:"IBM Plex Mono",monospace;font-size:21px;font-weight:600;letter-spacing:-.02em}
.ledger .sub{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--dim);margin-bottom:11px}
.lrow{display:flex;justify-content:space-between;gap:9px;font-family:"IBM Plex Mono",monospace;
  font-size:10.5px;padding:3px 0;color:var(--ink2)}
.lrow b{color:var(--ink);font-weight:500;font-variant-numeric:tabular-nums}
.lhead{font-family:"IBM Plex Mono",monospace;font-size:9px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--dim);margin:11px 0 4px;padding-top:9px;border-top:1px solid var(--edge)}
.warn{font-size:10px;color:var(--dim);line-height:1.45;margin-top:9px;padding-top:8px;
  border-top:1px solid var(--edge)}

/* ---------- roster ---------- */
.roster{position:fixed;left:16px;top:62px;width:186px;z-index:4;background:var(--panel);
  border:1px solid var(--edge);border-radius:4px;padding:11px 12px;max-height:calc(100vh - 190px);overflow-y:auto}
.rhead{font-family:"IBM Plex Mono",monospace;font-size:9px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--dim);margin:9px 0 4px}
.rhead:first-child{margin-top:0}
.rseat{display:flex;justify-content:space-between;gap:6px;font-family:"IBM Plex Mono",monospace;
  font-size:10px;padding:2px 5px;border-radius:2px;color:var(--dim)}
.rseat.logged{color:var(--ink2)}
.rseat.hot{background:var(--amber-dim);color:var(--amber)}
.rseat i{font-style:normal;opacity:.6;font-size:9px}

/* ---------- detail ---------- */
.detail{position:fixed;right:16px;bottom:96px;width:242px;z-index:4;background:var(--panel);
  border:1px solid var(--edge);border-radius:4px;padding:12px 13px}
.detail .who{font-family:"IBM Plex Mono",monospace;font-size:13px;font-weight:600;letter-spacing:-.01em}
.detail .said{font-size:12px;color:var(--ink2);margin:7px 0 10px;line-height:1.5;
  max-height:112px;overflow-y:auto}
.pill{display:inline-block;font-family:"IBM Plex Mono",monospace;font-size:9px;padding:1px 6px;
  border-radius:2px;letter-spacing:.04em;margin-bottom:7px}

/* ---------- timeline ---------- */
.strip{position:fixed;left:16px;right:16px;bottom:16px;height:64px;z-index:4;background:var(--panel);
  border:1px solid var(--edge);border-radius:4px;display:flex;align-items:center;gap:14px;padding:0 15px}
.strip .lbl{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--dim);white-space:nowrap}
.track{position:relative;flex:1;height:30px}
.track svg{position:absolute;inset:0;width:100%;height:100%}

canvas{position:fixed;inset:0;z-index:0}
svg#stage{position:fixed;inset:0;width:100%;height:100%;z-index:1}
.hint{position:fixed;left:50%;transform:translateX(-50%);bottom:22px;z-index:6;pointer-events:none;
  font-family:"IBM Plex Mono",monospace;font-size:9.5px;color:var(--dim);opacity:.55}
</style></head><body>

<canvas id="stars"></canvas>
<svg id="stage"><g id="scene"></g></svg>

<div class="top">
  <span class="brand">One Brain</span>
  <span class="meta" id="live"><span class="pulse"></span>connecting</span>
  <select id="sess"></select>
  <span class="spacer"></span>
  <span class="meta" id="hdr">—</span>
</div>

<div class="roster" id="roster"></div>

<div class="ledger" id="ledger"></div>

<div class="detail" id="detail" hidden></div>

<div class="strip">
  <span class="lbl" id="t0">—</span>
  <div class="track"><svg id="tl"></svg></div>
  <span class="lbl" id="t1">—</span>
</div>

<div class="hint">drag to pan · scroll to zoom · click a node</div>

<script>
var NS="http://www.w3.org/2000/svg",S=null,sel=null,misses=0,picked=null;
var view={x:0,y:0,k:1},placed=false;

function esc(s){return (s||"").replace(/[<>&"]/g,function(c){
  return {"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c]})}
function el(n,a){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);return e}
function ms(t){var d=new Date(t);return isNaN(d)?0:d.getTime()}
function hhmm(t){var d=new Date(t);return isNaN(d)?"":d.toTimeString().slice(0,5)}
function nfmt(n){return n>=1e6?(n/1e6).toFixed(2)+"M":n>=1e3?(n/1e3).toFixed(1)+"k":String(n)}
function levelOf(n){
  if(["cto","cpo","cxo","analyst"].indexOf(n)>=0)return "company";
  if(["pm","devops","content-manager"].indexOf(n)>=0)return "product";
  if(n==="po"||n==="qa"||n.indexOf("team-lead")===0)return "project";
  return "developer"}
var HUE={company:"var(--teal)",product:"var(--green)",project:"var(--amber)",developer:"var(--violet)"};

/* starfield — drawn once, cheap, sets the ground the nodes sit on */
(function(){
  var c=document.getElementById("stars"),x=c.getContext("2d");
  function paint(){
    c.width=innerWidth;c.height=innerHeight;
    x.fillStyle="#0B0F0E";x.fillRect(0,0,c.width,c.height);
    for(var i=0;i<190;i++){
      var r=Math.random()*1.1+.2;
      x.globalAlpha=Math.random()*.34+.05;
      x.fillStyle=i%9===0?"#5FA8AE":"#7E8C86";
      x.beginPath();x.arc(Math.random()*c.width,Math.random()*c.height,r,0,7);x.fill();
    }
    x.globalAlpha=1;
  }
  paint(); addEventListener("resize",function(){paint();place(true)});
})();

function hex(cx,cy,r){
  var p=[];
  for(var i=0;i<6;i++){var a=Math.PI/180*(60*i-30);
    p.push((cx+r*Math.cos(a)).toFixed(1)+","+(cy+r*Math.sin(a)).toFixed(1))}
  return p.join(" ");
}
function apply(){document.getElementById("scene").setAttribute("transform",
  "translate("+view.x+","+view.y+") scale("+view.k+")")}

/* ---------- the constellation ---------- */
function place(keep){
  var scene=document.getElementById("scene");
  while(scene.firstChild)scene.removeChild(scene.firstChild);
  if(!S||!S.runs)return;
  var TOP=54, BOT=96, band=innerHeight-TOP-BOT;
  var runs=S.runs, cx=innerWidth/2, cy=TOP+band/2;

  var defs=el("defs",{});
  ["teal","green","amber","violet"].forEach(function(n){
    var f=el("filter",{id:"g-"+n,x:"-60%",y:"-60%",width:"220%",height:"220%"});
    f.appendChild(el("feGaussianBlur",{stdDeviation:5,result:"b"}));
    var m=el("feMerge",{});m.appendChild(el("feMergeNode",{in:"b"}));
    m.appendChild(el("feMergeNode",{in:"SourceGraphic"}));f.appendChild(m);defs.appendChild(f);
  });
  scene.appendChild(defs);

  /* the Listener's own tool calls — short tethers, they belong to it and to nothing else */
  var recent=(S.events||[]).filter(function(e){return e.kind==="tool"}).slice(-14);
  recent.forEach(function(e,i){
    var a=Math.PI*2*(i/recent.length)+.35, r=118+((i%3)*15);
    var tx=cx+Math.cos(a)*r, ty=cy+Math.sin(a)*r;
    scene.appendChild(el("line",{x1:cx,y1:cy,x2:tx,y2:ty,stroke:"var(--edge)","stroke-width":1}));
    scene.appendChild(el("circle",{cx:tx,cy:ty,r:2.4,fill:"var(--dim)"}));
    var t=el("text",{x:tx+6,y:ty+3,fill:"var(--dim)","font-family":"IBM Plex Mono, monospace","font-size":8.5});
    t.textContent=e.tool; scene.appendChild(t);
  });

  /* agents on a ring, clockwise in dispatch order */
  var R=Math.max(150,Math.min(cx-190, band/2-58));
  runs.forEach(function(r,i){
    var a=Math.PI*2*(i/runs.length)-Math.PI/2;
    var nx=cx+Math.cos(a)*R, ny=cy+Math.sin(a)*R;
    var lv=levelOf(r.seat), hue=HUE[lv];
    var open=!r.end;

    // tether, bowed so crossings read as separate lines
    var mx=(cx+nx)/2+Math.cos(a+Math.PI/2)*34, my=(cy+ny)/2+Math.sin(a+Math.PI/2)*34;
    scene.appendChild(el("path",{d:"M"+cx+","+cy+" Q"+mx+","+my+" "+nx+","+ny,
      fill:"none",stroke:open?"var(--amber)":hue,"stroke-width":sel===r.instance?2:1,
      "stroke-opacity":sel===r.instance?.95:.4,"stroke-dasharray":open?"4 4":""}));

    var g=el("g",{}); g.style.cursor="pointer";
    // duration ring: how long this seat held the floor
    if(r.secs!=null){
      var frac=Math.min(1,r.secs/600), rr=32;
      var end=-Math.PI/2+Math.PI*2*frac;
      var lg=frac>.5?1:0;
      g.appendChild(el("path",{d:"M"+cx0(nx,rr)+","+(ny-rr)+" A"+rr+","+rr+" 0 "+lg+" 1 "+
        (nx+rr*Math.cos(end))+","+(ny+rr*Math.sin(end)),
        fill:"none",stroke:hue,"stroke-width":2.5,"stroke-linecap":"round","stroke-opacity":.85}));
    }
    g.appendChild(el("polygon",{points:hex(nx,ny,25),fill:"var(--deep)",stroke:hue,
      "stroke-width":sel===r.instance?2.2:1.4,filter:"url(#g-"+hueName(lv)+")"}));
    if(open) g.appendChild(el("circle",{cx:nx,cy:ny,r:4,fill:"var(--amber)"}));

    var nm=el("text",{x:nx,y:ny+46,"text-anchor":"middle",fill:"var(--ink)",
      "font-family":"IBM Plex Mono, monospace","font-size":10.5,"font-weight":500});
    nm.textContent=r.seat; g.appendChild(nm);
    var sc=el("text",{x:nx,y:ny+59,"text-anchor":"middle",fill:"var(--dim)",
      "font-family":"IBM Plex Mono, monospace","font-size":9});
    sc.textContent=(r.secs!=null?r.secs+"s":"open")+(r.inner?"  ·  "+r.inner.tool_total+" tools":"");
    g.appendChild(sc);
    // a second, inner arc: how much work happened inside, against the busiest run
    if(r.inner && r.inner.tool_total){
      var mx=Math.max.apply(null,(S.runs||[]).map(function(z){return z.inner?z.inner.tool_total:0}))||1;
      var f2=Math.min(1,r.inner.tool_total/mx), r2=20, e2=-Math.PI/2+Math.PI*2*f2;
      g.appendChild(el("path",{d:"M"+nx+","+(ny-r2)+" A"+r2+","+r2+" 0 "+(f2>.5?1:0)+" 1 "+
        (nx+r2*Math.cos(e2))+","+(ny+r2*Math.sin(e2)),
        fill:"none",stroke:hue,"stroke-width":1.5,"stroke-opacity":.45,"stroke-linecap":"round"}));
    }

    g.addEventListener("click",function(ev){ev.stopPropagation();sel=r.instance;detail(r);place(true)});
    scene.appendChild(g);
  });

  /* the Listener, at the centre, because everything actually does route through it */
  scene.appendChild(el("polygon",{points:hex(cx,cy,46),fill:"var(--deep)",stroke:"var(--teal)",
    "stroke-width":2,filter:"url(#g-teal)"}));
  scene.appendChild(el("polygon",{points:hex(cx,cy,33),fill:"none",stroke:"var(--teal)",
    "stroke-width":1,"stroke-opacity":.4}));
  var lt=el("text",{x:cx,y:cy+4,"text-anchor":"middle",fill:"var(--teal)",
    "font-family":"IBM Plex Mono, monospace","font-size":11,"font-weight":600});
  lt.textContent="listener"; scene.appendChild(lt);
  var lc=el("text",{x:cx,y:cy+68,"text-anchor":"middle",fill:"var(--dim)",
    "font-family":"IBM Plex Mono, monospace","font-size":9.5});
  lc.textContent=(S.tools||[]).reduce(function(a,t){return a+t[1]},0)+" tool calls";
  scene.appendChild(lc);

  if(!placed){placed=true;apply()}
}
function cx0(nx,rr){return nx}
function hueName(lv){return lv==="company"?"teal":lv==="product"?"green":lv==="project"?"amber":"violet"}

/* ---------- detail ---------- */
function detail(r){
  var d=document.getElementById("detail"), lv=levelOf(r.seat);
  var said=(S.events||[]).filter(function(e){return e.kind==="return"&&e.who===r.instance});
  d.hidden=false;
  d.innerHTML='<span class="pill" style="background:var(--panel);border:1px solid '+HUE[lv]+
    ';color:'+HUE[lv]+'">'+lv+'</span>'+
    '<div class="who">'+esc(r.seat)+'</div>'+
    '<div class="said">'+esc(r.desc||"—")+'</div>'+
    '<div class="lrow"><span>instance</span><b>'+esc(r.instance.slice(0,20))+'</b></div>'+
    '<div class="lrow"><span>held the floor</span><b>'+(r.secs!=null?r.secs+"s":"still open")+'</b></div>'+
    '<div class="lrow"><span>started</span><b>'+hhmm(r.start)+'</b></div>'+
    (r.inner?
      '<div class="lhead">what it did</div>'+
      '<div class="lrow"><span>tool calls</span><b>'+r.inner.tool_total+'</b></div>'+
      '<div class="lrow"><span>turns</span><b>'+r.inner.rows+'</b></div>'+
      '<div class="lrow"><span>output</span><b>'+nfmt(r.inner.out)+'</b></div>'+
      '<div class="lrow"><span>of which thinking</span><b>'+nfmt(r.inner.think)+'</b></div>'+
      '<div class="lrow"><span>cost</span><b>$'+r.inner.cost.toFixed(2)+'</b></div>'+
      '<div class="lhead">tools it ran</div>'+
      r.inner.tools.map(function(t){
        return '<div class="lrow"><span>'+esc(t[0])+'</span><b>'+t[1]+'</b></div>'}).join("")+
      (r.inner.files.length?'<div class="lhead">files it touched</div>'+
        r.inner.files.map(function(f){
          return '<div class="lrow"><span title="'+esc(f[0])+'">'+esc(f[0].split("/").pop())+
                 '</span><b>'+f[1]+'</b></div>'}).join(""):"")
      :'<div class="warn">No inner transcript found for this run.</div>')+
    (said.length?'<div class="lhead">what came back</div><div class="said">'+
      esc(said[said.length-1].text)+'</div>':'');
}

/* ---------- timeline ---------- */
function strip(){
  var sv=document.getElementById("tl");
  while(sv.firstChild)sv.removeChild(sv.firstChild);
  var ev=(S.events||[]).filter(function(e){return e.ts});
  if(!ev.length)return;
  var t0=ms(ev[0].ts), t1=ms(ev[ev.length-1].ts)||t0+1;
  var w=sv.clientWidth||900, h=30;
  document.getElementById("t0").textContent=hhmm(ev[0].ts);
  document.getElementById("t1").textContent=hhmm(ev[ev.length-1].ts);
  sv.appendChild(el("line",{x1:0,y1:h/2,x2:w,y2:h/2,stroke:"var(--edge)","stroke-width":1}));
  var C={prompt:"var(--ink)",dispatch:"var(--amber)",return:"var(--green)",
         message:"var(--teal)",tool:"var(--dim)"};
  ev.forEach(function(e){
    var x=t1===t0?0:(ms(e.ts)-t0)/(t1-t0)*w;
    if(e.kind==="tool"){
      sv.appendChild(el("rect",{x:x,y:h/2-2,width:1,height:4,fill:C.tool,"fill-opacity":.5}));
    }else{
      sv.appendChild(el("circle",{cx:x,cy:h/2,r:e.kind==="dispatch"?3.6:2.6,fill:C[e.kind]||C.tool}));
    }
  });
}

/* ---------- data ---------- */
function render(s){
  S=s;
  if(s.error){document.getElementById("hdr").textContent=s.error;return}
  document.getElementById("live").innerHTML='<span class="pulse'+(s.live?" on":"")+'"></span>'+
    (s.live?"live":"idle");
  var se=document.getElementById("sess");
  if(se.options.length!==s.sessions.length){
    se.innerHTML=s.sessions.map(function(x){return '<option value="'+x.id+'">'+(x.live?"● ":"")+
      x.id.slice(0,8)+'</option>'}).join(""); se.value=s.active;
  }
  var u=s.usage||{},woke=s.seats.filter(function(x){return x.dispatched>0}).length;
  document.getElementById("hdr").innerHTML='<b>'+s.runs.length+'</b> runs · <b>'+woke+
    '</b>/'+s.seats.length+' seats woken · <b>'+nfmt(u.out||0)+'</b> out';

  document.getElementById("ledger").innerHTML=
    '<div class="big">$'+(u.cost!=null?u.cost.toFixed(2):"—")+'</div>'+
    '<div class="sub">'+esc(u.model||"—")+' · '+(u.msgs||0)+' messages</div>'+
    '<div class="lrow"><span>output</span><b>'+nfmt(u.out||0)+'</b></div>'+
    '<div class="lrow"><span>of which thinking</span><b>'+nfmt(u.think||0)+'</b></div>'+
    '<div class="lrow"><span>input</span><b>'+nfmt(u["in"]||0)+'</b></div>'+
    '<div class="lhead">cache</div>'+
    '<div class="lrow"><span>read</span><b>'+nfmt(u.cache_read||0)+'</b></div>'+
    '<div class="lrow"><span>written</span><b>'+nfmt(u.cache_write||0)+'</b></div>'+
    '<div class="lhead">agents</div>'+
    '<div class="lrow"><span>runs with inner record</span><b>'+(s.inner_found||0)+'/'+s.runs.length+'</b></div>'+
    '<div class="lrow"><span>their tool calls</span><b>'+
      s.runs.reduce(function(a,r){return a+(r.inner?r.inner.tool_total:0)},0)+'</b></div>'+
    '<div class="lrow"><span>their output</span><b>'+
      nfmt(s.runs.reduce(function(a,r){return a+(r.inner?r.inner.out:0)},0))+'</b></div>'+
    '<div class="lrow"><span>their cost</span><b>$'+
      s.runs.reduce(function(a,r){return a+(r.inner?r.inner.cost:0)},0).toFixed(2)+'</b></div>'+
    '<div class="lhead">listener tools</div>'+
    (s.tools||[]).slice(0,6).map(function(t){
      return '<div class="lrow"><span>'+esc(t[0])+'</span><b>'+t[1]+'</b></div>'}).join("")+
    '<div class="warn">Cost covers input and output at the published Opus 5 rate. Cache is shown in '+
    'tokens and deliberately not priced — the rate depends on the TTL in use.</div>';

  var LV=[["company","Company"],["product","Product"],["project","Project"],["developer","Developers"]];
  document.getElementById("roster").innerHTML=LV.map(function(L){
    return '<div class="rhead">'+L[1]+'</div>'+s.seats.filter(function(x){return x.level===L[0]})
      .map(function(x){return '<div class="rseat'+(x.logged?" logged":"")+(x.dispatched>0?" hot":"")+
        '"><span>'+esc(x.name)+'</span>'+(x.dispatched>0?'<i>×'+x.dispatched+'</i>':
        '<i>'+esc(x.model.slice(0,4))+'</i>')+'</div>'}).join("")}).join("");

  place(true); strip();
}
function tick(){
  fetch("/api/state"+(picked?"?s="+picked:""))
    .then(function(r){return r.json()}).then(function(s){misses=0;render(s)})
    .catch(function(){if(++misses>=2)document.getElementById("live").innerHTML=
      '<span class="pulse"></span>server stopped'});
}
document.getElementById("sess").addEventListener("change",function(e){
  picked=e.target.value;sel=null;document.getElementById("detail").hidden=true;tick()});

/* pan + zoom */
var st=document.getElementById("stage"),dn=false,ox=0,oy=0;
st.addEventListener("mousedown",function(e){dn=true;ox=e.clientX-view.x;oy=e.clientY-view.y});
addEventListener("mouseup",function(){dn=false});
addEventListener("mousemove",function(e){if(dn){view.x=e.clientX-ox;view.y=e.clientY-oy;apply()}});
st.addEventListener("wheel",function(e){e.preventDefault();
  var f=e.deltaY<0?1.1:1/1.1,k=Math.min(2.6,Math.max(.35,view.k*f));
  view.x=e.clientX-(e.clientX-view.x)*(k/view.k);
  view.y=e.clientY-(e.clientY-view.y)*(k/view.k);view.k=k;apply()},{passive:false});
st.addEventListener("click",function(){sel=null;document.getElementById("detail").hidden=true;place(true)});

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
