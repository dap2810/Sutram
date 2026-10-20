# R12-03 — WS3: what is still open from R11

**Moved into this round's work, and not re-sent:**

- the default's grammar and the Linux IDEs: now R12-02
- the native review: now R12-01

**Checked on main `068afb26` (v204) this round.**

| # | Item | Whose | State on main |
|---|---|---|---|
| 1 | **`Sutram-Setup.exe` must be rebuilt** with the R11 compiler and IDE | ChatGPT (ROUND-80 is issued) | `cross_build_windows.py --check`: both compilers and the IDE MATCH; **the setup DIFFERS**. It still carries an older payload. |
| 2 | **`sutram_compiler` is mode 100644** | you | **This is not cosmetic: it breaks the tests on a fresh checkout.** The details are below the table. |
| 3 | **`--version` prints `v182`** | you (the number is yours) | unchanged |
| 4 | **The R8-02 language checks** (assigning to a `sutra`, `krama` outside a loop, a duplicate `bhavana`) | the owner | no decision |
| 5 | **The typing-mode extensions** (R10-04) | you | no decision |
| 6 | **`docs/sutram-stdlib.html` hand edits** | you | unchanged. Regenerating the page still changes 17 lines ("mala" → "pankti"). The fix belongs in the `lib/*.smlib` comments. |
| 7 | **The gutter drifts on taller Indic lines** | — | a known limit under Wine; not seen on Windows |
| 8 | **Three IDE details to check on Windows:** the Nirmala UI status line, the language's own name in it, and Clear shell | the owner's machine | Wine shows all three working (`evidence-r11/wine/`). Windows has not been run. |
| 9 | **A parse error at an operator with nothing after it points at the end of the file,** not at the `}` | — | unchanged (it predates R11) |
| 10 | **`tests/r69` (2 failures) and `tests/r71` (1)** | ChatGPT | as before; R71's lock belongs to an open ChatGPT review |
| 11 | **My draft PRs #31–#33, #35, #38, #40, #42, #44, #45, #46** are all on main by content | you | still open; all can be closed (#46 was merged as v203) |

**Item 2 in full:**

- **What fails:** with the binary not executable, `python3 tests/run_tests.py` stops with
  `PermissionError: … sutram_compiler`, and so does `tests/sandesh/test_sandesh.py`. I measured both
  on this round's checkout.
- **Why the gates do not show it:** `gates.sh` rebuilds the compiler before running, so it passes.
- **The fix:** `git update-index --chmod=+x sutram_compiler`, once, on main. It has been lost at three
  merges (R9, R10, R11).

**One new item: the 3 LIKELY WRONG messages** (R12-01): Sanskrit `msg_namespace_error`, Kannada
`r7_msg_mod_missing2`, Punjabi `msg_shell_bye`.

- **They are small, but they are known errors.** The first two are wrong as they stand; the third
  needs the owner's choice.
- **I can correct them as soon as a speaker confirms the replacement,** or on your word without one.
