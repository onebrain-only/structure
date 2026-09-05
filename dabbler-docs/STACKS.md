# Dabbler — Ownership Stacks

**Status:** PROPOSAL. Not ratified. No `DECISIONS.md` id yet.
**Authored:** 2026-09-04 · **Measured against:** `dabbler-code` HEAD `c46b5c5`, branch `Canary`
**Source:** `cto` stack analysis, session `01MCCanB436igB4CLHdMnD2R`
**Companion docs:** `PROJECT_STATE.md` §3 and §24 (build state) · `CONTRACT.md` (permission matrix) · `Dabbler/dabbler-code/docs/SCHEMA.md` (tables)

---

## 0. What this document is, and what it rests on

This is an **ownership** partition, not a taxonomy. It answers *"what must be changed
together, and what can be changed independently"* — not *"what belongs together
conceptually."*

The stacks were derived by measuring the **import graph between the 20 directories under
`Dabbler/dabbler-code/lib/features/`** and taking ownership from its strongly-connected components.
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

---

# PART II — RATIFIED WORK

**Added 2026-09-05 by `cto`, under `DECISIONS.md` `G-015`.** §§1–9 above are the 2026-09-04
proposal and are left unedited (append-only, `CONTRACT.md` §6). §10 and §11 supersede §1 and §3
where they differ; §12 records the differences against `CONTRACT.md` §3.

**Re-measured against `dabbler-code` `c46b5c5`, branch `Canary`, 2026-09-05 — the same commit
§§1–9 were measured at.** Every number below carries the command that produced it.

## 9a. The metric, stated once

Every coupling number in §10–§12 is **E(A→B) = the count of `.dart` files inside
`lib/features/A/` containing at least one `import`/`export` of a file inside
`lib/features/B/`**, resolving both `package:dabbler/…` and relative URIs. Undirected pair
strength is `E(A→B) + E(B→A)`.

**Reproduce with** `/Users/moatazmustapha/.claude/jobs/219439e2/tmp/coupling.py` — or equivalently:

```bash
cd dabbler-code
python3 - <<'EOF'
import os,re,collections
ROOT="lib"; FEAT="lib/features"
imp=re.compile(r"""^\s*(?:import|export)\s+['"]([^'"]+)['"]""",re.M)
def sl(p):
    r=os.path.relpath(p,ROOT).split(os.sep)
    return r[1] if r[0]=="features" and len(r)>1 else None
e=collections.defaultdict(set)
for dp,_,fs in os.walk(FEAT):
    for f in fs:
        if not f.endswith(".dart"): continue
        p=os.path.join(dp,f); s=sl(p)
        if not s: continue
        for u in imp.findall(open(p,errors="replace").read()):
            if u.startswith("package:dabbler/"): t=os.path.join(ROOT,u[16:])
            elif u.startswith(("dart:","package:")): continue
            else: t=os.path.normpath(os.path.join(dp,u))
            d=sl(t)
            if d and d!=s: e[(s,d)].add(p)
for k,v in sorted(e.items(),key=lambda x:-len(x[1])): print(k,len(v))
EOF
```

### 9b. Where §§1–9's numbers do not reproduce under this metric — corrections

`G-012`'s headline coupling claim mixed two metrics inside one phrase. The **direction and the
ranking hold; three counts do not.** Corrected here rather than silently restated.

| Claim in §§1–9 / `G-012` | What reproduces at `c46b5c5` | Verdict |
|---|---|---|
| "`profile`↔`social` fused at **5 files out / 10 in**" | `profile→social` = **7** source files (14 import statements, 5 distinct target files); `social→profile` = **9** source files (10 import statements, **2** distinct target files) | **Mixed metric.** "5 out" was *distinct target files*; "10 in" was *import statements*. Under one metric the pair is **7 out / 9 in = 16**, still the strongest edge in the tree by 1.8× |
| "`auth_onboarding` reaches into `profile` at **5 files, all domain-layer**" | **4** source files, 8 import statements, 6 distinct target files. **3 of the 8 statements target `profile/presentation/providers/add_persona_provider.dart`** | **Wrong on both counts.** The seam is 4 files, and it is *not* purely domain-layer |
| "`profile` reaches back at **4 files**, all auth presentation providers" | **3** source files, 4 statements, 3 target files — all under `auth_onboarding/presentation/providers/` | Count wrong (3, not 4); "all presentation providers" is correct |
| "`explore` imports **13 distinct files** across `games`, `venues`, `location`; imported back exactly once" | `explore` imports **13 distinct target files** (games 5 + venues 5 + location 3) from **3 source files**; imported back exactly once (`games→explore`, 1 file) | **Reproduces exactly** |
| "`misc/data/datasources` — **13 of 20** feature directories import it" | **13 of 20** feature dirs; **38 files total**, of which 11 are in `lib/data/`, plus `lib/providers.dart` and `lib/core/providers/geo_providers.dart` | Reproduces, and is larger than stated — the blast radius is 38 files, not 13 |
| `app_router.dart` 1,712 LOC · 85 `GoRoute` · `StatefulShellRoute` at `:746` · 13 of 20 feature dirs | All reproduce. Also: **83 imports, 69 from feature slices, 25 of those from `auth_onboarding` alone**; **80 top-level entries** in `_routes` (`:444`) | Reproduces |
| `profile_providers.dart` 870 lines | Reproduces | Reproduces |
| §3 G0c "the five game-composer screens" in `misc/` | `misc/presentation/screens/` holds **10** screens, not 8. `activities_screen_v2.dart` and `rewards_screen.dart` were **named nowhere in §§1–9 and are both live routed** (`app_router.dart:54-55`, routes at `:903` and `:914`) | **Gap.** G0c was incomplete; §10 P0-4 corrects it |

---

## 10. PHASE 0 — the executable plan

**Authorised by `G-015` Ruling 1.** No developer is dispatched onto app feature work until this
lands. This section is written so the `po` can ticket it and one `senior-frontend-N` can execute
it with no memory of this document.

### 10.0 Who executes it, and why one seat

**One senior, exclusively, for the duration.** Phase 0 touches `lib/app/`, `lib/core/`,
`lib/data/` and five feature directories. Every one of those is either CONTENDED or SHARED under
`CONTRACT.md` §4 — *one agent inside at a time*. Two developers in Phase 0 is not parallelism, it
is a merge conflict with a schedule attached.

**It must be the senior who owns `auth_onboarding`** — `senior-frontend-3` under §11, or
`senior-frontend-1` if Phase 0 is ticketed before §11 is reconciled into `CONTRACT.md` §3.
**Reason, measured:** 25 of the router's 69 feature imports and 18 of the 20 pre-shell route
entries are `auth_onboarding`'s. That seat carries the largest single share of the file being
split. **No junior enters any Phase 0 ticket** (`CONTRACT.md` §4).

**What may run in parallel with Phase 0 — the complete list:**

| Seat | May run | Why it is disjoint |
|---|---|---|
| `senior-backend` | security remediation in `supabase/**` | Phase 0 touches no path under `supabase/` |
| `content-manager` | EN/AR strings | Phase 0 touches no `.arb` file. **P0-5 must land before any generated-l10n Dart is committed** |
| `qa`, `analyst`, `cxo`, `cpo`, `pm`, `po` | read-only and document work | no write path into `lib/` |

**Nothing else.** In particular **no work in `lib/data/**`** — P0-2 rewrites imports in 11 files
there.

### 10.1 P0-1 — Route-inventory golden test. **This is first and it is not optional.**

**Finding that forces it:** `grep -rln "app_router\|AppRouter\|GoRouter" test/` returns **nothing**.
**Nine** `*_test.dart` files (`find test -name '*_test.dart' | wc -l`), 103 tests, and **not one
touches the router.** A 1,712-line refactor of the
app's most contended file currently has zero regression coverage. `flutter test` staying green
proves nothing about P0-3, because it never proved anything about the router in the first place.

**What comes into existence:** `Dabbler/dabbler-code/test/app/route_inventory_test.dart`.

**What it asserts,** walking `AppRouter.router.configuration.routes` recursively (go_router
`^12.0.0`, `pubspec.yaml:68`) and flattening to an ordered list of `(fullPath, name, runtimeType)`:

1. the flattened list is **exactly** the golden list checked in beside it;
2. the count of `GoRoute` is **85**;
3. exactly one `StatefulShellRoute.indexedStack` exists, with **4** `StatefulShellBranch`.

**Done when:** the test passes against **unmodified** `app_router.dart`, and passes again after
deliberately reordering any two top-level entries **fails** it. Both directions must be
demonstrated in the ticket comment — a golden test that cannot fail is not coverage.

**If `RouteConfiguration.routes` proves not to be public in the pinned version,** fall back to
asserting `router.routerDelegate.currentConfiguration` after `router.go(path)` for all 85 paths,
and say so on the ticket. **Do not upgrade `go_router` to make the test easier** — that is a
dependency change and it is not authorised (`G-015` scope).

### 10.2 P0-2 — `misc/data/datasources/**` → `lib/core/data/`

Cheapest high-value unblock, and it is bigger than §3 G0a said: **38 importing files across 13 of
20 feature directories, plus 11 files in `lib/data/`, `lib/providers.dart`, and
`lib/core/providers/geo_providers.dart`.**

**Moves — 3 files, unchanged content, path only:**

| From | To |
|---|---|
| `lib/features/misc/data/datasources/supabase_client.dart` | `lib/core/data/supabase_client.dart` |
| `lib/features/misc/data/datasources/supabase_error_mapper.dart` | `lib/core/data/supabase_error_mapper.dart` |
| `lib/features/misc/data/datasources/supabase_remote_data_source.dart` | `lib/core/data/supabase_remote_data_source.dart` |

**Done when:** `grep -rn "misc/data/datasources" lib/ test/` returns **zero** lines ·
`lib/features/misc/data/` no longer exists · `flutter analyze --no-pub --no-fatal-infos` exits 0
with **0 errors, 0 warnings** · `flutter test` exits 0 on **103 tests** · P0-1 green.

**Rule for the executor:** import-path edits only. **Do not reformat, reorder or "tidy" any of the
38 files** (`CONTRACT.md` §4 rule 1). A diff that touches more than one line per file, outside the
three moved files, is a rejection.

### 10.3 P0-3 — Split `app_router.dart`

**Two tickets, and P0-3a comes first.**

#### P0-3a — Prove which routes may be reordered

GoRouter matches in declaration order, so a split that changes order changes behaviour.
**Establish the constraint set before moving anything.**

**Deliverable:** a table, posted on the ticket, of every pair of the 80 top-level entries in
`_routes` (`app_router.dart:444`) whose path patterns can match a common URI. For each such pair,
their relative order is **frozen**. Everything not in that table is free to move.

**Watch for specifically:** `/game/:gameId` (`:865`) against `/sports/games/:gameId` (`:815`);
`'${RoutePaths.error}:message'` (`:1666`), which is a trailing catch-all shape and is **last for a
reason**; and any `RoutePaths.*` constant that resolves to a bare `:param` segment at a depth
where a literal sibling exists — resolve the constants from
`lib/utils/constants/route_constants.dart`, do not reason from the constant name.

**Done when:** the frozen-pair table exists, and `'${RoutePaths.error}:message'` is explicitly
listed as last-in-order regardless of module.

#### P0-3b — Extract the modules

**What comes into existence** — `lib/app/routes/` does not exist today (`find lib/app -type f`
returns exactly one file):

| New file | Exports | Bucketing rule |
|---|---|---|
| `lib/app/routes/identity_routes.dart` | `List<RouteBase> identityRoutes` | builder constructs a screen under `features/{auth_onboarding,username_engine,app_boot}/` |
| `lib/app/routes/profile_social_routes.dart` | `profileSocialRoutes` | `features/{profile,social,home,news,moderation}/` |
| `lib/app/routes/play_places_routes.dart` | `playPlacesRoutes` | `features/{games,venues,explore,location,venue_submissions,activities}/` |
| `lib/app/routes/notification_routes.dart` | `notificationRoutes` | `features/notifications/` |
| `lib/app/routes/platform_routes.dart` | `platformRoutes` | `features/{admin,error,misc}/`, settings, help, about, `/` and `/landing` |
| `lib/app/routes/home_shell_route.dart` | `RouteBase homeShellRoute` | the `StatefulShellRoute.indexedStack` at `:746`–`:814` and its 4 branches, moved whole |

**Bucket by the owning slice of the screen the builder constructs, never by the path string.**
`RoutePaths.socialNotifications` (`:1544`) builds a `social` screen, not a `notifications` one.

**What stays in `app_router.dart`:**

- `_handleRedirect` (`:149`–`:443`) — **entire, unmodified, not distributed.** It carries
  onboarding-step enforcement, an OAuth-callback profile check (`:268`–`:279`) and a
  shared-game-link branch (`:255`). **Redirect is policy and policy stays in one head.** A Phase 0
  diff that touches a single line inside this range is a rejection.
- `appRouter` / `AppRouter.router` (`:120`, `:142`–`:145`), `routerRefreshNotifier`.
- `_routes`, reduced to an ordered concatenation of the six module lists, respecting P0-3a's
  frozen pairs.

**Done when:** P0-1 golden test green **with no edit to the golden file** — that is the whole
proof · `app_router.dart` ≤ **450 LOC** · `app_router.dart` has **≤ 6** `features/` imports (down
from 69) · `flutter analyze` 0 errors 0 warnings · `flutter test` 103 green · no `.dart` file
outside `lib/app/` changed.

**Explicit non-goal:** do not fix, rename, delete or re-path any route while inside this refactor,
however wrong it looks (`CONTRACT.md` §4 rules 3 and 4). Report it; it gets its own ticket.

### 10.4 P0-4 — Empty `misc/presentation/screens/` down to its residue

`misc/` is not a feature. It is two unrelated things under one name. P0-2 removes the
infrastructure half; this removes most of the screens half.

**§3 G0c named 8 screens. There are 10.** The two it missed are both **live routed**:

| Screen | Destination | Evidence |
|---|---|---|
| `game_composer_screen.dart` | `features/games/presentation/screens/` | routed `app_router.dart:92`; composer |
| `sport_format_step.dart` | `features/games/presentation/screens/` | composer step |
| `venue_slot_step.dart` | `features/games/presentation/screens/` | composer step |
| `player_invitation_step.dart` | `features/games/presentation/screens/` | composer step |
| `review_confirmation_step.dart` | `features/games/presentation/screens/` | composer step |
| **`activities_screen_v2.dart`** | `features/activities/presentation/screens/` | **imported `app_router.dart:54`, routed `:903`. Named nowhere in §§1–9** |
| **`rewards_screen.dart`** | `features/rewards/presentation/screens/` | **imported `app_router.dart:55`, routed `:914`. Named nowhere in §§1–9** |
| `help_center_screen.dart` | **stays** | platform surface |
| `transactions_screen.dart` | **stays** | Commerce is dormant; §1 S7 |
| `participation_payment_step.dart` | **stays** | Commerce is dormant; §1 S7 |

**Ruling on the last three: they stay in `misc/`.** Creating a holding directory for two dormant
Commerce screens invents a slice for a domain the PO has not scheduled, and resurrecting the
payments slice deleted in `34f9a6d` as a side effect of a refactor is exactly the "while I'm in
here" failure `CONTRACT.md` §4 exists to stop.

**Done when:** `lib/features/misc/` contains exactly `presentation/screens/` with exactly those
**three** files and nothing else · analyze 0/0 · 103 tests green · P0-1 green.
**Sequencing: P0-4 runs after P0-3b**, so the router import churn happens once.

### 10.5 P0-5 — `build_runner` becomes a `devops`-owned commit-time step

**52 generated files, 45 of them under `lib/data/`** (`find lib -name '*.g.dart' -o -name
'*.freezed.dart' | wc -l`). `CONTRACT.md` §3 already says these are never hand-edited; it does not
say who regenerates them.

**Decision:** `devops` owns regeneration. A developer commits its source change only; `devops`
runs `dart run build_runner build -d` and commits the generated output as a **separate commit**.

**Why:** a stack that commits regenerated output alongside its source change produces a diff in
which 45 machine-written files hide the three hand-written ones. That diff is unreviewable, and at
sixteen developers two of them running `build_runner` concurrently produces a conflict in files
nobody authored.

**Done when:** the step is written into `agent/WORKFLOWS.md` by its owner and `devops` has run it
once end to end on a P0 ticket. **This is a process change, not code — it is the one Phase 0 item
that does not touch `lib/`, and it can run concurrently with P0-1 through P0-4.**

### 10.6 Phase 0 order, and what "Phase 0 has landed" means

```
P0-1 (golden test)  ──►  P0-2 (datasources)  ──►  P0-3a (order proof)  ──►  P0-3b (split)  ──►  P0-4 (misc screens)
P0-5 (build_runner process)  ──────────────── concurrent, no lib/ writes ────────────────►
```

**Phase 0 has landed when all five are Done and, at the resulting commit:**
`flutter analyze --no-pub --no-fatal-infos` exits 0 on 0 errors / 0 warnings · `flutter test`
exits 0 on 103 tests across 9 files **plus** `route_inventory_test.dart` · `app_router.dart`
≤ 450 LOC with ≤ 6 feature imports · `grep -rn "misc/data/datasources" lib/ test/` is empty ·
the Cloudflare `Canary` build is green on `canary.dabbler.pro`. **Only then are the sixteen
developer seats dispatched.**

**Phase 1 (`profile_providers.dart`, §3 G1) is NOT in Phase 0 and does not gate dispatch.** It
gates one thing: whether `team-lead-1`'s cluster can later be split across two leads. See §11.4.

---

## 11. THE PARTITION — five team leaders, from measured coupling

### 11.1 The graph the partition is cut from

Undirected pair strength at `c46b5c5`, all pairs ≥ 3, `misc` excluded because P0-2 and P0-4
dissolve it:

```
profile ── social            16      ◄── strongest edge in the tree
home ── social                8
auth_onboarding ── profile    7
location ── social            6
explore ── games              4
explore ── venues             3      games ── location        3
explore ── location           3      venues ── location       3
explore ── profile            3      auth_onboarding ── games 3
auth_onboarding ── social     3
```

Two dense components fall out, joined only by thin edges: **{profile, social, home, news}** and
**{games, venues, explore, location, venue_submissions}**. `notifications` is near-isolated
(heaviest edge: 2). `admin` has **zero** cross-feature edges.

### 11.2 The five leads

| Lead | Slices | Files | LOC | Coupling evidence for the grouping |
|---|---|---|---|---|
| **`team-lead-1`** — Profile, Social & Feed | `profile`, `social`, `home`, `news`, `moderation` | 167 | **69,485** | Holds the **16**-weight `profile↔social` edge and the **8**-weight `home↔social` edge intact. These are the two most expensive cuts available anywhere in the tree; both are internal here. `news↔profile`=1, `news↔social`=1, `moderation↔social`=1, `moderation↔profile`=1 |
| **`team-lead-2`** — Play & Places | `games`, `venues`, `explore`, `location`, `venue_submissions`, `activities` | 91 | 29,872 | Internal edges `explore↔games`=4, `explore↔venues`=3, `explore↔location`=3, `games↔location`=3, `venues↔location`=3, `games↔venues`=2 — **18 in total, all internal.** `explore` imports 13 distinct target files across `games`/`venues`/`location` from 3 source files and is imported back exactly once: it is a composition surface, not a peer |
| **`team-lead-3`** — Identity & Access | `auth_onboarding`, `username_engine`, `app_boot` | 53 | 13,127 | Cut at the `auth_onboarding↔profile` seam, weight **7** — the cheapest cut that separates a slice of this size (48 files / 12,896 LOC). The seam is directional: `auth→profile` 4 files, `profile→auth` 3 files, and every one of `profile`'s 4 back-imports targets `auth_onboarding/presentation/providers/` |
| **`team-lead-4`** — Rewards, Staff & Commerce | `rewards`, `admin` · **+ Commerce (`D4`) on activation** | 6 | 1,579 | `rewards↔home`=1, `rewards↔profile`=1. `admin` has **zero** cross-feature edges — it is separable at no cost from anywhere. Deliberately the lightest live load because it holds the largest dormant backlog |
| **`team-lead-5`** — Notifications & Messaging | `notifications` (+ `lib/services/notifications/**`) | 19 | 4,259 | Heaviest edge is **2** (`notifications↔activities`, `notifications↔profile`). **This boundary already works. Do not touch it** |

Unassigned by design: `core` (1 file, 18 LOC) and `error` (1 file, 53 LOC) are platform residue;
`misc` is dissolved by Phase 0. Total: 351 feature files, 125,851 LOC — reconciles.

### 11.3 Platform is not a sixth team

`lib/app/**`, `lib/core/**`, `lib/data/**`, `lib/widgets/**`, `lib/utils/**`, `lib/themes/**`,
`lib/design_system/**`, `lib/providers.dart`, `lib/l10n/**` and the four contended files stay
**SHARED with no single writer**, governed by `CONTRACT.md` §4.

**Rejected: create a platform lead.** `G-014` fixes the roster at five leads and this decision
does not reopen it. A sixth lead would have to be cut out of the five, and every candidate cut
costs more than the coordination it saves.

**The one exception is Phase 0 itself**, which is platform work with no owner today. §10.0 gives
it a single named executor for its duration and takes the surfaces out of shared use while it
runs. **After Phase 0 the surfaces return to §4 discipline.**

### 11.4 Is five the right number? — the answer, stated plainly

**Five is the right number of cuts. It is the wrong number of equal loads, and no roster change
fixes that.**

The coupling graph supports exactly five disjoint groups with a total cut cost of 24 file-edges.
But the load lands **55% / 24% / 10% / 1.3% / 3.4%** by LOC. `team-lead-1` holds more than half
the feature tree with one senior and two juniors; `team-lead-4` holds 1,579 lines.

**Adding a sixth lead does not help, and this is the measured reason.** The only place a sixth
lead could go is inside `team-lead-1`'s cluster, and every cut there is expensive:

| Candidate cut of `team-lead-1` | Cost | Verdict |
|---|---|---|
| `profile` \| `social` | **16** | Most expensive cut in the tree. **Two teams in `profile_providers.dart` on day one** |
| `social` \| `home` | 8 | `home` is 7 files; a 7-file team is not a team |
| move `news` out | 3 | Cheap, but `news` rendering already lives in `social` (`social/presentation/widgets/kind_cards/news_kind_card.dart`). Available if `team-lead-4` needs mass; the price is 3 |

**The imbalance is a code fact, not an org fact, and it has a code fix: Phase 1.** Splitting
`profile_providers.dart` (870 lines, three domains, `social` consumes 10 providers from it and
`home` 5) is what drops `social→profile` from 9 source files toward zero — **9 of its 10 import
statements target that one file.** After Phase 1 the `profile|social` cut stops costing 16 and
`team-lead-1` becomes divisible.

**Recommendation to the CEO and `pm`:** keep five. Load `team-lead-1` with the senior and both
juniors and hold `team-lead-4`'s and `team-lead-5`'s juniors idle rather than giving them work
outside their slices — `AGENTS.md` §5 puts the ceiling on parallelism at disjoint file sets, and
an idle seat costs nothing while a wandering one serialises everybody. **Schedule Phase 1 as the
next structural ticket after Phase 0**, not as a Phase 2 nicety: it is the only lever that
rebalances the roster.

### 11.5 What this partition does NOT settle

- **`B.9` Organiser dashboard.** §4 argues it goes to Play & Places; `G-013` argues it is the
  unstaffed admin-dashboard project. **Both readings stand; this decision rules neither**, because
  it is a product-scope question and the coupling graph is silent on it — organiser has no slice.
- **`D4` Commerce activation.** `team-lead-4` is named its custodian. Activation is a `pm`
  decision with the CEO (`AGENTS.md` §1).
- **The two design systems.** Unchanged, still closed under `G-011`, now joint `cxo` + `cto`.

---

## 12. DELTA against `CONTRACT.md` §3 — every difference and its price

`CONTRACT.md` §3's application-code map is **PROVISIONAL** under `G-015`. `analyst` owns that
file; the amendment below is **proposed by `cto`, not applied.**

| # | Slice | `CONTRACT.md` §3 (provisional) | §11 (measured) | Cost of leaving it unfixed |
|---|---|---|---|---|
| 1 | **`home`** | **absent — no writer** | `team-lead-1` | **This is the serious one.** `home` is 7 files / 3,403 LOC and contains `main_navigation_screen.dart`, the app shell reached by the `StatefulShellRoute`. It has the **8**-weight edge to `social`. An unowned slice with a shell in it is how the audit's 23 unowned slices happened |
| 2 | **`core`** | **absent — no writer** | platform residue (1 file, 18 LOC) | Negligible in size, but name it or it recurs |
| 3 | `auth_onboarding`, `username_engine`, `app_boot` | `team-lead-1` | **`team-lead-3`** | Leaving them: `team-lead-1` carries 220 files / 82,612 LOC — **66% of the feature tree on one senior.** This is the single largest correction |
| 4 | `venues`, `venue_submissions` | `team-lead-3` | **`team-lead-2`** | Splits the Play & Places component. Price: `explore↔venues`=3, `games↔venues`=2, `venues↔location`=3 become **cross-team edges — 8 file-edges of standing coordination** |
| 5 | `explore`, `location` | `team-lead-5` | **`team-lead-2`** | Same component split, a third way. Price: `explore↔games`=4, `explore↔venues`=3, `explore↔location`=3, `games↔location`=3, `venues↔location`=3 = **16 more cross-team file-edges.** Combined with #4, the provisional map cuts an 18-edge component **three ways** and pays 24 of those 18 edges twice over as coordination |
| 6 | `explore`, `location` on `team-lead-5` alongside `notifications` | — | `notifications` alone | `notifications`'s heaviest edge to anything is **2**. Pairing it with a 26-file discovery cluster gives lead 5 two unrelated mental models and no shared code |
| 7 | `activities` | `team-lead-2` | `team-lead-2` | **No change.** Listed because §11 keeps it while moving its neighbours |
| 8 | `moderation` | `team-lead-2` | `team-lead-1` | Price of leaving it: **2** (`moderation↔social`=1, `moderation↔profile`=1). **Merely different, not wrong** — take it or leave it |
| 9 | `admin` | `team-lead-2` | `team-lead-4` | Price: **0** — `admin` has no cross-feature edges. Preference only: §5 argues a staff console does not belong inside a consumer-product stack |
| 10 | `misc` | `team-lead-1` | **dissolved by Phase 0**; 3 residual screens shared | Leaving it: 13 of 20 feature dirs keep importing into one lead's directory |
| 11 | `news` | `team-lead-1` | `team-lead-1` | **No change**, but §11.4 records it as the cheap (cost 3) rebalancing lever if `team-lead-4` needs mass |
| 12 | `profile_providers.dart` | `senior-frontend-1`, "treat as contended" | **unchanged, and correct** | Confirmed: 9 of `social`'s 10 import statements into `profile` target this one file. The contended treatment is the right call and stays until Phase 1 |
| 13 | `lib/app/app_router.dart` | CONTENDED | CONTENDED **until Phase 0**, then 6 modules each following its lead | After P0-3b, five leads write their own module and only the assembly stays contended |

**Slices that move, in one line:** `auth_onboarding`, `username_engine`, `app_boot` → lead 3 ·
`venues`, `venue_submissions`, `explore`, `location` → lead 2 · `moderation` → lead 1 ·
`admin` → lead 4 · `home` and `core` gain a writer for the first time · `misc` dissolves.

**Stack labels that no longer describe the code.** `AGENTS.md` §1 gives lead 3 "D3 Venues · D10
Sports reference" and lead 5 "D6 Notifications · D9 Discovery". Under §11 lead 3 holds Identity
and lead 5 holds Notifications only. **The `D`-labels are a feature taxonomy and stay useful for
deciding *what* to work on; they are no longer the write boundary.** `G-013` already drew that
distinction — this makes it concrete.
