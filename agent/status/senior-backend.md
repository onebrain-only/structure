# agent/status/senior-backend.md

**Owner:** `senior-backend` (write) · all agents (read)

Append newest-first, in the FORMAT block of `agent/STATUS.md`. **`agent/WORKFLOWS.md` §1 rule 5:**
no task is complete until its entry is saved — a refusal, a diagnosis or a question answered
still gets one.

---

# LOG

_No entries yet._

## 2026-09-06 — Skills audit of this seat (survey, `team-lead` dispatch)

**Did.** Read-only survey. No SQL run, no migration touched, no Supabase call of any kind.
Read `agent/roles/senior-backend.md` (98 lines), `ls agent/skills/` (74), `agent/skills/AVAILABLE.md`,
`Dabbler/dabbler-docs/CONTRACT.md` §3, and opened the bodies of nine candidate `SKILL.md` files.

**Touched.** This file only.

**Decided.**
- Two skills claimed as core to this seat: `supabase` (repo, 112 lines + `references/`) and
  `supabase-postgres-best-practices` (repo, 64 lines + **34** reference files, wired to zero seats today).
- One repo skill claimed with a carve-out: `diagnosing-bugs`, for the feedback-loop discipline
  applied to a SQL probe rather than a test.
- Rejected after opening: `backend-patterns` (Node/Express/Next.js REST, not Postgres),
  `security-review` (`process.env` / TS web-app checklist), `verification-quality`
  (`npx ruflo` CI catalogue for the claude-flow repo, not this product), `system-design`,
  `tdd`, `domain-modeling` for this seat. `ddia-systems` accepted as reference-only, not a routine.
- The six mobile-security skills `cto` claims are all client-side; only `network-security-check`
  even mentions Postgres/RLS. **None of them is mine.** The database-security gap is real and unfilled.
- **Conflict found and flagged, not resolved:** the repo `supabase` skill's "Making and Committing
  Schema Changes" section instructs the reader to change schema with `execute_sql` and to iterate
  live. For this seat that is a `CONTRACT.md` §3 / decision `019` violation — `cto` is the only seat
  that may apply. The skill is safe for this seat only with that section carved out. Raised to
  `team-lead`; not amended (skills are not this seat's write surface).

**Blocked.** Nothing. Survey answered in full; no follow-up owed by this seat.

## 2026-09-06 — KAN-128 capacity: this seat sizes its own authoring (`team-lead` dispatch)

**Did.** Read-only. No SQL run, no migration authored, no Supabase call of any kind — every
figure below comes from `grep`/`sed` over
`Dabbler/dabbler-code/supabase/migrations/20260829080500_baseline_schema.sql` (39,291 lines),
plus `Dabbler/dabbler-docs/DECISIONS.md` `T-049`, KAN-128 and its three comments (10554/10555/10558),
`agent/skills/capacity-to-date/SKILL.md` and `agent/skills/money-write-invariants/SKILL.md`.

**Touched.** This file only.

**Number.** **2 sittings on this seat**, plus **2 gates on other seats** (`po`'s AC-3 review;
`cto`'s apply under `G-002`). Ceiling **3 sittings** — 2 plus one rework cycle, because AC 3's
probes run against `cto`'s applied database and a failure there returns the work here. **No date
set** — the calendar mapping is `po`'s (`capacity-to-date` §2 input 4). I agree with
`team-lead-4`'s count and with where it put the checkpoint.

- **Sitting 1 — mechanical.** Read the five live definitions via
  `pg_get_functiondef(...::regproc)`; DDL (`ALTER COLUMN ref_id SET NOT NULL`, `UNIQUE
  (ref_type, ref_id, direction)` on `wallet_ledger`, partial `UNIQUE (payment_intent_id,
  entity_type, entry_type)` on `financial_ledger`, `T-049`'s table-comment correction);
  `CREATE OR REPLACE` on the four signature-stable functions covering **6 of 7** insert sites —
  `admin_cancel_payout:2211`, `request_payout:10200`, `settle_game:17154`,
  `trgfn_payment_to_ledger:19215/:19226/:19237`.
- **Checkpoint.** Migration file holds the constraints and 6 of 7 conflict clauses;
  `admin_wallet_adjust` untouched. Reviewable and abandonable — and **not applicable**, because
  `ref_id NOT NULL` breaks `admin_wallet_adjust:2982` until sitting 2 lands. That un-appliability
  is what makes it a checkpoint rather than a partial finish.
- **Sitting 2 — the judgement.** `admin_wallet_adjust` is **not** a `CREATE OR REPLACE`:
  adding `p_ref_id uuid` changes the argument list, which produces an **overload**, not a
  replacement. It needs `DROP FUNCTION public.admin_wallet_adjust(uuid, ledger_direction,
  numeric, text, jsonb)` — dropping the NULL-writing path rather than leaving it callable —
  then `CREATE`, then re-`GRANT` to `anon`/`authenticated`/`service_role` (baseline
  `:34693`–`:34695`), which the `DROP` removes silently. The judgement inside it: the new
  parameter carries **no** `DEFAULT gen_random_uuid()`, because a per-call mint is exactly the
  guarantee `T-049` refuses. Then AC-3's four probes and the `G-002` ticket comment.

**Decided / found — three corrections to the measured scope, each re-read at the line:**

1. **KAN-128 AC 1 is wrong about `SECURITY DEFINER`.** It says *"None of the five is
   `SECURITY DEFINER`"*, generalising from the one function it checked
   (`trgfn_payment_to_ledger:19163`, correctly `LANGUAGE plpgsql` only). **Four of five are:**
   `admin_cancel_payout:2183`, `admin_wallet_adjust:2975`, `request_payout:10168`,
   `settle_game:17080`. `CREATE OR REPLACE` drops it. Following the AC literally would demote
   four money RPCs to `SECURITY INVOKER` — a privilege regression on the only paths that write
   `payouts` and `wallet_ledger`, whose table comment (`:26940`) states *"Only SECURITY DEFINER
   engine functions insert rows."*
2. **AC 1's `search_path` string is wrong for the same four.** They carry
   `SET search_path TO 'public'` — **no `pg_temp`**. Only `trgfn_payment_to_ledger:19166`
   carries `'public', 'pg_temp'`. `T-044`/`CONVENTIONS.md` §6c says *restate what is there*;
   restating the AC's string would silently change four functions' resolution scope.
   **Mitigation, and why neither corrections adds a sitting:** I author from
   `pg_get_functiondef` on the live catalogue, which is immune to both errors. The AC still
   needs correcting so review does not fail correct work.
3. **`admin_wallet_adjust`'s signature change breaks zero callers.**
   `grep -rnEi "admin_wallet_adjust|settle_game|request_payout|admin_cancel_payout|admin_approve_payout" lib supabase/functions`
   returns **nothing**. No client coordination is owed.

**Confirmed as measured.** All five `CREATE OR REPLACE` lines and all seven insert lines match
the brief exactly. `admin_approve_payout:2138` is `UPDATE`-only (`:2155`–`:2157`) — not an insert
site. `payment_intents` has **zero** SQL writers; the only Dart use is a `.select()` read at
`lib/features/profile/services/data_export_service.dart:932`. `wallet_ledger.ref_id` is nullable
(`:26929`) with only a non-unique btree on `(ref_type, ref_id)` (`:29421`); `financial_ledger`
has only a plain btree on `payment_intent_id` (`:28701`) — both constraints are genuinely absent.

**`payment_intents` half — declared unsizeable.** Its sitting count depends on the shape of a
writer that does not exist, so per `capacity-to-date` §4: *cannot size until a `payment_intents`
writer is designed, and `cto`/`po` hold that.* The DDL alone is two index statements, well under
one sitting, and **must not ship alone** — `cto`'s `T-052` ruling.

**Blocked.** Nothing. Two corrections owed to `po` as ticket edits (AC 1's `SECURITY DEFINER`
and `search_path` claims); neither blocks authoring. Number sent to `po`, copied to `pm` and
`team-lead-4`.

### Addendum, same day — four messages crossed my report; count holds at 2, checkpoint relocated

Briefs from `team-lead` (×2) and `team-lead-4` (×2) arrived after I had reported. Reconciled:

- **`financial_ledger` IN.** No change to my number — I had already sized both indexes and all
  three `trgfn_payment_to_ledger` inserts into sitting 1. `team-lead`'s original "size the
  `wallet_ledger` half only" was self-contradictory and I had not applied it.
- **7 vs 6 insert sites — no conflict, and I had already split it that way:** seven sites exist,
  six take a mechanical `ON CONFLICT DO NOTHING`, `admin_wallet_adjust:2982` is the seventh.
- **Zero callers** — found independently before the messages arrived. Newly checked:
  `supabase/schema/archive/fix_admin_functions_missing_auth_check.sql` names `admin_wallet_adjust`
  **only in a comment at `:9`**; it redefines `admin_force_delete_auth_user` and
  `admin_cleanup_user_data`, not any of my five. No competing definition exists in the repo.
- **`_wallet_recalc` AED-only** — noted, out of scope, will not touch.

**Checkpoint relocated — I now disagree with `team-lead-4` about where it falls, and with my own
first answer.** Both of us put it at the `admin_wallet_adjust` signature. On re-reading
`capacity-to-date` §1, the test for a second sitting is *a judgement whose output the next part of
the same ticket consumes* — and that signature is **ruled** by `T-049` (caller-generated uuid,
`NULLS NOT DISTINCT` rejected), has zero callers to migrate, and its output is consumed by a
single `ALTER COLUMN` statement in the same file. It is a decision taken inside a pass, not a
boundary between two. My first checkpoint — "a migration holding 6 of 7 clauses, not applicable" —
was a partial finish dressed as a checkpoint, which is the thing §1 warns against.

**The real boundary is migration-body-complete → AC-3 probe pack.** Sitting 1 is the whole
migration including `admin_wallet_adjust`, ending posted to the ticket in `G-002` format —
reviewable by `cto`, abandonable, complete in itself. Sitting 2 is AC 3's four probes, which need
fixtures (`settle_game`'s re-settle needs a game, an organiser and a commission rule) and a
**concurrent** replay demonstration for `financial_ledger`, since Invariant 5 is precisely about
the concurrent case a sequential probe cannot show.

**The one question that would take this to 1 sitting, named with its owner:** the ticket does not
say who authors AC 3's probes. **If `cto` owns them, KAN-128 is 1 sitting for this seat**; if they
come with the migration, it is 2. `po`/`cto` hold that. Ceiling stays 2 either way — one rework
cycle on a money migration that has never executed against rows anywhere.

**Re-flagged to `team-lead`, which reasserted it after my report:** *"restate `SET search_path TO
'public','pg_temp'` in every replaced function, do not add `SECURITY DEFINER`"* is wrong for four
of the five. They are `SECURITY DEFINER` and carry `SET search_path TO 'public'` with no `pg_temp`.
Unchanged from my report; the instruction has now been given twice.
