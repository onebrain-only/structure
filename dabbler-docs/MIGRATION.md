# Migration record — dabbler repo split into One Brain (2026-09-02)

## Why this file exists

On 2026-09-02 the `dabbler` repo at the old path `~/Desktop/dabbler` was split in
two. If a session, an agent, a script, or a stale absolute path reference expects
something at its pre-migration location and can't find it, the mapping below says
where it actually is now. Read this before assuming something was lost.

## Path mapping

| Old path (pre-migration) | New path |
|---|---|
| `~/Desktop/dabbler` (repo root) | `~/Desktop/One Brain/dabbler` (same repo, same `.git`, same remote — only the parent directory changed) |
| `~/Desktop/dabbler/.claude/` | `~/Desktop/One Brain/.claude/` |
| `~/Desktop/dabbler/.agents/` | `~/Desktop/One Brain/.agents/` |
| `~/Desktop/dabbler/.claude-flow/` | `~/Desktop/One Brain/.claude-flow/` |
| `~/Desktop/dabbler/.kilo/` | `~/Desktop/One Brain/.kilo/` |
| `~/Desktop/dabbler/.opencode/` | `~/Desktop/One Brain/.opencode/` |
| `~/Desktop/dabbler/.mcp.json` | `~/Desktop/One Brain/.mcp.json` |
| `~/Desktop/dabbler/CLAUDE.md` | `~/Desktop/One Brain/CLAUDE.md` |
| `~/Desktop/dabbler/docs/DECISIONS.md` | `~/Desktop/One Brain/docs/DECISIONS.md` |
| `~/Desktop/dabbler/docs/PROJECT_STATE.md` | `~/Desktop/One Brain/docs/PROJECT_STATE.md` |
| `~/Desktop/dabbler/docs/LEARN.md` | `~/Desktop/One Brain/docs/LEARN.md` |
| `~/Desktop/dabbler/docs/CONTRACT.md` | `~/Desktop/One Brain/docs/CONTRACT.md` |
| `~/Desktop/dabbler/docs/AGENTS.md` | `~/Desktop/One Brain/docs/AGENTS.md` |
| `~/Desktop/dabbler/docs/BRIEF.md` | `~/Desktop/One Brain/docs/BRIEF.md` |
| `~/Desktop/dabbler/docs/MANIFESTO.md` | `~/Desktop/One Brain/docs/MANIFESTO.md` |
| `~/Desktop/dabbler/docs/ROADMAP.md` | `~/Desktop/One Brain/docs/ROADMAP.md` |
| `~/Desktop/dabbler/docs/WORKFLOWS.md` | `~/Desktop/One Brain/docs/WORKFLOWS.md` |
| `~/Desktop/dabbler/docs/STATUS.md` | `~/Desktop/One Brain/docs/STATUS.md` |
| `~/Desktop/dabbler/docs/status/*` | `~/Desktop/One Brain/docs/status/*` |
| `~/Desktop/dabbler/docs/briefs/*` | `~/Desktop/One Brain/docs/briefs/*` |

## What did NOT move — still inside `One Brain/dabbler/`

Everything else: `lib/`, `android/`, `ios/`, `macos/`, `web/`, `assets/`, `test/`,
`integration_test/`, `supabase/`, `scripts/`, `.github/`, `.maestro/`,
`pubspec.yaml`/`.lock`, `analysis_options.yaml`, `.env`/`.env.example`,
`firebase.json`, `l10n.yaml`, `devtools_options.yaml`, `package.json`, `run.sh`,
`build_ios.sh`, and the technical docs that describe the app itself:
`docs/ARCHITECTURE.md`, `docs/SCHEMA.md`, `docs/CONVENTIONS.md`, `docs/README.md`,
`docs/LOCATION.md`, `docs/NOTIFICATIONS.md`, `docs/APPLE_REVIEW_SIGNIN.md`,
`docs/PLAN.md`, `docs/RESEARCH.md`, `docs/flutter_localization_checklist.md`,
`docs/screen-report.md`.

## Why named agents (cto, backend-owner, etc.) stopped resolving

Their registry is scoped to the session's working directory at launch. The session
that did this migration launched from the old `~/Desktop/dabbler` path, which no
longer exists (it's now `One Brain/dabbler`) — so its agent registry broke mid-move,
as expected. **A session launched from `~/Desktop/One Brain` (the new root, not the
`dabbler` subfolder) should resolve the full agent roster again**, since
`.claude/agents/` now lives at that root.

## Git state at time of migration

- `dabbler` repo: cleanup committed locally (`8f19922`, `7420408`), **not pushed**.
  Remote (`dabblersport/webapp`) still shows the old, unsplit history — nothing
  public has changed yet.
- `One Brain` repo: brand-new local repo (`abf851d`), no remote. The moved
  governance docs' history before 2026-09-02 lives only in the `dabbler` repo's
  history up to commit `a81da87` — `git log` on a file now under `One Brain/docs/`
  won't show anything before this migration unless you look in the old `dabbler`
  history for the same filename.
- The `.mcp.json` moved to `One Brain/` contains a live GitHub PAT — flagged to the
  PO for rotation, not yet acted on.

## Known harmless artifact

Right after the move, this session's own background hooks (claude-flow
intelligence, configured before the move) briefly recreated an empty
`~/Desktop/dabbler/.claude-flow/data/pending-insights.jsonl` at the *old* path —
a stale in-memory reference in this one session, not a sign anything else was
left behind. Its 3 lines were copied into `One Brain/.claude-flow/data/`. The
leftover empty directory at the old path is harmless and can be deleted manually
whenever convenient; a fresh session started at the new `One Brain` path won't
recreate it.

## If something still seems missing

Check this table first. If a file genuinely isn't at its mapped new location, it
likely means it was created *after* this migration in a session still pointed at
the old `dabbler` path (before the registry break was noticed) — check
`~/Desktop/dabbler` (the old, now-orphaned path) directly before assuming data loss.

## Second rename — 2026-09-02 (same day, later)

Per the PO's confirmed target layout:

```
Desktop/One Brain/
  CLAUDE.md
  .claude/agents/ ...
  dabbler-code/     (was: dabbler/)
  dabbler-docs/     (was: docs/)
```

| Old (from the first split, same day) | New |
|---|---|
| `One Brain/dabbler/` | `One Brain/dabbler-code/` |
| `One Brain/docs/` | `One Brain/dabbler-docs/` |

Nothing else moved. This was a plain rename (`mv`) on both — `dabbler-code`'s `.git`,
remote, and history are untouched, exactly as the first move preserved them.

Updated as part of this rename:
- `One Brain/.gitignore` — now ignores `dabbler-code/` (was `dabbler/`).
- `dabbler-code/docs/README.md` — pointer updated to `../dabbler-docs/`.
- All `.claude/agents/*.md` files and `CLAUDE.md` — every bare `docs/X.md` reference
  disambiguated to either `dabbler-docs/X.md` (governance: DECISIONS, PROJECT_STATE,
  LEARN, CONTRACT, AGENTS, BRIEF, MANIFESTO, ROADMAP, WORKFLOWS, STATUS, status/,
  briefs/) or `dabbler-code/docs/X.md` (technical: ARCHITECTURE, SCHEMA, CONVENTIONS,
  PLAN, README). This also fixed a pre-existing ambiguity from the first split, where
  agent definitions referenced bare `docs/X.md` without saying which of the two
  `docs/` folders they meant.

Not yet swept: the governance docs' own bodies (`DECISIONS.md`, `CONTRACT.md`, etc.)
may still contain bare `docs/` self-references from before either split — not fixed
in this pass, flagged if it comes up.
