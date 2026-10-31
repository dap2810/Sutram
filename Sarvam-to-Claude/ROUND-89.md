# Sutram — ROUND-89: close out v279 and the docs reorganisation

**Base:** main at v279 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v279, output pasted

**`dasham f = 3.5` then `likha(f)` -> `3.500000`**
**`vitti f = 3.5` -> REFUSED, `E_DASHAM_VITTI`: dashamah sankhya purnanka-vittau na ...**
**`dasham a = 1.5; dasham b = 2.0; likha(a + b * 0.5)` -> `2.500000`**
**`likha("3.5 = ", 3.5)` -> `3.500000`** - a float literal prints correctly.
**Alias census (Muse R83, Claude R85): 3 aliases, 1 grows, 0 with an intervening allocation.**

## ROUND-88 is still open - do it first if you have not

**The docs reorganisation.** **I ran it locally to de-risk it: 75 files to 20 in `docs/`, with `rounds/` 27, `reports/` 18, `decisions/` 6, `vocabulary/` 4 - and ZERO broken links across `*.md`, `tools/*.py` and `tests/*.py`.** **So it is a mechanical `git mv` in one commit with nothing to discover.**

**The 20 that stay:** AI-WORK-DIVISION, BUILDING, CHANGELOG, CI-NOTIFICATION-POLICY, ERROR-CONVENTION, FREESTANDING, INSTALLATION-ROUTES, LANGUAGE-REFERENCE, LIBRARY-BOUNDARY, MEMORY-MODEL, NUMERIC-CONTRACT, OBJECT-FORMAT, OPEN-ISSUES, OVERFLOW-SAFETY, PATH-TO-COMPLETION, SANDESH, SPECIFICATION, WHATS-LEFT, WINDOWS-PORT-PLAN, WINDOWS-SETUP.

## WS1 — your R87 was right and I verified it
**`dasham f = 3.5` gives `3.500000`. `vitti f = 3.5` is refused with `E_DASHAM_VITTI`. `dasham` arithmetic gives `2.500000`.**

**The refusal is the right fix - not making `vitti` hold floats, but stopping it from lying.**

## WS2 — the two goldens you added
**289 and 290.** **Say in one line each what they pin, so the next person knows why they exist.** **If either would fail on a legitimate future change, say which and why.**

## WS3 — and the one small thing
**`README.md` does not mention the `kosh` alias.** **The reference does.** **Add one sentence to the README pointing at it, so a reader who only reads the README is not surprised.**
