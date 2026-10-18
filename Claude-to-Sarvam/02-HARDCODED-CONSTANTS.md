# WS2 — What the rename missed: hardcoded keyword spellings and lengths

**Date:** 2026-10-18 · **Base:** main at v162, commit `feef075`
**Status:** findings and evidence only. **No repository file was changed.** Written at `feef075`; see `00-READ-FIRST-v164-REGRESSION.md` §3 for what v163/v164 changed (§4.1 below: the X11 GUI table is now fixed, the terminal IDE table is not). One scratch-only patched build
was made outside the tree to *prove* a finding (§3.1); it is not part of the delivery.

---

## 1. What I did

1. Scanned `src/sutram_compiler.asm` and every `.inc` the canonical entry assembles for **immediates that
   spell ASCII text** (every `0x…` of 4+ hex digits whose little-endian bytes are printable and contain a
   letter), and for **numeric skips** (`add/mov/sub rX, N`) that follow a keyword match.
2. Listed every keyword-matching site (`mg_match_at` callers, `strcmp` against `kw_*`/`mg_w_*`, explicit
   byte compares) and checked the length/spelling each one assumes against the current keyword table
   (`kw_table`, lines 461–500; `kw_*` strings, 664–691).
3. Decoded every compiled-in **Devanagari** keyword spelling (`kw_dev_*`, 694–707) and compared with
   `lang/sanskrit.lang` and the Devanagari column of `docs/sutram-vocabulary.html`.
4. Diffed the compiler's keyword table against the keyword tables in **both IDEs** (`ide/sutram_ide.asm`,
   `ide/sutram_gui_linux.asm`) and the Windows GUI (`windows/gui/sutram_gui.asm`).
5. Grepped every code file in the tree (`*.asm *.inc *.py *.ps1 *.sh`, excluding docs and the handoff
   folders) for the pre-v157 spellings, and ran the one test suite that turned up.
6. Ran the compiler on inputs that exercise each suspect site.

## 2. What I actually ran

```sh
# immediates that spell text (python one-liner over the .asm/.inc files; output in §3)
# keyword-site listing
grep -nE "mg_match_at|mg_w_|kw_to_str|kw_ayojan|lang_to_word" src/sutram_compiler.asm
# IDE tables vs compiler table (python set-diff; output in §4)
# old spellings anywhere in code
grep -rlwE "ayojan|punaravartana|pratiyati" --include=*.asm --include=*.inc --include=*.py --include=*.ps1 --include=*.sh .
# the module-graph reference suite
python3 -m unittest discover -s tests/module_graph -p 'test_*.py'
# location-printer probe (lib/a.smlib and lib/b.smlib are two v1 modules importing each other)
printf 'yoj a\nmukhya() { likha(1) }\n' > cyc.sm
./sutram_compiler --check cyc.sm ; ./sutram_compiler cyc.sm cyc.bin
# Devanagari spelling probe
printf 'मुख्य() {\n    वित्ति x = 1\n    यदि (x == 1) { likha(1) } अन्य { likha(2) }\n}\n' > dev_new.sm     # अन्य   = vocabulary's Devanagari for anya
printf 'मुख्य() {\n    वित्ति x = 1\n    यदि (x == 1) { likha(1) } अन्यत्र { likha(2) }\n}\n' > dev_old.sm   # अन्यत्र = old anyatra
./sutram_compiler --lang sanskrit dev_new.sm a.bin ; ./sutram_compiler --lang sanskrit dev_old.sm b.bin
# IDE highlight probe: drive sutram-ide in a PTY on a file using chakra/tak/prati/anya, inspect escape codes
```

## 3. Findings inside `src/sutram_compiler.asm`

### 3.1 CONFIRMED WRONG — `r49_print_module_location` still searches for `ayojan` (lines 2246–2264)

```
2250:    add rax,6                       ; needs 6 bytes left on the line  (ayojan/niryat length)
2255:    cmp dword [rbx+r9], 0x6A6F7961  ; "ayoj"
2256:    je .r49_check_ayoj
2263:    cmp word [rbx+r9+4], 0x6E61     ; "an"
```
This routine prints the **column** of the import keyword in every module-graph diagnostic
(`E_MODULE_V1_ALIAS`, `E_MODULE_MISSING`, `E_MODULE_INVALID`, cycle reports — all callers of
`r49_print_module_location`). It scans the original line for the 6-byte word `ayojan` (or `niryat`).
Since the keyword is `yoj`, it never matches an import line and falls through to `r49_unknown`, which
prints `?`:

```
$ ./sutram_compiler --check cyc.sm
cyc.sm:1:?: Sutram Error [E_MODULE_V1_ALIAS]: v1 module 'a' must be imported with an alias: yoj a@alias
```

**Proof that this is the cause:** I copied `src/` to a scratch directory, replaced only the `ayoj`/`an`
compare with a 3-byte `yoj` compare, rebuilt, and ran the same input:
```
cyc.sm:1:1: Sutram Error [E_MODULE_V1_ALIAS]: ...        (keyword at column 1)
cyc_indent.sm:1:5: Sutram Error [E_MODULE_V1_ALIAS]: ... (same file with 4 leading spaces)
```
The scratch patch is **not** in the tree; the real fix is ChatGPT's to make. Note also `add rax,6` at
2250: with a 3-byte keyword the guard is too strict by 3 bytes (an import keyword in the last 5 bytes of a
file would be missed) — harmless in practice, but it is the same stale constant.

**Side observation on the same routine:** in normal (non-`--check`) mode the same error prints
`cyc.sm:1:Sutram Error [...]` — no column field and no space — because `graph_print_file`/`mg_print_loc`
and `r49_print_module_location` are two different printers. Not a rename issue; noted for WS1's "two
format families" point.

### 3.2 CONFIRMED INCONSISTENT — the compiled-in Devanagari keyword aliases spell the **old** words

`kw_table` includes Devanagari alternates (comment: "Devanagari equivalents (optional script)"), compiled
in and active **without any pack**. Decoded:

| Line | Label | Bytes decode to | Maps to id | Current Latin keyword | Vocabulary's Devanagari for it |
|---|---|---|---|---|---|
| 706 | kw_dev_anyatra | अन्यत्र | KW_ANYATRA | `anya` | अन्य |
| 707 | kw_dev_pratiyati | प्रत्यायति | KW_PRATIYATI | `prati` | प्रति |
| 698 | kw_dev_pankti | पङ्क्ति | KW_PANKTI | `mala` | माला |
| 705 | kw_dev_prakriya | प्रक्रिया | KW_PRAKRIYA | `prakriya` | (unchanged) ✓ |
| 694–704 | mukhya, vitti, anka, yadi, yavat, kuru, dasham, kosh | मुख्य वित्ति अङ्क यदि यावत् कुरु दशम कोश | — | (unchanged) ✓ | ✓ |

The same is true of **`lang/sanskrit.lang`** (not the compiler file, but the same omission):

```
15: अन्यत्र anya        17: पुनरावर्तन chakra    18: प्रतियाति prati     25: उद्देश्य agrim
28: पङ्क्ति mala        29: सृजन ganana          30: निषेध abhava        32: आयोजन yoj
33: परिग्रह satya       35: पर्यन्त tak           40: निष्क्रिय yantra
```
i.e. every renamed keyword's Devanagari form is still the **pre-v157 word** (anyatra, punaravartana,
pratiyati, uddeshya, pankti, srijana, nishedha, ayojan, parigrah, nishkriya). Observed:

```
$ ./sutram_compiler --lang sanskrit dev_old.sm b.bin      # uses अन्यत्र
OK: compiled 334 bytes
$ ./sutram_compiler --lang sanskrit dev_new.sm a.bin      # uses अन्य, the vocabulary's spelling
Sutram Error: parse error at line 3:47 near token '}'
```

So a Sanskrit user writing in Devanagari must still type `अन्यत्र`, `पुनरावर्तन`, `प्रतियाति`, `आयोजन`…
while the vocabulary document — and the Hindi pack (`अन्यथा`, `पुनरावृत्ति`, `वापस`, `समावेश`) — have moved
on. Whether the Sanskrit pack *should* keep the fuller classical words is a language decision for Sarvam;
what is not in doubt is that **the compiler, the Sanskrit pack and the vocabulary table disagree with each
other** on the Devanagari spelling of eleven keywords. (The pack's line 70 `प॰ prati` abbreviation is
consistent with `prati`, so the pack was touched by the rename — just not these lines.)

### 3.3 Hardcoded spellings/lengths that are **CORRECT now** (listed so the sweep is complete)

| Line | Site | Assumes | Status |
|---|---|---|---|
| 2448–2451 | `expand_imports_pass .ei_check_ayojan` | `cmp word [rsi],0x6F79` + `cmp al,0x6A` = `yoj`, then `add r12,3` | **correct** (this is the one Sarvam fixed) |
| 7932–7938 | `parse_stmt` for-range | `cmp ecx,0x6174` + `cmp ecx,0x6B` + NUL = `tak` | **correct** (fixed); still a raw-byte compare rather than `kw_to_str` |
| 3705 | `mg_parse_ayojan` | `add r8,3 ; keyword is now "yoj"` | **correct** (fixed) |
| 3441, 3886 | `mg_parse_niryat`, `mg_scan_buf` | `add r8,6` = `niryat` | correct (`niryat` unchanged) |
| 3912 / 3909 | `mg_scan_buf` | `mov r8,8` = `prakriya`; `mov r8,27` = Devanagari `प्रक्रिया` (9 × 3 bytes) | correct |
| 3939 / 3948 | `mg_scan_buf` | `add r9,5` / `mov r8,5` = `sutra` | correct |
| 2257–2259 | `r49_print_module_location` | `niry` + `at` = `niryat` | correct |
| 5175–5192 | `ns_collect_funcs` | eight explicit byte compares `p r a k r i y a` | correct |
| 1278–1290 | `load_lang_file` | matches pack entries against `kw_to_str` (`tak`) by `strcmp` | correct |
| 7944–7952 | `parse_stmt` | native word for `tak` via `lang_to_word` (64-byte buffer) | correct |

No other immediates in the compiler or its includes spell letters (the remaining hits are operators
`&& || ++ += …`, `MZ`, `.text`, `.data` in the PE writer). I did **not** find a fourth stale constant of
the kind Sarvam found; the stale ones are 3.1 (a printer, so the suite could not catch it) and 3.2 (data,
so no gate compares it with the vocabulary).

### 3.4 Stale **comments** (no effect on behaviour)

`consume 'punaravartana'` (7907), `consume 'pratiyati'` (8241), "ayojan" in comments at 804, 831, 840,
912, 2207–2209, 2424, 2445, 2736. Cosmetic; listed because the brief asked for every site.

## 4. The same omission outside the compiler file

These are not in `src/sutram_compiler.asm`, but they are the direct consequence of the rename and they
are visible to a user, so I report them here rather than hide them in WS5.

### 4.1 CONFIRMED — both Linux IDEs highlight the **old** keywords and not the new ones

Set-diff of the compiler's 28 keywords against each highlighter's table:

| File | Table | Current keywords **not** highlighted | Old words still highlighted |
|---|---|---|---|
| `ide/sutram_ide.asm` 141–172 (`kw_count dq 31`) | 31 words | `abhava agrim anya chakra ganana mala prati satya tak yantra yoj` (11) | `anyatra ayojan nishedha nishkriya pankti parigrah pratiyati punaravartana srijana to uddeshya` (11) |
| `ide/sutram_gui_linux.asm` 194–198 | 26 words | the 11 above plus `bhavana sankhya` (13) | `anyatra ayojan pankti parigrah pratiyati punaravartana srijana uddeshya` (8) |
| `windows/gui/sutram_gui.asm` 333 | 17 words | (older still: has `anyatha`, `punar`, `phala`, `asatya` — a different vocabulary generation) | `ayojan nishkriya pratiyati` |

Observed in the terminal IDE (PTY, Ctrl-Q render of a 4-line file):
```
mukhya   '\x1b[95m'   <- keyword colour
yadi     '\x1b[95m'
krama    '\x1b[95m'
chakra   '\x1b[0m'    <- plain
tak      '\x1b[0m'
prati    '\x1b[0m'
anya     '\x1b[0m'
```
`tools/ide_test.py` reports "keyword colour: emitted" because its fixture uses `mukhya`/`likha`, which are
in both the old and new tables; it cannot detect this. (The `likha`/`grahan`/`shabda` entries in the IDE
tables are builtins, not keywords — harmless.)

### 4.2 CONFIRMED — the module-graph reference suite is broken by the rename: **6 PASS / 10 FAIL / 2 ERROR of 18**

`tools/module_graph_reference.py` was renamed (`IMPORT_RE` matches `yoj`, line 14), but its test file
`tests/module_graph/test_module_graph_reference.py` still builds fixtures with `ayojan …` and `pratiyati`
(lines 18–31 and onward). Every import line is therefore ignored by the model, so cycles are not
detected, orderings come back empty, and two tests error:

```
$ python3 -m unittest discover -s tests/module_graph -p 'test_*.py'
Ran 18 tests in 0.019s
FAILED (failures=10, errors=2)
  FAIL: test_cycle_reports_dependency_path      AssertionError: GraphDiagnostic not raised
  FAIL: test_deterministic_sibling_order        AssertionError: Lists differ: [] != ['d', 'c', 'b', 'a']
  FAIL: test_alias_conflict_diagnostic          AssertionError: GraphDiagnostic not raised
  ERROR: test_legacy_export_compatibility
  ERROR: test_private_not_visible
  ...
```
This is the suite the CHANGELOG historically reports as "module-graph 18/18" and that
`.github/workflows/r49-r50-native.yml`, `r53-integrated.yml`, `r54-native.yml`, `r55-native.yml`,
`r56-native.yml` run. It is not among the six commands in `PROJECT-MASTER.md` §11, which is why main is
"green" with it broken. `PROJECT-MASTER.md` §6 lists "Module graph | OK" — see WS3.

### 4.3 Nothing else

`grep -rlw` for the three old keywords across all code files finds only: the compiler (comments, §3.4),
the three IDE/GUI files (§4.1), and the one test file (§4.2). `tools/*.py` otherwise use the new names;
the 10 non-Sanskrit packs map their native words to the new names (checked with `grep` for the old Latin
names — none).

## 5. Observation outside the brief, stated as such

While probing 3.1 I noticed that a **misspelled or missing non-namespaced import is silently accepted**:
```
$ printf 'yoj ganit\nyoj nahi_hai\nmukhya() {\n    likha(1)\n}\n' > miss.sm && ./sutram_compiler miss.sm m.bin
OK: compiled 1750 bytes
```
The code says this is deliberate (`.ei_missing_module` 2875: "Legacy missing-module handling remains
unchanged" — only `module@alias` imports fail loudly). For a beginner the symptom of `yoj ganitt` is a
later `undefined function: varg`, not "module not found". Not a rename defect; raised because WS1 is
about what a non-English user sees when they make a mistake.

## 6. PASS / FAIL / NOT-RUN

| Check | Result |
|---|---|
| Immediate-spelling scan, compiler + 4 assembled includes | run; 1 stale site (3.1), 3 corrected sites, 9 correct sites |
| Devanagari alias decode vs vocabulary | run; 3 compiled-in + 11 pack entries use old words (3.2) |
| IDE keyword-table diff, 3 files | run; all 3 stale (4.1) |
| IDE highlight observation in a PTY | run; confirms 4.1 for `sutram-ide` |
| `windows/gui/sutram_gui.asm` behaviour | **NOT-RUN** (no Windows host); table contents read only |
| `tests/module_graph` suite | run; 6 PASS / 10 FAIL / 2 ERROR |
| `r71_*.inc` (not assembled by the canonical entry) | grepped only; no old spellings found; **NOT-RUN** |

## 7. What I did not do, and why

- Did not fix 3.1, 3.2, 4.1 or 4.2 — compiler and Sanskrit pack are ChatGPT's/Sarvam's; IDE is Sarvam's;
  the test file is a one-line `ayojan`→`yoj`, `pratiyati`→`prati` substitution that I left for the owner
  so that the fix and its re-run are recorded by the same party.
- Did not decide whether `lang/sanskrit.lang` *should* keep the classical words. That is the language
  directive's call; I only show the three sources disagree.
- Did not run the Windows GUI.
