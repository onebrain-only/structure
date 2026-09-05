# agent/status/analyst.md — `analyst` status log

**Header corrected 2026-09-05 (`G-016`).** This file was named for `master-analyst`, the seat's
name before the 2026-09-05 restructure. **The seat was renamed to `analyst`; the charter is
unchanged** (`AGENTS.md` §2, rename map). **Entries below dated before 2026-09-05 say
`master-analyst` and were deliberately not rewritten** — rewriting a log to match a later
reorganisation falsifies it.

**Owner:** `analyst` — **this agent, and only this agent, writes here.**
Every other agent reads it. `analyst` reads the other agents' files to reconcile
`agent/STATUS.md`; it does not write into them.

**Peer, not checkpoint.** `analyst` sits in the leadership layer alongside `cto`, `cpo` and
`cxo` (`AGENTS.md` §1). It does not review other agents' work — `po` does, exclusively — and is
not a default recipient of routine task completions.

**Purpose:** The detail behind this agent's work. `agent/STATUS.md` is the summary the PO
reads; this file is where the specifics live.

---

## SCOPE

Audits, project state, findings, the governance documents, and the reconciliation of every
other agent's entries into `agent/STATUS.md`. **Read-only against the codebase** — its writes
are documentation and its own memory.

## THE RULE

The status entry is **part of the task, not offered afterwards.** It is the last thing
written before the agent closes, and the agent may not report DONE without it. A task that
ends in a refusal, a diagnosis, or an unanswered question still gets an entry — those are
the ones most likely to be skipped and most needed.

## FORMAT — newest first

```
## YYYY-MM-DD — KAN-NN — Title
**Task:** what was asked
**Did:** what actually changed, with file:line or commit
**Did not:** what was out of scope or deliberately left
**Not verified:** stated explicitly, never omitted
**Handoff:** which agent picks this up, or none
```

---

# LOG

## 2026-08-27 — KAN-7 / KAN-14 / KAN-2 — Correcting two false findings
**Task:** Three tickets failed review. Correct the security scope and the schema-history claim.

**Did:**
- Verified both failures against the live DB before writing. All figures confirmed: 71/49/19 views, 237 ledger rows.
- Rewrote `SCHEMA.md` §2 as a full census — every one of 71 views has a position (EXPOSED 19 / definer+uid 8 / anon-revoked 23 / invoker 21), with the reproduction **and its control query**.
- Corrected `PROJECT_STATE.md` SEC-06 (HIGH → **CRITICAL**), CFG-02 (marked CORRECTED TWICE, both wrong versions kept), the exec summary, and open question 6.
- Corrected `MANIFESTO.md` §6, `ARCHITECTURE.md`, `WORKFLOWS.md`, `STATUS.md`, `CONTRACT.md`.
- Corrected the KAN-4 comment: `sports_history_screen.dart` has 3 importers and is live — only the class is dead. Someone working from Jira would have deleted a live file.
- Wrote **DECISIONS 019** (no agent writes production) and **020** (count populations, never infer from a tool's finding count); **MANIFESTO R14/R15**; `CONTRACT.md` read-open/write-never rows; 2 new `LEARN.md` lessons.
- Rescoped KAN-33 on its ticket — as filed it would have had someone author a baseline against a live 237-row ledger.

**Did not:** write anything to the production database. Every probe was a SELECT under `set local role`. Did not over-correct MANIFESTO's "no reproducible environment" claim — the reviewer was right that it survives.

**Got wrong:** the schema-history finding, **twice**. First "directory empty", then "wrong location". Both were filesystem searches; the ledger was one query away throughout. Recorded in `SCHEMA.md` §10 and `PROJECT_STATE.md` rather than quietly fixed.

**Not verified:** row counts for 12 of the 19 exposed views.

**Handoff:** `task-auditor` for In Review. notifications-specialist for KAN-36/37/38. PO for KAN-33 rescope.

## 2026-08-27 — KAN-8 — CONTRACT.md rework after failed review
**Task:** `task-auditor` failed KAN-8. Three items: the phantom `supabase/migrations/**` row, the missing `docs/README.md` row, the missing `task-auditor` column.

**Did:**
- Ran `ls supabase/` **before** writing. `supabase/migrations/` does not exist. Replaced the phantom row with five verified rows for the real tree — `schema/migrations/**` (38 files), `schema/snapshots/**`, top-level `schema/*.sql`, `schema.json`, `.temp/**`.
- Added `docs/README.md` and `docs/status/task-auditor.md` rows; added a `TA` column to all five matrix tables; added a Jira row recording that TA owns the board and I may transition only as far as In Review.
- §2 closed-loop now covers TA from the opposite direction: it judges others' work so it writes nothing they could be judged on.
- New §9 "What this file has been wrong about" — errata kept deliberately, because a matrix that silently self-corrects earns unearned trust.
- **Found the error had propagated to eight documents**, not one. Corrected `WORKFLOWS`, `ARCHITECTURE`, `STATUS`, `SCHEMA`, `MANIFESTO`, `ROADMAP`, `PROJECT_STATE` (×2).
- **Corrected the underlying finding**: KAN-33 claimed no schema history. There are 38 real migrations + a 65KB snapshot, 5,787 lines, 41 git-tracked, several of them security fixes. The real problem is that they are outside the CLI's path and lack timestamp prefixes. Commented the correction on KAN-33 and recommended it drop from HIGH.
- Appended 3 lessons to `LEARN.md`; added `task-auditor` to `AGENTS.md` (v0.3).
- Moved KAN-8, 16, 17, 18, 19, 20, 21, 22, 23 and the KAN-5 epic to **In Review**.

**Did not:** claim the rework is Done. My terminal state is In Review; `task-auditor` decides.

**Got wrong in the rework itself:** my bulk edit produced a **blank cell** in the Docs table — in the file whose §1 forbids blank cells. Caught by grepping `\|\s*\|`, fixed by splitting into two owned rows. Recorded rather than quietly repaired.

**Not verified:** the apply order of the 38 migrations against the live schema — filename order is alphabetical and probably not the order applied. Whether the top-level `add_comment_attachments.sql` is current or stale.

**Handoff:** `task-auditor` for the In Review queue. PO for KAN-33's rescope.

## 2026-08-26 — KAN-5 — Governance docs system
**Task:** Fill the 12 empty spec files in `docs/`, using `/Users/moatazmustapha/Desktop/Moataz_Next/docs` as a reference for the **pattern only**, never for content. One Jira child task per file.

**Did:**
- `CONTRACT.md` — permission matrix over every path × 4 agents, **zero blank cells**. Extended the closed-loop rule to `.claude/settings*.json` and `.mcp.json`, reasoning that an agent able to edit `settings.local.json` can grant itself any permission the matrix denies.
- `DECISIONS.md` — 18 entries. Verified three seeds against live systems rather than transcribing from memory: `trg_strip_signup_password` confirmed on `auth.users`; `JSONS/` confirmed dead (0 references); `.mcp.json` confirmed gitignored at `.gitignore:12`.
- `LEARN.md` — 21 lessons in 4 sections, append rule written into the file itself.
- `MANIFESTO.md` — 13 rules, each graded HOLDS / PARTIAL / NOT ENFORCED against measured counts.
- `CONVENTIONS.md`, `WORKFLOWS.md`, `SCHEMA.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `AGENTS.md` v0.2, `STATUS.md`, this file.
- `SCHEMA.md` verified entirely live via Supabase MCP — 184 tables, ~180 RPCs, ~200 triggers, 4 buckets, 16 extensions.

**New findings this task produced, beyond filling templates:**
- **112 of 113 feature flags are hardcoded `true`.** Only `enableRewards` is `false`. The file is not a control surface — even the 10 read flags are `const` and cannot gate anything off.
- **Two flags contradict their own comments** — `enablePlayerGameCreation = true; // Players CANNOT create games in MVP` and `enableOrganiserGameJoining = true; // Organisers CANNOT join games`. Both gate live code.
- **Five generations of `nearby_*` RPCs**, not four. All still callable; generation 4 (`rpc_get_nearby_*`) is current.
- **Trigger ordering hacks are load-bearing** — `trg_90_*` and `trg_zz_*` prefixes force execution order. Renaming one changes when it fires.
- **Six suspected duplicate trigger pairs**, marked unconfirmed — each needs its function body read before anything is dropped.
- **The analytics backend already exists.** `rpc_track_event` + `analytics_events` with policies; the gap is entirely client-side.

**Did not:**
- **Did not fill `BRIEF.md` with inferred content.** Product intent is not derivable from a year-old codebase full of abandoned directions; the file is `NEEDS PO INPUT` throughout with the questions listed.
- **Did not remove the banners from the other three agents' `status/*.md` files.** Those belong to their agents (`CONTRACT.md` §3), and the banner says "filled by its owning agent" — removing it would claim a file is filled when it is not. I confirmed all three scopes match their agent definitions and left the files alone.
- Did not fix anything found. Read-only holds.

**Not verified:** Cloudflare Preview variables (not readable from the repo — KAN-35). Whether the 30 zero-policy tables are deliberately definer-RPC-only (KAN-26). Whether the two contradictory flag comments or their values are the stale half.

**Handoff:** PO for four blocking decisions — roster shape (KAN-16), rewards (KAN-29), clean-arch stack (KAN-30), flag CUT/DEFER sign-off (KAN-22). notifications-specialist for KAN-24/25/26/27.

## 2026-08-26 — KAN-2 — Full project audit
**Task:** Establish ground truth across 13 questions. Read-only; findings only, no fixes.

**Did:** Ran the `project-audit` skill's five phases. Produced `docs/PROJECT_STATE.md` — 62 findings, executive summary, 25-slice completion table, incompleteness register, mandatory "looks bad but is actually fine" section (15 entries), and a handoff table. Created 8 audit child tasks and 12 follow-up tickets. Seeded 4 memory files.

**The finding that mattered:** probing as `anon` — no login — returned **609 notifications across 49 recipients** from `v_notifications_feed`, plus 9 open moderation tickets and the safety overview. `SECURITY DEFINER` views bypassing RLS. Escalated immediately as P0 rather than filed quietly.

**Corrections to the baseline I was given:** dead flags are 98/113 not 97 (`enablePushNotifications` is read only inside `feature_flags.dart`; the identical `UserSettings` field is unrelated). Orphan screens are 21 classes across 12 files, not 9 — the scanner substring-matched class names *and* missed relative imports, producing false positives in both directions. God files are 140 not 143 (three are generated l10n).

**Did not:** Fix anything, including the two P0 leaks. Did not delete the `rewards` or clean-arch stacks despite proving them unreachable — measurement establishes state, not intent, and 19,560 LOC is not a recoverable mistake.

**Not verified:** Cloudflare Preview variables. The intent behind the 30 zero-policy tables. Whether the six duplicate-looking trigger pairs are genuinely duplicates.

**Handoff:** notifications-specialist (KAN-24, 25, 26, 27) · a Flutter cleanup agent (KAN-31, 32) · QA (KAN-34) · version-control (KAN-35) · PO (KAN-29, 30).

---

## 2026-08-29 — backlog close-out (KAN-41 correction · KAN-88 filed · §2a reconciled · INDEX §9a)

**What I was asked to do:** clear my own open backlog — the KAN-41 nav-graph overstatement,
`SCHEMA.md` §2a's stale CRITICAL/OPEN language, and anything else of mine still reading as open.

**1. Both KAN-41 navigation dead-ends withdrawn; one real one found.**
`flutter-feature-agent-5` and `task-auditor-11` both flagged that NAV-02's
`onboarding_sports_screen.dart` sits in a closed legacy loop. I verified it myself rather than
accept it on report — and found the finding was wrong on a second, prior count I had not been
told about: **`:194` does not reference `onboardingBasicInfo` at all.** It reads
`context.go(RoutePaths.createUserInfo)`, a declared route. Re-checking NAV-01 for the same defect
found the same thing: `social_search_screen.dart:1811` reads
`context.push(RoutePaths.gameDetail(game.id))` and resolves correctly.

Searching for the literal instead of the constant name found the **real** dead end:
`notifications_screen_v2.dart:518` pushes `/games/<id>`, the only remaining `/games/` literal in
`lib/`, matching no route, **on a live bottom-nav screen** — strictly worse than either row it
replaces, and a defect neither withdrawn row would have led anyone to. **NAV-01a, KAN-88**,
owner `flutter-feature-agent`.

**Root cause, and it is an instrument fault not an attention lapse.** Constant-name matching and
`file:line` collection ran as **two passes**, joined without re-opening the cited line. Both
passes were individually correct; the **join** invented the findings. Recorded in `docs/LEARN.md`
and in `audit-false-positives.md` so neither row can come back.

**2. `SCHEMA.md` §2a reconciled.** The three rows read CRITICAL/OPEN while the note directly
beneath them said KAN-56 had closed them. Labels struck, arithmetic line moved to zero, exposure
table retained as the historical record. `version-control` had flagged this rather than editing
prose it does not own — that handoff worked exactly as intended and its note now says so.

**3. `INDEX.md` §9a — all 62 prefixed decisions indexed** with `DECISIONS.md` line numbers. A gap
in the answer desk: `G-008` was unanswerable without reading 3,500 lines. Also corrected two stale
claims — **"23 of 25 slices UNOWNED"** (superseded by `G-003`/`G-007`; 9 agents now, not 7) and
§11's blocking list, which still led with read leaks that are closed while SEC-16/SEC-13/SEC-17
are the live items.

**4. The status log has collapsed, and it is not only my file.** Entries dated 2026-08-28 or later
across `docs/status/`: `cpo` 1, `version-control` 1, everyone else **0**. `STATUS.md` stops on
2026-08-27 — through the two busiest days of the project. **I did not backfill it**, because
writing entries for work I did not do is fabrication and would defeat the point of the log.
A GAP NOTICE naming exactly what is missing and who owes it is now at the top of `STATUS.md`,
with the one PO decision it needs. `backend-owner` and `flutter-feature-agent` have **no status
file at all**.

**Not verified.** NAV-01a is confirmed **statically only** — no route pattern matches the literal;
I did not run the app and tap the row. The other 31 declared-never-navigated routes were **not**
re-derived for the same join defect; only the two dead-end rows were. I did **not** re-query the
database for the §2a reconciliation — I relied on two independent same-day confirmations already
in the record. The 62 decision titles are indexed but **not re-read for mutual consistency**;
silent supersession conflicts may exist.

**Files changed:** `docs/PROJECT_STATE.md` (§14e, §20b, changelog run 1z) · `docs/SCHEMA.md` (§2a,
allowlist note) · `docs/STATUS.md` (gap notice + 3 entries) · `docs/LEARN.md` (appended) ·
`docs/status/master-analyst.md` · `.claude/agent-memory/master-analyst/INDEX.md` ·
`.claude/agent-memory/master-analyst/audit-false-positives.md`. **Jira:** KAN-88 created,
KAN-41 commented. **No code touched.**

---

## 2026-09-05 — Applied `T-047`'s measured ownership partition; `CONTRACT.md` §3 amended and all 20 developer role files corrected

**Task.** From `team-lead`/master session. `EFFORT: high`. Apply `DECISIONS.md` `T-047`'s
five-lead partition under `G-015` Ruling 2, close the coverage gap it exposed, and correct the
generated role files that carried the superseded slice lists. **Applying a decision, not making
one** — the CEO ruled for `cto`'s measurement.

**Done.**

1. **`dabbler-docs/CONTRACT.md:141–226`** — §3 "Application code" rewritten. The provisional
   census-derived slice→writer table is deleted; `T-047`'s partition replaces it with an added
   **UNOWNED** row. **All 20 `lib/features/` directories are now named**; the superseded table
   named 18. Three rows of the path table were also amended: `lib/data/**` (records that `T-047`
   did not measure it), `app_router.dart` (`P0-3b` split), `profile_providers.dart` (re-measured
   importer set), plus the `l10n`/generated row (`P0-5`). The "open partition question" trailer is
   marked CLOSED and replaced by the three things that genuinely remain open.
2. **`agent/AGENTS.md` §1** — the "Stacks, and who holds them" table gains a fourth column,
   *Slices it writes*, plus a paragraph stating that the `D`-labels are a feature taxonomy and
   **not** the write boundary, and naming the two seats where they diverge (lead 3 is Identity not
   Venues; lead 5 is Notifications only). **§2** — `senior-frontend-1..5` row, parallelism
   paragraph, shared-surfaces paragraph, plus a new paragraph recording the three UNOWNED feature
   directories.
3. **All 20 role files** under `agent/roles/` rewritten: `team-lead-1..5` (the "Which code these
   stacks touch" section replaced), `senior-frontend-1..5` and `junior-frontend-1a..5b` (slice
   path lists, per-lead warnings, and the "Proposed mapping, not yet confirmed" trailer).
   `agent/scripts/build-agents.sh` run; **`--check` clean across all 30 seats, exit 0.**
4. **`dabbler-docs/DECISIONS.md:5432`** — **`G-016`** appended, ACTIVE.
5. **This file** — header corrected from `master-analyst`.

**Measured, not accepted.** Every file/LOC figure in `T-047` was independently reproduced at
`c46b5c5`: lead 1 167 / 69,485 · lead 2 91 / 29,872 · lead 3 53 / 13,127 · lead 4 6 / 1,579 ·
lead 5 19 / 4,259 · unassigned 15 / 7,529 · total 351 / 125,851. **All rows match exactly.**
One figure was corrected on my own measurement: `profile_providers.dart` has **32** importers
spanning leads 1, 2 and 5, not "leads 1 and 2" as §3 said under the old map.

**The hazard this closes.** `home` — 7 files, 3,403 LOC, holding `main_navigation_screen.dart`,
the app shell — had **no writer** in `CONTRACT.md` §3. A ticket assigned against it hit an
unowned slice. `core` was likewise absent. Both are now named: `home` to lead 1, `core` as
UNOWNED platform residue with a stated reason.

**Not verified.** I did not re-derive `T-047`'s **coupling edge weights** — the `E(A→B)` counts
(16, 8, 7, 18-internal, etc.) are `cto`'s and I reproduced the file/LOC totals, not the graph.
I did not re-check `PROJECT_STATE.md` against the tree in this session. I did not measure
`lib/data/`'s 71 repositories or the ~130 tables absent from `supabase_config.dart` — both remain
`cto`'s stated gaps. I did not open a Jira ticket for this work; it arrived as a direct brief.
**No code touched.**

**Files changed:** `dabbler-docs/CONTRACT.md` · `dabbler-docs/DECISIONS.md` (`G-016`) ·
`agent/AGENTS.md` · `agent/roles/team-lead-{1..5}.md` ·
`agent/roles/senior-frontend-{1..5}.md` · `agent/roles/junior-frontend-{1a,1b,…,5b}.md` ·
`.claude/agents/*.md` (regenerated, 20 files) · `agent/status/analyst.md`.

**Correction, same day, raised by `team-lead`.** The importer total was **32**, not 31 — an
arithmetic slip in my own summation; the per-slice breakdown was right and the finding
(collision spans leads 1, 2 and 5) is unaffected. Corrected in `CONTRACT.md` §3,
`DECISIONS.md` `G-016`, `senior-frontend-1.md`, `junior-frontend-1a/1b.md`, this entry and
memory. The five non-feature importers are now named in `CONTRACT.md` rather than counted:
`lib/main.dart`, `lib/app/app_router.dart`, `lib/widgets/app_top_bar.dart`,
`lib/core/services/auth_service.dart`, `lib/core/auth/session_cleanup.dart` — **the router and
the top bar being among them makes it worse than a feature-level collision.** Rebuilt;
`--check` ok × 30.

---

## 2026-09-05 — `CONTRACT.md` §4.1: the Phase 0 exclusive grant (`G-017`)

**Brief:** `team-lead`. Phase 0's named executor, `senior-frontend-3`, was forbidden by
`CONTRACT.md` §3/§4 from writing every surface Phase 0 requires. `cto` anticipated it at
`STACKS.md:739–741` — **but a plan cannot grant permission, only the contract can.**

**Done.** Added **`CONTRACT.md` §4.1** (`dabbler-docs/CONTRACT.md:358–443`), inside §4 because it
is an exception to §4's discipline, not a new regime. Nine paths named individually with the
status each returns to. Exclusion stated as plainly as the grant, with `STACKS.md` §10.0's
parallel-work allowlist carried across. Expiry = `STACKS.md` §10.6's landing test quoted verbatim
in substance **plus** `po` transitioning all five tickets to Done — automatic, no further decision.
Logged as **`G-017`**. Header `Last updated` moved.

**Two paths the brief did not name, added because omitting them re-blocks the executor at ticket
two:** `lib/providers.dart` (CONTENDED; `P0-2` rewrites an import there) and **other leads'
feature slices** (`P0-2`'s 38 importers span 13 of 20 feature dirs; `P0-4` moves seven screens
*into* leads 2 and 4's slices). Also added `test/app/route_inventory_test.dart` — §3 scopes a
developer's tests to code it owns and the router is nobody's — and
`lib/core/providers/geo_providers.dart`.

**What I did NOT verify.** I did not re-run the 38-importer or 13-of-20 counts, the 25-of-69
router-import figure, or the 11-files-in-`lib/data/` figure — all are `cto`'s at `c46b5c5`
(`STACKS.md` §9b, §10.2) and I took them as given for a permissions amendment. I did not check
the current worktree against `c46b5c5`. I did not open or edit any Jira ticket, `STACKS.md`, or
any `T-nnn`. **No code touched. Nothing committed or pushed — changes are in the working tree for
`cto`/`devops`.**

**Files changed:** `Dabbler/dabbler-docs/CONTRACT.md` · `Dabbler/dabbler-docs/DECISIONS.md`
(`G-017`) · `agent/status/analyst.md`.

---

## 2026-09-05 — The board becomes six columns; the documents are corrected to match

**What I did.** The CEO built a six-column board organised by Jira's three `statusCategory`
values, replacing the seven-column model the restructure spec assumed. `team-lead` verified
the mapping and the transition ids against the live board and briefed me. I corrected every
governance document that named a column which does not exist — a seat calling
`transitionJiraIssue` with `In Development` or `In Testing` would have failed on the first
real ticket.

**What I touched.**
- `agent/WORKFLOWS.md` §1 (`:19–50`) — lifecycle, three-state table, the dropped-column note,
  the CEO's-labels note, the who-moves-it mapping. §2 (`:93`, `:101–120`) — columns row and the
  six-row id table replacing the four-column paragraph. §3 (`:141`) and §5 (`:207–225`) —
  review-gate outcome and W1 steps 2–4 now pass to `QA-Test`, fail to `Ready`.
- `Dabbler/dabbler-docs/CONTRACT.md` §3 (`:300–303`) — the three "Release and the board"
  transition rows, plus one new row naming the six statuses.
- `agent/roles/po.md` (`:46–92`) — board section rewritten with exact names, live ids, the
  `Ready`=2 / `QA-Test`=3 pattern warning, and the read-the-ids-back rule restated here
  because this seat does the transitioning.
- `agent/roles/qa.md` (`:153–158`) — QA's work arrives in `QA-Test`; `qa` still transitions
  nothing.
- `agent/AGENTS.md` (`:174`) — `team-lead-1..5` owns one transition, not two.
- `.claude/bindings/team-lead-1..5.yml` — same correction in the seat descriptions;
  `.claude/agents/**` regenerated with `agent/scripts/build-agents.sh` (30 seats built).
- `agent/skills/task-review/SKILL.md` — id table completed to six; the verdict flow said
  Done / To Do, which contradicts `WORKFLOWS.md` §3 and `po.md`. Corrected to
  `QA-Test` / `Ready` under the precedence rule, and `task-auditor` in the verdict template
  replaced with `po`.
- `Dabbler/dabbler-docs/DECISIONS.md` (`:5600–5697`) — **G-018**, two rulings: the six-column
  model with its reasoning and live ids, and the standing constraint that nothing is pushed to
  any remote except One Brain until the CEO lifts it.

**What I decided.** Extending the correction into `agent/skills/task-review/SKILL.md` and
`agent/AGENTS.md`, neither named in the brief. Both carried board-status claims that would
have contradicted the corrected documents, and my role requires correcting the losing document
in the same session.

**What I did not do.** No Jira write of any kind. No board reconfiguration — the board is
correct as built. No `T-nnn` entry edited. No commit: everything is left in the working tree,
and `Dabbler/dabbler-docs` is its own git repo so its changes are invisible to One Brain's
`git status`.

**What I did not verify.** The transition ids and the status-to-category mapping are
`team-lead`'s measurement, taken as given — I made no API call this session. Whether any
existing KAN ticket currently sits in a status the old documents named.

**Blocked:** nothing.

## 2026-09-05 — `G-019`: Phase 0 grant amended (defect in `G-017`)

**Task:** from `team-lead` — `team-lead-3` found that `G-017`'s grant could not satisfy `P0-2`'s
own exit condition. Verified against the tree; the defect is real.

**Measured at HEAD (`dabbler-code`):**
- `grep -rl 'misc/data/datasources' test/` → `test/data/repositories/profiles_repository_impl_test.dart` — **1 file**, the only one.
- Totals: **39** importing files — 26 in `lib/features/` (13 dirs), **10** in `lib/data/`, 1 in `test/`, 2 (`lib/providers.dart`, `lib/core/providers/geo_providers.dart`).

**Written:**
- `Dabbler/dabbler-docs/CONTRACT.md:395` — new §4.1 grant row for that test file, **import-path rewrite only** (two lines, `:7`/`:8`). Not a grant over `test/`.
- `Dabbler/dabbler-docs/CONTRACT.md:391` — 11 → **10** files in `lib/data/`.
- `Dabbler/dabbler-docs/CONTRACT.md:398` — 38 → **39** importing files.
- `Dabbler/dabbler-docs/CONTRACT.md:4` — `Last updated` line.
- `Dabbler/dabbler-docs/DECISIONS.md` — **`G-019`**, ACTIVE, appended. `G-017` itself not edited.

**Open, owned by `cto`:** `STACKS.md` §10.2 still reads "38 importing files plus 11 in `lib/data/`".
`analyst` does not write `STACKS.md`. `G-017`'s prose at `DECISIONS.md:5580` also says 38; left as
the historical record, corrected in `G-019`.

**Not done:** nothing committed — left in the working tree, as instructed.
