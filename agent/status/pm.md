# agent/status/pm.md

**Owner:** `pm` (write) · all agents (read)

Append newest-first, in the FORMAT block of `agent/STATUS.md`. **`agent/WORKFLOWS.md` §1 rule 5:**
no task is complete until its entry is saved — a refusal, a diagnosis or a question answered
still gets one.

---

# LOG

## 2026-09-05 — Ruling: D2/D6 are QUEUED, not ACTIVE, while the Phase 0 grant (`G-017`/`G-019`) is live

**Task:** `team-lead` asked me to resolve the contradiction between `agent/AGENTS.md` §1 (D2, D6
marked Active) and Phase 0's exclusive grant, which leaves nothing legally runnable on them.

**Ruling:** D2 and D6 are relabelled **queued**, not active, for the duration of the Phase 0
grant. No stack is active right now.

**Evidence (measured, `grep -rl` at HEAD in `Dabbler/dabbler-code`):**
- D2 slices `games`, `venues`, `explore`, `location`, `venue_submissions` each contain files
  reserved under `CONTRACT.md` §4.1's "other leads' slice" row (import-path rewrite only, one
  line, `senior-frontend-3` exclusively): `lib/features/games/data/datasources/nearby_games_datasource.dart`,
  `lib/features/games/presentation/providers/nearby_games_provider.dart`,
  `lib/features/venues/providers.dart`, `lib/features/venues/data/datasources/nearby_venues_datasource.dart`,
  `lib/features/venues/presentation/providers/nearby_venues_provider.dart`,
  `lib/features/explore/providers/nearby_games_providers.dart`, `lib/features/explore/providers/feed_providers.dart`,
  `lib/features/location/providers/location_providers.dart`, `lib/features/location/providers/profile_location_providers.dart`,
  `lib/features/venue_submissions/providers.dart`. `games` and `activities` are additionally named
  P0-4 move targets (receiving 7 relocated screens).
- D6's `lib/features/notifications/**` and `lib/services/notifications/**` have **zero** files
  matching `grep -rl "misc/data/datasources"` and are not a P0-4 move target — they are the one
  slice genuinely outside the grant's path table by measurement.
- But every feature ticket that needs a route registered still hits `lib/app/app_router.dart`
  and `lib/providers.dart`, both CONTENDED and under `senior-frontend-3`'s exclusive grant with
  no parallel writer permitted (§4.1 "Exclusion" clause) — so even D6/notifications work stalls
  the moment it needs a route, which most feature work does.

**Re-activation condition (quoted from `CONTRACT.md` §4.1 "What ends it", = `STACKS.md` §10.6):**
grant expires automatically at the first `Canary` commit where `flutter analyze` is 0/0/0,
`flutter test` is 103 tests + `route_inventory_test.dart` all passing, `app_router.dart` ≤450 LOC
with ≤6 `features/` imports, `grep -rn "misc/data/datasources" lib/ test/` is empty,
`lib/features/misc/` holds only its 3 residual screens, Cloudflare `Canary` is green, and `po`
has moved all 5 Phase 0 tickets to Done.

**Wording proposed for `AGENTS.md` §1 (analyst to apply):** replace the `Active` column's `D2`
and `D6` entries with `queued (Phase 0)`, and add a footnote under the table: *"No stack is
active while the Phase 0 exclusive grant (`CONTRACT.md` §4.1) is live. D2 and D6 resume on the
grant's own expiry test, quoted there — not on a new decision."*

**Not verified:** whether `notifications` tickets exist that need zero router/provider touch
(would be the only work genuinely runnable right now) — that's a `team-lead-5` capacity
question, not mine to answer. Did not check STACKS.md for a `lib/features/<13 dirs>` full list;
relied on direct grep against D2/D6's named slices only, per scope.

**Reported to:** `team-lead`.

---
## 2026-09-05 — Post-Phase-0 activation plan

**Task:** `team-lead` asked what activates Monday 2026-09-14, how many of the sixteen
developers can genuinely work week one without colliding, and a prioritised weekend
company-work backlog. No code/ticket/Jira writes — decision only, routed back to
`team-lead` for `po` to ticket.

**What I did:** read `Dabbler/dabbler-docs/STACKS.md` in full (both the 2026-09-04
proposal §§1-9 and the `G-015` Part II re-measurement, §§9a-12 — the ratified write
partition supersedes the D-label groupings in `AGENTS.md` §1 for *who writes what*, though
the D-labels stay valid for *what to work on*), `agent/AGENTS.md` §§1-2, and my own prior
entry above (2026-09-05, D2/D6 grant-expiry analysis) rather than re-deriving it.

**What I decided:**
1. Monday activates two stacks, not the automatic-resume pair: **`team-lead-2` (Play &
   Places — venues/games/explore/location/venue_submissions/activities)** reaffirmed, and
   **`team-lead-4` (Rewards + Admin)** newly selected in place of `team-lead-5`
   (Notifications). Reasoning: the census's dominant finding — finished backends with no
   client — names `venue_bookings` (lead 2) and 14 rewards RPCs (lead 4) explicitly;
   notifications carries no such flagged backlog and, per my prior entry, stalls on the
   router the moment it needs a route, same as everything else. This overrides
   `AGENTS.md`'s "no fresh judgement" framing for D6 — `pm` may reselect, per `AGENTS.md`
   §1's "Selecting *which* stacks is a `pm` decision with the CEO."
2. A third week-one workstream: `senior-frontend-3` (freed from Phase 0) pairs with
   `senior-frontend-1` on the Phase 1 ticket (`STACKS.md` §3 G1 / §11.4) — splitting
   `profile_providers.dart` — the only lever that ever makes `team-lead-1`'s 55%-of-codebase
   cluster divisible. `team-lead-1`'s stack is held back from full activation this week;
   its two juniors stay idle rather than wander into the tree's most expensive coupling
   (`profile↔social`, weight 16) with no Phase 1 done and no test baseline beyond the new
   route-inventory golden test.
3. Held back entirely for week one: `team-lead-1` (full activation, pending Phase 1),
   `team-lead-3` (Identity — no flagged urgency, and its senior is on the Phase 1 ticket),
   `team-lead-5` (Notifications — stable, small, not in the unreachable-backend set).
4. Weekend backlog, prioritised: (1) gate-figure single-source-of-truth in `STACKS.md`
   §10.6, owner `analyst` — real recurring-drift defect, cheap fix; (2) role-file audit for
   the 30 seats (relative status paths, missing status rules, deleted-seat references),
   owner `analyst` (owns `AGENTS.md`); (3) write the release cadence into a doc, owner
   `devops`; (4) size/date `KAN-126` (build_runner devops step) before Monday — unsized
   today but load-bearing the moment two of the three active week-one stacks regenerate
   code concurrently.
5. Refused: a blanket "run all 22 untested seats once" sweep — padding that burns tokens
   validating seats with no real work queued; seats get validated when work actually
   reaches them.

**Capacity I do not have and named as owed:** `team-lead-2` and `team-lead-4` week-one
capacity (never reported — new activation); `team-lead-1` + `team-lead-3` joint Phase 1
estimate; `team-lead-3`'s Phase 0 landing date stands as already reported (Wed 2026-09-09
typical, Fri 2026-09-11 ceiling) and I did not re-ask for it.

**Not verified:** the census figures (squads/circles/ratings/venue_bookings/rewards RPCs
unreachable) are taken from `PROJECT_STATE.md` as reported by `analyst`, not re-measured by
me this session. Full reasoning, the parallelism answer, and the refusal rationale sent to
`team-lead` via `SendMessage`.

**Reported to:** `team-lead`.

---
## 2026-09-05 — Correction: weekend backlog reweighed for readiness, not utilisation

**Task:** `team-lead` relayed a CEO correction — the sixteen developers are not a pool to
be utilised; idle is the correct state for a seat with no work in its own territory. The
real question for weekend work is readiness: does a seat that has never run arrive at its
first real ticket with enough context to do the work well. `team-lead` measured this
directly (role-file line counts, status-log state, ever-run) rather than asking me to
re-derive it, and flagged that the thinnest files sit on the largest remits —
`senior-backend` (97 lines, never run, sole seat for all schema/RLS/edge-function writes)
being the sharpest case. Also flagged: `analyst` is the single writer of `CONTRACT.md`,
`AGENTS.md`, `WORKFLOWS.md`; `cto` of `STACKS.md` and architecture docs — several
readiness items would collide on those two seats if I routed everything through them.

**What I decided:** rewrote weekend item 3 only (sections 1, 2, 4, 5 of my prior plan
stand, per `team-lead`). Split the work into two lanes that don't collide:
- **Mechanical audit/fixes that touch `AGENTS.md`/`WORKFLOWS.md`** (relative status paths,
  missing status-entry rule, deleted-seat references) stay with `analyst` — narrow,
  serialized, and largely already scoped by `team-lead`'s own findings.
- **Content-deepening of individual role files** (not itself a governance doc, so not
  bound by the same single-writer list) — parallelized to each file's domain owner rather
  than funneled through `analyst`: `cto` deepens `senior-backend` (highest remit, thinnest
  file, sole seat, in the direct path of both stacks activating Monday); `team-lead`
  deepens `team-lead-2`/`team-lead-4` specifically, since those are the two about to take
  a real ticket for the first time and the crutch that worked for `team-lead-3` today
  (live brief-writing) doesn't scale to two simultaneous new activations; `content-manager`
  and `cxo` deepen their own files (both proximate — both activated stacks will produce
  new screens and strings this week); `team-lead-1/3/5` and the ten `junior-frontend`
  files deferred past this weekend as lower-remit or not-yet-activated.
- Restated the refusal from my prior entry under the new framing: a blanket run-all-22
  sweep still does not belong here, and more precisely now — readiness is a property of
  the file's content, not something proven by executing it once with no real ticket behind
  it. That was the flaw baked into treating it as a to-do in the first place.

**Not verified:** I do not have direct readiness data on `senior-frontend-2` and
`senior-frontend-4` specifically — `team-lead`'s table covers leads and juniors, not the
mid-tier seniors, and those two are the ones about to be tested for real on Monday. Flagged
to `team-lead` as a gap in the measurement rather than assumed either way.

**Reported to:** `team-lead`.

## 2026-09-06 — Skills audit (self), read-only survey for team-lead

**Task:** Four-question skills audit of my own seat (`agent/roles/pm.md`), no file changes.

**What I found:** the six skills my role file names (`prioritization-advisor`,
`feature-investment-advisor`, `opportunity-solution-tree`, `incoming-request-advisor`,
`problem-framing-canvas`, `to-spec`, plus `writing-for-agents`) all map to real decision
moments I hit — none are dead weight. Of the ~63 unlisted `pm-skills` entries I checked,
two look like real gaps for my seat (`roadmap-planning`, `lifecycle-play-advisor` /
`product-lifecycle-plays`); five write dev-ready stories/acceptance criteria
(`user-story`, `user-story-mapping`, `user-story-mapping-workshop`,
`epic-breakdown-advisor`, `user-story-splitting`) and belong to `po`'s task-analysis
remit under `G-023`, not mine; four more (`jobs-to-be-done`, `customer-journey-map(-workshop)`,
`stakeholder-mapping`, `saas-revenue-growth-metrics`) read as `cpo`-adjacent strategy/vision
tools I'd escalate on rather than run myself.

**Not verified:** I read `description:` frontmatter for the ~14 pm-skills names in question,
not the full `SKILL.md` body, for any of them — judged from description text plus my role
file's stated remit, per the audit's own warning that a name is not a fit. Full-body review
would be needed before actually adopting any of the two I flagged as gaps.

**Reported to:** `team-lead` (via SendMessage).
