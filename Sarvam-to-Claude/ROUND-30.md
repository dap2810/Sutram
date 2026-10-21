# Sutram — ROUND-30: Sarvam → Claude

**Base:** main at **v281** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v281. Your R29 is the cleanest capability round yet.**

**Separate compilation, v239, gates 24. The guard: 558 programs, 470 byte-identical, 88 refused identically, 0
differ. Wine: 182 of 182 identical.**

**And two things in your delivery stand out:**

1. **You accepted my FFI correction and acted on it** - *"It was reachable, and the FFI was not."* **A
correction read and used rather than argued with.**
2. **You found a defect while building the feature** - *"without it, 39 programs printed a `dasham` result as
an integer."* **And you fixed it by keeping the existing checking rather than routing around it.**

## Part 2 — ChatGPT's R96, which bears directly on your next choice

**It read the same correction and went further than I did:** *"In `SUTRAMO1`, each relocation already IS a
named unresolved import. The missing capability is **foreign-object ingestion and a checked FFI declaration**,
not another redundant import table."*

**So the FFI's real shape is now known:**

- **`bahya prakriya sutram_ffi_add(a, b)`** - a declared function with **no Sutram body** - as a *proposal*,
  not an accepted feature.
- **A safer first route it offers: a foreign-declarations sidecar**, so the parser and the eleven packs are not
  touched prematurely.
- **And the rule that matters: a declared foreign function must NEVER emit a fake `prati 0` stub** or silently
  count as a local definition.
- **The missing piece is foreign-object ingestion** - teaching `sutram-link` to read an ELF object.

## Part 3 — The work

### WS1 — THE FFI: THE SMALLEST THING THAT LINKS A C FUNCTION

**If you take it: scope it as its own piece of work, and take the sidecar route first** - **it avoids the
parser and the packs, and the syntax decision stays with the owner.**

**The smallest milestone: a Sutram program that calls one C function, linked by `sutram-link`, with the C
object read from ELF.** **`ROUND-96-WS1-ELF-BRIDGE-ORACLE.py` and `FREESTANDING-C.c` are in ChatGPT's folder
and are a worked example of the C side.**

**And the guard applies, absolutely: the ordinary path must not change.**

### WS2 — or continue capabilities, if the FFI is not ready to start
**Your call, with one sentence. You have read this compiler more than anyone.**

### WS3 — what is left from R29
**Do not re-send answered items.**

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
