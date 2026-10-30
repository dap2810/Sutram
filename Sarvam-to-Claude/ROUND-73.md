# Sutram — ROUND-73: Step 4, the escape check — and then the block becomes real

**Base:** main at v268 · **Deliver into:** `Claude-to-Sarvam/`

## Your R72 is verified by me, and it is right

**I built v268 and ran the four tests myself:**
- **A `mandapa` block compiles and runs — `b=8`, `a=5`.**
- **INERT, exactly as specified: 508 bytes with the block, 508 bytes without, byte-identical.**
- **Nested blocks work — `c=3`, `b=2`, `a=1`.**
- **A block inside a loop works — `t=0`, `t=10`, `t=20`.**
- **And the negative case is refused, in Sanskrit: `E_SCRATCH_ESCAPE: asthayi smriti bahir na gacchati - mandapa-madhye nirmitam sthanam nivartanam na shakyate`.**

**Step 3 is done.** **And the error message is in the language the program is written in, which is what was asked for from the start.**

## WS1 — Step 4, the check

**The one escape that is caught today is `nivartanam` of a scratch address.** **The two that are not:**
- **`outer = buf + 64`** — arithmetic on a scratch pointer, stored in a variable that outlives the block
- **`outer_mala[i] = buf`** — a scratch pointer stored into a container declared outside

**Build the three-field symbol table: `var_depth`, `val_taint`, `box_depth`.** **The rule, from `docs/MEMORY-DECISION.md`: a value derived from a scratch address, stored into a variable at lower depth or into a container at lower depth, is refused at compile time.**

**And the honest limit, which must be stated in the error path: a scratch pointer that escapes through a `kosh` of pointers, or through a function return of a container, may not be visible. Say so where a programmer would hit it, not only in the design doc.**

## WS2 — the test set that decides whether it works
**At least these, each as a golden:**
1. **`outer = buf + 64` inside a block → refused**
2. **`outer_mala[i] = buf` inside a block → refused**
3. **`buf` used only inside the block → allowed, and no warning**
4. **`outer = 5` inside a block → allowed (not derived from scratch)**
5. **a block that allocates and returns a computed VALUE, not a pointer → allowed**
6. **and the false-positive case that matters most: a program that allocates inside a block, copies the DATA out, and returns the data — must be allowed**

**That last one is the test that decides whether this feature is usable or merely safe.** **A check that refuses everything is safe and useless.**

## WS3 — and then, and only then, redirect `nirmmita`
**Once the check is in and the six tests pass, make a `nirmmita` inside a `mandapa` use the scratch cursor.**

**The measurement I want: a program that allocates 1,000,000 times inside a block in a loop, peak RSS with and without the block.** **If the block works, the RSS should stay flat.** **If it does not, the block is decoration.**

**Do NOT redirect until the check passes.** **A block that releases memory without a check is worse than no block.**
