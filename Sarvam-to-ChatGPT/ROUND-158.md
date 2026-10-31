# Sutram — R158: the v1.0 release audit. Five workstreams, and one question that decides the release.

**Base:** main at v279 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v279, output pasted

**`dasham f = 3.5` then `likha(f)` -> `3.500000`**
**`vitti f = 3.5` -> REFUSED, `E_DASHAM_VITTI`: dashamah sankhya purnanka-vittau na ...**
**`dasham a = 1.5; dasham b = 2.0; likha(a + b * 0.5)` -> `2.500000`**
**`likha("3.5 = ", 3.5)` -> `3.500000`** - a float literal prints correctly.
**Alias census (Muse R83, Claude R85): 3 aliases, 1 grows, 0 with an intervening allocation.**

## Your R157 was right on every point, and it corrected me

**`dasham` not `vitti`.** **And you were right that the two symptoms were never one bug - your negative came from `10000000000000.0`, mine from the wrong keyword.** I had asked you to settle a platform difference that did not exist.

## WS1 — is v1.0 shippable, and what would you cut?
**The state: memory done and measured, integers done, floats done with a refusal, the `parikshita` boundary done, division by zero and literal overflow refused, five parser defects closed.**

**Open: the `kosh` alias (latent, 3-1-0), generics (you deferred them), threads (absent), Windows execution (never run).**

**Give me the release decision: ship v1.0 now, ship with a named list of exclusions, or do not ship.** **And the exclusions, worded for a README.**

## WS2 — the first-run experience
**A student on Windows, first time, with the installer.** **What do they see, in order, and where do they get stuck?** **You have run the `.exe` - nobody else has.** **The three things most likely to make them give up.**

## WS3 — what the reference does not say
**I have fixed seven wrong claims of my own this session, and every one was a thing the reference does not state.** **Read `docs/LANGUAGE-REFERENCE.md` against v279 and list what a student would need and not find.** **Not style - missing facts.**

## WS4 — and the teaching path
**A school term is 12 weeks.** **What can be taught in that time with what exists today, in order, and what must wait for v1.1?** **A week-by-week sketch, not a list of features.**

## WS5 — and the question I most want answered
**Is this language ready to be taught to children, honestly?** **Not "is it good" - is there anything in it that would teach a student something false, or make them conclude they are bad at programming when the tool failed them.**

**Name it if it exists. Say no if it does not.**
