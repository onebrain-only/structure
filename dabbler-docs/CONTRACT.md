# docs/CONTRACT.md — The Agent Contract

**Owner:** analyst (write) · all agents (read)
**Last updated:** 2026-09-05 — restructured for the v0.7 company roster (17 seats)
**Purpose:** Who may read what, who may write what, and what gets learned where.
This is the file that stops two agents landing in the same place, and stops an agent
rewriting the rule it is judged against.

Precedence: `DECISIONS.md` (newest ACTIVE) → this file and `MANIFESTO.md` →
`CONVENTIONS.md` → everything else. If this file and another disagree, this one wins
and the other is corrected in the same session.

---

## 1. THE READING RULE

**Reading is open. Writing is scoped.**

Any agent may read any file in this repository, including files it may never write, and
including this one. An agent that has not read what it is about to touch is working
blind, and nothing in this contract is served by keeping an agent ignorant.

The single exception is the second, unrelated Supabase project on the Onebrain account.
**No agent reads it and no agent writes it.** Only `wtncuzcskpigqpmnxwws` is ours.

Writing is different. Every write path below has exactly one owner, or is explicitly
UNOWNED. There are no blank cells in the matrix, because a blank is ambiguous between
"the master owns this" and "nobody owns this" — and those are not the same thing.

---

## 2. THE CLOSED-LOOP RULE

**An agent must never be able to write the file that defines or judges it.**

These belong to analyst and to no one else:

| Path | Why it is closed |
|---|---|
| `.claude/agents/**` | An agent editing its own definition can widen its own scope. |
| `docs/CONTRACT.md` | An agent editing the permission matrix can grant itself a path. |
| `docs/MANIFESTO.md` | An agent editing the rules can remove the rule it just broke. |
| `docs/DECISIONS.md` | The tie-breaker. An agent that can edit it wins every disagreement. |
| `agent/AGENTS.md` | The roster. Same reasoning as `.claude/agents/**`. |
| `agent/WORKFLOWS.md` | Defines the handoffs an agent is judged against. |
| `docs/CONVENTIONS.md` | An agent that violated a convention could delete the convention. |
| Everything, for `po` | It reviews all of it. Write access anywhere would let the reviewer author what it later approves. |

**`po` is constrained the same way, from the opposite direction.** It judges other
agents' work, so it writes **nothing** they could be judged on — one status file, and its own
memory. It has no write access to a single line of code, schema, config or governance doc.
That is not a permission still to be granted: **a reviewer that can edit what it reviews is
not a reviewer.** Its authority is on the Jira board, not in the tree.

analyst is itself constrained, and the constraint is real rather than decorative:
it is **read-only over all code**. It may write governance docs, `PROJECT_STATE.md`,
`STATUS.md` and its own memory. It may not write `lib/`, `supabase/`, `test/`, or any
build config. It finds problems; it does not fix them. If analyst could both
declare a finding and fix it, no one would ever review either.

**The PO overrides everything here.** Every file in this table is the PO's to change at
any time. The closed loop constrains agents, not the person they work for.

---

## 3. THE PERMISSION MATRIX

**Restructured 2026-09-05.** This table used to carry one column per agent. At **17 seats**
that is 17 columns of which 15 read `R` on almost every row — noise that hides the one cell
that matters. It is now **writer-per-path**.

### How to read it

- **Every seat may read every path**, unless a row says **NO READ**. Reading is how findings
  get verified; restricting it has to be argued for, and is argued for in exactly one place
  below.
- **`Writer`** names the **single seat** that may write that path. Not two. Where a path has
  no writer it says **UNOWNED**, and UNOWNED means *nobody writes it* — not *anybody may*.
- **`A`** after a name means **append-only**: add, never edit or delete what is there.
- **CONTENDED** means §4 governs it, not this table.
- **GENERATED** means no one hand-edits it; it is regenerated.

**A new seat starts from read-only and is granted a writer cell explicitly.** No cell is ever
filled in by analogy with a similar agent — that is how a grant nobody made comes to exist.

### ROUTING — read this before dispatching anything (`G-008`)

**This is a routing table, not only a permission table.** A request goes **directly to the
row's writer.** Never through `cto`, `cpo` or the Listener as a relay. Managers coordinate
multi-domain work and make the rulings `021` reserves to them; they do not answer
implementation questions their specialists own, and they are **not an approval step for
single-domain work.** Work that splits into independent units is dispatched in parallel to
each writer, not bundled or serialised through a manager.

`cto`'s production-apply authority (`G-002`) is unaffected — **that is an authority, not a
hop.**

### Leadership, and the one thing that has drifted twice

`cto`, `cpo`, `cxo` and `analyst` are **four peers** (`021`, `G-005`). Not a hierarchy.
Nothing routes through `analyst`, and it is **not a default recipient of task completions,
migrations or ticket verdicts** — it reconciles its own files on its own audit cadence, **pull,
not push.** The one standing exception is a CEO-direct edit to one of the four closed-loop
files it exclusively writes, because that is the only change it has no other way to discover.

**The line that decides who owns a document:** `analyst` establishes **what is true**; `cto`,
`cpo` and `cxo` decide **what should be true next**. A file recording measurements stays with
the measurer, because a decision-maker has no reason to re-run the query and the file rots. A
file recording intent goes to the decider. Where one file holds both, it is **split by
section, not handed over whole** — see `SCHEMA.md` in §9.

### The boundaries most likely to be crossed by accident

- **A `senior-frontend-N` writes Dart and never a migration.** A feature needing schema routes
  that need to `senior-backend`; it does not write SQL itself. **There are five of them, one
  per lead, each scoped to its lead's slices.**
- **`senior-backend` writes SQL and never Dart features.** **One seat per project**, and the
  app is the only staffed project — so sixteen developers and five leads share one backend
  writer, which then queues again behind `cto`, the only seat that may apply. It is the
  narrowest resource in the system and is obliged to state its queue rather than absorb it
  silently.
- **A `junior-frontend-Na`/`-Nb` writes only where a pattern already exists** — single-file,
  mechanical, **citing the existing example by `file:line`**. It is never the writer of a path
  on its own; it works inside its senior's slices on a lead's assignment, and **hands back
  anything whose shape is not already in the tree.** Ten of them, two per lead.
- **`team-lead-1..5` write no code, no SQL and no copy at all.** Their only write surface is
  Jira transitions and their own status file. A lead editing a file is a lead who has stopped
  leading.
- **`po` reads everything and writes tickets, verdicts and one status file.** *A reviewer that
  can edit what it reviews is not a reviewer* — that mechanism moved here intact when
  `po` merged in.
- **`cxo` judges the design system and never edits it.** Same reason.

### `qa` has no database access at all

**This is the one deliberate departure from read-open**, carried forward from `G-010`. `qa`
writes no code, no SQL, no docs and no governance file; its output is Jira bugs and comments.
Every Supabase row is **NO READ** for it — including the reading row that is open to everyone
else. Copying the read-open default here would grant something the PO explicitly withheld.

### Application code

**Amended twice on 2026-09-05.** `lib/features/**` no longer has one writer. Each slice is
written by **the `senior-frontend-N` whose lead owns that slice**, assisted by that lead's two
juniors on pattern-repeat work only. **That scoping is the mechanism, not a formality** —
`AGENTS.md` §5 puts the ceiling on parallelism at disjoint file sets, so five seniors inside
their own slices run at once and one outside them serialises everybody.

**The partition below is MEASURED. It is no longer proposed.** The provisional census-derived
map that stood here earlier on 2026-09-05 is **superseded and gone.** What replaces it is
`cto`'s partition, cut from the measured cross-feature import graph at `dabbler-code`
`c46b5c5` — `DECISIONS.md` **`T-047`**, authorised by **`G-015`** Ruling 2, applied here by
`analyst` under **`G-016`**. Evidence: `STACKS.md` §9a (the metric), §11.1–11.2 (the graph and
the cut), §12 (the thirteen-row delta). The metric is `E(A→B)` = files in `lib/features/A/`
importing a file in `lib/features/B/`; its reproduction command is `STACKS.md` §9a.
**Do not re-derive slice ownership from the D1–D11 stack labels.** Those are a feature
taxonomy for deciding *what* to work on and are **not** the write boundary — `AGENTS.md` §1.

**Every one of the 20 directories in `lib/features/` appears below, by name.** That is the
point of the table. The version it replaces named 18 and silently omitted **`home`** and
**`core`** — and `home` holds `main_navigation_screen.dart`, the app shell reached by the
`StatefulShellRoute`. A ticket assigned against `home` from the old table hit a slice with no
writer. An unowned slice with a shell in it is how the audit's 23 unowned slices happened.

| Slices | Writer | Lead |
|---|---|---|
| `profile`, `social`, `home`, `news`, `moderation` | `senior-frontend-1` + `junior-frontend-1a/1b` | `team-lead-1` |
| `games`, `venues`, `explore`, `location`, `venue_submissions`, `activities` | `senior-frontend-2` + `junior-frontend-2a/2b` | `team-lead-2` |
| `auth_onboarding`, `username_engine`, `app_boot` | `senior-frontend-3` + `junior-frontend-3a/3b` | `team-lead-3` |
| `rewards`, `admin` — **plus Commerce if and when `D4` is activated** | `senior-frontend-4` + `junior-frontend-4a/4b` | `team-lead-4` |
| `notifications` (features **and** `lib/services/notifications/**`) | `senior-frontend-5` + `junior-frontend-5a/5b` | `team-lead-5` |
| `core` (1 file, 18 LOC) · `error` (1 file, 53 LOC) | **UNOWNED — platform residue** | **none, by design.** Too small to justify a boundary and coupled to nothing. Governed by §4 shared-surface discipline: one agent inside at a time, append your block, no junior. **Named here so the gap is visible rather than invisible** |
| `misc` (13 files) | **UNOWNED — dissolving** | **none.** Phase 0 `P0-2` and `P0-4` empty it to exactly three residual screens — `help_center_screen.dart`, `transactions_screen.dart`, `participation_payment_step.dart` — which then stay UNOWNED under §4 (`STACKS.md` §10.4). **Until Phase 0 lands, treat anything in `misc/` as unowned and ask before writing it** |

**The counts, so the table can be checked rather than believed.** 5 + 6 + 3 + 2 + 1 = **17
assigned**, plus `core`, `error` and `misc` = **20**, which is what `ls Dabbler/dabbler-code/lib/features/`
returns. Files / LOC: lead 1 **167 / 69,485** · lead 2 **91 / 29,872** · lead 3 **53 / 13,127** ·
lead 4 **6 / 1,579** · lead 5 **19 / 4,259** · unassigned **15 / 7,529**. Total **351 / 125,851**.
**Independently re-measured by `analyst` at `c46b5c5` on 2026-09-05; `cto`'s figures reproduce
exactly, every row.**

**The load lands 55 / 24 / 10 / 1.3 / 3.4 percent by LOC, and that is deliberate, not an
oversight.** `T-047` priced every alternative: the cheapest cut that would split `team-lead-1`
is `profile | social` at **16 file-edges**, the most expensive cut anywhere in the tree, and it
would put two teams inside `profile_providers.dart` on day one. **The imbalance is a code fact
with a code fix — Phase 1**, splitting `profile_providers.dart`. Until then, hold leads 4 and 5
juniors idle rather than sending them outside their slices; an idle seat costs nothing and a
wandering one serialises everybody.

**What this partition does NOT cover. Read this before inferring anything from it.** It is a cut
of **`lib/features/**` and nothing else.** It says nothing about who owns any given file in
`lib/data/`, `lib/core/`, `lib/app/`, `lib/widgets/`, `lib/utils/`, `lib/themes/` or
`lib/design_system/`. Ownership on those surfaces is unchanged, **unmeasured**, and set by the
path table immediately below plus §4. **Owning a slice does not acquire the `lib/data/`
repository that slice calls.**

| Path | Writer | Rule |
|---|---|---|
| `lib/features/<slice>/**` | the owning `senior-frontend-N` above | **Authors only — applies nothing to production, touches no migration.** Schema needs route to `senior-backend`. A junior works here on its lead's assignment, on pattern-repeat single-file work only, and must cite the existing example by `file:line` |
| `lib/core/**` (except the four contended files) | **SHARED — no single writer** | Cross-cutting: a change here changes every slice. Requires `cto`'s sign-off on shape **and** coordination between leads before it is assigned. Treat with §4 discipline: **append your block, touch nothing else.** No junior enters it |
| `lib/data/**` | **SHARED — no single writer** | Same rule. Holds the live repositories; the audit found three parallel profile stacks here already, which is what an unowned shared surface produces. **`T-047` did not re-derive this surface — its 71 repositories remain unmeasured and owned by filename under §4** |
| `lib/app/app_router.dart` | **CONTENDED** | §4. **1,712 lines, 85 routes, touched by nearly every feature.** At sixteen developers this is the schedule, not a safety rule. **Phase 0 `P0-3b` splits it into six modules under `lib/app/routes/`**, after which each lead writes its own module and only the assembly stays contended (`STACKS.md` §10.3) |
| `lib/providers.dart` | **CONTENDED** | §4 |
| `lib/core/config/feature_flags.dart` | **CONTENDED** | §4 |
| `lib/core/config/supabase_config.dart` | **CONTENDED** | §4 |
| `lib/features/profile/presentation/providers/profile_providers.dart` | `senior-frontend-1`, **but see the rule** | **870 lines holding three domains' concerns.** **Treat it as contended** — one agent inside at a time — despite sitting in lead 1's slice, until Phase 1 splits it. **Re-measured by `analyst` 2026-09-05:** 32 files import it — `social` 9, `profile` 8, `home` 2, `news` 1 (lead 1); `venues` 2, `explore` 2, `venue_submissions` 1, `location` 1 (lead 2); `notifications` 1 (lead 5); and 5 shared/platform files — `lib/main.dart`, `lib/app/app_router.dart`, `lib/widgets/app_top_bar.dart`, `lib/core/services/auth_service.dart`, `lib/core/auth/session_cleanup.dart`. **The router and the top bar being among them makes this worse than a feature-level collision.** **Under the measured partition the collision is leads 1, 2 and 5** — the earlier "leads 1 and 2" was written against the superseded map |
| `lib/themes/**`, `lib/design_system/**`, `lib/utils/**`, `lib/widgets/**` | **SHARED — no single writer** | `G-011`. Cross-cutting, so `cto` signs off on shape. **`cxo` owns the standard these must meet and never edits them.** **Two standing limits.** (1) **The two-design-systems question is not resolved by this row** — no agent deletes, merges or migrates one system into the other without a ruling, now **joint `cxo` + `cto`**. (2) A colour token lives in **three synced places** (tokens JSON, `lib/themes/app_theme.dart`, `tokens/*.dart`) — a write that changes one and not the others is a **defect, not a partial change** |
| `lib/main.dart`, `lib/firebase_options.dart` | **UNOWNED** | Nobody writes it, except `devops` for iOS bootstrap requirements raised by an actual App Review rejection |
| `lib/l10n/**`, all `*.g.dart`, all `*.freezed.dart` | **GENERATED** | Never hand-edited by anyone. Regenerate with `dart run build_runner build -d`. **`content-manager` supplies the strings and the keys; a developer wires them.** Phase 0 `P0-5` makes regeneration a `devops`-owned commit step |

**~~The open partition question.~~ CLOSED 2026-09-05 by `T-047` under `G-015`, applied by
`G-016`.** `G-012`'s seven stacks were mapped onto the five leads `G-014` fixes; the table above
is the result and it is authoritative. **`analyst` no longer confirms slices ticket by ticket** —
that instruction existed because the map was a guess, and it is not one any more. What remains
genuinely open is narrower and is recorded rather than hidden:

- **`B.9` Organiser dashboard.** `STACKS.md` §4 argues it belongs to Play & Places (`team-lead-2`);
  `G-013` argues it is the unstaffed **admin-dashboard project**, not an app feature. **Both
  readings stand and neither is ruled** — the coupling graph is silent on a persona with no
  slice, so `T-047` deliberately did not choose. It is a product-scope call for `cpo`/`pm` with
  the CEO. **Do not resolve it by assignment.**
- **`D4` Commerce activation.** `team-lead-4` is named custodian; activating the stack is a `pm`
  decision with the CEO. The two dormant Commerce screens stay in `misc/` (`STACKS.md` §10.4).
- **Two preferences, priced and deliberately not re-litigated as defects.** `moderation` to lead 1
  costs **2** file-edges either way; `admin` to lead 4 costs **0** — `admin` has no cross-feature
  edges at all. `T-047` rejected-alternative 6 records both as preference, not error.

### Backend

**Verified against the tree 2026-08-27.** `supabase/` contains exactly three things:
`functions/`, `schema/`, and `.temp/`. **There is no `supabase/migrations/` directory** — an
earlier version of this table granted ownership of a path that does not exist.

| Path | Writer | Rule |
|---|---|---|
| Supabase — **all** tables, RLS, triggers, RPCs, views (184 tables, 336 policies, 71 views) | `senior-backend` | **Notifications included since 2026-09-05.** **Authors only — it never applies to production** (`019` / `G-002`: `cto` or the CEO). `cto` rules on shape (`021`); `senior-backend` builds it. This is the row that was UNOWNED when the audit found the live data leaks |
| `supabase/functions/**` — including `send-push-notification`, `broadcast-notification`, `detect-country` | `senior-backend` | Notification edge functions came with the merge. Its inherited memory is at `.claude/agent-memory/senior-backend/notifications-inherited/` |
| `supabase/schema/migrations/**` — 38 `.sql` files | `senior-backend` | Where schema SQL is actually written. **These 38 files are real migrations with real reasoning in their comment headers — they are not scratch** |
| `supabase/schema/snapshots/**`, `supabase/schema/*.sql`, `supabase/schema/schema.json` | `senior-backend` | Includes `notification_schema_snapshot.sql` — a notification artefact despite the generic directory name |
| `supabase/.temp/**` | **UNOWNED** | Supabase CLI scratch. Not authored by anyone; do not edit or commit |
| Supabase project `wtncuzcskpigqpmnxwws` — **reading** | open to every seat **except `qa` (NO READ)** | SELECT, `list_tables`, `get_advisors`, probing as `anon`/`authenticated`. Reading is how findings get verified |
| Supabase project `wtncuzcskpigqpmnxwws` — **writing** | `cto` only | **NOBODY except `cto`, under `G-002`'s conditions** (claim-comment posted and re-checked immediately before applying — `G-006` — authored and posted first, preconditions measured live, schema/privilege/definition only, verified and posted back after). **User-data mutation is CEO-only (`019`)** except security-remediation changes meeting `G-009`'s three tests. Everyone else: no `apply_migration`, no DDL, no data change, no policy or grant change — **however correct or urgent.** Decisions `019`, `G-002`, `G-006`, `G-009` |
| **The second Supabase project on the account** | **FORBIDDEN — NO READ** | Not ours. Never read, never write |

**For the authoritative statement of the migration situation, read `SCHEMA.md` §8 mismatch 7.
Do not restate it here or anywhere else.** That single-location rule exists because this fact
has been wrong in this repository twice, in up to eight documents at a time, each copy
re-derived rather than read.

### Tests, tooling, config

| Path | Writer | Rule |
|---|---|---|
| `test/**` | `senior-backend`, any `senior-frontend-N`, any `junior-frontend-N*` | Each may add tests **for code it owns**. **Nobody deletes another owner's test** |
| `pubspec.yaml` — version string | `devops` | Owns bumps, including **every mirrored copy** of the version |
| `pubspec.yaml` — dependencies | **UNOWNED** | Adding a dependency is an architectural decision; it needs a `DECISIONS.md` entry from `cto` first |
| `ios/**` | `devops` | Came with the `app-store-submission-fixer` merge. `senior-frontend-5` may change push entitlements and APNs config **and must say so in its status entry** so `devops` is not surprised at submission |
| `android/**` | **SHARED** — any `senior-frontend-N`, coordinated by leads | `G-007`. Manifest, native resources, Gradle. Was UNOWNED until that ruling, caught when a write was made against the UNOWNED cell |
| `web/**` | **UNOWNED** | Except `senior-frontend-5` for the web-push service worker |
| `scripts/**` | `devops` | It owns `cloudflare-build.sh` |
| `.claude/agents/**` | **GENERATED** | Built by `agent/scripts/build-agents.sh` from `agent/roles/` + `.claude/bindings/`. **Never hand-edit** — `build-agents.sh --check` fails if it has drifted |
| `agent/roles/**`, `.claude/bindings/**`, `.claude/skills/**` | `analyst` | The seat definitions and their bindings. Closed loop — see §2 |
| `.claude/settings*.json`, `.mcp.json` | **UNOWNED** | **The CEO writes these.** No agent edits its own permissions or MCP wiring. This is a closed-loop rule with teeth: **an agent that can edit `settings.local.json` can grant itself anything in this table** |
| `.claude/agent-memory/<self>/**` | each seat, its own only | Every seat writes its own memory directory and **only** its own |
| `.claude/agent-memory/<other>/**` | **nobody** | Read to understand a teammate. Never write |
| `CLAUDE.md` | **UNOWNED** | **The CEO writes it.** Agents propose changes through `DECISIONS.md`; they do not edit it |

### Docs

| Path | Writer | Rule |
|---|---|---|
| `dabbler-docs/MANIFESTO.md`, `CONTRACT.md`, `agent/AGENTS.md`, `agent/WORKFLOWS.md` | `analyst` | The four closed-loop files — see §2. **`po` reads these to run its second gate and may never write them** |
| `dabbler-docs/DECISIONS.md` — governance (unprefixed, `G-`) | `analyst` | |
| `dabbler-docs/DECISIONS.md` — technical (`T-nnn`) | `cto` **A** | Append-only. Numbering rule in §9.3 |
| `dabbler-docs/DECISIONS.md` — product (`P-nnn`) | `cpo` **A** | Append-only |
| `dabbler-docs/DECISIONS.md` — experience (`D-nnn`) | `cxo` **A** | **New 2026-09-05.** Append-only. **`cxo` never starts a parallel decision store** — no `decisions/` directory, no separate design-system file. One file, four prefixes (§9.3) |
| `dabbler-docs/BRIEF.md`, `dabbler-docs/ROADMAP.md` | `cpo` | Filled from the business corpus in Notion — a real source. **Never inferred from code** |
| **The Notion business corpus** | `cpo` | **New 2026-09-05: `cpo` is its sole writer.** Its role file previously forbade writing it. Notion holds the core business documents — strategy, investment, monetisation; `dabbler-docs/` holds the business-**technical** documents. Two stores, one writer each, neither a copy of the other |
| `dabbler-docs/PROJECT_STATE.md` | `analyst` | The measured record. `cto`, `cpo`, `cxo` and `pm` **read it rather than re-measuring** |
| `dabbler-docs/ARCHITECTURE.md`, `CONVENTIONS.md` | `cto` | `CONVENTIONS.md` has a guard — see §9.2: a convention change requires a numbered decision, so a loosened standard is visible as a dated decision rather than a silent edit |
| `SCHEMA.md` §§1–8, §10 — **the measured census** | `analyst` | **SPLIT — see §9.1.** Every line carries a verification date and a regeneration query |
| `SCHEMA.md` §11 — **target state and standards** | `cto` | What the schema *should* be |
| `dabbler-docs/LEARN.md` | **append-only by every seat, except `po` (read-only)** | `po` reviews governance documents; appending there would make the reviewer an author of what it later approves. **When it has a lesson it hands the append-ready text to `analyst`, who appends it.** That is not a workaround — the content lands and the boundary holds. See §6 |
| `agent/STATUS.md` | `analyst` | Reconciles it. **This is the channel the CEO reads** |
| `agent/status/<self>.md` | each seat, its own only | **No seat writes another seat's status file.** All 17 exist as of 2026-09-05 |
| `agent/status/archive/**` | `analyst` | The logs of retired seats. **Never edited** — they are the record of what those seats did |
| `dabbler-docs/NOTIFICATIONS.md` | `senior-frontend-5` | Inherited with the notification client. **Known drifted** — its subject was rewritten after it was written |
| `dabbler-docs/LOCATION.md` | **UNOWNED** | |
| `dabbler-docs/RESEARCH.md` | `analyst` curates; `cpo`, `cto`, `cxo` **A** | The single living research file |

### Release and the board

| Path | Writer | Rule |
|---|---|---|
| Git — commit, branch, merge, tag, push | `devops` | **No other seat runs a write git command** |
| Branch `main` | **nobody** | **Nobody pushes it directly, `devops` included.** It deploys straight to app.dabbler.pro. Reached only by PR from `Canary` — and under the **standing freeze (`P-030`)** a PR into `main` may be opened but **is not merged without the CEO's explicit go-ahead in the moment** |
| Cloudflare Pages project `webapp` | `devops` | |
| App Store Connect, Google Play Console | `devops` | Came with the `devops` merge. `content-manager` supplies listing copy; `devops` files it |
| Jira — **creating, editing or re-wording any ticket** | `po` | **Sole writer. No exception.** The `pm` says what is needed; the `po` writes it |
| Jira — transitions into **In Progress** and **In Development** | the owning `team-lead-N` | |
| Jira — transition into **In Review** | the developer who finished the work | |
| Jira — the review verdict, and transitions into **In Testing** and **Done** | `po` | The gate that came from `po`. **Comment first, transition second** |
| Jira — bug reports and test findings | `qa` **A** | Comments and new bugs. **`qa` never fixes and never transitions another seat's ticket** |

---
## 4. THE FOUR CONTENDED FILES — AND THE SHARED SURFACES

Four files are touched by nearly every piece of feature work, so they are where parallel
agents collide. They are **not** owned by any one agent, and they are **not** UNOWNED.
They have a protocol instead.

> **Amended 2026-09-05.** The same protocol now also governs three **shared surfaces** —
> `lib/core/**`, `lib/data/**`, and `lib/themes/**`/`lib/design_system/**`/`lib/utils/**`/
> `lib/widgets/**` — plus one oversized file, `profile_providers.dart` (870 lines, three
> domains, consumed by `social` and `home`). **One agent inside at a time; append your block;
> touch nothing else; no junior enters any of them.**
>
> **Why this section now matters more than it did.** It was written when one
> `flutter-feature-agent` wrote all Dart. There are now **sixteen developers**. At that count
> `lib/app/app_router.dart` — 1,712 lines, 85 routes, touched by nearly every feature — stops
> being a safety rule and becomes **the schedule**. `G-012`'s Phase 0 split is the fix and it
> is not yet authorised.

| File | Why every agent needs it |
|---|---|
| `lib/app/app_router.dart` | 1,712 LOC, 85 `GoRoute`, 1 `StatefulShellRoute.indexedStack` (`:746`). Every new screen adds an import and a route. **Re-measured 2026-09-04 at `dabbler-code` `c46b5c5`; was 1,745.** |
| `lib/providers.dart` | CLAUDE.md requires every new provider to be exported here. |
| `lib/core/config/feature_flags.dart` | CLAUDE.md requires every new feature to be gated here. |
| `lib/core/config/supabase_config.dart` | Every table, bucket and RPC name lives here; hardcoding them is forbidden. |

**The protocol:**

1. **Append, do not restructure.** Add your import, your route, your provider export, your
   constant. Do not reorder, regroup, reformat, or "tidy" the file while you are in it.
   A diff that touches 40 lines to add 3 cannot be reviewed and will collide with
   everyone else's.
2. **One agent in one of these files at a time.** If two tasks both need `app_router.dart`,
   they are sequenced, not parallelised. The Workflows doc names who sequences them.
3. **Your feature's block only.** Do not fix a neighbouring feature's route while you are
   in the router, however obviously wrong it looks. Report it instead — see §5.
4. **Never delete another agent's entry.** Removing a dead flag or a dead route is
   cleanup work with its own ticket and its own owner. It is not a side effect of your
   feature.
5. **`supabase_config.dart` is add-only for constants.** Changing an existing constant's
   *value* changes which table the whole app talks to. That needs a `DECISIONS.md` entry.
   The audit found two constants pointing at buckets that do not exist
   (`venueImagesBucket = 'venue-images'`, plus a hardcoded `'avatars'`). **Both are fixed as of
   `c46b5c5`** — `avatarsBucket = 'Avatar'`, `venueImagesBucket = 'venue'`
   (`supabase_config.dart:3-4`). The rule stands; the example is now history.

**Why this is strict.** The audit measured what happens without it: 98 dead feature flags,
54 unreferenced route constants, and 1,745 lines in one router. **All three were since cleaned
up** — KAN-32 deleted the 98 flags (17 remain) and 75 route constants (1 unused remains), KAN-31
deleted 5 dead feature slices, and the router is 1,712 LOC. The numbers here are the evidence for
the protocol, not the current state. That is what a year of
"while I'm in here" produces.

---

## 5. THE INFORMATION CONTRACT — what gets learned where

Five destinations. Each has one test. **An entry that fails its test is not written** —
writing it anyway is how a living document becomes noise nobody reads.

| Destination | What goes there | The test |
|---|---|---|
| `docs/LEARN.md` | A lesson that generalises past the task that produced it — a bug class, a trap that cost a session, a preference discovered by being corrected, a rule that turned out to have an exception. | **"Would reading this before starting have saved time?"** If no, it does not belong. |
| `docs/DECISIONS.md` | A choice with reasoning, where a different choice was genuinely available. | **"Could a reasonable agent have chosen otherwise?"** If there was only one option, it is not a decision — it is just what happened, and it goes to STATUS. |
| `agent/STATUS.md` and `agent/status/<agent>.md` | What happened in a task: what changed, what was verified, what is left. | **"Does the PO need to know this happened?"** Every completed task passes this. Write it as part of the task, never as an afterthought. |
| `docs/PROJECT_STATE.md` | Measured state of the codebase, with a `file:line` or a scanner number. | **"Did I measure it?"** If it was estimated, inferred, or remembered, it does not go in. analyst only. |
| `.claude/agent-memory/<self>/` | What *you* need to not re-derive next session — schema facts, confirmed false positives, PO decisions in your area. | **"Will I waste time re-deriving this?"** Not for anything the repo already records. |

**Three clarifications that have already caused confusion:**

- **A decision and a lesson are different things.** "We chose Result over Either" is a
  decision. "Mixing Result and Either inside one slice produces silent type confusion
  that the analyzer does not catch" is a lesson. The first goes to DECISIONS, the second
  to LEARN. If you find yourself writing both in one paragraph, split it.
- **A status entry is not a lesson.** "Fixed the push 401" is status. "Server-triggered
  push fails with 401 when the shared secret is fetched per-request instead of per-warm-
  instance" is a lesson. Status answers *what happened*; LEARN answers *what to do
  differently*.
- **Reporting is not fixing.** When you find a problem outside your scope — and you will,
  constantly, in a codebase this size — the deliverable is the report, not the fix. Name
  it in your status entry with a `file:line`. Do not reach across the boundary because
  the fix looked small.

---

## 6. APPEND-ONLY DISCIPLINE

**`docs/LEARN.md` is append-only, by every agent including analyst — except
`po`, which is read-only on it.** It reviews this file; authoring in it would let
the reviewer approve its own writing. It routes lessons through analyst instead.

Never restructure it. Never reorder it. Never deduplicate it. Never "improve" it.
Never fix its formatting. The PO owns its shape.

Add your entry to the section it belongs to — not necessarily the end of the file. If no
section fits, add one at the end rather than forcing your lesson into a section that is
nearly right.

**Correcting an existing line is not appending.** If a lesson in LEARN.md has become
wrong, you do not edit it and you do not delete it. You append a new dated entry saying
what changed and why, and you report the contradiction in your status entry. The old
entry stays. Knowing that we once believed something false, and when we stopped, is
information — and an agent that silently rewrites history takes that away from everyone
who reads the file later.

`agent/status/<agent>.md` files are append-only within themselves: newest entry at the
top, older entries never edited.

---

## 7. WHAT IS NEVER WRITTEN DOWN

Not in docs, not in code, not in memory, not in a status entry, not in a Jira comment,
not in an App Store reply.

- **Secrets and credentials** — service-role keys, API keys with write scope, SMTP
  credentials, signing certificates, FCM server keys, private keys of any kind.
- **`.env` contents.** The file is gitignored and untracked; both verified by command.
  Keep it that way. Naming a variable is fine — `SUPABASE_ANON_KEY is required by the
  build` is useful. Pasting its value is not.
- **User PII** — real names, emails, phone numbers, addresses, avatars, message or
  notification bodies, device tokens. The audit needed to establish that
  `v_notifications_feed` exposed 609 rows across 49 recipients; it recorded *those two
  numbers* and never a single row of content. Do the same: characterise the exposure,
  never reproduce it.
- **Unredacted third-party material** — anything under an NDA or from a partner.

**Two things that look like secrets and are not**, so nobody wastes a session on them:
the Firebase `AIza…` keys in `lib/firebase_options.dart` and
`android/app/google-services.json` are public client identifiers and are meant to ship;
and `service_role` inside `supabase/functions/**` is server-side and correct. Neither is
a leak. Both are documented in `PROJECT_STATE.md` §9.

**If a secret does reach the repo:** stop, tell the PO immediately, and do not commit
over it. Rotating the credential comes first; scrubbing history is devops's job
and needs the PO's decision.

---

## 8. AMENDING THIS CONTRACT

An agent that finds this file wrong — a path with no owner it needs, a rule that blocks
legitimate work, a cell that contradicts its own definition — **reports it and stops.**
It does not edit this file. That is the closed-loop rule, and it applies to the contract
most of all.

The report goes in the agent's status entry and names the exact row. analyst
amends the matrix, logs the amendment in `DECISIONS.md`, and updates `Last updated` above.

**When a new agent is hired**, this matrix is amended *before* the agent runs, not after.
An agent whose paths are not in the matrix has no scope, and an agent with no scope
writes wherever it likes — which is the situation this file exists to prevent.

---

## 9. THE LEADERSHIP SPLIT — three rules it needs to hold

Added 2026-08-27 with `cpo` and `cto`. The split is right in principle; these three guards
are what stop it creating new failures.

### 9.1 `SCHEMA.md` is split by section, not handed over whole

**Why.** `cto.md:20` tells the CTO to *"read `PROJECT_STATE.md` rather than re-measuring —
the Analyst establishes what is true; you decide what should be true."* **`SCHEMA.md` §§1–8
are the same kind of artefact as `PROJECT_STATE.md`** — a census of what the database
currently contains, every figure carrying a verification date and a regeneration query.

If a decision-maker owns a measurement file, one of two things happens: it inherits a
re-measurement duty its own charter tells it not to perform, or nobody re-runs the queries
and the file rots. **This specific file has already been wrong twice** — 49 views that were
71, and "no schema history" against a 237-row ledger — and only re-measurement caught either.

So: **§§1–8 and §10 stay with analyst. §11 (target state and standards) is the
CTO's.** The CTO decides the RLS standard, the `security_invoker` default, which `nearby`
generation is canonical, and whether the 30 zero-policy tables are intentional. The Analyst
reports what is there.

Same logic for `ARCHITECTURE.md` §3b, whose flow-reachability figures are measured: the CTO
owns the file and its direction; the measured numbers inside it are re-measured by
analyst and must not be hand-edited.

### 9.2 A CTO convention change requires a numbered decision

**The closed-loop problem the split creates.** `po` runs Gate 2 against
`CONVENTIONS.md` and `ARCHITECTURE.md`. If the CTO owns those **and** directs the executive
work being judged, the CTO can edit the standard its own directed work is graded against.

That cannot happen today: analyst owns those files and is read-only over code, so it
gains nothing from loosening a rule. **A CTO gains something — its executives' work passes.**
This is precisely the failure §2 exists to prevent, and it is new.

**Not a blocker; a guard.** A CTO change to `CONVENTIONS.md` or `ARCHITECTURE.md` **must
carry a numbered `T-nnn` entry in `DECISIONS.md`**, and `po`'s Gate 2 reads the
decision log alongside the convention file. A relaxed standard then appears as a dated
decision with reasoning a reviewer can question — not a silent edit that turns yesterday's
violation into today's compliance.

### 9.2b Attribution names roles, never agent instances

*Added 2026-08-28, on the CTO's correction. Applies to every document in `docs/` and to
every agent's memory.*

**Write `cto`, never `cto-4` / `cto-5` / `cto-6`.** An instance name is an implementation
detail of how a session happened to be spawned. It means nothing to a reader six months out,
and it means something actively wrong: a record naming three `cto-N` reads as three CTOs, or
as three agents whose definitions someone will go looking for and not find. **The roster in
`AGENTS.md` is the list of names that exist.**

This was not hypothetical. On 2026-08-28 **71 instance-name references** had accumulated
across `PROJECT_STATE.md`, `SCHEMA.md`, `LEARN.md`, `CONTRACT.md` and two memory files before
anyone noticed. All collapsed to the role.

**When collapsing changes the meaning, fix the sentence, not the name.** Several entries
recorded one CTO instance correcting another; written as one role they read as
self-contradiction. The truthful form is sequential — *"the CTO ruled on this twice in
separate passes"* — because that is what happened: **one seat, two sittings.** Do not
reintroduce the instance number to preserve the drama of the correction.

### 9.3 `DECISIONS.md` numbering — prefixes, because four writers will collide

One sequence with several appenders produces two agents both writing `021` in parallel
sessions. From 2026-08-27:

| Prefix | Owner | Domain |
|---|---|---|
| *(unprefixed)* `001`–`021` | analyst | the existing governance sequence, now closed |
| `G-nnn` | analyst **and the Listener** | governance, process, the agent system |
| `D-nnn` | `cxo` | **added 2026-09-05** — experience, design system, look and feel |
| `T-nnn` | cto | architecture, schema, stack, engineering standards |
| `P-nnn` | cpo | product, scope, roadmap, monetisation |

Each agent numbers within its own prefix, so no coordination is needed and the prefix names
the domain at a glance. **Precedence is unchanged: the newest dated ACTIVE entry wins,
regardless of prefix.** A cross-domain supersede needs both owners to agree, or the PO decides.

**Why `G-nnn` has two appenders, named 2026-08-28 after a real collision (see errata).**
analyst's `G-nnn` entries are audit-derived: a process gap it found and is recording.
The assistant's are PO-direct: a structural or authority decision the PO made live in chat
(granting an agent new authority, filling a vacant seat), transcribed at the point of decision
rather than reached by any agent's own reasoning. Different origin, same domain, so they share
the prefix rather than getting a fifth one — but **no other agent appends to `G-nnn`.** A
leadership agent whose own ruling belongs in governance writes it as its own prefix (`T-nnn`
for `cto`, `P-nnn` for `cpo`) even when the topic brushes against process — as `T-026` does,
ruled on by `cto`, not filed as a fourth `G` writer.

---

## 10. WHAT THIS FILE HAS BEEN WRONG ABOUT

| When | What was wrong | Fix |
|---|---|---|
| 2026-08-26 → 2026-09-05 | **The matrix was one column per agent.** That was legible at 4 seats and unreadable at 17 — 15 columns of `R` on almost every row, hiding the one cell that carried meaning. It had already produced two documented errors of exactly this kind: a `LEARN.md` cell that gained a stray `A` as a **column-width artefact**, and cells that disagreed with the rule written beside them | Restructured to **writer-per-path**: read is open by default, each row names its single writer, and `NO READ` is stated where it is withheld. The column-artefact class of bug is now impossible because there are no columns |
| 2026-08-28 → 2026-09-05 | The `LEARN.md` reviewer exception was written against `task-auditor`, a seat that no longer exists | Rule carried to `po`, which inherited the review gate. **The exception was not dropped with the seat** — it is the mechanism, not the seat, that matters |


Kept deliberately. A permission matrix that silently corrects itself teaches readers to
trust it more than it has earned.

| Date | Error | Correction |
|---|---|---|
| 2026-08-26 → corrected 2026-08-27 | Granted `supabase/migrations/**` to notifications-specialist and called it "currently empty". **The directory does not exist.** The real tree is `supabase/schema/**` and had no row at all | Phantom row replaced with four real rows, verified against the tree |
| 2026-08-26 → corrected 2026-08-27 | `docs/README.md` had no row, and there is no catch-all | Row added under Docs |
| 2026-08-26 → corrected 2026-08-27 | No column for `task-auditor` | Column added to all five tables |
| 2026-08-27 → corrected same day | The `docs/LEARN.md` row read `A A A A **A**` — `task-auditor` granted append on a file it reviews, contradicting §2, the §1 note and §6. **A column-width artefact**: a uniform row gained a fifth `A` when the column was inserted, rather than a deliberate `R` | Cell set to `R`, with the exception and its routing stated |
| 2026-08-26 → corrected 2026-08-27 | "49 views" in the Supabase row | **71.** The 71/49/19 correction reached `SCHEMA.md` and `PROJECT_STATE.md` but not this file |
| 2026-08-27 | Sole ownership of `ARCHITECTURE.md`, `SCHEMA.md`, `CONVENTIONS.md`, `ROADMAP.md`, `BRIEF.md` and all of `DECISIONS.md` sat with master-analyst — **one agent holding both measurement and decision authority** | Split with `cpo`/`cto` per §9. `SCHEMA.md` divided by section rather than handed over whole, plus two structural guards |
| 2026-08-26 → corrected 2026-08-28 | **`docs/LEARN.md` gave `CP` and `CT` an `R` while the same row's rule read "append-only by every agent — with one exception: `task-auditor` is `R`."** The cells and the sentence beside them disagreed, and `cpo` and `cto` had both been appending to `LEARN.md` all along — correctly, per the rule, in violation of their own cells | Cells corrected to `A`. **The prose was right and the grid was wrong**, which is the reverse of the usual failure and the reason it survived: a reader checking the rule got the right answer, so nobody checked the row |
| 2026-08-28 | While adding `BO`/`FA`, the mechanical pass defaulted both columns to `cto`'s value — a read-only posture on most rows, but it silently handed the new agents `W` on `ARCHITECTURE.md`, `SCHEMA.md` §11, `CONVENTIONS.md` and **`docs/status/cto.md`**, and `A` on `DECISIONS.md` and `RESEARCH.md` | All six corrected to `R` before the edit was reported. **A default is a grant.** Filling a new agent's column by analogy with an existing one is how scope leaks in without a decision — G-003 named code and schema paths, so those are the only rows where either got `W` |
| 2026-08-28 | §9.3 said `G-nnn` had one appender, master-analyst. In practice **two others wrote to it the same day**: the assistant (`G-002`, `G-003` — PO-direct decisions, transcribed live) and `cto` (a QA/CI ruling, briefly filed as a second `G-003`). The rule and reality had already diverged before the collision made it visible | Colliding entry renumbered to `T-026` (cto's own prefix — the ruling was an engineering standard, not process). §9.3 amended to name the assistant as `G-nnn`'s second appender for PO-direct decisions specifically; every other agent's own-domain ruling stays in its own prefix even when the topic brushes governance |

**How the phantom path survived being written and self-reviewed:** nothing in the loop was
required to look at the filesystem. The row was internally consistent, plausibly worded, and
cited a real ticket. It was caught by a reviewer who ran `ls`. **A document can be coherent
and still be wrong about the tree** — the check that catches it has to touch reality.

---

## 11. ~~OPEN PROPOSAL~~ — RESOLVED 2026-08-28 by `DECISIONS.md` G-003

**The PO chose option A and filled both seats.** `backend-owner` (KAN-70) takes the database
paths; `flutter-feature-agent` (KAN-71) takes the 23 slices. The matrix in §3 is amended and
both carry `W` on their paths and **no production-write authority whatsoever** — that stays
with `cto` under `019`/`G-002`, exactly as this proposal asked.

**Kept below rather than deleted, because the reasoning is the precedent.** The next time a
gate item has no permitted writer, the argument that moved it was structural, not throughput:
*the work could not be sliced into anything an existing agent may author.* Option B — widening
a scoped agent under time pressure — was rejected and should be rejected again.

### The proposal as written

*Raised by `cto` 2026-08-28. Written here by `master-analyst` as a **proposal, not an
amendment**. Nothing in §3 changes until the PO accepts one of the options below. Per §8, a
matrix row is amended by the PO, and per `DECISIONS.md` 019 no agent writes the production
database at all.*

### The gap, stated precisely

Two promotion-gate items are database work. §3 rows 116 and 119–122 make every database path
**UNOWNED** except notification migrations. So the gate that blocks promotion cannot be
cleared by any agent currently in the matrix. This is not an oversight to be patched quietly
— it is the system working as designed and surfacing a hiring decision.

Two agents independently reached this boundary and both stopped at it rather than granting
themselves the path. That is §2 doing its job, and it is the right outcome: **an agent that
can widen its own scope to clear its own gate has no gate.**

### What the PO is being asked to decide

| Option | What it means | Cost |
|---|---|---|
| **A — hire a backend owner** | A new agent owns `supabase/schema/**` and the live schema. Already raised as **KAN-26** | A seventh agent, a new column, a definition to write |
| **B — widen `notifications-specialist`** | It already writes notification migrations and holds the only working DB-write precedent | Its name stops describing its scope, and it becomes the de facto backend owner without the review that hiring one would get |
| **C — PO executes the SQL** | Agents write and review the migration; the PO applies it | No new agent; the PO is the bottleneck on every schema change |
| **D — leave it UNOWNED** | The gate items are cleared by the PO or not at all | Honest, and it means the gate stays shut until the PO has time |

**The strongest argument for A is structural, not throughput** *(added 2026-08-28, `cto`)*.
The highest-severity finding on the board (SEC-16 / KAN-67) is one migration against
**schema-level** configuration — table and view grants plus `ALTER DEFAULT PRIVILEGES` in
`public`. There is no per-view `REVOKE` that fixes it. It therefore **cannot be sliced into
anything an existing agent may author**: carving it by view ownership yields two migrations
that each half-fix one setting, with the `pg_default_acl` half belonging to neither owner.
That is a gap in the matrix, not a queue that is moving too slowly — and it is the version
of this decision a PO can act on.

`master-analyst`'s recommendation: **A**, and not B. B is the cheapest thing to type and the
most expensive thing to live with — it converts a scoped agent into an unscoped one by
accretion, and the matrix stops describing the system. If A is too much agent for the amount
of work, **C** is the honest small answer; D is acceptable and should be chosen explicitly
rather than arrived at by neglect.

**Whoever gets the path, `DECISIONS.md` 019 still stands:** writing migration files in the
repo and writing the production database are different permissions, and this proposal is
only about the first.

### Constraint on whoever owns it

Any writer of this path inherits `SCHEMA.md` §8 mismatch 7 as the authoritative statement of
the migration situation: **237 rows in `supabase_migrations.schema_migrations` versus 38
tracked `.sql` files**, only one of which contains a `CREATE TABLE`. The repo is not a
reconstruction of the live schema and must not be treated as one.

