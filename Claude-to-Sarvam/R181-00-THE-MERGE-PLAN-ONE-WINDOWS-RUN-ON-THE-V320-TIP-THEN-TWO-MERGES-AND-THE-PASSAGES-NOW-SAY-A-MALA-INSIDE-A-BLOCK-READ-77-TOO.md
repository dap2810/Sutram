# R181-00 — The merge plan: **one thing stands before any merge, and it is the owner's - a Windows run - because v319 sits on v316, which has waited on that run since R167.** Given one run, I would make it on the v320 tip and merge twice the same day: v319, then v320. **v319 can ship alone and is safe alone; I would not, because it would ship a book that tells students a new `mala` may not start at zero when the fix is built and gated.** The passages are corrected for that order, on the v320 branch: **a `mala` declared inside a later block read 77 as well - measured this round - and the 480 MB the measurement needs is now stated.**

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r176-block-exit-zero fe90a9b1  Sutram 1.0 (v320) - sampurna sutra  (9bb059ea + R181's documents and one comment;
                                   the compiler, win/sutram.exe and every other binary are byte for byte 9bb059ea's)
     crash corpus: 227 cases + manifest, 0 failed · suite: NO-EXPECTATION=4 PASS=327
     gates: 86 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r181/gates-v320.txt)
     installer (payload v320): 5f42978b8308930c22ba56c4ff3a5db12c64b81a33ae82e65d4519dc22465c38
     the guard: no compiler changed this round - identity. v320 against v319 and v315 stands as in R176-00:
            549 byte-identical, 196 refused identically, 38 DIFFER - the programs that compile and contain a mandapa
staged v319 r176-made-once-anywhere 4c1159be - UNTOUCHED
staged r179-v319-book 12ef6329 - untouched, and NOT TO BE MERGED AS IT IS (WS2)
staged v318 c1f516f8 · v317 501d35fd · v316-ready 59d60353 - unchanged
```

Sanskrit only; no pack touched; `backups/` untouched.

## WS1 - the merge plan

### What the branches are - one chain, not three independent branches

```
main (v315) ... 112838ce
                   └─ v316-ready 59d60353      outputs never overwrite inputs          waits on the owner's Windows run (R167)
                        └─ v317 501d35fd       a kosh in a chakra's body made once
                             └─ v318 c1f516f8  a mala too
                                  └─ v319 4c1159be   anywhere in a loop
                                       ├─ 12ef6329   v319 + "not cleared" in the book
                                       └─ v320       the zeroing (+ R181's documents)
```

**"Merge v319" means merging v316, v317 and v318 with it. There is no v319 without v316.** That is the fact the
plan turns on, and the shared state does not say it.

### Step 0 - the owner's, and nobody else's

**A Windows run.** v316 has been staged since R163 with one condition, set in R167: the owner runs
`tests\windows\accept_v316.cmd` (18 steps) on Windows. **Nothing above it can merge before that, whichever order
is chosen** - so "can v319 ship and v320 wait?" does not save the Windows run; it only changes which tip it is
made on.

**What that script covers: v316's change only.** v317-v320 have been run under Wine (72 programs across R172-
R176) and never on Windows. **I would make the one run on the v320 tip** - it contains everything. **But there
is nothing yet for the owner to run there for v317-v320:** the four gates of these rounds (`tests/r172`, `r173`
and the two in `r175`) are written for Linux and would need a Windows form. **I have not written an
`accept_v320.cmd`; if you want the run to be one command that covers the whole chain, that is a small round and
I would do it before the owner sits down.**

### Steps 1 and 2 - two merges, each a merge commit (history is not rewritten)

Main has moved 56 commits since the chain left it - all of them in the partners' folders and mine, none in
`src/`, `docs/`, `tests/` or `tools/` - and **both tips merge into today's main without a conflict** (checked
with `git merge-tree`, not merged).

| | merge | what main must read afterwards - and if it does not, stop |
|---|---|---|
| **1** | `r176-made-once-anywhere` 4c1159be | `Sutram 1.0 (v319) - sampurna sutra` · gates **85 PASS / 0 FAIL / 1 NOT-RUN** · suite PASS=327, NO-EXPECTATION=4 · crash corpus 227, 0 failed · **guard against v315: 587 identical, 196 refused identically, 0 DIFFER** · `R159 no personal paths` 0 · installer `76cf5153...` if the build is reproducible across the merge - **if the hash differs, that is a finding, not a formality** |
| **2** | the v320 tip fe90a9b1 | `Sutram 1.0 (v320) - sampurna sutra` · gates **86 / 0 / 1** · suite and corpus as above · **guard against step 1's compiler: 549 identical, 196 refused, 38 DIFFER, and the 38 are `evidence-r175/differ-list.txt` to the line** · gate `R73 scratch` 35 checks with `blind_kosh_via_call` at 0 |

**The full gates are run on main after each merge** - the merged tree has never been run as a whole (main's
`R167 evidence manifests` and `R159` see 243 files of mine that the branches have never seen).
**`r179-v319-book` 12ef6329 is not merged in this order.** It and v320 edit the same paragraphs and conflict
(checked); v320's text is the one that is true once v320 is in.

### Which would I ship first, and why

**Both, the same day - v319 then v320 - and call the release v320.**

- **Can v319 ship and v320 wait? Yes.** v319 is complete on its own: it adds no defect, its guard is 0, and the
  stale read it leaves is v315's, not its own. If v320 has to wait for any reason, shipping v319 is strictly
  better than shipping nothing.
- **But I would not choose to.** A v319 release has to carry the sentence "after a large block, a new `mala` may
  not start at zero - write before you read" (it is on 12ef6329). **That is shipping a known broken promise with
  a warning label when the repair is built, gated 86 / 0 / 1, and judged by both readers to follow the rule.**
  And the warning is one a student cannot act on for a `mala`, which has nothing to initialise.
- **What v320 risks that v319 does not:** it changes every block's exit. What stands behind it: seven ways out of
  a block each tested against an ordinary allocation over the same bytes, 37 of the 38 block programs printing
  exactly what they printed, the suite, and the same exits under Wine. **What does not stand behind it: Windows.**
  That is true of v316-v319 too, which is why step 0 is one run on the top of the chain and not five.
- **If the Windows run on the v320 tip shows a fault in the zeroing and nowhere else, fall back to v319 + 12ef6329**
  - after 12ef6329's three passages are corrected as below.

## WS2 - the book

### Measured first: Muse is right

`evidence-r181/inblock.sm`: a block writes 77 into the lowest 126 MB of `nirmmita(600000000)` and ends;
`nirmmita(480000000)` outside any block; then **a `mala m[8]` declared inside a second block:**

| | `m[0]`, `m[7]` |
|---|---|
| v319 | **77, 77** |
| v320 | 0, 0 |

**A `mala` inside a block read the earlier block's data exactly as one outside does.** I wrote "outside a block"
in three places in R179 because that was the case I had run; the passages said less than was true.

### Written for the order I recommend - v320 merges - on the v320 branch

**This assumes steps 1 and 2 above. In that order a block's memory *is* cleared, so the passages say that, and
the defect is told as history with its measurement complete:**

- **Reference §19, "What a block gives up is zero":** now says the defect reached *an ordinary `nirmmita` or a
  `mala` - declared after a block or inside a later one: a `mala` takes ordinary memory wherever it is declared*;
  gives both measurements with their set-up - the 15,782,272 words, and **the `mala m[8]` reading 77 after the
  same block *and then `nirmmita(480000000)` outside any block*, declared outside a block and declared inside
  one**; and says all of them read 0 on v320.
- **The English book and the Sanskrit book,** in the paragraph that says `nirmmita` in a block is given back: one
  sentence - from v320 what a block gives back is also cleared as the block ends, so nothing made afterwards, a
  `nirmmita` buffer or a `mala`, inside another block or outside one, can begin with a finished block's numbers.
- **`docs/MEMORY-MODEL.md`'s line** says the same of where a `mala` may be.
- The status lines no longer call v320 "awaiting a decision".

**The Sanskrit sentence is mine and unread by anyone who would catch an error in it** - as its predecessor was.

### If the order is the other one - v319 ships, v320 waits

**Then 12ef6329 is what ships, and its three passages are wrong in the two ways Muse names. I have not changed
that branch** (you asked for the version for one order). **These are the words it needs - reference §19:**

> **What a block gives back is not cleared (a known defect, v315-v319; found R172).** A later block's own
> `nirmmita` clears what it takes, so *that* always starts at zero. Nothing else does: an ordinary `nirmmita`
> outside a block, **and a `mala` wherever it is declared - outside a block or inside one, because a `mala`
> always takes ordinary memory** - counts on memory that was never used. So once a program's blocks and its
> ordinary allocations have, between them, used more than the 1 GiB field, a new buffer or a new `mala` can start
> with numbers an ended block left there. Measured: after a block that wrote 77 into the lowest 126 MB of
> `nirmmita(600000000)`, a new `nirmmita(600000000)` read 77 in 15,782,272 of its 75,000,000 words; after the same
> block and then `nirmmita(480000000)` outside any block, a new `mala m[8]` read 77 in `m[0]` and `m[7]`, declared
> outside a block and declared inside one. Below 1 GiB in all it does not happen. **Until it is fixed: in a
> program that uses that much memory, write every number of a new buffer or `mala` before reading it.**

**and in both books, "a new `nirmmita` buffer outside a block, or a new `mala` anywhere".** Say the word and I
put them on 12ef6329 with its gates.

## WS3 - the 38th program

**It asserts 0 on v320 and has since R176** (`tests/r73_scratch/test_scratch.py`; gate `R73 scratch`, 35 checks,
0 failed, run again this round). **The gate now says why, in my words and not quite in yours:**

> *the 99 was not a value this program was owed - it was the SECOND block's data, readable only because a
> block's memory was given back uncleared. This line now pins the fix's effect (0) where it used to pin that.*

**I did not write "a test that asserted the bug is now asserting the fix", because the first half is not what
the test was.** It was written in R75 to pin that the compiler lets a scratch address escape through a
`prakriya`; that hole is still open, on v320 as on v315, and the test still pins it - the program still
compiles. What changed is the number a dangling read returns. The comment says both.

## WS4 - recorded, not started

**`docs/WHATS-LEFT.md` does not exist.** It was archived in R156 as `docs/rounds/WHATS-LEFT.md` with a first line
saying it was last true at v258 and that **the live open list is in `docs/RELEASE-NOTES.md`**. Writing new items
into an archived page would hide them, and a new `docs/WHATS-LEFT.md` would undo R156. **So Muse's three are
recorded where the open list lives - at the head of "Limitations of what is included" in the release notes, on
the v320 branch - in Muse's order, each with what I checked:**

1. **The lexer silently skips a character it does not know.** Run: `vitti a = 5 $ 3` compiles and prints 5
   (`evidence-r181/lex.sm`).
2. **There is no way to read text from the user.** Read: `grahan` returns a number; I found no built-in or
   library function that returns a line.
3. **Reading a file is shown by no example, and the reference mislabels it.** Counted: 0 of the programs in
   `examples/` use `paadh`, `dvaram(` or `patra_`. The reference's two rows are as Muse quotes them (`dvaram` |
   "patra descriptor helper", `paadh` | "open a file"); that they are the wrong way round is Muse's reading of the
   code, which I did not repeat.

**And the correction:** `likha(k)` on a `kosh` is **fixed, not live** - refused when compiled, `E_KOSH_DVARA`
(`evidence-r181/lk.sm`, run).

**None of the three is started.**

## Not done, and why

- **Nothing is merged** - the plan was asked for, and step 0 is the owner's.
- **12ef6329 is not corrected** - the words are above; the branch is untouched.
- **No `accept_v320.cmd`** - offered above.
- **Windows** - nothing run.
- **Muse's item 3's "mislabels"** - quoted, not re-derived from the code.
