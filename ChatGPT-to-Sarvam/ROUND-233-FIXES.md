# ROUND-233 — fixes, proof and release boundary

## Release line

```
main base a3f41178ed955105755edb85ba86c8b88856108f   Sutram 1.0 (v315) - sampurna sutra
staged chatgpt/r233-audit-fixes 55008b4e36e9a69bf448ac4d6162ae976611dad0
       Sutram 1.0 (v315) - sampurna sutra; R233 library/tools/docs candidate
       suite: NO-EXPECTATION=4 PASS=327 (331 attempted; 256 executable runs)
       crash corpus: 227 cases + manifest, 0 failed
       contracts: 139 checks, 0 failed; focused regressions: 21 tests, OK
       gates: 73 PASS / 5 FAIL / 4 NOT-RUN (Linux, no display or Wine)
       ELF and PE guard: 783 programs; 568 identical / 196 refused / 19 DIFFER / 0 new
       non-library changes alone: 587 identical / 196 refused / 0 DIFFER, both formats
       installer: NOT REBUILT; 7 embedded entries stale; native Windows: NOT RUN
       NOT MERGED; NOT RELEASE-READY
```

All 14 staged text files were fetched back through the GitHub API at the exact staged commit and compared with the local content. Their blob identities are in `source_api_verification` in `ROUND-233-EVIDENCE.json`. The branch contains one atomic commit: behavior, tests, reference, changelog and both book notes together. No release version or compiled binary was changed. Main advanced to `4bb49b956254718fdbdad01a28bd6040105307f0` during this work with only a Sarvam-to-Claude brief added; the candidate remains explicitly based on the pinned R233 main.

## Build and provenance

NASM was absent initially. Built official NASM 2.16.03 from the release archive; archive SHA-256 `1412a1c760bbd05db026b6c0d1657affd6631cd0a63cddb6f73cc6d4aa616148`. Source URL: https://www.nasm.us/pub/nasm/releasebuilds/2.16.03/nasm-2.16.03.tar.xz . No compiler source or emitted helper was replaced with a C implementation.

Commands below use `<base>`, `<candidate>`, `<toolchain>` and `<evidence>` as location placeholders. Run the build from each corresponding repository root:

```sh
<toolchain>/nasm -f elf64 -I. src/r68_compiler_entry.asm -o <evidence>/compiler.o
ld -o <evidence>/compiler-built <evidence>/compiler.o
sha256sum sutram_compiler <evidence>/compiler-built
```

Both baseline and final rebuilt compiler, and the committed compiler, hash to:
`813850f84b638848ec291c0fa8cf76de846ef605cdc3b6cd49f0a15b109f72ef`.
The source edits are comments only; library source is included by each program when it compiles.

## 1. Negative bigint digits — behavior fix

`lib/brihat.smlib:79`: change `abhava(d <= 9, ...)` to `abhava(d >= 0 && d <= 9, ...)`.
The prior check let a negative cell flow into `r * 10 + d`. The function's existing documentation already promised `E_MULYA_AYOGYA` for every digit outside 0..9.

Command, first with the new regression cases and the old library, then with the fixed library:

```sh
python3 tests/r116/test_contracts.py --compiler <evidence>/compiler-before
```

Before:

```
FAIL brihat_ank_tak_laghu(a, 1): got run 0 '-1' ''
FAIL brihat_ank_tak_laghu(a, 1): got run 0 '-9223372036854775808' ''
FAIL brihat_ank_tak_laghu(a, 2): got run 0 '-9' ''
FAIL brihat_ank_tak_laghu(a, 2): got run 0 '9' ''
r116 contracts: 139 checks, 4 failed
```

After: `r116 contracts: 139 checks, 0 failed`. Each invalid-digit case must now have exit 1, empty stdout, and the exact `E_MULYA_AYOGYA` stderr. This includes negative digits in both positions, not just a negative final answer. Added valid digit 9 and single digit 10 cases; existing tests retain zero, negative length, leading zeroes, MAX and positive overflow. The digit generator uses the established MIN-safe literal helper. The reference and both books explain the corrected contract, and the changelog names the candidate rather than implying it is merged. The small Sanskrit addition has not had native-speaker review.

## 2. Byte-guard false passes

`tools/guard_pair.py` previously counted matching timeouts, matching signal crashes, and exit-0-with-no-output as identical refusals. It also accepted matching failed outputs and discarded refusal messages.

```sh
python3 tests/r233/test_guard_pair.py
```

Before: `Ran 9 tests ... FAILED (failures=6)`.
After: `Ran 9 tests ... OK`.

Now byte-identical success requires both exit 0 and an output file; identical refusal requires both exit 1, no file, and identical stdout/stderr after normalizing invocation-dependent paths. Timeouts and other exit codes are differences. Input/output locations are resolved before changing the subprocess working directory, and source/output file reads are closed. Positive controls check byte-identical success and path-normalized refusal; a byte change remains a failure. These are controlled compiler outcomes, not claims to have crashed the Sutram compiler nine times.

An interim guard run with a relative `.` tree path over-normalized diagnostic periods and reported 104 differences. That implementation was corrected before staging. The final runs have 19 differences in each format and account for every one below; the interim result is not acceptance evidence.

## 3. Documentation-count checker

`tools/doc_counts_gate.py` compared a quoted gate count with PASS alone. With 73 passed, 7 failed and 2 skipped, it claimed only 73 gates existed; there were 82.

```sh
python3 tests/r233/test_doc_counts.py
```

Before: three test methods, four failed assertions/subtests (two false impossibility results and two wrong-denominator messages).
After: `Ran 3 tests ... OK`.

The impossibility threshold is now PASS + FAIL + NOT-RUN. A quoted passing count that differs from this run is a NOTE; more than the total remains FAIL. A count's historical context still needs human review. The final full gate says `doc counts (73 gates PASS, 5 FAIL, 4 NOT-RUN; suite PASS=327) PASS`.

## 4. Zero-check Windows gate incorrectly marked PASS

`tests/r124/test_lazy_commit.py` says NOT RUN when Wine is absent, then prints `0 checks, 0 failed`. The dispatcher in `tools/gates.sh` formerly interpreted only the final line and printed PASS.

```sh
python3 tests/r233/test_gate_skip.py
```

Before: `Ran 3 tests ... FAILED (failures=1)`.
After: `Ran 3 tests ... OK`.

The fixture invokes the actual shell dispatcher, not a reimplementation. Skip, actual pass, and actual failure are all checked. The final full gate correctly prints `R124 lazy commit NOT-RUN no Wine here: the PE runs and the commit checks need it`. This changes the measured totals; it does not create Windows coverage.

## 5. Reference rows and disabled-checker comments

Reference rows formerly called qword accesses eight-bit operations, called conditional memory access terminal I/O, mislabeled open/read, claimed the byte index was ignored, and omitted the equality-only comparison result. The corrected rows specify valid addresses, eight-byte width, the unsigned-start-only conditional guard, short reads/EOF/negative errors, indexed bytes, and equality versus lexical ordering.

```sh
python3 tests/r233/test_reference.py
```

`Ran 6 tests ... OK`. These tests exercise large qword values, conditional memory reads/writes (including its incomplete extent check using safely allocated memory), an actual byte index, both unequal string orderings, file open/short read/EOF, and open failure. The pre-fix document text is available in the parent commit; the executable behavior already contradicted it. No compiler behavior changed for these rows.

`src/sutram_compiler.asm`'s `rfx_check_likha` entry and call-site comments now describe the immediate-return no-op. The disabled bytes remain. A direct probe `likha(1, " ", 2)` prints `1 2` and exits 0; the rebuilt compiler remains byte-identical. Non-library ELF and PE comparisons both show zero differences.

## 6. Every changed program accounted for

Command (and again with `--pe`):

```sh
python3 tools/guard_pair.py <base> <evidence>/compiler-before <candidate> <evidence>/compiler-after <evidence>/guard-elf
```

Both formats: `783 programs: 568 byte-identical, 196 refused identically, 19 DIFFER, 0 new`; source-program text changes = 0.
Every differing source transitively imports `brihat`, directly or through `aadhar`. The included converter now emits the additional lower-bound test, changing module code and downstream offsets. For **each** of the 19 ELF programs, baseline and candidate executions finished without timeout and had equal exit code, stdout and stderr. The old/new hashes and actual outputs are in `differences` in the evidence. Existing programs retain their existing behavior; the newly generated negative-digit cases separately prove the intended changed behavior. PE bytes were compared, not executed.

| Program | Reason / observed runtime comparison |
|---|---|
| `examples/338_r116_brihat_ank_se.sm` | imports `aadhar`, `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `examples/339_r116_brihat_ank_tak_laghu.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/baseconv_roundtrip.sm` | imports `aadhar`, `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_add.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_cmp.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_copy.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_divmod.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_divzero.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_from_int.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_is_zero.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_mul.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_powmod.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_sub.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_to_int.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/bigint_zero.sm` | imports `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/r11_brihat_guards.sm` | imports `aadhar`, `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/r11_page_edges.sm` | imports `aadhar`, `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/r9_aadhar_alone.sm` | imports `aadhar`, `brihat`; converter lower-bound code added; stdout/stderr/exit unchanged |
| `tests/stdlib/r9_guard_cells.sm` | imports `anukram`, `brihat`, `khand`; converter lower-bound code added; stdout/stderr/exit unchanged |

For the non-library control, the candidate library was temporarily restored to the exact base bytes in the isolated working copy, both guards were run, and the fixed library was restored. Both: `783 programs: 587 byte-identical, 196 refused identically, 0 DIFFER, 0 new`. This isolates all comment, documentation and verification-tool changes. No semantic fix was reverted from the staged branch.

## 7. Regression and gate outcomes

```sh
python3 tests/run_tests.py
python3 tools/crash_corpus.py
python3 -m unittest discover -s tests/r233 -p 'test_*.py'
python3 -B tests/r158/test_doc_currency.py
PATH=<toolchain>:$PATH bash tools/gates.sh
```

| Check | Before | Final candidate |
|---|---|---|
| Suite | 327 PASS, 4 NO-EXPECTATION | 327 PASS, 4 NO-EXPECTATION |
| Unexpected suite FAIL / COMPILE-FAIL | 0 / 0 | 0 / 0 |
| Crash corpus | 227 cases, 0 failed | 227 cases, 0 failed |
| New focused tests | defects reproduced separately above | 21 tests, OK |
| Extended contracts | 139 checks, 4 failed | 139 checks, 0 failed |
| Documentation currency | not separately run before | 25 checks, 0 failed; includes 46 book programs |
| Full gates | 72 PASS, 8 FAIL, 2 NOT-RUN | 73 PASS, 5 FAIL, 4 NOT-RUN |

The suite's process exits nonzero for the four missing goldens, even though it reports no unexpected failures. Do not relabel 331 attempts as 331 passing executions: 75 are intended compile refusals; 256 compile/run; 252 runtime outputs and 75 refusals are compared.

Initial full gates had two missing-NASM-on-PATH failures, four missing-GNU-time failures, an R101 peak-output parsing failure, and the doc-count false failure. NASM on PATH fixed the two tool-resolution failures; R101 passed subsequent complete runs without source changes, so its first failure is retained as a transient measurement failure rather than a repaired defect. The five final failures are R73 scratch, R74 compose, R79 real, R127 descriptor (GNU time unavailable), and R140 package (seven embedded source/docs copies stale). The four NOT-RUN items are R124 Windows lazy commit, R133 Windows handler execution, X11 GUI execution, and native Windows acceptance. The R133 gate performed one static check before reporting unavailable execution; it is not a Windows pass.

The installer package's seven stale entries are the three copies of `lib/brihat.smlib` and four changed documentation files. **The package is not a distributable version of this candidate.** No Windows installer was installed, rebuilt or accepted. The staged v316 acceptance script could not run because no cmd.exe/Wine is available; its hardcoded `(v316)` check was inspected at the pinned v324 branch. Correct and execute it on the owning branch/platform before merge.

## Evidence and remaining work

`ROUND-233-EVIDENCE.json` preserves complete sanitized suite, corpus, guard, focused-test, contract and gate logs; gate failure details; all 19 runtime comparisons; package differences; source/error/library/book inventories; and exact-commit source verification. Invocation paths are normalized, but diagnostics and counts are otherwise retained. No goldens, old evidence or history were deleted or rewritten. The final privacy check inspected all 11,368 tracked files including these new reports/tests and found 0 with system details; `git diff --cached --check` passed.

The companion audit distinguishes repaired findings from remaining work. This pass does not close exhaustive control-flow reachability, all reference/prose corrections, whole-book translation equivalence, package rebuilding or native Windows acceptance. Continue from the explicit open findings; do not promote this source candidate to a release based on the passing subset.
