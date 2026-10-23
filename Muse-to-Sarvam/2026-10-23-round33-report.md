# ROUND-33 — triage the 161 stale-claim hits, guard

**Base:** `origin/main` at `1d16e647` (v325; round written against v324). Compiler v246.
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.

## WS1 — triage and fixes

`tools/doc_stale_claims.py` on v325: **163 hits** across 115 documents (161 on v322; +2 from new commits).

**Triage** (full table: `Muse-to-Sarvam/2026-10-23-round33-triage.md`):

| Bucket | Count | Disposition |
|---|---|---|
| **FALSE** — claim of absence for something that exists | 16 hits / 13 unique claims | **Fixed** (patch below) |
| **TRUE** — real limit, policy, or design proposal | 88 | Left alone |
| **HISTORICAL** — versioned history or dated snapshot | 57 | Left alone (CHANGELOG entries are versioned; old HTML reports carry "State as of" stamps) |
| **AMBIGUOUS** — needs the owner | 0 | — |

**FALSE fixes applied** (in `2026-10-23-round33-triage-fixes.patch`, 7 files):

| File | Was (false) | Now |
|---|---|---|
| `PROJECT-MASTER.md:107` | "Windows never executed" | "Windows executed — 16 required checks passed on real Windows 11 (standard user, not elevated)" |
| `PROJECT-MASTER.md:364` | "Windows execution and the freestanding boot — never performed by anyone" | Windows execution done; freestanding boot still never performed |
| `docs/LIBRARY-BOUNDARY.md:41` | "there is no FFI yet (not started)" | C FFI exists (R32–R34); library self-contained by design |
| `docs/LIBRARY-BOUNDARY.md:61` | "No first-class functions… no methods… language does not have them yet" | First-class functions and methods exist (R23); generic collections do not |
| `docs/sutram-design-parameters.html:159` | "not first-class — no function values" | First-class (R23); no closures/iterators/pattern matching |
| `docs/sutram-design-parameters.html:179` | "no methods" | Methods exist (R23); no traits/polymorphism |
| `docs/sutram-design-parameters.html:191` | "no slices" | Slices exist (R23, `vibhag`); no alignment/SIMD/vectors |
| `docs/sutram-design-parameters.html:316` | Windows sources "never been executed" | Executed — 16 checks on real Windows 11 |
| `docs/sutram-design-parameters.html:329` | "no separate compilation" | Separate compilation exists (R28/R29); no package manager/lockfile |
| `docs/sutram-design-parameters.html:365` | "no FFI" | C FFI exists (R32–R34) |
| `docs/sutram-project-status.html:147` | Windows compiler "Never executed by this project" | Executed — 16 checks passed |
| `docs/sutram-scorecard.html:150` | "no C FFI" | C FFI exists (R32–R34) |
| `lib/kalana.smlib:8` | "Sutram has no first-class functions" | Has first-class functions (R23); API predates them |

`docs/sutram-stdlib.html` regenerated via `tools/gen_stdlib_ref.py` (picks up the kalana fix plus the R31-noted brihat 12→13 / samanvaya 10→11 count corrections).

**Verification:** patch applies cleanly to pristine `origin/main`; after applying, the scanner reports 150 hits (13 fewer — the false claims are gone). `proof_lib` 224/224 and `proof_props` 86/86 still pass (kalana change is comment-only).

**HISTORICAL dating:** the 57 historical hits need no changes — CHANGELOG entries sit under version headings, and the old HTML snapshots carry "State as of 15 October 2026, CHANGELOG v146" stamps.

## WS2 — the guard

**This round's number, Linux, on v325: 551 programs, 470 byte-identical executables, 81 refused identically, 0 DIFFER.** (The round's "476" is the Windows session's count; Linux holds at 470. Fresh build byte-identical to committed binary.)

## Delivery

- `Muse-to-Sarvam/2026-10-23-round33-triage.md` — the full 163-hit triage table
- `Muse-to-Sarvam/2026-10-23-round33-triage-fixes.patch` — the 13 FALSE fixes (7 files)
- This report
- `git push` has no credentials here; delivery via the GitHub API as usual.
