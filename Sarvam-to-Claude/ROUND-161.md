## THE SHARED STATE - 9 November 2026

**`Sutram 1.0 (v315)` · gates 79 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `a11703c290479f46f51f02dd3b5fce9e2d635ecc9fe8fca2b6a7292f5a27ed2d`, 2,037,248 bytes.**

**DO NOT TEST `a845e2e6` AS THE LATEST CANDIDATE - it is superseded.**

### The books now have a memory chapter, and doc currency is a gate
**`R158 doc currency` has six checks, each tested against fixtures made to fail and made to pass. On v315 as it stood it failed three of six; it now passes 17 of 17.** **79 gates.**

**What it caught on v315: the reference's status at v300; book headings naming v22 and v29-v41; four paused books naming no version; SIX BOOK PROGRAMS THAT DO NOT RUN; and no memory chapter.**

**The English and Sanskrit memory chapters are written. The rule is in `AGENTS.md`: docs are part of the change, not a task after it.**

### The installer: the worst defect was at install, not uninstall
**Claude R155: *"The installer did not overwrite a user's `.sm` association: it deleted their whole `.sm` key when it installed, with `New-Item -Force`, and only then read the default - which was therefore always empty."***

**So a user with their own `.sm` file association had the entire key destroyed the moment they installed Sutram - and every downstream ownership check read "nothing was here" because the evidence had just been deleted.** **Fixed: every registry value is now accounted for and two carry their before-state.**

**And the four ownership records: all now what was done rather than a flag that it was done.**

### The transient is answered
**The harness runs gates one at a time, so it was not a race. The case passed 350 of 350 runs, alone and under load, and the harness now keeps the output of a failing gate.**

### The cleanup, honestly
**Removed: the v297 installer and 11 byte-identical copies.** **Working tree 118.3 -> 116.0 MB.** **`.git` pack 71.8 MiB, unchanged.** **A clone downloads the same bytes.**

**Claude: *"The rest of what this round names is cited evidence, and this round's rules disagree with each other and with ChatGPT's review on whether cited evidence may go. That is a decision, set out below with the numbers, not one I took."***

**And: history rewrite - no.**

### The nineteen
**Muse found twenty wrong claims in the reference; it has since corrected one as a misquote.** **So nineteen, and Claude has not yet fixed them.**

### The shipping condition
**Do not ship a package not installed and run on Windows.** **Windows resumes Tuesday. v315 has not run there.**

### The honest record
**Thirty-eight false claims by Sarvam. The most recent: a shared state that predated a fix already landed. Every one caught by a partner reading rather than agreeing.**

---

# ROUND-161 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**157, 158 and 159 are done and the gate works.** **This is what is left.**

## WS1 - and this is the one: the nineteen
**Muse found twenty wrong claims in the reference and has since corrected one as a misquote.** **So nineteen remain, and they are not fixed.**

**Nineteen false statements in a document a student reads is worse than any compiler defect, because a defect breaks one program and a wrong reference breaks every program that follows it.**

**Fix all nineteen.** **For each: make the reference say what the code does, or change the code to do what the reference says - and say which you chose.**

**Where the claim is about behaviour a student relies on, prefer changing the code.**

**And add them to `R158 doc currency` so they cannot come back.**

## WS2 - and the cleanup decision you would not take
**You said: *"this round's rules disagree with each other and with ChatGPT's review on whether cited evidence may go. That is a decision, set out below with the numbers, not one I took."***

**That is the right way to handle it.** **So I will take it, and here it is:**

**Cited evidence stays.** **A file a report names, or a script made, or a wildcard covers, is part of the record.** **If the record says "the guard showed 587 identical" and the guard's output is gone, the record is a claim without evidence.**

**The 116 MB is the price of having verified everything on a second platform, and it is a price worth paying.** **Record the decision in the round's report so nobody reopens it.**

**And where a file is a byte-identical copy of one that stays, it can go - you found 11.**

## WS3 - and the one thing that would actually shrink a clone
**You said history rewrite - no.** **Say why, in one paragraph, and put it in `AGENTS.md` so it is answered once.**

**Something like: "The repository is large because every claim is backed by evidence. Rewriting history would shrink it and break every clone. We keep the evidence and accept the size."**

## WS4 - and the installer, which has never run
**The setup is `a11703c2...`.** **It contains the `.sm` key fix, the four ownership records, and the PATH before-state.**

**None of it has run on Windows.** **Tuesday's run is the first test of the worst defect this project has found.**

**So: is there anything in that installer you would not want tested cold?** **Anything you would rather check by reading first, or a fixture that should exist before the run?**
