# Sutram — ROUND-09: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v185** · **Deliver into:** `Claude-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md` — this round advances **Step 5**, and **verifies F1**.

---

## Part 1 — Memory update

**v185.** Suite 203/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 ·
module_graph 18/18 · GUI 18/18 · performance 4 ran / 0 failed · **Windows PARTIAL**.

**Your R8 is merged.** Two things in it are outstanding:

**The gap list exists: 212 closed, 91 open of 303.** That number did not exist before this round.

**And you refused the easy measure** — a proof that only fails when the *whole body* is broken is a smoke
test, not a proof. Re-measuring with **1,119 bug-shaped mutants** and killing 781 → 862 is what makes the
number mean something. **That is the best piece of judgement in any delivery so far.**

---

## Part 2 — The work

### WS1 — F1: give me the reproduction *(first, and small)*

**I could not reproduce it, and I need to know which of us is wrong.**

**What I tried, all four giving the correct answer:**

| Test | Expected | Got |
|---|---|---|
| 26 variables in `mukhya`, summed | 325 | **325** |
| caller with 23 variables calling a function | 1007 | **1007** |
| 40-variable caller calling a function | 152 | **152** |
| a plain call | 1007 | **1007** |

**So deliver F1 as a file, not as a description:** the exact `.sm`, the exact command, and the observed
output — **paste it, do not summarise it.** If it only triggers through `yoj`-included library code, say
which module and give that program. **If it triggers only under Wine, say so and give the Windows output.**

**Why I am being strict about this:** your finding may be right and my test may be the wrong shape — that is
the likely case and it is why I have not called it false. But **"a function with more than 21 variables
computes wrong values" is a claim that, if true, stops everything.** It cannot be accepted on a description,
and it cannot be fixed on one either. **A file settles it in five minutes.**

**Until it is reproduced it is not a defect in the changelog and nobody fixes it.**

### WS2 — Step 5 continues: the 91 open functions

**Continue closing the gap**, largest-value first, using the mutant measure you established. **Say which you
closed and which you did not, and why.** If some of the 91 cannot be usefully proven — a wrapper, a trivial
contract — **say so rather than writing a proof that asserts nothing.**

### WS3 — F2 to F6

Take the five smaller findings. **For each: reproduce it as a file, then fix it or say why not.**
`nirmmita` returning `-errno` so "0 on failure" checks never fire is the one I would take first — **it is a
silent wrong answer in the same family as Step 1.**

### WS4 — the diagnostics decision

**Unchanged and still the owner's.** Restate it in one paragraph at the top of your delivery, with the
recommendation (**D now, E as translations arrive**). Do not change anything.

---

## Part 3 — Constraints

Least privilege, no credentials. **Read the current file from main before changing it.** Report PASS / FAIL /
NOT-RUN separately, with the environment named per check. Do not commit `__pycache__`.

## Part 4 — The standing rule

**A verified partial beats a claim** — and it now applies to your findings as much as to mine. **A
description is not a reproduction.** I could not reproduce F1, and I would rather say so than accept it or
dismiss it.
