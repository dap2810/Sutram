# R19-03 — WS3: the modes gate in a tarball, and `test_x11_edscroll`

## Can the "committed modes" gate run in a tarball? Yes, and it does now.

**Why it kept surviving, exactly:**

1. The merges that lose the mode are made through GitHub's file upload, **where no gate runs.**
2. **Where the gate does run, two things hide the loss before it looks:** `gates.sh` rebuilds the three
   Linux binaries with `ld` in its first step, which writes them **executable**; and `tests/run_tests.py`
   sets +x on a compiler it finds unset (R13's NOTE). **A check made after either sees executable files.**
   In a git checkout the gate asked the index (`git ls-files -s`), which neither touches, so it was right
   there; **in a tarball there is no index, and it said NOT-RUN.**

**What changed in `gates.sh`:**

- **The gate runs first,** before the build step and before any test.
- **With git:** the index, as before, now for **four** files (`sutram-fmt` too).
- **Without git (a tarball, a zip from GitHub):** the files' own mode, `test -x`. **Never NOT-RUN.**

**Proved on a tarball of main as it is** (`git archive origin/main`, `evidence-r19/modes-gate-in-a-tarball-of-main.txt`):

```
committed modes   FAIL   not executable: sutram_compiler sutram-ide sutram-gui sutram-fmt (chmod +x; in git also update-index --chmod=+x)
regression suite (NO-EXPECTATION=4 PASS=213) PASS
```

That is main today: the four executables are 100644 (lost at the R18 merge, the seventh time), and **the
gate now says so in a tarball, before the suite's NOTE papers over it.** Both are 100755 on this branch.

**What the gate still cannot do:** run on GitHub's upload form. **The only fix for that is the merge method:**
`git merge` or a cherry-pick keeps the mode; a per-file upload sets 100644 every time. The gate catches it at
the next run, which is what it is for.

## `test_x11_edscroll.py`: fixed, and it was not alone

**The deadlock:** the GUI repaints after every key and writes the drawing requests back over the socket. The
test sent all 90 keys before reading anything; the socket buffer filled, the GUI blocked on its write, the
test's `sendall` blocked on its send, and the test timed out (R14-01). **Now every key first drains what the
GUI has written into a buffer, and the reads are served from it.** Three runs in a row: `RESULT: True`.

**On the way, a gate defect:** **seven of the 18 X11 tests exited 0 whatever they found, and the gate
counts a test by its exit status.** Three of them were printing `RESULT: False`. So "17 of 18 pass" was
wrong: it was 14. Fixed two ways:

1. **Each of the seven now exits 1 on a False result** (`browser`, `clipboard`, `edit`, `edscroll`, `keys`,
   `open`; and `run`, below).
2. **Then three of them failed for real, and are fixed:**
   - `clipboard` and `edit`: **the same socket deadlock,** milder (the GUI stopped processing keys part way;
     the buffer the test read back was stale). The same drain fixes them.
   - `open`, case 2: the test looked for an English prompt, `Open:`. **The GUI's prompt has been `khol: `
     since slice 17** (the X11 GUI was Sanskrit long before R13). **A test that was false the whole time, and
     the gate never saw it.** The test now looks for `khol:`.

**`gates.sh` on the branch: X11 GUI protocol 18/18, and 16 PASS / 0 FAIL / 1 NOT-RUN overall.** The
NOT-RUN is Windows.

`test_x11_run.py` had no `RESULT` line and passed if it did not crash; it now exits by its one check (the
compiler's message is drawn in the pane), which holds. **Seven tests now exit by their result; the other
eleven already did.**
