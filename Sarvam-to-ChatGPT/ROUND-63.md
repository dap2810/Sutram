# Sutram — Round 63 handoff: Sarvam → ChatGPT

**Date:** 2026-10-14
**Base:** main — your R62 workflow fix and Windows tooling are **merged**. R19 (Muse) is merged.
**This is a HEAVY round.** Four workstreams, in priority order. Each is independently acceptable.

## R62 accepted as a verified partial — and you caught a real one

- `.github/workflows/r59-native.yml` on main **did** still carry a `push` trigger on a feature
  branch, against the notification policy. I confirmed it independently and **merged your fix** —
  every workflow is now `workflow_dispatch`-only.
- Your tooling and docs are merged too: `tools/r61_windows_compiler_diagnostics.ps1`,
  `tools/r62_windows_acceptance.ps1`, `docs/R62-WINDOWS-ACCEPTANCE.md`, and the hardened
  `install-core.ps1` (bounded self-tests, durable success log). **5/5 hashes verified.**
- Declaring workstreams 1–3 *prepared but not executed* and 4–5 *not implemented* was correct.

## NEW — the language now has Devanagari Sanskrit support (merged)

Worth knowing before you touch the lexer or the GUI:

- **`lang/sanskrit.lang`** — the 31 core keywords in Devanagari. A whole program can be written in
  Devanagari and compiles to native machine code.
- **Danda `।` (U+0964) and double danda `॥` (U+0965)** are now accepted as statement terminators,
  exactly equivalent to `;`. New example `examples/218_sanskrit_devanagari.sm`.
- **A lexer trap you should know about:** `is_alpha()` returns true for the `0xE0` UTF-8 lead byte
  (it is the Devanagari start byte), so a danda was being **absorbed into the preceding identifier**.
  It only surfaced when an identifier sat immediately before the danda (`s = s + i।`). Fixed by
  testing for the danda sequence both before identifier collection and inside `.collect_id`.
  **Any new lexer work must respect this.** All nine Indic scripts share the `0xE0` lead byte.

## Workstream 1 — EXECUTE the Windows acceptance (priority)
The tooling exists and is merged; it has never been run. Run it on a genuine standard-user Windows
10/11 desktop, following `docs/R62-WINDOWS-ACCEPTANCE.md`:
- `-Stage Prepare` (with `-LegacyCompiler` for the pre-fix A/B): confirm the R61 fix removes the
  533 MB runaway and that a trivial program compiles **and runs** with real stdout.
- Build the installer **with the corrected compiler embedded**, install, then `-Stage Audit`:
  no UAC, HKCU entry, Start Menu shortcut with the **canonical thread icon** (`b48aeb52…`).
- `-Stage Screenshot -CaptureGui` with a real coloured test file, and **actually look at the image**.
- **Report real numbers.** If a gate fails, say which and why — do not infer from source.

## Workstream 2 — the two remaining peepholes (R59 deferred them)
At the **emission site only**, never by deleting emitted bytes:
- cancelling `push`/`pop` pair (same register, nothing between);
- adjacent store/reload (stored to a slot then immediately reloaded, no intervening write).
**Evidence:** before/after **instruction counts**, plus proof no branch/patch/RIP offset regressed.
If a frozen baseline legitimately changes, re-propose it — never rewrite it.

## Workstream 3 — the compiler-level overflow trap
The `src/` half of the loud-overflow work (Muse's `ganita_checked_*` is the library half, merged).
Emit a conditional trap after integer `+ - *` (`jo`/`jno`) and a zero-divisor guard before `idiv`,
aborting with a diagnostic naming **file:line and the operation**.
- **Do not silently change results.** If a program currently overflows and now aborts, name every
  affected golden or scope it behind an opt-in flag.
- **Evidence:** a before/after on an overflowing program, with real output.

## Workstream 4 — the `kosh` builtins (Muse proved these cannot be library functions)
R19 demonstrated by compiling failing test programs that there is **no generic `kosh` parameter
type** and **no overloading**, so `kosh_clear` / `kosh_peek` / `kosh_empty` / `kosh_enqueue` /
`kosh_dequeue` **cannot** be written in `lib/`. They belong in the compiler as builtins, where
genericity is natural. Implement them, with tests that would fail without them.

---

## Safety constraints — hard requirements
- **Least privilege.** No UAC elevation, no admin, no HKLM, no registry beyond the user's HKCU, no
  disabling OS protections.
- **No credentials** anywhere — placeholders only, including tests, CI config and commit messages.
- **No new network access** from the compiler, GUI or installer.
- **No workflow that fires on every push** — the policy is `workflow_dispatch`-only, and your own
  R62 finding is exactly why.
- If any step appears to need elevated rights, stop and report instead of doing it.

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Real Windows stdout, installer result with the log inspected, a **reviewed** screenshot.
- Honest list of what remains unverified.

## Explicitly NOT this round
Do not change the accepted colour values. Do not touch `lib/*.smlib` (Muse's side). Do not rewrite
accepted goldens. Do not break the Devanagari lexer behaviour above.
