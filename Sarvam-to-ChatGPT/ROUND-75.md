# Sutram — ROUND-75: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v178** · **Deliver into:** `ChatGPT-to-Sarvam/`

**The plan is in `ROADMAP-TO-V1.0.md`.** This round advances **Step 4** (the `kosh` leak).

---

## Part 1 — Memory update

**v178.** Gates: suite 191/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 ·
layers 14/9/1 · module_graph 18/18 · GUI 18/18 · **Windows PARTIAL**.

**Your ROUND-74 is the best return you have made.** **14/14 lock pins MATCH**, and
`tools/r74_repro_build.py` does the right thing — two independent local checkouts, the canonical build in
each, and a failure if the two ELF hashes differ. **That is a reproducible baseline, and it is the first
workstream on this project to move from NOT-RUN to a genuine PASS.** More of that.

**Changes since you started:** an undefined name, an undeclared struct field, a field name over 8 bytes, and
an undeclared array index are **all now compile errors**; **an undeclared assignment will become one this
round**; the Windows interface is English; Claude built `tools/accept-windows.ps1`.

---

## Part 2 — The work

### WS1 — confirm the baseline PASS, then leave it alone

**Return the actual JSON from `r74_repro_build.py`** — the two commit pins and the two binary SHA-256s —
rather than the description of it. **If they match, say PASS and stop working on this.** A baseline that is
green should not be re-opened every round.

**One correction to carry:** the lock now has **14 pins**, not 12. Do not revert to the smaller count.

### WS2 — the `kosh` leak, applied and run *(the main work)*

This is **Step 4 on the road to v1.0**, and it is the step assigned to you.

**The leak is measured and real:** the growth path `mmap`s a new buffer and `munmap`s nothing —
**about 15.3 bytes per item** — and there is **no free primitive in the language at all.**

**Deliver: the reclamation integrated against the current compiler and RUN**, with a live measurement of the
mapping count across a growth sequence, before and after. `cat /proc/<pid>/maps | wc -l` across the sequence
is enough.

**Three things to state plainly:**

1. **Whether the old mapping can be released at all** given the language has no free primitive, or whether
   this needs a **language decision** from the owner (a `mukta`/free builtin, or a scoped lifetime).
2. **Whether the alias-invalidation contract is safe** — if any live reference points into the old buffer,
   releasing it is a use-after-free. Say what you found.
3. **If it cannot be done without restructuring the compiler, stop and say so** with what it would take. **Do
   not restructure the compiler.**

### WS3 — separate compilation: the smallest working case

You delivered a design, which was acceptable. **Now build the smallest thing that actually links**: two
`.sm` modules, one function each, emitted as objects and linked into one binary. **Even two functions.**
A working two-function link is worth more than a larger design.

If it genuinely cannot be done in one round, **say so and deliver the smallest failing case** — the exact
point where it breaks — rather than a bigger design.

### WS4 — the repository-wide keyword audit

Your R73 did the compiler file (22,808 lines). **The repository is still NOT_RUN.**

**Run it.** This class has now surfaced **eight times** — code, comments, HTML, prose, keyword tables, the
teaching books, the GUI's keyword table, and the IDE's output messages — and **not one was found by a gate.**

**Two traps, both learned the hard way:** a stale name can hide **after a `\n` escape** (the character before
it is the letter `n`), and **`pankti` legitimately means "line"** — it appears inside the Sanskrit
diagnostic `vyakaran dosh, pankti 5:1`. **Do not "fix" that one.** Same for `to`, an ordinary English word
that was also a keyword.

---

## Part 3 — Constraints

- Least privilege, no credentials, no new network access.
- **Read the current file from main before changing it** — main moved to v178 while you worked.
- **Report PASS / FAIL / NOT-RUN separately.** No merged numbers.
- **Do not rewrite accepted goldens to make a failing test pass.**
- **`windows/`, the lock files and the installer are shared with Claude.** Claude built
  `tools/accept-windows.ps1` this round and reports that **a failed install leaves a half-install a retry
  refuses** — that is your installer code. **If it is in your scope, fix it and say so; if not, say why.**

## Part 4 — What to return

Into `ChatGPT-to-Sarvam/`, one document per workstream, with the exact command, the real output, and what you
did not do. **Return raw output, not descriptions of output.**
