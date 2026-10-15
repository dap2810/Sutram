# Sutram Round 66 — source review and acceptance entry point

Base: main `9921cbf175b2fb7983e45305fdec963380532452` (CHANGELOG v143).
Required input compiler Git blob: `caee73735372cfd92f47ea18c9c1c6f8b70e9599`.
Incoming: `Sarvam-to-ChatGPT/ROUND-66.md`.

## Reconcile the brief with the live repository

The brief says R65 was never started. That historical statement is superseded
by the later v143 main commit: Sarvam reports staging, building and accepting
R65, including default/peephole/trap/combined builds, five trap cases,
unchanged default code, full UTF-8 diagnostic paths and Sanskrit aliases.
PR #23 remains draft/open, but its reviewed equivalent is already integrated
on main. This branch is based on that accepted main, not on the old draft.
Sarvam's prior native measurements are not counted as new R66 executions.

| Workstream | This delivery | Remaining boundary |
|---|---|---|
| WS1 peepholes | Preserve accepted R65 adjacent-store reuse and one-argument stack-transfer coalescing | No new general same-register push/pop cancellation; no safe additional generated site established. No new instruction-count or speed claim. |
| WS2 opt-in traps | Preserve accepted default-OFF R65 source and build modes | Regress default/trap/combined configurations after lexer integration. No arithmetic emitter changes made here. |
| WS3 Devanagari | Native integer/fraction digit reader, bounded lexer staging, exact U+0970 aliases, enqueue alias and example | Full staged compiler execution pending; abbreviation semantics are an explicit proposal. |
| WS4 Gujarati | Native digits; U+0AF0 aliases; preserved core pack plus vector/kosh aliases; Gujarati example; shared danda | Full native outputs pending; other scripts remain unchanged. |
| WS5 Windows layout | Standalone pure-NASM, Win64-ABI scoped cluster iterator plus RichEdit/Uniscribe integration plan | Not wired into GUI and not a glyph shaper; actual Windows execution/visual review pending. |
| WS6 installer | Existing legacy/native comparison kept authoritative; source findings clarified | Documentation only; no installer execution or implementation change. |

## Mandatory compiler staging, then integration

The branch intentionally leaves accepted `src/sutram_compiler.asm` unchanged.
New lexer behavior is delivered through the checksum-guarded preparation tool
and `src/r66_indic_lexer.inc`; merely checking out the branch does NOT enable it.
Prepare, inspect, build/test, then integrate the patch into the review branch
before considering any merge. Never merge an unprepared delivery as if its
new numeric syntax were already active.

From the repository root, with fresh output paths:

```sh
python3 -m unittest discover -s tests/r66 -p 'test_*.py' -v
python3 tools/r66_prepare_review.py --source src/sutram_compiler.asm \
  --output /tmp/sutram-r66.asm --patch-output /tmp/sutram-r66.patch
nasm -f elf64 -I. /tmp/sutram-r66.asm -o /tmp/r66.o
ld -o /tmp/r66-default /tmp/r66.o
python3 tools/r66_native_acceptance.py --compiler /tmp/r66-default \
  --reference /path/to/independently-built-accepted-R65-default
```

Native helper tests use Linux GCC/GNU-as only when available, through a narrow
syntax adapter and Win64 ABI bridge. They are separate from the complete
compiler gates. Preparation tests use captured-anchor fixtures and do not
claim complete production-source preparation. The tool rejects source drift,
missing/duplicate anchors, reapplication, and output overwrite attempts.

Build the staged source again with `-DSUTRAM_R65_PEEPHOLES=1`, with
`-DSUTRAM_R65_TRAP_INT=1`, and with both flags. Run the accepted R65 native
and finishing gates against those actual binaries, using the independently
built accepted baseline. Run the full accepted regression, language-pack,
module graph, library/property proof, R58/R59 frozen and R63/R64 gates.
The main suite supports `SUTRAM_COMPILER=/tmp/r66-default`; inspect every
other tool's compiler selection so a stale `./sutram_compiler` is not tested.
Do not rewrite accepted goldens to obtain green output.

The three new examples live under `examples/r66/` and are enumerated by the
new runner with exact output expectations, avoiding the legacy top-level
LANG-registration omission. The new runner also checks ASCII code identity
and rejects malformed Indic compiler inputs with explicit E_UTF8/exit 1.

## GUI source build (not GUI execution)

```sh
nasm -f win64 windows/gui/r66_indic_clusters.asm -o /tmp/r66-clusters.obj
```

This builds a callable object, not a GUI executable. Read
`R66-WINDOWS-SHAPING.md` before wiring it into any renderer. The existing
Windows RichEdit control and Linux fixed-cell code are not interchangeable.

## Evidence boundaries and safety

Locally observed: 33 unit tests passed: 17 isolated native-instruction helper
tests and 16 preparation/pack tests. The exhaustive digit test tries all
65,536 second/third-byte combinations after E0, plus the single-byte, valid
script digit, random-input and guard-page cases. Python syntax checks passed.
Full production compiler staging, NASM compiler builds, generated Sutram
program execution, full regressions and Windows GUI/installer testing were
NOT run here. There is no claim of a native-accepted R66 release.

No automatic CI or monitoring; no workflows changed; no accepted golden or
`lib/*.smlib` changes; no GUI palette changes; no network functionality,
credentials, elevation, HKLM writes or security bypasses added. Source and
review instructions stay in a draft branch; main receives handoff documents.
