# Sutram ROUND-114 WS3 — Sanskrit-language-design draft: disciplined analogies

**Pinned input:** `docs/reports/SANSKRIT-FOR-LANGUAGE-DESIGN.md`, Git blob `76fa06d09438f8a3eb33b300d85a417efe62d3b6`, pinned main `df4b5237b8962adda7f0693f1fc5bb1408567798`. **Scope:** source-grounded software-design reasoning; limited independent linguistic cross-check against public scholarly/reference material, **not** specialist certification of Sanskrit. Keep document DRAFT.

## The three requested verdicts

### 1. Utsarga / apavāda — DEFENSIBLE AS AN ANALOGY, not universal implementation

The general rule (utsarga) vs exception/specific rule (apavāda) distinction is genuine. A general prescription can remain available outside the exception's domain; within the exception domain its application is barred. **This does not guarantee the draft's description of priority in every interaction or all rule-conflict cases**: Pāṇinian ordering, domain specificity and metarules can matter. The language-design analogy to *default fallback and more-specific dispatch* is helpful as a proposal.

**Draft overclaim:** "one mechanism covers error handling, dispatch and defaults" is untested architecture, not a property. Error handling concerns propagation, observability and recovery, not just selection precedence. `abhava` and `anya` (negation/else) are not meaningful implementations of utsarga/apavāda. Minimum correction: "Inspired by the general-rule/exception pattern, a proposed precedence mechanism might serve typed dispatch/defaults; error handling needs a separate, explicitly specified result/exception contract."

References: https://sanskritdictionary.com/?q=apav%C4%81da (apavāda setting aside a general rule); https://sreenivasaraos.com/2020/05/24/yaska-and-panini-part-two/ (exception bars general rule within its scope). Specialist must approve precise grammatical terminology.

### 2. Kāraka — DEFENSIBLE SIX-ROLE SEMANTIC MODEL; FFI CONCLUSION A STRETCH

The six well-attested Pāṇinian kāraka relations are `kartṛ`, `karman`, `karaṇa`, `sampradāna`, `apādāna`, `adhikaraṇa`. The draft's rough labels agent, object, instrument, beneficiary/recipient, source, locus match reference treatments. Their actual status is **syntactic-semantic relations defined around an action**, not literally an unrestricted set of generic C parameter tags. Their mapping to case endings is not strictly one-to-one.

**Draft overclaim:** "named arguments with semantic roles, and argument order made irrelevant" does not follow automatically. A C ABI still uses positional register/stack assignments and precise types regardless of source-level named argument syntax. Designators like destination/source/length are valuable but not exhaustive six kārakas; they could be modeled as explicit **FFI contracts**, with ordinal ABI marshalling retained. Tagging arguments by role **cannot prove** pointer extent/provenance, lifetime, alignment, signedness, float layout, cross-platform calling convention or foreign binary compatibility. Smallest correction: "Kāraka-inspired semantic annotations could improve clarity and static diagnostics about argument *intent*, with compiler-generated positional lowering, while ABI types and memory safety remain separately checked."

References: https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART000995613 (Choi 2006, Pāṇini's Kāraka Theory); https://pmc.ncbi.nlm.nih.gov/articles/PMC6954025/ (six relations in computational analysis). Sanskritist still needed to certify glosses.

### 3. Bahuvrīhi — TRUE LINGUISTIC CATEGORY, WRONG AS AN EQUIVALENCE TO STRUCTURAL TYPING

Bahuvrīhi is broadly a possessive, *exocentric* compound: it may denote a referent characterized by something expressed in the compound rather than the compound's own syntactic head. This part is defensible.

**False leap:** a bahuvrīhi compound does not define a software object's members, method types, assignability, member-access checks or subtyping. "A thing described by a property" is not equivalent to structural type compatibility. The current statement "bahuvrīhi is the word-formation pattern for exactly that idea" is therefore **not defensible** as a linguistic or programming-language assertion. Minimum correction: "A proposed structural-typing syntax could borrow a memorable **metaphor** from bahuvrīhi's possessive characterization; it is not derived mechanically from Sanskrit morphology." Keep traits and structural typing as UNBUILT.

References: https://taalportaal.org/taalportaal/topic/pid/topic-13998813295820079 (linguistic exocentric/possessive); https://sanskritdictionary.com/?q=bahuvr%C4%ABhi (definition). A Sanskritist should review exocentric compound subtleties before making normative claims.

## Additional source-grounded / independently corroborated errors (not to ignore)

- **§2.4 wrong pratyāhāra example:** `aṇ` is **not the unambiguous term for all vowels**. The normal pratyāhāra for all vowels is **`ac`**; `aṇ` can denote a smaller set and has contextual ambiguity because marker `ṇ` appears twice in the Śivasūtras. The draft says `aṇ is all vowels`; change to **`ac`**, while preserving `hal` for consonants. Evidence: https://learnsanskrit.org/panini/shivasutras/ and https://www.premabase.com/siddhanta-kaumudi/p04/textbook/index.html.
- **§4 false project module statement:** the draft says the project "already has a `meru` module." Live library contains **`lib/chandas.smlib`**, with callable functions `meru` and `meru_mala`; it does **not** have a `lib/meru.smlib` module. Correction: "the `chandas` module implements `meru`/Meru-prastāra-related calculations." Historical Pingala date/equivalence should be reviewed by qualified historians of mathematics, not assumed.
- **§1 false dichotomy:** heading "it is a formal grammar, not a natural language" is misleading. **Sanskrit is a natural language**, while **Pāṇini's formalized description of Sanskrit** is an extraordinarily systematic grammatical metalanguage. Change heading accordingly.
- **§5 and §8 priority/uniqueness marketing:** "Pāṇini got there first," "only language," "all other FFIs require C runtime", "no English anywhere" are not proven by source review and demand independent comparisons. Keep as historical perspective or qualified hypotheses, not absolute facts. This is beyond the three primary analogies.
- A sound-inspired `yoj` composition rule must specify actual parser/module namespace semantics; physical sandhi analogy alone does not resolve a module system.

## Owner/partner next step

1. Sarvam revise **only draft prose**, retain implemented language syntax unchanged; distinguish `Sanskrit linguistic property`, `design metaphor`, `implementable formal spec`, `implemented/tested feature`.
2. A Sanskritist approves morphology, terminology, pratyāhāra and kâraka scope; domain expert reviews software-side ABI and type-system feasibility.
3. If owner wants implementation, write tiny falsifiable semantics+regression fixtures first and keep the existing guard absolute.

**Verdicts:** Utsarga/apavāda = **defensible but qualified**; kāraka = **defensible as six roles, stretched as order-free FFI guarantee**; bahuvrīhi = **valid possessive grammar, incorrect as structural typing equivalence**. Additional two concrete factual corrections above. **Native compiler tests NOT RUN - no toolchain; Sanskrit specialist signoff NOT RUN.**
