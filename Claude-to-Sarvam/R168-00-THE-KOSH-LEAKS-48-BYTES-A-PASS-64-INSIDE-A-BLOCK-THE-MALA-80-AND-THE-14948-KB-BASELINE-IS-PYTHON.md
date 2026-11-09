# R168-00 — A `kosh` made every pass leaks **48 bytes**; inside a `mandapa` it leaks **64** - the block makes it *worse*. A `mala` leaks **80**, block or not. At 800,000 passes that is 37.5 MB, 50 MB and 62 MB, against 0.3 MB for `nirmmita` in a block. And the 14,948 KB "baseline" is not the program: it is the Python process that started it. Under it, the first two rows of every table were invisible.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra, unchanged
     measurement only - no code, document or gate changed; gates not re-run (last full run: 81 PASS / 0 FAIL / 1
     NOT-RUN on 112838ce, Linux, Xvfb; this commit adds only Claude-to-Sarvam/ files)
     suite and crash corpus: unchanged since R167 (NO-EXPECTATION=4 PASS=327; 227 cases, 0 failed) - not re-run
staged v316-ready 59d60353: unchanged, waiting on the owner's Windows run (R167-00)
```

The guard: no compiler changed, so it is identity.

## WS6 first, because it changes every number: the baseline is the measurer

**Your 14,948 KB baseline is not the program's.** On Linux `ru_maxrss` is the high-water mark of the *process*, and a
process made by `fork` starts as a copy of its parent. Python's `subprocess` forks a ~13-15 MB interpreter, then
`exec`s; the high-water mark keeps the interpreter's size. So everything below ~14 MB reads as the baseline. Measured
the same way here (`run.py`, fork + exec + `wait4`), the empty program reads **13,380 KB**; with
`env -i /usr/bin/time -f %M`, whose parent is small, it reads **312 KB**. (Python's `os.posix_spawn` did not help: it
too reported ~13,800.)

| program, N = 200,000 | Python fork + `wait4` (as briefed) | `env -i /usr/bin/time` |
|---|---|---|
| A, `nirmmita`, no block | 13,380 KB | **12,416 KB** |
| C, a `kosh` every pass | 13,380 KB | **9,344 KB** |
| G, one `kosh` grown | 13,380 KB | **1,536 KB** |

**So under the fork method the 50,000 and 200,000 rows of A, C, D and G all read the same - the leak is hidden, not
absent.** The 800,000 row agrees under both methods because by then the program is larger than the interpreter.
Every number below is from `env -i /usr/bin/time -f %M` (3 runs each, identical), with the baseline stated: **312 KB**.
`parimana()` - the exact bytes held, from the same programs with one `likha(parimana())` added - is given beside it,
because it does not depend on pages or on who started the program. Wall times are best of five, `posix_spawn`,
including spawn (about 0.1 ms). All runs, all five times, all three methods: `evidence-r168/results.txt`; the programs
are in `evidence-r168/programs/`, made by `gen.py`.

## WS1 - C and D: a `kosh` every pass, without and with a `mandapa`

| N | C peak | D peak | C `parimana()` | D `parimana()` | C wall | D wall |
|---|---|---|---|---|---|---|
| 50,000 | 2,304 KB | 3,072 KB | 2,400,000 | 3,200,000 | 0.9 ms | 1.8 ms |
| 200,000 | 9,344 KB | 12,416 KB | 9,600,000 | 12,800,000 | 3.2 ms | 6.5 ms |
| 800,000 | **37,504 KB** | **49,920 KB** | 38,400,000 | 51,200,000 | 13.2 ms | 27.7 ms |

**Does D differ from C? Yes - and the other way from what one would hope: the block makes it a third larger and
twice as slow.** A program that makes a `kosh` inside a `mandapa` gives *every* `kosh` three more words for the
block-liveness check (R82), and checks them. The block reclaims none of it.

## WS2 - one leak, in bytes

From the peaks: C (37,504 − 9,344) KB ÷ 600,000 = **48.06 bytes**; D (49,920 − 12,416) KB ÷ 600,000 = **64.0**.
`parimana()` says exactly **48** and **64** per pass at every N.

**What it is: one allocation, descriptor and element buffer together, rounded up to 16.**
- C: a 32-byte descriptor + one 8-byte element = 40 → **48**.
- D: a 56-byte descriptor (R82) + 8 = 64 → **64**.

The arithmetic shows they are one allocation: as two, D would be 56 → 64 plus 8 → 16 = 80. And
`kosh a[1]` alone holds 48; the same `kosh` in a program that also makes one in a block holds 64 (`k1.sm`, `k2.sm`:
48, and 128 for two). **So: 40 bytes as you expected, plus 8 of rounding - nothing else is allocated. And 16 more when
any `kosh` in the program is made inside a `mandapa`, outside the block too.**

## WS3 - one `kosh`, grown

| N | peak | elements at the end (N x 8) | `parimana()` |
|---|---|---|---|
| 50,000 | 384 KB | 391 KB | 557,088 |
| 200,000 | 1,536 KB | 1,563 KB | 2,129,952 |
| 800,000 | **6,272 KB** | 6,250 KB | 8,421,408 |

**Peak is about the final size, not a multiple.** Keeping every intermediate buffer would be about twice the final
capacity (~16 MB at 800,000); nothing measured is near that. An outgrown region is given back (`munmap`) as it grows.
**But here the peak is not exact, and I will not pretend it is:** at 50,000 and 200,000 it reads *less* than the
elements alone (384 KB holding 391 KB of elements), which no real peak can. Linux updates the high-water mark lazily -
at an unmap and at exit - so for a program that unmaps as it goes, `ru_maxrss` can miss the moment just before an
unmap. At 800,000 it is within 1% of the elements; treat it as "about the final size", not as a figure to three digits.
`parimana()` is exact and counts **capacity**: 1,048,576 elements, 8,388,608 bytes, + the descriptor; 32,768 bytes of
it I did not trace (the early small buffers left in the arena are the likely part). Wall time at 800,000: **2.7 ms**. **Growth is not the problem.**

## WS4 - the `mala`

| N | `mala m[8]` every pass | the same inside a `mandapa` | `parimana()` (both) | wall (no block) |
|---|---|---|---|---|
| 50,000 | 3,840 KB | 3,840 KB | 4,000,000 | 1.3 ms |
| 200,000 | 15,616 KB | 15,616 KB | 16,000,000 | 5.2 ms |
| 800,000 | **62,464 KB** | **62,464 KB** | 64,000,000 | 20.8 ms |

**80 bytes a pass** - eight numbers and the length word, 72, rounded to 80 - **the same with a block**. It is the
largest of the three, as you expected.

## WS5 - the table

| Allocation kind, one per pass | Leaks in a loop? | Leaks inside a `mandapa`? | Bytes per pass | Peak at 800,000 (baseline 312 KB) |
|---|---|---|---|---|
| `nirmmita(64)` | yes (64) | **no** - 312 KB, flat | 64 / **0** | 49,920 KB / **312 KB** |
| `kosh temp[1]` | yes (48) | **yes, and more (64)** | 48 / **64** | 37,504 KB / **49,920 KB** |
| `mala m[8]` | yes (80) | **yes (80)** | 80 / **80** | 62,464 KB / **62,464 KB** |
| one `kosh` grown to N | no - bounded by its size | - | - | 6,272 KB (final size) |

Speed, at 800,000: `nirmmita` 15.3 ms without a block, **3.3 ms** with (4.6x - your 4.9x, near enough); a `kosh`
13.2 ms, 27.7 ms in a block; a `mala` 20.8 ms either way.

## The verdict

**On these numbers, reclaiming a `kosh` or a `mala` made in a block is worth building: they leak 48-80 bytes a pass,
the block reclaims none of it - for a `kosh` it adds 16 - and 800,000 passes cost 37-62 MB where `nirmmita` in a block
costs nothing.** Whether that should be a new `~` marker or `mandapa` itself reclaiming what is made in it is a
design question these numbers do not answer; they say the gap is real, and it is the size of one small allocation per
pass.

## Not done

- **No code, document or gate changed** - as briefed. The gates were not re-run for a commit that adds only this
  folder's files.
- **The chapter** says the block gives back `nirmmita` only (R166); it does not say that a block makes every `kosh`
  16 bytes larger. That is a sentence for the next documents round, not this one.
- **Windows** - not needed, not run.
