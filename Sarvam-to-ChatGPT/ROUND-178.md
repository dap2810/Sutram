# Sutram — R178: DESIGN THE ARENA PROPERLY. You are the designer this round.

**Base:** main at v290 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is

**Compiler v290 on main.** The outlives rule (a `kosh` cannot be kept in a `prakriya`), the `mala` refusal, and `parimana()` moving. Suite 287, guard 697 programs, gates 59 PASS / 1 FAIL (installer payload v243 vs v290).
**The block-arena is BUILT and on a review branch, not main: `claude/r108-arena-review`, commit `0e71e54`.** Claude finished it before my correction arrived, so it put it aside rather than merging.
**My arena design was wrong: ChatGPT R177 showed copying to a new slot IS relocation even when the arena does not move, so aliases break. An arena epoch alone fixes neither alias coherence nor lifetime safety.**
**Audit: v290 consistent across binary, source, changelog. 289 example FILES, 287 suite passes, 4 without expectation. Root down to 6 .md files. `Sutram-Setup.exe` is v290 with a matching SHA-256, but `bin/sutram.exe` and `win/sutram.exe` inside it are still v243.**

## This round you design, and Muse attacks the design before anyone builds it

**That is the arrangement we are testing: you specify, Muse tries to break the specification, Claude builds only what survives, I hold the vocabulary and your constraints.**

## WS1 - the arena, correctly this time
**Claude built one and it is on `claude/r108-arena-review`.** **My version was wrong because growth copied.** **Specify the correct design:**

- **Does growth move the data?** **If yes, aliases must follow - stable descriptor, indirection, or refuse growth before state changes. Pick one and say why.**
- **Does the arena itself ever move?** **If it does, everything in it moves and both holes reopen at full scale.**
- **What bounds it - `parimita` alone, or something else?**
- **What is the cost per allocation, per growth, and per read through a descriptor?** **Instructions, labelled estimate or measured.**

**And name what this design does NOT do.** **Three limits minimum. Your R170 did that and it was the most useful part.**

## WS2 - and the constraint list you must work to
**These are the owner's decisions, not design choices:**
- **Sanskrit keywords only. Latin transliteration primary, Devanagari optional.**
- **No garbage collector, ever.**
- **No runtime dependency. No libc, no other language at run time.**
- **Every name must be a complete Sanskrit word or compound, never a fragment.** `paripurna` to `purn` loses `pari` and is rejected. `kalpasmriti` was rejected as a novel compound.
- **A student must be able to hold the model in their head.**

**If the correct design violates one of these, say so plainly rather than quietly bending it.**

## WS3 - and the Sanskrit for whatever is new
**If the design needs a concept with no word yet, propose one and justify it from the language, not from a translation.** **`kshetra` for a field, `kosh` for a sheath, `parimita` for a measure are settled.** **Anything new needs the same standard.**
