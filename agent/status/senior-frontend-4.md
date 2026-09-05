# senior-frontend-4 — status

## 2026-09-06 · Skills audit (survey, no work) — first run of this seat

**Dispatched by** `team-lead-4`. Read-only survey. **No code written, no git, no Jira, no
`flutter`.** This file did not exist before today.

### What I did

Read `agent/skills/` (74), `agent/skills/AVAILABLE.md`, my role file, and then **opened
bodies** rather than judging by name: `release-it`, `ddia-systems` (+ their
`references/`), `paywalls` (full, + `references/experiments.md` listing), `pricing`,
`hooked-ux`, `microinteractions`, `drive-motivation`, `improve-retention`,
`flutter-implement-json-serialization`, `frontend-patterns`, `backend-patterns`.
Measured the repo where a claim depended on it.

### What I decided / found

1. **Enablement, not availability, is the binding constraint for my two stacks.**
   `/Users/moatazmustapha/Desktop/One Brain/.claude/settings.json` `enabledPlugins` does
   **not** contain `ux-design@wondelai-skills` and contains **zero** `marketingskills`
   plugins. So `hooked-ux`, `microinteractions`, `drive-motivation`,
   `improve-retention`, `paywalls`, `pricing`, `churn-prevention` — the seven closest
   to D7 Rewards and D4 Money — are installed on disk but **not invocable via `Skill`**.
   They can only be `cat`-ed. `AVAILABLE.md` lists them as "available to any seat today";
   for these seven that is not true of the `Skill` tool.

2. **A second `dart-flutter` member contradicts this repo**, on top of the one
   `senior-frontend-3` found. `flutter-implement-json-serialization` SKILL.md, Core
   Guidelines: *"Throw Exceptions on Failure… Do not return `null`."* That is the exact
   inverse of the repo's non-negotiable `Result<T, Failure>` / never-throw-across-layers
   rule. It also prescribes hand-written `fromJson`/`toJson` against a repo that uses
   Freezed + `build_runner`. `flutter-use-http-package` is dead here too — the client is
   `Supabase.instance.client`, not `package:http`. **Cite members, never the set.**

3. **Money-flow correctness has essentially no coverage in the ~524.** `idempoten*`
   appears in exactly two SKILL bodies: `ddia-systems` (one line, 153) and
   `marketing-loops` (a different sense of the word). The only real material is
   `release-it/references/stability-patterns.md:223-238` (retry budget, idempotency keys,
   retryable vs non-retryable split) and `ddia-systems/references/transactions.md:132-178`
   (write skew, worked `-- Double booking!` example). Both are server-side framing.
   **Nothing in the corpus is about payment *UI* correctness.**

4. **Two backend gaps found while checking whether the skill gap mattered** —
   `senior-backend`'s, not mine, flagged not fixed:
   - `payment_intents` (`supabase/migrations/20260829080500_baseline_schema.sql:23491-23503`)
     has **no idempotency-key column** and no uniqueness on `provider_intent_id`. Indexes
     at 28837/28841/28845 are all plain btree. A client retry mints a second intent.
   - `wallet_ledger` (`:26922-26940`) is documented append-only, but `(ref_type, ref_id)`
     carries only a plain index (`:29421`), not a unique constraint. Nothing at the schema
     level stops the same credit posting twice.

5. **`paywalls` implementation half is mine.** `content-manager` was right that the copy is
   its and the flow decision is `pm`/`cxo`'s, but SKILL.md §"Timing and Frequency" and
   §"Upgrade Flow Optimization" specify per-session caps, dismiss cool-downs measured in
   days, and post-upgrade immediate-access — all **client state I would have to build and
   persist**. It is not invocable (see 1), so today that is a read, not a `Skill` call.

### Blocked / not done

- Cannot invoke the seven skills in finding 1. Enabling `ux-design@wondelai-skills` and the
  relevant `marketingskills` plugins is a config decision above this seat — raised to
  `team-lead-4`, not acted on.
- The two schema gaps in finding 4 are `senior-backend`'s queue. Not raised as a ticket by
  me — I do not write tickets.
- **Not verified:** did not open all 524; did not read `churn-prevention`, `cro`,
  `ab-testing`, `onboarding`, `analytics`, `aso` bodies — judged from description only.
  Did not probe live Supabase; schema findings are from the baseline migration file, and
  `SCHEMA.md` §8 mismatch 7 warns the file is not the remote.
