# agent/WORKFLOWS.md — Workflows and Handoffs

**Owner:** analyst (write) · all agents (read)
**Last updated:** 2026-09-05 — the v0.7 company restructure
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
         → Backlog → Ready → In Progress → In Development → In Review → In Testing → Done
```

**Who moves a ticket into each column** — a transition made by the wrong seat is a process
failure, not a shortcut:

| Into | Moved by |
|---|---|
| Backlog | `po` |
| Ready | `po` |
| In Progress | the owning `team-lead-N` |
| In Development | the owning `team-lead-N` |
| In Review | the developer who finished it |
| In Testing | `po` — **only after its review gate passes** (§3) |
| Done | `po` |

**Writing is `po`-only.** No other seat creates, edits or re-words a ticket. The `pm` says
what is needed; the `po` writes it.

**Three standing rules on every ticket:**

- **No ticket without a `due_date`.** A ticket with no date is not scheduled, it is a wish.
- **The date comes from capacity, not estimation.** Capacity is reported by the owning
  `team-lead-N`. The `po` may not estimate it and may not ask a developer directly.
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
   `agent/status/<name>.md`.** This binds every agent, on every task, with no
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
| Columns | Backlog · Ready · In Progress · In Development · In Review · In Testing · Done |

**Epics do not render as cards on a team-managed board. Tasks do.**

This is the rule that was got wrong once, and it is why every trackable unit is filed as
`issueTypeName: "Task"` with a `parent` Epic. An Epic alone is invisible to the person
watching the board — the work exists in the API and nowhere a human is looking.

**Transition IDs are project configuration, not a constant, and this project's are being
changed.** The board carried four columns (To Do `11` · In Progress `21` · In Review `31` ·
Done `41`) until the 2026-09-05 restructure moved it to the seven above. **Always call
`getTransitionsForJiraIssue` and read the ids back** — never write a remembered number into a
transition call. Any id in any document here is a convenience, not an authority.

**Issue keys are not assigned sequentially.** Creating twelve tickets does not give you
twelve consecutive keys — KAN-5, 8, 10, 12 were interleaved with another epic's children in
the same session. **Never write a ticket key into a comment before the ticket exists.**
Create first, read the returned key, then reference it. Getting this wrong requires editing
a comment afterwards, which is recoverable but visible.

**Labels in use:** `audit`, `security`, `follow-up`, `bug`, `cleanup`, `config`,
`quality`, `po-decision`.

---

## 3. THE REVIEW GATE

`In Review` is not decoration. A ticket sitting there has a claim attached to it — "this
is done" — and the gate is where that claim is tested rather than accepted.

**The gate belongs to `po`** since 2026-09-05, when `task-auditor` was merged into it.
**Reviewing is a distinct act with its own skill.** Use the `task-review` skill, which applies
two gates: the ticket's own acceptance criteria, and alignment with the governance docs. The
outcome is a written verdict and a transition — to **In Testing**, handed to `qa`, or back to
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

**Agents do not brief each other. Briefs come from the Listener.**

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
- **The contract is enforced at one point or not at all.** The Listener knows the permission
  matrix; a worker deciding who to hand to next is deciding scope, which is not its call.

**The exception:** a direct message is fine for a *question* — "does the notification
schema already have a `read_at` column?" — where the answer changes nothing and creates no
work. The moment a handoff creates work, it goes through the Listener.

---

## 5. NAMED WORKFLOWS

### W1 — A feature change

1. **`po`** writes the ticket with testable acceptance criteria and a `due_date` taken from
   the owning lead's capacity. It moves it to **Ready**.
2. **`team-lead-N`** pulls it from Ready, confirms the slice's state with **`analyst`** rather
   than assuming it from the stack name, splits it into subtasks, and routes each by **task
   shape**: `junior-frontend` for repeating an existing pattern in a single file,
   `senior-frontend` for business logic and multi-file work, `senior-backend` for anything
   schema-shaped. Moves to **In Progress**, then **In Development**.
3. **The developer** implements, following the build order (`MANIFESTO.md` §2): database →
   constants → repository → providers → screen → route. Writes tests for what it built, runs
   `flutter analyze` and `flutter test`, and **pastes the output rather than summarising it.**
   Moves to **In Review**.
4. **`po`** runs the review gate (§3). Pass → **In Testing**. Fail → back to **Ready** with a
   rework brief.
5. **`qa`** executes the testing story it wrote when the task was dispatched, against the
   running app. Bugs go back to the owning developer, never fixed by `qa`.
6. **`cxo`** judges the experience if the change is user-visible — a separate question from
   whether it works.
7. **`devops`** commits, pushes `Canary`, and verifies canary.dabbler.pro.

| Step | Seat | Receives | Produces | Done when |
|---|---|---|---|---|
| 1 | `po` | The request | A ticket with criteria and a date | Criteria are testable; date came from capacity |
| 2 | `team-lead-N` | A Ready ticket | Subtasks, each assigned | Each routed by shape, not by who is idle |
| 3 | developer | A subtask | Code through step 6 of the build order | A route reaches it; `analyze` 0 errors; `test` passes |
| 4 | `po` | The diff | Verdict | In Testing, or back to Ready |
| 5 | `qa` | Passed work | Testing story executed | Bugs filed, or none found and said so |
| 6 | `cxo` | User-visible change | Experience verdict | Rule named, or nothing to raise |
| 7 | `devops` | Approved work | A verified Canary deploy | **The site shows it** |

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
