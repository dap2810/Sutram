# R66 — Devanagari and Gujarati lexical devices

Source basis: accepted compiler Git blob `caee73735372cfd92f47ea18c9c1c6f8b70e9599`,
main `9921cbf175b2fb7983e45305fdec963380532452`, and both existing language packs.
These are source implementations. The full staged compiler still needs Sarvam's
native acceptance; helper instruction tests alone do not establish integration.

## Script-specific versus shared

| Device | Devanagari | Gujarati | Shared behavior |
|---|---|---|---|
| Decimal zero..nine | U+0966..096F, `०१२३४५६७८९` | U+0AE6..0AEF, `૦૧૨૩૪૫૬૭૮૯` | Values 0..9; 3-byte UTF-8 units |
| UTF-8 digit range | `E0 A5 A6..AF` | `E0 AB A6..AF` | Check all bytes and exclusive end |
| Abbreviation mark | U+0970 `॰` | U+0AF0 `૰` | Part of explicitly listed aliases, not arbitrary prefix expansion |
| Danda/double danda | U+0964/U+0965 `।` / `॥` | Same shared codepoints | Existing statement terminators equivalent to `;` |
| Decimal point | ASCII `.` | ASCII `.` | Only starts fraction when followed by a recognized decimal digit |
| Keywords | Existing `lang/sanskrit.lang` | Existing `lang/gujarati.lang` | Existing Latin keyword/builtin IDs, not translated compiler semantics |

The Unicode codepoint identities above are verified against the Unicode nameslists:
- https://www.unicode.org/Public/UCD/latest/charts/nameslist/0900/
- https://www.unicode.org/Public/UCD/latest/charts/nameslist/0a80/

**The language interpretation of abbreviation marks is a proposed R66 design
choice**, not a Unicode grammar rule supplied by Sarvam. The brief names the
signs but does not define abbreviation syntax. This proposal makes a small,
unambiguous alias set instead of treating abbreviations as terminators or
silently interpreting every prefix of a keyword. Sarvam should approve it.

## Pack additions and preservation

Sanskrit preserves all 49 accepted entries and adds four exact abbreviations:
`वि॰ → vitti`, `लि॰ → likha`, `प्र॰ → prakriya`, `प॰ → pratiyati`, plus
`कोशप्रवेश → kosh_enqueue`. Total: **54 entries**. The other kosh primitives,
core constructs named in the brief and the corrected `sankhya` already exist.
No fictitious `niryat` export syntax is added: the inspected accepted keyword
IDs do not define that construct.

Gujarati preserves all 30 previous entries, adds `સંખ્યા → sankhya`, ten
existing array/kosh builtin aliases, and four abbreviations:
`ચ૰ → vitti`, `લ૰ → likha`, `ફ૰ → prakriya`, `પા૰ → pratiyati`.
Total: **45 entries**. Their RHS spellings select existing compiler operations.
Both packs stay below the current 96-keyword / 32-builtin / 64-byte-word limits.
New aliases reserve those exact spellings only when the relevant pack is active.

## Decimal behavior

`src/r66_indic_lexer.inc` supplies bounded compiler-host NASM functions.
`tools/r66_prepare_review.py` wires them into the accepted lexer, with eight
exact replacement anchors and a required input Git blob. Run the tool to
produce a separate source file, then build from the repository root.

Digits are recognized BEFORE the general E0 identifier path at token start.
Inside an already-started identifier, `n२` or `ન૧` stays an identifier.
A token beginning with a native digit becomes a number; this intentionally
changes any previous interpretation of a numeral-only identifier.

Integers and fractional digits share the value/width decoder. ASCII and native
digits can mix: `१२3૪` denotes 1234. The helper preserves RCX and R8-R11, which
hold the fraction precision count and lexer accumulators. Integer wrap and the
15-digit fraction precision policy remain the accepted behavior. This does not
change integer-overflow policy or enable the R65 arithmetic-trap build mode.

The ASCII hexadecimal `0x`/`0X` prefix is retained, with a bounded lookahead;
hexadecimal digits remain ASCII. Strings and comments are not rewritten.
Byte-position provenance arrays and source buffers are not normalized or copied.

Danda detection and Indic identifier copies check the complete 3-byte scalar
before reading/copying it. Malformed or truncated E0 identifier sequences produce
an explicit E_UTF8 compiler error rather than reading past the source boundary.
This is not a new whole-file UTF-8 validation policy for arbitrary string bytes.

## Examples and exact native gate

- `examples/r66/sanskrit_native.sm`: native digits, all four short aliases,
  functions, loop, shared danda/double danda and FIFO kosh operations.
- `examples/r66/gujarati_native.sm`: the same devices in Gujarati.
- `examples/r66/native_digits.sm`: both digit sets, mixed digits, fractions,
  negative floats, identifier suffix, ASCII hex and unchanged string bytes.

They live in a subdirectory deliberately: the existing `examples/*.sm` runner
would otherwise need new LANG entries. They are enumerated with exact expected
stdout by `tools/r66_native_acceptance.py`; accepted goldens are untouched.

## Template for another script

Preserve its existing keyword translations; choose exact aliases, identify its
real Unicode digit-zero and abbreviation codepoints, and add only bounded
UTF-8 decode cases for those codepoints. Do not equate E0 with one script.
Reuse the common danda logic, number accumulation, diagnostics and ASCII
fallback. Add one paired ASCII/native output case, a decimal case, a
string/comment preservation case, an identifier-suffix case, and truncated
UTF-8 boundary cases. Verify pack table/string capacities and native outputs.
This is a repeatable procedure, not a claim that the other scripts are enabled.
