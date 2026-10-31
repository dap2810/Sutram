# Sutram — ROUND-69: Step 2, the two cursors — and the block's scope stated honestly first

**Base:** main at v263, gates **48 PASS / 0 FAIL** · **Deliver into:** `Claude-to-Sarvam/`

## Your R68 is the strongest round of this work, and one thing in it is new

**The guard-page compiler — every `nirmmita` block flush against a `PROT_NONE` page, so one byte past is a SIGSEGV — running the whole suite, all 226 library proofs and all 86 property proofs with zero faults, and faulting on the two known bugs as controls.**

**That is a far better answer than "247 of 248 outputs unchanged", because it does not compare outputs — it proves nothing touches memory it does not own.** **It is now the release gate, and it should run on every future round.**

**And the audit number: 305 library functions, 371 write sites, 419 call sites, nothing else writes past a block.** **`pad_vam`'s contract was wrong, not its body — that is the right diagnosis and the right fix.**

## WS1 — before Step 2, three small things

**1. The two splitters ChatGPT flagged as having contract problems.** **You said you did not fix them because the brief said count and name. Fix them now — a wrong contract is a bug in the documentation that becomes a bug in every caller.**

**2. `tools/proof_props.py`'s `khand_mukt` — you fixed the 8-cell case. Confirm the fixed seed now draws a value that would have caught it, so it cannot regress silently.**

**3. And make the guard-page run a permanent tool, not a one-off.** **`tools/guard_page.py` or similar, runnable, documented, with the two control bugs named.** **If it lives in `evidence-r68/` only, it dies with this round.**

## WS2 — Step 2: `dvi-mukha`, the two cursors

**Now that the library is sound and the gate is green, build it.**

**One range, two opposing cursors: the persistent cursor grows up from the start, the scratch cursor grows down from the end.** **They cannot overlap, so the `kosh`-growth escape becomes structurally impossible.**

**Constraints:**
- **The persistent path must not change behaviour.** **Every program that allocates today must still work identically.**
- **Nothing may use the scratch cursor yet — the `mandapa` block does not exist.** **So the scratch cursor should be reserved, initialised, and unused.**
- **And the guard-page run must still pass, and still fault on the two controls.**

**The measurement I want: the range size, the instruction cost of the bounds check, and whether the two-cursor split changes anything measurable in the existing suite.**

## WS3 — and state the block's scope honestly in the code's own docs

**ChatGPT has now said three times: *"K0 is a small, opt-in scalar-scratch feature. Its checked function cannot contain unsupported `kosh` values or operations."***

**So a `mandapa` block holds scalar scratch, not vectors.** **That is a smaller feature than I have been describing, and I want it written down where a programmer will read it — not discovered later.**

**Add that to `docs/decisions/MEMORY-DECISION.md`: what a `mandapa` block can hold in v1.0, and what it cannot.** **And if that makes the block less useful than the round-3 claims suggested, say so in the doc rather than in a handback.**
