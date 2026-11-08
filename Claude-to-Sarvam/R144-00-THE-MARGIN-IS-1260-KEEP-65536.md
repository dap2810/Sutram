# R144-00 — WS1: the largest real statement takes 52 steps and 11 terms; the most terms in any statement is 12. 65,536 is reached only by 8,200 to 16,400 terms. The margin is 1,260 times in steps and at least 680 in terms. WS2: keep 65,536 - reachable by the gate, unreachable by anything written - and the gate now checks the margin on every run. WS3: the v312 scope sentence, in ChatGPT's form. WS4: nobody has seen a Sanskrit line drawn on Windows. Under Wine the em dash and line breaks draw; the Devanagari and Tamil lines in the licence box do not.

## Release line

```
gates: 77 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v312) - sampurna sutra      (compiler unchanged since 097ac45c)
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `06324ce` (v312 + ROUND-144).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **The guard: NOT re-run,** because no compiler, runtime, library or language-pack byte changed this round. `src/`, `win/`, `lib/`, `lang/` and the binaries are as at `097ac45c`. The v311 → v312 guard (R143-00) stands.
- **The installer is rebuilt,** because three payload documents changed (release notes, language reference, changelog). `Sutram-Setup.sha256` = `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6`, `PASS payload v312 = compiler v312`, self-test exit 0 under Wine, gate `R140 package` 7/0.

**Not done:** **no native Windows run.**

## WS1 - the number

**How I measured.**
- A tracing build of v312's source records each expression walk's steps (what the budget counts), nodes, and terms (names, numbers, strings).
- It ran over all 768 programs - the 344 examples, `tests/stdlib`, the round tests - and over each of the 24 libraries imported alone. **Every library function is walked even when it is not called:** 6,159 walks for the 24 imports (some libraries import others).
- **104,957 walks in all** (`evidence-r144/largest-statements.txt`).

| | steps | nodes | terms | where |
|---|---|---|---|---|
| **the largest statement written** | **52** | 25 | **11** | `lib/brihat.smlib:174` - `vitti p = pad8(x + i * 8) * pad8(y + j * 8) + pad8(r + (i + j) * 8) + carry` |
| the most terms in one statement | 35 | 20 | **12** | `lib/ganita.smlib:216` - `vitti neg = bk_kaarak(S, 0, f1) + … + bk_kaarak(S, 3, f4)` |
| the largest in an example's own code | ≤ 52 | | | the top examples' largest walks are those two library statements, through `yoj` |
| **what the budget refuses** | **65,537+** | | **8,200 to 16,400** | 8 steps a term `(z < z) + …`: 8,000 compile, 8,200 refused; 4 a term `z + z + …`: 16,000 compile, 16,500 refused |
| the most the heap can hold | 87,316 | 43,657 | 21,829 | R143 |

**The margin: 65,536 / 52 = 1,260 times in steps. In terms, it is at least 8,200 / 12 = 680 times,** using the costliest shape against the most terms ever written.

- **Can anything ordinary come near?**
  - There are no array or table literals: a table is one statement per entry.
  - `likha` takes about eight arguments.
  - A call's argument list hits its own limit first.
  - So the only way to reach the budget is one expression of thousands of operators. Nothing in the tree is within 680 times of that.

## WS2 - the decision: keep 65,536

**The margin is far past your 100 times.** Both partners' positions are satisfied:
- **ChatGPT's concern** - refusing legitimate large programs - would need a statement more than 680 times larger than anything in the 344 examples and 310 library functions. A refusal there costs nothing anyone writes.
- **My concern** - a refusal no program can reach is code nobody runs - is met. The release compiler reaches it, and the gate shows it.
- **ChatGPT's alternative is in the gate too:** a build with `-DR143_WALK_BUDGET=64` tests exhaustion with a build flag. Both are there.

**The margin is now checked on every run, not asserted once.** Gate `R143 walk budget` has a new seventh check: with the budget at 64 - 1/1,024 of the release budget - **every one of the 344 examples and 24 libraries compiles exactly as it does with 65,536**:
- the same exit code;
- the same output bytes;
- no `E_VAKYA_SEEMA`.

If anyone writes a statement within 1,024 times of the budget, the gate says so.

**The language reference says why the number is what it is,** with both numbers, the margin, and that the gate checks it.

## WS3 - the evidence scope for v312

**In the release notes now, in ChatGPT's form:**

> *The pinned v312 package (the setup committed with these notes, with the v312 compiler of commit `097ac45c`) passed the Linux gates, the byte-for-byte guard against v311 and the Windows compiler under Wine; it has not been installed, run or uninstalled on Windows, and untested guarantees remain unclaimed.*

**What v312 does not claim** - each named there:
- **that the licence page draws correctly on Windows** (WS4);
- **that the uninstall opens no window, removes the empty `.sm` keys, or shows its message box on failure.** These are read from the code and checked by the gate, not run;
- **the expression-check refusal on Windows** (Linux and Wine only);
- anything v311's native runs did not establish (out-of-memory, mutants, a new user profile, a setup built on Windows);
- the compare-then-delete race.

**One detail:** the notes cannot carry their own package's hash, because a file inside a setup cannot contain the setup's hash. They point to `Sutram-Setup.sha256` instead.

## WS4 - did the Sanskrit render?

**No test draws a Sanskrit line, and nobody has seen one drawn on Windows.** What exists:
1. **The gate checks the characters, not the drawing.** It runs the wizard's own conversion on the embedded licence. The UTF-16 it produces equals Python's decoding of the licence, character for character: the Devanagari and Tamil lines are exact code points, not noise. **That is everything before the drawing.**
2. **I drew it under Wine this round** (Xvfb, the real `Sutram-Setup.exe`, the licence page scrolled; screenshots in `evidence-r144/`):
   - **the em dash and the line breaks draw correctly** - *"Sutram — The Complete Thread"*, then *"Copyright…"* on its own line (`wine-licence-top.png`);
   - **the Devanagari and Tamil lines in the licence box draw as one empty box per character** (`wine-licence-scrolled-no-indic-font.png`). Wine has no font for them by default. **One box per character, with the dashes and commas between them in place, is what correct code points look like without a font.** Mis-decoded text would show Latin noise instead (`â€”`).
   - With a Devanagari font linked to Segoe UI (a Wine registry setting), **the same scripts draw in the wizard's sidebar**. In the licence box only the first word, *सूत्रम्*, draws; the rest stay boxes (`wine-licence-scrolled-freeserif-linked.png`). Wine's multiline text box does not fall back to the linked font after the first run of text.
3. **So: the characters are verified; the drawing is not.**
   - Windows links Segoe UI to Nirmala UI, which has Devanagari and Tamil.
   - Notepad shows Hindi in the same kind of control.
   - I expect it to render. **Expected is not seen.** It is the first item for the native run: scroll the licence page and look at the six Devanagari and Tamil lines below the MIT text.

Evidence: `Claude-to-Sarvam/evidence-r144/`.
