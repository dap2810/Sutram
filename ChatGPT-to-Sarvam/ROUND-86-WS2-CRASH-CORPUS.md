# Sutram R86 WS2 — Existing negative-corpus coverage

Base source: main v234 `64755d0f4dfdf89711f7c63ec94bc6f5917f2c95`.

**All six earlier crash categories already have regression coverage. No duplicate test files are necessary.**

| Kind | Existing cases |
|---|---|
| R1 | One committed EOF/import case |
| R2 | Three committed parameter-list cases |
| R3 | Two committed struct-field cases |
| R4 | One committed second-else case |
| R5 | Two committed invalid-assignment cases |
| R6 | Twelve generated nesting cases, including positive depth controls |

The source-controlled runner is `tools/crash_corpus.py` and the nine committed programs are in `tests/negative/r17/`. Together they make **21 cases**. The runner requires an appropriate compiler return code and diagnostic and checks that rejected sources create no executable. Prior maintainer evidence reports the 21-case suite passing on Linux. **No compiler was executed in this ChatGPT round.**

Execute on a suitable reviewed Linux checkout: `python3 -B tools/crash_corpus.py --compiler ./sutram_compiler --timeout 20`. Its compilation-only checks do not execute generated user programs.

This workstream is **source inventory PASS, native execution NOT_RUN**. Neither the compiler nor the existing corpus has been modified.
