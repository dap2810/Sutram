# Sutram Round 128 — NIVARTANAM documentation and exact-line audit

**Assigned:** [`Sarvam-to-ChatGPT/ROUND-128.md`](../Sarvam-to-ChatGPT/ROUND-128.md), blob `c681482f9f0a1a19e8002e0cc294e69790c59cfe`.
**Pinned starting `main`:** `b425a9f303013da37b5d11c2fe8ebe103072c792`; user decision is canonical `nivartanam` / `निवर्तनम्`, legacy `prati` retained. Only the R128 assignment was processed; issued R127 remains without a ChatGPT handoff.

## Critical status: owner-approved is not yet compiler-implemented at pinned head

**STATIC CHECK PASS:** the 27 specified UTF-8 bytes `E0 A4 A8 E0 A4 BF E0 A4 B5 E0 A4 B0 E0 A5 8D E0 A4 A4 E0 A4 A8 E0 A4 AE E0 A5 8D` decode to exactly **निवर्तनम्**; Python byte decoding measured **27 bytes**. Dictionary derivation **नि + √वृत्** produces `nivartana` as the neuter noun, `nivartanam` in the quoted form.

**AT THIS PIN:** `src/sutram_compiler.asm` blob `08ce26082060f2c1fe0fc9ae7584691877670b5f` has **zero `nivartanam` occurrences**. Current keyword is `kw_pratiyati db "prati", 0` at line 689; Devanagari compiler spelling at line 735 is `प्रति`. `lang/sanskrit.lang` blob `be62e4a2a529da5f0a62200d29c6f94bd3151853` line 18 is `प्रति prati`, not `निवर्तनम्`. Canonical migration is **NOT VERIFIED as implemented on this pinned SHA**. Therefore suggested new example is *expected after migration*, not compiled by ChatGPT. The brief's "all goldens byte-identical / 0 DIFFER" remains an acceptance criterion, **not a verified consequence merely because the keyword itself is not printed**.

## WS1 — Proposed exact reference entry

The first `docs/LANGUAGE-REFERENCE.md` keyword row currently reads:

```text
| `prati` | return |
```

Replace it **only after the canonical parser/pack migration has passed**:

```text
| `nivartanam` (निवर्तनम्; legacy alias: `prati`) | return / returning / turning back (नि + √वृत्) |
```

The original `prati` is accepted as an alias and continues to compile. Add the following explanatory block immediately **BEFORE** the unique heading `## 3. Operators and precedence`:

### Return keyword — `nivartanam` (निवर्तनम्)

**Approved canonical spelling (implementation pending exact-head verification):** `nivartanam` (निवर्तनम्). The neuter noun `nivartanam` means **returning / turning back**, derived from prefix `ni-` plus root `√vṛt` (to turn).

`prati` remains a **legacy alias**. It was a preposition/prefix meaning toward/back, whereas `nivartanam` names the return operation as a noun; the longer form is a precision improvement, not a claim that Sutram source is a fully inflected Sanskrit sentence.

After the canonical keyword and Devanagari mapping have been integrated and verified, this minimal program demonstrates the intended use:

```sutram
prakriya yog(a, b) {
    nivartanam a + b
}
mukhya() {
    likha(yog(2, 3))
}
```

**Expected stdout:** `5` followed by one newline (byte sequence `35 0A` in hexadecimal). **NOT RUN - no toolchain** against the proposed spelling: this is expected from the existing return and `likha` contracts, not an observed new-compiler result.

For a presently supported equivalent, use `prati a + b`; the alias is not scheduled for removal. A canonical name does not itself establish byte identity or compiler acceptance: those are separate native regression gates.


## WS2 — Current-document exact substitutions

**Application contract:** the following is **four-column raw TSV**, using the requested `path | mode | anchor_exact | insert_exact_line` shape; `anchor_exact` is the **entire old line**, and `insert_exact_line` is the **entire new line**. For `PROPOSE_AFTER_CANONICAL_MERGE`, replace a line only when the old line occurs **exactly once** in that file. If source has moved, do not apply obsolete substitutions. For `PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE`, all records share the unique `## 3. Operators and precedence` anchor and **must be inserted in TSV order as one block** (not reversed). `<BLANK>` represents an empty inserted line. `PROPOSE_EXACT_CURRENT` corrects a stale owner-decision/status row without pretending source changed. Frozen-pack columns in the reference's multilingual row must remain byte-for-byte unchanged. **No line below has been applied by ChatGPT to canonical docs.**

```tsv
path	mode	anchor_exact	insert_exact_line
docs/ERROR-CONVENTION.md	PROPOSE_AFTER_CANONICAL_MERGE	        prati 0	        nivartanam 0
docs/ERROR-CONVENTION.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati phal_asti_siddhi(out)	    nivartanam phal_asti_siddhi(out)
docs/reports/KOSH-BUILTINS.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati 0	    nivartanam 0
docs/reports/LAGHU-EXAMPLE.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati 0	    nivartanam 0
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	### Return keyword — `nivartanam` (निवर्तनम्)
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	<BLANK>
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	**Approved canonical spelling (implementation pending exact-head verification):** `nivartanam` (निवर्तनम्). The neuter noun `nivartanam` means **returning / turning back**, derived from prefix `ni-` plus root `√vṛt` (to turn).
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	<BLANK>
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	`prati` remains a **legacy alias**. It was a preposition/prefix meaning toward/back, whereas `nivartanam` names the return operation as a noun; the longer form is a precision improvement, not a claim that Sutram source is a fully inflected Sanskrit sentence.
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	<BLANK>
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	After the canonical keyword and Devanagari mapping have been integrated and verified, this minimal program demonstrates the intended use:
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	<BLANK>
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	```sutram
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	prakriya yog(a, b) {
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	    nivartanam a + b
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	}
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	mukhya() {
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	    likha(yog(2, 3))
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	}
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	```
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	<BLANK>
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	**Expected stdout:** `5` followed by one newline (byte sequence `35 0A` in hexadecimal). **NOT RUN - no toolchain** against the proposed spelling: this is expected from the existing return and `likha` contracts, not an observed new-compiler result.
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	<BLANK>
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	For a presently supported equivalent, use `prati a + b`; the alias is not scheduled for removal. A canonical name does not itself establish byte identity or compiler acceptance: those are separate native regression gates.
docs/LANGUAGE-REFERENCE.md	PROPOSE_INSERT_BEFORE_AFTER_CANONICAL_MERGE	## 3. Operators and precedence	<BLANK>
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	| `prati` | return |	| `nivartanam` (निवर्तनम्; legacy alias: `prati`) | return / returning / turning back (नि + √वृत्) |
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	| `siddhi` | return success: `prati siddhi(v)` (R25; §18) |	| `siddhi` | return success: `nivartanam siddhi(v)` (R25; §18) |
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	| `dosh` | return failure: `prati dosh(code)` (R25; §18) |	| `dosh` | return failure: `nivartanam dosh(code)` (R25; §18) |
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati a + b                 # return	    nivartanam a + b                 # return
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	    yadi (n < 2) { prati n }	    yadi (n < 2) { nivartanam n }
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati fib(n - 1) + fib(n - 2)	    nivartanam fib(n - 1) + fib(n - 2)
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati x	    nivartanam x
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE__FROZEN_COLUMNS_UNCHANGED	| prati | प्रतियाति | ফেরত | પાછા | वापस | ಹಿಂತಿರುಗು | മടങ്ങുക | परत | ଫେରସ | ਵਾਪਸ | திரும்ப | తిరిగి |	| nivartanam | निवर्तनम् | ফেরত | પાછા | वापस | ಹಿಂತಿರುಗು | മടങ്ങുക | परत | ଫେରସ | ਵਾਪਸ | திரும்ப | తిరిగి |
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	prakriya aarohi(a, b) { prati a - b }	prakriya aarohi(a, b) { nivartanam a - b }
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	prakriya Bindu.chal(swa, dx, dy) { swa.x = swa.x + dx  swa.y = swa.y + dy  prati 0 }	prakriya Bindu.chal(swa, dx, dy) { swa.x = swa.x + dx  swa.y = swa.y + dy  nivartanam 0 }
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	        prati dosh(1)            # failure, carrying the code 1	        nivartanam dosh(1)            # failure, carrying the code 1
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati siddhi(a / b)          # success, carrying the value	    nivartanam siddhi(a / b)          # success, carrying the value
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati siddhi(q + 1)	    nivartanam siddhi(q + 1)
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	- **A prakriya with a `prati siddhi(...)` or `prati dosh(...)` is a phal-prakriya.** In one, every `prati` is	- **A prakriya with a `nivartanam siddhi(...)` or `nivartanam dosh(...)` is a phal-prakriya.** In one, every `nivartanam` is
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	  `siddhi` or `dosh` (a plain `prati` is a compile error), and falling off its end is `siddhi(0)`.	  `siddhi` or `dosh` (a plain `nivartanam` is a compile error), and falling off its end is `siddhi(0)`.
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	  program with the code as its exit status (the low 8 bits). `prati dosh(c)` in `mukhya` exits with `c`.	  program with the code as its exit status (the low 8 bits). `nivartanam dosh(c)` in `mukhya` exits with `c`.
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	        prati mool	        nivartanam mool
docs/LANGUAGE-REFERENCE.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati q	    nivartanam q
docs/SPECIFICATION.md	PROPOSE_AFTER_CANONICAL_MERGE	    prati v	    nivartanam v
docs/SPECIFICATION.md	PROPOSE_AFTER_CANONICAL_MERGE	`prakriya` introduces a named function, `prati` returns, `vitti` introduces a	`prakriya` introduces a named function, `nivartanam` returns, `vitti` introduces a
docs/sutram-book-sanskrit.html	PROPOSE_AFTER_CANONICAL_MERGE	<code><span class="k" data-tip="अर्थः: return">prati</span></code>-द्वारा मूल्यं प्रत्यागच्छति:</p>	<code><span class="k" data-tip="अर्थः: return">nivartanam</span></code>-द्वारा मूल्यं प्रत्यागच्छति:</p>
docs/sutram-book-sanskrit.html	PROPOSE_AFTER_CANONICAL_MERGE	    <span class="k" data-tip="अर्थः: return">prati</span> mulya * mulya	    <span class="k" data-tip="अर्थः: return">nivartanam</span> mulya * mulya
docs/sutram-book-sanskrit.html	PROPOSE_AFTER_CANONICAL_MERGE	    <span class="k" data-tip="अर्थः: if">yadi</span> (n &lt; 2) { prati n }	    <span class="k" data-tip="अर्थः: if">yadi</span> (n &lt; 2) { nivartanam n }
docs/sutram-book-sanskrit.html	PROPOSE_AFTER_CANONICAL_MERGE	    prati fib(n - 1) + fib(n - 2)	    nivartanam fib(n - 1) + fib(n - 2)
docs/sutram-book-sanskrit.html	PROPOSE_AFTER_CANONICAL_MERGE	<tr><td><code><span class="k" data-tip="अर्थः: function">prakriya</span> / <span class="k" data-tip="अर्थः: return">prati</span></code></td><td>function / return</td></tr>	<tr><td><code><span class="k" data-tip="अर्थः: function">prakriya</span> / <span class="k" data-tip="अर्थः: return">nivartanam</span></code></td><td>function / return</td></tr>
docs/sutram-book-sanskrit.html	PROPOSE_AFTER_CANONICAL_MERGE	    <span class="kw">prati</span> s / <span class="kw">kosh_len</span>(xs)	    <span class="kw">nivartanam</span> s / <span class="kw">kosh_len</span>(xs)
docs/sutram-vocabulary.html	PROPOSE_AFTER_CANONICAL_MERGE	<tr><td><code>return</code></td><td><code>prati</code></td><td><b>prati</b></td><td>प्रति</td></tr>	<tr><td><code>return</code></td><td><code>nivartanam</code></td><td><b>nivartanam</b></td><td>प्रति</td></tr>
docs/WHATS-LEFT.md	PROPOSE_EXACT_CURRENT	| **F4** | **`prati` stays** - decided | **and `nivartan` was considered and set aside** |	| **F4** | **`nivartanam` (निवर्तनम्) approved as canonical return keyword** | `prati` remains a compatibility alias; compiler and documentation migration must be verified on exact main |
PROJECT-OVERVIEW.md	PROPOSE_AFTER_CANONICAL_MERGE	| `prakriya` | function | `prati` | return |	| `prakriya` | function | `nivartanam` | return |
README.md	PROPOSE_AFTER_CANONICAL_MERGE	| `prakriya` | function | `prati` | return |	| `prakriya` | function | `nivartanam` | return |
```

### Lines deliberately kept, and why

- **docs/LANGUAGE-REFERENCE.md:249 — KEEP_COMPATIBILITY_EXAMPLE.** `three brace-less statements fails with 'vyakaran dosh, pankti 3:5, shabd 'prati''.`
- **docs/SPECIFICATION.md:227 — KEEP_LEGACY_ALIAS.** `'प्र॰ -> prakriya', and 'प॰ -> prati' aliases. These are exact language-pack`

### Historical and frozen documentation register

- **docs/CHANGELOG.md — KEEP_HISTORICAL.** All historical v396/v397/v398 narrative, earlier spellings and test claims remain dated evidence; do NOT replace every prati.
- **docs/reports/LEXER-BOUNDARY-TEST.md — KEEP_HISTORICAL.** Recorded original lexer tests on prati, pratiX and prati_test retain meaning: prati remains accepted legacy alias.
- **docs/rounds/R56-MODULE-GLOBALS.md — KEEP_HISTORICAL.** Round-56 historical fixture example contains prati counter.
- **F7-SCALAR-INDEX-CRASH.md — KEEP_HISTORICAL.** Historical input example prati 1; preserve reproducer.
- **docs/vocabulary/VOCABULARY-TABLE.md — KEEP_HISTORICAL.** Older vocabulary proposal considered prati KEEP and wrong native प्रतियाति; preserve review as provenance, may append dated supersession later.
- **docs/vocabulary/VOCABULARY-SHORT.md — KEEP_HISTORICAL.** Earlier shortening proposal keeps prati; historical proposal rather than current syntax authority.
- **docs/vocabulary/VOCABULARY-DERIVATION.md — KEEP_HISTORICAL.** Historical keyword boundary and vocabulary reports; legacy alias remains accepted.
- **docs/LIBRARY-BOUNDARY.md — KEEP_COMPATIBILITY.** Mentions existing prati syntax in technical description; remains true after alias retained.
- **docs/_newchapter_en.html — DEFER_NON_SANSKRIT_DRAFT.** English-language appendix; don't alter frozen/non-active translation surfaces.
- **docs/sutram-book-english.html — DEFER_NON_SANSKRIT_BOOK.** English edition, do not change during Sanskrit-only development.
- **docs/sutram-book-gujarati.html — DEFER_FROZEN_LANGUAGE.** Frozen Gujarati book and translations.
- **docs/sutram-book-hindi.html — DEFER_FROZEN_LANGUAGE.** Frozen Hindi book and translations.
- **docs/sutram-book-tamil.html — DEFER_FROZEN_LANGUAGE.** Frozen Tamil book and translations.
- **docs/sutram-book-telugu.html — DEFER_FROZEN_LANGUAGE.** Frozen Telugu book and translations.
- **docs/sutram-keyword-words.html — DEFER_FROZEN_MULTILINGUAL.** One large mixed-language keyword table; do not blanket edit or rewrite frozen translations; reconsider Sanskrit-specific regeneration separately.

**Scoping:** I explicitly inspected **all 93 `docs/` Markdown/HTML/text files other than the extremely long `docs/CHANGELOG.md`**, plus **26 root-level or `compiler/` Markdown/text documents**, using the pinned GitHub tree and direct source reads; the changelog is classified as a **whole-file historical record**. Root and compiler historical files beyond the two matching entries did not contain a standalone `prati` token in those formats. This was a **documentation-surface sweep**, not a claim of exhaustive coverage of all 700+ partner handoffs, source archives, generated artifacts, binary resources or `.sm` examples; those may intentionally contain `prati` and must be reviewed by their own owners. Do not change any of them by a global search-and-replace.

## WS3 — Is there a shorter genuine Sanskrit noun?

**YES, as a dictionary fact (not a request to change the owner's settled choice):** **`nivritti` (निवृत्ति; `nivṛtti` in scholarly transliteration)** is an attested feminine noun for **returning / coming back**, and is **8 Latin characters** in `nivritti`, versus `nivartanam`'s **10**. It can also mean cessation, withdrawing or abstaining, so it has greater **stop/withdrawal ambiguity** as a programming `return` term. Apte and Monier-Williams record the returning sense: [Kosha `nivRtti`](https://kosha.sanskrit.today/word/sa/nivRtti). The owner's approved **`nivartanam`** is a real, precise and appropriate noun for turning/returning; see [Apte `nivartana`](https://akshara.ru/kosha/w/nivartana). **RECOMMEND KEEPING `nivartanam` for v1.0**. Record `nivritti` as the requested *future-only* alternative, not as a reopened naming decision. Sanskrit noun `nivṛtti` is not a clipped fragment.

## Verification record

- GitHub READ: `docs/LANGUAGE-REFERENCE.md 86bc60620bde169a2136cd6b1e934323f94d59bb 19 lexical-hit line(s)`
- GitHub READ: `docs/sutram-book-sanskrit.html b181c74f87543df7244624eae592d269d3b62862 6 lexical-hit line(s)`
- GitHub READ: `docs/SPECIFICATION.md 100e7b8e4b6ef919481b223c56f322806a210c98 3 lexical-hit line(s)`
- GitHub READ: `docs/ERROR-CONVENTION.md 06d1b7f73bfb3636cd4104fa5001563ce8556d97 2 lexical-hit line(s)`
- GitHub READ: `docs/reports/KOSH-BUILTINS.md 8062b5bae846c8314113c44f695ec44c18b0aa56 1 lexical-hit line(s)`
- GitHub READ: `docs/reports/LAGHU-EXAMPLE.md 271d7519c0f54675f1be807621f17463f9afd976 1 lexical-hit line(s)`
- GitHub READ: `README.md d711d81fe9cd8fa7aab592546e61302367a67442 1 lexical-hit line(s)`
- GitHub READ: `PROJECT-OVERVIEW.md d84993a3d84adb7c34986f9ed1bdb32843cfacfd 1 lexical-hit line(s)`
- GitHub READ: `docs/sutram-vocabulary.html 94c5d5221e7a6fcaf18502949bba824f62f59f65 1 lexical-hit line(s)`
- GitHub READ: `docs/WHATS-LEFT.md bfea3578c36bf314173b0f2219991f0d43ccf886 1 lexical-hit line(s)`
- **PASS:** byte decoding, source/doc path review, current reference line inventory and historical/frozen classification.
- **NOT APPLIED:** every canonical documentation insertion/rename above; this is a handoff exclusively in `ChatGPT-to-Sarvam/`.
- **NOT RUN - no toolchain:** new-keyword syntax, binary/output equality, regression guard, native compiler/goldens, Linux/Windows acceptance.
- **CANNOT CHECK from pinned source:** the subsequently merged canonical compiler form; refetch latest exact-head before application.
- **Protected areas unchanged:** `src/`, `lib/`, `docs/`, `tests/`, `lang/`, frozen translations, `Windows-to-Sarvam/`, and `backups/`.

**End of Round 128.** Stop until next manual `CHECK FOLDER`.
