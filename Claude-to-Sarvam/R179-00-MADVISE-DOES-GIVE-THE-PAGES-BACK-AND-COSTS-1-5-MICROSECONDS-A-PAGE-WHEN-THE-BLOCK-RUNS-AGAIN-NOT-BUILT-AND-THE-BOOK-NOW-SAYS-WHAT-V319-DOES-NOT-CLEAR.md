# R179-00 — `madvise(MADV_DONTNEED)` does give the pages back on the field's mapping: 274,880 KB → 12,736 KB for 256 MiB. It costs **about 1.5 µs a page every time the block runs again** - a 16 MiB block in a loop goes from 0.95 ms a pass to 7.2 ms. So 16 MiB is too low, and a flat threshold is the wrong shape. **I did not build it**, and say why. The zeroing questions are answered; nothing built there either, as asked. **And the book is changed: reference §19 and both books now say that what a block gives back is not cleared** - on a documents-only branch on top of v319, whose compiler bytes are untouched.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r176-made-once-anywhere 4c1159be  v319  UNTOUCHED - gates 85 PASS / 0 FAIL / 1 NOT-RUN, 0 DIFFER (R176-00)
staged r179-v319-book (SHA in the follow-up commit)  v319 + three documents (WS3); the compiler, win/sutram.exe and every other binary
                                are byte for byte 4c1159be's; the installer is rebuilt because the documents are in it
     crash corpus, suite, gates: ITS FULL GATES WERE STILL RUNNING at this first push - NOT YET A RESULT (next commit)
     the guard: no compiler changed - identity
staged r176-block-exit-zero 9bb059ea  v320  unchanged, NOT READY (the decision, WS2)
staged v318 c1f516f8 · v317 501d35fd · v316-ready 59d60353 - unchanged
```

**The guard is absolute: no compiler changed this round.** Sanskrit only; no pack touched; `backups/` untouched.
R177 and R178 were not started.

## WS1 - D, the `madvise` threshold

### What it buys - measured before anything was built

**Today** (`results-block-200mb-today.txt`, v319, R169's program): a block takes `nirmmita(200000000)`, touches
every page, ends. **VmRSS 195,328-195,336 KB inside the block, and the same after it, and at the program's end.**
Nothing comes back.

**With `madvise`** - measured on a mapping made with the field's own flags
(`mmap(1 GiB, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE)`), through libc from a small
harness; **not a Sutram program, no compiler changed** (`madv.py`, `results-madvise.txt`; best of 5):

| span | VmRSS, written | write it again, pages kept | `madvise` | VmRSS after | reads 0 | write it again, after the discard |
|---|---|---|---|---|---|---|
| 1 MiB | 13,652 KB | 0.03 ms | 0.03 ms | 12,628 KB | yes | 0.37 ms |
| 4 MiB | 16,828 KB | 0.20 ms | 0.14 ms | 12,732 KB | yes | 1.54 ms |
| **16 MiB** | 29,116 KB | **0.95 ms** | 0.55 ms | 12,736 KB | yes | **6.67 ms** |
| 64 MiB | 78,272 KB | 7.85 ms | 2.59 ms | 12,736 KB | yes | 33.9 ms |
| 256 MiB | 274,880 KB | 27.7 ms | 7.49 ms | 12,736 KB | yes | 113 ms |
| 512 MiB | 537,024 KB | 55.3 ms | 15.4 ms | 12,736 KB | yes | 231 ms |

(The harness's own baseline is 12,300 KB.)

**So the answer to "does VmRSS drop?" is yes - `MAP_NORESERVE` does not prevent it - all the way to the
baseline, and the pages read 0 afterwards.**

**And the price, which the table makes plain:** the call itself is cheap (about 0.12 µs a page), **but the next
block to use that memory takes every page as a fresh fault: about 1.5 µs a page more than if the pages had been
kept** (1,415-1,748 ns across the sizes). The price is per page and does not get better with size.

### The three conditions

**1. Rounding.** Discard `[round_up(cursor, 4096), round_down(mark, 4096))`, and only if that is not empty.
- **Can it discard a page an enclosing block still uses? No.** The block side grows down. Everything an enclosing
  block took before this one started lies at or above `mark`; the page that contains `mark` is cut off by the
  round-down. What the enclosing block takes *after* this one ends, it takes later, and its own `nirmmita` zeroes
  it.
- **Can it discard a page the ordinary side uses? No.** The ordinary side is below `cursor`; the page that
  contains `cursor` (which the two sides may share) is cut off by the round-up.
- A block that took 100 bytes has an empty range after rounding, and makes no call.

**2. Both routines.** The premise needs one correction: **a block's span is not raised by more than one path.**
One routine takes scratch memory (`r73_gen_scratch_nirm` lowers the cursor); the field never grows (it is 1 GiB;
a block that needs more stops with `kshetra purnam`); and **two routines give memory back - `r73_gen_rewind` and
`r73_gen_ret_rewind`**, called from four places (R175-00). The span at an exit is `mark - cursor`, whatever took
it; that is the true span. **The check must be in both of those two routines** - the same two places R175's
zeroing went.

**3. The threshold and the guard.**
- **How many guard programs differ: 38 - every program that compiles and has a `mandapa`.** Not "every block
  that crosses it": whether a block crosses the threshold is known only when the program runs, so the comparison
  has to be emitted at every block's exit. It is the same 38 as the zeroing's.
- **What the threshold should be: not 16 MiB, and not a flat cut-off at all.** A flat rule "discard the whole span
  at or above T" makes the block just above T pay for all its pages on every pass: **a 16 MiB block in a loop,
  0.95 ms a pass kept, 7.2 ms a pass discarded (0.55 + 6.67) - 7.6 times slower** to save 16 MB that would have
  been reused a moment later. A program that processes a thousand files, each in a 16 MiB block, is exactly the
  shape `mandapa` is for.
- **The rule I would propose instead - keep T, discard what is beyond it:** at an exit, discard only the part of
  the span more than T below the mark. Then a finished block never leaves more than T resident, a block of T or
  less never pays anything but the comparison, and a larger one pays only for its excess. **T is then not a
  performance tuning number but a statement: "the most idle memory a finished block may leave resident".**
  **I would set it at 64 MiB** - one sixteenth of the field, and the size the design already uses for a `kosh`'s
  region - **and I would call it a policy, not a measurement.** The measurement is the 1.5 µs a page; it says that
  any T is a trade of that against idle memory, and nothing in it favours one T.

### Why I did not build it

- **It is a second change to every block's exit, with the same 38 DIFFER as the zeroing.** The exit should be
  changed once, by one decision, not twice in two rounds. And the two interact: **a discarded page reads 0**, so
  for the part it discards `madvise` *is* the zeroing, at about a quarter of the cost of writing zeros (256 MiB:
  7.5 ms against the 27.7 ms a second pass costs). An exit that discards what is beyond T and zeroes - or does not zero -
  the T it keeps is one design; building half of it now would be building the wrong half.
- **It does not fix the stale-data defect on its own** (Muse said the same): the T that is kept stays dirty.
- **Windows needs a runtime entry.** The Windows runtime answers a system call it does not know with -1
  (`win/winrt_blob.asm`, `.error`), so the same instructions would do nothing there; the equivalent is
  `VirtualAlloc(MEM_RESET)` or a decommit, and that is a change to `win/winrt_blob.asm` that cannot be tested
  here beyond Wine.
- **What it buys a student is small.** It matters to a program that does one large piece of work in a block and
  then runs on for a long time. That is real, but it is not a defect, and nothing is wrong today that this fixes.

**If you want it built, say which exit: (i) discard beyond T only; (ii) discard beyond T and zero the kept T
(closes the defect, option A's cost bounded at T); (iii) discard beyond T, zero nothing, and close the defect by
the floor (R176-00's C).** I would take (iii).

## WS2 - the zeroing: answers, nothing built

**One fact in your list needs correcting first:** the `mala m[8]` that read 77 was **not inside a block**. It was
declared *outside* any block, after a block had ended (`evidence-r176/programs/kosh_after.sm`). Inside a block a
`mala` takes ordinary memory too, so the same could happen there, but it is not what was measured. And the cost
"0.8 ns when done once" is from a hand-patched program (R176-00), not a build.

**1. Is there a placement that fixes the 77 without touching the block's exit?** The `mala`'s memory comes from
the ordinary side (`emit_nirmmita_from_rax`): the same allocation every `mala`, every `kosh` descriptor and every
`nirmmita` outside a block uses. The places it could be cleared, and what each one changes:

| where | fixes | programs whose bytes change |
|---|---|---|
| at a `mala`'s declaration | a `mala` only - an ordinary `nirmmita` still reads 77 | every program with a `mala` |
| in the ordinary allocation, always | everything | every program that allocates; and every allocation pays |
| in the ordinary allocation, only above a mark | everything | every program that allocates (the comparison) |
| **at the block's exit** (A or B) | everything | **the 38 with a block** |
| **the floor** (C: the ordinary side never enters block memory) | everything | **the 38 with a block** (a block's `nirmmita`, its entry and its exits - but no zeroing at the exit) |

**So there is one placement that does not touch the *zeroing* at the exit - C - and none that touches fewer than
the 38.** Every fix on the ordinary side changes far more programs, because nearly every program allocates and
few have a block. The block's own code is the smallest place.

**2. Is 38 DIFFER acceptable? What the rule is for.** I did not write the rule and the decision is yours; this is
what I understand its reason to be. **Byte identity is the only complete, cheap proof that a change did nothing
it was not meant to do.** A test suite checks what somebody thought to test; the guard checks every instruction
of every program. "0 DIFFER" is that proof in its strongest form, and it is the right form for a change that
claims to add something new and disturb nothing.

**A deliberate change to what existing programs do cannot be put in that form, and the rule's purpose can still
be met - if all of these hold, and all of them did:**
- **the set that will differ is named beforehand by a rule a script can check** ("compiles and contains a
  `mandapa`"), not discovered afterwards;
- **the set that does differ equals it exactly** - nothing outside it, and nothing inside it left unchanged
  (38 = 38, in every run, ELF and PE, against two baselines);
- **every program in it is run old and new and compared** (37 identical in output and exit code);
- **every difference in behaviour is explained one by one** (the 38th).

**If you accept that, I would write it into the rule rather than waive the rule once:** *"0 DIFFER outside the
declared set; the declared set equals the differing set; every program in it run both ways."* A waiver is
forgotten; a rule is checked.

**3. The 38th - is it corrected?** **Yes, on the branch that changes it.** On `r176-block-exit-zero` (v320) the
pin in `tests/r73_scratch/test_scratch.py` is `'0'`, with a comment saying it was 99 and why, and the program's
own header says the same; gate `R73 scratch` passes there with 35 checks. **On v319 it still asserts 99, and
that is correct for v319**, which still prints 99.
**But I do not agree it "was checking the bug".** It was written in R75 to pin a *different* thing: a scratch
address that reaches a `kosh` through a `prakriya` the compiler cannot see into - a hole in the escape check. Its
comment says so, and says that a future check which refuses the program will fail the test, "and that is the
point". The 99 is simply what a dangling address happened to read. The zeroing changes what it reads; the hole
it pins is still open on every branch.

## WS3 - the book

**Changed in this round, on `r179-v319-book` - the line that can merge - because v319 does not clear:**

- **Reference §19**, a new point under "Run time": *what a block gives back is not cleared (a known defect,
  v315-v319)* - why a later block still sees zeros and an ordinary `nirmmita` or `mala` may not; when (more than
  the 1 GiB field used between blocks and ordinary allocations); the two measurements; and **what to do until it
  is fixed: in a program that uses that much memory, write every number of a new buffer or `mala` outside a block
  before reading it.**
- **Both books**, after the paragraph that says `nirmmita(n)` gives "fresh, zeroed memory": one paragraph, "one
  exception to *zeroed*", in English and in Sanskrit.
- The changelog's v319 entry and `docs/INSTALLER-REBUILD.md` say the documents changed and the compiler did not.

**If the zeroing ships instead,** v320's §19 already has the other sentence ("What a block gives up is zero",
with the cost), and these three paragraphs come out. **Muse's words were not in the tree when I wrote these;
they should replace mine.** The Sanskrit paragraph is mine and has not been read by anyone who would catch an
error in it.

## WS4

**No detach, no ping-pong, no `kosh temp[n]` work. `r176-made-once-anywhere` 4c1159be is untouched.**

## Not done, and why

- **D is not built** - the four reasons above.
- **The zeroing: nothing built** - as asked.
- **The `madvise` figures are from a harness in C-level calls, not from a compiled Sutram program**, and from
  Linux only. What Windows' `MEM_RESET` costs: NOT RUN.
- **Windows** - nothing run.
- **Six staged lines now, none merged:** v316, v317, v318, v319, v319 + the documents, v320.
