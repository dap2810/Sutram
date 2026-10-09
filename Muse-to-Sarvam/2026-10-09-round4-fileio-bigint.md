# Round report — Round 4: fileio retired, bigint domain, 118/118

Date: 2026-10-09 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse ROUND-04.md
— make fileio real or retire it, add one new library domain, keep the harness honest.

## 1. fileio — RETIRED

The four stubs (`file_open`, `file_read`, `file_write`, `file_close`, each just
`pratiyati 0`) are deleted, along with their 12 test/golden files.

**Why retire instead of implement:** I tested the compiler builtins
(`dvaram`/`paadh`/`likha`/`band`) by actually running them. Reading works.
File *creation* works — but `dvaram(path, flags)` takes no mode argument, so
`O_CREAT` files get whatever garbage is in `rdx` (observed: mode 0). As root
the round trip works; as non-root the created file is unopenable. A fileio
module that only works as root is worse than an honest gap. The builtins remain
available for direct use.

**Limitation stated plainly:** if `dvaram` ever gains a mode parameter, fileio
can be reimplemented on top of it. Until then, retired.

## 2. New domain: big integers — `lib/bigint.smlib`

Picked big-integer arithmetic (pure computation, no syscalls, no undefined
behavior). Base-10 digits (0-9), least-significant-first, fixed-size arrays.
9 functions, all verified by execution:

| Function | What it does |
|---|---|
| `bigint_zero(arr, n)` | Zero n digits |
| `bigint_from_int(val, arr, n)` | int → digits; returns 1 if fit, 0 if truncated |
| `bigint_to_int(arr, n)` | digits → int (for verification) |
| `bigint_copy(dst, src, n)` | Copy n digits |
| `bigint_cmp(a, b, n)` | -1 / 0 / 1 |
| `bigint_add(a, b, res, n)` | res = a+b; returns final carry |
| `bigint_sub(a, b, res, n)` | res = a-b (requires a≥b); returns borrow |
| `bigint_mul(a, b, res, n)` | res = a*b; res needs 2n digits |
| `bigint_is_zero(arr, n)` | 1 if all zero |

**Why not the other options:** statistics is already `sankhyiki` (10 functions);
string formatting is blocked because `likha` only prints string *literals* as
strings (runtime buffers print as integers — verified); date/time has no builtins.

## 3. Proof harness — 118/118

9 new test programs in `tests/stdlib/bigint_*.sm`, each with edge cases
(carry chains, borrow chains, overflow, truncation, zero). Goldens recorded
from actual runs via `--record`, then hand-checked:

- 12345+6789=19134, 999+1=1000 (carry 0), 99999999+1 → carry 1, low digits 0
- 12345-6789=5556, 1000-1=999 (borrow chain), 500-500=0
- 12345×6789=83810205, 999×999=998001, ×0=0
- cmp: -1/1/0/1 across orderings; from_int truncation returns 0 with low 8 digits

`docs/sutram-stdlib.html` regenerated: 13 modules, 118 functions.

## What was actually run

```
$ ./build/sutram_compiler bigtest.sm /tmp/bigtest.bin && /tmp/bigtest.bin
12345 / 19134 / 5556 / 83810205 / 1   (all correct)
$ python3 tools/proof_lib.py --compiler build/sutram_compiler
118 passed, 0 failed, 118 total
$ python3 tools/gen_stdlib_ref.py
Wrote docs/sutram-stdlib.html: 13 modules, 118 functions
```

Compiler built with NASM 2.16.03 from source; `win/rtblob.inc` stub used for
the Linux build only (not committed). **Did not modify `src/sutram_compiler.asm`.**

## What was NOT run / not verified

- File creation as non-root (retired before needing it).
- Harness on Windows (POSIX-only, shells to nasm/ld).

## File hashes (SHA-256)

```
c55ec1529d16d14430050b21e56aea1f6712c3004fef0f7e80ed5e64084829e6  lib/bigint.smlib (new, 9 functions)
DELETED: lib/fileio.smlib (4 stubs retired)
DELETED: tests/stdlib/fileio_* (12 files)
NEW: tests/stdlib/bigint_*.sm + goldens (27 files)
```

## Deliverables in this folder

- `2026-10-09-round4-fileio-bigint.md` — this report.
- `2026-10-09-round4-deliverable-src.tar.gz` (SHA-256: `31caec3e0070ba98880d274b7fec83168797c4cf17ff6506f1eb4029da03e73b`) — source archive.
- `2026-10-09-round4-deliverable.patch` (SHA-256: `bcb9e0e059c0bc44c2a949f9127145d516dbf7c2ebd61e1d56f918b72a43c41f`) — unified diff.

## Proposed next task

Sarvam to review: (a) the fileio retirement rationale; (b) run the harness
to confirm 118/118; (c) whether bigint should grow (divmod, powmod) or stay minimal.
