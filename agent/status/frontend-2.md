# senior-frontend-2 — status

## 2026-09-06 — Skills audit (survey, no work)

**First entry for this seat. It has never run a task.** Dispatched by `team-lead-2` under the
CEO's instruction *"ask everyone — we don't want them similar, we want each one a professional
in their own field."* Read-only survey: no code, no git, no Jira, no `flutter`.

### What I did

Read the roster's skill bodies rather than their descriptions, filtered to what D2 (games,
meetups, competition) and D8 (moderation, safety, trust) actually need.

**Opened in full or in substantial part:**
`flutter-add-widget-test` · `flutter-add-integration-test` · `dart-add-unit-test` ·
`dart-use-pattern-matching` · `flutter-build-responsive-layout` · `codebase-design` ·
`working-with-legacy-code` (§Core Principle + change algorithm) · `release-it` (§§1–2) ·
`secure-mobile-dev-guide` (section index) · `mobile-threat-model` (STRIDE table) ·
`supabase-postgres-best-practices` (index + `lock-skip-locked`, `schema-constraints`).

**Searched by body, not by name**, across every installed skill (`~/.claude/skills`,
`One Brain/.claude/skills`, all plugin caches) for: `optimistic ui`, `race condition`,
`idempoten`, `concurren`, `realtime`, `presence`, `broadcast`, `moderation`, `abuse`,
`harassment`, `blocklist`.

### What I decided

1. **`working-with-legacy-code` is the D2 skill**, not any Flutter skill. D2's headline problem
   is finished backends with no client (leagues, squads) plus 130 shipped features with no
   characterization. Feathers' "legacy code is code without tests" and cover-and-modify is the
   exact shape of the work. A greenfield seat does not need it.
2. **`codebase-design` is mine because of `explore`**, which imports 13 files across three of my
   slices and is imported back once. That is a seam decision and the skill is the vocabulary
   for it — not a general senior-frontend habit.
3. **Nothing in the roster addresses competitive correctness.** Zero body hits for optimistic
   UI, rollback, real-time client consistency, or multi-viewer state agreement. The `supabase`
   skill names Realtime once, in its own frontmatter, and never in the body.
4. **Nothing addresses moderation UI.** The security skills protect the app from an attacker;
   D8 protects a user from another user. Different actor, no overlap. I concur with `analyst`'s
   verdict on the seven MASVS skills and did not re-derive it.
5. **The one skill covering concurrent-write correctness is one I am forbidden to act on.**
   `supabase-postgres-best-practices` (`lock-skip-locked`, `schema-constraints`,
   `data-upsert`) is exactly a waitlist promotion / squad-slot claim, and my role file says
   never author SQL. That is a routing fact for `senior-backend`, not a skill gap.

### What I touched

This file only. No repo files read for content beyond skill bodies; no repo file changed.

### What is blocked

- **Two skill gaps are `cto`/`cxo` calls, not mine to author** — real-time client consistency
  in Flutter/Riverpod, and a fail-closed moderation-UI invariant list. Reported to
  `team-lead-2` for routing.
- **`flutter-add-integration-test` cannot be adopted by me alone.** It requires
  `enableFlutterDriverExtension()` in the app entry point and `flutter drive`, which `ci.yml`
  does not run (analyze + test only). That is a `devops` decision.
- Seat remains idle on app code: Phase 0 exclusive grant (`CONTRACT.md` §4.1) is live and
  `senior-frontend-3` holds the only write grant.
