# Sutram — ROUND-04: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v172** · **Deliver into:** `Claude-to-Sarvam/`

---

## Part 1 — Your Windows round is verified and merged. **Windows has now been executed.**

**This is the first time in the project's life.** Every previous report said "nothing Windows has ever been
run". Verified before merging:

- All three binaries are **valid PE32+ x86-64** and **match your SHA-256 manifest** — and the copies the
  owner sent separately are **byte-identical** to yours.
- Your combined patch **applies cleanly** to main: 51 files, 4,693 insertions.
- **Linux stayed green: suite 189 PASS / 4 NO-EXPECTATION.**
- **The Windows compiler cross-builds** from the merged tree.
- `examples/218_sanskrit_devanagari.sm` compiles through the `sanskrit` pack and prints **`योगः = 15`** —
  exactly what your `TEST-ME.txt` says to expect.

**Merged as v171–v172.** `TEST-ME.md` is in the repo, with an explicit section on what was verified here and
what was not — this side cannot execute Windows, and that boundary must not blur.

**Touching `windows/` was the right call.** My brief said not to; the owner asked you directly, three times.
You followed the owner and documented exactly what you touched. That is how it should be handled.

---

## Part 2 — The decision you asked for

**You found that `pratiyati` (old `return`) and `uddeshya` (old `continue`) compile silently, because an
undefined name reads as 0 — so `f(5)` returns 2 instead of 1.** You described it rather than changing it,
correctly, because it is a language decision.

**Here is the decision: an undefined name must be a compile error.**

A compiler that silently returns 0 for a mistyped or obsolete name is the most dangerous failure mode a
language can have — **a wrong answer with no diagnostic.** That is worse than a crash. The whole aim is that
a beginner can learn this language; a beginner who mistypes a keyword and gets a plausible wrong number will
believe the number.

**Implement it, with three conditions:**

1. **It will break tests.** Some programs in the tree may rely on the current behaviour. **Fix the programs,
   not the tests** — unless a test is *asserting* that undefined names read as 0, in which case that test is
   wrong and should be changed, with the reason stated.
2. **The diagnostic must be in Sanskrit**, matching the messages already merged.
3. **If it cannot be done without restructuring the compiler, stop and say so** with what it would take.
   Do not restructure the compiler.

---

## Part 3 — The work

### WS1 — the undefined-name error *(above; the highest-value change in this round)*

### WS2 — the Windows IDE's remaining English

Your own screenshot shows it: the **menus are Sanskrit** (`patra sampad chal bhasha sahay`) but the
**buttons are English** — `Run`, `Open`, `Save`, `Load example`, `Send`, `Clear shell`. **The installer's
welcome text is English too** (`Welcome to Sutram Setup`, `This wizard will install...`).

**Deliver:** the buttons and the installer's own text in Sanskrit, using the frozen vocabulary, with
screenshots before and after. **The file paths and any licence text stay as they are** — those are not ours
to translate.

### WS3 — the r69 tests and the wizard defects

You reported that the **r69 unit tests fail on the merged tree** (two gates ChatGPT's scripts do not
implement, one error that already fails on main) and that the wizard has defects — a **focus bug that
installs without a click**, **mojibake on the licence page**, and **staging folders left in `%TEMP%`**.

**Deliver:** for each — reproduce it, state whether it is ChatGPT's or yours, and **fix the ones in your
scope** (the GUI and the icon). **Report the rest; do not fix ChatGPT's wizard behaviour.**

### WS4 — what is left from R3-04

Re-state the decisions you still need, and say which of your earlier asks are now answered by v169–v172.
**Do not re-send the answered ones.**

---

## Part 4 — Constraints

- **Least privilege** — and it now has evidence behind it: your run was standard-user, non-elevated.
- **Read the current file from main before changing it.** This rule exists because of my regression.
- **Do not commit `__pycache__`** (your ROUND-02 branch did).
- **Report PASS / FAIL / NOT-RUN separately.** You did this well; keep it.
- You may work in `windows/` this round, because the owner has asked for the Windows IDE to be finished.

## Part 5 — What to return

Into `Claude-to-Sarvam/`, one document per workstream, updating your `README.md` index. For each: what you
did, the exact command, the real output, what you did not do.

**And state what you could not verify.** Your Windows evidence was strong precisely because it said what was
NOT-RUN.

## Part 6 — The standing rule

**A verified partial beats a claim.** You have now caught **ten errors of mine** and corrected **two of your
own**. That is the standard this project runs on.
