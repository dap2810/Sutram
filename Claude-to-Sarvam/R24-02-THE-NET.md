# R24-02 — WS2: the capability compiler against the net

**Compiler v235** (the v234 capabilities plus R24-03's hint). Environment: **Linux**.

## The numbers

| Run | Environment | Result |
|---|---|---|
| **regression suite** (`tests/run_tests.py`) | Linux | **PASS=216**, 4 NO-EXPECTATION, 0 FAIL (it exits 1 even when all pass, as `gates.sh` notes) |
| **crash corpus** | Linux | **227 cases + manifest, 0 failed** |
| **`fuzz_valid.py --seed 24 --count 500`** (the existing generator) | Linux | **500 / 500 agree**, 9,616 lines |
| **`fuzz_valid.py --seed 24 --count 500 --capabilities`** (new, below) | Linux | **500 / 500 agree**, 11,680 lines |
| `fuzz_r23.py --seed 24 --count 1000` (all three capabilities together) | Linux | **1000 programs, 31,271 values, 0 differ** |
| `fuzz_robust.py --seed 24 --mutations 5000` | Linux | **0 crash, 0 hang** |
| `tools/gates.sh` | Linux | **21 PASS / 0 FAIL / 1 NOT-RUN (Windows)** |
| `tests/r66 … r70` (11 folders) · `r69 --check-only` | Linux | all OK · SOURCE_PINS_CHECKED |

(`evidence-r24/`)

## The gap you asked about, named and closed

**The valid fuzzer's generator could not express function values.** Its model has functions, arrays,
`rachana`s, `kosh`, loops and recursion, but no function as a value, so R23's capability was outside it.

**Now it can:** with `--capabilities`,

- about **three calls in ten** become calls through a function value. They go through
  `lagu0` … `lagu5(fn, args...)`, which receive the function as a parameter and call it;
- `mukhya` also stores functions in variables and calls through them;
- these mix with everything the generator already does, including recursion, many locals (the F1
  shape), and calls inside arguments.

**It is off by default,** so every earlier seed generates exactly the same programs (I checked three:
identical). A 60-program `--capabilities` run is now a gate.

**What `fuzz_valid` still cannot express: methods and slices.** Its model has no slice view, and its
`rachana`s are anonymous field bags. Those two are covered by `fuzz_r23.py` (R23-04), which is also a gate.
Between them, all three capabilities are inside the net.
