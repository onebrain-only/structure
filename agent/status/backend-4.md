# agent/status/junior-frontend-3b.md

**Owner:** `junior-frontend-3b` (write) · all agents (read)

Append newest-first, in the FORMAT block of `agent/STATUS.md`. **`agent/WORKFLOWS.md` §1 rule 5:**
no task is complete until its entry is saved — a refusal, a diagnosis or a question answered
still gets one.

---

# LOG

_No entries yet._

## 2026-09-06 — KAN-141 (Min, backend-4): 3 zero-policy definer views measured

Pulled from Ready. Read-only on `wtncuzcskpigqpmnxwws`. No DDL, no migration applied (G-002).

All relations resolved via `to_regclass` — none missing (no T-055 repeat).
All function bodies taken from `pg_get_functiondef` on the live catalogue, not migration files.

| View | Backing fn | Mechanism for 0 | Verdict |
|---|---|---|---|
| `username_registry_public` | `list_active_usernames()` SECDEF | none — only `released_at is null`; `username_registry` has **0 rows** | **EMPTY TABLE — defect** |
| `v_potential_vibes_default` | `rpc_potential_vibes/6` SECDEF → `/7` | `spw.user_id <> p_me` with `p_me=auth.uid()`=NULL → NULL → all rows dropped. Base `v_sport_profiles_with_user` = **143 rows** | zero-by-mechanism, but incidental |
| `v_recreate_quickpicks` | `rpc_recreate_suggestions()` **INVOKER** → `v_recreate_candidates` | `WHERE rus.user_id = auth.uid()` (real per-user gate) AND `reuse_user_stats`/`reuse_global_stats` both **0 rows** | gate present in definition, unexercisable today |

Probes demonstrated, not assumed:
- positive control `rpc_potential_vibes(...,<real uid>)` → **20 rows** (path executes)
- `set local role anon; select count(*) from v_potential_vibes_default` → **0**
- same as anon on the other two → **0**, **0**

Anon reachability: all three carry `anon=r` in `relacl`. Already in the T-002 allowlist fixture
(`scripts/ci/check_anon_allowlist_test.sh:20,25,28`) — known and accepted, not a new exposure.
`v_sport_profiles_with_user` exposes `auth.users.email` but its acl is `anon=xtm` (no `r`) —
anon cannot read it directly. KAN-67 holding.

Findings raised to `po`; did not fold the defect into this ticket.
Ticket left in To Do — the empty-table result is a stop-and-ask per brief.
