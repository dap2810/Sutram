# Sutram — ROUND-120: clean the repository. 52 MB, and 37 MB of it is not the language.

**Base:** main at v297 · **Deliver into:** `Claude-to-Sarvam/`

## The audit, measured by me

**Repository: 52 MB, 6,158 files.**

| Directory | Size |
|---|---|
| `Claude-to-Sarvam/` | **15 MB** |
| `Windows-to-Sarvam/` | **12 MB** |
| `ChatGPT-to-Sarvam/` | **6.0 MB** |
| `Muse-to-Sarvam/` | **4.5 MB** |
| `tests/` | 2.4 MB |
| `docs/` | 2.3 MB |
| `src/` | 1.5 MB |
| everything else | ~8 MB |

**The four collaboration folders are 37.5 MB - 72% of the repository.** **The language itself is about 14 MB.**

## WS1 - the duplicate binaries. These are pure waste.
| File | Size |
|---|---|
| `Sutram-Setup.exe` (root) | **1,495 KB** |
| `Windows-to-Sarvam/win-v297-2026-11-03/Sutram-Setup-v297.exe` | **1,900 KB** |
| `Sarvam-to-ChatGPT/Sutram-Setup.exe` | **564 KB** |
| `sutram.exe` (root) | 502 KB |
| `win/sutram.exe` | 502 KB |
| `sutram_compiler` | 532 KB |

**The `Sarvam-to-ChatGPT/Sutram-Setup.exe` is a v243-era copy in an outbound folder - delete it.** **The Windows one is a test artefact - keep it only if the Windows round still needs it, otherwise delete.**

**That is ~2.5 MB of exact duplicates.**

## WS2 - and the 214 evidence directories in `Claude-to-Sarvam`
**214 `evidence-*` folders, 15 MB total.** **The biggest are `evidence-r15` (937 KB), `evidence-r8` (762 KB), `evidence-r34` (637 KB).**

**These are per-round proof files - JSON, logs, disassembly.** **They are valuable for a week and noise after a month.**

**Proposal: keep the evidence for the last 10 rounds, delete the rest.** **If a round record references a deleted file, say so and keep that one.**

**Do not delete a ROUND record. Only evidence.**

## WS3 - and the rule that matters
**The owner has said twice: do not remove rounds.** **Every `ROUND-*.md` and `R*.md` stays, whatever its age.**

**What goes: duplicate binaries, old evidence directories, and any file that is a copy of another file in the same repository.**

**What stays: every round record, every doc, every test, every example, every source file.**

## WS4 - and the size target
**Report what you achieve.** **If it drops from 52 MB to 20 MB, say so.** **If it only drops to 45 MB, say that too and say why.**

**And: does any of this break a link in the docs?** **Run the link check after.**

## WS5 - and the docs
**Every doc must still describe v297.** **The vocabulary page, the reference, the README.** **22 builtins renamed, `asti`/`nasti`, `Sutram truti`, `sankhya_bindu` withdrawn, 15 library contracts refusing.**

**If any doc still says `Sutram Error` or `kosh_push` as primary, it is stale.**
