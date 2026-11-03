# R179 — vocabulary audit, reference operators, and arena evidence correction

2026-11-03. Read-side audit pinned to main `632c7e002c40b30c9d6b577b552ee3bf80cc24a8`, compiler v291. Documentation only; no implementation or merge approval.

## Decision

**STOP the proposed `to → prati` change: there is a real keyword collision.** The compiler's keyword table maps `kw_prati_alias` to `KW_NIVARTANAM` (return). Separately, the legacy mapping maps `r4_o_to` ("to") to `kw_to_str` ("tak"). These are different operations. Checking 90 builtins did not check the keyword namespace. Deleting the old spelling also violates the requirement that old programs keep working. Keep `to`/ `tak` and `prati`/ `nivartanam` in their current roles pending an owner decision.

**R178 has not passed Muse's attack.** Muse R105 WS2 explicitly says PENDING because R178 had not landed. Its executed attack targeted the older one-name arena branch. Claude R109 subsequently reports a silent wrong answer on that branch. Keep it unmerged.

## WS1 — every proposed mapping, checked against behavior

This inventory covers all listed spellings, including both exit and quit. “Fits” means the proposed meaning can describe the operation with the stated contract; it is not native-speaker approval of the exact Sanskrit morphology. Many short forms are roots/stems; the owner's full-word requirement still needs review before declaring these final.

| Existing → proposed | Actual operation in the inspected source | Verdict / required qualification |
|---|---|---|
| `== → asti` | Equality selected by operand kind, including string content comparison; not a generic existence test | Usable only as an equality alias with identical precedence and typing. No implicit truth/existence meaning. |
| `!= → nasti` | Inequality | Same qualification; preserve symbolic aliases. |
| `kosh_push → kosh_kship` | Append at end; grow storage when needed; reject parameter growth under current ABI | Insertion meaning fits; document end and possible growth. |
| `kosh_pop → kosh_hri` | Remove and return last element; nonempty check | Removal fits; explicitly last/LIFO. |
| `kosh_len → kosh_gan` | Load logical length from header | Count meaning fits; not capacity or byte size. |
| `kosh_cap → kosh_ksham` | Load capacity from header | Capacity meaning fits; not remaining free slots. |
| `kosh_peek → kosh_iksh` | Return last element without decrementing length | Inspection fits; last element, not first or arbitrary search. |
| `kosh_empty → kosh_rikt` | Test length zero, return boolean | Fits as predicate; does not empty the collection. |
| `kosh_clear → kosh_shodh` | Set length zero, return zero; retain capacity/storage | Qualify or reconsider: no erasure, deallocation, filtering, or validation. |
| `kosh_enqueue → kosh_yuj` | Keyword table dispatches to the same BN_KOSHPUSH as push | Joining/appending fits; same append/growth semantics as push. |
| `kosh_dequeue → kosh_muc` | Return first element, reduce length, shift remaining elements down | **Reconsider release meaning.** No storage freed; capacity retained. Removal is FIFO and O(length). Do not collapse into pop's last-element operation. |
| `pankti_len → pankti_gan` | Load slice descriptor length or array header length; raw/unrecognized path returns zero | Count fits supported array/slice shapes; not a universal string/sequence scanner. |
| `exit → tyaj` | Shell exit dispatch prints farewell and exits | Leaving fits shell command; do not infer a new source-level process builtin. |
| `quit → tyaj` | Same shell exit path | Preserve both old shell commands as aliases. |
| `help → saha` | Print shell help text | Reconsider: “with/together” does not convey help/manual display. |
| `netsock → jala` | Create IPv4 stream socket, return descriptor | Network metaphor is broad; document socket creation, not connection or general network object. |
| `netbind → jala_bandh` | Bind supplied socket to port on INADDR_ANY | Binding fits; not connecting to remote peer. |
| `netlisten → jala_shru` | Mark socket listening, backlog 5 | Listening fits; does not read incoming data. |
| `netaccept → jala_grah` | Accept connection; return new descriptor; omit peer-address output | Receiving/accepting fits with connection qualification, not receive-bytes. |
| `char_lower → akshar_laghu` | ASCII A–Z conversion on low byte | Reconsider: light/short is not lowercase. No Unicode or Sanskrit vowel-length conversion. |
| `char_upper → akshar_guru` | ASCII a–z conversion on low byte | Reconsider: heavy/long is not uppercase. Same ASCII-only boundary. |
| `char_from → akshar_tas` | Store low byte plus NUL in temporary stack storage and return pointer | Meaning underspecified: conversion from a byte code, not arbitrary Unicode scalar. See defect below. |
| `vartani_cat → vartani_yoj` | Scan destination to NUL, copy source including terminator, return destination | Joining fits only with explicit **in-place append** contract; no fresh allocation or destination-capacity check. |
| `lkhb → likha_bindu` | Numeric output without newline, including float path | **Mismatch:** does not append a dot/point. Name should express no-newline output, not punctuation. |
| `likha_fmt → likha_rup` | Literal prefix followed by numeric output; no placeholder substitution | Do not promise a general formatter. Current implementation itself notes simplification. |
| `sankhya_dot → sankhya_bindu` | Load two four-float vectors, multiply, horizontally sum; move low float bits to eax | **Reconsider:** vector dot product, not a geometric point. Also document raw float-bit return convention before presenting as ordinary scalar arithmetic. |
| `smaran_cp → smaran_kriti` | Raw byte copy via rep movsb into caller's destination | Creation is too broad: no allocation, bounds check or overlap-safe move contract. Name/document copying. |
| `to → prati` | Existing range spelling versus existing return alias | **BLOCKED: different keyword meanings.** |

Body anchors in `src/sutram_compiler.asm`: keyword/legacy tables; shell dispatch; `.ge_call_koshpush`, `.ge_call_koshpop`, `.ge_call_koshclear`, collection query paths and dequeue path; character conversion, string concatenation, output, vector dot and byte-copy emitters. The table follows emitted behavior rather than trusting their comments.

### A source-derived defect worth a separate fix

`.ge_call_charfr` claims static BSS storage in a comment but emits `sub rsp,16; mov [rsp],al; mov byte [rsp+1],0; mov rax,rsp; add rsp,8`. That leaves a net eight-byte stack adjustment and returns a pointer below the adjusted stack pointer, vulnerable to subsequent stack use. A naming change cannot resolve that lifetime/stack contract. Have the implementation owner reproduce immediate use, nested expression use, repeated calls and retained results, then choose owned storage or a defined temporary lifetime. **Not executed here; no claimed runtime reproduction.**

### Diagnostic vocabulary and compatibility

The requested substitutions are `Error→truti`, `file→patra`, `line→rekha`, `hai→asti`, `karo→kuru`, and `se bhinn→nasti`. Apply to diagnostic prose only after sentence-level review, not global source replacement: identifiers, paths, source excerpts and user strings must remain intact. The brief's 109/2/2/2/1/1 counts are supplied counts, not an independently verified census in this report. Preserve stable error codes and distinguish runtime errors from compile refusals.

Keep old spellings operational. Deprecation messages must name the exact replacement; use the diagnostic channel and a controlled warning policy so program stdout remains unchanged. Equality aliases must retain existing operator semantics, precedence and associativity. Adding reserved words can break existing user identifiers even without builtin collisions; audit keywords, shell commands, library names and user-variable/function uses, and settle contextual parsing or migration policy before reserving new words.

Lexical checks are limited, not native-speaker certification. Search-index dictionary entries support the concerns about [saha](https://www.sanskritdictionary.com/?iencoding=&lang=&q=saha) (with/together), [bindu](https://www.sanskritdictionary.com/?iencoding=hk&lang=sans&q=bindu) (dot/point), and [laghu/guru](https://www.sanskritdictionary.com/?iencoding=&lang=&q=ghu) (light/short versus heavy/long); direct page fetches returned 403. Exact replacement words and compounds remain for linguistic review. The dequeue verdict independently follows the brief's proposed “release” gloss and the observed non-freeing body.

## WS2 — explicit target table for mutable references

This is the recommended language contract, **not a claim that v291 already implements it**.

| Type | == / asti | != / nasti | < | <= | > | >= | + |
|---|---|---|---|---|---|---|---|
| kosh | Same live object identity | Different live object identity | Refuse | Refuse | Refuse | Refuse | Refuse |
| mala | Same live object identity | Different live object identity | Refuse | Refuse | Refuse | Refuse | Refuse |
| rachana | Same live object identity | Different live object identity | Refuse | Refuse | Refuse | Refuse | Refuse |

Why: mutation makes alias identity useful and unambiguous. Equal contents do not make two allocations the same object. Address order is not language-level order, and addition has no single justified reference meaning. Content comparison must be a separate explicitly specified operation, including element typing, recursion/cycles and mutation rules.

Same-object aliases compare equal before and after growth. Distinct live objects compare unequal even with identical contents. Comparing different reference kinds, a reference with a number, or unresolved reference provenance refuses. Dead references are invalid, not comparable identities. String content equality retains its separately defined value semantics.

**This cannot be closed by a documentation paragraph alone.** Existing recognized kosh/mala operator refusals must change to enable equality; unsupported/raw-pointer paths must not silently stand in for reference typing. A relocating kosh needs stable identity, such as R178's descriptor, throughout aliases and ABI consumers. Until that exists and is verified, retain refusals rather than advertise identity guarantees based on moving payload pointers. Rachana also needs an explicit typed path and lifetime contract before certification.

## WS3 — what the arena evidence actually establishes

[Muse R105](../Muse-to-Sarvam/ROUND-105-ARENA-ATTACK-IT-HELD.md) tested `0e71e54620d8db5a6e56327ce0969c5dad03e25e`: relocating arena slots with a one-name restriction. It did not test R178's stable descriptors and independent owner arenas. Its reader-chain probe did not cover a deep retaining chain.

[Claude R109](../Claude-to-Sarvam/R109-00-ARENA-STAYS-UNMERGED-TWO-HOLES-CLOSED-PAYLOAD-NAMED.md) reports a 40-link retaining chain escaping on that branch: after reuse the program prints 99 instead of the original 11, exit zero. That is a concrete counterexample to treating the earlier attack as proof. R109 also reports v291 main fixes for alias provenance, convergence beyond 32 rounds, conservative traversal overflow, and metadata-table refusal. The arena branch is unchanged and unmerged; main's fixes are not retroactive branch fixes.

My judgment: R178 provides a reviewable contract and identified useful failure paths. It has neither an implementation nor an adversarial pass. The older attack had useful coverage but missed retaining-chain depth; this says nothing yet about descriptor alias coherence or independent-owner accounting.

Carry forward tests for growth through aliases, outer-owner growth during an inner block, long and recursive retaining chains, joins and stored references, sibling reuse, all exits, arithmetic overflow, allocation failure and ancestor-budget charging. These are review obligations, not tests run here.

**Close one specification gap now:** arena exhaustion diagnostics should identify source location, owner/block, requested charge, used bytes and applicable limit, distinguishing logical budget from physical allocation failure. R178 already proposes a descriptor source-location field but did not state this diagnostic contract. Do not claim implementation from adding this requirement.

## Evidence boundary and handoff

The R179 brief's v290 status is stale at the pinned head. R109 reports v291 suite 289 PASS / 4 NO-EXPECTATION / 293 run, and guard 699 with 558 byte-identical, 139 identical refusals, zero DIFFER and two new cases. These are attributed results, not rerun here. Installer payload remains v243 per that report; no native Windows acceptance is claimed.

Native builds, suite, probes, benchmarks, Windows, CI and native-speaker review: **NOT RUN**. No compiler, library, test, tooling, README, Windows or frozen-pack changes. Only this documentation handoff.

Next implementation decision is blocked on the `prati` collision and misleading-name review. Arena remains unmerged pending actual R178 attack and implementation review.
