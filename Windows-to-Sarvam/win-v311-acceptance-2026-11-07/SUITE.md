# D: native v311 suite and elapsed time

The unchanged `tools/test_windows_native.py` ran on native Windows against the pinned repository compiler, whose SHA-256 equals the embedded and installed compiler. The suite exited **0**.

| Status | Count |
| --- | ---: |
| PASS | 322 |
| FAIL | 0 |
| COMPILE_FAIL | 0 |
| TIMEOUT | 0 |
| NO_EXPECTATION | 3 |
| SKIP_LINUX_RAW_SYSCALL | 1 |
| SKIP_SIDE_EFFECT_OR_INLINE_ASM | 5 |

The three no-expectation cases are `215_r12_wordfreq`, `216_r12_expr` and `219_sanskrit_kosh_aliases`; they are not counted as passes. [Per-case native records](native-cases.json), [stdout](suite-stdout.txt), [stderr](suite-stderr.txt), [timing/environment](suite-timing.json), [timing wrapper](time-suite.py).

Measured wall time: **19.047598 seconds**, compared with the supplied v309 reference **18.6 seconds**: **+0.447598 seconds / +2.41%** (ratio 1.024064). No material slowdown is apparent in this one run. It is a single total-suite measurement, including process overhead and runtime, not an isolated compiler or `gen_expr` benchmark. The owner was invited to use Settings uninstall concurrently, so desktop load was not controlled; this cannot establish statistical performance parity or attribute the difference to the expression check.

Environment: Windows 11 build (redacted), Python 3.14.7 from Anaconda. No compiler, example, expectation or golden was changed. The requested suite was not repeatedly rerun to select a preferred timing.
