# Sutram Round 67 — source review and mandatory acceptance

Source base: `76137658ddd8fe8f23810cd5b55deb98ac381248` (2026-10-15).
Incoming: `Sarvam-to-ChatGPT/ROUND-67.md`. Work is source review, not a Windows release.

## WS1 — preserve the accepted Gujarati program

Choice **(b)**: do not reserve `સંખ્યા`. The held-back R66 pack is restored
with that one entry removed: **44 entries**, not 45. All 30 accepted core
entries and the other 14 R66 additions survive. The vector type remains
available as Latin `sankhya`; no new Gujarati vector synonym is invented.
`examples/37_native_gujarati.sm` and its exact `.out` golden are untouched.
The native runner pins both Git blobs and compares real stdout against the
existing golden, including its lack of a trailing newline.

**Not verified here:** complete compiler execution or the full suite with this
pack. Removing the reported reservation resolves that source-level cause,
but the required native suite is still Sarvam's acceptance decision.

## WS2 — Bengali and Punjabi/Gurmukhi

`src/r66_indic_lexer.inc` additionally recognizes Bengali U+09E6..09EF and
Gurmukhi U+0A66..0A6F. Existing ASCII/Devanagari/Gujarati behavior is retained.
All four Indic decimal ranges share final UTF-8 bytes A6..AF, but their
second byte is checked explicitly: A5 / AB / A7 / A9. Integer/fractional
consumption reuses the accepted R66 lexer path; no source text rewriting.
Each pack preserves its 30 old words and adds four exact abbreviation aliases:
Bengali U+09FD, Gurmukhi U+0A76. They are keyword aliases, not numeric signs,
statement delimiters or arbitrary prefix matching. Both use shared U+0964/
U+0965 danda. New examples and exact `.out`/`.exit` files are under examples/r67.

Unicode names/ranges were checked against the Unicode Consortium's Bengali
and Gurmukhi names lists. Sources:
- https://unicode.org/Public/18.0.0/charts/nameslist/0980/
- https://unicode.org/charts/nameslist/n_0A00.html
These sources define characters; the abbreviation alias choices are Sutram
language-design choices. They do not automatically enable the other scripts.

**Not verified here:** newly generated Sutram programs or full compiler tests.
The isolated digit helper is executed locally, including every E0 xx yy pair.

## Compiler synchronization finding and explicit preparation

The v145 changelog says R66's prepared compiler (`e1a67674...`) was synced.
The same pinned main also returns 404 for `windows/gui/r66_indic_clusters.asm`;
this branch explicitly restores the reviewed R66 helper (Git blob
`71cc89495add6ed2127daf41230b1040a3c65d72`) from R66 commit
`b406802dc7d155f0ea6a0c72e17d08e6ce90ba8e`. Its old standalone
comment is historical; the R67 GUI builder now supplies the linkage.
However, BOTH `fetch_file` and the pinned main `contents/src` API report
`caee73735372cfd92f47ea18c9c1c6f8b70e9599` (545382 bytes), the R65 compiler.
Do not silently treat that discrepancy as resolved. The committed R66 helper
alone does not activate native digits. R67's preparation tool deliberately
chains the existing exact R66 recipe from this observed input, then inserts
the optional same-register-pair emission hook. It rejects unknown source drift.
Sarvam should reconcile the main/compiler mismatch before final acceptance.

```sh
python3 tools/r67_prepare_compiler.py --source src/sutram_compiler.asm \
  --output /tmp/sutram-r67.asm --patch-output /tmp/sutram-r67.patch
nasm -f elf64 -I. /tmp/sutram-r67.asm -o /tmp/r67.o
ld -o /tmp/r67-default /tmp/r67.o
python3 tools/r67_native_acceptance.py --compiler /tmp/r67-default --suite
```

The complete production source has NOT been staged locally. Inspect the
resulting patch and test actual builds before integrating it. Build default,
R65 peepholes, R65 traps, combined R65 modes, and the optional R67 mode below.
Use the exact compiler under test via SUTRAM_COMPILER for historical gates.
`--suite` returns failure for unrecorded expectations; the known baseline
NO-EXPECTATION cases must not be silently relabelled as passing tests.

## WS3 — cluster helper linked in the GUI build

The GUI build now assembles **three** objects: `r67_gui_entry.asm`, the
existing `r66_indic_clusters.asm`, and `r67_cluster_count.asm`. The link
command includes all three. The entry wrapper includes the accepted GUI
unchanged and redirects only `call highlight_editor` through a small wrapper.
After highlighting, it reads UTF-16 text, converts an explicitly bounded range
to UTF-8, calls the real cluster iterator through the counter, and updates the
window title with a scoped cluster count. Invalid conversion/oversized text
produces "count unavailable", not a silently truncated count.

This is an actual source/build call path, not an unreferenced object. It does
**not** implement glyph shaping, full UAX #29, font fallback, pixel advances,
Bengali/Gurmukhi mark grouping, or caret/selection rewriting. RichEdit retains
rendering and UTF-16 positions. Only the inherited Devanagari/Gujarati scoped
clusters are grouped. Accepted colours, icon and original GUI source are untouched.

The wrapper uses NASM's documented instruction-name macro mechanism:
https://nasm.us/doc/nasm05.html (multiline macros / instruction overloading).
Full NASM preprocessing, Win64 linking, PowerShell execution, windows open/
close and visual rendering were NOT run here. Run `windows/gui/build-gui.ps1`
and the real Windows checklist. The packaging wrapper now builds this GUI
before the existing native installer packages the root GUI executable.

## WS4 — same-register cancellation, deliberately bounded

`src/r67_stack_pair.inc` recognizes an ENTIRE canonical hex block containing
only `push r; pop r`, for 15 of 16 64-bit GPRs (RSP excluded). It checks the
whole string and both encodings before emitting anything. Different registers,
NOPs, other prefixes/instructions, invalid hex, partial bytes and extra bytes
fail closed. No instruction bytes are deleted, and no existing code offsets
are decremented. Compiler branches/patch positions are computed after the
normal emission decision.

**Important explicit contract:** this is enabled only by
`-DSUTRAM_R67_PURE_STACK_PAIRS=1`. That define declares whole matching
`nishkriya` blocks to be pure stack-register round trips: no observation of
the transient write below RSP, no external entry into the block, and no
hand-calculated relative code offsets. Arbitrary inline assembly remains
byte-for-byte opaque by default. This is NOT a general byte-stream optimizer
or permission to remove stack effects from arbitrary raw assembly. Keep the
mode OFF for programs that rely on those effects. The source matcher covers
all same-register encodings within this restricted contract; further lowering
sites remain future work, not an implemented global optimizer.

```sh
nasm -DSUTRAM_R67_PURE_STACK_PAIRS=1 -f elf64 -I. /tmp/sutram-r67.asm -o /tmp/r67-pair.o
ld -o /tmp/r67-pair /tmp/r67-pair.o
python3 tools/r67_native_acceptance.py --compiler /tmp/r67-default \
  --pair-compiler /tmp/r67-pair --reference /path/to/accepted/default
```

The isolated matcher has been executed for every same/different GPR pair and
adversarial byte shapes; actual generated-program instruction-count/size A/B
and the semantic acceptance of this explicit pure-block contract are for Sarvam.

## WS5 — one installer policy, corrected route

The existing `docs/R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md` remains the canonical
comparison. `windows/WINDOWS-README.md` now points there instead of recommending
administrator NSIS/WSL steps. The convenience build wrapper points at the actual
`native-installer` folder and builds the linked GUI first. Its explicit execution-
policy bypass flags and obsolete transitional-ELF success message are removed.
The wrapper has a bounded resource self-test and does not claim visual acceptance.
No install/uninstall implementation, registry or OS settings were changed or run.

## Verification boundary and safety

53 local tests: 33 inherited helper/preparation tests adapted for the intended
new ranges/count; 20 new native-helper/source tests. All pass. These comprise
26 isolated assembly-helper test methods (GNU as/GCC on Linux, Win64 bridge
for the counter) and 27 source/pack/preparation methods. The exhaustive 65,536
byte combinations are inside one method, not 65,536 compiled Sutram programs.
Python syntax, source SHA-256 and uploaded Git blob checks are separate evidence.

No Windows runtime, full NASM compiler build, entire production preparation,
full compiler regression or installer execution is claimed. No workflow changes,
automatic CI, background monitoring, credentials, library edits, accepted-golden
rewrites, palette/icon changes, elevation or new application networking.
