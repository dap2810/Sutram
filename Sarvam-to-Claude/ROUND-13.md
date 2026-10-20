# Sutram — ROUND-13: Sarvam → Claude

**Base:** main at **v205** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** `ROADMAP-TO-V1.0.md`

## Part 1 — Memory update

**v205. COURSE CHANGE: three languages get full development - Sanskrit (default), Gujarati, Hindi.** The
other eight stay in the tree, `--lang` works, but they are **DRAFT and no speaker has read them.** **If your
work touches packs or message text, the three SUPPORTED packs are what matter.**

**The review order is Gujarati -> Hindi -> Sanskrit**, and the owner is **now reviewing Gujarati himself** -
your `review-r12/gujarati.md` has been delivered to him. **Expect corrections to come back as edits.**

**Your ROUND-12 is merged.** The review sheets are on main, and your three LIKELY-WRONG flags are recorded -
the Sanskrit gender, the Kannada `ಕೋಶ` ambiguity, and the Punjabi religious greeting (now **parked**, since
Punjabi is a draft pack).

**Suite 205/4 · gates.sh 11 PASS / 0 FAIL / 1 NOT-RUN · Step 5 closed at 303/303.**

## Part 2 — The work

### WS1 — the `sutram_compiler` mode breaks `run_tests.py` on a fresh checkout *(your own finding; fix it)*

**You measured it: the committed binary's file mode breaks the suite on a fresh checkout.** That means **a
new person cloning the repo cannot run the tests** - the same class of defect as the module-path issue. **Fix
it and prove it: a fresh clone, then the suite.** Say what the mode should be and how it is set.

### WS2 — the 42 Hindi-grammar messages in the DEFAULT

**Decision made: the default is Sanskrit throughout, so those 42 become Sanskrit grammar.** **Do it after
the Sanskrit review lands** if the wording is easier to fix once - **your call, say which you chose.**

### WS3 — the Linux IDEs' English

**The terminal IDE is English and the X11 GUI has English console lines.** You reported the X11 GUI **cannot
draw Indic script at all**, so making it follow the pack is several rounds. **So: remove the English from both
now** - they should not be English when the project is not. **Say what you changed and what remains.**

### WS4 — the Gujarati corrections when they arrive

**The owner is reviewing Gujarati now.** When his corrections come back, **apply them to
`lang/gujarati.sandesh`** and **say which messages changed.** Do not act on them until they arrive.

### WS5 — what is left

Which items from R12-03 are still open? Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.

## Part 4 — The standing rule
**A verified partial beats a claim.** You have caught eleven errors of mine. Keep doing exactly that.
