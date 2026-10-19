# Sutram — ROUND-76: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v182** · **Deliver into:** `ChatGPT-to-Sarvam/`

**The plan is in `ROADMAP-TO-V1.0.md`.** This round advances **Step 4** (the `kosh` leak) and continues
**Step 3** (separate compilation).

---

## Part 1 — Memory update

**v182.** Suite **203/4** · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 ·
layers 14/9/1 · module_graph 18/18 · GUI 18/18 · **performance 4 ran / 0 failed** · **Windows PARTIAL**.

**Your ROUND-75 is received and the reclamation staging is good work** — ported to the **current 14-pin
compiler**, with a checkpoint tool sampling `/proc/PID/maps`, VmRSS, VmHWM and VmSize before and after
growth. **And you stated plainly that it is not a new compiler and not a general-purpose free builtin. That
honesty is the reason the work is usable.**

**Three things changed while you worked:**

1. **Claude's ROUND-07 is merged and it closed Step 1.** Every name-resolution path now errors on a wrong
   name: undeclared assignment, block scope, re-declaration, fields, arrays, arity, modules, aliases. **The
   compiler changed, so your pins must be re-checked against current main.**
2. **`tools/gates.sh` now has a performance gate**, and reads **10 PASS / 0 FAIL / 1 NOT-RUN**.
3. **All seven committed binaries were rebuilt** by Claude and are reproducible — the repository's binaries
   are now the ones the source produces.

**Merge order, again:** your R75 prepare step pins the compiler blob that R7 changed. **R7 merged first.**
**Re-check your pins against current main before you apply anything.**

---

## Part 2 — The work

### WS1 — the `kosh` reclamation: measure it, then decide

Your R75 staged the payload. **Now produce the measurement that decides whether it is acceptable.**

**Deliver the JSON from your checkpoint tool, raw** — the mapping count, VmRSS, VmHWM and VmSize at start
and after growth, for both the legacy and the reclaim compiler, on the same source. **That before/after is
the whole point of the round.**

**Then answer three questions in plain words:**

1. **Does it actually reclaim?** If the mapping count returns to baseline, say so. If it does not, say that
   instead — **a prototype that does not reclaim is a useful result, not a failure.**
2. **Is the alias-invalidation contract safe?** If any live reference can point into the released buffer,
   this is a use-after-free. **Say what you found.**
3. **Does the language need a free primitive?** You have said this payload is Linux-only and not a general
   builtin. **If a `mukta` builtin is the right answer, say so and say what it would cost** — that is an
   owner decision and it is better raised now than after v1.0.

### WS2 — Step 3: the smallest working separate compilation

You delivered a design in R73 and the staging in R75. **Now build the smallest thing that actually links:**
two `.sm` modules, one function each, emitted as objects and linked into one binary. **Even two functions.**

If it genuinely cannot be done in one round, **deliver the smallest failing case** — the exact point where it
breaks, with the command and the error — rather than a larger design. **A failing case I can reproduce is
worth more than a design I cannot.**

### WS3 — the repository-wide keyword audit *(still NOT_RUN)*

Your R73 audited the compiler file — 22,808 lines. **The repository is still not done.**

**Run it.** This class has now surfaced **eight times** — code, comments, HTML, prose, keyword tables, the
teaching books, the GUI's keyword table, and the IDE's output messages — **and not one was found by a gate.**

**Two traps, both learned the hard way:** a stale name can hide **after a `\n` escape** (the character before
it is the letter `n`), and **`pankti` legitimately means "line"** — it appears inside the Sanskrit
diagnostic `vyakaran dosh, pankti 5:1`. **Do not "fix" that one.** Same for `to`, an ordinary English word
that was also a keyword.

### WS4 — the installer defect

Claude reported that **a failed install leaves a half-install that a retry refuses.** That is your installer
code. **If it is in your scope, fix it and say so; if it is not, say why.** A user who has one failed install
and cannot retry has a machine they cannot install Sutram on.

---

## Part 3 — Constraints

- Least privilege, no credentials, no new network access.
- **Read the current file from main before changing it** — main moved to v182 while you worked.
- **Report PASS / FAIL / NOT-RUN separately.** No merged numbers.
- **Return raw output, not descriptions of output.**
- **`windows/`, the lock files and the installer are shared with Claude** — state what you touched.

## Part 4 — What to return

Into `ChatGPT-to-Sarvam/`, one document per workstream, with the exact command and the real output.
**The `kosh` before/after JSON is the headline artefact — put it first.**
