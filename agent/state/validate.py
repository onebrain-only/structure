#!/usr/bin/env python3
"""Thebes Persistent State validator.

THIS IS NOT JSON SCHEMA. There is no jsonschema package installed and none is
added; these are executable Thebes rules. Record shapes are documented in
agent/state/README.md. Do not describe this as JSON Schema compliance.

WHAT IT CANNOT DO
  It cannot prove a valid-looking record went through store.py. Runtime files
  carry no external write ledger in Wave 4, so a careful manual edit is
  indistinguishable from a store.py write. The no-direct-edit rule is
  contractual, like the no-delegation rule. Stated here so nobody mistakes a
  green check for proof of provenance.

    python3 agent/state/validate.py --check
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(ROOT, "agent", "state")
RUNTIME = os.path.join(STATE, "runtime")
REGISTRY = os.path.join(STATE, "registry")
BINDINGS = os.path.join(ROOT, ".claude", "bindings")
SCHEMA_VERSIONS = {1}

CAPABILITIES = {"frontend", "backend", "qa", "content", "devops", "analyst",
                "ux-engineer", "product-designer", "po", "pm", "cto", "cpo", "cxo"}
ROUTING_STATUS = {"open", "routed", "resolved", "withdrawn"}
EXCEPTION_STATUS = {"open", "redirected", "resolved", "withdrawn"}
EXCEPTION_TYPES = {"scope", "acceptance", "work_definition", "technical_domain",
                   "product", "experience", "blocker"}
PROVENANCE_ACTORS = re.compile(r"^(po|pm|qa|system-policy|system-maintenance|worker:[a-z0-9-]+)$")
JIRA_KEY = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")

# Wave 4 gates. Each names the wave that lifts it, so a later wave edits one line.
NULL_IN_WAVE_4 = ["canonical_lifecycle", "jira_operational_column", "review_context"]
PROFILE_NULL_IN_WAVE_4 = ["execution_complexity", "risk", "model", "reasoning_effort",
                          "validation_route", "parallelism", "completion_route"]
PROFILE_AUTHORABLE = ["required_capability", "work_effort"]
PROFILE_NEVER_BY_PO_OR_WORKER = ["model", "reasoning_effort", "validation_route"]
MAX_REF_LEN = 300      # identifier/reference fields; catches a pasted ticket body


def seats():
    if not os.path.isdir(BINDINGS):
        return set()
    return {f[:-4] for f in os.listdir(BINDINGS) if f.endswith(".yml")}


def registry():
    prods, projs = {}, {}
    pdir = os.path.join(REGISTRY, "products")
    if not os.path.isdir(pdir):
        return prods, projs
    for pid in sorted(os.listdir(pdir)):
        pf = os.path.join(pdir, pid, "product.json")
        if os.path.exists(pf):
            prods[pid] = json.load(open(pf, encoding="utf-8"))
        jdir = os.path.join(pdir, pid, "projects")
        if os.path.isdir(jdir):
            for fn in sorted(os.listdir(jdir)):
                if fn.endswith(".json"):
                    r = json.load(open(os.path.join(jdir, fn), encoding="utf-8"))
                    projs[(pid, r.get("project_id"))] = r
    return prods, projs


def _req(rec, fields, errs, where):
    for f in fields:
        if f not in rec:
            errs.append("%s: missing required field %r" % (where, f))


def _reflen(rec, fields, errs, where):
    for f in fields:
        v = rec.get(f)
        if isinstance(v, str) and len(v) > MAX_REF_LEN:
            errs.append("%s: %r is %d chars — reference fields hold identifiers, "
                        "not ticket bodies, acceptance criteria or governance text"
                        % (where, f, len(v)))


def validate_profile(prof, errs, where):
    if prof is None:
        return
    for f in PROFILE_NULL_IN_WAVE_4:
        if prof.get(f) is not None:
            errs.append("%s: execution_profile.%s must be null in Wave 4 "
                        "(policy that derives it becomes effective in Wave 6)" % (where, f))
    st = prof.get("profile_status")
    if st != "draft":
        errs.append("%s: profile_status must be 'draft' in Wave 4, got %r" % (where, st))
    cap = prof.get("required_capability")
    if cap is not None and cap not in CAPABILITIES:
        errs.append("%s: unknown required_capability %r" % (where, cap))
    we = prof.get("work_effort")
    if we is not None and (not isinstance(we, int) or we < 0):
        errs.append("%s: work_effort must be a non-negative integer (sittings)" % where)
    prov = prof.get("provenance") or {}
    if not isinstance(prov, dict):
        errs.append("%s: provenance must be an object keyed by field name" % where)
        return
    for field, entry in prov.items():
        if not isinstance(entry, dict) or "by" not in entry:
            errs.append("%s: provenance.%s needs an object with 'by'" % (where, field))
            continue
        by = entry["by"]
        if not PROVENANCE_ACTORS.match(str(by)):
            errs.append("%s: provenance.%s.by %r is not a recognised actor" % (where, field, by))
        if field in PROFILE_NEVER_BY_PO_OR_WORKER and (
                by == "po" or by == "pm" or str(by).startswith("worker:")):
            errs.append("%s: %s may not be authored by %s — system policy derives it"
                        % (where, field, by))
    for field in prov:
        if prof.get(field) is None:
            errs.append("%s: provenance.%s present but the field is unset" % (where, field))


def validate_record(kind, rec, prods=None, projs=None, seatset=None):
    errs = []
    where = "%s/%s" % (kind, rec.get("work_item_id") or rec.get("request_id")
                       or rec.get("exception_id") or rec.get("dependency_id") or "?")
    if rec.get("schema_version") not in SCHEMA_VERSIONS:
        errs.append("%s: unsupported schema_version %r" % (where, rec.get("schema_version")))
    if not isinstance(rec.get("revision"), int) or rec["revision"] < 1:
        errs.append("%s: revision must be a positive integer" % where)
    _req(rec, ["created_at", "updated_at"], errs, where)

    prods = prods if prods is not None else registry()[0]
    projs = projs if projs is not None else registry()[1]
    seatset = seatset if seatset is not None else seats()

    pid = rec.get("product_id")
    if pid and pid not in prods:
        errs.append("%s: product_id %r is not in the registry" % (where, pid))
    jid = rec.get("project_id")
    if jid and (pid, jid) not in projs:
        errs.append("%s: project_id %r is not a registered Project of %r" % (where, jid, pid))

    for f in ("raised_by", "return_to", "selected_seat", "created_by"):
        v = rec.get(f)
        if v and v not in seatset:
            errs.append("%s: %s %r is not a declared seat in .claude/bindings/" % (where, f, v))

    if kind == "task":
        _req(rec, ["work_item_id", "product_id", "project_id"], errs, where)
        if rec.get("work_item_id") and not JIRA_KEY.match(rec["work_item_id"]):
            errs.append("%s: work_item_id must be a Jira key" % where)
        for f in NULL_IN_WAVE_4:
            if rec.get(f) is not None:
                errs.append("%s: %s must be null in Wave 4 (Wave 5 owns lifecycle)" % (where, f))
        ev = rec.get("executor_evidence")
        if ev is None:
            ev = []
        if not isinstance(ev, list):
            errs.append("%s: executor_evidence must be a list — it represents evidence, "
                        "not a claim, and may be empty or conflicting" % where)
        else:
            seen = set()
            for o in ev:
                if not isinstance(o, dict) or "seat_id" not in o:
                    errs.append("%s: executor_evidence entry needs seat_id" % where); continue
                if o["seat_id"] not in seatset:
                    errs.append("%s: executor_evidence seat %r is not declared" % (where, o["seat_id"]))
                key = (o.get("seat_id"), o.get("evidence_ref"), o.get("evidenced_at"))
                if key in seen:
                    errs.append("%s: duplicate identical executor_evidence entry" % where)
                seen.add(key)
                _reflen(o, ["evidence_ref"], errs, where)
        validate_profile(rec.get("execution_profile"), errs, where)

    elif kind == "routing":
        _req(rec, ["request_id", "originating_work_item", "required_capability",
                   "raised_by", "return_to", "status"], errs, where)
        if rec.get("required_capability") not in CAPABILITIES:
            errs.append("%s: unknown required_capability %r" % (where, rec.get("required_capability")))
        if rec.get("status") not in ROUTING_STATUS:
            errs.append("%s: unknown status %r" % (where, rec.get("status")))
        _reflen(rec, ["discovered_scope", "dependency_ref", "selection_evidence"], errs, where)

    elif kind == "exception":
        _req(rec, ["exception_id", "originating_work_item", "raised_by", "return_to",
                   "exception_type", "status"], errs, where)
        if rec.get("exception_type") not in EXCEPTION_TYPES:
            errs.append("%s: unknown exception_type %r" % (where, rec.get("exception_type")))
        if rec.get("status") not in EXCEPTION_STATUS:
            errs.append("%s: unknown status %r" % (where, rec.get("status")))
        rc = rec.get("redirect_count", 0)
        if not isinstance(rc, int) or rc < 0 or rc > 1:
            errs.append("%s: redirect_count must be 0 or 1 — the Dispatcher redirects once "
                        "and exits; a second redirect is a relay chain" % where)
        auth = rec.get("decision_authority")
        if auth and auth not in seatset:
            errs.append("%s: decision_authority %r is not a declared seat" % (where, auth))
        _reflen(rec, ["question", "resolution_ref"], errs, where)

    elif kind == "dependency":
        _req(rec, ["dependency_id", "product_id", "source_work_item", "target_work_item",
                   "relation", "completion_condition"], errs, where)
        if rec.get("relation") != "BLOCKS":
            errs.append("%s: relation must be BLOCKS — IS_BLOCKED_BY is a derived query, "
                        "never a second record" % where)
        if rec.get("completion_condition") != "DONE":
            errs.append("%s: completion_condition must be DONE in Wave 4" % where)
        for f in ("state", "satisfied", "active", "resolved"):
            if f in rec:
                errs.append("%s: %r is not stored — satisfaction is derived from canonical "
                            "lifecycle (Wave 5), never mirrored here" % (where, f))
        for f in ("source_work_item", "target_work_item"):
            if rec.get(f) and not JIRA_KEY.match(rec[f]):
                errs.append("%s: %s must be a Jira key" % (where, f))
        for f, p in (("source_project_id", rec.get("product_id")),
                     ("target_project_id", rec.get("product_id"))):
            v = rec.get(f)
            if v and (p, v) not in projs:
                errs.append("%s: %s %r is not a registered Project of %r" % (where, f, v, p))
    return errs


def check_graph_addition(edges, new):
    """Integrity of the whole graph, checked under the Product graph lock."""
    s, t = new.get("source_work_item"), new.get("target_work_item")
    if s == t:
        return "self-edge %s BLOCKS itself" % s
    if new.get("source_project_id") and new.get("target_project_id"):
        pass  # both belong to new['product_id']; cross-Product is structurally impossible here
    for e in edges:
        if e.get("source_work_item") == s and e.get("target_work_item") == t:
            return "duplicate active edge %s BLOCKS %s (%s)" % (s, t, e.get("dependency_id"))
    adj = {}
    for e in edges:
        adj.setdefault(e["source_work_item"], []).append(e["target_work_item"])
    adj.setdefault(s, []).append(t)
    colour = {}
    def cyclic(n):
        colour[n] = 1
        for m in adj.get(n, []):
            if colour.get(m) == 1:
                return True
            if colour.get(m) is None and cyclic(m):
                return True
        colour[n] = 2
        return False
    for n in list(adj):
        if colour.get(n) is None and cyclic(n):
            return "would create a dependency cycle involving %s" % s
    return None


def check(runtime=None):
    runtime = runtime or RUNTIME
    errs = []
    prods, projs = registry()
    if "dabbler" not in prods:
        errs.append("registry: product 'dabbler' is missing")
    seatset = seats()
    for pid, jid in projs:
        po = projs[(pid, jid)].get("current_po_seat_id")
        if po and po not in seatset:
            errs.append("registry: project %s/%s binds PO seat %r which is not declared"
                        % (pid, jid, po))
    kinds = {"task": "tasks", "routing": "routing",
             "exception": "exceptions", "dependency": "dependencies"}
    seen_ids = {}
    edges = []
    for kind, sub in kinds.items():
        d = os.path.join(runtime, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            p = os.path.join(d, fn)
            try:
                rec = json.load(open(p, encoding="utf-8"))
            except Exception as e:
                errs.append("%s: invalid JSON (%s)" % (p, e)); continue
            if isinstance(rec, list):
                errs.append("%s: a record file holds ONE record, never an array — "
                            "a single aggregate file would serialise every write" % p); continue
            idf = {"task": "work_item_id", "routing": "request_id",
                   "exception": "exception_id", "dependency": "dependency_id"}[kind]
            rid = rec.get(idf)
            if rid != fn[:-5]:
                errs.append("%s: filename does not match %s %r" % (p, idf, rid))
            if (kind, rid) in seen_ids:
                errs.append("%s: duplicate id %r" % (p, rid))
            seen_ids[(kind, rid)] = p
            errs += validate_record(kind, rec, prods, projs, seatset)
            if kind == "dependency" and not rec.get("retired_at"):
                edges.append(rec)
    built = []
    for e in edges:
        problem = check_graph_addition(built, e)
        if problem:
            errs.append("dependency graph: %s" % problem)
        else:
            built.append(e)
    return errs


if __name__ == "__main__":
    if "--check" not in sys.argv:
        print(__doc__.strip()); sys.exit(0)
    errs = check()
    if errs:
        for e in errs:
            print("FAIL  " + e)
        print("\n%d problem(s)" % len(errs)); sys.exit(1)
    print("ok      persistent state valid")
    sys.exit(0)
