# R119-00 — The eight Windows failures have three causes, and none is a compile failure: two are the native harness, four are Linux-only memory features the reference already says are Linux-only, and two (322/323) are two old builtin defects - `anka_akshar` and `vartani_sandhi` - that are wrong on Linux too, which Linux happens to hide. Diagnosis only; nothing fixed.

- **Commit on `main`:** `PENDING` (documentation and evidence only; on top of the Windows v297 results `e316585` and your R119 files `b7439d8`).
- **Compiler: `Sutram 1.0 (v297) - sampurna sutra`, unchanged.** Linux x86-64 cloud, with Wine 64 for PE runs.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=315  (319 run)`**, FAIL=0 (re-run on this tree).
- **Gates:** not re-run - no compiler, library, example or test changed. R118's run (62 PASS / 1 FAIL / 1 NOT-RUN, Xvfb, Linux) is the current one.
- **The guard:** not run for the same reason. **R118's Windows-compiler-under-Wine pass is still running** (the container restart stopped the first one); its line goes into the R118 hand-back when it ends.
- **Windows execution:** I have no Windows machine. I read `native-cases.json` (all 319 rows), reproduced every failure but one under Wine, and say where Wine and native Windows differ (`evidence-r119/wine-vs-native.txt`).

## WS1 - the eight, classified from `native-cases.json`

**Every one of the eight compiled on Windows** (`compile_exit` 0, or 1 where the refusal is the test). **So none is a COMPILER failure in the sense of "does not compile".** They split three ways:

| # | case | class | what the evidence shows |
|---|---|---|---|
| 1 | `220_hindi_parse_error` | **TEST HARNESS** | compiled without `--lang hindi`, so it printed the default (Sanskrit) refusal against a Hindi golden. `tools/test_windows_native.py`'s `langs` table lists five examples and **omits 220**, which `tests/run_tests.py` gives `hindi`. **With the flag, the Windows compiler (Wine) prints the golden byte for byte** |
| 2 | `29_nishkriya` | **TEST HARNESS** | the program exits through raw Linux `syscall` bytes in `yantra` (`mov eax,60; mov edi,42; syscall`). Native Windows: stdout identical, exit 0 not 42. **Linux-only by construction.** The harness's skip regex looks for the *word* `nishkriya` in the source; this file never writes it (it uses `yantra`), so it is run instead of skipped |
| 3 | `288_r86_kosh_alias_moves` | **OUTPUT - documented Linux-only** | Windows prints `a[0]=41 k[0]=99` / `a[0]=7 k[0]=99`. **That is word for word what `docs/LANGUAGE-REFERENCE.md` says Windows prints** ("On Windows the old behaviour remains ... a growing `kosh` always moves") |
| 4 | `303_r103_parimita_refuses` | **OUTPUT - documented Linux-only** | no `E_PARIMITA`; prints the sum, exit 0. The reference: *"Linux ELF only, as the block. In a Windows program a `mandapa` releases nothing, and its budget is not checked."* |
| 5 | `317_r107_parimana` | **OUTPUT - documented Linux-only** | every `parimana()` is 0. The reference: *"Linux ELF only; in a Windows program it returns 0."* |
| 6 | `318_r108_parimana_moves` | **OUTPUT - documented Linux-only** | the same: all 0 |
| 7 | `322_r111_new_names` | **COMPILER DEFECT** (in generated code) | after `laghu 97 guru 65`: one wrong byte instead of `B`, then `42`, then an access violation (0xC0000005) before `abcd` |
| 8 | `323_r111_old_names` | **COMPILER DEFECT** - the same one | identical stdout, identical crash. It compiles to the same bytes as 322 (R111) |

**Under Wine** (`evidence-r119/wine-vs-native.txt`): 288, 303, 317 and 318 give **exactly native Windows' stdout and exit**. 322/323 give the same first eight lines, a different garbage byte, and crash the same way. **29 is the exception: under Wine it exits 42**, because Wine runs on a Linux kernel and the raw `syscall` reaches it. **So Wine cannot stand in for Windows on `yantra` code.**

## WS2 - 322/323: not the alias table, not the message text - two builtins whose code is wrong on both systems

**You asked whether the alias table is built differently on the PE path, or the golden compares message text.** **It is neither:**

- **The alias table is the same on both paths:** R111's guard (and every guard since) has the old-name and new-name programs **byte-identical on PE** as on ELF, and the native run shows 322 and 323 failing identically.
- **The golden is stdout only**, and the difference is in the program's own output, before the crash.

**What fails is two builtins that both programs call** (`evidence-r119/the-two-builtins.txt`, programs beside it):

**1. `anka_akshar` (was `char_from`) returns a pointer to stack memory it has already given back.** The code it emits:

```
sub rsp,16 ; mov [rsp],al ; mov byte [rsp+1],0 ; mov rax,rsp ; add rsp,8
```

- The one-character string sits **8 bytes below the new stack pointer**: the next push or call overwrites it.
- The stack is also left **8 bytes lower than before** - unbalanced and misaligned, on every call.
- **Linux hides it in 322's shape:** `shabda(anka_akshar(66))` prints at once, and a Linux write is a bare `syscall` that touches no stack. **On Windows, `shabda` goes through the runtime's call into kernel32, which uses that stack:** the byte is gone before it is printed.
- **Linux is wrong too, as soon as the value is kept:** `vitti c = anka_akshar(66)`, `vitti d = anka_akshar(67)`, a `prakriya` call, then `shabda(c); shabda(d)`. That should print `BC`; **ELF prints `B` and five garbage bytes.**

**2. `vartani_sandhi` (was `vartani_cat`) appends into its first argument in place - and in 322 that argument is the literal `"ab"`.** A string literal lives in the program's code:

- **PE's code section is READONLY** (`objdump -h`), so the first write is the access violation.
- **ELF's single segment is RWE**, so Linux silently writes `cd\0` over the code after the literal. 322 survives because that code has already run. **Put the same call in a loop and Linux crashes too:** `abcd`, then SIGSEGV on the second time round (exit 139).
- **With a writable destination (`nirmmita` + `vartani_pratilip`) it is right on both** - `abcd`, exit 0, ELF and PE.

**How old:** both are in **v254, the repository's first commit**, and in v258 (old names, compilers from git history, PE under Wine: wrong byte, then crash). **They are not a build-path divergence and not this week's code. 322/323 (v292, R111) are simply the first examples to call these two builtins and the first to run natively on Windows.**

**So the bug is in the code the compiler generates, and the two platforms differ only in how fast they show it.** **The fixes are separate, and not made, as WS5 says:**

- `anka_akshar` needs storage that outlives the call: a 2-byte arena allocation, or a static per-program buffer;
- `vartani_sandhi` must not write into a literal: refuse a literal destination at compile time, or return a new string, as `+` has done since v288.

## WS3 - 317/318 (and 288, 303): your bet is half right

**Right:** the fix is the test, not the compiler - for v1.0, and with your agreement.

**Wrong in its premise:** these are **not Linux-shaped numbers from a different allocator.** Windows reports **0 every time**, because **the feature does not exist on the PE path**:

- **`parimana` returns 0** - the reference says so;
- **a `mandapa` reclaims nothing and its `parimita` budget is not checked** - the reference says so;
- **a `kosh` still moves on growth** - the reference says so, with this exact output.

All of it is R101A's Linux-only region work, and the reference documents the Windows behaviour, row by row. **There is nothing a conditional *number* could match.** What a Windows run should check:

- **288:** the documented Windows output - a second golden;
- **317 / 318:** `parimana() == 0` on PE - a second golden;
- **303:** skipped on Windows, and marked so. **The budget is a safety refusal Windows does not have**, and its absence should show up as a known gap, not pass as a quiet "same".

**One thing to see clearly:** 303 is the only one of the four where the gap matters to a user. **A budgeted block that refuses on Linux runs to completion on Windows.** That is documented, but it is a missing safety feature, not a reporting difference.

## WS4 - 29 and 220: were they always failing?

- **`29_nishkriya`: always failing, and already reported.** `Windows-to-Sarvam/WIN-RUN-2026-10-21.md` (v242) records it exactly so: stdout identical, exit 0 not 42, *"Linux-specific by construction."* It is the harness that should skip it.
- **`220_hindi_parse_error`: it passed on Windows before, and it is not failing now - the harness is.** On 2026-10-21 all 35 compile-must-fail examples, 220 among them, gave byte-identical diagnostics (that run passed the flag). The v297 run uses `tools/test_windows_native.py`, whose `langs` table lacks 220. **Given `--lang hindi`, the v297 Windows compiler prints the golden (Wine, `diff` empty).**
- **The other six are new to Windows, not regressions:**
  - 288 was added 2026-10-31; 303, 317 and 318 on 2026-11-02; 322 and 323 on 2026-11-03;
  - **none had been run natively before this build** - so it is six this week, not five (288 is from R86).

## The shared causes, in one line each

1. **The native harness** (`tools/test_windows_native.py`): its `langs` table lacks 220, and its skip test does not catch `yantra` (29). **2 cases.**
2. **R101A's memory model is Linux-only** - regions, `parimana`, the `mandapa` budget - and the goldens are the Linux behaviour. **4 cases**, all documented.
3. **Two builtins with wrong generated code since v254**, which Windows shows at once and Linux hides until a value is kept or a loop runs. **2 cases, 1 shared defect pair.**

## WS5 - nothing built

- **No fix and no installer.**
- **No golden or harness change** - the harness fixes and the Windows goldens are proposals, above.

## Not done, and why

- **Native Windows runs:** NOT RUN (no Windows host). Wine stands in, and differs on 29, as shown.
- **The fixes** (`anka_akshar` storage, `vartani_sandhi` destination, the harness's `langs` and skip, Windows goldens for 288/317/318, a marked skip for 303): diagnosis only, as you said.
- **Not touched:** `Windows-to-Sarvam/` (read only), `backups/`, the packs, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
