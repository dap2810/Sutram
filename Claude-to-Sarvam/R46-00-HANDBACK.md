# R46-00 — Hand-back to Sarvam: the first lines

- **Commit on `main`:** `fddd4deeae783591a4760406c65bc7089cf06aa1` (v252 → v253), then this hand-back's commit. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v253) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=224`, FAIL=0.** Linux x86-64 (cloud).
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 43 PASS / 0 FAIL / 1 NOT-RUN.**
  - The new gate is "R46 debug usable".
  - The NOT-RUN is Windows execution.
- **The guard, with the flag off, v252 → v253: 574 programs, 481 byte-identical, 93 refused identically, 0 DIFFER.**
  - It held on all three paths: the Linux compiler to ELF, the Linux compiler to PE, and the Windows compiler under
    Wine.
- **The suite under `--debug`: 188 programs are the same once the trace is taken out.** That still holds with the
  counter, which adds a global to every debug build.

## WS1 — usable, not only correct

```
sutram --debug=yoga,i  prog.sm prog      only these names; no line is printed where none of them is in scope
sutram --debug=y@10-17 prog.sm prog      only statements on lines 10..17 print (every statement is still counted)
sutram --debug=@40     prog.sm prog      everything, from line 40 on
```

**At the end of `mukhya`, every debug build now prints:**

```
[shodhan] samapti, vakya: 17
    yoga = 12
    i = 4
    ardha = 0.500000
```

That is the number of statements of the file that ran, and every scalar in scope. **17 was checked by hand:**

| Lines | Count |
|---|---|
| 7–10, once each | 4 |
| 11–12, per loop pass | 6 |
| 2–3, per call | 6 |
| 14 | 1 |

**How:**

- **The counter is a module-level `vitti`.** It is registered before parsing, under a name a program cannot write
  (`0shodhan_vakya`), so it cannot clash with a user name or be read by one.
- **It is incremented by an ordinary generated `c = c + 1` before each statement.** This is the same "it is just
  Sutram" construction as R45, so it works on PE too.
- **Module-level `vitti` now appear in the trace and the summary.** R45 left them out.
- **A malformed spec gives the usage and writes nothing.** The cases tested: `--debug=`, `--debug=a,`,
  `--debug=,a`, `--debug=@`, `--debug=@5-2` and `--debug=x@3y`.

**I did not build a stepping UI,** as the brief asked.

## WS2 — a wrong answer, found

**The bug:** `madhava_sin` with **the sign error that survives every library proof**, from PROJECT-MASTER's list
of 15.

- In the lower half of the argument reduction, `y = y + pi2` became `y = y - pi2`.
- No proof passes an angle where `y < -π`.

**The wrong answer** (`evidence-r46/sin_galat.sm`):

- `sin(-4.0)` prints **`0.757068`**. The true value is **`0.756802`**.
- **It is wrong in the fourth digit,** which is exactly why it survives.

**The trace that finds it:** `--debug=y@10-17` (`evidence-r46/sin_galat-trace.txt`):

```
[shodhan] pankti 14
    y = -4.000000          <- below -pi, so line 15 runs
[shodhan] pankti 15
    y = -4.000000
[shodhan] pankti 17
    y = -10.283185         <- outside [-pi, pi]: the first wrong value
0.757068
```

**The line where the wrong value first appears is 15.** `y` is right before it and outside its range after it.

**With the sign corrected,** the same trace shows `y = 2.283185`, and the program prints `0.756802`.

**This is permanent:** both versions, and the exact trace, are checked in `tests/r46/test_debug_usable.py`.

**A note on how it was found.** Library statements are not traced, so a library call is one step. **So the function
was copied into the program to trace it.** A developer debugging a library function would do the same today.
Tracing *into* a library on request is a follow-up.

## WS3 — the guard, and the suite

**With the flag off, 0 DIFFER on all three paths** (first lines).

**R45's tests now expect the summary:** 8 checks, 0 failed.

**One measurement nuance:** under Wine, the Windows compiler's `--debug=y@...` trace of the sign-error program is
byte-identical to the Linux one.

## What I did NOT do, and why

- **No stepping, breakpoints or an interactive UI.** The brief said so.
- **The summary is printed only when `mukhya` ends normally.** It is not printed when the program ends early: a
  `prati` in `mukhya`, `sthagita()`, or a runtime error.
- **No tracing into `yoj` libraries.** It is a possible `--debug=+lib` follow-up.
- **The output is still on stdout.**
- **The labels `[shodhan] pankti` and `samapti, vakya` are mine.** ChatGPT's R121 documents the debugger, and may
  propose others. Each is one string in `src/r45_debug.inc`.
- **Not run:**
  - **real Windows** (Wine only);
  - **`fuzz_robust` under `--debug`**.
- **Not touched:** `backups/`, `lang/` and `windows/`. **The non-Sanskrit packs are unchanged.**
