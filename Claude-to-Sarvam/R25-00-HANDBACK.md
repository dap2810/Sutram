# R25-00 — Hand-back to Sarvam: the first lines

- **Commit pushed to `main`: `528e4d4b`** (the code). The delivery documents are in the commit directly on
  top of it, so `main` = that docs commit, and `528e4d4b` is its parent.
- **Compiler on main: `Sutram 1.0 (v236) - sampurna sutra`**
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux)
- **Suite: PASS=217, FAIL=0, NO-EXPECTATION=4** (Linux). 216 + `249_r25_phal`; no existing golden changed.
  `run_tests.py` still exits 1 when everything passes, as `gates.sh` notes.
- **The fuzzer covers the error type: yes.** `fuzz_r23.py --seed 25 --count 1000`: **1000 programs, 33,206
  values, 0 differ**, exit statuses included (most programs end in a propagated failure). `fuzz_valid.py`
  does **not** write phal-prakriyas (R25-02 says why).
- **The four files (WS1), SHA-256 of the bytes on main now:**

```
7d42c065f75f419e1c75396f8e8d7b3215ca9d9899f5253be38ca008f7b00907  tests/negative/r17/r15-original/mutation-15-27971.sm
768e294160e48a93842dc9e5cc1eaafa7a30d29fc4ea256a92e248d9dfadc8a7  tests/negative/r17/r15-original/mutation-15-37233.sm
b251932b7364045da371e112ce1fe8efc1b9b160d074e7394f68e45d9ddb536d  tests/negative/r17/r15-original/mutation-15-42057.sm
2abae6b7323622ef12e4064ca90aaaa9ed79cca6fd3887b6135c985827b50bc7  tests/negative/r17/r15-original/mutation-15-574.sm
```

(The same four lines are in `tests/negative/r17/SHA256SUMS`, unchanged.)

**`tools/gates.sh` on the pushed tree: 22 PASS / 0 FAIL / 1 NOT-RUN (Windows).** Environment: Linux.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 22 PASS / 0 FAIL / 1 NOT-RUN |
| suite | Linux | PASS=217 |
| library proofs · property proofs | Linux | 220 / 220 · 86 / 86 |
| crash corpus | Linux | 227 + manifest, 0 failed |
| `tests/r25/test_phal.py` · `tests/r23/test_capabilities.py` | Linux | 14 / 14 · 23 / 23 |
| `fuzz_r23` 1000 · `--robust` 5000 | Linux | 0 differ · 0 crash, 0 hang |
| `fuzz_valid` 500 · `fuzz_valid --capabilities` 500 | Linux | 500 / 500 · 500 / 500 |
| `fuzz_robust` 5000 mutations | Linux | 0 crash, 0 hang |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` | Linux | all OK |
| `r69 --check-only` · `cross_build_windows --check` | Linux | SOURCE_PINS_CHECKED · REPRODUCED |
| the four capability examples (246–249) | **Wine** (not Windows) | output and exit status match the goldens |
| Windows | — | **NOT-RUN** |

(`evidence-r25/`.) **`FILES-R25.txt`** lists every changed file with its git blob, so you can check that
main has each one: `git rev-parse main:<path>` must equal the blob in the list.

## What is on main now that was not

1. **WS1:** the four corpus inputs restored, byte for byte (R25-01).
2. **Everything the R22–R24 merges did not land,** merged with git from my branch:
   - the four executables at 100755;
   - the `vibhag` keyword and the slice messages in the 22 `lang` files;
   - the generated includes and the pins;
   - the R23 gates, the formatter, the IDE keyword tables and the count tests;
   - `LANGUAGE-REFERENCE.md` §17, `fuzz_valid --capabilities`, and the method hint.
   **PRs #60–#63 are now merged in content; they can be closed.**
3. **WS2:** the error type (R25-02), v236.
4. **WS3:** the decision paragraph for the owner (R25-03). Not built.

## What I did NOT do, and why

- **I did not take R24's base64 storage for the four files.** You asked for the `.sm` files restored, so
  they are plain `.sm` again, and `tools/crash_corpus.py` is main's version. The base64 route stays
  available if a text merge ever has to touch them (R25-01).
- **No handler for the error type** (catch a failure and continue). The syntax is still open.
- **No `phal<T>` and no type on variables.** That waits for the owner's answer to R25-03.
- **`fuzz_valid` does not generate the error type;** `fuzz_r23` does.
- **Windows not run.** Wine is not Windows.
- **I pushed to `main` directly,** as ROUND-25's hand-back asks ("the commit SHA you pushed"). It was a
  normal git push, so modes and bytes came through intact. I did not use `--force`: main's v264 CHANGELOG
  commit, which landed while I worked, was merged in, and the installer rebuilt for it.
