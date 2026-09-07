# agent/state — Persistent Thebes State

**Added Wave 4, 2026-09-07.** An independent system layer. It is **not an agent, not a seat,
not a Role, not Orchestrator memory and not Main Session memory** — the Main Session reads and
writes it operationally, and will hand that to the Orchestrator in Wave 6.

## What this layer IS

- Orchestration state — what is currently being coordinated.
- Current execution context.
- Execution Profile persistence.
- Routing context — the durable form of what Wave 3 carried in prompt text.
- Exception context — likewise.
- Product dependency relationships.

## What this layer IS NOT

Jira · a second ticket database · a copy of acceptance criteria · Git architecture history ·
`dabbler-docs` governance · a Role contract · Role Learning · telemetry · agent memory ·
Main Session memory · Orchestrator memory.

## The non-duplication rule

**Persistent State stores identifiers, references, minimum orchestration facts, timestamps and
provenance. It never stores canonical prose owned elsewhere.**

| GOOD | BAD |
|---|---|
| `"work_item_id": "KAN-137"` | the ticket's description |
| `"decision_ref": "G-028"` + source + governance baseline | `G-028`'s text |
| `"project_id": "app"` | what the App project is |
| `"evidence_ref": "jira-comment:10453"` | the comment body |
| `"required_capability": "backend"` | the Role's behaviour |

The validator enforces a length ceiling on reference fields, which catches a pasted ticket body
or a rule copied in. **A second copy of a canonical fact is a second authority** — the defect
Wave 1 spent a whole closure removing from `CONTRACT.md`.

## Tracked vs runtime — the hybrid boundary

**If System Maintenance authors it, it is tracked. If a seat writes it during execution, it is
local-durable and git-ignored.**

| Tracked | Local-durable, git-ignored |
|---|---|
| this README · `store.py` · `validate.py` | `runtime/tasks/` · `runtime/routing/` |
| `registry/` — Company, Product, Projects | `runtime/exceptions/` · `runtime/dependencies/` |
| | `runtime/.locks/` |

Tracking mutable records would keep the working tree dirty during normal Product execution, let
unrelated product commits sweep runtime state, and make Git responsible for a live orchestration
database. `.gitignore` carries one rule: `/agent/state/runtime/`.

## Workspace-local — NOT global truth

**Runtime state is durable across sessions that share this working copy. It is not shared
across different clones, worktrees or cloud checkouts.**

`fcntl.flock` serialises processes on one filesystem. It is **not distributed locking**, and
none is invented here. A different checkout has entirely independent runtime state — which is
safe precisely because runtime records are never committed, so there is nothing to merge or
diverge. **Never describe this state as global occupancy or global truth.** Compatibility debt;
revisited in Wave 6.

## Every operational write goes through `store.py`

`read` · `create` · `update` · `create_dependency`. **No DELETE** — records are retired or
withdrawn, never removed.

`update` requires `expected_revision`. **There is no force mode**, because an optional safety
check is an absent one.

**Why a utility and not direct file writes.** Read-modify-check-write across four syscalls is
not compare-and-swap: two writers can both read revision 5, both re-check 5, and both write 6,
the second silently destroying the first. `os.replace()` makes a write atomic for *readers*; it
does nothing to serialise *writers*. So the revision check and the write happen inside one
`flock` region.

**Dependency mutations take a Product graph lock**, not a per-edge lock. Per-edge locking cannot
protect a graph invariant: two sessions adding `X→Y` and `Y→X` under different locks each pass a
cycle check alone and together make a cycle.

**System Maintenance may edit this README, the tooling and `registry/` directly** — reviewed
configuration, not concurrent runtime writes.

**Honest limit:** `validate.py` **cannot prove a record went through `store.py`.** Runtime files
carry no write ledger, so a careful manual edit is indistinguishable from a store write. The
no-direct-edit rule is contractual, exactly like the no-delegation rule.

## Record shapes

Documented here; enforced by `validate.py`. **These are executable Thebes rules, not JSON
Schema** — no `jsonschema` package is installed and none is added. There are deliberately no
`*.schema.json` files, because formal-looking files that nothing reads are worse than none.

Every record carries `schema_version`, `revision`, `created_at`, `updated_at`.

**Task** — `runtime/tasks/<JIRA-KEY>.json`. `work_item_id` · `product_id` · `project_id` ·
`executor_evidence` (list) · `execution_profile` (object or null) · `canonical_lifecycle` ·
`jira_operational_column` · `review_context`.

**`executor_evidence` is evidence, not CLAIM.** A list of `{seat_id, evidence_ref,
evidenced_at}`. Zero entries = no evidenced executor. One unique seat = usable MODEL C evidence.
**Two or more unique seats = conflicting evidence, and routing must refuse** — not pick the
latest, lowest or first. **CLAIM does not exist**; Wave 6 adds a separate claim structure.

**Execution Profile** — embedded 1:1 in a task, or null. Only `required_capability` and
`work_effort` may be populated in Wave 4; every derived field stays null and `profile_status` is
`draft`. **Provenance is per field**, so the validator can accept `work_effort` authored by `po`
while rejecting `model` authored by `po` in the same record. **The binding's `model:` and
`effort:` remain the actual harness execution defaults** — nothing here controls execution yet.

**Routing request** — `runtime/routing/rr-<uuid4>.json`. **NOT A QUEUE.** Nothing claims from
it, nothing pulls from it, nothing orders it. `selected_seat` stays null unless MODEL C evidence
determines one, and an open request with no seat stays open indefinitely.

**Exception** — `runtime/exceptions/exc-<uuid4>.json`. `redirect_count` is 0 or 1; the validator
rejects 2, because a second redirect is the relay chain the architecture forbids. **Wave 4
persists the record; it does not route automatically.**

**Dependency** — `runtime/dependencies/dep-<uuid4>.json`. One canonical direction: `source
BLOCKS target`. `IS_BLOCKED_BY` is a **derived query, never a second record**. Cross-Project
inside one Product is legal; cross-Product is rejected. `completion_condition` is `DONE`, so a
prerequisite in review has not satisfied anything. **Satisfaction is derived, never stored** —
`state`/`active`/`resolved`/`satisfied` are rejected outright. `retired_at`/`retired_reason`
describe the *edge* being cancelled, not the prerequisite completing.

**Endpoints are Jira keys and do not require local task records.** A task record is created only
when there is genuine task-level state to hold — executor evidence or an execution profile.
**No stubs, no backfill.**

## Checks

```
python3 agent/state/validate.py --check
```

Exit 0 clean; non-zero names the path and the reason.
