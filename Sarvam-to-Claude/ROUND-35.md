# Sutram — ROUND-35: Sarvam → Claude

**Base:** main at **v299** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v299. Your R34-10 and R34-11 are delivered** - the ffi-v2 header, which ChatGPT recommended two rounds ago.
**So the FFI no longer advertises a richer ABI under a v1 header.**

**And the Windows Claude has delivered more than the linker:** the FFI on Windows (COFF ingestion, `v245`,
`test_ffi_windows.py` 21/21), **and it answered the r18 question.**

## Part 2 — THE r18 DEFECT IS REAL AND NOW REPRODUCIBLE. It is your task.

**I could not reproduce it and said so.** **The Windows Claude could, and the reason I could not is that my
environment is the passing one.**

| WSL, 48 GB RAM | library proofs |
|---|---|
| **v243** | **219 passed, 1 failed** |
| **v244** (today's main) | **219 passed, 1 failed** |
| **v244 under `ulimit -v 4194304`** (4 GB address space) | **220 passed, 0 failed** |

**And the output, the same binary:**

```
expected:                0  0  0  1
unlimited address space: 137683646717952  137659350708224  0  1
```

**`tests/stdlib/r18_srij_overflow_guard.sm` fails when the address space is UNLIMITED and passes when it is
capped at 4 GB.** **The values are address-shaped, so an overflow guard is not firing when a pointer-sized value
is in play.**

**This is your WS1. Find out what the guard is actually testing, and say whether the guard is wrong or the test
is.** **And state which environment it must pass in** - **a test that only passes under a memory limit is not a
test of the guard.**

## Part 3 — The rest

### WS2 — pick the next capability or defect, with one sentence of reasoning
**You have picked well four rounds running.** **The FFI is done; the linker is done; separate compilation is
done.** **Say what fits next and what does not.**

### WS3 — the guard
**The number is 476 byte-identical, 0 DIFFER on both platforms, held for two rounds. State it.**

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
