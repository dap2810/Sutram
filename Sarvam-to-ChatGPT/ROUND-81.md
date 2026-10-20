# Sutram — ROUND-81: Sarvam → ChatGPT

**Base:** main at **v205** · **Deliver into:** `ChatGPT-to-Sarvam/` · **Plan:** `ROADMAP-TO-V1.0.md`

## Part 1 — Memory update

**v205. COURSE CHANGE: three languages get full development - Sanskrit (default), Gujarati, Hindi.** The
other eight are **DRAFT**; the `--lang` switch still works for all eleven. **If your work touches packs or
message text, the three SUPPORTED packs are what matter.**

**Your ROUND-80 is received** - the installer, the `kosh` A/B, the vocabulary audit and modules.

**The diagnostics are now in all eleven packs** (Claude's R11), so **nothing you write should match
Sanskrit-only diagnostic text** - the default is romanised Sanskrit and `--lang` switches the whole message.

## Part 2 — The work

### WS1 — the installer payload *(owner-visible; STILL OPEN, third round)*

**The committed `Sutram-Setup.exe` carries a compiler older than the `sutram.exe` beside it.** The owner
tests on Windows and **the installed version is the first thing he sees.** The compiler has now changed
**three times** since you last read the tree (the F1 fix, the pack diagnostics, the three-language change).

**Rebuild it so the payload is the current compiler and state the payload's hash.** If it needs a Windows
machine, **say so and give the exact command.** **If it cannot be rebuilt from your side, say that plainly
and stop** - a third round of silence on this is worse than a clear no.

### WS2 — the `kosh` A/B

Still open. **The three routes stand:** build NASM yourself; **ask me for a compiled ELF**; or **say plainly
that neither works.** A second NOT-RUN with a clear reason is acceptable; a third is not. **If you want the
binary, say the form you can consume.**

### WS3 — the repository-wide keyword audit

Still NOT_RUN. **Two traps:** a stale name can hide **after a `\n` escape**, and **`pankti` legitimately
means "line"** - and it now sits inside messages that are no longer Sanskrit-only, so **re-check rather than
assume.** Same for `to`.

### WS4 — separate compilation

The smallest working link, or **the smallest failing case** with the command and the error.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.** The installer is yours.

## Part 4 — What to return
One document per workstream. **WS1 first - and if it is blocked, say so in the first line.**
