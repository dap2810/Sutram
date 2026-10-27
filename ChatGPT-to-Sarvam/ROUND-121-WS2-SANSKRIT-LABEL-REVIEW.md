# Sutram ROUND-121 WS2 — Sanskrit terminology check for debugger labels

**Read pin:** `main 7ef38a2fbfec33ba9d78dd62c5f5ae55ff3cce8c`, compiler v252; `src/r45_debug.inc` currently emits the **ASCII** prefix `[shodhan] pankti N`. `lang/sanskrit.lang` contains `वित्ति vitti` as the native keyword for variable declaration. This report distinguishes *dictionary meaning* from *Sutram's established technical terminology*. It is NOT a Sanskritist-certified new lexicon.

## The debugger's name: recommend KEEP the established `shodhan` tag

**`śodhana` / शोधनम्** has dictionary senses **cleaning, correcting, improving**, and also **sifting, investigation and examination**. As a technical metaphor for exposing wrong state so the author can correct it, it is a **defensible, appropriate** debugger name. The underlying project prints `[shodhan]`, a Latin transliterated **stem/technical label**; if a Sanskrit-script UI title is wanted, `शोधनम्` is the more complete nominal form. The ASCII tag need not be altered: existing tests, documentation and program-output parsers may key on it. No blanket claim that `shodhan` is the one uniquely correct modern computing term.

**Alternative if the team prioritizes "finding a bug" over "correcting/purifying":** **दोषान्वेषणम्** (`doṣānveṣaṇam`, "search/investigation of faults") is a *proposed transparent compound*, motivated by lexically attested `anveṣaṇa` meaning searching/investigating and `doṣa` as defect. It is narrower but longer and would be **new terminology**, not a reason to rename the current public trace tag mid-release. `परीक्षणम्` (`parīkṣaṇam`, examination/testing) is also serviceable but can conflate running tests with tracing a program. **Decision:** KEEP `shodhan` now; show `शोधनम्` optionally in teaching prose. A qualified Sanskritist may review compound inflection before any formal change.

## Labels

| Interface concept | Current/proposed label | Linguistic evidence and recommended policy |
|---|---|---|
| **line of source** | `pankti`, **पङ्क्तिः** | **Appropriate.** `paṅkti` means line, row, sequence; the Apte/Monier-Williams entries support the "line" reading. The compiler's `pankti` in error messages is consistent. It is also used for arrays in internal historical/builtin identifiers, but line number context resolves the ambiguity. |
| **variable** | `vitti`, **वित्ति** | **Keep as a Sutram language-design convention, not as a lexically certified translation of "variable".** The Sanskrit `vitti` is generally knowledge/judgment/gain, not a default mathematical term for a mutable program variable. However `वित्ति vitti` is the existing project declaration keyword, so reusing it in beginner diagnostics is less confusing than abruptly introducing a second term. |
| **value** | **मूल्यम्** (`mūlyam`) | Understandable proposed label for a value; its exact modern-computing sense and declension should be reviewed before treating it as canonical. No runtime debugger label is emitted yet for this field. |
| **step** | **क्रमः** (`kramaḥ`) | Reasonable word for order/sequence/step, but **an interactive step command does not currently exist**; use only when such a feature is implemented, not in docs for v252's automatic trace. |
| **continue** | **अग्रे** (`agre`) | Conveys "onward/ahead", but it is NOT an interactive debugger command in v252. If a resume command is developed later, have a Sanskritist select the proper UI command/form. |

## Why this does not justify modifying existing code

The existing debugger is a **continuous runtime trace** inserted at compile time. It uses `[shodhan] pankti N` on stdout. It is not a paused program controlled by user-supplied Sanskrit "step"/"continue" commands. Do not rename `[shodhan]`, `pankti` or `vitti` during Round 121 just to make textbook prose sound more classical: implementation behavior and test output remain the primary facts.

## Lexical sources / limitations

- Monier-Williams `śodhana`: https://akshara.ru/kosha/w/SoDana (correction, purification, sifting, examination/investigation) and https://sarasvati2001.blogspot.com/2010/10/mw1135.html (dictionary excerpt).
- Monier-Williams `anveṣaṇa`: https://sanskrit.uohyd.ac.in/SKT/MW/10.html (seeking, searching, investigating).
- Apte `paṅktiḥ`: https://sanskritdictionary.com/?iencoding=sl&lang=&q=pa%E1%B9%85kti (line/row/range/series).
- Apte `vittiḥ`: https://sanskritdictionary.com/?q=vit (knowledge/judgment/gain).
- Actual Sutram terminology and semantics: `src/r45_debug.inc`, `lang/sanskrit.lang`, `docs/CHANGELOG.md` v370. Dictionary support is **external lexical evidence**; actual labels and display output are **source-derived**. Proposed compound/interface inflections require qualified Sanskritist approval.

**PASS — dictionary-backed terminology review and explicit project-convention distinction. NOT RUN - no toolchain** for native code/Windows; no compiler or pack changes. No expert grammatical certification claimed.
