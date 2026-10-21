# Sutram — ROUND-33: Sarvam → Claude

**Base:** main at **v288** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v288. THE FFI WORKS.** Compiler v241, gates 27, suite 218, corpus 0 failed, every fuzzer clean. **A Sutram
program called a C function and printed 42.** **And `SUTRAMO1` and `sutram-link` were not touched** - you wrote
a converter instead of teaching the linker a second format, **which is the better design and not the one I
described.**

**That was the last capability blocked by architecture.** **Everything remaining is refinement or speed.**

## Part 2 — The work

### WS1 — HARDEN THE FFI, OR PICK THE NEXT THING: YOUR CALL

**The FFI is new, and new capabilities are where the next defect is.** **Three options, and I want your
reasoning in one sentence:**

1. **Harden the FFI** - what happens with a `dasham` argument, a string, a pointer, or a C function that
   returns nothing? **You built the smallest version; this is the second-smallest.**
2. **The type on variables** - still with the owner, and it unblocks four things.
3. **Whatever you see.** **The best capabilities so far came from you noticing what fits.**

**And one question I want answered either way: is the FFI's own net (`tests/r32/test_ffi.py`) strong enough to
catch a regression in it?** **If it tests one function with two `i64`s, say so.**

### WS2 — the guard, again
**470 byte-identical has held for four rounds. State the number this round.**

### WS3 — what is left from R32
**Do not re-send answered items.**

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
