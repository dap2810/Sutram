# R67-00 — `217` settled: the example's bug; the leak's bound in bytes; Step 2 prepared

- **Base:** `main` at `ad3c05c`, compiler **v263**. **No source change this round.** Evidence in `evidence-r67/`.
- **Also answered here: ROUND-66's measurement** (the `kosh` aliasing count), and where ROUND-66's chunking stands
  against what shipped — see the last two sections.

## WS1 — `examples/217_r12_report.sm`: the example's bug. Step 1 stands.

**1. Old and new output.** Lines 15–22, the "Padded scores": old `    85 / 92 / 78 / 95 / 88 / 76 / 90 / 84`,
right-aligned in six; new `     5 /  2 /  8 /  5 /  8 /  6 /  0 /  4`. Both deterministic.

**2. The wrong line, and why it was wrong before.** Line 44: `vitti koshtha = nirmmita(32)` — **32 bytes is 4
qword cells.** Line 49 then calls `pad_vam(koshtha, cnt, 6, 32)`, whose contract in `lib/vakyank.smlib:237` says
*"Caller must allocate >= width cells"* — width 6, **48 bytes.** Lines 53–54 read `koshtha[j]` for `j < 6`. **So
the example writes and reads cells 4 and 5, sixteen bytes past the block it asked for.** It was wrong on the day it
was written; with one `mmap` per `nirmmita`, those sixteen bytes were the zeroed rest of `koshtha`'s own page, so the
over-write landed nowhere and the over-read returned what the over-write had put there.

**3. The same pattern in a minimal, `mandapa`-free program** (`evidence-r67/217-pattern-minimal.sm`): a 32-byte
`koshtha`, then a 64-byte `row` filled with `82`, then `pad_vam(koshtha, cnt, 6, 32)`:

| | `koshtha[4], koshtha[5]` after `pad_vam` | `row[0], row[1]` (were `82 82`) |
|---|---|---|
| **v261** | **`56 53`** — the digits `8`,`5`, written past a 4-cell block | `82 82` |
| **v263** | `56 53` | **`56 53`** — the same write, now landing in `row` |

**The write past the block happens on v261 too; the old allocator only gave it somewhere harmless to land.** It is
not specific to `217`: any program that allocates `n` and uses more than `n` behaves this way.

**4. The deciding question — reverted allocator, is the example still wrong? Yes.** Three independent checks:
- **The one-number fix, `nirmmita(48)`** (`217-fixed-48.sm`): **v261 and v263 produce identical output, and it is
  the original example's old output.** The allocator reproduces the intended output exactly once the example asks
  for what it uses.
- **The original example with `koshtha` allocated last** (`217-koshtha-last.sm`): **v263 gives the old output.**
  Nothing follows `koshtha`, so the overrun lands in unused arena — the difference is placement, not arithmetic.
- **The pattern program above shows the over-write on v261 itself.**

**Verdict: the example's bug, exposed not caused. Step 1 stands.** **The fix is `nirmmita(48)` on line 44, one
number; I have not applied it** — this round said settle, the last said report. It has no golden, so nothing else
moves when it is applied.

## WS2 — the leak's bound, as numbers

**Programs:** 1,000,000 `kosh_push` per `kosh`, measured peak RSS (`/usr/bin/time -v`), with a pre-sized
`kosh k[1000000]` control that never grows for the live-set figure (`evidence-r67/leak-bound-rss.txt`).

| Case | v261 | **v263** | live set (pre-sized control) | **abandoned on v263** | **per append** |
|---|---|---|---|---|---|
| one `kosh k[1]`, grown in a loop | 16,000 KB | **7,808 KB** | 7,808 KB | **0** | **0 B** |
| two `kosh k[1]`, pushes alternating | 32,128 KB | **32,000 KB** | 15,616 KB | **16,384 KB = 8,192 KB each** | **8.39 B per append per `kosh`** |
| three, round-robin | 48,256 KB | **48,000 KB** | 23,424 KB | **24,576 KB = 8,192 KB each** | **8.39 B** |

**The bound.** A `kosh` whose growths cannot extend abandons, at each doubling, its previous buffer:
`abandoned = 8·(C − c₀) + 16·g` bytes, where `C` is the final capacity, `c₀` the declared one and `g` the number
of growths (16 bytes of header each). For 1,000,000 appends into `k[1]`: `C = 1,048,576`, `g = 20`, so
`8·1,048,575 + 320 = 8,388,920 B = 8,192 KB` — **exactly the measured figure.**

- **It grows with the number of appends, not with the number of growths:** the geometric series is dominated by
  its last term, so abandoned ≈ 8·C, and C < 2n. **Worst case 16 bytes per append, typical 8.4, never more than the
  live capacity itself.** Abandoned memory is at most equal to the memory in use.
- **In-place extension removes all of it for one `kosh`** (0 bytes), **and almost none of it for two or more
  interleaved:** once two grow alternately, each copy puts the other below the cursor, so only the last-copied one
  can extend, and the next alternation undoes that. The 128 KB saved in the two-`kosh` case against v261 is page
  padding, not extension.
- **Before Step 1 the figure was the same 8.39 B per append plus a page per block.** The single-`kosh` case is the
  one Step 1 fixes, as the decision said.

## WS3 — Step 2 prepared, not built

**`dvi-mukha`: one range, two cursors.** The persistent cursor is `0kshetra_cur` as today; **`0kshetra_end` becomes
the scratch cursor** — it starts at the end of the range and moves down — so the persistent fast path needs no new
load: `room = scratch_cur − cur` is the comparison it already makes against `end`. One new hidden global holds the
range's true end for the scratch side's own check.

**Emitted code:**

| Path | Change | Bytes |
|---|---|---|
| persistent `nirmmita` (every site today) | **none**: it already computes `end − cur`; `end` is now the scratch cursor | 0 |
| reservation (first call) | also set the scratch cursor = range end, and the true end | +14 |
| scratch `nirmmita` (emitted only inside a `mandapa`, Step 3) | `scr −= align16(size)`; `cmp scr, cur`; `jb .full`; `rep stosb` | ~45 |
| `.full` for scratch | `kshetra purnam` runtime error, per the decision | ~30, once |

**Compiler lines:** ~15 in `r65_emit_nirm` (the reservation), ~60 for a sibling `r66_emit_scratch_nirm`, ~10 for
the third global: **~90 lines, in `src/r65_arena.inc`.** No existing path changes until Step 3 emits the scratch
form, so **Step 2 alone is guard-invisible except the 14 bytes at every reservation site — which is inside every
`nirmmita` site, so all 248 allocating programs change bytes again, with identical output.** Better: ship Step 2 and
Step 3 together, so the bytes change once.

**What Step 2 settles for the `kosh` escape:** a `kosh` lives on the persistent side, a `mandapa`'s blocks on the
scratch side; they cannot interleave, so an outer `kosh` growing inside a block is placed above the cursor, not in
the block's memory — **the R61 case 4b becomes structurally impossible, as the decision says.** In-place extension
is unaffected: the persistent top is still the persistent top.

**Two things Step 2 needs decided first:**
1. **ROUND-66's chunking** (next section) changes the shape: with chunks, "the end of the range" moves. The clean
   rule is that the scratch cursor lives in the **first** range only and persistent allocation moves on to new
   chunks; scratch exhaustion is then `kshetra purnam` as decided, and persistent exhaustion is a new chunk.
2. **The scratch fallback.** The decision says abort, never `mmap`; R62 §3.5 agreed. The message string and its
   place (outside the per-pack table, as R52 did) still need the owner's word.

## ROUND-66, answered

### Improvement 2 — chunking: what shipped, and what it would take

**Shipped (R65, before ROUND-66 was read): one 1 GiB `MAP_NORESERVE` reservation at the first `nirmmita`; on an
exhausted or refused reservation, today's per-call `mmap`.** That already has no fixed ceiling — exhaustion falls
back to the old allocator, never aborts — and the reservation costs one syscall per program, not one per 64 MB.

**ROUND-66 asked for something different:** a 64 MB `.bss` block, then a 64 MB `mmap` chunk at each exhaustion,
bumping continues in the new chunk. **The difference matters in one place: Windows.** `MAP_NORESERVE` has no
`VirtualAlloc` analogue, and a 1 GiB `MEM_COMMIT` charges the commit limit; 64 MB chunks are the call the adapter
already makes, far less often. **On Linux the shipped form is strictly better** (one syscall, no `.bss` load-time
risk — R60 measured a large `.bss` failing `execve` with no message).

**To add chunking to what shipped:** in the slow path, when the room is short, reserve a new chunk (64 MB,
`MAP_NORESERVE` on Linux) instead of falling to per-call `mmap`; per-call `mmap` only when the chunk reservation
itself fails. **~25 lines in `r65_emit_nirm`, about 40 more bytes at every `nirmmita` site**, a one-line change for
the Windows adapter once the owner builds it. In-place `kosh` extension cannot cross a chunk boundary, so a `kosh`
at the end of a chunk copies once. **I would build it together with Step 2**, since both touch the same slow path and
the bytes should change once. Not built this round.

### Improvement 1 — the measurement (`evidence-r67/kosh-alias-count.txt`)

646 `.sm`/`.smlib` files outside `tests/negative/`; 81 declare or take a `kosh`; **131 `kosh` declarations.**

| Question | Count | Where |
|---|---|---|
| **1. one `kosh` variable assigned to another** | **2 sites, 2 files** | `examples/252_r38_alias_kosh_oob.sm` (`w = v`), `examples/255_r42_alias_kosh_push.sm` (`w = v`) |
| **2. a `kosh` passed to a `prakriya`** | **162 call sites; the callee stores the parameter in 0 of them** | every one reads or pushes through the parameter; none keeps it |
| **3. a `kosh` stored in a `mala`, a `rachana` field, a `likh8` cell or another `kosh`** | **0** | — |
| **4. declarations unaffected by banning assignment** | **129 of 131** | the two files above hold one each |

**The two sites are not programs that happen to alias; they are the tests that pin aliasing as a feature.** `252`
is R38's *"a kosh alias via assignment must be bounds-checked like the original"*, `255` is R42's *"an alias of a
kosh is the kosh: `kosh_push` through it grows the original"*, with goldens. **So the answer to "is the fix free?" is:
in programs, yes — zero real uses; in the language, no — it reverses the R42 decision, and the two examples become
negative tests.** The compiler's `r38_mark_alias` (`src/sutram_compiler.asm:20897`) is the mechanism that would turn
into a refusal. **The number is in front of you: 2, both deliberate.**

## What I did not do

- No source change; `217` not fixed (one number, named above); Step 2 and chunking priced, not built.
- Not run: real Windows.
