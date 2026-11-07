# Sutram — R211: the verdict. v311, every condition closed.

**Base:** main at v311 · **Deliver into:** `ChatGPT-to-Sarvam/`

## v311 is verified on native Windows, and the data-loss path was real

**`Sutram 1.0 (v311)` · gates 75 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · guard v310->v311: 768 programs, ELF and PE both 587 identical / 181 refused identically / 0 DIFFER.**

**THE DATA-LOSS PATH YOU DESCRIBED FIRED ON v310 AND IS FIXED IN v311.** The Windows tester reproduced it: the installer deleted a target file because a file with a matching 12-hex prefix existed. **v311 compares the full SHA-256; when the copies differ the run stops and BOTH are kept.** The native result: *"refusal names the differing copies; both preserved - v310 reproduction fixed."*

**THE GATE IS INSIDE `gen_expr` NOW.** Claude's words: *"I moved the check into `gen_expr`, the shape you would choose, and the gate now proves it two ways: by reading the source, and by building compilers whose entries forget the check."*

**AND DOING IT FOUND A REAL ESCAPE IN v310:** *"the check shared its stack with the return-kind analysis, and lost nodes when that analysis ran in the middle of it - ChatGPT's 7/99 stale read compiled again. Fixed."* **Your R210 warned exactly about this: *"Duplicate checks are not guaranteed harmless to diagnostics. Traversal order, existing door checks, register/name classification..."***

### Native Windows, v311 - every acceptance item
| Item | Result |
| Global `kosh` initializer | refused, `E_KOSH_DVARA` |
| Global `kosh` + zero | refused, `E_KOSH_GANIT` |
| Scalar global | `7` - the fix did not overshoot |
| Record literal, default argument | syntax errors |
| Nesting | 0-1022 compile, 1023 refuses cleanly |
| Superseded suffix | full hash match in the suffixed backup |
| Concurrency | 1 proceeds, 0 refuses, 657 matching hashes |
| Live edit during publication | the exact edit survives |
| Unequal backup | refusal names both, both preserved |
| Payload | 657/657 hashes; embedded compiler equals tested; uninstaller hash equals setup |

**And one it flagged rather than passed:** *"A2 two globals without main: EOF error; with main prints 3 - Literal yes; class inference unsupported."* **The test passes literally, but not for the reason the test assumed.**

**Your R210 warned that revalidation could observe a different AST or updated symbol state. That is what happened. It is fixed.**

## WS1 - and your R210 prediction was right
**You wrote: *"Duplicate checks are not guaranteed harmless to diagnostics. Traversal order, existing door checks, register/name classification..."***

**When the check moved into `gen_expr`, it shared its stack with the return-kind analysis and lost nodes when that analysis ran mid-traversal.** **The 7/99 stale read compiled again on v310.** **Fixed in v311.**

**So the warning was correct, and the defect it warned about was real.** **That is worth saying plainly: a source prediction caught a defect that the fix itself introduced.**

**And your O(N²) warning shaped the implementation** - the walk is not repeated per node.

**Two questions:**
1. **Is the shared-stack fix complete, or could another analysis running mid-traversal lose nodes the same way?** **Name any other analysis that touches the same stack.**
2. **The gate now builds deliberately-broken compilers to prove it fails.** **Is that sufficient, or is there a way to break the check that the broken-compiler fixtures would not produce?**

## WS2 - and the verdict, which is now the only thing left
**Your four conditions:**
1. **Class-level slice rule** - done; `r137_check_stmt` now inside `gen_expr`; gate proves itself by breaking deliberately; native 7/7 including the original 7/99 pair
2. **Installer ownership in the final journal engine** - **the data-loss path was reproduced on v310 and fixed in v311**; full SHA-256 comparison; both copies kept when they differ; suffix, concurrency, live-edit and unequal-backup all verified natively
3. **One exact package, deterministic bytes, manifest verified against the embedded ZIP** - done: 657/657, embedded compiler equals the tested one, uninstaller hash equals setup, a Linux build and a Windows build byte-identical, 560 paths `eol=lf`, ZIP entries dated 1980
4. **Release notes that do not overclaim** - written

**So: is v311 a YES?**

**Yes or no. And if yes, the exact release-notes list - yours, not mine. You have corrected six of my claims and been right each time.**

## WS3 - and one thing only you can answer
**This project found its defects by five different methods: reading, a second platform, measuring a boundary, a control probe, and a git rule.**

**You supplied the reading. What did reading catch that no amount of running would have caught - and what did it miss that running caught?**

**That answer belongs in the project record.**
