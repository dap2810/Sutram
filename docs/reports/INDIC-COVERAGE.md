# Native-script coverage — explicit R69 boundary

This is the single current inventory for the 11 checked-in keyword packs.
Keyword aliases, decimal digits, punctuation and glyph shaping are distinct.
All R68 mappings and lexer bytes are preserved by R69; no unknown util_chinha is added.

| Packs | Decimal digit script | Current numeric support |
|---|---|---|
| Sanskrit, Hindi, Marathi | Devanagari | R68 included |
| Gujarati | Gujarati | R68 included |
| Bengali | Bengali | R68 included |
| Punjabi | Gurmukhi | R68 included |
| Odia | Odia | R68 included |
| Kannada | Kannada | R68 included |
| Tamil | Tamil decimal digits only | R68 included |
| Telugu | Telugu | R68 included |
| Malayalam | Malayalam | **Not implemented in the locked R68 digit helper** |

Malayalam keyword aliases exist, so Malayalam-pack programs may use ASCII
digits; this does not establish Malayalam-native numeral support. This round
chooses the brief's permitted **named-gap** option: native Malayalam digits are
deferred to avoid changing accepted lexer/lock/negative-corpus inputs during a
build-path and packaging repair. A later patch needs a bounded U+0D66–U+0D6F
recognizer plus full/native tests and explicit lock migration. No other installed
pack is silently omitted. Scripts not represented by these 11 packs are not
advertised; this is not a promise of every Indian language or numeral system.

Exact existing abbreviation spellings are pack entries, not arbitrary prefixes:
Devanagari U+0970, Gujarati U+0AF0, Bengali U+09FD, Gurmukhi U+0A76. No dedicated
abbreviation util_chinha is asserted here for Odia, Kannada, Tamil, Telugu or Malayalam.
All packs share the explicit U+0964/U+0965 danda terminators in the implementation.
An ASCII dot is the decimal separator. Normalization, confusable detection,
script-mixing policy and complete grapheme/font shaping remain separate gaps.

This is a source inventory at input blob
`64ea028a5ccf56117c132a7efd0673cbe2df3fc6`, not fresh cross-platform execution.
