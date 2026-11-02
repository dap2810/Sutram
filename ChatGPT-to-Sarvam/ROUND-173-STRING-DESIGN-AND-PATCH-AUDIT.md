# R173 — usable strings and FIXALL patch review

**Read-side audit/design, 2026-11-02.** Base: `106f2074ba675972bde3e25d2cf13c25307bb6c1` (v285).
Patch reviewed: `Muse-to-Sarvam/fixall_r100.patch`, with its report and evidence JSON. Delivery is documentation only.

**Verdict: request changes before accepting FIXALL unchanged.** The refusals address real traps, but source inspection finds a straight-line string-check bypass, inconsistent fast-path rules, and an environment-dependent recursion guard. For the language, **typed strings should compare contents and concatenate into a fresh value**. NUL-terminated pointers can already support both; a length prefix is an improvement option, not a prerequisite.

## WS1 — decision on each of the five changes

| Diagnostic/change | Immediate judgment | Intended language behavior |
|---|---|---|
| `E_LIKHA_TRAYA` | A compile-time refusal is an honest temporary replacement for the ambiguous raw-write interpretation. Separating `dvaram_likha` is useful. | After an explicit compatibility transition, `likha(a, " ", b)` should print three values. Once raw writes have their own operation, the literal-first exception should not become permanent. |
| `E_VARTANI_TUL` | Refusal is acceptable containment for operations whose operand types cannot yet be established. The patch's partial tracking is not sufficient to declare this trap closed. | Two text values: `==` compares contents and returns 1/0; `!=` is its complement. Text versus a number should be a type error unless a specific conversion is requested. |
| `E_VARTANI_CAT` | Refuse unsupported text addition temporarily. Do not advertise the existing unbounded mutable append as an equivalent safe replacement. | `s + t` returns newly allocated concatenated text, leaving both inputs unchanged. Allocation, overflow, lifetime and budget rules must be specified. |
| `E_MULYA_VINA` | **Accept the requirement that scalar locals have initializers as a small, explicit policy. This patch already reports a compile-time error.** | A future definite-assignment analysis may allow declaration followed by guaranteed assignment before every read. Runtime detection is unnecessary when the declaration is statically visible. Globals/arrays/empty collections need their separately documented rules. |
| `E_GAHANATA` | A clean runtime resource-limit diagnostic is appropriate. **Do not accept the fixed threshold as portable stack-exhaustion protection.** | Permit legitimate recursion within the supported resource budget; diagnose exhaustion before faulting. It does not prove that recursion lacks a base case. |

Two premise corrections:

- Strings **can already be compared**: builtin `vartani_tul(a,b)` scans NUL-terminated contents and returns **0 if equal, 1 otherwise**. `khand_sam(a,an,b,bn)` provides explicit-length equality; `khand_tul` provides bytewise ordering. Refusing an operator does not remove those APIs.
- “Every other language compares contents with ==” is too broad: Java's String `==` compares references, while `equals` compares contents. That is not a reason to copy Java's operator choice. Sutram's teaching goals favor content equality. [Java language specification §15.21.3](https://docs.oracle.com/javase/specs/jls/se9/html/jls-15.html#jls-15.21.3).

## Patch audit — findings to address before acceptance

### P173-01 — assigning to a string erases the evidence before checking the RHS

**Blocking; source-derived, NOT RUN.**

The added code at `.gs_assign` calls `rfx_note_value(target, RHS)` **before** evaluating or checking the RHS. `rfx_note_value` recognizes only AST_STR and AST_VAR; an AST_BINOP clears the destination's string flag.

Consequently, for:

```text
mukhya() {
    vitti s = "ab"
    s = s + s
    shabda(s)
}
```

the flag for `s` is cleared before either operand is classified. Both references to `s` now appear non-string to the fast path and generic checker. Source inspection predicts address addition survives, rather than `E_VARTANI_CAT`. The later `shabda` receives an invalid text address; **no particular crash/result was observed here**. `s = s + "cd"` is another important case: the cleared left operand can be accepted as an integer offset beside the literal.

This contradicts the report's “straight-line code is exact” claim. It is not merely the acknowledged branch-analysis limitation.

**Fix:** analyze/check the RHS against the incoming type state, obtain its result type, then update the destination state. Every optimization must use that same resolved classification. Preserve enough incoming state for self-referential assignments; moving one flag write is necessary but does not solve the broader type-analysis gaps.

### P173-02 — optimized and generic paths disagree on permitted pointer arithmetic

**Blocking; source-derived, NOT RUN.**

The generic `rfx_check_str_binop` permits one string operand plus an integer-like operand. But the added ADD checks in `try_emit_int_decl_reg` and `try_emit_int_reg_assignment` refuse when **either** operand is string-marked, without applying that generic exception.

Proposed paired probes:

```text
mukhya() {
    vitti s = "abcd"
    vitti off = 1
    vitti p = s + off
    shabda(p)
}
```

```text
mukhya() {
    vitti s = "abcd"
    vitti off = 1
    shabda(s + off)
}
```

With register-eligible locals, the first shape reaches the fast declaration rejection; the second reaches the generic pointer-offset allowance. Adding enough locals to spill the destination can also change which rule is applied. **These are predictions from the inspected branches, not compiler runs.**

**Fix:** decide the operator's meaning once, before register allocation/code generation. Fast paths may change how an accepted operation is emitted; they must not change whether it is legal. If pointer offsets remain in the legacy raw API, apply that policy consistently. In a typed text API, use explicit bounded slicing rather than silently treating text-plus-integer as text or raw address arithmetic.

### P173-03 — “not known to be text/float” is not proof of an integer

The patch explicitly leaves parameters, call results, globals and indexed values untracked, and uses last-emitted assignment state across branches and loops. `rfx_is_int` accepts other expression kinds when `expr_is_float` returns false. A call returning a text pointer therefore can qualify as an integer offset.

Proposed bypass probe, **NOT RUN**:

```text
prakriya banao() {
    nivartanam "cd"
}
mukhya() {
    vitti s = "ab"
    vitti u = s + banao()
    shabda(u)
}
```

Similarly, an untyped `prakriya barabar(a,b) { nivartanam a == b }` does not acquire text types just because a caller passes two text values. A branch that assigns a number can erase evidence even when that branch is not taken at runtime.

The report acknowledges much of this. The scope limitation is honest, but the feature must be described as **partial trap detection**, not closure of string operations. Simply replacing a detected comparison with a byte scan using these same flags can turn a missed refusal into an invalid memory read.

**Fix direction:** maintain a real distinction between text, integer, raw pointer and unknown/mixed values. Merge control-flow states conservatively; establish parameter/result/global contracts or reject unresolved overloaded operations. Fixed inferred binding types are a simpler initial policy if accepted explicitly. If reassignment between kinds remains allowed, flow analysis must model it. Unknown is not synonymous with integer. This need not require dynamic tags, a C runtime or a GC.

String ordering and other numeric operators on text remain separate holes; the patch's equality checks do not close them. Existing `khand_tul` means explicit bytewise ordering is already possible even though `vartani_tul` itself is only an equality-style result.

### P173-04 — recursion threshold depends on the actual stack environment

**Blocking for the claimed universal protection; source-derived, NOT RUN.**

The patch compares `entry_rsp - rsp` against **8,339,456 bytes** after function prologue work and `sub rsp, 2048`. Its successful guard path is four instructions: load, subtract, compare, conditional branch. That is inexpensive, but the constant does not establish where this process's stack actually ends.

Linux's enforced stack limit can be smaller than 8 MiB, and argument/environment storage also matters. With a smaller limit, earlier prologue pushes/calls or frame accesses can fault before the fixed threshold is reached. Repeated ASLR runs in one environment do not prove an all-environments guarantee. [Linux getrlimit manual, RLIMIT_STACK](https://man7.org/linux/man-pages/man2/getrlimit.2.html).

**Fix direction:** derive a supported stack bound at startup, accounting for initial usage, worst-case frame/temporary/argument demand and diagnostic headroom, then check before dangerous stack consumption; alternatively use a deliberately managed stack with known bounds. Reading RLIMIT_STACK alone is not an exact remaining-space calculation. A configured recursion budget is also useful, but must be labeled a policy limit rather than a universal fault-prevention proof.

Keep PE and object/separate-mode exclusions explicit. Test the requested 500-level correct recursion, mutual/no-base recursion, boundary depths, and smaller stack limits/large environments. The 500-level case must return the expected value in the supported configuration, not merely avoid a crash.

The patch emits the diagnostic bytes in each function. Userspace fast-path cost is four instructions; emitted guard/trap cost is **22 + 36 + message_length bytes per guarded function**, plus a seven-byte entry save and eight-byte shared slot, based on the patch's layout. Kernel/latency cost is not measured here. Consider a shared cold failure stub to reduce duplication after correctness.

### What the patch does well, and what its evidence does not establish

- It separates raw writes from a printer overloaded by argument syntax, preserves the write result needed by `patra_likh_sarv`, and migrates its selected call sites.
- It refuses bare local scalar declarations during compilation rather than leaving old register/stack contents observable.
- Appending/patching the stack-top slot after allocator globals addresses the specific global-slot collision described in its report.
- It states substantial exclusions instead of presenting them as tested.

I independently read the **18-file diff (+757/-68)**. An **in-memory exact-context application matched all 50 hunks against this pinned v285 tree**, including 30 compiler hunks. No working-tree source was changed. This is not a native build and not a substitute for Claude's `git apply --check` and regression runs.

Muse's 270 suite passes, proofs and 549 DIFFERs refer to its earlier v283-based test environment. They were **not reproduced here**. Compilation exit 0 for both versions is not proof that all 549 programs print identical output. Run each affected case as requested in R104, recording expected refusals separately from compatible output and unintended changes. For migrated raw-write sources, distinguish old-source/old-compiler from migrated-source/new-compiler tests rather than implying identical source input.

## WS2 — content comparison does not require a new representation

Current literal emission produces NUL-terminated bytes and returns an eight-byte address. `.ge_call_vartcmp` already emits a byte loop; `.ge_call_vartcat` already scans a destination and appends source bytes in place. The hard problems are **typing, capacity, ownership and consistent lowering**, not the absence of any byte-comparison algorithm.

### Stage 1: typed NUL-terminated text, reusing the existing comparison kernel

For operands proved to be valid terminated text:

- Evaluate each operand once in the defined order.
- Compare bytes until the first difference or shared terminator.
- Convert the existing 0-equal/1-unequal result into a language boolean. Because its result is exactly 0/1, `==` can invert it with one XOR; `!=` can use it directly. Conditions must use the same semantics.
- Do not call this scan on a number, an unbounded raw pointer, a nonterminated slice, or a dead reference.
- Keep existing explicit builtin conventions unchanged; changing `vartani_tul` to return 1 for equality would break callers.

**Cost:** no allocation and no extra string-object metadata for this representation. Reading the current emitter gives **nine instructions per matching non-NUL byte** in its simple loop (two byte loads, compare/branch, zero-test/branch, two increments, jump), plus setup/termination. This is a **source hand-count**, not disassembly or a timing measurement. The boolean inversion adds one instruction for equality. Work is O(common prefix + 1), at worst linear in string length; pointer equality was constant work but answered the wrong text question.

A length prefix can accelerate unequal-length rejection and length lookup. It is not needed to stop returning false for separately stored identical text.

### Representation alternatives and prices

The following are **layout/design estimates**, excluding allocator and lifetime metadata, padding, cache effects and validity checks.

| Representation | Reference/storage cost | Equality and length | Concatenation implications |
|---|---|---|---|
| Typed NUL-terminated pointer | 8-byte reference; N+1 bytes payload | Equality scans; length is O(N). Cannot represent embedded NUL as part of this text contract. | Determine lengths, allocate result, copy. No ABI width change, but real compiler type information is still required. |
| Owned length-prefixed text, pointer still addresses bytes | 8-byte reference; 8-byte length prefix + N+1 payload, then alignment | Load two lengths and compare/branch, roughly 4 instructions before content loop; length is one load. Equal-length content still needs checking. | Known lengths eliminate preliminary scans. Raw/interior pointers cannot safely be assumed to have a prefix. |
| Explicit byte view (pointer, length) | 16-byte value; may borrow payload with no new header | O(1) length; unequal lengths can reject immediately; bounded byte comparison | Supports slices/embedded NUL. Changes parameter/return/spill/container handling; ownership and lifetime need a separate contract. |

**Recommendation:** first fix type classification and deliver correct operators for the established terminated-text contract. Keep explicit-length byte APIs for slices. A length-bearing text/view design is the stronger long-term direction, but migrate deliberately across callers, globals, fields, collections, module ABI and raw-byte interop. Do not read `[ptr-8]` from today's arbitrary eight-byte values.

Define text equality initially as **exact UTF-8 byte equality**, without implicit case folding, locale collation or Unicode normalization. Identical Sanskrit bytes compare equal. Canonically equivalent but differently encoded sequences need not compare equal under this contract. Lengths above are **bytes**, not displayed characters or graphemes. If normalization is desired later, make its semantics/cost explicit.

### Stage 2: fresh-result concatenation

For `u = s + t`, with byte lengths L and R:

1. Validate operands/lifetimes and evaluate each once.
2. Obtain lengths (scan for NUL under the current contract, or use stored lengths).
3. Check addition and allocation-size overflow for L+R, header, terminator and alignment before allocation.
4. Check the relevant budget and allocate a fresh result.
5. Copy L bytes from s and R bytes from t; write the terminator when required; publish u only after success.

Inputs must remain unchanged; `s + s` must work without overlapping-copy corruption. OOM/budget refusal must leave the inputs and destination binding intact.

Let T=L+R. **Estimated work for a naive implementation:**

- NUL representation: about T+2 preliminary byte reads to find both lengths, followed by T source-byte reads and T+1 destination-byte writes to form the result.
- Stored lengths: skip those preliminary scans; comparison/overflow checks add a small fixed cost.
- Roughly **10–30 fixed userspace instructions** for checks/setup around the loops, excluding operand evaluation, allocator, lifetime checks and error paths; a simple byte-copy loop costs roughly **5–7 instructions per byte**. The existing strlen-style loop is about five per non-NUL byte. These are planning estimates, not emitted counts or benchmarks.
- **One result allocation**, at least T+1 payload bytes for NUL text, or 8+T+1 for the proposed length prefix, plus allocator metadata/alignment. Retained input storage remains live. Any allocator zeroing is additional work.

`rep movsb` or word/vector loops may improve copying; one architectural instruction does not mean constant runtime. No elapsed-time or source-line commitment is justified before implementation.

The existing `vartani_cat(dst,src)` is **not this operation**. It mutates dst, has no capacity argument/check, and does not allocate a new result. Using a literal or an exactly sized input as dst can overwrite unrelated storage; self/overlapping append is not a safe general case. Its presence proves byte copying is possible, not that safe `+` is already implemented. A refusal hint should not steer beginners to it without explicit writable-capacity/nonoverlap requirements.

A checked caller-buffer alternative can avoid implicit allocation, but needs an actual capacity parameter and bounded inputs. It is a distinct API, not a silent reinterpretation of the current two-argument builtin.

### Allocation ownership is part of the price

Repeated `s = s + piece` copies growing prefixes: total work is quadratic for a long append sequence. With the current retention-based allocation paths, old results can also accumulate. A builder with checked geometric capacity can be a later optimization/API; no GC is required to make the first implementation correct.

Specify whether a concatenated result belongs to a block or a persistent owner, and reject escaping block-owned text or transfer ownership through an explicit safe mechanism. The v285 budget covers its declared allocation paths; hidden concatenation allocations do not become budgeted simply by appearing inside `mandapa parimita`. The compiler/helper must charge the selected owner, including headers/alignment and transient storage.

The cost advantage is clearest for equality: **no allocation and no new representation are intrinsically required**. Fresh concatenation is a larger change because it creates owned storage.

## Concrete acceptance cases for Claude

All below are **proposed, NOT RUN — no toolchain**:

| Area | Required observation |
|---|---|
| Printing | Numeric-first and text-first three-value calls follow the chosen policy consistently; raw writes preserve bytes written, partial-write/error behavior and migrated library use. |
| Content equality | Literal/literal, separate equal buffers, aliases, unequal prefixes, empty text, variable/literal, variable/variable, condition/value contexts and nested calls give consistent booleans. Existing builtin 0-equal convention remains. |
| Patch bypasses | `s=s+s`, `s=s+"cd"`, call-returned strings, branch joins, loops and globals cannot fall back to address arithmetic/comparison unnoticed. |
| Optimizer invariance | The paired offset probes above behave consistently; adding locals to cause spills cannot change type legality. |
| Concatenation | Empty sides, self-concatenation, chained expressions, unchanged inputs, large/multibyte text, insufficient budget, overflow and allocation failure. No mutation is published on failure. |
| Representation boundaries | Nonterminated slices use explicit lengths; embedded-NUL policy is enforced; raw pointers/numbers cannot acquire a text header by assumption. |
| Initialization | Bare local vitti/dasham fail compilation with no usable output executable; initialized locals, loop reentry, documented globals, arrays and empty koshes retain their distinct semantics. |
| Recursion | Exact answers at 500 levels and other supported depths; named refusal for exhaustion; test smaller stack limits and large environments, and disclose PE/object exclusions. |

## Late cross-review: Muse R100

Before delivery, main advanced to `f9f876cb5296c1017c45b5b0af2843c733f9a417`, adding only Muse's R100 report and census JSON. The audited compiler and patch are unchanged.

Muse reports new patched-v285 runs of examples 31 and 256, four refusal cases, an allowed `s + 1`, and an untracked-parameter residual. These are attributed subset results, not runs performed here or a replacement for the full regression gate. An accepted offset expression does not resolve P173-02's disagreement between generic and register-optimized paths.

I checked `fold_const` and `examples/31_strcat.sm`: string/string literals and string/integer constants fold into text, with signed decimal conversion for the integer. Thus “string plus integer is pointer arithmetic” is incomplete; constant folding already gives some forms different semantics. This audit does not propose removing that existing behavior as part of FIXALL. For the eventual typed operator, preserve decimal formatting consistently for text-plus-integer and integer-plus-text, including variables, while making raw offsets explicit through raw/slice APIs. That requires a deliberate migration of existing pointer-offset idioms and additional formatting/allocation cost beyond the text-plus-text estimates above. Check the chosen type rule before folding so optimization cannot determine meaning. Float formatting needs its own specified policy.

Muse's ownership/type constraints on fresh concatenation agree with this report: a bare NUL pointer is sufficient to implement copying, but it does not supply those contracts. Existing builtin comparison conventions should remain intact; adapt the result at the operator boundary.

## Delivery and verification

Read current source and reference, the complete patch, affected call-site migrations, Muse's report/evidence, and R173/R104/R100 assignments. Verified all 50 hunk preimages in memory on the pinned tree; inspected the resulting source text without building or installing it.

**Native build, operator/bypass probes, recursion probes, suite, proofs, guard and performance: NOT RUN — no toolchain.** `command -v nasm` returned no executable. Native Windows and CI: NOT RUN. No source changes or patch application to the repository were made.

Recommended integration order: retain the raw-write separation and compile-time initialization policy; repair the classification/order/fast-path defects and stack-bound contract before declaring the full patch accepted. Then implement typed content equality using the existing kernel; implement fresh concatenation only with explicit allocation/ownership rules. A temporary refusal can ship as a clearly scoped safeguard, not as the final teaching-language design.

Carry forward R172's correction: the aliasing guarantee is still about **proposed capacity**, not all lengths below 8,388,603; from capacity one the identified relocation begins at push 4,194,305. Also distinguish retained kosh storage from its logical block lifetime: the existing R82 check still rejects certain post-block uses.

Primary evidence:
- `Muse-to-Sarvam/FIXALL-R100-TRAPS.md`, `fixall_r100.patch`, `fixall_evidence.json`
- `src/sutram_compiler.asm` at blob `837db0b34ac156cb2c7cca3849e27dd4ef67c41f`: `.gs_assign`, fast integer emission, `.ge_call_vartcmp`, `.ge_call_vartcat`, `.ge_call_vartlen`, literal emission
- `lib/khand.smlib`: explicit-length comparison and slice contracts; `lib/varna.smlib`: separate representations
- `docs/LANGUAGE-REFERENCE.md`: printing/raw-write/text contracts
- `Sarvam-to-ChatGPT/ROUND-173.md`, `Sarvam-to-Claude/ROUND-104.md`, `Sarvam-to-Muse/ROUND-100.md`

