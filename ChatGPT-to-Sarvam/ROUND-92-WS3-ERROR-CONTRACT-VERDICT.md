# Sutram ROUND-92 WS3 — The rejected-under-strict, accepted-today program

**Verdict: YES, the Round-91 error-type page contains the essential counterexample.** It is source-specific, with a named rejected use. The actual native strict mode is **NOT IMPLEMENTED**; no compiler rejection may be claimed yet.

**Exact source:** [ROUND-91-WS3-UNHANDLED.sm](ROUND-91-WS3-UNHANDLED.sm), line **7** extracts a failed value without checking its result flag:

```sutram
# sutram-errors-v1
yoj phal
mukhya() {
    vitti r = nirmmita(2 * 8)
    phal_janchit_bhaj(r, 10, 0)
    likha(phal_mulya(r))   # unchecked value: failure indistinguishable from success zero
}
```

The explanatory source comment in the saved original does not change the behavior. **Current compiler:** `src/sutram_compiler.asm:5980–5983` treats `#` as a comment; the compiler source has **no** `sutram-errors-v1` recognizer or `E_PHAL_UNHANDLED` diagnostic. **Existing library:** `lib/phal.smlib:127` defines checked division writing a caller-owned `[ok,value]`; `phal_mulya(r)` at line 56 reads `r[1]` unconditionally, with no status requirement. Dividing by zero yields failure `[0,0]`. Existing `tests/stdlib/result_chain.sm` demonstrates the explicit checking convention; it is not a native test of this exact fixture.

**Future STRICT profile:** If the opt-in directive is approved and actually parsed, the same source **MUST NOT COMPILE**: `Sutram Error [E_PHAL_UNHANDLED]` at its unchecked extraction (proposed line 7), no emitted executable. Merely having called a checked producer does not discharge its error obligation.

**Counterpart:** [ROUND-91-WS3-HANDLED.sm](ROUND-91-WS3-HANDLED.sm) calls `phal_asti_siddhi(r)`, then unconditionally returns on failure **before** extracting `phal_mulya(r)`. Future STRICT mode must accept that path, while rejecting a guard on the wrong result, a fallthrough failure branch, or an alias modified after the check. [Full proposed contract](ROUND-91-WS3-ERROR-TYPE.md); [13 exact source checks](ROUND-92-WS3-ERROR-CONTRACT-CHECK.json).

**Important evidence boundary:** The old source shape and library are **readably compatible today**, but the Round-91 standalone `.sm` sample was **NOT executed with the native compiler** in this environment. A R84 Python prototype validated its own conservative subset in earlier tests; it does **not** add this guarantee to Sutram. The strong claim `UNHANDLED.sm` **fails compilation** becomes true **only after native flow/alias analysis and an opt-in strict mode are implemented and tested**, plus negative diagnostics, a positive failure branch, and the standard fuzzer/suite acceptance.

**Statuses:** source contract and counterexample **PASS**; compiled-today acceptance of the exact `.sm` fixture **NOT_RUN**; strict-mode rejection **NOT_IMPLEMENTED / NOT_RUN**; modifications to compiler or `lib/phal.smlib` **NONE**.
