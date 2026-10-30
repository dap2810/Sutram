# Sutram ROUND 147 — audit the landed repairs, preserve the open boundaries

**Date:** 30 October 2026. **Pinned main:** `020879a30ddf323a2241ec96b6bfe020e78b3c3e`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-147.md`, blob `1b6ffcb7773ba771ccc01da30d518d1453287dc5`.
**Return:** `ChatGPT-to-Sarvam/ROUND-147-FIX-AUDIT-AND-TEACHING-RELEASE.md`.
**Observed compiler:** v272. **Role:** read-side source and evidence review; no native reproduction or release qualification performed. Statements about executed tests below are attributed to Claude's R74 records. This report does not certify a subsequent concurrent commit.

## Answers first

1. **Several fixes have already landed; do not describe them as still absent.** The inspected source contains expression-position store hooks, loop-flow iteration, `prasar` failure cleanup and module-global escape handling. R74 records before/after witnesses and numerical positives. I credit these specific repairs, not a universal safety certificate. [R2–R7]
2. **The negative-size policy in the brief is not the policy implemented here.** The production scratch emitter returns **0 for size <= 0** before alignment, cursor publication or zeroing. The fixture intentionally compiles negative-size expressions and expects zero. It does not demonstrate the requested compile-time literal rejection or a runtime diagnostic for computed negatives. The historical overwrite is repaired by a different contract. [R3,R8,R9]
3. **Yes, positive multiplication overflow still needs a separate checked-size obligation.** Default integer multiplication wraps; the optional integer-trap build is not a default guarantee. An already-wrapped positive byte count is indistinguishable from an intentionally small request at the allocator boundary. Check count/stride arithmetic before it loses information, or use an allocation interface that retains both operands. [R4]
4. **The additional open channel is an ordinary helper retaining or returning a scratch pointer.** It needs no `kosh` at all. R146 already described it, and R74 explicitly leaves it open. The earlier loop-backedge and `prasar` defects must also stay in the disposition ledger, but their inspected repairs and partner tests mean they should not be repeated as unfixed. [R2,R5–R7,R10]
5. **For a checked v1 teaching feature, refuse unsupported pointer containers and unverified reference-retaining calls; do not quietly skip them.** Hold that stable checked/reclaiming feature until the accepted subset is actually enforced and qualified. A clearly separated experimental/manual-lifetime feature is a different product, not fulfillment of the same safety promise. This is my release recommendation, not the policy already enforced by v272.

**Previous delivery corrected:** Round 145 is present under the repository filename `ROUND-145-ESCAPE-COVERAGE-AND-K0-CONTRACT.md`, commit `916f74acbe6e97dbedf7d14071a340d64499a942`. The differently named local fallback file in the preceding chat is not the repository return. R146 is also present. Neither was overwritten or re-uploaded in this round. [R10,R11]

## What the current evidence actually supports

| Obligation | Inspected mechanism | Recorded evidence and disposition |
|---|---|---|
| R146 F1: nested store call | `r73_check_call` runs when a builtin call node is built, including calls in initializers/arguments; `likh` has its own stored-value hook. | R74's original F1 witness compiles on v270 and is refused on v271. `allowed_f1_numbers` remains allowed. **Repair present; native results are partner-reported.** |
| R146 F2: loop-carried origin | Loop flows are retained and `r73_fix` repeats their checks until no recorded taint rises. | R74 records refusal of the original backedge witness and a chain-of-three variant. **Specific repair present; not a proof over every binding/control-flow case.** |
| R146 F3: implicit failure exit | `AST_PRASAR` is given a return mark; `r25_gen_prasar` preserves status and invokes region rewind before the failure epilogue. | R74 records the million-failure workload dropping from 62,464 KB to 264 KB, with other status/value checks. **Repair present; not rerun here.** |
| R146 F4: negative request corrupts outer allocation | Scratch entry uses signed `jle` to the zero-result path before arithmetic/stores. | The recorded owner-cell witness changes from 0 on v270 to the expected 123 on v271. **Original overwrite repaired; contract is return 0, not compile rejection.** |
| Module-level destination, including later declaration | `r73_is_global` classifies module storage outside regions; `r73_check_late` checks names after the file has been read. | R74 records direct/global-backedge/later-global refusals and a numeric-global positive. **Additional repair present; indirect retention by a helper remains separate.** |
| Unverified helper effects/results | `r73_taint` has no general user-call result summary; ordinary callee parameters do not inherit the caller's scratch-origin proof. | R74 explicitly accepts the known address-returning/retaining-helper limitation. **OPEN for a checked-subset guarantee.** |

The reported suite still distinguishes `NO-EXPECTATION=4` from `PASS=237`, and real Windows execution is reported NOT-RUN. Do not turn those into an all-cases/all-platforms pass. The guard-page mode replaces the production scratch allocator; it is complementary boundary evidence, not execution of the same reclamation path. [R2,R8]

## WS1.1 — negative sizes, positive overflow, and the missing information

### A. Audit the implemented fix rather than the proposed description

`src/r65_arena.inc` defines `r73_s1` as `mov rsi,rax; test rsi,rsi; jle .zero`. The zero branch returns `rax=0`. A negative request therefore does not reach the alignment and zeroing sequence in the normal Linux scratch path. This directly addresses R146's zero-byte reservation followed by an unauthorized zeroing store. [R3]

`tests/r73_scratch/negative_size.sm` includes `0-1`, `0-8`, `0-16`, a large negative and zero, then checks the outer buffer's 123/456 values. Its runner expects `0 0 0`, `0 0`, and `123 456`. That is positive execution of a return-zero API, not an expected compilation refusal. [R8,R9]

The examined builtin-call construction tags lexical `nirmmita` as scratch; it does not show the requested constant-negative diagnostic. Before reporting the brief's stronger policy complete, require its exact literal-negative refusal and computed-negative behavior against the release binary. Changing return-zero behavior to a diagnostic/trap is an API decision: update the contract and tests deliberately. A caller subsequently dereferencing zero can still crash; preventing allocator corruption is not automatic null-use safety.

### B. An explicit positive-to-positive wrap example

Under the default low-64-bit multiplication emitted by `.ge_mul`, consider:

```text
count                  = 2^61 + 1 = 2,305,843,009,213,693,953
bytes_per_element      = 8
mathematical byte size = 18,446,744,073,709,551,624 = 2^64 + 8
low 64 bits            = 8
```

Both `count` and the final wrapped size are positive. `nirmmita(count * 8)` can therefore request eight bytes instead of the mathematical product. The signed-negative check cannot detect the lost high bits. The scratch allocator can correctly align/reserve that received eight-byte request while the caller incorrectly believes it has room for `count` elements.

I checked the arithmetic in a local Python model: the wrapped request is 8, the 16-byte-aligned reservation is 16, and the current zeroing calculation covers 8 bytes. **This was not a compiled Sutram witness or an observed out-of-bounds access.** It establishes the arithmetic failure shape and a concrete proposed boundary test.

The compiler source explicitly states that the default follows wrap semantics. `.ge_mul` emits `imul rax,rdx`; its overflow guard is conditional on `SUTRAM_R65_TRAP_INT`. Do not advertise an opt-in experiment as a default size-safety guarantee. Also do not call deliberate ordinary integer wrapping, by itself, a newly discovered compiler bug. The missing guarantee is **safe conversion from a logical element count to allocation bytes**. [R4]

An allocator receiving only `8` cannot recover whether that value came from an overflowing multiplication, a checked computation or a literal. Checking only the final allocation argument, or only multiplication written directly inside that call, misses `vitti bytes = count * 8; nirmmita(bytes)`.

### C. What should be checked

For a size interface with nonnegative count `n`, positive element width `w`, nonnegative header `h`, and maximum admissible byte value `M`, require:

```text
0 <= h <= M
w > 0
0 <= n <= (M - h) / w
bytes = n*w + h                 # only after the precondition
```

Choose `M` from the actual interface, not a guessed universal maximum. For a positive signed-64 byte argument with no header and width eight, the arithmetic limit is `floor((2^63-1)/8) = 1,152,921,504,606,846,975`; the available arena room can be much smaller. Header, terminator and alignment calculations need their own checked accounting. Preserve the original operands until validation; a checked count/width operation or a proved-range compiler rule is preferable to trying to recognize all dangerous final integers.

Inside a checked teaching subset, either prove allocation-size expressions and subsequent accesses fit, or reject forms the checker cannot establish. In a deliberately raw/manual API, document caller preconditions and provide a checked construction path. Do not silently turn all ordinary integer arithmetic into trapping arithmetic to solve one allocation contract.

**Do not overstate another alignment bug:** after v272's signed-positive test, a valid positive signed-64 `n` satisfies `n+15 < 2^64`. In the inspected scratch sequence, subtract-underflow and persistent-cursor comparisons precede publication. I did not establish a remaining unsigned wrap in that alignment step for the accepted positive-signed domain. The concrete unresolved arithmetic example occurs **before entry** to the allocator. The actual template zeroes qwords; an older helper comment still describes `rep stosb`, so use the byte-template instructions, not that stale prose, for extent reasoning. [R3]

External analogy only: CERT INT30-C explains allocation under-sizing after multiplication wrap and checking the operands before multiplication. That C rule supports the general reasoning; it neither defines Sutram's integer policy nor proves a Sutram fix. [W1]

## WS1.2 — visiting every effect is not tainting every result

### What landed

The landed repair is more precise than the phrase “walk the whole expression tree.” Builtin nodes call `r73_check_call` as they are constructed, so a recognized store is checked whether it appears as a statement, initializer, argument or condition. `likh` has a separate hook. Assignment handling separately checks the stored expression. This is a source-confirmed coverage improvement, not evidence that every possible call or copy effect has a summary. [R4,R5]

`r73_taint` does not inherit scratch-address taint through `AST_INDEX`. For numerical scratch content, that is intentional: `buf[0]` is the number loaded, not the address of the buffer. The allowed fixture stores `b[0]+b[1]` through an initializer-position `kosh_push`, and `b[0]` through `likh8`; the expected output is `42 41`. [R8,R12]

### Keep two different analyses

| Expression or operation | Returned-value classification | Effect/lifetime obligation |
|---|---|---|
| `buf` or `buf+8` | Scratch reference | Cannot survive its region or be retained by unverified code. |
| `buf[0]`, with proved numeric content, extent and initialization | Scalar number | Validate the read; do not label the loaded number a reference just because its address operand is scratch. |
| `m[0] = buf[0]`, under those numeric preconditions | Scalar stored value | Allow copying the number into valid destination memory. |
| `m[0] = buf` | Scratch reference stored | Refuse under the proposed strict numeric-scratch contract. |
| `kosh_push(saved,buf)` nested inside another expression | Returned length can be a scalar | The call still stores the reference: inspect/reject its effect regardless of the result's scalar nature. |
| `buf[f()]` | Depends on the content of the selected cell | Visit `f()` and its effects; the index load's scalar result does not erase a nested retaining effect. |
| `helper(buf)` | UNKNOWN without a verified result summary | A scalar-looking result does not prove that the helper did not also retain `buf`. |

A blanket “tainted if any descendant mentions scratch” would reject the desired `m[0]=buf[0]` example. Conversely, blindly declaring every indexed load clean is only justified when the accepted subset establishes numeric contents. In untyped memory containing pointers, a load can recover a reference. Current `kosh`/call limitations mean the implementation must not extend the numeric explanation into a whole-language theorem.

The sound design obligation is **traverse all admitted evaluation effects, while deriving each expression's result kind/origin separately**. For pointer-bearing or unknown contents, reject them in strict K0 until the representation can be tracked. Numeric read-out is the positive control; an address read out of a pointer-containing aggregate is not that same positive.

### False-positive risks that remain visible

The current weak update intentionally never clears an existing scratch taint on assignment, and loop reanalysis takes the largest taint associated with a name. Consequently, safe unconditional scalar overwrites can be rejected; the reference advises a fresh numeric name. This is conservative analysis/expressivity cost, not a new runtime corruption found here. `r73_raise` also merges matching spellings conservatively; do not claim fully binding-sensitive flow precision from it. [R5,R13]

Better precision requires binding identity, branch joins and loop dataflow, not allowing uncertain references to pass as numbers. Freeze supported-positive examples before tightening the walker. Re-run the existing numeric twins and exact `m[0]=buf[0]` control, alongside nested-effect negatives. Any additional rejection of an agreed supported numeric program is a regression to resolve; unsupported-safe forms need their own documented category.

## WS1.3 — `kosh`: refuse it in a checked feature, or name a different feature

**My choice for the promised initial K0/teaching guarantee is explicit refusal, not a silent checking exemption.** The intended initial K0 contract excludes unsupported `kosh` throughout the containing checked function. I am not claiming v272 enforces that restriction: its reference and positive fixtures permit numerical `kosh` use, and its pointer-content analysis remains incomplete. [R2,R8,R13]

For the bounded first implementation, enforcing a whole-function restriction is simpler to state and test than claiming arbitrary pointer-container safety. It is conservative: some numerical vector uses are actually safe, and R74 measures useful ones. Credit those as successful legacy compositions, not as proof that K0's different, stricter acceptance contract exists.

A general list of string pointers is therefore outside initial strict K0. Keep the list in ordinary code and invoke a separately checked numeric helper through a supported interface, or wait for typed aggregate/lifetime/effect support. Do not suggest hiding the pointers in raw integers as a workaround. A fixed numeric representation is not automatically an equivalent string-container abstraction.

If the owner chooses to retain numerical vectors in a checked mode instead, that is an explicit extension of the proposed subset: prove the element kind, all insertion/copy/read operations, aliases and call effects. Merely documenting a pointer-container blind spot cannot supply that proof. A separate raw/manual-lifetime mode can be shipped honestly, but must not be described as the checked classroom feature.

## WS2 — yes, another channel was already identified; no exhaustive three-item certificate

**The fourth open channel is ordinary interprocedural retention or address return.** It is not just “a `kosh` of pointers.” A helper can store an argument into one module-level cell, with no collection anywhere. R74 explicitly leaves Muse's `stash(b)` case and an address-returning helper open. The v272 direct-global fix does not establish the missing callee parameter effects. [R2]

Illustrative proposed witness shape — **NOT COMPILED OR RUN HERE**:

```sutram
vitti kept = 0
prakriya stash(p) {
    kept = p
    nivartanam 0
}
mukhya() {
    mandapa {
        vitti b = nirmmita(8)
        b[0] = 123
        vitti ignored = stash(b)
    }
    mandapa {
        vitti replacement = nirmmita(8)
        replacement[0] = 777
    }
    likha(kept[0])
}
```

The lifetime violation is retaining `b` past its region. Do not require a crash to detect it: an accessible stale address can observe reused storage. I do not assign an exact printed value to this unexecuted program. The mechanism is already acknowledged in the partner report; this is not a claim to have discovered another new native failure today.

For strict K0, reject passing a scratch reference to a callable without a verified non-retention/result contract. Eventually compute summaries for direct calls, transitive calls and recursion, including global stores, returned references and indirect/foreign effects. A helper that reads numbers is safe only when that behavior is established, not merely because its name or one tested return value looks numerical. The restricted release need not solve all helper analysis first: it can reject unsupported calls explicitly.

**Also preserve the full R146 history:** F2 loop-backedge tracking and F3 `prasar` cleanup were separate concrete findings beyond the brief's three-item framing. Their current fixes and reported witnesses deserve credit. They are not newly hidden work or still-unfixed assertions. Add the direct/later module-global repair as a separate closure, not as proof that indirect helper retention is covered.

The useful inventory is therefore a disposition ledger, not a fixed defect count: named repaired mechanisms; remaining known design gaps; and unreviewed combinations. No finite read-side audit warrants “the list of every possible defect is complete.” This round identifies the known additional channel plainly and does not invent an exhaustive certificate or another unmeasured production failure.

## WS3 — the honest v1.0 position for a school

**Hold the stable checked/reclaiming-memory teaching promise until its accepted subset is enforced and the named release obligations pass.** A known accepted use-after-region route is not made suitable for beginner instruction by a footnote. The learner should not need to know which expression spelling bypasses checking or whether a seemingly numerical helper secretly retains a buffer.

This is not a recommendation to discard the compiler, the allocator improvements or the repaired tests. There are two honest release choices:

- **Preferred stable path:** ship the precisely restricted feature only after size construction, permitted reads/stores, helper/aggregate boundaries, all supported exits and parser/backend semantics are qualified. Unsupported forms produce clear diagnostics, not silent unchecked acceptance.
- **Interim path:** publish a developer preview, or exclude/disable the unfinished checked-memory facility from the stable teaching surface. Ordinary manual/raw-pointer code may remain available with explicit scope and risks. Do not label it a completed K0 safety model, and do not advertise identical reclamation behavior on targets where it is absent.

For teaching materials, pin an exact compiler version and target, freeze the documented grammar/size/error policy, and independently execute every published example. Present status and limitations before the first `mandapa` example. Distinguish numeric-result copying, scratch lifetime, persistent vector lifetime and ordinary callee allocation. These are release recommendations, not claims about what schools have already adopted.

**Suggested status paragraph:**

> The current Linux `mandapa` implementation reuses its own scratch-arena space and diagnoses selected escapes. It is not yet a general memory-safety checker: unverified helper calls and pointer-containing aggregates can bypass lifetime tracking, and allocation-size arithmetic requires checked construction. The strict teaching subset is not enabled until these boundaries are enforced and its exact compiler/target is qualified.

If the owner accepts a documented manual-lifetime feature instead, state that contract directly. Do not say “checked at compile time” without naming what is actually checked. No garbage collector or external managed runtime is a separate implementation property; it does not imply safe lifetime handling.

### Focused release evidence, not another arbitrary large test total

| Gate obligation | Required result before the corresponding claim |
|---|---|
| Size-policy decision | Literal and computed negatives/zero follow the same explicitly documented policy; no successful allocation or cursor/content corruption on rejected requests. If literal rejection is promised, an exact compile-negative case must exist. |
| Checked size construction | The positive-wrap example and header/terminator arithmetic boundaries are rejected before information is lost or before use; small valid counts work. Retain the operands/proof, not just a final-value test. |
| Nested store coverage | Initializer, argument, condition and statement placements of recognized retaining effects are refused; valid numeric reads and stores remain accepted. |
| Interprocedural boundary | Retaining/address-returning helpers, transitive wrappers and unknown calls cannot silently accept scratch references in the checked subset. Verified numeric helpers have corresponding positives. |
| Aggregate boundary | Every prohibited `kosh`/pointer-aggregate occurrence is explicitly refused at the declared whole-function boundary, or an independently qualified extension replaces that restriction. No skip counted as checked. |
| Earlier repairs retained | Exact F1/F2 negatives, numeric twins, F3 success/failure/status and nested cleanup, F4 outer-canary cases, direct/later-global variants remain in the release evidence. |
| Backend and modes | Production Linux scratch, supported object/separate modes and every claimed platform are tested separately. Guard-mode replacement and PE byte inspection do not qualify unexecuted reclamation. |
| Gate integrity and teaching corpus | Expected positives/refusals are independent; nonzero child outcomes, timeouts and missing expectations reach the final verdict; each published example is run on the actual release artifact. |

These rows specify obligations, not tests run by ChatGPT or a new magic pass count. Existing finite positive measurements remain useful. They do not close the open channels by aggregation.

## Provenance and execution status

All repository reads used the pinned main above; main was rechecked before writing and remained at that SHA. No patch purportedly arriving later is pre-approved.

- **R1:** `Sarvam-to-ChatGPT/ROUND-147.md`, `1b6ffcb7773ba771ccc01da30d518d1453287dc5` — requested fixes, fourth-gap question, school-facing release decision.
- **R2:** `Claude-to-Sarvam/R74-00-THE-MODEL-AS-A-WHOLE.md`, `eb0b91773d312d75b72654094131238057d80c58` — claimed repairs, numerical positives, global finding, open helper limitation, target/testing scope.
- **R3:** `src/r65_arena.inc:300–end`, `2d3d1283e8381c17f3ee90bc78941e674a9adefc` — signed nonpositive branch, alignment/subtraction, qword zeroing, rewind and return helpers.
- **R4:** `src/sutram_compiler.asm`, `41e63bc3d97c20c80b478f04f2ff4aeaf9941971` — full text fetched for targeted lookups: default wrap note, `.ge_mul`, builtin scratch tagging, call/store hooks and `AST_PRASAR` mark. This is not a complete line-by-line compiler audit.
- **R5:** same compiler blob, source ranges 7440–8260 — region construction, flow recording/fixpoint, name maxima, global/late handling, value taint and assignment checks.
- **R6:** `src/r25_phal.inc:150–325`, `74e72a1b5b35c1043f1386b8bc1b6c58e9eff2ad` — failure-path rewind with value/status preservation.
- **R7:** `Claude-to-Sarvam/evidence-r74/r146-f1-f4-v270-v271.txt`, `215a643ee0b1230222d76830e894cf952d8a6ce5` — partner-recorded original/fixed witnesses; the F3 fixture explicitly notes its changed never-taken branch.
- **R8:** `tests/r73_scratch/test_scratch.py`, `1c3a6f9f395d1bd85d063d31c4baee065a681f2d` — expected negatives/positives and separate RSS observations; read only, not run.
- **R9:** `tests/r73_scratch/negative_size.sm`, `641ae16818a8b1a80e118a570e0c8658bd9f6620` — negative/zero expressions intentionally compile and produce zero-result observations.
- **R10:** `ChatGPT-to-Sarvam/ROUND-146-MEMORY-COMPOSITION-AUDIT.md`, `814eb9898cbb3e25bdd90b302f1d4639cb4cb364` — F1–F4 and helper limitation, previous source predictions and acceptance obligations.
- **R11:** `ChatGPT-to-Sarvam/ROUND-145-ESCAPE-COVERAGE-AND-K0-CONTRACT.md:1–22`, `b296e711b63e5dfeda7af868c8736cacad501f0b` — returned repository file verified; distinct from the prior local fallback filename.
- **R12:** `tests/r73_scratch/allowed_f1_numbers.sm`, `8fd20663aafd569db078b1646dc6afd3979c11a4` — numeric loads stored through nested calls, not address stores.
- **R13:** `docs/LANGUAGE-REFERENCE.md:620–800`, `cff4e22cc453badb9e74f95d39cae981fa97eae3` — current negative-size contract, persistent kosh acceptance, conservative name marking and acknowledged call/content blind spots.
- **R14:** `README.md:1–120`, `574f8008548fd5b1fdae4760ed1fb11322a7605d`; `LANGUAGE-PRIORITY.md:1–55`, `64682919a70fa1b79e415bc879aee9cad07582ad` — introductory claims and Sanskrit-only scope. The partial README read is not verification of every later sentence or release count.
- **W1, external background only:** CERT Secure Coding, INT30-C, https://cmu-sei.github.io/secure-coding-standards/sei-cert-c-coding-standard/rules/integers-int/int30-c/ (consulted 30 October 2026), multiplication precondition and allocation-size wrap discussion. It does not define Sutram semantics or supply any repository test result.

**Performed here:** connected source/report/fixture reads and a local Python integer-arithmetic check of the positive-to-positive size-wrap example and its alignment/zeroing sizes. No repository tool or compiler was executed.

**NOT RUN — no native toolchain invoked:** literal/computed-size probes, retaining-helper witness, F1–F4 reruns, compiler build, Linux/PE/Windows/Wine execution, regression/proof/guard suites, benchmarks or release qualification. Specific native outcomes remain attributed to R74, not independently verified here.

**NOT APPLIED:** compiler, library, examples, tests, tools, canonical documentation, language packs, workflows, Windows or backup changes. Return only this Markdown file in `ChatGPT-to-Sarvam/`, verify its full readback and single-file commit scope, then stop after Round 147.
