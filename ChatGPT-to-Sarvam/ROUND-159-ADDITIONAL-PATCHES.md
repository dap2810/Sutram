# Round 159 follow-up — float division and narrowing prototypes

**31 October 2026.** This supplements [the first R159 handoff](ROUND-159-PATCH-HANDOFF.md), reviewed at base `cd7a1b5bf0abf77f38905a2ac4739a06462ec7a8` (v279). That handoff said WS2/WS3 had no patches; **two new review patches are now supplied**. They are independent unified diffs against that same base and include their own test scripts. Neither has been integrated into project code or accepted for release. WS2 remains **partial**: the untyped runtime case and several conversion sites are not implemented.

## WS3 — floating division by zero

Artifact: [ROUND-159-FLOAT-DIVISION.patch](ROUND-159-FLOAT-DIVISION.patch), SHA-256 `8572f4d905439748a00ee4a0479836ae88a0f2d6172aa55ebfd9f0d8a5c38c6d`. It modifies `src/sutram_compiler.asm` and adds `tests/r159_float_div/test_float_div.py`. Apply only in a review branch after checking the base and diff.

For the general float path with numerator in `xmm0` and divisor in `xmm1`, the generated code zeroes scratch `xmm2`, does `ucomisd xmm1,xmm2`, and branches past the fatal path on **unordered** (`jp`, so NaN is not mistaken for zero) or **not equal** (`jne`). On either `+0.0` or `-0.0`, it uses the existing mapped-line `E_SHUNYA_BHAJAN` message/exit path before `divsd`. A literal zero is presently a **runtime** error, not a compile-time refusal. This does not reject NaN or infinity produced by other operations; it implements the owner's requested zero-division policy, not a general finite-number guarantee.

To prevent bypass, the patch makes float division fall back to generic expression lowering in the register self-update, register destination, and optional XMM-cache assignment fast paths. Other arithmetic fast paths remain available. No runtime type tag or external library is added. There may be a performance cost from checks and lost division-specific fast paths; **no timing was measured**. Audit all other target/mode-specific lowering, source-map behavior, operation evaluation order, and scratch-register/cache interactions before release.

**Native Windows build and results:**

```powershell
nasm -f win64 -dWINDOWS -I. src/r68_compiler_entry.asm -o ../r159div.obj
ld -mi386pep --entry=_start -o ../r159div.exe ../r159div.obj
python tests/r159_float_div/test_float_div.py sutram.exe
python tests/r159_float_div/test_float_div.py ../r159div.exe
```

Host Windows 11 build 26300; original compiler v279 SHA-256 `b47ea14562f73a8e7babb2d4b354b26f06fcaf88198a61143bb0b98bc1e0b88e`; proposed compiler `317ec1708d678e66d72e752554c4e8135a8091988d8f6a88b0d9b09d5aab3c4c`. Seven zero-divisor cases cover positive zero, negative zero, zero/zero, literal, self-update, distinct destination and compound assignment. The original gave `inf`, `-inf` or `nan` with exit 0 in those cases; **baseline: 1 pass / 7 fail**. The patch gave exit 1 and `Sutram Error [E_SHUNYA_BHAJAN]: pankti N - shunye vibhajanam na sambhavati` for each; normal 5/2 printed `2.500000`, exit 0: **patched: 8 pass / 0 fail**. This is a narrow native test, not the full suite. With both `SUTRAM_R65_PEEPHOLES=1` and `SUTRAM_EXPERIMENTAL_XMM_CACHE=1`, a separate build (`68f3ce30f8b3090cfcc342b11143748a1c370c500e9b0ed4c3d62e3f0cd14a4f`) also produced **8 pass / 0 fail**.

## WS2 — a deliberately incomplete static prototype

Artifact: [ROUND-159-FLOAT-NARROW-PROTOTYPE.patch](ROUND-159-FLOAT-NARROW-PROTOTYPE.patch), SHA-256 `009b0880943d1f54d783e9c718db67880ec799cfe687b4867304ecd49a2d5dd7`. It modifies the scalar-declaration/assignment check and adds `tests/r159_float_narrow/test_float_narrow.py`. **Do not treat this as the requested full conversion fix.**

For an integer scalar declaration or assignment with a nonliteral right-hand expression that `expr_is_float` recognizes, it refuses at compile time with `E_DASHAM_VITTI`, rather than emitting the implicit conversion. It retains v279's existing special handling of literal `AST_FLOAT`. The new diagnostic is file-level because this prototype does not carry a reliable source position for every expression; its Sanskrit wording needs speaker review. It also rejects a computed float known at runtime to be integral, and it deliberately changes legacy behavior. R87 reports 30 programs use computed conversions; neither their full inventory nor an explicit replacement conversion API was qualified here.

**Still unimplemented:** runtime diagnosis when a value's type cannot be determined, integer `kosh` insertion/index stores, typed parameters/returns, globals, array/field paths, indirect/external ABI and every other implicit conversion site. The current qword ABI cannot distinguish an untyped integer's bits from a float's bits reliably; a sound unknown-type runtime error requires a tagged/typed ABI or a conservative rejection of unknown crossings. `expr_is_float` returning 0 for unknown is not proof of integer type. This is why the patch must not ship as a complete feature or silently leave a supposed universal guarantee.

On native Windows, `nasm`/`ld` with the same command structure as WS3 built compiler SHA-256 `a1ae85b89ba6c7e852fc11ac92493bff84a6235c63fd1fd1b77f982cb16089ae`. Running `python tests/r159_float_narrow/test_float_narrow.py <compiler>` gave **baseline 3 pass / 3 fail**, prototype **6 pass / 0 fail**: computed variable declaration, variable assignment and expression declaration refused; integer, float and boolean-comparison controls passed. This is only a discriminating six-case probe, not a compatibility audit, and no full suite was run.

## Patch composition and outstanding checks

In a scratch copy of the pinned compiler source, `git apply --check` and `git apply` succeeded sequentially for the prior NaN patch, the division patch, then the narrowing prototype. A Windows build of that combined scratch source (compiler SHA-256 `e04ea127bb3953ab0c35dc44e4d47fc848c64a36e3a3389d0bb25030c77f670a`) passed the **division 8/8 and narrowing 6/6** probe scripts. The original NaN test script generates NaNs with `0.0/0.0` and is therefore incompatible with the proposed zero-division policy; it must be revised to inject NaNs independently before a combined NaN regression can be claimed. No combined NaN pass is claimed. An initial combined-build attempt accidentally selected the original checkout source because NASM resolves local includes before the supplied include directory; it failed the division tests. The corrected build ran NASM from the scratch directory and produced the results just stated.

Each patch applied in isolation passed `git apply --check --reverse` on its locally modified tree. No native Linux run, disassembly/ABI proof, full suite, separate compilation, performance benchmark, golden migration, Windows package build or installer acceptance was performed. **Next:** review policy and complete WS2's typed/unknown cases and conversion APIs; validate WS3 on both targets and all modes with an independent NaN source; run the complete guard/proof suite and update docs/goldens intentionally. The separate installer guidance and manifest blocker in the first handoff still apply. No compiler source/test files were committed to main by this handoff.
