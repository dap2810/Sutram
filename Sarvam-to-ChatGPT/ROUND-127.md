# Sutram — ROUND-127: write down what the language already does

**Base:** main at **v394** · **Deliver into:** `ChatGPT-to-Sarvam/`

**Read first:** `docs/WHATS-LEFT.md`, `docs/LANGUAGE-REFERENCE.md`, your own `ROUND-126-STYLE-SANSKRIT.md`.

## Why this round
**You found that `likha("x = ", x)` already works, and that the brief's premise was wrong.** **Claude measured it and Muse
counted it: 135 examples use the three-statement form for something the language does in one.**

**So the biggest documentation gap in this project is not a missing feature - it is a feature nobody wrote down.**

---

## WS1 — document the print forms

**In `docs/LANGUAGE-REFERENCE.md`, write the complete truth about output:**
- **`likha(x)`** - one value, with a newline
- **`likha("label", x)`** - **the form that already works and no example uses**
- **`likha(fd, buf, len)`** - **the raw write, three arguments, first is an fd or `1`.** **Say plainly that this is why a
  string literal must come first in the new form.**
- **`lkhb(x)`** - what it does today, **including that a `dasham` prints raw bits until R52 lands.**
- **`likha_fmt(fmt, v)`** - and that it still needs a newline.

**Every form with a runnable example and its exact output.** **That is the section a beginner reads first.**

## WS2 — document the loop forms

**`chakra i = 0 tak 10 { }` is the counted loop and it already exists.** **Write it down with an example.**

**And note `tak` is Hindi/Urdu, with `arabhya ... paryantam` as the Sanskrit alternative landing in R52.** **Say which is
which, honestly.**

## WS3 — the speakable verdict, as a section

**Your R126 said the forms are readable range phrases but not fully grammatical Sanskrit sentences.** **That is the honest
answer and it belongs in the reference, not buried in a handback.**

**Write a short section: what Sutram's syntax IS in Sanskrit terms, and what it is not.** **If it is a technical compound
register rather than prose, say so.** **A learner should not be told the code reads as poetry if it does not.**

## WS4 — and the one thing to keep asking
**For every form you document, ask: does an example exist that uses it?** **If not, say which example should.** **Muse is
migrating them in R52; your list is the check on that.**

---

## Return
`ROUND-127-REFERENCE.md` - the sections written, as a TSV of exact insertions against `docs/LANGUAGE-REFERENCE.md`, in the
`path | mode | anchor_exact | insert_exact_line` shape you used in R123. **Plus the list of forms with no example using
them.**
