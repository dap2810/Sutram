# Sutram ROUND 137 — vocabulary roles, diagnostic cases, and the K0 implementation contract

**Date:** 29 October 2026. **Pinned source:** `2bc54c3a937db5b113b15a08475f336da07ce13a`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-137.md`, blob `9c8533335f467e0123943f810e91454892301ab9`, including its amendment.
**Return:** `ChatGPT-to-Sarvam/ROUND-137-VOCABULARY-K0-FREEZE.md`.
**Read-side scope:** documentation only. No compiler, library, test, pack, workflow, Windows or backup changes.

## Status and decisions

The amendment governs: **`mandapa` / मण्डप is the proposed block keyword; `kshetra` / क्षेत्र names the arena in diagnostics/docs only; `avayava` / अवयव names a structure member.** Older reports calling the source construct `kshetra` are superseded on that spelling, not on their lifetime requirements. `docs/vocabulary/VOCABULARY-RULE.md` was read; its three vocabulary tests and separation of programmer-facing syntax from explanatory terminology are retained. No additional memory keywords or programmer-selectable size-tier syntax are proposed here. [R1, R2]

**WS1 is a scoped verification, not a completed repository-wide census.** Primary dictionary pages were checked; compiler text, the complete Sanskrit keyword pack, selected message packs and the generated library reference were inspected. The broad assertion that every `lib/`, `examples/`, `tests/` file and every message pack has been independently scanned is **NOT** made. Sarvam's totals of 44 pack entries and eight expected-output files remain **partner-reported, not independently reproduced in full**. A zero-result GitHub search returned `incomplete_results:true`, including for a term known to exist, so it cannot establish absence. This limitation is a remaining verification gate, not a reason to invent a new name.

**WS2:** recommended case-correct Devanagari renderings for all four field-related fragments are supplied below, as future wording changes.

**WS3:** freeze the restricted K0 contract below as this handoff's implementation target. The three requested fields separate three different facts, but **three untyped depth integers alone are not a sound checker**. Value kind, owner identity, extent/offset, null facts and verified call effects remain mandatory.

**WS4:** specify semantic compatibility separately from byte identity. Step-3/4 no-block identity is measured against the same Steps-0–2 allocator baseline, not automatically against v261. No guard was run here.

## WS1 — three words, three distinct roles

### 1. Dictionary verdicts

| Word | Attested sense | Fit for the owner-selected use | Qualification |
|---|---|---|---|
| `mandapa` — मण्डप, scholarly `maṇḍapa` | MW page 775 records a hall, pavilion, and a temporary shed among its senses. | A defensible metaphor for the explicitly delimited scratch block. **Keep the chosen name.** | The dictionary does not imply automatic teardown, a lifetime proof, a particular capacity, or that every pavilion is temporary. Those are language rules. The keyword uses the stem, not an inflected sentence form. |
| `avayava` — अवयव | MW 1872 page 92 records a member, part or component. Masculine noun. | Precise for a member of a `rachana`, including the member-lookup terminology used for methods. **Keep.** | This is a modern technical application of an attested noun, not an ancient dictionary definition of a struct layout. |
| `kshetra` — क्षेत्र, scholarly `kṣetra` | Benfey page 240 records field, place and extent; neuter noun. | Suitable for the arena/space described in messages and documentation. **Keep in that role; do not add a second block keyword.** | Existing field-diagnostic use is a semantic overlap to migrate deliberately, not proof of an existing lexer keyword collision. |

Original page images were inspected for W1–W3. The interpretation as a memory construct is this review's design judgment; it is not attributed to the dictionaries.

### 2. Compiler and keyword-pack checks

The pinned compiler is blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`, unchanged from the relevant R136 source. A fresh pinned raw-text retrieval was searched for `mandapa`, `avayava`, `kshetra`, and the canonical native strings मण्डप, अवयव, क्षेत्र. The compiler header was included as a positive control. The returned source matches were the four known Roman field-diagnostic fragments, not candidate keyword definitions. Duplicated copies of content in a connector response are not separate source occurrences.

- **`mandapa`:** no literal Roman/native match found in that compiler text search.
- **`avayava`:** no literal Roman/native match found there.
- **`kshetra`:** four Roman substring occurrences: lines 313, 317, 328 (`kshetram`), and 827. No literal Devanagari क्षेत्र match found in that text search.
- **`lang/sanskrit.lang`:** the complete pinned file, blob `27eda2b6a9be2cca76e375cfec9d73b865c7b4e8`, contains no mapping for any of the three spellings or their canonical Devanagari forms.

A Unicode text search is not a decoder for NASM `db 0x...` byte strings. The previously inspected keyword/builtin definition inventory at the same compiler blob supplies a separate check of existing public spellings; no candidate keyword/builtin collision was identified. This is not a new native lexer test and does not certify every include or possible transliteration variant. [R3, R4, R8]

There is **no new third collision demonstrated for `avayava`** in these checked surfaces. Do not replace it on the strength of an imagined collision. Conversely, do not promote the scoped result into a claim of universal identifier uniqueness.

### 3. Message packs: what is verified and what remains open

The pinned `lang/` tree is `e711e1b8f4e5e2d1d6fe9512d933912a0eb02296`. Its complete listing contains 11 `.sandesh` packs: Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Sanskrit, Tamil and Telugu.

Direct reads in this round include Sanskrit, Bengali, Gujarati, Hindi and Kannada message files. Full-content candidate-search results were checked with identifiable content for the Sanskrit, Gujarati and Hindi examples; other partial/displayed reads are not upgraded to whole-file negative-search certificates. In those checked results, `kshetra` appears in Roman default-message comments corresponding to the same four keys:

```text
r5_msg_field
r7_msg_field_amb
r5_msg_field_hint2
msg_rachana_fields_overflow
```

The Sanskrit translations already contain क्षेत्रम् / क्षेत्रं / क्षेत्र in these messages. Gujarati and Hindi show their own translated field wording. No candidate `mandapa` or `avayava` match was identified in the fully searched examples. The whole eleven-pack absence result remains **NOT INDEPENDENTLY VERIFIED** here.

**Counting distinction:** a Roman `kshetra` match in a default-text COMMENT is not an additional keyword, builtin or alias. Four corresponding message records in each of eleven packs would give 44 records, but comments, translated payloads, matching lines and token occurrences are different counts. Report the counted unit and file list. Do not say '44 keyword collisions'.

The ten non-Sanskrit packs are frozen. Their inventory and existing strings can be read and reported, but this handoff does not authorize changing their translations or default comments. Keep pack key identifiers stable. A future Sanskrit/default-message migration must not silently regenerate every frozen pack. [R5]

### 4. Library names, examples and tests

The pinned generated `docs/sutram-stdlib.html` reference was retrieved and searched with its title as a positive control. No candidate Roman/native name was found in that reference. This is corroborating evidence about the published callable inventory, **not a fresh independent parse of every live library definition**. The signature checker was not run.

The known field-diagnostic expectations and `tests/r23/test_capabilities.py` were already documented in R136. Their relevance remains, but **the amendment's count of eight expected-output files was not fully enumerated in this round**. Likewise no independently complete zero-hit census of every example/test identifier is claimed. GitHub search returned incomplete results even for existing `kshetra` test text. [R6, R8]

**Required closure before calling WS1 fully verified:** run a pinned full-text/definition scan on a complete repository checkout and return the paths, matching lines, counts and checked commit. The following is a read-only starting command, **NOT RUN here**:

```sh
PIN=2bc54c3a937db5b113b15a08475f336da07ce13a
git grep -n -I -E 'mandapa|avayava|kshetra|मण्डप|अवयव|क्षेत्र' "$PIN" -- \
  src/sutram_compiler.asm lang lib examples tests
```

Classify its results into comments, message keys/payloads, keyword/builtin definitions, library declarations, program identifiers and expectations. Also inspect numeric UTF-8 `db` sequences in the actual keyword tables, distinguish exact identifiers from substrings/inflections, and list every `.sandesh` path searched. A grep result containing no candidate does not establish anything about files excluded from that command. This remaining census is explicitly open; no native test or safety claim depends on pretending it was completed.

### 5. Applying the standing vocabulary rule

- **Ambiguity removed:** `mandapa` denotes the lifetime-bearing block, `kshetra` the arena it allocates from, and `avayava` a structural member. Do not conflate these roles again.
- **Compound before new root:** use the established words in explanatory compounds rather than inventing another root for this round. A compositional name is not automatically a proof of grammatical or technical precision.
- **Compiler names versus user choices:** only `mandapa` is proposed source syntax. Arena/member terminology and documented tier names do not automatically become additional keywords or allocation policy choices.

No new allocator tier behavior, fallback policy, or punctuation feature is inferred from the vocabulary document. The parked danda proposal stays parked. [R2]

## WS2 — the four messages in their grammatical positions

`avayava` is masculine. Its nominative singular is **अवयवः**; accusative singular is **अवयवम्**; inside a compound its stem is **अवयव-**. The old neuter क्षेत्रम् cannot simply be copied as अवयवम् in every position. The following uses nominative labels, not an unexpressed accusative object. W2 establishes gender; W4–W5 support the declension/sandhi rules. These are proposed rendered text, not observed compiler output or a claimed Sanskritist certification of a shipped translation.

| Fragment | Recommended rendered Devanagari | Grammar |
|---|---|---|
| `r5_msg_field`, compiler line 313 | `: Sutram Error [E_UNKNOWN_FIELD]: अज्ञातोऽवयवः 'w'` | Nominative adjective and noun: `अज्ञातः + अवयवः`, joined by visarga sandhi. No governing transitive verb requires an accusative here. |
| `r7_msg_field_amb`, line 317 | `: Sutram Error [E_AMBIGUOUS_FIELD]: अवयवः 'x'` | Nominative member label, preserving the original fragment's structure; the error ID supplies 'ambiguous'. An added adjective is not necessary for this rename. |
| `r5_msg_field_hint2`, line 328 | `सूचना: 'w' कस्याश्चिदपि रचनाया अवयवो नास्ति।` | Underlying forms: `कस्याश्चित् अपि रचनायाः अवयवः नास्ति`. The genitive pronoun agrees with feminine रचना. `रचनायाः + अवयवः` gives `रचनाया अवयवः`; `अवयवः + नास्ति` gives `अवयवो नास्ति`. |
| `msg_rachana_fields_overflow`, line 827 | `Sutram Error: रचनावयवसीमातिक्रमः` | Compound label: `रचना + अवयव + सीमा + अतिक्रमः`; internal members use stems, and the compound's final noun is nominative. It names exceeding the structure-member limit. |

The quoted identifiers are opaque program names. Do not Sanskrit-inflect or sandhi-transform the bytes of `w`, `x`, or arbitrary user identifiers. The prefix/suffix templates must preserve their quotes, source locations, stable error IDs and newlines.

**This table is not a drop-in `.sandesh` patch.** The actual capacity message currently contains `{kw:rachana}`. Preserve required keyword placeholders rather than hardcoding a fused string in a way that defeats pack substitution. A segmented display such as `{kw:rachana}-अवयव-सीमातिक्रमः` can retain the existing template structure; the fully joined form above explains the Sanskrit compound. Validate actual fragment concatenation and the pack checker before choosing final template bytes. The full hint also spans a prefix, printed identifier and suffix; do not duplicate the identifier when applying it.

A wording migration intentionally changes diagnostic expectations. Keep it in a separately authorized change, including the fourth hint, not hidden inside the allocator/checker guard comparison. No wording or expected output is changed by this report.

## WS3 — freeze K0, with the three fields defined rather than guessed

### 1. Scope of the frozen target

This is K0 from R135–R136, now spelled with **`mandapa`** for the block. It checks the whole function opting into that construct and the exact bodies of admitted helpers. It remains deliberately narrow: scalar-only buffers, immutable reference bindings, constant sizes and statically bounded accesses, no pointer-bearing aggregates, and verified scalar-only direct calls. Unknown proof/effect information is a compile error at the unsupported use. No warning-only escape hatch belongs to the checked profile.

This is a specification, not an implemented checker or a machine-checked soundness proof. The guarantee concerns region references through admitted operations, assuming correct allocation, null/bounds checks and exit lowering. It is not a sandbox against arbitrary unchecked legacy assembly or memory corruption outside that boundary.

### 2. Exact meanings of the requested fields

| Field | Meaning | Must NOT mean |
|---|---|---|
| `var_depth` | Lexical declaration depth of a BINDING in the current function's scope tree. Pair with `binding_id` and `decl_scope_id`. For a direct local assignment, this locates the destination binding's usable lifetime. | The lifetime of every numeric value assigned to it; the owner of storage reached through its pointer value. |
| `val_taint` | Reference-origin dependency of a VALUE: `CLEAN`, a specific region identity R, or `UNKNOWN`. In K0 a region Reference carries R, an ordinary Scalar is CLEAN, and a persistent Reference has no scratch dependency but is still a Reference. | Merely the depth where a number was calculated; a substitute for value kind; zero meaning 'definitely not a pointer'. |
| `box_depth` | Lifetime depth of the OBJECT/storage reached by an admitted Reference. Copy it through aliases. Persistent storage has depth 0; a region object has its owner's depth. Scalar values have `NOT_APPLICABLE`, not depth 0. Pair with `box_owner_id`/`object_id`. | The declaration depth of the variable that happens to hold the object's address. |

Use explicit tags for CLEAN, UNKNOWN and NOT_APPLICABLE. A numeric depth is only a projection of a scope/owner identity. Check containment using the actual scope tree, not `depth(lhs) >= depth(rhs)` alone. No comparisons between unrelated functions' depth counters are meaningful.

**Mandatory additional metadata:**

```text
kind = Scalar | Reference | Literal | Unknown
binding_id, decl_scope_id
owner_id, object_id, byte_extent, constant_byte_offset
null_fact = MaybeNull | NonNull
verified_callee_summary (for each admitted call)
```

These may live in compiler tables rather than physically inside every value record. They are still required facts. A literal may be consumed only by specified intrinsic forms. A persistent Reference and a scalar both lacking scratch taint must remain distinguishable.

### 3. Why the scalar example is accepted

```sutram
# Proposed K0 source, NOT RUN.
vitti total = 0
mandapa {
    vitti x = 42
    total = total + x
}
```

Suppose `total.var_depth=1` and `x.var_depth=2`. Both values are Scalar, both have `val_taint=CLEAN`, and neither has a pointee `box_depth`. Scalar addition yields Scalar/CLEAN. Assigning that result to `total` is allowed. **The declaration lifetime of x is not inherited by the number 42.** The split fixes the false rejection only when these transfer rules are used; adding three fields while still setting taint to declaration depth does not fix it.

For `vitti q = p`, where p is a Reference, q gets its own declaration depth but copies p's value kind, owner/object, taint, pointee depth, extent and offset. Renaming q cannot change the lifetime result.

### 4. Construct-by-construct implementation rules

| Construct | Required handling of the three fields | Reject | Allow |
|---|---|---|---|
| **Direct assignment / declaration** | A Scalar RHS has CLEAN taint regardless of `var_depth`. For a fresh Reference binding, copy `val_taint` and `box_depth`; compare its owner's identity with destination `decl_scope_id` (whose rank is `var_depth`). | Reference into a longer-lived binding; reference rebinding; Scalar/Reference class-changing assignment; Unknown RHS. | Mutable scalar state and numeric values copied outward; fresh same-region/deeper immutable Reference aliases. |
| **Indexed store `q[i] = v`** | Look at q's pointee `box_depth`/owner/object, NOT `q.var_depth`. Verify q is live/non-null and the access is within its known extent. Require v to be Scalar/CLEAN. | Any Reference or Unknown stored in memory, even same-region memory; unknown destination; dynamic/unproved index or out-of-bounds write. | Constant-bounded scalar write to an admitted scalar-only object, including an outer object's valid scalar slot. |
| **Struct-member store `q.member = v`** | Do not manufacture a safe `box_depth` from q's name or field spelling. Current K0 has no verified member-layout/carrier rule. | The construct in a K0 function, until separately specified checked lowering exists; reject even a plausible scalar store rather than silently accepting an unchecked layout. | No struct-member store in K0. Existing legacy use remains available outside the opt-in checked boundary. |
| **`kosh_push` / append and equivalent collection retention** | Existing `kosh` representation/effects do not become safe because a variable's depth is known. Do not reset `val_taint` merely because append returns a length. | The operation in K0; in particular appending a region Reference to an older container. | None in initial K0. Under the owner's allocator policy, supported outer-kosh growth is persistent, but that routing does not grant K0 admission. |
| **`prakriya` call** | Require a verified exact-body/transitive value-only summary. Every argument must be Scalar/CLEAN; result kind/taint comes from that summary, never from a result variable's `var_depth`. No pointer argument means no admitted pointee `box_depth` crosses this interface. | Unknown or indirect/FFI target, missing/stale/cyclic summary, Reference argument/result, mutable global/raw-memory effects. Initial helper whitelist also refuses persistent-allocation effects. | Verified acyclic scalar helpers, including helpers with their own checked scratch and scalar results. Trusted intrinsics are checked by actual overload. |
| **`nivartanam`, including result payloads** | Require Scalar/CLEAN result; `box_depth` must be NOT_APPLICABLE. Evaluate the entire expression while owners are live, preserve result/status, then restore marks for the exited region identities and return. | Direct/derived/wrapped Reference or Unknown result, including persistent Reference returns under this minimal profile. | Scalar early returns, checked scalar loads returned outward, scalar success/failure. |

**Strictness is intentional:** the generic lifetime condition could permit storing a Reference in a shorter-lived object, but K0 does not implement pointer-containing memory. It therefore rejects ALL reference stores. Do not replace that rule with only `val_taint_depth <= box_depth` and still call the implementation K0.

### 5. Remaining mandatory transfer/control-flow rules

1. **Numeric expressions:** Scalar operands produce Scalar/CLEAN. Numeric input can never be converted into a Reference, even if its bits equal an address.
2. **Allocation:** direct `nirmmita(C)` has known positive constant extent, lexical owner and MaybeNull reference class. In a `mandapa` it is scratch; outside one it is persistent. Allocation routing is lexical, not dynamically inherited by ordinary callees.
3. **Reference arithmetic:** permit only proved constant in-object offsets, after the required non-null fact. Preserve kind, owner, object, `val_taint` and `box_depth`; update checked offset. Reject other arithmetic, bitwise disguises, float conversions and integer-to-reference reconstruction.
4. **Loads:** only a live, non-null, statically bounded scalar-only object can produce a Scalar/CLEAN load. Unknown raw qwords are not presumed harmless. General `pad8`/`likh8`, raw copies, slices and aggregate carriers are rejected unless specifically implemented as checked intrinsics; no generic API-name whitelist.
5. **Null facts and merges:** continuing access must be dominated by a valid null guard or specified fail-stop assertion. Intersect definite facts at joins. Re-executed initializers reset their facts. Reference-valued joins/rebinding and loop-carried mutable references are rejected in K0.
6. **Calls and effects:** verify complete bodies and admitted transitive callees before caching approval. An ordinary scalar return type is not a no-retention proof. Static literals, scalar printing, assertions and allocation have explicit intrinsic contracts; raw three-argument `likha` is not automatically allowed because another overload prints a scalar.
7. **All exit edges:** normal exit, break, continue, return and failure propagation restore exactly the exited region suffix. An inner-loop edge staying within a region does not restore it. Handled failure remaining in a region does not restore it. Marks are activation-local. Cleanup changes S only, not persistent P or freelists.
8. **Bounds and limits:** validate rounding/overflow and arena gap before mutation; failed allocation returns 0 without changing cursors. For a qword access prove `0 <= offset + 8*i` and `offset + 8*i + 8 <= extent` using checked compile-time arithmetic. Unknown/dynamic cases and exhausted analyzer tables are compilation errors, not skipped checking.

The return sequence remains **evaluate -> convert/form scalar status -> preserve -> restore S -> epilogue**. An allocating helper does not require rewinding before expression evaluation. `helper(buf)` is refused by K0's Reference-argument rule; a verified `helper(buf[0])` can be allowed after a valid scalar load. The separate `prasar` failure epilogue must receive cleanup and preserve RAX/RDX; its branch displacement must remain valid. R135–R136 already identified those insertion requirements. [R8]

### 6. Cases where three depth fields are still insufficient

**Persistent pointer versus scalar:** both can have no scratch taint and depth-zero storage association. Without `kind`, a persistent pointer result can be mistaken for a scalar, and a numeric value can be used as an address. The three fields do not distinguish those operations.

**Aliased outer storage:** an inner-declared `q` may point to outer storage. `q.var_depth` is inner, but its `box_depth`/owner remains outer. This is exactly why destination storage provenance must be retained. Even three integers are insufficient if an unknown load or call result is allowed to supply a fabricated depth.

**Bounds:** `p[1000]` and `p[0]` have the same three depths. For an eight-byte object, one is invalid. Without object extent/offset and null information, an unchecked store can overwrite other objects or allocator state and invalidate the lifetime argument.

**Sibling/repeated scopes:** distinct regions can have equal numerical depth. A stale owner or cached summary cannot be validated solely because a new region has the same depth. Track identities and reinitialize per-execution facts. K0 rejects reference merges rather than solving them incompletely.

**Opaque helper:** `helper()` may return an allocation or an arbitrary loaded qword despite having no arguments. None of the caller's three existing depth fields determines that result's class/effect. Unknown call result is rejection until exact-body verification supplies the facts.

These are reasons the metadata above is mandatory, not known holes permitted by the frozen rules. With scalar-only memory, immutable references, no forging, verified scalar-only calls and correct cleanup, the admitted continuation has no surviving checked reference to a reclaimed region. The argument depends on those restrictions; removing one requires a new analysis/proof, not a renamed field.

### 7. Cost and what the implementer may claim

Retain R135–R136's **960–1,800 added/changed NASM-line estimate** for Steps 3–4. This is an engineering estimate, not an implementation measurement, and excludes Steps 0–2, test fixtures, Windows allocator work and a broader borrowed-buffer profile.

Compiler-only work estimates after lookup remain approximately 8–25 simple instructions for classified assignment/alias handling, 6–20 for scalar-operator classification, 15–40 for constant-reference-offset checks, and summary lookup plus roughly 4–10 per call argument. Extent/null joins and first-time callee verification are additional static work. These are not machine-code benchmark results.

**Extra target provenance instructions:** zero for those compile-time checks in the admitted constant-only subset. Region mark save/restore is separate: two MOVs at entry and two per exited mark in the memory-cursor/frame-slot sketch, before spills; multiple shared-cursor-only restores may be collapsed to the outermost exited mark after proving equivalence. Allocation gap checks, zeroing, user-written null guards and ordinary calls retain their actual costs. No total-cycle claim follows from a zero runtime taint-map claim.

## WS4 — exactly what compatibility and the guard can promise

Define three compiler states with identical target/build flags:

```text
A = v261 before the new allocator
B = accepted Steps 0–2 allocator, diagnostic wording unchanged
C = B plus mandapa/K0 Steps 3–4, diagnostic wording still unchanged
D = separately authorized avayava diagnostic migration
```

### 1. C versus B: the required zero-difference gate

For an input/translation unit with no actual `mandapa` construct, and the same dependency/link inputs, **C must preserve B's acceptance, diagnostics, output and complete emitted bytes**. Recognize an AST construct, not the word occurring in a comment/string or as an existing identifier. A linked dependency that itself introduces region machinery is not the same no-region experiment.

No new mark slots, spills, cleanup, literal strings, helper stubs, runtime state, header/section growth or unconditional branch widening may appear in the no-region path. Keep emission order stable and feature data lazy. Static compiler tables do not themselves require extra bytes in the compiled program. Preserve valid identifiers named `mandapa` by a specified contextual parse or acknowledge a compatibility break; corpus absence is not proof that no user's program uses the name.

**This is the promised design invariant. Measured 0 DIFFER: NOT RUN.** A documentation-only commit changing no executable is not evidence that C passes this gate.

### 2. B versus A: semantic compatibility, not universal binary identity

Allocation sequences/layout may change intentionally, so allocator-using binaries generally need not have identical bytes. Compare agreed program behavior and the existing expected-output/diagnostic corpus, plus allocator/failure/alias invariants. Programs that make ordinary scalar computations over valid allocated objects must keep their results, with matched inputs and specified allocation-success conditions.

A universal 'all old programs print identical output' promise is too strong when raw addresses are observable. Address printing, timing, memory usage, allocation ordering and resource-exhaustion outcomes may change when the backend changes. Enumerate those differences explicitly; do not silently normalize them away or use them to excuse changed arithmetic results. A limited arena's success/failure policy requires an explicit contract.

**Alias invalidation is not automatically an acceptable allocator-dependent difference.** If an old program was valid under an accepted collection alias contract, silently reusing its still-live backing block is a regression or a separately approved semantic change, not an innocent address change. K0 does not certify Step 0's freelists or make legacy aliases unique.

Non-allocating old programs may retain identical bytes, but no A/B blanket guarantee is asserted without checking image-layout and unconditional initialization changes. The mandatory C/B gate is the clean way to isolate accidental Step-3/4 effects.

### 3. Region programs and diagnostic migration

New `mandapa` programs have no equivalent accepted A/B baseline. Check them against the new specification: successful scalar results, escape/unsupported-use diagnostics, null/bounds behavior, nested cleanup, failure paths and bounded scratch high-water. An old parser rejecting the keyword is not a successful safety test.

D intentionally changes the four member-message fragments and their specifically authorized expectations. Preserve error IDs, source locations, member semantics and frozen-language scope. Do not combine D with the C/B zero-diagnostic-difference gate or edit all goldens to hide a regression. Version the expected changes separately.

No 225/227/577 count from a brief is a test result produced by this round. Run the real guard at exact A/B/C commits with recorded flags and compare accepted and rejected programs; report bytes and semantic results as separate columns.

## Focused acceptance additions for R137

All cases below are **proposed, NOT RUN**.

| ID | Case | Required outcome |
|---|---|---|
| R137-01 | Complete pinned corpus scan, all eleven message packs and public definitions | Per-file receipt; distinguish comments/strings from exact identifiers; close the WS1 coverage gap. |
| R137-02 | Render all four avayava messages, including the hint and capacity template | Correct case/agreement, quotes/placeholders and IDs; intentional separate expected-output changes only. |
| R137-03 | Inner `vitti x = 42`; outer `total = total + x` | Accept Scalar/CLEAN flow. |
| R137-04 | Inner Reference plus constant assigned to outer slot | Reject escape; arithmetic does not erase owner. |
| R137-05 | Inner alias of persistent buffer used to store a Reference | Reject; destination is not inner-owned merely because alias is local. |
| R137-06 | Persistent Reference and Scalar both having zero scratch taint | Keep kinds distinct; do not permit integer dereference or pointer-as-scalar return. |
| R137-07 | Same-depth sibling/re-entered regions and repeated initializer | Identity/null facts are not reused incorrectly. |
| R137-08 | Unknown zero-argument helper versus verified scalar helper | Reject former; accept latter only after exact-body/transitive verification. |
| R137-09 | Scalar return expression using a helper's own scratch | Evaluate before rewind; preserve result/status; no blanket return prohibition. |
| R137-10 | Indexed scalar store versus struct store and kosh append | Accept only the proved scalar-buffer form; other unsupported constructs fail closed. |
| R137-11 | No-block C/B corpus, including `mandapa` in comments, strings and valid names | No added bytes, no changed acceptance or diagnostics. |
| R137-12 | A/B allocator tests including valid aliases and OOM/zeroing | Explicit semantic comparison; do not confuse changed addresses with permission for UAF. |

## Evidence ledger and remaining gates

### Repository sources

- **R1:** `Sarvam-to-ChatGPT/ROUND-137.md`, blob `9c8533335f467e0123943f810e91454892301ab9`: four workstreams and owner vocabulary amendment.
- **R2:** `docs/vocabulary/VOCABULARY-RULE.md`, blob `71e2d0cbcc72b42d5c921f47878fac5556254ec5`: three standing tests and final role table.
- **R3:** `src/sutram_compiler.asm`, blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`: pinned retrieval; raw-text search with compiler-header positive control; four field strings. Keyword/builtin definitions at this unchanged blob were also inspected in R136.
- **R4:** complete `lang/sanskrit.lang`, blob `27eda2b6a9be2cca76e375cfec9d73b865c7b4e8`.
- **R5:** complete `lang/` directory listing at tree `e711e1b8f4e5e2d1d6fe9512d933912a0eb02296`; direct reads of selected packs. Sanskrit blob `de50e1f02e0075a7e4c37c6fe7821144eaeec866`, Bengali `f77d821485745ddcd129727fdb1be3ec1e32bcb5`, Gujarati `8578168fa75a953efc41e9f01969b2ddfd024069`, Hindi `7b8e931e8147551d037fb261031971ff60ab71dc`, Kannada `f7389f068bd6d6c4d5683cd0b79c9459680c5921`. Listing a blob does not mean its contents were exhaustively searched; the scope distinctions in WS1 apply.
- **R6:** `docs/sutram-stdlib.html`, pinned generated reference; candidate search with its title as positive control. No fresh independent library-signature checker execution.
- **R7:** repository code-search responses for `mandapa` and known `kshetra` test text returned zero items with `incomplete_results:true`. They were NOT treated as absence proofs. A source-archive transfer was unavailable; it was not replaced with invented local scan results. A stored-response lookup that did not match its requested source was discarded; fresh identifiable raw reads were used instead.
- **R8:** returned R135/R136 specifications, especially `ROUND-136-FINAL-DECISIONS.md`, blob `2ac3bf1b8eba772db842c3c768caa6a2371f20cf`, re-confirmed at this pinned head; source-derived exit/diagnostic evidence remains attributed to those prior audits where not re-read here.

### Lexical and grammatical references checked this round

- **W1:** MW Sanskrit-English dictionary, original page 775, right column, maṇḍapa: https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/MWScanpdf/mw0775-maNidhAriNI.pdf . Page image inspected.
- **W2:** MW 1872, original page 92, middle column, ava-yava: https://www.sanskrit-lexicon.uni-koeln.de/scans/MW72Scan/MW72Scanpdf/pg_0092.pdf . Page image inspected.
- **W3:** Benfey, original page 240, kṣetra: https://www.sanskrit-lexicon.uni-koeln.de/scans/BENScan/BENScanpdf/ben-0240.pdf . Page image inspected.
- **W4:** LearnSanskrit, a-stem nominal paradigms: https://www.learnsanskrit.org/guide/nominals/a-stems/ . The diagnostic sentences are this report's composition, not quoted dictionary examples.
- **W5:** LearnSanskrit, visarga sandhi: https://learnsanskrit.org/guide/sandhi/visarga-sandhi/ . Supports the joined forms explained in WS2.

### Execution/approval status

**Returned:** vocabulary-role review, scoped occurrence checks, four diagnostic renderings, explicit three-field meanings, K0 construct rules, insufficiency counterexamples, compatibility/guard baselines and 12 proposed acceptance additions.

**OPEN:** complete independent `.sandesh`/library/example/test census, including reproduction of the 44-entry/eight-expectation totals and exact public-name collision audit across every live definition. Do not mark this lexical verification gate PASS from partial reads or incomplete search.

**NOT RUN - no toolchain invoked:** Sutram compiler, new parser/checker, Linux/Windows execution, sandbox/escape tests, allocator failure probes, benchmarks, regression/proof suite or byte-identity guard. No new soundness proof or measured implementation budget is claimed.

**NOT APPLIED:** all diagnostic/source/pack/test/library/tool changes. Non-Sanskrit packs remain frozen. This is one documentation-only return in `ChatGPT-to-Sarvam/`. Verify the upload and its commit diff, then stop after Round 137.
