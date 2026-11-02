# R107-00 — The block-arena `kosh` priced (not built); the escape error and `parimana()` built (v289); the R106 decision argued. One commit.

- **Commit on `main`:** `cbfae59` (rebased onto ChatGPT's R176 and Muse's R103 files, `5f88f12`; the v288 base was `466c7d7`).
- **Compiler: `Sutram 1.0 (v289) - sampurna sutra`** (was v288). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=285`, FAIL=0** (283 + goldens 316, 317; 287 is now a compile-time refusal golden).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, v243
  against v289). **The first run was 57 / 3 / 1** - WS4 below.
- **The guard, origin/main (v288) → v289, 695 programs** (`evidence-r107/guard.txt`):
  - **Linux ELF: 556 byte-identical, 136 refused identically, 1 DIFFER, 2 new.**
  - **Linux PE: 556 byte-identical, 136 refused identically, 1 DIFFER, 2 new.**
  - **The Windows compiler under Wine: 556 byte-identical, 136 refused identically, 1 DIFFER (the same 287), 2 new; its 1113 outputs are byte-identical to the Linux compiler's PE outputs.**
  - **The one DIFFER is `examples/287`, and it is the intended one:** it stored a block's `kosh` in an outer variable
    and read it after the block; v288 compiled it and stopped at run time with `E_KOSH_MANDAPA`; v289 refuses it at
    compile time with the same error code. The old behaviour was the caught bug, the new one catches it earlier.

## WS1 - the price of "a `kosh` in a block is a slot in the block's arena"

All numbers are measured on v289 unless marked computed (`evidence-r107/ws1-measurements.txt`, programs in
`evidence-r107/programs/`).

**1. A slot against a region: a slot is much cheaper, and never touches the slow path.**

| | a region (today) | a slot in the block's arena |
|---|---|---|
| instructions to allocate | **12, then an `mmap` system call** (`dis_region.disasm.txt`) | **14, no system call** (`dis_slot.disasm.txt`): cursor down, round to 16, two bound checks, store |
| zeroing | none (the kernel hands out zeroed pages, at a page fault each) | 4 instructions per 8 bytes (scratch memory is reused) - **a `kosh` slot can skip it** (its length starts at 0) |
| kb1: 100,000 blocks each making a 100-number `kosh` | **0.46-0.59 s, 400,000 KB** | **0.03-0.04 s, 0 KB** (`kb1_arena_equivalent.sm`: the same blocks drawing all eight slots of a `kosh` grown from capacity 1 to 128, filled with the same numbers) |

The slow path is the arena's reservation (one `mmap` of 1 GiB at the first allocation, shared by every block) and
its exhaustion message; a slot reaches neither.

**2. Growth with waste, a `kosh` grown to 1,000 inside a block: 8,656 dead bytes.** Measured with `parimana()`
inside a block, slots for capacities 1, 2, 4, ... 1,024, each a 40-byte header (a program with a `kosh` in a block
has the 5-word header) plus 8 bytes a number, rounded to 16 (`growth_1000_in_block.sm`):

| | bytes |
|---|---|
| all slots | **16,896** |
| the live slot (capacity 1,024) | 8,240 |
| **dead slots, summed** | **8,656** |
| after the block | **0** |

A `kosh` declared with the default capacity 4 skips the 1- and 2-slots: **16,784 total, 8,544 dead - the same
figure ChatGPT's R176 computed**, so the two analyses agree. The waste is about one more `kosh`, bounded by the
block and by `parimita`.

**3. Fixed size: enough.** The block's arena is the scratch side of the 1 GiB range; it does not grow.
`scratch_full.sm` asks for 100 MB per pass inside one block: the tenth succeeds (`block holds 1000000000`), the
eleventh stops with `Sutram Error: kshetra purnam - mandapa-smritih samapta`, exit 1. With `parimita N` the refusal
comes at the budget instead (R103). A growing `kosh` slot would draw on the same side, so it inherits both. (That
message has no error code yet; it should get one when this lands.)

**4. What breaks: one example - `287` - and no running program.** The v288 tree has **287 examples** (the brief's 283
is the v287 count; v289 adds two, 289). Three make a `kosh` inside a `mandapa`: `286` and `299` use it only inside and
keep working; `287` keeps it in an outer variable and uses it after the block, on purpose - it was written to show
R82's check (and v289 now refuses it at compile time). Nothing in `lib/` makes a `kosh` in a block; the tests add
none. **Muse's independent count (R103, which arrived while I was finishing) is the same: 3 make one, 1 uses it after
(287, through the alias `bahar = k`), 0 running programs break** - and Muse names the same second cost below
(growth moves the `kosh`, so the never-move guarantee does not hold inside a block). The two counts agree.

**What the design costs that the four questions do not ask** - the part I would not skip:

- **Aliasing comes back inside blocks.** A slot that grows moves, so `vitti a = k` then `kosh_push(k, ...)` past
  capacity leaves `a` on the old slot - the divergence v284 closed (example 288), back for block `kosh`s. **Fix: refuse
  `vitti a = k` for a block `kosh`** - cheap with this round's escape machinery, and one more rule: a block `kosh`
  has one name.
- **The runtime check loses its exactness for the case the compiler cannot see** (a `prakriya` that keeps the
  `kosh`, example 316). Today the dead `kosh`'s header survives, so R82 names the block. In a block arena the header
  is in memory the next block reuses: zeroed memory reads as "made outside any block" and passes; the same block
  re-entered puts a new `kosh` at the same address with a fresh generation, and the stale handle reads it. That is
  the gap `nirmmita` scratch already has ("What it does not see", §19) - extended to `kosh`.
- **The slot must not be zeroed** for speed, or the 4-instructions-per-8-bytes cost returns.

**Net:** the design is right for memory (400 MB → 0, 15x faster on kb1) and the escape error built this round is
its enforcement point. It needs the alias refusal with it, and it costs R82's exact message for `prakriya`-kept
`kosh`s. I estimate 3 days with the alias rule.

## WS2 - built

**The escape error.** A `kosh` declared inside a `mandapa` now carries the block's depth as its R73 taint, so the
scratch-escape rules apply to the `kosh` itself, with its own message:

```
Sutram Error [E_KOSH_MANDAPA]: mandape rachitah kosh mandapat bahih na gacchati - bahya-vittau na sthapyate
Sanket: kosh mandape eva upayujyatam (k[i], kosh_len(k)), mulyam nivartyatam; bahih avashyakah cet mandapat purvam rachyatam
```

| the `kosh` tries to leave by | v288 | v289 |
|---|---|---|
| a variable declared outside the block (`bahar = k`, example 287) | ran; stopped at the next `prakriya` (R82) | **refused at compile time**, `... bahya-vittau na sthapyate` |
| memory (`kosh_push(outer, k)`, `m[i] = k`) | ran | **refused**, `... smritau na likhyate` |
| `nivartanam k` from inside the block | ran | **refused**, `... nivartanam na shakyate` |
| a `prakriya` that returns or keeps it (example 316) | stopped at the next `prakriya` (R82) | **the same** - the runtime check stays for this |
| `k[i]`, `kosh_len(k)`, `padh(k, i)`, `vitti a = k` inside the block | allowed | allowed |

The code name is R82's, so a student meets one error for one rule, at compile time when the compiler can see it and
at run time when it cannot. **Its cost: none at run time** (a parse-time check); no program without a `kosh` in a
block changes. The R82 gate now routes its five runtime cases through a `prakriya` (the shape the compiler cannot
see), and checks the three compile-time refusals: 12 checks, 0 failed.

One known limit: an alias made inside the block (`vitti a = k`, then `bahar = a`) is refused too, but with the
general `E_SCRATCH_ESCAPE` message, not the `kosh` one.

**`parimana()` / `परिमाण()`** - the bytes the program's allocations hold now (golden 317):

```
start 0
after nirmmita(64) 64
in a block, nirmmita(1000) 1072
after the block 64
a kosh of 1000 8272
```

It is the arena's persistent side (`cur - start`) plus its scratch side (`sima - end`, which falls when a block ends)
plus each `kosh`'s header and capacity, from a hidden counter `0parimana` updated at each region's allocation and
growth. **The counter is emitted only in programs that call `parimana`**, so every other program compiles to the
same bytes (the guard: 556 identical). It is what the program asked for, not resident pages; a `nirmmita` past the
1 GiB arena (its own `mmap` fallback) is not counted. Linux ELF (direct, `--object`, `--separate`); on Windows 0.
This round's WS1 measurement of the dead slots is the first one in the project taken by the program itself.

## WS3 - the R106 decision, in one paragraph

**It was risk first, then a cost that made the risk not worth taking.** The risk: R82's `E_KOSH_MANDAPA` reads the
`kosh`'s header after the block to say "this `kosh` died with the block on line N"; a region returned at block exit
takes the header with it, so the one case the check exists for becomes a SIGSEGV (unmapped) or a silent read of
whatever `kosh` is given that address next (reused) - a regression from a named error to a crash or a wrong answer.
The cost: the only way to keep the check exact was to keep the header's page, which is 4 KB - the whole of a small
`kosh` - so the return would have freed nothing in exactly the case that wastes memory (kb1's 100,000 small `kosh`s),
and in the tree it would free nothing at all (the three programs with a `kosh` in a block read 0 KB). It was never the
instruction cost. **What changed this round:** the escape error now refuses at compile time every escape the compiler
can see, and a block-arena `kosh` has no page granularity, so the cost half of the argument is gone. The risk half
remains for one shape - a `prakriya` that keeps the `kosh` - and that is the price to weigh (WS1, above).

## WS4 - the first run, honestly

**The first gate run on v289 was 57 / 3 / 1** (`evidence-r107/gates-first-run.txt`):

- **`R82 kosh-mandapa` 5 failed** - its five runtime cases stored the block `kosh` in an outer variable, which is
  exactly what v289 refuses. I rewrote them to leave through a `prakriya` (so the runtime check is still exercised,
  and still names the right block line) and added the three compile-time cases.
- **`guard pages` 1 failed** - golden 317 reads the arena, which the guard-page build does not have (it printed 0s).
  Skipped there, as 288 and 303 are.
- **`installer version`** - the standing v243 failure.

**Re-run: 59 / 1 / 1.** The guard ran once, on the final compiler (the two fixes are in tests and tools, not the
compiler).

## Not done

- **The block-arena `kosh`**: priced above, not built, as the brief said.
- **ChatGPT's R176 identity table** (`kosh == kosh` as identity rather than v288's refusal): not changed this round;
  it is a choice between two defensible rules and belongs with the arena decision.
- **The installer** (v243); **native-speaker review** of the three new `E_KOSH_MANDAPA` texts: NOT RUN; real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
