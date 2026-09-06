---
name: capacity-to-date
description: How a team lead converts capacity into a due_date without estimating, and the sitting unit that makes it arithmetic. Use whenever a date is asked for, challenged, or compressed — "when can this land", "can we finish by Friday", a re-date after a ticket runs early or late; whenever work is sized against senior-backend or any shared single-writer seat whose queue you do not own; whenever an exclusive grant collapses a chain onto one seat; and whenever a task cannot be sized and the honest output is a named blocker instead of a number.
---

# Capacity to date

`agent/WORKFLOWS.md:58` states the rule the whole company's scheduling runs on:

> **The date comes from capacity, not estimation.** Capacity is reported by the owning
> `team-lead-N`. The `po` may not estimate it and may not ask a developer directly.

That is a prohibition with no method behind it. A lead reading it learns what it must not do
and nothing about what to do instead. **This skill is the method.** It is written from the
five Phase 0 tickets `KAN-121`–`KAN-125`, where every number on the board came out of this
process.

**The distinction, made operational.** An estimate answers *how long will this take* — a
guess about the future wearing a number. Capacity answers *how many units does this task
consume, and how many can this seat absorb* — a count. The difference is that capacity is
**countable before the work starts** and an estimate is not. Everything below is counting.

## 1. The sitting — the unit

> **A sitting is one uninterrupted pass at a ticket by one seat, ending at a checkpoint
> where the work can be handed off, reviewed, or abandoned without losing state.**

The unit is already in live use — `KAN-124` is a two-sitting ticket on the board, and `po`
and `devops` both schedule in it — and it was defined nowhere until this file.

**The checkpoint is what makes it a sitting. Elapsed time does not.** Two sittings run
back-to-back are still two sittings, because the checkpoint between them is still there.
Hold this exact line under pace pressure: *"we work 24 hours"* is not an argument that the
work is smaller, and running two passes end to end does not merge them into one.

**A sitting is not a day.** The board renders sittings as calendar dates because `due_date`
is a date field. That mapping is a separate, stated assumption owned by `po` — see §2 input
4 and the open question at the end. Report sittings; do not report days.

### Counting sittings on a ticket

**One sitting** — the whole population of changes is enumerable before starting, and every
change is the same kind. The work is *mechanical*: you can write down what "done" looks like
in full before touching anything.

- `KAN-121` (P0-1): write one golden test file. One deliverable, one kind.
- `KAN-122` (P0-2): move 3 files, rewrite 42 import lines across 39 files. Every one of the
  39 was enumerable in advance by `grep -rln "misc/data/datasources" lib/ test/` before the
  ticket opened.

**Two or more sittings** — the ticket contains a **judgement whose output the next part of
the same ticket consumes**. That dependency boundary *is* the checkpoint, and it is what
makes the count go above one.

- `KAN-124` (P0-3b): bucket 80 top-level route entries into 6 module files, then extract
  them, and prove it with `KAN-121`'s golden test green **with no edit to the golden file**
  (`STACKS.md` §10.3). The extraction cannot start until the bucketing is settled, and the
  bucketing can be wrong. Sitting 1 ends at *modules exist, golden test not yet green* —
  a real checkpoint: reviewable, abandonable, and not done.
- `KAN-128`: author one migration, then run the AC-3 probe pack. Sitting 1 ends at
  *migration body complete and posted in `G-002` format*; sitting 2 is the probes, which need
  fixtures and — for `financial_ledger` — a **concurrent** replay, since a sequential retry
  cannot demonstrate the failure at all: the failure *is* the interleaving.

  **This example is deliberately left branched, because the branch is the more instructive
  half.** Who authors the AC-3 probes is open with `po` as of 2026-09-06: **`cto` owning them
  makes it 1 sitting on `senior-backend`; shipping them with the migration makes it 2. The
  ceiling is 2 either way.** A count of "2" teaches the arithmetic; "2, or 1 if a named seat
  owns a named deliverable, and here is who was asked" teaches §4 — which is the part leads
  get wrong. Report a branch this way rather than resolving it to the number you prefer.

### Neither risk nor volume is a checkpoint. A dependency boundary is.

**The test is whether the ticket's next part cannot start until the judgement lands** — not
how likely the judgement is to be wrong. This is the distinction a lead gets wrong at speed,
and it was got wrong on `KAN-128` before `senior-backend` corrected it.

The tempting reading was that `admin_wallet_adjust`'s signature change is a checkpoint because
it is an interface commitment with no caller to validate against, so it is hard to verify. It
is not a checkpoint: the signature is **ruled** by `T-049` (caller-generated uuid,
`NULLS NOT DISTINCT` explicitly rejected), it has **zero callers to migrate**, and its output
is consumed by one `ALTER COLUMN ref_id SET NOT NULL` in the same file. That is a decision
taken *inside* a pass.

In `senior-backend`'s own words, confirmed first-hand: *"less checkable raises the odds of a
rework cycle, which is why my ceiling is 2 rather than a flat 2. But §1's test is dependency,
not risk."*

**Risk is not discarded — it is banked in the ceiling.** Say that in the same breath as the
rule, because a lead who takes only *risk is not a checkpoint* may conclude risk goes nowhere,
which is worse than the error it replaces. Hard-to-verify work lands in the gap between your
earliest and ceiling columns (§2). That gap is where it is supposed to go, and pricing it there
is what makes the two-column report do real work. It does not buy a sitting.

**The failure is substituting a proxy for the test, and risk is only the nearest one.** The
test is a single question — *can the next part start before this lands?* Under time pressure a
lead reaches for whichever proxy is closest to hand and answers an easier question that feels
like the same one. Two have now been caught on the same lead, by the same seat:

| Proxy | The reasoning that feels right | Why it fails |
|---|---|---|
| **Risk** | less checkable, therefore a checkpoint | raises the odds of a rework cycle; creates no boundary (`KAN-128`) |
| **Volume** | materially bigger, therefore more sittings | adds no boundary unless it adds one (`KAN-130`/`KAN-131`) |

On the volume case, `senior-backend` again: *"Volume shifts the start, not the cost — that is
your own argument about the `payment_intents` cut, and it runs symmetrically: lighter mechanical
work buys back no sitting, and heavier mechanical work adds none unless it adds a **boundary**.
I went looking for a second boundary and could not find one."* The bundle came back **2 sittings,
ceiling 3** — the same shape as the ticket it was supposed to dwarf.

**Expect a third proxy you have not met.** Test a proposed sitting by naming the boundary out
loud; if the sentence that justifies it does not contain *"cannot start until"*, you are holding
a proxy. *(Two instances, one lead, one correcting seat — a hypothesis about how the test gets
misread, not a measured pattern.)*

### The opposite failure: a partial finish dressed as a checkpoint

The inflation direction, and it is seductive. The worked example is `senior-backend`'s own
first checkpoint on `KAN-128`, which it proposed and then discarded — a seat rejecting its own
boundary, which is better evidence than a lead rejecting someone else's:

> *"The migration file holds the constraints and 6 of 7 conflict clauses; `admin_wallet_adjust`
> untouched — reviewable and abandonable, and **not applicable**, because `ref_id NOT NULL`
> breaks `:2982` until sitting 2 lands."*

It argued that the un-appliability was what made it a checkpoint. **It is the opposite.** A
migration that cannot be applied is not a state anyone can hand off, review to a verdict, or
abandon and still have something — it is half a file, with its incompleteness dressed up as the
evidence for its completeness.

**The tell: *"it cannot be applied yet"* sounds like a boundary and is only a middle.** Test a
proposed checkpoint by asking what a reviewer would do with the artifact if the ticket stopped
there. If the answer is "nothing, it doesn't work yet," it is a pause.

### Mechanical tickets finishing early is not evidence a judgement ticket is smaller

`KAN-121` and `KAN-122` both ran clean at one sitting on 2026-09-05, faster than their board
spacing. That is what a correctly-sized mechanical ticket does — it is evidence the *spacing*
carried slack, not that the *sizing* was generous. It says nothing about `KAN-124`, which is
the only Phase 0 ticket carrying design judgement.

**Shift the start; keep the cost.** Two clean mechanical tickets buy a schedule shift and
never a re-size.

**The same rule runs in the other direction, when scope is cut mid-ticket.** Everyone's
instinct is that a smaller ticket lands sooner, and for a judgement ticket that is usually
false. `KAN-128` had `payment_intents` dropped from its scope on 2026-09-06 (no SQL writer
exists for it, so a bare constraint would have been the failure `T-049` forbids). The cut
removed DDL volume from the authoring pass and touched nothing about the probe pack that makes
the ticket two sittings. **Ask which sitting the cut came out of.** If it came out of the
mechanical one, the cost is unchanged and only the start moves.

**It runs symmetrically, and the upward direction is the one that catches people.** Lighter
mechanical work buys back no sitting; heavier mechanical work adds none — unless it adds a
boundary. A lead who has internalised the cut direction will still expect a materially bigger
ticket to cost more, because the symmetry is not obvious from reading only the downward case.
It is the same rule.

## 2. Capacity to date — the arithmetic

The conversion has exactly four inputs. **A lead supplies three and never the fourth.**

1. **Sittings per ticket** — from §1, with the reason named for anything above 1.
2. **Serialisation** — which tickets can run at the same time, and why. Phase 0: zero
   parallelism, one seat (§5).
3. **Gates and hand-offs** — everything inside the ticket that is not the author's own
   sitting. Both run on other seats' clocks and both are counted separately. Never fold
   either into a sitting.
   - A **gate** is acceptance. `WORKFLOWS.md`: *a slot frees on acceptance, not delivery* —
     a seat that has handed work to review still holds its slot. A chain of N tickets costs
     **N sittings plus N gates**.
   - A **hand-off** is a sitting on a different seat than the author, inside one ticket, that
     is *work* rather than acceptance. `KAN-128` is the shape: `senior-backend` authors the
     migration, **`cto` applies it**, `po` gates it — two sittings, one hand-off, one gate,
     across three seats. A hand-off serialises the ticket internally, so it is a dependency
     as well as a cost.

   **Each leg is sized by the seat that executes it** — see §3. The author does not size the
   hand-off and the hand-off's owner does not size the authoring. Expect this shape to be
   normal rather than exotic: `money-write-invariants` already rules that a money write is
   `senior-backend` (schema, RPC) *plus* `senior-frontend-4` (call site, controller), and D4
   carries 110 features.
4. **The calendar mapping** — sittings and gates resolved onto dates under a stated
   work-week assumption. **This is `po`'s, not yours.** Hand over counts and a rate.

### Worked example — the whole Phase 0 chain

What I reported (`agent/status/team-lead-3.md`, 2026-09-05): **6 sittings, strictly serial,
one seat, zero parallelism** — P0-1 `1`, P0-2 `1`, P0-3a `1`, P0-3b `2`, P0-4 `1`.

What `po` did with it (`agent/status/po.md`): converted **"6 sittings + 5 acceptance gates"**
under a written assumption — one sitting and one gate per working day, Mon–Fri — into
`KAN-121` 09-07 · `KAN-122` 09-09 · `KAN-123` 09-11 · `KAN-124` 09-16 · `KAN-125` 09-18.
Two board-days per sitting.

**I set none of those dates.** Every number is `po`'s, derived from my count. That split is
the whole rule: the lead owns the count, `po` owns the calendar.

### Give two dates, not one

**A `due_date` is a ceiling, not a target.** Earliest-believed and outer-bound are different
numbers and both get reported. The gap between the columns is the **rework budget, stated
openly** rather than hidden inside the ceiling as padding.

| Ticket | Sittings | Earliest believed | Ceiling committed |
|---|---:|---|---|
| `KAN-123` P0-3a | 1 | 2026-09-06 | 2026-09-07 |
| `KAN-124` P0-3b | 2 | 2026-09-07 | 2026-09-09 |
| `KAN-125` P0-4 | 1 | 2026-09-08 | 2026-09-10 |

The live board carries the ceiling column exactly (verified 2026-09-06: `KAN-123` `2026-09-07`,
`KAN-124` `2026-09-09`, `KAN-125` `2026-09-10`). The gap is roughly two rework cycles, and it
was named as such on the epic rather than left to be discovered as slack. (This column pair is
an aggregated project buffer in Goldratt's sense; the vocabulary is public, the practice here
was derived without it.)

**The stronger reason is that two numbers are auditable and one is not.** The rework budget
explains why the gap exists; this explains why a downstream seat can catch an error inside it.
On `KAN-128`, `po` first set the `due_date` to **2026-09-09**, then corrected it to
**2026-09-10** — because 09-09 was **`cto`'s apply slot, not the ceiling on `senior-backend`'s
authoring**. The wrong seat's clock.

That correction was possible only because both columns were on the record **with their bases
named**, so it reduced to a one-line reasoning fix rather than a re-derivation. A single date
would have hidden it completely: 09-09 is entirely plausible, and nothing about it looks wrong
from the outside. **State the basis of each column, not just the number** — the basis is what
makes a category error visible.

### Re-dating: move the start, keep the cost

When a ticket lands early or late, recommend a **uniform shift of the entire remaining chain
at the unchanged rate**, derived from the remaining sitting count. Do not re-size.

On 2026-09-05, with two sittings consumed and four remaining, I recommended a uniform −4 day
shift across `KAN-123`/`124`/`125` — *"derived from the four remaining sittings at the same
2-day rate, not from the fact that two tickets went fast."* Every ticket kept its sitting cost.

**Two conditions travel with a shift and are stated, not assumed:**

- **The chain is serial on `Done`, not on `In Review`.** A shift conditional on a predecessor
  clearing its gate shrinks one-for-one if that gate sends work back.
- **`po` owns the weekend.** My −4 arithmetic put `KAN-124` on Saturday 2026-09-12. `po` used
  Friday 09-11 instead, preserving the two-sitting cost in *working* days. Hand over sittings
  and a rate; let `po` resolve them against the calendar rather than doing that half badly
  yourself.

## 3. Sizing against a shared single-writer seat

`senior-backend` (Shu) is **one seat serving all five teams**. A date on its work is a claim
on a queue you do not own, and a lead that issues one is estimating.

> **For your own developers, report a cost and a date. For a shared seat, report a cost, no
> date, and the name of the seat that owns the queue.**
>
> **Then ask that seat for its own count, and carry it back unchanged.** The prohibition is
> on *producing* the number, not on requesting it. **A seat sizing its own work is capacity,
> not estimation** — that is the whole basis of the rule, applied one seat over.

**Naming the owner is half the job. Stopping there orphans the count.** This section said only
the first half until 2026-09-06, and the cost was measured: on `KAN-128` — a migration racing
D4's 2026-09-14 activation, free only while five money tables hold zero rows — **four seats
refused in sequence and every refusal was correct.** `team-lead-4` refused under this section;
`po` under `WORKFLOWS.md:58`; `pm` applying the same rule to itself; `cto` under `G-025`. Four
correct refusals, no owner, and a deadline-bound ticket standing still.

*(Provenance, since a case study is only as good as its sourcing: the first three are
first-hand from the seats themselves. `cto`'s refusal reached `team-lead-4` relayed by `pm` and
is second-hand — the grounds are almost certainly right, the chain of custody is one link
longer than the sentence above implies.)*

Resolution, reached by `team-lead` on 2026-09-06 and recorded here rather than invented here:
**the lead asks the owning seat for its own count and carries it unchanged.** If you believe
that reading of `WORKFLOWS.md:58` is wrong, take it to `pm` — do not quietly resume dating a
seat you do not own.

**Ask the right seat for the right leg.** On a ticket with a hand-off (§2 input 3), each leg is
sized by the seat that executes it: `senior-backend` sizes its own authoring, `cto` sizes the
apply. Asking one seat to confirm another's count is this same error one level up, and it looks
like diligence.

### What the owning seat should hand back — the required shape

**`KAN-126` (P0-5), owned by `devops`, is the pattern to ask for by name.** `po` left the
`due_date` unset on purpose and recorded why: *"No capacity number exists for `devops`, and I
was told not to estimate one."* `devops` then supplied its own number
(`agent/status/devops.md`): **2 sittings — sitting 1 datable and fully parallel with
`senior-frontend-3` (no shared path); sitting 2 undatable, its precondition outside `devops`'s
control.**

That is the shape a shared seat owes: **a per-sitting count, which sittings are datable, and
the named blocker on any that are not.** A partial answer from the seat that owns the queue
beats a whole answer from one that does not. Ask for it in those terms — a seat asked simply
"when?" tends to return a single date, which is the estimate you were avoiding.

**What a lead may state about a shared seat without owning its date:**

- **That it is a dependency, and whether it is on the critical path.** A claim about
  ordering, not duration.
- **Disjointness — measurable, so settle it yourself.** `senior-backend` may run
  `supabase/**` alongside Phase 0 because Phase 0 touches no path under `supabase/`
  (`CONTRACT.md` §4.1). That is a fact about paths, and it is checkable.

**The characteristic error is over-coupling, and I made it.** I flagged `KAN-126` as sitting
on Phase 0's Friday critical path. It does not: `CONTRACT.md` §4.1 limits the grant to
`P0-1`–`P0-4`, and P0-5 needs no grant. Before you put a shared seat on your critical path,
read the document that defines the path.

## 4. When a task is unsizeable

> **A task is unsizeable when its sitting count depends on a fact that does not exist yet.**

The honest output is then a **named blocker and its owner** — *"cannot size until X, and Y
holds it"* — never a number with a caveat bolted on. A caveated number is read as a number.

**The mirror of that rule, and it spends other seats' capacity rather than your own: a
measurable question framed as a decision manufactures a decision.** On `KAN-130`,
`team-lead-4` raised a scope question — four lines or eight — as a choice, when it was a fact
it had not checked: `wallet_ledger` carries its own `user_id`, so the second class was never
in scope. `po` answered because it was asked, `team-lead` ratified because it looked like
judgement being exercised, and one read of the table definition would have settled it before
anyone was asked. **Before you escalate a sizing input, check whether a command or a file
answers it** — the general rule is in every role file's escalation test; the capacity-specific
cost is that a manufactured decision consumes two other seats' sittings and produces a wrong
edit.

Two shapes, both live in Phase 0:

- **The precondition sits outside the seat's control.** `devops`'s P0-5 sitting 2, above.
  Named as undatable; the number was still delivered for the half that was datable. Size the
  sizeable part and name the rest.
- **A predecessor's output is your denominator.** `KAN-124`'s two-sitting cost rests on
  `KAN-123` producing a builder→slice bucketing table for all 80 entries. If that table comes
  back thin, the basis for the cost is gone.

### Decide the contingency before the fact lands

This is the transferable move, and it is what keeps a re-cost from being an improvisation on
the day. Before `KAN-123` opened, I wrote its three branches onto the ticket:

- **Fewer than 80 entries covered** → incomplete work, not a re-cost. Straight back under the
  ticket's own rework triggers; `KAN-124`'s cost untouched.
- **Sparse collision sets** → a legitimate finding that makes `KAN-124` *cheaper*, and still
  buys back no sitting: its cost is the six-file extraction plus the golden test, not the
  ordering constraint.
- **A frozen pair spanning two buckets** → the only branch that re-costs upward, and a spec
  problem for `analyst`/`cto` rather than a sizing problem. Put on the ticket as
  **flag-on-sight, do not save for the writeup**, so it surfaces on day one.

**Measure the denominator before calling anything thin.**
`awk 'NR>=444' lib/app/app_router.dart | grep -cE '^    (GoRoute|StatefulShellRoute|ShellRoute)'`
returns **80**. Once that number was mechanical, "thin" stopped being an argument and became
a comparison.

## 5. Sizing under an exclusive grant

An exclusive grant (`CONTRACT.md` §4.1 is the live one) names a single seat as sole executor
of a set of tickets. **Capacity arithmetic changes shape, and a lead sizing during a grant
should know it is doing different arithmetic.**

- **Headcount stops being an input.** Sixteen developer seats exist; fifteen are idle on app
  code for the duration (§4.1, *The exclusion*). My own two juniors are barred outright —
  `STACKS.md` §10.0: *no junior enters any Phase 0 ticket* — and contribute zero.
- **Total is the sum of the sittings. There is no division.** Six sittings on one seat is six.
  Adding people makes it slower: `G-015` Ruling 1 — *dispatching before the split buys
  queueing, not throughput*.
- **The chain is strictly serial, so nothing parallelises out of trouble.** A slip anywhere
  shifts everything after it one-for-one. Take that to the lead and re-date; do not absorb it.
- **Only the rework budget is compressible.** A compression request may spend slack; it may
  not spend sitting cost. When Phase 0 was asked to finish by Friday 2026-09-11, the answer
  was **yes, conditional on `KAN-124` keeping two sittings and Friday carrying no ticket** —
  yes to the date, no to the shrink, with the window holding exactly one rework cycle.
- **Read the grant's own expiry test before putting anything on its critical path.** §4.1
  expires by measurement at the `STACKS.md` §10.6 landing test, not by decision. Which
  tickets are inside it is written down — check rather than infer (§3).

**Name what breaks under pace.** Compression pressure has predictable failure modes and they
belong in the capacity report, not in hindsight. For Phase 0 the four were: editing the golden
file to make a red test pass (which converts the only proof into evidence of nothing); a
`reset`/`checkout`/`stash` against the uncommitted tree four tickets are stacked on; a review
gate that keeps pace by becoming a rubber stamp; and a dependency on a seat outside the grant.

## What a capacity report contains

Every line, or the report is not finished:

- [ ] Sittings per ticket, with the checkpoint named for anything above 1.
- [ ] What is serial, what is parallel, and the measured reason each is so.
- [ ] Gates and hand-offs counted separately from sittings, each attributed to its seat.
- [ ] Every shared-seat count **requested from that seat and carried unchanged** — never
      produced by you, and never confirmed by a third seat on its behalf.
- [ ] Two columns — earliest believed and ceiling committed — with the gap named as the
      rework budget.
- [ ] Every shared-seat dependency named with its owning seat and **no date**.
- [ ] Anything unsizeable stated as *"cannot size until X, and Y holds it"*, with the
      sizeable part still sized.
- [ ] Contingency branches written down for any figure resting on a predecessor's unfinished
      output — decided now, not on the day.
- [ ] **No date set by the lead.** The counts go to `po` through the channel `WORKFLOWS.md`
      §4 names.

## Open questions — undefined, and deliberately not invented

**The sitting-to-calendar-day mapping has no method behind it.** `po` assumed one sitting plus
one gate per working day; the board has run at roughly two board-days per sitting. Both were
assumptions, both were stated as assumptions, and neither is derived from anything. The only
evidence is two mechanical tickets closing inside a day each, and the ticket that most needs
the mapping — `KAN-124` — is the one they say nothing about. **No rule is offered here.** A
lead reports sittings; the mapping stays `po`'s stated assumption until someone has enough
data points to derive one. Whoever gets the fifth and sixth should write it into this file.

**Two more points arrived on 2026-09-06 and still do not derive it.** `KAN-128` came out at
2 sittings on `senior-backend` plus one hand-off and one gate — but its `due_date` was never
set, so it yields a cost with no elapsed time to compare against. `team-lead-4`, who reported
it, said plainly that its data is not clean enough to derive from. Recorded so the next seat
does not re-count them as evidence: **four points, none of them a measured sitting-to-day
ratio on a judgement ticket.**

**Whether a sitting transfers to a non-developer seat is unruled.** `devops` used the unit for
a documentation write plus an end-to-end demonstration and it appeared to work. Nobody has
ruled that it generalises, and this skill does not.

## Owed elsewhere

Two things belong in `agent/WORKFLOWS.md` and are not written by this skill — it was under
another seat's hand when this was written, and both are `po`-or-`devops` edits routed the
usual way.

1. **`:58` states the capacity-not-estimation rule and points at no method.** It should point
   here.
2. **The shared-seat resolution in §3 currently lives only in this file.** `:58` says capacity
   is reported by the owning `team-lead-N` and says nothing about a seat no lead owns — the
   silence that stalled `KAN-128` through four correct refusals. The governing document should
   carry *the lead asks the owning seat for its own count and carries it unchanged*; a company
   rule that exists only in a skill is one seat's note, and the next seat to hit this will read
   `:58`, not this file.
