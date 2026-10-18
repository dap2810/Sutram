# WS1 — Inventory of the compiler's user-facing strings

**Date:** 2026-10-18 · **Base:** main at v162, commit `feef075` · **Compiler built from:** `src/r68_compiler_entry.asm`
**Status:** inventory and proposals only. **Nothing in the compiler was changed.** Line numbers and quoted text are from `feef075`; `00-READ-FIRST-v164-REGRESSION.md` lists the 27 string lines v164 changed since (same line numbers, older text).

---

## 1. What I did

1. Built the compiler with the canonical entry and confirmed the baseline (see `README.md`, section
   "Baseline I measured").
2. Extracted **every `db` line that contains a quoted string** from `src/sutram_compiler.asm` and from the
   `.inc` files the canonical entry actually assembles (`r66_indic_lexer.inc`, `r67_stack_pair.inc`,
   `r68_diagnostics.inc`, `r68_unicode_helpers.inc`). **312 labels.** `win/rtblob.inc` and `win/winrt.inc`
   were checked separately: they contain only Win32 import names (`kernel32.dll`, `WriteFile`, …) — class
   (c), listed in §6.
3. For every label, found **every referencing line** and the **routine that contains it** (script output
   kept as `xref.txt`; the method is: nearest preceding `name:` label at column 0). From the routine I
   assigned the phase: driver / module-graph / import-expansion / lex / parse / codegen / **embedded
   runtime** (string is copied into the *generated program* and printed when that program runs).
4. Ran the compiler on deliberately broken inputs, with and without `--lang`, with `--check`, and with
   `SUTRAM_LANG`, and captured the bytes it actually wrote.
5. Classified each string (a) already Sanskrit, (b) still English, (c) code / identifier / path.

## 2. What I actually ran

```sh
nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/s.o && ld -o sutram_compiler /tmp/s.o
printf 'mukhya() {\n    vitti x = \n}\n' > bad.sm
./sutram_compiler bad.sm bad.bin
./sutram_compiler --lang hindi bad.sm bad.bin
./sutram_compiler --lang tamil bad.sm bad.bin
./sutram_compiler --check bad.sm
SUTRAM_LANG=hindi ./sutram_compiler --check bad.sm
./sutram_compiler --lang hindi --check bad.sm
./sutram_compiler --check --lang hindi bad.sm
./sutram_compiler /nonexistent.sm x.bin ; echo "exit=$?"
./sutram_compiler --lang hindi bad.sm bad.bin > hindi_err.txt 2>&1 ; xxd hindi_err.txt | head -3
./sutram_compiler bad.sm bad.bin > /dev/null        # is anything on stderr? (no)
printf 'mukhya() {\n    mala a[3]\n    vitti i = 5\n    a[i] = 1\n    likha(a[i])\n}\n' > oob.sm
./sutram_compiler oob.sm oob.bin && ./oob.bin ; echo "exit=$?"
printf 'mukhya() {\n    likha(foo(1))\n}\n' > undef.sm
./sutram_compiler undef.sm u.bin ; ./sutram_compiler --check undef.sm
```

## 3. What I observed (pasted)

**Default (no pack) — English, with a Hindi hint:**
```
Sutram Error: parse error at line 4:1 near token 'end of file'
  
  ^
Sanket: is sthan par shabd aur vyakaran dekho.
exit=1
```

**`--lang hindi` — the bytes written are double-encoded UTF-8 (mojibake), not Devanagari:**
```
$ xxd hindi_err.txt | head -3
00000000: 4268 6173 6861 2070 616b 206c 6f61 6420  Bhasha pak load
00000010: 6875 613a 2068 696e 6469 0a0a c3a0 c2a4  hua: hindi......
00000020: c2b8 c3a0 c2a5 c282 c3a0 c2a4 c2a4 c3a0  ................
```
`c3 a0 c2 a4 c2 b8` is the UTF-8 encoding of `Ã  Â¤ Â¸`, i.e. the UTF-8 bytes of `स` (`e0 a4 b8`)
re-encoded as if they were Latin-1. A terminal shows `à¤¸à¥à¤¤à¥à¤°à¤®à¥ à¤¤à¥à¤°à¥à¤à¤¿: ...`
instead of `सूत्रम् त्रुटि: पंक्ति 4:1 ...`. **The same is true for all 10 packs** (see F1).

**`--check` — a different format, always English, ignores the pack:**
```
bad.sm:3:1: Sutram Error [E_PARSE]: near '}'
  }
  ^
Sutram janch: dosh mile; nirgat binary nahi
exit=1
```
(Note the two modes also disagree on *where* the error is: normal mode says 4:1 at end-of-file,
`--check` says 3:1 at `}`. Both are defensible; they are just not the same.)

**`--lang hindi --check bad.sm` and `--check --lang hindi bad.sm`:**
```
Bhasha pak load hua: hindi
<mojibake of "त्रुटि: इनपुट फ़ाइल नहीं खुली">     <- it tried to open "--check" as the input file
exit=0
---
Error: cannot open input file                         <- it tried to open "--lang" as the input file
exit=0
```

**Missing input file exits 0:**
```
$ ./sutram_compiler /nonexistent.sm x.bin ; echo "exit=$?"
Error: cannot open input file
exit=0
```

**Runtime diagnostic inside the generated program (English, exit 1):**
```
$ ./oob.bin
Sutram Error: array index out of bounds
exit=1
```

**Undefined function — two different texts for the same error depending on mode:**
```
$ ./sutram_compiler undef.sm u.bin
Sutram Error: undefined function: foo
$ ./sutram_compiler --check undef.sm
undef.sm:2:11: Sutram Error [E_UNDEFINED_FUNCTION]: unknown function 'foo'
      likha(foo(1))
            ^
```

**Everything above is written to stdout (fd 1).** `print_str_z` (line 21831) always writes to fd 1;
redirecting stdout to `/dev/null` silences every diagnostic. Nothing is written to stderr.

## 4. Findings (confirmed unless marked otherwise)

**F1 — All 50 pack-localized diagnostic strings are double-UTF-8-encoded in the source.**
Lines 315–373 of `src/sutram_compiler.asm` define `err_line_*`, `err_near_*`, `err_eof_*`, `err_hint_*`,
`open_err_*` for bn/gu/hi/kn/ml/mr/or/pa/ta/te. Decoding each as UTF-8 → Latin-1 bytes → UTF-8 recovers
clean text in the right script for all 50 (I checked each one; the recovered text is in §5.8). So the
*intent* is right and the *bytes in the file* are wrong — a file was saved as UTF-8 once too many.
Because the compiler copies these bytes verbatim, **a user who selects a pack and makes a syntax error sees
mojibake**, which is worse than English. No test covers this: no golden under `tests/expect/` contains a
localized error, and the five `LANG` entries in `tests/run_tests.py` are all programs that compile
cleanly. *Fix is mechanical (re-encode the 50 lines) but the file is ChatGPT's; I did not touch it.*

**F2 — Two Tamil strings contain Gujarati letters.** After un-doubling, `err_hint_ta` (line 366) and
`open_err_ta` (line 367) contain U+0AAA `પ` (Gujarati PA) where Tamil U+0BAA `ப` is meant — three
occurrences: `குறிપு`, `சரிપார்க்கவும்`, `கோપ்પை`. The other eight Tamil/other-script strings are
single-script.

**F3 — The localization mechanism exists, but Sanskrit (the default) gets English.** `cur_lang_id`
(line 400) indexes five 11-entry tables (`tbl_err_line`, `tbl_err_near`, `tbl_err_eof`, `tbl_err_hint`,
`tbl_open_err`, lines 376–385) through `pick_lang_str` (line 6718). Slot 0 is "default" and holds the
English strings. `set_lang_id` (6723) matches only the ten names at lines 389–398; `sanskrit` is not among
them, so `--lang sanskrit` and plain Sanskrit both print English. Only **5 message families** go through
this table; the other ~95 user-facing strings are printed directly.

**F4 — `--check` mode bypasses the table entirely.** `parse_error` (6757) jumps to
`_start.r48_parse_failure` when `r48_mode` is set, and `r48_print_parse_error` (7075) prints the fixed
English `r48_msg_near`. So even where localization exists it does not reach the IDE/check path.

**F5 — `--check` and `--lang` cannot be combined** in either order (observed above; the arg parser at
1897–1935 takes `argv[1]` as the mode and `argv[2]` as the file). The only way to combine them is
`SUTRAM_LANG=<pack>` — which, per F4, then has no effect on the diagnostic text anyway.

**F6 — "cannot open input file" exits with status 0.** `read_file` (5723) prints and jumps to `do_exit`
(2044), which does `xor rdi, rdi; call os_exit`. Any script or IDE that relies on the exit status will
treat a missing input as success. Same path for `--check`.

**F7 — All diagnostics go to stdout.** See above. Not necessarily wrong, but tooling (and the IDE) cannot
separate program output from compiler diagnostics by stream.

**F8 — Eight strings are dead** (defined, never referenced): `r54_msg_arity` (227), `msg_parse_err` (452),
`msg_guna_dbg1/2/3` (714–716, debug leftovers `"G1"`, `"BAD\n"`, `"LK"`), `graph_msg_limit` (767),
`graph_arrow` (771), `graph_limit_prefix` (778). (`r54_msg_arity` is the generic arity message; the four
specific arity messages at 223–226 are what is actually used.)

**F9 — The version banner says v160** (`msg_version`, line 215: `"Sutram 1.0 (v160) - sampurna sutra"`)
while main is v162 and `CHANGELOG.md`'s top entry is v162.

**F10 — The "Sanskrit" strings are mostly romanized Hindi, not Sanskrit.** *This is an observation about
register, stated plainly because the directive says every new identifier must be Sanskrit.* `dekho`,
`dabao`, `mile`, `nahi`, `hua`, `lete hain`, `is sthan par`, `ke paas` are Hindi verb forms and
postpositions. The nouns (`dosh`, `sanket`, `pankti`, `prakriya`, `paribhasha`, `vyakaran`, `nirgat`,
`janch`, `bhasha`, `sankalan`) are shared by Sanskrit and Hindi. I have marked these strings **(a)** in the
tables because they are not English, but Sarvam should decide whether "Sanskrit" for diagnostics means
Sanskrit grammar or Hindi-with-Sanskrit-nouns. My proposals in §5 deliberately use **noun-only templates**
(no verbs, no postpositions) so that they read the same in either register and translate cleanly into the
packs.

**F11 — `docs/sutram-vocabulary.html` already lists renamed error codes and flags that the code does not
have.** Its "Error codes and CLI flags" table says E_PARSE→**E_VYAKARAN**, E_UTF8→**E_LIPI**,
E_UNDEFINED_FUNCTION→**E_AGYAT**, E_MODULE_CYCLE→**E_CHAKRA**, E_UNSAFE_BOUNDARY→**E_SEEMA**,
E_INTEGER_TRAP→**E_ANK_DOSH**, and `--check`→**`--janch`**, `--lang`→**`--bhasha`**,
`--version`→**`--sanskaran`**. The compiler still emits E_PARSE etc. and accepts only `--check`, `--lang`,
`--version`. If that table is a plan, it should say so; if it is a claim, it is wrong. I used its names in
my proposals below because they are the frozen vocabulary.

**F12 — In normal mode, the parse-error line number is wrong whenever the program imports a module.**
Found while writing WS4. `parse_error` reports the line within the *expanded* buffer (after `yoj`
inlining), not the user's file; `--check` mode maps back through the R51 origin table and is right:
```
$ printf 'yoj ganit\nmukhya() {\n    vitti x = \n}\n' > lineno.sm
$ ./sutram_compiler lineno.sm l.bin
Sutram Error: parse error at line 169:1 near token 'end of file'     <- lib/ganit.smlib is 163 lines
$ ./sutram_compiler --check lineno.sm
lineno.sm:4:1: Sutram Error [E_PARSE]: near '}'
```
For the 214-line WS4 program the normal-mode error said line **2020**; `--check` said **175**, which was
right. Since `sutram in.sm out.bin` is the command every document teaches, a beginner who uses the
library gets a line number that points nowhere. (Language of the message aside, this is the single
thing I would fix first.)

## 5. The inventory

Columns: **Line** (in `src/sutram_compiler.asm` unless prefixed), **Label**, **Text as in source**,
**Class**, **Phase / routine**, **Proposed Sanskrit** (only for (b)). Placeholders: `N` number, `X` name,
`F` file. Proposals keep code tags (`[E_…]`), paths and identifiers unchanged.

Glossary used in proposals (all already present in the repo's vocabulary or strings): `dosh` error ·
`vyakaran` syntax · `pankti` line · `patra` file · `prakriya` function · `tark` argument · `avashyak`
required · `agyat` unknown · `punah` again/duplicate · `seema` limit · `atikram` exceeded · `rikta` empty ·
`upanaam` alias · `niryat` export · `yoj` import · `paribhasha` definition · `ghoshana` declaration ·
`bhinn` differs · `mulya` value · `lipi` script/encoding · `srot` source · `nivesh` input · `nirgat` output ·
`sankalan` compile · `siddh` done/ok · `sanskaran` version · `prayog` usage · `shabd` token/word ·
`patra-ant` end of file · `samip` near.

### 5.1 Driver (`_start`, `read_file`, `try_load_lang`) — printed by the compiler process

| Line | Label | Text | Class | Phase | Proposed |
|---|---|---|---|---|---|
| 208 | msg_usage | `Sutram - sampurna sutra` | a | driver | — |
| 209 | msg_usage | `Usage:` | **b** | driver | `Prayog:` |
| 210 | msg_usage | `  sutram <input.sm> <output.bin>          compile` | **b** (`compile`); `<input.sm>`/`<output.bin>` are (c) | driver | `sutram <nivesh.sm> <nirgat.bin>   sankalan` |
| 211 | msg_usage | `  sutram --check <input.sm>  parse/check, no output binary` | **b** | driver | `sutram --check <nivesh.sm>   janch matra, nirgat nahi` |
| 212 | msg_usage | `  sutram --lang <pack> <in.sm> <out.bin>  with language pack` | **b** | driver | `sutram --lang <pak> <nivesh.sm> <nirgat.bin>   bhasha pak sahit` |
| 213 | msg_usage | `  sutram -i   interactive shell` | **b** | driver | `sutram -i   khol (samvad)` |
| 214 | msg_usage | `  sutram --version   version info` | **b** | driver | `sutram --version   sanskaran` |
| 215 | msg_version | `Sutram 1.0 (v160) - sampurna sutra` | a, **but v160 is stale (F9)** | driver | update number |
| 216 | msg_version | `Samskrita-mukhya bhasha -> x86-64 yantra-code` | a | driver | — |
| 220 | r48_msg_ok | `Sutram janch: OK (nirgat binary nahi)` | a (`OK`, `binary` are loanwords) | driver, `--check` success | optionally `Sutram janch: siddh (nirgat nahi)` |
| 221 | r48_msg_errors | `Sutram janch: dosh mile; nirgat binary nahi` | a (Hindi verb, F10) | driver + `backpatch_calls` 10658 | optionally `Sutram janch: dosh; nirgat nahi` |
| 402 | msg_lang_ok | `Bhasha pak load hua: ` | **b** (`load`) | driver, `try_load_lang` 1154 | `Bhasha pak prapt: ` |
| 403 | msg_lang_fail | `Chetavani: bhasha pak nahi mila: ` | a (F10) | driver, 1142 | — |
| 451 | msg_open_err | `Error: cannot open input file` | **b** | driver, `read_file` 5731 via `tbl_open_err[0]` | `Dosh: nivesh patra aprapt` |
| 453 | msg_ok | `OK: compiled ` | **b** | driver, 2034 | `Siddh: ` |
| 454 | msg_bytes | ` bytes` | **b** | driver, 2041 | ` byte sankalit` (byte is a loanword in every pack) |
| 452 | msg_parse_err | `Error: parse error at token ` | **b**, **dead (F8)** | — | delete |

### 5.2 Module graph pre-pass (`check_module_graph`, `mg_*`, `graph_*`; runs before `expand_imports`)

| Line | Label | Text | Class | Phase | Proposed |
|---|---|---|---|---|---|
| 764 | graph_v1_header | `# sutram-module-v1` | c (file marker) | module-graph | — |
| 765 | graph_msg_cycle | `E_MODULE_CYCLE` | c (code) | `mg_print_cycle` 4096 | keep; vocabulary says `E_CHAKRA` (F11) |
| 766 | graph_msg_missing | `E_MODULE_MISSING` | c | `mg_process_imports` 4279 | keep |
| 767 | graph_msg_limit | `E_MODULE_LIMIT` | c, **dead** | — | — |
| 768 | graph_msg_invalid | `E_MODULE_INVALID` | c | 4252 | keep |
| 769 | graph_prefix | `: Sutram Error [` | **b** (`Error`) | `graph_error` 2346, `mg_print_cycle` | `: Sutram dosh [` |
| 770 | graph_close | `]: ` | c | | — |
| 771 | graph_arrow | ` -> ` | c, **dead** | | — |
| 772 | graph_colon | `:` | c | | — |
| 773 | r49_unknown_column | `?` | c | | — |
| 774 | r51_unknown_origin | `:?:?` | c | | — |
| 776 | graph_cycle_prefix | `dependency cycle: ` | **b** | `mg_print_cycle` 4100/4113 | `yoj chakra: ` |
| 777 | graph_missing_prefix | `cannot open import ` | **b** | 4280 | `yoj patra aprapt: ` |
| 778 | graph_limit_prefix | `too many modules or oversized module` | **b**, **dead** | — | delete |
| 779 | graph_invalid_prefix | `invalid module name` | **b** | 4253 | `ashuddh module naam` |
| 2926 | mg_e_cycle | `Sutram Error [E_MODULE_CYCLE]: cyclic import: ` | **b** (text) / c (code) | 4118 | `Sutram dosh [E_MODULE_CYCLE]: yoj chakra: ` |
| 2927–2929 | mg_e_noexp1..3 | `Sutram Error [E_MODULE_NOT_EXPORTED]: '` X `' is not exported by module '` M `'` | **b** | `mg_check_edge` 4691, `mg_check_qualified` 4866 | `Sutram dosh [E_MODULE_NOT_EXPORTED]: 'X' module 'M' se aniryat` |
| 2930–2932 | mg_e_dupexp1..3 | `… [E_MODULE_DUP_EXPORT]: duplicate export '` X `' in module '` M `'` | **b** | `mg_parse_niryat` 3500 | `… [E_MODULE_DUP_EXPORT]: punah niryat 'X', module 'M'` |
| 2933–2935 | mg_e_undef1..3 | `… [E_EXPORT_UNDEFINED]: export '` X `' has no matching definition in module '` M `'` | **b** | `mg_verify_exports` 3672 | `… [E_EXPORT_UNDEFINED]: niryat 'X' paribhasha-rahit, module 'M'` |
| 2936–2938 | mg_e_unknown1..3 | `… [E_EXPORT_UNDEFINED]: unknown qualified symbol '` X `' in module '` M `'` | **b** | `mg_check_qualified` 4876 | `… [E_EXPORT_UNDEFINED]: agyat sanket 'X', module 'M'` |
| 2940 | mg_e_depth | `Sutram Error [E_MODULE_DEPTH]: import depth exceeded` | **b** | `mg_visit` 4408 | `Sutram dosh [E_MODULE_DEPTH]: yoj gahrai seema atikram` |
| 2941 | r51_colon_space | `: ` | c | | — |
| 2942–2944 | mg_e_valias1..3 | `… [E_MODULE_V1_ALIAS]: v1 module '` X `' must be imported with an alias: yoj ` X `@alias` | **b** | `mg_valias_error` 4011 | `… [E_MODULE_V1_ALIAS]: v1 module 'X' upanaam avashyak: yoj X@upanaam` |
| 2945 | mg_e_limit | `Sutram Error [E_MODULE_LIMIT]: too many modules or imports` | **b** | `mg_visit` 4413 | `Sutram dosh [E_MODULE_LIMIT]: module/yoj seema atikram` |
| 2946 | mg_root_name | `__root__` | c | | — |
| 2947 | mg_v1_mark | `sutram-module-v1` | c | | — |
| 2948 | mg_arrow | ` -> ` | c | 4146 | — |
| 2949 | mg_colon | `:` | c | | — |
| 2939, 2950–2952 | mg_w_sutra/niryat/prakriya/ayojan | `sutra` `niryat` `prakriya` `yoj` | c (keyword scan) | | — |

### 5.3 Import expansion (`expand_imports`, `expand_imports_pass`, `ns_*`; textual inclusion before lex)

| Line | Label | Text | Class | Phase | Proposed |
|---|---|---|---|---|---|
| 758 | msg_namespace_error | `Sutram Error: invalid namespaced yoj (use module@alias, max 31 alias bytes)` | **b** | `expand_imports_pass` 2883 | `Sutram dosh: ashuddh yoj (roop: module@upanaam, upanaam ≤ 31 byte)` |
| 759 | msg_namespace_module_missing | `Sutram Error: namespaced module file not found` | **b** | 2878 | `Sutram dosh: module patra aprapt` |
| 760 | msg_namespace_alias_reuse | `Sutram Error: namespaced alias already assigned to another module` | **b** | 2678 | `Sutram dosh: upanaam purv-niyukt (anya module)` |
| 761 | r51_alias_conflict | `: Sutram Error [E_MODULE_ALIAS_REUSE]: namespaced alias already assigned to another module` | **b** | 2672 | `: Sutram dosh [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya module)` |
| 762 | msg_namespace_func_limit | `Sutram Error: namespaced module has too many or oversized function names` | **b** | `ns_collect_funcs` 5301 | `Sutram dosh: module prakriya-naam seema atikram` |
| 763 | msg_import_overflow | `Sutram Error: expanded module source too large` | **b** | `expand_imports` 2395, 2888, `ns_emit_byte` 5518, `r51_register_module` 5594 | `Sutram dosh: vistarit srot seema atikram` |

### 5.4 Lexer and pre-lex (`r68_prelex_validate`, `lex`)

| Line | Label | Text | Class | Phase | Proposed |
|---|---|---|---|---|---|
| r68_diagnostics.inc:7 | r68_utf8_prefix | `Sutram Error [E_UTF8]: ` | **b**/c | pre-lex, `r68_prelex_validate` 109 | `Sutram dosh [E_UTF8]: ` (vocabulary: `E_LIPI`) |
| r68_diagnostics.inc:9 | r68_utf8_tail | `: invalid or truncated UTF-8 in source code` | **b** | 111 | `: srot me ashuddh/khandit UTF-8` |
| r68_diagnostics.inc:17 | r68_colon | `:` | c | `r68_report_error` 187 | — |
| r66_indic_lexer.inc:11 | r66_msg_bad_utf8 | `Sutram Error [E_UTF8]: invalid or truncated Indic identifier` | **b** | `lex` 5892 | `Sutram dosh [E_UTF8]: ashuddh/khandit bharatiya naam` |

### 5.5 Parser (`parse_*`, `alloc_ast`, `r55_register_proto`, `r56_register_global`, `r68_guard_value_start`)

| Line | Label | Text | Class | Phase | Proposed |
|---|---|---|---|---|---|
| 278 | msg_err_line | `\nSutram Error: parse error at line ` | **b** | `parse_error` 6759 via `tbl_err_line[0]` | `\nSutram dosh [E_VYAKARAN]: pankti ` |
| 279 | msg_err_near | ` near token '` | **b** | 6777 via `tbl_err_near[0]` | `, shabd '` |
| 280 | msg_err_end | `'` + newline | c | 6831 | — |
| 281 | msg_err_eof | `end of file` | **b** | 6826 via `tbl_err_eof[0]` | `patra-ant` |
| 282 | msg_err_hint | `Sanket: is sthan par shabd aur vyakaran dekho.` | a (Hindi, F10) | 6847 via `tbl_err_hint[0]` | noun form: `Sanket: shabd va vyakaran janch.` |
| 283 | msg_err_colon | `:` | c | | — |
| 284, 285, 288 | msg_diag_indent/space/caret | `  `, ` `, `^` | c | `print_source_context`, `r51_print_original_context` | — |
| 289 | msg_err_arg_limit | `Sanket: prakriya adhiktam 6 tark lete hain.` | a (Hindi verb) | `parse_error` 6837 | `Sanket: prakriya tark seema 6.` |
| 290 | msg_err_duplicate_func | `Sanket: dohri prakriya paribhasha (naam takkar).` | a (`dohri`, `takkar` are Hindi) | 6843 | `Sanket: punah prakriya paribhasha (naam sangharsh).` |
| 291 | msg_duplicate_func | `Sutram Error: duplicate function definition: ` | **b** | `parse_function` 6558 | `Sutram dosh: punah prakriya paribhasha: ` |
| 218 | r48_msg_near | `: Sutram Error [E_PARSE]: near '` | **b** | `--check` only, `r48_print_parse_error` 7080 | `: Sutram dosh [E_VYAKARAN]: shabd '` |
| 219 | r48_msg_end | `'` + newline | c | 7123, 7050 | — |
| 222 | r48_msg_eof | `<EOF>` | c-ish | 7120 | `<patra-ant>` if 281 changes |
| 780 | msg_ast_overflow | `Sutram Error: AST capacity exceeded` | **b** | `alloc_ast` 6464 | `Sutram dosh: AST seema atikram` |
| 781 | msg_func_params_overflow | `Sutram Error: function parameter table capacity exceeded` | **b** | `parse_stmt` 7868 | `Sutram dosh: prakriya tark-suchi seema atikram` |
| 785 | msg_func_defs_overflow | `Sutram Error: function definition table capacity exceeded` | **b** | `parse_function` 6534/6581, `gen_stmt` 10790 | `Sutram dosh: prakriya-suchi seema atikram` |
| 789 | msg_rachana_overflow | `Sutram Error: rachana table capacity exceeded` | **b** | `parse_stmt` 8355 | `Sutram dosh: rachana-suchi seema atikram` |
| 790 | msg_rachana_fields_overflow | `Sutram Error: too many fields in rachana` | **b** | 8358 | `Sutram dosh: rachana kshetra seema atikram` |
| 791 | msg_block_nesting_overflow | `Sutram Error: block nesting capacity exceeded` | **b** | `parse_block` 7414 | `Sutram dosh: khand gahrai seema atikram` |
| 792 | msg_block_stmt_overflow | `Sutram Error: too many statements in block` | **b** | `parse_func_block` 6679, `parse_block` 7402 | `Sutram dosh: khand kathan seema atikram` |
| 793 | r55_msg_proto_duplicate | `Sutram Error: duplicate prakriya forward declaration` | **b** | `r55_register_proto` 10219 (called from `parse_function` 6546) | `Sutram dosh: punah prakriya purv-ghoshana` |
| 794 | r55_msg_proto_missing | `Sutram Error: prakriya forward declaration has no definition` | **b** | `r55_validate_prototypes` 10283 (called 6586, end of parse) | `Sutram dosh: prakriya purv-ghoshana paribhasha-rahit` |
| 795 | r55_msg_proto_signature | `Sutram Error: prakriya prototype signature (arity/type) differs from definition` | **b** | 10286 | `Sutram dosh: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar)` |
| 796 | r55_msg_proto_capacity | `Sutram Error: too many prakriya prototypes` | **b** | 10222 | `Sutram dosh: prakriya purv-ghoshana seema atikram` |
| 797 | r56_msg_global_capacity | `Sutram Error: too many module-level vitti variables` | **b** | `r56_register_global` 20474 (called 6518) | `Sutram dosh: module-star vitti seema atikram` |
| 798 | r56_msg_global_duplicate | `Sutram Error: duplicate module-level vitti name` | **b** | 20471 | `Sutram dosh: punah module-star vitti naam` |
| r68_diagnostics.inc:11 | r68_value_prefix | `Sutram Error [E_ABBREVIATION_VALUE]: ` | **b**/c | `r68_guard_value_start` 151 (wrapped around `parse_primary`) | `Sutram dosh [E_ABBREVIATION_VALUE]: ` |
| r68_diagnostics.inc:13 | r68_value_tail | `: abbreviation keyword is not a value: '` | **b** | 153 | `: sankshep shabd mulya nahi: '` |

### 5.6 Code generation (`gen_*`, `emit_byte`, `backpatch_calls`, `mark_*`, `alloc_var`) — compile-time

| Line | Label | Text | Class | Phase | Proposed |
|---|---|---|---|---|---|
| 223 | r50_msg_setchar_arity | `Sutram Error: akshar_rakh requires exactly 3 arguments` | **b** | `gen_expr` 15525 | `Sutram dosh: akshar_rakh: 3 tark avashyak` |
| 224 | r52_msg_dvaram_arity | `Sutram Error: dvaram requires 2 or 3 arguments` | **b** | 14072 | `Sutram dosh: dvaram: 2 va 3 tark avashyak` |
| 225 | r52_msg_charat_arity | `Sutram Error: akshar requires exactly 2 arguments` | **b** | 15559 | `Sutram dosh: akshar: 2 tark avashyak` |
| 226 | r52_msg_charcode_arity | `Sutram Error: aksharank requires 1 or 2 arguments` | **b** | 15603 | `Sutram dosh: aksharank: 1 va 2 tark avashyak` |
| 227 | r54_msg_arity | `Sutram Error: builtin argument count does not match signature` | **b**, **dead** | — | delete or wire up |
| 277 | r48_msg_undefined | `: Sutram Error [E_UNDEFINED_FUNCTION]: unknown function '` | **b** | `--check`, `r48_print_undefined_function` 7046 (from `backpatch_calls`) | `: Sutram dosh [E_AGYAT]: agyat prakriya '` |
| 292 | msg_undefined_func | `Sutram Error: undefined function: ` | **b** | `backpatch_calls` 10635; fallback 7057 | `Sutram dosh: agyat prakriya: ` |
| 294 | msg_kosh_required | `Sutram Error: kosh builtin requires a kosh variable` | **b** | `gen_expr` 13926 | `Sutram dosh: kosh prakriya hetu kosh-vitti avashyak` |
| 309 | msg_kosh_param_type | `Sutram Error: kosh parameter requires matching kosh element type` | **b** | `gen_typed_call_arg` 18439 | `Sutram dosh: kosh tark: tatv prakar bhinn` |
| 310 | msg_kosh_param_push | `Sutram Error: kosh_push on a kosh parameter is not supported` | **b** | `gen_expr` 13919 | `Sutram dosh: kosh tark par kosh_push asamarthit` |
| 782 | msg_var_table_overflow | `Sutram Error: variable table capacity exceeded` | **b** | `alloc_var` 18854, `mark_*` 17886/18619/18671/18723, `gen_all_functions` 10519 | `Sutram dosh: vitti-suchi seema atikram` |
| 783 | msg_func_table_overflow | `Sutram Error: function table capacity exceeded` | **b** | `gen_all_functions` 10559 | `Sutram dosh: prakriya-suchi seema atikram` |
| 784 | msg_patch_overflow | `Sutram Error: call patch table capacity exceeded` | **b** | `gen_stmt` 10924, `gen_expr` 13024 | `Sutram dosh: aahvan-suchi seema atikram` |
| 786 | msg_break_patch_overflow | `Sutram Error: too many break statements in active loops` | **b** | `gen_stmt` 12145 | `Sutram dosh: chakra me krama seema atikram` |
| 787 | msg_continue_patch_overflow | `Sutram Error: too many continue statements in active loops` | **b** | 12164 | `Sutram dosh: chakra me agrim seema atikram` |
| 788 | msg_code_overflow | `Sutram Error: generated code capacity exceeded` | **b** | `emit_byte` 9993 | `Sutram dosh: yantra-code seema atikram` |
| 799 | r56_msg_patch_capacity | `Sutram Error: too many global data references` | **b** | `r56_record_patch` 20541 | `Sutram dosh: sarvatrik data sandarbh seema atikram` |

### 5.7 Embedded runtime — copied into the **generated program**, printed when *it* runs

These are what an end user of a compiled Sutram program sees; they are not compiler output.

| Line | Label | Text | Class | Emitted by | Proposed |
|---|---|---|---|---|---|
| 293 | msg_array_oob | `Sutram Error: array index out of bounds` | **b** | `emit_array_bounds_check` 12658 (as an AST_STR → `likha`) | `Sutram dosh: mala ank seema atikram` |
| 306 | msg_kosh_empty | `Sutram Error: kosh pop from empty array` | **b** | `emit_kosh_empty_check_r9` 12708 | `Sutram dosh: rikta kosh se kosh_pop` |
| 307 | msg_kosh_peek_empty | `Sutram Error: kosh peek from empty array` | **b** | 12711 | `Sutram dosh: rikta kosh se kosh_peek` |
| 308 | msg_kosh_dequeue_empty | `Sutram Error: kosh dequeue from empty array` | **b** | 12716 | `Sutram dosh: rikta kosh se kosh_dequeue` |
| 296 | r65_msg_prefix | `Sutram Error [E_INTEGER_TRAP] ` | **b**/c | `r65_emit_fatal` 21493 — **only when built with `-DSUTRAM_R65_TRAP_INT=1`; not in the canonical build** | `Sutram dosh [E_ANK_DOSH] ` |
| 297 | r65_msg_colon | `:` | c | | — |
| 298 | r65_msg_add | `: signed addition overflow` | **b** | opt-in build, `gen_expr` 17622 | `: yog atipravah` |
| 299 | r65_msg_sub | `: signed subtraction overflow` | **b** | 17635 | `: nyun atipravah` |
| 300 | r65_msg_mul | `: signed multiplication overflow` | **b** | 17650 | `: gun atipravah` |
| 301 | r65_msg_div | `: division by zero` | **b** | 17664 | `: shunya se bhajan` |
| 302 | r65_msg_mod | `: remainder by zero` | **b** | 17459, 21674 | `: shunya se shesh` |
| 303 | r65_msg_div_overflow | `: signed division overflow` | **b** | 21676 | `: bhajan atipravah` |
| 304 | r65_msg_mod_overflow | `: signed remainder overflow` | **b** | 21678 | `: shesh atipravah` |

Note on **division by zero in the canonical build**: without the R65 flag there is no message at all; the
program takes the CPU's `#DE` and dies with SIGFPE. That is a separate (Gate 4) question, not a string.

### 5.8 The pack-localized set (lines 315–373) — class **(a) in intent, broken in bytes (F1)**

Reachable only via `--lang <pack>` or `SUTRAM_LANG`, only for the 10 non-Sanskrit packs, only on the
normal (non-`--check`) path. Recovered text after un-doubling; `✗` marks the Tamil script mix (F2).

| Pack | err_line | err_near | err_eof | err_hint | open_err |
|---|---|---|---|---|---|
| bn 315–319 | সূত্রম্ ত্রুটি: পংক্তি | এর কাছে টোকেন ' | ফাইলের শেষ | পরামর্শ: এই স্থানের কাছে কূটশব্দের বানান ও সিন্ট্যাক্স পরীক্ষা করুন। | ত্রুটি: ইনপুট ফাইল খোলা যাচ্ছে না |
| gu 321–325 | સૂત્રમ્ ભૂલ: પંક્તિ | નજીક ટોકન ' | ફાઇલનો અંત | સંકેત: આ સ્થળની નજીક કૂટશબ્દની જોડણી અને વાક્યરચના ચકાસો. | ભૂલ: ઇનપઁટ ફાઇલ ખૂલી શકી નહીં |
| hi 327–331 | सूत्रम् त्रुटि: पंक्ति | के पास टोकन ' | फ़ाइल का अंत | संकेत: इस स्थान के पास कूटशब्द की वर्तनी और वाक्य-रचना जाँचें। | त्रुटि: इनपुट फ़ाइल नहीं खुली |
| kn 333–337 | ಸೂತ್ರಮ್ ದೋಷ: ಸಾಲು | ಬಳಿ ಟೋಕನ್ ' | ಕಡತದ ಅಂತ್ಯ | ಸೂಚನೆ: ಈ ಸ್ಥಳದ ಬಳಿ ಕೀವರ್ಡ್ ಕಾಗುಣಿ ಮತ್ತು ಸಿಂಟ್ಯಾಕ್ಸ್ ಪರಿಶೀಲಿಸಿ. | ದೋಷ: ಇನ್‌ಪುಟ್ ಕಡತ ತೆರೆಯಲಾಗುತ್ತಿಲ್ಲ |
| ml 339–343 | സൂത്രം പിശക്: വരി | ന്റ്റെ അടുത്ത് ടോക്കണ് ' | ഫയലിന്റെ അവസാനം | സൂചന: ഈ സ്ഥലത്തിനടുത്ത് കീവേഡ് അക്ഷരവിന്യാസവും വാക്ക്യഘടനയും പരിശോധിക്കുക. | പിശക്: ഇൻപുട്ട് ഫയൽ തുറക്കാനായില്ല |
| mr 345–349 | सूत्रम् त्रुटी: ओळ | च्या जवळ टोकन ' | फाइलचा शेवट | सूचना: या जागी कूटशब्दाची शुद्धलेखन आणि वाक्यरचना तपासा. | त्रुटी: इनपुट फाइल उघडता आली नाही |
| or 351–355 | ସୂତ୍ରମ୍ ତ୍ରୁଟି: ଧାଡ଼ି | ପାଖରେ ଟୋକେନ୍ ' | ଫାଇଲର ଶେଷ | ସୂଚନା: ଏହି ସ୍ଥାନ ପାଖରେ କୀଵାର୍ଡ୍ର ବନାନ ଓ ସିଣ୍ଟାକ୍ସ ଯାଞ୍ଚ କରନ୍ତୁ। | ତ୍ରୁଟି: ଇନପୁଟ୍ ଫାଇଲ୍ ଖୋଲିହେଲା ନାହିଁ |
| pa 357–361 | ਸੂਤਰਮ੍ ਗਲਤੀ: ਲਾਈਨ | ਦੇ ਨੇੜੇ ਟੋਕਨ ' | ਫਾਈਲ ਦਾ ਅੰਤ | ਸੰਕੇਤ: ਇਸ ਥਾਂ ਦੇ ਨੇੜੇ ਕੂਟਸ਼ਬਦ ਦੀ ਸਪੈਲਿੰਗ ਅਤੇ ਸੰਟੈਕਸ ਜਾਂਚੋ। | ਗਲਤੀ: ਇਨਪੁਟ ਫਾਈਲ ਨਹੀਂ ਖੁੱਲ੍ਹੀ |
| ta 363–367 | சூத்திரம் பிழை: வரி | அருகில் டோக்கன் ' | கோப்பின் முடிவு | ✗ குறிપு: … சரிપார்க்கவும். | ✗ பிழை: உள்ளீட்டுக் கோપ்પை திறக்க முடியவில்லை |
| te 369–373 | సూత్రమ్ దోషం: వరుస | దగ్గర టోకెన్ ' | దస్త్రం ముగింపు | సూచన: ఈ స్థలం దగ్గర కీలకపద వర్ణన, సింటాక్స్ తనిఖీ చేయండి. | దోషం: ఇన్‌పుట్ దస్త్రం తెరవబడలేదు |

### 5.9 Interactive shell (`shell_main`, `-i`) — class (a) except where noted

| Line | Label | Text | Class |
|---|---|---|---|
| 436–438 | msg_shell_banner | `Sutram khol v1.0 - sampurna sutra` / `Sutram kathan likho aur Enter dabao. Turant chalega.` / `Aadesh: sahayata (sahay) \| nirgat (nikas) \| sarvam (dekho)` | a (Hindi, F10); `Enter` is a key name (c) |
| 439 | msg_shell_prompt | `sutra> ` | a |
| 440 | msg_shell_bye | `Namaste! Satra samapt.` | a |
| 441–448 | msg_shell_help | `Sutram khol sahay:` + 7 example lines (`likha paath`, `char ghoshan`, `vyakti likha`, `aavartan`, `mala ghoshan`, `pura karyakram dekho`, `khol se nikal`) | a |
| 430–435 | str_exit1..3, str_help1..2, str_sarvam | `nirgat` `exit` `quit` `sahayata` `help` `sarvam` | c (accepted commands; `exit`/`quit`/`help` are English aliases, kept deliberately I assume) |
| 449–450 | repl_prog_hdr/ftr | `mukhya() {` / `}` | c |
| 419–428 | str_repl_in/out, str_repl_quote/space | temp paths | c |

### 5.10 Pure code / identifier / path strings — class (c), listed for completeness

207 `.exe` · 217 `--check` · 405–409 `-i` `--shell` `--version` `-v` `--lang` · 410–415 `SUTRAM_LANG=`
`HOME=` `lang/` `.lang` `/.local/share/sutram/lang/` `/proc/self/exe` · 389–398 the ten pack names ·
423–425 Win32 import names · 664–691 the 28 keyword spellings (`kw_*`) · 709–756 the 48 builtin names
(`bn_*`) · 574–658 `grahan_*_tail`, `float_print_prefix_bytes` (machine-code templates, not text) ·
`win/winrt.inc` 429–445 (`ntdll.dll`, `kernel32.dll`, `LdrLoadDll`, `GetStdHandle`, `WriteFile`,
`ReadFile`, `CreateFileA`, `CloseHandle`, `VirtualAlloc`, `ExitProcess`, `GetCommandLineA`) ·
`win/rtblob.inc` (bytes only).

Dead debug strings (F8): 714–716 `msg_guna_dbg1..3` = `"G1"`, `"BAD\n"`, `"LK"`.

## 6. Totals (counted from the tables above, not from memory)

| | Count |
|---|---|
| Text strings a user can see, default build, compiler process (dead ones excluded) | **80** (5.1: 16 · 5.2: 12 · 5.3: 6 · 5.4: 3 · 5.5: 23 · 5.6: 16 · 5.9: 4) |
| — of which **(b) still English** | **67** (5.1: 10 · 5.2: 12 · 5.3: 6 · 5.4: 3 · 5.5: 20 · 5.6: 16) |
| — of which (a) non-English | 13 (5.1: 6 · 5.5: 3 · 5.9: 4 — mostly Hindi register, F10) |
| Strings a user can see **inside a compiled program** (5.7) | 4 in the canonical build; +8 with the R65 flag — all (b) |
| Pack-localized strings (5.8) | 50 — intent (a), **bytes broken (F1)**, 2 with script mix (F2) |
| Dead strings (F8) | 8 |
| Pure (c) strings | ~110 (keywords, builtins, flags, paths, Win32 names, machine-code templates) |

(Counting rule: each `db` label is one string; multi-line labels such as `msg_usage` are counted per line
because each line is independently classifiable. If Sarvam counts differently the tables still hold.)

## 7. Evidence for the design decision (packs vs compiled-in) — no recommendation made

Facts that bear on it:

- **Both mechanisms already exist in the binary.** The `tbl_*`/`pick_lang_str` design (5.8) is
  "compiled-in, selected at run time by pack id". It costs 7,435 bytes of text as stored (about half
  that once F1 is fixed) plus 55 pointers for 5 messages × 11 slots, and it is wired into exactly one
  path (`parse_error` + `read_file`). Extending it to the 67 (b) strings is 67 × 11 pointers plus the
  text — on the order of 25–35 KB in the compiler binary, zero new I/O, and no change to how a user
  invokes anything.
- **The packs today are keyword maps only.** `lang/hindi.lang` header: `# Format: <native word>
  <sanskrit keyword>`; `load_lang_file` (line 1167) parses two words per line and resolves the second
  against the keyword and builtin tables (the `tak` special case is at 1278). Routing messages
  through packs means a second section in the pack format, a parser for it, and a buffer for the loaded
  strings; the compiler would then print a message it read from disk, which the "no runtime, no
  toolchain" line in `PROJECT-MASTER.md` does not forbid for the *compiler*, but it is a new kind of
  dependency: a missing or stale pack would change what an error *says*.
- **The default language has no pack.** Sanskrit is slot 0 and that slot holds English. Whatever is
  chosen, the Sanskrit strings must be compiled in — there is nothing to load for the default case.
- **`--check` (the IDE path) does not go through the table at all** (F4), so either design has to
  touch `r48_print_parse_error` / `r48_print_undefined_function` before the IDE user sees anything.
- **The embedded runtime strings (5.7) are a third case**: they are copied into the output program at
  compile time, so the pack in force *at compile time* decides what the program says *at run time*. That
  is probably what a user wants, but it should be a stated decision.
- **Format drift.** Normal mode prints `Sutram Error: parse error at line L:C near token 'X'` and
  `--check` prints `F:L:C: Sutram Error [E_PARSE]: near 'X'`; undefined-function likewise has two texts.
  Whichever way the text is sourced, there are two format families to unify first, or the translation
  work doubles.

## 8. What I did not do, and why

- **Did not change `src/sutram_compiler.asm` or the `.inc` files** — ChatGPT's, and the brief says
  inventory only.
- **Did not test on Windows** — no Windows host here; the Windows runtime strings (`win/winrt.inc`) are
  import names only, so there is nothing to translate there, but I could not observe a Windows diagnostic.
- **Did not exercise every (b) string** — I triggered the parse error, open error, UTF-8 error,
  undefined function and array-bounds paths. The capacity-overflow messages (5.5/5.6, lines 780–799) are
  classified from their call sites, not from observed output; I did not construct inputs large enough to
  overflow each table.
- **Did not verify the Sanskrit of my proposals with a Sanskrit speaker.** The words are taken from the
  repo's own vocabulary and existing strings; the grammar is deliberately absent (nouns only). Treat the
  proposal column as a starting point for Sarvam's decision, not as frozen text.
- **Did not review the 10 pack translations for correctness** beyond script consistency (F2). I can read
  the Devanagari ones; I did not judge the others.
