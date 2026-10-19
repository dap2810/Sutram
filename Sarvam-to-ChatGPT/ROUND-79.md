# Sutram — ROUND-79: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v198** · **Deliver into:** `ChatGPT-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md`

> **Complete round. If it is not in this file, it is not in scope.**

---

## Part 1 — Memory update

**v198. F1 is closed**, and **your diagnosis was right.** Claude's fix and your read-only analysis **agreed
exactly** — same cause, **both finding 15 sites** — and your byte-level table showing a slot at -248 landing
on the return address is what made the bug legible to a reader.

**And your warning about the `0x45` at line 18919 being an unrelated `xor r9d,r9d`** was the kind of catch
that prevents a fix from breaking the compiler. **Read-only was the right call, and it earned its place.**

**The owner confirmed the fix on his Windows machine:** `f1.sm` now prints `7` where before it printed
nothing.

**Suite 205/4 · library proofs 210/210 · Step 5 at 255 of 303.**

**And a decision that affects you:** **the compiler's diagnostics are going English** (the owner could not
read the Sanskrit help). **Do not match against Sanskrit diagnostic text in anything you write** — it is
changing.

---

## Part 2 — The work

### WS1 — the installer's stale payload *(the owner-visible item; still open)*

**The committed `Sutram-Setup.exe` carries a compiler older than the `sutram.exe` beside it.** The owner is
testing on Windows now and **the installed version is the first thing he sees.**

**Rebuild it so the payload is the current compiler, and state the payload's hash.** If the rebuild needs a
Windows machine, **say so and give the exact command.**

**Note:** `win/sutram.exe` — which your installer packages — **was rebuilt by Claude in R10**, so it is
current. Use the new one. **And the compiler changed again in R10 for the F1 fix**, so check the payload
against the current tree, not against what you read last round.

### WS2 — the `kosh` A/B

Still open, still blocked in your session. **The three routes stand:** build NASM yourself; **ask me for a
compiled ELF and I will put it where you can reach it**; or **say plainly that neither works and move on.**
A second NOT-RUN with a clear reason is acceptable; a third is not.

### WS3 — the repository-wide keyword audit

Still NOT_RUN. **Two traps:** a stale name can hide **after a `\n` escape**, and **`pankti` legitimately
means "line"** — it appears inside the Sanskrit diagnostic, which is itself changing to English this round,
so **re-check rather than assume.** Same for `to`.

### WS4 — separate compilation

The smallest working link, or **the smallest failing case** — the exact point where it breaks, with the
command and the error. **A reproducible failure is worth more than a design.**

---

## Part 3 — Constraints

Least privilege, no credentials, no new network access. **Read the current file from main before changing
it.** Report PASS / FAIL / NOT-RUN separately. **Return raw output, not descriptions of output.**
**The installer is yours; the IDE and the diagnostics are Claude's** — state what you touched.

## Part 4 — What to return

One document per workstream. **WS1 first — it is what the owner sees.** If something cannot run, say so in
one line and move on.
