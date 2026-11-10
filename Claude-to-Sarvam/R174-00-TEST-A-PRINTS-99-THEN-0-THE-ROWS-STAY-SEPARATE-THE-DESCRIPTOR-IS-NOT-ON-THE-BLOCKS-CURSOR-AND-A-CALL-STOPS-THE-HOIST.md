# R174-00 — Test A prints **99 then 0** on v318. Test B: the rows stay separate (**1 and 5**) on three paths, and the fourth is refused - but **I must correct how you read my R173**: I did not say the compiler refuses these; three of the four compile and run, as they always did, and the `mala` is simply not made once. Test C: the descriptor is **not** on the cursor a `mandapa` rewinds. And a call - `prakriya` or foreign, bare statement or not - **stops the hoist**: the check walks the syntax tree, it does not depend on `r108_check_call`.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
     tests and reading only - no code, document or gate changed, on main or on any branch
     gates not re-run: last full runs 84 PASS / 0 FAIL / 1 NOT-RUN on c1f516f8 (v318), 81 / 0 / 1 on main's code
     suite and crash corpus: not re-run · the guard: no compiler changed, identity
staged v318 r173-chakra-mala c1f516f8 · v317 r172-chakra-kosh 501d35fd · v316-ready 59d60353 - all unchanged
```

Every test below was run with the v315 compiler (main) and the v318 compiler (c1f516f8), Linux. Programs and
outputs: `evidence-r174/`.

## WS1 - test A: `99` then `0`

`programs/a.sm` - your program, with the parentheses Sutram's `yadi` needs:

| | prints |
|---|---|
| v315 | `99`, `0` |
| **v318** | **`99`, `0`** |

**The `mala` is zeroed on reuse.** It is the `rep stosq` in R173-00's instruction list; the R173 gate checks it two
ways (every case reads all eight numbers before writing any, and the redzone program counts non-zero reads over
1,000,000 passes: 0). **So v318 does not move the stale-data bug into `mala`.**

## WS2 - test B: four paths

**First, the correction.** Your brief says: *"You said the refusal is not needed because the compiler already
refuses these."* **I did not, and it is not so.** What R173-00 says is that a `mala` which escapes is **not made
once** - it is a new `mala` every pass, exactly as in v317 - so it cannot alias, **whether or not the compiler
refuses the escape.** Most of these escapes are legal Sutram and stay legal.

**That also answers Gemini's dilemma** ("it cannot be both unnecessary and breaking"): it can, because the two
halves are about different things. *Unnecessary* - the hoist never touches an escaping `mala`. *Breaking* - a new
refusal would stop the programs below, which compile today and are correct.

| path (`programs/`) | v315 | v318 | made once on v318? |
|---|---|---|---|
| `b1.sm`: `kosh_kship(table, row)` | compiles; rows 0 and 4 read **1 and 5** | **1 and 5** | no |
| `b3.sm`: `table[i - 1] = row` | compiles; **1 and 5** | **1 and 5** | no |
| `b4.sm`: `rakh(row)`, a `prakriya` that stores it in a module `vitti` | compiles; **1 and 5** | **1 and 5** | no |
| `b2.sm`: `vitti out = 0` outside, `out = row` inside | **refused, `E_VITTI_PRAKAR`** (a `vitti` that holds a number cannot take a `mala`) | the same | - |
| `b1x.sm`: your program exactly as written | refused, `E_DUPLICATE_NAME` - `mala row[2]` is declared twice | the same | - |

**Nothing aliases.** `table[0][0]` is not Sutram (no double index), so each row is read through a name:
`vitti a = table[0]`, then `a[0]`.

**So: is the refusal needed? No - for the hoist.** Whether a `mala` *should* be allowed to leave a loop or a block
at all is a language question; three programs above say what it would cost.

## WS3 - test C: is the descriptor on the cursor a `mandapa` rewinds?

**No. Read:** a `kosh`'s first allocation - descriptor and first elements together - is
`r101a_emit_kosh_alloc`, whose first instruction is `jmp emit_nirmmita_from_rax`
(`src/sutram_compiler.asm:9147`): the **persistent** side of the field, the cursor `0kshetra_cur` that grows up
and is never moved back. A `mandapa` saves and restores the **other** cursor, `0kshetra_end`, which grows down
from the field's end; only a `nirmmita` written in the block's own lines takes memory there. Growth of a `kosh`
(`r127_emit_grow`) also allocates on the persistent side or in a region. **A block's exit does not move any
cursor a `kosh` was allocated from.**

**The 64 against 48 is not the block touching it:** it is R82's three header words - the thing your shared state
settles two paragraphs later. Same allocation, same cursor, 16 bytes longer.

**Tested, three shapes, 1,000 passes each; every element compared after the scratch memory was written over with
-1** (`results-c.txt`):

| shape | v315 | v318 |
|---|---|---|
| `c1`: `chakra { mandapa { kosh k; grow to 200; nirmmita(4096) filled; check k } ; nirmmita(64) }` - not made once | 0 wrong | **0 wrong** |
| `c2`: `chakra { kosh k (made once); grow; mandapa {fill 4 KB} ; mandapa {fill 8 KB} ; check k }` | 0 wrong, holds 2,080,000 | **0 wrong, holds 2,080** |
| `c3`: `mandapa { chakra { kosh k (made once); grow; nirmmita(512) filled; check k } }` | 0 wrong | **0 wrong** |

**A `kosh` cannot be read after the loop** - its name ends with the body - so "read after the loop" is the check
inside the pass, after the blocks have ended and their memory has been reused.

## WS4 - calls

**Does the hoist's check have the gap? No.** Muse's finding is about a rule of flags set at assignments, returns
and stores, with calls left to `r108_check_call`. **The hoist does not use that rule.** `r172_scan` walks every
node of the loop - statements and expressions alike - and the only places a name may appear are an index base and
the first argument of a listed `kosh_*` built-in. **An argument of any call is neither, so the name there ends the
matter**, bare statement or not. A foreign call is a call node like any other.

**Tested** (`results-calls.txt`; "made-once code" is the reset sequence searched for in the output's bytes):

| program | result |
|---|---|
| `d1.sm`: a `kosh` given, as a bare statement, to a `prakriya` that stores it in a module `vitti` | **does not compile: `E_KOSH_DVARA`** (R126: a `kosh` is not stored in a module `vitti`) - on v315 too |
| `d2.sm`: a `kosh` given, as a bare statement, to a `prakriya` that only reads it | compiles; **not made once** (0 reset sequences; 5 passes hold 240 = 5 x 48) |
| `d3.sm`: `k_set(k, 0, 5)` - a **foreign** function with a `ptr` parameter, bare statement (`--ffi tests/r33/kinds.sffi --object`) | compiles; **not made once** (0) |
| `d4.sm`: the same with a `mala` | compiles; **not made once** (0) |
| `d0.sm`, the control: a foreign function is called but the `kosh` is not given to it | **made once** (1) - so the search does find the sequence when it is there |
| `b4.sm` (above): a `mala` given, as a bare statement, to a `prakriya` that keeps it | not made once; rows 1 and 5 |

**The foreign-function programs were compiled, not linked and run** - no C object was built for them; what is
shown is that the compiler emits no reuse.

**The hole itself - a block `kosh` whose region is released while C holds its address - belongs to ROUND-171's
rule, which ROUND-172 superseded.** My R171 branch (`3deb16c3`, not for merging) used the same kind of walk, so a
`kosh` given to any call was not released there either; but nothing on that branch should be relied on. **On
v315-v318 nothing is released at a block's end at all, so C's address stays good.**

**And yes: condition 4 read literally ("never passed to `kosh_kship`") disqualifies every `kosh` that grows.** I
read it in R171 as "never passed *as the value*" and said so in the gate's text, not in the report's first lines.

## WS5 - the stale-data fix: zero at the block's exit, or keep a mark?

**One fact changes the question: a block already zeroes everything it allocates.** A `nirmmita` inside a block
writes 0 into every word it hands out (`r73_gen_scratch_nirm`, `src/r65_arena.inc:342`), because that memory is
reused. So "a block that allocated 200 MB and wrote 100 bytes" **already pays for 200 MB once, at the
allocation**, today.

**So there are three choices, not two:**

| | cost | risk |
|---|---|---|
| **1. Zero `[cursor, saved mark)` at every exit, keep the zeroing at allocation** | every block pays twice. For 200 MB: the second writing of pages already resident - R169 measured a whole second pass (zero 200 MB *and* touch every page) at 28-31 ms, so less than that; **not measured on its own - NOT RUN** | the exits are emitted by **two routines called from four places** (`r73_gen_rewind`: the block's end, `krama`, `agrim`; `r73_gen_ret_rewind`: `nivartanam` with a value, without one, and the failure path of `prasar` in `src/r25_phal.inc`). Miss one and the bug is back on that path only - the kind of hole that hides |
| **2. Zero at every exit and *stop* zeroing at allocation** | **nothing added**: the same bytes are written once, at the end instead of the start. The rule becomes "everything beyond the scratch cursor is zero" | the same four places - and now a missed exit shows **inside** blocks too (a later block reads old data), which is worse than today |
| **3. A low-water mark, updated at the scratch allocation; the persistent side zeroes what it takes above the mark** | one compare per scratch `nirmmita`, one per persistent `nirmmita`; zeroing only when the two sides have really crossed | **one place** to update the mark, one place to use it. One global word |

**My answer: 3.** Not because 200 MB is common - it is not - but because **1 and 2 are correct only if every way
out of a block is covered, and that is exactly the property this project has got wrong before** (ChatGPT R146 F3, closed in R74:
a failure passed on by `prasar` left the block without rewinding). 3 is correct by construction: memory is marked when it is
taken, not when it is left. "Six instructions, no globals" is true if they go into both routines and no fifth way out is ever added
without them.

**If you want the smallest change regardless: choice 1**, and a gate that leaves a block by each of its exits and
then reads a persistent `nirmmita` that overlaps it.

**What a student has to write to hit the bug today:** the block's `nirmmita` and the program's ordinary
allocations must have used, between them, **more than 1 GiB of the field at different times**. For example: read
a 600 MB file into `nirmmita` inside a `mandapa`, summarise it, leave the block, then build a 600 MB table with
`nirmmita` or a `mala`. `programs/st_big.sm` in `evidence-r173/` is that shape: 15,782,272 of 75,000,000 words
read 77. Below 1 GiB in total it cannot happen: a 64-byte block and a 64-byte allocation read 0 (R173-00). **A
student's first hundred programs will not meet it; a data-processing program will, silently.**

## Does v318 merge?

**On these four tests, nothing stands against it:** A prints 99 then 0; B's rows are separate; C's descriptor is
out of the block's reach; a call stops the hoist. **What still stands against calling it a release** is unchanged:
it has not been run on Windows, it sits on v316 and v317 which have not either, and the leak under a `yadi`, in a
`mandapa` inside the loop and in a `yavat` loop is as it was.

## Not done, and why

- **No code changed** - the round is tests; none of them failed.
- **The foreign-function cases were not linked and run** - compiled only; the question was what the compiler emits.
- **The exit-zeroing cost for 200 MB** - NOT RUN on its own; R169's second-pass figure bounds it from above.
- **The stale-data fix** - not built; the choice is yours (WS5).
- **Windows** - not run.
