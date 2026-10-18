# READ FIRST — v164 (`a5c871c`) reverted 27 compiler string lines and the suite is 181, not 187

**Date:** 2026-10-18, found when I fetched before delivering. The five workstream documents were written
against `feef075` (v162). While I worked, `main` moved to `1f031a8` (v164). I rebased, rebuilt the
compiler from `1f031a8`, and re-ran the suite. **Everything in 01–05 still holds**, with the two
qualifications in §3 below — but this comes first because it is a live regression on `main`.

---

## 1. What I observed on `1f031a8`

```
$ nasm -f elf64 -I. src/r68_compiler_entry.asm -o s.o && ld -o sutram_compiler s.o
$ ./sutram_compiler --version
Sutram 1.0 (v29) — the complete thread
Sanskrit-keyword language -> x86-64 machine code

$ python3 tests/run_tests.py | tail -1
FAIL=6  NO-EXPECTATION=4  PASS=181
--- 158_namespaced_alias_digit: FAIL
--- 159_namespaced_path_traversal: FAIL
--- 160_namespaced_empty_alias: FAIL
--- 161_namespaced_overlong_alias: FAIL
--- 162_namespaced_import_capacity: FAIL
--- 214_r41_v1_noalias: FAIL

--- expected compiler output ---
Sutram Error: invalid namespaced yoj (use module@alias, max 31 alias bytes)
--- actual compiler output ---
Sutram Error: invalid namespaced ayojan (use module@alias, max 31 alias bytes)
```

`docs/CHANGELOG.md` v164 says "These are comments, so they break nothing … Suite still 187." **On this
checkout the suite is 181.** The six failing goldens are the ones that contain a compiler string.

## 2. What `a5c871c` actually changed (`git diff feef075 a5c871c -- src/sutram_compiler.asm`)

33 lines changed. **6 are the `KW_*` comments the commit message describes** (`KW_NISHEDHA`, `KW_UDDESHYA`,
`KW_PARIGRAH`, `KW_SRIJANA`, `KW_NISHKRIYA`, `KW_PANKTI`). The other **27 are `db` strings in the data section, and every one of them went backwards** — to the pre-v157 English text, to
the pre-rename keyword names, and in one case to the v29 version banner:

| Label | v162 (`feef075`) | v164 (`a5c871c`) | Effect |
|---|---|---|---|
| `msg_usage` 208 | `Sutram - sampurna sutra` | `Sutram — the complete thread` | banner back to English |
| `msg_version` 215–216 | `Sutram 1.0 (v160) - sampurna sutra` / `Samskrita-mukhya bhasha -> x86-64 yantra-code` | `Sutram 1.0 (v29) — the complete thread` / `Sanskrit-keyword language -> …` | **version string says v29** |
| `r48_msg_ok`, `r48_msg_errors` 220–221 | `Sutram janch: …` | `Sutram check: OK (no output binary)` / `… errors found; no output binary` | `--check` summary English |
| `r50/r52_msg_*_arity` 223, 225, 226 | `akshar_rakh` / `akshar` / `aksharank` requires … | **`set_char` / `char_at` / `char_code`** requires … | **the error names builtins that no longer exist** |
| `msg_err_hint` 282 | `Sanket: is sthan par shabd aur vyakaran dekho.` | `Hint: check the keyword spelling and syntax near this spot.` | hint English |
| `msg_err_arg_limit`, `msg_err_duplicate_func` 289–290 | `Sanket: …` | `Hint: …` | hints English |
| `msg_lang_ok`, `msg_lang_fail` 402–403 | `Bhasha pak load hua:` / `Chetavani: …` | `Language pack loaded:` / `Warning: language pack not found:` | English |
| `msg_shell_banner`, `msg_shell_bye`, `msg_shell_help` 436–448 | Hindi/Sanskrit | English, **and the help now teaches `punaravartana i = 0 to 5 { … }` and `pankti arr[5]`** | **the shell's own help text does not compile**: `parse error at line 2:41` on `punaravartana … to` |
| `msg_namespace_error` 758 | `… invalid namespaced yoj …` | `… invalid namespaced ayojan …` | 5 goldens fail |
| `mg_e_valias2` 2943 | `… with an alias: yoj ` | `… with an alias: ayojan ` | 1 golden fails; the message tells the user to type a keyword that does not exist |

The shape of the diff — comments corrected, strings restored to an old revision in the same hunks — looks
like the edit was made on a pre-v157 copy of lines 130–450 and 2926–2950 and pasted back. I did not
confirm how; I only confirm what the file now contains.

## 3. What this does to the delivery

- **01-DIAGNOSTICS-INVENTORY.md** line numbers are unchanged (same line count), but the *text* of the labels above is now the v164 text. The classification moves: the 13 strings I marked **(a)** in 5.1
  and 5.9 are now **(b)** too, so on `main` today the count is **80 visible, 80 English** — none of the
  compiler's own messages is in an Indian language any more, except the 50 double-encoded pack strings.
  F9 (stale version number) is worse: it now says v29.
- **02-HARDCODED-CONSTANTS.md** §4.1: `b1d5166` (v163) fixed `ide/sutram_gui_linux.asm` — I verified
  the new table carries 27 of the 28 current keywords plus `likha`/`grahan`/`shabda` — only `sankhya`
  is still missing. **`ide/sutram_ide.asm`
  (the terminal IDE, the one `tools/ide_test.py` drives) is still the old table** — the PTY observation
  in §4.1 was made on that binary and still reproduces on `1f031a8`. The CHANGELOG v164 note that
  "there are two Linux IDEs" is the same finding from the other side.
- Everything else in 01–05 (the stale `ayojan` search in `r49_print_module_location`, the Devanagari
  aliases, `tests/module_graph` 6/18, the document audit, the WS4 program) is unaffected by v163/v164;
  the WS4 program compiles and produces the same output on `1f031a8` (re-checked).

## 4. What I did not do

I did not revert `a5c871c` or touch the compiler — it is ChatGPT's file and this is a report. The
restore is mechanical: the 27 `db` lines at `feef075` are the correct ones; the 6 comment lines at
`a5c871c` are the correct ones. After that, the suite should read 187 again, and `tests/expect/` needs
no change.
