# Sutram R32 — Stage 2 call-boundary feasibility and safe implementation gate

**Status: design/research ONLY. Not emitted, not released. Experimental Stage 1 stays OFF by default.**

## 1. Verified baseline and reason for this design

- The exact, Sarvam-verified PERF-FG2 compiler of R30 is preserved as
  `compiler/verified_snapshots/FG2_R30_verified.asm.txt` (SHA-256
  `ada9e37417edd84e40bbf5d4375e468cfbe3fa6bbbc39640261b354c2245b39a`).
- R31 Stage 1 was three-way merged on top of that proven compiler without
  conflicts. `tools/verify_fg2_restoration.py` requires the effective flag-OFF
  source (apart from comments/whitespace) to remain identical to verified FG2.
- Sarvam measured R31 Stage 1 on `126_numeric_pipeline`: OFF min 77.12ms, ON
  min 78.14ms. **Keep Stage 1 OFF by default; this is a measured negative.**
- 126's hot loop executes `total = total + measure(values)` with a function
  call in every iteration. Stage 1 must invalidate XMM2..XMM5 across that call.
  Keeping XMM cache residency across the call is NOT automatically profitable.

## 2. Non-negotiable ABI facts

- Sutram's `prakriya` scalar arguments/results are currently raw qword bits in
  the established custom calling convention. **Do not replace this convention**.
- **SysV AMD64:** XMM0..XMM15 caller-saved, no XMM callee-save guarantee.
- **Windows x64:** XMM0..XMM5 volatile; XMM6..XMM15 nonvolatile and require
  full 128-bit preservation, but Stage 1 uses only XMM2..XMM5.
- Thus **XMM2..XMM5 must be assumed clobbered by *any* function call** on
  both hosts, regardless of source-level purity or whether the callee writes
  the caller's array. A function that is observationally pure can still
  overwrite volatile XMM registers without breaking the ABI.
- Nested/recursive `prakriya`, external helpers, `likha`, and all library
  calls need the same conservative treatment. No privilege/elevation required.

## 3. Candidate Stage 2 mechanisms (not implemented)

A. **Caller-side physical save/restore for live cached XMM slots:**
   - At an AST_CALL boundary, capture the compile-time valid/live mask.
   - Save only live XMM2–XMM5 as **raw qword payloads**, never cvttsd2si,
     with appropriately aligned stack slots; restore the same slots after
     argument teardown, before the caller next consumes the cached values.
   - Preserve the raw-qword function-return value in RAX while restoring.
     Do not push additional data between an already-assembled argument vector
     and the actual call instruction: that changes argument locations.
   - Recompute / enforce host-specific shadow space, stack alignment, and
     outgoing argument offsets after accounting for spill slots; do not assume
     the compiler uses a standard C ABI. This is why a naïve push/pop wrapper
     around a machine `call` is insufficient.
   - Recursive and nested calls must use frame-local shadow storage, not
     globals; preserve all exact IEEE-754 bit patterns.
   - This adds a minimum of one store and one load *per surviving slot* per
     call, in addition to any stack setup. If 126 reuses a local only once
     after the call, preserving it may cost more than an ordinary MOVQ reload.

B. **Callee preservation of XMM2–XMM5 at every prologue/epilogue:**
   - This would introduce a *new internal-only* Sutram-to-Sutram convention,
     requiring whole-program call-graph closure and protection at every early
     return, recursion and external/helper call. Under SysV this cannot be
     assumed for arbitrary library/native helpers. Windows must retain its
     own XMM6..XMM15 rules. NOT appropriate without a verified call graph.
   - Unconditional prologue/epilogue spilling in a 100k-call numerical loop
     is unlikely to improve runtime; benchmark before adopting.

C. **Explicit cache invalidation/reload (current Stage 1):**
   - Always valid and ABI-compatible, and already implemented; Sarvam measured
     it marginally slower on 126. No further safety work is needed for this
     fallback, but it does not meet the performance acceptance criterion.

## 4. Profitability gate — before any Stage 2 assembly

The candidate must *first* demonstrate repeated accesses to the **same float
cache slot on each side of a call**, enough to offset the number of necessary
spills, RAX preservation and stack adjustments. Use actual disassembly and
`tools/shape_profile.py`, not assignment count alone. In `126`, the loop has
one call-containing float update and no straight-line cache reuse sequence
between call barriers. The first hypothesis to test is therefore that a
call-preserving cache will **lose** time on 126, not win.

A lower-risk alternative target is reducing temporary traffic *inside*
`measure` and its callees without preserving volatile XMM values across a
caller-callee boundary. It may need a separate branch-aware expression
scheduler but leaves function ABI unchanged.

## 5. Concrete acceptance matrix, both Linux and Windows

1. Rebuild FG2 baseline from the archived snapshot, release flag-OFF compiler
   from merged `src/sutram_compiler.asm`, and opt-in Stage1 compiler; **every
   flag-OFF program must be byte-identical to FG2** (ELF and PE32+ outputs).
2. Run `tools/verify_fg2_restoration.py` before any rebuild: requires exact
   independently verified source hash + effective release-path identity.
3. `python3 tests/run_tests.py` must pass **163/163** after adding 146–148.
   `python3 tools/codegen_gate.py` must pass **12/12** for FG2 release.
4. `tools/test_xmm_stage1.py` must pass on real flag-OFF/ON compilers;
   146–148 test repeated loop calls, recursive calls, and shared kosh writes.
5. For ANY Stage 2 candidate, a new **call-boundary code-shape gate** must
   assert raw-bit preserve/restore (if used), stack balance, and no unguarded
   use of XMM2..5 after unknown calls. Exact-bit tests must include +/-0,
   subnormals, 2^53 boundaries and NaN payloads where the language permits.
6. An actual Windows x64 runtime runner must validate the Windows binary;
   PE header validation is not runtime validation. No Windows IDE claim.
7. `126_numeric_pipeline` native ELF SHA must **change** and its pinned
   min/p10 runtime must **improve** versus the same-source flag-OFF baseline.
   Use interleaved A/B and report run-to-run variance. A result like Stage1's
   ~78.14ms ON vs 77.12ms OFF means **reject Stage2 as a release feature**.
8. If the performance gate fails, leave both Stage1 and Stage2 disabled by
   default and preserve the last independently verified FG2 release path.

**Decision R32:** Stage 2 runtime cache survival is intentionally NOT shipped:
without NASM or a Windows runtime and with a negative Stage1 measurement,
there is no defensible way to prove its benefit or safety in this environment.
The substantial deliverable this round is the verified recovery of lost FG2,
which had an independently measured ~1.10x improvement on the representative
program, plus hard future regression gates and adversarial call-boundary tests.
