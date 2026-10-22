# Sutram Round 101 WS1 — Independent source-first diagnosis of `r18_srij_overflow_guard`

**Date:** 2026-10-21/22. **Initial pinned `main`:** `4d25df8901e07a58b1ebf3a869f5638ac13ac512` (changelog v300). **This reading is independent of Claude Round 35**; it examined the actual current test, original golden, `lib/suchi.smlib`, generated `nirmmita` code and the existing Windows/WSL raw reproduction BEFORE Claude's R35 answer. **No source/compiler/test/golden file changed.**

## Verdict — distinguish the TWO faults

**A. The immediate failing test and golden are WRONG as a portable overflow proof.** The test's first two inputs `3037000499` are NOT an overflow when multiplied by eight. They demand a valid (though very large) allocation, so either successful anonymous virtual-address mapping (nonzero handle) or allocation failure (zero) can be correct depending on the host. Requiring `0` in the `.out` golden on every host is a false expectation. Merely making this test pass by assuming a fixed amount of available RAM or forcing a `ulimit` **does not test the overflow guard**.

**B. The actual constructors' multiplication guard IS ALSO incomplete for a different, deterministic case.** Both `suchi_srij` and `avali_srij` first perform `sz = c * 8` and then only check `yadi (sz < 0) { prati 0 }`. Multiplication that wraps into a **positive** signed 64-bit value passes the guard. For `c = 2^61 + 1 = 2305843009213693953`, the true byte request is **`2^64 + 8`**, yet 64-bit arithmetic yields **8**. The signed negative-size check sees `8 < 0` as **false**, `nirmmita(8)` can succeed, and the constructor returns a handle claiming capacity `2^61+1` backed by **only one qword**. A later element access could be out of bounds. This is a real guard flaw **proven by source and modular arithmetic**, not yet reproduced by executing a native compiled Sutram `.sm` in R101.

## Precise sources and why the discrepancy arises

| Source | Actual contract / code | What it proves |
|---|---|---|
| `tests/stdlib/r18_srij_overflow_guard.sm:1–14` (blob `8a19d6435b7b5c8891ca637582de7516dfc795dc`) | comment: “capacity whose byte size would wrap must give 0”; calls `suchi_srij(3037000499)`, `avali_srij(3037000499)`, `avali_srij(9223372036854775807)`, and `suchi_srij(2)` | First TWO calls do not meet the comment's premise |
| `tests/stdlib/r18_srij_overflow_guard.out` (blob `2887b954df0778b72ef88477fc7fa30186b7534b`) | expected `0,0,0,1` (with extra newlines) | Hardcodes failure for both legal 22.63 GiB allocation requests |
| `lib/suchi.smlib:46–61` and `:377–394` (blob `c85eb3cb5d8de4d01ca624b895462c1337ff7aac`) | `c = max(cap,1); sz = c*8; if sz<0 return0; hdr=nirmmita(24/32); data=nirmmita(sz); return nonzero handle` if both mappings succeed | The intended guard only tests the *result's signed sign* and relies on OS mapping failure for otherwise valid sizes |
| `src/sutram_compiler.asm:19630–19729` (blob `8b7875c06893333ee8be4191a04a94029a09d218`) | Linux `nirmmita` emits `mmap(0,length,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0)`, converting syscall `-errno` to zero | A successful large address reservation returns **an address**, even without physical memory ever being touched or committed |
| `tools/proof_lib.py:101–150` (blob `7c52f1bd2d4ccd62043bfeaf1dac164153d57d78`) | globs every `.sm` in `tests/stdlib/` and checks exact stdout against a stored golden | Test exists even if grepping `tools/` for its filename finds nothing; no environment predicate in the expectation |
| `Windows-to-Sarvam/win-ffi-2026-10-21/r18-proofs-and-r29-wsl.txt` (blob `9c343c13582b5bed94f81f3bb9b99836e59f8a34`) | WSL default virtual-address limit unlimited: three nonzero addresses in first two slots; 4 GiB RLIMIT_AS: all three runs return zeros | Same program depends on virtual memory reservation policy; no evidence these addresses represent 24 GiB of resident/committed RAM |

## Exact 64-bit arithmetic

```text
INT64_MAX                           9223372036854775807
floor(INT64_MAX / 8)                1152921504606846975
first two input capacities          3037000499
first two requested bytes           24296003992        (22.6274 GiB, fits int64)
sz < 0                              false
third input capacity                9223372036854775807
third wrapped size in uint64        18446744073709551608
third interpreted signed size       -8
sz < 0                              true => immediate 0 (works for THIS overflow)
missing guard test input            2305843009213693953 (= 2^61+1)
true requested bytes                18446744073709551624 (= 2^64+8)
wrapped 64-bit size                 8
sz < 0                              false => WRONG, possible 8B mapping
```

The first two capacities are close to `sqrt(INT64_MAX)` (the maximal safe input for a *square*), but this code multiplies by **8**, not by capacity. `sqrt`-adjacent numbers are therefore not a useful 64-bit byte-length overflow witness.

## Host control genuinely executed (NOT Sutram compiler)

[The C witness](ROUND-101-R18-MMAP-CONTROL.c) and [exact raw stdout](ROUND-101-R18-HOST-OBSERVED.txt) use GCC 14.2, unsigned 64-bit arithmetic with bit-preserving signed interpretation, and a **single anonymous mapping per candidate followed immediately by `munmap`**. **No pages are touched**; no risky large buffer is filled. This environment's **RLIMIT_AS was `unlimited`**, yet an attempted 24,296,003,992-byte `mmap` failed with **errno 12 (ENOMEM)**. A separate run with `ulimit -v 4194304` (4 GiB) also failed; the wrapped **8-byte** map succeeded under BOTH regimes. The exact arithmetic was invariant. This counterexample is important: `RLIMIT_AS=unlimited` does **not guarantee** a giant allocation succeeds; cgroup, global commit limits, memory overcommit policy and address layout also matter. It differs from Windows/WSL, where large mappings did succeed. **Host C control PASS for arithmetic/mmap observation; native Sutram reproduction in R101 NOT_RUN.**

## What to fix without cheating the golden

1. **Fix the guard first in `suchi_srij` AND `avali_srij`:** before `sz=c*8`, if `c > 1152921504606846975` (i.e. `INT64_MAX/8`) return 0. The check must precede multiplication. This catches positive-wrap, negative-wrap and all other oversized signed capacities regardless of host memory policy. Alternatively use compiler-proven checked multiplication and reject *any* overflow. Keep `cap<1` clamping as documented. Avoid calling `nirmmita` for invalid sizes.
2. **Also audit growth**: `suchi_vardh` (`lib/suchi.smlib:66–79`) and `avali_pravesh` (`:407–421`) calculate doubled capacity and `ncap * 8` without this guard. On growth, reject `old_cap > floor(INT64_MAX/16) = 576460752303423487` before doubling; preserve old handle/data when refusing. Review arithmetic for intermediate overflows and upper bounds. **No native growth repro yet.**
3. **Split portable tests**, with no silent expected-file rewrite:
   - Overflow cases: `suchi_srij(2305843009213693953)`, `avali_srij(2305843009213693953)`, `avali_srij(9223372036854775807)` **must return 0** under *both* unlimited and 4 GiB process address spaces; zero page touching. The first two are deterministic positive-wrap regressions.
   - Small capacity `suchi_srij(2) != 0` must be 1 under normal non-starved conditions.
   - Put `3037000499` into a **separate, environment-sensitive allocation test**, with **both zero and a nonzero handle allowed** under the documented contract; do not touch the giant allocation. If its purpose is to test a product-imposed maximum size, first specify that policy independently of OS capacity, then enforce that bound and test it.
4. **Do not** use `--record` to bless the current host's arbitrary large-address success; retain the old exact .out until the owner/reviewer approves a new deterministic test, and explicitly document the old test as an invalid overflow witness. After reviewed code+test changes, run native compiler, `tools/proof_lib.py`, R29 separate compilation, fuzz/crash corpus and Windows acceptance where applicable. Compare ordinary binaries and source pins; no golden drift by fiat.

**Short answer:** immediate R18 **test/golden assumption wrong**, plus **library guard wrong on positive-wrap capacities**. `mmap` succeeding in a large virtual address space is correct for a non-overflowing request. A test passing only under memory limits proves OS allocation behavior, not checked arithmetic. **R101 WS1 independent reading DONE; changes to production/test/golden code DEFERRED to Claude R35 / owner decision.**
