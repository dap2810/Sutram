# R184 — 531 English words/abbreviations, 2,251 occurrences: a workstream

Base: `ff5d9d419976f3f48f37e63ab4aefaa56f41dd9b`, v292. 2026-11-03. Read-side inventory and vocabulary proposals, not a rename patch.

**531 distinct English surface words or conventional English abbreviations/components, 2,251 occurrences under the explicit counting method below. This is a workstream, not an under-50-word round.** These are identified lexical candidates, not 531 approved new public names. English in deliberately English documentation is excluded. Sutram is excluded and must remain unchanged.

| Requested scope | Files inspected | Identified occurrences |
|---|---:|---:|
| examples/*.sm: identifiers and strings, not comments | 299 | 1,386 |
| lib/*.smlib: function names, parameters and strings, not local variables/comments | 24 | 330 |
| lang/*.lang: entries and comments | 11 | 508 |
| src/sutram_compiler.asm: diagnostic/help string candidates, excluding Sutram Error | 1 | 27 |
| Total | 335 | 2,251 |

[ROUND-184-ENGLISH-TABLE.csv](ROUND-184-ENGLISH-TABLE.csv) is the full 531-row table: word, count, per-scope counts, preferred lexical draft, second option where supplied, collision-screened identifier candidate, decision and every file:line occurrence with its original token. [ROUND-184-ENGLISH-INVENTORY.json](ROUND-184-ENGLISH-INVENTORY.json) contains the machine-readable evidence, exclusions and other tokens for review. The table is the requested inventory, not merely a sample.

## Counting rules and confidence

The scan uses the exact checked-out commit. It tokenizes Sutram's # comments and double-quoted strings separately. Examples contribute code identifiers and string words; libraries contribute declaration names/parameters and strings. Underscores and camel case split identifier components; decimal suffixes do not create extra words. Case is folded, but different surface forms such as word/words remain separate. Thus kosh_push contributes the English component push, not an English classification of kosh.

Single-letter mathematical identifiers, E_ codes, proper names and Sanskrit/Indic transliterations are not counted as English. Articles/pronouns in prose are distinguished from single-letter test data. Sanskrit words that look English are not automatically translated. For example compiler ghatak-star means module level, not a celestial star; pad8c is an established read builtin. The unused BAD debug label has no demonstrated output path and is excluded. The evidence records these exclusions.

The compiler scan selects db string fragments associated with diagnostic/help labels (msg/hdr/hint/prefix/txt/usage/banner, module errors and the displayed root name), then reviews English candidates. It is **a source-string inventory, not a complete proof of output reachability**: computed output, byte-encoded text and every unusual label need a separate reachability pass before claiming an exhaustive public-message census. This limitation does not affect the workstream decision: the examples/lib/packs alone exceed the threshold. The complete raw-token classification is not a language-recognition theorem; Romanized Sanskrit, abbreviations and borrowed technical terms can be ambiguous.

The library signature pass covers the previously counted 306 definitions. A word occurring in five calls is counted five times; definitions alone are not the denominator. The 531 total includes technical/legacy words that should be retained under explicit compatibility rules, not only prose requiring translation. In particular it is not the number of breaking API renames required.

## Representative entries — the full table is attached

| English | Occurrences | Preferred lexical direction | Second option / treatment |
|---|---:|---|---|
| push | 139 | antakshepa | Existing kosh_push alias remains valid; use the approved kosh_kship spelling in new teaching material, not a third alias from this glossary |
| out | 81 | nirgamana | Rename only local/example bindings or parameter labels after binding checks |
| len | 58 | daurghya | Existing approved length APIs retain their meanings |
| cap | 44 | dharanashakti | dharanakshamata |
| is | 35 | vidyate | Translate complete sentence, not isolated token substitution |
| src | 30 | srotasthana | Parameter/identifier context |
| ok | 29 | saphala | Preserve existing status/result contract |
| the | 29 | no standalone substitution | Rewrite sentence; Sanskrit does not require an English-style definite article |
| a | 26 | no standalone substitution | Sentence-level choice; do not replace mathematical a |
| done | 26 | samapita | Check whether it is a message, state or control variable |
| buf | 24 | sanchayika | Preserve buffer capacity/ownership semantics |
| count | 13 | ganana_kriya | Full identifier candidate supplied in CSV |

These are **proposed technical vocabulary**, not certified idiomatic Sanskrit sentences. Second options are supplied only where a plausible second was available; blank means no second proposed, not that no alternative exists. Native-speaker review: NOT RUN. The glossary needs that review before publication. A lexical suggestion does not certify every grammatical form, compound or sense in every occurrence.

## Collision checks and replacement rules

The namespace was built from compiler keyword/builtin table rows resolved to string labels and both columns of every .lang entry. Candidate identifiers were also screened against identifiers already appearing in examples/lib. Every concrete identifier candidate in the table is absent from the checked reserved namespace. If a lexical suggestion already existed as an identifier, a context-qualified compound was selected rather than overwriting the binding. Phrases/articles and retained units are explicitly marked as not identifier renames.

This is an **exact-spelling collision screen**, not proof that a bulk rename is safe. It does not establish that two proposed replacements cannot collide when applied together to a particular local scope, nor that an identifier avoids every scanner defect. Before changing a binding, generate the full proposed identifier and check its scope, exports, callers, lang mappings and scanner behavior. In particular test the known yoj-whitespace suffix case; do not trust table matching alone.

Apply complete lexical words/compounds to future names. Keep existing owner-approved roots and all published aliases operational. The 22 v292 mappings are settled compatibility facts; this audit does not replace them with a competing glossary. A draft such as antakshepa explains push's action; it does not authorize renaming kosh_kship again.

Different contexts require different treatment:

- **Prose in string literals:** translate the whole sentence. Update its golden only as an intentional output change. Do not render an article, preposition or verb by mechanical one-word replacement.
- **Example-local names:** use a meaningful complete identifier; update every bound reference. Deliberately invalid examples must remain invalid for the same reason.
- **Library public functions and parameter names:** parameter labels are readable API documentation; public function names may have external users. Add compatibility aliases for any public rename. Preserve function behavior, arity and calling convention.
- **Legacy builtin spellings:** they are compatibility cases, not mistakes to delete. Some examples intentionally test old-name acceptance and warning emission; keep those tests as controls.
- **Unit names:** miles/pounds/kilometers/kilograms remain exact physical units in this inventory. Translate surrounding labels or adopt a reviewed unit name without changing the unit's value. Replacing mile by krosha would be a semantic bug.
- **External/technical identities:** CLI flags, file extensions, filenames, foreign API symbols, mathematical conventions and E_ tags are identifiers/contracts. Translate explanatory prose around them. Renaming requires its own compatibility decision; a Sanskrit-looking string is not a valid substitute for an OS symbol.
- **Pack comments/entries:** all eleven were read. The ten frozen non-Sanskrit packs remain unchanged; this inventory is not permission to translate their comments or remap entries.

## Compiler-specific findings

The residual compiler count includes actual prose terms tab and space in the mixed-indentation diagnostic; bit in numeric/bit-operation explanations; and embedded technical exemplars such as fd, arr, --check, --lang, --version, .bin and old builtin spellings. These require different policies. For example avakasha is a draft for a prose description of a space, while --lang is an accepted command-line interface and cannot be translated only in its help text.

Sutram Error is deliberately excluded because R183 already inventories its migration. No Error→truti change is made here. Many surviving Roman words are Sanskrit or Indic, not English; detecting Hindi versus Sanskrit would be a different audit and should not be hidden inside this English count.

## Recommended workstream

1. Accept the scope/count method and review the vocabulary table with a qualified Sanskrit reviewer. Resolve ambiguous/technical terms and sentence contexts before editing.
2. Improve Sanskrit teaching examples and their intended output, preserving negative tests and legacy-alias controls. This is likely the most visible student benefit.
3. Review public library names separately from parameter/local names; introduce aliases only for approved public changes.
4. Revise default Sanskrit diagnostic prose with exact expected-output changes. Keep code words, flags, units and external symbols accurate.
5. Queue the frozen-pack findings until the owner explicitly changes that scope. Do not use this audit to bypass the freeze.

Verification performed: pinned tree retrieval, lexical inventory, file/line attribution, declared-name collision screening and output generation. No source, library, examples, packs or compiler were changed. Native build/suite/guard: NOT RUN — no toolchain used. Translation fluency and complete compiler output reachability remain unverified. This report should not be described as a fully approved, mechanically applicable 531-word rename plan.
