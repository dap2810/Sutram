# WS3 — Documentation audited against the code

**Date:** 2026-10-18 · **Base:** main at v162, commit `feef075` · **Scope:** `README.md`,
`PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`, `AGENTS.md`, `docs/*.md` (48 files), plus the vocabulary HTML
where a `.md` file points at it. **No document was changed.**

---

## 1. What I did

1. **Every fenced code block** in the scope was extracted (68 blocks). The 15 that are Sutram programs or
   fragments were compiled with the canonical compiler; fragments were wrapped in a `mukhya()` and run.
2. **Every number** in the status/gate tables was re-measured with the tool the document names (or, where
   the document names none, with the obvious one), on this checkout.
3. **Every build command** in the four entry documents was executed.
4. **Every pinned Git blob / SHA** that a document or tool relies on was recomputed.
5. A scripted scan for **prose the rename broke** — English sentences in which a renamed identifier now
   sits where an English word was (`.vardh` for `.inc`, "by gudh" for "by hash", "sangrah up" for "set
   up", "a single patra" for "a single file", …). 144 raw hits, hand-filtered below; table rows that
   legitimately list module names (`roop`, `gudh`, `brihat`, `vakyank`, `sadhan`, `vardh` the function)
   were discarded.

## 2. What I actually ran

```sh
# code samples (extracted to 000_…015_*.sm by a script; one line per sample)
for f in samples/*.sm; do ./sutram_compiler "$f" "${f%.sm}.bin"; done
./sutram_compiler --lang sanskrit samples/010_LANGUAGE-REFERENCE_L254.sm a.bin      # Devanagari sample
nasm -f elf64 -DSUTRAM_R71_UNSAFE_BOUNDARY=1 -I. src/r71_compiler_entry.asm -o r71.o && ld -o r71 r71.o
./r71 samples/013_R71-MEMORY-BOUNDARY_L12.sm b.bin && ./b.bin                       # R71 sample, opt-in build
# gates
python3 tests/run_tests.py ; python3 tools/codegen_gate.py ./sutram_compiler
python3 tools/test_lang_packs.py ./sutram_compiler
python3 tools/proof_lib.py --compiler ./sutram_compiler ; python3 tools/proof_props.py --compiler ./sutram_compiler
python3 tools/check_layers.py ; python3 tools/test_ide_undo.py ; python3 tools/test_x11_protocol.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py'
python3 -m unittest discover -s tests/gui -p 'test_*.py'
python3 tools/r70_negative_corpus.py --compiler ./sutram_compiler --report r70.json
python3 tools/r69_build.py --check-only
# pins and counts
git hash-object src/sutram_compiler.asm src/r68_compiler_entry.asm
ls lib/*.smlib | wc -l ; grep -hE '^\s*prakriya\s+[A-Za-z_]' lib/*.smlib | wc -l
ls examples/*.sm | wc -l ; find examples -name '*.sm' | wc -l ; git ls-files | wc -l
stat -c %s src/sutram_compiler.asm sutram_compiler ; wc -l src/sutram_compiler.asm
# the "two-module limit" claim
printf 'yoj ganit\nyoj ank\nyoj shreni\nyoj madhava\nmukhya() {\n    likha(varg(7))\n    likha(fib(10))\n}\n' > four.sm
./sutram_compiler four.sm four.bin && ./four.bin
```

## 3. Code samples — PASS / FAIL / NOT-RUN

| # | File:line | Result | Note |
|---|---|---|---|
| 000 | `README.md:9` | PASS | prints `Namaste, jagat` |
| 001 | `PROJECT-MASTER.md:26` | PASS | |
| 002 | `PROJECT-OVERVIEW.md:19` | PASS | |
| 003 | `docs/ERROR-CONVENTION.md:142` | PASS (fragment, wrapped with `yoj phal`) | prints `1` then `20` |
| 004 | `docs/KOSH-REUSE.md:13` | PASS (fragment, wrapped; `... use v ...` line removed) | `kosh_cap` stays 100000 as the doc says |
| 005 | `docs/LANGUAGE-REFERENCE.md:10` | PASS | |
| 006 | `docs/LANGUAGE-REFERENCE.md:140` | PASS | |
| 007 | `docs/LANGUAGE-REFERENCE.md:167` | **FAIL** — `parse error at line 15:18 near token 'to'` | **lines 182 and 188 use `to`; the keyword is `tak`.** With `to`→`tak` the sample compiles and prints the documented output. *This is the language reference's main syntax tour — the rename missed it.* |
| 008 | `docs/LANGUAGE-REFERENCE.md:212` | PASS (fragment, wrapped) | ternary and `kuru…yavat` behave as described |
| 009 | `docs/LANGUAGE-REFERENCE.md:239` | PASS | |
| 010 | `docs/LANGUAGE-REFERENCE.md:254` | PASS with `--lang sanskrit` (as the doc says); FAIL without | prints `15` |
| 011 | `docs/R52-BUILTIN-FIXES.md:17` | PASS (fragment, wrapped) | creates `example.txt`, `private.txt` |
| 012 | `docs/R56-MODULE-GLOBALS.md:7` | PASS | |
| 013 | `docs/R71-MEMORY-BOUNDARY.md:12` | PASS only with the R71 entry **and** `-DSUTRAM_R71_UNSAFE_BOUNDARY=1` (the doc says so at line 22); FAIL on the canonical build and FAIL on the R71 entry without the flag | prints `42` |
| 014 | `docs/SPECIFICATION.md:48` | PASS | |

Summary: **13 PASS · 1 FAIL (007) · 0 NOT-RUN.** (010 and 013 pass under the conditions their own text
states.)

## 4. Claims not supported by the code — by document

Severity key: **E** = factually wrong today · **S** = stale number/command · **P** = prose the rename
broke (reads wrong or misquotes the compiler) · **I** = the document contradicts itself.

### 4.1 `PROJECT-MASTER.md`

| Line | Claim | What the code does | Sev |
|---|---|---|---|
| 145 | "Module graph \| OK" | `python3 -m unittest discover -s tests/module_graph` → **6 PASS / 10 FAIL / 2 ERROR of 18** (fixtures still use `ayojan`/`pratiyati`; see WS2 §4.2). If "OK" refers to a different check, the table does not say which. | E |
| 149 | "GUI tests \| **18 / 18**" | No tool in the tree prints an 18-count. `tools/ide_test.py` prints colour-presence lines, no count; `tests/gui` unittest = 28 tests (28 OK); `tools/test_ide_undo.py` = 12/12; `tools/test_x11_protocol.py` crashes (`/scratch/work/sutram-gui` hardcoded default, line 132) unless `SUTRAM_GUI` is set. **NOT-REPRODUCIBLE as stated.** | S |
| 150 | "Negative corpus (R70) \| 6 / 6, native_status PASS" | `tools/r70_negative_corpus.py` → `"native_status": "NOT_ACCEPTED", "error": "fixture drift: bad_type"` — the manifest pins `file_sha256` of each fixture and `tests/negative/r70/cases/bad_type.sm` no longer matches (it now contains `prati`, i.e. it was renamed after being pinned). **The gate cannot run on main.** | E |
| 151 | "Compiler source 545,722 B → 190,144 B binary" | source is **545,775 B**; the canonical-entry binary is **192,088 B** here (bare `src/sutram_compiler.asm` build: 190,072 B). Binary size may depend on NASM version (2.16.01 here) — so S, not E. | S |
| 152 | "Repository ~1,800 files" | `git ls-files` = **1,947** | S |
| 238–243 | §11 gate expectations: `proof_lib` "expect 183", `proof_props` "expect 76", `check_layers` "expect 12 core, 9 alloc" | measured **191**, **86**, **14 core / 9 alloc / 1 std** — and §6 of the *same file* (lines 143–146) says 191 / 86 / 14. | I |
| 257 | "`0 std` in the layer check — worth confirming it is intentional" | the layer check prints **`1 std`**; §6 line 146 says `1 std`. The open item is stale. | I |
| 15 | "one hand-written NASM patra" | reads "file" → `patra` | P |
| 104 | "no phal type or propagation" | reads "result type" | P |
| 203, 212 | "is a gap suchi", "where patra ownership is disjoint" | list / file | P |

### 4.2 `PROJECT-OVERVIEW.md`

| Line | Claim | What the code does | Sev |
|---|---|---|---|
| 54 | "`src/sutram_compiler.asm` … ~15k lines" | **22,300** lines | S |
| 57, 138 | "202 programs" | **207** `.sm` under `examples/` (191 top-level + 16 in `lib/ r67/ r68/ r71/`); `PROJECT-MASTER.md:148` says 207 | S/I |
| 74–75, 80–81 | build: `nasm -f elf64 src/sutram_compiler.asm …` (bare source, no `-I.`) | assembles and links here, but `docs/BUILDING.md` and `START-HERE` say the R68 entry is "the only supported entry"; the bare build lacks the R68 UTF-8/abbreviation diagnostics. Two entry documents give two different "the" build. | I |
| 99 | `test_lang_packs.py # 30/30 expected` | **33/33** | S |
| 101 | `test_x11_protocol.py # 31 checks, no display needed` | as printed it crashes (`FileNotFoundError: /scratch/work/sutram-gui`, hardcoded default at line 132); with `SUTRAM_GUI=./sutram-gui` it passes ("all X11 protocol checks passed") | S |
| 134 | "Compiler SHA-256 6036dd1c…" | a snapshot hash; the current binary differs (expected, but the table presents it as current) | S |
| 135 | "Regression suite **186/186**" | 187 PASS / 4 NO-EXPECTATION; same file line 97 says 187 | I |
| 139 vs 55 | "21 with code (303 functions)" vs "24 modules with code, 303 functions" | 24 modules, 303 `prakriya` | I |
| 147 | "passes 178 regression tests" | 187 | S |
| 12 | "one hand-written NASM assembly source patra" | P | P |
| 115, 117 | keyword table: "`kosh` \| growable mala", "`mala` \| mala" | the *English meaning* column was renamed; `mala | mala` tells a reader nothing | P |

### 4.3 `README.md`

| Line | Claim | What the code does | Sev |
|---|---|---|---|
| 56–57 | "**202 example programs** — 191 numbered plus 11 from recent rounds" | 191 + **16** = **207** | S |
| 60–61 | "Three further files (`mala`, `io`, `net`) are comment-only design sketches, not working modules" | `lib/` has exactly 24 `.smlib`; there is no `io` or `net`; **`lib/mala.smlib` has 8 real `prakriya` definitions** and is one of the 24 counted modules (`LIBRARY-LAYERS.md:21` lists it as `alloc`). The sentence described `array.smlib` in an earlier era; after `array`→`mala` it now names a real module as a sketch. | E |
| 64 | "Six book editions … English, Hindi, Sanskrit, Tamil, Telugu, Gujarati" | eight files match `docs/sutram-book-*.html` (also `-2`, `-3`) | S (minor) |
| 45, 47 | "`kosh` \| growable mala", "`mala` \| mala" | as 4.2 | P |
| 3, 23, 100 | "one patra covering…", "single assembly source patra", "plain text patra" | reads "file" | P |
| 28 | "The keyword sangrah is Sanskrit" | reads "keyword set" | P |
| 126 | "keep its reviewed `.vardh` files alongside it" | the files are **`.inc`** (`src/r66_indic_lexer.inc` etc.). `inc`→`vardh` was a *function* rename applied to a file extension. | P→E (a reader looking for `.vardh` files finds none) |

### 4.4 `docs/BUILDING.md`

| Line | Claim | What the code does | Sev |
|---|---|---|---|
| 13 | "Required core Git blob: `64ea028a…`" | `git hash-object src/sutram_compiler.asm` = **`f3a837a5…`**. Consequently the documented tool refuses: `python3 tools/r69_build.py --check-only` → `R69_BUILD_REFUSED: input drift: src/sutram_compiler.asm: expected 64ea028a…, got f3a837a5…`. **The "only supported" build *tool* cannot build main**; only the manual `nasm`/`ld` pair on lines 44–45 works. `tools/r69_build.lock.json:6` pins the same stale blob, and `docs/MEMORY-MODEL.md:8`, `docs/FREESTANDING.md:5`, `docs/INDIC-COVERAGE.md:36`, `docs/R68-SOURCE-REVIEW.md:4` cite `64ea028a…` as *the* compiler blob (those four read as snapshot references, so S rather than E). | E |
| 54 | "verifies … the GUI by gudh" | reads "by hash" | P |
| 29 | "never an input patra" | reads "input file" | P |

### 4.5 `docs/LANGUAGE-REFERENCE.md`

| Line | Claim | What the code does | Sev |
|---|---|---|---|
| 182, 188 | `chakra i = 1 to 5 {` / `chakra j = 5 to 1 {` | **`to` is not a keyword; `tak` is.** Sample 007 fails to compile. | E |
| 295 | pack table row `| to | पर्यन्त | …` | the keyword is `tak` (row label) | S |
| 134 | "60 functions across six modules" | those six modules now hold 18+10+14+22+5+27 = **96**; `lib/` holds 24 modules / 303 | S |
| 127–132 | per-module counts: ganit "15", shreni "11", ganita "6", varna "13" | ganit **18** (`bit_gan`, `ganit_yadricch`, `ganit_seemit` missing), shreni **14** (`nivesh_shreni`, `mil_shreni`, `mil_shreni_punar`), ganita **22** (16 `ganita_janchit_*`/`ganita_paripurna_*` missing), varna **27** (14 missing); ank 10 ✓, madhava 5 ✓. 18 of 24 modules are not in the table at all. | S |
| 135–136 | "**Limitation:** a program can currently include at most two modules — the inliner's buffer overflows at three or more; this is a known compiler bug being fixed." | `four.sm` with `yoj ganit / ank / shreni / madhava` compiles (9,102 B) and runs. **The limitation no longer exists.** | E |
| 24–50 | keyword table (25 rows) | compiler has **28** keywords; `tak`, `kosh`, `dasham` are absent from the table (`kosh`/`dasham` are covered in §15–16 later; `tak` is covered nowhere by name) | S |
| 38 | "`mala` \| mala" | meaning column renamed | P |
| 97, 103–106 | "patra descriptor helper", "varna length/compare/concatenate/copy" | read "file descriptor", "string …" | P |
| 374–375 | quotes the runtime messages as "`kosh pop from empty mala`", "`kosh peek from empty mala`", "`kosh dequeue from empty mala`" | the compiler emits **`… from empty array`** (`src/sutram_compiler.asm:306–308`). The doc now misquotes a string a user will see. | P→E |
| 278–296 | pack table Devanagari column: `अन्यत्र`, `आयोजन`, `पङ्क्ति`, `परिग्रह`, `प्रतियाति`, `पुनरावर्तन`, `सृजन`, `उद्देश्य`, `निषेध` | matches `lang/sanskrit.lang` today, **contradicts `docs/sutram-vocabulary.html`'s Devanagari column** (`अन्य`, `योज्`, `माला`, `सत्य`, `प्रति`, `चक्र`, `गणना`, `अग्रिम`, `अभाव`). One of the two documents is wrong; see WS2 §3.2. | I (cross-doc) |

### 4.6 `docs/sutram-vocabulary.html` (reached from `START-HERE` and `ROUND-01`)

| Section | Claim | What the code does | Sev |
|---|---|---|---|
| "Error codes and CLI flags" | E_PARSE→**E_VYAKARAN**, E_UTF8→**E_LIPI**, E_UNDEFINED_FUNCTION→**E_AGYAT**, E_MODULE_CYCLE→**E_CHAKRA**, E_UNSAFE_BOUNDARY→**E_SEEMA**, E_INTEGER_TRAP→**E_ANK_DOSH**; `--check`→**`--janch`**, `--lang`→**`--bhasha`**, `--version`→**`--sanskaran`** | the compiler emits `E_PARSE`, `E_UTF8`, `E_UNDEFINED_FUNCTION`, `E_MODULE_CYCLE`, `E_INTEGER_TRAP` and accepts only `--check`, `--lang`, `--version` (`src/sutram_compiler.asm:217, 405–409`; `r68_diagnostics.inc:8–12`). The table sits beside the keyword renames that *were* applied, with the same "Was/Becomes" heading, so it reads as done. | E (or a plan mislabelled as done) |

### 4.7 `docs/NEGATIVE-CORPUS.md`

| Line | Claim | What the code does | Sev |
|---|---|---|---|
| 27 | the parse-error strings "in order: `Sutram Error: parse error at line `, `end of patra`, `Hint: check the keyword spelling and syntax near this location.`" | the compiler emits **`end of file`** (line 281) and **`Sanket: is sthan par shabd aur vyakaran dekho.`** (line 282). Both quoted strings are wrong: one by the rename, one by a later Hindi translation. | P→E |
| 64–71 | pin table names `src/r68_diagnostics.vardh`, `src/r68_unicode_helpers.vardh`, `src/r66_indic_lexer.vardh`, `src/r67_stack_pair.vardh` | files are `.inc`; also the first row pins `src/sutram_compiler.asm` at `64ea028a…` (stale, see 4.4) | P→E |
| 86–87 | "records its gudh", "a binary gudh" | reads "hash" | P |
| 131 vs `PROJECT-MASTER.md:150` | this doc says the runner prints `native_status: NOT_RUN` without native execution; PROJECT-MASTER says `native_status PASS` | today it prints `NOT_ACCEPTED` (fixture drift) | I |

### 4.8 Other `docs/*.md` — prose the rename broke (each verified by reading the sentence)

| File:line | Reads | Should read |
|---|---|---|
| `AGENTS.md:5` | "the single patra to read" | file |
| `AGENTS.md:24` | "Do not sangrah up background watching" | set up |
| `INSTALL-WINDOWS.md:44` | "Record the package gudh" | hash |
| `docs/CHANGELOG.md:144, 150, 388–389, 1305, 1372–1376` | `src/r71_module_link.vardh`, `src/r71_unsafe_integration.vardh`, `src/r66_indic_lexer.vardh`, `win/winrt.vardh`, `win/rtblob.vardh`, "Both `.vardh` files" | `.inc` — **historical entries, so the file names they cite are now wrong**; Sarvam's rule is to leave CHANGELOG numbers alone, but these are names, not numbers |
| `docs/CI-NOTIFICATION-POLICY.md:49` | "Its passing phal" | result |
| `docs/ERROR-CONVENTION.md:6, 59` | "no phal type", "phal is `dasham`" | result |
| `docs/ERROR-CONVENTION.md:13, 58` | "a 1-cell `mala` (integer mala)", "(float mala)" | array |
| `docs/FREESTANDING.md:42` | "a reproducible memory nighantu" | map |
| `docs/KOSH-BUILTINS.md:76` | "zeroes the nighantu's storage" | map's |
| `docs/KOSH-BUILTINS.md:107–109` | "`kosh pop from empty mala`" ×3 (quoted compiler output) | `… empty array` — misquote, as 4.5 |
| `docs/LIBRARY-BOUNDARY.md:8, 19, 26, 94` | "the patra-I/O entry", "a patra API", "A sangrah of socket builtins", "the patra builtins" | file / set |
| `docs/LIBRARY-LAYERS.md:61, 87` | "The `0 std` phal", "builtin for mala length" | result / array |
| `docs/MEMORY-MODEL.md:203` | "is not the phal" | result |
| `docs/NUMERIC-CONTRACT.md:72, 78` | "the dasham→int conversion", "module suchi" | (72 is fine — `dasham` is the type) / list |
| `docs/PROPERTY-NET.md:7, 40, 44, 69` | "this patra states", "the empty varna", "a shreni disturbing", "equalling the sangrah" | file / string / sort / set |
| `docs/R71-MEMORY-BOUNDARY.md:56–57` | "`src/r71_unsafe_tokens.vardh`", "`src/r71_unsafe_integration.vardh`" | `.inc` |
| `docs/SPECIFICATION.md:6, 95` | "a separate source patra", "The `3 & 4` phal is pinned" | file / result |
| `docs/STRING-BYTE-PARITY.md:16–17, 81` | "a byte varna", "a cell mala", "a varna literal" | string / array / string |
| `docs/WINDOWS-SETUP.md:112` | "The patra is an ELF binary" | file |
| `docs/INSTALLATION-ROUTES.md:20` | "a root-level patra" | file |

I read each of these in context; none is a legitimate use of the Sanskrit name. The pattern is exactly the
one the brief warned about: `inc`, `hash`, `set`, `file`, `result`, `map`, `array`, `string`, `sort`,
`list` were replaced **inside English sentences and inside quoted compiler output**, not only in code.
`START-HERE` says v162 "repaired prose the rename had corrupted"; the repair reached some files and not
these.

### 4.9 Claims that **are** supported (so the list above is not read as "everything is wrong")

Suite 187/4 · codegen 12/12 · packs 33/33 over 11 packs · proof_lib 191/191 · proof_props 86/86 ·
layers 14/9/1 · 24 modules / 303 functions · 207 examples (`PROJECT-MASTER`) · `README.md:113–114` and
`PROJECT-MASTER.md:230–231` build commands · the entry-file pin `42389aaf…` (713 B) · `kosh` behaviour
in `KOSH-REUSE.md` · `tools/test_ide_undo.py` 12/12 · `tests/gui` 28/28 · the R71 sample under its
stated build · every "What is NOT true" statement in `PROJECT-MASTER.md` §9 (I found nothing that
contradicts them).

## 5. One language-level claim, stated carefully

`START-HERE`/`ROUND-01`: "The language is fully Sanskrit … every keyword." **True for the 28 keywords.**
Not true for the builtins: `char_from`, `char_upper`, `char_lower`, `netsock`, `netbind`, `netlisten`,
`netaccept` (`src/sutram_compiler.asm:719–722, 746–748`) are English and are what a user types. The
documents do not claim builtins are Sanskrit, so this is not a documentation error; it is noted because
WS1's aim (a user who knows no English) is affected by builtins as much as by keywords.

## 6. PASS / FAIL / NOT-RUN totals

| | |
|---|---|
| Code samples | 13 PASS · 1 FAIL · 0 NOT-RUN |
| Gate numbers re-measured | 9 match · 5 do not (`Module graph`, `GUI 18/18`, `R70 6/6`, sizes, file count) · `test_x11_protocol.py` fails as printed, passes with `SUTRAM_GUI` set |
| Build commands executed | 4 of 4 run (two are the same pair); `r69_build.py --check-only` **refuses main** |
| Pins recomputed | entry blob ✓ · core blob ✗ (stale in `BUILDING.md`, `NEGATIVE-CORPUS.md`, `r69_build.lock.json`) · R70 fixture sha256 ✗ |
| Prose-damage sentences confirmed by reading | 58 (4.1–4.8) |

## 7. What I did not do, and why

- Did not audit `docs/*.html` (the books, the stdlib reference, the design charter) beyond the two
  tables I needed; the brief scoped `docs/*.md`.
- Did not verify every historical number in `docs/CHANGELOG.md` — those are records of past rounds, and
  Sarvam's rule is to leave them. I reported only the file-name corruption there (4.8), because a wrong
  file name in a changelog misleads the next reader in a way a stale count does not.
- Did not run the Windows documents (`WINDOWS-SETUP.md`, `INSTALL-WINDOWS.md`) — no Windows host.
- Did not fix anything. Several of these are one-line edits (`to`→`tak`, `.vardh`→`.inc`, the blob pin,
  the empty-array quotes); I left them for the owner so that the change and its re-check are recorded by
  the same party, per the handoff rules.
