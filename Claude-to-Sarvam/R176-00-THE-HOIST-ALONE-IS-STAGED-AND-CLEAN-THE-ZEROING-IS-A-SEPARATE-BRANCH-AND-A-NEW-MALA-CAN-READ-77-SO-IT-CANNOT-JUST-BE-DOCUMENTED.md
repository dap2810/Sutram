# R176-00 — Split. **v319, "made once anywhere in a loop", is staged alone: 0 DIFFER, gates clean, faster in every nested shape, costs nothing.** The zeroing is its own branch on top (v320), not ready. For the decision: **(a) the cost is 3.4 ns a block, not 7.6 - my R175 figure was a noisy single batch; (b) it is still far faster than no block at all, 8.9 ms against 27.7; (c) all of the cost is the second zeroing, and zeroing *only* at the exit costs 0.8 ns; (d) "document it" does not hold: a newly declared `mala m[8]` reads 77.** And the 38th program is a test, not an example, and it went 99 → 0, not the other way.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r176-made-once-anywhere 4c1159be  Sutram 1.0 (v319) - sampurna sutra  (on r173-chakra-mala c1f516f8; NOT merged)
     crash corpus: 227 cases + manifest, 0 failed · suite: NO-EXPECTATION=4 PASS=327
     gates: 85 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r176/gates-v319.txt)
     guard, the ordinary way, 783 programs, ELF and PE, against v318 and against v315 (main), four runs:
            587 byte-identical, 196 refused identically, 0 DIFFER
     installer (payload v319): 76cf5153fe50ec47df4aec751eaa3637fd6f0e5430902e1be8b14fba61c44c6c
staged r176-block-exit-zero 9bb059ea  Sutram 1.0 (v320) - sampurna sutra  (on v319; NOT merged; NOT READY - a decision)
     crash corpus: 227 cases + manifest, 0 failed · suite: NO-EXPECTATION=4 PASS=327
     gates: 86 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; evidence-r176/gates-v320.txt)
     installer (payload v320): ef35642401cd298d6d806e589c09a2da705a090ec880d787a2aea82b1ea3835b
     guard against v319 and v315, ELF and PE, four runs: 549 byte-identical, 196 refused identically, 38 DIFFER -
            the same 38 as in R175: exactly the programs that compile and contain a mandapa
staged v318 c1f516f8 · v317 501d35fd · v316-ready 59d60353 - unchanged
```

**The guard is absolute. v319 holds it: 0 DIFFER.** v320 does not and cannot (R175-00); that is one of the reasons
it is separate. Sanskrit only; no pack touched; `backups/` untouched.

**A correction to R175-00's release line.** It named one staged branch, `r175-nested-and-zero`, "SHA in the
follow-up commit". **That branch was never pushed.** Its first full gate run came back **84 PASS / 2 FAIL** - a
pin I had not updated (below) - and before I re-ran it your R176 asked for the split. So the two changes are now
two branches, v319 and v320, and nothing called `r175-nested-and-zero` exists on the remote. I have changed that
line in R175-00 to say so.

**The pin that failed, and what it was:** gate `R101 memory` held the line *"a `kosh` made in a block 100,000
times is NOT reclaimed (the documented gap): over 8 MB"*, with a note written in R101 that the reference must
change when it closes. The nested hoist closes it for a `kosh` used only as `k[i]` and with the `kosh_*`
built-ins: **106 MB → under 1 MB.** I changed that line and added the one that keeps the remaining gap pinned:
**the same `kosh` given to a `prakriya`: still over 8 MB (106,240 KB).** The second failure was `doc counts`,
which only repeats that a gate failed.

## WS1 - the hoist alone

**Staged: `r176-made-once-anywhere`, v319, on v318.** Its compiler is byte for byte the "step 1" compiler of
R175, and the guard was run again from the branch: **0 DIFFER, ELF and PE, against v318 and against v315.**
**Gates 85 / 0 / 1.** New gate `R175 nested made once` (16 checks; 13 fail on v318). Under Wine: its 15 programs
compile to the same PE as on Linux and print what the ELF prints (`wine.txt`). **Not run on Windows.**

**Speed - 800,000 passes, three runs each, the time for the first 400,000** (`results-nested.txt`; the gates were
running on the same machine during this batch, so read the times as "about"):

| the declaration is | v318: VmRSS at 800,000 | v319 | v318: 400,000 passes | v319 |
|---|---|---|---|---|
| `kosh`, under a `yadi` | 37,512-37,516 KB | **20 KB** | 6.8-10.4 ms | **2.0-2.1 ms** |
| `kosh`, in a `mandapa` inside the loop | 50,016 KB | **16-20 KB** | 21.4-22.3 ms | **9.4-9.6 ms** |
| `mala m[8]`, in a `mandapa` inside the loop | 62,512-62,516 KB | **20 KB** | 13.4-13.9 ms | **5.9-6.1 ms** |
| `kosh`, in a `yavat` | 37,512-37,516 KB | **16-20 KB** | 10.0-10.5 ms | **1.4-1.5 ms** |

**The hoist alone costs nothing that I can find: it is two to seven times faster in these shapes** (no allocation
after the first pass), **and a program without the case compiles to the same bytes** - `t_small.sm`, a block with
a `nirmmita` and no `kosh`, is identical from v318 and v319.

**That branch can merge as far as these checks go.** What stands against calling it a release is what stood
before: not run on Windows, and it sits on v316, v317 and v318, which have not been either.

## WS2 - the zeroing, as a decision

**First, two of the facts in your brief need correcting - one of them is my own number.**

- **"13.2 ns against 5.6" → 8.9 against 5.5.** My R175 figure came from one batch of seven runs; this machine's
  timings drift between batches (one later batch read v318 itself at 10.4). Measured properly - all the programs
  run in turn, 25 rounds, the best of each (`results-what-the-time-is.txt`) - **a block of `nirmmita(64)` in a
  loop takes 5.5 ns a pass on v318 and 8.9 ns with the zeroing: +3.4 ns, 1.6x, not 2.4x.**
- **"Slower than if they had written no block at all" - no.** The same loop with no `mandapa` takes **27.7 ns a
  pass** (every `nirmmita(64)` stays and touches new memory). With the block and the zeroing: 8.9. **The block is
  still three times faster than no block.**

### 1. Zero only what was written?

**The compiler does not know what was written, and cannot cheaply.** A store into scratch memory is `p[i] = v`
with `i` computed at run time, or a store made by a `prakriya` or a built-in the address was given to; the
compiler cannot even tell, at a store, that the address is scratch memory. Knowing would mean tracking the lowest
and highest address written - two compares on **every** indexed store in the program. That costs more than the
zeroing. **No.**

### 2. What is the extra time made of?

**The stores. Nothing else.** One compiled program, its bytes changed by hand to take pieces out
(`patched-variants.txt` says exactly what was changed):

| variant | 1,000,000 passes |
|---|---|
| v318 - zero at the allocation only | 5.5 ms |
| zero at the allocation **and** at the exit (R175's code; v320) | **8.9 ms** |
| the exit's instructions run, but its loop is skipped | 5.5 ms - **the dozen extra instructions cost nothing measurable** |
| zero at the exit only (the allocation's zeroing loop removed) | **6.3 ms** |
| neither | 4.1 ms |
| the exit zeroing with `rep stosq` at every size (my first build) | 53.5 ms |

**So: one zeroing of 64 bytes costs about 1.4-2.2 ns here, and v320 does it twice.** It is not "one or two
stores" because the block took 64 bytes and all eight words are cleared; the program wrote one of them.
**The last line answers your `rep stosq` question:** it was the whole of my first build's cost and is not in the
current code below 1 KiB.

### 3. Leave the memory dirty and keep `nirmmita` out of it?

**Yes, this is possible, and it is the option that costs least. Not built.**

- **No page map is needed.** What a block has used is one range: from the lowest address the scratch cursor ever
  reached, to the field's end. One word holds it.
- **The form that changes the fewest programs:** today the ordinary side reads the word `0kshetra_end` as its
  limit, and a block's exit moves that word back up. **Make that word a floor that only ever goes down** - the
  lowest the block side has reached - and give the block side a word of its own for its moving cursor. The
  ordinary side's code is then untouched (it still reads the same word); it simply never climbs into memory a
  block has used, so that memory never needs zeroing for it, and a block still zeroes what it takes when it takes
  it, as today.
- **Cost:** one compare at a block's `nirmmita` ("is this lower than the floor?"). No zeroing added anywhere.
  **NOT MEASURED - nothing was built**; from the table above, an untaken compare is in the "nothing measurable"
  row.
- **What it gives up:** memory a block once used is never available to the ordinary side again. After a 600 MB
  block, ordinary allocations have 424 MB of the field, not 1 GiB; past that they take the path they already take
  when the field is full (their own mapping). The programs that would notice are the ones that hit the defect
  today - and they would get zeros.
- **Guard:** the block programs change (the same 38), and any program that asks `parimana()` *and* has a block;
  a program with no block need not change at all.

### 4. Just document it?

**It would be a bug left in, and the sentence you propose is not one a student can follow.** *"Initialise before
you read"* assumes the student is the one reading uninitialised memory. **Sutram reads it for them:**

```
mandapa { vitti p = nirmmita(600000000) ; 77 written into its lowest 126 MB }
vitti q = nirmmita(480000000)        # ordinary memory, up to where the block's began
mala m[8]                            # a new mala: "eight numbers, all 0"
likha(m[0], m[7])                    # prints 77 77
```

`programs/kosh_after.sm`, `results-mala-after-block.txt`. **A `mala` has no initialiser to forget; the language
promises its numbers start at 0** (and `nirmmita` promises zeroed bytes, reference §4). A `mala` of 70,000,000
declared after the same block has **10,782,273 numbers that are not 0** (`mala_after.sm`). So the fourth sentence
in §19 would have to read: *"after a large block, a new `mala` may not start at zero."* That is not a limitation;
it is a broken promise written down.

### My view, since you gave yours

**I disagree with "a documented limitation may be worth more than the slowdown" - on the facts above, not on the
principle.** The slowdown is 3.4 ns, the block stays three times faster than no block, and the defect reaches a
student who did nothing wrong. **But I also would not merge v320 as it is,** because the same result is available
for less:

| option | a small block, 1,000,000 passes | fixes the defect | changes |
|---|---|---|---|
| v319 as it is | 5.5 ms | no | - |
| **A. v320: zero at the exit, keep zeroing at the allocation** | 8.9 ms | yes | 38 block programs |
| **B. zero at the exit only** | 6.3 ms (from the patched program; not a build) | yes | the same 38 |
| **C. the floor (§3): the ordinary side never enters block memory** | about 5.5 ms (NOT MEASURED) | yes | the same 38, plus `parimana()` in block programs |
| D. document it | 5.5 ms | **no** | - |

**I would build C.** It adds no zeroing, it leaves a block's `nirmmita` exactly as it is, and its one invariant -
"the ordinary side stays below the floor" - is checked in one place. **B is the fallback** if C's lost memory
matters to you: it is correct for the reason given in R175-00 (the cursor moves back in two routines only), but
it makes "memory beyond the cursor is zero" depend on those two routines for blocks' own correctness too, where
today a block zeroes for itself. **A is the safest of the three and the slowest; it is what is staged.**

## WS3 - the 38th program

- **It is `tests/r73_scratch/blind_kosh_via_call.sm` - a test, not an example.** It is run by gate `R73 scratch`,
  it is not in `examples/`, it is not in the installer's payload, and no document a student reads shows it. The
  README describes the *limit* it pins, in words, as something not to do ("pass scratch buffers to functions to
  be read or written, never to be kept").
- **The direction is the other way round from your brief: it printed 99 and now prints 0.** It was written in R75
  to pin a known limit - a scratch address smuggled out through a `prakriya`, read after its block has ended -
  and its own first lines say *"A KNOWN LIMIT, pinned: this compiles, and prints 99 - the NEXT block's data."* It
  did not rely on the defect to work; it recorded the defect's cousin on purpose. With the zeroing the dangling
  address reads 0 instead. **The program is still wrong either way, and the book teaches nothing from it.**
- On v319 (the hoist alone) it still prints 99 and its pin is unchanged. The pin changes only on v320.

## WS4 - the scope

- **The hoist is staged and gate-clean - `r176-made-once-anywhere` 4c1159be, v319 - and, on these checks, ready to
  merge.** Not run on Windows.
- **The zeroing is staged and NOT ready - `r176-block-exit-zero` 9bb059ea, v320, gates 86 / 0 / 1 - pending your decision among A, B, C.**
- **The nested cases now reclaim** (v319): a proven-local `kosh` or `mala` under a `yadi` or `anya`, in a
  `mandapa` inside the loop, at any depth, and in a `yavat` loop.
- **What still does not:**
  - a `kosh` or `mala` given to a `prakriya`, given a second name, sliced - made every pass and kept (48 / 64 and
    80 bytes a pass; the R101 pin: 106 MB for 100,000 passes of a `kosh` grown to 100);
  - a `kosh` in a loop inside the loop - once per start of the inner loop;
  - **a block never returns memory to the operating system**, and a `kosh` made once keeps what it grew to;
  - **a dead big `kosh` keeps its 64 MiB reservation** whenever it is not made once;
  - **on v319, the stale-data defect is open** - it is closed only on the v320 branch.
- **Five staged compilers, none merged, none run on Windows: v316, v317, v318, v319, v320**, each on the one
  before.

## Not done, and why

- **Options B and C are not built.** B's time comes from a hand-patched program; C's is not measured at all.
- **Windows** - Wine only. v320's code was run under Wine in R175 (23 programs, including the seven 600 MB exits);
  the v320 binary differs from that one only in its version string, and was not re-run under Wine.
- **Reference §19** - my paragraphs, on both branches; Muse's wording should replace them.
- **`tests/windows/accept_v316.cmd`** still covers only v316.
