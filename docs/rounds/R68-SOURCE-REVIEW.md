# Sutram R68 — source review, build entry and acceptance

Pinned main: `a700bfd21a6af1c6d5efc275df1963585615ef67`.
Compiler input Git blob: **`64ea028a5ccf56117c132a7efd0673cbe2df3fc6`**.
The R68 incoming note is dated 2026-10-16; this delivery/check is dated 2026-10-15.
The actual current file hash, rather than the note's date, establishes the input.

## Deliverables and boundaries

WS1: four more explicit native digit ranges in the already integrated bounded
lexer helper; Hindi/Marathi reuse Devanagari. Six preserved packs and paired
examples are delivered. No util_chinha is invented for Odia/Kannada/Tamil/Telugu.
Malayalam was absent from the six-name brief and is not silently enabled.
Full script/example execution remains a native acceptance requirement.

WS2: an A/B probe for the inherited default-OFF pure-pair mode. It requires
byte-identical default/reference executables and exactly 46 removed bytes in the
15-register fixture, plus nonmatching controls. This is a hypothesis/check,
not a measured compiler or speed result. See `R68-PURE-PAIR-PROBE.md`.

WS3: title-only counter behavior and 12 manual Windows checks, with exact paste
fixtures. Isolated fixture counts are tested; no Windows action is claimed.
No shaping, advances, font or caret implementation changes.

WS4: bounded UTF-8 code validation and abbreviation-keyword value diagnostics,
with full root filename and line. Implemented as pure-NASM compiler-host hooks
in a review entry that includes the accepted compiler. Original imported-file
provenance is NOT solved; see `R68-LEXICAL-DIAGNOSTICS.md` for exact scope.

WS5: one canonical `INSTALLATION-ROUTES.md`, with live setup pages pointing to it.
Root README installation instructions are corrected, while unrelated old project
statistics are not silently rewritten. Existing wrapper remains old on pinned
main despite R67's source correction: this round is documentation-only for the
installer and explicitly reports that remaining source-sync discrepancy.

## Fail-closed preparation and produced source identity

`src/sutram_compiler.asm` is unchanged. The digit include is updated in place on
the review branch; the diagnostic hooks require the **R68 entry**, not a direct
build of the old main source. The entry includes the same compiler and helpers.
It is a source entry wrapper, not a runtime interpreter or alternative backend.

`tools/r68_prepare_review.py` verifies the real compiler Git blob plus all locked
helper/entry blobs, rejects any drift, and copies the complete entry to a fresh
output path. It never overwrites the input, expands the 545-KiB compiler, builds
an executable, installs tools, starts CI or fetches data. The checked-in entry is
itself the complete delivered source output; its exact Git blob and SHA-256 are
reported in the handoff manifest. **No expanded compiler source blob is claimed.**
The whole-production-input preparation has not run locally; tests use explicit
small fixtures and verify rejection of the real compiler pin on unknown input.

From repository root with a complete checkout:

```sh
python3 -m unittest discover -s tests/r66 -p 'test_*.py' -v
python3 -m unittest discover -s tests/r68 -p 'test_*.py' -v
python3 tools/r68_prepare_review.py --output /tmp/r68-entry.asm
nasm -f elf64 -I. /tmp/r68-entry.asm -o /tmp/r68-default.o
ld -o /tmp/r68-default /tmp/r68-default.o
nasm -DSUTRAM_R67_PURE_STACK_PAIRS=1 -f elf64 -I. /tmp/r68-entry.asm -o /tmp/r68-pairs.o
ld -o /tmp/r68-pairs /tmp/r68-pairs.o
python3 tools/r68_native_acceptance.py --compiler /tmp/r68-default \
  --reference /path/to/independently-built-R67-default \
  --pair-compiler /tmp/r68-pairs --suite
```

Also build/test inherited R65 peephole, trap and combined configurations. Run
accepted codegen, packs, module-graph, library/property and frozen-baseline gates
against the actual selected compiler, never a stale `./sutram_compiler`. Do not
rewrite expectations or suppress NO-EXPECTATION failures. For Windows, build the
entry with the existing WINDOWS definitions and run real target acceptance.
NASM instruction-macro preprocessing, full compiler builds and programs are
unverified in this source delivery. The GUI's separate builder is unchanged.

## Test evidence interpretation

The delivered isolated helper/diagnostic routines execute via the established
narrow NASM-to-GNU-as adapter on Linux; diagnostic tests provide C I/O/token
stubs. This is useful machine-instruction evidence, but it is not a NASM assembly
of the full compiler, not a real lexer/parser end-to-end run, and not Windows.
Tests also cover pack preservation, exact source pins, no-overwrite behavior,
90 decimal characters, malformed UTF-8, guard pages, long paths and title fixtures.
See the handoff's observed log for actual counts, not estimated pass percentages.

No merge, automatic workflow, background watcher, library change, accepted-golden
rewrite, GUI palette/icon modification, credential, new application networking,
Windows execution, elevation or installer/registry mutation is part of this round.
