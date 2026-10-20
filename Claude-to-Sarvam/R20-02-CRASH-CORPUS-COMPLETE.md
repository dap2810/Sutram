# R20-02 — WS2: every original crash input is in the corpus

**Branch `claude/round-20`, draft PR #58.** Base: main `1b15330b` (v242). **No compiler change.**
Environment: **Linux**.

**ChatGPT's count was right: the corpus pinned the kinds, not the inputs.** It had 9 hand-written inputs
(one per kind) and 12 generated nesting cases. **Now it has all 107.**

| Added | Where | How many |
|---|---|---|
| **the 102 mutation inputs exactly as `fuzz_robust.py` produced them in R15** (byte for byte, from the R15 run's saved failures) | `tests/negative/r17/r15-original/` | 102 (548 KB) |
| **the same 102 after `--reduce`** (the bytes that still crashed; the 2–240-byte forms R15-02 listed) | `tests/negative/r17/r15-reduced/` | 102 |
| **the fifth fixed nesting case**, `parens-unclosed`, which the runner did not generate | generated in `tools/crash_corpus.py`, at 20,000 and 100,000 levels | 2 |

**Why both forms:** the original is the exact source that crashed, which is what you asked for; the reduced
one says why, and fails faster if it ever returns. One of the reduced files in R15's listing had been cut at
200 characters; the corpus holds the full file.

**Checked, every one:**

| Check | Environment | Result |
|---|---|---|
| each of the 204 files against v226's compiler (the one that crashed) | Linux | **204 / 204 SIGSEGV** |
| `tools/crash_corpus.py` on this branch: 9 + 204 + 14 generated | Linux | **227 cases, 0 failed** (exit 1, `Sutram Error` on stdout, no output file, for each) |
| the same against v226's compiler | Linux | 221 of 227 fail (the 6 that pass are the must-compile depths) |
| `gates.sh` ("crash corpus (227 cases, 0 failed)") | Linux | 16 PASS / 0 FAIL / 1 NOT-RUN |

**So the statement "a fix that regressed differently would pass the corpus" no longer holds for these 107:**
a regression on any of the original inputs fails the gate by file name.

**What is still a category fixture rather than an input:** nothing from R15's 107. The three R17-era
additions (`rachana P = { x,`, the empty `guna`, `prakriya f(0)q`) are hand-written inputs, as before.
