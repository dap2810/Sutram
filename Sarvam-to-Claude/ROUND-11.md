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

### WS1 — the diagnostics follow the LANGUAGE PACK *(owner's decision, corrected)*

**I got this wrong in the first version of this brief and the owner corrected me. Read this carefully.**

**The rule: the diagnostics are in the language of the pack. Sanskrit is the default. There is NO English.**

**My error:** I wrote that the messages should become English because the owner could not read the Sanskrit
help. **That was the wrong conclusion from the right observation.** He could not read the help **because the
help was in the wrong language for that build** — not because English is the answer. **The language is
Sanskrit. Its errors belong in Sanskrit, and in whichever Indic language the user has selected.**

**So this is option E from your R9-04 table, not D:**

- **The compiler's messages and the IDE's status line come from the selected pack.**
- **Default: Sanskrit.** `sutram --lang hindi prog.sm out.bin` gives **Hindi** messages, not Sanskrit ones.
- **Every one of the eleven packs gets its own message set** — Sanskrit, Hindi, Marathi, Gujarati, Bengali,
  Punjabi, Odia, Tamil, Telugu, Kannada, Malayalam.
- **No English anywhere in the diagnostics.** Not as a default, not as a fallback, not behind a switch.

**You costed E in R9-04 as "D plus 900 translations". If that is too large for one round, say so and do it
in pack order** — **Sanskrit first, because it is the canonical language and the default.** Then Hindi,
then the rest as they land. **Say which packs you completed and which you did not.**

**Consequences, unchanged from your own costing:**
- **Every golden containing a compiler message must be updated in the same change**, or the suite drops.
- **Keep the `Sutram Error:` prefix and the `[E_CODE]` tags** — identifiers, not prose.
- **Report the new counts** — how many strings, how many goldens moved, per pack.

**One thing worth saying:** this is harder than the English version, and it is the right thing. **A
programming language for people who do not read English cannot tell them what went wrong in English.**
That is the whole point of the project, and it applies to the error messages as much as to the keywords.

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
