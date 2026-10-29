# Sutram ROUND 132 — Sanskrit memory terminology audit (READ SIDE)

**Assignment:** `Sarvam-to-ChatGPT/ROUND-132.md`, pinned Git blob `d7ae60b8fba1fd40c66c20952558f783ffb7c8bc`. **Baseline `main`:** `b6106934a9d51b0381dc3f09e478a79c8cdc5ff6`. **Inputs read:** `docs/MEMORY-DESIGN.md` blob `eb7b23bded2aa5475cc710eeb34f6c1b0cb12d48`, `LANGUAGE-PRIORITY.md` blob `64682919a70fa1b79e415bc879aee9cad07582ad`, `lang/sanskrit.lang` blob `27eda2b6a9be2cca76e375cfec9d73b865c7b4e8`, and `src/sutram_compiler.asm` blob `e64bcce50e1e05a2a0a9fca9f337b8c0b7b93345`. Sanskrit-only; memory-vocabulary review, not permission to implement memory design. Round 133 is separately issued and **not performed** in this check.

## Executive verdict

**Five genuine Sanskrit words; only some fit these APIs.** The words are real; the proposed technical entailments are not automatically real. Retain `nyasa` only as an optional name for *placing/depositing*; reject the invented *must return it* lexical obligation. `pratyarpana` is valid for *giving back*, but `mocana` (मोचन, releasing/unbinding) is more exact for `free`. `kosa` points to the same Devanagari कोश already occupied by Sutram's existing **`kosh`** growable collection; do **not** reuse it as a memory region. Prefer `kshetra` (क्षेत्र), a directly attested *region/field* term, provisionally. `samskara` is a real word but **reject it as a word for stale contents in recycled memory**. `rna` really means *debt/obligation*, but an allocation-count debt is a conscious metaphor, not a semantic rule enforced by the word.

## WS1 — five words, independently judged

| Proposed spelling | Real Sanskrit? | Grounded sense | Fit and decision |
|---|---|---|---|
| **`nyasa`** — न्यास (*nyāsa*) | **YES**, masculine noun | Putting/placing, deposit or pledge, entrusting, **also** putting aside, relinquishment | **PARTIAL** for allocate/deposit. Nothing in the noun says every deposit *must* be returned by the depositor or that it is a linear resource. Using `nyasa` for alloc/free pairs would express an analogy, not establish an obligation or automatic check. It can even mean **giving up**, so do not claim unique allocate-versus-release direction. |
| **`pratyarpana`** — प्रत्यर्पण (*pratyarpaṇa*) | **YES**, neuter noun | Giving back, restoring, returning | **YES as a deliberately figurative 'return to owner'**, although kernel memory reclamation is release of a resource, not always repayment of an entrusted deposit. **`mocana` is less metaphorical for deallocation**. Do not promise `pratyarpana` automatically checks aliases or ownership. |
| **`kosa`** — proposed कोश (*kośa*) | **YES, word; NO, not a safe new Sutram keyword** | Case, sheath, enclosure, store, treasury, dictionary; in philosophical language multiple sheaths | **REJECT AS NEW REGION KEYWORD.** Project already has **`kosh` = कोश** (compiler `kw_kosh` at line 718, `kw_dev_kosh` at 735, plus `kosh_*` collection functions). Two Latin spellings for the same native word but different memory types will mislead users and risk Devana-gari vocabulary collision. Moreover *pañcakośa* is not linguistic evidence for nested regions being 'shed outside-in' or released at function return; that is an imported computer-lifetime concept. Standard transliteration for कोश is *kośa*; plain ASCII `kosa` can conceal the crucial ś/sh sound. |
| **`samskara`** — संस्कार (*saṃskāra*) | **YES**, masculine noun | Preparation, refinement, purification, correction; also *mental* impressions/latent dispositions in philosophical systems | **NO for stale bytes or 'uninitialized residue'.** The term's cognitive/ritual impressions are not a claim about residual physical RAM. In memory APIs it might someday name *initialization/refinement* if carefully specified, but could misleadingly imply safety/cleaning that the program does not perform. **Do not use it for the proposed memory feature at all.** |
| **`rna`** — ऋण (*ṛṇa*) | **YES**, neuter noun | Debt, obligation, something owed; also mathematical minus/negative quantity | **METAPHOR ONLY** for outstanding allocations. 'Three deposits owed' could be a debug accounting metaphor, but the word does not encode ownership, escape analysis, byte lengths, or when/whom repayment is due. A `rna` counter is not proof of memory safety; region-batched release also makes raw deposit counts misleading. Prefer explicit count fields/diagnostics over a new keyword. Pronunciation and ASCII convention need review before using `rna` publicly. |

**Direct lexical checks (dictionary senses, not invented Sanskrit poetry):**
- [Nyāsa, Monier-Williams/Apte](https://kosha.sanskrit.today/word/sa/nyAsa) — deposit **and** placing aside/renouncing.
- [Pratyarpaṇa, Apte/MW](https://kosha.app/word/sa/%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A4%A4%E0%A5%8D%E0%A4%AF%E0%A4%B0%E0%A5%8D%E0%A4%AA%E0%A4%A3?q=%E0%A4%B0%E0%A4%A5%E0%A5%8D%E0%A4%AF%E0%A4%BE%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A4%B8%E0%A4%B0%E0%A5%8D%E0%A4%AA%E0%A4%A3%E0%A5%87&scope=kosha) — returning/restoring.
- [Kośa, Apte](https://kosha.sanskrit.today/word/sa/%E0%A4%95%E0%A5%8B%E0%A4%B6%E0%A4%83) — container, sheath, treasury.
- [Saṃskāra, MW excerpt](https://dictionary.buddhistdoor.net/details/samskara/) — forming/refining and mental impressions, separate senses.
- [Ṛṇa, MW](https://www.sanskritdictionary.in/shabdkosh?search=%E0%A4%8B%E0%A4%A3) — debt, obligation, negative quantity.

## WS2 — a single word for releasing what is held

**YES: `mocana` (मोचनम्, *mocana*), noun for loosening, freeing, releasing.** More direct than `pratyarpana` when the operation means *cease holding a resource* rather than *return a borrowed item*. Another valid, slightly longer option is `vimocana` (विमोचन), 'unloosing, unharnessing, releasing'. For an actual Sutram built-in called as a function, `mocana(pointer, length)` would mean 'release this mapping' **only by an explicitly written API contract** (Linux `munmap` requires mapped address and length; Windows needs allocation-base information for `VirtualFree`). The noun does not make dangling pointers safe. [Mocana, MW](https://learnsanskrit.ru/lexeme/6a9a617319804823b03cf6ae9cba066e.html), [Vimocana, Apte/MW](https://akshara.ru/kosha/w/vimocana).

The 'zero-cost' sense is **different**. `niḥśulka` (निःशुल्क) means *free of a fee/charge*, not released-from-memory and **not** literally zero CPU cycles or zero page costs. [Kosha 'free' terminology](https://kosha.sanskrit.today/word/en/free). Thus two separate technical senses can be named without ambiguity, but **the existence of distinct words does not make deallocation zero-cost**. `tyāga` (त्याग) is also real 'renouncing/giving up', but can imply abandonment, which is precisely what a leaking pointer does — do not adopt as the freeing API. [Tyāga dictionary](https://kosha.sanskrit.today/word/sa/%E0%A4%A4%E0%A5%8D%E0%A4%AF%E0%A4%BE%E0%A4%97%E0%A4%83).

**Requested answer:** choose **`mocana`** for a future release operation, subject to API/compatibility tests. `pratyarpana` remains a correct word for *returning* but is less technically exact.

## WS3 — the region/container word

**Prefer `kshetra` (क्षेत्र, *kṣetra*) provisionally**: dictionary-attested *field, place, region, area, bounded plot/portion of space*. The word describes the spatial/scope dimension of a region without colliding with existing collection `kosh`. [Kṣetra, MW/Apte](https://kosha.sanskrit.today/word/sa/%E0%A4%95%E0%A5%8D%E0%A4%B7%E0%A5%87%E0%A4%A4%E0%A5%8D%E0%A4%B0).

Second choice: **`koshtha` (कोष्ठ)**, a room/compartment/enclosed space; more *container* than *range*, but already used as a component of `nighantu_koshtha_likh` (map-slot function) and could misleadingly mean a single cell. [Koṣṭha dictionary](https://kosha.sanskrit.today/word/sa/%E0%A4%95%E0%A5%8B%E0%A4%B7%E0%A5%8D%E0%A4%A0). `patra` means vessel but is already a file module in Sutram; `kalasha` is a particular pot/vessel and more decorative than exact for a memory region. **Do not invent 'a Sanskrit word that intrinsically means all allocations get bulk-freed together'**; that is a programming policy. A name must be paired with an explicit rule: allocation into `kshetra`, lifetime boundary, release operation, and escape guarantees.

**Important collision distinction:** `kosa`/कोश versus existing `kosh`/कोश is a *concept and Devanagari identity collision*, even if the literal Latin tokens differ. `kshetra` is not wholly novel to compiler prose: existing diagnostic strings already use `kshetra` in the sense of *struct field*. That is a **semantic overload risk** (same 'field' sense), not currently an identical public reserved keyword, and requires user-facing naming review.

## WS4 — `samskara` specifically

**REJECT for 'residue of reused memory'.** Traditional latent/mental impressions are not bytes remaining after a deallocation. The alternative lexical sense of refinement, ritual preparation or purification might even suggest the memory has been zeroed when it has not. If reused memory is dirty, say so technically: *uninitialized contents*, *stale bytes*, *previously written bytes*; none warrants promoting an aesthetically pleasing philosophical noun into v1 syntax. Existing `mmap` anonymous memory starts zeroed, but arena reuse can expose prior bytes unless explicitly cleared. The zeroing choice must be in the machine-code contract, **not** inferred from `saṃskāra`.

## Minimal owner-facing decision table

| Proposed API concept | Recommended public word | Status |
|---|---|---|
| Current raw allocator `nirmmita` | **KEEP `nirmmita`** | Existing accepted public builtin; no migration mandated |
| Optional deposit/entrust analogy | `nyasa` | Valid word, but **not recommended as a second allocator** until semantics differ meaningfully |
| Release individual mapping/resource | **`mocana`** | Strong lexical candidate; implementation and alias/compatibility still unapproved |
| Region/grouped lifetime | **`kshetra`** | Strong region noun; note compiler already uses *kshetra* for struct fields in diagnostics |
| `kosa` for region | **REJECT** | Same कोश concept as existing `kosh` collection |
| `samskara` for stale RAM | **REJECT** | Mental/ritual sense misapplied |
| `rna` for allocation obligations | **KEEP ONLY AS METAPHOR, not keyword** | Debt is genuine, but no safety semantics follow |

## Measured versus inferred, and compatibility

- **Source-grounded:** current `nirmmita` uses `mmap` on Linux / `VirtualAlloc` on Windows (Round 131 trace); `kosh` is an existing Sanskrit compiler keyword (`src/sutram_compiler.asm:504,520,718,735`); `lang/sanskrit.lang:61-62` already uses `कोश...` for collection operations.
- **Dictionary-grounded:** each noun's ordinary semantics, including ambiguous secondary senses, from the links above.
- **Interpretive design judgment:** why a lexical metaphor is or is not an honest API name. No dictionary claims that words enforce escape checks, reset lifetime, or deallocation.
- **NOT RUN - no toolchain:** new compiler keywords, UTF-8 lexer tests, source or API migration, runtime release correctness, Windows, guard or performance.
- **NOT APPLIED:** no `src/`, `lib/`, `docs/`, `tests/`, `tools/`, `lang/`, other-language packs, or `Windows-to-Sarvam/` changes. Only handoff text under `ChatGPT-to-Sarvam/` delivered.

**R132 completed. R133 remains separately issued and is not worked until the next manual CHECK FOLDER.**
