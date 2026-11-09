# ROUND-228 — A temporary region needs ownership, not just a marker

9 November 2026. Reviewed main **acc4e4c5a5fbf5f58877f4c569d17d72b3f66bac**, Sarvam ROUND-228, relevant lexer, mandapa/escape and kosh allocation/growth source, and the R167 verifier/normalizer changes.
Documentation-only design return. **Runtime checks: NOT RUN — read-side role, no toolchain used.**

## Verdict

**Right-with-a-caveat: keep the owner's character, use `~ { ... }`, and treat this as a design candidate, not an implementation-ready cursor patch.** The spelling makes intent explicit. It does not prove non-escape, decide allocation ownership, or replace slice validity checks.

| Requested decision | Answer |
|---|---|
| Character | `~` only; no danda alias |
| Extent | (b), the braced region |
| Reclamation | Both descriptor and all region-owned buffers must be reclaimed; today's scratch rewind does neither for kosh |
| Escape check | Declaration-depth comparison alone is insufficient |
| Existing output bytes | An additive implementation can preserve them; not proved until the guard runs |
| Earlier designs | This can replace an alternative region-entry spelling. It does not replace ownership or the existing slice/alias safety mechanisms |

## 1. Two lexer facts change the proposal

In `src/sutram_compiler.asm`, `lex .not_comment` calls `r66_is_danda_at`; `.emit_danda` emits **TOK_DELIMITER with the semicolon value**. The helper in `src/r66_indic_lexer.inc` recognizes both single and double danda. Danda is already assigned syntax. Repurposing it as a region entry would change existing source meaning. Do not give it a second lifetime meaning.

In `lex .try_operator`, tilde has no branch and reaches **“Unknown char — skip.”** It is available for a future token, but is not currently rejected as unsupported syntax. A standalone tilde before otherwise valid old statements can therefore disappear during lexing. Do not tell users that v315 understands or enforces the new promise. New examples need an explicit minimum compiler version; an older compiler is not a safe feature detector. This is a source finding, not a compiled demonstration.

Reserve tilde at statement start followed by a braced body. Diagnose missing braces, expression uses and stray tilde explicitly in the new implementation. Future unary operators would need a deliberate grammar decision. Keep strings and comments unaffected.

The symbol's meaning must be taught as “temporary region”; it is not self-explanatory. ASCII accessibility and the owner's choice justify it. No claim about every Indian keyboard is needed for this decision.

## 2. Choose a braced region, not the remaining statements

A beginner should see both where the temporary lifetime begins and where it ends. Braces make nesting and movement of statements visible. A suffix marker makes an unrelated later declaration temporary simply because it was moved below one line.

The suffix form also exposes a direct defect in the proposed depth test: a variable declared before tilde and a temporary declared after tilde can have **the same lexical declaration depth**. The comparison `lhs.depth < rhs.depth` then misses the escape. Inventing a new region depth at the marker can fix that particular example, but now the marker introduces a real region anyway.

Proposed syntax, not accepted current Sutram:

```text
~ {
    kosh temp[10]
    // use temp here
}
```

One execution enters one region; repeated loop executions create successive lifetimes. Sibling regions at equal nesting depth are different owners. Return, break and continue must release exactly the regions they leave, innermost first; continuing a loop inside a region must not release an enclosing region that remains active. Recursive calls need separate dynamic instances.

## 3. Save/restore is not a kosh implementation

The existing reusable machinery is real but narrower:

- `r72_parse_mandapa` lowers to a saved scratch cursor, body and AST_REWIND. `r73_ret_mark` and the loop-exit machinery arrange early-exit cleanup.
- `r108_kosh_alloc` remembers open-block kosh for call restrictions, then reaches `r101a_emit_kosh_alloc`, which jumps to persistent `emit_nirmmita_from_rax`.
- `r127_emit_grow` in `src/r65_arena.inc` extends small persistent allocations or allocates new buffers; large storage can be separately mapped.

Restoring the scratch cursor alone therefore does **not** reclaim a kosh descriptor or its persistent buffers. Restoring the persistent cursor as well is unsafe.

Counterexample: create an outer kosh; enter a temporary region; grow the outer kosh until its elements move; leave the region; read the outer kosh. Its descriptor now points to storage allocated after the entry mark. A global persistent rewind invalidates that storage even though no local collection escaped. In-place extension across that mark is another case to handle. The relevant property is **who owns an allocation**, not when it happened.

Required contract:

1. A kosh created in the region belongs to that region. Its descriptor, initial buffer, replacement small buffers and separately mapped buffers are accounted to that owner.
2. An older kosh keeps its original owner when grown inside the region, including through aliases and function parameters. It survives the region's exit.
3. On exit, release the region's current large mappings, retained small allocations and descriptors, without touching older owners. Do not double-free an old mapping already released during growth.
4. Preserve alias agreement while the owner lives. Never reclaim the descriptor and then expect its own liveness field to safely detect stale access.
5. Define allocation failure, alignment and accounting before claiming a budget or measured memory improvement.

Owner-specific chunks plus an explicit list of large mappings are a possible lowering. They require emitted bookkeeping, allocation routing and cleanup; they are not two cursor instructions. An owner/handle design is another option, with the ABI and access costs already described in ROUND-225. The marker does not choose between these implementations.

“Everything allocated after it” must be corrected to “allocations owned by this region.” Growing an older object is the necessary exception. Also decide whether mala and raw nirmmita participate. Ordinary called functions must retain their existing allocation behavior unless a specified region-aware calling convention routes their new allocations elsewhere. A lexical marker must not silently turn every callee allocation into temporary storage.

## 4. The escape proof still has work to do

Use owner provenance and an outlives relation, not declaration depth alone. Depth can help for direct lexical nesting but cannot represent aliases, equal-depth siblings or function retention by itself.

| Path | Required rule |
|---|---|
| Assignment to an outer variable | Refuse region-owned reference; permit copied scalar data |
| Store into an outer kosh or other memory | Refuse references to shorter-lived region storage; inspect the stored value, not only the receiver |
| Return | Refuse a region-owned reference and any slice/interior pointer derived from it |
| Call | Allow only a proven non-retaining use, with result provenance accounted for; unknown/foreign calls must conservatively refuse unless an explicit safe contract exists |
| Alias or conditional expression | Propagate the possible owners through assignment and joins |
| Slice | Carry the source owner's lifetime and retain existing slice growth/escape restrictions |
| Nested regions | An inner reference cannot be retained by an outer owner; an outer object may be borrowed by an inner region |
| Analysis limit | Refuse when the proof cannot finish; never interpret exhaustion as safe |

There are already useful pieces: `r73_check_stored`, `r108_note_alias`, `r108_check_call` and its retention summaries. Extending these is still analysis. The programmer's statement of intent removes a choice about desired lifetime; it does not remove the compiler's duty to verify that intent.

A slice can become invalid during a region's lifetime if its backing storage moves. A promise about what happens at region exit does not solve that separate invalidation problem. Keep the existing fifteen-shape refusal coverage and the current predicate/walk checks. **Do not delete FLAG_SLICED/peer_binds proposals or their equivalent safety obligations merely because tilde exists.** Those names are design vocabulary, not a claim that these exact symbols implement main.

## 5. Additive output is a requirement, not a result

It is feasible to preserve output for programs without the new syntax by keeping their parser/lowering, descriptor layout, helpers, globals and allocation paths unchanged. Emit new region support only when requested.

Changing the shared kosh ABI or emitting unconditional owner machinery can change old output. Removing or changing existing mandapa behavior would also violate the additive requirement. Adding keyword-free punctuation does not automatically preserve bytes.

Run the established ELF/PE guard on the eventual implementation and compare both successful output bytes and existing refusals. Also cover tilde in comments/strings and old danda programs. **No 783-program result for this feature exists in this review.** Existing contributor guard results concern their compiler changes, not this unimplemented proposal.

## 6. Does it simplify the language?

**It sits beside existing behavior if introduced additively.** It could become the preferred explicit region entry and share cleanup/ownership implementation with a future mandapa revision. It cannot silently replace mandapa today while promising old bytes, nor replace kosh/slice safety.

A strictly verified region might avoid generation-handle checks for its own non-escaping references if the static proof is complete. That is a meaningful potential simplification, not an established proof. Calls, raw addresses, slices and storage into containers are precisely where that proof must hold.

Recommendation: retain the syntax candidate, reject the “cursor plus depth comparison is sufficient” implementation claim, and settle owner routing and non-escape semantics before requesting a prototype. The smallest spelling does not imply the smallest compiler change.

Proposed acceptance cases, **NOT RUN**: local small/large kosh reclamation; outer kosh growth in place and by movement; aliases and parameter growth; nested/sibling regions; same-scope pre-marker assignment; stored/returned/indirectly retained references; all existing slice refusals; raw/foreign escape; early exits; recursion; allocation failure; and unchanged legacy output. Include repeated short regions and one long-lived region: only the former promises periodic reuse.

## R167 follow-through on the prior return

The new verifier source addresses the three principal ROUND-226 follow-up 2 findings: strict manifest parsing, connected digest traversal, and digest-aware removed-image classification. Manifest-relative path resolution now uses structural lexical containment. The normalizer validates decoded JSON text and reports before/after/neither after a partial write. These are source-level closures, not test results from this reviewer.

Two narrower verifier hardening limits remain visible:
- Lexical containment does not exclude an in-tree symlink resolving outside the repository; the retained-copy path also bypasses resolve(). Validate canonical containment or explicitly reject symlinks, and validate retained-copy paths under the same policy.
- Removed/copy TSV rows overwrite duplicate path keys without rejecting conflicts. Graph ambiguity is checked when follow() is reached; an exact OK digest bypasses it. If the contract is that any conflicting record invalidates the whole input, validate records once at load time, including conflicting duplicates and cycles.

No claim is made that the current tracked records contain these defects. Fixtures for those cases would test the advertised boundary.

Claude R167 reports 81 PASS / 0 FAIL / 1 NOT-RUN on main and staged v316 acceptance under Wine. Native Windows acceptance remains pending; no compiler merge or release acceptance is performed here. Current-tree privacy normalization is not a history purge.
