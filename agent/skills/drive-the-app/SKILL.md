---
name: drive-the-app
description: Get a running Dabbler app in front of you and drive it, on the surface that actually works today. Use when a ticket must be tested end to end, when a "done" claim needs checking against real running behaviour, when a bug must be reproduced, or when you need a screenshot of the real app rather than a widget test. Covers choosing a surface (Android emulator, Chrome/CanvasKit, iOS, web integration_test), starting it, driving it by screenshot and coordinate, and the five traps that make a run lie to you.
---

# Drive the App

The only seat that opens the running Dabbler app is `qa`. This is how, in steps, on the
surfaces measured to work **on this machine**.

Every step below is marked. **[M]** = measured, with the date it was last run.
**[U]** = untested here; inherited or documented but not executed. Do not present a `[U]`
step's outcome as fact — run it and upgrade it, or say it is untested in your report.

Repo root throughout: `/Users/moatazmustapha/Desktop/Thebes/Dabbler/dabbler-code`.
**Use absolute paths.** A relative `agent/status/` resolves against the project tree and
silently creates a second, unread log.

---

## Step 0 — Pick the surface before you start anything

Do not default to web. **[M] 2026-09-06** — surface availability was measured today and
is not what the older prose assumed:

| Surface | State today | Use it for |
|---|---|---|
| **Android emulator** (`Dabbler_test`) | **[M]** works — `integration_test` runs green in 12s | automated harness runs; ADB screenshot/tap driving |
| **Chrome, `flutter run`** | **[U]** documented, not run today | manual screenshot-and-coordinate driving |
| **iOS simulator** | **[M]** **BLOCKED** — see Trap 4 | nothing, until the path bug is fixed |
| **macOS desktop** | **[M]** not configured — `No macOS desktop project configured` | nothing |
| **Web + `integration_test`** | **[M]** **BLOCKED** two ways — see Trap 3 | nothing |

Rule of thumb: **an automated harness run goes to Android. Manual driving goes to
Chrome.** Neither goes to iOS today.

---

## Step 1 — See what is actually connected

```bash
cd "/Users/moatazmustapha/Desktop/Thebes/Dabbler/dabbler-code"
flutter devices
```

**[M] 2026-09-06.** With nothing booted this returns only `macOS` and `Chrome`. An
emulator or simulator appears here **only after you boot it** — its absence is not a
finding.

Boot the Android emulator **[M] 2026-09-06**:

```bash
flutter emulators --launch Dabbler_test
sleep 45
~/Library/Android/sdk/platform-tools/adb devices     # expect: emulator-5554  device
```

`flutter emulators` **[M]** lists exactly two: `Dabbler_test` (android) and
`apple_ios_simulator` (ios).

---

## Step 2a — Run the automated harness (Android)

`integration_test/app_test.dart` boots the **real** app through the production bootstrap
(`Environment.load` → Firebase → ThemeService → AppTheme → Supabase → `runApp`) and
asserts a `MaterialApp` mounted. It is a launch smoke test, not a feature test.

**[M] 2026-09-06 — this is the command that works:**

```bash
cd "/Users/moatazmustapha/Desktop/Thebes/Dabbler/dabbler-code"
flutter test integration_test/app_test.dart -d emulator-5554 --dart-define-from-file=.env
```

Measured result: **exit 0, `00:12 +1: All tests passed!`**. It leaves the git tree clean —
`git status --porcelain` was empty afterwards.

**Do not use `scripts/run_integration_tests.sh`.** **[M] 2026-09-06** — it auto-detects a
booted *iOS* simulator and routes there, straight into the Trap 4 failure. It is an
iOS-only script and its header says so. Call `flutter test` directly with `-d`.

**[M] This run hits LIVE Supabase and authenticates as a real user.** The measured run
logged `FCM token saved for user ec959ff7-46ef-4bf2-aab4-3515b81f5846` and loaded 20 real
notifications from the emulator's persisted session. It is not hermetic. Treat every run
as touching production data, and never point it at anything you would not want written to.

---

## Step 2b — Drive the app by hand (Chrome)

**[U] — documented in `agent/roles/qa.md`, not executed in this pass.**

```bash
flutter run -d chrome --dart-define-from-file=.env
```

**The `--dart-define-from-file=.env` flag is not optional** — without it the app hangs on
the launch screen. Test the local `localhost:<port>` build, never `canary.dabbler.pro`
(that is `devops`' release-verification surface) and **never** `app.dabbler.pro` (real
user data).

Then drive with `mcp__claude-in-chrome__computer` — screenshot, click, type, scroll — and
`resize_window` for the viewport. Cover **both** ~390×844 (phone, the primary form factor)
and desktop width as full passes; desktop web is a supported surface and a desktop-only
bug is a real bug at its real severity.

### Driving Android by ADB instead **[U]**

`computer-use` cannot see the Android emulator on this machine (a Claude Desktop rollout
flag, `"androidEmulator":{"status":"unsupported"}`). Use ADB over plain Bash:

```bash
ADB=~/Library/Android/sdk/platform-tools/adb

$ADB -s emulator-5554 shell screencap -p /sdcard/qa_shot.png
$ADB -s emulator-5554 pull /sdcard/qa_shot.png <local-path>.png    # then Read the file
$ADB -s emulator-5554 shell input tap <x> <y>
$ADB -s emulator-5554 shell input text "some%stext"                # %s = space
$ADB -s emulator-5554 shell input swipe 500 1500 500 500 300
$ADB -s emulator-5554 shell input keyevent KEYCODE_BACK
$ADB -s emulator-5554 logcat -v time | grep -i flutter
```

Tap coordinates are in the **device's native pixels**, not the screenshot's displayed
size. If a screenshot came back scaled, convert first:
`real_x = displayed_x * (device_width / displayed_width)`.

---

## The five traps

### Trap 1 — CanvasKit gives you no DOM **[U, inherited; measured 2026-08-29]**

Dabbler's web build is CanvasKit. The page is a canvas: no readable DOM, no accessibility
tree, no trustworthy `aria-label`s. `read_page {filter:"interactive"}` returns one generic
node, `document.body.innerText` is empty, `flt-semantics-host` has zero children.

**You work by screenshot and coordinate. Never "find" an element by DOM query, text
content, or accessibility role.** A call that tries returns nothing — and reporting that
nothing as a missing button is a false bug. This is also why the `browser` skill's
`@e1`/`@e2` element-ref model does not apply to you.

### Trap 2 — `read_network_requests` only captures from the moment you arm it **[U, inherited]**

Arm it (call once) → act → read. Calling it after the fact and seeing nothing means you
forgot to arm it, **not** that no request happened. This is your substitute for database
access: verify persistence by reloading and re-checking, never by querying Postgres.

### Trap 3 — the web integration_test path does not exist here **[M] 2026-09-06**

Two independent blockers, both measured today:

- `flutter test integration_test/app_test.dart -d chrome` exits with
  **`Web devices are not supported for integration tests yet.`** `flutter test` cannot
  drive web at all.
- The documented alternative, `flutter drive` + ChromeDriver, has **neither half present**:
  `chromedriver` is not on `PATH` and not under `/opt/homebrew`, `/usr/local` or
  `~/Downloads`; and `test_driver/` does not exist in the repo — `flutter drive` for web
  requires a `test_driver/integration_test.dart` entry point that has never been written.

So the gap on web is **setup that was never done**, not a tool that is forbidden. See the
`#356` note in `agent/roles/qa.md`.

### Trap 4 — iOS is blocked by a space in the repo path **[M] 2026-09-06**

`flutter test integration_test/app_test.dart -d <ios-udid>` fails before any Dart runs:

```
Xcode failed to resolve Swift Package Manager dependencies:
xcodebuild: error: Could not resolve package dependencies:
  main/Package.swift:79: Fatal error: Failed to load configuration:
  fileNotFound("Error loading or parsing pubspec.yaml: ... NSFilePath=/Users/moatazmustapha/
  Desktop/One%20Brain/.../pubspec.yaml, NSURL=file:///Users/moatazmustapha/Desktop/
  One%2520Brain/.../pubspec.yaml ...")
```

**The file is not missing.** `ios/Flutter/ephemeral/pubspec.yaml` exists on disk at 1172
bytes — verified. Note `One%20Brain` in `NSFilePath` against `One%2520Brain` in `NSURL`:
the space in `One Brain` is **percent-encoded twice**, so Xcode's SwiftPM resolver looks
for a directory literally named `One%20Brain`. Every iOS build from this checkout hits it.

**Do not file this as a Dabbler app bug.** It is an environment/toolchain defect in the
repo's location. If iOS coverage is needed, that is an escalation to `po`.

### Trap 5 — an HTTP 200 on `*.dabbler.pro` is not evidence a file exists **[U, inherited; measured 2026-08-29]**

Cloudflare Pages' SPA fallback serves the same `index.html` for *any* unmatched path — a
real 200, real `text/html`, identical bytes. Before escalating "sensitive path X is
exposed", **run the discriminator**: fetch the suspect path, a known-nonexistent path, and
a known-real asset (`/flutter_bootstrap.js`). If the suspect matches the nonexistent one
in size, content-type and hash, nothing is served there.

---

## Step 3 — Report honestly

- **Untested is never reported as passing.** A feature you could not log into is
  *blocked*, never *clean*.
- **Never report an absence without confirming the check could have found the thing.**
  Before filing "there is no error state", confirm you triggered the error condition.
  Before filing "the button is missing", confirm you screenshotted the right scroll
  position and viewport.
- Say which surface you ran on. "It works" means nothing without "on Android emulator,
  `integration_test`, exit 0".
- Leave the tree clean. Run `git status --porcelain` before you report and paste it. If a
  run left artefacts, say where they are — do not `git clean` them.
- You never fix what you find; findings become tickets for the owning specialist.

## Read, don't run

`.maestro/dabbler_tests/` holds 12 YAML flows (account creation, login, OTP
rate-limit/invalid/expired, password reset, session expiry, find-nearby-venue). Read them
as a source of intended-behaviour cases. You do not run Maestro.
