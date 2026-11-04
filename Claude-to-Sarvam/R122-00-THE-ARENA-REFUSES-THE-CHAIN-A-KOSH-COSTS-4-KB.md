# R122-00 — The arena branch refuses `chain40_reuse.sm` (and every chain from 32 up), as main does. Merged, it would change one program's output on main (318, the right way) and one program's bytes. A `kosh` costs one 4 KB page plus 8 bytes a number - and 64 MiB of address space, which is not free: under a 1 GiB address limit the 16th `kosh` crashes the program. With the arena, the region return is moot. Not merged.

- **Commit on `main`:** `c494dfd` (documentation and evidence only; main stays v298).
- **The branch:** `claude/r108-arena-review` at **`3a6292e`**, **not merged** (Sutram v290). I rebuilt its compiler from its source: **byte-identical to the binary committed there.**
- **Suite, gates, guard:** not re-run for this round (no code changed); R121's are current.

## WS1 - the arena, re-run

**1. `chain40_reuse.sm` on the branch: refused.** `Sutram Error [E_KOSH_MANDAPA]` (the branch predates v294's `truti`), **as on main** (`Sutram truti [E_KOSH_MANDAPA]`). The same holds for the 32-, 33- and 40-link chains. `ok_chain120.sm` (a 120-link chain that does not keep the `kosh`) compiles and prints 11 on both (`evidence-r122/ws1-chain-and-what-merging-changes.txt`).

**2. What merging would change - measured two ways.**

**(a) Against its own base** (main `416637b`, v289, the commit it was cut from): **every one of the branch's 685 programs**, compiled by both, each in its own tree, ELF (`evidence-r122/branch-vs-its-base.txt`, the script beside it):

| | programs |
|---|---:|
| identical bytes | **554** |
| refused by both | 125 |
| different bytes, **same output and exit** | **2** - `examples/286`, `299`: the two that make a `kosh` inside a `mandapa` |
| refused by the branch only | **1** - `examples/316` (the outlives rule; **main has refused it since v291**) |
| new on the branch | 3 (its own examples 318-320) |
| **different output or exit** | **0** |

**(b) On main today: the arena touches only programs that make a `kosh` inside a `mandapa`. On main that is 6 of 712:**

- **4 are refusals already** (287, 316, 320, 321) and stay refusals.
- **`286` runs** and prints the same (385 / 338350).
- **`318_r108_parimana_moves` prints a different number**, run on the branch with the names translated back to v290's: `and a kosh of 8 in it` **288 → 296**, `after the block` **176 → 72**.
  - **The new output is the right one for the arena:** the block's `kosh` is given back when the block ends, so `parimana()` falls back to what the program holds outside it (72, the outer `kosh` of capacity 4).
  - The 8 more inside the block (296, not 288) is how the branch counts the slot; I measured it and have not traced it.
  - **Its golden would be re-recorded, deliberately.**

**So: 1 program changes output, 1 changes bytes only, 0 others.**

**And what merging costs** (R115's list stands):

- the branch is **eight versions behind** (v290 → v298), in the same file, so it needs a full port, not a merge;
- **it is not the design R178 accepted** (stable descriptors); it refuses every second name for a block `kosh`;
- **the R101 memory gate's "not reclaimed" result flips** - which is the point.

**Muse attacks it next, as you ordered.**

## WS2 - what a `kosh` costs, measured

**Main v298, Linux ELF; `/proc/PID/status` read while the program waits at its end** (`evidence-r122/ws2-kosh-cost.txt`, the script beside it). N koshes, each made in a loop pass (its region is kept for the program's life), with E numbers pushed into each:

| koshes | numbers each | address space (VmPeak) | resident peak (VmHWM) | per `kosh`: address / resident |
|---:|---:|---:|---:|---|
| 1 | 1 | 64 MiB | 40 KB | 64 MiB / 8 KB |
| 10 | 1 | 640 MiB | 76 KB | 64 MiB / 4.4 KB |
| 100 | 1 | 6.3 GiB | 432 KB | 64 MiB / 4.0 KB |
| **1000** | 1 | **62.5 GiB** | **4.0 MB** | 64 MiB / **4.0 KB** |
| 1000 | 100 | 62.5 GiB | 4.0 MB | 64 MiB / 4.0 KB |
| 1000 | 10,000 | 62.5 GiB | 80 MB | 64 MiB / 80 KB |

**The number a student can hold:**

- **A `kosh` costs one page, 4 KB, plus 8 bytes for every number it has ever held, rounded up to pages** (10,000 numbers: 80 KB).
- **It never moves while it holds fewer than 8,388,603 numbers.**
- **What it does not cost is memory:** the 64 MiB is address space, reserved (`MAP_NORESERVE`), not committed.

**But the address space is not free - I found a defect measuring it.** Under an address-space limit (`ulimit -v`, common on shared and CI machines), the program **crashes**:

| `ulimit -v` | a `kosh` per loop pass, 40 passes |
|---|---|
| unlimited, 4 GiB | all 40, exit 0 |
| **1 GiB** | **15, then SIGSEGV** (exit 139) - no message |
| 256 MiB | 3, then SIGSEGV |

- **The region's `mmap` failure is not checked**, and the program writes through the error value.
- The arena's own reservation failing *is* caught: `kshetra purnam - mandapa-smritih samapta`, exit 1.
- **Not fixed - this round is answers. It is new:** the tree has R101's note on `nirmmita`'s large maps, not this.

**Can the reservation be smaller? Yes, but the reservation *is* the never-move limit:** `R101A_MAXCAP = (R101A_REGION - 40) / 8`.

| region | a `kosh` never moves up to | 1000 koshes take | under a 1 GiB limit (64 MiB measured; the rest computed) |
|---|---:|---:|---|
| **64 MiB (today)** | **8,388,603** numbers | 62.5 GiB | 15 koshes |
| 16 MiB | 2,097,147 | 15.6 GiB | ~60 |
| 4 MiB | 524,283 | 3.9 GiB | ~250 |
| **1 MiB** | **131,067** | **1 GiB** | ~1,000 |

**What 1 MiB would break:** nothing that works today, for a `kosh` of up to 131,067 numbers. **Past that, the `kosh` takes the old relocating path** (R101A's fallback), so **a second name to it goes stale again** - the alias defect R101A closed, reopened for big collections only. The resident cost is the same at every size.

**My answer:**

- **The 64 MiB is not what makes memory invisible; the missing failure check is.** Fix that first: refuse with a message, or fall back to the relocating path when the reservation is refused. Then the student's rule is the one above.
- If you want the address space small too, **1-4 MiB with the never-move limit stated** is defensible; 64 MiB only matters for a single collection past half a million numbers.
- **Not built.**

## WS3 - with the arena, is the region return needed?

**No - the arena makes it moot.**

- **A block's `kosh` lives in the block's arena, and the block gives the arena back when it ends.** Measured with each `kosh` inside a `mandapa` (the same table's programs, 1000 blocks with a 10,000-number `kosh` each):
  - **main: 63.5 GiB of address space, 80 MB resident, and growing with every block;**
  - **the arena branch: 1.0 GiB (the arena's fixed reservation) and 0.3 MB, flat.**
- **The region return was only ever about block koshes.** A `kosh` outside a block lives as long as the program on both designs.

## Not done, and why

- **The merge:** not this round, as you said - Muse's attack first.
- **The region-failure crash, and a smaller region:** found and costed, not built.
- **Threads (your gap 5):** not in this round's questions.
- **Windows:** the branch is Linux-only as main's regions are; no PE measurements.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the packs, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`, and the arena branch itself.
