# R14-04 — WS4: what is still open from R13

**Done or answered since R13, not re-sent:**

| R13-05 item | Now |
|---|---|
| #1 the setup rebuild | **done on the branch** (R14-01). The payload is v208. Windows: NOT-RUN. |
| new #1 the R5 decision | **the question is ready for the owner** (R14-02) |
| new #2 the version gate's cost | **answered by you:** a lag of up to 8 is a NOTE, and only a version ahead of the CHANGELOG FAILs. On main: v208 against v212, PASS. |

**Still open, checked on main `a82968d1` or the branch:**

| # | Item | Whose | State |
|---|---|---|---|
| 1 | **The binaries' mode, lost at a fourth merge** | you | 100644 on main again after the R13 merge; the gate FAILs there. **Fixed on PR #49.** The cause is the per-file upload merge. **Please merge my branches with `git merge` or a cherry-pick.** |
| 2 | **The R8-02 language checks** (assigning to a `sutra`, `krama` outside a loop, a duplicate `bhavana`) | the owner | no decision |
| 3 | **The typing-mode extensions** (R10-04) | you | no decision |
| 4 | **`docs/sutram-stdlib.html` hand edits** | you | unchanged. `gates.sh` still regenerates it differently; I restored main's page after each run. |
| 5 | **The Indic gutter drift** | — | a known limit under Wine |
| 6 | **Three IDE details to see on Windows** (the status line font, the language's own name, Clear shell) | the owner's machine | unseen |
| 7 | **A parse error at an operator with nothing after it points at the end of the file** | — | not rechecked this round |
| 8 | **`tests/r69` (2 failures) and `tests/r71` (1)** | ChatGPT | not rechecked this round |
| 9 | **My draft PRs #31–#33, #35, #38, #40, #42, #44–#46**, all on main by content | you | still open; can be closed. **#48 is merged by content too** (v209), and can be closed. #49 is this round's. |
| 10 | **Sanskrit `msg_namespace_error`** (LIKELY WRONG, a supported pack) | | waits for the Sanskrit review |

**New this round:**

1. **The setup goes stale with every change to `docs/`** (R14-01). The payload carries all of `docs/`. Decide
   whether DIFFERS between releases is expected, or whether `docs/` (or just `CHANGELOG.md`) should leave the
   payload.
2. **ChatGPT's PR #47 (R80) changes `build-installer.ps1`.** It builds the compiler inside the installer
   build and checks the PE's payload symbols.
   - **My rebuild follows main's `build-installer.ps1`, not #47's.**
   - **If #47 merges,** the cross-build must follow it, and the setup must be rebuilt again. Its verifier,
     `tools/r80_payload_verify.py`, needs a build report from `r69_build.py` and an unstripped PE. **I did
     not run it** (NOT-RUN).
   - **The two should not both land without one of us reconciling them.** Please say whose that is.
3. **One X11 test fails, and has failed since before R13:** `test_x11_edscroll.py` deadlocks on a full
   socket (R14-01). The gate counts it, so `gates.sh` shows 1 FAIL on the branch. Say if I should fix the
   test (it should read the replies while it types).
4. **The review sheets' Default lines are stale** after R13's Sanskrit-grammar default: 41 lines in each of
   the Gujarati, Hindi and Sanskrit sheets (R14-03). The Gujarati is unchanged. They should be regenerated
   before the Hindi and Sanskrit reviews start.
