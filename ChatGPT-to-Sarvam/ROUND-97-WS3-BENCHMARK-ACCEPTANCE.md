# ROUND-97 WS3 — Explicit acceptance threshold for the deferred 7-workload benchmark

**NO new speed test was run in R97.** This is a **future acceptance rule**, not a claim of superiority. The owner's current priority remains language development before optimisation. Source: `ROUND-96-WS3-DEFERRED-BENCHMARK-MATRIX.md`, the seven shapes (integer sum, recursion/calls, arrays/slices, growing `kosh`, strings, checked library math, streaming I/O).

## Gate 0 — Comparable work and correctness, otherwise INVALID

Each implementation must produce the **same full verified output hash, exit status, input size, error semantics and relevant bounds/overflow behavior**, with equivalent buffering/growth algorithms and known safety policies. Use the same CPU/ISA, compiler versions, inputs, runtime thread count and OS; clearly separate C `-O2/-O3`, Zig `ReleaseSafe/ReleaseFast` and Sutram default/approved optimisations. For unsafe-fast C/Zig modes, report a *separate performance class* rather than claiming one optimised language was faster at a different task. No eliminated work: externally checked digest and side effects. Gate 0 also requires Sutram regression suite, negative corpus, fuzzer and relevant Windows/native gates **PASS** against the exact benchmarked revision. If program semantics differ, **INVALID**, not a numeric loss/win.

## Two different claims with two thresholds

Define `T_lang,j` = median measured steady-state wall-clock work time on benchmark `j` (exclude launch); `T_best,j = min(T_C,j,T_Zig,j)` measured from the **fastest semantically comparable** settings; `speedup_j=T_best,j/T_Sutram,j` (>1 means Sutram faster). At least **30** independent, random-order runs per workload and profile after a documented warmup, with **paired bootstrap 95% confidence intervals** for speedup. Report raw run-level timings, median, p10/p90 and interval; use 2 hardware hosts before making broad product statements.

| Criterion | **MET (bounded: faster on the seven tested tasks)** | **NOT MET / INVALID** |
|---|---|---|
| Correctness | Gate 0 exact behavior and accepted regression/corpus/fuzz gates PASS | Any mismatch, crash, lost output, untested safety obligation → INVALID |
| Steady-state speed | **7 of 7** workloads have Sutram median **≥5% faster** than the best comparable C/Zig build: `speedup_j≥1.05`; each speedup 95% CI **lower bound >1.00** | Even **one** workload <1.05, or interval includes parity → NOT MET on this suite |
| Repeatability | Same speed thresholds on **two distinct machines** with all configs/input hashes preserved | Only one host or unreproducible source/profile → NOT YET MET |
| Honesty in reporting | State the 7 program names, exact tools/options, hardware, raw results and which configs were excluded | Universal “faster than all C/Zig” without evidence → claim NOT SUPPORTED |

That first threshold answers the narrower, measurable question **“is Sutram at least 5% faster than both C and Zig on every benchmark in our predeclared seven-program suite?”** It is **not** proof of being universally fastest.

**Stricter “all measured aspects MET” stretch target** (only **after** the above speed criterion): on **all seven** programs, Sutram must simultaneously (1) satisfy the 7/7 speed rule, (2) have measured startup latency **median at least 5% below both** C and Zig with bootstrap CI supporting an advantage, (3) produce a **disk executable no larger** than the smallest comparable competitor profile, (4) have **peak resident memory no higher** than the lowest comparable competitor in repeatable runs (account for page-granularity uncertainty; inconclusive = not established), and (5) have **developer build time no higher** than the fastest comparable compiler on each program (record clean and incremental builds separately). Do not combine unlike metrics in a weighted score to conceal a loss. If any of these five axes fails or lacks comparable measurements, the claimed **all-measured-aspects threshold is NOT MET**. No finite suite can prove an absolute “faster than C and Zig in all aspects” claim across all programs/machines.

**Where we expect losses (hypotheses, not R97 results):** tight reduction (loop/register pressure), arrays (SIMD, alias/bounds optimisations), strings (allocation/copy), `kosh` RSS (old mappings), checked-library pipeline (call/check overhead). File I/O may be dominated by OS/cache, so document it rather than excluding an inconvenient result.

**Current outcome:** **NOT_RUN / NOT YET ASSESSED** for the seven-program matrix. The prior single-loop/fib timing figures and the one-language-only `kosh` test do not satisfy Gate 0, 7/7 performance threshold, two-machine threshold, or five-aspect target. Do not report **MET** until the later scheduled performance phase executes them all.
