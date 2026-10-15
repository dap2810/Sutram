# R66 — Windows Indic layout and scoped cluster source

## Source finding: do not replace the working text control with byte drawing

At main `9921cbf175b2fb7983e45305fdec963380532452`, the header of
`windows/gui/sutram_gui.asm` identifies a pure-NASM Win64 GUI using MSFTEDIT
RichEdit; it loads `Msftedit.dll` and declares `RICHEDIT50W`. The fixed 8-pixel
byte advance described in the incoming brief matches the separately documented
Linux X11 renderer. The later CHANGELOG v142 explicitly distinguishes cluster
advance/caret changes from glyph shaping. These are different code paths.

The existing Windows source, rather than the premise that every platform has
the same renderer, is the basis for this plan. No existing GUI colors, fonts,
window-creation code or control behavior is changed by R66.

Microsoft documents that Rich Edit uses complex-script support and that glyph
widths depend on context. Therefore, counting clusters is NOT equivalent to
shaping a Devanagari or Gujarati run, and one cluster is NOT always 8 pixels.
The task's "one advance" is interpreted as one logical editor cluster step,
not an assertion about its physical width.

Primary references used for this plan:
- https://learn.microsoft.com/en-us/windows/win32/intl/complex-script-processing
- https://learn.microsoft.com/en-us/windows/win32/intl/using-character-clusters
- https://learn.microsoft.com/en-us/windows/win32/intl/displaying-text-with-uniscribe
- https://www.unicode.org/reports/tr29/

## Delivered clustering half

`windows/gui/r66_indic_clusters.asm` is pure NASM, with a Windows x64-callable
entry `r66_next_indic_cluster(RCX=start, RDX=exclusive_end) -> RAX=next`.
It returns UTF-8 byte boundaries, not pixels or UTF-16 selection offsets.
No heap allocation, system DLL loading, network access or runtime dependency.
It preserves nonvolatile registers and reserves Win64 shadow space on calls.

The deliberate scope is a small Devanagari/Gujarati **editor-tailored subset**:
base+vowel signs/nukta, same-script virama-linked consonants, optional ZWJ,
ZWNJ as an explicit conjunct-stopping boundary, ASCII CRLF, and common
U+0300..036F combining marks. It strictly decodes 1..4-byte UTF-8; an invalid
sequence consumes one byte without looking past the exclusive end. Digits,
danda and abbreviation marks remain separate clusters. Leading combining
marks, cross-script sequences and unsupported scripts are handled conservatively.

Examples: `कि`, `क्ष`, `क्‍ष`, `કિ`, `ક્ષ` are each one returned cluster;
`क्‌ष` and `ક્‌ષ` break after the ZWNJ-containing visible-virama cluster.
The helper is **not complete Unicode UAX #29 conformance**: no full Unicode
property tables, emoji-ZWJ/flag tailoring, bidi order or all-script coverage.
Nor does it reorder matras, form glyph conjuncts, draw a shirorekha, select a
font, or provide OpenType shaping. Never advertise it as that full shaper.

## Integration plan

1. Keep the source file UTF-8 and the RichEdit buffer UTF-16. Maintain a tested
   byte-offset ↔ UTF-16-code-unit map at the conversion boundary. Do not use
   this UTF-8 helper's offsets directly with RichEdit selection messages.
2. Let the Unicode RichEdit control own normal rendering, input, hit-testing
   and caret movement. Audit conversion APIs, surrogate handling and any
   custom caret/selection overrides before adding custom layout logic.
3. Use RichEdit's character-position queries (`EM_POSFROMCHAR` /
   `EM_CHARFROMPOS`) for actual layout positions. The helper can serve source
   navigation or a fallback logical-column model; never substitute count×8
   for measured positions in proportional or complex-script layout.
4. For a future truly custom renderer, process a whole text run: ScriptItemize,
   ScriptShape, ScriptPlace, then ScriptTextOut, with a matching font cache
   and font-fallback/error path. Cluster indices, glyph advances and logical
   caret stops must be retained together. Splitting a run before shaping can
   lose contextual shaping. Do not mix a fixed-cell byte renderer with the
   new logical-cluster count and call it completed shaping.

**Integration status:** the new helper is a standalone review source, not yet
linked into the existing GUI. Native Windows integration, rendering and visual
acceptance remain Sarvam's responsibility; no Windows window was opened here.

## What was actually tested

The helper's exact instructions were adapted from this simple NASM source to
GNU-as Intel syntax, linked on Linux, and invoked through a Windows-x64 ABI
bridge. Unit tests exercise clusters, malformed sequences, mixed widths,
ZWNJ/ZWJ, random bytes, and inaccessible guard pages immediately after EOF.
This validates isolated CPU behavior in that test arrangement. It does not
validate NASM assembly, a Win64 PE, RichEdit integration or Windows rendering.

## Windows visual acceptance checklist (not executed)

On a standard-user machine, use a freshly built GUI and locally available
Indic-capable fonts. Open a UTF-8 sample with both scripts; test `कि`, `क्ष`,
`क्‍ष`, `क्‌ष`, `કિ`, `ક્ષ`, `ક્‍ષ`, `ક્‌ષ`, both numeral sets and signs.
Check render, arrow keys, mouse hit-testing, selection, backspace/delete,
line wrap, zoom, scrolling and file save/reopen byte equality. Also check
normal open/close and unsaved-change handling. Inspect actual screenshots;
a captured image or a passing cluster test is not visual acceptance.
Do not install fonts, elevate, or bypass protections as part of this test.
