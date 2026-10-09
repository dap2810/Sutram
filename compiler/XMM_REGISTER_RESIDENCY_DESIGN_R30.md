# Sutram R30 — persistent floating-point register residency design

**Status: REVIEW DESIGN, NOT IMPLEMENTED.** Owner: compiler workstream (ChatGPT). No changes to the runtime ABI are included in R30. The implemented R30 expression optimization is deliberately restricted to the existing ABI and independent of this design.

## 1. Current observable contract

Sutram's compiler is a single NASM x86-64 source emitting native Linux ELF or Windows PE32+ instructions. The T12 scalar `dasham` representation is an IEEE-754 binary64 **bit pattern in a 64-bit GPR or scalar stack slot**, including function arguments and return values. At a generated `prakriya` call, arguments are evaluated in source order and forwarded in the existing integer-sized register/stack slots; the return is in RAX, even for `dasham`. The generator already assigns locals 1–5 to RBX/R12/R13/R14/R15, and other locals to RBP-relative slots. The F1/F2/FC1/FG1/FG2 fast paths use XMM0/XMM1 only as **temporary computation registers** and materialize the result back to the existing scalar ABI before completing an expression. `kosh dasham` elements remain 64-bit values in the heap, not vectors; a kosh passed to `prakriya` is a pointer-by-value view, and `kosh_push` on such a parameter is rejected to avoid stale pointers.

No persistent-XMM step may change the function-call ABI implicitly. Current call/return, argument conversion, recursion, Windows PE and Linux ELF targets, array aliasing, exact float conversions, and mixed `vitti`/`dasham` expressions are release-critical.

## 2. System ABI distinctions — explicitly not interchangeable

| Feature | Linux x86-64 SysV ABI | Windows x64 ABI |
|---|---|---|
| XMM caller-saved/volatile | XMM0–XMM15 | XMM0–XMM5 |
| XMM callee-saved/nonvolatile | **none** | XMM6–XMM15 (must restore the full 128-bit contents when used) |
| Argument passing to external C APIs | floating arguments conventionally use XMM0–XMM7 | first four positional argument registers are type-dependent (XMM0–3 for floating values); caller provides 32-byte home/shadow space |
| Stack alignment | 16-byte aligned **before** `call` | 16-byte alignment before call; mandatory 32-byte shadow space for ordinary Win64 ABI calls |
| Existing Sutram `prakriya` ABI | custom raw-qword calling convention, DO NOT silently replace it with SysV | same custom raw-qword convention, DO NOT silently replace it with Win64 |

The platform ABI table matters at **external/system** calls and compiler/runtime helper boundaries. Sutram-to-Sutram calls currently have custom semantics and must either preserve them or introduce an explicitly versioned ABI transition. In particular **never assume XMM6 survives on Linux**; it is volatile there. Never start allocating XMM6–XMM15 on Windows until prologues/epilogues are modified to save and restore them correctly.

## 3. Proposed staging and register allocation

**Stage 0 — shipping baseline.** Keep binary64 locals canonically in their current GPR/stack slots. Use XMM0/XMM1 for one expression and materialize in RAX/GPR at the exit. This is current R30, requires no ABI change, and can be verified by the shape gates.

**Stage 1 — within-basic-block virtual XMM cache, no calls.** Start with XMM2–XMM5 as temporary values for up to four `dasham` locals; keep current GPR/stack locations as authoritative at basic-block entry/exit. XMM0/XMM1 remain expression/scratch registers. Cache metadata per local: current stack/GPR home; live-in/liveness; allocated XMM register; dirty bit; original numeric type; whether an array/address may alias that value; last use. Only cache scalar locals without escaped addresses. Fallback transparently to current generator when pressure exceeds four. Spills write the exact 64-bit payload using MOVQ/MOVSD—**no float→integer conversion**. Do not reorder AST nodes; cache only after the original left-to-right evaluation. A cache is invalid after any expression with unknown side effects.

**Stage 2 — call boundaries.** At every `prakriya` call, built-in call, generated runtime allocation, print, system call, indirect callback, exceptional exit, or unknown helper: spill all live/dirty cached values to canonical homes and mark every cache entry invalid. Reload lazily after return. Also finish evaluating arguments in source order, preserving the current per-argument conversion and pointer-view semantics. Emit existing qword argument and RAX return ABI. Never assume an XMM register survives a call, even if its numeric argument was typed `dasham`. This conservative spill barrier is valid on BOTH systems and across nested calls/recursion. A later interprocedural ABI version could use XMM args/returns, but that requires a separate transition plan, not a silent optimization.

**Stage 3 — branch, loop, merge and scope edges.** Flush dirty XMM cache at conditional branches/ternary selection, the entry and exit of `yadi`, `yavat`, `punaravartana`, `break`, `continue`, scope exits, function returns and generated error edges. At a join, treat all cache entries as invalid until an explicit data-flow merge is proven correct. Respect short-circuit `&&` and `||` order. The first implementation should keep branch/loop edges conservative so no phi-node machinery is required; only then consider cross-block residency.

**Stage 4 — external ABI-aware allocation.** Linux: after establishing exact save/restore semantics, XMM2–XMM15 may be used **only within segments known to contain no calls**, because all are caller-saved. Windows: XMM2–XMM5 are similarly safe volatile scratch. Using Windows XMM6–XMM15 for longer residency requires 16-byte aligned stack save slots and saves/restores of the full XMM register in every function prologue/return/error/unwind path, with the required shadow space and stack alignment. No such extension should ship without Windows execution testing. Prefer common-denominator Stage 1/2 until tested on both hosts.

## 4. Critical safety properties and how to check them

1. **Array mutation/evaluation order:** `data[0] + mutate(data)` must read the old element first; `mutate(data) + data[0]` must read the new value. Nested indexed reads may themselves contain calls; never commute them. Regression: `135_r30_float_index_scalar` and a dedicated two-call alias test.
2. **Argument order/call clobbers:** `f(update(a), read(a))` must evaluate the first argument before the second. Cached values must be flushed before each call. Test on nested two-/six-argument calls and recursive `prakriya` returning `dasham`.
3. **Windows nonvolatile XMM:** initialize XMM6–XMM15 with distinct 128-bit sentinels in an external Windows test harness, call Sutram code repeatedly, and assert all 128 bits unchanged. For Stage 1 no nonvolatile XMM is touched.
4. **Linux caller-saved XMM:** an assembly caller clobbers XMM0–15 around a `prakriya` call; the callee must not rely on any XMM value surviving. Verify with nested arithmetic and recursive calls.
5. **Stack discipline:** verify `rsp` alignment at every emitted call; for Win64 verify 32-byte shadow space at external API calls. Test deep recursion, many scalar locals, and mixed-typed arguments.
6. **Exact bits:** +0.0/−0.0, infinities, quiet NaN payload round trips, extreme finite/denormal values, and integers past 2^53 must not be accidentally converted. Distinguish machine-bit tests from decimal `likha` output checks. Existing setcc/UCOMISD NaN comparison semantics must remain byte-identical until intentionally specified.
7. **Spill/alias safety:** a register-resident scalar is not address-taken; if a future language feature exposes its address, invalidate on potential aliased writes. `kosh` grows may invalidate old element pointers; never cache heap element addresses through a call or reallocation.
8. **Loop joins and premature returns:** nested `break`/`continue`, early return, ternaries, short-circuit and exceptional exits must all flush or invalidate consistently. Re-run B10/B11 regressions.
9. **Platform target parity:** compile identical `.sm` input to ELF and PE32+; assert both binaries have valid headers, compile on both assemblers, and RUN on actual Linux and Windows systems. File-format inspection alone is not runtime validation.
10. **Benchmark acceptance:** test generated-code shape and full `126_numeric_pipeline` binary change, exact stdout, and same-machine pinned min/p10 warm-up-discarded A/B. Report meaningful speedup only when measured above noise.

## 5. Test sequence / go-no-go gates

A. Baseline 147 tests / 9 gates, including F1/F2/FC1/FG1; preserve all Sarvam's IDE and numerical module files. B. Implement Stage 1 behind a disabled-by-default experimental flag, preserving the old generator path. C. Add unit-level AST/codegen gates, instrument spills/reloads and call invalidations, and run branch/mutation/recursion/Win64 sentinel tests. D. Rebuild from NASM for Linux and Windows without privilege elevation. E. Validate cross-system behavior; if no actual Windows runner, the feature stays experimental, not released. F. A/B `126_numeric_pipeline` and independently generated nested-array/float/branch workloads against the exact old compiler with pinned min/p10. Only enable by default after correctness, code-shape, and meaningful realistic speed gains.

## 6. Stage 1 implementation sketch (pseudocode only)

```
for each basic block:
    invalidate_all_xmm_cache_entries()
    for each expression, traverse operands LEFT to RIGHT:
        if operand_is_scalar_dasham_and_non_aliasing:
            load_from_canonical_home_or_cache(operand)
        else:
            flush_dirty_cache()
            evaluate_existing_codegen(operand)
            invalidate_if_unknown_side_effect()
        if call_or_array_write_or_branch:
            flush_dirty_cache_and_invalidate()
        emit_safe_SSE2_op_in_XMM0_XMM1_or_fallback()
    flush_dirty_cache_and_invalidate_at_block_exit()
```

**Not addressed in this round:** global liveness across loops, XMM6+ allocation, new calling convention, vectorization, exception unwinding, Windows IDE. This deliberate boundary prevents a source-level optimizer from invalidating the already working cross-platform compiler.
