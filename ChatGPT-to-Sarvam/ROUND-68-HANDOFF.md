# Sutram Round 68 — ChatGPT to Sarvam source-review handoff

Delivery/check date: **2026-10-15**. Incoming `ROUND-68.md` is dated 2026-10-16;
that future heading is recorded as supplied, not treated as today's date.
Review: [draft PR #26](https://github.com/dap2810/Sutram/pull/26).
Branch: `feature/r68-devices-probes-diagnostics-20261015`.
Source commit: `31b9e7c96db65c23d160e60f15864fb967910454`.
Pinned main input: `a700bfd21a6af1c6d5efc275df1963585615ef67`.

**Source work delivered, not a native-accepted release.** All 55 changed files
are uploaded. Their locally computed Git blob IDs reproduce the exact uploaded
tree `7647297b8b2fa7b0b930b20c0c6fc41db4076ed9` in two independent groups
(28 non-example paths and 27 example paths); no path/content correction was
needed. Main receives only this handoff, observations, checksums and review index.

## Five workstreams

| Workstream | Delivered source/documentation | Honest remaining limit |
|---|---|---|
| WS1 six requested packs | Explicit Odia/Kannada/Tamil/Telugu decimal ranges; Hindi/Marathi reuse Devanagari. All old words preserved; four exact U+0970 aliases added to each Hindi/Marathi pack. Six .sm/.out/.exit triples exercise integers, fractions and both dandas. | Whole compiler/sample execution pending. No dedicated sign invented for the other four. Malayalam is outside the six-name brief, not silently declared complete. |
| WS2 pure-pair probe | Three fixtures, independent-reference/default/pure-mode comparison, 15 non-RSP registers and exactly 46 EXPECTED removed bytes, pair-free equality and nonmatching controls. | No full-compiler A/B or timing measurement here; 46 is a testable hypothesis, not an observed saving. |
| WS3 Windows GUI | Exact title-only counter description, 12 manual checks and 11 paste/title fixtures tested against the isolated counter. | No Windows opening/closing/rendering/installer run; no shaping, advances, caret or GUI source changes. |
| WS4 lexical diagnostics | Pure-NASM compiler-host UTF-8 precheck and abbreviation-keyword value guard; exact root file:line/alias messages, exit 1. | Build the R68 entry to activate them. No full NASM macro/compiler execution; imported-file provenance is explicitly root/expanded-line, not original source-map resolution. |
| WS5 installer docs | One canonical INSTALLATION-ROUTES.md; root/Windows pointers and setup guide consolidated; old Program Files/allow-antivirus/missing install.sh claims removed from setup instructions. | Documentation only. Old main wrapper f51f3acc... still differs from R67's delivered fix; no installer-source repair or target execution is claimed. |

## Exact compiler input and produced output

Required inherited compiler Git blob:
`64ea028a5ccf56117c132a7efd0673cbe2df3fc6` (545722 bytes).
This time the actual main file matches the R67 integration record.

The produced source output is **the complete NASM ENTRY WRAPPER**, not an expanded
copy of the inherited compiler:

- Path: `src/r68_compiler_entry.asm`
- Git blob: `42389aaf73179726d91e23359aee2199734036e1`
- SHA-256: `2c18d5958337ce55ac2f7f0c922cde99ec3fd637570606ad5d60ec1d5b584085`
- Length: 713 bytes

`tools/r68_prepare_review.py` rejects drift in the compiler and locked helper
inputs, refuses overwrite, and copies that entry to a fresh output. Whole-input
production preparation was NOT executed locally because the complete inherited
compiler was not materialized here. Unit tests use explicit mock inputs.
**No expanded compiler source blob or compiled executable hash is claimed.**
The digit include changes on the review branch; new diagnostic hooks require
the entry rather than a bare build of `src/sutram_compiler.asm`.

## Mandatory reviewer entry point

Read `docs/R68-SOURCE-REVIEW.md`, then in a complete verified checkout:

```sh
python3 -m unittest discover -s tests/r66 -p 'test_*.py' -v
python3 -m unittest discover -s tests/r68 -p 'test_*.py' -v
python3 tools/r68_prepare_review.py --output /tmp/r68-entry.asm
nasm -f elf64 -I. /tmp/r68-entry.asm -o /tmp/r68-default.o
ld -o /tmp/r68-default /tmp/r68-default.o
nasm -DSUTRAM_R67_PURE_STACK_PAIRS=1 -f elf64 -I. /tmp/r68-entry.asm -o /tmp/r68-pairs.o
ld -o /tmp/r68-pairs /tmp/r68-pairs.o
python3 tools/r68_native_acceptance.py --compiler /tmp/r68-default \
  --reference /path/to/independent-accepted-R67-default \
  --pair-compiler /tmp/r68-pairs --suite
```

Also build/test inherited R65 peephole, trap and combined modes; run codegen,
packs, graph, proofs and frozen gates on the actual selected compiler. Do not
silently test a stale executable or waive NO-EXPECTATION failures. Keep valid-code
identity separate from intentionally improved malformed-input behavior.

The prelex diagnostic is `Sutram Error [E_UTF8]: <file>:<line>: invalid or truncated UTF-8 in source code`.
The value diagnostic is `Sutram Error [E_ABBREVIATION_VALUE]: <file>:<line>: abbreviation keyword is not a value: '<alias>'`.
Both end in LF and exit 1. The helper tests validate these exact messages with
stubbed host I/O/token access, not a full Sutram frontend.

## Observed evidence and acceptance gaps

**57 local test methods passed**: 32 isolated machine-code/helper methods using
GNU as/GCC on Linux (C I/O/token stubs; Win64 ABI bridge where appropriate),
plus 25 source/pack/mock-preparation methods. Four Python files passed syntax
checking. The digit test exercises 65536 E0 byte combinations inside ONE method,
not 65536 independent Sutram programs. Long paths, malformed UTF-8, guard pages,
exact error lines and isolated title fixture counts are covered.

All 55 source/test/doc file hashes cover 95636 bytes. Verification used root,
source and language readbacks plus the two-group whole-tree identity check;
it did NOT fetch and execute every complete production file. Full test logs are
in the source supplement and summarized in ROUND-68-OBSERVED.txt.

**Not run:** complete production preparation, NASM preprocessing/full compiler
build, generated Sutram programs, reference/pair A/B, complete regressions,
Windows GUI/OS-shim/installer execution. Sarvam's previous native measurements
are not counted as new R68 results. The actual Windows checklist is blank.

Main's pinned `windows/build-windows-setup.ps1` still has blob
`f51f3accf46eb59d6fe37a21dad7eea73ddd16a6`, referencing the obsolete folder and
bypass flags. The canonical document identifies the actual native builder and
requires this sync discrepancy to be reconciled before release. No code mutation
of that wrapper was made in this documentation-only workstream.

No merge, automatic CI, background monitoring, library/accepted-golden change,
GUI palette/icon modification, credential, runtime networking, elevation or
registry mutation. Preserve newer main/Muse/GUI changes when reconciling PR #26.
