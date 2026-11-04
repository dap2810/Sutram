# R121-00 — Both builtins are fixed (v298) and wrong on Linux as proved. But no golden encoded the breakage: 322/323's `B42` / `abcd` were the right answers, which Linux printed by luck. Goldens that did record a wrong answer exist - three found and corrected before, by an independent oracle each time - and the honest count of goldens checked against an answer known in advance is small.

- **Commit on `main`:** `PENDING-SHA` (one commit; on top of your R120/R121 files, `c803cc0`).
- **Compiler: `Sutram 1.0 (v298) - sampurna sutra`** (was v297). Linux x86-64 cloud; PE run under Wine 64.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=315  (319 run)`**, FAIL=0 - no golden changed.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 63 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, payload v243, as before; NOT-RUN: Windows execution) - 65 gates now, with **`R121 builtins` (14 checks, 0 failed)**.
- **The guard, origin/main (v297) → v298, 725 programs** (`evidence-r121/guard.txt`):
  - **Linux ELF and Linux PE: 579 byte-identical, 143 refused identically, 3 DIFFER, 0 new.** The 3 are exactly the programs that call the two builtins: `examples/322`, `323` (whose text changed) and `tests/r54_check/raw_valid.sm`.
  - **Run old and new:** ELF the same output and exit for all 3. PE under Wine: **322/323 crashed on v297 (exit 5, a garbage byte) and print their golden on v298**; `raw_valid` the same.
  - **The Windows compiler under Wine: running; its line follows in the next commit.**
  - **The first run was discarded:** I had skipped the run-time check in `--object` mode, and the R28/R29 gates caught 322 compiled as an object no longer matching the direct build. Now a root object emits exactly what a direct compile does; only a module object (no `mukhya`) skips it. Rebuilt, everything rerun.
- **R118's Windows-compiler-under-Wine line is filled in its own hand-back** (it finished during this round).

## WS1 - proved on Linux, and which goldens encode the wrong behaviour: none

**Your premise needs one correction.** *"Linux hides because the golden was recorded from the same broken behaviour"* - **no: the golden is right.** `shabda(anka_akshar(66))` should print `B`, and `vartani_sandhi` of `ab` and `cd` should give `abcd`. 322's golden says exactly that. **On Linux the broken code happened to produce the right bytes in that one shape; Windows did not.** The defect was in the code, never in the expectation.

**Proved on Linux, v297** (`evidence-r121/before-after.txt`, every program beside it, ELF native and PE under Wine):

| program | v297 Linux | v297 Windows (Wine) | v298, both |
|---|---|---|---|
| `shabda(anka_akshar(66))` | `B` (right, by luck) | `P` (a garbage byte) | `B` |
| `c = anka_akshar(66)`, `d = anka_akshar(67)`, a `prakriya` call, `shabda(c); shabda(d)` | **`B` and five garbage bytes** | `B` and two garbage bytes | **`BC`** |
| `vartani_sandhi("ab", "cd")` once | `abcd` (it overwrote the code after the literal) | access violation | **refused when compiled** - `E_VARTANI_STHIRA`, at the literal |
| the same, three times round a loop | **`abcd`, then SIGSEGV** (exit -11) | access violation | refused when compiled |
| `s = "ab"`, then `vartani_sandhi(s, "cd")` | **`abcd` and the program ran on** (code overwritten) | access violation | **stops: `E_VARTANI_STHIRA` on stderr, exit 1** |
| a writable destination (`nirmmita` + `vartani_pratilip`) | `abcd` | `abcd` | `abcd` |

**Answers to your two questions:**

- **What does `anka_akshar(66)` return?** A pointer to a one-character string, `B`. **v297 wrote that character below the stack pointer, returned its address, and left `rsp` 8 bytes lower.** The next push or call destroys it:
  - on Windows at once, because `shabda` goes through the runtime's kernel32 call, which uses that stack;
  - on Linux as soon as the value is kept.
- **What does `vartani_sandhi` do?** It appends `t` to `s` **in place** and returns `s`, as C's `strcat`. **v297 accepted a string literal as `s`**, and a literal is part of the program's code:
  - **Windows's code section is read-only**, so the first write is the access violation;
  - **Linux's single segment is writable**, so the program overwrote its own instructions.

**Which goldens need re-recording once fixed: none.** Every program in the tree that calls either builtin:

- `examples/322`, `323` - **goldens unchanged.** I changed the *programs* to append into a `nirmmita` buffer (a literal destination is refused now). They print the same `B42` / `abcd`, ELF and PE (Wine); and 322 = 323 byte for byte, ELF and PE, as R111 requires;
- `tests/r54_check/raw_valid.sm` - appends into a buffer; its asserted `4` is right and still holds (the R121 gate checks the same shape);
- `tests/r111/test_vocabulary.py` - compiles `vartani_cat(S, "!")` with `S = "ab"` and compares bytes, never runs it. **Still passes (57 / 0).** Run, that program would now stop with `E_VARTANI_STHIRA` instead of writing into its own code.

## WS2 - the fix, one commit

**`anka_akshar(code)` now takes two bytes from nirmmita's allocator** (zeroed; the R65 arena on Linux, `VirtualAlloc` through the runtime on Windows), as `s + t` has since v288. The result lives as long as the program; no stack is touched; `rsp` is balanced.

- **Cost:** 16 bytes of arena per call on Linux (the arena rounds to 16): 200,001 calls in a loop, the gate's case, run normally.
- **On Windows, one allocation per call**, exactly as `s + t` costs there today.

**`vartani_sandhi(s, t)` keeps its meaning** - in place, returns `s`. R54's raw test and any program that appends into a buffer depend on that. **What changes is that it can no longer write into the program:**

- **A literal destination is refused when compiled**, at the literal (line and column), with no output written:

```
p.sm:2:30: Sutram truti [E_VARTANI_STHIRA]: vartani_sandhi prathamam vartanim tasyah sthane eva vardhayati - sthira vartani ("...") karyakramasya bhagah, tasyam likhitum na shakyate
      vitti s = vartani_sandhi("ab", "cd")
                               ^
Sanket: s + t navinam vartanim rachayati; athava b = nirmmita(n), vartani_pratilip(b, s), tatah vartani_sandhi(b, t)
```

- **A literal arriving through a variable stops the program at run time.** The emitted code checks the destination against the program's own image - from the first byte of its code to a hidden global (`0sandhi`) that lies past every literal. On a hit: `Sutram truti [E_VARTANI_STHIRA]: vartani_sandhi: ...` on stderr, exit 1, ELF and PE.
- That check costs two compares per call, and **only programs that call `vartani_sandhi` change bytes.**
- **Not in an `--object` module**, whose code is not the whole image; the compile-time refusal still applies there.

**Which programs print something different, and why the new output is right:**

- **None in the tree.** The guard shows every changed binary is a program that calls one of the two builtins.
- **Outside the tree:**
  - a program that wrote `vartani_sandhi` into a literal is now refused or stopped - before, it corrupted its own code (Linux) or crashed (Windows);
  - a program that kept an `anka_akshar` result now prints the character instead of garbage.

**What it does not do:** `vartani_sandhi` still trusts that `s` has room for `t`, as `strcat` does. A buffer too short is the caller's mistake, unchecked - **this is your trust-the-count rule's "caller-bounded" class, and the reference now says so.** The checked alternative is `s + t`.

**The gate `R121 builtins`** (14 checks; ELF run, PE run under Wine when present, said when not):

- `anka_akshar` printed at once; kept across a call; two kept; 200,001 calls;
- `vartani_sandhi` into a buffer, and in place as R54 does it;
- the literal refused when compiled, ELF and PE;
- the literal through a variable stopped at run time.

## WS3 - goldens recorded from whatever the code printed

**How a golden is made here:** `tests/run_tests.py --record` writes what the compiler's program printed. **So every one of the 315 example goldens and 229 library goldens began as recorded output.** The question is which were checked against an answer known first. Two measurements:

**1. Goldens that changed while their program did not** - re-recorded to follow the code (`evidence-r121/goldens-re-recorded-without-the-program.txt`, from `git log`): **85**.

- **82 are message-wording rounds** - R114 (`Sutram Error` → `Sutram truti`), R111, R65's *avayava* - where the change was the point and each diff was read.
- **The other three are this round's class exactly: a golden that had recorded a wrong answer, caught only by an independent oracle.**

| golden | what it had recorded | caught by |
|---|---|---|
| `tests/stdlib/numeric29.out` (and `tools/proof_props.py`) | `kuttaka`'s overflowed answer, 2605677504891245458; the solution is 1483584605987376058 | R76: exact arithmetic on 600 random cases (`9f54350`) |
| `tests/stdlib/r8_split_model.out` | 40 `maxparts = 0` results that broke the model its own header states (`str.split` truncated) | R69: the model, 300 cases × 2 functions (`9888227`) |
| `numeric29.out`, `r76_known_values.out` again | wrapped values (`dvigun` and others, v295) | R116: ChatGPT R189's contract matrix - the tests were rewritten, not re-recorded |

**2. Goldens with an answer known before recording** - the ones I can name:

- the R116 contracts gate (133 hand values from R189's matrix);
- the property proofs (86) and library proofs (229) in `tools/proof_props.py`, which check properties or exact values computed outside Sutram;
- `r76_known_values` (exact arithmetic);
- `r8_split_model` (Python's `str.split`);
- `examples/345` (an expectation written in Python first);
- 346/347 (each value derived in R118's hand-back);
- and the refusal goldens, whose content *is* the message the round designed.

**Everything else** - most of the ~500 run-output goldens - **is recorded output, read by eye at best.** I cannot name which of those are wrong without an oracle for each. That is the honest answer: **unverified, not known-wrong.**

**A mechanical scan of all 544 goldens** found nothing that marks a bad recording: no non-UTF-8 or control bytes; no value that looks like a printed address; 62 int64 edge values, all deliberate (saturation tests, refusal texts); 3 `nan`/`inf`, all deliberate float-print tests.

**My recommendation:** the cheapest real oracle is the one that caught all three - **a second implementation in Python for each pure library function**, compared on random inputs, as R76 did for `kuttaka`. `tools/proof_props.py` already has the harness. Extending it module by module would turn "recorded" into "checked" where it matters most, in the numeric library.

## WS4 - R120's cleanup

**Next, as you said - not in this commit.**

## Not done, and why

- **R120** (the repository cleanup): after this, as WS4 says.
- **The buffer-room check for `vartani_sandhi`:** not added. Capacity is unknown for a raw pointer - your caller-bounded class, documented.
- **Native Windows runs:** NOT RUN (no Windows host); PE runs are under Wine, which matches native Windows for these programs (R119 `wine-vs-native.txt`).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, every pack file, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
