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

    return {"events": events, "dispatches": dispatches, "messages": messages,
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
--signal:#B4560B;--signalsoft:#F6E4D2;--live:#1F6F4A;--livesoft:#DCEDE3}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--paper:#111513;--raise:#181E1B;
--ink:#E7ECE7;--ink2:#B4BDB8;--muted:#828E88;--rule:#2B332F;--soft:#212824;--struct:#7FAAAE;
--structsoft:#1C2626;--signal:#E5883C;--signalsoft:#2B1E11;--live:#5FBE8C;--livesoft:#14241B}}
:root[data-theme=dark]{--paper:#111513;--raise:#181E1B;--ink:#E7ECE7;--ink2:#B4BDB8;--muted:#828E88;
--rule:#2B332F;--soft:#212824;--struct:#7FAAAE;--structsoft:#1C2626;--signal:#E5883C;
--signalsoft:#2B1E11;--live:#5FBE8C;--livesoft:#14241B}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 "IBM Plex Sans",system-ui,sans-serif;
-webkit-font-smoothing:antialiased}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
h1{font-family:"Bricolage Grotesque",system-ui,sans-serif;font-size:20px;font-weight:800;
letter-spacing:-.02em;margin:0}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.14em;
text-transform:uppercase;color:var(--muted)}

/* top bar */
.bar{display:flex;align-items:center;gap:18px;flex-wrap:wrap;padding:12px 20px;
border-bottom:1px solid var(--rule);background:var(--raise);position:sticky;top:0;z-index:10}
.dot{width:8px;height:8px;border-radius:50%;background:var(--muted);display:inline-block;margin-right:7px}
.dot.on{background:var(--live);box-shadow:0 0 0 3px var(--livesoft)}
@media(prefers-reduced-motion:no-preference){.dot.on{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}
.counts{display:flex;gap:0;margin-left:auto;border:1px solid var(--rule);border-radius:2px;overflow:hidden}
.counts div{padding:5px 13px;border-right:1px solid var(--rule)}
.counts div:last-child{border-right:0}
.counts b{font-family:"IBM Plex Mono",monospace;font-size:15px;font-variant-numeric:tabular-nums;display:block;line-height:1.2}
.counts span{font-size:10px;color:var(--muted)}
select{font-family:"IBM Plex Mono",monospace;font-size:11px;padding:5px 8px;background:var(--paper);
color:var(--ink);border:1px solid var(--rule);border-radius:2px}

/* layout */
.grid{display:grid;grid-template-columns:250px minmax(0,1fr) 330px;gap:0;height:calc(100vh - 53px)}
@media(max-width:1100px){.grid{grid-template-columns:1fr;height:auto}}
.pane{overflow-y:auto;padding:16px 18px}
.pane+.pane{border-left:1px solid var(--rule)}
.pane h2{font-family:"Bricolage Grotesque",sans-serif;font-size:13px;font-weight:600;margin:0 0 10px;
letter-spacing:-.01em}

/* roster */
.lvl{margin-bottom:14px}
.lvl>.eyebrow{display:block;margin-bottom:6px;color:var(--struct)}
.seat{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:4px 8px;
border:1px solid transparent;border-radius:2px;font-family:"IBM Plex Mono",monospace;font-size:11px}
.seat.logged{color:var(--ink2)}
.seat:not(.logged){color:var(--muted)}
.seat.hot{background:var(--signalsoft);border-color:var(--signal);color:var(--signal);font-weight:600}
.seat .tier{font-size:9.5px;opacity:.7}
.seat .n{background:var(--signal);color:#fff;border-radius:8px;padding:0 5px;font-size:9.5px;font-weight:600}

/* flow spine */
.flow{position:relative;padding-left:26px}
.flow:before{content:"";position:absolute;left:8px;top:6px;bottom:6px;width:2px;background:var(--rule)}
.node{position:relative;margin-bottom:10px}
.node:before{content:"";position:absolute;left:-22px;top:9px;width:9px;height:9px;border-radius:50%;
background:var(--paper);border:2px solid var(--rule)}
.node.dispatch:before{border-color:var(--signal);background:var(--signal)}
.node.message:before{border-color:var(--struct);background:var(--struct)}
.node.prompt:before{border-color:var(--ink);background:var(--ink)}
.node.return:before{border-color:var(--live);background:var(--livesoft)}
.card{border:1px solid var(--rule);border-radius:2px;background:var(--raise);padding:9px 12px}
.node.dispatch .card{border-left:3px solid var(--signal)}
.node.message .card{border-left:3px solid var(--struct)}
.node.prompt .card{border-left:3px solid var(--ink);background:var(--soft)}
.node.return .card{border-left:3px solid var(--live)}
.node.return .who{color:var(--live)}
.card .who{font-family:"IBM Plex Mono",monospace;font-size:11.5px;font-weight:600;letter-spacing:-.01em}
.node.dispatch .who{color:var(--signal)}
.node.message .who{color:var(--struct)}
.card .t{font-size:12.5px;color:var(--ink2);margin-top:3px}
.card .meta{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--muted);margin-top:4px}
.runs{display:flex;flex-wrap:wrap;gap:4px;margin-top:7px}
.chip{font-family:"IBM Plex Mono",monospace;font-size:10px;padding:1px 6px;border:1px solid var(--rule);
border-radius:2px;color:var(--muted);white-space:nowrap}

/* right rail */
.row{display:flex;justify-content:space-between;gap:10px;padding:4px 0;border-bottom:1px solid var(--soft);
font-family:"IBM Plex Mono",monospace;font-size:11px}
.row:last-child{border-bottom:0}
.row span{color:var(--muted);font-variant-numeric:tabular-nums}
.row b{font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.barfill{height:3px;background:var(--structsoft);border-radius:2px;overflow:hidden;margin-top:3px}
.barfill i{display:block;height:100%;background:var(--struct)}
.empty{color:var(--muted);font-size:13px;padding:20px 0}
</style></head><body>

<div class="bar">
  <h1>One Brain</h1>
  <span class="eyebrow" id="livelabel"><span class="dot" id="dot"></span>connecting</span>
  <select id="sess"></select>
  <div class="counts">
    <div><b id="cTurns">0</b><span>turns</span></div>
    <div><b id="cDisp">0</b><span>dispatches</span></div>
    <div><b id="cTools">0</b><span>tool calls</span></div>
    <div><b id="cSeats">0</b><span>seats woken</span></div>
  </div>
</div>

<div class="grid">
  <div class="pane"><h2>The roster</h2><div id="roster"></div></div>
  <div class="pane"><h2>Flow</h2><div class="flow" id="flow"></div></div>
  <div class="pane">
    <h2>Tools</h2><div id="tools"></div>
    <h2 style="margin-top:20px">Files under attention</h2><div id="files"></div>
  </div>
</div>

<script>
var LEVELS=[["company","Company"],["product","Product"],["project","Project"],["developer","Developers"]];
var picked=null, lastCount=-1;

function esc(s){return (s||"").replace(/[<>&]/g,function(c){return {"<":"&lt;",">":"&gt;","&":"&amp;"}[c]})}
function clock(ts){ if(!ts) return ""; var d=new Date(ts);
  return isNaN(d)?"":d.toTimeString().slice(0,5) }

function render(s){
  if(s.error){ document.getElementById("flow").innerHTML='<p class="empty">'+esc(s.error)+'</p>'; return }

  document.getElementById("dot").className = "dot"+(s.live?" on":"");
  document.getElementById("livelabel").innerHTML =
    '<span class="dot'+(s.live?" on":"")+'"></span>'+(s.live?"live":"idle");

  var sel=document.getElementById("sess");
  if(sel.options.length!==s.sessions.length){
    sel.innerHTML=s.sessions.map(function(x){
      return '<option value="'+x.id+'">'+(x.live?"● ":"")+x.id.slice(0,8)+
             "  ·  "+(x.size/1048576).toFixed(1)+"MB</option>" }).join("");
    sel.value=s.active;
  }

  var disp=s.dispatches.length, toolN=s.tools.reduce(function(a,t){return a+t[1]},0);
  document.getElementById("cTurns").textContent=s.turns;
  document.getElementById("cDisp").textContent=disp;
  document.getElementById("cTools").textContent=toolN;
  document.getElementById("cSeats").textContent=s.seats.filter(function(x){return x.dispatched>0}).length;

  // roster
  document.getElementById("roster").innerHTML = LEVELS.map(function(L){
    var rows=s.seats.filter(function(x){return x.level===L[0]}).map(function(x){
      var cls="seat"+(x.logged?" logged":"")+(x.dispatched>0?" hot":"");
      return '<div class="'+cls+'"><span>'+esc(x.name)+'</span>'+
        (x.dispatched>0?'<span class="n">'+x.dispatched+'</span>'
                       :'<span class="tier">'+esc(x.model)+'·'+esc(x.effort)+'</span>')+'</div>'
    }).join("");
    return '<div class="lvl"><span class="eyebrow">'+L[1]+'</span>'+rows+'</div>'
  }).join("");

  // flow — prompts, dispatches and messages on one spine, with tool runs folded in
  var out=[], pend=[];
  function flush(){
    if(!pend.length) return "";
    var h='<div class="runs">'+pend.slice(0,26).map(function(t){
      return '<span class="chip">'+esc(t)+'</span>' }).join("")+
      (pend.length>26?'<span class="chip">+'+(pend.length-26)+'</span>':"")+'</div>';
    pend=[]; return h;
  }
  s.events.forEach(function(e){
    if(e.kind==="tool"){ pend.push(e.tool); return }
    if(e.kind==="say"){ return }
    var runs=flush();
    if(e.kind==="prompt"){
      out.push('<div class="node prompt"><div class="card"><div class="who">CEO</div>'+
        '<div class="t">'+esc(e.text.slice(0,180))+'</div>'+
        '<div class="meta">'+clock(e.ts)+'</div>'+runs+'</div></div>');
    } else if(e.kind==="dispatch"){
      out.push('<div class="node dispatch"><div class="card">'+
        '<div class="who">▸ '+esc(e.seat)+'</div>'+
        '<div class="t">'+esc(e.text)+'</div>'+
        '<div class="meta">'+esc(e.instance)+' · '+clock(e.ts)+'</div>'+runs+'</div></div>');
    } else if(e.kind==="return"){
      out.push('<div class="node return"><div class="card">'+
        '<div class="who">◂ '+esc(e.who)+'</div>'+
        '<div class="t">'+esc(e.text)+'</div>'+
        '<div class="meta">returned · '+clock(e.ts)+'</div>'+runs+'</div></div>');
    } else if(e.kind==="message"){
      out.push('<div class="node message"><div class="card">'+
        '<div class="who">→ '+esc(e.to)+'</div>'+
        '<div class="t">'+esc(e.text)+'</div>'+
        '<div class="meta">'+clock(e.ts)+'</div>'+runs+'</div></div>');
    }
  });
  var tail=flush();
  if(tail) out.push('<div class="node"><div class="card"><div class="meta">still working</div>'+tail+'</div></div>');
  document.getElementById("flow").innerHTML = out.join("") || '<p class="empty">No activity yet.</p>';

  var max=s.tools.length?s.tools[0][1]:1;
  document.getElementById("tools").innerHTML=s.tools.map(function(t){
    return '<div class="row"><b>'+esc(t[0])+'</b><span>'+t[1]+'</span></div>'+
           '<div class="barfill"><i style="width:'+Math.round(t[1]/max*100)+'%"></i></div>' }).join("");

  document.getElementById("files").innerHTML=s.files.length?s.files.map(function(f){
    return '<div class="row"><b title="'+esc(f[0])+'">'+esc(f[0].split("/").pop())+'</b><span>'+f[1]+'</span></div>'
  }).join(""):'<p class="empty">Nothing yet.</p>';

  // keep the newest work in view while live
  if(s.live && s.events.length!==lastCount){
    var p=document.querySelectorAll(".pane")[1];
    p.scrollTop=p.scrollHeight;
  }
  lastCount=s.events.length;
}

var misses=0;
function tick(){
  fetch("/api/state"+(picked?"?s="+picked:""))
    .then(function(r){return r.json()})
    .then(function(s){ misses=0; render(s) })
    .catch(function(){ if(++misses>=2) document.getElementById("livelabel").innerHTML=
      '<span class="dot"></span>server stopped' });
}
document.getElementById("sess").addEventListener("change",function(e){
  picked=e.target.value; lastCount=-1; tick();
});
tick(); setInterval(tick, 2000);
</script></body></html>"""


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
