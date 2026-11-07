# R205–R206 — v306 review: the OOM patch is present; an indirect call bypasses the slice rule

Reviewed main at **`8edb8b90862f4a3b6140cbcf41c6271d8ab76cd9`**, compiler v306. This answers both `Sarvam-to-ChatGPT/ROUND-205.md` and `ROUND-206.md`; v306 supersedes v305 for the release decision. The implementation changes are `773bb77` (v304), `c716813` (v305), and `94e5e2d` (v306).

**Verdict: NO to releasing this v306 as v1.0 with only native Windows acceptance remaining.** This is a new verdict against the new tree, not a carry-forward of the v303 verdict. The original R204 direct-call reproductions are addressed, but the same stale-slice path remains reachable through a function value, by source trace below. Reproduce and close that path before declaring the slice class closed. The Windows handler-registration failure is a second, distinct failure-path gap.

**Evidence boundary:** this round read source, diffs, recorded results and API contracts, compared PR files, hashed binaries and inspected the embedded ZIP. **Compiler/build/native/Wine/installer/GUI execution: NOT RUN — read-side role, no toolchain used.** The programs below are proposed reproductions, not observed executions. No production source, tests, tools, reference, packs or Windows handoff files were changed. This handoff and the companion static-identity JSON are documentation only.

## 1. What is closed, and what is actually verified

| Item | Assessment at this pin |
|---|---|
| R204 S1, direct call with a `kosh` slice beside a mutating argument | Addressed: `r129_check_call` examines direct, known callees and refuses the combination for a `vibhag` parameter. Both expression and statement calls invoke it. The existing reproductions and whole-`kosh`/alias variant are in the gate. |
| A direct call giving a `kosh` slice to a growing callee | Addressed for the analyzed direct-call graph: `r129_may_grow` propagates `BN_KOSHPUSH` to a fixpoint, including recursive cycles. Both `kosh_kship` and `kosh_yuj` use that builtin ID. |
| R204 S2, omitted upper endpoint after a mutating lower bound | Closed by the source change: after refreshing the descriptor, `r23_gen_slice` reloads `rax` from the refreshed length when `[AST+24]` is zero. Explicit endpoints are not overwritten. Recorded growth, shrink and clear cases cover the selected semantics. |
| Capacity invariant during growth | Added before any region/in-place/arena growth branch in `r127_emit_grow`. Given the constructor bound `capacity <= 2^40`, doubling cannot wrap before this check; growth above `2^40` is refused before byte-size multiplication. This closes the R204 invariant request. |
| Parameter growth | The old rejection is removed; caller and parameter hold the same descriptor. The move/copy/publish path updates that descriptor. Recorded small, large, alias and block cases support the change. |
| PR #66 integration | **Observed exact equality:** both `win/winrt_blob.asm` and `win/rtblob.inc` at the review pin equal those files at PR head `3426712b2726247a8661cf6bd5049bbd2512d5d2`. The patch is present unmodified. The PR itself was still open/draft when read; this is an integration-by-copy finding, not a claim it was merged. |
| IDE refused-load path | Source now clears output, appends the refusal and states that the editor retains the previous file. Preserving that editor and its filename is correct. Claude supplies Wine screenshots; native v306 behavior remains to be checked. |
| `79_ayojan_cwd` | The harness selects the root compiler with adjacent `lib/` for that case while retaining the outside working directory. This is a layout/harness correction, not a compiler lookup change. |

Claude's recorded v306 full gate log is **69 PASS / 0 FAIL / 1 NOT-RUN**. Its guard logs say **584 identical ELF binaries + 153 identical refusals**; all 584 PE binaries changed with the embedded runtime and reportedly retained their output/exit under Wine. These are inspected author results, not reruns here. The PR #66 native candidate results are also distinct from running the shipped v306 binaries.

The unreachable `msg_kosh_param_push`/`.ge_call_koshpush_param_bad` remains source cleanup, not a live misleading refusal. Muse R131 correctly distinguishes it from the current behavior.

## 2. Release blocker S3: calling the same function through a variable bypasses S1's guard

**Finding confidence: source-confirmed bypass and stale-address dataflow; proposed output/crash NOT RUN.** A change of call form removes the check without changing the callee or the slice representation.

Trace in `src/sutram_compiler.asm` at the pinned tree:

1. `r129_check_call` (around 28301) calls `r23_call_is_indirect` and immediately leaves on a nonzero result. It does not inspect any argument on that path.
2. `func_param_type` (26851) looks up the syntactic callee name. For a local function variable, no definition has that name, so it returns zero, the scalar/default path.
3. `gen_typed_call_arg` (27162 onward) then calls `r126_check_untyped_arg`. That check rejects `kosh` kinds **2, 3, 6**, but a slice is kind **1** (`r126_value_kind`, `r126_is_kosh_value`). Consequently an explicit `k[0:1]` is not rejected there.
4. A slice is not a `dasham`; scalar conversion is a no-op. `r23_gen_slice` emits the same two-word descriptor containing the current **raw element address and length**, and the indirect callee receives its pointer intact.
5. `.ge_funcall` evaluates argument expressions left to right. Its second argument can therefore move the `kosh` after the first argument captured the address. `r23_emit_indirect_call` then calls the function value; the callee's `vibhag` indexing uses the captured address.

This is not a fabricated function address or wrong argument count. It calls a real function with the arguments its declaration expects. Reference §17 documents unchecked function values, but the new slice guarantee does not say that this ordinary call form may bypass its lifetime restriction. The whole-`kosh` equivalent is already rejected through a function value by R126; the slice equivalent needs its own protection.

### Small deterministic candidate: a write goes to the abandoned buffer

```sutram
prakriya badal(vibhag s, ignored) {
    s[0] = 99
    nivartanam 0
}
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    vitti f = badal
    likha(f(k[0:1], kosh_kship(k, 8)))
    likha(k[0])
}
```

**Prediction:** accepted, then `0` and `7`, because the obstacle prevents the small buffer's in-place extension; the callee writes 99 into the old arena buffer. A supported mutable view would make `k[0]` become 99. Under the chosen conservative policy, the appropriate result is instead a compile-time `E_KOSH_VIBHAG` refusal. Replacing `f(...)` with `badal(...)` is the refusal control; removing the growth argument is the positive control.

### Large candidate: the same R204 region-release fault through a function value

```sutram
prakriya pratham(vibhag s, ignored) {
    nivartanam s[0]
}
mukhya() {
    kosh k[1]
    vitti obstacle = nirmmita(8)
    chakra i = 1 tak 8388608 {
        kosh_kship(k, i)
    }
    vitti f = pratham
    likha(f(k[0:1], kosh_kship(k, 9)))
}
```

**Prediction:** the slice captures the full 64 MiB region, the next push moves and releases it, and the callee reads the released address. An access violation/SIGSEGV is expected, subject to execution confirming the trace. The direct `pratham(...)` version must continue to refuse. This is an expression call deliberately; the existing statement-call argument order is different and must not be mistaken for a fix.

### Required closure

Protect slice provenance before relying on the target's formal parameter kind. A conservative v1 fix may refuse `kosh`-derived slices at indirect/untyped call boundaries. If such calls are supported, their remaining argument evaluation and callee effects need the same borrow guarantee as direct calls. Passing a slice through a `vibhag` parameter, alias or another wrapper must not erase that guarantee. Unknown targets must not silently acquire a proven no-growth effect.

The present `r129_may_grow` also skips unresolved callees (`rfx3_fn_index == -1`) when constructing effects. I am **not** claiming every such call can currently receive a `kosh`: R126 closes that direct route. It is nevertheless the wrong default for a general no-growth proof if new ways to carry aliases are added.

Ask the implementer to pin the small example first, then the region example, with direct/indirect, expression/statement and safe no-growth controls. Keep safe direct slice writes working. Do not declare success just because the large example stops crashing: a retained stale buffer can still silently lose writes, as the small example demonstrates.

`tests/r127/test_descriptor.py` currently covers direct known callees in its slice refusal loop; it does not contain the function-value variant above. Muse R131 likewise probed direct slice calls. Those passes do not contradict this finding.

## 3. R206 WS1: the OOM patch fixes failed commitment, not every prerequisite or allocation failure

### The measured class is addressed

`win/winrt_blob.asm:239–308` now branches from a failed `VirtualAlloc(MEM_COMMIT)` to `.v_nomem`. It uses a static message, writes directly through the existing Win32 imports, restores the console output code page when recorded, and calls `ExitProcess(1)`. It does not reenter `rt_touch`, request another Sutram allocation, or retry the faulting instruction.

The three saved registers and 96-byte local frame preserve call alignment. Shadow space, the fifth `WriteFile` argument, the bytes-written slot and the query buffer are separate. The normal successful commit still resumes execution; faults outside the existing eligibility predicate still continue exception search. This path covers both `kosh` and `nirmmita` faults, including first touches caused by `rt_touch` before I/O. Its diagnostic is correctly generic: it cannot promise that an in-progress operation left a `kosh` unchanged.

The preserved PR evidence reports eight native baseline/candidate cases, including invalid stderr and a null-pointer control. The candidate compiler hash is `3bad012a...`; the actual v306 compiler hash is `d3f3dc15...`. Do not relabel the candidate's native run as the final binary's acceptance.

### W1 — a neighboring failure remains unchecked: installing the handler itself

`rt_init`, lines 17–20, calls `AddVectoredExceptionHandler` and restores the frame without testing its return value. Microsoft's [API contract](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-addvectoredexceptionhandler) defines NULL as failure.

**Conditional source finding:** if registration returns NULL, the program continues using reserve-only allocations but has no registered `rt_veh` to commit their first touched page. That first touch can still terminate with an access violation and no new diagnostic. PR #66 cannot handle this case because its handler was never installed. The Job-limit cases do not force this API to fail.

This is a failure-path hardening gap, **not a claim that it occurred in the recorded native run**. Before claiming reliable handling of the runtime's setup failures, check the registration result and stop with an appropriate static diagnostic/exit when it fails, or establish a deliberate eager-commit fallback. Inject NULL specifically at registration in a test runtime. Do not silently continue with lazy allocation enabled. An init-time helper must establish its own valid call frame; it should not jump into the middle of `.v_nomem` with that handler's assumed stack layout.

### W2 — bound the claims about other faults

The unchanged handler eligibility test is `MEM_RESERVE` + `MEM_PRIVATE`, outside the current thread's stack. It does **not** consult a table of Sutram-owned reservations and does not test the exception's read/write/execute access kind. Therefore “all unrelated faults are unchanged” is too broad: the null-pointer control establishes one excluded case, not ownership discrimination for arbitrary foreign/private reservations. An invalid raw pointer or foreign component can reach a reservation that meets the predicate. This is a pre-existing R124 classification limitation, not a new PR #66 regression and not an independently reproduced defect here.

For a stronger contract, retain reservation ownership and reject execution faults/nonowned ranges before committing or diagnosing OOM. For the present contract, state the exact predicate and keep foreign/raw memory errors outside the memory-safety promise. The [VirtualQuery contract](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualquery) describes region attributes, not allocator ownership.

There is also no demonstrated guarantee for host-wide exhaustion, a blocked output pipe, arbitrary failure inside the Windows diagnostic APIs, or recovery after fatal OOM. A failed immediate `nirmmita` allocation still returns 0; callers must honor that contract. Those are different paths from failed lazy commitment.

### Correct the companion OOM diagnosis before reusing it

Muse R133's claim that arena reservation accepts a PE `-1` as success is contradicted by `r69_n3` in `src/r65_arena.inc:82–85`: immediately after the syscall it compares against `-4095` and selects the zero-room sentinel on an error. The earlier `test rax,rax` tests whether the arena was initialized; it is not the allocation-result check. The fallback and region paths also normalize/check the negative error range. Do not patch those based on that claim.

Also, Linux `ulimit -v`/`RLIMIT_AS` and a Windows Job commit limit restrict different resources. The release-note sentence “On Linux the same pressure is refused earlier” is not a general platform guarantee. Linux overcommit policy affects whether an allocation is refused or a later page access encounters system OOM; see the [kernel's overcommit documentation](https://docs.kernel.org/mm/overcommit-accounting.html). Report the actual limits and outcomes instead of equating them.

## 4. Installer and release evidence

Observed statically, with full hashes in `ROUND-205-206-STATIC-IDENTITY.json`:

- Setup SHA-256 **`e6006caf2bacebf378b9d3b8cd4527d63c1de6ac2e96efa630e5c268ff852e5f`** matches `Sutram-Setup.sha256`.
- Embedded ZIP: **658 files**, including the manifest; **657 manifest entries**, no missing, mismatched or unmanifested payload files.
- Both embedded compilers are v306 and byte-identical to `win/sutram.exe`; root `sutram.exe` matches too. Embedded linker and IDE match the tree binaries.
- Both current engine scripts are embedded verbatim. All **25 source-lock pins** match the files' Git blob hashes.

These checks identify the package; they do not prove successful installation, upgrade, uninstall or GUI behavior. The 16-check R130 gate mostly matches source text and embedded bytes. It is useful as a packaging/structural gate, not proof that every failure or timeout is handled correctly.

The latest native diagnostic establishes an **ownership refusal**, not a reproduced hang, and the owner-authorized empty-target repair completed with the unchanged v305 installer. A product-shipped linker with a mismatching old manifest hash is still a modified file from the ownership guard's perspective; its product filename alone does not justify overwriting it. Preserve the recovery procedure and the guard.

v306 adds competing-install detection, fresh-PATH/version checks, logging and a bounded installation-engine wait. Native acceptance must cover the actual wizard and the repaired v305-to-v306 upgrade, not only an engine-only clean-install harness. Keep the existing owner's installation out of a disposable clean-install/uninstall test. Check the duplicate-install refusal and an injected mid-install failure for honest failure state and a documented recovery path. The current catch path reports failure; it is not a rollback transaction.

The wizard now requests process-scoped execution-policy Bypass. The old README still says the scripts obey the existing policy and are blocked under Restricted/AllSigned, so it is stale for this launch path. Explain the actual delivery behavior and supported policy configuration; a Group Policy override is not solved by this flag. This review has not changed or bypassed any machine policy. Do not keep the old R204 policy conclusion unchanged after the launcher changed, and do not turn the new flag into a universal zero-configuration claim.

## 5. Exact release-note text to retain or substitute

The current notes already incorporate most R204 corrections. Keep those corrections; do not revert to unlimited objects, automatic reclamation of all block memory, or `parimana()` as resident memory. The following is the final exclusion text I recommend, in addition to the operational limits below:

> **Not included in Sutram 1.0:** threads or concurrent execution within a process; closures; generics or user-defined type/trait dispatch; checked function-value signatures; non-local exceptions or stack unwinding; an interactive debugger or emitted debug symbols; user-controlled `free`, garbage collection, or automatic reclamation of all `kosh` storage at block exit; slices of `kosh dasham` or slices outliving their creating function; mixed-compiler-version object compatibility; formal verification of the compiler or library; continued development of the ten frozen non-Sanskrit packs. Threads are deferred beyond v1.0, not ruled out permanently.
>
> Explicit `siddhi`/`dosh` results and `prasar` exist, with their documented restrictions; they do not provide exception unwinding. Library “proofs” are executable tests. `--debug` provides traces, not an interactive debugger. Rebuild every object with the same compiler: the linker does not enforce version compatibility.

Operational limitations that must accompany that exclusion list:

1. **Slices:** “A `kosh` slice borrows its current element storage. Unsupported storage and call combinations are refused. A no-growth guarantee must hold while it is in use. `k[lo:]` uses the length after evaluating `lo`.” **Do not publish this as fully enforced until S3 is closed.** Until then explicitly list the function-value gap; disclosure alone is not my recommendation to ship it.
2. **Memory lifetime:** “A `mandapa` reuses its lexical scratch `nirmmita` storage at exit. It does not reclaim its `kosh` descriptors, their initial payloads or helper allocations. Outgrown large backing regions are released; old arena buffers and the initial descriptor/payload allocation remain. There is no general user `free`.”
3. **Limits and accounting:** “Capacities above `2^40` elements are refused at construction and growth. `parimana()` is allocator accounting, not RSS, commit or reservation; independent fallback mappings are excluded. `mandapa parimita` limits that block's scratch allocations, not the whole process.”
4. **Allocation failures:** “Checked `kosh` allocation failures are fatal diagnostics. Immediate raw allocation failure returns 0. On Windows, after successful runtime handler registration, failure to commit an eligible reserved page is fatal: best-effort `Sutram truti: smritih na labdha` on stderr, exit 1. There is no recovery guarantee, no guarantee that the failing operation was atomic, and no universal host-OOM guarantee.” Resolve W1 rather than leaving handler setup silently unchecked.
5. **Pointers/FFI:** “Raw and foreign pointers are not generally bounds- or lifetime-checked. A foreign borrow of `kosh` elements expires when growth moves them. Do not keep it across growth.”
6. **Arithmetic:** “Runtime integer operators wrap; overflowing literals/constant expressions are refused. Library functions follow their individual contracts: some terminate, some return a status or sentinel, and some saturate.”
7. **Strings/files:** “Strings are byte sequences; character/case helpers are ASCII-only. In-place copy/append/format operations require sufficient writable destination capacity. Literal destinations are refused; `s + t` creates a new string. `patra_asti` means opens read-only, not a general existence query. File-flag support is platform-specific.”
8. **Windows UI/delivery:** “The editor refuses files at its documented size limit; a refused load clears output and retains the previous editor file with a notice. Run Module has no interactive input; some UI remains English. Installer scripts are unsigned and use the documented launch policy; hashes establish integrity, not publisher identity. Native acceptance applies only to the exact binary hashes and workflows exercised.”

Make three further factual edits to the current notes: replace “no runtime, no dependencies” with **“native executables with embedded support code; no separately installed language VM; platform system APIs are used”**; replace the universal Linux OOM comparison as above; and update the Wine-observation paragraph's “native Windows has not been run on these versions” because native v305 evidence now exists. Keep the rare Wine exit fault as an unresolved observation unless a later investigation establishes its cause.

The registered installer `DisplayVersion` still says `0.1.0`; align that with the intended product-version scheme before presenting it as v1.0. This is a packaging identity correction, not the slice release blocker.

## 6. R205 WS3 / R206 WS3 — the missing coverage is at transitions and failure prerequisites

It would be false to answer “fuzzing”, “property testing”, “mutation testing” or “fault injection” as though this project had never used them. They exist: `fuzz_valid.py`, `fuzz_r23.py`, `proof_props.py`, `lib_proof_gaps.py`, and the Linux `--fail-alloc` gate. `fuzz_r23.py` even combines function values and slices, but its slice model uses small `mala` arrays. `fuzz_valid.py` deliberately keeps functions free of these side effects and does not model slices. Neither establishes the new descriptor/borrow transition invariant.

**For the Windows question, the missing method in the inspected coverage is deterministic failure injection at the runtime's OS-API boundaries.** A commit-limit sweep is valuable but does not choose which prerequisite API fails. Inject failure separately at handler registration, reservation, page commitment and diagnostic output, with success and unrelated-fault controls. W1 is exactly the sort of missed prerequisite this would expose. The existing `--fail-alloc` is Linux-only and bypasses `mmap`; it does not exercise these Windows paths. This is a scoped coverage finding, not a claim about every experiment ever performed outside the tree.

For the compiler, add **stateful descriptor/borrow model tests with call-form transformations**: generate short sequences of create, alias, slice, read/write, grow, shrink, clear and block exit; vary direct/indirect calls and argument placements. Cross small relocation and region-release boundaries. The oracle must permit either the documented result or the documented conservative refusal, and must reject silent stale writes and use-after-release. Do not assert universal equivalence of expression and statement side-effect order: that order is currently unspecified. Test the borrow invariant under each form's actual order.

A focused direct-to-function-value transformation of R204's existing reproduction would have exposed S3 without needing millions of random programs. Pairwise feature composition is the next useful extension of the existing methods, not a replacement for them.

## 7. Is the memory model finished, and what closes this review?

**No.** The descriptor representation, propagation through typed parameters, capacity bound and omitted-end rule are much stronger now. The remaining concrete class is **borrow provenance/effect information disappearing at an indirect or untyped boundary**. Windows additionally relies on a successfully registered handler without checking that prerequisite. Reading has not exhausted all possible defects; neither a finite corpus nor a source review can establish that.

The intended v1 scope can still be finished without adding a garbage collector, threads, generics, a new slice representation or general reclamation. For this candidate, the concrete acceptance sequence is:

1. Reproduce S3 on pinned v306, close the call-boundary gap, and retain both silent-write and region-release controls.
2. Handle failed handler registration and validate it with a targeted injected failure; keep the existing failed-commit, successful-allocation, invalid-stderr and unrelated-fault controls.
3. Apply the remaining factual release-note/package corrections, then build the actual replacement candidate and use the project's required change-specific guards.
4. Perform native Windows acceptance on that candidate's exact hashes: OOM controls, suite/layout, refused-load UI, wizard clean installation and upgrade, duplicate detection, PATH, and uninstall/recovery behavior.

A native v306 pass alone would not close S3. Conversely, source equality and the recorded v305-candidate native results are useful evidence for the OOM fix; they should not be discarded or inflated into final acceptance. This review recommends the smallest concrete closure above and adds no request for unrelated features or a redundant full rerun of unchanged work.
