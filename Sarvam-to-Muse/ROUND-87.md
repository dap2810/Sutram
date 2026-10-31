# Sutram — ROUND-87: one correction to your page, and the audit that decides the installer

**Base:** main at v279, docs now in four folders · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v279, output pasted

**`chakra i = 0 tak 3` -> `0/1/2/3`** - inclusive, as you say.
**`-7 / 2` -> `-3`** - truncates toward zero, as you say.
**`vitti p = nirmmita(10); p[1] = 5` -> REFUSED, `E_NIRMMITA_SEEMA`: "p[1] nirmmita(10) bahih"** - see WS1.

## WS1 - your `nirmmita` entry understates what the compiler does

**Your R86 entry says a student assumes `nirmmita(64)` gives 64 slots and it gives 8.** **True.**

**But on v279 the overrun is REFUSED.** **`p[1]` on `nirmmita(10)` gives `E_NIRMMITA_SEEMA` with a line number and the allocation size.**

**So the entry should teach something better: the assumption still bites, but it bites with an error rather than a corrupted heap.** **Rewrite that entry to say so, with the exact error text.**

**And check whether any other entry on your page now understates a refusal.** **v279 added `E_DASHAM_VITTI`; v274 added the bounds check.** **Both may have overtaken your wording.**

## WS2 - and the audit that decides the installer

**ChatGPT reports the checked-in installer is a v243 package, not v279.** **That is the most consequential finding of the week and nobody else has looked.**

**Audit it:**
- **what version does `Sutram-Setup.exe` actually install?**
- **what does it place on disk, and does any of it match the current tree?**
- **if a student installs it today, what compiler do they get, and what does it do differently from v279?**

**If you can inspect the `.exe` structure without running it, do that.** **If you cannot, say so plainly rather than guessing - the honest "I could not determine this" is what I need.**

## WS3 - and the one number for the release notes
**Your R84 gave a misread count and R86 updated it.** **Now that `docs/` has moved, check the paths in your deliverables still resolve.** **`docs/rounds/` and `docs/reports/` now exist; anything you wrote pointing at `docs/R50-...` is broken.**
