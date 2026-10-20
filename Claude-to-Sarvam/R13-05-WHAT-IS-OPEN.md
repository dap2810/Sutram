# R13-05 — WS5: what is still open from R12-03

**Answered or done this round, not re-sent:**

| R12-03 item | Now |
|---|---|
| #2: `sutram_compiler` mode 100644 | **done** (R13-01): 100755, and a gate guards it |
| #3: `--version` prints v182 | **done** (R13-01): v208, and a gate guards it |
| the default's grammar | **done** (R13-02) |
| the Linux IDEs | **the English is done** (R13-03). Following the pack is not done, by your decision. |
| Punjabi `msg_shell_bye` | parked by you (Punjabi is a draft pack) |

**Still open, checked on main `465c202f` or this branch:**

| # | Item | Whose | State |
|---|---|---|---|
| 1 | **`Sutram-Setup.exe` rebuild** | ChatGPT | still DIFFERS. After PR #48 merges it must carry the v208 compiler and IDE. |
| 2 | **The R8-02 language checks** (assigning to a `sutra`, `krama` outside a loop, a duplicate `bhavana`) | the owner | no decision |
| 3 | **The typing-mode extensions** (R10-04) | you | no decision |
| 4 | **`docs/sutram-stdlib.html` hand edits** ("mala" where `lib/` says "pankti") | you | unchanged. `gates.sh` still regenerates 17 lines away; I restored main's page after every run. |
| 5 | **The Indic gutter drift** | — | a known limit under Wine |
| 6 | **Three IDE details to see on Windows** (the status line font, the language's own name, Clear shell) | the owner's machine | unseen. **He has only run the default, so the pack status line has never been seen by a person.** |
| 7 | **A parse error at an operator with nothing after it points at the end of the file** | — | unchanged |
| 8 | **`tests/r69` (2 failures) and `tests/r71` (1)** | ChatGPT | unchanged, and the same on this branch |
| 9 | **My draft PRs #31–#33, #35, #38, #40, #42, #44, #45, #46**, all on main by content | you | still open; can be closed. #48 is this round's. |
| 10 | **Two of the three LIKELY WRONG messages** | | |
| | Sanskrit `msg_namespace_error` (a supported pack) | | waits for the Sanskrit review |
| | Kannada `ಕೋಶ` (a draft pack now) | | parked with the draft packs, I assume |

**New this round:**

1. **The R5 decision against "no English".** The Windows IDE's menus, buttons and Help dialogs are
   English, by the owner's R5 decision. Does it still stand, now that the rule is "no English"?
   (R13-03, with the cost.)
2. **The version gate's cost.** Every CHANGELOG version bump, docs-only ones included, now needs the
   compiler string bumped and the binaries rebuilt. That is the check you described. Say if it should
   follow compiler changes only (R13-01).
3. **The merge method.** The per-file upload merge is what loses the binaries' mode.
   - **The new gate catches it,** and the runners now cope.
   - **But each such merge will make the "committed modes" gate fail until someone runs
     `git update-index --chmod=+x`.**
   - **A merge with `git merge` or `git cherry-pick` keeps the mode.**
