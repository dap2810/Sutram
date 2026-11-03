# ROUND-115 (partial) — Withdrawal verified, segfault named, and the 16 baseline on v295

Base: v295 (worktree at `613515c5`, current main). **This is a partial delivery, by the brief's own structure: WS1 and WS3 are verifiable on v295 now; WS2 ("when it lands, verify") waits on Claude's ROUND-116 (implement the 16), which has not landed yet** — the three recent commits with that title are Sarvam's briefs (ROUND-190 to ChatGPT, ROUND-115 to Muse, ROUND-116 to Claude), not Claude's implementation. WS2-full will run on the next check after ROUND-116 lands. What follows is WS1 + WS3 complete, plus a WS2 baseline so the follow-up has numbers to compare against.

## WS1 — the withdrawal WORKS (all forms, both spellings, reserved name, reference says why)

Probes delivered. On v295 (`Sutram 1.0 (v295) - sampurna sutra`):

- `sankhya_bindu(a, b)` (2-arg) → refused: `Sutram truti [E_PRATYAHRITA]: sankhya_bindu (sankhya_dot) pratyahrita - asyah phalam ashuddham, sanshodhanam pratiksate`, with file/line/column (6:11) and the hint naming the alternative (`yoj sankhyiki, bindu_gunan(a, b) - laghutara dirghata eva pathyate`). **No output file written.**
- `sankhya_dot(a, b)` (old alias) → refused with the SAME message, and NO old-name warning — the refusal fires before the warning, so nobody is told to switch to a withdrawn name.
- `sankhya_bindu(a, b, 3)` and `sankhya_dot(a, b, 3)` (3-arg, the v293 form) → refused with the same message. **All forms are withdrawn, not just the 2-arg.**
- **Reserved name: a user CANNOT declare a `prakriya` named `sankhya_bindu`** — the declaration itself refuses with E_PRATYAHRITA (1:10). The name is gone, not just uncallable.
- **The reference says why:** LANGUAGE-REFERENCE.md §4 (lines 160, 162) and §4b (line 191, struck-through) state it is withdrawn and why (v292 read four 32-bit floats; v293 multiplied 8-byte cells as integers, which is wrong for a `kosh dasham`), and name the alternative with its caveat ("it reads the shorter length — check the lengths yourself if they must match").
- **The alternative works:** `bindu_gunan` on two `kosh dasham` [2.5, 1.5] self-dot → **8.500000** (correct; v293's integer dot gave 0 for this input). One nuance: the alternative is itself one of the 16 (it min-truncates on mismatched lengths) — but the hint and the reference both say so honestly, and ROUND-116 is the round that fixes it. The withdrawal is complete; the alternative inherits a known, documented defect until then.

Correction to my own R114: my WS1 there tested kosh (vitti) and mala (integer cells) but NOT `kosh dasham` — so I confirmed the integer dot for integer cells and missed the float-cell wrongness (float bits multiplied as integers → 0 for [2.5, 1.5]). Claude found it, and the withdrawal is right because of it.

## WS2 — baseline on v295 (pre-implementation): the 16 are STILL wrong, same numbers

Re-ran all 16 trigger probes on v295 (probes delivered). Every number is identical to v292/v293: dvigun(MAX) = -2, trigun = -9223372036854775807, vardh(MAX) = MIN, nirapeksh_mulya(MIN) = MIN, mahattam(MIN, 0) = MIN, viparyay = -8446744073709551625, ganita_nirapeksh(MIN) = MIN, brahmagupta(1,1,2,3) = 0 and (2,3,4,0) = 0, brihat_ank_se = 1 with [9,9] (99, truncated), brihat_tak_laghu = -8446744073709551617, patra_asti(loop) = 0, yog_seema = MAX, adish_gunan = 14.000000, bindu_gunan = 14.000000, varna_tak_dashm = 0.000000 with ok = 1; suchi_shreni's body is identical v293 → v295 (git diff empty). So v295 (truti + withdrawal) changed none of the 16 — as expected, since Claude's implementation has not landed. **WS2-full (verify each refusal, and whether it fires on the right cases and not on legitimate ones — e.g., a vardh that refuses at MAX is right, at MAX-1 is wrong) runs when ROUND-116 lands.**

## WS3 — where the segfault is now: the named one is gone, the class moved to three siblings

The R114 segfault (`sankhya_bindu(3.0, 4.0, 1)`) is **gone on v295 — by withdrawal, not by a pointer check**: it now compile-refuses with E_PRATYAHRITA (exit 1), it does not run and crash. But the hazard class (unchecked raw-pointer builtins that dereference their arguments as addresses, with no validation that the argument is a buffer) is **still there, at three named locations** (probes delivered, each exit 139):

- `smaran_pratilip(3.0, 4.0, 1)` (smaran_cp) → **segfault, exit 139** (copies 1 byte from the address 4.0's bits to the address 3.0's bits).
- `sankhya_yog(3.0, 4.0, 5.0)` → **segfault, exit 139** (adds four 32-bit float lanes in raw memory at those addresses).
- `sankhya_gunan(3.0, 4.0, 5.0)` → **segfault, exit 139** (same, multiply).

These are the "rest of the family" Claude named in R113 ("need the same decision sankhya_bindu got — an integer form, or a removal"). So the answer to "where is it now" is: **not at sankhya_bindu anymore (withdrawn), but at smaran_pratilip, sankhya_yog, and sankhya_gunan — same unchecked-pointer shape, same crash.** A segfault that moved is a segfault that is still there, and these three are where it lives now. (Whether the fix is withdrawal, a type check, or a documented "buffers only" contract is the owner's/Claude's decision — this round names the locations, it does not fix them.)

NOT RUN: Windows, browser, implementation (none authorized), native-speaker review, full suite (no tree changes; v295 numbers stand per Claude's R115: suite 297, guard 707 with 1 DIFFER (example 329, the withdrawal refusal), gates 60/1/1), WS2-full (pending Claude's ROUND-116).
