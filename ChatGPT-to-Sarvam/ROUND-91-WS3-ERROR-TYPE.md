# Sutram ROUND-91 WS3 — Error handling: exact syntax and a mandatory rejection (one-page design)

**Status: proposed STRICT profile + future built-in `phal<anka>` type; NOT implemented in the accepted compiler.** This restates [ROUND-84 WS2](ROUND-84-WS2-ERROR-HANDLING.md) while retaining the tested existing `lib/phal.smlib` convention. Do not quietly claim that a Python precheck is a native compiler feature.

## Today's accepted forms (the weakness)

`yoj phal` imports existing `lib/phal.smlib`. `phal_janchit_bhaj(out, a, b)` writes a **caller-owned two-cell Result `[ok,value]`**: `[0,0]` on division by zero and `[1,q]` on success. `phal_asti_siddhi(r)` reads the success flag and `phal_mulya(r)` reads the value **even if the operation failed**. The accepted compiler has no obligation to examine `ok` before extracting `value`.

This is the smallest **currently accepted but future STRICT-invalid** program, saved verbatim as [ROUND-91-WS3-UNHANDLED.sm](ROUND-91-WS3-UNHANDLED.sm):

```sutram
# sutram-errors-v1
yoj phal
mukhya() {
    vitti r = nirmmita(2 * 8)
    phal_janchit_bhaj(r, 10, 0)
    likha(phal_mulya(r))
}
```

**Proposed new feature:** The `# sutram-errors-v1` comment becomes a compiler-recognized opt-in source-profile declaration. In the **current compiler** it is only a normal `#` comment, so the existing call is **not rejected**. Under the new profile, the standalone checked producer creates an obligation on `r`. Reading `phal_mulya(r)` without a proved success path is a **compile-time error**, source-located **`Sutram Error [E_PHAL_UNHANDLED]`** (code and diagnostic both **PROPOSED**, not present in the native compiler). Failure may never be silently treated as success-zero.

**Positive guarded example**, saved as [ROUND-91-WS3-HANDLED.sm](ROUND-91-WS3-HANDLED.sm):

```sutram
# sutram-errors-v1
yoj phal
mukhya() {
    vitti r = nirmmita(2 * 8)
    phal_janchit_bhaj(r, 10, 0)
    yadi (phal_asti_siddhi(r) == 0) {
        likha("division-failed\n")
        prati 0
    }
    likha(phal_mulya(r))
}
```

**Exact enforcement rule for this minimal subset:** Within `# sutram-errors-v1`, each recognized `phal_janchit_*(result, ...)` producer must be followed by a checked failure path that cannot fall through to extracting the payload: `yadi (phal_asti_siddhi(result) == 0) { ... prati ... }` or explicit propagation of the same Result. A wrong variable, missing check, discarded producer, alias-changing assignment or path that reaches `phal_mulya(result)` while status is unknown **rejects**. A conditional that merely calls `phal_asti_siddhi` and then falls through does **not** discharge the obligation. The old unsafe APIs remain accepted in legacy files without the opt-in marker, so this is a backwards-compatible staging path rather than a stealth global breaking change.

## Final target surface — typed value with propagation (separate implementation decision)

Make `phal<T>` a **compiler primitive discriminated return type**, not a general-purpose generics implementation. Illustrative proposed grammar:

```sutram
prakriya safe_bhaj(a, b) -> phal<anka> {
    yadi (b == 0) { prati dosh(1) }
    prati siddhi(a / b)
}
prakriya add_one(a, b) -> phal<anka> {
    vitti q = prasar safe_bhaj(a, b)
    prati siddhi(q + 1)
}
```

Here `siddhi(v)` produces success, `dosh(code)` produces a tagged failure, and **`prasar`** propagates failure early from a compatible `phal<T>`-returning procedure, unwrapping success into `q`. All of `-> phal<anka>`, `siddhi`, `dosh`, and `prasar` are **new proposed syntax; none compiles today**. `prasar` is proposed instead of postfix `?` to avoid silently colliding with today's `? :` ternary expression grammar. New typed results must not be discarded; consumers exhaustively branch or propagate. Error identity must survive chaining, unlike today's generic `[0,0]` failure. No ownership, general generics, or unbounded alias guarantees are implied without additional compiler work.

**Scope gate:** A correct implementation requires native parser/type tagging and control-flow/alias validation. If this requires a broad restructuring of the 23,000-line compiler, **STOP and separate the RFC from implementation**, per Round-91 instructions.

## Required acceptance and evidence (none native run here)

1. Old unchanged `.sm` file still compiles in legacy mode; same source with the future strict marker **fails compilation** with exact `E_PHAL_UNHANDLED` location and no output binary.
2. The guarded positive source compiles and executes the failure branch, printing `division-failed`, and a success test prints the expected quotient. A guard against a different Result or an alias modified between check and value must fail.
3. Typed `phal<anka>` producer and `prasar` preserve error code through a two-step chain; wrong return type, unchecked extraction and discarded Result fail with source locations. Selected language diagnostics remain valid.
4. The **full accepted goldens, fuzzer and 227-case crash corpus** run on the rebuilt Linux compiler, and Windows tests separately, without rewriting goldens merely to pass.

**Prior evidence:** `tools/r84_phal_gate.py` and 12 Python tests in [draft PR #51](https://github.com/dap2810/Sutram/pull/51) already reject the narrow old-style unchecked source and accept an immediate guarded pattern, **at Python prototype level**. That is **not native enforcement**. `docs/ERROR-CONVENTION.md` and `tests/stdlib/result_chain.sm` confirm the current library convention. **This Round-91 native compiler testing: NOT_RUN. Compiler/type/ABI modifications: NONE.**
