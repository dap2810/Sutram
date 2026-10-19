# Sutram — ROUND-08: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v182** · **Deliver into:** `Claude-to-Sarvam/`

**The plan is in `ROADMAP-TO-V1.0.md`.** This round advances **Step 5** (prove the library is complete).

---

## Part 1 — Memory update

**v182.** Suite **203/4** · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 ·
layers 14/9/1 · module_graph 18/18 · GUI 18/18 · **performance 4 ran / 0 failed** · **Windows PARTIAL**.

**Your ROUND-07 is merged and it closed Step 1.** Verified by hand: `totl = 10` now errors, a block `vitti`
is invisible after its block, and re-declaring errors. **Suite 203/4, nine new goldens that all fail on the
previous compiler.**

**And you did the two things that made it a real close rather than another instance:** you delivered a
**50-probe inventory** instead of a fix list, and you **measured block scope before changing it — 0 programs
relied on the old behaviour.** You also found a **codegen bug already on main** (`vitti x = 1 … vitti x = 2`
kept 1) and **two bugs in the project's own tests.**

**One thing to know:** **Muse is paused**, so **Step 5 has no owner and is now yours.** That is why this
round is different from the last.

---

## Part 2 — The work

### WS1 — Step 5: prove the library is complete *(the main work)*

**The state of it, honestly:** the library is **24 modules and 303 functions**, with **191 library proofs and
86 property proofs** passing. **191 is not 303, and nobody currently knows which functions have no proof.**

**Deliver, in this order:**

1. **The gap list.** Which of the 303 functions have no proof, module by module. **This is the number that has
   to exist before release, and it does not exist today.** It is also the most valuable single artefact this
   round can produce.
2. **A contract for each unproven function** — what it promises, in one line.
3. **Proofs for as many as the round allows**, starting with the ones a user is most likely to call. Say
   which you proved and which you did not.

**Do not pad the count.** If a function cannot be usefully proven — because it is a wrapper, or its contract
is trivial — **say so and say why.** A proof that asserts nothing is worse than no proof, because it looks
like coverage.

### WS2 — the non-name silent cases you flagged

Your R7-01 mentions **non-name silent cases left for a decision.** **State them plainly, with what each
would cost, and recommend.** Given that the owner has now decided three times in favour of erroring, say
whether these are the same class. **Do not implement without the decision.**

### WS3 — the diagnostics decision *(still waiting on the owner)*

Your R7-02 prepared the table and recommended **D now, E as translations arrive**. **That is still the
owner's call.** Restate it in one paragraph at the top of your delivery so it is easy to find — and if you
have new information since R7-02, add it. **Do not change anything.**

### WS4 — what is left

Which items from R7-04 are still open? Do not re-send answered ones.

---

## Part 3 — Constraints

- Least privilege, no credentials.
- **Read the current file from main before changing it** — main moved to v182 while you worked, and
  `tools/gates.sh` and the CHANGELOG were mine.
- **Report PASS / FAIL / NOT-RUN separately, with the environment named per check.**
- Do not commit `__pycache__`.

## Part 4 — What to return

Into `Claude-to-Sarvam/`, one document per workstream, updating your `README.md` index. **The gap list is the
headline artefact — put it first.**

## Part 5 — The standing rule

**A verified partial beats a claim.** You have caught **eleven errors of mine**. Keep doing exactly that.
