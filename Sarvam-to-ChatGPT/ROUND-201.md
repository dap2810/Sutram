# Sutram — R201: the tracking is unsound. What should it be?

**Base:** main at v300 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v300 on main

**Windows memory works: `parimana()` returns real bytes, `mandapa parimita` enforces, the `kosh` alias holds. 312 Windows passes, 315 on Linux.**
**v300 fixed the Windows 1 GiB commit - and it was the ARENA, not the 64 MiB reservation, that caused it. That defect is gone.**
**The compiler DOES track `vitti` type - through `kosh_vars`, a per-function table keyed by variable NAME, set by `r38_mark_alias` from a bare variable only.**
**That tracking is unsound in three ways and the round that checked it found THREE LIVE DEFECTS: two segfaults and one silent read past a `kosh`'s length. All in shipped v300.**
**Making the tracking sound is days, not weeks.**
**The descriptor design remains viable; the 64 MiB reservation is still present and still caps a program at about 15 `kosh` under a 1 GiB limit.**

## WS1 - your "undocumented choice" argument, now with the real mechanism
**You argued twice that the defect is an undocumented choice between identity, contents and raw bits.**

**The actual mechanism: `kosh_vars`, a per-function table keyed by variable NAME, set only from a bare variable, never cleared, blind to control flow.** **It found three live defects - two segfaults and a silent over-read.**

**So the choice IS made, but by a name-keyed flag that can be stale.**

**Is a name-keyed flag the right mechanism at all?** **What would you use instead in a single-pass compiler with no flow analysis?**

**Options to consider and price:**
- **a name-keyed flag, but cleared on reassignment**
- **a type tag stored in the symbol table entry and updated on every assignment**
- **a small type inference pass before emission**
- **require an explicit declaration, so the type is stated rather than inferred**

**Pick one and say what it costs to implement and what it costs a student to learn.**

## WS2 - and the question I most want answered
**Once the tracking is sound, does `vitti a = k` know enough to emit a descriptor access instead of a direct buffer access?**

**If yes, the descriptor is one emit path, not a redesign.** **If no, what is still missing?**

**This decides whether two weeks of descriptor discussion becomes code.**

## WS3 - and the 64 MiB, now the only memory defect left
**The Windows commit is fixed at v300 - it was the arena, not the reservation.**

**So what remains: the reservation caps a program at about 15 `kosh`, and the alias cliff past 4.2M elements.**

**Is removing the reservation now a small change, or does it depend on the descriptor landing first?** **Say the order and the reason.**
