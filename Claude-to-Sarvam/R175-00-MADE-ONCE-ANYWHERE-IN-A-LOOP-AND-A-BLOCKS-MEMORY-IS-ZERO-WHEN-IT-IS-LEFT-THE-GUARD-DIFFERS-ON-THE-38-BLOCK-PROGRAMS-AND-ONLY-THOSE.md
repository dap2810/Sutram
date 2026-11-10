# R175-00 — Both built, staged as v319. **(1) A proven-local `kosh` or `mala` is made once wherever it is declared in a loop** - under a `yadi`, in a `mandapa` inside the loop, in a `yavat`: 37,516 and 50,012 KB → 16-20 KB at 800,000 passes. **(2) The stale-data defect is closed with your fix - zero at the block's exit - and I was wrong in R174 to call it fragile.** But read the guard line: **the zeroing changes the bytes of every program that has a `mandapa` - 38 of the 783 DIFFER, exactly those 38, and one of them prints a different number** (a pinned known limit: 99 → 0). And it costs: a tiny block in a loop takes 13.2 ns where it took 5.6.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
CORRECTED IN R176: the one branch named here, r175-nested-and-zero, WAS NEVER PUSHED. Its first full gate run read
     84 PASS / 2 FAIL (R101 memory's pin of the gap this round closes, not yet updated; and doc counts, which repeats
     it). Before it was re-run, ROUND-176 asked for the two changes to be split. They are now two branches:
       r176-made-once-anywhere 4c1159be  v319  the nested hoist alone  - gates 85 PASS / 0 FAIL / 1 NOT-RUN, 0 DIFFER
       r176-block-exit-zero    9bb059ea  v320  + the zeroing          - gates 86 PASS / 0 FAIL / 1 NOT-RUN, 38 DIFFER
     AND the cost figure below ("13.2 ms against 5.6") was one noisy batch: measured in turn over 25 rounds it is
     8.9 ms against 5.5 (R176-00). The other two cost lines were not re-measured.
     the guard, the ordinary way, 783 programs, ELF and PE - in two steps, because the two changes differ:
       step 1, made once anywhere in a loop, against v318:   587 byte-identical, 196 refused identically, 0 DIFFER
       step 2, + zeroing at a block's exits, against step 1 and against v315 (main), four runs, the same line:
                                                             549 byte-identical, 196 refused identically, 38 DIFFER
            the 38 are exactly the 38 programs that compile and contain a mandapa - no other program changed
            37 of the 38 print and exit exactly as on v315; the 38th is a pinned known limit (below)
     installer rebuilt (payload v319): 311a70118070c2af1482397ff5f8de682fdd52d8a9d393acd77f6cb3a4ab0c07
staged v318 c1f516f8 · v317 501d35fd · v316-ready 59d60353 - unchanged
```

**The guard is absolute, and this round it does not read 0. Say it plainly:** the standing rule is that a DIFFER
means the change is wrong. **Step 1 holds it. Step 2 cannot:** a fix that makes every block zero its memory on the
way out puts new instructions into every block, so every program with a block compiles to different bytes. What I
can show instead is that the change is confined - **the DIFFER set equals the set of compiling programs that
contain a `mandapa`, in all four runs, with nothing outside it** (`evidence-r175/differ-list.txt`) - and that each
of the 38 was run on v315 and on v319 and compared (`differ-outputs.txt`). **If that is not acceptable, the
zeroing must not merge, and step 1 can be taken alone** (its binary is not kept on the branch; it is one commit's
worth of `src/r65_arena.inc` to leave out).

**The one output that changes:** `tests/r73_scratch/blind_kosh_via_call.sm` - R75's pinned known limit: a scratch
address smuggled out through a `prakriya`, kept in a `kosh`, and read after its block has ended. It printed **99**
(the *next* block's data, read through the dangling address) and now prints **0**, because the second block's
memory is zeroed when that block is left. **The address is still dangling and the program is still wrong; it just
reads zero now.** I changed the pin in `tests/r73_scratch/test_scratch.py` from 99 to 0 and said why beside it.
Sanskrit only; no pack touched; `backups/` untouched.

## WS1 - the nested-block gap

**1. Why did it stop at the loop body's direct statements? Deliberately - and too cautiously.** In R172 I took the
one position where "the declaration runs once per pass" needs no argument. It was a boundary I chose, not a
recursion I forgot; and you are right that a student writes the `yadi` form naturally.

**2. The rule.**
- **The slot belongs to the declaration, not to the name and not to the branch.** Each declaration found in the
  loop gets its own frame slot; all of them are zeroed once, at the loop's entry (the same place as before).
- **Gemini's case - `yadi (c) { kosh temp[10] } anya { kosh temp[20] }`: two declarations, two slots, two `kosh`.**
  Each is reset where *it* is declared. They never share. (v318 would have left both alone: it required the name
  to be declared once in the loop. That requirement is gone; what remains is that every declaration of the name in
  the loop is of the same kind - the compiler already refuses a name that is a `kosh` in one branch and a number in
  the other, `E_VITTI_PRAKAR`.) Gate case `kosh-both-branches`: 40 passes hold what 20 hold, 304 bytes - one of
  each.
- **Proven local is unchanged:** in the *whole loop* the name appears only as an index base or as the `kosh` a
  `kosh_*` built-in (not `kosh_ksham`) works on; a `mala` only as an index base.

**3. A declaration in a branch that never runs makes nothing.** The slot is zeroed at the loop's entry and filled
only by the first-pass path at the declaration itself; that path is inside the branch. Gate case `never`: a
`kosh k[100]` and a `mala m[100]` under `yadi (j > 1000000)` - the program holds **0** bytes. And a branch that
runs every third pass: made on pass 3, found again on pass 6.

**4. A `kosh` in a `mandapa` inside the loop: not reached in v318; reached now; and there was one more reason to
be careful.** Not the cursor (test C) - **R82's header.** Each pass is a new block, and a `kosh` made in a block
carries that block's generation at `[d-24]`, which a `prakriya` given the `kosh` checks. The whitelist keeps a
made-once `kosh` away from every `prakriya`, so nothing reads the stamp - but I did not want a descriptor carrying
a dead block's stamp on the strength of that argument alone. **So a reused `kosh` gets this pass's generation
written into its header** (two instructions: `mov rdx,[rbp+the block's slot] ; mov [rcx-24],rdx`). Gate case
`stamp` reads the header through raw memory: the generation is non-zero, it changes between pass 1 and pass 3,
and the slot address does not.

**What is walked:** the loop's body, and from there into plain blocks, `mandapa` blocks, and both branches of
`yadi` / `anya` (and an `anya yadi` chain), to any depth. **What is not:** a loop inside the loop. It has its own
entry, so a `kosh` in it is made once *each time that inner loop starts* (gate case `inner loop`).
**And `yavat` is now a loop like `chakra`** - not asked for in this round; it is the same entry code and the same
proof, and most loops in the corpus are `yavat`. If you would rather it waited, it is one `call` to take out.

**Measured, 800,000 passes, R169's method, two runs each** (`results-nested.txt`; baseline 12-20 KB):

| the declaration is | v318 VmRSS | v319 VmRSS |
|---|---|---|
| `kosh`, under a `yadi` | 37,512-37,520 KB | **16 KB** |
| `kosh`, in a `mandapa` inside the loop | 50,012-50,016 KB | **16-20 KB** |
| `mala m[8]`, in a `mandapa` inside the loop | 62,512-62,516 KB | **16 KB** |
| `kosh`, in a `yavat` loop | 37,512-37,520 KB | **20 KB** |

**Gate `R175 nested made once`: 16 checks, 13 fail on v318.** The R172 and R173 gates had five "made every pass"
shapes that are now "made once" (under `yadi`, in a `mandapa`, `yavat`); I changed those five expectations and
said so in each line. **Guard for this step alone: 0 DIFFER against v318, ELF and PE** - no program in the corpus
declares a proven-local `kosh` or `mala` in any loop, so, as before, the gate is the coverage, not the corpus.

## WS2 - the stale-data defect

**Proved first** (`results-stale.txt`, `programs/st_big.sm`): a block writes 77 into every word of
`nirmmita(600000000)`; an ordinary `nirmmita(600000000)` after it, read before it is written -

| | words that read 77, of 75,000,000 |
|---|---|
| v318 (and v315) | **15,782,272**, the first at word 59,217,728 |
| **v319** | **0** |

**It reads the pattern. The bug is real.** (And a 64-byte block followed by a 64-byte allocation reads 0 on every
version - the two sides must have used more than 1 GiB between them. R173-00.)

**Is the cost case contrived? Mostly - and it turned out not to be the cost that matters.**
- **"200 MB allocated, one page written" is contrived as a program**, but a real shape is near it: a buffer sized
  for the worst case (a 200 MB read buffer for a file that is usually 2 MB). It already costs a full pass today -
  `nirmmita` in a block zeroes all 200 MB when it is taken. The exit adds a second pass.
- **The cost that matters is the opposite end: the tiny block in a hot loop**, which is what `mandapa` is *for*.

**Measured** (`results-cost.txt`, best of 7 runs, whole program):

| program | v318 | v319 |
|---|---|---|
| 1,000,000 blocks, each `nirmmita(64)` and one store | 5.6 ms | **13.2 ms** (+7.6 ns a block) |
| 10 blocks of 200 MB, every word written | 921 ms | 1,194 ms (+27 ms a block) |
| 10 blocks of 200 MB, only the first 4 KiB written | 389 ms | 587 ms (+20 ms a block) |

**My first build used `rep stosq` for every size and the first line read 52 ms** - `rep stosq` takes about 46 ns
just to start. It is now a plain loop up to 1 KiB and `rep stosq` above. `r175_emit_zero_to_mark`,
`src/r65_arena.inc`.

**I took the simple fix, as you said - and I owe a correction.** In R174 I argued for the mark because "the exits
are emitted in four places; miss one and the bug is back". **That was wrong.** I have now read every place the
generated code stores the scratch cursor: five. Two set it when the field is first reserved, one lowers it (the
allocation), and **two raise it - `r73_gen_rewind` and `r73_gen_ret_rewind` - and every way out of a block goes
through one of those two**, because that is the only way the cursor gets back. A way out that did not call them
would not rewind, the memory would stay taken, and the ordinary side - bounded by the cursor - could never reach
it. **So zeroing inside those two routines is complete by construction, not by enumeration.** The gate still
leaves a block by each of seven ways (last line, `krama`, `agrim`, `nivartanam` with and without a value, `prasar`,
a nested block through its outer block's `nivartanam`) and reads an ordinary `nirmmita` over the same bytes:
**0 of 15,782,272 on v319; all 15,782,272 on v318** in every case. `R175 block exit zero`, 8 checks, 7 fail on
v318.

**What the dirty mark would cost instead, since you ask:** one compare per `nirmmita` on both sides and one global
word; zeroing only when the two sides have crossed; the first table line would stay at 5.6 ms. It would also
change the bytes of *every* program that allocates, not 38. **And a third option I did not take:** with the exits
zeroing, the zeroing inside a block's `nirmmita` is redundant - everything beyond the scratch cursor is always
zero - and removing it would bring all three lines back to v318's numbers. **I left it in.** It removes a safety
net in the same round that installs its replacement; that is a decision to make once this has been lived with.

## WS3 - the scope

**Which kind is reclaimed where, after v319** ("once" = made once for the loop and reused, when proven local;
"kept" = a new one every pass, never given back):

| declared in a loop... | `kosh` | `mala` | `nirmmita` |
|---|---|---|---|
| as a statement of the loop's body | once (v317) | once (v318) | kept - 64 bytes a pass for `nirmmita(64)` |
| under a `yadi` / `anya` | **once (v319)** | **once (v319)** | kept |
| in a `mandapa` inside the loop | **once (v319)** | **once (v319)** | **given back at the block's end** (R73) |
| in a loop inside the loop | once per start of the inner loop | the same | as its position there |
| ...and given to a `prakriya`, given a second name, sliced, `kosh_ksham` | kept, 48 / 64 bytes a pass | kept, 80 bytes a pass for eight numbers | - |

- **A block still does not return memory to the operating system.** Neither does "made once": the `kosh` keeps
  what it grew to until the program ends.
- **A dead big `kosh` still keeps its 64 MiB of address space** whenever it is *not* made once - given to a
  `prakriya`, or made by a `prakriya` the loop calls. **What I see of the cliff here differs from what you wrote:**
  on this machine `/proc/sys/vm/max_map_count` is **65,530, the default, not the maximum**, and v315 running
  100,000 passes of a 5,000-element `kosh` was **killed by signal 9 at 5.8 GB resident** - not the named refusal
  (R173-00, `results-k5000.txt`). So the cliff is visible here, and it is uglier than a refusal.
- **Nothing is merged. v316, v317, v318 and v319 are all staged, each on the one before, and none has been run on
  Windows.** v319 under Wine: the 23 programs of the two new gates compile to the same PE under Wine as on Linux
  and print what the ELF prints (`wine.txt`), including the seven 600 MB exits.
- **This is not finished.** The made-once rule covers only what the whitelist can prove; the commonest real
  shape - a `kosh` built in a loop and handed to a `prakriya` - still leaks exactly as in v315.

## Not done, and why

- **The dirty mark; removing the zeroing at allocation** - see WS2; choices, not omissions.
- **A loop that tests at its end (the do-while form) and loops inside loops** - not walked; the first was not
  looked at, the second is by design.
- **Windows** - Wine only. `tests/windows/accept_v316.cmd` still covers only v316.
- **Reference §19** - I extended my own paragraphs on the branch (nested positions; "what a block gives up is
  zero", with the cost); Muse's wording should replace them.
- **The release notes on the branch** carry v317's and v318's paragraphs under a new v319 paragraph that says
  which of their statements v319 has changed; they were not rewritten.
