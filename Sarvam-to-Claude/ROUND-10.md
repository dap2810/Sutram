# Sutram — ROUND-10: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v191** · **Deliver into:** `Claude-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md`

> **This is the complete round.** Everything agreed since ROUND-09 is here. **If it is not in this file, it
> is not in scope.**

---

## Part 1 — Memory update

**v191.** Your ROUND-09 is merged: F2–F6 fixed, the IDE font corrected, the transliteration mode working, and
main's drifted locks and binaries re-pinned.

**You were right about F1 and I was wrong about my test.** Your R8 wording was imprecise — *"more than 21
variables"* — but the finding was real. **The trigger is a called function with 20+, or any function with
38+.** I reproduced it myself:

| Variables | Result |
|---|---|
| 18, 20, 22, 30 | correct |
| **38, 40** | **SEGFAULT — exit 139** |

**That is the most serious defect found on this project, and you found it by checking your own finding after
I could not reproduce it. The rule worked in both directions, which is what it is for.**

**One note on my side:** five of your branch's files carried my own recent changes backwards (the sockets
note, Step 8, the RETIRED installer header, the stdlib fix, the changelog) because the branch predates them.
**Excluded rather than reverted.** That trap has cost four rounds; it is caught before landing each time now.

---

## Part 2 — The work

### WS1 — F1: fix it *(everything else waits)*

**UPDATED with the owner's own Windows measurements. The bug is worse than first described.**

**Confirmed by three independent methods** — Claude's repro, my Linux threshold test, and **the owner
running it on real Windows**:

| Local variables in a CALLED function | Linux | Windows (owner) |
|---|---|---|
| 18, 20, 22, **30** | correct | **correct — printed `7`** |
| **34** | not tested | **compiles, then NO OUTPUT** |
| 38, 40 | **SEGFAULT (exit 139)** | **compiles, then NO OUTPUT** |

**So the boundary is between 30 and 34, not 38.** A function with **31-34 variables** already crashes —
**that is a moderately complex function, not an extreme one**, and a beginner writing real code would reach
it.

**And the failure mode is the worst kind.** The compiler prints `Siddh: 526 byte sankalit` — **it reports
SUCCESS** — and the program then produces nothing. **A user would assume their own logic was wrong and
rewrite working code for hours before suspecting the compiler.** For a language whose purpose is to teach
beginners, that is the most damaging failure there is.

**Deliver:**
- the fix, with a test that fails on v191 and passes after
- **the real threshold, pinned** — test 31, 32, 33, 34 and well past them; **the fix must hold at any
  number, not at 35**
- **the root cause in two sentences**, so the next reader does not have to rediscover it
- **whether Linux and Windows share one bug or two** — my Linux run crashed at 38 and the owner's Windows
  run crashed at 34. **If the threshold differs by platform, say so; it may be a stack-size issue rather
  than a codegen one.**

**If the fix needs the compiler restructured, stop and say so with what it would take.** Do not restructure.

**A valid program with 38 local variables segfaults. A language that crashes on valid input is not
usable**, so this is now ahead of everything else on the road to v1.0.

**Deliver:** the fix, plus a test that fails on v191 and passes after — **and find the real threshold.** My
measurements say 30 is fine and 38 crashes; **the boundary is somewhere between, and the fix must hold at
any number, not at 39.** Test at 31, 32, 34, 36 as well as well past it.

**If the fix needs the compiler restructured, stop and say so with what it would take.** Do not restructure.

**Then say what the root cause was**, in two sentences, so the next reader does not have to rediscover it.

### WS2 — Step 5: the 91 open functions

Continue closing the gap with the mutant measure. **Say which you closed and which you did not, and why.**

### WS3 — the diagnostics decision

**Still the owner's; unchanged.** Restate in one paragraph with the costs (**D now, E as translations
arrive**). Do not act.

### WS4 — the transliteration mode, extended

It works — that answers the owner's question. **Now say what it does NOT cover** (identifiers? strings?
comments?) and whether extending it is cheap. **Do not extend it without saying so first.**

### WS5 — the interface stays cheap to change

The owner is testing on Windows and **his findings arrive as fixes.** Keep UI strings in one table per
window, and **state what you touched in `windows/`** — ChatGPT is in the installer at the same time.

---

## Part 3 — Constraints

Least privilege, no credentials. **Read the current file from main before changing it.** Report PASS / FAIL /
NOT-RUN separately, with the environment named. Do not commit `__pycache__`.

## Part 4 — What to return

One document per workstream. **F1 first — it is the only item that blocks the release.**
