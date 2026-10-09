# R31: Experimental Stage 1 XMM scalar-local cache (disabled by default)

**Status:** source implemented and statically audited, **unassembled locally** because NASM is absent. Do not enable in release builds. No user privilege/elevation is needed. Read the R30 XMM design in this directory for the full ABI constraints.

## Activation / mode distinction

- Default normal NASM build (NO define) compiles the old code generator: all added branches, data and helpers are under `%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE`.
- Opt-in compiler build: `nasm -f elf64 -DSUTRAM_EXPERIMENTAL_XMM_CACHE=1 src/sutram_compiler.asm -o /tmp/xmm-on.o` then link.
- Use `tools/build_xmm_variants.sh` to build both Linux variants in a project-local folder and run `tools/test_xmm_stage1.py`; the script adds project-local symlinks for library lookup.
- Never confuse opt-in experimental code generation with changing the Sutram source-language ABI or enabling the optimization by default.

## Implementation and hard limits

1. **Scope:** Straight-line adjacent `AST_ASSIGN` statements, where target and both inputs are named scalar `dasham` variables in logical GPR slots 1–4. These map deterministically to XMM2–XMM5. A fifth or stack local, ternary, indexed operand, expression tree, integer-mixed arithmetic, return/call, or aliased array falls back to the existing generator.
2. **Value storage:** Cache validity/liveness bitmasks are held in compiler metadata. A runtime miss emits raw `MOVQ xmmN,GPR`; hits reuse the XMM register. The result is always written through using `MOVQ GPR,xmmN`; the existing raw-qword GPR/stack location stays authoritative. Consequently **dirty bitmask is always zero**, a deliberate conservative implementation of dirty tracking. There are no delayed spills and no floating→integer numerical conversion. No XMM6–XMM15 are touched.
3. **Evaluation:** Only plain scalar variables without calls or memory accesses qualify; the original left-to-right evaluation is preserved. Sub/div aliasing uses XMM0 scratch so `b = a / b` and `b = a - b` remain correctly ordered. `a = a + b` can be performed directly in its cached destination.
4. **Barriers:** Cache metadata is invalidated at generated block entry/exit, for every non-assignment statement (calls, branches, loops, print, return, declarations, inline asm), when assigning arrays/fields, and on every unmatched scalar assignment. No persisted XMM values cross function calls or control-flow merge points.
5. **ABI:** Generated `prakriya` arguments/returns stay raw qword in original registers/stack and RAX. Windows XMM6–15 nonvolatile rules are not implicated; Linux XMM2–XMM5 may be clobbered by calls, hence strict barriers. Stage 3 cross-block caching and Stage 4 Windows nonvolatile XMM allocation remain out of scope.

## Acceptance requirements (must be executed by Sarvam)

- Build off/on variants with NASM. `tools/test_xmm_stage1.py --baseline <last verified R30 compiler> --off <new compiler flag-off> --on <new compiler flag-on>` MUST pass byte identity of default-mode ELF and PE outputs, exact stdout/stderr/exit for five new regressions + the realistic pipeline, and a hot-slice gate proving reuse and smaller code with no push/pop.
- Run full golden suite (160/160 expected) and current codegen gates (12/12 expected) on the newly built **flag-off** compiler. Run full suite on flag-on compiler. Verify Windows PE32+ format. Actually run on Windows before calling Windows runtime verified.
- Benchmark `benchmarks/xmm_cache_heavy.sm` with both compilers using same host pinned CPU, warmups and min/p10. Verify exact output `750001.000000` in both cases.
- Run the realistic `126_numeric_pipeline` with off/on variants; note binary SHA and same-host min/p10. **If realistic output binary is identical or no speedup exceeds noise, leave the feature disabled.** The tool reports this as an explicit release-go/no-go signal.
- Test plus/minus zero, denormals, recursive float calls, nested loops, early returns, indexed array mutation, and >4 float locals on real rebuilt binaries. For byte-exact FP-bit tests, compare memory/return bit patterns rather than only `likha()` formatting.

## Risk log / limitations

- No NASM compiler toolchain was available to the ChatGPT container this round. Syntax and execution of the new `%ifdef` path remain **unverified**; static audits cannot replace a build.
- Cache is not full persistent XMM residency and deliberately does NOT retain across calls or blocks, reducing the speedup opportunity in the call-heavy 126 workload. This experiment may not meet the realistic performance acceptance test.
- The shipped Linux/Windows compiler executables remain the independently verified previous builds; the changed source is experimental until Sarvam rebuilds.
