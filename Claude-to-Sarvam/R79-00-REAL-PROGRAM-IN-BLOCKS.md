# R79-00 — A real program in `mandapa` blocks

**Verdict: the block sells itself.** I wrapped the three allocating functions of a real 185-line program in a block
and changed nothing else. Memory fell from 185 MB to 110 MB, and the program got about 5% faster. With the
library's own temporaries in blocks too, memory falls to **7 MB**, which is the program's data and nothing more.

- **Commits, compiler, numbers:** as `R77-00-BYTES-CELLS-SILENT-DROPS.md` — **v275**, crash corpus 227/0, suite
  244, library proofs 228/228, properties 86/86, guard pages 5/5, gates 55/0/1 (Linux, Xvfb; new gate
  **`R79 real`**), guard v273 → v275 on all three paths, all 35 DIFFER same output and exit code.

## WS1 — the program, twice

**`tests/r79_real/report_plain.sm`: a class marks report, 185 lines, written the natural way.** It reads N students
from stdin (roll number and three marks). It computes totals and grades, and per-subject mean, **median** (from a
sorted copy), lowest and highest. It prints a histogram of totals in 10 bins and the grade counts, then **every
student ranked by total** (a recursive merge sort), in aligned columns. The allocations are where anyone would put
them:
- the column printer `stambh` makes a 32-byte buffer for each number it prints;
- each merge step makes a temporary array;
- each median makes a sorted copy.

**`tests/r79_real/report_blocks.sm` is the same file** with the bodies of those three functions (`stambh`,
`milan`, `madhyaka`) inside `mandapa { … }`.

**Both print exactly what an independent Python implementation prints** (`tests/r79_real/reference.py`): 29 lines
for 12 students, and **100,017 lines for 100,000 students, byte for byte.**

**Measured on 100,000 students, 7 interleaved runs, medians** (`evidence-r79/measurement-100000.txt`):

| | peak memory | | time |
|---|---|---|---|
| **no block** (the library as shipped) | **184,704 KB** | 100% | 1.11 s |
| **blocks in the program** (the library as shipped) | **110,208 KB** | **60%** | 1.05 s |
| no block, the library with R76's patch (its own temporaries in blocks) | 81,536 KB | 44% | 1.01 s |
| **blocks in the program and the library** | **7,040 KB** | **3.8%** | 1.01 s |

**7 MB is the data itself:** six arrays of 100,000 numbers are 4.8 MB, plus the empty process. Everything else the
program allocated was temporary, and the blocks gave all of it back.

**Time:** about 5–9% faster with blocks, which is within the spread of the runs. A report that prints 100,000 lines
is dominated by printing, so this is not a speed claim; the memory figures are.

**Where the other half went in row 2:** `roop_ank`, which turns a number into text, makes a 176-byte buffer of
its own on every call. A block in the *caller* cannot reclaim it, because a block reclaims only the `nirmmita`
written inside it. The library's temporaries are about 103 MB of row 2's 110 MB (110,208 − 7,040 KB). The R76 patch puts that buffer in a block inside `roop_ank`,
and row 4 is the result. **That patch is still not landed; this is the number that says it should be.**

## WS2 — the friction: none

The whole change is `plain-to-blocks.diff` (`evidence-r79/`): `mandapa {`, one more level of indentation, and `}`,
in three functions.
- **Did any allocation have to move?** No.
- **Did a variable have to be hoisted out of the block?** No. `stambh` returns its digit count, a number, from inside
  the block. `milan` copies the merged numbers from the scratch `tmp` back into the caller's `idx`, which is allowed
  because data may leave a block. `madhyaka` returns `copy[...]`, which is data.
- **Did anything become illegal?** No. It compiled the first time, and the escape check refused nothing.
- **What made it easy:** this is the shape the block was designed for. Each allocation is temporary, lives inside one
  function, and only numbers leave it. A program that kept an address from a scratch buffer, for example returning
  `tmp` itself, would be refused, and would then need restructuring.
- **The one friction is not in the program.** Half of the savings needs the library to use blocks too, and the
  programmer cannot add those.

## WS3 — the plain statement

**On this program, the block needed no restructuring.** Wrapping three function bodies cut memory by 40%. With the
library's temporaries in blocks too, it cut memory by 96%, with the same output and slightly less time.

`tests/r79_real/test_real_program.py` (gate **`R79 real`**) keeps this true on every compile. At 20,000 students it
checks that both versions match the Python reference, and that the block version stays under 75% of the plain
version's memory (it measures 62%).

## What I did not do

- **The R76 library patch is still not landed.** It is the difference between 60% and 3.8% here, and it is your
  decision: it changes the binary of every program that uses six library modules.
- **I wrote one real program, not two different ones.** It covers sorting, statistics, a histogram and formatted
  output. A program that keeps addresses (a tree, a graph) is the case where the block would refuse, and I did not
  write one.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs.
