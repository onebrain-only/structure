# agent/status/cto.md — CTO status

**Last run:** 2026-08-28 · **Branch:** `Canary` · **Epic:** KAN-39

## Standing verdict

**Dabbler is not promotable today.** Re-sorted 2026-08-27 after `master-analyst` caught the
criterion being applied loosely — the verdict is unchanged, the grounds are now precise.

**Promotion blockers — harm occurring or executable today:**

| | Ticket | Owner | Needs DB access |
|---|---|---|---|
| **0** | **KAN-67** — **revoke `anon` on the 8 write-path views** (7 fixable; see T-015). Live unauthenticated write onto `notifications`, `posts`, reputation and drafts. Demonstrated at plan level with a control; RLS not consulted — view owner is `postgres` with `rolbypassrls`. None of the 8 is referenced anywhere in `lib/`, so a **full** `anon` revoke on them is behaviourally free and strictly safer than a write-only one. **Do this first — destructive beats confidential.** | `cto` authors, PO gates | yes |
| 1 | **KAN-56** — anon definer-view **read** leak (609 private notifications, 49 users) | `notifications-specialist` | yes |
| 2 | **KAN-58** — logout clears nothing, FCM token never revoked | `notifications-specialist` | no |
| 3 | **KAN-59** — any account can push arbitrary title/body to any user | `notifications-specialist` | no |

**Sequence: KAN-67 → KAN-56 → KAN-58 / KAN-59.** If exactly one thing ships, it is KAN-67 —
closing only the read path leaves `anon` holding DELETE on eight views.

**Pre-promotion requirement, different grounds:**

| | Ticket | Owner | Needs DB access |
|---|---|---|---|
| 4 | **KAN-57** — Play upload key credential public 9 months | `version-control` + PO | no |

**KAN-57 harms no user today.** The password alone signs nothing: the keystore has never been
in the repository in any form (verified across all refs and all history, including encoded
blobs), and Android signing never runs in CI. It goes before promotion because the disclosure
is **permanent and unrecoverable** and the fix costs an afternoon — not because anyone is at
risk. **Argue it to the PO as "a credential is exposed, the signing artifact is not."** The
stronger phrasing is not true, and an overstated blocker is how a real one gets discounted.

Full reasoning, with rejected alternatives, in `DECISIONS.md` **T-011** and **T-003**.

## Open tickets raised this run

| Ticket | Summary | Owner | Blocker? |
|---|---|---|---|
| KAN-56 | Close the anon definer-view leak | `notifications-specialist` | **yes** |
| KAN-57 | Rotate the Play upload key | `version-control` | **yes** |
| KAN-58 | Logout teardown + FCM revocation | `notifications-specialist` | **yes** |
| KAN-59 | Edge-function authorization scope | `notifications-specialist` | no (but abusable today) |
| KAN-60 | Android backup exclusion rules | `app-store-submission-fixer` | no |
| KAN-61 | Anon-reachability allowlist in CI | `version-control` | no (depends on KAN-56) |
| KAN-62 | Re-scope KAN-27 and KAN-28 | `master-analyst` | no |
| KAN-63 | Four broken-but-not-leaky surfaces | mixed | no |
| KAN-64 | This assessment | `cto` | **In Review** |

## Decisions landed

`DECISIONS.md` **T-001 .. T-011**. `ARCHITECTURE.md` **§10 — the security architecture**.

Load-bearing positions: views default to `security_invoker = true` (T-001) · anon reachability
is a CI-enforced allowlist (T-002) · no credential literal in a tracked file (T-003) · logout is
a teardown contract (T-004) · session stays in SharedPreferences, backup exclusion is the control
(T-005) · **no certificate pinning** (T-006) · dead-but-wired code is deleted, not implemented
(T-007) · `Either` converts on touch, no migration project (T-008) · edge functions verify
authorization scope, not just authentication (T-009) · line count and colour literals are budgets,
not defects (T-010).

## Deliberately not blockers

143 files over 500 lines · 317 hardcoded colours across 43 files · three error-handling
conventions · 20,545 lines of unreachable rewards code · 113 feature flags of which 10 gate
anything · 13 `MaterialPageRoute` sites bypassing GoRouter.

All real. **None can harm somebody who installs the app.** They are why the product feels
immature — a product judgement, and the `cpo`'s half of KAN-39. Attacking them instead of the
leak and the signing key would be a serious misallocation of the pre-launch window.

## What the assessment confirmed is sound

`flutter analyze` → **0 errors** (55 warnings, 102 infos) · `flutter test` → **66 pass** ·
authorization deferred to RLS with **no client-side authorization decisions anywhere** · admin
routes server-authoritative and fail **closed** · deep links do **not** bypass the auth gate ·
transport clean, ATS correct, no cleartext · **no service-role key ever committed** (full
object-database sweep, 8,301/8,301 blobs).

The database leak is a failure of a **view layer built on a correct model**, not a failure of
the model.

## Next

1. `master-analyst` re-scopes KAN-27/28 (KAN-62) before any agent works them.
2. Migration for KAN-56 drafted and reviewed — **base-table policies before the invoker flip**, or live screens go blank (`public.games` has RLS with zero policies).
3. KAN-57 and KAN-58 can proceed in parallel; neither needs database access.

**No agent writes to production** (decision `019`). Everything ships `Canary` → verify → PR.

---

## Rulings, 2026-08-28 (run 2, in response to `master-analyst` briefing)

**T-012 — RLS-on/zero-policy tables: revoke the grant, do not add policies.** The definer
funnel is real (`games` → 37 definer functions, found via `prosrc`; **`pg_depend` returns 0 and
is an artifact**). But all 30 still `GRANT SELECT` to `anon`, so the only protection is an
*absent* policy — a design that fails open on one mistake.

**This corrected my own earlier instruction.** `T-001` said "base-table policies before the
invoker flip". For definer-funnel tables that is wrong — they must not get policies.
`v_mod_queue_open` and `v_safety_overview` are **revoked, not flipped**; flipping them would
blank the moderation queue for admins while looking fixed. KAN-56 has the corrected sequence.

**T-013 — four design-system surfaces, not three.** `lib/themes/AppTheme` is canonical for
theming — `main.dart:156,265-266` proves it is what `MaterialApp` consumes, and it was not
among the three offered. `lib/core/design_system/` canonical for components;
`lib/design_system/` absorbed on touch; `dabbler_design_system` (0 imports) removed now.

**T-014 — the Flutter feature agent is the first hire.** Not on throughput grounds:
**KAN-58 is a promotion blocker nobody on the roster can finish.** Its teardown half is Dart in
`lib/core/**`, which `CONTRACT.md` §3 leaves unowned. Its first task is that teardown — **not**
the 69,612 dead lines, which is the riskiest work available with zero coverage on live paths.

**T-003 second amendment — the `build.gradle.kts` change in the working tree does not close
KAN-57.** It is correct and well made (fails loudly rather than debug-signing), but removing the
literal stops only *future* exposure. **Only rotation invalidates the password.** It is also
uncommitted and touches release signing while only web has been verified — do not commit it
without an Android release build.

## Flagged to the Analyst

The working tree is **101 entries** (80 deletions, 11 modifications, 10 untracked), not the 16
described — including deletions of `lib/core/services/onboarding_service.dart` and its mock.
Those are safe (0 references to the `OnboardingService` symbol outside their own files), but the
description would not lead a reader to expect Dart deletions.

**T-015 — `geometry_columns` is excluded from the revoke and the migration enumerates its
targets.** Migrations run as `postgres`, which is not superuser and not a member of
`supabase_admin` (the owner), so `REVOKE` on it **fails**. The obvious single-statement form,
`REVOKE … ON ALL TABLES IN SCHEMA public FROM anon`, is the trap: it either halts a security
migration partway or skips the object and reports success. 7 of 8 close; the 8th is documented as
platform-owned. An honest partial fix beats a blanket statement that appears total and is not.

**T-016 — two rulings from the orphan-table measurement (KAN-68).**

*(a) `safety_blocklist_terms` gets a DEFINER function, not a read policy.* A read policy would
work and would be wrong: **every user could download the list of banned terms and author around
it.** A control whose contents are visible to those it constrains is not a control. Same for
`context_rating_config`. Note this is a genuinely different shape from `T-012`'s funnel tables —
all three referencing functions are `prosecdef=false`, so these tables are not funnel-protected,
they are **unreachable**. Applying `T-012` here by analogy would have been wrong; the
`prosecdef` column is what separated them.

*(b) Dead **data** is not dropped like dead **code**.* `challenge_types` and `surface_catalog`
have no reader of any kind — revoke now, **defer the drop**. `T-007`'s deletion default does not
transfer: dead Dart is recoverable from git in one command, 38 rows of dropped config are
recoverable from nothing. `space_slot_holds` is left alone — it is named in
`supabase_config.dart:141` and `slot.dart:66`, so it is parked scaffolding and a `cpo` question.

**BUG-07 / KAN-68 — the content blocklist fails open, twice, independently.** The locale
predicate can never match (`'any'` is treated as a property of the stored term, not the query),
**and** RLS returns zero terms regardless. Either alone returns a silent `0` — a plausible
"clean" — for every input. **Not a promotion blocker:** nothing calls
`contentHitsBlocklist`, so no content is being let through. But `moderation_service.dart` is
live across five screens, so it is one wiring change from a silent safety failure. Verification
must run as role `authenticated`, **never service role** — a service-role test passes while
production fails, which is how this survived.

**T-017 — SEC-17 (`creator_user_id` exposure) is NOT folded into KAN-67.** `master-analyst`
recommended folding; overruled on evidence. Opposite risk profiles: KAN-67 is a `REVOKE` with
**0** client references across all 8 views; SEC-17 redefines `v_game_card`, and `creator_user_id`
has **3 read sites on the view** — of which **exactly one is a filter**
(`game_history_providers.dart:79-80`, applied to `.from(vGameCardTable)`), the other two being
parses (`game_view_controller.dart:212`, `game_model.dart:81`). *Corrected 2026-08-28: the
figure was 6 sites / 3 filters. Two of those six —`supabase_games_datasource.dart:507` and
`sport_profile_view_provider.dart:264` — query `.from(gamesTable)`, not the view, so a view
change does not touch them. The one filter is the site that fails as **silently wrong results**
rather than an error, which is the whole reason this does not get bundled.*

**KAN-67 is the only production change in this plan that is verifiably risk-free.** That property
is why it ships first while a destructive hole is open, and folding a six-call-site client
regression into it destroys exactly that. SEC-17's real fix is *migrate the call sites to
`creator_profile_id`, then drop the uid* — a coordinated Dart + SQL change in unowned code, so it
**sits behind the `T-014` Flutter hire** alongside KAN-58.

**Scale for the PO:** 61 of 240 users — **25% of the user base** — have their raw `auth.users`
UUID readable with no account (`master-analyst`'s sweep, reproduced on `v_game_card`: 216 of 216).


---

## 2026-09-05 — `G-015` discharged: five-lead partition + executable Phase 0 (`T-047`)

**Branch:** `Canary` · **Measured at:** `dabbler-code` `c46b5c5` (unchanged since the 2026-09-04
stack analysis, so §§1–9 of `STACKS.md` were re-checkable at the same commit).

**Note on the gap in this log.** The 2026-09-03/04 stack analysis that produced
`dabbler-docs/STACKS.md` and `DECISIONS.md` `G-012` was **never recorded here.** That work exists
only in those two documents. Recorded now so the omission is visible rather than silent.

**Delivered.**
- `dabbler-docs/STACKS.md` **Part II (§9a–§12)** — the coupling metric stated once with its
  reproduction command; §9b corrections table; §10 the five-ticket Phase 0 plan; §11 the five-lead
  partition with per-grouping evidence; §12 the thirteen-row delta against `CONTRACT.md` §3.
- `dabbler-docs/DECISIONS.md` **`T-047`** — ACTIVE, with six rejected alternatives.

**The partition.** lead 1 `profile`+`social`+`home`+`news`+`moderation` (167 files / 69,485 LOC) ·
lead 2 `games`+`venues`+`explore`+`location`+`venue_submissions`+`activities` (91 / 29,872) ·
lead 3 `auth_onboarding`+`username_engine`+`app_boot` (53 / 13,127) · lead 4 `rewards`+`admin`
+ Commerce (6 / 1,579) · lead 5 `notifications` (19 / 4,259).

**Answer given to `G-015`'s five-vs-seven constraint:** five is the right number of **cuts** and the
wrong number of equal **loads** — 55/24/10/1.3/3.4 by LOC — and no roster change fixes it, because
the only place a sixth lead fits is inside lead 1 where the cheapest cut is `profile|social` at 16
file-edges. The fix is Phase 1, not headcount.

**Three findings worth carrying.**
1. **Nothing in `test/` references the router.** 9 `*_test.dart` files, 103 tests, zero router coverage on
   a 1,712-LOC / 85-route file. `flutter test` green would have proved nothing about the split, so
   P0-1 is now a golden route-inventory test and it gates the refactor.
2. **`home` and `core` have no writer in `CONTRACT.md` §3.** `home` is 7 files / 3,403 LOC and
   contains `main_navigation_screen.dart` — the shell the `StatefulShellRoute` reaches.
3. **My own `G-012` numbers did not fully reproduce.** "`profile↔social` 5 out / 10 in" mixed
   distinct-target-files with import-statements in one phrase (truth: 7 out / 9 in). "`auth` reaches
   `profile` at 5 files, all domain-layer" is wrong twice — 4 files, and 3 of 8 statements hit
   `presentation/providers/add_persona_provider.dart`. `STACKS.md` §3 G0c named 8 screens in
   `misc/`; there are 10, and the two it missed are both live routed. **The argument held; three
   counts did not.**

**Handed on.** `analyst` owns the `CONTRACT.md` §3 and `AGENTS.md` §1 amendments — proposed in
§12, **not applied by me.** `po` tickets P0-1…P0-5 from §10. No app feature work is dispatched
until Phase 0 lands (`G-015` Ruling 1).

**Not verified:** nothing was run. No `flutter analyze`, no `flutter test`, no app, no database
query. Every number is static analysis of the tree at `c46b5c5`.

## 2026-09-05 — T-048: corrected `STACKS.md` §10.2 blast-radius counts

**Task:** from `team-lead` — two numbers in my own `STACKS.md` §10.2 did not reproduce.
**Effort:** low, as briefed. Read-only against `Dabbler/dabbler-code/`; no code, no commit.

**Measured** at `c46b5c5`: `grep -rl 'misc/data/datasources' lib/ test/ | wc -l` → **39**
(not 38). By location: `lib/features/` **26** across 13 of 20 dirs · `lib/data/repositories/`
**10** (not 11) · `lib/providers.dart` + `lib/core/providers/geo_providers.dart` **2** ·
`test/` **1** — `test/data/repositories/profiles_repository_impl_test.dart`, two import lines
(`:7`, `:8`), covered by `G-019`.

**Changed:** `STACKS.md:486` (§9b correction row), `:551-563` (§10.2 — now a by-location table
plus the named test file), `:582` ("any of the 39 files"). No other occurrence of the figures
exists in the document — `:184` G0a and `:156` state only the 13-of-20 directory count, which
reproduces.

**Recorded:** `DECISIONS.md` T-048. Phase 0 plan, partition and acceptance criteria untouched.
