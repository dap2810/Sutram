# R44 native acceptance candidates

These seven cases are intentionally *not* in the golden suite yet. Their success or
failure has not been observed on an assembled Round 44 native compiler. Do not
copy predicted output into tests/expect.

After assembling the compiler, run:

    python3 tools/r44_pending_acceptance.py
    python3 tests/run_tests.py
    python3 tools/codegen_gate.py
    python3 tools/test_lang_packs.py

Cases:
1. Undeclared export: E_EXPORT_UNDEFINED with module file and niryat line.
2. Exported top-level sutra: use alias-qualified constant with no runtime global.
3. Unknown qualified function: E_EXPORT_UNDEFINED, not generic undefined function.
4. Known private constant: E_MODULE_NOT_EXPORTED.
5. Known private function: E_MODULE_NOT_EXPORTED.
6. Exported function calling local private helper: must run successfully.
7. Legacy non-opt-in import unchanged.

After native execution, record actual stdout, exit status, generated executable
format, and normalized diagnostic path. Only then consider promoting cases to
the main suite with .out/.exit/.compile_fail files.
