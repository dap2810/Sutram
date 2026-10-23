# Sutram ROUND-106 — ChatGPT → Sarvam

**Date:** 23 October 2026. **Current project task:** `Sarvam-to-ChatGPT/ROUND-106.md` (issued on v316), applied to **pinned initial live main `e6914bc598958053817f7c61133d579f1ba19bc2`**, changelog **v318**. **Sanskrit is the ONLY language under active development until v1.0**, under `LANGUAGE-PRIORITY.md`; all other ten language packs remain intact but frozen. `docs/PATH-TO-COMPLETION.md` is the canonical order, currently a dated v315 snapshot. **This is a READ-SIDE delivery only. No source, tests, tools, Windows channel, backups or installers edited.**

## WS1 — Actionable prose corrections, CURRENT TREE, not the old v310 list

[**Round106 WS1: exact file/line/verbatim claim/tree fact/smallest edit**](ROUND-106-WS1-ACTIONABLE-PROSE-CORRECTIONS.md). Sarvam wanted a precise edit list rather than our longer R105 survey, so the report is a **P0/P1 table of replacements**, preserving the dated source wording and honest acceptance distinctions.

**Already fixed since R105 — do not repeat**: README “no separate compilation/no first-class/Windows GUI never” rows; Windows-real-test and object-compilation absence in `docs/sutram-roadmap.html`; `docs/sutram-scorecard.html` now admits functions/methods/slices in its line 206. `PROJECT-OVERVIEW.md` was **only partly fixed**: its `159–160` paragraph begins by admitting separate compilation, functions and methods, then still says **“No first-class functions. No collections beyond kosh and mala.”** Fix that as **one paragraph**, not two contradictory edits. Its lines 153–155 still falsely say no Windows GUI/installer was ever executed.

**Highest-priority remaining false claims**:
1. `docs/sutram-project-status.html` says **“Windows ... Unverified”**, **“installer itself untested on Windows”**, **“No C FFI”**, and labels 2026-vintage pending items as “open”; owner’s real 16-check Windows acceptance and Linux-main FFI refute those absolutes. Update with pinned test branch/commit rather than claiming v318 Windows release.
2. `docs/sutram-design-parameters.html` “Today” cells still deny **first-class functions, methods, slices, layered library enforcement, Windows execution, opt-in separate compilation and Linux FFI**, and incorrectly say fuzzing/cross-platform execution have not occurred. The *charter's design goals*, including memory safety by default, are clearly aspirational; do not erase them.
3. `PROJECT-MASTER.md` falsely says Windows never ran, no C FFI, no first-class functions/methods/slices, and uses obsolete 20-charter numbering. Its old three-language plan is now **superseded by Sanskrit-only**. It calls `ROADMAP-TO-V1.0.md` the canonical path despite the owner's newer `docs/PATH-TO-COMPLETION.md`. The `:360–362` assertion Windows was never executed contradicts its own `:306–311` Windows evidence.
4. **Check-the-math:** Master `:270–273` calls RAM and no-runtime **Sutram WINS** and claims “four of five wins”. But the same table shows **Zig 16,008 KB < Sutram 16,128 KB** and **both need no runtime**. Against Zig, the listed five-aspect comparison yields **two clear wins (startup, binary size), two losses (speed, RSS), one tie (runtime)**. Preserve the dated measured values, fix the labels and summary, and do not extrapolate universal performance.
5. The `docs/sutram-scorecard.html` still denies C FFI, claims 21 rather than 24 library modules and a 136-test suite, and says no formatter/undo. `tools/sutram_fmt.py` exists and source includes CLI format/check/verify switches; `lib/phal.smlib` has a *library Result abstraction*, not a compiler-enforced result type. Mark percentages **subjective**; don't invent updates.
6. `docs/PATH-TO-COMPLETION.md` is explicitly **dated v315** and reports 25 computed allocations/6 bounded/19 exempt, while later R39 measured **26/13/13** and library 224/224. That is **out-of-date, not a fraudulent historical number**: only Sarvam should refresh the canonical as-of claim after its current fresh-clone run.
7. Archive or clearly date old chapter/windows/no-execution claims and speculative benchmark comparison rows; `docs/sutram-stdlib-reference.html` should replace **“Safe anywhere, including a freestanding program”** with the truthful **“Core has no direct OS/heap dependency; no freestanding or ownership safety proved.”** Keep non-Sanskrit books/packs **untouched** by this round.

## WS2 — Verdict on the old 19 exempt allocation sites

[**WS2: old 19 vs current 13, exact source-derived formulas**](ROUND-106-WS2-EXEMPTIONS-VERDICT.md).

**Answer: YES, the previous exemption rationale failed scrutiny — and YES, it has since been fixed.**

- **12 of the historical 19** were set/map scratch allocations trusting an independent **caller-supplied `cap/bcap/scap`** without relating it to the allocated object. This was a real unsafe assumption; Claude R39 **native-reproduced** a buffer overwrite/garbage result and changed scratch formulas to use `a[0]`, `b[0]`, `s[0]`, `src[0]` as appropriate.
- **Six** former `aadhar/brihat/shreni` exemptions relied on assumed caller-owned raw buffer length. Current library adds arithmetic bounds and current gate no longer exempts them; raw pointer extent is still a caller contract, not a memory-safety guarantee.
- **One** historical exemption, `nighantu_vardh: oldcap=m[0]`, was mathematically valid **for a genuine constructor-created map**, and remains valid conditionally.
- **Current main:** `tools/check_alloc_bounds.py` has **12 exact-expression keys covering 13 sites**, all derived from map/set *container-owned* capacity fields. `nighantu_srij` checks `c <= floor((INT64_MAX-16)/56)`; therefore for a valid, unmodified map `33*c+1`, `32*c+1`, and `8*c` fit signed 64-bit. **Current exemptions SOUND UNDER THOSE EXPLICIT PRECONDITIONS; no general raw-pointer ownership/validity proof.**
- **Reported R39 Linux run:** 26 computed allocations, 13 bounded, 13 exempt, 0 failed; distinct from the old R37/R38 25/6/19. **NOT RUN - no toolchain** in this ChatGPT round.

## WS3 — What to UPDATE, mark historical, merge in specifications

[**WS3: per-file version-aware maintenance actions**](ROUND-106-WS3-SPEC-MAINTENANCE-ACTIONS.md). Minimal consolidation, no new code:

- **Historical, don't rewrite:** R97 `--ffi-sidecar` proposal (shipped as `--ffi`); R97/R98 zero-reloc ELF first milestone (R33 now supports bounded internal PC32); old R100 Windows “FFI not implemented” time-bound status (owner tested v245 Windows FFI branch).
- **Corrected version decision:** R100 pointer contract incorrectly proposed safe kinds under v2; R101 reserves a **future v3**. R102 `sutram-ffi-v3|windows-x86_64-msabi` / literal-only `cstr_ro` remains **PROPOSED/NOT_IMPLEMENTED**. Do not alter accepted v1/v2; sidecar version is independent from SUTRAMO1/SUTRAMO2 object-format markers.
- **Keep/merge current docs, not source:** R100 Microsoft x64 ABI is a valid reference; link its later tested branch status. Index R97 future 7-workload benchmark target together with R98 preflight gate as **DEFERRED/NOT RUN**, *after Sanskrit v1.0*. Fold R104 “validity before address formation” examples into `docs/OVERFLOW-SAFETY.md` and link R39's actual 13 guarded/exempt boundaries; no claim that a regex gate proves raw pointer safety.
- **Recommendation:** a short source-pinned `docs/SPEC-STATUS.md` index with categories **implemented on main / branch-tested / historical first stage / proposed / future performance**; maintain original round files as dated evidence.

## Raw source evidence / PASS–FAIL–NOT RUN

[**RAW SOURCE-READ OUTPUT**](ROUND-106-RAW-SOURCE-CHECKS.txt): 12 live files read from pinned GitHub commit, **16 PASS / 0 FAIL** source-presence/claim predicates. This is not machine-code test output. [**SHA/claim ledger**](ROUND-106-OBSERVED.json) lists source blobs for 21 supporting files and current owner language/roadmap priority.

| Check | Result |
|---|---|
| Read owner Sanskrit-only priority and canonical completion path | **PASS — source read** |
| WS1 verify current stale prose vs already-fixed claims; propose minimal edits | **PASS — read-only audit** |
| WS2 reconcile original 19 vs current exact 13 exemptions | **PASS — source math and source audit** |
| WS3 file-by-file historic/current/proposed spec decisions | **PASS — source audit** |
| Raw pinned GitHub source assertions | **16 PASS / 0 FAIL (not native tests)** |
| Run Sutram compiler, tests, gates, fuzz, crash corpus and proof suite | **NOT RUN - no toolchain** |
| Real Windows FFI, GUI, installer or terminal acceptance | **NOT RUN - no toolchain** |
| Run benchmark or implement proposed v3 `cstr_ro` | **NOT RUN - no toolchain; v3 NOT IMPLEMENTED** |
| Changes to `src/`, `lib/`, `tests/`, `tools/`, `Windows-to-Sarvam/`, `backups/`, frozen language packs | **NONE** |

**For Sarvam:** please apply only **current P0/P1 prose corrections**, not already-fixed historical ones; refresh canonical measured counts only from an exact fresh-clone run. Preserve raw acceptance evidence and the Sanskrit-only scope. The Windows branch merge/real acceptance remain the Windows channel and owner’s work. This handoff ends **Round 106**; await next manual `CHECK FOLDER`.
