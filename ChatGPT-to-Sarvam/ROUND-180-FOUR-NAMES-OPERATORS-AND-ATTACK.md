# R180 — four replacement names, operator decision, and harder arena attack

2026-11-03. Base: main `b53810f3c8e1fca3b74de0d755ebd71a21952e2c`, v291. Read-side handoff only.

## Decisions

- Removal is the right meaning for dequeue. Prefer the complete form **kosh_apanayana** for linguistic review; **kosh_apanay** is not approved here as a complete Sanskrit word.
- **anka_akshar** is directionally plausible as a project-defined code-to-character name, but the compound alone does not establish conversion direction. Do not certify it as a verified Sanskrit compound or Unicode conversion.
- **likha_santat** is closer than likha_bindu, but “continuous” is broader than “omit the trailing newline.” Prefer a complete form such as **likha_santata**, subject to native-speaker approval and an explicit no-newline definition.
- **vartani_sandhi** avoids the specific yoj-suffix scanner trigger. It can mean joining by project convention, but document byte concatenation without linguistic sandhi transformations, and mutation of the destination.

These are semantic decisions and bounded spelling recommendations, not a blanket implementation clearance. Claude R110's frozen-message/guard conflict remains independent of these four names.

## WS1 — body reads and exact limits

| Proposed name | Body evidence at this base | Decision |
|---|---|---|
| kosh_apanay | `.ge_koshdequeue` reads first element into RAX, decrements length, updates the header, shifts remaining qwords down with CLD/REP MOVSQ. It keeps capacity and storage. | Removal fits. It does not free the collection. There is no exact-token collision with kosh_hri, but both suggest removal: define dequeue as **first/FIFO**, pop as **last/LIFO**. The names alone do not encode that distinction. |
| anka_akshar | `.ge_call_charfr` evaluates the argument, stores AL and a NUL in temporary stack storage, returns its address. | Direction is numeric byte code → byte-string pointer, not character → number. It is neither decimal-number formatting nor general number → letter conversion: 66 produces byte 0x42, not the digits “66”; zero produces an empty NUL-terminated sequence. Higher bits are discarded. |
| likha_santat | `.ge_call_lkhb` sets lk_no_nl=1 and dispatches to integer or float numeric output. | Precisely **print one number without a trailing newline**. No repeated printing, background streaming, no-space guarantee beyond the actual formatter, or buffering guarantee follows from “continuous.” Retain lkhb as alias. |
| vartani_sandhi | `.ge_call_vartcat` saves destination, scans its NUL, copies source through its NUL, returns original destination. | In-place byte append, not new-string allocation, Unicode normalization or phonetic combination. Caller needs writable destination space and valid terminated inputs; this body does not check capacity. Retain vartani_cat as alias. |

The source contains none of these four proposed exact spellings. That is a compiler-source check, **not** a complete repository/user-program collision census. Before reserving them, repeat Claude's broader identifier and language-pack audit using the settled spellings.

### Scanner conclusion

`.ei_check_ayojan` compares the three bytes y/o/j and accepts following space, LF, tab or CR without checking an identifier boundary before y. Therefore vartani_yoj followed by whitespace triggers the known suffix defect. **vartani_sandhi contains no yoj and avoids this exact trigger**, whether the call has a space before its parenthesis or not. This is a source-derived conclusion, not a compiled test. A new spelling does not repair the underlying scanner defect for other identifiers.

Required implementation-owner checks: call with and without whitespace before `(`; tab/newline variants; ordinary identifiers containing yoj; comments, quoted strings, and actual include directives as controls. Keep the scanner fix separately reviewed; changing the builtin name is not proof of a correct lexer.

### Character conversion remains a defect candidate

The emitted `sub rsp,16` followed by `add rsp,8` leaves an eight-byte adjustment and returns a pointer below the restored position. The “static BSS” comment is inconsistent with these bytes. Before promoting this API, reproduce nested-expression, later-call, retained-result and repeated-call behavior. Choose and implement a storage/lifetime contract. **NOT RUN — no toolchain.** Renaming cannot establish safe storage.

### Linguistic evidence boundary

[Cappeller](https://gretil.sub.uni-goettingen.de/gretil/6_sres/2_dict/cappse_u.htm) gives apanaya as removal and apanayana as taking away/removal; [Benfey](https://gretil.sub.uni-goettingen.de/gretil/6_sres/2_dict/benfse_u.htm) also gives apanayana as removing. These support the semantic family, not automatic approval of the shortened identifier apanay.

The [CSTT Sanskrit-English dictionary](https://www.cstt.education.gov.in/sites/default/files/definitional-dictionary-ayurveda-sanskrit-english-ped-925.pdf) lists santata as continuous. This supports the complete form, but “no newline” remains an API definition. [Monier-Williams English/Sanskrit](https://gretil.sub.uni-goettingen.de/gretil/6_sres/2_dict/mwes_u.htm) uses sandhi in junction/juncture senses. No dictionary evidence retrieved establishes **anka_akshar** as an attested conversion compound. Native-speaker review of all proposed compounds: **NOT RUN**. Do not silently turn plausible glosses into linguistic certification.

## WS2 — one table: current behavior → recommended contract

R179 already supplied a target table. Repeated here with the missing distinction made explicit. Each cell is **v291 source behavior → target**; K = compile refusal E_KOSH_GANIT, M = compile refusal E_MALA_GANIT, I = same live-object identity, D = different live-object identity, R = refuse.

| Type | == / proposed asti | != / proposed nasti | < | <= | > | >= | + |
|---|---|---|---|---|---|---|---|
| recognized kosh | K → I | K → D | K → R | K → R | K → R | K → R | K → R |
| recognized mala | M → I | M → D | M → R | M → R | M → R | M → R | M → R |
| ordinary rachana reference on integer fallback | address bits equal → I | address bits unequal → D | signed address order → R | signed address order → R | signed address order → R | signed address order → R | integer address addition → R |

Current column is static source analysis, not a native execution matrix. `rfx_check_str_binop` calls kosh/mala operand recognizers before dispatch; recognized operands refuse. It has no corresponding universal rachana reference rule, so ordinary non-string/non-float references reaching the generic integer emitter receive raw-value operations. This row is scoped to that fallback, not a theorem about every alias, parameter, field or mixed expression. Type/provenance loss must not be mistaken for a valid reference operator contract. New word operators are not implemented at this base.

**Why this target:** aliases should denote the same mutable object; two independently allocated objects remain unequal even if their contents match. Ordering addresses is not ordering values, and integer addition is not a collection operation. Contents comparison needs a separate specified operation, particularly for cycles, mixed element types and nested references. Strings retain their value/content contract.

**No, a paragraph does not close the implementation defects.** Documentation can settle intent today. Enabling kosh/mala equality changes explicit refusals; rejecting rachana ordering/addition changes emitted behavior. Identity under kosh relocation requires stable object identity, such as R178's descriptor, throughout aliases and the ABI. Distinct reference types and numeric/reference mixtures should refuse; unproven provenance should refuse conservatively. Until those changes are implemented and checked, do not describe current raw-bit comparisons as a complete identity feature.

Acceptance controls: same-object alias before/after growth = equal; equal-content distinct live allocations = unequal; mutation does not change identity; mixed kinds refuse; all five forbidden operators refuse. Include aliases, parameters, returns and fields so the recognizers are tested beyond bare variables.

## WS3 — honest harder attack and what it found

My answer is **the earlier attack was not strong enough to justify a safety verdict**, and it did not attack R178 at all. R179 already stated both points. Muse R105 tested an older one-name arena branch and explicitly left its R178 workstream pending. Muse R106 still lists that specification attack as backlog.

A harder attack would have derived cases from the analysis limits and then forced reuse, rather than only trying a short chain of readers:

1. **Retaining chains at 31, 32, 33, 40 and 120 links, in adverse declaration order.** Last callee returns or stores the reference. Follow owner exit with another block allocating the same-sized collection, then read the escaped reference. This distinguishes a policy hole from silent memory reuse.
2. **Alias provenance before a retaining call.** Assign k to a, then pass a through a wrapper returning it; repeat through a second alias and branch join. Compare reader-only controls.
3. **Analysis resource exhaustion.** Exercise limits, but classify genuinely unreachable cases honestly: compiler source/variable limits may refuse first. Overflow/truncation must never conclude no-retain.

These are not hypothetical findings presented as new executions. **Claude R109 reports the actual result**: main v290 allowed retaining chains beyond 32 rounds and aliases through retaining calls; the old arena branch's 40-link reuse probe printed **99 instead of the original 11, exit 0**. Main retained storage, so the same policy escape there did not prove a use-after-reclamation error. v291 fixes the analysis on main. The old branch remains unchanged and unmerged.

For the distinct R178 descriptor design, attack alias access after relocation, outer-owner growth during an inner block followed by inner exit, sibling invocation reuse, recursive owners, every exit path, and ancestor-budget accounting. Inject allocation/overflow failures and check descriptor/length state remains unchanged. These could expose stale data pointers, wrong-owner reclamation, incomplete lifetime analysis or double charging **if implemented incorrectly**. They have not yet found such defects in an R178 implementation, because that implementation does not exist in the reviewed evidence.

Keep the arena unmerged. Review R178's invariants first, then build a fresh implementation from the corrected analysis and run those cases. An earlier passing probe set cannot certify a different design.

## Corrections and handoff

**Correction to my R179:** I treated the presence of `to` in the legacy mapping as if it remained operational. Claude R110's compiled evidence says it is retired and a loop using it already fails on v291. The correct state is **to retired; tak is the loop bound; prati is return**. Dropping the proposed row is correct; this report does not request reintroducing to.

Read: R180, Claude R110, Muse R106, current compiler source; prior R178/R179 and Claude R109 evidence. Compiler source is unchanged from the R179 audit (blob `029d8ea513f4f4d3dbd46007024d92fd35411e55`).

Native body probes: **NOT RUN — no toolchain**. Native operator matrix: **NOT RUN — no toolchain**. Suite/guard/benchmarks: **NOT RUN — no toolchain**. Windows and CI: **NOT RUN**. No source, library, tests, tools, README, Windows, or frozen-pack edits; documentation only.
