# Sutram — R141: the guard-page compiler, and the scope of the block

**Base:** main at v263, gates 48 PASS / 0 FAIL · **Deliver into:** `ChatGPT-to-Sarvam/`

## Your R140's K0 answer is accepted, and it changes what I say about the block

**You have now said three times that K0 is a small, opt-in scalar-scratch feature whose checked function cannot contain `kosh`.** **I am writing that into `docs/decisions/MEMORY-DECISION.md` as the block's actual v1.0 scope, rather than continuing to describe it as the memory model.**

## WS1 — Claude built the gate you asked for
**A guard-page compiler: every `nirmmita` block ends flush against a `PROT_NONE` page, so one byte written or read past a block is a SIGSEGV.** **It runs the whole suite, all 226 library proofs and all 86 property proofs with 0 faults, and faults on the two known bugs as controls.**

**So: is that sufficient evidence to call v263 safe?** **You said 247/248 outputs was not enough. Is this?** **If not, what does it still miss — be specific about what a guard page cannot catch.**

## WS2 — the audit's number, and what it does not cover
**Claude: across 305 library functions, 371 write sites and 419 call sites, nothing else writes past a block.** **One live finding beyond `217`: `proof_props.py` gave `khand_mukt` 8 cells and it writes cell `n`, so `n = 8` was one past — fixed.**

**Is that audit complete for the class you identified, or does it miss a shape?** **Specifically: it checks writes past a block. Does it check READS past a block?** **A read one cell past is not a corruption but it is still a bug, and a guard page catches it — did the audit look?**

## WS3 — the 48 fixtures
**You proposed 48 named deterministic fixtures.** **Name the ones that matter most — the ten that would catch the most.** **And say whether any of them needs a construct that does not exist yet, because if they all need `mandapa`, they cannot be written before Step 3.**

## WS4 — and the question I keep asking
**If a `mandapa` block holds scalar scratch only, and most real code uses vectors, then what should the reference page say the block is FOR?** **Give me the sentence a beginner should read.**
