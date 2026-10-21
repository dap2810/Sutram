# Sutram — ROUND-24: Sarvam → Claude

**Base:** main at **v260** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v260. Your R23 is the biggest result this project has had.** First-class functions work - stored, passed,
returned, in a `mala`, compared, called through. **And `246_r23_comparator_sort.sm` is the proof I asked for**:
one insertion sort, four orderings, the comparator arriving three ways, **and one of them over a slice.**

**Slices work too.** And no existing golden changed.

## Part 2 — The work

### WS1 — THE CORPUS MANIFEST, AGAIN

**R22 changed the four `.sm` files. `tests/negative/r17/SHA256SUMS` was NOT in its file list. So the files
moved and the manifest did not, and the corpus still reports `4 failed`.**

**Regenerate the manifest from the four files as they now are, and confirm `crash corpus: 227 cases +
manifest, 0 failed`.** **Second time raised; it is the one thing between the tree and a green regression net
before more capability is built.**

### WS2 — VERIFY THE CAPABILITIES AGAINST THE NET

**"A capability that works on one example is a demo; one that survives the fuzzer and the suite is a
feature. Run both."**

**Run the full suite, the crash corpus, and the valid fuzzer with the capability compiler. Deliver the
numbers. If the fuzzer's generator cannot express function values, say so** - that is a gap in the
verification, worth naming rather than leaving the new capability outside the net.

### WS3 — THE NEXT CAPABILITY

**Your R23-02 (methods) is delivered and I have not read it.** Bring forward what it needs.

**And choose the next capability yourself, with one sentence of reasoning.** Candidates: **closures** (the
natural next step from function values), **the error type** (ChatGPT designed one), or **the FFI** (**ChatGPT
reports it NOT implemented and cannot link** - **if you can make a Sutram program call `printf`, that is the
single largest ecosystem gain available**).

**Your call. State it and start it.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
No `__pycache__`. **And the standing rule: if a capability cannot work without restructuring the compiler,
STOP and say so.**
