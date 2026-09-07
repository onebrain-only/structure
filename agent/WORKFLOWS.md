# agent/WORKFLOWS.md — Workflows and Handoffs

**Owner:** `po` (write) · all agents (read) — moved from `analyst` 2026-09-06, `G-022`
**Last updated:** 2026-09-06 — W1 corrected: `Development` is a real column, not a dropped
one (see below); ownership table given its `Development` row and `Done` corrected to `qa`.
§2's column line changed from restating the column list to citing §1's table, after the
restatement went stale there while §1 was fixed — one fact, one place, from here on.
Previously: 2026-09-05, W6 added (regeneration), W1 amended to match.
**Purpose:** The procedure. `AGENTS.md` carries the shape of the roster; this carries how
a task that crosses two or three agents actually moves, end to end.

---

## 1. THE TASK LIFECYCLE

**Jira is the single source of truth for progress.** Not the terminal, not an agent's
final message, not this repo. If the board does not show it, it did not happen.

```
CEO request
   → Epic (the container)
      → child Tasks (the trackable units)
         → To Do → Ready → In Progress / Development → In Review → QA-Test → Done
```

**Seven columns inside three states — corrected 2026-09-06.** This document previously said
six and stated flatly that `Development` "does not exist and is not coming back." That was
wrong: `Development` is a real status (`status id 10010`, transition id `4`, category **In
Progress**), and `getTransitionsForJiraIssue`/JQL confirm real tickets sitting there
(`KAN-119`, `KAN-128`, `KAN-132`, `KAN-136` as of 2026-09-06) — the first time it has been
used. **Correction, same day:** an earlier version of this line credited the transitions to
`team-lead-1` and `team-lead-4` by name. `team-lead-4` denied making any transition this
session, and the Jira changelog cannot settle it either way — every API call in this workspace
authenticates as the one account (`Moataz Mustapha`), so `changelog.histories[].author` never
names the agent seat that issued the call, only the shared credential. **Do not cite the Jira
changelog as evidence of which seat performed an action** — it proves a transition happened
and when, never who. Jira has exactly three `statusCategory` values; the board's columns live
inside them. A column is a position within a state, never a state of its own:

| State (Jira `statusCategory`) | Columns |
|---|---|
| **To Do** | `To Do` · `Ready` |
| **In Progress** | `In Progress` · `Development` · `In Review` · `QA-Test` |
| **Done** | `Done` |

**The CEO's spoken labels are not the board's names.** He says *Backlog* for `To Do`,
*Development* for `In Progress` (a conversational label, not to be confused with the real
`Development` status above — check `getTransitionsForJiraIssue` rather than assuming which one
a spoken instruction means), *Testing* for `QA-Test`. Documents and API calls carry the exact
status names above, never the spoken ones.

**Who moves a ticket into each column** — a transition made by the wrong seat is a process
failure, not a shortcut:

| Into | Moved by |
|---|---|
| To Do | `po` |
| Ready | `po` |
| In Progress | the owning `team-lead-N` |
| Development | the lead owning the **content**, not the directory a file sits in (`T-066`, ruled 2026-09-07, not yet committed — a slice's route module, e.g., can live under `lib/app/routes/` outside every slice's own tree; ownership follows what the file is about). **Correction, 2026-09-06:** the lead does not hand-assign the developer — the CEO's `YOU PULL, YOU DO NOT WAIT` ruling (in every developer role file) has developers pulling their own next ticket from `Ready` when free, with no lead in that loop. The lead's actual job at this transition is (a) confirming the ticket is genuinely ready to start (slice state, sequencing on any contended/shared file per §4) and (b) making the transition itself once a developer has picked it up — not choosing which developer. Two leads independently naming different executors for the same ticket today (`KAN-119`) is the direct cost of this ambiguity; the ticket's named executor is whoever actually pulled it, verified on the ticket, not whoever a lead's brief assumed. **`qa` writes the test script for the ticket during `Development`, in parallel with the developer — not after, and not at `QA-Test`.** |
| In Review | the developer who finished it |
| QA-Test | `po` — **only after its review gate passes** (§3) |
| Done | `qa` |

**Writing is `po`-only.** No other seat creates, edits or re-words a ticket. The `pm` says
what is needed; the `po` writes it.

**Three standing rules on every ticket:**

- **No ticket without a `due_date`.** A ticket with no date is not scheduled, it is a wish.
- **The date comes from capacity, not estimation.** Capacity is reported by the owning
  `team-lead-N`. The `po` may not estimate it and may not ask a developer directly. See
  `agent/skills/capacity-to-date/SKILL.md` for how a lead's capacity number becomes a
  `due_date` without either side estimating.
- **A slot frees on acceptance, not delivery.** A developer who has handed work to review is
  still holding that slot until the gate passes it. This is what stops the board filling with
  work that is "done" and not accepted.

**Rules that keep that true:**

1. **A task is transitioned to In Progress when work starts**, not retroactively.
2. **Findings are commented on the ticket as the work produces them**, not saved for a
   summary at the end. The board should tell the story without anyone opening the repo.
3. **A task moves to Done only when its acceptance criteria are met** — or to In Review
   first, where the work needs a second pair of eyes (§3).
4. **An Epic closes only when its children are Done.** If children remain open by design —
   follow-ups, deferred work — say so explicitly in the closing comment. A green Epic
   above open CRITICAL children is a lie the board tells.
5. **No task is complete until the agent has appended to its own
   `agent/status/<name>.md`.** **The path is resolved from the One Brain workspace
   root, never from the project tree the agent happens to be standing in** — today
   that root is `/Users/moatazmustapha/Desktop/Thebes`, so the entry goes to
   `/Users/moatazmustapha/Desktop/Thebes/agent/status/<name>.md` and the 30 role
   files carry it absolute for exactly this reason. **The failure this prevents is
   silent:** on 2026-09-05 `po` ran with its working directory set to
   `Dabbler/dabbler-code`, and the "create the file if it does not exist" clause below
   turned a relative path into a brand-new `dabbler-code/agent/status/po.md` that
   nothing reads. No error was raised. This binds every agent, on every task, with no
   exemption for small work. The entry records **what it did, what it touched,
   what it decided, and what is blocked**. **Create the file if it does not
   exist** — several seats have none yet, and a missing file is not a reason to
   skip the entry. A task that ends with no change still gets one: a refusal, a
   question returned, a diagnosis. Write that explicitly so the silence reads as
   deliberate rather than as an agent that stopped early. The principle is
   `MANIFESTO.md` §5; this is the operational form of it.

---

## 2. JIRA CONVENTIONS

| Setting | Value |
|---|---|
| Site | `dabbler.atlassian.net` |
| cloudId | `18c8e9f5-d139-4e03-b5d8-89122cc14937` |
| Project key | `KAN` — "Dabbler Team", **team-managed** |
| Columns | See §1's table — do not restate the list here; a second copy is exactly how `Development` went missing from this section before. |

**Epics do not render as cards on a team-managed board. Tasks do.**

This is the rule that was got wrong once, and it is why every trackable unit is filed as
`issueTypeName: "Task"` with a `parent` Epic. An Epic alone is invisible to the person
watching the board — the work exists in the API and nowhere a human is looking.

**Transition ids are project configuration, not constants.** These are the live values, read
back from `getTransitionsForJiraIssue` with `includeUnavailableTransitions: true` on
2026-09-05:

| Status name (exact) | status id | transition id | Category |
|---|---|---|---|
| `To Do` | 10004 | `11` | To Do |
| `Ready` | 10008 | `2` | To Do |
| `In Progress` | 10005 | `21` | In Progress |
| `Development` | 10010 | `4` | In Progress |
| `In Review` | 10006 | `31` | In Progress |
| `QA-Test` | 10009 | `3` | In Progress |
| `Done` | 10007 | `41` | Done |

**`Ready` is `2` and `QA-Test` is `3` — they break the 11/21/31/41 pattern.** Anyone who
assumes the pattern guesses wrong, which is exactly why the next rule exists.

**Always call `getTransitionsForJiraIssue` and read the ids back** — never write a remembered
number into a transition call. Any id in any document here is a convenience, not an
authority; the board carried four columns until the 2026-09-05 restructure and the table
above will go stale the same way.

**Issue keys are not assigned sequentially.** Creating twelve tickets does not give you
twelve consecutive keys — KAN-5, 8, 10, 12 were interleaved with another epic's children in
the same session. **Never write a ticket key into a comment before the ticket exists.**
Create first, read the returned key, then reference it. Getting this wrong requires editing
a comment afterwards, which is recoverable but visible.

**Labels in use:** `audit`, `security`, `follow-up`, `bug`, `cleanup`, `config`,
`quality`, `po-decision`.

### A silent data-loss trap in the Jira tooling — read before editing any ticket

**A markdown table inside a numbered list item silently destroys the content it is part
of, and the API reports success.** Found by `po` on 2026-09-06 while correcting KAN-128's
AC 1: the edit dropped the acceptance criterion's **entire** body, and the tool returned
no error. It was caught only because `po` re-read the ticket immediately afterwards.

The cause is the markdown→ADF conversion, so it is not specific to one ticket, one field
or one seat. Any agent writing an acceptance criterion with a table in it — which is the
natural way to express a per-function or per-file rule — will hit it.

**Two rules, both cheap:**

1. **Never nest a table inside a numbered or bulleted list item.** Pull the table out into
   its own section and reference it from the list item. This is what `po` did to recover
   KAN-128, and the ticket reads better for it.
2. **Re-read every ticket immediately after editing it.** Not the edit response — the
   ticket. A success code from this API is not evidence the content landed. `po` adopted
   this as standing practice after the incident; it is the general rule, not one seat's.

**Why it is in this file rather than in a status log:** the failure is invisible at the
moment of writing and the loss is total, so the seat that hits it next will not know to
look unless it was told beforehand.

---

## 3. THE REVIEW GATE

`In Review` is not decoration. A ticket sitting there has a claim attached to it — "this
is done" — and the gate is where that claim is tested rather than accepted.

**The gate belongs to `po`** since 2026-09-05, when `task-auditor` was merged into it.
**Reviewing is a distinct act with its own skill.** Use the `task-review` skill, which applies
two gates: the ticket's own acceptance criteria, and alignment with the governance docs. The
outcome is a written verdict and a transition — to **QA-Test**, handed to `qa`, or back to
**Ready** with what is missing. There is no third outcome.

**The `po` writes the criteria and also judges against them.** That closed loop is deliberate
(`AGENTS.md` §2) and is held by two rules: the `po` never reviews work it executed, and where
a criterion turns out to be badly written **the verdict says so** rather than failing the
developer for the PO's wording.

**What goes through review:**

| Work | Review required? |
|---|---|
| Anything touching a contended file (§7) | **Yes** |
| Any schema or RLS change | **Yes** |
| Anything that closes a `security`-labelled ticket | **Yes** |
| A release to `main` | **Yes** — the launch gate is the review |
| Documentation owned by the writer | No — straight to Done |
| An audit refresh | No — `analyst` owns the output |

**The reviewer is never the author.** An agent does not review its own ticket. Where the
`po` cannot review — because it executed the work, which should not happen — the review
escalates to the `pm`. **Skipping is never the same as being unable to run it**, and the
ticket says which happened.

---

## 4. THE HANDOFF RULE

**Agents do not brief each other, and no agent hands execution to another.** Briefs come from
the Temporary Compatibility Dispatcher. A worker needing a scope or acceptance decision asks
**`po`** directly; a general domain decision goes up as an exception request for one redirect.

**The no-delegation rule is contractual, not enforced by the harness.** No binding restricts
tools, and runtime evidence shows the harness blocks only *named teammate → named teammate*
spawning — `fork` and unnamed subagent creation are available. **You may not call `Agent` or
`fork` to create an executor, and you may not use `SendMessage` to hand your work to another
seat.** Nothing will stop you; the rule is the constraint.

**Amended 2026-09-06 by the CEO (`G-024`).** Until today every question and every finished
report came back to the Listener, and that was never written anywhere — no role file
mentions the Listener at all. It happened because the Listener dispatches, so agents reply
to their caller. The cost is measurable: every report enters the Listener's context and is
re-sent on every request after it. **The hierarchy exists; use it.**

**Corrected 2026-09-05.** This section used to read *"Everything routes through the master…
reports to `master-analyst` / the orchestrating session."* That was wrong twice over:
`AGENTS.md` §1 has said since `G-005` that **nothing routes through `analyst`** — it measures,
it does not route — and the `orchestrator` seat that the phrase also pointed at **no longer
exists.**

**The Listener is the distribution layer**, and it is a behaviour in the main session's
thinking rather than a seat in the tree. It writes **directly** to whichever seat owns the
question — a senior developer included — and never down a chain of managers. An agent
finishing a step reports to the Listener, which decides what happens next. Agent A does not
hand work straight to Agent B.

Use the **`route-to-seat`** skill to decide who is concerned and to write the prompt.

**Why, given direct messaging is technically available:**

- **Subagents cannot spawn subagents.** Nesting is off by default and version-dependent, so
  a chain assembled from inside the chain breaks in a way that is hard to see. Parallelism
  and sequencing come from the top.
- **A silent fallback beats an error here.** `.claude/agents/` is registry-scoped to the
  working directory, and an unrecognised `subagent_type` falls back to a generic agent with
  no error raised. An agent-to-agent handoff can therefore land in a generic agent that
  answers plausibly and owns nothing.
- **A worker does not decide who executes next.** That is a routing decision, and after
  Wave 3 it belongs to the Dispatcher — on evidence, or not at all. **`po` owns task analysis
  and the review gate; a team lead owns readiness, the `Development` transition, capacity and
  contention.** **A lead does not choose or assign the developer** (`YOU PULL`, §1).

**The channels, corrected 2026-09-07 (Wave 3):**

| Direction | Goes to | Example |
|---|---|---|
| **Down — a brief** | the **Temporary Compatibility Dispatcher** (the Main Session), and only it | dispatching work from the CEO's word |
| **Up — scope, acceptance, work definition, criteria** | **`po`**, directly. `po` answers directly | "this acceptance criterion cannot be met" · "this needs a second sitting" |
| **Up — a general domain decision outside your authority** | a **structured exception request** to the Dispatcher, which redirects **once** | "this needs an architecture call nobody has made" |
| **Standing authorised direct routes** | the named authority, directly | `backend-N` → `cto` for `G-028` confirmation |
| **Sideways — a factual question** | the **peer**, directly (`grill-peer`) | "does the notification schema already have a `read_at` column?" |
| **Cross-capability work you discovered** | a **structured routing request** to the Dispatcher (§4.1) | frontend finds the RPC does not exist |

**The team lead is no longer an escalation target for finding an executor.** It never chose
the developer (`YOU PULL`), and after Wave 3 it does not appear in any routing path. It keeps
its readiness, transition, capacity and contention duties — see §1 and §7.

**One redirect, then the Dispatcher exits.** After a redirect the authority talks to the
original worker directly. **Forbidden:** `Authority → Dispatcher → po → developer`, or any
chain where an answer is passed along rather than given.

**What still reaches the Dispatcher:** a dispute no single seat owns, anything touching the
CEO's own files, structured routing requests, and general exception requests. On 2026-09-05
`team-lead-3` and `devops` disagreed on whether `KAN-126` was on Phase 0's critical path.
Neither could settle it; `CONTRACT.md:378` did. **That is the shape of it, and it is rare.**

---

## 4.1 STRUCTURED ROUTING REQUEST — TEMPORARY, WAVE 3

> **TEMPORARY. Exit: Wave 6.** Capability queues replace this.
>
> **Wave 4 made these records durable.** A routing request is written through
> `agent/state/store.py` and gets an `rr-<uuid>` id; an exception gets `exc-<uuid>`. They survive
> session loss, which prompt text did not. **They are still not a queue** — nothing claims from
> them, nothing pulls from them, nothing orders them, and `selected_seat` stays null until MODEL C
> evidence determines one.

**A worker that discovers work for another capability does not hand it over.** Direct
execution delegation is prohibited (§4). Instead it returns a structured request:

```
ORIGINATING WORK ITEM:  KAN-nnn
REQUIRED CAPABILITY:    backend | frontend | content | qa | devops | ...
DISCOVERED SCOPE:       what is actually needed, in one or two sentences
DEPENDENCY / BLOCKER:   what it blocks, or what blocks it
RAISED_BY:              the seat raising it
RETURN_TO:              where the result should go
```

**The discovering worker names the capability. It does not name the seat** — that is the
Dispatcher's job, and only on evidence (`route-to-seat`).

**Jira authority is unchanged.** If genuinely new work must be authored, the request goes to
**`po`**, which writes it. **A developer does not create or edit tickets.**

**Blockers, since Wave 4:** a structural blocker may become a **dependency record** —
`source BLOCKS target`, one canonical direction, `IS_BLOCKED_BY` derived by query and never
stored as a second record. Written through `store.py` under the Product graph lock, which is
what rejects cycles and duplicate edges. Continue to name the blocker in a ticket comment where
the current workflow already requires one, citing the `dep-<id>`.

**Satisfaction is not something you write.** An edge carries `completion_condition: DONE`, so a
prerequisite sitting in review has satisfied nothing. Whether it is satisfied is derived once
canonical lifecycle exists (Wave 5). **Blockers recorded before Wave 4 stay as ticket comments —
there is no backfill**, because inferring past relationships from comment prose would be
fabrication.

### The result comes back directly

**The Dispatcher is not in the technical return path.** The receiving seat sends its result to
`RETURN_TO` **directly** via `SendMessage` when that seat is addressable in the same session.

**When `RETURN_TO` is not addressable** — a different session, or an identity that no longer
resolves — the Dispatcher may re-wake the originating seat with the result as context. That is
a **COMPATIBILITY RE-WAKE**, and it must be called that. **It is not direct messaging**, and
cross-session `SendMessage` does not exist. The exception and routing records live only in
prompt context until Wave 4 gives them durable state.

---

## 5. NAMED WORKFLOWS

### W1 — A feature change

1. **`po`** writes the ticket with testable acceptance criteria and a `due_date` taken from
   the owning lead's capacity. It moves it to **Ready**.
2. **`team-lead-N`** confirms the ticket is genuinely ready to start — the slice's state with
   **`analyst`** rather than assuming it from the stack name, and sequencing against any
   contended or shared file per §7 — and splits it into subtasks along the **frontend /
   backend** line, which is what the pairs are: Dart and the app to a `frontend-N`, schema,
   migrations, RLS, RPCs and edge functions to a `backend-N`.

   **The lead does not choose which developer takes it.** Per §1's `Development` row and the
   CEO's `YOU PULL, YOU DO NOT WAIT` ruling of 2026-09-06, a developer pulls its own next
   ticket from `Ready` when free, and the lead makes the transition once one has. **There is no
   task-shape routing by seniority** — `senior-frontend`, `junior-frontend` and `senior-backend`
   were retired the same day, and no `frontend-N` is senior to another.

   *(Corrected 2026-09-07. This step previously had the lead hand-assign each subtask by task
   shape, which contradicted §1's own correction inside this file.)*
3. **The developer** implements, following the build order (`MANIFESTO.md` §2): database →
   constants → repository → providers → screen → route. Writes tests for what it built, runs
   `flutter analyze` and `flutter test`, and **pastes the output rather than summarising it.**
   **It commits hand-written source only — generated output is `devops`'s, at step 7 (W6).**
   Where the change touches a Freezed model, a Riverpod generator or an `.arb` file, it may run
   `build_runner` locally to make `analyze` pass, but **leaves the regenerated files out of the
   handoff and says in the ticket that regeneration is owed.** Moves to **In Review**.
4. **`po`** runs the review gate (§3). Pass → **QA-Test**. Fail → back to **Ready** with a
   rework brief.
5. **`qa`** executes the testing story it wrote when the task was dispatched, against the
   running app. Bugs go back to the owning developer, never fixed by `qa`.
6. **`cxo`** judges the experience if the change is user-visible — a separate question from
   whether it works.
7. **`devops`** regenerates if regeneration is owed — **W6**, a separate commit of its own —
   then commits, pushes `Canary`, and verifies canary.dabbler.pro.

| Step | Seat | Receives | Produces | Done when |
|---|---|---|---|---|
| 1 | `po` | The request | A ticket with criteria and a date | Criteria are testable; date came from capacity |
| 2 | `team-lead-N` | A Ready ticket | Readiness confirmed; work split frontend/backend | Slice state checked, contention sequenced, `Development` transitioned once a developer has pulled it. **The lead does not choose the developer** |
| 3 | developer | A subtask | Code through step 6 of the build order, **hand-written source only** | A route reaches it; `analyze` 0 errors; `test` passes; **no `*.g.dart` / `*.freezed.dart` in the diff** |
| 4 | `po` | The diff | Verdict | QA-Test, or back to Ready |
| 5 | `qa` | Passed work | Testing story executed | Bugs filed, or none found and said so |
| 6 | `cxo` | User-visible change | Experience verdict | Rule named, or nothing to raise |
| 7 | `devops` | Approved work | **Regeneration commit if owed (W6)**, then a verified Canary deploy | Generated output is its own commit; **the site shows it** |

**Step 2 is where money is saved or wasted.** A junior given senior work produces a rewrite;
a senior given junior work is burned budget. The test is the work, never the queue.

### W2 — A schema change

1. Backend agent inspects live state first — `list_tables`, `get_advisors`, and a probe as
   `anon`. **Never work from the migration file alone**; the remote is the truth, and
   **`SCHEMA.md` §8 mismatch 7 is the authoritative statement of the migration situation —
   read it, do not restate it.** In brief: 237 migrations are applied per
   `supabase_migrations.schema_migrations`; the 38 `.sql` files tracked at
   `supabase/schema/` are outside the path the CLI reads, so `db diff` and
   `migration list` see nothing.
2. Writes the change **as a migration**, plus its RLS policies in the same change.
3. Verifies empirically: query as `anon` and as `authenticated`, with a control query that
   should return 0 to prove the probe works.
4. Adds any new identifier to `supabase_config.dart`.
5. Domain agent wires the client side.
6. Review gate — **mandatory** for schema.
7. devops ships.

| Step | Agent | Receives | Produces | Done when |
|---|---|---|---|---|
| 1 | backend agent | The requirement | Current live state | Probed, not assumed |
| 2 | backend agent | State | Migration + policies | Both in one change |
| 3 | backend agent | Applied change | Probe results | `anon` returns what it should, control returns 0 |
| 4 | backend agent | New names | Constants | No literal in `lib/` |
| 5 | domain agent | Constants | Client wiring | Reachable |
| 6 | reviewer | The change | Verdict | Approved |
| 7 | devops | Approved | Deploy | Verified on canary |

### W3 — A release

1. devops confirms the launch gate (`MANIFESTO.md` §4) — **all seven items**.
2. Bumps the version in every place it is duplicated.
3. Commits, pushes `Canary`.
4. **Waits for the Cloudflare build and loads canary.dabbler.pro.** A green push is not a
   green deploy.
5. Opens a PR from `Canary` into `main`. **Never a direct push.**
6. After merge, confirms app.dabbler.pro serves the change.

| Step | Agent | Receives | Produces | Done when |
|---|---|---|---|---|
| 1 | devops | Work on Canary | Gate check | All 7 pass, or STOP |
| 2 | devops | Gate passed | Version bump | Every copy updated |
| 3–4 | devops | Commit | Canary deploy | **canary.dabbler.pro shows it** |
| 5 | devops | Verified canary | PR | PR open, never a push |
| 6 | devops | Merge | Production | **app.dabbler.pro shows it** |

**As of 2026-08-26 this workflow cannot complete.** Launch gate item 4 fails — KAN-24 and
KAN-25 are open unauthenticated data leaks.

### W4 — An audit refresh

analyst alone. No handoffs.

1. Read the existing `PROJECT_STATE.md` first.
2. Run the `project-audit` skill's five phases.
3. Mark fixed findings `RESOLVED`, update moved numbers, tag new ones `NEW`.
4. Append a dated changelog row.
5. Report deltas against the baseline in `.claude/agent-memory/analyst/`, not
   absolutes.

Output is findings, never fixes. Each finding names the work it implies and who should own
it — an audit that does not become assignable work has failed.

### W5 — An App Store rejection

**Owned by `devops` since 2026-09-05**, when `devops` was merged into it.
Read `agent/roles/references/app-store-review.md` first — it carries that seat's operating
procedure, guardrails and per-rejection output format.

1. **`devops`** diagnoses against the cited guideline. **Identified, never guessed.**
2. If the fix is **inside `ios/**` or App Store Connect metadata**, `devops` makes it and
   drafts the Resolution Centre reply. **It never claims a fix it cannot evidence.**
3. If the fix is **outside that scope**, `devops` writes a report naming the slice and the
   change needed, and **stops.** It does not reach into code it does not own.
4. **`po`** turns that report into a ticket; the owning `team-lead-N` assigns it.
5. A rejection needing a **product** change goes to `cpo`; one needing an **architecture**
   change goes to `cto`. Fix the submission; escalate the direction.
6. **`devops`** bumps the version — **a rejected marketing version must be bumped, not just
   the build number** — builds, and uploads.

| Step | Seat | Receives | Produces | Done when |
|---|---|---|---|---|
| 1 | `devops` | Rejection text + guideline | A diagnosis naming the guideline and the offending behaviour | The guideline is identified, not guessed |
| 2 | `devops` | In-scope fix | The fix + a Resolution Centre reply | Change made, reply drafted, evidenced |
| 3 | `devops` | Out-of-scope fix | A report naming the slice. **STOPS** | The report exists; no out-of-scope edit was made |
| 4 | `po` | That report | A ticket | Criteria testable, owner named |
| 6 | `devops` | An approved fix | Version bump + build + upload | Build accepted by App Store Connect |

### W6 — Regenerating generated code

**Owned by `devops`.** Established by `STACKS.md` §10.5 under the Phase 0 authorisation
(`G-015`); `CONTRACT.md` §3:209 forward-references it. `CONTRACT.md` §3 already said generated
files are never hand-edited — it did not say **who regenerates them**, and this is that answer.

**It runs at commit time, after a developer's source-only commit.** It is not a step a developer
performs and not something that happens during implementation.

**Trigger:** a change to a Freezed model, a Riverpod generator, or an `.arb` file — anything whose
output lands in `lib/l10n/**`, `*.g.dart` or `*.freezed.dart` (`CONTRACT.md` §3:209).

1. **The developer commits hand-written source only** and does **not** commit `build_runner`
   output. It may run `build_runner` locally to make `flutter analyze` pass; the regenerated files
   stay out of the commit. It says in the ticket that regeneration is owed.
2. **`devops` runs `dart run build_runner build -d`** against that commit.
3. **`devops` commits the generated output as a separate commit containing nothing else** — no
   source, no formatting, no unrelated file. One commit, machine-written, reviewable by being
   skipped rather than read.
4. **`devops` runs `flutter analyze` and `flutter test` on the result** and pastes the output. A
   regeneration that breaks either is a finding, not a commit.
5. Then W1 step 7 proceeds: push `Canary`, verify canary.dabbler.pro.

| Step | Seat | Receives | Produces | Done when |
|---|---|---|---|---|
| 1 | developer | A source change | A commit of hand-written files only | **No `*.g.dart` / `*.freezed.dart` / `lib/l10n/**` in the diff**; the ticket says regeneration is owed |
| 2–3 | `devops` | That commit | A separate commit of generated output | The regeneration commit touches **only** generated paths |
| 4 | `devops` | Both commits | `analyze` + `test` output, pasted | 0 errors, tests pass |
| 5 | `devops` | A green tree | Canary deploy | **canary.dabbler.pro shows it** |

**Only one `build_runner` run at a time across the roster.** `devops` holds that lock; no other
seat runs it against `dabbler-code`. This is the same class of rule as §7 but a different surface —
§7 names four contended **files**, this names a contended **command**, and the four-file check at
dispatch does not catch it.

**Why the rule exists, measured 2026-09-05 at `dabbler-code` HEAD:** **52 generated files, 45 of
them under `lib/data/`** (`git ls-files | grep -cE '\.(g|freezed)\.dart$'` → 52;
`git ls-files 'lib/data/*' | grep -cE '\.(g|freezed)\.dart$'` → 45). A commit mixing 45
machine-written files with three hand-written ones is unreviewable — the review gate (§3) cannot
see the three. And at sixteen developers, two concurrent `build_runner` runs conflict in files
nobody authored, which is a merge conflict with no author to resolve it.

**`content-manager` dependency:** `STACKS.md` §10.5 and §10.0's parallel-work table tie this to the
first generated-l10n commit — **P0-5 must land before any generated-l10n Dart is committed**, not
to Phase 0's completion.

---

## 6. THE STOP CONDITION

A workflow halts mid-flight when any of these is true:

- **An open question whose answer changes the work.** Stopping is the correct output.
  A guess that keeps the session moving costs more than the pause.
- **A gate fails** — `flutter analyze` errors, a failed test, an unverified deploy.
- **The task needs a path its agent does not own** (`CONTRACT.md`).
- **The work is frozen by a decision** — `rewards` (015), the clean-arch stack (016).
- **A CRITICAL security finding is open and the workflow ends in a release.**

**What happens to the remaining steps:** they do not run. The ticket goes back to `To Do`
with a comment naming the blocker, and the blocker is added to `MANIFESTO.md` §6 if it
blocks more than this one task.

**What must not happen:** the agent must not substitute adjacent work to have something to
show. A halted task that reports the blocker is a success. A halted task that quietly
delivers something else is worse than one that delivers nothing, because the blocker stays
invisible.

---

## 7. THE CONTENTION PROTOCOL

Four files are touched by nearly every feature change, and they are the practical limit on
how many agents can run at once:

`lib/app/app_router.dart` · `lib/providers.dart` ·
`lib/core/config/feature_flags.dart` · `lib/core/config/supabase_config.dart`

**The procedure:**

1. **Before dispatching parallel agents, the Listener checks which of the four each task
   needs.** Tasks needing the same file are **sequenced, not parallelised**. This check
   happens at dispatch, not after a conflict.
2. **An agent in one of these files appends only.** Add your import, route, export, or
   constant. Do not reorder, regroup, reformat, or tidy.
3. **Your feature's block only.** Do not fix a neighbouring feature's entry, however
   obviously wrong. Report it (`MANIFESTO.md` R8).
4. **Never delete another agent's entry.** Removing a dead flag or route is cleanup work
   with its own ticket and owner.
5. **A diff touching one of these files goes through the review gate** (§3).
6. **`supabase_config.dart` is add-only for values.** Changing an existing constant's value
   redirects the whole app and needs a `DECISIONS.md` entry first.

**How many agents can safely run in parallel:** as many as have disjoint file sets. In
practice, with three developers, that means **at most three concurrent code tasks with
disjoint file sets, plus `devops`, plus `analyst`** — and only one of those inside a contended
file at a time. Parallelism beyond that produces conflicts faster than it produces work, which
is also why only two stacks are active (`AGENTS.md` §1).

**The one contended surface this section does not cover is a command, not a file.**
`dart run build_runner build -d` rewrites the 52 generated files — 45 of them under
`lib/data/` — and two concurrent runs collide in files nobody authored. That lock is
`devops`'s and the procedure is **W6** (§5): regeneration runs at commit time, after a
developer's source-only commit, and lands as a commit of its own. The four-file check at
step 1 does not catch it, because no agent declares a *command* in its file set.
