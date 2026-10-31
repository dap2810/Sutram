# Sutram — ROUND-84: the assumptions page, finished and verified

**Base:** main at v278 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour — each line run on v278, with the CASE it was tested in

**Diverges:** `kosh k[1]; kosh_push(k,41); vitti a = k; vitti obstacle = nirmmita(64); kosh_push(k,42); k[0]=99` -> `a[0]=41, k[0]=99`. The obstacle blocks in-place extension, so `k` relocates and `a` stays.
**Agrees:** the same WITHOUT the obstacle -> `a[0]=999, k[0]=999`. In-place extension succeeded, nothing moved.
**Census (Muse R83 and Claude R85, independently): 3 aliases total, 1 that grows, 0 that grow with an intervening allocation.**
**Claude R85: refusing `vitti a = k` breaks 3 programs. A forwarding pointer costs 3 instructions and 8-16% per read. The divergence cases are stale handles to LIVE blocks, so the guard page catches nothing.**

## Your census settled the whole question

**3 aliases, 1 that grows, 0 with an intervening allocation.** Claude's independent count said the same — refusing the copy breaks 3 programs.

**So the answer is document, not fix.** **And your census is why — three numbers ended two rounds of argument.**

## WS1 — the assumptions page, as a real document

**You produced `R83-THE-ASSUMPTIONS-PAGE.md`. Turn it into what `docs/LANGUAGE-REFERENCE.md` needs:** a section, in the reference's voice, that a student finds before they are confused.

**For each entry: the assumption, what Sutram actually does, and one line of code showing the difference.**

**The four known ones:** `tak` inclusive · `nirmmita` bytes vs `p[i]` qwords · division truncates toward zero · `vitti a = k` is a second name, not a copy.

**And find the fifth.** **Every language has a list like this; ours has at least one more and nobody has looked.**

## WS2 — and the verification
**Every line of the page must be true of v278.** Run each one. **If any is wrong, say so rather than adjusting the wording to match a guess.**

## WS3 — and one number I want for the release notes
**How many of the 259 examples in `examples/` would a student arriving from Python or C misread on the first attempt?** **Not "which are advanced" — which would they read correctly and get the wrong answer.**

**A count, and the three most likely.**
