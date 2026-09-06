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

## 2026-09-06 — KAN-130+131 capacity, and a skill quotation verified (`team-lead-4` / `team-lead-3`)

**Did.** Read-only. Read `DECISIONS.md` `T-051` (`:6362`) and `T-052` (`:6475`) in full, and every
line they cite: `wallets` (`:26677`), `wallets_pkey` (`:28296`), `wallets_user_id_fkey` (`:31858`),
`wallets_id_unique` (`:29605`), `wallets_unique_idx` (`:29609`), `wallets_self_read` (`:34003`),
`wallets_block_dml` (`:33999`), `financial_ledger_wallet_fkey` (`:30583`), `fn_get_wallet`
(`:6088`–`:6102`), `_wallet_recalc` (`:1794`–`:1819`), `_wallet_after_ledger` (`:1780`),
`request_payout:10190`, `delete_my_account` (`:5257`–`:5306`), `v_wallet_balance`,
`v_wallet_admin_overview`.

**Touched.** This file only.

**Number — KAN-130+131 as one migration: 2 sittings, ceiling 3.** Same shape as KAN-128, and the
same probe branch: sitting 1 is the whole migration ending posted in `G-002` format; sitting 2 is
the probe pack. **3 if the erasure question below resolves "yes".** No date.

**I disagree with `team-lead-4`'s "materially larger than KAN-128" read.** It is larger in
*volume* — 6 DDL statements on `wallets`, a policy swap, four function bodies rewritten, one new
function — but volume shifts the start, not the cost. That is `team-lead-4`'s own argument about
the `payment_intents` cut, applied symmetrically: lighter mechanical work buys back no sitting, and
heavier mechanical work adds none, unless it adds a **boundary**. I could not find a second
boundary. The DDL ordering looks like a judgement and is not one — `T-051`'s six-item list fixes
the end state, and the sequencing (dropping `user_id` takes `wallets_pkey` and
`wallets_user_id_fkey` with it as dependents, so the new PK must be added in the same statement
block) is craft inside a pass.

**The exhaustiveness check `T-051` invites.** SQL references to `public.wallets` outside DDL are
**exactly four**: `_wallet_recalc:1813`, `fn_get_wallet:6090`/`:6096`, `request_payout:10190`.
Plus the policy, the PK, the FK, and two views. `v_wallet_balance` already keys on
`owner_type`/`owner_id`/`id` and needs no change; `v_wallet_admin_overview` reads only
`balance_aed`. **`fn_get_wallet` itself needs no edit** — its `INSERT` already omits `user_id`,
which is precisely what the drop makes legal. `T-051`'s six dependents are complete for the SQL
half.

**Under-specified, with its holder — the answer to what `team-lead-4` asked for.**
`T-051` item 3 makes `delete_my_account` delete the wallet before `delete from auth.users`, calling
it "an erasure obligation, not tidiness". But **`financial_ledger` has no FK to `auth.users`** and
`trgfn_payment_to_ledger:19219` writes `entity_type='user', entity_id=NEW.user_id`. So after
erasure the user's uuid remains in `financial_ledger` indefinitely, and
`financial_ledger_wallet_fkey`'s `ON DELETE SET NULL` (`:30583`) only clears `wallet_id`, not
`entity_id`. This predates KAN-130 and is not caused by it, but KAN-130 is the ticket that opens
`delete_my_account` and states an erasure obligation. **Cannot size that slice until it is ruled,
and `cto` holds it** (a retention/erasure call, possibly `cpo`). If it resolves "also scrub
`financial_ledger`", that is a judgement the rest of the migration consumes and the count goes to 3.

**Two I can settle myself, noted rather than escalated.** `request_payout:10190`'s replacement
lookup needs a `currency` predicate, which `T-051` omits — I will mirror `_wallet_recalc`'s ruled
AED-only design rather than leave a `select … into` that takes an arbitrary row once multi-currency
exists. And `wallets_id_unique` (`:29605`) becomes redundant once `id` is the PK — I will leave it
rather than drop it, since dropping it is unrelated cleanup.

**A third `search_path` string, which sharpens the standing correction.** `delete_my_account:5259`
is `SECURITY DEFINER` with `SET search_path TO 'public', 'auth', 'extensions'` — not `'public'`,
not `'public','pg_temp'`. Three distinct strings now across the functions in play. **The rule is
restate each function's own header, read from `pg_get_functiondef`; there is no shared string.**

**Confirmed for `team-lead-3`** the five points of my KAN-128 checkpoint reasoning quoted in
`capacity-to-date`, with one wording correction and the probe branch flagged as still open.

**Blocked.** Nothing. Cannot start KAN-130/131 authoring until `cto` applies KAN-128
(`T-052` requires rebasing on live post-128 definitions). The erasure question is with `cto`.

### Addendum — my own "concurrent replay" framing is not executable here, and does not need to be

**Measured live** (read-only, `list_extensions` on `wtncuzcskpigqpmnxwws`): **`dblink` is available but
NOT installed** (`installed_version: null`), `pg_background` is absent entirely, and **`pgtap` 1.2.0
IS installed** in `extensions`.

**Consequence.** A genuinely concurrent probe needs two sessions interleaved. Nothing in this
database provides that without `CREATE EXTENSION dblink`, which is a DDL change to production,
`cto`'s to apply, and outside KAN-128's scope. Adding an extension to production to run one test is
not worth it and I am not proposing it.

**And it is not needed — the probe should target the constraint, not the trigger path.** My original
point stands where it was aimed: a sequential retry through `trgfn_payment_to_ledger` proves nothing,
because the `EXISTS` guard at `:19183`–`:19189` absorbs it before reaching the insert. But the fix
under test is the **unique index**, not the trigger. Two **direct** inserts into `financial_ledger`
with the same `(payment_intent_id, entity_type, entry_type)` demonstrate it exactly, and
sequentially: pre-index both succeed (2 rows), post-index the second is absorbed (1 row). That
satisfies `cto`'s failing-first condition cleanly. Concurrency-safety is then a property **inherited
from the unique index** — Postgres serialises on it — not something the probe reproduces. That is
the whole reason `T-049` ruled a constraint over the `EXISTS` guard.

**Owed as a correction, because it is my phrasing that propagated.** "Concurrent replay
demonstration" is now in KAN-128's AC 3 and in `capacity-to-date`'s worked example, in my words.
As literally written it is not executable on this database. It should read: *a direct two-insert
probe against the constraint, demonstrated failing pre-index* — with the note that the trigger path
cannot be used to show the failure because its `EXISTS` guard hides it. Raised to `team-lead` for
routing to `po` (AC 3) and `team-lead-3` (the skill).

**No change to the count.** KAN-128 stays **2 sittings** — `cto` has ruled I author the probes, so
the branch is closed at 2, not 1. This changes what sitting 2 contains, not its size; arguably it
shrinks it, since the direct-insert probe is simpler than what I had imagined.

**Also noted from `cto`'s corrected AC 1:** the `admin_wallet_adjust` re-grant is `authenticated`
and `service_role` **only** — `anon` is deliberately dropped from the baseline's `GRANT ALL`
(`:34693`). That is a privilege reduction, and I will not "restore" it while restating.

### Close — erasure branch resolved downward; my pseudonymisation proposal was wrong

`cto` ruled the `financial_ledger` erasure slice **out of KAN-130's scope** (`T-054`, commit
`c3a2930`). **KAN-130+131 is therefore 2 sittings firm; the third does not fire.** The distinction
is worth keeping: `T-051`'s wallet delete *restores* a guarantee the `auth.users` cascade gave until
`T-051` itself removed it — a repair. A `financial_ledger` scrub would *create* a guarantee that
never existed — a policy call, not a repair.

**My pseudonymise-`entity_id` proposal is ruled illusory, and I should not have made it.**
`booking_id` and `payment_intent_id` still trace to the user, so severing one identifier severs
nothing — and `financial_ledger.entity_id` is `NOT NULL` (`:22706`), which I had **read myself**
while sizing KAN-130 and failed to apply. `cto` also found the stronger objection: the three rows
per payment are a balanced double-entry set, so deleting one side leaves `v_wallet_balance`
unreconciled for counterparties who never asked to be erased. Recommendation to `cpo` is documented
retention — zero SQL.

Not an exposure: `relrowsecurity` on `financial_ledger` is `true` with one policy
(`financial_ledger_admin_read`, qual `is_admin()`), and `is_admin(null)` is `false`.

**Owed to this seat later, logged so it is not rediscovered:** whatever `cpo` rules on retention,
`delete_my_account`'s comment block should state it. `cto` is barred from `dabbler-code`; a function
body is this seat's surface. One-liner, folds into whichever migration is live when the ruling lands.

**KAN-130 AC 2 item 3** now states all three `search_path` values explicitly, with the reason that
beats mine: `delete_my_account` needs `auth` on its path to run `delete from auth.users`, so
restating any other string **fails at runtime on account deletion, not at apply time.**
