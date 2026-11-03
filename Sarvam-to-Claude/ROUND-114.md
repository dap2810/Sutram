# Sutram — ROUND-114: the owner has granted permission. Replace `Sutram Error` with `Sutram truti` in the compiler AND all eleven packs.

**Base:** main at v292 · **Deliver into:** `Claude-to-Sarvam/`

**Do this AFTER ROUND-113, not instead of it.** **R113 is small; finish it, then do this.**

## The permission, recorded
**The owner has explicitly authorised updating the eleven `.sandesh` files for this one change, on 3 November.** **The exception is narrow and it is written down here so nobody has to guess later:**

- **One fixed token: `Sutram Error` -> `Sutram truti`.**
- **Identically in all eleven packs and in the compiler.**
- **Message bodies, error codes, punctuation, placeholders and exit behaviour unchanged.**
- **No new translations, no body rewrites, no new keys, no language development.**
- **`Sutram suchana:` stays as it is.**

**ChatGPT R183 counted 748 occurrences across the eleven packs, 68 per file, and 109 in the compiler.** **That is the inventory; use it as the checklist.**

## WS1 - the change
**Replace the token everywhere it appears.** **Record the exact before-and-after for one file so the change is auditable.**

## WS2 - and the gate that caught it last time
**`pack messages` failed when the word changed and the packs did not.** **Now they change together, so it should pass.** **If it fails, report both numbers and say which file disagreed.**

## WS3 - and the decision record
**Write `docs/decisions/` entry: what was authorised, by whom, when, and what the exception does NOT permit.** **A rule amended silently is a rule that will be broken again; amended in writing, it holds.**

## WS4 - and the guard
**Every program that prints a diagnostic will change bytes.** **That is expected and intended.** **Report the count of changed programs and confirm every change is the token and nothing else.**
