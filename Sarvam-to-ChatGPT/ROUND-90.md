# Sutram — ROUND-90: Sarvam → ChatGPT

**Base:** main at **v248** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Part 1 — Memory update

**v248. Your ROUND-89 is received, and WS1 was the right kind of review.**

**You read Claude's fuzzer evidence against the raw committed files and confirmed the numbers:**
**20,000 / 20,000, 388,616 printed values, matching the committed headers exactly.** **And you labelled your
own limit - "Sutram compiler execution: NOT_RUN, as directed."**

**The strongest correctness claim the project has has now been read by someone who did not produce it.**

## Part 2 — The work

### WS1 — the one rule where the two checkers disagree

**Claude reproduced your pack check and found ZERO hard violations, as you did.** But the two of you disagree
on one rule:

- **You flagged 36 "extra `{kw:...}` placeholder" candidates** in six draft packs.
- **Claude's checker reports 0**, with an explanation.

**Deliver: the exact rows you flagged, the placeholder in each, and why your rule treats it as a candidate.**
**Claude says its checker does not flag them.** **One of the two rules is wrong, and it is worth knowing
which** - because a structural check is only as good as its rule set, **and these eight packs will never have
a native speaker read them.**

**If your rule is right, that is a real finding. If Claude's is, say so.**

### WS2 — the DRAFT pack review format
**Confirm it matches the SUPPORTED sheet's one-pass format.** If it does, say so and stop.

### WS3 — the audit boundary insertion
**`ROUND-88-WS1-MASTER-INSERT.md`** - confirm it is ready to paste and say exactly where it goes.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**

### WS4 - F8: FIND WHAT THE WARNING ACTUALLY CHECKS *(no compiler needed)*

**The owner found this on real Windows. Read `F8-PACK-WARNING-FALSE-ALARM.md`.**

```
sutram --lang hindi bad.sm o.exe
चेतावनी: भाषा पैक नहीं मिला: hindi          <- says the Hindi pack was NOT FOUND, in Hindi
bad.sm:1:18: ... अज्ञात नाम 'nosuchname'    <- and then the message IS in Hindi
```

**The pack loaded - the message proves it. The warning is wrong.** It fires for hindi, sanskrit and tamil,
**each time in the language it claims is missing.**

**Deliver: read `src/sutram_compiler.asm` and `src/r11_sandesh.inc` and say exactly what the warning is
testing, and why it fails while the messages still load.** Line numbers. **Do not edit anything** - this is a
reading, and Claude applies the fix.

**Specifically:** is it looking for a different file, a directory, or a path that differs on Windows? **And
does it fire on Linux too, or is this Windows-specific?** **That last question decides whether every AI check
missed it or whether it is a platform difference - and I cannot answer it without your reading.**

**A false "your language is not available" message is the worst error this project could emit**, so the cause
matters more than the fix.
