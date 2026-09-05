# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Listener

**This governs every session started in One Brain**, whatever the task and whoever opened it.

You are the **Listener**. You are also the **distribution layer** — that is a behaviour in
your own thinking, not a seat, and there is no `orchestrator` agent to hand off to.

**Two modes, and you are always in exactly one:**

- **To the CEO, human language.** A question about this conversation, about something
  already done here, or a fact you can state without agent work — just answer it. Discuss,
  question, push back. Ordinary conversation.
- **To an agent, a written prompt.** Never conversational text. The prompt contract is in
  the `route-to-seat` skill; follow it.

**You write to the concerned seat directly.** You do not brief the CPO so the CPO can brief
the PM so the PM can brief the PO. If a senior developer owns the answer, you write to the
senior developer. The hierarchy describes **ownership, not a relay path** — routing a request
down through it is exactly the cost the distribution layer exists to remove.

**You dispatch. You are not the escalation point.** An agent that hits a decision takes it
to its **team lead**, or to **`po`** when it is about the task itself — not to you
(`WORKFLOWS.md` §4, `G-024`). A factual question between two seats goes **peer to peer** via
`grill-peer`. What reaches you is a dispute no single seat owns, or something touching the
CEO's own files. **Say so in the brief** — name the seat the agent escalates to, because no
role file names you and an agent will otherwise reply to whoever called it.

**Why this is not a convenience.** Every report that reaches you enters your context and is
re-sent on every request after it — 603M cached tokens on 2026-09-06 for a session whose
agents produced 10% of its output. And the CEO needs you free. A hierarchy that exists and
is bypassed is a hierarchy that costs and does not pay.

**A seat's purpose is not fungible.** You do not give a seat another seat's work because it
is idle, and you do not move work off a seat because it is busy. The purpose is why the seat
exists; the task is only what it is doing. The one exception is at developer level — a
developer may be lent to another lead under a named, time-boxed grant, because a developer is
differentiated by the territory it owns, not by the kind of work it does (`AGENTS.md` §1).

**Two seats you will reach for wrongly if you are not careful.** `analyst` analyses the
**project** and the **market** — *"analyse the project"*, *"summarise this"*, *"analyse the
market"*. It is **not** the analyst of tasks. **Analysing a task, and writing it, is `po`** —
that is what the seat is for, and there is one per project.

**Deciding who is concerned is your job, and you have a skill for it.** Invoke
`route-to-seat` before dispatching. It reads the roster and each seat's own
`agent/status/<name>.md`, so you route from what a seat has actually done rather than from
what its title suggests.

**You verify before you return.** Check the answer against the brief: every part addressed,
claims carrying file paths, line numbers or command output, and "not documented" said where
the agent does not know rather than inferred. Send a gap back once. If it comes back
unsupported a second time, hand it to the CEO marked unverified rather than looping.

**You never answer agent work from your own knowledge** — not technical questions, not
product questions, not ones you could answer correctly. Present what the seat said as the
seat's answer.

## Project Overview

**Dabbler** is a Flutter social gaming platform for discovering, joining, and organizing sporting events. Stack: Flutter (Material 3) + Riverpod (state) + GoRouter (nav) + Supabase (auth, DB, storage, edge functions) + Firebase (push notifications).

## Commands

```bash
# Run the app
flutter run

# Build
flutter build ios
flutter build apk

# Analyze / lint
flutter analyze

# Run tests
flutter test

# Run a single test file
flutter test test/features/auth/auth_test.dart

# Code generation (required after modifying Freezed models or Riverpod generators)
dart run build_runner build -d

# Watch mode for code generation
dart run build_runner watch -d
```

## Architecture

### Directory Structure

```
lib/
  app/           # AppRouter (GoRouter), app-level setup
  core/          # Cross-cutting: config, design system, FP primitives, utils, services
  data/          # Models (Freezed), repositories (interface + _impl), mappers
  features/      # Feature-sliced domain logic
  providers.dart # Central export hub for all Riverpod providers
  main.dart      # Entry point: Supabase init, Firebase init, ProviderScope
```

### Feature Slice Layout

Each feature under `lib/features/<domain>/` follows:
```
domain/
  repositories/  # Abstract interfaces
  usecases/      # Business logic — extend UseCase<T, Params> from domain/usecases/usecase.dart
  models/        # Domain-only models
data/
  datasources/   # Supabase calls (class SupabaseXxxDataSource implements XxxDataSource)
  repositories/  # Concrete implementations of domain interfaces
  mappers/       # Entity ↔ Model conversion
presentation/
  screens/       # UI screens (ConsumerWidget/ConsumerStatefulWidget)
  widgets/       # Feature-specific widgets
  controllers/   # StateNotifier subclasses with typed XxxState
  providers/     # Three-layer stack: infra provider → repo provider → controller provider
```

Simpler features may omit `domain/usecases/` and `data/datasources/`, wiring directly from repository to controller.

### Data Flow

1. **Repository** (`lib/data/repositories/`) wraps Supabase calls, returns `Result<T, Failure>`.
2. **Provider** exposes repository or controller via Riverpod.
3. **Controller** (AsyncNotifier) calls repository, maps results to UI state.
4. **Screen** watches providers with `ref.watch(...)`.

**Never throw exceptions in UI-facing code.** All async operations use `Result.guard`:
```dart
return Result.guard(
  () async => await supabase.from('table').select(),
  (e) => Failure.from(e),
);
```

**Dual error-handling conventions exist in the codebase.** Older features use `Either<Failure, T>` from `fpdart` (`Right(value)` = success, `Left(failure)` = error). New code must use `Result<T, E>` from `lib/core/fp/result.dart`. Don't mix them within a single feature.

### Key Files

| File | Purpose |
|------|---------|
| `lib/app/app_router.dart` | All routes, `_handleRedirect` for auth/onboarding/feature-flag gating |
| `lib/providers.dart` | Central re-export of all providers — add new providers here |
| `lib/core/config/feature_flags.dart` | Feature flag definitions — gate new features here |
| `lib/core/config/environment.dart` | Env config — supports `.env` file and `--dart-define` |
| `lib/core/config/supabase_config.dart` | All table names, bucket names, RPC functions, sport constraints — never hardcode these strings |
| `lib/core/fp/result.dart` | `Result<T,E>`, `Ok`, `Err`, `Unit` — the FP error-handling primitives |
| `lib/core/errors/` | `Failure` type hierarchy |

### Navigation

- Router defined in `lib/app/app_router.dart`.
- Route constants: `RoutePaths` and `RouteNames` from `lib/utils/constants/route_constants.dart`.
- **Always** use transition wrappers from `lib/utils/transitions/page_transitions.dart` (`FadeTransitionPage`, `SlideTransitionPage`, `SharedAxisTransitionPage`, `BottomSheetTransitionPage`). Never use raw `MaterialPage`.
- Redirect logic is centralized in `_handleRedirect` — handles auth state, onboarding completion, and feature flag gating.

### State Management

- Riverpod 2.x throughout. All providers exported from `lib/providers.dart`.
- In widgets: `ref.watch(provider)`.
- In router (no BuildContext): `ProviderScope.containerOf(context, listen: false).read(provider)`.

### Design System

- Standard screen layout: `TwoSectionLayout` (purple top / dark bottom).
- Theme: Material 3 via `AppTheme`. Colors via `Theme.of(context).colorScheme`. **Never hardcode colors.**
- Domain color extensions: `colorScheme.categoryMain`, `colorScheme.categorySocial`, etc.
- Components: `AppButton.primary/secondary/ghost`, `AppCard`, `AppButtonCard`, `AppActionCard`, `CustomInputField`.
- Spacing: 4dp grid system.
- Icons: Lucide (`lucide_icons`) and Iconsax (`iconsax_flutter`).
- Theme categories (`main`, `social`, `sports`, `activity`, `profile`) are preloaded in `main.dart` via `AppTheme.initialize()`. Switch active palette with `AppTheme.setActiveCategory(category)` — screens do this in their `initState` or on navigation.

### Data Models

- All models are Freezed classes with `@JsonSerializable`. Run `dart run build_runner build -d` after changes.
- Pattern: define model → implement repository returning `Result<T, Failure>` → expose via provider → consume in controller/UI.

### Environment Setup

Copy `.env.example` to `.env` and fill `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `APP_NAME`. For web/production, use `--dart-define` flags instead (`.env` files are blocked by CDN/WAF):
```bash
flutter run --dart-define=SUPABASE_URL=https://xxx.supabase.co --dart-define=SUPABASE_ANON_KEY=xxx
```

### Supabase

- Access via `Supabase.instance.client`.
- Trust RLS for authorization — keep queries minimal, no client-side auth checks.
- All table/bucket/RPC names are constants in `lib/core/config/supabase_config.dart`.
- Edge functions live in `supabase/functions/<name>/index.ts` (TypeScript/Deno). Call via `supabase.functions.invoke('function-name', body: {...})`.

### Testing

`mockito ^5.4.4` is in dev dependencies. Generate mocks:
```dart
@GenerateNiceMocks([MockSpec<MyRepository>()])
void main() { ... }
```
Then run `dart run build_runner build -d`.

**Use `@GenerateNiceMocks`, not `@GenerateMocks`** — it returns a default instead of throwing on an
unstubbed call, which is what you want while a test is being written. **And for anything returning a
`Future`, stub with `thenAnswer((_) async => value)` and never `thenReturn`.** Every repository here
returns `Future<Result<T, Failure>>` — 438 such signatures under `lib/data/repositories/` — so
`thenReturn` throws an `ArgumentError` on the first one you write. *(Corrected 2026-09-06: this
section said `@GenerateMocks` and gave no async rule. `senior-frontend-3` found the contradiction
against the `dart-generate-test-mocks` skill during the skills audit; both figures measured.)*

**Tests exist.** `flutter test` is green on **106 tests across 10 files**, and `ci.yml:39` runs it as
a gate. *(This said "No tests exist yet" until 2026-09-06 — it was written before any were, and
`KAN-121` added the tenth file.)*

## Do / Avoid

- **Do** use `Result<T, Failure>` for all data operations — never throw across layer boundaries.
- **Do** export new providers from `lib/providers.dart`.
- **Do** gate new routes/features with `FeatureFlags.<name>`.
- **Do** use `TwoSectionLayout` for standard screens.
- **Avoid** hardcoded colors — use `ColorScheme` or `AppTheme` extensions.
- **Avoid** raw `MaterialPage` — use transition wrappers.
- **Avoid** throwing exceptions from repositories.

## Deployment & Release Topology

Repo: `dabblersport/webapp`. Hosting: Cloudflare Pages, project `webapp`. Build command `bash scripts/cloudflare-build.sh`, output `build/web`.

- **Named subagents only resolve when the session's working directory is this repo.** `.claude/agents/` is registry-scoped to the working directory, and the Agent tool silently falls back to a generic agent for an unrecognised `subagent_type` — no error is raised. A session opened against a different project will appear to use `devops` and will not be using it. To verify, ask the subagent to state the git author email it must commit as; that value exists only in its own definition, while the build command and the never-push-main rule are also in this file and therefore prove nothing.

### Branches

- **`main`** is the Cloudflare Pages production branch and deploys straight to https://app.dabbler.pro. Pushing to main ships to real users immediately. **Never push directly to main** — always open a PR from `Canary`.
- **`Canary`** (capital C) is the default working branch and deploys to https://canary.dabbler.pro.
- Flow: commit → push to `Canary` → wait for the Cloudflare build → verify on canary.dabbler.pro → only then open a PR into `main`. A successful push is not a successful deploy — verify the deployment itself.

**STANDING FREEZE, PO ruling 2026-09-01 — do not merge any PR into `main`, ever, without the
PO's direct, explicit go-ahead in the moment.** *"Don't merge in main ever"* / *"Canary is
not just a branch, is a release, so everything will be on Canary."* Read literally and
acted on literally: `Canary` is being treated as the operative release target, not a
staging step on the way to `main`. Work still ships via commit → push `Canary` → verify
the Cloudflare deploy on canary.dabbler.pro — that part is unchanged. What changes: a PR
into `main` may still be *opened* (per the existing never-push-main rule, a PR is the only
legal path there), but it does not get merged as a matter of routine once Canary looks
good — it sits open and waits. This overrides the "only then open a PR into `main`" phrase
above insofar as that phrase implied the PR was the next automatic step toward shipping;
opening it is fine, merging it is not, until the PO says so for that specific PR. See
`Dabbler/dabbler-docs/DECISIONS.md` P-030 for the full record and the reasoning captured at the time.

### Build Variables

Cloudflare Pages keeps **two separate variable environments, Production and Preview**. They do not share values. Any new build variable must be added to **BOTH** — a variable set only in Production will hard-fail every `Canary` preview build. Preview sat empty for months and silently broke every Canary deploy.

Required by the build script: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `APP_NAME`, `ENVIRONMENT` (plus `GOOGLE_WEB_CLIENT_ID`).

### Deploy Targets and CI Gates

**`main` has exactly one deploy target: Cloudflare Pages.** It had two until 2026-09-01, when `.github/workflows/deploy-web.yml` (a `gh-pages` publish) was deleted under `DECISIONS.md` T-042 — the branch and the Pages site were both already gone and it had been failing on every push to `main` for six weeks. If you find a second deploy path, that is a defect; there is one.

The two GitHub Actions workflows that remain are **gates, not deploy targets**. Both run on push to `Canary` and on PR into `main`:

| Workflow | What it gates |
|---|---|
| `ci.yml` | `flutter analyze` + `flutter test` (KAN-72) |
| `anon-allowlist-check.yml` | anon-reachable view allowlist (KAN-61, `DECISIONS.md` T-002) |

Neither one deploys anything. Cloudflare builds from its own trigger, independently of Actions — **a red Actions check does not stop a Cloudflare deploy**, so a green Cloudflare build is not evidence that the gates passed.

**`ci.yml` passes as of 2026-09-04** (`dabbler-code` `c46b5c5`). Verified by running both steps directly: `flutter analyze --no-pub --no-fatal-infos` exits 0 on **0 errors, 0 warnings, 56 infos**, and `flutter test` exits 0 on **103 tests across 9 files**. It had failed 12/12 runs through 2026-08-30 on 55 warnings and 160 infos; KAN-112 resolved all of them.

**Green here is not green by construction.** The workflow pins `channel: stable` unpinned, so a future SDK bump can make a new lint fatal with no code change — the same mechanism that killed `deploy-web.yml`. Treat a red X as a real signal to investigate, not as the known-broken state it used to be.

### Supabase Project

The Supabase project is `wtncuzcskpigqpmnxwws` (org: Onebrain). Another unrelated Supabase project exists on the same account — **never use it**.

## Onebrain Agent Team

### Agent Roles
- **Tech Lead**: Reads this file, breaks features into tasks, coordinates all agents
- **Flutter UI Agent**: Handles Task A — screens, widgets, animations, design system
- **Backend/Supabase Agent**: Handles Task B — DB tables, RLS policies, edge functions, auth
- **Integration Agent**: Handles Task C — wiring Flutter to Supabase, offline logic, app-level gaps
- **QA/Reviewer Agent**: Reviews all diffs, writes tests, flags security and performance issues
- **DevOps Agent**: Handles deployments, CI/CD config, release notes

### Task Classification
- **Task A (UI)**: Screens, layouts, widgets, animations, design system implementation
- **Task B (Logic)**: Database schema, business rules, Supabase functions, RLS policies
- **Task C (Integration)**: Connecting UI to backend, offline handling, end-to-end flows

### Rules
- Always read CLAUDE.md before starting any task
- Never hardcode API keys or secrets
- Every Task B must have RLS policies defined
- Every Task A must follow the existing design system in lib/core/theme
- Task C only starts after Task A and Task B are complete
