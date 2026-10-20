# R84 WS2 — Checked-result obligations (PARTIAL compiler feature)

Review: https://github.com/dap2810/Sutram/pull/51 (DRAFT).
Main baseline inspected v224, 4c8209c935389d5f2a9c54b9c98d577fe58f514d. Assignment ROUND-84.

## Existing language baseline
lib/phal.smlib already supplies a mutable 2-cell [ok, value] result, phal_janchit_bhaj, phal_asti_siddhi and phal_mulya. docs/ERROR-CONVENTION.md acknowledges callers can still ignore ok; phal_mulya on failure returns 0. tests/stdlib/result_chain.sm demonstrates manual early return but no enforcement. Do not duplicate this library.

## New review-only files
- tools/r84_phal_gate.py — experimental Python pre-compilation checker for a STRICT subset of standalone phal_janchit_* calls.
- tests/r84/test_phal_gate.py — 12 isolated Python unit tests.
- tests/r84/cases/ignored_failure.sm — division by zero, followed by phal_mulya WITHOUT check.
- tests/r84/cases/checked_failure.sm — same failure, immediately branches on phal_asti_siddhi(r)==0 and unconditionally returns before reading value.

The prototype requires an immediate yadi (phal_asti_siddhi(r) == 0) { ... prati ... } (or sthagita) error exit after the standalone checked call. It rejects wrong checked variable, unchecked use, missing exit, nested/unsupported guard, alternate else, and unsupported inline producer form. It masks comments and string literals. Any unsupported producer syntax encountered is rejected rather than assumed safe. It is NOT a general flow/alias/type analyzer, and is not integrated with NASM compiler.

## Actually executed locally (Python 3)

    python3 -m unittest discover -s tests/r84 -p 'test*.py' -v
    Ran 12 tests in 0.002s
    OK

    python3 tools/r84_phal_gate.py tests/r84/cases/ignored_failure.sm --json
    exit 1; REJECTED; E_PHAL_UNHANDLED on line 4

    python3 tools/r84_phal_gate.py tests/r84/cases/checked_failure.sm --json
    exit 0; ACCEPTED_SUBSET_ONLY; issues []

All four GitHub-uploaded source blobs were read back and matched the exact Git blobs of the locally tested files (see ROUND-84-OBSERVED.txt). Native Sutram compile/runtime NOT_RUN. This is a Python prototype rejection, NOT an actual new Sutram compiler diagnostic.

## Recommended true compiler contract (not implemented yet)
Introduce a disjoint tagged return type, e.g. phal<anka>, with siddhi(value) and dosh(error_code). Functions returning phal<T> create a consume obligation. A caller must choose an exhaustive error/success branch or propagate the entire result with an operator such as ? from a compatible phal-returning function. Discarding the return, extracting its payload without a check, or falling through while still holding a result is a compile-time E_PHAL_UNHANDLED. This must be enforced by the native compiler type checker and control-flow logic, not library discipline. Preserve old two-cell phal and ok APIs during compatibility staging; obtain owner language approval for new syntax.

Required compiler acceptance tests after implementation: negative unchecked program fails compilation with exact E code; checked positive compiles and executes the correct failure branch; chained propagation preserves error identity. Test selected-language diagnostics. Do not rewrite accepted goldens to simulate success.

## Limits
The current Sutram compiler still accepts unchecked old-style phal calls; native compiler enforcement and propagation are NOT IMPLEMENTED. Python gate tests PASS 12/12, native compiler execution NOT_RUN/BLOCKED, no unverified compiler claim. PR #51 remains DRAFT; do not merge as a completed error-handling feature.
