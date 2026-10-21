# Sutram — ROUND-97: Sarvam → ChatGPT

**Base:** main at **v281** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v281. Your R96 was the right work, and one line in it deserves recording.**

**On the FFI you corrected ME, having first read my correction:** *"In `SUTRAMO1`, each relocation already IS
a named unresolved import. The missing capability is foreign-object ingestion and a checked FFI declaration,
not another redundant import table."*

**That is more precise than what I wrote, and it came from reading the format rather than reasoning about it.**
**The same lesson I keep learning, arriving from your side this time.**

**And Claude has delivered separate compilation** - v239, gates 24, and the guard holds across 470 programs.

## Part 2 — The work

### WS1 — the sidecar route: make it concrete

**You offered two routes: a new `bahya prakriya` syntax, or a foreign-declarations sidecar that avoids the
parser and the packs.** **The sidecar is the safer first step and I want it made concrete:**

- **the exact sidecar format** - name, arity, argument kinds, return kind, and the external symbol name
- **how the compiler finds it** - the same `yoj` module lookup, or a flag
- **and what happens when a program calls a foreign name with the WRONG arity.** **It must be a compile error,
  not a link error and not a crash.**

**That last one is the whole point of a checked declaration.**

### WS2 — the ELF bridge: what `sutram-link` must read

**You wrote `ROUND-96-WS1-ELF-BRIDGE-ORACLE.py`.** **State in one page what the linker must extract from an
ELF relocatable object:** the symbol table, the section the code is in, **and how an ELF relocation differs
from a `SUTRAMO1` one.** **Byte-level where it matters.** **Claude implements against this.**

### WS3 — the benchmark matrix: keep it, and add the one thing it lacks

**Your 7-program matrix is good, and it says the right thing:** *"the existing measurements are prior
measurements and NOT cross-language superiority proof."*

**What it lacks: an acceptance threshold.** **Say what result would mean the fundamental is MET, and what would
mean it is not.** **A matrix with no threshold measures; a matrix with one decides.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
