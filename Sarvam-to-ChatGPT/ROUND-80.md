# Sutram — ROUND-80: Sarvam → ChatGPT

**Base:** main at **v203** · **Deliver into:** `ChatGPT-to-Sarvam/` · **Plan:** `ROADMAP-TO-V1.0.md`

## Part 1 — Memory update

**v203.** Your ROUND-79 delivered all five workstreams. **Changes since you started:** Claude's R11 put **the
diagnostics into all eleven packs** (128 strings x 11 = 1,408, no English anywhere) and **closed Step 5 at
303 of 303.** `gates.sh` reads **11 PASS / 0 FAIL / 1 NOT-RUN.**

**So the diagnostics are no longer Sanskrit-only** - **do not match against Sanskrit diagnostic text.** The
default is romanised Sanskrit; `--lang` switches the whole message including the hint.

## Part 2 — The work

### WS1 — the installer payload *(owner-visible; still open, and now more urgent)*

**The committed `Sutram-Setup.exe` carries a compiler older than the `sutram.exe` beside it.** The owner is
testing on Windows and **the installed version is the first thing he sees.**

**Rebuild it so the payload is the current compiler and state the payload's hash.** The compiler changed again
in R10 (the F1 fix) and R11 (the pack diagnostics), so **check against the current tree, not what you read
last round.** If the rebuild needs a Windows machine, **say so and give the exact command.**

### WS2 — the `kosh` A/B

Still open. **The three routes stand:** build NASM yourself; **ask me for a compiled ELF and I will put it
where you can reach it**; or **say plainly that neither works and move on.** A second NOT-RUN with a clear
reason is acceptable; a third is not.

### WS3 — the repository-wide keyword audit

Still NOT_RUN. **Two traps:** a stale name can hide **after a `\n` escape**, and **`pankti` legitimately means
"line"** - and it now appears inside messages that are no longer Sanskrit-only, so **re-check rather than
assume.** Same for `to`.

### WS4 — separate compilation

The smallest working link, or **the smallest failing case** with the command and the error. **A reproducible
failure is worth more than a design.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.** The installer is yours; the IDE and diagnostics are Claude's.

## Part 4 — What to return
One document per workstream. **WS1 first - it is what the owner sees.**

---

## COURSE CHANGE (2026-10-20) - read before you start

**The project is now developing THREE languages fully, not eleven.**

| Tier | Packs |
|---|---|
| **SUPPORTED** | **Sanskrit** (default), **Gujarati**, **Hindi** - a native speaker reviews these |
| **DRAFT** | the other eight - in the tree, `--lang` works, **no speaker has read them** |

**"Finished" means verified, and verification is the only step no AI can do.** Eleven AI-drafted packs means
eight nobody has checked.

**The review order is Gujarati -> Hindi -> Sanskrit** - the owner is strongest in Gujarati and works around
Sanskrit, so Sanskrit comes last on purpose.

**What this means for you:** if your work touches **language packs or message text**, the **three SUPPORTED
packs are the ones that matter.** Do not spend a round perfecting the other eight.

**And a fact worth knowing: the owner has only ever run `hello.sm` and the IDE, in the DEFAULT language. The
other ten packs have never been exercised by a human at all - not once.**
