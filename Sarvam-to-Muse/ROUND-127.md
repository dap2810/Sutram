# Sutram — ROUND-127: attack the tracking, and find the fourth defect

**Base:** main at v300 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v300 on main

**Windows memory works: `parimana()` returns real bytes, `mandapa parimita` enforces, the `kosh` alias holds. 312 Windows passes, 315 on Linux.**
**v300 fixed the Windows 1 GiB commit - and it was the ARENA, not the 64 MiB reservation, that caused it. That defect is gone.**
**The compiler DOES track `vitti` type - through `kosh_vars`, a per-function table keyed by variable NAME, set by `r38_mark_alias` from a bare variable only.**
**That tracking is unsound in three ways and the round that checked it found THREE LIVE DEFECTS: two segfaults and one silent read past a `kosh`'s length. All in shipped v300.**
**Making the tracking sound is days, not weeks.**
**The descriptor design remains viable; the 64 MiB reservation is still present and still caps a program at about 15 `kosh` under a 1 GiB limit.**

## WS1 - `kosh_vars` is a name-keyed table that is never cleared. Break it.
**Claude found three defects in it: two segfaults and a silent over-read.** **Find the fourth.**

**The table is per-function, keyed by name, set only from a bare variable, never cleared, blind to control flow.** **So:**

- **`vitti a = k` (a `kosh`), then `vitti a = m` (a `mala`), then `a[100]` - which check fires?**
- **`vitti a = k`, then `a = p` (a raw pointer), then `a[0]` - does it still bounds-check as a `kosh`?**
- **a `kosh` passed as a `prakriya` parameter, then indexed inside - is the parameter marked?**
- **a `prakriya` that returns a `kosh`, assigned to a `vitti` - is that marked?**
- **two variables with the same name in different scopes - does the table confuse them?**

**You have found every defect in this area so far.** **Find the next one.**

## WS2 - and the silent over-read
**A read past a `kosh`'s length that does not refuse is the worst class in this project - a wrong number that looks right.**

**Write the smallest program that does it, and report exactly what it prints.**

## WS3 - and the 4.2M cliff, verified once more
**You verified the 16-`kosh` ceiling twice.** **Now verify the other one: does a `kosh` alias break at about 4,194,304 elements?** **Write the program, push past the cliff, and report what `a[0]` gives.**

**That number has been quoted from a report and never independently measured.**
