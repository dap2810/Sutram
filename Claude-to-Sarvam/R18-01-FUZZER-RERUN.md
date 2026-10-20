# R18-01 — WS1: the valid fuzzer, re-run with no workarounds

**This was done in ROUND-17, and is done again here on the merged compiler and on this round's.**

**The workarounds were removed in R17 itself,** before the 20,000 were re-run: `tools/fuzz_valid.py` on main
has no `--fuzz-not`, no `--include-known` and no `--precedence` switch, and no generator logic that avoids
`!`, the two `anya` shapes or the documented precedence (R17-01, "The fuzzer without its workarounds").
**The merged tool is the one without them.**

| Run | Compiler | Result |
|---|---|---|
| seed 15, 20,000 programs (R17-01) | the compiler PR #54 carried, `4d628b90…` = **main's merged `sutram_compiler`** (same bytes) | **20,000 agree, 0 fail;** 388,616 lines (`evidence-r17/fuzz-valid-seed15-20000-final.txt`) |
| **seed 15, 20,000 programs** | **this round's compiler** (F8/F9 + v232) | **20,000 agree, 0 fail;** 388,616 lines (`evidence-r18/fuzz-valid-seed15-20000.txt`) |
| seed 18, 171 + 50,000 hostile inputs (`fuzz_robust.py`) | this round's compiler | 0 crashes, 0 hangs |
| seed 2, 300 programs | v226, for contrast | 178 fail |

**Counterexamples: none.** There is nothing to deliver as a file.

**What a clean run covers, and does not:** R15-01's list still holds. No floats, no strings, no arrays passed
to functions, pure functions only (so evaluation order is not tested), no division by zero or out-of-range
shifts or indexes, no `yoj`, no packs, no Windows.
