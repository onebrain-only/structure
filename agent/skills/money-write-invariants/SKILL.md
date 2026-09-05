---
name: money-write-invariants
description: The five invariants every money-touching write must satisfy, and the definition-of-done vocabulary for a money ticket. Use when writing, assigning, reviewing or accepting any work that inserts, updates or reads a row in wallet_ledger, financial_ledger, payment_intents, wallets, payouts or game_settlements — and whenever a ticket in stack D4 (Money, payments & subscriptions) is being scoped or closed.
---

A double-written booking is visible. A double-written credit is not: it passes review,
passes QA, ships, and is found by a user holding the wrong balance. Every rule here exists
because the failure it prevents is **silent**.

Authority: `dabbler-docs/DECISIONS.md` **T-049**. This skill is the working form; T-049 is
the ruling and carries the reasoning and the rejected alternatives.

## THE TABLES THIS APPLIES TO

`wallet_ledger` · `financial_ledger` · `payment_intents` · `wallets` · `payouts` ·
`game_settlements`. If a change touches any of them — schema, RPC body, trigger, or a Dart
call site — it is a money write and every section below applies.

**There are two ledgers, not one.** `wallet_ledger` is the user-balance journal
(`direction`/`amount_aed`/`ref_type`+`ref_id`). `financial_ledger` is the
booking-settlement journal (`entry_type`/`amount`/`payment_intent_id`, split three ways
across user, platform and venue). They have different keys and different writers. A rule
proved on one is not proved on the other — say which you mean.

## THE FIVE INVARIANTS

### 1. Every ledger write is keyed, and the key is UNIQUE in the schema

A ledger row carries a **natural key** identifying the real-world event that caused it.
That key must be enforced by a `UNIQUE` index, and the write must be
`ON CONFLICT DO NOTHING`.

Do **not** add an `idempotency_key` column. The natural key already exists on every one of
these tables; what is missing is the constraint. Adding a second key beside an unenforced
first one gives you two keys and no guarantee.

| Table | Natural key |
|---|---|
| `wallet_ledger` | `(ref_type, ref_id, direction)` |
| `financial_ledger` | `(payment_intent_id, entity_type, entry_type)`, partial `WHERE payment_intent_id IS NOT NULL` |
| `payment_intents` | `(provider, provider_intent_id)` partial `WHERE provider_intent_id IS NOT NULL`; **and** one live intent per booking |

`direction` and `entry_type` are **in** the key on purpose — see invariant 2. `status` is
**out** of the key on purpose — see invariant 3.

**`ref_id` is never NULL.** A unique index treats NULLs as distinct, so a NULL `ref_id`
silently opts that row out of every guarantee on this page. `admin_wallet_adjust` writes
`ref_type='adjustment', ref_id=NULL` today — an adjustment must supply a caller-generated
`uuid` instead. Never "fix" this with `NULLS NOT DISTINCT`; that would collapse all
adjustments into one row.

### 2. A reversal is a new opposing row, never an edit of the original

A refund, a chargeback, a cancelled payout, a corrected settlement — each is a **new row in
the opposite direction**, referencing the same `ref_id`. The original row is never amended
and never deleted.

This is why `direction` is in the unique key: the debit and its reversing credit share a
`ref_id` and must coexist, while neither may post twice.

`admin_cancel_payout` already does this correctly — it inserts a `'credit'` reversal rather
than touching the original debit. **Copy that shape.**

### 3. Amount is immutable; status is a permitted transition

`wallet_ledger` rows move `pending → posted` and `pending → voided` by `UPDATE`. That is
allowed and is not a violation of invariant 2 — a hold becoming a settled debit is the same
event reaching its next state, not a different event.

What is never allowed: changing `amount_aed`, `direction`, `user_id`, `ref_type` or
`ref_id` after insert, or `DELETE`ing a ledger row at all.

The table comment on `wallet_ledger` says "Append-only journal". Read it as
*amount-immutable*, not literally append-only; the status transitions above are the
intended design.

### 4. Balance is derived. A stored balance is a cache, and a cache is only ever recomputed

`wallets.balance_aed` and `wallets.held_aed` are **caches**, not a second source of truth.
The ledger is authoritative.

A cache may only be refreshed by **recomputing the full sum from the ledger** —
`_wallet_recalc` does exactly this, driven by an `AFTER INSERT OR UPDATE OR DELETE` trigger.
It may **never** be incremented in place (`balance = balance + x`). An increment loses the
ability to detect that it has drifted; a recompute cannot drift by construction.

Any change touching balance must leave the reconciliation true: for every wallet, the stored
balance equals the recomputed ledger sum.

### 5. Replay is absorbed by a constraint, not by a lookup

`IF EXISTS (SELECT …) THEN RETURN` is **not** idempotency. It is a read-then-write with no
lock: two concurrent deliveries both read "absent" and both insert.

Both current guards are this shape — `trgfn_payment_to_ledger` checks `financial_ledger`
for the `payment_intent_id`, and `perform_check_in` checks `last_check_in` against today.
Each tolerates a **sequential** retry and loses a **concurrent** one.

The `EXISTS` check may stay, as a cheap early return that avoids an error round-trip. It may
never be the only thing standing between a webhook and a double credit. The constraint is
what makes the guarantee; the check is an optimisation.

## THE CALL-SITE RULE

**A Dart call site must make the guarantee visible.** Reading
`svc.client.rpc('perform_check_in', …)` tells you nothing about whether the server dedups —
which means "repeat the existing pattern" is unsafe advice on a money path, because the
pattern being repeated may be the one case that was safe.

Every money write from Dart therefore:

1. Goes through an **RPC**, never a direct `.from(table).insert()`. Table-level writes to
   these tables are blocked by RLS and must stay blocked.
2. Names the RPC through a **`SupabaseConfig` constant**, never a string literal.
3. Carries a **one-line comment at the call site naming the constraint that makes it safe** —
   e.g. `// Idempotent: UNIQUE (ref_type, ref_id, direction) on wallet_ledger.` A reviewer
   must be able to see the guarantee without opening the database.
4. Is guarded against double-submit in the controller with an **in-flight flag**, not by
   trusting the server to absorb it. Server idempotency is the backstop, not the plan.

## DEFINITION OF DONE FOR A MONEY TICKET

A money ticket is not done until every line is true and demonstrated:

- [ ] The write's natural key is stated in the ticket, and a `UNIQUE` index enforces it.
- [ ] The write is `ON CONFLICT DO NOTHING` (or an explicit, justified `DO UPDATE`).
- [ ] Reversals are new opposing rows; no path edits or deletes a posted row's amount.
- [ ] No stored balance is incremented in place; any cache is recomputed from the ledger.
- [ ] **The replay test:** the same operation is executed twice and the ledger row count,
      the balance, and the returned result are identical after the second call. Run it — a
      reasoned argument that it is safe is not the test.
- [ ] The Dart call site goes through an RPC named by a `SupabaseConfig` constant, and
      carries the comment naming its constraint.
- [ ] The controller has an in-flight guard; the button cannot fire twice.

## WHO MAY DO THIS WORK

**No `junior-frontend-*` seat takes a money write.** Not because the seat is weak, but
because its rule — *repeat the existing pattern in a single file* — cannot be executed
safely here: the pattern does not carry its own safety, and the seat is explicitly not asked
to open the database to find out. A money write is `senior-backend` (the RPC, the schema)
plus `senior-frontend-4` (the call site and the controller).

A junior may take **read-only** money work — a balance display, a ledger list, a payout
history — provided the ticket says so and no `.insert()`, `.update()`, `.upsert()`, `.rpc()`
or edge-function call appears in the change.

Once the call-site rule above holds everywhere in D4, this bar is worth revisiting. It is a
consequence of the guarantee being invisible, not a permanent judgement about the seat.
