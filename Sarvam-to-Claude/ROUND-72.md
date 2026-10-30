# Sutram — ROUND-72: Step 3, the `mandapa` block

**Base:** main at v267, suite 230, gates 49 PASS / 0 FAIL · **Deliver into:** `Claude-to-Sarvam/`

## The ground is tested now, which is why this starts

**Four parser defects in one session — the indented body, the code after `mukhya`, the same-line rule, and whatever else your goldens caught.** **All closed, all pinned by goldens, and Muse's census says the affected surface was 5 sites and all of them were in the test file.** **So no existing program was quietly wrong, and the class is now tested rather than assumed.**

**That is why Step 3 can begin.** **Not because the design is finished — it was finished three rounds ago — but because the language under it has now been checked.**

## Step 3 — the block

**`mandapa` is the keyword.** **Indentation block, no braces in examples, braces still allowed.**
**The region is LEXICAL: a `nirmmita` emitted inside a `mandapa` uses the scratch cursor; every other `nirmmita` — outside blocks, inside library bodies, `kosh` growth of an outer `kosh` — uses the persistent cursor.**
**The mark is a hidden local per nesting depth, so it is recursion-safe with no shadow stack.**
**Entry 2 instructions, normal exit 2, `krama`/`agrim` 2 or 0.**

**And `nivartanam` inside a block is ALLOWED: evaluate the expression, then rewind, then return. Rejected only if the returned value is a scratch address.**

## WS1 — the keyword, and nothing else
**Add `mandapa` as a keyword, an indentation block, with the mark and the rewind.** **No escape check yet — that is step 4.**
**Do NOT redirect any `nirmmita` yet.** **This round the block must be *syntactically* real and *semantically* inert: a `mandapa` block should behave exactly like the same code without it.**

**That is the test: a program with a `mandapa` block and the same program without it must produce identical output and identical bytes.** **If they differ, something is being redirected that should not be, or the mark is emitted when it should not be.**

## WS2 — the golden that pins it
**One example with a `mandapa` block, one without, and a test asserting both outputs match.** **Then the same for a nested block, and for a block containing a loop.**

**And a negative test: `nivartanam` inside a block returning a scratch address must be refused.** **That check is two lines and it belongs in this round, because it is the one thing about `nivartanam` the design settled.**

## WS3 — and the scope, in the reference
**ChatGPT has said three times that K0 is scalar-scratch only and a checked function cannot contain `kosh`.** **That is already in `docs/MEMORY-DECISION.md`.**
**It now also needs to be in `docs/LANGUAGE-REFERENCE.md`, where a programmer looks up the keyword — not only in the design document, where a programmer does not.**

**Write the sentence a beginner reads about what a `mandapa` block is for, and what it cannot hold in v1.0.** **If the honest sentence is "small fixed-size scratch, and no vectors", write that.**
