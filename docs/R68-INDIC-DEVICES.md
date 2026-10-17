# R68 Indic device registry — six requested language packs

This implements the six names in `Sarvam-tak-ChatGPT/ROUND-68.md`: **Odia,
Kannada, Marathi, Tamil, Telugu, Hindi**. Language and script are not synonymous:
Hindi and Marathi reuse Devanagari. No old pack word is removed or renamed.

| Language pack | Decimal digits | Dedicated abbreviation util_chinha adopted here |
|---|---|---|
| Odia | U+0B66–U+0B6F, `୦୧୨୩୪୫୬୭୮୯` | None; no new abbreviation aliases |
| Kannada | U+0CE6–U+0CEF, `೦೧೨೩೪೫೬೭೮೯` | None; no new abbreviation aliases |
| Marathi | U+0966–U+096F, `०१२३४५६७८९` | U+0970 `॰`, exact aliases below |
| Tamil | U+0BE6–U+0BEF, `௦௧௨௩௪௫௬௭௮௯` | None; no new abbreviation aliases |
| Telugu | U+0C66–U+0C6F, `౦౧౨౩౪౫౬౭౮౯` | None; no new abbreviation aliases |
| Hindi | U+0966–U+096F, `०१२३४५६७८९` | U+0970 `॰`, exact aliases below |

The authoritative character identities were checked against Unicode 17.0.0
[UnicodeData](https://www.unicode.org/Public/17.0.0/ucd/UnicodeData.txt) and
[NamesList](https://www.unicode.org/Public/17.0.0/ucd/NamesList.txt), not inferred
from visually similar symbols. “None” means no dedicated character is adopted
by this registry; it does not mean the natural language never abbreviates.
Do not repurpose Oriya Isshar, Telugu Tuumu, vowel marks, or Tamil number signs.

Hindi/Marathi add exactly `मु॰ → mukhya`, `च॰ → vitti`, `लि॰ → likha`,
`द॰ → dasham`. These are Sutram design choices, not Unicode-defined keyword
semantics. The whole alias must match; the util_chinha is not arbitrary prefix
expansion. Other four packs change documentation only; their exact old words
are preserved. `tests/r68/baseline_packs.json` records verified prior bytes/IDs.

## Shared rules

The R66 lexer calls `r66_decimal_digit_at` before treating E0 as an identifier
start. R68 extends that bounded helper with four explicit ranges; its ABI is
unchanged: digit 0–9 in RAX, consumed width 1 or 3 in EDX, otherwise -1/0.
RCX and R8–R11 remain preserved. Integer and fractional loops already use this
helper, so there is no global text replacement or new UTF-8 byte-at-a-time path.

ASCII `.` remains the decimal point. Both `।` U+0964 and `॥` U+0965 remain
statement terminators under every pack. They are never reinterpreted as
abbreviations by this language, even though natural-language punctuation may
have other uses. Strings/comments retain their original bytes. ASCII-only
hexadecimal prefix rules are unchanged. Mixed supported decimal scripts remain
accepted as in R66/R67; no locale-dependent normalization is introduced.

There are now **90 recognized decimal characters**: ASCII plus eight Indic
script ranges. Malayalam was not in the six-name R68 brief and is **not silently
added**; its numeral range remains outside this delivery. This is not a claim
that every Indic script in Unicode, or every repository language pack, is done.

The six `examples/r68/<language>.sm` files have accompanying `.out` and `.exit`.
They cover all ten digits, fractional digits, and both danda forms. Expected
outputs are fixtures; full compiler execution remains Sarvam's acceptance gate.
