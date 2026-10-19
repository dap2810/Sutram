# Sutram — ROUND-77: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v185** · **Deliver into:** `ChatGPT-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md` — this round advances **Step 4** and **Step 3**.

---

## Part 1 — Memory update

**v185.** Suite 203/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 ·
module_graph 18/18 · GUI 18/18 · performance 4 ran / 0 failed · **Windows PARTIAL**.

**Your ROUND-76 is received.** **Native `kosh` A/B: NOT_RUN** — no compiler executable in your session and
NASM absent. **You said so plainly and explicitly did not invent the mapping counts. That is exactly right,
and it is worth more than a fabricated measurement.** 14/14 lock pins still match; 9/9 structural checks pass.

**Three changes since you started:** every name-resolution path now errors on a wrong name (Claude's R7);
Claude's R8 closed **43 library functions** and produced the gap list — **212 of 303 closed, 91 open**; and
**the version string was fixed** (it had said v160 while the project was at v182).

---

## Part 2 — The work

### WS1 — the `kosh` A/B: get a compiler into your session *(first)*

**Your blocker is a missing binary, not a Sutram failure.** `tools/r76_kosh_measure.py` exited 2 with
`nonregular executable` — a prerequisite failure.

**Deliver: the measurement, or a precise statement of what you need.** Options, easiest first:

1. **Build the compiler yourself.** NASM 2.16 is a single static binary; if you can fetch it, the canonical
   build is two commands. **If you cannot fetch it, say so and stop** — do not simulate.
2. **Ask me for a binary.** Say what form you can consume (base64, a path, a GitHub release asset) and I
   will put the compiled ELF where you can reach it. **This is the channel working as intended.**
3. **If neither works, say so plainly and move on.** A second NOT-RUN with a clear reason is an acceptable
   answer; a third is not.

**The three questions still stand, and they matter more than the numbers:** does it actually reclaim; is the
alias-invalidation contract safe; and **does the language need a free primitive** — which is an owner
decision.

### WS2 — Step 3: separate compilation, the smallest working link

Two `.sm` modules, one function each, emitted as objects and linked into one binary. **Or the smallest
failing case** — the exact point where it breaks, with the command and the error. **A reproducible failure
is worth more than a design.**

### WS3 — the repository-wide keyword audit *(still NOT_RUN)*

Your R73 did the compiler file — 22,808 lines then, 23,335 now. **The repository is still not done.**
This class has surfaced **eight times** and **not one was found by a gate.**

**Two traps:** a stale name can hide **after a `\n` escape** (the character before it is the letter `n`), and
**`pankti` legitimately means "line"** — it appears inside the Sanskrit diagnostic `vyakaran dosh, pankti
5:1`. **Do not "fix" that one.** Same for `to`, an ordinary English word that was also a keyword.

### WS4 — the installer

Claude reported that **a failed install leaves a half-install that a retry refuses**, and that **the
committed `Sutram-Setup.exe` carries a compiler older than the `sutram.exe` beside it** — so installing
reports `v160` while the project is at v185. **Both are your installer code.**

**Fix them, or say why they are not fixable from your side.** A user who cannot retry an install, or who
sees a version number twenty-five releases stale, has a broken first impression.

---

## Part 3 — Constraints

Least privilege, no credentials, no new network access. **Read the current file from main before changing
it.** Report PASS / FAIL / NOT-RUN separately. **Return raw output, not descriptions of output.**
**`windows/` and the installer are shared with Claude** — state what you touched.

## Part 4 — What to return

One document per workstream, exact commands and real output. **If something cannot run, say so in one line
and move to the next workstream** — a clean NOT-RUN costs nothing, and I would rather have four honest
results than one padded one.
