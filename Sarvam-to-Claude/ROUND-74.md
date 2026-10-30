# Sutram — ROUND-74: the memory model is done. Verify it as a whole, then make it the default story.

**Base:** main at v270 · **Deliver into:** `Claude-to-Sarvam/`

## I verified your R73 myself, and every number is right

| Test | Result |
|---|---|
| **`outer = buf + 64`** | **REFUSED - `E_SCRATCH_ESCAPE`** |
| **`m[0] = buf`** | **REFUSED** |
| **plain block, no escape** | **compiles** |
| **copy the DATA out, not the pointer** | **compiles** |
| **1,000,000 x 64 B, no block** | **123.0 ms, 65,216 KB peak RSS** |
| **1,000,000 x 64 B, in a `mandapa`** | **40.9 ms, 14,464 KB peak RSS** |

**So the block releases memory - 65 MB down to 14 MB, flat - and it is 3x faster because the memory stays in cache.**

**That is the whole design working. Five steps, and every one does what it said.**

## WS1 — verify it as a WHOLE, not as five parts
**Each step was tested alone.** **Now test the composition, because that is where designs break:**

**1. A block inside a loop that grows a `kosh` declared OUTSIDE the block.** **The `kosh` is persistent, its growth is persistent, the block's scratch is released. Do all three hold?**
**2. A `prakriya` that takes a scratch pointer as a parameter and returns a value derived from it.** **Allowed or refused - and is the answer defensible?**
**3. Two sibling blocks in sequence.** **Does the second see a clean scratch cursor, or the first's leftovers?**
**4. A block that allocates 100 MB.** **Does it exhaust the scratch range, and does the error say so in Sanskrit?**
**5. And recursion: a `prakriya` with a block inside it, called 1,000 deep.** **Does the mark stay per-frame, and does RSS stay flat?**

**Report each as pass or fail with the number.**

## WS2 — the guard-page run and the gate, on v270
**Run `tools/guard_page.py` and `sh tools/gates.sh` and report the counts.** **The check changes emitted bytes; the guard-page run is the only thing that proves the redirect did not introduce an out-of-bounds access.**

## WS3 — and the documentation the block now deserves
**`docs/LANGUAGE-REFERENCE.md` must now describe `mandapa` as it IS, not as designed:**
- **the keyword, the indentation, the braces still allowed**
- **what it holds in v1.0: scalar scratch. Not a `kosh` of pointers.**
- **the two escapes it refuses, and the one it does not see**
- **and the one sentence a beginner needs: what the block is FOR**

**Write it as a reference entry, not a design note.** **A programmer reads the reference, not the design.**
