# R180-00 — The arena already has two cursors. The floor is possible: it is a **fourth word** that splits one word's two jobs, and it costs one comparison at a block's `nirmmita` and nothing anywhere else. **But it gives the blocks their peak for ever** - whatever a block once used, the ordinary side never gets - and that brings a cliff nearer that I have now measured: past the field an allocation costs **3 µs and 4 KB instead of 30 ns and 64 bytes**. **So I am changing my recommendation: A, the zeroing as staged (v320), not the floor.** In R176 I chose the floor on cost alone, before reading what it needs. **And yes: 38 DIFFER is acceptable, and I say under which conditions it would not be.** Nothing built.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
     reading and measurement only - no code, document, gate or branch changed
     gates not re-run (last full runs: v319 4c1159be 85 PASS / 0 FAIL / 1 NOT-RUN; v319 + documents 12ef6329 85 / 0 / 1;
     v320 9bb059ea 86 / 0 / 1 - all Linux, Xvfb) · suite and crash corpus not re-run
     the guard: no compiler changed - identity
staged v319 r176-made-once-anywhere 4c1159be - UNTOUCHED · r179-v319-book 12ef6329 · v320 r176-block-exit-zero 9bb059ea
       · v318 c1f516f8 · v317 501d35fd · v316-ready 59d60353 - all unchanged
```

Sanskrit only; no pack touched; `backups/` untouched. The measurements below are with the v319 compiler (4c1159be).

## WS1 - the floor

### 1. What the arena looks like today: two cursors, not one

`src/r65_arena.inc:29-36` (R69, "one range, two opposing cursors"). **One reservation of 1 GiB, three words:**

| word | what it is | who moves it |
|---|---|---|
| `0kshetra_cur` | the ordinary side's cursor; starts at the bottom, **grows up**, never goes back | every ordinary `nirmmita`, `mala` and `kosh` (`r65_emit_nirm`, `r65_emit_kosh_extend`) |
| `0kshetra_end` | the block side's cursor; starts at the top, **grows down**, and goes back up when a block ends | a block's `nirmmita` lowers it; `r73_gen_rewind` and `r73_gen_ret_rewind` raise it |
| `0kshetra_sima` | the true end of the range | nobody, after the reservation |

**So a block's allocations and ordinary allocations do not share a cursor, and nothing has to be marked and
skipped.** The two sides are a stack at the top and a bump at the bottom, and they never interleave.

**The defect is that `0kshetra_end` has two jobs.** It is the block side's cursor, **and it is the ordinary
side's limit** - the ordinary side computes its room as `end - cur` (`:17`, `:33`). When a block ends, the cursor
goes back up, **and the limit goes up with it** - over memory the block wrote. The ordinary side does not zero
what it takes (`:23`: "memory from the arena is never reused, so it arrives zeroed"). That sentence stopped being
true in R73, when the second job was added.

### 2. When the block runs again

**It re-enters the same memory - today, and under the floor.** The block cursor returns to the top when a block
ends, so the next block takes the same addresses, and its own `nirmmita` zeroes what it takes (`r73_s6`). That
is why `nirmmita` in a block in a loop is flat, and none of it changes. **The leak you fear - each pass taking
fresh memory past the last - cannot come from the floor: the floor does not move the block's cursor at all.**

### 3. What the floor amounts to - named plainly

**Not a second cursor - the arena has two. It is a fourth word, and it splits `0kshetra_end`'s two jobs:**

- **`0kshetra_end` keeps one job: the ordinary side's limit. It only ever goes down.** It is the lowest address
  any block has ever taken - the floor of the blocks' region.
- **A new word - call it `0kshetra_agra` - takes the other job: the block side's cursor.** It moves down and up
  exactly as `0kshetra_end` does today.

**This is a real change to the arena, and this is what it changes:** today the field is one pool that the two
sides share over time - whatever a block gives back, either side may take. **Under the floor it is two regions
with a one-way boundary: memory a block has once used belongs to blocks for the rest of the program.** A block
may still push the boundary further down, as long as it does not meet the ordinary cursor; the ordinary side can
never push it back.

**Why it fixes the defect:** the ordinary side then only ever takes memory below the floor, and memory below the
floor has never been used by anything. Nothing needs clearing.

**What has to change, read from the code - five places, not two:**

| place | change |
|---|---|
| a block's `nirmmita` (`r73_gen_scratch_nirm`) | reads and writes the new word; and **three instructions more: `cmp rax,[end] ; jae .keep ; mov [end],rax`** - lower the floor when this block goes lower than any before |
| a block's entry (`r73_gen_scrcur`) | the mark is the new word - and **it must be given its first value here** (`if it is 0, it is sima`), because the code that reserves the field is in every program that allocates and cannot change without changing all of them |
| the two exits (`r73_gen_rewind`, `r73_gen_ret_rewind`) | store the mark into the new word instead of `0kshetra_end`. Same size as today |
| `parimana()` | counts the block side as `sima - end` today (`src/sutram_compiler.asm`, `.pm_arena`). `end` would no longer come back, so it would count dead block memory for ever; it must read the new word |
| the hidden words' registration (`r65_ensure_globals`, `r65_root_globals`) | a fourth word, registered only where a block's code is emitted - **except** that in `--separate` a root with modules defines the arena's words whether or not it allocates (`:137-139`), so **every `--separate` root with modules gains a word**, block or no block |

**The ordinary side's code does not change at all** - it goes on reading `0kshetra_end`. That is the whole trick,
and it is why the ordinary-way guard would show the same 38: of the 587 programs that compile, 38 contain a
`mandapa`, and the only two that call `parimana()` are among them (`evidence-r180/parimana-count.txt`).
**Outside the ordinary way, the `--separate` roots with modules would change too.** Read, not built.

### 4. The cost per allocation

| | today | under the floor |
|---|---|---|
| an ordinary `nirmmita`, `mala`, `kosh` | - | **nothing - the same instructions** |
| a block's `nirmmita` | - | **one comparison** (a load, a compare, a branch not taken; a store only when a block goes lower than any before) |
| a block's entry | - | one test (is the new word set yet?) |
| a block's exit | - | nothing |

**NOT MEASURED - nothing is built.** The nearest measurement is R176's patched program, where a dozen untaken
instructions at a block's exit made no difference that seven or twenty-five runs could show (5.5 ms against 5.5).

### The attack on it - what the floor costs that is not time

**The blocks keep their peak for ever.** If a block once used 600 MB, the ordinary side has 424 MB of the field
for the rest of the program, where today (and with the zeroing) it has the whole 1 GiB again.

**And past its limit the ordinary side does not stop - it falls off a cliff that already exists.** Every ordinary
allocation that does not fit takes the old path: its own `mmap` (`r65_emit_nirm`, `.mmap`). Measured with v319,
100,000 allocations of 64 bytes, and 100,000 calls of a `prakriya` that makes a `kosh`
(`results-past-the-field.txt`, `programs/`):

| | in the field | past the field |
|---|---|---|
| 100,000 x `nirmmita(64)` | under 0.01 s, peak 6,272 KB | **0.32 s, peak 399,872 KB** - 99,989 `mmap` calls |
| 100,000 x a `kosh` made in a `prakriya` | 0.02 s, peak 4,608 KB | **0.22 s, peak 399,872 KB** |

**About 3 µs and one whole 4 KB page for each small allocation - a hundred times the time and sixty times the
memory.** Nothing fails (no allocation returned 0, with `max_map_count` at its default 65,530 here); it is slow
and large, not wrong.

**So the three ways treat the same program - a 600 MB block, then 600 MB of ordinary data - like this:**

| | what the program gets |
|---|---|
| v319 | fast, the whole field - **and 126 MB of it holds the block's data** |
| **A, zeroing** | fast, the whole field, zeros |
| **B, the floor** | zeros; 424 MB at full speed, **then every further allocation at the cliff** |

**The programs the floor slows are exactly the programs the defect hits** - the ones whose blocks and ordinary
data have used more than 1 GiB between them. The floor makes them right and slow; the zeroing makes them right.

## WS2 - the choice

**I recommended the floor in R176 and I am withdrawing that.** I chose it there from one table of timings - it
was the row that cost nothing. I had not then read what it touches, and I had not measured where it sends a
program that outgrows it. **Having done both for this round, I choose A.**

| | A - zero at the block's exit (v320 as staged) | B - the floor |
|---|---|---|
| **built?** | yes: built, gates 86 / 0 / 1, measured | no |
| **places changed** | 2 routines, 1 new emitter (`r175_emit_zero_to_mark`) | 5 (the table above) |
| **new state** | none | a fourth word, with an owner in separately compiled programs and a first value to be set at a block's entry |
| **why it is right** | the cursor goes back in two routines only; zero there, and nothing unzeroed is ever given back | the ordinary side stays below a boundary that only moves down |
| **if it is wrong somewhere** | the stale read is back on that path - today's behaviour, no worse | the stale read is back; **or** a block's cursor is wrong - a false `kshetra purnam` or a block writing where it should not |
| **memory** | the whole field stays usable by both sides | the blocks' peak is lost to the ordinary side for ever; the cliff comes that much sooner |
| **time, a block of `nirmmita(64)` in a loop** | **8.9 ns a pass against 5.5** (measured build; no block at all: 27.7) | about 5.5 (not measured) |
| **time, a 200 MB block** | 20-27 ms more at its end | none |
| **behaviour of the 38** | 37 the same; the 38th reads 0 where it read 99 | all 38 the same - the 38th still reads 99 |
| **`--separate`** | untouched | every root with modules gains a word |
| **the sentence in the book** | "a block's memory is cleared when the block ends" | "what a block has once used stays the blocks'; the rest of the program has 1 GiB less that" |

- **Which is smaller? A.** Two routines against five places and a new word.
- **Which is safer? A.** It adds no state, it cannot make a block's cursor wrong, and it takes nothing away from
  any program. The floor's argument is just as sound, but it has more places to be implemented wrongly and one
  consequence - the lost memory - that no test would flag, because it is not an error.
- **Which would I rather maintain? A.** Its whole contract is one sentence at the two places memory is given
  back. The floor changes what the arena *is*, and everything written later about the arena has to know it.
- **What A costs is real and small:** 3.4 ns on the smallest block (it stays three times faster than no block),
  and a second pass over a large one. **If that second pass ever matters, R179's measurement is the answer, and
  it fits A, not B:** a discarded page reads 0, so beyond some size the exit can hand pages back with `madvise`
  instead of writing zeros over them - cheaper than the zeroing and it returns the memory. That is a later
  round's refinement of A's one routine.

**The one thing the floor does better is leave all 38 programs behaving exactly as before.** I do not think that
outweighs the rest, because the one program A changes is a deliberately wrong program (WS3).

### Is 38 DIFFER acceptable? My judgement: yes.

**The rule exists so that no working program changes by accident, and "by accident" is the word that matters.**
Byte identity is the cheapest complete proof that a change did only what it was meant to. This change is meant to
alter every block's exit. **Demanding 0 of it does not protect anything; it only forbids fixing the block.** A
rule that cannot tell a defect from its repair is measuring the wrong thing at that moment.

**What the rule's intent requires of a deliberate change, and what was shown for v320:**

| the intent requires | shown |
|---|---|
| the set that will differ is named **before** the run, by a test a script can make | "compiles and contains a `mandapa`" |
| the set that differs **equals** it - nothing outside, nothing inside left unchanged | 38 = 38, in every run: ELF and PE, against v319 and against v315 |
| every program in it is **run** old and new and compared | 37 identical in output and exit code |
| every change of behaviour is **explained one by one** | the 38th (WS3) |

**I would say no - 0 means 0 - in any of these cases:** a program outside the declared set differs, even one;
the set can only be described after seeing it; a program in the set changes what it prints and nobody can say
why in one sentence; or the change claims to add something and disturb nothing (v317, v318 and v319 each claimed
that, and each showed 0).

**And I would put it in the rule, not grant it once:** *"0 DIFFER outside the declared set. The declared set is
written down before the run and equals the differing set. Every program in it is run both ways, and every change
in what one prints is explained."* A waiver is forgotten by the next round; a rule is checked by it.

## WS3 - the 38th program

**It is corrected: on v320 (9bb059ea) the pin is 0** (`tests/r73_scratch/test_scratch.py:33`, with the reason
beside it; the program's header says the same), and gate `R73 scratch` passes there. **On v319 it asserts 99,
and v319 prints 99.** Nothing is asserting a value its own branch does not produce. **Nothing to fix.**

**Is 0 the right value? There is no right value - and that is the answer to your second question too. The fix
broke nothing legitimate.** The program (`tests/r73_scratch/blind_kosh_via_call.sm`, 12 lines):

```
mandapa { vitti buf = nirmmita(64) ; buf[0] = 42 ; kosh_push(k, adr(buf)) }    # adr() returns its argument
mandapa { vitti other = nirmmita(64) ; other[0] = 99 }
vitti p = k[0]
likha(p[0])
```

**It keeps the address of a block's buffer after the block has ended** - smuggled past the compiler through a
`prakriya` that returns it - **and reads through it.** The language gives that read no meaning; the README lists
it under what not to do. What it read was whatever lay at that address: on v319 the *second* block's 99 (never
the 42 it stored), on v320 the 0 the second block's exit left.

**So it was not "checking the bug", and I should stop letting that pass.** The stale-data defect is an *ordinary*
`nirmmita` or `mala` - a legitimate program - being handed dirty memory. This test is the opposite case: an
illegitimate program holding a dangling address. It was written in R75 to pin one fact - **the compiler lets
this through** - and its header says a future check that refuses it should fail the test. The printed number
only shows that the program ran. **Under the floor it would go on printing 99.**

## WS4 - v319 and the documents

- **v319 `4c1159be` is untouched.** Nothing was built on it or beside it this round.
- **Noted, not written: the sentence on `r179-v319-book` changes with whatever lands.**
  - **If A lands:** the "not cleared" point in §19 and the paragraph in both books come out, and v320's
    paragraph ("what a block gives up is zero", with its cost) is the text - with 8.9 and 5.5 in place of any
    figure from R175.
  - **If the floor lands:** they come out too, and the new sentence has to say two things - that a new buffer or
    `mala` always starts at zero, and that memory a block has once used is kept for blocks, so a program with
    large blocks has that much less of the field for everything else.
  - **Muse's words were not in the tree for either.**

## Not done, and why

- **Nothing built** - as asked. The floor's cost is read from the code and from R176's patched program, **not
  measured**.
- **The `--separate` consequence of the floor is read, not run.**
- **Windows** - nothing run. Past the field on Windows (a `VirtualAlloc` for each allocation): NOT RUN.
- **No gate run** - no tree changed.
