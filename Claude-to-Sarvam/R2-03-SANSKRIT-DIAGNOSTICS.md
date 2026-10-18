# ROUND-02 / WS4 — the compiler's diagnostics in Sanskrit, compiled in

**Date:** 2026-10-18 · **Base:** main `5eec849` (v167) · **Code:** branch `claude/round-02`, commit
`784779e` (draft PR #31).

---

## 1. What I did

Applied the decision in ROUND-02 Part 3 WS4: **compiled-in Sanskrit, no pack routing.** Every string
the ROUND-01 inventory marked **(b)** was replaced, keeping two things verbatim as class (c):

- the `Sutram Error:` / `Sutram Error [` prefix, everywhere it occurred (and `--check`'s
  `file:line:col: Sutram Error [E_…]` shape, which the X11 GUI parses to jump to the error line);
- every `[E_CODE]` tag (`E_PARSE`, `E_UTF8`, `E_UNDEFINED_FUNCTION`, `E_MODULE_*`, `E_EXPORT_UNDEFINED`,
  `E_ABBREVIATION_VALUE`, `E_INTEGER_TRAP`, `E_MODULE_ALIAS_REUSE`).

Register: nouns only, from the repo's own vocabulary and existing strings (`dosh`, `vyakaran`, `pankti`,
`patra`, `prakriya`, `tark`, `avashyak`, `agyat`, `punah`, `seema`, `atikram`, `rikta`, `upanaam`,
`niryat`, `paribhasha`, `ghoshana`, `bhinn`, `mulya`, `srot`, `nivesh`, `nirgat`, `sankalan`, `siddh`,
`sanskaran`, `prayog`, `shabd`, `patra-ant`). No verbs, no postpositions, so the strings read the same in
Sanskrit and Hindi register and translate one-to-one into the packs later. The three Hindi hints
(`Sanket: …`), the shell, the banners and the pack-localized table were not touched.

Also changed, because they were (b): the usage text, `OK: compiled N bytes` → `Siddh: N byte sankalit`,
`Bhasha pak load hua:` → `Bhasha pak prapt:`, `Error: cannot open input file` → `Sutram Error: nivesh
patra aprapt` (gains the standard prefix), the four runtime messages embedded in generated programs, the
seven R65 opt-in trap messages, and the three strings in `src/r68_diagnostics.inc` /
`src/r66_indic_lexer.inc`.

Not changed: dead strings (`msg_parse_err`, `msg_guna_dbg1..3`, `graph_arrow`, `graph_msg_limit`), the
orphan `"Run 'sutram -i' and type 'sahayata' for help."` at line 401 (no label; never printed), and
`msg_version`'s `v160` (Sarvam's number to set).

## 2. The goldens — exactly what changed

28 files under `tests/expect/` were re-recorded with `python3 tests/run_tests.py --record <names>`.
**Before recording** I diffed every failing case's expected vs actual output: **in all 28, exactly one
line differed, and it was the message line.** No exit code changed (`--record` rewrote five `.exit`
files with only a trailing newline difference; I reverted those, so the `.exit` files are untouched).
The 28: `68 69 70 71 73 98 100 101 105 106 108 120 121 156 157 158 159 160 161 162 164 165 204 210
212 213 214` and `220_hindi_parse_error` (whose first line is `Bhasha pak prapt:`).

## 3. What I ran, and the gates

```sh
nasm -f elf64 -I. src/r68_compiler_entry.asm -o s.o && ld -o sutram_compiler s.o
python3 tests/run_tests.py                                 # NO-EXPECTATION=4  PASS=188
python3 tools/codegen_gate.py ./sutram_compiler            # 12 PASS
python3 tools/test_lang_packs.py ./sutram_compiler         # 33/33
python3 tools/proof_lib.py --compiler ./sutram_compiler    # 191 passed, 0 failed, 191 total
python3 tools/proof_props.py --compiler ./sutram_compiler  # 86/86 properties hold
python3 tools/check_layers.py                              # layers OK: 14 core, 9 alloc, 1 std
python3 -m unittest discover -s tests/module_graph         # Ran 18 tests ... OK
python3 -m unittest discover -s tests/r68                  # see §5
sh tools/gates.sh                                          # all PASS except the false suite FAIL (R2-02)
```

Sample of what a user now sees:

```
$ ./sutram_compiler undef.sm u.bin
Sutram Error: agyat prakriya: foo
$ ./sutram_compiler --check undef.sm
undef.sm:2:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'foo'
$ ./sutram_compiler lineno.sm l.bin
Sutram Error: vyakaran dosh, pankti 5:1, shabd 'patra-ant'
$ ./oob.bin
Sutram Error: mala ank seema atikram
$ ./sutram_compiler badutf.sm x.bin
Sutram Error [E_UTF8]: badutf.sm:5: srot me ashuddh ya khandit UTF-8
$ ./sutram_compiler
Sutram - sampurna sutra
Prayog:
  sutram <nivesh.sm> <nirgat.bin>         sankalan
  ...
```

## 4. Every string, before and after

(83 changed `db` lines; multi-line labels such as `msg_usage` and the three-part module messages appear as
several rows, continuation rows marked —.)

| Label | Before | After |
|---|---|---|
| — | Sutram Error [E_UTF8]: invalid or truncated Indic identifier | Sutram Error [E_UTF8]: ashuddh ya khandit bharatiya naam |
| — | : invalid or truncated UTF-8 in source code | : srot me ashuddh ya khandit UTF-8 |
| — | : abbreviation keyword is not a value: ' | : sankshep shabd mulya nahi: ' |
| — | Usage: | Prayog: |
| — |   sutram <input.sm> <output.bin>          compile |   sutram <nivesh.sm> <nirgat.bin>         sankalan |
| — |   sutram --check <input.sm>               parse/check, no output binary |   sutram --check <nivesh.sm>              janch matra, nirgat nahi |
| — |   sutram --lang <pack> <in.sm> <out.bin>  with language pack |   sutram --lang <pak> <nivesh.sm> <nirgat.bin>  bhasha pak sahit |
| — |   sutram -i                               interactive shell |   sutram -i                               khol (samvad) |
| — |   sutram --version                        version info |   sutram --version                        sanskaran |
| `r48_msg_near` | : Sutram Error [E_PARSE]: near ' | : Sutram Error [E_PARSE]: shabd ' |
| `r48_msg_eof` | <EOF> | <patra-ant> |
| `r50_msg_setchar_arity` | Sutram Error: akshar_rakh requires exactly 3 arguments | Sutram Error: akshar_rakh: 3 tark avashyak |
| `r52_msg_dvaram_arity` | Sutram Error: dvaram requires 2 or 3 arguments | Sutram Error: dvaram: 2 va 3 tark avashyak |
| `r52_msg_charat_arity` | Sutram Error: akshar requires exactly 2 arguments | Sutram Error: akshar: 2 tark avashyak |
| `r52_msg_charcode_arity` | Sutram Error: aksharank requires 1 or 2 arguments | Sutram Error: aksharank: 1 va 2 tark avashyak |
| `r54_msg_arity` | Sutram Error: builtin argument count does not match signature | Sutram Error: tark sankhya hastakshar se bhinn |
| `r48_msg_undefined` | : Sutram Error [E_UNDEFINED_FUNCTION]: unknown function ' | : Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya ' |
| `msg_err_line` | Sutram Error: parse error at line  | Sutram Error: vyakaran dosh, pankti  |
| `msg_err_near` |  near token ' | , shabd ' |
| `msg_err_eof` | end of file | patra-ant |
| `msg_duplicate_func` | Sutram Error: duplicate function definition:  | Sutram Error: punah prakriya paribhasha:  |
| `msg_undefined_func` | Sutram Error: undefined function:  | Sutram Error: agyat prakriya:  |
| `msg_array_oob` | Sutram Error: array index out of bounds | Sutram Error: mala ank seema atikram |
| `msg_kosh_required` | Sutram Error: kosh builtin requires a kosh variable | Sutram Error: kosh prakriya hetu kosh-vitti avashyak |
| `r65_msg_add` | : signed addition overflow | : yog atipravah |
| `r65_msg_sub` | : signed subtraction overflow | : nyun atipravah |
| `r65_msg_mul` | : signed multiplication overflow | : gun atipravah |
| `r65_msg_div` | : division by zero | : shunya se bhajan |
| `r65_msg_mod` | : remainder by zero | : shunya se shesh |
| `r65_msg_div_overflow` | : signed division overflow | : bhajan atipravah |
| `r65_msg_mod_overflow` | : signed remainder overflow | : shesh atipravah |
| `msg_kosh_empty` | Sutram Error: kosh pop from empty array | Sutram Error: rikta kosh se kosh_pop |
| `msg_kosh_peek_empty` | Sutram Error: kosh peek from empty array | Sutram Error: rikta kosh se kosh_peek |
| `msg_kosh_dequeue_empty` | Sutram Error: kosh dequeue from empty array | Sutram Error: rikta kosh se kosh_dequeue |
| `msg_kosh_param_type` | Sutram Error: kosh parameter requires matching kosh element type | Sutram Error: kosh tark: tatv prakar bhinn |
| `msg_kosh_param_push` | Sutram Error: kosh_push on a kosh parameter is not supported | Sutram Error: kosh tark par kosh_push asamarthit |
| `msg_lang_ok` | Bhasha pak load hua:  | Bhasha pak prapt:  |
| `msg_open_err` | Error: cannot open input file | Sutram Error: nivesh patra aprapt |
| `msg_ok` | OK: compiled  | Siddh:  |
| `msg_bytes` |  bytes |  byte sankalit |
| `msg_namespace_error` | Sutram Error: invalid namespaced yoj (use module@alias, max 31 alias bytes) | Sutram Error: ashuddh yoj (roop: module@upanaam, upanaam 31 byte tak) |
| `msg_namespace_module_missing` | Sutram Error: namespaced module file not found | Sutram Error: module patra aprapt |
| `msg_namespace_alias_reuse` | Sutram Error: namespaced alias already assigned to another module | Sutram Error: upanaam purv-niyukt (anya module) |
| `r51_alias_conflict` | : Sutram Error [E_MODULE_ALIAS_REUSE]: namespaced alias already assigned to another module | : Sutram Error [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya module) |
| `msg_namespace_func_limit` | Sutram Error: namespaced module has too many or oversized function names | Sutram Error: module prakriya-naam seema atikram |
| `msg_import_overflow` | Sutram Error: expanded module source too large | Sutram Error: vistarit srot seema atikram |
| `graph_cycle_prefix` | dependency cycle:  | yoj chakra:  |
| `graph_missing_prefix` | cannot open import  | yoj patra aprapt:  |
| `graph_limit_prefix` | too many modules or oversized module | module/yoj seema atikram |
| `graph_invalid_prefix` | invalid module name | ashuddh module naam |
| `msg_ast_overflow` | Sutram Error: AST capacity exceeded | Sutram Error: AST seema atikram |
| `msg_func_params_overflow` | Sutram Error: function parameter table capacity exceeded | Sutram Error: prakriya tark-suchi seema atikram |
| `msg_var_table_overflow` | Sutram Error: variable table capacity exceeded | Sutram Error: vitti-suchi seema atikram |
| `msg_func_table_overflow` | Sutram Error: function table capacity exceeded | Sutram Error: prakriya-suchi seema atikram |
| `msg_patch_overflow` | Sutram Error: call patch table capacity exceeded | Sutram Error: aahvan-suchi seema atikram |
| `msg_func_defs_overflow` | Sutram Error: function definition table capacity exceeded | Sutram Error: prakriya paribhasha-suchi seema atikram |
| `msg_break_patch_overflow` | Sutram Error: too many break statements in active loops | Sutram Error: chakra me krama seema atikram |
| `msg_continue_patch_overflow` | Sutram Error: too many continue statements in active loops | Sutram Error: chakra me agrim seema atikram |
| `msg_code_overflow` | Sutram Error: generated code capacity exceeded | Sutram Error: yantra-code seema atikram |
| `msg_rachana_overflow` | Sutram Error: rachana table capacity exceeded | Sutram Error: rachana-suchi seema atikram |
| `msg_rachana_fields_overflow` | Sutram Error: too many fields in rachana | Sutram Error: rachana kshetra seema atikram |
| `msg_block_nesting_overflow` | Sutram Error: block nesting capacity exceeded | Sutram Error: khand gahrai seema atikram |
| `msg_block_stmt_overflow` | Sutram Error: too many statements in block | Sutram Error: khand kathan seema atikram |
| `r55_msg_proto_duplicate` | Sutram Error: duplicate prakriya forward declaration | Sutram Error: punah prakriya purv-ghoshana |
| `r55_msg_proto_missing` | Sutram Error: prakriya forward declaration has no definition | Sutram Error: prakriya purv-ghoshana paribhasha-rahit |
| `r55_msg_proto_signature` | Sutram Error: prakriya prototype signature (arity/type) differs from definition | Sutram Error: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar) |
| `r55_msg_proto_capacity` | Sutram Error: too many prakriya prototypes | Sutram Error: prakriya purv-ghoshana seema atikram |
| `r56_msg_global_capacity` | Sutram Error: too many module-level vitti variables | Sutram Error: module-star vitti seema atikram |
| `r56_msg_global_duplicate` | Sutram Error: duplicate module-level vitti name | Sutram Error: punah module-star vitti naam |
| `r56_msg_patch_capacity` | Sutram Error: too many global data references | Sutram Error: sarvatrik data sandarbh seema atikram |
| `mg_e_cycle` | Sutram Error [E_MODULE_CYCLE]: cyclic import:  | Sutram Error [E_MODULE_CYCLE]: yoj chakra:  |
| `mg_e_noexp2` | ' is not exported by module ' | ' module ' |
| `mg_e_noexp3` | ' | ' se aniryat |
| `mg_e_dupexp1` | Sutram Error [E_MODULE_DUP_EXPORT]: duplicate export ' | Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat ' |
| `mg_e_dupexp2` | ' in module ' | ', module ' |
| `mg_e_undef1` | Sutram Error [E_EXPORT_UNDEFINED]: export ' | Sutram Error [E_EXPORT_UNDEFINED]: niryat ' |
| `mg_e_undef2` | ' has no matching definition in module ' | ' paribhasha-rahit, module ' |
| `mg_e_unknown1` | Sutram Error [E_EXPORT_UNDEFINED]: unknown qualified symbol ' | Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket ' |
| `mg_e_unknown2` | ' in module ' | ', module ' |
| `mg_e_depth` | Sutram Error [E_MODULE_DEPTH]: import depth exceeded | Sutram Error [E_MODULE_DEPTH]: yoj gahrai seema atikram |
| `mg_e_valias2` | ' must be imported with an alias: yoj  | ' upanaam avashyak: yoj  |
| `mg_e_valias3` | @alias | @upanaam |
| `mg_e_limit` | Sutram Error [E_MODULE_LIMIT]: too many modules or imports | Sutram Error [E_MODULE_LIMIT]: module/yoj seema atikram |

## 5. Consequences to know about — stated, not hidden

1. **`tests/r68` has one more failure than on main.** `test_lock_has_real_compiler_pin` checks the Git
   blobs in `tools/r68_review.lock.json`; my one-string change to `src/r66_indic_lexer.inc` moves its
   blob from `3633bd55…` to `998b6cb7…`. (On main this test was already failing on the compiler's own
   pin, `64ea028a…`, which has been stale since v157; the suite was 3 failures + 1 setup error before,
   4 + 1 after.) **The lock needs re-pinning by its owner** — or, if the lock must stay, I can revert
   that single string and leave `E_UTF8`'s Indic message in English; say which.
2. **Eleven historical acceptance tools still match the English text** (`tools/r48_native_acceptance.py`,
   `r48_stage2_acceptance.py`, `r49_diagnostic_audit.py`, `r49_repeated_semantic.py`,
   `r51_native_audit.py`, `r52_native_acceptance.py`, `r54_native_acceptance.py`, `r64_source_gate.py`,
   `r68_native_acceptance.py`, `r71_native_acceptance.py`, `test_namespace_contract_oracle.py`) and so
   does `tests/negative/r70/manifest.json` (already unrunnable: fixture sha drift, R1-WS3). None is in
   the gate list; all are ChatGPT's round tools. They will report mismatches if re-run. I did not edit
   them.
3. **`docs/*.md` quote the old English messages** in several places (`KOSH-BUILTINS.md:107–109`,
   `LANGUAGE-REFERENCE.md:374–375`, `NEGATIVE-CORPUS.md:27`, `ERROR-CONVENTION.md`, the stdlib
   reference) — R1-WS3 already listed the ones that were wrong *before* this change; now the rest are
   out of date too. A documentation-only sweep is the natural next item.
4. The Windows target **assembles and links** with these strings (`nasm -f win64 -DWINDOWS=1`, 176,234 B);
   it was not executed.

## 6. What I did not do

- Did not route anything through the packs (per the decision).
- Did not translate the three `Sanket:` hints or the shell (already non-English; register is Sarvam's
  call, R1-WS1 F10).
- Did not touch `windows/`, `lang/`, `docs/`, or any tool.
