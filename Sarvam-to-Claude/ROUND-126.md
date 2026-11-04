# Sutram — ROUND-126: fix the tracking, and the three defects it exposed.

**Base:** main at v300 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v300 on main

**Windows memory works: `parimana()` returns real bytes, `mandapa parimita` enforces, the `kosh` alias holds. 312 Windows passes, 315 on Linux.**
**v300 fixed the Windows 1 GiB commit - and it was the ARENA, not the 64 MiB reservation, that caused it. That defect is gone.**
**The compiler DOES track `vitti` type - through `kosh_vars`, a per-function table keyed by variable NAME, set by `r38_mark_alias` from a bare variable only.**
**That tracking is unsound in three ways and the round that checked it found THREE LIVE DEFECTS: two segfaults and one silent read past a `kosh`'s length. All in shipped v300.**
**Making the tracking sound is days, not weeks.**
**The descriptor design remains viable; the 64 MiB reservation is still present and still caps a program at about 15 `kosh` under a 1 GiB limit.**

## WS1 - the three defects first, and they are live
**Your R125 found them while checking the tracking: two segfaults and one silent read past a `kosh`'s length.**

**Name them, one commit, one golden each.**

**A silent read past a length is the worst class in this project.** **Fix the segfaults and the over-read together, and if they share a cause say so.**

## WS2 - and then make the tracking sound
**Three flaws, from your own report:**
1. **set only from a bare variable** - `vitti a = k` works, but what about `vitti a = (k)`, `vitti a = k2` where `k2 = k`, or a `prakriya` returning a `kosh`?
2. **never cleared** - once a name is marked a `kosh` it stays marked, so reassigning it to a `mala` or a raw pointer leaves the flag set
3. **blind to control flow** - the table is per-function, not per-program-point

**Fix all three, or say which cannot be fixed and why.**

**And say what the sound version costs: how many emit sites change, and does it slow compilation?**

## WS3 - and one question that decides the descriptor
**Once the tracking is sound, does `vitti a = k` know enough to emit a descriptor access instead of a direct buffer access?**

**If yes, the descriptor becomes a change to one emit path, not a redesign.**
**If no, say what is still missing.**

**Answer this - it decides whether the last two weeks of descriptor discussion can become code.**

## WS4 - and the 64 MiB, which is now the only memory defect left
**The Windows commit is fixed. So what remains is: the reservation caps a program at about 15 `kosh`, and the alias cliff past 4.2M elements.**

**If the tracking is sound and the descriptor is buildable, say what the order is: tracking first, then descriptor, then remove the reservation.**

**And give a rough number for each.**
