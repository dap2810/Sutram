# R186 — repair the typed binary64 dot product and its result ABI

Base: `1ea8220426c9a6377d90ee8860a969f8b99bb3a0`, compiler v292, 2026-11-03. Read-side design delivery. Compared with the R184/R185 source base `ff5d9d419976f3f48f37e63ab4aefaa56f41dd9b`: intervening changes are handoffs/evidence only; the inspected compiler and library files are unchanged.

**Choose option 1: two typed `kosh dasham` inputs, equal logical lengths, returning a binary64 `dasham`. Refuse unequal lengths before reading elements.** A separate vector type is unnecessary: two suitable library loops already exist. The builtin needs both an input-representation repair and a return-type/ABI repair.

## 1. What the current code actually does

`src/sutram_compiler.asm:23719` (`.ge_call_vecdot`) loads exactly 16 bytes from each supplied pointer with `movups`, multiplies four binary32 lanes with `mulps`, reduces them with two `haddps`, then uses `movd eax,xmm0`. It returns a zero-extended **binary32 bit pattern**, not a binary64 numeric value. Despite the comment, it does not emit `dpps`. It has no length-driven loop and no collection-type validation in this emitter.

`expr_is_float` at line 26355 does not recognize BN_VECDOT as a floating result: its builtin cases recognize kosh pop/peek/dequeue only. Merely replacing `mulps` with binary64 multiplication would leave result classification wrong. Merely converting the final binary32 result to binary64 would leave input interpretation wrong.

Two corrections to the brief matter:

- A current kosh variable points to its **element data**, not its header. `r82_emit_kosh_header` at 10492 writes five header qwords then advances the pointer by 40. Logical length is at `[ptr-16]`; capacity is at `[ptr-8]`. Do not add 40 to an already-adjusted user pointer in the replacement.
- Four packed binary32 values are not a supported typed collection, but raw byte/cell operations can construct that representation. “No constructible input” is too strong. The actual defect is that the public builtin does not implement its advertised numerical operation over normal Sutram collections, and its return is not a dasham. Raw packed buffers would need a separate explicit low-level contract.

The attached [read-side evidence](ROUND-186-READ-SIDE-EVIDENCE.json) models the emitted representation arithmetic, without running Sutram:

| Input cells | Interpreted four binary32 lanes | Current model result | Correct dot |
|---|---|---|---|
| integer 5, 6 | tiny subnormals, 0, tiny subnormals, 0 | 0 | 61 |
| binary64 5.0, 6.0 | 0, 2.3125, 0, 2.375 | float32 10.98828125, returned integer bits 1093652480 | 61.0 |

The integer result agrees with Sarvam's reported observation; that is corroborating source analysis, not an independent native reproduction. Reads from empty or short inputs can also exceed logical data: spare capacity does not make those elements valid.

## 2. Three choices

| Choice | Representation, cost and limitation | Decision |
|---|---|---|
| Typed decimal kosh dot | Binary64 elements, logical length available, scalar O(n) loop, O(1) working storage, no allocation or external runtime. Correct result typing must reach callers. | **Choose.** Matches existing statistics and linear-algebra APIs. |
| Integer mala dot | Requires trustworthy length metadata or explicit lengths at untyped boundaries. Integer products and the accumulator can overflow even when a final mathematical result fits through cancellation. Checked, wrapping and saturating contracts differ. | Useful separate future operation, not an equivalent replacement. |
| Withdraw | Stops advertising broken behavior but removes a useful operation already expressible with typed collections. | Temporarily refuse unsupported calls until repaired; do not withdraw the mathematical capability permanently. |

For n elements, a simple implementation uses 2n element loads, n binary64 multiplies and n binary64 additions, plus index/branch work and two initial length reads. Logical input traffic is 16n bytes, not a measured DRAM figure; cache reuse can reduce physical traffic. A direct lowering avoids a call, while a shared helper adds ordinary call overhead. No benchmark, generated code size or speed ratio is claimed.

### Precise contract

- Inputs: two live `kosh dasham` values. Reject integer kosh, mala and raw pointers rather than reinterpret them. A future explicit conversion may accept integer data separately.
- Check both lifetimes using existing kosh machinery, then compare **logical lengths**, once each, before element reads. Evaluate input arguments once, left to right. Support typed parameters without losing provenance.
- Length mismatch: a clear Sanskrit diagnostic and fail-stop refusal in the two-argument builtin. Never silently select the shorter length. This is a shape error, not numeric zero.
- Equal empty inputs: return `+0.0`. One empty and one nonempty: mismatch.
- Equal nonempty inputs: left-to-right binary64 `sum = sum + a[i]*b[i]`, initially `+0.0`. Inputs unchanged; `a` and `b` may be the same collection.
- Specify separate multiply/add rounding; no FMA or reassociation in the initial contract. Floating rounding, cancellation and intermediate overflow remain possible; this is not arbitrary-precision or an exact-real dot product. Non-finite values follow the defined scalar binary64 arithmetic policy, not a new silent sentinel convention.
- Return binary64 bits through the normal Sutram float-return convention and mark BN_VECDOT as float in expression/type inference, printing, assignments and nested calls. Do not return float32 bits as a vitti.
- Keep both `sankhya_bindu` and legacy `sankhya_dot` mapped to the same corrected operation. This is an intentional semantic repair: disclose changed results and rejection of old raw-pointer calls, rather than calling it byte-compatible.

Do not promise a native `dosh` carrying a dasham result today. R185 documents that the native result interface does not support floating payloads. If recoverable mismatch is required immediately, a separate explicitly named checked wrapper can use an already-established status out-parameter contract with a float return. Its caller-owned output must exist and must not alias either input. Zero alone must never encode failure. A general float-result ABI is a separate design decision.

### Reuse existing work, without silently changing old contracts

`lib/sankhyiki.smlib:99` has `bindu_gunan(kosh dasham a, kosh dasham b)` and `lib/samanvaya.smlib:135` has `adish_gunan(kosh dasham u, kosh dasham v)`. Both already loop over binary64 elements and return a dasham. They currently use `min(length_a,length_b)`.

`examples/207_sankhyiki_vector.sm` explicitly teaches that truncation. Preserve those library contracts until an owner-approved migration; do not silently change their goldens while repairing the builtin. The strict builtin can reuse their arithmetic structure with an up-front equality check. If a library implementation is chosen, explicitly arrange lowering/linkage; an ordinary user procedure cannot simply shadow a reserved builtin token. In the longer term, one documented strict semantic implementation should back the public dot-product APIs, with prefix behavior retained only under a clearly distinguished compatibility contract.

## 3. Name and four tests

**Retain `sankhya_bindu` for the repaired dot product.** No new synonym is necessary.

| Test | Result |
|---|---|
| Complete word/compound | `sankhya` + `bindu`, existing project compound; not a clipped English fragment. |
| No collision | It is already the canonical BN_VECDOT name, with `sankhya_dot` its compatibility alias. Reuse that exact symbol, not a second declaration. Existing `bindu_gunan` and `adish_gunan` are occupied library names and cannot be proposed as fresh declarations. |
| Typeable | ASCII spelling, 13 characters including underscore, already used in the project. |
| Meaning describes operation | The repaired operation really is a numerical dot product; documentation must specify two decimal sequences and equal lengths. The brief already accepts bindu's meaning. |

This is a reuse decision, not a claim that the existing name is absent from the namespace. Linguistic certification is not claimed. If packed binary32 intrinsics remain, give them an explicitly unsafe representation-specific API through separate review; do not retain the current misleading general contract under a cosmetic Sanskrit rename.

## 4. Wider source review: distinguish defects from documented limitations

This was a targeted review of adjacent builtins and numerical/file libraries, **not certification of all 306 definitions**. The broken builtin itself is not one of those 306 library procedures. None of the following is a new native test result.

### A. Same representation defect in two neighboring builtins — high priority

`sankhya_yog` (`.ge_call_vecadd`, line 23594) and `sankhya_gunan` (`.ge_call_vecmul`, 23660) load/store 16 bytes and apply packed binary32 add/multiply. They are documented as “integer add” and “integer multiply” in `docs/LANGUAGE-REFERENCE.md:160–161`. Their source and reference do not describe the same operation. They cannot serve as general whole-collection arithmetic on either i64 or binary64 cells. Multiplying integer cells 5 and 6 as float32 lanes underflows toward zero. Three pointer arguments also make a scalar integer description misleading.

Action: review/contain all three intrinsics together. Specify typed elementwise operations with lengths and output capacity/alias rules, or explicitly withdraw their high-level claims. A fixed 16-byte low-level operation needs its own bounds, lane-type, ISA and unsafe contract. The dot emitter's `haddps` additionally imposes an instruction-set requirement that a scalar baseline loop can avoid; do not infer AVX from stale comments naming vaddps/vmulps.

### B. Integer mean can be wrong even when its answer fits

`lib/sankhyiki.smlib:131–145`: `purna_yoga` adds with ordinary wrapping integer arithmetic; `purna_madhya` divides that already-wrapped sum. For `[MAX,MAX]`, n=2, the model sum is -2 and mean is **-1**, whereas the correct mean is **MAX**. This is not merely unavoidable overflow of the requested mean: the mean is representable.

`purna_prasaran` at 182 then consumes that bad mean. On the same constant data, its difference guard returns -1 although the correct variance is zero. The function's checks on squared deviations do not repair the earlier mean.

Action: compute a checked/widened or rigorously overflow-safe mean; do not “fix” this with binary64 conversion, which loses integer precision near MAX. Specify and test mixed signs, truncation toward zero, MIN/MAX and cancellation. Preserve the documented integer-variance convention based on the truncated mean unless explicitly changing it.

### C. Matrix output aliasing silently corrupts input

`lib/samanvaya.smlib:50–62`: `vivartana(a,2,2,a)` on `[1,2,3,4]` overwrites an element before reading it. The model gives `[1,2,2,4]`, not `[1,3,2,4]`.

At lines 91–108, `matrika_gunana(a,I,2,2,2,I)` overwrites the identity input while using it. Model result `[1,2,3,10]` differs from `[1,2,3,4]`.

These are **missing alias-contract/enforcement findings**, not proof that disjoint-input implementations cannot work. The header says inputs are read-only and outputs written in place, but does not make an enforceable non-overlap precondition explicit. Existing tests use distinct outputs.

Action: reject overlapping output/input before writing, or provide explicit caller-owned temporary storage/in-place algorithms. Exact pointer inequality alone does not establish non-overlap for arbitrary raw views. Do not reject every matrix operation's aliasing indiscriminately: simple elementwise operations have different dependency patterns.

### D. Norm loses a representable nonzero answer

`lib/sankhyiki.smlib:114–116`: `manak` squares via dot product and then takes a square root. For `[1e-200]`, binary64 squaring underflows to zero although the norm `1e-200` is representable. The read-side model returns 0.0. Large finite elements can similarly overflow the intermediate sum of squares.

Action: use a scaled sum-of-squares norm, with separately specified zero/non-finite handling. A generic dot-product replacement alone does not fix this. This is a numerical stability/domain limitation, not a claim that ordinary small inputs fail.

### E. File “any error” promise ignores close status

`lib/patra.smlib` promises -1 on any OS error, but `patra_likh_sarv` at 57–76 calls `band(fd)` and unconditionally returns the accumulated count on its success path. `patra_path_sarv` similarly discards close status. Source proves the return is unchecked; no real filesystem failure was induced here.

Action: define whether close errors are part of success, then check the result once according to the target OS contract. Do not add blind close retries. Separately, the known `patra_asti` behavior tests read-openability, not existence independent of permissions; its current local comment already admits that limitation.

### Findings that should not be overstated

`bindu_gunan` and `adish_gunan` do compute useful dot products, including equal-length input; their prefix-length policy is documented. `viparyay_ank` overflow is explicitly pinned as wrapping by `tests/stdlib/numeric29.sm`, so it is not a newly discovered hidden representation defect. Empty statistics returning zero, truncated integer variance and negative-domain sentinels need clear documentation, but should not be presented as universally broken functions merely because their mathematical domains are narrower.

## 5. Acceptance work for the implementation owner

Native build, suite, guard, Windows execution: **NOT RUN — no toolchain used in this read-side assignment.** The accompanying JSON contains executed Python representation/arithmetic models only.

Before accepting a replacement, test:

1. Binary64 `[5,6]` self-dot =61; `[1.5,2.5]` dot `[2,4]` =13; equal empty =0; one element, odd lengths and lengths greater than two. Check printing and using the result in float arithmetic, return values and assignments.
2. Reject mismatched lengths in both directions, including empty/nonempty. Verify refusal before any element read or output mutation. Capacity greater than logical length must not affect the answer.
3. Reject integer kosh, mala, scalar and raw-pointer inputs under the typed contract; check both old/new names and arity. Validate kosh parameters and expired mandapa references.
4. Self-aliasing of the two read-only inputs succeeds; inputs remain unchanged. Preserve existing evaluation order and lifetime checks.
5. Cancellation/rounding, finite extremes, signed zero, non-finite inputs and the declared scalar evaluation order. Do not turn ordinary floating approximations into a claim of exactness.
6. Add independently calculated oracles for the concrete library findings above; separate expected refusal from numerical success. Test on each supported native target before claiming portability.

R184 and R185 remain delivered with their stated limitations; R186 adds this higher-priority design and targeted review. No src/, lib/, tests/, tools/, production documentation or frozen non-Sanskrit packs were changed. No merge or CI run was performed.
