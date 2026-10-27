# Sutram ROUND-118 WS1 — precise keyword/identifier boundary contract (Sanskrit v1.0)

**Assignment** `Sarvam-to-ChatGPT/ROUND-118.md` (blob `bb076a71b2377b05aa519287f778328e3b72fc05`); **source pin** `3b1a9e7f5369a7f826cfa9ce07c4d873a40973e6`, compiler **v249**, changelog **v361**. Target **active Sanskrit/Devanagari** plus existing Latin transliterations only; do not change the ten frozen packs. This is a **contract/spec**, not an implementation, native run or proof of Unicode correctness.

## 1. The lexical invariant: a keyword is a WHOLE token

**Boundary predicate**, for a source-byte offset `p` at which a complete keyword spelling `K` matches:

1. `p` is a real token start, not inside an already collected identifier, string, comment, numeric literal or UTF-8 scalar.
2. `q = p + byte_length(K)` must end **on a UTF-8 scalar boundary**.
3. If `q == source_end`, the keyword's right boundary **passes**.
4. Else decode **the full UTF-8 scalar starting at q**, *safely bounded by source_end*. If it is an `IdentifierContinue` code point, **DO NOT recognize K as a keyword prefix**. Continue collecting the entire identifier, or reject the entire invalid identifier; never split `K` + suffix into a keyword and leftover letters.
5. If the next scalar is whitespace, a recognized operator/punctuation delimiter, or a comment opener **at a token boundary**, the right boundary **passes**. The following token/comment is processed separately.
6. After collecting a complete identifier, compare its **ENTIRE spelling**, not a prefix, against the active keyword table, then builtin table, then classify as ordinary identifier. Preserve the exact spelling and source positions. Keyword match is case-sensitive, with no implicit normalization or silent aliases added in this round.

**Equivalent safer algorithm**: `identifier := IdentifierStart IdentifierContinue*` (maximal munch), then exact full-token equality to a loaded keyword or builtin spelling. A prefix-only string-match is never an adequate substitute. Mixed-script continuation is **not** a token boundary.

## 2. What counts as a word character?

For the active Sanskrit source language, recommend a **version-pinned Unicode identifier profile** based on **Unicode UAX #31** (`XID_Start` / `XID_Continue`) with explicitly allowed leading `_`. Minimum acceptance requirements:

- `IdentifierStart`: `A-Z`, `a-z`, underscore, and supported Devanagari Unicode identifier-start **letters**. No initial decimal digit, orphan mark, punctuation, danda, or arbitrary UTF-8 continuation byte.
- `IdentifierContinue`: everything in Start, plus ASCII **0-9**, supported Devanagari **decimal digits**, and relevant combining marks (`Mn`, `Mc`) such as vowel signs, anusvāra/nukta and virāma. Mixed Latin/Devanagari letters and digits remain **one identifier**, e.g. `pratiक`, `वित्तिX`, `प्रतियाति३`.
- `XID_Continue` is a Unicode **code-point property**, not the test `next byte <= 0x7F`, `byte == 0xE0`, or ASCII `[a-zA-Z0-9_]`. Vowel signs and virāma are continuation marks even though they are not ordinary base letters. A general implementation may use UAX31's `XID` properties directly; for a deliberately restricted current-script profile, document that profile and classify unsupported characters as errors rather than pretending they are keyword delimiters.
- UTF-8 decoding must reject invalid continuation sequences, truncated scalars, overlong encodings, surrogate code points and out-of-range scalars. **Never** scan past source_end; **never** let malformed bytes act as valid word boundaries. Distinguish tokenizer errors from syntactic parse errors.
- Unicode has join controls (`U+200C/U+200D`) under special identifier constraints. Do **not** silently allow/disallow them based on byte values; specify an explicit allowed-context policy or report unsupported input. Do not broaden frozen packs or silently normalize identifiers while fixing keyword prefixes.
- **Important script-specific fact:** `lang/sanskrit.lang` maps **`प्रतियाति` → `prati`**, *not* `प्रति` → `prati`. Thus `प्रतियातिक`, `प्रतियातिX`, `प्रतियाति३` are genuine keyword-prefix collision tests. `प्रतिलिपि` is useful as an ordinary Devanagari identifier test but **does not begin with the actual native return keyword**.
- Current abbreviation aliases like `प॰` (`prati`) and `वि॰` (`vitti`) contain punctuation `U+0970` and are **explicit exact alias spellings**, not evidence that arbitrary punctuation belongs to normal identifiers. Test them as special terminal aliases; don't generalize them into unrestricted identifier continuations.

**Unicode reference:** [Unicode Standard Annex #31, Unicode 18.0](https://unicode.org/reports/tr31/) (default `XID_Start`, `XID_Continue`, combining-mark support, optional identifier profiles). Formal language-wide adoption of all Unicode scripts/NFC or NFKC is a separate compatibility decision and **not** implied by this Sanskrit-only task.

## 3. Each delimiter / boundary case

| Following item after exact K | Required lexing |
|---|---|
| **EOF** | K as keyword; no lookahead beyond the source end |
| Space, tab, CR, LF, CRLF | K as keyword, then whitespace skipped; preserve line and byte-offset diagnostics |
| Recognized operator or delimiter such as `+`, `=`, `(`, `)`, `,`, `{`, `}` | K as keyword, then the operator/delimiter; parser separately determines grammatical legality |
| Comment start `#`, `//`, `/*` at token boundary | K as keyword; then a comment, not a literal suffix; comments within strings are not comments |
| Devanagari danda `।` (U+0964) or double danda `॥` (U+0965) | Keyword then statement terminator; both are **not** identifier letters; preserve compiler's existing special handling |
| ASCII letter, digit or underscore | **One ordinary identifier** (e.g. `pratiX`, `prati3`, `prati_test`) |
| Devanagari letter, digit or combining mark | **One ordinary identifier**, including mixed-script continuations (e.g. `pratiक`, `प्रतियातिX`, `प्रतियाति३`) |
| Malformed UTF-8 after keyword bytes | **Lexical error**, not keyword + silently discarded invalid byte |
| Embedded keyword in a longer identifier | Entire name remains ordinary identifier (`xprati`, `vartani_pratilip`); never scan a keyword in the middle |
| Keyword spelling inside string/comment | Literal/comment content; never keyword-token recognition |
| Special alias `प॰` | Exact keyword alias per Sanskrit pack; `॰` is an alias terminator, not a generic identifier letter |

## 4. What CURRENT SOURCE supports versus what remains unproven

**Direct read evidence, current v249:**

- `src/sutram_compiler.asm:6210-6276` collects a full identifier (up to the delimiter), and `:6278-6318` runs `lookup_keyword`, `lookup_builtin`, then emits `TOK_IDENT`.
- `src/sutram_compiler.asm:24058-24116` and `:24118-24176` use exact `strcmp` against keyword/builtin tables, not prefix comparisons.
- `src/sutram_compiler.asm:23969-23990`: **`is_alpha` reads a single byte** and accepts `0xE0` as an Indic scalar start, not a Unicode category/property classifier. `src/r66_indic_lexer.inc` validates selected 3-byte `E0` sequences and handles danda, but that is not general scalar-aware `XID_Continue` checking.
- `src/sutram_compiler.asm:6206-6208` and `:6320+` recognize numeric tokens before general identifiers, including native decimal forms.
- `src/sutram_compiler.asm:6143-6193` handles whitespace, `#`, `//` and `/*...*/` comments; `:6195-6200` special-cases danda.

**Partner-measured, not rerun by ChatGPT:** `docs/LEXER-BOUNDARY-TEST.md` reports four compiled+executed Latin-script tests on v249: `prati_test` printed 6, `mukhyata` 7, `pratiX` 3, and a **variable** `vartani_pratilip` printed 9. This is **NOT** a native test of a function *definition plus a call* `vartani_pratilip(x)`. `Sarvam-to-Muse/ROUND-43.md` asks that separately.

**NOT RUN / unresolved:** Exact cross-script and combining-mark behaviors under the full compiler; Devanagari keyword plus native letter, Latin plus Devanagari letter, Devanagari plus Latin; alias punctuation in ambiguous adjacency; invalid-scalar failure behavior in those exact contexts; canonical normalization equivalence; any performance/golden effects of a future change. These are measurable by the explicit TSV corpus.

## 5. Acceptance contract for Claude/Muse and owner

1. Pin exact main SHA and `--lang sanskrit`; get a **BEFORE** baseline with verbatim compiler output, exit code, and runtime output for each runnable test. The TSV states **normative expected behavior**, not claimed current behavior.
2. If the current compiler already passes every scoped case, **NO CODE CHANGE** is required; add the permanent regression cases. Never rewrite a functioning lexer just because a speculative problem was proposed.
3. If a scoped case fails, write an isolated minimal fix with exact Unicode scalar and mixed-script boundary validation, no changes to language packs, source spellings, comments or runtime semantics outside the target.
4. Retest the TSV, UTF-8 rejection cases, guard, regression suite, crash corpus and `fuzz_robust` on the exact change. Report deliberate changed fixtures separately from byte-identical existing programs and from Windows NOT-RUN.
5. Unicode tables must be **version-pinned and audited** or use a clearly documented subset; a coarse `byte >= 0x80` shortcut is not the promised behavior.

**Status:** PASS — source-reviewed boundary specification and acceptance criteria. **NOT RUN - no toolchain** — native compiler, Sanskrit pack end-to-end, Windows, guard, fuzzing. Frozen packs and protected paths unchanged.
