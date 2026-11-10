# ROUND-229 — Refuse unsupported code characters at their source position

10 November 2026. Static review of main **27bed64a66371e7e526a6f17181a017d6193f2c8**.
**Compiler, suite and runtime checks: NOT RUN — read-side role, no toolchain used.**
A separate Python byte-routing audit read committed blobs; it did not execute the compiler, test generators or gates.

## Decision

**Refuse, at the offending character.** Do not warn and continue by deleting source text. A warning is appropriate for a renamed builtin with defined equivalent meaning; an unsupported operator, quote or invisible character has no such meaning.

No accepted example dependency on the skip path was found in the 331 main examples. Eight deliberately malformed crash fixtures contain raw skip candidates. Preserve their original bytes and manifests; earlier, better refusal is compatible with their documented contract.

## The complete skip class

This is a byte lexer, not a Unicode-token lexer. The following is the complete classification at the main lexer's code-dispatch point, outside ASCII-quoted strings and recognized comments, **after import expansion**:

| Class | Bytes / characters | Where encountered |
|---|---|---|
| Printable ASCII | 24 dollar sign; 27 apostrophe; 40 at sign; 5C backslash; 60 grave accent/backtick; 7E tilde (hexadecimal byte values) | All six are ordinary keyboard characters; currency, quoted prose, email/import-like syntax, paths, Markdown and proposed operators |
| C0 controls | 00–08, 0B–0C, 0E–1F | NUL, pasted/binary corruption; vertical tab and form feed are not recognized whitespace |
| DEL | 7F | Control/delete byte, usually pasted or generated rather than typed as visible text |
| High bytes | 80–DF and E1–FF | Unsupported UTF-8 scalars, or malformed byte sequences when considering the bare lexer |

Byte E0 is the exception among high bytes. A valid E0 A0–BF 80–BF sequence represents U+0800–U+0FFF and follows the Indic identifier/digit/danda logic. A malformed E0 sequence takes E_UTF8, not the skip branch.

For **valid UTF-8**, all non-ASCII scalars outside U+0800–U+0FFF have their bytes skipped by this lexer. That includes accented Latin, Greek, Arabic, CJK and emoji; this is broader than the short punctuation list. This is not a proposal to reject all non-ASCII source: preserve the supported scripts and explicitly define any future identifier extension.

There is an important pipeline distinction: the standard build uses the R68 entry, which calls **r68_prelex_validate before lex**. It rejects malformed UTF-8 in code. Thus the raw high-byte class above is not a claim that every malformed sequence reaches the shipped lexer's default branch. Valid but unsupported Unicode passes UTF-8 validation and is still skipped. Strings/comments intentionally retain byte semantics in that validator.

At-sign is legitimate in an import such as `yoj module@alias`: expand_imports consumes it before lex. It is **not** a general main-lexer operator. Put the new refusal in the lexer's existing fallback, not in a context-free filter over raw input.

## The requested characters

The “today” column describes token routing inferred from source, not executions performed here. Whether a whole program compiles depends on the surrounding tokens. Skipping does not reliably concatenate adjacent words: an identifier already emitted before an unsupported byte stays a separate token.

| Character | Normal use / entry | Today outside ASCII strings/comments |
|---|---|---|
| ASCII apostrophe U+0027 | Keyboard quote | Skipped; apostrophes around a number can disappear without making a character literal |
| Curly single quotes U+2018/U+2019 | Word processors and pasted text | All bytes skipped; enclosed text is parsed as code |
| Curly double quotes U+201C/U+201D | Word processors and pasted text | All bytes skipped; they do not start/end a string |
| En/em dash U+2013/U+2014 | Pasted punctuation | Skipped, not subtraction or negation |
| NBSP U+00A0 | Web/document spacing | Both bytes skipped; it can act like an accidental token separator |
| ZWNJ/ZWJ U+200C/U+200D | Indic input methods and pasted text | All bytes skipped; can split an identifier into separate tokens |
| Single/double danda U+0964/U+0965 | Indic punctuation/input | Recognized and emitted as semicolon delimiters; not skipped |
| Devanagari digits U+0966–U+096F | Indian-language input | Recognized as decimal digits at numeric-token positions; not skipped |
| Other Devanagari signs in U+0800–U+0FFF | Script marks/punctuation | Generally consumed as identifier bytes unless handled specially; not the unknown-byte fallback |
| Rupee sign U+20B9 | Indian keyboard layout or pasted currency | All bytes skipped |
| Copyright, registered and degree U+00A9/U+00AE/U+00B0 | Symbols/paste | Both bytes of each are skipped |
| Multiplication/division U+00D7/U+00F7 | Mathematical text/paste | Skipped; not multiplication or division |
| Tilde/backtick | Ordinary keyboard; Markdown/proposed syntax | Skipped |
| Dollar/backslash outside a string | Ordinary keyboard; currency/path text | Skipped |
| U+FEFF / Unicode spaces outside the supported range | BOM or pasted formatting | Skipped as unsupported UTF-8; do not infer a formal whitespace policy from this accident |

Examples of the risk, **source-derived predictions, NOT RUN**: a stray tilde before a valid statement can vanish; `likha(“7”)` can become a numeric print rather than a string print; removing a Unicode minus before a number can change its sign; a Unicode multiplication mark between numbers can leave an invalid expression and blame a later token. No one universal “compile” or “fail” outcome can be assigned to a character independently of context.

## Corpus check and actual impact

Read all **3,826 tracked .sm/.smlib blobs** at the reviewed commit:
361 under examples (including the **331 top-level suite examples**), 691 under tests, 24 under lib, eight benchmarks, and 2,742 contributor evidence sources.

The model follows the main lexer's whitespace, comments, string escapes, identifiers, native digits, numeric literals and operators. It reports raw fallback candidates, not parser acceptance.

- **34 files / 57 byte candidates** in raw sources.
- **26 files / 48 candidates** are at-signs exclusively on import directives. They are handled before lex, or belong to intentionally invalid import cases. They are not evidence that silent skipping is needed.
- **Eight files / nine candidates** remain, all under `tests/negative/r17/r15-original/`.
- No remaining candidates in examples, library sources or the other tracked Sutram sources.

The remaining fixture locations use physical byte columns:

| Fixture basename | Line:byte-column | Hex byte |
|---|---|---|
| mutation-15-12832.sm | 1:37 | 00 |
| mutation-15-25786.sm | 120:14 | 0F |
| mutation-15-26963.sm | 1:31 | 00 |
| mutation-15-27522.sm | 10:5 and 10:7 | 1C and 24 |
| mutation-15-40049.sm | 30:13 | 1E |
| mutation-15-45236.sm | 11:14 | 1E |
| mutation-15-47726.sm | 105:16 | 00 |
| mutation-15-9720.sm | 2:16 | 19 |

These are **raw lexical candidates**; earlier import/validation/parser failures may already stop a particular file. `tools/crash_corpus.py` requires exit 1, a diagnostic beginning with “Sutram truti,” and no output. It does not require the same later diagnostic. Do not “clean up” these fixtures.

Also inspected candidates from constant strings in all 89 Python files under tests. The 55 candidate literals were documentation, labels or patterns, not evidence of accepted Sutram using the fallback. This does not instantiate dynamically constructed test inputs. The R66/R68 byte-helper tests also intentionally supply malformed bytes directly to helpers; changing lex's fallback must not alter those helpers or string/comment byte semantics.

Evidence and the reproducible raw scanner are adjacent:
- `ROUND-229-LEXER-STATIC-EVIDENCE.json`
- `ROUND-229-LEXER-STATIC-SCAN.py`

**Conclusion:** no valid-example break found; malformed inputs may fail earlier. A future compiler run is still needed to establish the exact suite/guard result. This static audit is not a replacement for that run.

## Implementation contract and cost

Replace the existing default skip with a diagnostic using the current source pointer, a stable error code, line/column and original imported-file mapping. For a valid scalar, show its Unicode code point and readable representation; render controls as escaped codes. Never print a raw terminal-control byte as the “character.” Suggest a replacement only for an unambiguous case; do not silently convert typography into syntax.

Keep all accepted branches and output emission unchanged. No extra comparison per accepted character is required just to change the fallback: the dispatch already reaches that point only when nothing matched. Scalar decoding/diagnostic formatting can run on the error path. This adds **no instructions or runtime overhead to generated Sutram programs**. Any proposal for an additional whole-source validation pass has a separate compile-time cost and is unnecessary for this particular fix.

Do not treat U+00A0 or joiners as whitespace by accident. If wanted, specify and test their meaning separately. Supporting joiners in identifiers is a script/identifier policy, not the unknown-character fix.

Acceptance should include the six printable ASCII characters, controls, each requested Unicode category, supported digits/danda, imports containing at-sign, comments/strings, imported-file locations, malformed UTF-8 under the normal build entry, and unsupported characters next to identifiers and numbers. Require nonzero exit and no emitted artifact for refusal. Preserve successful-program bytes; explain any changed refusal messages. **All such compiler checks remain NOT RUN here.**
