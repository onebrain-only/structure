# agent/status/senior-backend.md

**Owner:** `senior-backend` (write) · all agents (read)

Append newest-first, in the FORMAT block of `agent/STATUS.md`. **`agent/WORKFLOWS.md` §1 rule 5:**
no task is complete until its entry is saved — a refusal, a diagnosis or a question answered
still gets one.

---

# LOG

_No entries yet._

## 2026-09-06 — Skills audit of this seat (survey, `team-lead` dispatch)

**Did.** Read-only survey. No SQL run, no migration touched, no Supabase call of any kind.
Read `agent/roles/senior-backend.md` (98 lines), `ls agent/skills/` (74), `agent/skills/AVAILABLE.md`,
`Dabbler/dabbler-docs/CONTRACT.md` §3, and opened the bodies of nine candidate `SKILL.md` files.

**Touched.** This file only.

**Decided.**
- Two skills claimed as core to this seat: `supabase` (repo, 112 lines + `references/`) and
  `supabase-postgres-best-practices` (repo, 64 lines + **34** reference files, wired to zero seats today).
- One repo skill claimed with a carve-out: `diagnosing-bugs`, for the feedback-loop discipline
  applied to a SQL probe rather than a test.
- Rejected after opening: `backend-patterns` (Node/Express/Next.js REST, not Postgres),
  `security-review` (`process.env` / TS web-app checklist), `verification-quality`
  (`npx ruflo` CI catalogue for the claude-flow repo, not this product), `system-design`,
  `tdd`, `domain-modeling` for this seat. `ddia-systems` accepted as reference-only, not a routine.
- The six mobile-security skills `cto` claims are all client-side; only `network-security-check`
  even mentions Postgres/RLS. **None of them is mine.** The database-security gap is real and unfilled.
- **Conflict found and flagged, not resolved:** the repo `supabase` skill's "Making and Committing
  Schema Changes" section instructs the reader to change schema with `execute_sql` and to iterate
  live. For this seat that is a `CONTRACT.md` §3 / decision `019` violation — `cto` is the only seat
  that may apply. The skill is safe for this seat only with that section carved out. Raised to
  `team-lead`; not amended (skills are not this seat's write surface).

**Blocked.** Nothing. Survey answered in full; no follow-up owed by this seat.
