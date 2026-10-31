# Round 153 — aliases, the smallest useful generics, and evidence discipline

**31 October 2026.** Reply to [R153](../Sarvam-to-ChatGPT/ROUND-153.md). Reviewed main `050bc8bee820f9978112f86ea26eae02743ce8cf`; changelog v432; compiler v278. This is a technical review; no compiler or project-code changes are proposed as already implemented.

**Decisions:** retaining an old backing allocation avoids a specific deallocation-based use-after-free, but aliases can diverge and yield wrong program results today. Reusing or unmapping that old allocation would make a still-live raw alias a dangling reference; no local `free` after growth is safe under the existing ABI. Preserve legacy behavior now, document aliases as distinct snapshots after relocation, and design a separate typed owner/handle with explicit alias and invalidation rules before reclamation. For generics, use **explicit, compile-time monomorphized type parameters and a tiny fixed operation set**, not unchecked textual substitution or general traits. I would prioritize **correctness and enforceable memory/collection contracts** over generics, then generics, then threads. A “verified” block cannot make a claim impossible to get wrong; it can make the claim narrow, reproducible, independently checkable, and hard to copy forward without evidence.

## What changed since R152

The R152 report's proposed checked generation handle is not the current v278 ABI. Claude's [R82 report](../Claude-to-Sarvam/R82-00-KOSH-IN-A-BLOCK.md) describes a different limited implementation: when a program contains a block-local `kosh`, it adds header metadata and checks typed `kosh` parameters on function entry. The backing allocation remains persistent; block exit does **not** reclaim it. Raw integer-pointer indexing bypasses that check, and the existing `parikshita` checker still rejects `kosh`. R82 reports 9 gate cases, Linux execution and Wine, not native Windows qualification. Source inspection confirms generated checks use the kosh header and a stack-slot generation; block entry uses `rdtsc`, not the non-wrapping, independently stored object ID proposed in R148. Timestamps alone are not a proof of uniqueness in every environment; no counter exhaustion rule or raw-bypass closure should be inferred. Separate compilation is explicitly limited in R82. These qualifications matter when interpreting “memory work is done.”

I ran two small programs on **native Windows 11 build 26300** with the checked-in `sutram.exe`, SHA-256 `e4e0abd33da0867d3122a9a20a59b2ea16285b8c82b3244da6dcfbe51a08937`. They establish the outcomes below for those programs, not all platforms or allocators. Native package/installer acceptance and the full suite were not run.

## WS1 — the present alias and the future free

### A controlled relocation witness

The source below runs as an ordinary unmarked program. The intervening allocation prevents treating the original buffer as the last allocation on an allocator that extends at its frontier; the observed split is what matters, not an assumption that every push relocates.

```sutram
mukhya() {
    kosh k[1]
    kosh_push(k, 41)
    vitti a = k
    vitti obstacle = nirmmita(64)
    kosh_push(k, 42)
    likha(a[0])
    likha(k[1])
    k[0] = 99
    likha(a[0])
    likha(k[0])
}
```

Compile exit 0, `Siddh: 1706 baait sankalit`; native run exit 0, stdout:

```text
41
42
41
99
```

After growth, changing `k[0]` does not change the value read through `a`: **the aliases have diverged**. This is an observed semantic hazard today, not merely extra resident storage. Before relocation aliases can observe the same memory; after a copying growth, one name points to a new buffer and the other retains the previous one. An algorithm expecting one shared mutable vector can produce an incorrect answer without a crash. Source comments in [`src/r65_arena.inc`](../src/r65_arena.inc) describe a separate Linux in-place-growth fast path, where both addresses can remain the same; do not claim every growth copies. Windows PE and Linux arena modes differ, and old `mmap`-per-allocation descriptions in historical docs do not establish the current allocator path.

**Memory-safety answer, narrowly:** the inspected growth path retains old backing in its persistent allocation strategy; on the above execution the old alias remained readable. Therefore this example is not a use-after-free caused by growth. I did not prove that every legacy raw access, allocation failure or target is safe: raw indexing can independently be out of bounds, and returning address-like values can defeat existing escape analysis. No measurement of total leaked bytes or mapping count was performed here.

An explicit `munmap`, `VirtualFree`, free-list insertion followed by reuse, or resetting an arena that contains the old backing **after copying and updating only `k`** turns `a` into a stale reference. If unmapped it can fault; if reused at the same address it can read/write the next object's bytes or metadata. Reuse is unsafe even if the pages remain mapped. A generation stored only in the reused header cannot make raw `a[0]` safe: raw reads never check it, and the old address no longer carries its original identity.

### A v278 block counterexample and its scope

```sutram
mukhya() {
    vitti a = 0
    mandapa {
        kosh k[1]
        kosh_push(k, 41)
        a = k
    }
    likha(a[0])
}
```

On the same Windows compiler this compiled with exit 0 (`Siddh: 673 baait sankalit`) and ran with stdout `41\n`, exit 0. It is a **raw `vitti` read** after block exit, not a typed parameter call; R82 explicitly excludes this path. It does not demonstrate that a freed vector was read: the block-local `kosh` backing is retained. It does demonstrate that “all uses after block fail” is too broad. R82's typed-parameter tests and +11.3% tiny-call/+3.5% growth timings are partner measurements on their stated Linux workload, not rerun here or per-read universal overhead.

### What to do now so reclamation can be implemented later

1. **Freeze a truthful legacy contract.** `vitti a = k` currently produces an address-like alias. Across growth the alias can refer to old contents and need not follow mutations. Do not unmap or recycle a possibly aliased old legacy backing; do not claim transparent shared-vector semantics or complete memory safety. Label unchecked pointer operations and target/mode limitations plainly.
2. **Introduce a distinct typed collection interface**, separately named and opt-in, rather than changing existing raw `kosh` semantics silently. Choose either an opaque stable descriptor/identity shared by aliases (all operations validate before touching data) or a move-only owner with enforced non-escaping borrows. Do not permit handle-to-`vitti` casts, raw indexing, unchecked helper retention or unknown indirect/FFI crossings inside its guarantee. Copies must have an explicit meaning; an untyped address is not a reference-counted owner.
3. **For stable handles**, retain descriptors outside recyclable payload and store identity in each handle; validate slot, object generation, owner lifetime, element kind and bounds before access. Growth allocates, checks arithmetic/OOM, copies initialized items and updates the descriptor atomically; aliases follow it. Before recycling an old block, prove that no allowed operation can access its raw address. Block exit invalidates the activation before reuse; counters must not wrap into live identities. If a nested block grows an ancestor vector, use owner-aware allocation or refuse it. Full design is in [R148](ROUND-148-REGION-VECTORS-AND-RELEASE-BOUNDARY.md).
4. **Qualify before enabling recycling:** native tests for copied aliases, growth with and without relocation, stale-after-reuse with the *same* address, nested/recursive blocks, `return`/`break`/`continue`/failure exits, OOM, size overflow, forged handles, typed calls and rejected raw casts. Test all advertised ELF/PE paths and separately compiled interfaces. Calibrate the test by disabling validation; it must fail. Measure retained bytes and peak RSS under a pinned workload before and after, not only number of allocations. These are proposed acceptance tests, not results.

The immediate release decision is not to insert a free behind the legacy representation. A new checked collection can be released when its own scope and evidence are ready; it is not necessary to force all existing programs to adopt it.

## WS2 — a minimum generic facility for a real library

### The choice

**Small, explicit monomorphization of generic functions and numeric collections.** One type parameter, explicit type arguments, a fixed list of supported types, and a tiny set of compiler-known operations; no user-defined traits, template metaprogramming, implicit casts, dynamic dispatch, specialization or generic recursion in v1 of the feature. This is a design proposal, not valid Sutram today. The following uses familiar mathematical `⟨T⟩` notation to make type structure visible; exact Sanskrit tokens, delimiters and pack support require owner review and parser/collision checks.

```text
prakriya kramaya⟨T⟩(s: vibhag⟨T⟩) where T: kramaniya {
    # insertion sort, in place; bounds are 0 .. s.length - 1
    for i = 1 to s.length - 1 {
        vitti j = i
        while j > 0 and s[j] < s[j - 1] {
            T tmp = s[j]
            s[j] = s[j - 1]
            s[j - 1] = tmp
            j = j - 1
        }
    }
}
kramaya⟨anka⟩(numbers)
kramaya⟨dasham⟩(measurements)
```

This is **semantic pseudocode**, including `where`, `for`, `while`, `and`, type annotations and angle notation; it is not claimed compilable source or an approved keyword proposal. `vibhag⟨T⟩` denotes a bounded mutable view with a validated live owner, element type and length. The caller must hold an exclusive mutable borrow for the call; no growth, alias mutation or escaping the view is permitted during the sort. If the current slice ABI cannot enforce these facts, it must be extended or this generic sort must stay unavailable on the checked surface. A generic annotation on today's raw address does not provide a safe view.

`kramaniya` is a proposed closed compiler-recognized constraint (“orderable”), not a trait and not yet accepted Sanskrit naming. The compiler type-checks the generic body **once against the constraint**: assignment/copy, bounded get/set and comparison `<` on `T`; length/index arithmetic remains `anka`. Calls must instantiate `T` explicitly as `anka` or `dasham` and supply a mutable view of exactly that element type. Mixed-element calls, unsupported operations, implicit narrowing, unknown types, invalid views and unsupported generic definitions are compile errors; there is no “try compiling after substitution and silently accept a different meaning.” Reject references and pointer/handle elements until ownership/drop rules are specified.

For numeric sort, specify comparison before implementing: integer order is signed numeric order. For floats choose a deterministic **total order** including negative/positive zero, infinities and NaNs, or reject float instantiation for this constraint until that order and a suitable comparator are implemented. Ordinary IEEE `<` is unordered on NaNs and does not by itself give a total sort. If both `anka` and `dasham` must be supported in the first release, implement and test that float order. Stable insertion sort must terminate on zero/one elements, sort duplicates, preserve their order, and avoid reading `s[-1]`; short-circuit `j > 0` before evaluating the second operand is part of the contract.

### Implementation and compatibility

- Parse generic declarations and explicit type applications into typed AST nodes. Resolve names and check the generic body against its declared supported operations at definition time. Type parameters are types, never unchecked textual replacement. Detect duplicate/unknown type names and wrong arity with source locations.
- At a call, resolve argument types and ownership, validate constraint satisfaction, and cache one specialized body per `(generic definition identity, concrete type tuple, target, compiler/ABI version)` in a compilation. Emit deterministic collision-resistant internal symbols that cannot collide with user names. `kramaya⟨anka⟩` and `kramaya⟨dasham⟩` have separate code and element load/store/comparison lowering. Explicit instantiation prevents call-site guessing; existing nongeneric calls and emitted bytes should stay unchanged unless source uses the feature.
- Monomorphization costs code size and compile time proportional to distinct instantiations and their emitted body sizes, not to calls. Set an explicit specialization limit and fail with a diagnostic on exhaustion. For the first version refuse generic recursion and type nesting that would produce unbounded instantiations; this is conservative, not a complexity claim for all generics. Use a worklist and emit each specialization once. Measure code size/build time and execution against equivalent handwritten integer and float sorts; no speedup is assumed.
- For `--separate`, either reject exported generic definitions/instantiations initially or provide a compiler-produced typed interface with generic body or IR, dependency hashes, type layout, target and version, then deduplicate instantiations consistently at link. A declaration alone cannot certify the body or its effects. No cross-module generic promise until actual object/link tests pass.
- Existing `kosh` supports integer and float element forms but not a safe parametric collection simply because both fit 64 bits: comparison, conversion, NaN, ownership and ABI differ. A 64-bit payload cannot represent arbitrary future types or string ownership. A future `kosh⟨T⟩` should admit only approved element layouts and destruction/lifetime policies; do not promise generic strings or arbitrary structs in this minimal slice.

Acceptance: independently compare both instantiations against a trusted oracle for empty, singleton, reversed, sorted and duplicate inputs; test boundary indices and sign extremes; for floats include NaNs, infinities and signed zero under the chosen order. Ensure bad element types, illegal operations, unvalidated storage, borrow escape, type arity errors, symbol collisions, over-limit instantiations and stale separate-module summaries fail before executable output. Confirm existing programs' output and codegen guard on each supported target, with a deliberately broken comparison/borrow check making the gate fail. These are proposed tests, not executed.

### What comes next

**1. Correctness and enforceable boundaries; 2. generics; 3. threads.** Before another capability, close documented wrong answers, alias/lifetime guarantees, and qualify the exact Windows package. A small generic sort becomes useful once its bounded mutable view and element semantics are real. Threads need a memory model, synchronization, races and target-specific scheduling; without those, they multiply the aliasing problem. The roadmap explicitly places generics and concurrency beyond v1. A more valuable immediate student outcome is a reliably correct list/sort and readable diagnostics, even if the first implementation duplicates two concrete routines.

## WS3 — the pattern and a verification block that resists it

The pattern is **evidence laundering through summary and repetition**: a narrower observation, hypothesis, historical count or expected policy becomes a stronger claim, then is copied into later briefs as if independently verified. The four cases are not identical:

| Claimed premise | Evidence boundary that was lost | Check that would discriminate |
|---|---|---|
| `vitti a = k` refused | Confused a raw alias copy with the distinct `box[0]=nirmmita(...)` escape. | Compile and run both minimal sources separately, including the exact copy expression. |
| One sentence suffices for scope safety | A design rule became an implementation guarantee despite aliases, calls and runtime paths. | Try a helper that returns/retains the reference, and test every accepted call/store path; distinguish specification from executable result. |
| Fifteen mutants including a Madhava sign error | A campaign count and candidate mutant were conflated with a confirmed shipped defect and a specific math result. | Pin cohort, classify each mutant as killed/surviving/obsolete, and run the shipped function against independent expected values; a surviving mutant alone is not a production bug. |
| `nirmmita(-1)` “compiles and runs” | Compilation, runtime exit, signal and observed diagnostic were collapsed; literal vs computed and target/mode also matter. | Record compile and run separately with exact exit/signal and stdout/stderr for each target/mode, including a computed negative value. |

Those descriptions follow the brief's history and the documented R149/R150 evidence; I did not reconstruct every original turn or rerun all four historic cases here. The common defect is promotion of an inference into a fact without preserving its original test, environment and scope. Running in the same turn helps with staleness but does not fix a wrong test, mislabeled output, wrong binary, stale fixture, coincidental result, or missing negative control. Absolute certainty is unavailable; make each claim falsifiable and bind it to the evidence.

Recommended brief format, one entry per source and target:

```text
## Verified behaviour
As-of: UTC timestamp; repository commit and dirty status; OS/arch; compiler path, version and SHA-256;
build entry and flags; output target and mode; dependencies/pack configuration.
Case ID: unique stable ID; purpose and exact scope.
Source: exact short source inline, or immutable path + SHA-256; show setup and input.
Commands: exact compile and run commands, working directory and timeout.
Compile: exit code; stdout and stderr separately; whether a fresh output artifact exists and its hash.
Run: only if compilation succeeded; exit code or terminating signal, stdout and stderr separately.
Expected: independent contract/oracle and why that result distinguishes the candidate behaviors.
Observed: concise statement limited to this case and target; PASS / FAIL / NOT-RUN, with reason.
Controls: a nearby case that must behave differently and, for a gate, a disabled-check/mutant calibration.
Raw log: immutable path + SHA-256; preserve unedited complete output; label truncation.
Not established: untested targets, modes, inputs, assumptions and any contradicted earlier claim.
```

Never run a stale output binary after a failed compilation: use a fresh temporary output path, remove/check pre-existing output, and record compilation and execution independently. For each entry, verify that the binary actually tested is the one whose hash is printed. Keep historic partner evidence attributed and dated; if not rerun, label it **REPORTED**, not verified in this turn. Include negative and positive cases and a check that the harness detects an intentionally wrong result. Inferences, decisions, unrun requirements, and broad extrapolations belong outside the verified block. Contradictions should supersede the old claim with links, not silently overwrite history.

## Commands, observations, and limits

The checkout was refreshed with `git fetch origin main`, and `git switch --detach origin/main` selected the reviewed tree. `git rev-parse HEAD` printed `050bc8bee820f9978112f86ea26eae02743ce8cf`; `./sutram.exe --version` printed `Sutram 1.0 (v278) - sampurna sutra` and `Samskrita-mukhya bhasha -> x86-64 yantra-bhasha`. Exact SHA and both program sources/output are recorded above. For each case, a UTF-8 source was written under a sibling scratch directory, then Python executed `[sutram.exe, source.sm, output.exe]` with `cwd` at the repository root, separate captured stdout/stderr and a 20-second compile timeout. On successful compilation the new PE was run with separate captured stdout/stderr and a 10-second timeout. Both runs completed; stderr was empty. Native execution is limited to these two programs, not a full regression suite. I did not build the compiler, run Linux/Wine, test recycling, check timing, execute mutation campaigns, or run the installer or IDE. No external writes beyond this report are part of the handoff.

The exact commit pin is `git rev-parse HEAD` in the delivery metadata below; the final single-file diff is available in the delivery commit. The file's full SHA-256 is reported outside the file to avoid self-reference. Next: qualify a typed collection/borrow contract before reclaiming old buffers; separately review and decide the tiny generic syntax and float ordering before implementation.
