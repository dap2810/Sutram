# Sutram — ROUND-78: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v191** · **Deliver into:** `ChatGPT-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md`

> **Complete round. If it is not in this file, it is not in scope.**

---

## Part 1 — Memory update

**v191.** Your ROUND-77 is received and **WS5 is a real fix** — `install-core.ps1` now distinguishes a fresh
directory from an existing install and **rolls back only after a fresh install has started changing files**,
removing only what it created, preserving unknown files, reverting PATH only if this attempt added it, and
removing HKCU keys only if they were absent before. **A user can now retry a failed install.**

**Changes since you started:** Claude's R9 fixed **F2–F6**, corrected **the IDE's font** (it asked for
Consolas, which covers none of the eleven scripts), and made **the transliteration mode work** — the owner
can now type `mukhy` and get `मुख्य` from an English keyboard.

**And a new top item, which is why this round is short:** **F1 is confirmed — a function with 38+ variables
segfaults.** I reproduced it. **Claude is fixing it, and nothing else on the critical path matters until it
is fixed.**

---

## Part 2 — The work

### WS0 — F1: find the ROOT CAUSE *(read-only; do not edit the compiler)*

**The most serious defect on this project, now confirmed on Windows by the owner:**

| Local variables in a CALLED function | Linux | Windows (owner) |
|---|---|---|
| 18, 20, 22, **30** | correct | **correct - printed `7`** |
| **34** | not tested | **compiles, then NO OUTPUT** |
| 38, 40 | **SEGFAULT (exit 139)** | **compiles, then NO OUTPUT** |

**The compiler prints `Siddh: ... byte sankalit` - it reports SUCCESS - and the program then produces
nothing.** A user would rewrite working code for hours before suspecting the compiler.

**Why you, and why read-only:** Claude is fixing it, and **two of us editing the same 570 KB assembly file
is how you get a merge nobody can untangle.** So **do not edit `src/sutram_compiler.asm`.** Read it.

**Deliver:**
1. **The exact site.** Where local variables are assigned stack slots - the function that computes the
   offset, and the lines that encode it. **Give line numbers.**
2. **The root cause, in two sentences.** Claude's earlier description was *"stack slots past the 16th are
   encoded with a one-byte displacement and land in the caller's frame."* **Confirm it, correct it, or
   replace it - with the code that proves it.**
3. **Why Linux crashes at 38 and Windows at 34.** **This is the clue neither of us had.** If the threshold
   differs by platform, the cause may be **stack size rather than codegen** - the frame layout, the red
   zone, or a guard page. **Say which, and say how you would tell them apart.**
4. **The proposed patch, as a diff in your document** - not applied. Claude applies and verifies it.

**A wrong root cause costs a round. Say "I could not determine this" rather than guessing.**


### WS1 — the installer's stale payload *(the owner-visible item; still open)*

**The committed `Sutram-Setup.exe` carries a compiler older than the `sutram.exe` beside it**, so **an
installed copy reports the wrong version.** The owner is testing on Windows now and **this is the first thing
he will see.**

**Rebuild the installer so its payload is the current compiler**, and **state the payload's hash.** If the
rebuild needs a Windows machine, **say so and give the exact command** so it can be run there.

**Note:** `win/sutram.exe` — which your installer packages — **was rebuilt by Claude this round**, so it is
current now. **Use the new one.**

### WS2 — the `kosh` A/B

Still the open question, and still blocked in your session. **The three routes stand:** build NASM yourself;
**ask me for a compiled ELF and I will put it where you can reach it**; or **say plainly that neither works
and move on.** A second NOT-RUN with a clear reason is acceptable; a third is not.

**If you ask for the binary, say what form you can consume** (base64, a path, a release asset).

### WS3 — the repository-wide keyword audit

Still NOT_RUN. **Two traps:** a stale name can hide **after a `\n` escape**, and **`pankti` legitimately
means "line"** — it appears inside the Sanskrit diagnostic `vyakaran dosh, pankti 5:1`. **Do not "fix" that
one.** Same for `to`.

### WS4 — separate compilation

The smallest working link, or **the smallest failing case** — the exact point where it breaks, with the
command and the error. **A reproducible failure is worth more than a design.**

---

## Part 3 — Constraints

Least privilege, no credentials, no new network access. **Read the current file from main before changing
it.** Report PASS / FAIL / NOT-RUN separately. **Return raw output, not descriptions of output.**
**The installer is yours; the IDE is Claude's** — state what you touched.

## Part 4 — What to return

One document per workstream. **WS1 first — it is what the owner sees.** If something cannot run, say so in
one line and move on.
