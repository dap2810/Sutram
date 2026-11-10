# Sutram — ROUND-181: the merge plan, and three sentences the book still needs.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Both readers agree on the decision, and one of them found the rule already permits it.** **This round is the merge, and the last documentation gap.**

---

## 1. The decision, with both readers' reasons

**Claude: the zeroing (v320), not the floor.** **The floor gives blocks their peak for ever — whatever a block once used the ordinary side never gets — and past the field an allocation costs 3 µs and 4 KB instead of 30 ns and 64 bytes.** **And it reversed its own R176 choice to get there.**

**Muse: the floor holds as a correctness design but admits a broken implementation** — a persistent allocation inside a block can overlap the block's live scratch if the mark is recorded only at block exit. **And the "38 is the minimum" claim is true only under one of two implementations; the other is 404.**

**So: v320, the zeroing.**

**And the rule question is answered by the rule itself:**

> *"The rule as written is not '0 DIFFER, unconditionally': it is 0 DIFFER for programs that do not use a `mandapa`, and for the rest a stated list with every changed program producing the same output. The 38th is carried by the project's own precedent, not by a waiver."*

**37 of the 38 differ only in bytes and produce the same output. The 38th is covered by precedent.** **So the change follows the rule rather than breaking it.**

---

## 2. WS1 - and this is the round: the merge plan, in order
**Three branches are staged, all gate-clean:**

- **v319 `4c1159be`** — made once anywhere in a loop. **85 gates, 0 DIFFER, faster in every nested shape, free.**
- **v319 + book `12ef6329`** — §19 and both books now say what a block gives back is not cleared. **Compiler untouched.**
- **v320 `9bb059ea`** — the block-exit zeroing. **86 gates, 38 DIFFER.**

**Give the order they merge in, and what each merge is expected to read afterwards.**

**And one question the owner will ask: does v320 need to merge at all, or can v319 ship and v320 wait?** **The stale-data bug is real, and a student who reads before writing gets 77.** **But v319 alone is a complete improvement with a clean guard.**

**Answer which you would ship first, and why.**

## WS2 - and the book, which has one imprecision left
**Muse: *"A `mala` declared inside a block is also an ordinary allocation and can read stale bytes the same way, but the passages warn only about one outside a block."***

**So the three passages warn about the wrong case.** **A student reading them would think a `mala` inside a block is safe, and it is not.**

**Fix all three — reference §19, the English book, the Sanskrit book — so they say what is true: a `mala` declared anywhere can read what a previous block wrote, inside a block or after one.**

**And the reference's measurement sentence omits the 480 MB ordinary allocation that the `mala m[8]` reading of 77 depends on.** **Add it, so the measurement can be reproduced.**

**And if v320 merges, all four passages change again — a block's memory IS cleared.** **So: write the version for whichever order you recommend in WS1, and say which order it assumes.**

## WS3 - and the 38th program
**It asserted 99 and now gets 0.** **Muse says it is carried by precedent.**

**So: correct it to assert 0, and say in the gate why — a test that asserted the bug is now asserting the fix.**

## WS4 - and one thing to note, not fix
**Muse's ranking of what is left, which is the first non-memory answer anyone has given:**

1. **The lexer silently skips unknown characters** — a student types one, it vanishes, and the error lands three lines later.
2. **There is no way to read text from the user.**
3. **Reading a file is the one basic thing the language can do that no example shows and the reference mislabels.**

**Record these in `docs/WHATS-LEFT.md` in that order.** **Do not start them.**

**And one correction to record: `likha(kosh)` printing an address was fixed, not still live.**
