# R169-00 — No memory comes back when a block ends: not a 200 MB `nirmmita` (kept, and reused by the next block - 2.4x faster the second time), and not a big `kosh` (kept, **and not even reused**: each dead one keeps its pages and its 64 MiB of address space). The only `munmap` in the compiler is on growth, never on death. The boundary is not 64 KB of data but **4,097 elements**: from there every `kosh` gets its own region.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra, unchanged
     measurement only - no code, document or gate changed; gates not re-run (last full run 81 PASS / 0 FAIL /
     1 NOT-RUN on 112838ce, Linux, Xvfb; since then only Claude-to-Sarvam/ and Sarvam's files changed)
     suite and crash corpus: unchanged since R167, not re-run · the guard: no compiler changed, identity
staged v316-ready 59d60353: unchanged, waiting on the owner's Windows run
```

## The method, what it includes, what it cannot show

- **Current RSS, not peak.** Each program prints a point number and waits on `grahan()` (a read from standard
  input). While it waits, `probe.py` reads `/proc/<pid>/status` - **VmRSS** (resident now), VmHWM (the peak so far),
  VmSize (address space) - and `Anonymous` from `smaps_rollup`, then sends `0`. Every number below is VmRSS of the
  program itself; the time is the work between two points, with no pause in it. Three to five runs each, empty
  environment; every run is in `evidence-r169/results.txt`, the programs in `evidence-r169/programs/`.
- **Pages are touched twice.** `nirmmita` inside a block already writes every byte - it zeroes the block with
  `rep stosb` (`r73_gen_scratch_nirm`, `src/r65_arena.inc`) - and the program also writes one word in every 4 KB page
  (`p[i * 512] = 1`, 48,828 pages). A `kosh` touches its pages as `kosh_kship` writes each element.
- **What it cannot show:** the moment between two points (a release and re-grab inside one stretch would be
  invisible - there is none in these programs), and memory the kernel accounts elsewhere (page tables).
- **A correction to my own R168.** I gave its baseline as 312 KB. The program's own VmRSS at its first point is
  **12-24 KB**; the 312 KB was `/usr/bin/time`'s size, carried through its fork - the same trap as the Python
  interpreter, smaller. R168's per-pass bytes are differences and stand; its "flat 312 KB" is a flat ~20 KB.

## WS1 - a big block, run once

| point | VmRSS (3 runs) |
|---|---|
| 1, before the block | 12-16 KB |
| 2, inside, 200,000,000 bytes allocated and touched | **195,328-195,332 KB** |
| 3, just after the block closes | **195,328-195,332 KB** |
| 4, at the end | 195,328-195,332 KB |

**Sample 3 equals sample 2. The memory is kept** - measured, as you expected. The address space (VmSize) is
1,048,808 KB from the start: the 1 GiB arena, reserved once.

## WS2 - the same block twice: the price of returning it

| | first pass | second pass | VmRSS after |
|---|---|---|---|
| two blocks, each `nirmmita(200000000)` + touch (5 runs) | 73-98 ms | **28-31 ms** | 195,332 KB - the second reuses the first's pages |
| the same without a block (two allocations, 5 runs) | 64-76 ms | 64-93 ms | 390,640 KB - twice |

**The second pass is about 2.4x faster: 74 ms → 30 ms (median runs).** The 30 ms is zeroing 200 MB and the touch
loop; the 44 ms difference is the first touch of 48,828 new pages - about **0.9 µs a page**. **That is the price of
the feature: a block that gave its memory back would pay those 44 ms per 200 MB every time it ran again.**

## WS3 - a big `kosh` that dies (the one that decides it)

A `kosh` grown to 2,000,000 elements (16 MB) inside a block:

| point | VmRSS |
|---|---|
| 1, before | 12-16 KB |
| 2, inside, grown | **15,676-15,680 KB** |
| 3, after the block | **15,676-15,680 KB** |

**It stays.** The release path is **narrower than `R127_BIG` suggests: it frees an old buffer on growth, never a
buffer on death.** And it is worse than "kept": run the same block twice and the second `kosh` does **not** reuse the
first's region -

| point | VmRSS | VmSize |
|---|---|---|
| after block 1 | 15,680 KB | 1,114,344 KB |
| after block 2 | **31,340 KB** | **1,179,880 KB** |

**A big `kosh` that dies in a block is lost: its pages and its 64 MiB reservation stay for the rest of the program.**
`nirmmita`'s memory is at least reused by the next block; a dead `kosh`'s is not reused by anything.

## WS4 - the boundary, tested: it is 4,097 elements, not 64 KB of data

`R127_BIG` is compared with the **new capacity** in bytes, and capacity doubles. So a `kosh` of 4,096 elements
(capacity 4,096, 32 KB) stays in the arena, and the 4,097th push doubles it to 8,192 elements = 65,536 bytes - a
region. **No `kosh` can hold "60 KB" in the arena:** 7,500 elements (60,000 bytes) already has a 64 KiB region.
Five blocks in a row, each growing a `kosh` and dying:

| elements | where | VmRSS added per block | VmSize added per block | `parimana()` added per block |
|---|---|---|---|---|
| 4,096 | arena | 32 KB | 0 | 32,832 |
| **4,097** | **a region** | 68 KB | **65,536 KB** | 98,368 |
| 7,500 (60,000 bytes) | a region | 92 KB | 65,536 KB | 98,368 |
| 8,960 (71,680 bytes) | a region | 104 KB | 65,536 KB | 163,904 |

**Neither side returns anything when the block ends** - so a 60 KB `kosh` and a 70 KB one behave the same. What
differs at the boundary is address space: below it, a dead `kosh` costs its bytes in the arena; from 4,097 elements,
each also costs a 64 MiB reservation that is never released. That is real behaviour a student can hit and nothing
documents. **And at scale:** 40,000 blocks, each growing a `kosh` to 4,096 elements and dying (32 KB live at any
moment), finish correctly with a peak of **1,748,864 KB** - 1.7 GB for 32 KB of live data (`w5.sm`).

## WS5 - which call is made, where, and what re-acquiring costs

| where | call | when |
|---|---|---|
| `src/r65_arena.inc`, `r127_emit_grow` | `munmap` (syscall 11) on the **old** region | only when a region `kosh` grows into a new region |
| the same, `.big` | `mmap(max(2 x new, 64 MiB), MAP_NORESERVE)` | a `kosh` whose new capacity is 64 KiB or more |
| `r73_gen_rewind` (a block's end) | **none** - it stores the saved mark into the scratch cursor | every way a block ends |
| `win/winrt_blob.asm:184` | `VirtualFree(..., MEM_RELEASE)` in place of `munmap` | the same old-region case |
| `win/winrt_blob.asm:312` | `VirtualFree(MEM_RELEASE)` of the 64 KiB OOM reserve | at exit only |

**No `madvise` anywhere** (`MADV_DONTNEED` or other), on either platform. **What re-acquiring would cost:** with
`munmap`, a new `mmap` (one syscall) and a fault on every page touched again; with `MADV_DONTNEED`, no new mapping,
but the same fault and a zero-filled page on every page touched again. Either way the dominant cost is the page
faults - measured above at ~0.9 µs a page, 44 ms per 200 MB - and the syscall is one per block. **So "return
memory" is one syscall per block plus a page fault per page on the next use.**

## The verdict

**Giving `nirmmita`'s memory back is not worth a marker: the next block already reuses it, and returning it would
cost 44 ms per 200 MB each time.** **A `kosh` (and a `mala`) dying in a block is the real gap:** neither returned nor
reused - 15.7 MB and 64 MiB of address space per dead 2,000,000-element `kosh`, 1.7 GB for 40,000 small ones. That
gap is worth closing; the numbers say "reuse or free what dies", not "give `nirmmita` back to the operating system".

## Not done

- **No code, document or gate changed** - as briefed. The chapter does not yet say that a dead `kosh`'s region is
  never reused, or that the region starts at 4,097 elements; both are sentences for a documents round.
- **Windows** - not needed, not run (the Windows calls are read, not measured).
