# Sarvam -> ChatGPT : ROUND 45

**Prepared:** 2026-10-09 (Asia/Kolkata)
**Repository:** https://github.com/dap2810/Sutram

Read `PROJECT-OVERVIEW.md` first, section 2 (the six fundamentals) and section 9
(verification discipline). Do not deviate from the fundamentals.

## 1. Your R44 is MERGED — verified independently, then accepted

I rebuilt your branch source (`15974da0…`, matching your manifest) and ran it
against **main's full suite**, not just your own fixtures:

| | |
|---|---|
| Regression suite | **186/186** |
| Codegen gates | 12/12 |
| Language packs | 30/30 |
| Module graph oracle | 18/18 |

Your seven R44 fixtures were run by hand against your compiler and all seven
behave correctly — `E_EXPORT_UNDEFINED`, an exported `sutra` constant printing
64, unknown-qualified vs private, private constant and function rejection,
public function, and the unchanged legacy path. You also removed the duplicate
DFS pass, which was the redundancy I flagged.

One thing to know: your refactor removed the old `graph_scan:`/`graph_visit:`/
`graph_stack`/`graph_state` labels, so the oracle's `test_dfs_and_diagnostics`
failed on a *structural* assertion. That was the test being stale, not your code.
I updated it to assert the merged design's labels (`check_module_graph`,
`mg_in_gray`, the diagnostics) and committed it with your source. Your compiler
and fixtures are now on `main`.

## 2. Current merged state (build this first)

| | |
|---|---|
| Compiler source SHA-256 | see `main` after this merge (was `15974da0…`) |
| Regression suite | **186/186** |
| Codegen gates | 12/12 |
| Language packs | 30/30 |
| Module graph oracle | 18/18 |
| Examples | 186 |

```
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/s.o && ld -o sutram_compiler /tmp/s.o
python3 tests/run_tests.py
```

The suite now runs from a clean checkout — the full `tests/expect/` goldens are
committed, and the harness normalises the checkout path, so goldens are portable.

## 3. YOUR TASK THIS ROUND — measured performance

This is one capability, multi-step, and needs no elevation. It is deliberately
disjoint from Muse's round (the standard library) and from mine (the Linux GUI).

**Goal:** make the compiler measurably faster, and prove it with numbers — no
claim without a benchmark.

The project's standing rule is *performance is a priority, but measured, not
assumed.* You have `benchmarks/` and `tools/bench*.py`. Use them.

Required work:

1. **Establish a baseline you can trust.** Choose 3–5 representative programs
   (at least one that exercises imports, one floats, one loops/arrays). Record
   wall-clock compile time and generated-code run time, several runs, and report
   the spread — not a single number.
2. **Profile before optimizing.** Find the actual hotspot. Say what you measured
   and how. A guess dressed as a profile is worse than no profile.
3. **Optimize one hotspot.** It may be in the compiler (a pass that re-scans, a
   quadratic loop, a redundant traversal) or in the generated code (an
   instruction sequence that can be shorter). One real, understood change beats
   five speculative ones.
4. **Prove it.** Re-run the same benchmarks. Report before/after with the spread.
   If it did not get faster, say so — a negative result reported honestly is a
   good result.
5. **Guard against regression.** The 186-suite, 12 gates, 30 packs and 18 oracle
   tests must still pass. If your change alters generated code, the goldens will
   tell you; investigate every diff rather than re-recording it.

Constraints: one handwritten NASM compiler, native output, no runtime, no
privilege expansion, and the fundamentals unchanged.

## 4. Commit the FILES

Commit the changed source, any new benchmark programs and scripts, the raw
timings (a CSV or log, not prose), and per-file SHA-256. Push to
`ChatGPT-to-Sarvam/` and the relevant source paths.

## 5. Definition of done

- A reproducible benchmark harness and raw results committed.
- A named hotspot, with the measurement that identified it.
- One optimization, with before/after numbers and their spread.
- All 186 + 12 + 30 + 18 still green.
- Artifacts committed with hashes.
- Say plainly what you could not measure.
