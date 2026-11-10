# AUDIT-01, the fixes — The owner read the audit and said: fix those, and give it to Sarvam with the probes. **Five of the six defects are closed, staged as v322.** **84 of the 783 guard programs differ in bytes; all 84 were run on v321 and v322 and print and exit the same; none is newly refused.** The sixth defect and the eight messages are not done, and I say why. **The 150 probes, re-run on v322, changed in exactly the fifteen places they should.**

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged audit-01-fixes (SHA in the follow-up commit)  Sutram 1.0 (v322) - sampurna sutra   (on v321 r182-unknown-character c0fdebe8; NOT merged)
     crash corpus, suite, gates: ITS FULL GATES WERE STILL RUNNING at this first push - NOT YET A RESULT (next commit)
     guard, the ordinary way, 783 programs, ELF and PE, against v321:
            503 byte-identical, 196 refused identically, 84 DIFFER, 0 newly refused
            all 84 run on v321 and on v322: 84 print and exit exactly the same (evidence-audit-01-fixes/differ-outputs.txt)
     installer rebuilt (payload v322): e6eb61f3536158c951bc1d99c7c7140b7498fcf335843aaf5790d6214b08ef25
staged v321 c0fdebe8 · v320 fe90a9b1 · v319 4c1159be · 12ef6329 · v318 · v317 · v316-ready - unchanged
```

**This is not a round of yours.** The owner asked for the audit in chat on 10 November, chose "correctness" and
"report first", read `AUDIT-01-CORRECTNESS-...md`, and then told me to fix what it found and hand it to you with
the probes. **You have not judged any of this. Three of the five changes refuse programs that compile today, and
one changes what a program returns - those are language decisions and they are staged, not merged, so that you
can refuse them.**

**The guard does not read 0, and the set was not named before the run.** I can say what the 84 are - programs
with a `prakriya` that does not end in `nivartanam` (two more bytes each) or a `mala` whose length is not a small
number written out, most of them through the library they `yoj` - **but I did not write a script that predicts
the set, so by the rule as Muse read it this change satisfies "every changed program produces the same output"
and not "a stated list".** If you want the list predicted, that is a small piece of work I have not done.

Sanskrit only; no pack touched; `backups/` untouched.

## The five, each with what it was and what it is

| | up to v321 | v322 |
|---|---|---|
| **1** a `prakriya` that ends without `nivartanam` | returned whatever the last instruction left: `prakriya f(a) { vitti b = a * 3 }`, `f(5)` → **15**; after a summing loop, the loop's bound | **returns 0** - `xor eax,eax` at the end of a body whose last statement is not `nivartanam` (`a1_emit_fall_off`). A body that ends with `nivartanam` has the same bytes as before |
| **2** `krama` / `agrim` outside every loop of their `prakriya` | compiled, did nothing | **refused, `E_AVARTAN_VINA`**, at the word, with a `Sanket` (`chakra` or `yavat`; `nivartanam` to leave a `prakriya`). Inside a `prakriya` called from a loop too - the loop is the caller's |
| **3** `mala m[n]`, `n` negative or impossible | **SIGSEGV** - `mala m[-3]` compiled; a computed -1; 16 GB | `mala m[-3]` **refused when compiled**; anything not a small number written out **checked when run** - the length, and that memory was had: **`E_MALA_PARIMAN`, exit 1**. `mala m[8]` gets no new code |
| **4** `likha(m)` on a `mala` | printed the `mala`'s address | **refused, `E_MALA_LIKHA`** - in any position among `likha`'s values |
| **5** a `kosh` as a whole condition | always true, an empty one too | **refused, `E_KOSH_SATYA`** - `yadi (k)`, `yavat (k)`; the rule a string already has (`E_VARTANI_SATYA`) |

**The messages' Sanskrit is mine and unread.**

## The probes - what you asked for

- **`evidence-audit-01/`** - the audit's 150 probes: `probe.py`, the programs `b1.txt` ... `b7.txt`, what v321
  printed (`b1.out` ... `b7.out`), and findings 1-5 on v315 (`v315.out`).
- **`evidence-audit-01-fixes/`** - the same 150 on v322 (`b1-on-v322.out` ...), the nineteen programs written for
  the fixes (`fx.txt`, `fx.out`), the 84 (`differ-list.txt`, `differ-outputs.txt`), the gate on v322 and on v321,
  the 23 cases under Wine.
- **`python3 evidence-audit-01/probe.py b1.txt`** runs a batch (it needs the compiler as `./sc` beside it).

**Of the 150, on v322, fifteen lines changed and 135 did not:** the five mala-length probes (three SIGSEGV, now
`E_MALA_PARIMAN`), the four loop-word probes (now `E_AVARTAN_VINA`), the four no-`nivartanam` probes (now 0),
`mala_likha` and `kosh_as_cond`. Nothing else moved - including the 25 with a known computed answer.

**Gate `AUDIT-01 fixes`, `tests/audit01/test_audit01.py`: 23 checks; 15 fail on v321.** For each fix, the cases
that must now fail and the neighbouring cases that must go on working (`krama` inside a loop, `likha(m[0])`,
`mala m[0]`, a computed length that is fine, `yadi (kosh_gan(k) > 0)`, a `prakriya` that does end with
`nivartanam`). **Under Wine, with `win/sutram.exe`: 23 of 23.** Not run on Windows.

## Two other files changed, and why

- **`tests/r158/test_doc_currency.py`:** the changelog rule demanded `(who, R<number>)` in every version's heading.
  This version has no round. The rule now also accepts `AUDIT-<number>`.
- **`docs/LANGUAGE-REFERENCE.md`:** four rows added to the table of things that compiled once and are refused now.

## Not done, and why

- **Finding 6 - a `chakra` whose end is the largest number never ends.** The fix is an overflow test after the
  loop's increment, and the increment is emitted three ways (a module variable, a stack slot, a register). It
  would change the bytes of every program with a `chakra` for a bound no student writes. **I left it, and it is
  recorded in the release notes as open.**
- **The eight unhelpful messages** (an unclosed string, a missing `mukhya`, a `prakriya` after `mukhya`, seven
  parameters, seven values to `likha`, `yadi a == 1`, `yadi (a = 1)`, `1e5`). Each is its own small change in the
  parser; none is a wrong answer. Not started.
- **One thing seen on the way and not looked into:** `likha(3, "\n")` prints `3`, a newline, and a second newline,
  while `likha("a", 5, "\n")` prints `a5` and one. The reference says the last number adds a newline; whether the
  two forms are meant to differ I did not check.
- **ROUND-183 (queued)** - not started.
- **Windows** - Wine only.
