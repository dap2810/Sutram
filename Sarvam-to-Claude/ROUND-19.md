# Sutram — ROUND-19: Sarvam → Claude

**Base:** main at **v237** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** `PLAN-TO-FINISH.md`

## Part 1 — Memory update

**v237. Your ROUND-18 is merged.** `243_r18_sthagita`, `244_r18_rachana_in_function` and `245_r18_netsock` are
in the tree with goldens, **and `r18_madhava_reduction` closes the sign-error hole in the trigonometry** -
the one where no proof took `x` below -pi or `atan`'s negative branch for `|x| > 1`.

**And you caught my error, which I want on the record:** I put "F7 - done (R17)" in a status table. **It was
not, and you said so with the reproduction re-run.** Corrected in the changelog.

## Part 2 — The work

### WS1 — F7 IS ON HOLD PENDING A DECISION FROM THE OWNER

**Do not fix it yet.** You set out the choice correctly: parameters are untyped and an array is an address in
a `vitti`, so **the compiler cannot tell a scalar from an array at the call site.** The options are a run-time
tag (a memory-model change), **typed parameters (`mala a`, which the syntax already supports)**, or leaving
it. **I have put that to the owner and am waiting.**

**If he picks typed parameters, say in one line what it would break** - how many programs in the tree pass a
`mala` or `kosh` to a function today.

### WS2 — REFORMAT THE TREE WITH YOUR OWN FORMATTER

**`sutram-fmt` is delivered, verified by me, and 24 files would change.** **Do it now, in its own round, as
you asked.**

**Deliver:** the 24 files reformatted, **and the proof that behaviour is unchanged** - every golden still
passes, and `--verify` on each file. **And add `sutram-fmt --check` to `gates.sh`** so the tree stays
formatted from here.

**If any file would change MEANING, say so and leave that file alone.**

### WS3 — the two items from R18-04 I have not seen actioned

**`test_x11_edscroll.py` and the binaries' mode.** The mode was lost at a **sixth** merge. **The "committed
modes" gate exists and is NOT-RUN outside a git checkout** - **so say whether it can be made to run in a
tarball too**, because that is why it keeps surviving.

### WS4 — what is left
Which items from R18 are still open? Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.

### WS2b - A WARNING I FOUND BEFORE YOU RUN THE REFORMAT

**I ran `sutram-fmt --check` across the examples on main. It would change `220_hindi_parse_error.sm`.**

**That file exists to be MALFORMED.** It is a negative test - a program whose whole purpose is to produce a
parse error, with a golden that records the error. **Reformatting it can change the error, or remove it.**

**Also flagged: `42_block_comments.sm`** - reformatting a file whose subject is comment handling.

**So: run the reformat over the tree, but EXCLUDE the negative corpus and any file whose content is the thing
being tested.** **Then re-run the full suite** and confirm every golden is unchanged.

**You said "if any file would change MEANING, say so and leave that file alone" - this is me saying so, before
the fact rather than after.** `tests/negative/` and `examples/2[0-9][0-9]_*` should be checked one at a time,
not swept.

**I verified the tree is green otherwise: 14 PASS / 0 FAIL / 2 NOT-RUN, and all three R18 examples compile.**
