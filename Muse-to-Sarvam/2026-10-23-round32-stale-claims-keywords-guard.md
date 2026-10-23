# ROUND-32 — stale-claims check, keyword count, guard

**Base:** `origin/main` at `fd486195` (v322; the round was written against v321, main moved one commit). Compiler v246.
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12. No X11, no Windows.
**Language priority:** Sanskrit only. No pack touched.

## WS1 — built `tools/doc_stale_claims.py`

The check for absence-claims going stale, in the shape of `check_layers.py` / `doc_counts_gate.py`. It scans every `.md` and `.html` outside the collaboration folders (`*-to-*`) and `backups/` for eight absence-shaped patterns (`there is no`, `no <capability>`, `not [yet] implemented/supported/available`, `never been/run/executed`, `does not [yet] exist/work`, and three more), and reports each hit with file, line, pattern name and the sentence — for a human to confirm or clear. Its output states plainly that **it is a floor, not a proof**: it finds sentences shaped like absence claims and cannot decide whether a claim is still true.

**Run on main: 115 documents, 161 hits.** I did not fix any; the significant ones, verified:

1. **`PROJECT-OVERVIEW.md:159` — contradictory paragraph, partially fixed.** The v318 changelog says the stale claims were fixed, but the paragraph now reads "**Not implemented.** Separate compilation with object files now exists (our own linker, `SUTRAMO1`/`SUTRAMO2`), as do first-class functions and methods. Still absent: ... No concurrency. **No first-class functions.**" — it asserts first-class functions both exist and don't exist in the same paragraph. The fix landed on the head of the paragraph and missed the tail.
2. **`PROJECT-OVERVIEW.md:155`** — "The **Windows installer has never been executed on Windows**." Stale: the installer passed 16 required checks on real Windows 11 (R31 brief).
3. **`docs/sutram-scorecard.html:198`** — "No first-class functions, namespaced modules, or pattern matching." First-class functions exist (R23, gate PASS); the other two are still true.
4. **`sutram-completion-roadmap.html:343` / `docs/sutram-project-status.html:186`** — "no FFI". Stale: the C FFI shipped in R32–R34 (gates PASS).
5. **`compiler/MODULE_SYSTEM_R40_DESIGN.md:73`** — "Real separate compilation, native objects (not implemented)". Stale: R28/R29 built it.

The remaining ~150 hits are a mix of still-true limits (no concurrency, no GC, no package manager), historical snapshots in old HTML reports, and design docs describing unbuilt proposals. The full list is one command away: `python3 tools/doc_stale_claims.py`.

The tool is delivered as `tools/doc_stale_claims.py` on main (new file, no existing file modified).

## WS2 — the keyword count, three ways

| Number | Source | What it actually counts |
|---|---|---|
| **32** | `docs/sutram-scorecard.html:48` | The `KW_*` token-type constants in `src/sutram_compiler.asm` (`KW_MUKHYA`…`KW_PRASAR`) — the parser's keyword vocabulary, counted by me from the source. |
| **28** | `docs/sutram-scorecard.html:237` | Unknown. It appears nowhere else in the tree; both numbers were introduced in the same commit, so it is not an older count. Most likely a miscount. |
| **52** | `lang/sanskrit.lang` | Distinct words the Sanskrit pack maps to Devanagari — but this is **not** a keyword count. It is 32 keywords **plus** builtins (`likha`, `paadh`, `band`, `dvaram`, `nirmmita`…), the `kosh_*` methods, and other reserved names (`yoj`, `tak`, `chakra`, `mala`…). |

I did not pick one — the definition is the owner's call (now with ChatGPT as ROUND-107). The three quantities are named precisely above so he can.

## WS3 — the guard

**This round's number, Linux, on v322: 551 programs, 470 byte-identical executables, 81 refused identically, 0 DIFFER.**

Method as R31: committed `./sutram_compiler` vs fresh build from `src/r68_compiler_entry.asm` (binaries byte-identical); every `.sm` in `examples/`, `examples/*/`, `tests/stdlib/`, `tests/r*/`; executable bytes + compiler output + exit status compared. (The round's "476" is the Windows session's count; Linux holds at 470.) Wine/real Windows: NOT-RUN.

## Delivery

- New tool `tools/doc_stale_claims.py` uploaded directly (round-authorized build).
- This report: `Muse-to-Sarvam/2026-10-23-round32-stale-claims-keywords-guard.md`.
- No existing file modified; tree clean. `git push` has no credentials here, so delivery is via the GitHub API as usual.
