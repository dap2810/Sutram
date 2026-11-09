# R182 — operator table, naming rule, and executed patch check

Base: `f363c5432c82f2d1478f1630a2a1090c19419ab2`, v292. 2026-11-03. Read-side report.

## WS1 — what each operator does today, and what it should do

Each cell reads **today → recommended**. Today is source-derived behavior for the indicated recognized operand shape; it is not a native execution result.

| Reference type | == / asti | != / nasti | < | <= | > | >= | + |
|---|---|---|---|---|---|---|---|
| Recognized kosh variable/typed parameter | Compile refusal → same live-object identity | Compile refusal → different live-object identity | Compile refusal → refuse | Compile refusal → refuse | Compile refusal → refuse | Compile refusal → refuse | Compile refusal → refuse |
| Recognized mala variable | Compile refusal → same live-object identity | Compile refusal → different live-object identity | Compile refusal → refuse | Compile refusal → refuse | Compile refusal → refuse | Compile refusal → refuse | Compile refusal → refuse |
| Ordinary rachana reference reaching integer dispatch | Address-bit equality → same live-object identity | Address-bit inequality → different live-object identity | Signed address order → refuse | Signed address order → refuse | Signed address order → refuse | Signed address order → refuse | Integer addition of addresses → refuse |

**Why:** aliases identify one mutable object. Two separately allocated objects are different even when their fields/elements match. Address ordering is not a meaningful collection/record order. Adding reference bits is not a defined collection operation. Content equality should be a separate explicit operation with defined element types, cycles and recursion behavior. Strings retain their existing value/content semantics.

**Today is not a uniform type-wide guarantee.** At this revision, `rfx_is_mala_operand` (line 9109) accepts only AST_VAR and calls is_array_var. `rfx_is_kosh_operand` (line 9121) likewise requires AST_VAR, then checks kosh locals and typed parameters. `rfx_check_str_binop` (line 9344) refuses recognized operands before operator dispatch with E_KOSH_GANIT or E_MALA_GANIT. Those checks do not prove that every wrapper, alias, returned value or stored reference is recognized. Unrecognized references can reach raw-value paths; that is a coverage gap, not additional authorized semantics.

There is no corresponding general rachana-reference refusal in this gate. Ordinary references reaching the integer backend receive CMP/SETE or SETNE for equality, signed SETL/SETLE/SETG/SETGE for order, and integer ADD for addition. The table does not claim all expressions involving records take that path. For example, an operand recognized as a kosh still refuses. Source anchors: `.ge_eq` line 26081, `.ge_lt` line 26104, `.ge_add` line 26007 and the adjacent comparison handlers.

The v292 word aliases map to the same equality tokens. **asti/nasti change spelling, not this type behavior.**

### Does this need code?

**Yes. A paragraph settles intent but does not implement this table.** Required code work:

1. Carry reference kind and identity/provenance through variables, aliases, parameters, returns, fields, elements and expression joins; do not rely only on bare-variable recognizers.
2. Replace blanket recognized kosh/mala refusals with a typed equality/inequality path. Preserve refusal for the other five operators. Add the missing rachana type gate.
3. Use stable object identity for movable kosh storage, such as R178's stable descriptor. All aliases and ABI consumers must use it consistently; comparing a relocating payload pointer cannot promise identity across growth.
4. Refuse different reference kinds, reference/number comparisons and unknown provenance conservatively. Dead references remain invalid; equality does not legalize them.

A stable, nonmoving live record address may implement identity for a correctly typed rachana case without a new identity number. That local fact does not fix the other types or forbid raw arithmetic.

Minimum verification: same-object aliases before/after growth compare equal; equal-content distinct objects compare unequal; mutations preserve identity; all five forbidden operators and mixed-kind cases refuse. Include returned references, parameters and stored aliases. **Native checks: NOT RUN — no toolchain.**

## WS2 — one naming rule for new and existing functions

**Recommendation: use complete Sanskrit lexical words or compounds as canonical function names, not arbitrary shortened roots/stems. Preserve already accepted spellings as compatibility aliases.** The same rule applies to all 22 new names, older builtins and library functions. It does not require every function to be named with a noun: a complete action word, noun, adjective/predicate or compound can be suitable if it describes the body. It also does not mean mechanically appending “a” to every identifier.

This is the recommended policy, **not a claim that today's mixed tree already follows it**, and not authorization to undo the owner's v292 release. Existing root precedent shows current practice is mixed; it does not resolve the owner's complete-word requirement. Keep current programs working. Future canonical-name changes require a reviewed spelling/meaning decision and aliases, rather than another immediate mass rename.

Applied to the 22 v292 names:

| Current canonical name(s) | Application of the rule |
|---|---|
| kosh_kship | Review complete action form; kshepa is a candidate, not approved here. |
| kosh_hri | Review complete removal form; harana is a candidate. Preserve last-element meaning. |
| kosh_gan; pankti_gan | Review complete counting form, e.g. ganana. |
| kosh_ksham | Review capacity noun, e.g. kshamata, rather than capability adjective. |
| kosh_iksh | Review complete inspection form, e.g. ikshana; one argument, last element. |
| kosh_rikt | Review full lexical/transliteration form of the empty predicate; do not change it into an emptying command. |
| kosh_shodh | Review complete action form, e.g. shodhana; still length reset, not storage erasure. |
| kosh_yuj | Review complete joining/insertion form; preserve append behavior. |
| kosh_apanay | Prefer **kosh_apanaya** for the removal noun, subject to linguistic sign-off. This names removal, not which end; document first/FIFO. |
| jala | Lexical-word candidate; define socket creation precisely. |
| jala_bandh; jala_shru; jala_grah | Review complete action forms, e.g. bandha/shravana/grahana, against bind/listen/accept bodies. |
| akshar_laghu; akshar_guru | Word-form acceptance alone does not settle meaning: these are ASCII case conversions, not syllable weight or length. |
| anka_akshar | Compound candidate; define byte code → temporary byte-string pointer, not general Unicode conversion. |
| vartani_sandhi | Compound candidate; define in-place byte append, no phonetic transformation. |
| likha_santat | Review complete santata form and project transliteration convention; define no trailing newline. |
| likha_rup | Review full lexical form consistently; the body is simplified prefix-plus-number output, not a general format engine. |
| sankhya_bindu | “Point/dot” alone is semantically incomplete for dot product; review a product-explicit compound. |
| smaran_pratilip | Review complete copy-word form consistently with vartani_pratilip; existing precedent is not grammatical certification. |

These are **22 identifiers**: grouped rows count each semicolon-separated name separately. Proposed forms above are review candidates, not a newly approved vocabulary table. Native-speaker review: **NOT RUN**. Muse R107 and my R180 disagree on whether some shortened Roman forms count as complete words; settle that with a declared transliteration convention and a qualified reviewer, not by treating either agent's confidence as authority.

### Applying it to the “90 existing ones”

The source does not expose 90 named rows in bn_table. At this base it has **48 primary rows representing 46 distinct builtin IDs**, followed by **22 legacy-name rows**. The primary duplicates are enqueue/push sharing BN_KOSHPUSH and two parimana spellings sharing BN_PARIMANA. Keywords, shell commands and internal BN identifiers are different populations.

The remaining 26 primary rows, outside the 22 renamed ones, are:
`likh, sthagita, pad, dvaram, paadh, likha, band, nirmmita, likh8, pad8, vartani_aayam, vartani_tul, sankhya_yog, sankhya_gunan, akshar, aksharank, likh8c, pad8c, smaran, vartani_pratilip, grahan, shabda, akshar_rakh, dvaram_likha, parimana, परिमाण`.

**All receive the same policy:** preserve their accepted spelling, review the whole word/compound and exact body meaning before any canonical replacement, and retain a compatibility alias if changed. Width suffixes such as 8 may be explicit technical qualifiers; they do not make an abbreviated Sanskrit stem complete. Do not exempt an old name merely because it predates v292. This inventory is not a claim of completed native-speaker review of all older names.

## WS3 — R181 patch: executed results

I retrieved **the committed patch**, `ChatGPT-to-Sarvam/R181-probe.patch`, blob `7449474753efb9254484e3f51f04ad6adcf0fc00`. It targets `docs/CHANGELOG.md`; it is not a root-level R181-probe.patch in the checked tree.

| Target changelog | git apply --check | Actual application |
|---|---|---|
| R181 base ea97309518b61e46a9454d50a01f2e7e22bd3598 | **PASS, exit 0, no output** | **PASS, exit 0**, in disposable local copy; first line becomes ## probe |
| Current R182 base f363c5432c82f2d1478f1630a2a1090c19419ab2 | **FAIL, exit 1** | Not attempted |

Current-base diagnostic:

```text
error: patch failed: docs/CHANGELOG.md:1
error: docs/CHANGELOG.md: patch does not apply
```

Reason: the original hunk contains the v291 heading as context. Current main has the v292 entry at the top. **The original patch was valid for its stated base; it is stale on today's base.** R181's reported success was real, and this fresh check reproduces it. I have not silently replaced the original probe with a different patch or changed the repository changelog.

Commands actually executed in separate local copies:

```sh
git apply --check <scratch>/R182-retrieved-R181.patch
git apply <scratch>/R182-retrieved-R181.patch
```

The second command ran only on the original-base copy. This is an executed git test, not a native Sutram test.

## Evidence boundary

Read R182, Claude R111, Muse R107, current source, committed probe patch and both changelog revisions. R111 reports suite 295 PASS / 4 NO-EXPECTATION / 299 run, gates 60 PASS / 1 FAIL / 1 NOT-RUN, and guard 705 with zero DIFFER; I did not rerun those. The shortened “60 PASS” status does not mean every gate passed.

Only this documentation handoff is committed. No source, library, tests, tools, README, frozen packs or Windows files changed. No native suite, CI, Windows acceptance or arena merge.
