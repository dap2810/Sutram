# R65-00 — Hand-back to Sarvam: the `avayava` reword applied, Step 1 built

- **Commits on `main`, in order:** `817cd89` (1/2: the reword, v262) · `593fc6d` (2/2: Step 1, v263) ·
  `81dc568` (3/3: a proof's own over-read corrected) · then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v263) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**. Property proofs: **86/86**.
- **R28 linker 208/0, R29 separate 0 failed (152 no-module programs byte-identical), R30 8/8, R32 50/50,
  R38 fail-alloc 115/115, R45 8/8, R46 20/20, R70 corpus 6/0.**
- **Gates (`sh tools/gates.sh`), with a display (Xvfb): 47 PASS / 1 FAIL / 1 NOT-RUN.**
  - **The FAIL is "doc counts", and it is not this round's:** the v411 banner the owner added to `PROJECT-MASTER.md`
    says *"property proofs 86/86"*, and `tools/doc_counts_gate.py` reads any two-digit `N/N` above the gate count as an
    impossible gate claim. It fails on the R58 transcript too. One fix is "86 of 86" in the banner; the other is the
    tool. **Docs prose is not mine, so it is reported.** With it, 48 PASS as before.
  - The NOT-RUN is Windows execution.
- **The guard, stated the way you asked (two runs, each on ELF, PE and Wine):**
  - **v261 → v262, the reword alone: 577 programs, 486 byte-identical, 91 refused identically, 0 DIFFER** on all
    three paths.
  - **v262 → v263, Step 1:**
    - **Linux ELF: 248 programs changed bytes — every program that allocates — and 238 are byte-identical: the
      programs that neither allocate nor grow a `kosh`.** 91 refused identically.
    - **PE and the Windows compiler under Wine: 0 DIFFER.** Windows keeps the per-call `VirtualAlloc`, as the owner's
      own work.
    - **Of the 248: 247 produce the same output and exit code. One differs, `examples/217_r12_report.sm`, and it
      is a bug in the example, exposed not caused** (below). It has no golden.

## WS1 — Muse's `avayava` patch

**`git apply --check` passed; applied; 0 rejected hunks; 19 files** (`evidence-r65/avayava-patch.txt`).
- 4 default strings in the compiler; 4 entries in `lang/sanskrit.sandesh`; `src/r11_sandesh.inc` regenerated.
- **The ten frozen packs changed only in their comment lines** — the default text that precedes each entry —
  **0 translation lines.** Verified per pack.
- 4 goldens plus `tests/sandesh/expect/sanskrit/unknown_field.out`; 2 assertions in `tests/r23`.
- **Every change is text in a compile-time refusal.** No program's output changes: the guard reads 0 DIFFER.

## WS2 — Step 1

### `nirmmita` is a contiguous bump

`src/r65_arena.inc`, pinned with the compiler. At every `nirmmita` site in a Linux ELF build (`r38_nirm_seq` now
begins with the gate), the emitted code is:

- **fast path, 6 instructions:** `room = end − cur`; if `cur ≠ 0`, `size ≠ 0` and `size ≤ room`: the block is `cur`,
  and `cur = align16(cur + size)`;
- **first call:** `mmap(0, 1 GiB, RW, PRIVATE|ANONYMOUS|NORESERVE)`; on success `cur`/`end` are set and the fast path
  retried; on failure `cur = end = 16`, so the room is 0 forever;
- **fallback:** today's 43-byte sequence, unchanged, so `nirmmita(0)` is still 0 (EINVAL) and an exhausted or
  unreservable arena behaves exactly like today.

**The cursor and the end are two hidden module globals, `0kshetra_cur` / `0kshetra_end`,** registered at the first
emission only — so a program that never allocates registers nothing and emits the same bytes. They are names no
program can write. The debugger now hides any global whose name starts with `0`, as it hid its own counter.

**Measured** (`evidence-r65/r59-benchmark-on-v263.txt`, R59's own programs): 100,000 × 64 B, each touched —
**44–64 cycles per allocation and 6,144 KB resident, against 4,600–8,200 cycles and 400,000 KB on v261.** The
one-block program is unchanged at ~50 cycles. The arena memory is never reused, so it is zeroed like `mmap` memory.

### In-place `kosh` extension — the safe half only

In the growth path (`:15799`), after `newcap` is known and before anything is allocated: **if `align16(user_ptr +
cap·8) == cur`, the buffer is the last allocation, so `cur = align16(user_ptr + newcap·8)` and the capacity field
becomes `newcap`; nothing is copied and nothing moves.** Otherwise today's copy runs. Odd capacities extend too
(`kosh k[3]` → 6 → 12 → … → 192 in place).

**The proof you asked for, before and after** (`evidence-r65/kosh-alias.sm`, `kosh-measurements.txt`):

```
kosh k[1]; kosh_push(k, 7); vitti a = k; kosh_push(k, 8); kosh_push(k, 9)
```

| | `kosh_len(a)` | `kosh_len(k)` | `a[2]` | `a == k` |
|---|---|---|---|---|
| **v261** | **1** | 3 | **bounds error** (two buffers; `a` holds the old one) | — |
| **v263** | **3** | 3 | **9** | **1** (one buffer, extended) |

**The change in behaviour is stated: an alias of a `kosh` now follows its growth.** Before, it silently kept a stale
copy.

**The aliasing hazard cannot occur: no block changes hands.** Extension moves the cursor forward over bytes no one
has been given; a buffer that is not at the cursor is copied as today and the old one is abandoned as today, never
reused. There is no path by which a block reaches a different `kosh`. The 1,000,000-append program's `kosh_cap` is
1,048,576 before and after, so no output that prints a capacity changes.

### `--object` / `--separate` take the same path

The first build kept object mode on the old sequence, and the R28 and R29 gates failed: **they require an object
linked by `sutram-link` to be byte-identical to the direct compile.** So objects use the arena too, and the two
globals are ordinary module `vitti` of the object: **the root defines them** (always, when the program has modules,
since a module object that allocates refers to them as extern `vitti:0kshetra_cur`), **a module object marks them
extern**, and a root without modules registers them lazily like a direct compile, which keeps the 152 no-module
programs byte-identical. R28 208/0, R29 0 failed, R30 8/8, R32 50/50.

## WS3 — the measurement

**1,000,000 `kosh_push` onto `kosh k[1]`: peak RSS 16,000 KB on v261, 7,808 KB on v263** — the same as a
`kosh k[1000000]` that never grows, on both. **The leak is gone for the single-vector-in-a-loop case**, and it was
caught by extension at every doubling. When another allocation sits above the `kosh`, growth copies as today: a
bounded leak, never a reuse.

## Test expectations that followed the bytes, and one that followed a bug

- **24 `tests/sandesh` goldens record the compiled size** (`Siddh: 369 baait sankalit` → 536, in 11 packs for the
  two allocating cases). Re-recorded with the test's own `--record`; nothing else in them changed.
- **`tests/r29`, `tests/r30`, `tests/r32` list an object's exported symbols exactly.** The root now also exports
  the two hidden `vitti`; the three helpers leave `vitti:0*` out, so the lists mean what they meant.
- **`--fail-alloc`'s skip-jump became `rel32`:** the sequence is 196 bytes, past a `rel8`. Test builds only.
- **One property proof was wrong, and `mmap` had been hiding it** (`evidence-r65/proof-overread.txt`): *bigint divmod
  reconstruct* allocated `a` and `r` with 8 cells and then compared `a` over 16 digits and added `r` over 16. The 8
  cells past each block used to be the zeroed rest of its page; in the arena they are the next block. **Fixed in
  commit 3/3 by allocating the 16 cells it reads; 86/86 on v261 and on v263. The library is untouched.**

## Found, not fixed: `examples/217_r12_report.sm`

`vitti koshtha = nirmmita(32)` — 4 cells — then `pad_vam(koshtha, cnt, 6, 32)`, whose contract says *"caller must
allocate ≥ width cells"*: 6 cells, 48 bytes. The two cells past the block land in `row`, allocated right after, and
the program prints `row`: its "Padded scores" read `     5` where they read `    85`
(`evidence-r65/217-report-overrun.txt`). Deterministic both ways. **It is the 248th program, the one whose output
changed, and it is the example's bug: the fix is `nirmmita(48)`, one number, in a later round.**

**The same class, found and reported, nothing else:** these two are the first consequences of blocks no longer being
page-padded. Anything in the tree that reads past its own allocation now reads its neighbour.

## What I did NOT do

- **Nothing in Steps 2–4**, no cursor pair, no keyword.
- **Windows:** the PE emitter and the adapter are unchanged; the Windows compiler was rebuilt from the same source
  and compiles every program to the same bytes as v262.
- **Not fixed:** `217_r12_report`'s size; the `PROJECT-MASTER` banner's `86/86`.
- **Not run:** real Windows (Wine only).
- **Not touched:** `lib/`, `lang/`, `backups/`, `Windows-to-Sarvam/`, the frozen packs' translations.
