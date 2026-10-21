# R30-02 — ChatGPT's scanner finding: the bug is in the compiler, and a fix is ready on a branch

## ChatGPT R96's finding, checked end to end

ChatGPT found that `tools/sutram_build.py` takes `yoj` inside a string as an import, and marked the end-to-end
run NOT_RUN. **I ran it. The builder copied the compiler's own rule exactly, so the compiler does the same
thing, on the ordinary path, today (v240 on main):**

| Program | The ordinary compile on main |
|---|---|
| `likha("yoj bogus")` | **fails**: `E_MODULE_MISSING: yoj patra aprapt: bogus")` |
| `likha("yoj ganit ")` | **compiles, silently wrong:** ganit's whole source is copied *into the string* |
| `likha("a \" yoj ganit ")` | the same |
| `vitti sanyoj = 4` (a name that ends in `yoj`) | **fails**: `E_MODULE_MISSING: yoj patra aprapt: =` |

**The cause:** the import pass (`expand_imports_pass`) looks for `yoj` at **every byte** outside a comment. It
never knew about strings, or about where a name starts. **No program in the repository hits it,** which is why
nothing ever failed.

## The fix, on branch `claude/round-30-yoj-scan` — NOT on main

**In the import pass:**

1. **A string literal is copied as it is,** by the lexer's own rule: from `"` to the next unescaped `"`, where a
   backslash escapes one byte. Nothing inside it is a comment or a `yoj`.
2. **`yoj` straight after a letter, a digit, `_` or a non-ASCII byte is part of that name,** not an import.

**`tools/sutram_build.py` follows the same rule,** so the builder and the compiler still agree byte for byte.

| On the branch (v241) | Environment | Result |
|---|---|---|
| the guard: 559 programs, v240 vs v241, ordinary path | Linux | **471 identical, 88 identical refusals, 0 differ** |
| every example's `.exe` | **Wine** | **182 / 182 identical** |
| `tests/r30/test_yoj_scan.py` (the five cases above, plus a real `yoj` and one in a comment) | Linux | **5 / 5** on the branch; **4 of 5 fail on main** |
| `tools/gates.sh` | Linux | 26 PASS / 0 FAIL / 1 NOT-RUN |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |

## Why it is not on main

**It changes the ordinary path.** It changes it only for programs that fail or compile wrongly today, and no
program in the repository changed (0 of 559). **But "the ordinary path must not change" is the rule, so the
merge is the owner's decision, not mine.** The branch is complete: pins moved, the Windows set rebuilt, the gate
added. **To take it:** `git merge claude/round-30-yoj-scan` (then rebuild the installer if `docs/` moved).
