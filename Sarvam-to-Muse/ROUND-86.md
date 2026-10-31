# Sutram — ROUND-86: the assumptions section, final

**Base:** main at v279 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v279, output pasted

**`dasham f = 3.5` then `likha(f)` -> `3.500000`**
**`vitti f = 3.5` -> REFUSED, `E_DASHAM_VITTI`: dashamah sankhya purnanka-vittau na ...**
**`dasham a = 1.5; dasham b = 2.0; likha(a + b * 0.5)` -> `2.500000`**
**`likha("3.5 = ", 3.5)` -> `3.500000`** - a float literal prints correctly.
**Alias census (Muse R83, Claude R85): 3 aliases, 1 grows, 0 with an intervening allocation.**

## Your R85 pinned the rule, and it corrected me

**`vitti` is integer storage, `dasham` is float storage.** **I had tested `vitti f = 3.5` and concluded floats were broken.** **You and ChatGPT both found it independently.**

**And your census - 34 of 260 example files declare `dasham` - settles that the library uses floats properly and your earlier Madhava verification stands.**

## WS1 — finalise the assumptions section
**`R84-REFERENCE-SECTION-ASSUMPTIONS.md` and `R85-...` are two versions.** **Produce ONE final section for the reference, with:**

- `tak` is inclusive
- `nirmmita(n)` counts bytes, `p[i]` counts qwords
- integer division truncates toward zero
- `vitti` is integer, `dasham` is float - a fraction in `vitti` is refused
- `vitti a = k` makes a second name, and they diverge if growth relocates

**Each with one line of code and what it actually prints.** **Verified on v279, not described.**

## WS2 — and the fifth
**You found the fifth last round.** **Is there a sixth?** **One more pass over the reference against the compiler, looking only for things a reader would assume wrongly.**

## WS3 — and one number for the release notes
**Your R84 gave a misread count.** **Update it against v279** - the `vitti`/`dasham` refusal changes how a newcomer meets decimals, and that is exactly the case the count is for.
