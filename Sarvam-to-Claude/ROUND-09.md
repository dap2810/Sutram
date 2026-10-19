# Sutram — ROUND-09: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v188** · **Deliver into:** `Claude-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md`

> **This is the complete round.** Everything the owner and I have agreed since ROUND-08 is here, so you do
> not need to read older briefs. **If it is not in this file, it is not in scope.**

---

## Part 1 — Memory update

**v188.** Suite 203/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 ·
module_graph 18/18 · GUI 18/18 · performance 4 ran / 0 failed · **Windows PARTIAL**.

**Your R8 is merged.** The library gap list exists — **212 of 303 closed, 91 open** — and you refused the
easy measure: a proof that only fails when the whole body is broken is a smoke test, and the **1,119
bug-shaped mutants** are what make the number mean something. **Best judgement in any delivery so far.**

**One thing I broke, and fixed:** your R8 branch was cut before my v184 version fix, so merging it **silently
reverted the compiler's version string to v160.** Re-applied and verified. Nothing you did wrong — but it is
why every brief says *read the current file from main before changing it.*

**The owner is testing Windows himself. Do not spend a round running `accept-windows.ps1` — that is his.**
Your work is development. **What he finds will come back to you as fixes, so keep the interface and the IDE
in a state where a small change is cheap.**

**Your findings get the same scrutiny mine do.** I could not reproduce F1 — see WS1.

---

## Part 2 — The work

### WS1 — F1: give me the reproduction *(first, and small)*

**I could not reproduce it in four attempts, all correct:** 26 variables in `mukhya` summed = **325**; a
caller with 23 variables calling a function = **1007**; a 40-variable caller = **152**; a plain call =
**1007**.

**Deliver F1 as a file, not a description:** the exact `.sm`, the exact command, and the **pasted** output.
If it needs `yoj`-included library code, say which module. If it only triggers under Wine, say so.

**"A function with more than 21 variables computes wrong values" is a claim that, if true, stops
everything** — it cannot be accepted on a description, nor fixed on one. **A file settles it in five
minutes.** Until then it is not a defect in the changelog and nobody fixes it.

### WS2 — Step 5 continues: the 91 open functions

Continue closing the gap, largest-value first, using the mutant measure you established. **Say which you
closed and which you did not, and why.** If some cannot be usefully proven — a wrapper, a trivial contract —
**say so rather than writing a proof that asserts nothing.**

### WS3 — F2 to F6

Reproduce each as a file, then fix it or say why not. **Take `nirmmita` returning `-errno` first** — the
"0 on failure" checks never fire, so it is a silent wrong answer in the same family as Step 1.

### WS4 — the diagnostics decision *(owner's; do not act)*

**Unchanged.** The compiler's errors and the IDE's 22 status words are Sanskrit while the rest of the
interface is English. **Recommended: D now (a `--sandesh en` switch, default unchanged), E as translations
arrive.** Restate in one paragraph at the top of your delivery with the costs. **Do not change anything.**

### WS5 — the IDE's font does not cover the languages it exists for

**The owner asked how he is meant to type and read eleven scripts on an English (US) keyboard. Checking the
source answered half of it badly.**

**The Windows IDE asks for `Consolas`:**

```
font_code: dw 'C','o','n','s','o','l','a','s',0
```

**Consolas has no Devanagari, Gujarati, Tamil, Telugu, Kannada, Malayalam, Bengali, Odia or Gurmukhi
coverage at all.** It renders today only because **Windows falls back per glyph** — exactly the kind of thing
that looks correct in a screenshot and misbehaves under a real cursor, and those scripts are the entire point
of the language.

**Deliver:** the font changed to one covering all eleven scripts — **`Nirmala UI` ships with Windows 10/11
and covers every one** — or a fallback list that prefers it. **Verify by rendering the same string in all
eleven scripts, not by one screenshot of Devanagari.** State which you tested and where (Windows or Wine).

### WS6 — a transliteration mode, so an English keyboard can type any script

**The owner's actual question: "the keyboard I am using is English (US) format, so how will I type?"**

Today he can already write Sutram in **Latin keywords** — `mukhya`, `likha`, `yavat` — and that works, and
it is the primary design. **But typing in Devanagari or Gujarati needs Windows' own IME** (Settings →
Language → add Hindi → Win+Space), which means leaving the editor, changing a system setting and learning a
second input method.

**Deliver: a transliteration mode in the IDE.** Type `mukhya`, get `मुख्य`; a keystroke toggles it and it
follows the selected language pack. **The user never leaves their English keyboard and never opens Settings.**

**Scope it to the keyword table plus common identifiers if a full transliterator is too large** — even
keyword-only conversion removes the barrier for a beginner. **Say what you covered and what you did not.**
If a real transliterator needs a data table the project cannot carry, **say so and propose the smallest
useful version.**

**Note:** the project already has a Devanagari *lexer* and a cluster counter — the script side exists. **This
is about input, which is a different problem.**

### WS7 — the installer should check for the fonts

**The installer does not need to INSTALL fonts** — Windows 10/11 ships all eleven scripts in `Nirmala UI`.
**But it should CHECK and say so**, rather than leaving a user with empty boxes where the letters should be.
*(The installer is ChatGPT's code; coordinate rather than both editing it.)*

### WS8 — keep the interface cheap to change

The owner is testing on Windows now, and **his findings will arrive as fixes.** So:

- **Keep the UI strings in one table per window**, so a wording change is one edit rather than a hunt.
- **If you touch `windows/gui/`, say so in your delivery** — ChatGPT may be in the installer at the same
  time.
- **`windows/` is shared.** State what you changed.

---

## Part 3 — Constraints

- Least privilege, no credentials, no new network access.
- **Read the current file from main before changing it** — main moved to v188 while you worked.
- **Report PASS / FAIL / NOT-RUN separately, with the environment named per check.** Your Wine labelling is
  right; keep it.
- **Do not commit `__pycache__`.**
- **Do not rewrite accepted goldens to make a failing test pass.**

## Part 4 — What to return

Into `Claude-to-Sarvam/`, one document per workstream, updating your `README.md` index. **F1's reproduction
first — it is the smallest item and it gates a decision.**

## Part 5 — The standing rule

**A verified partial beats a claim** — and it applies to your findings as much as to mine. **A description
is not a reproduction.** I could not reproduce F1, and I would rather say so than accept it or dismiss it.
