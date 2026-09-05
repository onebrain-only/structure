# junior-frontend-3a — status log

## 2026-09-06 — Skills audit of this seat (survey, from `team-lead`)

**What it was.** A read-only survey, not work: four questions about which skills the
junior-frontend seat needs. First entry in this file — this seat has never run a task.

**What I did.** Read `agent/roles/junior-frontend-3a.md`, listed `agent/skills/` (75 entries
including `AVAILABLE.md`, so **74 skills**), read `agent/skills/AVAILABLE.md`, opened the
frontmatter of 12 repo skills and the bodies of 7 `dart-flutter` plugin skills, and checked
`Dabbler/dabbler-code/docs/CONVENTIONS.md` for whether it answers "which example do I copy".

**What I touched.** This file only. No `lib/`, no `test/`, no git, no Jira, no `flutter`
command. `CONTRACT.md` §4.1 bars this seat from Phase 0 and Phase 0 is live.

**What I decided.**
- The seat's reflex table is nearly right and needs **removals, not additions**. Of the five
  `dart-flutter` candidates offered, I would take **none** as a standing reflex.
- `flutter-fix-layout-issues` — cited in my role file — is the one plugin skill worth keeping,
  and it is already there.
- `flutter-apply-architecture-best-practices` is actively dangerous for this seat: it prescribes
  MVVM/`ChangeNotifier` and a `lib/data/services/` tree, both of which contradict this repo
  (Riverpod 2.x three-layer stack; `lib/data/**` is not a junior's). It is not on my list and
  should not reach any junior.
- The one real gap is **finding the canonical example** — the thing my whole seat is defined by.
  There is no tool for it and no index. `docs/CONVENTIONS.md` gives naming rules, not
  `file:line` exemplars.

**What is blocked.** Nothing. Survey answered; no follow-up requested.
