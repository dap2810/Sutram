# Diagnosis of the eight v297 Windows failures

Date: 2026-11-03. Diagnostic round only: no compiler, library or golden changes; no rebuild.
Tested source is the preserved v297 export of `1263356b6cb434871680c83c6f70a8c67eb016a3`, not any newer remote changes. Existing compiler SHA-256: `ccc8368eb57e91da54a3bed5c824bf63892bc5f9329ff34bf5f16cc1d3a1370e`.

**Primary classification against the documented v297 contract: 2 COMPILER cases, 6 HARNESS cases, 0 unexplained output-only cases.** This does not mean Windows has Linux memory features: four harness mismatches expose explicitly documented missing Windows capabilities. Against the stronger cross-platform acceptance target, 303/317/318/288 remain functionality gaps.

| Test | Class (compiler / output / harness) | Evidence | Fix |
|---|---|---|---|
| `303_r103_parimita_refuses` | HARNESS (documented unsupported Windows capability) | No refusal: prints not reached 499999500000, exit 0. Reference explicitly says Windows budgets are not checked. This is an absent feature, not a different allocation count. | Make the test conditional on platform for current documented support; implement Windows budget checking before claiming parity. |
| `317_r107_parimana` | HARNESS | Every value is zero; PE codegen explicitly emits xor eax,eax. Reference and example explicitly specify Windows returns 0. | Make the test conditional on platform; do not alter Linux golden. |
| `318_r108_parimana_moves` | HARNESS | Same explicit PE zero-return path as 317; not allocator rounding or a byte-count variance. | Make the test conditional on platform; implement accounting separately if Windows parity is required. |
| `322_r111_new_names` | COMPILER | Exit 0xC0000005 after corrupt character output. Identical PE bytes to 323. Isolated char prints P instead of B; literal concatenation independently crashes. | Fix compiler/runtime character-buffer lifetime; resolve literal concatenation contract/codegen so accepted examples do not write read-only literals. |
| `323_r111_old_names` | COMPILER | Same executable and same failures as 322; expected rename notices are on compiler stderr. | Fix the shared builtin behavior, not the alias table. |
| `288_r86_kosh_alias_moves` | HARNESS (documented platform gap) | Actual alias values match the Windows behavior explicitly documented in reference section 16. Linux alone has in-place region growth. | Make the test conditional on platform; Windows region/alias parity is separate compiler work. |
| `29_nishkriya` | HARNESS | Linux raw syscall bytes use syscall 60 and expect exit 42. Windows run prints the text and exits 0. Inline raw syscall is not the compiler Win32 adapter. | Make the test conditional on platform; do not execute Linux syscall fixtures as portable Windows tests. |
| `220_hindi_parse_error` | HARNESS | Original harness omits --lang hindi. Explicit Hindi rerun matches the full golden exactly and exits 1 as expected. | Fix the harness language map (no golden change). |

## Shared causes

303, 317, 318 and 288 share the Linux-only arena/region implementation boundary: PE uses the ordinary allocation path, no block budget enforcement, zero-return accounting, and moving kosh growth. This is one architectural portability gap, but not proof that a single small fix implements all four features. 322 and 323 are the same machine code and share **two** builtin problems: the character temporary’s lifetime and a write into literal storage. 29 is a Linux syscall fixture; 220 is a missing harness language flag. They are independent.

## Evidence behind the classifications

- Reference lines 976–980 explicitly predict the observed Windows alias outputs. Lines 1307–1308 explicitly state that parimana returns 0 on Windows. Lines 1352–1353 explicitly say a Windows block budget is not checked. Example317 states the same zero-return restriction. These facts correct the earlier reports’ interpretation: the observed cross-platform acceptance failures are real, but they are not newly discovered regressions against the documented Windows contract.
- Compiler `.ge_call_parimana` emits `31 C0` (`xor eax,eax`) when `r65_active` is false. `.r73_ge_scratch` falls back to ordinary `emit_nirmmita_from_rax` for PE. Zero counters and missing refusal are deliberate code paths, not OS rounding. The diagnostic brief’s allocation-count hypothesis is refuted: 303 completes all 1,000,000 allocations and reaches the final print.
- Compiler `.ge_call_charfr` reserves 16 stack bytes, writes the character at rsp, returns that pointer, then restores only 8 bytes. The returned pointer is therefore at rsp-8. The PE runtime call can place its return address at that exact address, overwriting the character before WriteFile reads it. The isolated new and old character probes both print `P` (hex 50) instead of `B` (42); the larger examples emit a different invalid byte. That byte depends on the generated layout. This is a codegen/lifetime defect, not a Unicode-font issue or renamed keyword issue.
- `.ge_call_vartcat` is an in-place strcat-style operation: it scans the first argument and emits `mov [rdi],cl`. Both alias fixtures pass a literal as that destination. Literal-destination probes crash with 0xC0000005, while a nirmmita buffer initialized with ab produces abcd. The fixture is exercising a writable-destination contract ambiguity as well as a PE failure. Do not “fix” this by making code pages writable. Clarify the API: either reject immutable destinations and change the fixture deliberately, or implement allocating concatenation if that is the intended contract. The crash belongs to the compiler bucket under this round’s requested crash rule; the source test misuse must also be reviewed.
- All three new/old pairs are byte-identical: full 322/323, isolated character conversion, and literal concatenation. This directly refutes differently emitted alias-table code as the cause.
- The original Windows harness’s language map omits case220. Its inline-assembly exclusion scans obsolete `nishkriya` but not current `yantra`, so case29 reaches execution despite the skip category.

## Corrections to the supplied diagnostic procedure

The Windows command shown with `examples\303_*.sm` is not a reliable way to pass a source filename: CMD does not expand wildcards into argv for this native compiler. All reruns used exact filenames. Each subprocess had a five-second timeout. No timeout occurred. No Linux run is newly claimed.

`results.json` preserves every command as an argv array, working directory, stdout, stderr, stdout hex, exit status, duration and successful binary SHA-256. `diagnose.py` and the reduced `.sm` probes reproduce the work. The original eight results remain in the earlier native-cases.json. Source excerpts below are copied from the pinned build tree. The test installer remains under `Windows-to-Sarvam/win-v297-2026-11-03/`, not at the root path implied by the brief.

## Actual outputs and expected outputs

### 303_r103_parimita_refuses

compile: exit 0; 0.0126 seconds.

stdout:
```text
Siddh: 397 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0; 3.2651 seconds.

stdout:
```text
not reached 499999500000
```

stderr:
```text
(empty)
```

Expected output:
```text
Sutram truti [E_PARIMITA]: pankti 6 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 1048576 baait)
```
Expected exit: 1

### 317_r107_parimana

compile: exit 0; 0.0161 seconds.

stdout:
```text
Siddh: 1584 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0; 0.0496 seconds.

stdout:
```text
start 0
after nirmmita(64) 0
in a block, nirmmita(1000) 0
after the block 0
a kosh of 1000 0
```

stderr:
```text
(empty)
```

Expected output:
```text
start 0
after nirmmita(64) 64
in a block, nirmmita(1000) 1072
after the block 64
a kosh of 1000 8272
```
Expected exit: 0

### 318_r108_parimana_moves

compile: exit 0; 0.0114 seconds.

stdout:
```text
Siddh: 2322 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0; 0.0418 seconds.

stdout:
```text
start 0
a kosh of 1 0
grown to capacity 4 0
a block's nirmmita(100) 0
and a kosh of 8 in it 0
after the block 0
```

stderr:
```text
(empty)
```

Expected output:
```text
start 0
a kosh of 1 48
grown to capacity 4 72
a block's nirmmita(100) 184
and a kosh of 8 in it 288
after the block 176
```
Expected exit: 0

### 322_r111_new_names

compile: exit 0; 0.0113 seconds.

stdout:
```text
Siddh: 3623 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 3221225477; 0.1223 seconds.

stdout:
```text
gan 3 ksham 4
iksh 11
hri 11
apanay 3
rikt 0
rikt 1
pankti_gan 5
laghu 97 guru 65
�42
```

stderr:
```text
(empty)
```

Expected output:
```text
gan 3 ksham 4
iksh 11
hri 11
apanay 3
rikt 0
rikt 1
pankti_gan 5
laghu 97 guru 65
B42
abcd
```
Expected exit: 0

### 323_r111_old_names

compile: exit 0; 0.0114 seconds.

stdout:
```text
Siddh: 3623 baait sankalit
```

stderr:
```text
Sutram suchana: 'kosh_push' purana nama - 'kosh_kship' likhatu
Sutram suchana: 'kosh_enqueue' purana nama - 'kosh_yuj' likhatu
Sutram suchana: 'kosh_len' purana nama - 'kosh_gan' likhatu
Sutram suchana: 'kosh_cap' purana nama - 'kosh_ksham' likhatu
Sutram suchana: 'kosh_peek' purana nama - 'kosh_iksh' likhatu
Sutram suchana: 'kosh_pop' purana nama - 'kosh_hri' likhatu
Sutram suchana: 'kosh_dequeue' purana nama - 'kosh_apanay' likhatu
Sutram suchana: 'kosh_empty' purana nama - 'kosh_rikt' likhatu
Sutram suchana: 'kosh_clear' purana nama - 'kosh_shodh' likhatu
Sutram suchana: 'pankti_len' purana nama - 'pankti_gan' likhatu
Sutram suchana: 'char_lower' purana nama - 'akshar_laghu' likhatu
Sutram suchana: 'char_upper' purana nama - 'akshar_guru' likhatu
Sutram suchana: 'char_from' purana nama - 'anka_akshar' likhatu
Sutram suchana: 'lkhb' purana nama - 'likha_santat' likhatu
Sutram suchana: 'vartani_cat' purana nama - 'vartani_sandhi' likhatu
```

run: exit 3221225477; 0.0678 seconds.

stdout:
```text
gan 3 ksham 4
iksh 11
hri 11
apanay 3
rikt 0
rikt 1
pankti_gan 5
laghu 97 guru 65
�42
```

stderr:
```text
(empty)
```

Expected output:
```text
gan 3 ksham 4
iksh 11
hri 11
apanay 3
rikt 0
rikt 1
pankti_gan 5
laghu 97 guru 65
B42
abcd
```
Expected exit: 0

### 288_r86_kosh_alias_moves

compile: exit 0; 0.0116 seconds.

stdout:
```text
Siddh: 1999 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0; 0.0323 seconds.

stdout:
```text
a[0]=41 k[0]=99
a[0]=7 k[0]=99
```

stderr:
```text
(empty)
```

Expected output:
```text
a[0]=99 k[0]=99
a[0]=7 k[0]=7
```
Expected exit: 0

### 29_nishkriya

compile: exit 0; 0.0133 seconds.

stdout:
```text
Siddh: 588 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0; 0.0528 seconds.

stdout:
```text
Yantra: Inline Assembly
==========================
This program exits with code 42 using raw x86-64 bytes.
mov eax,60 / mov edi,42 / syscall  is just:
  yantra("B8 3C 00 00 00")
  yantra("BF 2A 00 00 00")
  yantra("0F 05")
Exiting with code 42...
```

stderr:
```text
(empty)
```

Expected output:
```text
Yantra: Inline Assembly
==========================
This program exits with code 42 using raw x86-64 bytes.
mov eax,60 / mov edi,42 / syscall  is just:
  yantra("B8 3C 00 00 00")
  yantra("BF 2A 00 00 00")
  yantra("0F 05")
Exiting with code 42...
```
Expected exit: 42

### 220_hindi_parse_error

compile: exit 1; 0.0105 seconds.

stdout:
```text

Sutram truti: vyakaran dosh, pankti 7:1, shabd 'patra-ant'
  
  ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```

stderr:
```text
(empty)
```

Expected output:
```text
भाषा पैक मिला: hindi

Sutram truti: व्याकरण दोष, पंक्ति 7:1, शब्द 'फ़ाइल का अंत'
  
  ^
संकेत: इस स्थान पर शब्द और व्याकरण जाँचें।
```
Expected exit: 1

### 220_with_hindi

compile: exit 1; 0.0106 seconds.

stdout:
```text
भाषा पैक मिला: hindi

Sutram truti: व्याकरण दोष, पंक्ति 7:1, शब्द 'फ़ाइल का अंत'
  
  ^
संकेत: इस स्थान पर शब्द और व्याकरण जाँचें।
```

stderr:
```text
(empty)
```

Expected output:
```text
भाषा पैक मिला: hindi

Sutram truti: व्याकरण दोष, पंक्ति 7:1, शब्द 'फ़ाइल का अंत'
  
  ^
संकेत: इस स्थान पर शब्द और व्याकरण जाँचें।
```
Expected exit: 1

### new_char

compile: exit 0; 0.0121 seconds.

stdout:
```text
Siddh: 155 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0; 0.0563 seconds.

stdout:
```text
P
```

stderr:
```text
(empty)
```

### old_char

compile: exit 0; 0.0114 seconds.

stdout:
```text
Siddh: 155 baait sankalit
```

stderr:
```text
Sutram suchana: 'char_from' purana nama - 'anka_akshar' likhatu
```

run: exit 0; 0.0340 seconds.

stdout:
```text
P
```

stderr:
```text
(empty)
```

### new_concat_literal

compile: exit 0; 0.0127 seconds.

stdout:
```text
Siddh: 164 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 3221225477; 0.0970 seconds.

stdout:
```text
(empty)
```

stderr:
```text
(empty)
```

### old_concat_literal

compile: exit 0; 0.0121 seconds.

stdout:
```text
Siddh: 164 baait sankalit
```

stderr:
```text
Sutram suchana: 'vartani_cat' purana nama - 'vartani_sandhi' likhatu
```

run: exit 3221225477; 0.0723 seconds.

stdout:
```text
(empty)
```

stderr:
```text
(empty)
```

### new_concat_writable

compile: exit 0; 0.0109 seconds.

stdout:
```text
Siddh: 278 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0; 0.0701 seconds.

stdout:
```text
abcd
```

stderr:
```text
(empty)
```

## Pinned source excerpts

docs/LANGUAGE-REFERENCE.md:976–980
```text
976: **On Windows the old behaviour remains (not yet changed there):** a growing `kosh` always moves, `a` stays on
977: the old buffer, and the program prints `a[0]=41 k[0]=99` / `a[0]=7 k[0]=99` - reading through `a` gives the
978: old data, writing through `a` does not reach `k`. Up to v283 Linux did the same whenever something had been
979: allocated after the `kosh`. **Until Windows has regions too, keep one name per `kosh` and copy values out
980: (`k[i]`, `kosh_len(k)`), not the `kosh`.** A program that does not alias is unaffected on both systems.
```

docs/LANGUAGE-REFERENCE.md:1307–1308
```text
1307: - **Cost:** a program without `parimana` compiles to the same bytes; with it, each `kosh` allocation and growth
1308:   adds one counter update. **Linux ELF only; in a Windows program it returns 0.**
```

docs/LANGUAGE-REFERENCE.md:1350–1353
```text
1350: - **Cost:** a program without `parimita` compiles to the same bytes as before. In a budgeted block each
1351:   `nirmmita` gains one compare per budget around it.
1352: - **Linux ELF only, as the block.** In a Windows program a `mandapa` releases nothing, and its budget is not
1353:   checked.
```

src/r65_arena.inc:111–135
```text
111: ; r65_active -> rax = 1 when the arena path applies to this build: a Linux ELF target.
112: ; --object / --separate builds take the same path, so that an object linked by sutram-link
113: ; is byte-identical to the direct compile (R28/R29); the two globals are then ordinary
114: ; module vitti of the object - defined by the root, extern in a module object.
115: r65_active:
116:     xor eax, eax
117: %ifndef GUARD_PAGES
118:     cmp qword [rel target_pe], 0
119:     jne .no
120:     mov eax, 1
121: .no:
122: %endif
123:     ret
124: 
125: %ifdef GUARD_PAGES
126: ; r69_emit_guard: the guard-page allocation sequence (rax = size -> rax = block or 0).
127: r69_emit_guard:
128:     lea rsi, [rel r69_guard_seq]
129:     mov rcx, r69_guard_len
130:     call r23_emit_bytes
131:     ret
132: %endif
133: 
134: ; r65_root_globals: at the start of code generation. In --separate, a root with modules
135: ; defines the two globals whether or not its own code allocates, because a module object
```

src/sutram_compiler.asm:23398–23410
```text
23398: .r73_ge_scratch:
23399:     mov rax, [rbx+24]
23400:     call gen_expr
23401:     cmp qword [rel r38_fail_n], 0  ; --fail-alloc counts the ordinary path
23402:     jne .r73_ge_plain
23403:     call r65_active                ; not Linux ELF (PE, GUARD_PAGES): the ordinary nirmmita
23404:     test rax, rax
23405:     jz .r73_ge_plain
23406:     call r73_gen_scratch_nirm
23407:     jmp .ge_call_done
23408: .r73_ge_plain:
23409:     call emit_nirmmita_from_rax
23410:     jmp .ge_call_done
```

src/sutram_compiler.asm:23607–23620
```text
23607: .ge_call_parimana:
23608:     ; R107: parimana() -> the bytes the program's nirmmita and kosh hold now: the arena's
23609:     ; persistent side (cur - start) and scratch side (sima - end), and the kosh regions
23610:     ; (0parimana, counted at each region's allocation and growth). Linux ELF (direct, --object, --separate); on PE 0.
23611:     call r65_active
23612:     test rax, rax
23613:     jnz .pm_arena
23614:     mov dil, 0x31                  ; xor eax,eax
23615:     call emit_byte
23616:     mov dil, 0xC0
23617:     call emit_byte
23618:     jmp .ge_call_done
23619: .pm_arena:
23620:     call r65_ensure_globals
```

src/sutram_compiler.asm:24195–24249
```text
24195: .ge_call_charfr:
24196:     ; char_from(code) → pointer to a char (writes code to a temp buffer)
24197:     ; Uses a static 1-byte buffer in BSS
24198:     mov rax, [rbx+24]
24199:     call gen_expr
24200:     ; lea rdi, [rel char_buf] — we need the runtime address
24201:     ; But lea [rel] in generated code needs the address at link time
24202:     ; Instead: mov [rsp-1], al; lea rax, [rsp-1]
24203:     ; sub rsp, 16 = 48 83 EC 10
24204:     mov dil, 0x48
24205:     call emit_byte
24206:     mov dil, 0x83
24207:     call emit_byte
24208:     mov dil, 0xEC
24209:     call emit_byte
24210:     mov dil, 0x10
24211:     call emit_byte
24212:     ; mov [rsp], al = 88 04 24
24213:     mov dil, 0x88
24214:     call emit_byte
24215:     mov dil, 0x04
24216:     call emit_byte
24217:     mov dil, 0x24
24218:     call emit_byte
24219:     ; mov byte [rsp+1], 0 = C6 44 24 01 00
24220:     mov dil, 0xC6
24221:     call emit_byte
24222:     mov dil, 0x44
24223:     call emit_byte
24224:     mov dil, 0x24
24225:     call emit_byte
24226:     mov dil, 0x01
24227:     call emit_byte
24228:     xor edi, edi
24229:     call emit_byte
24230:     ; mov rax, rsp = 48 89 E0
24231:     mov dil, 0x48
24232:     call emit_byte
24233:     mov dil, 0x89
24234:     call emit_byte
24235:     mov dil, 0xE0
24236:     call emit_byte
24237:     ; add rsp, 8 (preserve the byte for return) = 48 83 C4 08
24238:     mov dil, 0x48
24239:     call emit_byte
24240:     mov dil, 0x83
24241:     call emit_byte
24242:     mov dil, 0xC4
24243:     call emit_byte
24244:     mov dil, 0x08
24245:     call emit_byte
24246:     jmp .ge_call_done
24247: 
24248: .ge_call_charup:
24249:     ; char_upper(ch) → uppercase ASCII letter code
```

win/winrt_blob.asm:29–44
```text
29:     push rbx
30:     push rbp
31:     push rsi
32:     push rdi
33:     push rdx
34:     push r8
35:     push r9
36:     push r10
37:     push r11
38:     push r12
39:     push r13
40:     push r14
41:     push r15
42:     mov r12,rax
43:     mov r13,rdi
44:     mov r14,rsi
```
