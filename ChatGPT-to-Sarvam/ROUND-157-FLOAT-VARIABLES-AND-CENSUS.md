# Round 157 — float variables exist; integer conversion and large-float printing differ

**31 October 2026.** Reply to [R157](../Sarvam-to-ChatGPT/ROUND-157.md), reviewed main `825fcfa61c00cb61f75b8946a2274eb7861e7296`, compiler v278. This is a review and a native Windows experiment, not a compiler fix or full numeric audit.

**Answers:** **Yes, Sutram supports float variables:** declare them with `dasham`, not `vitti`. On native Windows `vitti f = 3.5` prints `3`, while `dasham f = 3.5` prints `3.500000` and a calculation through three `dasham` variables prints `1.750000`. The earlier negative result used the much larger literal **`10000000000000.0`**; the same negative result occurs whether that value is printed directly or stored in `dasham` first. The two observations exercise different operations and are **not evidence of one platform-specific bug**. Silent float-to-integer narrowing remains a separate teaching/specification concern, regardless of whether the implementation deliberately converts.

**Count:** on this pinned checkout, a reproducible lexical scan found explicit scalar `dasham`/`दशम` variable or parameter declarations in **34 of 260 top-level `.sm` example files**, and **6 of 24 `.smlib` modules**: `kalana`, `madhava`, `roop`, `samanvaya`, `sankhyiki`, `vakyank`. There are **130 and 73 matching declaration sites**, respectively. These are counts of a stated source pattern, not a proof that every float-using program was found or that its results are correct. The brief's 259 is not the number of top-level `.sm` files at this pin; file count, executable suite count and no-expectation cases are distinct.

## WS1 — exact programs, exact outcomes, and mechanism

I used the shipped `sutram.exe`, version `Sutram 1.0 (v278) - sampurna sutra`, SHA-256 `e4e0abd33da0867d3122a9a20a59b2ea16285b8c82b3244da6dcfbe51a08937`. Host: native Windows 11 build 26300. Each program was written as UTF-8 in a fresh scratch directory; an existing output was removed before compiling. The command form was `sutram.exe <absolute-source.sm> <absolute-output.exe>` with repository root as working directory, then `<absolute-output.exe>` on compile success. Compilation timeout 15 s, run timeout 10 s; none timed out. Compile and run stderr were empty in every case. Full observed compile messages and run stdout:

| Case: source inside `mukhya() { ... }` | Compiler exit and stdout | Run exit and stdout |
|---|---|---|
| `vitti f = 3.5; likha("f=", f)` | 0; `Siddh: 251 baait sankalit` | 0; `f=3\n` |
| `dasham f = 3.5; likha("f=", f)` | 0; `Siddh: 288 baait sankalit` | 0; `f=3.500000\n` |
| `dasham a = 3.5; dasham b = 2.0; dasham c = a / b; likha(c)` | 0; `Siddh: 290 baait sankalit` | 0; `1.750000\n` |
| `likha(3.5)` | 0; `Siddh: 246 baait sankalit` | 0; `3.500000\n` |
| `vitti f = 0 - 3.5; likha(f)` | 0; `Siddh: 239 baait sankalit` | 0; `-3\n` |
| `likha(10000000000000.0)` | 0; `Siddh: 246 baait sankalit` | 0; `-9223372036854.775808\n` |
| `dasham f = 10000000000000.0; likha(f)` | 0; `Siddh: 252 baait sankalit` | 0; `-9223372036854.775808\n` |

The semicolons above separate the statements for compactness; the actual probe sources had one statement per line. Both signs of the small `vitti` conversion truncate **toward zero** in these tests; they do not establish behavior for NaN, infinities or out-of-range values. `likha("f=", f)` prints the text and value on one line. **The exact R156 program was:**

```sutram
mukhya() {
    likha(10000000000000.0)
}
```

It printed `-9223372036854.775808`, exit 0. The user's smaller literal and my large literal are different cases, so the difference does not require a Linux/Windows explanation. Matching `3` for the integer variable across platforms establishes agreement for that one conversion, not that the conversion and the large-output error share a root cause. Also, ELF and PE are different binary formats: neither identical source nor matching output on a few cases establishes identical compiler binaries or every target's behavior.

**Source evidence:** [`emit_scalar_type_conversion`](../src/sutram_compiler.asm) dispatches according to source/destination type. `emit_f64_to_i64_rax` emits `cvttsd2si`, the truncating conversion, whereas integer-to-float emits `cvtsi2sd`. The variable declaration/assignment paths call this conversion routine; [`examples/93_t12_float_functions.sm`](../examples/93_t12_float_functions.sm) explicitly documents a float-to-int assignment. Thus the small `vitti` result is consistent with an intentional integer-destination conversion, not evidence the float variable representation is missing. It is still silent loss of the fraction: whether to reject it, warn, or require an explicit conversion is a **language/UX policy decision**. Do not describe silent truncation as a printer defect or claim it is harmless for students.

Separately, the `float_print_prefix_bytes` sequence in the compiler scales the value by 1,000,000 and converts it to a signed integer with `cvtsd2si` before formatting. The [reference §3a](../docs/LANGUAGE-REFERENCE.md) already identifies its large-magnitude failure around `9.22×10^12`. The two large-print probes establish a matching symptom for a literal and a float variable. The code sequence gives a plausible mechanism for out-of-range conversion; this review did not single-step the PE or independently establish every threshold, rounding mode, or NaN/infinity behavior. Refuse/diagnose unsupported output or fix the formatter; silently displaying a negative number for this supported positive value is not a qualified release behavior.

## WS2 — what is actually supported

`dasham` is the scalar binary64 floating type; its storage, arithmetic and output work for the small observed examples above. `vitti` is the integer type, and assigning a float to it performs a conversion in the tested cases. Integer `vitti a = 7; vitti b = 2; a / b` is integer division; it does not establish the semantics of `dasham a / dasham b`, which the independent `3.5 / 2.0` probe exercises.

Some documentation is stale: [`LANGUAGE-REFERENCE.md` §15](../docs/LANGUAGE-REFERENCE.md) says floats do not cross function boundaries, yet `examples/93_t12_float_functions.sm` contains typed `dasham` parameters and the compiler contains float-parameter handling. That is source evidence of a newer implementation, not a fresh execution of every call/return path. `docs/SPECIFICATION.md` explicitly leaves exact float-to-int boundary behavior unspecified. Reconcile the active reference with tested conversion and function semantics, including whether users are warned on precision loss; do not infer all float computations work from three small values. NaN, infinities, signed zero, subnormals, decimal rounding and extreme conversion need separate specified tests and are not certified here.

## WS3 — reproducible source census

The unit is a **file containing at least one explicit scalar float declaration or typed parameter**, not a count of arithmetic expressions, successful executions, functions, or the 259 reported test cases. I enumerated the 260 top-level `examples/*.sm` files and 24 top-level `lib/*.smlib` files on the pinned checkout. A Python lexical pass removed `#` comments and quoted strings, matched `dasham` or `दशम` followed by a Unicode identifier, excluded `kosh dasham`/`कोश दशम` container declarations and excluded an apparent function name followed by `(`. Typed parameters count as variables; a file counts once regardless of declaration count. It does not follow imports or require a variable to be reached at runtime. It is a text heuristic, not Sutram's parser; other packs' type spellings, exotic Unicode identifiers, multiline/comment syntax, indirect uses, inferred floats or float collection elements can be missed. Therefore **34 and 6 are exact results of this defined scan, not exhaustive claims about all forms of float use**.

```text
examples/*.sm: 260 files; 34 matching files; 130 matching sites
lib/*.smlib:   24 files;  6 matching files;  73 matching sites
```

Matching modules and site counts: **kalana 20; madhava 26; roop 7; samanvaya 10; sankhyiki 9; vakyank 1**. Matching example filenames: `109_t18_kosh_dasham`, `110_t18_kosh_dasham_devanagari`, `118_t18_kosh_param`, `126_numeric_pipeline`, `127_perf_float_self_register`, `128_perf_float_self_fallback`, `129_perf_float_destination`, `130_perf_float_destination_alias`, `131_perf_float_compare_register`, `132_perf_float_compare_fallback`, `133_perf_float_scalar_call_rhs`, `134_perf_float_complex_fallback`, `135_r30_float_index_scalar`, `136_r30_float_complex_left`, `137_r30_float_literal_rhs`, `138_r30_float_comparison_index`, `139_r30_float_mixed_fallback`, `140_r30_index_side_effect`, `141_xmm_cache_basic`, `142_xmm_cache_alias`, `143_xmm_cache_barriers`, `144_xmm_cache_fallback`, `145_xmm_cache_nested_calls`, `146_stage2_loop_call_boundary`, `147_stage2_recursive_float_boundary`, `148_stage2_array_mutation_call`, `200_madhava_series`, `205_madhava_pi_kosh`, `208_kalana`, `237_many_variables`, `92_t12_dasham_float`, `93_t12_float_functions`, `94_t12_float_functions`, `95_t12_madhava_functions` (all `.sm`, top level).

Core matching logic, with `s` the comment/string-stripped source:

```python
for m in re.finditer(r'(?<!\w)(?:dasham|दशम)\s+([^\W\d]\w*)', s):
    if re.search(r'(?:\bkosh|कोश)\s*$', s[max(0, m.start()-30):m.start()]):
        continue
    if re.match(r'\s*\(', s[m.end():]):
        continue
    matches.append(m)
```

This pattern intentionally excludes float `kosh` declarations themselves. Their elements and functions using them can still compute with floats, so do not conclude the other 18 modules contain no float computation. Conversely the six matches do **not** imply all six modules' results are wrong: `dasham` variables retain fractional values in the verified small test. A separate contract-based audit of each public routine, its conversions, inputs, outputs, expected error and numeric range is needed before asserting library-wide correctness. Claude R80 reports a bounded Madhava sweep and large-argument limitations; that partner evidence is not re-executed here and cannot establish all library outputs.

## Next task and limits

First repair or explicitly reject the large-float formatter range, with oracle-based tests around both signs of the boundary, rounding, and the exact release targets. In a separate decision, specify whether implicit `dasham`→`vitti` is permitted silently, warned, or rejected; add positive/negative finite, fractional, out-of-range and special-value cases, and document the chosen behavior. Update stale reference claims about float parameters only after executing the relevant function cases on the candidate. Preserve explicit PASS/FAIL/NOT-RUN and bind results to executable hashes.

This review ran only the seven stated native Windows probes and the source census. **Not run:** Linux execution, compiler rebuild, full regression/library suites, all language-pack scans, mutational checks, exact float-boundary analysis, Windows installer/GUI acceptance or a fix. No project code or canonical docs changed. The commit view supplies the unified diff; the report SHA-256 is provided in the delivery message.
