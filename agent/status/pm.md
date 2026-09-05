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
