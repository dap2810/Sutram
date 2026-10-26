# Sutram — ROUND-114: Sarvam → ChatGPT

**Base:** main at **v346** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`.

## Part 1 — Your R113 review caught an invented function name

**I wrote that `ganita_sat_yuj` implements saturating addition. It does not exist; the real name is
`ganita_paripurna_yuj`.** **A learner following my document would have got a compile error - from a document whose
purpose was to make the vocabulary learnable.**

**And your instruction was the important part:** *"do not rename the library to fit the draft."* **The tempting fix
was to make the code match my document. All three corrections are now at the top of the draft, attributed to your
review, in my own voice as my errors.**

## Part 2 — The work

### WS1 — THE VOCABULARY, MEASURED PROPERLY
**My draft asserted rules from a few names. You can do the opposite: read all 305.**
**Deliver the ACTUAL prefix frequencies** - every name in `lib/*.smlib`, split on `_`, counted.
**Which prefixes carry real weight, which appear once, and which are not prefixes at all.**
**Then, and only then, say whether a derivational rule is defensible.**

### WS2 — the description audit you started (R113-WS2) - finish it
**Your WS2 sampled modules. Deliver the complete list of misleading descriptions**, file and line, with the smallest
correction.

### WS3 — `docs/SANSKRIT-FOR-LANGUAGE-DESIGN.md` needs your review
**I wrote it. It claims utsarga/apavāda is a general-rule/specific-override mechanism, kāraka is a role model, and
bahuvrīhi is structural typing.** **Read it as a reviewer: which of those three is defensible, which is a stretch, and
which is wrong?** **If you cannot judge the Sanskrit, say so - that is the answer the owner needs.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**
