# Sutram — ROUND-86: document the alias, and make the assumptions page real

**Base:** main at v278, suite 255, gates 57 PASS · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour — each line run on v278, with the CASE it was tested in

**Diverges:** `kosh k[1]; kosh_push(k,41); vitti a = k; vitti obstacle = nirmmita(64); kosh_push(k,42); k[0]=99` -> `a[0]=41, k[0]=99`. The obstacle blocks in-place extension, so `k` relocates and `a` stays.
**Agrees:** the same WITHOUT the obstacle -> `a[0]=999, k[0]=999`. In-place extension succeeded, nothing moved.
**Census (Muse R83 and Claude R85, independently): 3 aliases total, 1 that grows, 0 that grow with an intervening allocation.**
**Claude R85: refusing `vitti a = k` breaks 3 programs. A forwarding pointer costs 3 instructions and 8-16% per read. The divergence cases are stale handles to LIVE blocks, so the guard page catches nothing.**

## Your R85 settled it, and I accept the answer

**Option 1 breaks 3 programs. A forwarding pointer costs 8-16% per read. The divergence is stale handles to live blocks, so nothing faults.**

**Given 3 - 1 - 0, the answer is DOCUMENT. Do not build a fix, do not refuse the copy.**

## WS1 — the documentation, and it must be precise

**In `docs/LANGUAGE-REFERENCE.md`, a section a student will find.** It must say:
- **`vitti a = k` makes a second name for the same `kosh`, not a copy.**
- **If `k` grows and cannot extend in place — because something else was allocated in between — `k` moves and `a` still points at the old buffer.**
- **Reading through `a` after that gives the old data. Writing through `a` does not affect `k`.**
- **Nothing in the standard examples does this, and a program that does not alias is unaffected.**

**One worked example with its actual output, taken from your `evidence-r85/`.** Not a description — a program and what it prints.

## WS2 — and the assumptions page

**Muse is writing it.** Do not duplicate. Instead: **check Muse's page against the compiler and report any claim in it that is wrong.**

**A page of "what you will assume wrongly" is only useful if every line is true.**

## WS3 — and the regression test that keeps the documentation honest
**Add a golden that pins the current behaviour: the obstacle case, printing `a[0]=41 k[0]=99`.**

**If anyone ever fixes the alias, that golden fails — which is exactly what you want, because the documentation would then be wrong.**
