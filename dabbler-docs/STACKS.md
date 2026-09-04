# Dabbler — Ownership Stacks

**Status:** PROPOSAL. Not ratified. No `DECISIONS.md` id yet.
**Authored:** 2026-09-04 · **Measured against:** `dabbler-code` HEAD `c46b5c5`, branch `Canary`
**Source:** `cto` stack analysis, session `01MCCanB436igB4CLHdMnD2R`
**Companion docs:** `PROJECT_STATE.md` §3 and §24 (build state) · `CONTRACT.md` (permission matrix) · `dabbler-code/docs/SCHEMA.md` (tables)

---

## 0. What this document is, and what it rests on

This is an **ownership** partition, not a taxonomy. It answers *"what must be changed
together, and what can be changed independently"* — not *"what belongs together
conceptually."*

The stacks were derived by measuring the **import graph between the 20 directories under
`dabbler-code/lib/features/`** and taking ownership from its strongly-connected components.
They were **not** derived from the Supabase table families. That distinction matters: a
separate analysis (`cpo`, same session) clustered the 650 corpus features by table family
into eleven domains D1–D11, and four of those groupings break when a developer is placed
inside them. §6 records where and why.

### 0a. Provenance — read this before relying on any number here

- **Everything in §1–§4 was verified by command against `c46b5c5`** unless explicitly marked
  inferred. §8 separates confirmed from inferred.
- **The feature-count mapping in §5 was NOT.** It was produced by `cpo` against a prose
  summary of this proposal relayed in-session by the team lead — **not against this
  document, which did not exist at the time.** Two boundary assignments there are judgment
  calls (B.2 → S2, B.16 → S3); if this document draws them differently, 30 and 25 features
  move respectively. **Re-derive §5 against this file before planning from it.**
- **A count is only true at a commit.** `PROJECT_STATE.md` §24i records why: "25 slices"
  and "113 flags" were each correct when measured and wrong within a week, and two
  downstream analyses spent real effort on them. Every count here carries `c46b5c5`.

---

## 1. The seven stacks

Six active, one dormant. The number was not targeted; it is what the import graph supports.

### S1 — Identity & Access

| | |
|---|---|
| **Absorbs** | D1 identity half (`11b` IDs 1–55, B.1) |
| **Writes** | `lib/features/{auth_onboarding,username_engine,app_boot}/**` · `lib/core/auth/**` · `lib/core/services/{auth_service,auth_profile_service,user_service,profile_cache_service,avatar_service,default_avatar_service}.dart` · `lib/features/profile/domain/{models/persona_rules.dart,services/persona_service.dart}` · `lib/data/repositories/{username,display_name,profiles,supabase_profile}_repository*.dart` · `lib/data/models/authentication/**` |
| **Reads** | `lib/features/profile/**` (S2) · `lib/core/config/**` (S5) |
| **Tables** | `profiles`, `profile_follows` (shared read with S2), auth-adjacent tables named in `supabase_config.dart` |

**Boundary evidence.** `auth_onboarding` reaches into `profile` at 5 files, all domain-layer.
`profile` reaches back at 4 files, all auth presentation providers — a thin back-edge in the
correct direction (a profile screen reading the session is normal). `persona_service.dart`
imports only riverpod, `supabase_config`, `supabase_flutter` and its own `persona_rules.dart`,
so moving it carries no cross-feature dependency.

**Note.** S1 is the heaviest single consumer of the router: 25 of `app_router.dart`'s 69
feature imports come from `auth_onboarding` alone.

### S2 — Profile, Social & Feed

| | |
|---|---|
| **Absorbs** | D5 (356–400), D7 (451–475), D1 presentation half, D8 client half |
| **Writes** | `lib/features/{profile,social,home,news,activities,rewards,moderation}/**` · `lib/services/{post_service,sport_profile_service,moderation_service}.dart` · `lib/data/repositories/{post,friends,block,circle,user_circles,squads,public_activity,search,feed,ratings,sport_profiles,moderation,check_in,profile}_repository*.dart` · `lib/data/models/{social,feed,rewards,news,sport_profiles,check_in,profile}/**` and the loose `squad*`/`friend*`/`circle*`/`rating*` models |
| **Reads** | S1 identity providers · S3 location providers · S5 design system and `misc` datasources |
| **Tables** | `posts`, `post_*`, `comments`, `likes`, `reactions`, `hashtags`, `circles`, `circle_members`, `squads`, `squad_*`, `friendships`, `friend_edges`, `profile_follows`, `user_blocks`, `public_activities`, `feed_*`, `ratings`, `game_rating_aggregate`, `user_reputation_aggregate`, `vibes`, `v_circle_feed`, `v_squad_card` |

**~177 files, ~75k lines — roughly 40% of the feature tree.** One Team Lead, 3–4 developers.
**It cannot be split today.** See §3 gate G1.

### S3 — Play & Places

| | |
|---|---|
| **Absorbs** | D2 (56–135, 291–315, 401–425), D3 (186–250), D9 (476–500), D10 (316–355), **and B.9 (251–290)** — see §7 |
| **Writes** | `lib/features/{games,venues,explore,location,venue_submissions}/**` · the five game-creation screens currently in `lib/features/misc/presentation/screens/` (`game_composer_screen`, `sport_format_step`, `venue_slot_step`, `player_invitation_step`, `review_confirmation_step`) · `lib/core/services/{location_service,gps_service,ip_service}.dart` · `lib/core/providers/geo_providers.dart` · `lib/data/repositories/{games,venues,nearby_games,area,geo,place,vibes,availability,venue_config,joinability,bench_mode,venue_submission,profile_location,sports}_repository*.dart` · `lib/data/models/{games,nearby,activities}/**`, `area.dart`, `place.dart`, `slot.dart`, `venue*.dart`, `sport_tags.dart` |
| **Reads** | S1 (auth guards) · S2 (profile providers for the organiser persona) · S5 |
| **Tables** | `games`, `matches`, `match_participants`, `match_waitlist`, `venues`, `venue_*`, `space_slot_*`, `areas`, `geo_locations`, `profile_locations`, `sports` |

**Boundary evidence.** `explore` imports 13 distinct files across `games`, `venues` and
`location` and is imported back exactly once — it is a composition surface, not a peer
domain. Splitting discovery from games would put the composer on one side of a boundary and
its inputs on the other.

**Staffing asymmetry, and it is the point.** S3 is the **largest stack by feature count and
among the smallest by code** (85 files, ~30k lines). It is the least-built, most-specified
part of the product. Load it accordingly.

### S4 — Notifications & Messaging

| | |
|---|---|
| **Absorbs** | D6 (426–450) |
| **Writes** | `lib/features/notifications/**` · `lib/services/notifications/**` · `supabase/functions/{send-push-notification,broadcast-notification}/**` · notification tables and their RLS |

**This boundary already works and should not be touched.** `notifications` imports only
`activities` (3) and `profile` (1); nothing imports it except `profile` (3).

**Note.** `FeatureFlags.messaging = false` (`feature_flags.dart:20`). Chat is dark by flag,
not merely unbuilt, and the previously-CRITICAL "live button → Coming Soon" (INV-01/WIRE-09)
is resolved by that gate plus a route guard.

### S5 — Platform & Foundations

| | |
|---|---|
| **Absorbs** | D11 minus AI (561–630), the `analytics` and `data_export` capabilities, the admin/staff console |
| **Writes** | `lib/app/app_router.dart` and `lib/app/routes/**` · `lib/providers.dart` · `lib/core/config/**` · `lib/themes/**`, `lib/design_system/**`, `lib/core/design_system/**`, `lib/core/theme/**` · `lib/widgets/**` · `lib/utils/**` · `lib/main.dart` · `lib/core/{fp,errors,error,constants,utils}/**` · `lib/core/services/{cache,storage,image_cache,theme,app_lifecycle,mock_localization}.dart` · `lib/core/analytics/**` · `lib/features/misc/data/datasources/**` · `lib/features/{admin,error,core}/**` · `lib/l10n/*.arb` · `android/**`, `web/**`, CI workflows |
| **Reads** | everything. Writes nothing inside another stack's feature directory. |

### S6 — Backend & Data Platform

Existing `backend-owner` seat, unchanged. Writes `supabase/**` — migrations, RLS, RPCs,
views, non-notification edge functions.

**Authors only.** Per `CONTRACT.md` "Supabase project — writing", nobody but `cto` applies to
production, under G-002. Every other stack files schema requests here. This is the
throughput ceiling on every feature with a schema component, and it is a deliberate
prohibition (decision 019), not an unfilled seat.

### S7 — Commerce · **DORMANT — do not create yet**

| | |
|---|---|
| **Would absorb** | D4 (136–185, 501–560) |
| **Would own** | `lib/data/repositories/wallet_repository*` · `lib/data/models/payments/**` · `payout.dart`, `wallet.dart` · `misc/presentation/screens/{transactions_screen,participation_payment_step}.dart` · tables `wallets`, `wallet_ledger`, `payouts` |

`FeatureFlags.enablePayments = false` (`feature_flags.dart:54`); `wallet_repository` has zero
consumers outside `lib/data/`; the payments feature slice was deleted in `34f9a6d`.

**RULING: do not hand D4 to S3 or S5 as a side quest.** A 110-feature domain half-built
inside somebody else's mental model is how you get a fourth parallel profile stack. S7 is
created as a real stack with its own lead on the day the PO schedules `enablePayments` to
open. Until then D4 is a backlog, not a stack.

**Unresolved:** 19 D4 features carry Phase 1A in the corpus (16 in B.5, 2 in B.6, 1 in B.19).
"S7 dormant" is unambiguous against MVP 1 and contradicts the corpus against the full 1A
stage. That is a PO scope question, not something a stack activation settles.

---

## 2. The collision surface

The section that determines whether parallel work is possible at all.

| # | Surface | Measured at `c46b5c5` | Ruling |
|---|---|---|---|
| 1 | `lib/app/app_router.dart` | 1,712 LOC · 85 `GoRoute` · 1 `StatefulShellRoute.indexedStack` (`:746` — a plain-`ShellRoute` grep misses it) · imports from 13 of 20 feature dirs | **Split into per-stack route modules** exporting `List<RouteBase>`. S5 keeps `_handleRedirect`, the refresh listenable and the assembly. See gate G0b. |
| 2 | `lib/providers.dart` | 39 lines, 29 exports | Keep `CONTRACT.md` §4's append-only protocol. Fine as-is. |
| 3 | `lib/core/config/feature_flags.dart` | 17 `static const bool` (12 true, 5 false) plus a string-keyed switch — **adding a flag is a two-place edit** | S5 owns it. Stacks request flags; they do not add them. A flag is a product decision with a `DECISIONS.md` consequence. |
| 4 | `lib/core/config/supabase_config.dart` | 260 lines, ~55 table constants | `CONTRACT.md` §4's add-only rule is correct and sufficient. Note the ~55 named here are a fraction of SCHEMA.md's 184. |
| 5 | `lib/data/**` | 71 repository files, ~90 model files, flat, all domains | **Ownership by filename, not directory.** Each stack owns its own `<domain>_repository*.dart` and models. **Nobody restructures `lib/data/`** — re-homing ~160 files would collide with every in-flight branch at once. |
| 6 | Generated code | 52 `.g.dart`/`.freezed.dart`, **45 under `lib/data/`** | Stays UNOWNED. **Regeneration becomes a commit-time step owned by `version-control`**, not a stack action. A stack that commits regenerated output alongside its source change produces an unreviewable diff. |
| 7 | Design systems (four trees) | `lib/core/design_system/`, `lib/design_system/tokens/`, `lib/themes/`, `lib/core/theme/` | S5 owns all four. **The consolidation question stays closed** under G-011's standing limit; no agent merges one into another without a `cto` ruling. |
| 8 | `lib/features/misc/**` | imported by **13 of 20** feature directories | Not a feature — two unrelated things under one name: shared Supabase infrastructure, and five screens belonging to other stacks. S5 owns it until dissolved. See gate G0a. |
| 9 | `lib/core/services/**` | 16 services | Split by file: auth/user/profile-cache/avatar → S1 · location/gps/ip → S3 · cache/storage/image_cache/theme/lifecycle/analytics → S5. No shared file. |
| 10 | `lib/widgets/**` | 13 top-level widgets incl. `responsive_app_shell.dart`, imported by `main.dart` | S5, exclusively. |
| 11 | `lib/l10n/*.arb` | 2 files | Append-only, same protocol as `providers.dart`. Generated localisation Dart regenerated by `version-control`, per #6. |

**The router protocol problem, stated plainly.** `CONTRACT.md` §4 serialises edits to the
contended files — *"one agent in one of these files at a time."* That rule was written for a
single `flutter-feature-agent`. **At six stacks it stops being a safety rule and becomes the
schedule.** Splitting the route table is what makes it survivable.

**`_handleRedirect` must NOT be distributed.** It already carries onboarding-step
enforcement, an OAuth-callback profile check and a shared-game-link branch. It is the single
most contended piece of logic in the app and it stays in one head (S5), because redirect is
policy.

**One-line fix worth taking early.** `social/` imports
`home/presentation/widgets/reaction_picker_sheet.dart` — the only thing `social` takes from
`home`, against six things `home` takes from `social`. Move the widget into `social/` and
`home → social` becomes strictly one-way.

---

## 3. Sequencing gates

Parallel work is **not** available today. These gates come first.

### Phase 0 — S5 only. Nothing else starts.

- **G0a. Move `misc/data/datasources/**` into `lib/core/`.** 13 feature directories import it
  today. Until this lands, every stack writes imports pointing into another stack's
  directory. **Cheapest high-value unblock in the programme — do it first.**
- **G0b. Split `app_router.dart` into per-stack route modules.** Without it, `CONTRACT.md`
  §4's one-agent-at-a-time rule is the schedule for all six stacks.
- **G0c. Relocate the five game-composer screens** out of `misc/` to S3; `transactions_screen`
  and `participation_payment_step` to a holding place for S7; `help_center_screen` stays S5.
- **G0d. Establish the `version-control`-owned `build_runner` regeneration step** before two
  stacks ever run it concurrently.

### Phase 1 — S1 + S2 jointly, one ticket, before either does feature work.

- **G1. Break up `lib/features/profile/presentation/providers/profile_providers.dart`.**
  **870 lines** holding three stacks' concerns: the identity bootstrap, the follow graph, and
  seven profile-screen controllers. It imports across two feature boundaries
  (`social/block_providers.dart`, `auth_onboarding/.../auth_profile_providers.dart`).
  `social` consumes **10** providers from it; `home` consumes **5**.

  Split: identity providers (`myProfileId`, `currentUserProfile`, `activeProfileType`,
  `availableProfiles`, `initializeProfileData`, `profileBootstrapCompleted`) → S1 ·
  follow-graph providers (`followers*`, `following*`, `isFollowing`, `searchProfiles`) → S2's
  social side · the 7 controllers stay in `profile`.

  When it lands, `social → profile` drops to zero and an S2a/S2b split becomes real.
  **Until then S2 is one stack.** Do not wait for it — but do not promise a split that is not
  available.

### Phase 2 — S1, S2, S3, S4, S5 in parallel. S4 never stopped.
### Phase 3 — S7 created, on the day the PO schedules `enablePayments` to open.

### 3a. Where the finished-backend pattern inverts the default ordering

**For squads, circles, ratings, venue bookings, payments and the rewards RPCs there is no
backend work to sequence before the client work. S6 is not on the critical path for any of
them.** A plan that schedules S6 ahead of S2/S3 for those domains idles two stacks waiting
for something already built.

S6's actual queue is **security remediation**, not feature enablement. It gates S2 and S3 at
two named edges only:
- **T-016** gates anything wiring `contentHitsBlocklist`.
- **T-024** gates any new write path routing through a definer view over a zero-policy base
  table.

Two further edges:
- S3's booking client is blocked on nothing technical, but `FeatureFlags.enableBookingFlow`
  is `true` while `venuesBooking` is annotated *"venues remain read-only"* — **a product
  contradiction S3 must get resolved before scoping, not after.**
- S2's chat work is blocked by product, not code: `FeatureFlags.messaging = false`.

---

## 4. B.9 — Organiser dashboard (40 features, IDs 251–290)

**RULING: no stack of its own. It goes to S3.**

**Organiser is a persona, not a domain.** There is no organiser table, no organiser feature
slice, and no organiser screen. `organiser_benefits_repository` has zero consumers outside
`lib/data/`. Grepping "organiser" across `lib/` returns hits only in `feature_flags.dart`,
`profile/utils/persona_label.dart`, `profile/domain/models/persona_rules.dart`,
`profile_providers.dart`, two `explore` screens, three `social` widgets/screens,
`core/services/auth_service.dart`, and all of `lib/features/venue_submissions/` — whose
router comment reads `// Organiser venue submissions`.

The 40 features are already distributed across three stacks as **views on their data**.
A composition belongs where its heaviest dependency is: ~30 of the 40 are game and venue
operations, and S3 already owns `venue_submissions` entirely, plus `games` and `venues`.

| Stack | Contribution |
|---|---|
| S3 | Dashboard shell, game/venue/submission panels, the route module entry |
| S1 | Persona switching and organiser eligibility (`persona_rules.dart`, `persona_service.dart`) |
| S2 | A single entry point from the profile screen — one line, append-only protocol |
| S7 (dormant) | Payouts and organiser benefits, when Commerce exists |

This reuses an existing relationship rather than inventing one: `profile` already embeds
`social/presentation/widgets/feed_post_card.dart` rather than reimplementing it.

**Caveat that must travel with S3's headline number.** P-020 (`DECISIONS.md`) moves the
organiser persona to MVP 1+ — *"section E of the checklist is 0/20 verified."* It does not
remove B.9 from Phase 1A in the corpus. **S3 against MVP 1 and S3 against the full 1A stage
differ by exactly B.9.** Both numbers are correct; they answer different questions. State
which one is in play whenever S3 is resourced.

---

## 5. D8 — Moderation (13 tables, **zero** corpus features, live BUG-07)

**RULING: no team. You do not assign features here, because moderation is not a feature
domain. You assign controls, and controls follow the surface they attach to.**

| Layer | Owner |
|---|---|
| User-facing controls (report a post, block a user, hide content) | The stack owning the surface — posts/profiles → S2, games/venues → S3. They already live there. |
| Staff console (`lib/features/admin/**`) | **S5.** Different user, different product, different QA path. Do not put a staff console inside a consumer-product stack. |
| Enforcement layer (`safety_blocklist_terms`, `content_hits_blocklist`, `context_rating_config`, the 13 tables' RLS) | S6 |
| The 13 tables | S6 — none has a client |

**How to write acceptance criteria with no feature list: the security rulings are the spec.**
`DECISIONS.md` T-016 already states the required end state verbatim — the locale predicate
becomes `where p_locale = 'any' or locale = 'any' or locale = p_locale`;
`content_hits_blocklist` becomes `SECURITY DEFINER`; direct `SELECT` on
`safety_blocklist_terms` is REVOKEd from `anon` and `authenticated` (explicitly **not** a read
policy — a blocklist visible to the people it constrains is not a control). Verify as role
`authenticated`, never as service role. Fix both defects or remove both artifacts, never one
of each.

**That is an acceptance-criteria block an agent with no memory of this conversation can
execute.** The absence of a feature census is not the blocker it appears to be.

**BUG-07 is a trap, not a breach.** `contentHitsBlocklist` has no caller anywhere in `lib/`,
so nothing is being let through today. Its consequence for stack planning is a **sequencing
edge, not a stack**: whoever wires it first gets a silent `0` — a plausible "clean" — for
every input, with both defects invisible at the call site. **Put that edge in the S2 and S3
briefs explicitly or someone will walk into it.**

---

## 6. Where this departs from the D1–D11 table-family clustering

The `cpo` census is a good taxonomy. It is not an ownership map.

1. **SPLIT D1.** Identity and profile are two directories with a thin directional seam.
   Meanwhile `profile` is fused to `social` at 5 files out and 10 in — a far tighter bond
   than anything inside D1. **Grouping by table family put the loose pair together and the
   tight pair apart.**
2. **MERGE D5 into the profile half of D1** — and understand it cannot then be un-merged
   until gate G1 lands. See §3.
3. **REJECT "D10 Sports reference — no slice, reference data."** `sports_repository.dart`
   exists, and `supabase_config.dart` carries three hardcoded sport maps in Dart
   (`sportFormats`, `sportDefaultDurations`, `sportMaxParticipants`) alongside
   `FeatureFlags.isSportEnabled(String)` and `lib/core/utils/sports_config.dart`. **Sport
   configuration is duplicated between the database and two Dart files** — a live
   consistency hazard belonging to whoever owns game creation. It goes to S3, and
   reconciling the three sources is an S3 ticket.
4. **D8 has no client-side existence as a cluster.** Treating it as one produces a phantom
   team. See §5.
5. **The census's biggest blind spot: it clustered `lib/features/`, and most of the
   finished-backend-no-client pattern is not there.** `lib/data/` is a flat directory holding
   71 repositories and ~90 model files for every domain at once — including domains with no
   feature slice.

   **Eleven repositories have zero consumers anywhere outside `lib/data/`:** `audit_safety`,
   `availability`, `bench_mode`, `display_name`, `joinability`, `localization`,
   `organiser_benefits`, `ratings`, `supabase_profile`, `venue_config`, `wallet`.

   **This does not match a "DEAD slice" label one-for-one.** `squads_repository`,
   `circle_repository` and `user_circles_repository` each have **exactly one** consumer in
   `social`'s DI. **Squads and circles are not dead in Dart — they are wired and have no
   screens.** A brief written from the "DEAD slice" label would send a developer looking for
   code that is already there.

6. **The dead surface in this codebase is repositories and flags, not screens.** Of 62
   `*_screen.dart` files, only `SavedLocationsScreen` and `SportsLibraryScreen` have a class
   name that never appears in `app_router.dart`. **Any stack brief written around
   "unreachable screens" is aimed at the wrong target.**

---

## 7. Scope findings that belong to the PO, not to a stack

Recorded here because they exist nowhere else and the next census would otherwise re-derive
them for a fourth time.

### 7a. Squads and circles appear in **none** of the 650 corpus features

The `cpo` searched all 650 rows of `11b`: **the word "squad" appears in no feature, and the
word "circle" appears in no feature.** The only near-hits are 385 "Group chat (per game)"
[1A], 386 "Group chat (general)" [2] and 400 "Group invitations" [1A] — those are messaging,
not circles.

Yet both have complete schemas and **live Dart repository layers**:

| | Schema | Dart |
|---|---|---|
| Squads | `squads` (3 policies) + `squad_members`, `squad_invites`, `squad_join_requests`, `squad_link_tokens` (all zero-policy, RPC-only) + 8 `rpc_squad_*` + `v_squad_card` | `squads_repository.dart` (112) + `_impl` (762) = **874 LOC**, consumed by `lib/features/social/providers.dart:8-9`, which has 3 importers |
| Circles | `circles` (6) + `circle_members` (5) + `post_circles`, `profile_circles`, `profile_circle_members` + `v_circle_feed` | `circle_repository` and `user_circles_repository`, one consumer each |

**Something was built twice over — schema and repository layer — against no committed
scope.** It cannot be prioritised against the roadmap because it is not on the roadmap.

**Three options, and only the PO can choose:** add them to `11b` as a section; cut them with
a decision id and delete the repositories; or record them as deliberate un-roadmapped
capability. **What is not tenable is the current state**, in which `FeatureFlags.squads` is
`true` — advertising a slice deleted in `34f9a6d` to a now-live analytics sink — and
`v_circle_feed` still returns 6 rows to `anon` (SEC-05, HIGH, open) in service of a feature
nobody has decided exists.

**Same category, same question:** `bench_mode` and `audit_safety` (0 corpus features each,
schemas live, clients deleted), and **D8 moderation** (13 tables, two routed admin screens,
zero corpus features — built for App Store compliance rather than from the roadmap).

### 7b. B.15 Achievements & Gamification is claimed by no stack

25 features, 7 of them Phase 1A. Dormant in practice — `enableEarlyBirdCheckIn = false`, the
slice is down to 690 LOC, and P-024 requires no work because "hidden" is already true — but
**dormant by nobody's decision.** Assign it to a stack or cut it with a decision id. An
unassigned section is how scope reappears mid-sprint.

---

## 8. Confirmed vs inferred

### Confirmed by command against `c46b5c5`

Per-directory file and line counts for all 20 feature directories · the full cross-feature
import matrix and the per-file detail on every edge reasoned from · `app_router.dart` 1,712
lines / 85 `GoRoute` / 1 `StatefulShellRoute` / imports from 13 of 20 feature dirs ·
`providers.dart` 39 lines / 29 exports · `supabase_config.dart` 260 lines · 71 repository
files, and the 11 with zero consumers outside `lib/data/` · 52 generated files, 45 under
`lib/data/` · 62 `*_screen.dart` with exactly 2 never named in the router ·
`profile_providers.dart` 870 lines with its import list and the 10 + 5 consumed-provider
lists · `persona_service.dart` imports nothing cross-feature · `feature_flags.dart` 17
`static const bool`, 12 true, 5 false.

### Inferred — verify before this is load-bearing

1. **Feature-ID → file mapping.** `11b`'s ID ranges were never opened. D-clusters were mapped
   to directories by name and by `supabase_config.dart`'s table constants. **Spot-check five
   IDs per stack before publishing assignments.**
2. **Table ownership coverage.** The per-stack table lists derive from the ~55 tables named
   in `supabase_config.dart`. `SCHEMA.md` counts 184. **Roughly 130 tables are not named in
   `supabase_config.dart` at all** — they have no client and therefore no stack, and stay
   with S6 until claimed. **Do not read §1's lists as a partition of 184.**
3. **The 11 zero-consumer repositories are a Dart-layer measurement only.** No database query
   was issued. Whether each corresponds to a *complete* backend is a separate claim.
4. **Staffing.** File counts and LOC, not task counts. S2 at ~177 files / ~75k lines and S3 at
   ~300 features / ~30k lines are sized on different axes and have not been reconciled into
   headcount. The S3 capacity note in §1 is a judgment, not a measurement.
5. **No runtime behaviour was verified.** Everything here is static. No app was run.
6. **§5's feature-count mapping** — see §0a. Derived against a session-relayed prose summary,
   not this document.

### Two places the codebase contradicted the docs (codebase wins, both reported)

- `PROJECT_STATE.md`'s WIRE-09 stated `FeatureFlags.messaging` was `true` at
  `feature_flags.dart:53`. It is at line 20 and it is `false`. Corrected in run 6.
- `CONTRACT.md` §4 stated `app_router.dart` is 1,745 LOC. It is 1,712.

---

## 9. To ratify

This document is a proposal and binds nothing. Until the S1–S7 boundaries, the Phase 0/1
gates and the router-module ruling carry `DECISIONS.md` ids with their rejected
alternatives, **they will be re-litigated.**
