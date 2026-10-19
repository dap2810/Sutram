# Sutram — ROUND-11: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v198** · **Deliver into:** `Claude-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md`

> **Complete round. If it is not in this file, it is not in scope.**

---

## Part 1 — Memory update

**v198. F1 IS CLOSED.** Verified by me and **confirmed by the owner on his Windows machine**: `f1.sm`
(38 local variables) now prints `7`, where before it compiled to 562 bytes and printed nothing. **The byte
count rose to 622 — the proof it is a different build**, since the fix uses 4-byte displacements where a
1-byte one overflowed silently.

**And ChatGPT's independent root-cause analysis agreed with yours exactly** — same cause, and **both of you
found 15 sites.** It also disassembled the wrap byte by byte and showed a slot at -248 landing on the return
address. **Two readings, arrived at separately, naming the same code.** That is as strong as confirmation
gets.

**Suite 205/4 · library proofs 210/210 · Step 5 at 255 of 303 closed, 48 open.**

---

## Part 2 — The work

### WS1 — the diagnostics go English *(the owner's decision)*

**The owner has decided, and it is not the option you recommended — that is fine, he weighed it.**

**The compiler's messages and the IDE's status line become ENGLISH by default**, because **he could not read
them**: he ran `sutram.exe` and got `Prayog`, `nivesh.sm`, `sankalan`; he hit an error and got
`vyakaran dosh, pankti 3:13`. **He is the target user and the help screen was useless to him.**

**The Sanskrit is kept, behind a switch** — so nothing is lost for anyone who wants it. **Pick the switch
name and say what you chose.** `--sandesh sa` or similar; your call, stated in your delivery.

**Consequences to handle, all of which you already costed in R9-04 and R10-03:**
- **Every golden containing a compiler message must be updated in the same change**, or the suite drops.
- **Keep the `Sutram Error:` prefix and the `[E_CODE]` tags** — they are identifiers, not prose.
- **The help text, the arity errors, the hints, the `--check` summary and the IDE's status line.**
- **Report the new counts** — how many strings, how many goldens moved.

**This is the last item of the interface work.** When it lands, the interface and the diagnostics are in the
same language, which was Step 2's whole point.

### WS2 — Step 5: the 48 open functions

Continue with the mutant measure. **255 of 303 closed.** Say which you closed and which you did not, and why.

### WS3 — what is left

Which items from R10 are still open? **Do not re-send answered ones.**

---

## Part 3 — Constraints

Least privilege, no credentials. **Read the current file from main before changing it.** Report PASS / FAIL /
NOT-RUN separately, with the environment named. Do not commit `__pycache__`.

## Part 4 — What to return

One document per workstream, updating your `README.md` index.
