# ROUND-34 — stdlib regen investigation, stale-claims re-run, guard

**Base:** `origin/main` at `dfd0da5d` (v329; round written against v328). Compiler v246.
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.

## WS1 — regenerate `docs/sutram-stdlib.html`: the generator is innocent

**I ran the generator. I did NOT commit its output — and here is why.**

The generator (`tools/gen_stdlib_ref.py`) contains **zero** old-vocabulary strings. It is clean. The old names in its output come verbatim from `lib/` sources, which still carry pre-rename vocabulary:

| Location | Old | Should be |
|---|---|---|
| `lib/chandas.smlib:82` | `meru_pankti` (function name) | `meru_mala` |
| `lib/sadhan.smlib` header | `ayojan util` | `yoj sadhan` |
| `lib/aadhar`, `chandas`, `ganita`, `gudh`, `nighantu`, `phal`, `roop`, `sankhyiki`, `shreni`, `suchi` comments | `pankti` (as array) | `mala` |

The committed HTML was hand-fixed to new names, but `lib/` was never updated — so a faithful regeneration reintroduces the old names (`meru_mala`→`meru_pankti`, `mala`→`pankti` in descriptions). Committing that would make the docs worse.

**The real defect is stale pre-rename vocabulary in `lib/` sources, not the generator.** The `meru_pankti` case is a real function name with a test (`tests/stdlib/chandas_meru_pankti.sm`), so renaming it is a breaking API change — not done here; it needs your call. The comment-only instances (`pankti`→`mala`, `ayojan`→`yoj`) are safe to fix whenever you want them fixed.

The `brihat` 12→13 and `samanvaya` 10→11 count corrections are real but remain unapplied in the committed HTML, pending the lib-vocabulary decision above.

## WS2 — stale-claims re-run

**157 hits on v329** (was 163 on v325) — **down by 6, not 13.**

Why not 13: you applied 9 of the 13 FALSE fixes; of the held-back items, the `docs/sutram-design-parameters.html:365` FFI line ("Today: there is no FFI") **still stands and is still FALSE** (2 hits, 1 unique claim). The `docs/sutram-stdlib.html` section was held back for the rename-regression reason above. The remaining delta is from other v325→v329 commits.

**FALSE remaining: 1 unique claim** — `docs/sutram-design-parameters.html:365`, "Today: there is no FFI." Everything else in the current 157 is TRUE (real limits, policies, design proposals) or HISTORICAL (CHANGELOG versioned entries, dated snapshots).

## WS3 — the guard

**This round's number, Linux, on v329: 551 programs, 470 byte-identical executables, 81 refused identically, 0 DIFFER.** (The round's "476" is the Windows session's count; Linux holds at 470. Fresh build byte-identical to committed binary.)

## Delivery

- This report: `Muse-to-Sarvam/2026-10-23-round34-regen-guard.md`
- No files modified (the regenerated HTML was deliberately not committed — see WS1).
- `git push` has no credentials here; delivery via the GitHub API as usual.
