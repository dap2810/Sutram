# ROUND-02 / WS1 — the four defects, fixed

**Date:** 2026-10-18 · **Base:** main `5eec849` (v167) · **Code:** branch `claude/round-02`, commit
`5dc77d5` (draft PR #31). Per `AGENTS.md`, code changes stay on a review branch; this document is the
delivery on `main`.

All four fixes are **contained** — strings, the argument parser, one exit path, and the diagnostics
printer. **No restructuring**; the one change with any reach (d) is explained in full below.

---

## (a) The double-UTF-8-encoded pack strings — fixed, and pinned by a golden

**What I did.** The 50 strings are in `src/sutram_compiler.asm` lines 315–373 (not in `lang/*.lang`,
which were already correct UTF-8 — the brief says "pack files"; the defect was in the compiler's
compiled-in table). Each quoted segment was decoded UTF-8 → Latin-1 bytes → UTF-8, which recovers the
intended text for all 50. In the two Tamil strings, four Gujarati PA letters (U+0AAA `પ`) were replaced
by Tamil PA (U+0BAA `ப`), and `குறிபு` was spelled `குறிப்பு` (note/hint) — that last one is my
judgement, flagged here so a Tamil reader can confirm.

**Bytes before and after** (`git show 67423bc:src/sutram_compiler.asm | sed -n 327p` vs the branch;
first 24 bytes after the opening quote):

```
line 327  err_line_hi
  before: c3 a0 c2 a4 c2 b8 c3 a0 c2 a5 c2 82 c3 a0 c2 a4 c2 a4 c3 a0 c2 a5 c2 8d   ("Ã Â¤Â¸Ã Â¥Â‚…")
  after:  e0 a4 b8 e0 a5 82 e0 a4 a4 e0 a5 8d e0 a4 b0 e0 a4 ae e0 a5 8d 20 e0 a4   ("सूत्रम् …")
```

**What the compiler now writes** (`./sutram_compiler --lang <pack> bad.sm b.bin > err.txt`; the hex
is the third line of the file, first 24 bytes):

```
hindi    e0 a4 b8 e0 a5 82 e0 a4 a4 e0 a5 8d e0 a4 b0 e0 a4 ae e0 a5 8d 20 e0 a4
         सूत्रम् त्रुटि: पंक्ति 4:1 के पास टोकन 'फ़ाइल का अंत'
         संकेत: इस स्थान के पास कूटशब्द की वर्तनी और वाक्य-रचना जाँचें।
tamil    e0 ae 9a e0 af 82 e0 ae a4 e0 af 8d e0 ae a4 e0 ae bf e0 ae b0 e0 ae ae
         சூத்திரம் பிழை: வரி 4:1 அருகில் டோக்கன் 'கோப்பின் முடிவு'
         குறிப்பு: இந்த இடத்தின் அருகில் குறிச்சொல்லின் மொழியும் தொடரியலைச் சரிபார்க்கவும்.
bengali  e0 a6 b8 e0 a7 82 e0 a6 a4 e0 a7 8d e0 a6 b0 e0 a6 ae e0 a7 8d 20 e0 a6
         সূত্রম্ ত্রুটি: পংক্তি 4:1 এর কাছে টোকেন 'ফাইলের শেষ'
```

**The golden.** `examples/220_hindi_parse_error.sm` (a deliberate syntax error) with
`tests/expect/220_hindi_parse_error.{compile_fail,out,exit}` and a `LANG` entry in
`tests/run_tests.py`. The `.out` holds the real Devanagari bytes. **It fails against the v166 compiler
and passes on the branch** — i.e. it would have caught this:

```
$ SUTRAM_COMPILER=/scratch/sutram_v166 python3 tests/run_tests.py 220_hindi_parse_error
FAIL=1
$ python3 tests/run_tests.py 220_hindi_parse_error
PASS=1
```

## (b) Missing input file exits 0 — fixed

`read_file` (line ~5723) printed the open-error and jumped to `do_exit`, which is `exit(0)`. It now does
`mov rdi,1 ; call os_exit`. Observed:

```
$ ./sutram_compiler /nonexistent.sm x.bin ; echo "exit=$?"
Sutram Error: nivesh patra aprapt
exit=1
$ ./sutram_compiler --check /nonexistent.sm ; echo "exit=$?"
Sutram Error: nivesh patra aprapt
exit=1
```

Not changed, noted: `.usage` (wrong argument count) and `--version` still exit 0; the usage case
arguably should not, but it is not the defect that was reported.

## (c) `--check` and `--lang` combine in either order — fixed

The parser took `argv[1]` as the mode and `argv[2]` as the file, so the second flag was read as a file
name. Two small branches added: in check mode, if `argv[2]` is `--lang` then `argv[3]` is the pack and
`argv[4]` the input; in lang mode, if `argv[3]` is `--check` then check mode is set and `argv[4]` is the
input. All four forms observed:

```
$ ./sutram_compiler --check --lang hindi bad.sm        -> Bhasha pak prapt: hindi / bad.sm:3:1: … / exit=1
$ ./sutram_compiler --lang hindi --check bad.sm        -> same
$ ./sutram_compiler --check bad.sm                     -> unchanged
$ ./sutram_compiler --lang hindi bad.sm b.bin          -> unchanged (Devanagari diagnostic)
```

Note for WS4: in `--check` mode the pack still only selects the *keywords*; the check-mode message text
is the compiled-in (now Sanskrit) one, because the `r48_*` printer never used the pack table (R1 F4).

## (d) Wrong line numbers in normal mode when a module is imported — fixed

**Cause.** The R51 origin map (which byte of the expanded buffer came from which file and offset) was
built **only in `--check` mode**: nine `cmp qword [rel r48_mode],0 / je …` gates around pure
bookkeeping (`r51_init_map`, `r51_register_module`, `r51_stamp_legacy`, `r51_init_raw_map`,
`r51_finish_origin_pass`, `r51_copy_origin`, `r51_raw_copy_position`, `r51_mark_namespaced`,
`r51_mark_newline`). Normal-mode `parse_error` therefore had only the expanded-buffer line.

**Change.** The nine gates are removed — the map is now maintained in every mode (it is memory writes;
expansion semantics are untouched, and the check-mode-only *behaviour* gates — error counting, recovery,
the alias-conflict printer — are left exactly as they were). A new 60-line helper
`r51_origin_line_col` (same scan as `r51_print_origin`, without printing) returns the original line,
column and file; `parse_error` uses it and falls back to the old numbers if the original file cannot be
re-read. An error inside an imported module names the module.

**Observed** (same inputs as ROUND-01 F12):

```
$ printf 'yoj ganit\nmukhya() {\n    vitti x = \n}\n' > lineno.sm
before:  Sutram Error: parse error at line 169:1 near token 'end of file'
after:   Sutram Error: vyakaran dosh, pankti 5:1, shabd 'patra-ant'        (5 = the file's own EOF line)
$ ./sutram_compiler Claude-to-Sarvam/04-ankatalika.sm   (with the deliberate `band` error of ROUND-01)
before:  line 2020        after: line 175:11                                 (--check also says 175:11)
$ (error on line 4 of lib/badmod.smlib, imported via yoj badmod@b)
after:   Sutram Error: vyakaran dosh, pankti badmod.smlib:5:1, shabd '}'
```

Column semantics changed with it: the column is now the UTF-8 **display** column (as `--check` already
reported), not the byte offset — `अन्य` on a Devanagari line went from `2:47` to `2:42`. No golden
contains a normal-mode parse error, so nothing needed re-recording for this.

**Cost.** None measurable: the map arrays already existed; the suite runs in the same time.

## What I ran, and the gates after WS1 alone

```sh
nasm -f elf64 -I. src/r68_compiler_entry.asm -o s.o && ld -o sutram_compiler s.o
python3 tests/run_tests.py            # NO-EXPECTATION=4  PASS=187  (+1 new golden = 188 once added)
python3 tools/codegen_gate.py ./sutram_compiler       # 12 PASS
python3 tools/test_lang_packs.py ./sutram_compiler    # 33/33
python3 tools/proof_lib.py --compiler ./sutram_compiler    # 191 passed, 0 failed
python3 tools/proof_props.py --compiler ./sutram_compiler  # 86/86
nasm -f win64 -DWINDOWS=1 -I. src/r68_compiler_entry.asm -o s.obj && ld -mi386pep --subsystem console --entry=_start -o sutram.exe s.obj
                                      # assembles and links (176,234 B) — NOT executed
```

## What I did not do

- Did not change `lang/*.lang` (they were correct).
- Did not make usage/`--version` exit non-zero.
- Did not run anything on Windows.
