; ============================================================
; Sutram Compiler — Sutram Compiler — Sanskrit → x86-64
; ============================================================
; Pure x86-64 assembly. No libc, no C, no Python.
; Reads .sk source, produces a raw ELF executable.
;
; CALLING CONVENTION:
;   - Arguments in rdi, rsi, rdx, rcx, r8, r9
;   - Return value in rax
;   - Callee-saved: rbx, r12, r13, r14, r15, rbp
;   - Caller-saved: rax, rcx, rdx, rsi, rdi, r8-r11
;   - Every function must push/pop any callee-saved reg it uses
;   - Stack must be 16-byte aligned before every CALL
;
; Build: nasm -f elf64 Sutram Compiler -o sc.o && ld -o sc sc.o
; Run:   ./Sutram compiler input.sk output.bin
; ============================================================

BITS 64

BASE_ADDR    equ 0x400000
ELF_HDR_SIZE equ 64
PHDR_SIZE    equ 56
HEADERS_SIZE equ 120
TOKEN_SIZE   equ 40
TOKEN_CAP    equ 65537      ; max one token per source byte + EOF
STR_POOL_CAP equ 65537      ; max lexeme bytes + terminators for 64 KiB source
IMPORT_BUF_CAP equ 65536    ; expanded source cannot exceed source_buf
AST_NODE_SIZE equ 72
BLOCK_STMT_CAP equ 256        ; B11: max statements stored in one AST_BLOCK
AST_BLOCK_EXTRA equ (BLOCK_STMT_CAP * 8) - (AST_NODE_SIZE - 16)
AST_HEAP_CAP equ 786432       ; T18/R12: 4x headroom (~10922 regular nodes)
FUNC_PARAMS_CAP equ 8192      ; 1024 parameter-name slots; >= 128 funcs * 6 args
VAR_TABLE_CAP equ 256         ; entries; 16 bytes each
FUNC_TABLE_CAP equ 128        ; entries; matches func_defs capacity
PATCH_LIST_CAP equ 512        ; entries; 16 bytes each
FUNC_DEFS_CAP equ 128         ; entries; 8 bytes each
CODE_BUF_CAP equ 262144       ; generated machine-code bytes; 4x guarded headroom
BREAK_PATCH_CAP equ 1024      ; active break patch entries across nested loops
CONTINUE_PATCH_CAP equ 1024   ; active continue patch entries across nested loops
RACHANA_CAP equ 16            ; 256-byte entries in 4096-byte table
RACHANA_FIELDS_CAP equ 15     ; 16-byte header + 15*16-byte fields = 256 bytes
BLOCK_NESTING_CAP equ 128     ; parser recursion guard for nested blocks
NS_FUNC_CAP equ 128         ; max exported user functions in an aliased module
NS_FUNC_NAME_CAP equ 63    ; max function name bytes for module rewrite
NS_ALIAS_CAP equ 31        ; ASCII alias bound, excluding terminator
IMPORT_NAMES_CAP equ 16       ; 64-byte dedupe slots
KOSH_VAR_CAP equ 256          ; growable-array names tracked per generated scope
KOSH_PARAM_VAR_CAP equ 6      ; user functions accept at most six parameters
PARAM_RAW equ 0               ; untyped/integer scalar parameter
PARAM_DASHAM equ 1            ; scalar IEEE-754 binary64 parameter
PARAM_KOSH equ 2              ; integer/raw-qword growable-array parameter
PARAM_KOSH_DASHAM equ 3       ; binary64 growable-array parameter

; Token types
TOK_KEYWORD   equ 1
TOK_IDENT     equ 2
TOK_NUMBER    equ 3
TOK_OPERATOR  equ 4
TOK_DELIMITER equ 5
TOK_BUILTIN   equ 6
TOK_EOF       equ 0
TOK_STRING    equ 7
TOK_FLOAT     equ 8    ; T12 IEEE-754 binary64 literal

; AST node types
AST_NUM       equ 1
AST_VAR       equ 2
AST_ASSIGN    equ 3
AST_BINOP     equ 4
AST_IF        equ 5
AST_WHILE     equ 6
AST_RETURN    equ 7
AST_CALL      equ 8
AST_DECL      equ 9
AST_BLOCK     equ 10
AST_FUNC      equ 11
AST_HALT      equ 12
AST_WRITEMEM  equ 13
AST_STR       equ 14
AST_VEC       equ 15
AST_FUNCDEF   equ 16
AST_FUNCALL   equ 17
AST_INDEX     equ 18    ; array read: [type][name_ptr][index_node]
AST_FIELD     equ 19    ; field access: [type][name_ptr][field_offset]
AST_FOR       equ 20    ; for loop: [type][var_name][start_expr][end_expr][body][0]
AST_BREAK     equ 21    ; break: [type][0][0][0][0]
AST_CONTINUE  equ 22    ; continue: [type][0][0][0][0]
AST_ASSERT    equ 23    ; assert: [type][cond_expr][0][0][0]
AST_TERNARY   equ 27    ; conditional expr: [type][cond][true_expr][false_expr]
AST_DO_WHILE  equ 28    ; do-while stmt: [type][body][cond]
AST_FLOAT     equ 29    ; T12 IEEE-754 binary64 bits in field1
FUNC_SPILL_BYTES equ 2048 ; reserved stack spill area per generated function/main
; R31 experimental, disabled by default. Enable only with NASM:
;   -DSUTRAM_EXPERIMENTAL_XMM_CACHE=1
; This is a *compiler build* feature flag, not a source-language flag.
; When omitted, zero generated-code paths or data change. Stage 1 uses only
; volatile XMM2-XMM5, never XMM6-XMM15 (Windows nonvolatile).


; Operator IDs
OP_ADD equ 1
OP_SUB equ 2
OP_MUL equ 3
OP_DIV equ 4
OP_EQ  equ 5
OP_LE  equ 6
OP_LT  equ 7
OP_GT  equ 8
OP_GE  equ 9
OP_NE  equ 10
OP_MOD equ 11   ; modulo (%)
OP_AND equ 12   ; bitwise AND (&)
OP_OR  equ 13   ; bitwise OR (|)
OP_XOR equ 14   ; bitwise XOR (^)
OP_LAND equ 15  ; logical AND (&&)
OP_LOR equ 16   ; logical OR (||)
OP_SHL equ 17   ; shift left (<<)
OP_SHR equ 18   ; shift right (>>)

; Keyword IDs
KW_MUKHYA  equ 2
KW_VITTI   equ 3
KW_ANKA    equ 4
KW_YADI    equ 6
KW_YAVAT   equ 8
KW_PRATIYATI equ 9
KW_SANKHYA   equ 10
KW_ANYATRA  equ 11
KW_PRAKRIYA equ 12
KW_AYOJAN  equ 13
KW_RACHANA equ 14
KW_PUNARAVARTANA equ 15
KW_ATHA equ 16    ; atha = then/to (contextual keyword for for-loop)
KW_SUTRA    equ 17    ; sutra = compile-time constant (rule/formula)
KW_NISHEDHA equ 18    ; nishedha = assert/guard (prohibition)
KW_KRAMA    equ 19    ; krama = break (order/sequence - stop)
KW_UDDESHYA equ 20    ; uddeshya = continue (purpose - skip)
KW_PURNA   equ 21    ; purna = true (complete/full)
KW_SHUNYA  equ 22    ; shunya = false (void/empty)
KW_PARIGRAH equ 23   ; parigrah = bool type (possession/holding)
KW_SRIJANA  equ 24   ; srijana = enum (creation)
KW_GUNA     equ 25   ; guna = switch (quality/attribute)
KW_BHAVANA  equ 26   ; bhavana = case (state/condition)
KW_NISHKRIYA equ 27   ; nishkriya = inline assembly
KW_PANKTI    equ 28   ; pankti = array (row/line in Sanskrit)
KW_KURU      equ 29   ; kuru = do (imperative Sanskrit, for do-while)
KW_DASHAM    equ 30   ; dasham / दशम = scalar IEEE-754 binary64
KW_KOSH      equ 31   ; kosh / कोश = growable qword array
AST_NISHKRIYA equ 26  ; inline asm statement node

; Builtin IDs
BN_LIKH     equ 1
BN_STHAGITA equ 3
BN_PAD      equ 4
BN_DVARAM   equ 5
BN_PAADH    equ 6
BN_LIKHA    equ 7
BN_BAND     equ 8
BN_NETSOCK  equ 9
BN_NETBIND  equ 10
BN_NETLIST  equ 11
BN_NETACC   equ 12
BN_NIRMRITA equ 13
BN_LIKH8    equ 14
BN_PAD8     equ 15
BN_VARTLEN  equ 16
BN_VARTCMP  equ 17
BN_VARTCAT  equ 18
BN_VECADD  equ 19
BN_VECMUL  equ 20
BN_VECDOT  equ 21
BN_LKFMT   equ 22
BN_CHARAT  equ 23
BN_CHARCD  equ 24
BN_CHARFR  equ 25
BN_CHARUP  equ 26
BN_CHARLO  equ 27
BN_LIKH8C  equ 28
BN_PAD8C   equ 29
BN_MEMSET  equ 30
BN_MEMCPY  equ 31
BN_VARTCP  equ 32
BN_GRAHAN  equ 33   ; grahan = read number from stdin
BN_LKHB     equ 34   ; lkhb = print number without newline
BN_SHABDA   equ 35   ; shabda = print a NUL-terminated string (variable)
BN_PANKTILEN equ 36   ; pankti_len = array length for declared arrays
BN_KOSHPUSH equ 37   ; kosh_push(k, value) -> new length
BN_KOSHPOP  equ 38   ; kosh_pop(k) -> removed value
BN_KOSHLEN  equ 39   ; kosh_len(k) -> logical length
BN_KOSHCAP  equ 40   ; kosh_cap(k) -> current capacity
BN_SETCHAR  equ 41   ; R50 one-byte store into byte-packed text

; ============================================================
; DATA
; ============================================================
section .data
str_dot_exe  db ".exe", 0
    msg_usage    db "Sutram — the complete thread", 10
                  db "Usage:", 10
                  db "  sutram <input.sm> <output.bin>          compile", 10
                  db "  sutram --check <input.sm>               parse/check, no output binary", 10
                  db "  sutram --lang <pack> <in.sm> <out.bin>  with language pack", 10
                  db "  sutram -i                               interactive shell", 10
                  db "  sutram --version                        version info", 10, 0
    msg_version  db "Sutram 1.0 (v29) — the complete thread", 10
                  db "Sanskrit-keyword language -> x86-64 machine code", 10, 0
    r48_flag db "--check",0
    r48_msg_near db ": Sutram Error [E_PARSE]: near '",0
    r48_msg_end db "'",10,0
    r48_msg_ok db "Sutram check: OK (no output binary)",10,0
    r48_msg_errors db "Sutram check: errors found; no output binary",10,0
    r48_msg_eof db "<EOF>",0
    r50_msg_setchar_arity db "Sutram Error: set_char requires exactly 3 arguments",10,0
    r48_msg_undefined db ": Sutram Error [E_UNDEFINED_FUNCTION]: unknown function '",0
    msg_err_line db 10, "Sutram Error: parse error at line ", 0
    msg_err_near db " near token '", 0
    msg_err_end  db "'", 10, 0
    msg_err_eof  db "end of file", 0
    msg_err_hint db "Hint: check the keyword spelling and syntax near this spot.", 10, 0
    msg_err_colon db ":", 0
    msg_diag_indent db "  ", 0
    msg_diag_space db " ", 0
    msg_diag_tab db 9, 0
    msg_diag_nl db 10, 0
    msg_diag_caret db "^", 10, 0
    msg_err_arg_limit db "Hint: functions accept at most 6 arguments.", 10, 0
    msg_err_duplicate_func db "Hint: duplicate function definition (module/program name collision).", 10, 0
    msg_duplicate_func db "Sutram Error: duplicate function definition: ", 0
    msg_undefined_func db "Sutram Error: undefined function: ", 0
    msg_array_oob db "Sutram Error: array index out of bounds", 10, 0
    msg_kosh_required db "Sutram Error: kosh builtin requires a kosh variable", 10, 0
    msg_kosh_empty db "Sutram Error: kosh pop from empty array", 10, 0
    msg_kosh_param_type db "Sutram Error: kosh parameter requires matching kosh element type", 10, 0
    msg_kosh_param_push db "Sutram Error: kosh_push on a kosh parameter is not supported", 10, 0

    ; ===== Localized error messages (v27) =====
    ; Index: 0=default 1=bengali 2=gujarati 3=hindi 4=kannada 5=malayalam
    ;        6=marathi 7=odia 8=punjabi 9=tamil 10=telugu
    err_line_bn db 10, "à¦¸à§à¦¤à§à¦°à¦®à§ à¦¤à§à¦°à§à¦à¦¿: à¦ªà¦à¦à§à¦¤à¦¿ ", 0
    err_near_bn db " à¦à¦° à¦à¦¾à¦à§ à¦à§à¦à§à¦¨ '", 0
    err_eof_bn  db "à¦«à¦¾à¦à¦²à§à¦° à¦¶à§à¦·", 0
    err_hint_bn db "à¦ªà¦°à¦¾à¦®à¦°à§à¦¶: à¦à¦ à¦¸à§à¦¥à¦¾à¦¨à§à¦° à¦à¦¾à¦à§ à¦à§à¦à¦¶à¦¬à§à¦¦à§à¦° à¦¬à¦¾à¦¨à¦¾à¦¨ à¦ à¦¸à¦¿à¦¨à§à¦à§à¦¯à¦¾à¦à§à¦¸ à¦ªà¦°à§à¦à§à¦·à¦¾ à¦à¦°à§à¦¨à¥¤", 10, 0
    open_err_bn db "à¦¤à§à¦°à§à¦à¦¿: à¦à¦¨à¦ªà§à¦ à¦«à¦¾à¦à¦² à¦à§à¦²à¦¾ à¦¯à¦¾à¦à§à¦à§ à¦¨à¦¾", 10, 0

    err_line_gu db 10, "àª¸à«àª¤à«àª°àª®à« àª­à«àª²: àªªàªàªà«àª¤àª¿ ", 0
    err_near_gu db " àª¨àªà«àª àªà«àªàª¨ '", 0
    err_eof_gu  db "àª«àª¾àªàª²àª¨à« àªàªàª¤", 0
    err_hint_gu db "àª¸àªàªà«àª¤: àª àª¸à«àª¥àª³àª¨à« àª¨àªà«àª àªà«àªàª¶àª¬à«àª¦àª¨à« àªà«àª¡àª£à« àªàª¨à« àªµàª¾àªà«àª¯àª°àªàª¨àª¾ àªàªàª¾àª¸à«.", 10, 0
    open_err_gu db "àª­à«àª²: àªàª¨àªªàªàª àª«àª¾àªàª² àªà«àª²à« àª¶àªà« àª¨àª¹à«àª", 10, 0

    err_line_hi db 10, "à¤¸à¥à¤¤à¥à¤°à¤®à¥ à¤¤à¥à¤°à¥à¤à¤¿: à¤ªà¤à¤à¥à¤¤à¤¿ ", 0
    err_near_hi db " à¤à¥ à¤ªà¤¾à¤¸ à¤à¥à¤à¤¨ '", 0
    err_eof_hi  db "à¤«à¤¼à¤¾à¤à¤² à¤à¤¾ à¤à¤à¤¤", 0
    err_hint_hi db "à¤¸à¤à¤à¥à¤¤: à¤à¤¸ à¤¸à¥à¤¥à¤¾à¤¨ à¤à¥ à¤ªà¤¾à¤¸ à¤à¥à¤à¤¶à¤¬à¥à¤¦ à¤à¥ à¤µà¤°à¥à¤¤à¤¨à¥ à¤à¤° à¤µà¤¾à¤à¥à¤¯-à¤°à¤à¤¨à¤¾ à¤à¤¾à¤à¤à¥à¤à¥¤", 10, 0
    open_err_hi db "à¤¤à¥à¤°à¥à¤à¤¿: à¤à¤¨à¤ªà¥à¤ à¤«à¤¼à¤¾à¤à¤² à¤¨à¤¹à¥à¤ à¤à¥à¤²à¥", 10, 0

    err_line_kn db 10, "à²¸à³à²¤à³à²°à²®à³ à²¦à³à²·: à²¸à²¾à²²à³ ", 0
    err_near_kn db " à²¬à²³à²¿ à²à³à²à²¨à³ '", 0
    err_eof_kn  db "à²à²¡à²¤à²¦ à²à²à²¤à³à²¯", 0
    err_hint_kn db "à²¸à³à²à²¨à³: à² à²¸à³à²¥à²³à²¦ à²¬à²³à²¿ à²à³à²µà²°à³à²¡à³ à²à²¾à²à³à²£à²¿ à²®à²¤à³à²¤à³ à²¸à²¿à²à²à³à²¯à²¾à²à³à²¸à³ à²ªà²°à²¿à²¶à³à²²à²¿à²¸à²¿.", 10, 0
    open_err_kn db "à²¦à³à²·: à²à²¨à³âà²ªà³à²à³ à²à²¡à²¤ à²¤à³à²°à³à²¯à²²à²¾à²à³à²¤à³à²¤à²¿à²²à³à²²", 10, 0

    err_line_ml db 10, "à´¸àµà´¤àµà´°à´ à´ªà´¿à´¶à´àµ: à´µà´°à´¿ ", 0
    err_near_ml db " à´¨àµà´±àµà´±àµ à´à´àµà´¤àµà´¤àµ à´àµà´àµà´à´£àµ '", 0
    err_eof_ml  db "à´«à´¯à´²à´¿à´¨àµà´±àµ à´à´µà´¸à´¾à´¨à´", 0
    err_hint_ml db "à´¸àµà´à´¨: à´ à´¸àµà´¥à´²à´¤àµà´¤à´¿à´¨à´àµà´¤àµà´¤àµ à´àµà´µàµà´¡àµ à´à´àµà´·à´°à´µà´¿à´¨àµà´¯à´¾à´¸à´µàµà´ à´µà´¾à´àµà´àµà´¯à´à´à´¨à´¯àµà´ à´ªà´°à´¿à´¶àµà´§à´¿à´àµà´àµà´.", 10, 0
    open_err_ml db "à´ªà´¿à´¶à´àµ: à´àµ»à´ªàµà´àµà´àµ à´«à´¯àµ½ à´¤àµà´±à´àµà´à´¾à´¨à´¾à´¯à´¿à´²àµà´²", 10, 0

    err_line_mr db 10, "à¤¸à¥à¤¤à¥à¤°à¤®à¥ à¤¤à¥à¤°à¥à¤à¥: à¤à¤³ ", 0
    err_near_mr db " à¤à¥à¤¯à¤¾ à¤à¤µà¤³ à¤à¥à¤à¤¨ '", 0
    err_eof_mr  db "à¤«à¤¾à¤à¤²à¤à¤¾ à¤¶à¥à¤µà¤", 0
    err_hint_mr db "à¤¸à¥à¤à¤¨à¤¾: à¤¯à¤¾ à¤à¤¾à¤à¥ à¤à¥à¤à¤¶à¤¬à¥à¤¦à¤¾à¤à¥ à¤¶à¥à¤¦à¥à¤§à¤²à¥à¤à¤¨ à¤à¤£à¤¿ à¤µà¤¾à¤à¥à¤¯à¤°à¤à¤¨à¤¾ à¤¤à¤ªà¤¾à¤¸à¤¾.", 10, 0
    open_err_mr db "à¤¤à¥à¤°à¥à¤à¥: à¤à¤¨à¤ªà¥à¤ à¤«à¤¾à¤à¤² à¤à¤à¤¡à¤¤à¤¾ à¤à¤²à¥ à¤¨à¤¾à¤¹à¥", 10, 0

    err_line_or db 10, "à¬¸à­à¬¤à­à¬°à¬®à­ à¬¤à­à¬°à­à¬à¬¿: à¬§à¬¾à¬¡à¬¼à¬¿ ", 0
    err_near_or db " à¬ªà¬¾à¬à¬°à­ à¬à­à¬à­à¬¨à­ '", 0
    err_eof_or  db "à¬«à¬¾à¬à¬²à¬° à¬¶à­à¬·", 0
    err_hint_or db "à¬¸à­à¬à¬¨à¬¾: à¬à¬¹à¬¿ à¬¸à­à¬¥à¬¾à¬¨ à¬ªà¬¾à¬à¬°à­ à¬à­à¬µà¬¾à¬°à­à¬¡à­à¬° à¬¬à¬¨à¬¾à¬¨ à¬ à¬¸à¬¿à¬£à­à¬à¬¾à¬à­à¬¸ à¬¯à¬¾à¬à­à¬ à¬à¬°à¬¨à­à¬¤à­à¥¤", 10, 0
    open_err_or db "à¬¤à­à¬°à­à¬à¬¿: à¬à¬¨à¬ªà­à¬à­ à¬«à¬¾à¬à¬²à­ à¬à­à¬²à¬¿à¬¹à­à¬²à¬¾ à¬¨à¬¾à¬¹à¬¿à¬", 10, 0

    err_line_pa db 10, "à¨¸à©à¨¤à¨°à¨®à© à¨à¨²à¨¤à©: à¨²à¨¾à¨à¨¨ ", 0
    err_near_pa db " à¨¦à© à¨¨à©à©à© à¨à©à¨à¨¨ '", 0
    err_eof_pa  db "à¨«à¨¾à¨à¨² à¨¦à¨¾ à¨à©°à¨¤", 0
    err_hint_pa db "à¨¸à©°à¨à©à¨¤: à¨à¨¸ à¨¥à¨¾à¨ à¨¦à© à¨¨à©à©à© à¨à©à¨à¨¸à¨¼à¨¬à¨¦ à¨¦à© à¨¸à¨ªà©à¨²à¨¿à©°à¨ à¨à¨¤à© à¨¸à©°à¨à©à¨à¨¸ à¨à¨¾à¨à¨à©à¥¤", 10, 0
    open_err_pa db "à¨à¨²à¨¤à©: à¨à¨¨à¨ªà©à¨ à¨«à¨¾à¨à¨² à¨¨à¨¹à©à¨ à¨à©à©±à¨²à©à¨¹à©", 10, 0

    err_line_ta db 10, "à®à¯à®¤à¯à®¤à®¿à®°à®®à¯ à®ªà®¿à®´à¯: à®µà®°à®¿ ", 0
    err_near_ta db " à®à®°à¯à®à®¿à®²à¯ à®à¯à®à¯à®à®©à¯ '", 0
    err_eof_ta  db "à®à¯à®ªà¯à®ªà®¿à®©à¯ à®®à¯à®à®¿à®µà¯", 0
    err_hint_ta db "à®à¯à®±à®¿àªªà¯: à®à®¨à¯à®¤ à®à®à®¤à¯à®¤à®¿à®©à¯ à®à®°à¯à®à®¿à®²à¯ à®à¯à®±à®¿à®à¯à®à¯à®²à¯à®²à®¿à®©à¯ à®®à¯à®´à®¿à®¯à¯à®®à¯ à®¤à¯à®à®°à®¿à®¯à®²à¯à®à¯ à®à®°à®¿àªªà®¾à®°à¯à®à¯à®à®µà¯à®®à¯.", 10, 0
    open_err_ta db "à®ªà®¿à®´à¯: à®à®³à¯à®³à¯à®à¯à®à¯à®à¯ à®à¯àªªà¯àªªà¯ à®¤à®¿à®±à®à¯à® à®®à¯à®à®¿à®¯à®µà®¿à®²à¯à®²à¯", 10, 0

    err_line_te db 10, "à°¸à±à°¤à±à°°à°®à± à°¦à±à°·à°: à°µà°°à±à°¸ ", 0
    err_near_te db " à°¦à°à±à°à°° à°à±à°à±à°¨à± '", 0
    err_eof_te  db "à°¦à°¸à±à°¤à±à°°à° à°®à±à°à°¿à°à°ªà±", 0
    err_hint_te db "à°¸à±à°à°¨: à° à°¸à±à°¥à°²à° à°¦à°à±à°à°° à°à±à°²à°à°ªà°¦ à°µà°°à±à°£à°¨, à°¸à°¿à°à°à°¾à°à±à°¸à± à°¤à°¨à°¿à°à± à°à±à°¯à°à°¡à°¿.", 10, 0
    open_err_te db "à°¦à±à°·à°: à°à°¨à±âà°ªà±à°à± à°¦à°¸à±à°¤à±à°°à° à°¤à±à°°à°µà°¬à°¡à°²à±à°¦à±", 10, 0

    ; Language id 0 = default (existing English strings)
    tbl_err_line:
        dq msg_err_line, err_line_bn, err_line_gu, err_line_hi, err_line_kn, err_line_ml, err_line_mr, err_line_or, err_line_pa, err_line_ta, err_line_te
    tbl_err_near:
        dq msg_err_near, err_near_bn, err_near_gu, err_near_hi, err_near_kn, err_near_ml, err_near_mr, err_near_or, err_near_pa, err_near_ta, err_near_te
    tbl_err_eof:
        dq msg_err_eof, err_eof_bn, err_eof_gu, err_eof_hi, err_eof_kn, err_eof_ml, err_eof_mr, err_eof_or, err_eof_pa, err_eof_ta, err_eof_te
    tbl_err_hint:
        dq msg_err_hint, err_hint_bn, err_hint_gu, err_hint_hi, err_hint_kn, err_hint_ml, err_hint_mr, err_hint_or, err_hint_pa, err_hint_ta, err_hint_te
    tbl_open_err:
        dq msg_open_err, open_err_bn, open_err_gu, open_err_hi, open_err_kn, open_err_ml, open_err_mr, open_err_or, open_err_pa, open_err_ta, open_err_te

    lang_names:
        dq 0, ln_bn, ln_gu, ln_hi, ln_kn, ln_ml, ln_mr, ln_or, ln_pa, ln_ta, ln_te
    ln_bn db "bengali", 0
    ln_gu db "gujarati", 0
    ln_hi db "hindi", 0
    ln_kn db "kannada", 0
    ln_ml db "malayalam", 0
    ln_mr db "marathi", 0
    ln_or db "odia", 0
    ln_pa db "punjabi", 0
    ln_ta db "tamil", 0
    ln_te db "telugu", 0

    cur_lang_id dq 0
                  db "      Run 'sutram -i' and type 'sahayata' for help.", 10, 0
    msg_lang_ok  db "Language pack loaded: ", 0
    msg_lang_fail db "Warning: language pack not found: ", 0
    msg_nl       db 10, 0
    str_flag_i   db "-i", 0
    str_flag_shell db "--shell", 0
    str_flag_ver db "--version", 0
    str_flag_v   db "-v", 0
    str_flag_lang db "--lang", 0
    str_envlang  db "SUTRAM_LANG=", 0
    str_envhome  db "HOME=", 0
    str_lp1      db "lang/", 0
    str_lp2      db ".lang", 0
    str_lp3      db "/.local/share/sutram/lang/", 0
    str_procself db "/proc/self/exe", 0
%ifdef WINDOWS
    ; Keep REPL scratch files in the current directory on Windows.  The output
    ; suffix intentionally selects the PE backend for the child compilation.
    str_repl_in  db ".sutram_repl.sm", 0
    str_repl_out db ".sutram_repl.exe", 0
    str_repl_quote db '"', 0
    str_repl_space db " ", 0
    wn_repl_createprocess db "CreateProcessA", 0
    wn_repl_wait          db "WaitForSingleObject", 0
    wn_repl_getexit       db "GetExitCodeProcess", 0
%else
    str_repl_in  db "/tmp/.sutram_repl.sm", 0
    str_repl_out db "/tmp/.sutram_repl.bin", 0
%endif
    str_exit1    db "nirgat", 0
    str_exit2    db "exit", 0
    str_exit3    db "quit", 0
    str_help1    db "sahayata", 0
    str_help2    db "help", 0
    str_sarvam   db "sarvam", 0
    msg_shell_banner db "Sutram Shell v1.0 — the complete thread", 10
                      db "Type a Sutram statement and press Enter. It runs instantly.", 10
                      db "Commands: sahayata (help) | nirgat (exit) | sarvam (show session)", 10, 10, 0
    msg_shell_prompt db "sutra> ", 0
    msg_shell_bye db "Namaste! Session ended.", 10, 0
    msg_shell_help db "Sutram Shell help:", 10
                     db `  likha("Namaste\n")            print text`, 10
                     db "  vitti x = 5             declare variable", 10
                     db "  likha(x + 3)            print expression", 10
                     db "  punaravartana i = 0 to 5 { likha(i) }   loops", 10
                     db "  pankti arr[5]           declare array", 10
                     db "  sarvam                  show full session program", 10
                     db "  nirgat                  exit the shell", 10, 0
    repl_prog_hdr db "mukhya() {", 10, 0
    repl_prog_ftr db 10, "}", 10, 0
    msg_open_err  db "Error: cannot open input file", 10, 0
    msg_parse_err db "Error: parse error at token ", 0
    msg_ok        db "OK: compiled ", 0
    msg_bytes     db " bytes", 10, 0
    dbg_pfb       db 0
    lk_no_nl      dq 0
    for_descend  dq 0      ; 1 = descending for-loop
    newline       db 10, 0

    ; Keyword table: [ptr][type][id] — 24 bytes each
    kw_table:
        dq kw_mukhya,    TOK_KEYWORD, KW_MUKHYA
        dq kw_vitti,     TOK_KEYWORD, KW_VITTI
        dq kw_anka,      TOK_KEYWORD, KW_ANKA
        dq kw_yadi,      TOK_KEYWORD, KW_YADI
        dq kw_yavat,     TOK_KEYWORD, KW_YAVAT
        dq kw_pratiyati, TOK_KEYWORD, KW_PRATIYATI
        ; Vector type
        dq kw_sankhya,   TOK_KEYWORD, KW_SANKHYA
        dq kw_anyatra,  TOK_KEYWORD, KW_ANYATRA
        dq kw_dev_anyatra, TOK_KEYWORD, KW_ANYATRA
        dq kw_prakriya,  TOK_KEYWORD, KW_PRAKRIYA
        dq kw_dev_prakriya, TOK_KEYWORD, KW_PRAKRIYA
        dq kw_ayojan,  TOK_KEYWORD, KW_AYOJAN
        dq kw_rachana,  TOK_KEYWORD, KW_RACHANA
        dq kw_punaravartana, TOK_KEYWORD, KW_PUNARAVARTANA
        dq kw_sutra,      TOK_KEYWORD, KW_SUTRA
        dq kw_nishedha,   TOK_KEYWORD, KW_NISHEDHA
        dq kw_krama,      TOK_KEYWORD, KW_KRAMA
        dq kw_uddeshya,   TOK_KEYWORD, KW_UDDESHYA
        dq kw_purna,      TOK_KEYWORD, KW_PURNA
        dq kw_shunya,     TOK_KEYWORD, KW_SHUNYA
        dq kw_parigrah,   TOK_KEYWORD, KW_PARIGRAH
        dq kw_srijana,    TOK_KEYWORD, KW_SRIJANA
        dq kw_guna,       TOK_KEYWORD, KW_GUNA
        dq kw_bhavana,    TOK_KEYWORD, KW_BHAVANA
        dq kw_pankti,     TOK_KEYWORD, KW_PANKTI
        dq kw_nishkriya,  TOK_KEYWORD, KW_NISHKRIYA
        dq kw_kuru,       TOK_KEYWORD, KW_KURU
        dq kw_dasham,     TOK_KEYWORD, KW_DASHAM
        dq kw_kosh,       TOK_KEYWORD, KW_KOSH
        ; Devanagari equivalents (optional script)
        dq kw_dev_mukhya,    TOK_KEYWORD, KW_MUKHYA
        dq kw_dev_vitti,     TOK_KEYWORD, KW_VITTI
        dq kw_dev_anka,      TOK_KEYWORD, KW_ANKA
        dq kw_dev_yadi,      TOK_KEYWORD, KW_YADI
        dq kw_dev_yavat,     TOK_KEYWORD, KW_YAVAT
        dq kw_dev_pratiyati, TOK_KEYWORD, KW_PRATIYATI
        dq kw_dev_pankti,    TOK_KEYWORD, KW_PANKTI
        dq kw_dev_kuru,      TOK_KEYWORD, KW_KURU
        dq kw_dev_dasham,    TOK_KEYWORD, KW_DASHAM
        dq kw_dev_kosh,      TOK_KEYWORD, KW_KOSH
    kw_table_end:

    ; Builtin table
    bn_table:
        dq bn_likh,     TOK_BUILTIN, BN_LIKH
        dq bn_sthagita, TOK_BUILTIN, BN_STHAGITA
        dq bn_pad,      TOK_BUILTIN, BN_PAD
        dq bn_dvaram,   TOK_BUILTIN, BN_DVARAM
        dq bn_paadh,    TOK_BUILTIN, BN_PAADH
        dq bn_likha,    TOK_BUILTIN, BN_LIKHA
        dq bn_band,     TOK_BUILTIN, BN_BAND
        dq bn_netsock,  TOK_BUILTIN, BN_NETSOCK
        dq bn_netbind,  TOK_BUILTIN, BN_NETBIND
        dq bn_netlist,  TOK_BUILTIN, BN_NETLIST
        dq bn_netacc,   TOK_BUILTIN, BN_NETACC
        dq bn_nirm,     TOK_BUILTIN, BN_NIRMRITA
        dq bn_likh8,    TOK_BUILTIN, BN_LIKH8
        dq bn_pad8,     TOK_BUILTIN, BN_PAD8
        dq bn_vartlen,  TOK_BUILTIN, BN_VARTLEN
        dq bn_vartcmp,  TOK_BUILTIN, BN_VARTCMP
        dq bn_vartcat,  TOK_BUILTIN, BN_VARTCAT
        dq bn_vecadd,   TOK_BUILTIN, BN_VECADD
        dq bn_vecmul,   TOK_BUILTIN, BN_VECMUL
        dq bn_vecdot,   TOK_BUILTIN, BN_VECDOT
        dq bn_lkfmt,    TOK_BUILTIN, BN_LKFMT
        dq bn_charat,   TOK_BUILTIN, BN_CHARAT
        dq bn_charcd,   TOK_BUILTIN, BN_CHARCD
        dq bn_charfr,   TOK_BUILTIN, BN_CHARFR
        dq bn_charup,   TOK_BUILTIN, BN_CHARUP
        dq bn_charlo,   TOK_BUILTIN, BN_CHARLO
        dq bn_likh8c,   TOK_BUILTIN, BN_LIKH8C
        dq bn_pad8c,    TOK_BUILTIN, BN_PAD8C
        dq bn_memset,   TOK_BUILTIN, BN_MEMSET
        dq bn_memcpy,   TOK_BUILTIN, BN_MEMCPY
        dq bn_vartcp,   TOK_BUILTIN, BN_VARTCP
        dq bn_grahan,   TOK_BUILTIN, BN_GRAHAN
        dq bn_lkhb,     TOK_BUILTIN, BN_LKHB
        dq bn_shabda,   TOK_BUILTIN, BN_SHABDA
        dq bn_panktilen, TOK_BUILTIN, BN_PANKTILEN
        dq bn_koshpush, TOK_BUILTIN, BN_KOSHPUSH
        dq bn_koshpop,  TOK_BUILTIN, BN_KOSHPOP
        dq bn_koshlen,  TOK_BUILTIN, BN_KOSHLEN
        dq bn_koshcap,  TOK_BUILTIN, BN_KOSHCAP
        dq bn_setchar,  TOK_BUILTIN, BN_SETCHAR
    bn_table_end:

    ; grahan(): read one line from stdin, parse digits, return in rax.
    ; The read operation itself is emitted through emit_syscall.  Linux gets a
    ; native syscall instruction; PE targets get a rel32 call to rt_syscall,
    ; whose syscall-0 path uses kernel32!ReadFile on the cached stdin handle.
    ;
    ; Replacing the 2-byte Linux syscall with a 5-byte PE call changes the
    ; backwards branch distances in the parse loop, so the common prefix and
    ; target-specific tails are stored separately.
    grahan_prefix_bytes:
        db 0x48, 0x83, 0xEC, 0x10            ; sub rsp, 16
        db 0x45, 0x31, 0xC0                  ; xor r8d, r8d
        ; --- .read_loop ---
        db 0x31, 0xC0                        ; xor eax, eax         (sys_read)
        db 0x31, 0xFF                        ; xor edi, edi         (fd=0)
        db 0x48, 0x89, 0xE6                  ; mov rsi, rsp         (buf)
        db 0xBA, 0x01, 0x00, 0x00, 0x00      ; mov edx, 1          (len)
    grahan_prefix_end:
    GRAHAN_PREFIX_LEN equ grahan_prefix_end - grahan_prefix_bytes

    ; Tail for Linux: follows a 2-byte syscall at offset 19.
    grahan_linux_tail:
        db 0x85, 0xC0                        ; test eax, eax
        db 0x7E, 0x24                        ; jle .eof (+36)
        db 0x0F, 0xB6, 0x14, 0x24            ; movzx edx,[rsp]
        db 0x80, 0xFA, 0x0A                  ; cmp dl, 10
        db 0x74, 0x16                        ; je .done (+22)
        db 0x80, 0xFA, 0x30                  ; cmp dl, '0'
        db 0x7C, 0xE0                        ; jl .read_loop (-32)
        db 0x80, 0xFA, 0x39                  ; cmp dl, '9'
        db 0x7F, 0xDB                        ; jg .read_loop (-37)
        db 0x80, 0xEA, 0x30                  ; sub dl, '0'
        db 0x4D, 0x6B, 0xC0, 0x0A            ; imul r8, r8, 10
        db 0x49, 0x01, 0xD0                  ; add r8, rdx
        db 0xEB, 0xCF                        ; jmp .read_loop (-49)
        ; --- .done ---
        db 0x4C, 0x89, 0xC0                  ; mov rax, r8
        db 0xEB, 0x07                        ; jmp .ret (+7)
        ; --- .eof: EOF -> return -1 ---
        db 0x48, 0xC7, 0xC0, 0xFF, 0xFF, 0xFF, 0xFF ; mov rax, -1
        ; --- .ret ---
        db 0x48, 0x83, 0xC4, 0x10            ; add rsp, 16
    grahan_linux_tail_end:
    GRAHAN_TAIL_LEN equ grahan_linux_tail_end - grahan_linux_tail

    ; Tail for PE: follows a 5-byte call to rt_syscall.  Forward branches keep
    ; the same displacement; only the three branches back to .read_loop grow by 3.
    grahan_pe_tail:
        db 0x85, 0xC0                        ; test eax, eax
        db 0x7E, 0x24                        ; jle .eof (+36)
        db 0x0F, 0xB6, 0x14, 0x24            ; movzx edx,[rsp]
        db 0x80, 0xFA, 0x0A                  ; cmp dl, 10
        db 0x74, 0x16                        ; je .done (+22)
        db 0x80, 0xFA, 0x30                  ; cmp dl, '0'
        db 0x7C, 0xDD                        ; jl .read_loop (-35)
        db 0x80, 0xFA, 0x39                  ; cmp dl, '9'
        db 0x7F, 0xD8                        ; jg .read_loop (-40)
        db 0x80, 0xEA, 0x30                  ; sub dl, '0'
        db 0x4D, 0x6B, 0xC0, 0x0A            ; imul r8, r8, 10
        db 0x49, 0x01, 0xD0                  ; add r8, rdx
        db 0xEB, 0xCC                        ; jmp .read_loop (-52)
        db 0x4C, 0x89, 0xC0                  ; mov rax, r8
        db 0xEB, 0x07                        ; jmp .ret (+7)
        db 0x48, 0xC7, 0xC0, 0xFF, 0xFF, 0xFF, 0xFF ; mov rax, -1
        db 0x48, 0x83, 0xC4, 0x10            ; add rsp, 16
    grahan_pe_tail_end:
    GRAHAN_PE_TAIL_LEN equ grahan_pe_tail_end - grahan_pe_tail

    ; T12 fixed-six-decimal float printer. Input: raw binary64 bits in RAX.
    ; Prefix ends immediately before the platform write syscall/call so the
    ; existing emit_syscall abstraction remains valid for ELF and PE.
    float_print_prefix_bytes:
        db 0x66,0x48,0x0F,0x6E,0xC0                  ; movq xmm0, rax
        db 0x48,0xC7,0xC1,0x40,0x42,0x0F,0x00       ; mov rcx, 1000000
        db 0xF2,0x48,0x0F,0x2A,0xC9                  ; cvtsi2sd xmm1, rcx
        db 0xF2,0x0F,0x59,0xC1                       ; mulsd xmm0, xmm1
        db 0xF2,0x4C,0x0F,0x2D,0xC0                  ; cvtsd2si r8, xmm0
        db 0x48,0x83,0xEC,0x40                       ; sub rsp, 64
        db 0x48,0x8D,0x74,0x24,0x3F                  ; lea rsi,[rsp+63]
        db 0xC6,0x06,0x0A                             ; newline
        db 0x48,0xFF,0xCE                             ; dec rsi
        db 0x45,0x31,0xC9                             ; xor r9d,r9d
        db 0x4D,0x85,0xC0,0x79,0x06                  ; test r8,r8 / jns
        db 0x49,0xF7,0xD8,0x41,0xB1,0x01             ; neg r8 / sign=1
        db 0xB9,0x06,0x00,0x00,0x00                  ; six fractional digits
        db 0x31,0xD2,0x4C,0x89,0xC0                  ; frac loop: xor edx,edx; mov rax,r8
        db 0x41,0xBA,0x0A,0x00,0x00,0x00             ; mov r10d,10
        db 0x49,0xF7,0xF2,0x49,0x89,0xC0             ; div r10; mov r8,rax
        db 0x80,0xC2,0x30,0x88,0x16,0x48,0xFF,0xCE  ; digit/store/dec rsi
        db 0xFF,0xC9,0x75,0xE3                       ; dec ecx; jnz frac loop
        db 0xC6,0x06,0x2E,0x48,0xFF,0xCE             ; '.' / dec rsi
        db 0x4D,0x85,0xC0,0x75,0x08                  ; test r8 / jnz integer loop
        db 0xC6,0x06,0x30,0x48,0xFF,0xCE,0xEB,0x1E  ; integer zero / jump done
        db 0x31,0xD2,0x4C,0x89,0xC0                  ; integer loop
        db 0x41,0xBA,0x0A,0x00,0x00,0x00             ; mov r10d,10
        db 0x49,0xF7,0xF2,0x49,0x89,0xC0             ; div r10; mov r8,rax
        db 0x80,0xC2,0x30,0x88,0x16,0x48,0xFF,0xCE  ; digit/store/dec rsi
        db 0x4D,0x85,0xC0,0x75,0xE2                  ; loop while nonzero
        db 0x45,0x84,0xC9,0x74,0x06                  ; test sign / jz
        db 0xC6,0x06,0x2D,0x48,0xFF,0xCE             ; '-' / dec rsi
        db 0x48,0xFF,0xC6                             ; inc rsi
        db 0x48,0x8D,0x54,0x24,0x40,0x48,0x29,0xF2  ; length = rsp+64-rsi
        db 0xBF,0x01,0x00,0x00,0x00                  ; edi=stdout
        db 0xB8,0x01,0x00,0x00,0x00                  ; eax=write
    float_print_prefix_end:
    FLOAT_PRINT_PREFIX_LEN equ float_print_prefix_end - float_print_prefix_bytes
    float_print_suffix_bytes:
        db 0x48,0x83,0xC4,0x40                       ; add rsp,64
    float_print_suffix_end:
    FLOAT_PRINT_SUFFIX_LEN equ float_print_suffix_end - float_print_suffix_bytes

    kw_mukhya    db "mukhya", 0
    kw_vitti     db "vitti", 0
    kw_anka      db "anka", 0
    kw_yadi      db "yadi", 0
    kw_yavat     db "yavat", 0
    kw_pratiyati db "pratiyati", 0
    kw_sankhya   db "sankhya", 0
    kw_anyatra  db "anyatra", 0
    kw_prakriya db "prakriya", 0
    kw_ayojan  db "ayojan", 0
    kw_rachana db "rachana", 0
    kw_punaravartana db "punaravartana", 0
    kw_to_str   db "to", 0
    kw_sutra    db "sutra", 0
    kw_nishedha db "nishedha", 0
    kw_krama    db "krama", 0
    kw_uddeshya db "uddeshya", 0
    kw_purna    db "purna", 0
    kw_shunya   db "shunya", 0
    kw_parigrah db "parigrah", 0
    kw_srijana  db "srijana", 0
    kw_guna     db "guna", 0
    kw_bhavana  db "bhavana", 0
    kw_pankti   db "pankti", 0
    kw_nishkriya db "nishkriya", 0
    kw_kuru      db "kuru", 0
    kw_dasham    db "dasham", 0
    kw_kosh      db "kosh", 0

    ; Devanagari keyword strings (UTF-8 encoded)
    kw_dev_mukhya    db 0xE0,0xA4,0xAE,0xE0,0xA5,0x81,0xE0,0xA4,0x96,0xE0,0xA5,0x8D,0xE0,0xA4,0xAF, 0
    kw_dev_vitti     db 0xE0,0xA4,0xB5,0xE0,0xA4,0xBF,0xE0,0xA4,0xA4,0xE0,0xA5,0x8D,0xE0,0xA4,0xA4,0xE0,0xA4,0xBF, 0
    kw_dev_anka      db 0xE0,0xA4,0x85,0xE0,0xA4,0x99,0xE0,0xA5,0x8D,0xE0,0xA4,0x95, 0
    kw_dev_yadi      db 0xE0,0xA4,0xAF,0xE0,0xA4,0xA6,0xE0,0xA4,0xBF, 0
    kw_dev_pankti    db 0xE0, 0xA4, 0xAA, 0xE0, 0xA4, 0x99, 0xE0, 0xA5, 0x8D, 0xE0, 0xA4, 0x95, 0xE0, 0xA5, 0x8D, 0xE0, 0xA4, 0xA4, 0xE0, 0xA4, 0xBF, 0
    kw_dev_yavat     db 0xE0,0xA4,0xAF,0xE0,0xA4,0xBE,0xE0,0xA4,0xB5,0xE0,0xA4,0xA4,0xE0,0xA5,0x8D, 0
    kw_dev_kuru      db 0xE0,0xA4,0x95,0xE0,0xA5,0x81,0xE0,0xA4,0xB0,0xE0,0xA5,0x81, 0
    ; दशम
    kw_dev_dasham   db 0xE0,0xA4,0xA6,0xE0,0xA4,0xB6,0xE0,0xA4,0xAE, 0
    ; कोश
    kw_dev_kosh     db 0xE0,0xA4,0x95,0xE0,0xA5,0x8B,0xE0,0xA4,0xB6, 0
            kw_dev_prakriya db 0xE0,0xA4,0xAA,0xE0,0xA5,0x8D,0xE0,0xA4,0xB0,0xE0,0xA4,0x95,0xE0,0xA5,0x8D,0xE0,0xA4,0xB0,0xE0,0xA4,0xBF,0xE0,0xA4,0xAF,0xE0,0xA4,0xBE, 0
    kw_dev_anyatra db 0xE0,0xA4,0x85,0xE0,0xA4,0xA8,0xE0,0xA5,0x8D,0xE0,0xA4,0xAF,0xE0,0xA4,0xA4,0xE0,0xA5,0x8D,0xE0,0xA4,0xB0, 0
    kw_dev_pratiyati db 0xE0,0xA4,0xAA,0xE0,0xA5,0x8D,0xE0,0xA4,0xB0,0xE0,0xA4,0xA4,0xE0,0xA5,0x8D,0xE0,0xA4,0xAF,0xE0,0xA4,0xBE,0xE0,0xA4,0xAF,0xE0,0xA4,0xA4,0xE0,0xA4,0xBF, 0

    bn_likh      db "likh", 0
    bn_sthagita  db "sthagita", 0
    bn_pad       db "pad", 0
    bn_dvaram    db "dvaram", 0
    bn_paadh     db "paadh", 0
    msg_guna_dbg1  db "G1", 10
    msg_guna_dbg2  db "BAD\n", 0
    msg_guna_dbg3  db "LK", 10
    bn_likha     db "likha", 0
    bn_band      db "band", 0
    bn_netsock   db "netsock", 0
    bn_netbind   db "netbind", 0
    bn_netlist   db "netlisten", 0
    bn_netacc    db "netaccept", 0
    bn_nirm      db "nirmmita", 0
    bn_likh8     db "likh8", 0
    bn_pad8      db "pad8", 0
    bn_vartlen   db "vartani_len", 0
    bn_vartcmp   db "vartani_cmp", 0
    bn_vartcat   db "vartani_cat", 0
    bn_vecadd    db "sankhya_yog", 0
    bn_vecmul    db "sankhya_gunan", 0
    bn_vecdot    db "sankhya_dot", 0
    bn_lkfmt     db "likha_fmt", 0
    bn_charat    db "char_at", 0
    bn_setchar   db "set_char", 0
    bn_charcd    db "char_code", 0
    bn_panktilen db "pankti_len", 0
    bn_koshpush db "kosh_push", 0
    bn_koshpop  db "kosh_pop", 0
    bn_koshlen  db "kosh_len", 0
    bn_koshcap  db "kosh_cap", 0
    bn_charfr    db "char_from", 0
    bn_charup    db "char_upper", 0
    bn_charlo    db "char_lower", 0
    bn_likh8c    db "likh8c", 0
    bn_pad8c     db "pad8c", 0
    bn_memset    db "smaran", 0
    bn_memcpy    db "smaran_cp", 0
    bn_vartcp    db "vartani_cp", 0
    bn_grahan    db "grahan", 0
    bn_lkhb      db "lkhb", 0
    bn_shabda    db "shabda", 0

    msg_namespace_error db "Sutram Error: invalid namespaced ayojan (use module@alias, max 31 alias bytes)", 10, 0
    msg_namespace_module_missing db "Sutram Error: namespaced module file not found", 10, 0
    msg_namespace_alias_reuse db "Sutram Error: namespaced alias already assigned to another module", 10, 0
    msg_namespace_func_limit db "Sutram Error: namespaced module has too many or oversized function names", 10, 0
    msg_import_overflow db "Sutram Error: expanded module source too large", 10, 0
    graph_v1_header db '# sutram-module-v1', 0
    graph_msg_cycle db 'E_MODULE_CYCLE', 0
    graph_msg_missing db 'E_MODULE_MISSING', 0
    graph_msg_limit db 'E_MODULE_LIMIT', 0
    graph_msg_invalid db 'E_MODULE_INVALID', 0
    graph_prefix db ': Sutram Error [', 0
    graph_close db ']: ', 0
    graph_arrow db ' -> ', 0
    graph_colon db ':', 0
    r49_unknown_column db "?", 0
    graph_nl db 10,0
    graph_cycle_prefix db 'dependency cycle: ',0
    graph_missing_prefix db 'cannot open import ',0
    graph_limit_prefix db 'too many modules or oversized module',0
    graph_invalid_prefix db 'invalid module name',0
    msg_ast_overflow db "Sutram Error: AST capacity exceeded", 10, 0
    msg_func_params_overflow db "Sutram Error: function parameter table capacity exceeded", 10, 0
    msg_var_table_overflow db "Sutram Error: variable table capacity exceeded", 10, 0
    msg_func_table_overflow db "Sutram Error: function table capacity exceeded", 10, 0
    msg_patch_overflow db "Sutram Error: call patch table capacity exceeded", 10, 0
    msg_func_defs_overflow db "Sutram Error: function definition table capacity exceeded", 10, 0
    msg_break_patch_overflow db "Sutram Error: too many break statements in active loops", 10, 0
    msg_continue_patch_overflow db "Sutram Error: too many continue statements in active loops", 10, 0
    msg_code_overflow db "Sutram Error: generated code capacity exceeded", 10, 0
    msg_rachana_overflow db "Sutram Error: rachana table capacity exceeded", 10, 0
    msg_rachana_fields_overflow db "Sutram Error: too many fields in rachana", 10, 0
    msg_block_nesting_overflow db "Sutram Error: block nesting capacity exceeded", 10, 0
    msg_block_stmt_overflow db "Sutram Error: too many statements in block", 10, 0

section .bss
    source_buf  resb 65536
    source_len  resq 1
    source_path_ptr resq 1      ; original input path for ayojan resolution
    r48_mode resq 1
    r48_error_count resq 1
    r48_parse_rsp resq 1
    r48_stmt_start resq 1
    r48_stmt_valid resq 1
    r48_error_line resq 1
    r48_charbuf resb 4
    ; R51 diagnostic origin maps, bounded to expanded source capacity.
    r51_src_file resq IMPORT_BUF_CAP
    r51_dst_file resq IMPORT_BUF_CAP
    r51_src_off resd IMPORT_BUF_CAP
    r51_dst_off resd IMPORT_BUF_CAP
    r51_import_paths resb IMPORT_NAMES_CAP * 512
    r51_paths_used resq 1
    r51_current_path resq 1
    r51_import_start resq 1
    r51_raw_map resd IMPORT_BUF_CAP
    r51_ns_emit_pos resq 1
    token_arr   resb TOKEN_CAP * TOKEN_SIZE ; capacity matches 64 KiB source + EOF
    token_cnt   resq 1
    token_idx   resq 1
    ast_heap    resb AST_HEAP_CAP
    ast_ptr     resq 1
    str_pool    resb STR_POOL_CAP ; lexer identifier/string storage for max-size source
    import_buf  resb IMPORT_BUF_CAP ; dedicated ayojan expansion buffer
    ns_active resq 1
    ns_alias resb 32
    ns_dedupe_key resb 64
    ns_raw_buf resb IMPORT_BUF_CAP
    ns_raw_len resq 1
    ns_func_count resq 1
    ns_func_names resb NS_FUNC_CAP * 64
    ns_func_is_const resb NS_FUNC_CAP ; 1 for top-level sutra, 0 for prakriya
    module_path_buf resb 512      ; dedicated ayojan path scratch
    str_ptr     resq 1
    code_buf    resb CODE_BUF_CAP
    code_sz     resq 1
    var_table   resb VAR_TABLE_CAP * 16 ; [name_ptr(8)][offset(8)]
    var_cnt     resq 1
    stack_dep   resq 1
    array_vars  resq 256        ; T8b: pankti names in current generated-function scope
    array_var_cnt resq 1
    kosh_vars   resq KOSH_VAR_CAP ; T18 growable-array names in current generated-function scope
    kosh_var_cnt resq 1
    kosh_param_vars resq KOSH_PARAM_VAR_CAP ; T18: kosh parameters (growth cannot replace caller ptr)
    kosh_param_var_cnt resq 1
    float_kosh_vars resq KOSH_VAR_CAP ; T18: kosh dasham element-type names in current scope
    float_kosh_var_cnt resq 1
    float_vars  resq VAR_TABLE_CAP ; T12 dasham names in current generated-function scope
    float_var_cnt resq 1
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    ; Stage 1 within-basic-block virtual cache. Fixed logical slots 1..4 map
    ; to XMM2..XMM5. GPRs/stack remain authoritative at ALL times (write-through).
    ; Dirty stays zero: no delayed spills can cross calls/branches/return edges.
    xmm_cache_valid_mask resq 1
    xmm_cache_live_mask resq 1
    xmm_cache_dirty_mask resq 1
    xmm_cache_hits resq 1
    xmm_cache_misses resq 1
    xmm_cache_barriers resq 1
%endif
    num_buf     resb 32
    out_fd      resq 1
    root_node   resq 1
    call_args   resb 256
    param_buf_pos resq 1
    blob_calls   resq 256
    blob_call_cnt resq 1
    target_pe    resq 1
    pe_hdr       resb 512
    pe_pad       resb 256
    func_params resb FUNC_PARAMS_CAP ; aggregate parameter-name storage
    func_param_types resb FUNC_PARAMS_CAP / 8 ; T12/T18: PARAM_* byte per parameter slot
    func_table  resb FUNC_TABLE_CAP * 16 ; [name_ptr(8)][code_offset(8)]
    func_count  resq 1
    patch_list   resb PATCH_LIST_CAP * 16 ; [call_offset(8)][name_ptr(8)]
    patch_count  resq 1
    func_defs    resb FUNC_DEFS_CAP * 8 ; [funcdef_node_ptr(8)]
    func_def_cnt resq 1
    top_const_count resq 1
    top_const_nodes resq 128   ; compile-time top-level sutra initializers
    in_function  resq 1       ; 0 = in main, 1 = in user function
    current_func_float resq 1 ; T12: active prakriya returns binary64 when nonzero
    alloc_sizes  resb 1024    ; [name_ptr(8)][size(8)] = 16 bytes each (borrow checker)
    alloc_sz_cnt resq 1
    import_names resb IMPORT_NAMES_CAP * 64 ; fixed 64-byte module-name slots for ayojan dedupe
    import_count resq 1
    import_new_this_pass resq 1  ; R40: transitive import fixed-point tracker
    import_depth_round resq 1   ; R40: bounded graph expansion passes
    ; Single-pass R44 module graph uses mg_* tables below; no duplicate 1MiB
    ; R41 graph_buffers allocation or second DFS state remains.
    graph_detail_ptr resq 1  ; only retained for portable R41 missing diagnostic
    rachana_defs resb RACHANA_CAP * 256 ; [name_ptr(8)][field_count(8)][fields...]
    rachana_cnt  resq 1
    break_patch_positions resq BREAK_PATCH_CAP ; positions of break jmps to backpatch
    break_patch_cnt      resq 1
    continue_patch_positions resq CONTINUE_PATCH_CAP ; positions of continue jmps to backpatch
    continue_patch_cnt      resq 1
    guna_expr   resq 1      ; switch expression for guna parser
    guna_first  resq 1      ; first if node in chain
    guna_last   resq 1      ; last if node in chain
    cur_line    resq 1      ; current source line (error reporting)
    parse_error_kind resq 1 ; 0=generic, 1=too many function args, 2=duplicate function
    parse_block_depth resq 1 ; B10 audit: guarded recursive block nesting depth
    orig_rsp    resq 1      ; original stack ptr at _start (for envp scan)
    ; Language pack support
    lang_file_buf resb 16384 ; contents of .lang file
    lang_w1     resb 64      ; native word scratch
    lang_to_word resb 64     ; native word for 'to' (loop ranges)
    lang_w2     resb 64      ; sanskrit keyword scratch
    lang_kw_strs resb 8192   ; pool for native keyword strings
    lang_str_ptr resq 1      ; current pos in lang_kw_strs
    lang_kw_table resb 2304  ; runtime keyword entries (24 bytes x 96)
    lang_kw_cnt resq 1       ; number of loaded entries
    lang_builtin_table resb 768 ; runtime builtin aliases (24 x 32)
    lang_builtin_cnt resq 1  ; number of loaded builtin aliases
    lang_entry_type resq 1   ; scratch: 1=keyword, 0=builtin
    lang_path_buf resb 256   ; scratch for building paths
    ; REPL support
    repl_line   resb 512     ; one input line
    repl_session resb 8192   ; accumulated program lines
    repl_self   resb 256     ; path of this executable
    repl_argv1  resq 6       ; argv for compile exec
    lang_loaded_name resb 64  ; name of the active language pack
    repl_argv2  resq 3       ; argv for run exec
    repl_envp   resq 1       ; empty envp
    repl_status resq 1       ; child exit status
    repl_total_len resq 1    ; program buffer length
%ifdef WINDOWS
    ; Windows REPL process-launch state.  STARTUPINFOA is 104 bytes on x64;
    ; PROCESS_INFORMATION is 24 bytes.
    repl_cmd_compile resb 1024
    repl_cmd_run     resb 512
    repl_win_si      resb 104
    repl_win_pi      resb 24
    repl_win_exit    resd 1
    repl_win_written resd 1
    p_repl_createprocess resq 1
    p_repl_wait          resq 1
    p_repl_getexit       resq 1
%endif
    pe_charbuf  resb 8       ; scratch for operator chars

; ============================================================
; CODE
; ============================================================
section .text
    global _start

; ============================================================
; ENTRY POINT
; ============================================================

; ============================================================
; SHELL & LANGUAGE PACK RUNTIME
; ============================================================

; get_self_path: remember the compiler path for REPL child launches.
get_self_path:
%ifdef WINDOWS
    ; win_build_argv has already constructed a Linux-like argv array and put
    ; its address in orig_rsp.  Copy argv[0] instead of relying on /proc.
    mov rax, [rel orig_rsp]
    test rax, rax
    jz .gsp_done
    mov rsi, [rax+8]
    test rsi, rsi
    jz .gsp_done
    lea rdi, [rel repl_self]
    call str_copy
%else
    lea rdi, [rel str_procself]
    lea rsi, [rel repl_self]
    mov rdx, 255
    call os_readlink
    test rax, rax
    jle .gsp_done
    lea rcx, [rel repl_self]
    mov byte [rcx + rax], 0
%endif
.gsp_done:
    ret

; env_get_value(rdi = "NAME=") -> rax = value ptr or 0
env_get_value:
    push rbx
    push r12
    mov rbx, rdi                ; name=
    mov r12, [rel orig_rsp]
    mov rax, [r12]              ; argc
    lea r12, [r12 + rax*8 + 16] ; &env[0]
.env_loop:
    mov rsi, [r12]
    test rsi, rsi
    jz .env_notfound
    xor rcx, rcx
.env_cmp:
    mov dl, [rbx + rcx]
    test dl, dl
    jz .env_found
    cmp dl, [rsi + rcx]
    jne .env_next
    inc rcx
    jmp .env_cmp
.env_next:
    add r12, 8
    jmp .env_loop
.env_found:
    lea rax, [rsi + rcx]        ; value ptr
    pop r12
    pop rbx
    ret
.env_notfound:
    xor rax, rax
    pop r12
    pop rbx
    ret

; maybe_load_env_lang: load SUTRAM_LANG pack if the env var is set
maybe_load_env_lang:
    push rbx
    lea rdi, [rel str_envlang]
    call env_get_value
    test rax, rax
    jz .mle_done
    mov rdi, rax
    call try_load_lang
.mle_done:
    pop rbx
    ret

; str_copy(rdi = dst, rsi = src): copy null-terminated string
str_copy:
    push rbx
    mov rbx, rdi
.sc_loop:
    movzx rax, byte [rsi]
    mov [rbx], al
    test al, al
    jz .sc_done
    inc rbx
    inc rsi
    jmp .sc_loop
.sc_done:
    pop rbx
    ret

; str_append(rdi = dst, rsi = src): append src to dst
str_append:
    push rbx
    push r12
    mov rbx, rdi
.sa_find_end:
    cmp byte [rbx], 0
    je .sa_copy
    inc rbx
    jmp .sa_find_end
.sa_copy:
    movzx r12, byte [rsi]
    mov [rbx], r12
    test r12b, r12b
    jz .sa_done
    inc rbx
    inc rsi
    jmp .sa_copy
.sa_done:
    pop r12
    pop rbx
    ret

; try_load_lang(rdi = pack name): search paths, load, report
try_load_lang:
    push rbx
    push r12
    mov r12, rdi                ; save pack name
    ; remember the pack name for the REPL child processes
    lea rdi, [rel lang_loaded_name]
    mov rsi, r12
    call str_copy
    ; path 1: lang/<name>.lang
    lea rdi, [rel lang_path_buf]
    lea rsi, [rel str_lp1]
    call str_copy
    lea rdi, [rel lang_path_buf]
    mov rsi, r12
    call str_append
    lea rdi, [rel lang_path_buf]
    lea rsi, [rel str_lp2]
    call str_append
    lea rdi, [rel lang_path_buf]
    call load_lang_file
    test rax, rax
    jnz .tll_ok
    ; path 2: $HOME/.local/share/sutram/lang/<name>.lang
    lea rdi, [rel str_envhome]
    call env_get_value
    test rax, rax
    jz .tll_fail
    mov rsi, rax
    lea rdi, [rel lang_path_buf]
    call str_copy
    lea rdi, [rel lang_path_buf]
    lea rsi, [rel str_lp3]
    call str_append
    lea rdi, [rel lang_path_buf]
    mov rsi, r12
    call str_append
    lea rdi, [rel lang_path_buf]
    lea rsi, [rel str_lp2]
    call str_append
    lea rdi, [rel lang_path_buf]
    call load_lang_file
    test rax, rax
    jnz .tll_ok
.tll_fail:
    lea rdi, [rel msg_lang_fail]
    call print_str_z
    mov rdi, r12
    call print_str_z
    lea rdi, [rel msg_nl]
    call print_str_z
    xor rax, rax
    pop r12
    pop rbx
    ret
.tll_ok:
    call set_lang_id              ; localize error messages by pack name
    lea rdi, [rel msg_lang_ok]
    call print_str_z
    mov rdi, r12
    call print_str_z
    lea rdi, [rel msg_nl]
    call print_str_z
    mov rax, 1
    pop r12
    pop rbx
    ret

; load_lang_file(rdi = path) -> rax = 1 loaded, 0 failed
; File format: "<native word> <sanskrit keyword>" per line, # comments
load_lang_file:
    push rbx
    push r12
    push r13
    push r14
    push r15
    ; open(path, O_RDONLY)
    xor rsi, rsi
    xor rdx, rdx
    call os_open
    test rax, rax
    js .llf_fail
    mov r12, rax                 ; fd
    ; read(fd, buf, 16384)
    mov rdi, r12
    lea rsi, [rel lang_file_buf]
    mov rdx, 16384
    call os_read
    mov r13, rax                 ; length
    ; close(fd)
    mov rdi, r12
    call os_close
    test r13, r13
    jle .llf_fail
    ; init string pool only on first pack
    cmp qword [rel lang_kw_cnt], 0
    jne .llf_no_init
    lea rax, [rel lang_kw_strs]
    mov [rel lang_str_ptr], rax
.llf_no_init:
    lea r14, [rel lang_file_buf]
    lea r15, [rel lang_file_buf]
    add r15, r13                 ; end
.llf_line:
    cmp r14, r15
    jae .llf_done
    movzx rax, byte [r14]
    cmp al, 10
    je .llf_adv
    cmp al, 13
    je .llf_adv
    cmp al, ' '
    je .llf_adv
    cmp al, 9
    je .llf_adv
    cmp al, '#'
    je .llf_skip_line
    ; --- word 1 (native) -> lang_w1 ---
    lea rbx, [rel lang_w1]
.llf_w1:
    cmp r14, r15
    jae .llf_w1_done
    movzx rax, byte [r14]
    cmp al, ' '
    je .llf_w1_done
    cmp al, 9
    je .llf_w1_done
    cmp al, 10
    je .llf_w1_done
    cmp al, 13
    je .llf_w1_done
    mov [rbx], al
    inc rbx
    inc r14
    jmp .llf_w1
.llf_w1_done:
    mov byte [rbx], 0
    ; skip separators
.llf_sep:
    cmp r14, r15
    jae .llf_w2_done
    movzx rax, byte [r14]
    cmp al, ' '
    je .llf_sep_adv
    cmp al, 9
    je .llf_sep_adv
    jmp .llf_w2
.llf_sep_adv:
    inc r14
    jmp .llf_sep
.llf_w2:
    lea rbx, [rel lang_w2]
.llf_w2c:
    cmp r14, r15
    jae .llf_w2_done
    movzx rax, byte [r14]
    cmp al, 10
    je .llf_w2_done
    cmp al, 13
    je .llf_w2_done
    mov [rbx], al
    inc rbx
    inc r14
    jmp .llf_w2c
.llf_w2_done:
    mov byte [rbx], 0
    ; --- process the pair ---
    ; lookup the sanskrit keyword id
    lea rdi, [rel lang_w2]
    call lookup_keyword          ; rax = 1 found, rdx = id
    test rax, rax
    jz .llf_try_builtin
    mov qword [rel lang_entry_type], 1   ; keyword
    jmp .llf_have_id
.llf_try_builtin:
    lea rdi, [rel lang_w2]
    call lookup_builtin          ; rax = 1 found, rdx = builtin_id
    test rax, rax
    jnz .llf_have_builtin
    ; not a keyword or builtin — is it the contextual 'to' word?
    lea rdi, [rel lang_w2]
    lea rsi, [rel kw_to_str]
    call strcmp
    test rax, rax
    jnz .llf_line                ; unknown entry: skip
    ; store w1 as the native word for 'to' (loop ranges)
    lea rsi, [rel lang_w1]
    lea rdi, [rel lang_to_word]
.llf_tocopy:
    movzx rax, byte [rsi]
    mov [rdi], al
    test al, al
    jz .llf_todone
    inc rdi
    inc rsi
    jmp .llf_tocopy
.llf_todone:
    jmp .llf_line
.llf_have_builtin:
    nop
    mov qword [rel lang_entry_type], 0   ; builtin
.llf_have_id:
    ; copy native word into the pool (rdx = id survives, no calls)
    lea rsi, [rel lang_w1]
    mov rdi, [rel lang_str_ptr]
    mov r13, rdi
.llf_pcopy:
    movzx rax, byte [rsi]
    mov [rdi], al
    test al, al
    jz .llf_pcopy_done
    inc rdi
    inc rsi
    jmp .llf_pcopy
.llf_pcopy_done:
    inc rdi
    mov [rel lang_str_ptr], rdi
    ; store entry in the right table
    cmp qword [rel lang_entry_type], 0
    je .llf_store_builtin
    ; keyword entry
    mov rax, [rel lang_kw_cnt]
    cmp rax, 96
    jge .llf_line
    imul rax, rax, 24
    lea rcx, [rel lang_kw_table]
    mov [rcx + rax], r13
    mov qword [rcx + rax + 8], TOK_KEYWORD
    mov [rcx + rax + 16], rdx
    inc qword [rel lang_kw_cnt]
    jmp .llf_line
.llf_store_builtin:
    ; builtin entry
    mov rax, [rel lang_builtin_cnt]
    cmp rax, 32
    jge .llf_line
    imul rax, rax, 24
    lea rcx, [rel lang_builtin_table]
    mov [rcx + rax], r13
    mov qword [rcx + rax + 8], TOK_BUILTIN
    mov [rcx + rax + 16], rdx
    inc qword [rel lang_builtin_cnt]
    jmp .llf_line
.llf_skip_line:
    cmp r14, r15
    jae .llf_done
    movzx rax, byte [r14]
    cmp al, 10
    je .llf_adv
    inc r14
    jmp .llf_skip_line
.llf_adv:
    inc r14
    jmp .llf_line
.llf_done:
    cmp qword [rel lang_kw_cnt], 0
    je .llf_fail
    mov rax, 1
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
.llf_fail:
    xor rax, rax
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ============================================================
; INTERACTIVE SHELL (REPL)
; ============================================================

shell_main:
    lea rdi, [rel msg_shell_banner]
    call print_str_z
    lea rax, [rel repl_session]
    mov byte [rax], 0
.shell_loop:
    lea rdi, [rel msg_shell_prompt]
    call print_str_z
    ; read a line from stdin
    xor rdi, rdi
    lea rsi, [rel repl_line]
    mov rdx, 512
    call os_read
    test rax, rax
    jle .shell_exit
    lea rcx, [rel repl_line]
    mov byte [rcx + rax], 0
.shell_strip:
    test rax, rax
    jz .shell_stripped
    movzx edx, byte [rcx + rax - 1]
    cmp dl, 10
    je .shell_trim
    cmp dl, 13
    je .shell_trim
    cmp dl, ' '
    je .shell_trim
    jmp .shell_stripped
.shell_trim:
    dec rax
    mov byte [rcx + rax], 0
    jmp .shell_strip
.shell_stripped:
    cmp byte [rcx], 0
    je .shell_loop
    ; exit commands
    lea rdi, [rel repl_line]
    lea rsi, [rel str_exit1]
    call strcmp
    test rax, rax
    jz .shell_exit
    lea rdi, [rel repl_line]
    lea rsi, [rel str_exit2]
    call strcmp
    test rax, rax
    jz .shell_exit
    lea rdi, [rel repl_line]
    lea rsi, [rel str_exit3]
    call strcmp
    test rax, rax
    jz .shell_exit
    ; help commands
    lea rdi, [rel repl_line]
    lea rsi, [rel str_help1]
    call strcmp
    test rax, rax
    jz .shell_help
    lea rdi, [rel repl_line]
    lea rsi, [rel str_help2]
    call strcmp
    test rax, rax
    jz .shell_help
    ; sarvam: show the session
    lea rdi, [rel repl_line]
    lea rsi, [rel str_sarvam]
    call strcmp
    test rax, rax
    jz .shell_show
    ; append the line to the session
    lea rdi, [rel repl_session]
    lea rsi, [rel repl_line]
    call str_append
    lea rdi, [rel repl_session]
    lea rsi, [rel msg_nl]
    call str_append
    ; write program, compile and run it
    call repl_write_program
    call repl_compile_and_run
    jmp .shell_loop
.shell_help:
    lea rdi, [rel msg_shell_help]
    call print_str_z
    jmp .shell_loop
.shell_show:
    lea rdi, [rel repl_prog_hdr]
    call print_str_z
    lea rdi, [rel repl_session]
    call print_str_z
    lea rdi, [rel repl_prog_ftr]
    call print_str_z
    jmp .shell_loop
.shell_exit:
    lea rdi, [rel msg_shell_bye]
    call print_str_z
    jmp do_exit

; fd_write_str(rdi = fd, rsi = str): write null-terminated string
fd_write_str:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    mov r12, rsi
    xor r13, r13
.fws_len:
    cmp byte [r12 + r13], 0
    je .fws_go
    inc r13
    jmp .fws_len
.fws_go:
    mov rdi, rbx
    mov rsi, r12
    mov rdx, r13
    call os_write
    pop r13
    pop r12
    pop rbx
    ret

; repl_write_program: write mukhya(){session} to the REPL scratch source.
; Linux deliberately keeps the original raw-syscall path byte-for-byte.
repl_write_program:
%ifdef WINDOWS
    ; CreateFileA(str_repl_in, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
    ;             FILE_ATTRIBUTE_NORMAL, NULL)
    push rbx
    push r12
    sub rsp, 56                  ; shadow + args 5..7, keep Win64 alignment
    lea rcx, [rel str_repl_in]
    mov rdx, 0x40000000          ; GENERIC_WRITE
    xor r8d, r8d                 ; no sharing needed for scratch file
    xor r9d, r9d                 ; lpSecurityAttributes = NULL
    mov qword [rsp+32], 2        ; CREATE_ALWAYS
    mov qword [rsp+40], 0x80     ; FILE_ATTRIBUTE_NORMAL
    mov qword [rsp+48], 0        ; hTemplateFile = NULL
    call qword [rel p_createfile]
    cmp rax, -1                  ; INVALID_HANDLE_VALUE
    je .rwp_win_done
    mov r12, rax
    mov rdi, r12
    lea rsi, [rel repl_prog_hdr]
    call repl_win_write_str
    mov rdi, r12
    lea rsi, [rel repl_session]
    call repl_win_write_str
    mov rdi, r12
    lea rsi, [rel repl_prog_ftr]
    call repl_win_write_str
    mov rcx, r12
    call qword [rel p_closehandle]
.rwp_win_done:
    add rsp, 56
    pop r12
    pop rbx
    ret
%else
    push rbx
    push r12
    lea rdi, [rel str_repl_in]
    mov rsi, 0x241               ; O_WRONLY|O_CREAT|O_TRUNC
    mov rdx, 0x1A4               ; 0644
    mov rax, 2                   ; sys_open
    syscall
    test rax, rax
    js .rwp_done
    mov r12, rax                 ; fd
    mov rdi, r12
    lea rsi, [rel repl_prog_hdr]
    call fd_write_str
    mov rdi, r12
    lea rsi, [rel repl_session]
    call fd_write_str
    mov rdi, r12
    lea rsi, [rel repl_prog_ftr]
    call fd_write_str
    mov rdi, r12
    mov rax, 3                   ; sys_close
    syscall
.rwp_done:
    pop r12
    pop rbx
    ret
%endif

%ifdef WINDOWS
; repl_win_write_str(rdi=HANDLE, rsi=zstr)
; WriteFile helper used only by the compiler-host REPL scratch file.
repl_win_write_str:
    push rbx
    push r12
    push r13
    sub rsp, 48                  ; Win64 shadow + OVERLAPPED argument
    mov rbx, rdi
    mov r12, rsi
    xor r13, r13
.rww_len:
    cmp byte [r12+r13], 0
    je .rww_go
    inc r13
    jmp .rww_len
.rww_go:
    mov rcx, rbx
    mov rdx, r12
    mov r8, r13
    lea r9, [rel repl_win_written]
    mov qword [rsp+32], 0
    call qword [rel p_writefile]
    add rsp, 48
    pop r13
    pop r12
    pop rbx
    ret
%endif

; repl_compile_and_run: compile the accumulated session, then run it.
repl_compile_and_run:
%ifdef WINDOWS
    ; Build a mutable CreateProcessA command line.  CreateProcessA is allowed
    ; to modify lpCommandLine, so these live in BSS rather than .data.
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_quote]
    call str_copy
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel repl_self]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_quote]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_space]
    call str_append

    lea rax, [rel lang_loaded_name]
    cmp byte [rax], 0
    je .rcr_win_plain
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_flag_lang]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_space]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel lang_loaded_name]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_space]
    call str_append
.rcr_win_plain:
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_quote]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_in]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_quote]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_space]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_quote]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_out]
    call str_append
    lea rdi, [rel repl_cmd_compile]
    lea rsi, [rel str_repl_quote]
    call str_append

    lea rdi, [rel repl_cmd_compile]
    call repl_win_spawn
    test eax, eax
    jne .rcr_win_ret             ; compiler failed: do not run stale output

    lea rdi, [rel repl_cmd_run]
    lea rsi, [rel str_repl_quote]
    call str_copy
    lea rdi, [rel repl_cmd_run]
    lea rsi, [rel str_repl_out]
    call str_append
    lea rdi, [rel repl_cmd_run]
    lea rsi, [rel str_repl_quote]
    call str_append
    lea rdi, [rel repl_cmd_run]
    call repl_win_spawn
.rcr_win_ret:
    ret
%else
    ; build compile argv (with --lang if a pack is active)
    lea rax, [rel repl_argv1]
    lea rcx, [rel repl_self]
    mov [rax], rcx
    lea rdx, [rel lang_loaded_name]
    cmp byte [rdx], 0
    je .rcr_plain
    lea rcx, [rel str_flag_lang]
    mov [rax+8], rcx
    lea rcx, [rel lang_loaded_name]
    mov [rax+16], rcx
    lea rcx, [rel str_repl_in]
    mov [rax+24], rcx
    lea rcx, [rel str_repl_out]
    mov [rax+32], rcx
    mov qword [rax+40], 0
    jmp .rcr_fork_compile
.rcr_plain:
    lea rcx, [rel str_repl_in]
    mov [rax+8], rcx
    lea rcx, [rel str_repl_out]
    mov [rax+16], rcx
    mov qword [rax+24], 0
.rcr_fork_compile:
    mov rax, 57                  ; sys_fork
    syscall
    test rax, rax
    js .rcr_ret
    jz .rcr_child_compile
    mov rdi, rax
    lea rsi, [rel repl_status]
    xor rdx, rdx
    xor r10, r10
    mov rax, 61                  ; sys_wait4
    syscall
    cmp dword [rel repl_status], 0
    jne .rcr_ret                 ; compile failed: skip run
    ; build run argv
    lea rax, [rel repl_argv2]
    lea rcx, [rel str_repl_out]
    mov [rax], rcx
    mov qword [rax+8], 0
    mov rax, 57                  ; sys_fork
    syscall
    test rax, rax
    js .rcr_ret
    jz .rcr_child_run
    mov rdi, rax
    lea rsi, [rel repl_status]
    xor rdx, rdx
    xor r10, r10
    mov rax, 61                  ; sys_wait4
    syscall
.rcr_ret:
    ret
.rcr_child_compile:
    lea rdi, [rel repl_self]
    lea rsi, [rel repl_argv1]
    lea rdx, [rel repl_envp]
    mov rax, 59                  ; sys_execve
    syscall
    mov rdi, 127
    mov rax, 60
    syscall
.rcr_child_run:
    lea rdi, [rel str_repl_out]
    lea rsi, [rel repl_argv2]
    lea rdx, [rel repl_envp]
    mov rax, 59                  ; sys_execve
    syscall
    mov rdi, 127
    mov rax, 60
    syscall
%endif

%ifdef WINDOWS
; Resolve the process APIs lazily.  They are host-only and deliberately stay
; out of the embedded generated-program runtime.
repl_win_init:
    cmp qword [rel p_repl_createprocess], 0
    jne .rwi_done
    lea rdi, [rel wn_repl_createprocess]
    call win_resolve
    mov [rel p_repl_createprocess], rax
    lea rdi, [rel wn_repl_wait]
    call win_resolve
    mov [rel p_repl_wait], rax
    lea rdi, [rel wn_repl_getexit]
    call win_resolve
    mov [rel p_repl_getexit], rax
.rwi_done:
    ret

; repl_win_spawn(rdi=mutable command line) -> eax=child exit code, -1 on error
repl_win_spawn:
    push rbx
    push r12
    push r13
    mov r12, rdi
    call repl_win_init
    cmp qword [rel p_repl_createprocess], 0
    je .rws_fail_nostack
    cmp qword [rel p_repl_wait], 0
    je .rws_fail_nostack
    cmp qword [rel p_repl_getexit], 0
    je .rws_fail_nostack

    ; Clear STARTUPINFOA and PROCESS_INFORMATION on every launch.
    lea rdi, [rel repl_win_si]
    xor eax, eax
    mov ecx, 13                  ; 13 qwords = 104 bytes
    rep stosq
    lea rdi, [rel repl_win_pi]
    mov ecx, 3                   ; 3 qwords = 24 bytes
    rep stosq
    mov dword [rel repl_win_si], 104
    mov dword [rel repl_win_exit], -1

    ; Entry RSP is 8 mod 16. Three pushes above make it aligned; 80 bytes
    ; supplies 32-byte shadow space plus CreateProcessA arguments 5..10.
    sub rsp, 80
    xor ecx, ecx                 ; lpApplicationName = NULL (parse command line)
    mov rdx, r12                 ; mutable lpCommandLine
    xor r8d, r8d                 ; process attributes
    xor r9d, r9d                 ; thread attributes
    mov qword [rsp+32], 1        ; inherit console/std handles
    mov qword [rsp+40], 0        ; creation flags
    mov qword [rsp+48], 0        ; inherit environment
    mov qword [rsp+56], 0        ; current directory
    lea rax, [rel repl_win_si]
    mov [rsp+64], rax
    lea rax, [rel repl_win_pi]
    mov [rsp+72], rax
    call qword [rel p_repl_createprocess]
    test eax, eax
    jz .rws_fail

    ; The thread handle is no longer needed once the process has started.
    mov rcx, [rel repl_win_pi+8]
    test rcx, rcx
    jz .rws_wait
    call qword [rel p_closehandle]
.rws_wait:
    mov rcx, [rel repl_win_pi]
    mov edx, 0xFFFFFFFF          ; INFINITE
    call qword [rel p_repl_wait]
    mov rcx, [rel repl_win_pi]
    lea rdx, [rel repl_win_exit]
    call qword [rel p_repl_getexit]
    mov rcx, [rel repl_win_pi]
    call qword [rel p_closehandle]
    mov eax, [rel repl_win_exit]
    add rsp, 80
    pop r13
    pop r12
    pop rbx
    ret
.rws_fail:
    add rsp, 80
.rws_fail_nostack:
    mov eax, -1
    pop r13
    pop r12
    pop rbx
    ret
%endif

; The Windows host stores argc/argv in win_stack, NOT at native process RSP.
; Keep OS thread stack intact (for WinAPI/unwind), switch only argument loads.
%ifdef WINDOWS
%define R49_ARG(n) [rel win_stack + n]
%else
%define R49_ARG(n) [rsp + n]
%endif

_start:
%ifdef R49_WIN_DIAG_0
    ; CI-only entrypoint probe. Normal builds never include this.
    mov eax, 71
    ret
%endif
    mov [rel orig_rsp], rsp
%ifdef WINDOWS
    call rt_init                ; resolve kernel32 before any I/O
%ifdef R49_WIN_DIAG_1
    mov eax, 72
    ret
%endif
    call win_build_argv         ; build argc/argv from GetCommandLineA
%ifdef R49_WIN_DIAG_2
    mov eax, 73
    ret
%endif
%endif
    call get_self_path
    ; decide the output format now: .exe -> Windows PE, else Linux ELF
%ifdef WINDOWS
    mov qword [rel target_pe], 1
%else
    mov rax, R49_ARG(0)
    cmp rax, 3
    jl .tp_done
    mov rdi, R49_ARG(24)           ; argv[2] = output file
    test rdi, rdi
    jz .tp_done
    call want_pe
    mov [rel target_pe], rax
.tp_done:
%endif
    ; argc check
    mov rax, R49_ARG(0)
    cmp rax, 2
    jl .usage
    ; -i / --shell : interactive REPL
    mov rdi, R49_ARG(16)
    lea rsi, [rel str_flag_i]
    call strcmp
    test rax, rax
    jz shell_main
    mov rdi, R49_ARG(16)
    lea rsi, [rel str_flag_shell]
    call strcmp
    test rax, rax
    jz shell_main
    ; --version / -v
    mov rdi, R49_ARG(16)
    lea rsi, [rel str_flag_ver]
    call strcmp
    test rax, rax
    jz .show_version
    mov rdi, R49_ARG(16)
    lea rsi, [rel str_flag_v]
    call strcmp
    test rax, rax
    jz .show_version
    ; R48 --check <input.sm>: use the real lexer/parser/codegen semantic
    ; validation without ever creating the output file.
    mov rdi, R49_ARG(16)
    lea rsi, [rel r48_flag]
    call strcmp
    test rax, rax
    jnz .not_check_mode
    mov rax, R49_ARG(0)
    cmp rax, 3
    jl .usage
    mov qword [rel r48_mode], 1
    mov rax, R49_ARG(24)
    mov R49_ARG(16), rax           ; normalize input argument for normal I/O
    call maybe_load_env_lang
    jmp .args_ok
.not_check_mode:
    ; --lang <pack> <in.sm> <out.bin>
    mov rdi, R49_ARG(16)
    lea rsi, [rel str_flag_lang]
    call strcmp
    test rax, rax
    jz .lang_mode
    ; normal mode
    mov rax, R49_ARG(0)
    cmp rax, 3
    jl .usage
    call maybe_load_env_lang
    jmp .args_ok
.lang_mode:
    mov rax, R49_ARG(0)
    cmp rax, 5
    jl .usage
    mov rdi, R49_ARG(24)           ; argv[2] = pack name
    call try_load_lang
    ; rewrite argv[1]/argv[2] to point at input/output
    mov rax, R49_ARG(32)           ; argv[3] = input
    mov R49_ARG(16), rax
    mov rax, R49_ARG(40)           ; argv[4] = output
    mov R49_ARG(24), rax
    jmp .args_ok
.show_version:
    lea rdi, [rel msg_version]
    call print_str_z
    jmp do_exit
.usage:
    lea rdi, [rel msg_usage]
    call print_str_z
    jmp do_exit
.args_ok:
    ; Read source file
    mov rdi, R49_ARG(16)          ; argv[1]
    mov [rel source_path_ptr], rdi
    call read_file
    mov [rel source_len], rax
%ifdef R49_WIN_DIAG_3
    mov eax, [rel source_len]   ; host exit = actual bytes read
    ret
%endif

    ; R41: opt-in module-v1 graph preflight runs BEFORE destructive expansion.
    ; The legacy import and generated-code path is byte-for-byte unchanged.
    call graph_preflight_v1   ; R44 single graph traversal (dispatch to merged Muse DFS)
%ifdef R49_WIN_DIAG_4
    mov eax, 74
    ret
%endif
    ; Expand imports (inline .smlib files)
    call expand_imports
%ifdef R49_WIN_DIAG_5
    mov eax, 75
    ret
%endif
    ; Lex
    call lex
%ifdef R49_WIN_DIAG_6
    mov eax, 76
    ret
%endif

    ; Parse using the ordinary parser, but in check mode recover at a safe
    ; statement/brace boundary after each parser error and restart the parser.
.r48_parse_again:
    mov qword [rel token_idx], 0
    cmp qword [rel r48_mode], 0
    je .r48_parse_normal
    mov [rel r48_parse_rsp], rsp
    mov qword [rel r48_stmt_valid], 0
    mov qword [rel func_def_cnt], 0
    mov qword [rel parse_block_depth], 0
.r48_parse_normal:
    call parse_program
%ifdef R49_WIN_DIAG_7
    mov eax, 77
    ret
%endif
    cmp qword [rel r48_mode], 0
    je .r48_generate
    cmp qword [rel r48_error_count], 0
    jne .r48_check_fail
.r48_generate:
    ; Generate code. --check intentionally still validates generator-side
    ; semantic constraints; code is kept in memory and never written.
    mov qword [rel code_sz], 0
    call gen_code
    cmp qword [rel r48_mode], 0
    je .r48_normal_write
    lea rdi, [rel r48_msg_ok]
    call print_str_z
    jmp do_exit
.r48_check_fail:
    lea rdi, [rel r48_msg_errors]
    call print_str_z
    mov rdi, 1
    call os_exit
.r48_parse_failure:
    ; A parser may jump here with arbitrary nested expression/AST stack
    ; frames. Restore its saved top-level stack before attempting recovery.
    mov rsp, [rel r48_parse_rsp]
    call r48_print_parse_error
    inc qword [rel r48_error_count]
    cmp qword [rel r48_error_count], 8
    jae .r48_check_fail
    call r48_recover_stmt
    test rax, rax
    jz .r48_check_fail
    jmp .r48_parse_again
.r48_normal_write:
    ; Write output
    mov rdi, R49_ARG(24)           ; argv[2]
    call write_elf

    ; Print success
    lea rdi, [rel msg_ok]
    call print_str_z
    mov rdi, [rel code_sz]
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    lea rdi, [rel msg_bytes]
    call print_str_z

do_exit:
    xor rdi, rdi
    call os_exit

; build_module_path_from_file(rdi=file path)
; Build <directory-of-file>/lib/<module>.smlib into module_path_buf.
; If the file path contains no slash/backslash, use ./lib/...
build_module_path_from_file:
    push rbx
    push r12
    mov r12, rdi
    lea rbx, [rel module_path_buf]
    xor rcx, rcx
    xor r8, r8                  ; position just after last separator
.bmp_scan:
    mov al, [r12 + rcx]
    test al, al
    jz .bmp_scanned
    cmp al, '/'
    je .bmp_mark
    cmp al, 92                  ; '\\'
    jne .bmp_next
.bmp_mark:
    lea r8, [rcx + 1]
.bmp_next:
    inc rcx
    cmp rcx, 240
    jb .bmp_scan
.bmp_scanned:
    test r8, r8
    jnz .bmp_copy_dir
    mov byte [rbx], '.'
    mov byte [rbx+1], '/'
    mov rdi, rbx
    add rdi, 2
    jmp .bmp_append_lib
.bmp_copy_dir:
    xor rcx, rcx
.bmp_dir_loop:
    cmp rcx, r8
    jae .bmp_dir_done
    mov al, [r12 + rcx]
    mov [rbx + rcx], al
    inc rcx
    jmp .bmp_dir_loop
.bmp_dir_done:
    lea rdi, [rbx + rcx]
.bmp_append_lib:
    mov byte [rdi], 'l'
    mov byte [rdi+1], 'i'
    mov byte [rdi+2], 'b'
    mov byte [rdi+3], '/'
    add rdi, 4
    lea rsi, [rel num_buf]
.bmp_name:
    mov al, [rsi]
    test al, al
    jz .bmp_suffix
    mov [rdi], al
    inc rdi
    inc rsi
    jmp .bmp_name
.bmp_suffix:
    mov byte [rdi], '.'
    mov byte [rdi+1], 's'
    mov byte [rdi+2], 'm'
    mov byte [rdi+3], 'l'
    mov byte [rdi+4], 'i'
    mov byte [rdi+5], 'b'
    mov byte [rdi+6], 0
    pop r12
    pop rbx
    ret

; build CWD-relative lib/<module>.smlib into module_path_buf
build_module_path_cwd:
    lea rdi, [rel module_path_buf]
    mov byte [rdi], 'l'
    mov byte [rdi+1], 'i'
    mov byte [rdi+2], 'b'
    mov byte [rdi+3], '/'
    add rdi, 4
    lea rsi, [rel num_buf]
.bmpc_name:
    mov al, [rsi]
    test al, al
    jz .bmpc_suffix
    mov [rdi], al
    inc rdi
    inc rsi
    jmp .bmpc_name
.bmpc_suffix:
    mov byte [rdi], '.'
    mov byte [rdi+1], 's'
    mov byte [rdi+2], 'm'
    mov byte [rdi+3], 'l'
    mov byte [rdi+4], 'i'
    mov byte [rdi+5], 'b'
    mov byte [rdi+6], 0
    ret

; ============================================================
; R41: opt-in module-v1 dependency graph preflight, pure x86-64 NASM.
; This rejects cycles/missing modules before the R40 visited-set expansion.
; It changes NOTHING for existing files without an exact v1 header.
; Contract: source-order DFS, dependencies before importer, siblings in source
; order, and each module visited once. Runtime initializers are NOT yet supplied.
; Source-path diagnostics point at the importing file and directive line.
; ============================================================
graph_preflight_v1:
    ; R44: one module graph traversal, preserving R41 exact-header semantics.
    ; The merged Muse DFS is authoritative; duplicate R41 scan was removed.
    mov byte [rel mg_root_exact_v1], 0
    lea rdi, [rel source_buf]
    lea rsi, [rel graph_v1_header]
    xor rcx, rcx
.r44_header:
    mov al, [rsi + rcx]
    test al, al
    jz .r44_eol
    cmp rcx, [rel source_len]
    jae .r44_done
    cmp al, [rdi + rcx]
    jne .r44_done
    inc rcx
    jmp .r44_header
.r44_eol:
    cmp byte [rdi + rcx], 10
    je .r44_optin
    cmp byte [rdi + rcx], 13
    jne .r44_done
.r44_optin:
    mov byte [rel mg_root_exact_v1], 1
.r44_done:
    jmp check_module_graph

; R44: historic R41 graph_scan/graph_visit removed. The Muse DFS now performs
; the ONE native dependency traversal for modern and legacy programs.

; File:line uses a stable basename so golden diagnostics remain portable
; across checkout locations on Windows/Linux.
graph_print_file:
    push rbx
    mov rbx,rdi
.find_separator:
    mov al,[rdi]
    test al,al
    jz .basename
    cmp al,'/'
    je .mark
    cmp al,92
    jne .advance
.mark:
    lea rbx,[rdi+1]
.advance:
    inc rdi
    jmp .find_separator
.basename:
    mov rdi,rbx
    call print_str_z
    pop rbx
    ret

; R49 check-only accurate location for an ayojan module directive.
; Reads the original importer (not flattened source), searches that line for
; the actual "ayojan" keyword and returns an honest column.  If the original
; location cannot be recovered, use '?' rather than fabricating column 1.
; rdi = original importer path, rsi = original 1-based line.
r49_print_module_location:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r12, rdi
    mov r13, rsi
    call graph_print_file
    lea rdi, [rel graph_colon]
    call print_str_z
    mov rax, r13
    call mg_print_uint
    lea rdi, [rel graph_colon]
    call print_str_z
    mov rdi, r12
    call mg_read_file
    test rax, rax
    js .r49_unknown
    mov r14, rax             ; original file size
    lea rbx, [rel mg_buf]
    xor r9, r9               ; byte position
    mov r8, 1                ; current source line
.r49_findline:
    cmp r8, r13
    jae .r49_on_line
    cmp r9, r14
    jae .r49_unknown
    cmp byte [rbx+r9], 10
    jne .r49_nextline
    inc r8
.r49_nextline:
    inc r9
    jmp .r49_findline
.r49_on_line:
    mov r15, r9             ; byte start of original physical line
.r49_findword:
    mov rax, r9
    add rax, 6
    cmp rax, r14
    ja .r49_unknown
    cmp byte [rbx+r9], 10
    je .r49_unknown
    cmp dword [rbx+r9], 0x6A6F7961 ; little endian "ayoj"
    jne .r49_nextword
    cmp word [rbx+r9+4], 0x6E61     ; "an"
    jne .r49_nextword
    mov rax, r9
    sub rax, r15
    inc rax                 ; 1-based position on this physical line
    ; Count ASCII module-keyword positions precisely. The keyword itself is
    ; ASCII; tabs before it count as one source column, like calc_src_column.
    call mg_print_uint
    jmp .r49_done
.r49_nextword:
    inc r9
    jmp .r49_findword
.r49_unknown:
    lea rdi, [rel r49_unknown_column]
    call print_str_z
.r49_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; Diagnostic rdi=importer path, rsi=1-based line, rdx=code, rcx=message.
; Print to stdout to match the existing compiler's diagnostic convention.
graph_error:
    push rcx               ; message prefix (printed second)
    push rdx               ; error code     (printed first)
    push rsi               ; line
    cmp qword [rel r48_mode], 0
    jne .r49_check_location
    call graph_print_file
    lea rdi,[rel graph_colon]
    call print_str_z
    pop rdi
    lea rsi,[rel num_buf]
    call itoa
    mov rdi,rax
    call print_str_z
    jmp .r49_after_location
.r49_check_location:
    pop rsi
    call r49_print_module_location
.r49_after_location:
    lea rdi,[rel graph_prefix]
    call print_str_z
    pop rdi
    call print_str_z
    lea rdi,[rel graph_close]
    call print_str_z
    pop rdi
    call print_str_z
    mov rdi,[rel graph_detail_ptr]
    test rdi,rdi
    jz .no_detail
    call print_str_z
.no_detail:
    lea rdi,[rel graph_nl]
    call print_str_z
    mov rdi,1
    call os_exit

; ============================================================
; MODULE IMPORT - expand ayojan directives
; Scans source for ayojan <name> and inlines lib/<name>.smlib
; ============================================================
; R40: Expand transitive imports in bounded, deterministic breadth-first rounds.
; The visited module key table is shared by every round, so diamond imports
; include the same module source once. Existing legacy imports remain accepted.
; NOTE: this is still single-translation-unit source expansion; NOT object-file
; separate compilation. Cyclic edges currently collapse via visited keys rather
; than yielding a cycle diagnostic. Do not advertise this as the complete module
; system until that distinct failure mode and export isolation exist.
expand_imports:
    push rbx
    mov qword [rel import_count], 0
    mov qword [rel import_depth_round], 0
.ei_round:
    mov qword [rel import_new_this_pass], 0
    call expand_imports_pass
    cmp qword [rel import_new_this_pass], 0
    je .ei_finished
    inc qword [rel import_depth_round]
    cmp qword [rel import_depth_round], IMPORT_NAMES_CAP
    jbe .ei_round
    lea rdi,[rel msg_import_overflow]
    call print_str_z
    mov rdi,1
    call os_exit
.ei_finished:
    pop rbx
    ret

expand_imports_pass:
    push rbx
    push r12
    push r13
    push r14
    lea rsi, [rel source_buf]
    lea rdi, [rel import_buf] ; dedicated expanded-source output buffer
    xor r12, r12              ; source pos
    mov r13, [rel source_len]
    xor r14, r14              ; output pos
.ei_loop:
    cmp r12, r13
    jae .ei_done
    ; Check for comment lines — skip them (don't look for ayojan inside)
    lea rsi, [rel source_buf]
    add rsi, r12
    movzx eax, byte [rsi]
    cmp eax, '#'
    je .ei_copy_line
    cmp eax, '/'
    jne .ei_check_ayojan
    movzx eax, byte [rsi+1]
    cmp eax, '/'
    jne .ei_check_ayojan
.ei_copy_line:
    ; Copy bytes until newline (inclusive)
    cmp r14, IMPORT_BUF_CAP
    jae .ei_overflow
    lea rsi, [rel source_buf]
    movzx eax, byte [rsi + r12]
    lea rdi, [rel import_buf]
    mov [rdi + r14], al
    inc r12
    inc r14
    cmp eax, 10
    je .ei_loop
    cmp r12, r13
    jae .ei_loop
    jmp .ei_copy_line
.ei_check_ayojan:
    ; Check for "ayojan" at current pos
    lea rsi, [rel source_buf]
    add rsi, r12
    ; Compare 6 bytes: a(61) y(79) o(6F) j(6A) a(61) n(6E)
    cmp dword [rsi], 0x6A6F7961    ; "ayoj" in LE = 6A 6F 79 61
    jne .ei_copy
    movzx eax, word [rsi+4]
    cmp ax, 0x6E61                   ; "an" in LE = 6E 61
    jne .ei_copy
    ; Found "ayojan" - skip it and module name
    add r12, 6
    ; Skip spaces/newlines
.ei_skip_sp:
    cmp r12, r13
    jae .ei_copy
    lea rsi, [rel source_buf]
    movzx eax, byte [rsi + r12]
    cmp eax, 32
    je .ei_sp_adv
    cmp eax, 10
    je .ei_sp_adv
    cmp eax, 13
    je .ei_sp_adv
    jmp .ei_read_mod
.ei_sp_adv:
    inc r12
    jmp .ei_skip_sp
.ei_read_mod:
    ; Legacy: ayojan math. Namespaced: ayojan math@maths.
    ; The core Sanskrit keyword is unchanged and no runtime lookup is needed.
    mov qword [rel ns_active], 0
    mov byte [rel ns_alias], 0
    lea rdi, [rel num_buf]
    xor rcx, rcx
.ei_mod_loop:
    cmp r12, r13
    jae .ei_mod_done
    lea rsi, [rel source_buf]
    movzx eax, byte [rsi + r12]
    cmp eax, 10
    je .ei_mod_done
    cmp eax, 13
    je .ei_mod_done
    cmp eax, 32
    je .ei_mod_done
    cmp eax, 9
    je .ei_mod_done
    cmp eax, '@'
    je .ei_alias_start
    cmp rcx, 30                 ; bounded module file-name scratch
    jae .ei_namespace_error
    mov [rdi], al
    inc rdi
    inc r12
    inc rcx
    jmp .ei_mod_loop
.ei_alias_start:
    test rcx, rcx
    jz .ei_namespace_error
    mov byte [rdi], 0          ; terminate the module name before alias
    inc r12                    ; consume @
    mov qword [rel ns_active], 1
    lea rdi, [rel ns_alias]
    xor rcx, rcx
.ei_alias_loop:
    cmp r12, r13
    jae .ei_alias_done
    lea rsi, [rel source_buf]
    movzx eax, byte [rsi+r12]
    cmp eax, 10
    je .ei_alias_done
    cmp eax, 13
    je .ei_alias_done
    cmp eax, 32
    je .ei_alias_done
    cmp eax, 9
    je .ei_alias_done
    cmp rcx, NS_ALIAS_CAP
    jae .ei_namespace_error
    cmp al, '_'
    je .ei_alias_char
    cmp al, 'A'
    jb .ei_alias_digit
    cmp al, 'Z'
    jbe .ei_alias_char
    cmp al, 'a'
    jb .ei_namespace_error
    cmp al, 'z'
    jbe .ei_alias_char
    jmp .ei_namespace_error
.ei_alias_digit:
    test rcx, rcx
    jz .ei_namespace_error    ; leading digit not an identifier
    cmp al, '0'
    jb .ei_namespace_error
    cmp al, '9'
    ja .ei_namespace_error
.ei_alias_char:
    mov [rdi+rcx], al
    inc rcx
    inc r12
    jmp .ei_alias_loop
.ei_alias_done:
    test rcx,rcx
    jz .ei_namespace_error
    mov byte [rdi+rcx], 0
    ; num_buf was already terminated before parsing the alias.
    jmp .ei_build_key
.ei_mod_done:
    mov byte [rdi], 0
.ei_build_key:
    ; R34: opt-in namespace imports must be simple, project-local module names.
    ; Legacy imports deliberately retain their old path interpretation.
    ; Disallow '/' and '.' segments so a namespaced module cannot traverse out
    ; of an intended lib/ lookup root. Allow ASCII alnum, '_' and '-'.
    cmp qword [rel ns_active],0
    je .ei_module_safe
    lea rsi,[rel num_buf]
.ei_validate_mod:
    mov al,[rsi]
    test al,al
    jz .ei_module_safe
    cmp al,'_'
    je .ei_mod_char_ok
    cmp al,'-'
    je .ei_mod_char_ok
    cmp al,'0'
    jb .ei_namespace_error
    cmp al,'9'
    jbe .ei_mod_char_ok
    cmp al,'A'
    jb .ei_namespace_error
    cmp al,'Z'
    jbe .ei_mod_char_ok
    cmp al,'a'
    jb .ei_namespace_error
    cmp al,'z'
    ja .ei_namespace_error
.ei_mod_char_ok:
    inc rsi
    jmp .ei_validate_mod
.ei_module_safe:
    ; Unique dedupe keys incorporate the alias, so one module may be imported
    ; under more than one name. Legacy keys remain identical to their old form.
    lea rsi, [rel num_buf]
    lea rdi, [rel ns_dedupe_key]
    xor rcx,rcx
.ei_key_module:
    mov al,[rsi+rcx]
    test al,al
    jz .ei_key_alias
    cmp rcx, 62
    jae .ei_namespace_error
    mov [rdi+rcx],al
    inc rcx
    jmp .ei_key_module
.ei_key_alias:
    cmp qword [rel ns_active],0
    je .ei_key_done
    cmp rcx,62
    jae .ei_namespace_error
    mov byte [rdi+rcx],'@'
    inc rcx
    lea rsi,[rel ns_alias]
    xor rdx,rdx
.ei_key_alias_copy:
    mov al,[rsi+rdx]
    test al,al
    jz .ei_key_done
    cmp rcx,62
    jae .ei_namespace_error
    mov [rdi+rcx],al
    inc rcx
    inc rdx
    jmp .ei_key_alias_copy
.ei_key_done:
    mov byte [rdi+rcx],0
    ; R34: one alias means one module. An exact duplicate is idempotent, but
    ; importing two different modules under the same alias is ambiguous.
    ; Reuse the existing bounded dedupe table; never allocate a second registry.
    cmp qword [rel ns_active],0
    je .ei_alias_verified
    xor rbx,rbx
.ei_alias_scan:
    cmp rbx,[rel import_count]
    jae .ei_alias_verified
    mov rax,rbx
    shl rax,6
    lea rsi,[rel import_names]
    add rsi,rax
.ei_find_at:
    mov al,[rsi]
    test al,al
    jz .ei_next_alias
    cmp al,'@'
    je .ei_compare_alias
    inc rsi
    jmp .ei_find_at
.ei_compare_alias:
    inc rsi
    lea rdi,[rel ns_alias]
    call strcmp
    test rax,rax
    jne .ei_next_alias
    ; Alias matches: allow only the SAME full module@alias key.
    mov rax,rbx
    shl rax,6
    lea rsi,[rel import_names]
    add rsi,rax
    lea rdi,[rel ns_dedupe_key]
    call strcmp
    test rax,rax
    jz .ei_next_alias
    lea rdi,[rel msg_namespace_alias_reuse]
    call print_str_z
    mov rdi,1
    call os_exit
.ei_next_alias:
    inc rbx
    jmp .ei_alias_scan
.ei_alias_verified:
    ; T4: including the same module twice is idempotent.  Keep a compact list
    ; of module names already expanded during this compilation.
    xor rbx, rbx
.ei_dup_loop:
    cmp rbx, [rel import_count]
    jae .ei_new_module
    lea rsi, [rel import_names]
    mov rax, rbx
    shl rax, 6              ; 64-byte fixed slot
    add rsi, rax
    lea rdi, [rel ns_dedupe_key]
    call strcmp
    test rax, rax
    jz .ei_duplicate_module
    inc rbx
    jmp .ei_dup_loop
.ei_new_module:
    cmp qword [rel import_count], IMPORT_NAMES_CAP
    jb .ei_add_module
    ; Legacy behaviour remains unchanged; namespaced imports must fail closed
    ; once alias deduplication can no longer be guaranteed.
    cmp qword [rel ns_active],0
    je .ei_build_path
    jmp .ei_namespace_error
.ei_add_module:
    mov rax, [rel import_count]
    shl rax, 6
    lea rdi, [rel import_names]
    add rdi, rax
    lea rsi, [rel ns_dedupe_key]
    xor rcx, rcx
.ei_save_name:
    mov dl, [rsi + rcx]
    mov [rdi + rcx], dl
    inc rcx
    test dl, dl
    jz .ei_saved_name
    cmp rcx, 63
    jb .ei_save_name
    mov byte [rdi + 63], 0
.ei_saved_name:
    inc qword [rel import_count]
    jmp .ei_build_path
.ei_duplicate_module:
    ; The directive has already consumed the module name.  Leave at most the
    ; original line ending in the stream; do not inline definitions again.
    jmp .ei_loop
.ei_build_path:
    ; B5: resolve module relative to (1) source-file directory,
    ; (2) compiler executable directory, then (3) current working directory.
    ; This makes ayojan independent of the caller's CWD while preserving the
    ; historical CWD fallback.
    mov rdi, [rel source_path_ptr]
    call build_module_path_from_file
    lea rdi, [rel module_path_buf]
    xor rsi, rsi              ; O_RDONLY
    call os_open
    test rax, rax
    jns .ei_opened

    lea rdi, [rel repl_self]
    call build_module_path_from_file
    lea rdi, [rel module_path_buf]
    xor rsi, rsi
    call os_open
    test rax, rax
    jns .ei_opened

    ; Final backwards-compatible fallback: CWD/lib/<name>.smlib
    call build_module_path_cwd
    lea rdi, [rel module_path_buf]
    xor rsi, rsi
    call os_open
    test rax, rax
    js .ei_missing_module
.ei_opened:
    ; This source was not previously imported: scan newly inserted text in the
    ; next pass. In particular this resolves children of imports and diamonds.
    mov qword [rel import_new_this_pass], 1
    ; Qualified imports run a bounded lexical rename pass on module source.
    ; Existing unqualified imports use the EXACT legacy path below.
    cmp qword [rel ns_active], 0
    jne .ei_namespaced_read
    ; Read module only into the remaining expanded-source capacity.
    mov rbx, rax              ; fd
    cmp r14, IMPORT_BUF_CAP - 1 ; keep room for separator newline
    jae .ei_overflow_close
    lea rsi, [rel import_buf]
    add rsi, r14
    mov rdx, IMPORT_BUF_CAP - 1
    sub rdx, r14
    mov r10, rdx              ; remember requested bytes across syscall
    mov rdi, rbx
    call os_read
    test rax, rax
    js .ei_close_only
    add r14, rax
    cmp rax, r10
    jne .ei_close_success
    ; Buffer filled exactly: probe one more byte so oversized modules fail
    ; cleanly instead of being silently truncated.
    mov rdi, rbx
    lea rsi, [rel num_buf + 31]
    mov rdx, 1
    call os_read
    cmp rax, 0
    jg .ei_overflow_close
    ; If a legacy module exactly fills capacity, the EOF probe returns zero:
    ; close it normally. Do not fall into the namespaced-read path with an
    ; already consumed fd (a previously latent boundary-case bug).
    jmp .ei_close_success
.ei_namespaced_read:
    mov rbx, rax
    lea rsi, [rel ns_raw_buf]
    mov rdx, IMPORT_BUF_CAP - 1
    mov r10, rdx
    mov rdi, rbx
    call os_read
    test rax,rax
    js .ei_close_only
    mov [rel ns_raw_len],rax
    cmp rax,r10
    jne .ei_ns_read_complete
    mov rdi,rbx
    lea rsi,[rel num_buf+31]
    mov rdx,1
    call os_read
    cmp rax,0
    jg .ei_overflow_close
.ei_ns_read_complete:
    mov rdi,rbx
    call os_close
    call ns_collect_funcs
    call ns_strip_niryat         ; drop niryat lines (v1 modules) before rewrite
    call ns_rewrite_funcs        ; updates r14, keeps r12/r13 intact
    jmp .ei_no_file
.ei_close_success:
    ; Close file
    mov rdi, rbx
    call os_close
.ei_no_file:
    ; Namespaced imports fail explicitly instead of silently omitting a file.
    ; The successful namespaced read jumps here after transformation.
    ; Legacy missing-module handling remains unchanged.
    ; Add newline after imported content
    cmp r14, IMPORT_BUF_CAP
    jae .ei_overflow
    lea rdi, [rel import_buf]
    mov byte [rdi + r14], 10
    inc r14
    jmp .ei_loop
.ei_copy:
    cmp r14, IMPORT_BUF_CAP
    jae .ei_overflow
    lea rsi, [rel source_buf]
    movzx eax, byte [rsi + r12]
    lea rdi, [rel import_buf]
    mov [rdi + r14], al
    inc r12
    inc r14
    jmp .ei_loop
.ei_overflow_close:
    mov rdi, rbx
    call os_close
    jmp .ei_overflow
.ei_close_only:
    mov rdi, rbx
    call os_close
    jmp .ei_no_file
.ei_missing_module:
    cmp qword [rel ns_active],0
    je .ei_no_file
    lea rdi,[rel msg_namespace_module_missing]
    call print_str_z
    mov rdi,1
    call os_exit
.ei_namespace_error:
    lea rdi,[rel msg_namespace_error]
    call print_str_z
    mov rdi,1
    call os_exit
.ei_overflow:
    lea rdi, [rel msg_import_overflow]
    call print_str_z
    mov rdi, 1
    call os_exit
.ei_done:
    ; Copy dedicated import buffer back to source_buf
    lea rsi, [rel import_buf]
    lea rdi, [rel source_buf]
    mov rcx, r14
    rep movsb
    mov [rel source_len], r14
    ; Reset str_ptr
    lea rax, [rel str_pool]
    mov [rel str_ptr], rax
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ============================================================
; ROUND 41: module graph pre-pass.
; Three-colour DFS over the import graph BEFORE textual expansion:
;  - visiting -> visiting  =  E_MODULE_CYCLE with file:line and the cycle path
;  - v1 modules (marked "# sutram-module-v1" in both importer and module)
;    get export visibility: `niryat` declares exports; duplicate exports are
;    E_MODULE_DUP_EXPORT; references to alias__<private> from outside the
;    defining module are E_MODULE_NOT_EXPORTED (checked in Phase B below).
;  - v1 modules must be imported with an alias (E_MODULE_V1_ALIAS otherwise).
; The pass is read-only: it never modifies source_buf. Missing module files
; are skipped here and reported by the expansion phase as before.
; ============================================================

section .data
mg_e_cycle:   db "Sutram Error [E_MODULE_CYCLE]: cyclic import: ", 0
mg_e_noexp1:  db "Sutram Error [E_MODULE_NOT_EXPORTED]: '", 0
mg_e_noexp2:  db "' is not exported by module '", 0
mg_e_noexp3:  db "'", 10, 0
mg_e_dupexp1: db "Sutram Error [E_MODULE_DUP_EXPORT]: duplicate export '", 0
mg_e_dupexp2: db "' in module '", 0
mg_e_dupexp3: db "'", 10, 0
mg_e_undef1:  db "Sutram Error [E_EXPORT_UNDEFINED]: export '", 0
mg_e_undef2:  db "' has no matching definition in module '", 0
mg_e_undef3:  db "'", 10, 0
mg_e_unknown1: db "Sutram Error [E_EXPORT_UNDEFINED]: unknown qualified symbol '", 0
mg_e_unknown2: db "' in module '", 0
mg_e_unknown3: db "'", 10, 0
mg_w_sutra:    db "sutra", 0
mg_e_depth:   db "Sutram Error [E_MODULE_DEPTH]: import depth exceeded", 10, 0
mg_e_valias1: db "Sutram Error [E_MODULE_V1_ALIAS]: v1 module '", 0
mg_e_valias2: db "' must be imported with an alias: ayojan ", 0
mg_e_valias3: db "@alias", 10, 0
mg_e_limit:   db "Sutram Error [E_MODULE_LIMIT]: too many modules or imports", 10, 0
mg_root_name: db "__root__", 0
mg_v1_mark:   db "sutram-module-v1", 0
mg_arrow:     db " -> ", 0
mg_colon:     db ":", 0
mg_w_niryat:   db "niryat", 0
mg_w_prakriya: db "prakriya", 0
mg_w_ayojan:   db "ayojan", 0
; Devanagari प्रक्रिया (27 bytes), same as kw_dev_prakriya
mg_w_devprak:  db 0xE0,0xA4,0xAA,0xE0,0xA5,0x8D,0xE0,0xA4,0xB0,0xE0,0xA4,0x95,0xE0,0xA5,0x8D,0xE0,0xA4,0xB0,0xE0,0xA4,0xBF,0xE0,0xA4,0xAF,0xE0,0xA4,0xBE,0

section .bss
mg_buf:       resb 65536
mg_gray:      resb 1024
mg_gray_n:    resq 1
mg_black:     resb 1024
mg_black_n:   resq 1
mg_rec_n:     resq 1
mg_rec_name:  resb 1024
mg_rec_path:  resb 8192
mg_rec_v1:    resb 16
mg_exp:       resb 16384
mg_exp_n:     resb 16
mg_exp_line:  resq 16 * 16       ; line number for each rec/declared export
mg_def:       resb 32768
mg_def_n:     resb 16
mg_imp:       resb 24576
mg_imp_n:     resb 16
mg_list:      resb 2048
mg_list_line: resq 16
mg_list_n:    resq 1
mg_cur_name:  resb 64
mg_cur_path:  resb 512
mg_cur_line:  resq 1
mg_cur_alias: resb 64
mg_path_stk:  resb 8192
mg_tmp_name:  resb 64
mg_tmp_alias: resb 64
mg_pat:       resb 128
mg_root_exact_v1: resb 1 ; R44 preserve R41 header-specific cycle/missing precedence
mg_deferred_alias: resb 1
mg_deferred_alias_name: resb 64
mg_deferred_alias_path: resb 512
mg_deferred_alias_line: resq 1
mg_pat_len:   resq 1    ; R44 qualified-name prefix length

section .text

; --- mg_in_gray: rdi = name -> rax = 1 if on DFS stack, else 0 ---
mg_in_gray:
    push rbx
    push r12
    xor r12, r12
.g_loop:
    cmp r12, [rel mg_gray_n]
    jae .g_no
    mov rax, r12
    shl rax, 6
    lea rsi, [rel mg_gray]
    add rsi, rax
    call strcmp
    test rax, rax
    jz .g_yes
    inc r12
    jmp .g_loop
.g_no:
    xor eax, eax
    jmp .g_done
.g_yes:
    mov eax, 1
.g_done:
    pop r12
    pop rbx
    ret

; --- mg_in_black: rdi = name -> rax = 1 if fully visited, else 0 ---
mg_in_black:
    push rbx
    push r12
    xor r12, r12
.b_loop:
    cmp r12, [rel mg_black_n]
    jae .b_no
    mov rax, r12
    shl rax, 6
    lea rsi, [rel mg_black]
    add rsi, rax
    call strcmp
    test rax, rax
    jz .b_yes
    inc r12
    jmp .b_loop
.b_no:
    xor eax, eax
    jmp .b_done
.b_yes:
    mov eax, 1
.b_done:
    pop r12
    pop rbx
    ret

; --- mg_push_gray: rdi = name (copies to stack top) ---
mg_push_gray:
    push rbx
    mov rax, [rel mg_gray_n]
    shl rax, 6
    lea rbx, [rel mg_gray]
    add rbx, rax
    ; copy NUL-terminated, max 63 chars
    xor rcx, rcx
.pg_copy:
    mov al, [rdi + rcx]
    mov [rbx + rcx], al
    inc rcx
    test al, al
    jz .pg_done
    cmp rcx, 63
    jb .pg_copy
    mov byte [rbx + 63], 0
.pg_done:
    inc qword [rel mg_gray_n]
    pop rbx
    ret

; --- mg_pop_gray ---
mg_pop_gray:
    dec qword [rel mg_gray_n]
    ret

; --- mg_add_black: rdi = name ---
mg_add_black:
    push rbx
    mov rax, [rel mg_black_n]
    shl rax, 6
    lea rbx, [rel mg_black]
    add rbx, rax
    xor rcx, rcx
.ab_copy:
    mov al, [rdi + rcx]
    mov [rbx + rcx], al
    inc rcx
    test al, al
    jz .ab_done
    cmp rcx, 63
    jb .ab_copy
    mov byte [rbx + 63], 0
.ab_done:
    inc qword [rel mg_black_n]
    pop rbx
    ret

; --- mg_find_rec: rdi = name -> rax = record index or -1 ---
mg_find_rec:
    push rbx
    push r12
    xor r12, r12
.fr_loop:
    cmp r12, [rel mg_rec_n]
    jae .fr_no
    mov rax, r12
    shl rax, 6
    lea rsi, [rel mg_rec_name]
    add rsi, rax
    call strcmp
    test rax, rax
    jz .fr_yes
    inc r12
    jmp .fr_loop
.fr_no:
    mov rax, -1
    jmp .fr_done
.fr_yes:
    mov rax, r12
.fr_done:
    pop r12
    pop rbx
    ret

; --- mg_new_rec: rdi = name, rsi = path -> rax = index or -1 ---
mg_new_rec:
    push rbx
    push r12
    cmp qword [rel mg_rec_n], 16
    jae .nr_full
    mov r12, [rel mg_rec_n]
    ; name
    mov rax, r12
    shl rax, 6
    lea rbx, [rel mg_rec_name]
    add rbx, rax
    xor rcx, rcx
.nr_name:
    mov al, [rdi + rcx]
    mov [rbx + rcx], al
    inc rcx
    test al, al
    jz .nr_path
    cmp rcx, 63
    jb .nr_name
    mov byte [rbx + 63], 0
.nr_path:
    mov rax, r12
    shl rax, 9
    lea rbx, [rel mg_rec_path]
    add rbx, rax
    xor rcx, rcx
.nr_pcopy:
    mov al, [rsi + rcx]
    mov [rbx + rcx], al
    inc rcx
    test al, al
    jz .nr_zero
    cmp rcx, 511
    jb .nr_pcopy
    mov byte [rbx + 511], 0
.nr_zero:
    lea rax, [rel mg_rec_v1]
    mov byte [rax + r12], 0
    lea rax, [rel mg_exp_n]
    mov byte [rax + r12], 0
    lea rax, [rel mg_def_n]
    mov byte [rax + r12], 0
    lea rax, [rel mg_imp_n]
    mov byte [rax + r12], 0
    inc qword [rel mg_rec_n]
    mov rax, r12
    jmp .nr_done
.nr_full:
    mov rax, -1
.nr_done:
    pop r12
    pop rbx
    ret

; --- mg_print_uint: rax = number -> prints decimal ---
mg_print_uint:
    push rbx
    sub rsp, 32
    lea rbx, [rsp + 31]
    mov byte [rbx], 0
    mov rcx, 10
.pu_loop:
    xor rdx, rdx
    div rcx
    add dl, '0'
    dec rbx
    mov [rbx], dl
    test rax, rax
    jnz .pu_loop
    mov rdi, rbx
    call print_str_z
    add rsp, 32
    pop rbx
    ret

; --- mg_print_loc: prints "path:line: " using mg_cur_path / mg_cur_line ---
mg_print_loc:
    push rax
    lea rdi, [rel mg_cur_path]
    call print_str_z
    lea rdi, [rel mg_colon]
    call print_str_z
    mov rax, [rel mg_cur_line]
    call mg_print_uint
    lea rdi, [rel mg_colon]
    call print_str_z
    mov al, ' '
    ; print single space via stack
    sub rsp, 16
    mov [rsp], al
    mov byte [rsp+1], 0
    lea rdi, [rsp]
    call print_str_z
    add rsp, 16
    pop rax
    ret

; --- mg_read_file: rdi = path -> rax = bytes read into mg_buf, or -1 ---
mg_read_file:
    push rbx
    push r12
    mov rbx, rdi
    xor rsi, rsi
    xor rdx, rdx
    call os_open
    test rax, rax
    js .rf_fail
    mov r12, rax
    mov rdi, r12
    lea rsi, [rel mg_buf]
    mov rdx, 65536
    call os_read
    push rax
    mov rdi, r12
    call os_close
    pop rax
    jmp .rf_done
.rf_fail:
    mov rax, -1
.rf_done:
    pop r12
    pop rbx
    ret

; --- mg_resolve: rdi = module name -> rax=1 and module_path_buf set, else 0 ---
; Mirrors the expansion's three-step resolution (source dir, exe dir, CWD).
mg_resolve:
    push rbx
    push r12
    mov r12, rdi
    ; num_buf = module name
    lea rbx, [rel num_buf]
    xor rcx, rcx
.rs_name:
    mov al, [r12 + rcx]
    mov [rbx + rcx], al
    inc rcx
    test al, al
    jz .rs_try1
    cmp rcx, 31
    jb .rs_name
    mov byte [rbx + 31], 0
.rs_try1:
    mov rdi, [rel source_path_ptr]
    call build_module_path_from_file
    lea rdi, [rel module_path_buf]
    xor rsi, rsi
    xor rdx, rdx
    call os_open
    test rax, rax
    js .rs_try2
    mov rdi, rax
    call os_close
    mov rax, 1
    jmp .rs_done
.rs_try2:
    lea rdi, [rel repl_self]
    call build_module_path_from_file
    lea rdi, [rel module_path_buf]
    xor rsi, rsi
    xor rdx, rdx
    call os_open
    test rax, rax
    js .rs_try3
    mov rdi, rax
    call os_close
    mov rax, 1
    jmp .rs_done
.rs_try3:
    call build_module_path_cwd
    lea rdi, [rel module_path_buf]
    xor rsi, rsi
    xor rdx, rdx
    call os_open
    test rax, rax
    js .rs_fail
    mov rdi, rax
    call os_close
    mov rax, 1
    jmp .rs_done
.rs_fail:
    xor eax, eax
.rs_done:
    pop r12
    pop rbx
    ret

; --- mg_match_at: rbx=buf, r12=pos, rdx=len, rsi=word -> rax=1 if word matches ---
mg_match_at:
    push rcx
    xor rcx, rcx
.mm_loop:
    mov al, [rsi + rcx]
    test al, al
    jz .mm_yes
    mov r8, r12
    add r8, rcx
    cmp r8, rdx
    jae .mm_no
    cmp al, [rbx + r8]
    jne .mm_no
    inc rcx
    jmp .mm_loop
.mm_yes:
    mov rax, 1
    jmp .mm_done
.mm_no:
    xor eax, eax
.mm_done:
    pop rcx
    ret

; --- mg_is_ident: dil = char -> rax=1 if [A-Za-z0-9_], else 0 ---
mg_is_ident:
    movzx eax, dil
    cmp al, '_'
    je .ii_yes
    cmp al, 'A'
    jb .ii_no
    cmp al, 'Z'
    jbe .ii_yes
    cmp al, 'a'
    jb .ii_no
    cmp al, 'z'
    jbe .ii_yes
    cmp al, '0'
    jb .ii_no
    cmp al, '9'
    jbe .ii_yes
.ii_no:
    xor eax, eax
    ret
.ii_yes:
    mov eax, 1
    ret

; --- mg_check_marker: rbx=buf, r12=pos of '#', rdx=len, r15=rec ---
; Sets mg_rec_v1[r15]=1 if the line is "# sutram-module-v1".
mg_check_marker:
    push rcx
    push r8
    mov r8, r12
    inc r8                       ; skip '#'
.cm_ws:
    cmp r8, rdx
    jae .cm_no
    movzx eax, byte [rbx + r8]
    cmp al, ' '
    je .cm_adv
    cmp al, 9
    jne .cm_match
.cm_adv:
    inc r8
    jmp .cm_ws
.cm_match:
    lea rsi, [rel mg_v1_mark]
    xor rcx, rcx
.cm_loop:
    mov al, [rsi + rcx]
    test al, al
    jz .cm_end_ok
    mov r9, r8
    add r9, rcx
    cmp r9, rdx
    jae .cm_no
    cmp al, [rbx + r9]
    jne .cm_no
    inc rcx
    jmp .cm_loop
.cm_end_ok:
    ; must be followed by end-of-line
    mov r9, r8
    add r9, rcx
    cmp r9, rdx
    jae .cm_yes
    movzx eax, byte [rbx + r9]
    cmp al, 10
    je .cm_yes
    cmp al, 13
    je .cm_yes
    cmp al, ' '
    je .cm_yes
    cmp al, 9
    jne .cm_no
.cm_yes:
    lea r9, [rel mg_rec_v1]
    mov byte [r9 + r15], 1
.cm_no:
    pop r8
    pop rcx
    ret

; --- mg_parse_niryat: rbx=buf, r12=pos of 'n', rdx=len, r13=line, r15=rec ---
; Parses "niryat <name>", adds to exports, errors on duplicates.
mg_parse_niryat:
    push r8
    push r9
    push rcx
    mov r8, r12
    add r8, 6                    ; skip "niryat"
.pn_ws:
    cmp r8, rdx
    jae .pn_bail
    movzx eax, byte [rbx + r8]
    cmp al, ' '
    je .pn_adv
    cmp al, 9
    jne .pn_name
.pn_adv:
    inc r8
    jmp .pn_ws
.pn_name:
    ; read identifier into mg_tmp_name
    lea r9, [rel mg_tmp_name]
    xor rcx, rcx
.pn_rd:
    cmp r8, rdx
    jae .pn_got
    movzx eax, byte [rbx + r8]
    mov dil, al
    call mg_is_ident
    test rax, rax
    jz .pn_got
    cmp rcx, 63
    jae .pn_bail
    movzx eax, byte [rbx + r8]
    mov [r9 + rcx], al
    inc rcx
    inc r8
    jmp .pn_rd
.pn_got:
    test rcx, rcx
    jz .pn_bail
    mov byte [r9 + rcx], 0
    ; duplicate check against mg_exp[r15]
    lea r11, [rel mg_exp_n]
    movzx r10, byte [r11 + r15]
    xor rcx, rcx
.pn_dup:
    cmp rcx, r10
    jae .pn_add
    mov rax, r15
    shl rax, 10                  ; rec * 1024
    mov r11, rcx
    shl r11, 6
    add rax, r11
    lea rsi, [rel mg_exp]
    add rsi, rax
    mov rdi, r9
    call strcmp
    test rax, rax
    jz .pn_dup_err
    inc rcx
    jmp .pn_dup
.pn_dup_err:
    ; E_MODULE_DUP_EXPORT with file:line
    mov [rel mg_cur_line], r13
    call mg_print_loc
    lea rdi, [rel mg_e_dupexp1]
    call print_str_z
    mov rdi, r9
    call print_str_z
    lea rdi, [rel mg_e_dupexp2]
    call print_str_z
    mov rax, r15
    shl rax, 6
    lea rdi, [rel mg_rec_name]
    add rdi, rax
    call print_str_z
    lea rdi, [rel mg_e_dupexp3]
    call print_str_z
    mov rdi, 1
    call os_exit
.pn_add:
    cmp r10, 16
    jae .pn_bail                  ; too many exports; ignore extras
    mov rax, r15
    shl rax, 10
    mov r11, r10
    shl r11, 6
    add rax, r11
    lea rsi, [rel mg_exp]
    add rsi, rax
    mov rdi, r9
    xor rcx, rcx
.pn_cp:
    mov al, [rdi + rcx]
    mov [rsi + rcx], al
    inc rcx
    test al, al
    jnz .pn_cp
    ; Preserve the physical niryat declaration line for diagnostics.
    mov rax, r15
    shl rax, 4
    add rax, r10
    lea r11, [rel mg_exp_line]
    mov [r11 + rax*8], r13
    lea r11, [rel mg_exp_n]
    inc byte [r11 + r15]
.pn_bail:
    mov r12, r8                   ; advance past parsed text
    pop rcx
    pop r9
    pop r8
    ret

; --- mg_parse_prakriya: rbx=buf, r12=pos (after keyword), rdx=len, r15=rec ---
; r8 = keyword length (8 or 27). Collects the defined function name.
mg_parse_prakriya:
    push r8
    push r9
    push rcx
    mov r9, r12
    add r9, r8                    ; skip keyword
.pp_ws:
    cmp r9, rdx
    jae .pp_bail
    movzx eax, byte [rbx + r9]
    cmp al, ' '
    je .pp_adv
    cmp al, 9
    jne .pp_name
.pp_adv:
    inc r9
    jmp .pp_ws
.pp_name:
    lea rsi, [rel mg_tmp_name]
    xor rcx, rcx
.pp_rd:
    cmp r9, rdx
    jae .pp_got
    movzx eax, byte [rbx + r9]
    cmp al, '('
    je .pp_got
    mov dil, al
    call mg_is_ident
    test rax, rax
    jz .pp_got
    cmp rcx, 63
    jae .pp_bail
    movzx eax, byte [rbx + r9]
    mov [rsi + rcx], al
    inc rcx
    inc r9
    jmp .pp_rd
.pp_got:
    test rcx, rcx
    jz .pp_bail
    mov byte [rsi + rcx], 0
    lea r11, [rel mg_def_n]
    movzx r10, byte [r11 + r15]
    cmp r10, 32
    jae .pp_bail
    mov rax, r15
    shl rax, 11                  ; rec * 2048
    mov r11, r10
    shl r11, 6
    add rax, r11
    lea rdi, [rel mg_def]
    add rdi, rax
    xor rcx, rcx
.pp_cp:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .pp_cp
    lea r11, [rel mg_def_n]
    inc byte [r11 + r15]
.pp_bail:
    mov r12, r9
    pop rcx
    pop r9
    pop r8
    ret

; --- mg_verify_exports: r15=record index, mg_cur_path is module path. ---
; Enforces that a v1 niryat names an actual prakriya or sutra definition.
; Legacy non-opt-in imports bypass this check.
mg_verify_exports:
    push rbx
    push r12
    push r13
    push r14
    push r15
    lea rax, [rel mg_rec_v1]
    cmp byte [rax + r15], 0
    je .ve_done
    lea rax, [rel mg_exp_n]
    movzx r12, byte [rax + r15]
    xor r13, r13
.ve_export:
    cmp r13, r12
    jae .ve_done
    mov rax, r15
    shl rax, 10
    mov rcx, r13
    shl rcx, 6
    add rax, rcx
    lea rbx, [rel mg_exp]
    add rbx, rax               ; exported symbol
    lea rax, [rel mg_def_n]
    movzx r14, byte [rax + r15]
    xor r10, r10
.ve_def:
    cmp r10, r14
    jae .ve_missing
    mov rax, r15
    shl rax, 11
    mov rcx, r10
    shl rcx, 6
    add rax, rcx
    lea rsi, [rel mg_def]
    add rsi, rax
    mov rdi, rbx
    push r10
    call strcmp
    pop r10
    test rax, rax
    jz .ve_valid
    inc r10
    jmp .ve_def
.ve_missing:
    mov rax, r15
    shl rax, 4
    add rax, r13
    lea rdx, [rel mg_exp_line]
    mov rax, [rdx + rax*8]
    mov [rel mg_cur_line], rax
    call mg_print_loc
    lea rdi, [rel mg_e_undef1]
    call print_str_z
    mov rdi, rbx
    call print_str_z
    lea rdi, [rel mg_e_undef2]
    call print_str_z
    mov rax, r15
    shl rax, 6
    lea rdi, [rel mg_rec_name]
    add rdi, rax
    call print_str_z
    lea rdi, [rel mg_e_undef3]
    call print_str_z
    mov rdi, 1
    call os_exit
.ve_valid:
    inc r13
    jmp .ve_export
.ve_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- mg_parse_ayojan: rbx=buf, r12=pos of 'a', rdx=len, r13=line ---
; Adds (name, alias, line) to mg_list. Advances r12 past the directive.
mg_parse_ayojan:
    push r8
    push r9
    push rcx
    mov r8, r12
    add r8, 6
.pa_ws:
    cmp r8, rdx
    jae .pa_bail
    movzx eax, byte [rbx + r8]
    cmp al, 32
    je .pa_adv
    cmp al, 10
    je .pa_adv
    cmp al, 13
    je .pa_adv
    jmp .pa_name
.pa_adv:
    inc r8
    jmp .pa_ws
.pa_name:
    lea r9, [rel mg_tmp_name]
    xor rcx, rcx
.pa_rd:
    cmp r8, rdx
    jae .pa_got
    movzx eax, byte [rbx + r8]
    cmp al, 10
    je .pa_got
    cmp al, 13
    je .pa_got
    cmp al, 32
    je .pa_got
    cmp al, 9
    je .pa_got
    cmp al, '@'
    je .pa_alias
    cmp rcx, 63
    jae .pa_bail
    mov [r9 + rcx], al
    inc rcx
    inc r8
    jmp .pa_rd
.pa_got:
    mov byte [r9 + rcx], 0
    jmp .pa_store
.pa_alias:
    mov byte [r9 + rcx], 0
    inc r8
    lea r9, [rel mg_tmp_alias]
    xor rcx, rcx
.pa_aloop:
    cmp r8, rdx
    jae .pa_agot
    movzx eax, byte [rbx + r8]
    cmp al, 10
    je .pa_agot
    cmp al, 13
    je .pa_agot
    cmp al, 32
    je .pa_agot
    cmp al, 9
    je .pa_agot
    mov dil, al
    call mg_is_ident
    test rax, rax
    jz .pa_agot
    cmp rcx, 63
    jae .pa_bail
    movzx eax, byte [rbx + r8]
    mov [r9 + rcx], al
    inc rcx
    inc r8
    jmp .pa_aloop
.pa_agot:
    mov byte [r9 + rcx], 0
    jmp .pa_store2
.pa_store:
    ; no alias: clear temp
    mov byte [rel mg_tmp_alias], 0
.pa_store2:
    cmp qword [rel mg_list_n], 16
    jae .pa_bail
    mov rax, [rel mg_list_n]
    shl rax, 7                   ; *128
    lea rsi, [rel mg_list]
    add rsi, rax
    ; name
    lea rdi, [rel mg_tmp_name]
    xor rcx, rcx
.pa_cpn:
    mov al, [rdi + rcx]
    mov [rsi + rcx], al
    inc rcx
    test al, al
    jnz .pa_cpn
    ; alias at +64
    lea rdi, [rel mg_tmp_alias]
    xor rcx, rcx
.pa_cpa:
    mov al, [rdi + rcx]
    mov [rsi + 64 + rcx], al
    inc rcx
    test al, al
    jnz .pa_cpa
    ; line
    mov rax, [rel mg_list_n]
    lea rcx, [rel mg_list_line]
    mov [rcx + rax*8], r13
    inc qword [rel mg_list_n]
.pa_bail:
    mov r12, r8
    pop rcx
    pop r9
    pop r8
    ret

; --- mg_scan_buf: rsi=buf, rdx=len, rdi=rec_idx ---
; Fills v1 flag, exports, defs, and the temp import list (mg_list).
mg_scan_buf:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rsi
    mov r15, rdi
    xor r12, r12
    mov r13, 1
    mov r14, 1
    mov qword [rel mg_list_n], 0
.sb_loop:
    cmp r12, rdx
    jae .sb_done
    movzx eax, byte [rbx + r12]
    cmp al, 10
    jne .sb_not_nl
    inc r13
    mov r14, 1
    inc r12
    jmp .sb_loop
.sb_not_nl:
    cmp r14, 1
    jne .sb_not_ws
    cmp al, ' '
    je .sb_ws
    cmp al, 9
    je .sb_ws
    cmp al, 13
    je .sb_ws
    jmp .sb_not_ws
.sb_ws:
    inc r12
    jmp .sb_loop
.sb_not_ws:
    cmp al, '#'
    je .sb_comment
    cmp al, '/'
    jne .sb_not_cmt
    mov r8, r12
    inc r8
    cmp r8, rdx
    jae .sb_not_cmt
    movzx eax, byte [rbx + r8]
    cmp al, '/'
    jne .sb_not_cmt
.sb_comment:
    call mg_check_marker
.sb_skip:
    cmp r12, rdx
    jae .sb_done
    movzx eax, byte [rbx + r12]
    inc r12
    cmp al, 10
    jne .sb_skip
    inc r13
    mov r14, 1
    jmp .sb_loop
.sb_not_cmt:
    cmp r14, 1
    jne .sb_not_niryat
    lea rsi, [rel mg_w_niryat]
    call mg_match_at
    test rax, rax
    jz .sb_not_niryat
    mov r8, r12
    add r8, 6
    cmp r8, rdx
    jae .sb_not_niryat
    movzx eax, byte [rbx + r8]
    cmp al, ' '
    je .sb_niryat_ok
    cmp al, 9
    jne .sb_not_niryat
.sb_niryat_ok:
    call mg_parse_niryat
    mov r14, 0
    jmp .sb_loop
.sb_not_niryat:
    cmp r14, 1
    jne .sb_not_prakriya
    lea rsi, [rel mg_w_prakriya]
    call mg_match_at
    test rax, rax
    jnz .sb_prak_ok
    lea rsi, [rel mg_w_devprak]
    call mg_match_at
    test rax, rax
    jz .sb_not_prakriya
    mov r8, 27
    jmp .sb_prak_do
.sb_prak_ok:
    mov r8, 8
.sb_prak_do:
    ; word boundary: whitespace or '(' after keyword
    mov r9, r12
    add r9, r8
    cmp r9, rdx
    jae .sb_not_prakriya
    movzx eax, byte [rbx + r9]
    cmp al, ' '
    je .sb_prak_call
    cmp al, 9
    je .sb_prak_call
    cmp al, '('
    jne .sb_not_prakriya
.sb_prak_call:
    call mg_parse_prakriya
    mov r14, 0
    jmp .sb_loop
.sb_not_prakriya:
    ; v1 top-level sutra names count as local definitions for niryat.
    cmp r14, 1
    jne .sb_not_sutra
    lea rsi, [rel mg_w_sutra]
    call mg_match_at
    test rax, rax
    jz .sb_not_sutra
    mov r9, r12
    add r9, 5
    cmp r9, rdx
    jae .sb_not_sutra
    movzx eax, byte [rbx + r9]
    cmp al, ' '
    je .sb_sutra_ok
    cmp al, 9
    jne .sb_not_sutra
.sb_sutra_ok:
    mov r8, 5
    call mg_parse_prakriya  ; common name collector (no backend effects)
    mov r14, 0
    jmp .sb_loop
.sb_not_sutra:
    lea rsi, [rel mg_w_ayojan]
    call mg_match_at
    test rax, rax
    jz .sb_advance
    call mg_parse_ayojan
    mov r14, 0
    jmp .sb_loop
.sb_advance:
    mov r14, 0
    inc r12
    jmp .sb_loop
.sb_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- mg_valias_error: rdi = parent path. Prints E_MODULE_V1_ALIAS and exits. ---
; Uses mg_cur_line, mg_cur_name.
mg_defer_valias:
    ; rdi=importer path, mg_cur_name/line=offending import. Retain the first
    ; deterministic v1 alias error until AFTER dependency graph DFS diagnostics.
    cmp byte [rel mg_deferred_alias], 0
    jne .da_done
    mov byte [rel mg_deferred_alias], 1
    mov rax, [rel mg_cur_line]
    mov [rel mg_deferred_alias_line], rax
    mov rsi, rdi
    lea rdi, [rel mg_deferred_alias_path]
    mov rcx, 512
    rep movsb
    lea rsi, [rel mg_cur_name]
    lea rdi, [rel mg_deferred_alias_name]
    mov rcx, 64
    rep movsb
.da_done:
    ret

mg_valias_error:
    push rdi
    call print_str_z
    lea rdi, [rel mg_colon]
    call print_str_z
    mov rax, [rel mg_cur_line]
    call mg_print_uint
    lea rdi, [rel mg_colon]
    call print_str_z
    lea rdi, [rel mg_e_valias1]
    call print_str_z
    lea rdi, [rel mg_cur_name]
    call print_str_z
    lea rdi, [rel mg_e_valias2]
    call print_str_z
    lea rdi, [rel mg_cur_name]
    call print_str_z
    lea rdi, [rel mg_e_valias3]
    call print_str_z
    mov rdi, 1
    call os_exit

; --- mg_copy_list_to_rec: r15 = rec_idx. Copies mg_list -> mg_imp[r15]. ---
mg_copy_list_to_rec:
    push r12
    push r13
    mov r12, [rel mg_list_n]
    cmp r12, 12
    jbe .cl_ok
    mov r12, 12
.cl_ok:
    lea r11, [rel mg_imp_n]
    mov byte [r11 + r15], r12b
    xor r13, r13
.cl_loop:
    cmp r13, r12
    jae .cl_done
    ; src = mg_list[r13] (128B), dst = mg_imp + r15*1632 + r13*136
    mov rax, r13
    shl rax, 7
    lea rsi, [rel mg_list]
    add rsi, rax
    mov rax, r15
    imul rax, rax, 1632
    mov rbx, r13
    imul rbx, rbx, 136
    add rax, rbx
    lea rdi, [rel mg_imp]
    add rdi, rax
    ; name (64)
    xor rcx, rcx
.cl_name:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .cl_name
    ; alias (64) at +64
    xor rcx, rcx
.cl_alias:
    mov al, [rsi + 64 + rcx]
    mov [rdi + 64 + rcx], al
    inc rcx
    test al, al
    jnz .cl_alias
    ; line at +128
    lea r11, [rel mg_list_line]
    mov rax, [r11 + r13*8]
    mov [rdi + 128], rax
    inc r13
    jmp .cl_loop
.cl_done:
    pop r13
    pop r12
    ret

; --- mg_print_cycle: prints E_MODULE_CYCLE with file:line and cycle path ---
; Uses mg_cur_path, mg_cur_line (back-edge location), mg_gray, mg_cur_name.
mg_print_cycle:
    push rbx
    push r12
    cmp byte [rel mg_root_exact_v1], 1
    jne .pc_muse_prefix
    ; R41 compatible basename/line and error prefix.
    lea rdi, [rel mg_cur_path]
    call graph_print_file
    lea rdi, [rel graph_colon]
    call print_str_z
    mov rax, [rel mg_cur_line]
    call mg_print_uint
    lea rdi, [rel graph_prefix]
    call print_str_z
    lea rdi, [rel graph_msg_cycle]
    call print_str_z
    lea rdi, [rel graph_close]
    call print_str_z
    lea rdi, [rel graph_cycle_prefix]
    call print_str_z
    jmp .pc_prefix_done
.pc_muse_prefix:
    call mg_print_loc
    lea rdi, [rel mg_e_cycle]
    call print_str_z
.pc_prefix_done:
    ; start from the first occurrence of the offending module (the actual cycle)
    xor r12, r12
.pc_find:
    cmp r12, [rel mg_gray_n]
    jae .pc_loop
    mov rax, r12
    shl rax, 6
    lea rsi, [rel mg_gray]
    add rsi, rax
    lea rdi, [rel mg_cur_name]
    push r12
    call strcmp
    pop r12
    test rax, rax
    jz .pc_loop
    inc r12
    jmp .pc_find
.pc_loop:
    cmp r12, [rel mg_gray_n]
    jae .pc_last
    mov rax, r12
    shl rax, 6
    lea rdi, [rel mg_gray]
    add rdi, rax
    call print_str_z
    lea rdi, [rel mg_arrow]
    call print_str_z
    inc r12
    jmp .pc_loop
.pc_last:
    lea rdi, [rel mg_cur_name]
    call print_str_z
    sub rsp, 16
    mov byte [rsp], 10
    mov byte [rsp+1], 0
    lea rdi, [rsp]
    call print_str_z
    add rsp, 16
    pop r12
    pop rbx
    ret

; --- mg_process_imports: r15 = rec_idx. Loops over mg_imp[r15], recursing. ---
; Expects mg_cur_path = this module's path (saved/restored via mg_path_stk).
mg_process_imports:
    push rbx
    push r12
    push r13
    push r14
    ; save this module's path at depth gray_n
    mov rax, [rel mg_gray_n]
    shl rax, 9
    lea rdi, [rel mg_path_stk]
    add rdi, rax
    lea rsi, [rel mg_cur_path]
    mov rcx, 512
    rep movsb
    xor r12, r12                  ; import index
.pi_loop:
    lea r11, [rel mg_imp_n]
    movzx eax, byte [r11 + r15]
    cmp r12, rax
    jae .pi_done
    ; entry = mg_imp + r15*1632 + r12*136
    mov rax, r15
    imul rax, rax, 1632
    mov rbx, r12
    imul rbx, rbx, 136
    add rax, rbx
    lea rsi, [rel mg_imp]
    add rsi, rax
    ; name -> mg_cur_name
    lea rdi, [rel mg_cur_name]
    xor rcx, rcx
.pi_name:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .pi_name
    ; alias -> mg_cur_alias
    lea rdi, [rel mg_cur_alias]
    xor rcx, rcx
.pi_alias:
    mov al, [rsi + 64 + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .pi_alias
    ; line -> mg_cur_line
    mov rax, [rsi + 128]
    mov [rel mg_cur_line], rax
    ; Match R41 exact opt-in preflight name validation before the DFS edge.
    ; Old graph_scan allows only up to 30 ASCII module-name bytes (A-Z,
    ; a-z, 0-9, '_' and '-'). Legacy behavior is deliberately unchanged.
    cmp byte [rel mg_root_exact_v1], 1
    jne .pi_name_checked
    lea rdi, [rel mg_cur_name]
    xor rcx, rcx
.pi_validate_name:
    movzx eax, byte [rdi + rcx]
    test al, al
    jz .pi_validate_end
    cmp rcx, 30
    jae .pi_invalid_name
    cmp al, '_'
    je .pi_valid_char
    cmp al, '-'
    je .pi_valid_char
    cmp al, '0'
    jb .pi_invalid_name
    cmp al, '9'
    jbe .pi_valid_char
    cmp al, 'A'
    jb .pi_invalid_name
    cmp al, 'Z'
    jbe .pi_valid_char
    cmp al, 'a'
    jb .pi_invalid_name
    cmp al, 'z'
    ja .pi_invalid_name
.pi_valid_char:
    inc rcx
    jmp .pi_validate_name
.pi_validate_end:
    test rcx, rcx
    jz .pi_invalid_name
    jmp .pi_name_checked
.pi_invalid_name:
    lea rdi, [rel mg_cur_path]
    mov rsi, [rel mg_cur_line]
    lea rdx, [rel graph_msg_invalid]
    lea rcx, [rel graph_invalid_prefix]
    call graph_error
.pi_name_checked:
    ; gray check -> cycle
    lea rdi, [rel mg_cur_name]
    call mg_in_gray
    test rax, rax
    jnz .pi_cycle
    ; black check -> skip recurse (but valias check below needs record)
    lea rdi, [rel mg_cur_name]
    call mg_in_black
    test rax, rax
    jnz .pi_black
    ; resolve
    lea rdi, [rel mg_cur_name]
    call mg_resolve
    test rax, rax
    jnz .pi_resolved
    ; R41 exact opt-in: missing import fails with stable basename:line.
    cmp byte [rel mg_root_exact_v1], 1
    jne .pi_next               ; legacy missing behaviour is unchanged
    lea rax, [rel mg_cur_name]
    mov [rel graph_detail_ptr], rax
    lea rdi, [rel mg_cur_path]
    mov rsi, [rel mg_cur_line]
    lea rdx, [rel graph_msg_missing]
    lea rcx, [rel graph_missing_prefix]
    call graph_error
.pi_resolved:
    ; mg_cur_path = module_path_buf
    lea rsi, [rel module_path_buf]
    lea rdi, [rel mg_cur_path]
    xor rcx, rcx
.pi_cpp:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .pi_cpp
    call mg_visit
    ; restore this module's path
    mov rax, [rel mg_gray_n]
    shl rax, 9
    lea rsi, [rel mg_path_stk]
    add rsi, rax
    lea rdi, [rel mg_cur_path]
    mov rcx, 512
    rep movsb
    jmp .pi_next
.pi_black:
    ; already visited: still enforce v1+alias for this edge
    lea rdi, [rel mg_cur_name]
    call mg_find_rec
    cmp rax, 0
    jl .pi_next
    lea r11, [rel mg_rec_v1]
    movzx r8, byte [r11 + rax]
    test r8, r8
    jz .pi_next
    cmp byte [rel mg_cur_alias], 0
    jne .pi_next
    ; parent's path is mg_cur_path (not clobbered in this branch)
    lea rdi, [rel mg_cur_path]
    cmp byte [rel mg_root_exact_v1], 1
    jne .pi_alias_now
    call mg_defer_valias
    jmp .pi_next
.pi_alias_now:
    call mg_valias_error
.pi_next:
    inc r12
    jmp .pi_loop
.pi_cycle:
    call mg_print_cycle
    mov rdi, 1
    call os_exit
.pi_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- mg_visit: DFS visit. mg_cur_name/path/alias/line set by caller. ---
mg_visit:
    push rbx
    push r12
    push r13
    push r14
    push r15
    ; depth check
    cmp qword [rel mg_gray_n], 16
    jae .v_depth
    ; push gray
    lea rdi, [rel mg_cur_name]
    call mg_push_gray
    ; find or create record
    lea rdi, [rel mg_cur_name]
    call mg_find_rec
    test rax, rax
    jns .v_have_rec
    lea rdi, [rel mg_cur_name]
    lea rsi, [rel mg_cur_path]
    call mg_new_rec
    test rax, rax
    js .v_limit
.v_have_rec:
    mov r15, rax
    ; read file
    lea rdi, [rel mg_cur_path]
    call mg_read_file
    test rax, rax
    js .v_read_fail
    ; scan
    lea rsi, [rel mg_buf]
    mov rdx, rax
    mov rdi, r15
    call mg_scan_buf
    ; v1+alias check (fresh visit; v1 flag now known)
    lea r11, [rel mg_rec_v1]
    movzx eax, byte [r11 + r15]
    test eax, eax
    jz .v_no_valias
    cmp byte [rel mg_cur_alias], 0
    jne .v_no_valias
    ; parent's path is at mg_path_stk[gray_n - 1]
    mov rax, [rel mg_gray_n]
    dec rax
    shl rax, 9
    lea rdi, [rel mg_path_stk]
    add rdi, rax
    cmp byte [rel mg_root_exact_v1], 1
    jne .v_alias_now
    call mg_defer_valias
    jmp .v_no_valias
.v_alias_now:
    call mg_valias_error
.v_no_valias:
    ; Save import list, traverse dependencies and collect R41 cycle/missing
    ; errors before either export or alias diagnostics for an exact-v1 root.
    call mg_copy_list_to_rec
    call mg_process_imports
    ; Now root graph reachability is checked through this module.
    call mg_verify_exports
    ; pop gray, blacken
    call mg_pop_gray
    lea rdi, [rel mg_cur_name]
    call mg_add_black
    jmp .v_done
.v_read_fail:
    call mg_pop_gray
    jmp .v_done
.v_depth:
    lea rdi, [rel mg_e_depth]
    call print_str_z
    mov rdi, 1
    call os_exit
.v_limit:
    lea rdi, [rel mg_e_limit]
    call print_str_z
    mov rdi, 1
    call os_exit
.v_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- check_module_graph: main pre-pass entry. Called before expand_imports. ---
check_module_graph:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov byte [rel mg_deferred_alias], 0
    ; root record
    lea rdi, [rel mg_root_name]
    mov rsi, [rel source_path_ptr]
    call mg_new_rec
    ; mg_cur_path = source_path_ptr (for error locations in root scan)
    mov rsi, [rel source_path_ptr]
    lea rdi, [rel mg_cur_path]
    xor rcx, rcx
.cg_cpp:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .cg_cpp
    mov qword [rel mg_cur_line], 1
    mov byte [rel mg_cur_alias], 0
    ; push root to gray; save root path at stack[0]
    lea rdi, [rel mg_root_name]
    call mg_push_gray
    lea rdi, [rel mg_path_stk]
    lea rsi, [rel mg_cur_path]
    mov rcx, 512
    rep movsb
    ; scan root source
    lea rsi, [rel source_buf]
    mov rdx, [rel source_len]
    xor rdi, rdi
    call mg_scan_buf
    ; save imports, process
    xor r15, r15
    call mg_copy_list_to_rec
    call mg_process_imports
    ; pop gray, blacken root
    call mg_pop_gray
    lea rdi, [rel mg_root_name]
    call mg_add_black
    ; After DFS, replay the first v1 alias violation, preserving the old
    ; cycle/missing diagnostic precedence of the R41-first architecture.
    cmp byte [rel mg_deferred_alias], 0
    je .cg_no_alias
    lea rsi, [rel mg_deferred_alias_name]
    lea rdi, [rel mg_cur_name]
    mov rcx, 64
    rep movsb
    mov rax, [rel mg_deferred_alias_line]
    mov [rel mg_cur_line], rax
    lea rdi, [rel mg_deferred_alias_path]
    call mg_valias_error
.cg_no_alias:
    ; Phase B: export visibility
    call mg_check_visibility
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- mg_find_ref: rbx=buf, r12=len, rdi=pattern -> rax=line or 0 ---
; Finds `pattern` as a whole token followed by optional space/tab and '('.
; Skips # and // comments and "..." strings.
mg_find_ref:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r9, rdi                   ; pattern (r9 survives: mg_is_ident uses only rax)
    xor r13, r13
.fr_plen:
    cmp byte [r9 + r13], 0
    je .fr_scan
    inc r13
    jmp .fr_plen
.fr_scan:
    xor r14, r14                  ; pos
    mov r15, 1                    ; line
    xor r8, r8                    ; in_string
    xor r10, r10                  ; at_line_start
    inc r10
.fr_loop:
    mov rax, r14
    add rax, r13
    cmp rax, r12
    ja .fr_notfound
    movzx eax, byte [rbx + r14]
    cmp al, 10
    jne .fr_not_nl
    inc r15
    mov r10, 1
    inc r14
    jmp .fr_loop
.fr_not_nl:
    mov r10, 0
    cmp al, '"'
    jne .fr_not_q
    xor r8, 1
    inc r14
    jmp .fr_loop
.fr_not_q:
    cmp r8, 1
    je .fr_adv
    cmp al, '#'
    je .fr_skip
    cmp al, '/'
    jne .fr_match
    mov rax, r14
    inc rax
    cmp rax, r12
    jae .fr_match
    movzx eax, byte [rbx + rax]
    cmp al, '/'
    jne .fr_match
.fr_skip:
    ; skip to end of line
.fr_sl:
    cmp r14, r12
    jae .fr_notfound
    movzx eax, byte [rbx + r14]
    inc r14
    cmp al, 10
    jne .fr_sl
    inc r15
    jmp .fr_loop
.fr_match:
.fr_cmp_entry:
    xor rcx, rcx
.fr_cmp:
    cmp rcx, r13
    jae .fr_matched
    mov rax, r14
    add rax, rcx
    mov ah, [rbx + rax]
    mov al, [r9 + rcx]
    cmp al, ah
    jne .fr_adv
    inc rcx
    jmp .fr_cmp
.fr_matched:
    ; preceding char must not be an identifier char
    test r14, r14
    jz .fr_after
    movzx eax, byte [rbx + r14 - 1]
    mov edi, eax
    call mg_is_ident
    test rax, rax
    jnz .fr_adv
.fr_after:
    mov rax, r14
    add rax, r13
.fr_ws:
    cmp rax, r12
    jae .fr_adv
    movzx ecx, byte [rbx + rax]
    cmp cl, ' '
    je .fr_ws_adv
    cmp cl, 9
    jne .fr_chk_p
.fr_ws_adv:
    inc rax
    jmp .fr_ws
.fr_chk_p:
    cmp cl, '('
    jne .fr_adv
    mov rax, r15
    jmp .fr_done
.fr_adv:
    inc r14
    jmp .fr_loop
.fr_notfound:
    xor eax, eax
.fr_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- mg_check_edge: rbx=importer buf, r12=len, r13=mod rec, r14=alias ---
; Errors if the importer references alias__<private> for a private of the module.
mg_check_edge:
    push rbx
    push r12
    push r13
    push r14
    push r15
    xor r15, r15                  ; def index
.ce_def:
    lea r11, [rel mg_def_n]
    movzx eax, byte [r11 + r13]
    cmp r15, rax
    jae .ce_done
    ; def_is_exported?
    xor r8, r8
    lea r11, [rel mg_exp_n]
    movzx eax, byte [r11 + r13]
.ce_exp:
    cmp r8, rax
    jae .ce_private
    ; exp = mg_exp + r13*1024 + r8*64 ; def = mg_def + r13*2048 + r15*64
    mov rcx, r13
    shl rcx, 10
    mov rdx, r8
    shl rdx, 6
    add rcx, rdx
    lea rsi, [rel mg_exp]
    add rsi, rcx
    mov rcx, r13
    shl rcx, 11
    mov rdx, r15
    shl rdx, 6
    add rcx, rdx
    lea rdi, [rel mg_def]
    add rdi, rcx
    call strcmp
    test rax, rax
    jz .ce_next_def
    inc r8
    jmp .ce_exp
.ce_private:
    ; build "alias__def" in mg_pat
    lea rdi, [rel mg_pat]
    mov rsi, r14
    xor rcx, rcx
.ce_pa:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .ce_pa
    dec rcx
    mov byte [rdi + rcx], '_'
    mov byte [rdi + rcx + 1], '_'
    add rcx, 2
    mov rax, r13
    shl rax, 11
    mov rdx, r15
    shl rdx, 6
    add rax, rdx
    lea rsi, [rel mg_def]
    add rsi, rax
    push rsi                      ; save def ptr
    xor rdx, rdx
.ce_pd:
    mov al, [rsi + rdx]
    mov [rdi + rcx], al
    inc rcx
    inc rdx
    test al, al
    jnz .ce_pd
    lea rdi, [rel mg_pat]
    call mg_find_ref              ; rbx, r12 live; rdi = mg_pat
    test rax, rax
    jz .ce_no_ref
    ; E_MODULE_NOT_EXPORTED at mg_cur_path:rax
    mov [rel mg_cur_line], rax
    call mg_print_loc
    lea rdi, [rel mg_e_noexp1]
    call print_str_z
    pop rsi
    push rsi
    mov rdi, rsi                  ; def name
    call print_str_z
    lea rdi, [rel mg_e_noexp2]
    call print_str_z
    mov rax, r13
    shl rax, 6
    lea rdi, [rel mg_rec_name]
    add rdi, rax
    call print_str_z
    lea rdi, [rel mg_e_noexp3]
    call print_str_z
    mov rdi, 1
    call os_exit
.ce_no_ref:
    pop rsi
.ce_next_def:
    inc r15
    jmp .ce_def
.ce_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- R44: validate any qualified alias__symbol token, including constants. ---
; rbx=importer bytes, r12=length, r13=target rec, r14=import alias.
; Lexically ignores comments and double-quoted strings (with escapes).
; This distinguishes unknown symbols from defined-but-private symbols.
mg_check_qualified:
    push rbx
    push r12
    push r13
    push r14
    push r15
    ; Build the exact alias__ prefix in a bounded scratch buffer.
    lea rdi, [rel mg_pat]
    mov rsi, r14
    xor rcx, rcx
.cq_prefix:
    cmp rcx, 62
    jae .cq_done
    mov al, [rsi + rcx]
    test al, al
    jz .cq_prefix_end
    mov [rdi + rcx], al
    inc rcx
    jmp .cq_prefix
.cq_prefix_end:
    mov byte [rdi + rcx], '_'
    mov byte [rdi + rcx + 1], '_'
    add rcx, 2
    mov byte [rdi + rcx], 0
    mov [rel mg_pat_len], rcx
    xor r8, r8                    ; input offset
    mov r9, 1                     ; physical line
    xor r10, r10                  ; 0 code, 1 comment, 2 string, 3 escaped
.cq_scan:
    cmp r8, r12
    jae .cq_done
    movzx eax, byte [rbx + r8]
    cmp al, 10
    je .cq_newline
    cmp r10, 1
    je .cq_advance
    cmp r10, 2
    je .cq_string
    cmp r10, 3
    je .cq_escaped
    cmp al, '#'
    je .cq_comment
    cmp al, '/'
    jne .cq_quote
    lea rcx, [r8 + 1]
    cmp rcx, r12
    jae .cq_quote
    cmp byte [rbx + rcx], '/'
    je .cq_comment
.cq_quote:
    cmp al, '"'
    jne .cq_ident
    mov r10, 2
    jmp .cq_advance
.cq_ident:
    mov dil, al
    call mg_is_ident
    test rax, rax
    jz .cq_advance
    mov r15, r8
.cq_token:
    cmp r8, r12
    jae .cq_token_end
    mov dil, [rbx + r8]
    call mg_is_ident
    test rax, rax
    jz .cq_token_end
    inc r8
    jmp .cq_token
.cq_token_end:
    mov rcx, [rel mg_pat_len]
    mov rax, r8
    sub rax, r15
    cmp rax, rcx
    jbe .cq_scan                 ; no suffix
    lea rsi, [rel mg_pat]
    lea rdi, [rbx + r15]
    xor r11, r11
.cq_prefix_match:
    cmp r11, rcx
    jae .cq_copy_suffix
    mov al, [rsi + r11]
    cmp al, [rdi + r11]
    jne .cq_scan
    inc r11
    jmp .cq_prefix_match
.cq_copy_suffix:
    mov rax, r8
    sub rax, r15
    sub rax, rcx
    cmp rax, 63
    ja .cq_scan
    lea rsi, [rbx + r15]
    add rsi, rcx
    lea rdi, [rel mg_tmp_name]
    mov rcx, rax
    rep movsb
    mov byte [rdi], 0
    ; Lookup in *definitions* before exports, so private != unknown.
    lea rax, [rel mg_def_n]
    movzx r14, byte [rax + r13]
    xor r15, r15
.cq_def:
    cmp r15, r14
    jae .cq_unknown
    mov rax, r13
    shl rax, 11
    mov rcx, r15
    shl rcx, 6
    add rax, rcx
    lea rsi, [rel mg_def]
    add rsi, rax
    lea rdi, [rel mg_tmp_name]
    call strcmp
    test rax, rax
    jz .cq_known
    inc r15
    jmp .cq_def
.cq_known:
    lea rax, [rel mg_exp_n]
    movzx r14, byte [rax + r13]
    xor r15, r15
.cq_exp:
    cmp r15, r14
    jae .cq_private
    mov rax, r13
    shl rax, 10
    mov rcx, r15
    shl rcx, 6
    add rax, rcx
    lea rsi, [rel mg_exp]
    add rsi, rax
    lea rdi, [rel mg_tmp_name]
    call strcmp
    test rax, rax
    jz .cq_scan
    inc r15
    jmp .cq_exp
.cq_private:
    mov [rel mg_cur_line], r9
    call mg_print_loc
    lea rdi, [rel mg_e_noexp1]
    call print_str_z
    lea rdi, [rel mg_tmp_name]
    call print_str_z
    lea rdi, [rel mg_e_noexp2]
    call print_str_z
    jmp .cq_module_name
.cq_unknown:
    mov [rel mg_cur_line], r9
    call mg_print_loc
    lea rdi, [rel mg_e_unknown1]
    call print_str_z
    lea rdi, [rel mg_tmp_name]
    call print_str_z
    lea rdi, [rel mg_e_unknown2]
    call print_str_z
.cq_module_name:
    mov rax, r13
    shl rax, 6
    lea rdi, [rel mg_rec_name]
    add rdi, rax
    call print_str_z
    lea rdi, [rel mg_e_unknown3]
    call print_str_z
    mov rdi, 1
    call os_exit
.cq_comment:
    mov r10, 1
    jmp .cq_advance
.cq_string:
    cmp al, 92
    jne .cq_end_quote
    mov r10, 3
    jmp .cq_advance
.cq_end_quote:
    cmp al, '"'
    jne .cq_advance
    xor r10, r10
    jmp .cq_advance
.cq_escaped:
    mov r10, 2
    jmp .cq_advance
.cq_newline:
    inc r9
    cmp r10, 1
    jne .cq_advance
    xor r10, r10
.cq_advance:
    inc r8
    jmp .cq_scan
.cq_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; --- mg_check_visibility: Phase B. Checks all v1 import edges. ---
mg_check_visibility:
    push rbx
    push r12
    push r13
    push r14
    push r15
    xor r15, r15                  ; importer rec
    lea r11, [rel mg_rec_v1]
.cv_rec:
    cmp r15, [rel mg_rec_n]
    jae .cv_done
    ; Called validators use volatile r11: rebase every iteration.
    lea r11, [rel mg_rec_v1]
    movzx eax, byte [r11 + r15]
    test eax, eax
    jz .cv_next_rec
    ; load importer's buffer: rbx, r12; set mg_cur_path for errors
    cmp r15, 0
    jne .cv_module
    lea rbx, [rel source_buf]
    mov r12, [rel source_len]
    mov rsi, [rel source_path_ptr]
    lea rdi, [rel mg_cur_path]
    xor rcx, rcx
.cv_cproot:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .cv_cproot
    jmp .cv_buf_ok
.cv_module:
    mov rax, r15
    shl rax, 9
    lea rsi, [rel mg_rec_path]
    add rsi, rax
    lea rdi, [rel mg_cur_path]
    xor rcx, rcx
.cv_cpmod:
    mov al, [rsi + rcx]
    mov [rdi + rcx], al
    inc rcx
    test al, al
    jnz .cv_cpmod
    lea rdi, [rel mg_cur_path]
    call mg_read_file
    test rax, rax
    js .cv_next_rec
    lea rbx, [rel mg_buf]
    mov r12, rax
.cv_buf_ok:
    xor r14, r14                  ; import index
    lea r11, [rel mg_imp_n]
.cv_imp:
    ; Reestablish import-count table after per-edge scanner calls.
    lea r11, [rel mg_imp_n]
    movzx eax, byte [r11 + r15]
    cmp r14, rax
    jae .cv_next_rec
    mov rax, r15
    imul rax, rax, 1632
    mov rcx, r14
    imul rcx, rcx, 136
    add rax, rcx
    lea rsi, [rel mg_imp]
    add rsi, rax
    push rsi
    mov rdi, rsi                  ; name
    call mg_find_rec
    pop rsi
    cmp rax, 0
    jl .cv_next_imp
    lea r11, [rel mg_rec_v1]
    movzx ecx, byte [r11 + rax]
    test ecx, ecx
    jz .cv_next_imp
    ; r13 = mod rec; alias = rsi+64 -> r14 (save index first)
    mov r13, rax
    push r14
    lea r14, [rsi + 64]
    ; rbx, r12 already set
    call mg_check_edge
    call mg_check_qualified
    pop r14
.cv_next_imp:
    inc r14
    jmp .cv_imp
.cv_next_rec:
    inc r15
    jmp .cv_rec
.cv_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ============================================================
; R33: namespaced module lexical rewriting (compile time, pure NASM)
; ayojan module@alias  -> exported calls alias__function(...).
; Collect only top-level line-start prakriya declarations, then rename those
; identifier tokens when followed by '(' (definition or local call). Strings,
; # comments and // comments are copied verbatim. No runtime linker/namespace.
; ============================================================
; --- ns_strip_niryat: removes `niryat <name>` lines from ns_raw_buf ---
; Only for v1-marked modules (detected via the marker substring). Updates
; ns_raw_len. Called before ns_rewrite_funcs so niryat never reaches the parser.
ns_strip_niryat:
    push rbx
    push r12
    push r13
    push r14
    lea rbx, [rel ns_raw_buf]
    mov r13, [rel ns_raw_len]
    lea rsi, [rel mg_v1_mark]
    xor r12, r12
.ns_find:
    mov rax, r12
    add rax, 16
    cmp rax, r13
    ja .ns_done
    xor rcx, rcx
.ns_cmp:
    mov al, [rsi + rcx]
    test al, al
    jz .ns_found
    mov r9, r12
    add r9, rcx
    cmp al, [rbx + r9]
    jne .ns_next
    inc rcx
    jmp .ns_cmp
.ns_next:
    inc r12
    jmp .ns_find
.ns_found:
    xor r12, r12                  ; read pos
    xor r14, r14                  ; write pos
    mov r8, 1                     ; at_line_start
.ns_loop:
    cmp r12, r13
    jae .ns_strip_done
    movzx eax, byte [rbx + r12]
    cmp al, 10
    jne .ns_not_nl
    mov [rbx + r14], al
    inc r12
    inc r14
    mov r8, 1
    jmp .ns_loop
.ns_not_nl:
    cmp r8, 1
    jne .ns_copy
    cmp al, ' '
    je .ns_ws
    cmp al, 9
    je .ns_ws
    cmp al, 13
    je .ns_ws
    ; try match "niryat"
    lea rsi, [rel mg_w_niryat]
    xor rcx, rcx
.ns_m:
    mov al, [rsi + rcx]
    test al, al
    jz .ns_m_ok
    mov r9, r12
    add r9, rcx
    cmp r9, r13
    jae .ns_copy
    cmp al, [rbx + r9]
    jne .ns_copy
    inc rcx
    jmp .ns_m
.ns_m_ok:
    mov r9, r12
    add r9, rcx
    cmp r9, r13
    jae .ns_copy
    movzx eax, byte [rbx + r9]
    cmp al, ' '
    je .ns_skip_line
    cmp al, 9
    jne .ns_copy
.ns_skip_line:
    cmp r12, r13
    jae .ns_strip_done
    movzx eax, byte [rbx + r12]
    inc r12
    cmp al, 10
    jne .ns_skip_line
    mov r8, 1
    jmp .ns_loop
.ns_ws:
    movzx eax, byte [rbx + r12]
    mov [rbx + r14], al
    inc r12
    inc r14
    jmp .ns_loop
.ns_copy:
    movzx eax, byte [rbx + r12]
    mov [rbx + r14], al
    inc r12
    inc r14
    mov r8, 0
    jmp .ns_loop
.ns_strip_done:
    mov [rel ns_raw_len], r14
.ns_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
ns_collect_funcs:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov qword [rel ns_func_count],0
    mov rbx,[rel ns_raw_len]
    xor r15,r15
.nc_line:
    xor r14,r14              ; 0 function; 1 compile-time constant
    cmp r15,rbx
    jae .nc_done
.nc_indent:
    cmp r15,rbx
    jae .nc_done
    lea rdx,[rel ns_raw_buf]
    mov al,[rdx+r15]
    cmp al,' '
    je .nc_skip_indent
    cmp al,9
    jne .nc_maybe_def
.nc_skip_indent:
    inc r15
    jmp .nc_indent
.nc_maybe_def:
    cmp rbx,r15
    jbe .nc_done
    mov rax,rbx
    sub rax,r15
    cmp rax,8
    jb .nc_try_dev
    ; match ASCII 'prakriya' as a whole word using 8 explicit bytes
    cmp byte [rdx+r15],'p'
    jne .nc_try_dev
    cmp byte [rdx+r15+1],'r'
    jne .nc_try_dev
    cmp byte [rdx+r15+2],'a'
    jne .nc_try_dev
    cmp byte [rdx+r15+3],'k'
    jne .nc_try_dev
    cmp byte [rdx+r15+4],'r'
    jne .nc_try_dev
    cmp byte [rdx+r15+5],'i'
    jne .nc_try_dev
    cmp byte [rdx+r15+6],'y'
    jne .nc_try_dev
    cmp byte [rdx+r15+7],'a'
    jne .nc_try_dev
    add r15,8
    jmp .nc_after_keyword
.nc_try_dev:
    ; Devanagari प्रक्रिया is the same keyword, never a separate namespace rule.
    lea rsi,[rel kw_dev_prakriya]
    xor rcx,rcx
.nc_dev_byte:
    mov r11b,[rsi+rcx]
    test r11b,r11b
    jz .nc_dev_ok
    mov rax,r15
    add rax,rcx
    cmp rax,rbx
    jae .nc_try_sutra
    lea rdx,[rel ns_raw_buf]
    cmp r11b,[rdx+rax]
    jne .nc_try_sutra
    inc rcx
    jmp .nc_dev_byte
.nc_dev_ok:
    add r15,rcx
    jmp .nc_after_keyword
.nc_try_sutra:
    ; Add sutra NAME as a separately tagged unqualified symbol.  Its bare
    ; uses (not only calls) must be renamed under module@alias.
    lea rdx, [rel ns_raw_buf]
    mov rax, rbx
    sub rax, r15
    cmp rax, 5
    jb .nc_next_line
    cmp byte [rdx+r15], 's'
    jne .nc_next_line
    cmp byte [rdx+r15+1], 'u'
    jne .nc_next_line
    cmp byte [rdx+r15+2], 't'
    jne .nc_next_line
    cmp byte [rdx+r15+3], 'r'
    jne .nc_next_line
    cmp byte [rdx+r15+4], 'a'
    jne .nc_next_line
    mov r14, 1
    add r15, 5
    jmp .nc_after_keyword
.nc_after_keyword:
    cmp r15,rbx
    jae .nc_next_line
    mov al,[rdx+r15]
    cmp al,' '
    je .nc_before_name
    cmp al,9
    jne .nc_next_line
.nc_before_name:
    inc r15
    cmp r15,rbx
    jae .nc_done
    mov al,[rdx+r15]
    cmp al,' '
    je .nc_before_name
    cmp al,9
    je .nc_before_name
    mov r12,r15
.nc_read_name:
    cmp r15,rbx
    jae .nc_name_done
    mov al,[rdx+r15]
    cmp al,'('
    je .nc_name_done
    cmp al,' '
    je .nc_name_done
    cmp al,9
    je .nc_name_done
    cmp al,10
    je .nc_name_done
    cmp al,13
    je .nc_name_done
    inc r15
    jmp .nc_read_name
.nc_name_done:
    mov rax,r15
    sub rax,r12
    test rax,rax
    jz .nc_next_line
    cmp rax,NS_FUNC_NAME_CAP
    ja .nc_capacity
    cmp qword [rel ns_func_count],NS_FUNC_CAP
    jae .nc_capacity
    mov rcx,[rel ns_func_count]
    shl rcx,6
    lea rdi,[rel ns_func_names]
    add rdi,rcx
    lea rsi,[rel ns_raw_buf]
    add rsi,r12
    mov rcx,rax
    rep movsb
    mov byte [rdi],0
    mov rax, [rel ns_func_count]
    lea rdi, [rel ns_func_is_const]
    mov byte [rdi+rax], r14b
    inc qword [rel ns_func_count]
.nc_next_line:
    cmp r15,rbx
    jae .nc_done
    lea rdx,[rel ns_raw_buf]
    mov al,[rdx+r15]
    inc r15
    cmp al,10
    jne .nc_next_line
    jmp .nc_line
.nc_capacity:
    lea rdi,[rel msg_namespace_func_limit]
    call print_str_z
    mov rdi,1
    call os_exit
.nc_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

ns_rewrite_funcs:
    push rbx
    push r12
    push r13
    push r15
    mov rbx,[rel ns_raw_len]
    xor r15,r15
    xor r13,r13              ; 0 code, 1 comment, 2 string, 3 string escape
.nr_loop:
    cmp r15,rbx
    jae .nr_done
    lea rdx,[rel ns_raw_buf]
    mov al,[rdx+r15]
    cmp r13,1
    je .nr_comment
    cmp r13,2
    je .nr_string
    cmp r13,3
    je .nr_escape
    cmp al,'#'
    je .nr_start_comment
    cmp al,'/'
    jne .nr_quote_check
    lea rcx,[r15+1]
    cmp rcx,rbx
    jae .nr_quote_check
    cmp byte [rdx+rcx],'/'
    je .nr_start_comment
.nr_quote_check:
    cmp al,'"'
    je .nr_start_string
    ; Tokenize identifiers only; numeric/string/comment bytes remain unchanged.
    cmp al,'_'
    je .nr_ident
    cmp al,'A'
    jb .nr_copy
    cmp al,'Z'
    jbe .nr_ident
    cmp al,'a'
    jb .nr_copy
    cmp al,'z'
    jbe .nr_ident
    cmp al,128
    jae .nr_ident
    jmp .nr_copy
.nr_ident:
    mov r12,r15
.nr_ident_more:
    inc r15
    cmp r15,rbx
    jae .nr_ident_end
    lea rdx,[rel ns_raw_buf]
    mov al,[rdx+r15]
    cmp al,'_'
    je .nr_ident_more
    cmp al,'0'
    jb .nr_check_alpha
    cmp al,'9'
    jbe .nr_ident_more
.nr_check_alpha:
    cmp al,'A'
    jb .nr_ident_end
    cmp al,'Z'
    jbe .nr_ident_more
    cmp al,'a'
    jb .nr_ident_end
    cmp al,'z'
    jbe .nr_ident_more
    cmp al,128
    jae .nr_ident_more
.nr_ident_end:
    mov r9,r15
    sub r9,r12
    ; Require a call/definition '(' immediately or after spacing.
    mov r8,r15
.nr_skip_ws:
    cmp r8,rbx
    jae .nr_raw_token
    lea rdx,[rel ns_raw_buf]
    mov al,[rdx+r8]
    cmp al,' '
    je .nr_ws_inc
    cmp al,9
    je .nr_ws_inc
    cmp al,10
    je .nr_ws_inc
    cmp al,13
    jne .nr_check_paren
.nr_ws_inc:
    inc r8
    jmp .nr_skip_ws
.nr_check_paren:
    ; Functions require a call '('; compile-time sutra constants do not.
    xor r8,r8
    cmp al,'('
    sete r8b
    xor r10,r10
.nr_match_func:
    cmp r10,[rel ns_func_count]
    jae .nr_raw_token
    mov rax,r10
    shl rax,6
    lea r11,[rel ns_func_names]
    add r11,rax
    xor rcx,rcx
.nr_compare:
    cmp rcx,r9
    jae .nr_exact
    cmp rcx,NS_FUNC_NAME_CAP
    jae .nr_next_func
    lea rdx,[rel ns_raw_buf]
    lea rax,[rdx+r12]
    mov dl,[r11+rcx]
    cmp dl,[rax+rcx]
    jne .nr_next_func
    inc rcx
    jmp .nr_compare
.nr_exact:
    cmp byte [r11+rcx],0
    jne .nr_next_func
    lea rdx, [rel ns_func_is_const]
    cmp byte [rdx+r10],1
    je .nr_qualified
    test r8,r8
    jnz .nr_qualified
.nr_next_func:
    inc r10
    jmp .nr_match_func
.nr_qualified:
    lea rsi,[rel ns_alias]
.nr_prefix:
    mov al,[rsi]
    test al,al
    jz .nr_separator
    call ns_emit_byte
    inc rsi
    jmp .nr_prefix
.nr_separator:
    mov al,'_'
    call ns_emit_byte
    mov al,'_'
    call ns_emit_byte
.nr_raw_token:
    xor r10,r10
.nr_emit_token:
    cmp r10,r9
    jae .nr_loop
    lea rdx,[rel ns_raw_buf]
    lea rax,[rdx+r12]
    mov al,[rax+r10]
    call ns_emit_byte
    inc r10
    jmp .nr_emit_token
.nr_start_comment:
    mov r13,1
    jmp .nr_copy
.nr_comment:
    cmp al,10
    jne .nr_copy
    xor r13,r13
    jmp .nr_copy
.nr_start_string:
    mov r13,2
    jmp .nr_copy
.nr_string:
    cmp al,92
    je .nr_string_escape
    cmp al,'"'
    jne .nr_copy
    xor r13,r13
    jmp .nr_copy
.nr_string_escape:
    mov r13,3
    jmp .nr_copy
.nr_escape:
    mov r13,2
.nr_copy:
    call ns_emit_byte
    inc r15
    jmp .nr_loop
.nr_done:
    pop r15
    pop r13
    pop r12
    pop rbx
    ret

; al -> next expansion byte; named capacity error instead of corruption
ns_emit_byte:
    cmp r14,IMPORT_BUF_CAP-1
    jae .ne_overflow
    push rdx
    lea rdx,[rel import_buf]
    mov [rdx+r14],al
    pop rdx
    inc r14
    ret
.ne_overflow:
    lea rdi,[rel msg_import_overflow]
    call print_str_z
    mov rdi,1
    call os_exit

; ============================================================
; FILE I/O
; ============================================================
read_file:
    push rbx
    mov rbx, rdi               ; filename
    mov rsi, 0                  ; O_RDONLY
    xor rdx, rdx
    call os_open
    test rax, rax
    jns .opened
    lea rdi, [rel tbl_open_err]
    call pick_lang_str
    mov rdi, rax
    call print_str_z
    jmp do_exit
.opened:
    mov rbx, rax               ; fd
    mov rdi, rbx
    lea rsi, [rel source_buf]
    mov rdx, 65536
    call os_read
    push rax                   ; save byte count
    mov rdi, rbx
    call os_close
    pop rax                    ; restore byte count
    pop rbx
    ret

; ============================================================
; LEXER
; ============================================================
lex:
    push rbx
    push r12
    push r13
    push r14
    push r15
    lea r13, [rel source_buf]  ; r13 = source pos
    lea r14, [rel source_buf]
    add r14, [rel source_len]  ; r14 = source end
    lea r15, [rel token_arr]   ; r15 = token write ptr
    mov qword [rel token_cnt], 0
    mov qword [rel cur_line], 1
    lea rax, [rel str_pool]
    mov [rel str_ptr], rax

.lex_loop:
    cmp r13, r14
    jae .lex_eof
    mov r12, r13               ; source pointer for this token (diagnostics)
    movzx rax, byte [r13]
    mov rdi, rax

    ; Skip whitespace
    call is_space
    test rax, rax
    jnz .skip_ws

    ; Skip comments
    movzx rax, byte [r13]
    cmp al, '/'
    jne .not_comment
    movzx rax, byte [r13+1]
    cmp al, '/'
    je .skip_comment
    cmp al, '*'
    jne .not_comment
    ; Block comment /* ... */ — skip to the closing */
    add r13, 2
.bc_loop:
    cmp r13, r14
    jae .lex_eof
    movzx rax, byte [r13]
    cmp al, '*'
    jne .bc_adv
    movzx rax, byte [r13+1]
    cmp al, '/'
    je .bc_done
.bc_adv:
    movzx rax, byte [r13]
    cmp al, 10
    jne .bc_inc
    inc qword [rel cur_line]
.bc_inc:
    inc r13
    jmp .bc_loop
.bc_done:
    add r13, 2
    jmp .lex_loop
.skip_comment:
    inc r13
    cmp r13, r14
    jae .lex_loop
    movzx rax, byte [r13]
    cmp al, 10
    jne .skip_comment
    inc qword [rel cur_line]
    inc r13
    jmp .lex_loop
.not_comment:
    ; Check for # comments
    movzx rax, byte [r13]
    cmp al, '#'
    je .skip_comment

    ; Identifier/keyword?
    movzx rax, byte [r13]
    mov rdi, rax
    call is_alpha
    test rax, rax
    jz .try_number

    ; Collect identifier
    mov rsi, [rel str_ptr]     ; rsi = write pos in str_pool
.collect_id:
    cmp r13, r14
    jae .id_done
    movzx rax, byte [r13]
    mov rdi, rax
    call is_alpha
    test rax, rax
    jnz .store_id
    call is_digit
    test rax, rax
    jz .id_done
.store_id:
    ; Check if this is a multi-byte UTF-8 character (0xE0 = Devanagari start)
    movzx rax, byte [r13]
    cmp al, 0xE0
    je .store_multibyte
    ; Single-byte character
    movzx rax, byte [r13]
    mov [rsi], al
    inc r13
    inc rsi
    jmp .collect_id
.store_multibyte:
    ; UTF-8 3-byte sequence
    movzx rax, byte [r13]
    mov [rsi], al
    movzx rax, byte [r13+1]
    mov [rsi+1], al
    movzx rax, byte [r13+2]
    mov [rsi+2], al
    add r13, 3
    add rsi, 3
    jmp .collect_id
.id_done:
    mov byte [rsi], 0          ; null terminate
    mov rbx, [rel str_ptr]    ; rbx = string start
    inc rsi
    mov [rel str_ptr], rsi

    ; Check keyword
    mov rdi, rbx
    call lookup_keyword        ; rax=1 if found, rdx=keyword_id
    test rax, rax
    jz .check_builtin
    ; It's a keyword
    mov qword [r15], TOK_KEYWORD
    mov [r15+8], rbx
    mov [r15+16], rdx
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12          ; exact source position for column/snippet diagnostics
    add r15, TOKEN_SIZE
    inc qword [rel token_cnt]
    jmp .lex_loop

.check_builtin:
    mov rdi, rbx
    call lookup_builtin         ; rax=1 if found, rdx=builtin_id
    test rax, rax
    jz .emit_ident
    mov qword [r15], TOK_BUILTIN
    mov [r15+8], rbx
    mov [r15+16], rdx
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12          ; exact source position for column/snippet diagnostics
    add r15, TOKEN_SIZE
    inc qword [rel token_cnt]
    jmp .lex_loop

.emit_ident:
    mov qword [r15], TOK_IDENT
    mov [r15+8], rbx
    mov qword [r15+16], 0
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12          ; exact source position for column/snippet diagnostics
    add r15, TOKEN_SIZE
    inc qword [rel token_cnt]
    jmp .lex_loop

.try_number:
    movzx rax, byte [r13]
    mov rdi, rax
    call is_digit
    test rax, rax
    jz .try_operator

    xor r8, r8                 ; accumulated integer value / final bits
    xor r11d, r11d             ; T12: 0=integer token, 1=float token
    ; Hex?
    movzx rax, byte [r13]
    cmp al, '0'
    jne .dec_loop
    movzx rax, byte [r13+1]
    cmp al, 'x'
    je .hex_prefix
    cmp al, 'X'
    je .hex_prefix
    jmp .dec_loop
.hex_prefix:
    add r13, 2
.hex_loop:
    cmp r13, r14
    jae .num_done
    movzx rax, byte [r13]
    mov rdi, rax
    call is_hex
    test rax, rax
    jz .num_done
    imul r8, r8, 16
    movzx rax, byte [r13]
    call hexval
    add r8, rax
    inc r13
    jmp .hex_loop
.dec_loop:
    cmp r13, r14
    jae .num_done
    movzx rax, byte [r13]
    mov rdi, rax
    call is_digit
    test rax, rax
    jnz .dec_digit
    ; T12 decimal fraction: only treat '.' as numeric when followed by a digit.
    movzx rax, byte [r13]
    cmp al, '.'
    jne .num_done
    movzx rax, byte [r13+1]
    mov rdi, rax
    call is_digit
    test rax, rax
    jz .num_done
    inc r13                    ; consume '.'
    xor r9, r9                 ; fractional integer
    mov r10, 1                 ; decimal divisor
    xor ecx, ecx               ; kept precision digits
.float_frac_loop:
    cmp r13, r14
    jae .float_frac_done
    movzx rax, byte [r13]
    mov rdi, rax
    call is_digit
    test rax, rax
    jz .float_frac_done
    cmp ecx, 15                ; binary64 does not benefit from unbounded decimal accumulation
    jae .float_frac_consume
    imul r9, r9, 10
    movzx rax, byte [r13]
    sub rax, '0'
    add r9, rax
    imul r10, r10, 10
    inc ecx
.float_frac_consume:
    inc r13
    jmp .float_frac_loop
.float_frac_done:
    ; Convert integer + fractional components to an IEEE-754 binary64 value.
    cvtsi2sd xmm0, r8
    cvtsi2sd xmm1, r9
    cvtsi2sd xmm2, r10
    divsd xmm1, xmm2
    addsd xmm0, xmm1
    movq r8, xmm0
    mov r11d, 1
    jmp .num_done
.dec_digit:
    imul r8, r8, 10
    movzx rax, byte [r13]
    sub rax, '0'
    add r8, rax
    inc r13
    jmp .dec_loop
.num_done:
    cmp r11d, 1
    jne .num_emit_int
    mov qword [r15], TOK_FLOAT
    jmp .num_emit_value
.num_emit_int:
    mov qword [r15], TOK_NUMBER
.num_emit_value:
    mov [r15+8], r8
    mov qword [r15+16], 0
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12          ; exact source position for column/snippet diagnostics
    add r15, TOKEN_SIZE
    inc qword [rel token_cnt]
    jmp .lex_loop

.try_operator:
    ; Check for string literal (double quote = 0x22)
    movzx r8, byte [r13]
    cmp r8, 0x22
    je .lex_string
    ; Two-char operators
    cmp r8, '='
    je .check_eqeq
    cmp r8, '!'
    je .check_neq
    cmp r8, '<'
    je .check_le
    cmp r8, '>'
    je .check_ge
    ; Delimiters
    cmp r8, '('
    je .emit_delim
    cmp r8, ')'
    je .emit_delim
    cmp r8, '{'
    je .emit_delim
    cmp r8, '}'
    je .emit_delim
    cmp r8, ';'
    je .emit_delim
    cmp r8, ','
    je .emit_delim
    cmp r8, '['
    je .emit_delim
    cmp r8, ']'
    je .emit_delim
    cmp r8, '.'
    je .emit_delim
    cmp r8, ':'
    je .emit_delim
    cmp r8, '?'
    je .emit_delim
    ; Single-char operators (with compound assignment check)
    cmp r8, '+'
    je .check_pluseq
    cmp r8, '-'
    je .check_mineq
    cmp r8, '*'
    je .check_muleq
    cmp r8, '/'
    je .check_diveq
    cmp r8, '%'
    je .check_modeq
    cmp r8, '&'
    je .check_amp
    cmp r8, '|'
    je .check_pipe
    cmp r8, '^'
    je .emit_op
    cmp r8, '='
    je .check_eqeq_short
    cmp r8, '<'
    je .check_le
    cmp r8, '>'
    je .check_ge
    ; Unknown char — skip
    inc r13
    jmp .lex_loop

.check_amp:
    movzx rax, byte [r13+1]
    cmp al, '&'
    je .emit_ampamp
    mov r8, '&'
    jmp .emit_op
.emit_ampamp:
    mov r8, 0x2626     ; &&
    add r13, 2
    jmp .emit_op2

.check_pipe:
    movzx rax, byte [r13+1]
    cmp al, '|'
    je .emit_pipepipe
    mov r8, '|'
    jmp .emit_op
.emit_pipepipe:
    mov r8, 0x7C7C     ; ||
    add r13, 2
    jmp .emit_op2

.check_eqeq_short:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_eqeq
    mov r8, '='
    jmp .emit_op

; ============================================================
; STRING LITERAL COLLECTION
; ============================================================
.lex_string:
    inc r13                      ; skip opening quote
    mov rsi, [rel str_ptr]       ; rsi = write position in string pool
.str_collect:
    cmp r13, r14
    jae .str_done
    movzx rax, byte [r13]
    cmp al, 0x22
    je .str_done
    cmp al, 0x5C
    je .str_escape
    mov [rsi], al
    inc r13
    inc rsi
    jmp .str_collect
.str_escape:
    inc r13
    cmp r13, r14
    jae .str_done
    movzx rax, byte [r13]
    cmp al, 'n'
    jne .str_esc_t
    mov al, 10
    jmp .str_esc_store
.str_esc_t:
    cmp al, 't'
    jne .str_esc_q
    mov al, 9
    jmp .str_esc_store
.str_esc_q:
    cmp al, '"'
    jne .str_esc_bs
    mov al, 0x22
    jmp .str_esc_store
.str_esc_bs:
    cmp al, 0x5C
    jne .str_esc_0
    mov al, 0x5C
    jmp .str_esc_store
.str_esc_0:
    cmp al, 'r'
    jne .str_esc_z
    mov al, 13
    jmp .str_esc_store
.str_esc_z:
    cmp al, '0'
    jne .str_esc_default
    mov al, 0
    jmp .str_esc_store
.str_esc_default:
.str_esc_store:
    mov [rsi], al
    inc r13
    inc rsi
    jmp .str_collect
.str_done:
    mov byte [rsi], 0
    inc r13
    mov rbx, [rel str_ptr]
    inc rsi
    mov [rel str_ptr], rsi
    mov qword [r15], TOK_STRING
    mov [r15+8], rbx
    mov qword [r15+16], 0
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12          ; exact source position for column/snippet diagnostics
    add r15, TOKEN_SIZE
    inc qword [rel token_cnt]
    jmp .lex_loop

.check_pluseq:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_pluseq
    cmp al, '+'
    je .emit_incr
    mov r8, '+'
    jmp .emit_op
.emit_incr:
    mov r8, 0x2B2B          ; ++
    add r13, 2
    jmp .emit_op2
.emit_pluseq:
    mov r8, 0x3D2B          ; +=
    add r13, 2
    jmp .emit_op2
.check_mineq:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_mineq
    cmp al, '-'
    je .emit_decr
    mov r8, '-'
    jmp .emit_op
.emit_decr:
    mov r8, 0x2D2D          ; --
    add r13, 2
    jmp .emit_op2
.emit_mineq:
    mov r8, 0x3D2D          ; -=
    add r13, 2
    jmp .emit_op2
.check_muleq:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_muleq
    mov r8, '*'
    jmp .emit_op
.emit_muleq:
    mov r8, 0x3D2A          ; *=
    add r13, 2
    jmp .emit_op2
.check_diveq:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_diveq
    mov r8, '/'
    jmp .emit_op
.emit_diveq:
    mov r8, 0x3D2F          ; /=
    add r13, 2
    jmp .emit_op2
.check_modeq:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_modeq
    mov r8, '%'
    jmp .emit_op
.emit_modeq:
    mov r8, 0x3D25          ; %=
    add r13, 2
    jmp .emit_op2

.check_eqeq:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_eqeq
    mov r8, '='
    jmp .emit_op
.emit_eqeq:
    mov r8, 0x3D3D
    add r13, 2
    jmp .emit_op2
.check_neq:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_neq
    inc r13
    jmp .lex_loop
.emit_neq:
    mov r8, 0x3D21
    add r13, 2
    jmp .emit_op2
.check_le:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_le
    cmp al, '<'                  ; << shift-left
    je .emit_shl
    mov r8, '<'
    jmp .emit_op
.emit_shl:
    mov r8, 0x3C3C
    add r13, 2
    jmp .emit_op2
.emit_le:
    mov r8, 0x3D3C
    add r13, 2
    jmp .emit_op2
.check_ge:
    movzx rax, byte [r13+1]
    cmp al, '='
    je .emit_ge
    cmp al, '>'                  ; >> shift-right
    je .emit_shr
    mov r8, '>'
    jmp .emit_op
.emit_shr:
    mov r8, 0x3E3E
    add r13, 2
    jmp .emit_op2
.emit_ge:
    mov r8, 0x3D3E
    add r13, 2
    jmp .emit_op2

.emit_op:
    inc r13
.emit_op2:
    mov qword [r15], TOK_OPERATOR
    mov [r15+8], r8
    mov qword [r15+16], 0
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12          ; exact source position for column/snippet diagnostics
    add r15, TOKEN_SIZE
    inc qword [rel token_cnt]
    jmp .lex_loop

.emit_delim:
    inc r13
    mov qword [r15], TOK_DELIMITER
    mov [r15+8], r8
    mov qword [r15+16], 0
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12          ; exact source position for column/snippet diagnostics
    add r15, TOKEN_SIZE
    inc qword [rel token_cnt]
    jmp .lex_loop

.skip_ws:
    cmp byte [r13], 10
    jne .sw_no_nl
    inc qword [rel cur_line]
.sw_no_nl:
    inc r13
    jmp .lex_loop

.lex_eof:
    mov r12, r13
    mov qword [r15], TOK_EOF
    mov qword [r15+8], 0
    mov qword [r15+16], 0
    mov rax, [rel cur_line]
    mov [r15+24], rax
    mov [r15+32], r12
    inc qword [rel token_cnt]
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ============================================================
; PARSER
; ============================================================
; AST node: 72 bytes
;   [0:8]  type
;   [8:16] field1
;   [16:24] field2
;   [24:32] field3
;   [32:40] field4
;   [40:48] field5
;   [48:56] field6
;   [56:64] field7
;   [64:72] field8

capacity_fail:
    ; rdi = NUL-terminated diagnostic. Capacity faults are compiler errors,
    ; never silent writes into the following BSS object.
    call print_str_z
    mov rdi, 1
    call os_exit

reserve_ast_block_extra:
    ; AST_BLOCK stores up to BLOCK_STMT_CAP statement pointers after the regular node.
    mov rax, [rel ast_ptr]
    add rax, AST_BLOCK_EXTRA
    lea rcx, [rel ast_heap]
    add rcx, AST_HEAP_CAP
    cmp rax, rcx
    ja .rabe_overflow
    mov [rel ast_ptr], rax
    ret
.rabe_overflow:
    lea rdi, [rel msg_ast_overflow]
    jmp capacity_fail

alloc_ast:
    push rbx
    mov rbx, [rel ast_ptr]
    lea rax, [rel ast_heap]
    add rax, AST_HEAP_CAP - AST_NODE_SIZE
    cmp rbx, rax
    ja .aa_overflow
    xor rax, rax
    mov [rbx], rax
    mov [rbx+8], rax
    mov [rbx+16], rax
    mov [rbx+24], rax
    mov [rbx+32], rax
    mov [rbx+40], rax
    mov [rbx+48], rax
    mov [rbx+56], rax
    mov [rbx+64], rax
    mov rax, rbx
    add rbx, AST_NODE_SIZE
    mov [rel ast_ptr], rbx
    pop rbx
    ret
.aa_overflow:
    pop rbx
    lea rdi, [rel msg_ast_overflow]
    jmp capacity_fail

cur_tok:
    mov rax, [rel token_idx]
    imul rax, rax, TOKEN_SIZE
    lea rcx, [rel token_arr]
    add rax, rcx
    ret

advance_tok:
    inc qword [rel token_idx]
    ret

parse_program:
    mov qword [rel top_const_count], 0
    mov qword [rel parse_error_kind], 0
    lea rax, [rel ast_heap]
    mov [rel ast_ptr], rax
    call parse_function
    mov [rel root_node], rax
    ret

parse_function:
    push rbx
    ; Parse top-level declarations (rachana, ayojan, prakriya) before mukhya
.pf_top_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_KEYWORD
    jne .pf_expect_mukhya
    mov rcx, [rax+16]
    cmp rcx, KW_RACHANA
    je .pf_top_decl
    cmp rcx, KW_AYOJAN
    je .pf_top_decl
    cmp rcx, KW_PRAKRIYA
    je .pf_top_decl
    cmp rcx, KW_SUTRA
    je .pf_top_const
    jmp .pf_expect_mukhya
.pf_top_const:
    ; Top-level sutra is a compile-time constant available to main and
    ; functions parsed below it. No native global storage/runtime init.
    call parse_stmt
    cmp qword [rax], AST_DECL
    jne parse_error
    mov rcx, [rel top_const_count]
    cmp rcx, 128
    jae .pf_top_const_limit
    lea rdx, [rel top_const_nodes]
    mov [rdx + rcx*8], rax
    inc qword [rel top_const_count]
    jmp .pf_top_loop
.pf_top_const_limit:
    lea rdi, [rel msg_func_defs_overflow]
    jmp capacity_fail
.pf_top_decl:
    call parse_stmt          ; parse the declaration
    ; If it's a FUNCDEF, store it in func_defs for gen_all_functions
    mov rcx, [rax]          ; node type
    cmp rcx, AST_FUNCDEF
    jne .pf_top_skip_store
    ; T4: definitions imported by ayojan share the same namespace as program
    ; functions.  Reject collisions instead of silently clobbering addresses.
    push rax
    mov rdi, [rax+8]
    call funcdef_name_exists
    test rax, rax
    jz .pf_top_unique
    pop rax
    push rax
    lea rdi, [rel msg_duplicate_func]
    call print_str_z
    pop rax
    mov rdi, [rax+8]
    call print_str_z
    lea rdi, [rel msg_nl]
    call print_str_z
    mov rdi, 1
    call os_exit
.pf_top_unique:
    pop rax
    ; Store in func_defs
    push rax
    mov rdx, [rel func_def_cnt]
    cmp rdx, FUNC_DEFS_CAP
    jae .pf_top_func_defs_overflow
    lea rcx, [rel func_defs]
    mov [rcx + rdx*8], rax
    inc qword [rel func_def_cnt]
    pop rax
    jmp .pf_top_skip_store
.pf_top_func_defs_overflow:
    pop rax
    lea rdi, [rel msg_func_defs_overflow]
    jmp capacity_fail
.pf_top_skip_store:
    jmp .pf_top_loop
.pf_expect_mukhya:
    ; Now expect mukhya
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_KEYWORD
    jne parse_error
    mov rcx, [rax+16]
    cmp rcx, KW_MUKHYA
    jne parse_error
    call advance_tok
    ; Expect ()
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne parse_error
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne parse_error
    mov rcx, [rax+8]
    cmp rcx, ')'
    jne parse_error
    call advance_tok
    ; Parse function body — braces are optional
    ; If '{', parse a brace-delimited block (multiple statements)
    ; If no '{', parse multiple statements until EOF
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pf_no_brace
    mov rcx, [rax+8]
    cmp rcx, '{'
    je .pf_brace
.pf_no_brace:
    ; Braceless function body — parse statements until EOF
    call parse_func_block
    jmp .pf_done
.pf_brace:
    call advance_tok          ; consume '{'
    call parse_block          ; rax = block node
.pf_done:
    mov rbx, rax              ; save block
    call alloc_ast            ; rax = new node
    mov qword [rax], 11      ; AST_FUNC
    mov [rax+8], rbx         ; body = block
    pop rbx
    ret

; parse_func_block() -> rax = block node
; Parses multiple statements until EOF (for braceless function bodies)
parse_func_block:
    push rbx
    push r12
    push r13
    call alloc_ast
    mov rbx, rax
    call reserve_ast_block_extra
    mov qword [rbx], AST_BLOCK
    xor r12, r12              ; statement count
.pfb_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_EOF
    je .pfb_done
    cmp rcx, TOK_DELIMITER
    jne .pfb_stmt
    mov rcx, [rax+8]
    cmp rcx, '}'
    je .pfb_done
.pfb_stmt:
    cmp r12, BLOCK_STMT_CAP
    jae .pfb_stmt_overflow
    call parse_stmt
    mov [rbx + 16 + r12*8], rax
    inc r12
    jmp .pfb_loop
.pfb_stmt_overflow:
    lea rdi, [rel msg_block_stmt_overflow]
    jmp capacity_fail
.pfb_done:
    mov [rbx+8], r12
    mov rax, rbx
    pop r13
    pop r12
    pop rbx
    ret

; parse_body() -> rax = block node
; For if/while bodies: if '{', parse brace block; else parse single statement
parse_body:
    push rbx
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pb_single
    mov rcx, [rax+8]
    cmp rcx, '{'
    je .pb_braces
.pb_single:
    call alloc_ast
    mov rbx, rax
    mov qword [rbx], AST_BLOCK
    call parse_stmt
    mov [rbx + 16], rax
    mov qword [rbx+8], 1
    mov rax, rbx
    pop rbx
    ret
.pb_braces:
    call advance_tok
    call parse_block
    pop rbx
    ret

; pick_lang_str(rdi = table of 11 string ptrs) -> rax = string for current language
pick_lang_str:
    mov rax, [rel cur_lang_id]
    shl rax, 3
    mov rax, [rdi + rax]
    ret

; set_lang_id: set cur_lang_id from the pack name held in r12
set_lang_id:
    push rbx
    xor rbx, rbx
.sli_loop:
    cmp rbx, 11
    jae .sli_done
    lea rax, [rel lang_names]
    mov rdi, [rax + rbx*8]
    test rdi, rdi
    jz .sli_next
    mov rsi, r12
    push rbx
    call strcmp
    pop rbx
    test rax, rax
    jz .sli_found
.sli_next:
    inc rbx
    jmp .sli_loop
.sli_found:
    mov [rel cur_lang_id], rbx
.sli_done:
    pop rbx
    ret

parse_error:
    cmp qword [rel r48_mode], 0
    jne _start.r48_parse_failure
    ; Sutram Error: parse error at line N near token 'X'
    push rbx
    lea rbx, [rel token_arr]
    mov r9, [rel token_idx]
    imul r9, r9, TOKEN_SIZE
    add rbx, r9             ; rbx = current token (callee-saved by our ABI)
    ; Print header + line number (localized)
    lea rdi, [rel tbl_err_line]
    call pick_lang_str
    mov rdi, rax
    call print_str_z
    mov rdi, [rbx+24]       ; line number (stored by lexer)
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    lea rdi, [rel msg_err_colon]
    call print_str_z
    mov rdi, [rbx+32]        ; exact token source pointer
    call calc_src_column
    mov rdi, rax
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    lea rdi, [rel tbl_err_near]
    call pick_lang_str
    mov rdi, rax
    call print_str_z
    ; Print the token text based on type
    mov r9, [rbx]           ; token type
    cmp r9, TOK_KEYWORD
    je .pe_strval
    cmp r9, TOK_IDENT
    je .pe_strval
    cmp r9, TOK_BUILTIN
    je .pe_strval
    cmp r9, TOK_STRING
    je .pe_strval
    cmp r9, TOK_NUMBER
    je .pe_numval
    cmp r9, TOK_EOF
    je .pe_eof
    ; TOK_OPERATOR / TOK_DELIMITER: value = char code (1 or 2 chars packed)
    mov rax, [rbx+8]
    push rax
    lea rcx, [rel pe_charbuf]
    mov [rcx], al
    mov byte [rcx+1], 0
    pop rax
    cmp rax, 255
    jbe .pe_printbuf
    shr rax, 8
    push rax
    lea rcx, [rel pe_charbuf]
    mov [rcx+1], al
    mov byte [rcx+2], 0
    pop rax
.pe_printbuf:
    lea rdi, [rel pe_charbuf]
    call print_str_z
    jmp .pe_end
.pe_strval:
    mov rdi, [rbx+8]
    call print_str_z
    jmp .pe_end
.pe_numval:
    mov rdi, [rbx+8]
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    jmp .pe_end
.pe_eof:
    lea rdi, [rel tbl_err_eof]
    call pick_lang_str
    mov rdi, rax
    call print_str_z
.pe_end:
    lea rdi, [rel msg_err_end]
    call print_str_z
    mov rdi, [rbx+32]
    call print_source_context
    cmp qword [rel parse_error_kind], 1
    jne .pe_check_duplicate
    lea rdi, [rel msg_err_arg_limit]
    call print_str_z
    jmp .pe_exit
.pe_check_duplicate:
    cmp qword [rel parse_error_kind], 2
    jne .pe_generic_hint
    lea rdi, [rel msg_err_duplicate_func]
    call print_str_z
    jmp .pe_exit
.pe_generic_hint:
    lea rdi, [rel tbl_err_hint]
    call pick_lang_str
    mov rdi, rax
    call print_str_z
.pe_exit:
    pop rbx
    mov rdi, 1
    call os_exit

; R48 post-parse semantic diagnostics for unresolved user function calls.
; The code generator already owns function lookup; no second parser is used.
; Match the exact original lexer token pointer to recover line, column,
; offending identifier and source/caret. No output binary is written.
r48_print_undefined_function:
    push rbx
    push r12
    push r13
    mov r12, rdi
    xor ebx, ebx
.r48_lookup:
    cmp rbx, [rel token_cnt]
    jae .r48_fallback
    mov rax, rbx
    imul rax, TOKEN_SIZE
    lea r13, [rel token_arr]
    add r13, rax
    cmp qword [r13], TOK_IDENT
    jne .r48_next
    ; R49: token lexeme pointers are unique per occurrence. Matching by
    ; string text mislocated repeated unresolved calls at the FIRST call.
    ; Patch-list function-name pointers come from their exact lexer token,
    ; so pointer identity gives the original occurrence and caret.
    cmp qword [r13+8], r12
    je .r48_found
.r48_next:
    inc rbx
    jmp .r48_lookup
.r48_found:
    mov rdi, [rel source_path_ptr]
    call graph_print_file
    lea rdi, [rel msg_err_colon]
    call print_str_z
    mov rdi, [r13+24]
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    lea rdi, [rel msg_err_colon]
    call print_str_z
    mov rdi, [r13+32]
    call calc_src_column
    mov rdi, rax
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    lea rdi, [rel r48_msg_undefined]
    call print_str_z
    mov rdi, r12
    call print_str_z
    lea rdi, [rel r48_msg_end]
    call print_str_z
    mov rdi, [r13+32]
    call print_source_context
    jmp .r48_sem_done
.r48_fallback:
    ; In unusual imported/rewritten source, a call-name pointer may not
    ; match a local token. Never fabricate a line number or location.
    lea rdi, [rel msg_undefined_func]
    call print_str_z
    mov rdi, r12
    call print_str_z
    lea rdi, [rel msg_nl]
    call print_str_z
.r48_sem_done:
    pop r13
    pop r12
    pop rbx
    ret

; R48 check mode: diagnostics reuse lexer-origin token source position.
; Unlike the normal localized parser error output, the check-mode protocol
; produces stable path:line:column and offending token plus source/caret.
r48_print_parse_error:
    push rbx
    call cur_tok
    mov rbx, rax
    mov rax, [rbx+24]
    mov [rel r48_error_line], rax
    mov rdi, [rel source_path_ptr]
    call graph_print_file
    lea rdi, [rel msg_err_colon]
    call print_str_z
    mov rdi, [rbx+24]
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    lea rdi, [rel msg_err_colon]
    call print_str_z
    mov rdi, [rbx+32]
    call calc_src_column
    mov rdi, rax
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    lea rdi, [rel r48_msg_near]
    call print_str_z
    mov rcx, [rbx]
    cmp rcx, TOK_EOF
    je .r48_eof
    cmp rcx, TOK_IDENT
    je .r48_word
    cmp rcx, TOK_KEYWORD
    je .r48_word
    cmp rcx, TOK_BUILTIN
    je .r48_word
    cmp rcx, TOK_STRING
    je .r48_word
    cmp rcx, TOK_NUMBER
    je .r48_num
    mov rax, [rbx+8]
    lea rcx, [rel r48_charbuf]
    mov [rcx], al
    mov byte [rcx+1], 0
    cmp rax, 255
    jbe .r48_chars
    shr rax, 8
    mov [rcx+1], al
    mov byte [rcx+2], 0
.r48_chars:
    mov rdi, rcx
    call print_str_z
    jmp .r48_end
.r48_word:
    mov rdi, [rbx+8]
    call print_str_z
    jmp .r48_end
.r48_num:
    mov rdi, [rbx+8]
    lea rsi, [rel num_buf]
    call itoa
    mov rdi, rax
    call print_str_z
    jmp .r48_end
.r48_eof:
    lea rdi, [rel r48_msg_eof]
    call print_str_z
.r48_end:
    lea rdi, [rel r48_msg_end]
    call print_str_z
    mov rdi, [rbx+32]
    call print_source_context
    pop rbx
    ret

; Synchronize by removing ONLY the malformed lexical statement from the
; in-memory token stream, then re-run the same parser from its top level.
; Original source text and source offsets remain unchanged for diagnostics.
; Stop before '}' or EOF, or consume ';'; do not discard a closing brace.
; Abort when a safe separator cannot be found to avoid phantom errors.
r48_recover_stmt:
    ; Stage 2: start at malformed statement (not the error token).
    ; Deep expression parsing may have already passed a safe ';' boundary.
    ; Track delimiter depth, protect enclosing '}' and original EOF.
    push rbx
    push r12
    push r13
    push r14
    cmp qword [rel r48_stmt_valid], 1
    jne .r48_no
    mov r8, [rel r48_stmt_start]
    mov r12, [rel token_idx]
    mov r10, [rel token_cnt]
    cmp r8, r12
    ja .r48_no
    cmp r12, r10
    jae .r48_no
    mov r9, r8
    xor r13d, r13d                 ; parentheses depth
    xor r14d, r14d                 ; brackets depth
    xor ebx, ebx                   ; braces depth
.r48_find:
    cmp r9, r10
    jae .r48_no
    mov rax, r9
    imul rax, TOKEN_SIZE
    lea r11, [rel token_arr]
    add r11, rax
    cmp qword [r11], TOK_EOF
    je .r48_no                     ; never remove EOF and restart
    cmp qword [r11], TOK_DELIMITER
    jne .r48_line
    mov rax, [r11+8]
    cmp rax, '('
    je .r48_open_paren
    cmp rax, ')'
    je .r48_close_paren
    cmp rax, '['
    je .r48_open_bracket
    cmp rax, ']'
    je .r48_close_bracket
    cmp rax, '{'
    je .r48_open_brace
    cmp rax, '}'
    je .r48_close_brace
    cmp rax, ';'
    jne .r48_line
    test r13, r13                   ; semicolon in for(...) is not stmt end
    jnz .r48_next
    test r14, r14
    jnz .r48_next
    test rbx, rbx
    jnz .r48_next
    inc r9                         ; consume outer statement ';'
    jmp .r48_found
.r48_open_paren:
    inc r13
    jmp .r48_next
.r48_close_paren:
    test r13, r13
    jz .r48_next
    dec r13
    jmp .r48_next
.r48_open_bracket:
    inc r14
    jmp .r48_next
.r48_close_bracket:
    test r14, r14
    jz .r48_next
    dec r14
    jmp .r48_next
.r48_open_brace:
    inc rbx
    jmp .r48_next
.r48_close_brace:
    test rbx, rbx
    jz .r48_found                  ; protect enclosing block closer
    dec rbx
    jmp .r48_next
.r48_line:
    cmp r9, r12
    jbe .r48_next
    mov rax, [r11+24]
    cmp rax, [rel r48_error_line]
    jbe .r48_next
    cmp qword [r11], TOK_KEYWORD
    jne .r48_next
    ; Preserve conservative fallback when the subsequent physical line
    ; has a keyword-led statement but the delimiter is missing.
    jmp .r48_found
.r48_next:
    inc r9
    jmp .r48_find
.r48_found:
    cmp r9, r8
    jbe .r48_no
    mov rax, r9
    sub rax, r8
    mov rdx, r10
    sub rdx, rax
    mov [rel token_cnt], rdx
    lea rdi, [rel token_arr]
    mov rax, r8
    imul rax, TOKEN_SIZE
    add rdi, rax
    lea rsi, [rel token_arr]
    mov rax, r9
    imul rax, TOKEN_SIZE
    add rsi, rax
    mov rcx, r10
    sub rcx, r9
    imul rcx, TOKEN_SIZE
    cld
    rep movsb
    mov eax, 1
    jmp .r48_done
.r48_no:
    xor eax, eax
.r48_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; calc_src_column(rdi = token source pointer) -> rax = 1-based display column
; UTF-8 continuation bytes do not advance the display column.
calc_src_column:
    push rbx
    push r12
    mov rbx, rdi
    lea r12, [rel source_buf]
    mov rax, 1
    cmp rbx, r12
    jbe .csc_done
    dec rbx
.csc_loop:
    cmp rbx, r12
    jb .csc_done
    movzx edx, byte [rbx]
    cmp dl, 10
    je .csc_done
    mov ecx, edx
    and ecx, 0xC0
    cmp ecx, 0x80
    je .csc_prev
    inc rax
.csc_prev:
    dec rbx
    jmp .csc_loop
.csc_done:
    pop r12
    pop rbx
    ret

; print_source_context(rdi = token source pointer)
; Prints the offending source line plus a caret under the token.  Tabs are
; preserved and UTF-8 continuation bytes do not add extra caret spacing.
print_source_context:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r12, rdi                    ; token pointer
    lea r13, [rel source_buf]       ; source start
    lea r15, [rel source_buf]
    add r15, [rel source_len]       ; source end
    cmp r12, r15
    jbe .psc_ptr_ok
    mov r12, r15
.psc_ptr_ok:
    ; Find start of the source line.
    mov rbx, r12
.psc_back:
    cmp rbx, r13
    jbe .psc_line_start
    cmp byte [rbx-1], 10
    je .psc_line_start
    dec rbx
    jmp .psc_back
.psc_line_start:
    mov r13, rbx                    ; r13 = line start
    ; Find end of the source line.
    mov r14, r13
.psc_fwd:
    cmp r14, r15
    jae .psc_line_end
    mov al, [r14]
    cmp al, 10
    je .psc_line_end
    cmp al, 13
    je .psc_line_end
    inc r14
    jmp .psc_fwd
.psc_line_end:
    lea rdi, [rel msg_diag_indent]
    call print_str_z
    mov rdi, 1
    mov rsi, r13
    mov rdx, r14
    sub rdx, r13
    call os_write
    lea rdi, [rel msg_diag_nl]
    call print_str_z
    lea rdi, [rel msg_diag_indent]
    call print_str_z
    ; Reproduce horizontal layout up to the token using spaces/tabs.
    mov rbx, r13
.psc_caret_loop:
    cmp rbx, r12
    jae .psc_caret
    movzx eax, byte [rbx]
    cmp al, 9
    je .psc_tab
    mov edx, eax
    and edx, 0xC0
    cmp edx, 0x80
    je .psc_next                  ; continuation byte: same display cell
    lea rdi, [rel msg_diag_space]
    call print_str_z
    jmp .psc_next
.psc_tab:
    lea rdi, [rel msg_diag_tab]
    call print_str_z
.psc_next:
    inc rbx
    jmp .psc_caret_loop
.psc_caret:
    lea rdi, [rel msg_diag_caret]
    call print_str_z
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_block() → rax = block node
parse_block:
    push rbx
    push r12
    push r13
    mov rax, [rel parse_block_depth]
    cmp rax, BLOCK_NESTING_CAP
    jae .pblock_nesting_overflow
    inc qword [rel parse_block_depth]
    call alloc_ast
    mov rbx, rax              ; block node
    call reserve_ast_block_extra
    mov qword [rbx], AST_BLOCK
    xor r12, r12              ; statement count
.pblock_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pblock_stmt
    mov rcx, [rax+8]
    cmp rcx, '}'
    je .pblock_done
.pblock_stmt:
    cmp r12, BLOCK_STMT_CAP
    jae .pblock_stmt_overflow
    call parse_stmt           ; rax = statement node
    mov [rbx + 16 + r12*8], rax
    inc r12
    jmp .pblock_loop
.pblock_stmt_overflow:
    lea rdi, [rel msg_block_stmt_overflow]
    jmp capacity_fail
.pblock_done:
    call advance_tok          ; consume }
    mov [rbx+8], r12          ; statement count
    mov rax, rbx
    dec qword [rel parse_block_depth]
    pop r13
    pop r12
    pop rbx
    ret
.pblock_nesting_overflow:
    lea rdi, [rel msg_block_nesting_overflow]
    jmp capacity_fail

; parse_stmt() → rax = statement node
parse_stmt:
    push rbx
    cmp qword [rel r48_mode], 0
    je .r48_no_mark
    mov rax, [rel token_idx]
    mov [rel r48_stmt_start], rax
    mov qword [rel r48_stmt_valid], 1
.r48_no_mark:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_EOF          ; stop cleanly instead of looping on malformed input
    jne .ps_not_eof
    pop rbx
    jmp parse_error
.ps_not_eof:
    mov rdx, [rax+16]

    ; Variable declaration?
    cmp rcx, TOK_KEYWORD
    jne .ps_check_expr
    cmp rdx, KW_VITTI
    je .ps_decl
    cmp rdx, KW_ANKA
    je .ps_decl
    cmp rdx, KW_SANKHYA
    je .ps_decl
    cmp rdx, KW_PARIGRAH
    je .ps_decl
    cmp rdx, KW_PANKTI
    je .ps_decl
    cmp rdx, KW_DASHAM
    je .ps_fdecl
    cmp rdx, KW_KOSH
    je .ps_kosh
    cmp rdx, KW_SRIJANA
    je .ps_sutra
    cmp rdx, KW_GUNA
    je .ps_guna
    cmp rdx, KW_NISHKRIYA
    je .ps_nishkriya
    cmp rdx, KW_YADI
    je .ps_if
    cmp rdx, KW_PRAKRIYA
    je .ps_funcdef
    cmp rdx, KW_AYOJAN
    je .ps_ayojan
    cmp rdx, KW_RACHANA
    je .ps_rachana
    cmp rdx, KW_YAVAT
    je .ps_while
    cmp rdx, KW_KURU
    je .ps_do_while
    cmp rdx, KW_PRATIYATI
    je .ps_return
    cmp rdx, KW_PUNARAVARTANA
    je .ps_for
    cmp rdx, KW_SUTRA
    je .ps_sutra
    cmp rdx, KW_NISHEDHA
    je .ps_nishedha
    cmp rdx, KW_KRAMA
    je .ps_krama
    cmp rdx, KW_UDDESHYA
    je .ps_uddeshya
    jmp .ps_check_expr

.ps_decl:
    call advance_tok          ; consume type keyword
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_IDENT
    jne parse_error
    mov rbx, [rax+8]         ; variable name ptr
    call advance_tok
    ; Check for [N] (array declaration: vitti arr[10] / pankti arr[10])
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .ps_decl_check_init
    mov rcx, [rax+8]
    cmp rcx, '['
    jne .ps_decl_check_init
    ; Array declaration: vitti name[size]
    call advance_tok          ; consume '['
    call parse_expr           ; rax = size expr
    ; T8b: keep the size AST on the declaration itself.  Runtime array
    ; metadata is stored in a hidden header immediately before element 0,
    ; avoiding the old compilation-global name table and supporting dynamic
    ; lengths plus same-named arrays in separate function scopes.
    push rax                  ; save size expr
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ']'
    jne parse_error
    call advance_tok          ; consume ']'
    call maybe_semi
    ; Build DECL directly.  The array code generator owns allocation, so no
    ; legacy nirmmita(size*8) AST is needed and the size expression is kept
    ; intact/evaluated exactly once at runtime.
    call alloc_ast
    pop rdx                   ; original size expression
    mov qword [rax], AST_DECL
    mov [rax+8], rbx          ; name
    mov qword [rax+16], 0     ; no ordinary initializer
    mov [rax+24], rdx         ; nonzero marks array declaration + size AST
    pop rbx
    ret
.ps_decl_check_init:
    ; Check for = expr
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .ps_decl_noinit
    mov rcx, [rax+8]
    cmp rcx, '='
    jne .ps_decl_noinit
    call advance_tok          ; consume '='
    call parse_expr           ; rax = init expr
    ; Build decl node with init
    push rax                  ; save init expr
    push rbx                  ; save name
    call alloc_ast
    pop rbx                   ; restore name
    pop rcx                   ; restore init expr (was rax from parse_expr)
    ; Wait — alloc_ast clobbers rax. But we pushed the init expr value.
    ; Actually: we pushed rax (init expr), then rbx (name).
    ; alloc_ast returns in rax. pop rbx restores name. pop rcx restores init expr.
    ; But alloc_ast might clobber rcx! Let me fix the pop order.
    ; Actually, alloc_ast only uses rbx (pushed/popped internally).
    ; So rcx from pop is safe.
    mov qword [rax], AST_DECL
    mov [rax+8], rbx          ; name
    mov [rax+16], rcx         ; init expr
    call maybe_semi
    pop rbx
    ret

.ps_decl_noinit:
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_DECL
    mov [rax+8], rbx
    mov qword [rax+16], 0
    call maybe_semi
    pop rbx
    ret

.ps_kosh:
    ; T18 growable array. `kosh name` is integer/raw-qword;
    ; `kosh dasham name` / `कोश दशम name` stores IEEE-754 binary64 elements.
    ; Capacity is optional (default 4); logical length starts at zero.
    call advance_tok         ; consume kosh / कोश
    call cur_tok
    mov rdx, 2               ; AST_DECL marker 2 = integer/raw kosh
    cmp qword [rax], TOK_KEYWORD
    jne .ps_kosh_name
    cmp qword [rax+16], KW_DASHAM
    jne .ps_kosh_name
    mov rdx, 3               ; marker 3 = kosh dasham
    call advance_tok         ; consume dasham / दशम
    call cur_tok
.ps_kosh_name:
    push rdx                 ; preserve element type through parsing
    cmp qword [rax], TOK_IDENT
    jne parse_error
    mov rbx, [rax+8]
    call advance_tok
    call cur_tok
    cmp qword [rax], TOK_DELIMITER
    jne .ps_kosh_default_cap
    cmp qword [rax+8], '['
    jne .ps_kosh_default_cap
    call advance_tok
    call parse_expr
    push rax
    call cur_tok
    cmp qword [rax+8], ']'
    jne parse_error
    call advance_tok
    jmp .ps_kosh_have_cap
.ps_kosh_default_cap:
    call alloc_ast
    mov qword [rax], AST_NUM
    mov qword [rax+8], 4
    push rax
.ps_kosh_have_cap:
    push rbx
    call alloc_ast
    pop rbx
    pop rcx                  ; capacity expression
    pop rdx                  ; declaration element-type marker
    mov qword [rax], AST_DECL
    mov [rax+8], rbx
    mov qword [rax+16], 0
    mov [rax+24], rcx
    mov [rax+32], rdx        ; 2=integer/raw kosh, 3=kosh dasham
    call maybe_semi
    pop rbx
    ret

.ps_fdecl:
    ; T12 scalar double declaration: dasham name [= expr]
    call advance_tok
    call cur_tok
    cmp qword [rax], TOK_IDENT
    jne parse_error
    mov rbx, [rax+8]
    call advance_tok
    call cur_tok
    cmp qword [rax], TOK_OPERATOR
    jne .ps_fdecl_noinit
    cmp qword [rax+8], '='
    jne .ps_fdecl_noinit
    call advance_tok
    call parse_expr
    push rax
    push rbx
    call alloc_ast
    pop rbx
    pop rcx
    mov qword [rax], AST_DECL
    mov [rax+8], rbx
    mov [rax+16], rcx
    mov qword [rax+32], 1     ; declaration type marker: dasham
    call maybe_semi
    pop rbx
    ret
.ps_fdecl_noinit:
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_DECL
    mov [rax+8], rbx
    mov qword [rax+16], 0
    mov qword [rax+32], 1
    call maybe_semi
    pop rbx
    ret

.ps_nishkriya:
    ; nishkriya("hex bytes") — inline assembly
    call advance_tok          ; consume 'nishkriya'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok
    call cur_tok
    mov rcx, [rax]            ; token type
    cmp rcx, TOK_STRING
    jne parse_error           ; nishkriya requires a string literal
    mov rbx, [rax+8]          ; rbx = string pointer
    call advance_tok          ; consume string
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ')'
    jne parse_error
    call advance_tok          ; consume ')'
    ; Build node: [AST_NISHKRIYA][str_ptr][0][0]
    push rbx
    call alloc_ast
    pop rcx
    mov qword [rax], AST_NISHKRIYA
    mov [rax+8], rcx          ; hex string pointer
    mov qword [rax+16], 0
    call maybe_semi
    pop rbx
    ret

.ps_if:
    ; Simplified — parse if(cond){block}
    call advance_tok          ; consume 'yadi'
    ; expect (
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok
    call parse_expr           ; rax = condition
    mov rbx, rax              ; save condition
    ; expect )
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ')'
    jne parse_error
    call advance_tok
    ; Parse body — braces optional
    call parse_body            ; rax = then-block
    ; Build if node: [AST_IF][cond][then][else=0]
    push rax                  ; save then-block
    push rbx                  ; save condition
    call alloc_ast
    pop rbx                   ; restore condition
    pop rcx                   ; restore then-block
    ; Same issue: alloc_ast clobbers rax, but rbx and rcx are from pop
    mov qword [rax], AST_IF
    mov [rax+8], rbx          ; condition
    mov [rax+16], rcx         ; then block
    mov qword [rax+24], 0    ; no else
    ; Check for 'anyatra' (else)
    push rax                  ; save if-node
    call cur_tok
    mov rcx, [rax]            ; token type
    cmp rcx, TOK_KEYWORD
    jne .ps_if_no_else
    mov rcx, [rax+16]         ; keyword id
    cmp rcx, KW_ANYATRA
    jne .ps_if_no_else
    ; Found 'anyatra' — consume it
    call advance_tok
    ; Parse else body
    call parse_body            ; rax = else-block
    mov rcx, rax              ; rcx = else-block
    mov rax, [rsp]            ; rax = if-node
    mov [rax+24], rcx         ; store else block
.ps_if_no_else:
    ; Check for 'anyatra' (else or elif)
    ; if-node is already on stack from push at line ~1245
    call cur_tok
    mov rcx, [rax]            ; token type
    cmp rcx, TOK_KEYWORD
    jne .ps_if_done
    mov rcx, [rax+16]         ; keyword id
    cmp rcx, KW_ANYATRA
    jne .ps_if_done
    ; Found 'anyatra' — check if next is 'yadi' (elif)
    call advance_tok          ; consume 'anyatra'
    call cur_tok
    mov rcx, [rax+16]
    cmp rcx, KW_YADI
    jne .ps_if_else_body
    ; It's 'anyatra yadi' (elif) — parse as nested if
    call .ps_if               ; recursively parse if, returns in rax
    mov rcx, rax              ; rcx = nested if-node
    mov rax, [rsp]            ; rax = original if-node
    mov [rax+24], rcx         ; store as else block
    jmp .ps_if_done
.ps_if_else_body:
    ; Regular else — parse body
    call parse_body            ; rax = else-block
    mov rcx, rax
    mov rax, [rsp]            ; rax = if-node
    mov [rax+24], rcx         ; store else block
.ps_if_done:
    pop rax
    pop rbx
    ret

.ps_funcdef:
    ; prakriya name(params) { body }
    push r12                 ; save r12 (parse_func_block uses it as stmt count)
    push r13                 ; save r13 (parse_func_block uses it as stmt index)
    call advance_tok          ; consume 'prakriya'
    ; Expect function name
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_IDENT
    jne parse_error
    mov rbx, [rax+8]         ; function name ptr
    call advance_tok
    ; Expect (
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok
    ; Parse parameter list — collect param names into func_params
    ; r13 continues from param_buf_pos so each function's params stay intact
    xor r12, r12             ; param count
    mov r13, [rel param_buf_pos]   ; offset in func_params (accumulating)
.ps_fd_param:
    xor r10d, r10d            ; PARAM_RAW unless an explicit type prefix follows
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .ps_fd_param_maybe_type
    mov rcx, [rax+8]
    cmp rcx, ')'
    je .ps_fd_params_done
    cmp rcx, ','
    je .ps_fd_comma
    jmp parse_error
.ps_fd_param_maybe_type:
    cmp rcx, TOK_KEYWORD
    jne .ps_fd_param_name
    cmp qword [rax+16], KW_DASHAM
    je .ps_fd_param_dasham
    cmp qword [rax+16], KW_KOSH
    je .ps_fd_param_kosh
    jmp parse_error
.ps_fd_param_dasham:
    mov r10d, PARAM_DASHAM
    call advance_tok          ; consume dasham / दशम
    call cur_tok
    mov rcx, [rax]
    jmp .ps_fd_param_name
.ps_fd_param_kosh:
    mov r10d, PARAM_KOSH
    call advance_tok          ; consume kosh / कोश
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_KEYWORD
    jne .ps_fd_param_name
    cmp qword [rax+16], KW_DASHAM
    jne parse_error
    mov r10d, PARAM_KOSH_DASHAM
    call advance_tok          ; consume dasham / दशम after kosh
    call cur_tok
    mov rcx, [rax]
.ps_fd_param_name:
    ; Preserve the historical permissive untyped-parameter grammar. Explicit
    ; dasham/kosh prefixes require a following identifier.
    test r10d, r10d
    jz .ps_fd_param_name_ok
    cmp rcx, TOK_IDENT
    jne parse_error
.ps_fd_param_name_ok:
    cmp r12, 6
    jb .ps_fd_param_ok
    mov qword [rel parse_error_kind], 1
    jmp parse_error
.ps_fd_param_ok:
    cmp r13, FUNC_PARAMS_CAP
    jae .ps_fd_param_capacity
    ; Store parameter type in a parallel table indexed by the qword name slot.
    mov rdx, r13
    shr rdx, 3
    lea rcx, [rel func_param_types]
    mov [rcx + rdx], r10b
    mov rcx, [rax+8]         ; param name ptr
    lea rax, [rel func_params]
    mov [rax + r13], rcx
    add r13, 8
    inc r12
    call advance_tok
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne parse_error
    mov rcx, [rax+8]
    cmp rcx, ','
    je .ps_fd_comma
    cmp rcx, ')'
    je .ps_fd_params_done
    jmp parse_error
.ps_fd_comma:
    call advance_tok
    jmp .ps_fd_param
.ps_fd_param_capacity:
    lea rdi, [rel msg_func_params_overflow]
    jmp capacity_fail
.ps_fd_params_done:
    call advance_tok          ; consume ')'
    ; Parse body
    call parse_body           ; rax = body block
    ; Build funcdef node: [AST_FUNCDEF][name_ptr][param_count][body]
    push rax                  ; save body
    push rbx                  ; save name
    push r12                  ; save param count
    call alloc_ast
    pop r12                   ; restore param count
    pop rbx                   ; restore name
    pop rcx                   ; restore body
    mov qword [rax], AST_FUNCDEF
    mov [rax+8], rbx          ; function name
    mov [rax+16], r12         ; param count
    mov [rax+24], rcx         ; body block
    mov [rax+32], r13         ; param buffer end position
    mov qword [rax+40], 0
    mov [rel param_buf_pos], r13   ; remember cursor for the next function
    pop r13                  ; restore r13
    pop r12                  ; restore r12
    pop rbx
    ret

.ps_for:
    ; punaravartana i = start to end { body }
    call advance_tok          ; consume 'punaravartana'
    ; Expect variable name
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_IDENT
    jne parse_error
    mov rbx, [rax+8]         ; var name ptr
    call advance_tok
    ; Expect '='
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '='
    jne parse_error
    call advance_tok          ; consume '='
    ; Parse start expression
    call parse_expr           ; rax = start expr
    push rax                  ; save start expr
    ; Expect 'to' keyword (punaravartana uses 'to' as contextual keyword)
    ; We accept bare identifier 'to' or keyword
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_IDENT
    jne .ps_for_check_kw
    ; Check if it's literally 'to' (2 bytes: 't','o',0)
    mov rdi, [rax+8]
    movzx ecx, word [rdi]
    cmp ecx, 0x6F74       ; 'to' in LE = 0x6F74
    jne .ps_for_lang_to
    movzx ecx, byte [rdi+2]
    test ecx, ecx
    jnz .ps_for_lang_to
    jmp .ps_for_got_to
.ps_for_lang_to:
    ; or the loaded language's native word for 'to'
    cmp byte [rel lang_to_word], 0
    je parse_error
    call cur_tok
    mov rdi, [rax+8]
    lea rsi, [rel lang_to_word]
    call strcmp
    test rax, rax
    jnz parse_error
    jmp .ps_for_got_to
.ps_for_check_kw:
    jmp parse_error
.ps_for_got_to:
    call advance_tok          ; consume 'to'
    ; Parse end expression
    call parse_expr           ; rax = end expr
    push rax                  ; save end expr
    ; Parse body
    call parse_body           ; rax = body block
    push rax                  ; save body
    ; Build AST_FOR node
    push rbx                  ; save var name
    call alloc_ast
    pop rbx                   ; restore var name
    pop rcx                   ; restore body
    pop rdx                   ; restore end expr
    pop rsi                   ; restore start expr
    mov qword [rax], AST_FOR
    mov [rax+8], rbx          ; var name
    mov [rax+16], rsi         ; start expr
    mov [rax+24], rdx         ; end expr
    mov [rax+32], rcx         ; body block
    mov qword [rax+40], 0    ; no step yet
    call maybe_semi
    pop rbx
    ret

.ps_sutra:
    ; sutra NAME = value  (compile-time constant — treated as vitti)
    call advance_tok          ; consume 'sutra'
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_IDENT
    jne parse_error
    mov rbx, [rax+8]
    call advance_tok
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '='
    jne parse_error
    call advance_tok
    call parse_expr
    push rax
    push rbx
    call alloc_ast
    pop rbx
    pop rcx
    mov qword [rax], AST_DECL
    mov [rax+8], rbx
    mov [rax+16], rcx
    call maybe_semi
    pop rbx
    ret

.ps_nishedha:
    ; nishedha(expr)  — assert: if expr is false, exit with error
    call advance_tok          ; consume 'nishedha'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok           ; consume '('
    call parse_expr            ; rax = condition
    push rax                  ; save condition
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ')'
    jne parse_error
    call advance_tok           ; consume ')'
    call maybe_semi
    pop rcx                   ; restore condition
    push rcx
    call alloc_ast
    pop rcx
    mov qword [rax], AST_ASSERT
    mov [rax+8], rcx          ; condition
    mov qword [rax+16], 0
    pop rbx
    ret

.ps_krama:
    ; krama  — break out of loop
    call advance_tok          ; consume 'krama'
    call maybe_semi
    push 0
    call alloc_ast
    pop rcx
    mov qword [rax], AST_BREAK
    mov qword [rax+8], 0
    pop rbx
    ret

.ps_uddeshya:
    ; uddeshya  — continue to next loop iteration
    call advance_tok          ; consume 'uddeshya'
    call maybe_semi
    push 0
    call alloc_ast
    pop rcx
    mov qword [rax], AST_CONTINUE
    mov qword [rax+8], 0
    pop rbx
    ret

.ps_guna:
    ; guna (expr) { bhavana VAL: { body } ... anyatra: { body } }
    ; Desugars to if-elif chain using stack: [rbp_g-8]=expr, [rbp_g-16]=first, [rbp_g-24]=last
    call advance_tok          ; consume 'guna'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok          ; consume '('
    call parse_expr           ; rax = switch expression
    push rax                  ; [rsp+16] = switch_expr
    push 0                    ; [rsp+8]  = first_if = NULL
    push 0                    ; [rsp+0]  = last_if = NULL
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ')'
    jne parse_error
    call advance_tok          ; consume ')'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '{'
    jne parse_error
    call advance_tok          ; consume '{'

.ps_guna_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .ps_guna_check_kw
    mov rcx, [rax+8]
    cmp rcx, '}'
    je .ps_guna_done

.ps_guna_check_kw:
    mov rcx, [rax]
    cmp rcx, TOK_KEYWORD
    jne .ps_guna_done
    mov rdx, [rax+16]
    cmp rdx, KW_BHAVANA
    je .ps_guna_case
    cmp rdx, KW_ANYATRA
    je .ps_guna_default
    jmp .ps_guna_done

.ps_guna_case:
    call advance_tok          ; consume 'bhavana'
    call parse_expr           ; rax = case value
    push rax                  ; [rsp+0]=case_val, [rsp+8]=last, [rsp+16]=first, [rsp+24]=expr
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ':'
    jne parse_error
    call advance_tok          ; consume ':'
    ; Now parse_body. Save nothing extra - parse_body preserves rsp.
    ; But we need switch_expr after parse_body. It's at [rsp+24].
    call parse_body           ; rax = body block
    pop rcx                   ; rcx = case_val. [rsp+0]=last,[rsp+8]=first,[rsp+16]=expr
    ; Create BINOP(OP_EQ, switch_expr, case_val)
    push rax                  ; save body. [rsp+0]=body,[rsp+8]=last,[rsp+16]=first,[rsp+24]=expr
    call alloc_ast            ; rax = binop node
    pop rdx                   ; rdx = body. [rsp+0]=last,[rsp+8]=first,[rsp+16]=expr
    mov qword [rax], 4        ; AST_BINOP
    mov qword [rax+8], OP_EQ
    mov r8, [rsp+16]          ; r8 = switch_expr
    mov [rax+16], r8          ; left = switch_expr
    mov [rax+24], rcx         ; right = case_val
    ; Create IF(binop, body, NULL)
    ; rax=binop, rdx=body. Save both on stack.
    push rdx                  ; save body
    push rax                  ; save binop
    call alloc_ast            ; rax = if node
    pop rdx                   ; rdx = binop
    pop rcx                   ; rcx = body
    mov qword [rax], 5        ; AST_IF
    mov [rax+8], rdx          ; cond = binop
    mov [rax+16], rcx         ; then = body
    mov qword [rax+24], 0     ; else = NULL
    ; Link: if last != NULL, set [last+24] = this_if
    mov r8, [rsp]             ; r8 = last_if
    test r8, r8
    jz .ps_guna_newfirst
    ; Wrap this IF in a BLOCK node so gen_block can handle it as else
    push rax                  ; save IF2. Stack: [IF2][last][first][expr]
    call alloc_ast            ; rax = block node. Stack unchanged.
    pop rdx                   ; rdx = IF2. Stack: [last][first][expr]
    mov qword [rax], 10       ; AST_BLOCK
    mov [rax+16], rdx          ; statement[0] = IF2
    mov qword [rax+8], 1      ; count = 1
    ; Link: prev_if.else = block(IF2)
    mov [r8+24], rax
    mov rax, rdx              ; rax = IF2 (not BLOCK) so setlast stores IF2
    jmp .ps_guna_setlast
.ps_guna_newfirst:
    mov [rsp+8], rax          ; first_if = this_if
.ps_guna_setlast:
    mov [rsp], rax            ; last_if = this_if
    jmp .ps_guna_loop

.ps_guna_default:
    call advance_tok          ; consume 'anyatra'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ':'
    jne parse_error
    call advance_tok          ; consume ':'
    call parse_body           ; rax = default body
    mov r8, [rsp]             ; r8 = last_if
    test r8, r8
    jz .ps_guna_loop
    mov [r8+24], rax          ; last_if.else = default body
    jmp .ps_guna_loop

.ps_guna_done:
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '}'
    jne parse_error
    call advance_tok          ; consume '}'
    call maybe_semi
    mov rax, [rsp+8]          ; first_if
    add rsp, 24               ; clean up 3 pushes
    pop rbx
    ret

.ps_while:
    call advance_tok          ; consume 'yavat'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok
    call parse_expr           ; rax = condition
    mov rbx, rax              ; save condition
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ')'
    jne parse_error
    call advance_tok
    ; Parse body — braces optional
    call parse_body            ; rax = body
    push rax                  ; save body
    push rbx                  ; save condition
    call alloc_ast
    pop rbx                   ; condition
    pop rcx                   ; body
    mov qword [rax], AST_WHILE
    mov [rax+8], rbx          ; condition
    mov [rax+16], rcx         ; body
    pop rbx
    ret

.ps_do_while:
    ; kuru { body } yavat (condition) ;
    ; Sanskrit-only do-while form: body executes once before the test.
    call advance_tok          ; consume 'kuru'
    call parse_body           ; rax = body block
    push rax                  ; save body
    call cur_tok
    cmp qword [rax], TOK_KEYWORD
    jne parse_error
    cmp qword [rax+16], KW_YAVAT
    jne parse_error
    call advance_tok          ; consume 'yavat'
    call cur_tok
    cmp qword [rax+8], '('
    jne parse_error
    call advance_tok
    call parse_expr           ; rax = condition
    push rax                  ; save condition
    call cur_tok
    cmp qword [rax+8], ')'
    jne parse_error
    call advance_tok
    call maybe_semi
    call alloc_ast
    pop rcx                   ; condition
    pop rdx                   ; body
    mov qword [rax], AST_DO_WHILE
    mov [rax+8], rdx          ; body
    mov [rax+16], rcx         ; condition
    pop rbx
    ret

.ps_return:
    call advance_tok          ; consume 'pratiyati'
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .ps_ret_check_eof
    ; A delimiter means 'no value' only for ) } ; — a '(' starts an expression
    mov rcx, [rax+8]
    cmp rcx, ')'
    je .ps_ret_noexpr
    cmp rcx, '}'
    je .ps_ret_noexpr
    cmp rcx, ';'
    je .ps_ret_noexpr
    jmp .ps_ret_parse
.ps_ret_check_eof:
    cmp rcx, TOK_EOF
    je .ps_ret_noexpr
.ps_ret_parse:
    call parse_expr           ; rax = return value
    mov rbx, rax              ; save it
    jmp .ps_ret_build
.ps_ret_noexpr:
    xor rbx, rbx
.ps_ret_build:
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_RETURN
    mov [rax+8], rbx
    call maybe_semi
    pop rbx
    ret

.ps_rachana:
    ; rachana Name = { f1, f2, ... }
push r12                  ; save r12 (parse_func_block uses it)
    push r13                  ; save r13
    call advance_tok          ; consume 'rachana'
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_IDENT
    jne parse_error
    mov rbx, [rax+8]         ; rachana name ptr
    call advance_tok
    ; Expect '='
    call cur_tok
    cmp qword [rax+8], '='
    jne parse_error
    call advance_tok
    ; Expect '{'
    call cur_tok
    cmp qword [rax+8], '{'
    jne parse_error
    call advance_tok
    ; Register rachana
    mov rcx, [rel rachana_cnt]
    cmp rcx, RACHANA_CAP
    jae .pr_rachana_overflow
    lea rax, [rel rachana_defs]
    shl rcx, 8               ; 256 bytes per entry
    mov [rax + rcx], rbx     ; name ptr
    mov qword [rax + rcx + 8], 0  ; field count = 0
    ; Parse fields
    xor r12, r12             ; field count
.pr_field_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pr_field_name
    cmp qword [rax+8], '}'
    je .pr_field_done
    jmp parse_error
.pr_field_name:
    cmp r12, RACHANA_FIELDS_CAP
    jae .pr_rachana_fields_overflow
    mov rdx, [rax+8]         ; field name ptr
    call advance_tok
    ; Store field: [rachana_entry + 16 + field_count * 16] = name, +8 = offset
    lea rax, [rel rachana_defs]
    mov rcx, [rel rachana_cnt]
    shl rcx, 8
    ; offset = field_count * 8
    mov r8, r12
    shl r8, 3
    ; Compute store address manually (no *16 scale in NASM)
    mov r9, r12
    shl r9, 4               ; field_count * 16
    add r9, 16              ; + 16 (fields start at offset 16)
    add r9, rcx             ; + rachana base offset
    mov [rax + r9], rdx     ; field name ptr
    mov [rax + r9 + 8], r8  ; field offset
    inc r12
    ; Update field count
    mov [rax + rcx + 8], r12
    ; Check for comma
    call cur_tok
    cmp qword [rax+8], ','
    jne .pr_field_done
    call advance_tok
    jmp .pr_field_loop
.pr_field_done:
    call cur_tok
    cmp qword [rax+8], '}'
    jne parse_error
    call advance_tok
    inc qword [rel rachana_cnt]
    call maybe_semi
    call alloc_ast
    mov qword [rax], AST_HALT
    pop r13                  ; restore r13
    pop r12                  ; restore r12
    pop rbx
    ret
.pr_rachana_overflow:
    lea rdi, [rel msg_rachana_overflow]
    jmp capacity_fail
.pr_rachana_fields_overflow:
    lea rdi, [rel msg_rachana_fields_overflow]
    jmp capacity_fail

.ps_ayojan:
    ; ayojan module_name — Python-style import (documentation directive)
    call advance_tok
    call advance_tok
    pop rbx
    ret

.ps_check_expr:
    ; Could be assignment or expression statement
    call parse_expr           ; rax = left side
    mov rbx, rax              ; save it
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .ps_expr_done
    mov rcx, [rax+8]
    cmp rcx, '='
    jne .ps_check_compound
    ; Assignment: rbx = parse_expr
    call advance_tok          ; consume '='
    call parse_expr           ; rax = value
    ; Build assign node
    push rax                  ; save value
    push rbx                  ; save target
    call alloc_ast
    pop rbx                   ; target
    pop rcx                   ; value
    mov qword [rax], AST_ASSIGN
    mov [rax+8], rbx          ; target
    mov [rax+16], rcx         ; value
    call maybe_semi
    pop rbx
    ret
.ps_check_compound:
    ; Check for compound assignment operators += -= *= /= %=
    ; Also postfix ++ and --
    ; CRITICAL: r12 is parse_block's statement counter — save it!
    push r12
    cmp rcx, 0x2B2B          ; ++
    je .ps_incr
    cmp rcx, 0x2D2D          ; --
    je .ps_decr
    cmp rcx, 0x3D2B          ; +=
    je .ps_compound_add
    cmp rcx, 0x3D2D          ; -=
    je .ps_compound_sub
    cmp rcx, 0x3D2A          ; *=
    je .ps_compound_mul
    cmp rcx, 0x3D2F          ; /=
    je .ps_compound_div
    cmp rcx, 0x3D25          ; %=
    je .ps_compound_mod
    pop r12                  ; no match — restore and continue
    jmp .ps_expr_done
.ps_compound_add:
    mov r12, OP_ADD
    jmp .ps_do_compound
.ps_compound_sub:
    mov r12, OP_SUB
    jmp .ps_do_compound
.ps_compound_mul:
    mov r12, OP_MUL
    jmp .ps_do_compound
.ps_compound_div:
    mov r12, OP_DIV
    jmp .ps_do_compound
.ps_compound_mod:
    mov r12, OP_MOD
    jmp .ps_do_compound
.ps_incr:
    mov r12, OP_ADD
    jmp .ps_do_incdec
.ps_decr:
    mov r12, OP_SUB
    jmp .ps_do_incdec
.ps_do_incdec:
    ; rbx = target AST node, r12 = OP_ADD or OP_SUB
    ; x++ → x = x + 1 ;  x-- → x = x - 1
    call advance_tok          ; consume ++ or --
    ; Build NUM(1) node
    call alloc_ast
    mov qword [rax], 1        ; AST_NUM
    mov qword [rax+8], 1      ; value = 1
    mov r13, rax              ; r13 = rhs (NUM 1)
    ; Build binop node: [AST_BINOP][op][left=target][right=NUM(1)]
    call alloc_ast
    mov qword [rax], AST_BINOP
    mov [rax+8], r12          ; op
    mov [rax+16], rbx         ; left = target
    mov [rax+24], r13         ; right = 1
    mov r14, rax              ; r14 = binop
    ; Build assign node: [AST_ASSIGN][target][value=binop]
    call alloc_ast
    mov qword [rax], AST_ASSIGN
    mov [rax+8], rbx          ; target
    mov [rax+16], r14         ; value = binop
    call maybe_semi
    pop r12
    pop rbx
    ret
.ps_do_compound:
    ; rbx = target AST node, r12 = operator id
    ; Desugar: target op= rhs  →  target = target op rhs
    call advance_tok          ; consume the compound operator
    call parse_expr           ; rax = rhs (rbx, r12 preserved)
    mov r13, rax              ; r13 = rhs
    ; Build binop node: [AST_BINOP][op][left=target][right=rhs]
    call alloc_ast            ; rax = binop node (rbx preserved)
    mov qword [rax], AST_BINOP
    mov [rax+8], r12          ; op
    mov [rax+16], rbx         ; left = target
    mov [rax+24], r13         ; right = rhs
    mov r14, rax              ; r14 = binop node
    ; Build assign node: [AST_ASSIGN][target][value=binop]
    call alloc_ast            ; rax = assign node
    mov qword [rax], AST_ASSIGN
    mov [rax+8], rbx          ; target
    mov [rax+16], r14         ; value = binop
    call maybe_semi
    pop r12                  ; restore parse_block's statement counter
    pop rbx
    ret

.ps_expr_done:
    call maybe_semi
    mov rax, rbx
    pop rbx
    ret

maybe_semi:
    push rax
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .ms_done
    mov rcx, [rax+8]
    cmp rcx, ';'
    jne .ms_done
    call advance_tok
.ms_done:
    pop rax
    ret

; ============================================================
; EXPRESSION PARSING
; ============================================================
; Simple single-level: additive (op additive)*
; This avoids complex precedence for now.

parse_expr:
    ; Top-level: ternary ?: (lower precedence than ||, right-associative)
    push rbx
    push r12
    push r13
    push r14
    call parse_ternary
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_ternary() -> rax = AST node
; conditional := logical_or ('?' expression ':' conditional)?
parse_ternary:
    push rbx
    push r12
    push r13
    call parse_lor
    mov rbx, rax              ; condition / ordinary expression
    call cur_tok
    cmp qword [rax], TOK_DELIMITER
    jne .pt_done
    cmp qword [rax+8], '?'
    jne .pt_done
    call advance_tok          ; consume '?'
    call parse_expr           ; true branch; ':' naturally terminates it
    mov r12, rax
    call cur_tok
    cmp qword [rax], TOK_DELIMITER
    jne parse_error
    cmp qword [rax+8], ':'
    jne parse_error
    call advance_tok          ; consume ':'
    call parse_ternary        ; false branch: right-associative
    mov r13, rax
    push rbx
    push r12
    push r13
    call alloc_ast
    pop r13
    pop r12
    pop rbx
    mov qword [rax], AST_TERNARY
    mov [rax+8], rbx
    mov [rax+16], r12
    mov [rax+24], r13
    mov rbx, rax
.pt_done:
    mov rax, rbx
    pop r13
    pop r12
    pop rbx
    ret

; parse_lor() -> rax = AST node
; Handles || (logical OR)
parse_lor:
    push rbx
    push r12
    push r13
    push r14
    call parse_land
    mov rbx, rax              ; left
.lor_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .lor_done
    mov rcx, [rax+8]
    cmp rcx, 0x7C7C           ; ||
    jne .lor_done
    mov r12, OP_LOR
    call advance_tok
    call parse_land           ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    mov rbx, rax
    jmp .lor_loop
.lor_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_land() -> rax = AST node
; Handles && (logical AND)
parse_land:
    push rbx
    push r12
    push r13
    push r14
    call parse_cmp
    mov rbx, rax              ; left
.land_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .land_done
    mov rcx, [rax+8]
    cmp rcx, 0x2626           ; &&
    jne .land_done
    mov r12, OP_LAND
    call advance_tok
    call parse_cmp            ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    mov rbx, rax
    jmp .land_loop
.land_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_cmp() -> rax = AST node
; Handles ==, !=, <, >, <=, >=
parse_cmp:
    push rbx
    push r12
    push r13
    push r14
    call parse_bitor
    mov rbx, rax              ; left
.cmp_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .cmp_done
    mov rcx, [rax+8]
    cmp rcx, 0x3D3D           ; ==
    je .c_eq
    cmp rcx, 0x3D21           ; !=
    je .c_ne
    cmp rcx, 0x3D3C           ; <=
    je .c_le
    cmp rcx, 0x3D3E           ; >=
    je .c_ge
    cmp rcx, '<'
    je .c_lt
    cmp rcx, '>'
    je .c_gt
    jmp .cmp_done
.c_eq:
    mov r12, OP_EQ
    jmp .c_do
.c_ne:
    mov r12, OP_NE
    jmp .c_do
.c_le:
    mov r12, OP_LE
    jmp .c_do
.c_ge:
    mov r12, OP_GE
    jmp .c_do
.c_lt:
    mov r12, OP_LT
    jmp .c_do
.c_gt:
    mov r12, OP_GT
.c_do:
    call advance_tok
    call parse_bitor            ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    mov rbx, rax
    jmp .cmp_loop
.cmp_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_add() → rax = AST node
; Handles + and -
; parse_bitor() -> rax = AST node
parse_bitor:
    push rbx
    push r12
    push r13
    push r14
    call parse_bitxor
    mov rbx, rax              ; left
.bor_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .bor_done
    mov rcx, [rax+8]
    cmp rcx, 0x7C
    je .bor_take
    jmp .bor_done
.bor_take:
    mov r12, OP_OR
    call advance_tok
    call parse_bitxor               ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    mov rdi, rax
    call fold_const
    mov rbx, rax
    jmp .bor_loop
.bor_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_bitxor() -> rax = AST node
parse_bitxor:
    push rbx
    push r12
    push r13
    push r14
    call parse_bitand
    mov rbx, rax              ; left
.bxor_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .bxor_done
    mov rcx, [rax+8]
    cmp rcx, '^'
    je .bxor_take
    jmp .bxor_done
.bxor_take:
    mov r12, OP_XOR
    call advance_tok
    call parse_bitand               ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    mov rdi, rax
    call fold_const
    mov rbx, rax
    jmp .bxor_loop
.bxor_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_bitand() -> rax = AST node
parse_bitand:
    push rbx
    push r12
    push r13
    push r14
    call parse_shift
    mov rbx, rax              ; left
.band_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .band_done
    mov rcx, [rax+8]
    cmp rcx, 0x26
    je .band_take
    jmp .band_done
.band_take:
    mov r12, OP_AND
    call advance_tok
    call parse_shift               ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    mov rdi, rax
    call fold_const
    mov rbx, rax
    jmp .band_loop
.band_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_shift() -> rax = AST node   (<< and >> bind looser than + -, tighter than comparisons)
parse_shift:
    push rbx
    push r12
    push r13
    push r14
    call parse_add
    mov rbx, rax              ; left
.sh_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .sh_done
    mov rcx, [rax+8]
    cmp rcx, 0x3C3C           ; <<
    je .sh_left
    cmp rcx, 0x3E3E           ; >>
    je .sh_right
    jmp .sh_done
.sh_left:
    mov r12, OP_SHL
    jmp .sh_go
.sh_right:
    mov r12, OP_SHR
.sh_go:
    call advance_tok
    call parse_add            ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    mov rbx, rax
    jmp .sh_loop
.sh_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

parse_add:
    push rbx
    push r12
    push r13
    push r14
    call parse_mul
    mov rbx, rax              ; left
.add_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .add_done
    mov rcx, [rax+8]
    cmp rcx, '+'
    je .a_add
    cmp rcx, '-'
    je .a_sub
    jmp .add_done
.a_add:
    mov r12, OP_ADD
    jmp .a_do
.a_sub:
    mov r12, OP_SUB
.a_do:
    call advance_tok
    call parse_mul            ; rax = right
    mov r13, rax              ; save right
    mov r14, r12              ; save op
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    ; --- Constant folding ---
    ; If both operands are AST_NUM, compute result now
    mov rdi, rax              ; BINOP node
    call fold_const           ; rax = folded node (or unchanged)
    mov rbx, rax
    jmp .add_loop
.add_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; parse_mul() → rax = AST node
; Handles * and /
parse_mul:
    push rbx
    push r12
    push r13
    push r14
    call parse_primary
    mov rbx, rax              ; left
.mul_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_OPERATOR
    jne .mul_done
    mov rcx, [rax+8]
    cmp rcx, '*'
    je .m_mul
    cmp rcx, '/'
    je .m_div
    cmp rcx, '%'
    je .m_mod
    jmp .mul_done
.m_mul:
    mov r12, OP_MUL
    jmp .m_do
.m_div:
    mov r12, OP_DIV
    jmp .m_do
.m_mod:
    mov r12, OP_MOD
.m_do:
    call advance_tok
    call parse_primary        ; rax = right
    mov r13, rax
    mov r14, r12
    push rbx
    push r14
    push r13
    call alloc_ast
    pop r13
    pop r14
    pop rbx
    mov qword [rax], AST_BINOP
    mov [rax+8], r14
    mov [rax+16], rbx
    mov [rax+24], r13
    ; --- Constant folding ---
    mov rdi, rax              ; BINOP node
    call fold_const           ; rax = folded node (or unchanged)
    mov rbx, rax
    jmp .mul_loop
.mul_done:
    mov rax, rbx
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; fold_const(rdi = BINOP node) -> rax = folded AST_NUM or original node
; If both operands are AST_NUM, compute the result at compile time
fold_const:
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rdi              ; rbx = BINOP node
    ; Check that node type is AST_BINOP (3)
    mov rax, [rbx]
    cmp rax, AST_BINOP
    jne .fc_return            ; not a binop, return as-is
    ; Get left and right operands
    mov r12, [rbx+16]         ; left node
    mov r13, [rbx+24]         ; right node
    ; --- Compile-time string concatenation: "a"+"b", "a"+42, 42+"a" ---
    mov rax, [rbx+8]         ; operator
    cmp rax, OP_ADD
    jne .fc_no_strcat
    mov rax, [r12]
    cmp rax, AST_STR
    je .fc_sc_left
    mov rax, [r13]
    cmp rax, AST_STR
    je .fc_sc_right
    jmp .fc_no_strcat
.fc_sc_left:
    mov rax, [r13]
    cmp rax, AST_STR
    je .fc_sc_both
    cmp rax, AST_NUM
    je .fc_sc_str_num
    jmp .fc_return
.fc_sc_right:
    mov rax, [r12]
    cmp rax, AST_NUM
    je .fc_sc_num_str
    jmp .fc_return
.fc_no_strcat:
    ; Check left is AST_NUM (1)
    mov rax, [r12]
    cmp rax, AST_NUM
    jne .fc_return
    ; Check right is AST_NUM (1)
    mov rax, [r13]
    cmp rax, AST_NUM
    jne .fc_return
    ; Both are numbers! Get values
    mov r14, [rbx+8]          ; operator
    mov rax, [r12+8]          ; left value
    mov rcx, [r13+8]          ; right value
    ; Compute based on operator
    cmp r14, OP_ADD
    je .fc_add
    cmp r14, OP_SUB
    je .fc_sub
    cmp r14, OP_MUL
    je .fc_mul
    cmp r14, OP_DIV
    je .fc_div
    cmp r14, OP_MOD
    je .fc_mod
    cmp r14, OP_AND
    je .fc_and
    cmp r14, OP_OR
    je .fc_or
    cmp r14, OP_XOR
    je .fc_xor
    jmp .fc_return            ; unknown op, return as-is
.fc_add:
    add rax, rcx
    jmp .fc_make
.fc_sub:
    sub rax, rcx
    jmp .fc_make
.fc_mul:
    imul rax, rcx
    jmp .fc_make
.fc_div:
    test rcx, rcx
    jz .fc_return             ; division by zero, return as-is
    xor rdx, rdx
    cqo
    idiv rcx
    jmp .fc_make
.fc_mod:
    test rcx, rcx
    jz .fc_return
    xor rdx, rdx
    cqo
    idiv rcx
    mov rax, rdx            ; remainder
    jmp .fc_make
.fc_and:
    and rax, rcx
    jmp .fc_make
.fc_or:
    or rax, rcx
    jmp .fc_make
.fc_xor:
    xor rax, rcx
    jmp .fc_make
.fc_make:
    ; Create a new AST_NUM node with the computed value
    push rax
    call alloc_ast
    pop rcx
    mov qword [rax], AST_NUM
    mov [rax+8], rcx          ; value
    jmp .fc_done

.fc_sc_both:
    mov rdi, [rel str_ptr]
    mov rsi, [r12+8]         ; left string
    call fc_copy_str
    mov rsi, [r13+8]         ; right string
    call fc_copy_str
    mov byte [rdi], 0        ; final null
    inc rdi
    mov r14, [rel str_ptr]
    mov [rel str_ptr], rdi
    call fc_make_str
    jmp .fc_done
.fc_sc_num_str:
    mov rdi, [rel str_ptr]
    mov rax, [r12+8]         ; number value
    call fc_num_to_str       ; rdi = past digits
    mov rsi, [r13+8]         ; right string
    call fc_copy_str
    mov byte [rdi], 0
    inc rdi
    mov r14, [rel str_ptr]
    mov [rel str_ptr], rdi
    call fc_make_str
    jmp .fc_done
.fc_sc_str_num:
    mov rdi, [rel str_ptr]
    mov rsi, [r12+8]         ; left string
    call fc_copy_str         ; rdi at the null after left
    mov rax, [r13+8]         ; number value
    call fc_num_to_str       ; digits written at rdi
    mov byte [rdi], 0
    inc rdi
    mov r14, [rel str_ptr]
    mov [rel str_ptr], rdi
    call fc_make_str
    jmp .fc_done

.fc_return:
    mov rax, rbx              ; return original node
.fc_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; fc_num_to_str: rax = signed number, rdi = dest
; writes decimal digits at rdi; returns rdi = past last digit
fc_num_to_str:
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rdi             ; save dest base
    mov r12, rdi             ; write pos
    test rax, rax
    jns .fns_pos
    neg rax
    mov byte [r12], '-'
    inc r12
.fns_pos:
    mov r13, r12
    add r13, 24              ; rightmost digit pos
    mov r14, r13
.fns_loop:
    xor edx, edx
    mov rcx, 10
    div rcx
    add dl, '0'
    dec r13
    mov [r13], dl
    test rax, rax
    jnz .fns_loop
    ; compact: move [r13..r14) to [r12..)
    mov rsi, r13
    mov rdi, r12
.fns_move:
    cmp rsi, r14
    jae .fns_done
    mov al, [rsi]
    mov [rdi], al
    inc rsi
    inc rdi
    jmp .fns_move
.fns_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; fc_copy_str(rsi = src) -> copies null-terminated string to [rdi]
; on return rdi points AT the null (so a following copy overwrites it)
fc_copy_str:
    push rax
.fcs_loop:
    mov al, [rsi]
    mov [rdi], al
    inc rsi
    inc rdi
    test al, al
    jnz .fcs_loop
    dec rdi
    pop rax
    ret

; fc_make_str(r14 = string ptr) -> rax = new AST_STR node
fc_make_str:
    push r14
    call alloc_ast
    pop rcx
    mov qword [rax], AST_STR
    mov [rax+8], rcx
    ret

; parse_primary() → rax = AST node
parse_primary:
    push rbx
    call cur_tok
    mov rcx, [rax]            ; token type
    cmp rcx, TOK_EOF          ; ran out of input mid-expression -> diagnostic
    jne .pp_not_eof
    pop rbx
    jmp parse_error
.pp_not_eof:
    ; Check for unary minus: -expr
    cmp rcx, TOK_OPERATOR
    jne .pp_check_kw
    mov rcx, [rax+8]
    cmp rcx, '-'
    jne .pp_check_delim
    ; Unary minus — consume '-' and parse the following expression
    call advance_tok          ; consume '-'
    call parse_primary        ; rax = inner expr
    ; Check if inner is a constant number — if so, negate directly
    mov rcx, [rax]
    cmp rcx, AST_FLOAT
    je .pp_neg_float
    cmp rcx, AST_NUM
    jne .pp_neg_expr
    ; Negate constant
    mov rcx, [rax+8]
    neg rcx
    mov [rax+8], rcx
    pop rbx
    ret
.pp_neg_float:
    ; IEEE-754 sign bit toggle for a literal.
    btc qword [rax+8], 63
    pop rbx
    ret
.pp_neg_expr:
    ; Create BINOP(0 - expr): [AST_BINOP][OP_SUB][AST_NUM(0)][expr]
    ; rax = inner expr, rbx is already pushed by parse_primary entry
    push rax                  ; save expr on stack
    call alloc_ast            ; rax = new node for AST_NUM(0)
    mov qword [rax], AST_NUM
    mov qword [rax+8], 0
    push rax                  ; save AST_NUM(0) on stack
    call alloc_ast            ; rax = new node for BINOP
    pop rcx                   ; rcx = AST_NUM(0) (left)
    pop rdx                   ; rdx = expr (right)
    mov qword [rax], AST_BINOP
    mov qword [rax+8], OP_SUB
    mov [rax+16], rcx         ; left = 0
    mov [rax+24], rdx         ; right = expr
    pop rbx
    ret

.pp_check_kw:
    ; Check for purna/shunya (true/false)
    cmp rcx, TOK_KEYWORD
    jne .pp_check_delim
    mov rdx, [rax+16]        ; keyword ID (rax = token ptr from cur_tok)
    cmp rdx, KW_PURNA
    jne .pp_check_shunya
    ; purna: return AST_NUM(1)
    call advance_tok          ; consume 'purna'
    push 1
    call alloc_ast
    pop rcx
    mov qword [rax], AST_NUM
    mov qword [rax+8], 1
    pop rbx
    ret
.pp_check_shunya:
    cmp rdx, KW_SHUNYA
    jne .pp_check_delim
    call advance_tok          ; consume 'shunya'
    push 0
    call alloc_ast
    pop rcx
    mov qword [rax], AST_NUM
    mov qword [rax+8], 0
    pop rbx
    ret

.pp_check_delim:
    cmp rcx, TOK_DELIMITER
    jne .pp_str
    mov rcx, [rax+8]
    ; Parenthesized expression: ( expr )
    cmp rcx, '('
    je .pp_paren
    cmp rcx, '['
    jne .pp_str
    jmp .pp_vector_lit
.pp_paren:
    call advance_tok          ; consume '('
    call parse_expr           ; rax = inner expression
    push rax                  ; SAVE result (cur_tok clobbers rax!)
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ')'
    jne parse_error
    call advance_tok          ; consume ')'
    pop rax                   ; RESTORE result
    pop rbx
    ret
.pp_vector_lit:
    ; VECTOR LITERAL [n1, n2, n3, n4]
    call advance_tok          ; consume '['
    ; Parse 4 numbers
    push r12
    push r13
    push r14
    xor r12, r12              ; element count
    mov r13, 0                ; accumulator for values
.pv_loop:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_NUMBER
    jne .pv_done
    mov rax, [rax+8]          ; value
    ; Store in AST_VEC node fields
    push rax
    inc r12
    call advance_tok
    ; Check for comma
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ','
    jne .pv_check_end
    call advance_tok          ; consume comma
    jmp .pv_loop
.pv_check_end:
    cmp r12, 4
    jge .pv_done
    jmp .pv_loop
.pv_done:
    ; AST_VEC has exactly four payload slots.  Older code always popped four
    ; values even when fewer were parsed, corrupting the parser stack (for
    ; example: vitti a = [1, 2, 3]) and eventually segfaulting the compiler.
    ; Reject any non-4-wide literal cleanly before touching the saved stack.
    cmp r12, 4
    jne parse_error
    ; Expect ']'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ']'
    jne parse_error
    call advance_tok          ; consume ']'
    ; Create AST_VEC node with 4 values on stack
    ; Pop values in reverse order
    call alloc_ast
    mov qword [rax], AST_VEC
    ; Pop 4 values (reverse order)
    pop rcx                   ; val4
    mov [rax+40], rcx
    pop rcx                   ; val3
    mov [rax+32], rcx
    pop rcx                   ; val2
    mov [rax+24], rcx
    pop rcx                   ; val1
    mov [rax+16], rcx
    mov [rax+8], r12          ; count
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.pp_str:
    ; STRING
    cmp rcx, TOK_STRING
    jne .pp_num
    mov rbx, [rax+8]         ; string pointer
    call advance_tok
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_STR
    mov [rax+8], rbx         ; string ptr
    pop rbx
    ret

.pp_num:
    ; NUMBER / T12 FLOAT
    cmp rcx, TOK_FLOAT
    je .pp_float
    cmp rcx, TOK_NUMBER
    jne .pp_ident
    mov rbx, [rax+8]         ; numeric value
    call advance_tok
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_NUM
    mov [rax+8], rbx         ; value
    pop rbx
    ret
.pp_float:
    mov rbx, [rax+8]         ; raw IEEE-754 binary64 bits
    call advance_tok
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_FLOAT
    mov [rax+8], rbx
    pop rbx
    ret

.pp_ident:
    cmp rcx, TOK_IDENT
    jne .pp_builtin
    mov rbx, [rax+8]         ; name ptr
    ; Resolve previously declared top-level sutra symbols before building an
    ; AST_VAR. Compile-time inlining works inside functions without a global
    ; data section or cross-function variable lifetime.
    xor r8, r8
.pp_top_const:
    cmp r8, [rel top_const_count]
    jae .pp_not_top_const
    lea rdx, [rel top_const_nodes]
    mov rax, [rdx + r8*8]
    mov rdi, rbx
    mov rsi, [rax+8]
    push r8
    call strcmp
    pop r8
    test rax,rax
    jz .pp_found_top_const
    inc r8
    jmp .pp_top_const
.pp_found_top_const:
    lea rdx, [rel top_const_nodes]
    mov rax, [rdx + r8*8]
    mov rax, [rax+16]        ; initializer AST, immutable read-only use
    push rax
    call advance_tok
    pop rax
    pop rbx
    ret
.pp_not_top_const:
    call advance_tok
    ; Check if next token is '(' → function call
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pp_ident_var
    mov rcx, [rax+8]
    cmp rcx, '('
    je .pp_ident_call
    cmp rcx, '['
    je .pp_ident_index
    cmp rcx, '.'
    je .pp_ident_field
.pp_ident_var:
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_VAR
    mov [rax+8], rbx
    pop rbx
    ret
.pp_ident_field:
    ; Field access: ident.field
    call advance_tok          ; consume '.'
    call cur_tok
    cmp qword [rax], TOK_IDENT
    jne parse_error
    mov rdx, [rax+8]         ; field name ptr
    call advance_tok          ; consume field name
    push rbx                 ; save var name
    push rdx                 ; save field name
    ; Search rachana entries for this field
    xor r8, r8
.pif_search:
    cmp r8, [rel rachana_cnt]
    jae .pif_notfound
    lea r9, [rel rachana_defs]
    mov r10, r8
    shl r10, 8
    add r9, r10              ; r9 = entry base
    mov r10, [r9 + 8]        ; field count
    xor r11, r11
.pif_fields:
    cmp r11, r10
    jae .pif_next
    ; Compare field name (simple: compare first 2 chars)
    mov rax, r11
    shl rax, 4
    mov rdi, [r9 + 16 + rax] ; field name ptr from rachana table
    ; Compare byte-by-byte without strcmp
    ; rdi = table field name, rdx = search field name
    movzx rax, byte [rdi]
    movzx rcx, byte [rdx]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    movzx rax, byte [rdi+1]
    movzx rcx, byte [rdx+1]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    movzx rax, byte [rdi+2]
    movzx rcx, byte [rdx+2]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    movzx rax, byte [rdi+3]
    movzx rcx, byte [rdx+3]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    movzx rax, byte [rdi+4]
    movzx rcx, byte [rdx+4]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    movzx rax, byte [rdi+5]
    movzx rcx, byte [rdx+5]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    movzx rax, byte [rdi+6]
    movzx rcx, byte [rdx+6]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    movzx rax, byte [rdi+7]
    movzx rcx, byte [rdx+7]
    cmp al, cl
    jne .pif_no_match
    cmp al, 0
    je .pif_found
    ; More than 8 chars - assume match
    jmp .pif_found
.pif_no_match:
    inc r11
    jmp .pif_fields
.pif_next:
    inc r8
    jmp .pif_search
.pif_found:
    ; Get field offset
    mov rax, r11
    shl rax, 4
    mov rdx, [r9 + 16 + rax + 8]  ; field offset
    pop rax                  ; discard saved field name
    pop rbx                  ; restore var name
    push rbx
    push rdx
    call alloc_ast
    pop rdx
    pop rbx
    mov qword [rax], AST_FIELD
    mov [rax+8], rbx         ; var name
    mov [rax+16], rdx        ; field offset
    pop rbx
    ret
.pif_notfound:
    pop rax                  ; discard saved field name
    pop rbx                  ; restore var name
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_FIELD
    mov [rax+8], rbx
    mov qword [rax+16], 0
    pop rbx
    ret

.pp_ident_index:
    ; Array index: ident[expr]
    call advance_tok          ; consume '['
    ; Save name ptr
    push rbx
    ; Parse index expression
    call parse_expr
    ; rax = index node
    push rax                  ; save index
    ; Expect ']'
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, ']'
    jne parse_error
    call advance_tok          ; consume ']'
    ; Create AST_INDEX node: [AST_INDEX][name_ptr][index_node]
    pop rcx                   ; index node
    pop rdx                   ; name ptr (was rbx, now in rdx)
    push rdx                  ; save name
    push rcx                  ; save index
    call alloc_ast
    pop rcx                   ; index
    pop rdx                   ; name
    mov qword [rax], AST_INDEX
    mov [rax+8], rdx          ; name ptr
    mov [rax+16], rcx         ; index node
    pop rbx
    ret

.pp_ident_call:
    ; Function call: name(args)
    call advance_tok          ; consume '('
    push r12                  ; save r12 (parse_func_block uses it)
    xor r12, r12             ; arg count
.pp_ic_args:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pp_ic_parse
    mov rcx, [rax+8]
    cmp rcx, ')'
    je .pp_ic_done
.pp_ic_parse:
    cmp r12, 6
    jb .pp_ic_parse_ok
    mov qword [rel parse_error_kind], 1
    jmp parse_error
.pp_ic_parse_ok:
    call parse_expr
    push rax                 ; stash arg (nest-safe)
    inc r12
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pp_ic_args
    mov rcx, [rax+8]
    cmp rcx, ','
    jne .pp_ic_args
    call advance_tok
    jmp .pp_ic_args
.pp_ic_done:
    call advance_tok          ; consume ')'
    ; Build funcall node: [AST_FUNCALL][name_ptr][arg_count][arg1..arg6]
    push rbx
    push r12
    call alloc_ast
    pop r12
    pop rbx
    mov qword [rax], AST_FUNCALL
    mov [rax+8], rbx          ; function name
    mov [rax+16], r12         ; arg count
    ; pop stashed args (pushed in order) into node slots in reverse
    mov rcx, r12
    test rcx, rcx
    jz .pp_no_pop_f
    lea rdx, [rax + 24]
    mov r8, r12
    dec r8
    shl r8, 3
    add rdx, r8
.pp_pop_f:
    pop r8
    mov [rdx], r8
    sub rdx, 8
    dec rcx
    jnz .pp_pop_f
.pp_no_pop_f:
    pop r12                   ; restore r12
    pop rbx
    ret

.pp_builtin:
    cmp rcx, TOK_BUILTIN
    je .pp_builtin_valid
    ; Check mode must reject stray ';', ']', ',' and other tokens here.
    ; The legacy fallback treated every unsupported primary as '(' and
    ; accidentally consumed tokens in later malformed declarations.
    ; Preserve historical non-check compilation behavior unchanged.
    cmp qword [rel r48_mode], 0
    jne parse_error
    jmp .pp_paren
.pp_builtin_valid:
    mov rbx, [rax+16]        ; builtin id
    call advance_tok          ; consume builtin name
    ; expect (
    call cur_tok
    mov rcx, [rax+8]
    cmp rcx, '('
    jne parse_error
    call advance_tok
    ; Parse args
    push r12                  ; save r12 (parse_func_block uses it)
    xor r12, r12             ; arg count
.pp_args:
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pp_arg_parse
    mov rcx, [rax+8]
    cmp rcx, ')'
    je .pp_args_done
.pp_arg_parse:
    call parse_expr          ; rax = arg
    push rax                 ; stash arg (nest-safe; call_args would be clobbered)
    inc r12
    ; Check comma
    call cur_tok
    mov rcx, [rax]
    cmp rcx, TOK_DELIMITER
    jne .pp_args
    mov rcx, [rax+8]
    cmp rcx, ','
    jne .pp_args
    call advance_tok          ; consume comma
    jmp .pp_args
.pp_args_done:
    call advance_tok          ; consume )
    ; Build node based on builtin
    cmp rbx, BN_STHAGITA
    je .pp_halt
    cmp rbx, BN_LIKH
    je .pp_writemem
    ; Generic call
    push rbx
    push r12
    call alloc_ast
    pop r12
    pop rbx
    mov qword [rax], 8       ; AST_CALL
    mov [rax+8], rbx          ; builtin id
    mov [rax+16], r12         ; arg count
    ; pop stashed args (pushed in order) into node slots in reverse
    mov rcx, r12
    test rcx, rcx
    jz .pp_no_pop_b
    lea rdx, [rax + 24]
    mov r8, r12
    dec r8
    shl r8, 3
    add rdx, r8
.pp_pop_b:
    pop r8
    mov [rdx], r8
    sub rdx, 8
    dec rcx
    jnz .pp_pop_b
.pp_no_pop_b:
    pop r12                   ; restore r12
    pop rbx
    ret

.pp_halt:
    push rbx
    call alloc_ast
    pop rbx
    mov qword [rax], AST_HALT
    pop r12                   ; restore r12
    pop rbx
    ret

.pp_writemem:
    push rbx
    push r12
    call alloc_ast
    pop r12
    pop rbx
    mov qword [rax], AST_WRITEMEM
    mov [rax+8], r12          ; arg count
    lea rdx, [rel call_args]
    mov rcx, [rdx]            ; arg1 (address)
    mov [rax+16], rcx
    mov rcx, [rdx+8]         ; arg2 (value)
    mov [rax+24], rcx
    pop r12                   ; restore r12
    pop rbx
    ret

; ============================================================
; CODE GENERATOR
; ============================================================
; Emits x86-64 machine code into code_buf.
; Stack-based: every expression leaves result in RAX.


; emit_syscall — Linux: the 2-byte syscall instruction.
;                Windows: a call into the embedded runtime shim (patched later).
emit_syscall:
    cmp qword [rel target_pe], 0
    jne .es_pe
    ; Linux target: the 2-byte syscall instruction
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x05
    call emit_byte
    ret
.es_pe:
    ; Windows target: call into the embedded runtime shim (patched later)
    mov dil, 0xE8
    call emit_byte
    mov rax, [rel code_sz]          ; position of the rel32 field
    lea rcx, [rel blob_calls]
    mov rdx, [rel blob_call_cnt]
    shl rdx, 3
    mov [rcx + rdx], rax
    inc qword [rel blob_call_cnt]
    xor edi, edi
    call emit_u32
    ret

emit_byte:
    ; dil = byte to emit
    push rbx
    mov rbx, [rel code_sz]
    cmp rbx, CODE_BUF_CAP
    jae .emit_byte_overflow
    lea rcx, [rel code_buf]
    mov [rcx + rbx], dil
    inc rbx
    mov [rel code_sz], rbx
    pop rbx
    ret
.emit_byte_overflow:
    pop rbx
    lea rdi, [rel msg_code_overflow]
    jmp capacity_fail

emit_u32:
    ; edi = 32-bit value
    push rbx
    mov ebx, edi
    movzx edi, bl
    call emit_byte
    shr ebx, 8
    movzx edi, bl
    call emit_byte
    shr ebx, 8
    movzx edi, bl
    call emit_byte
    shr ebx, 8
    movzx edi, bl
    call emit_byte
    pop rbx
    ret

emit_u64:
    ; rdi = 64-bit value
    push rbx
    push rdi
    mov rbx, rdi
    ; low 32 bits
    mov edi, ebx
    call emit_u32
    ; high 32 bits
    shr rbx, 32
    mov edi, ebx
    call emit_u32
    pop rdi
    pop rbx
    ret

gen_code:
    push rbx
    push r12
    push r13
    push r14
    push r15
    ; T12: establish prakriya return metadata before main call sites are typed.
    call classify_float_functions
    ; PE target: call the embedded runtime's rt_init first (the blob sits
    ; at image offset 0, so this call is always exactly 5 bytes back)
    cmp qword [rel target_pe], 0
    je .gc_no_rtinit
    mov dil, 0xE8
    call emit_byte
    mov edi, -(RT_BLOB_LEN + 5)      ; call back to the blob at image offset 0
    call emit_u32
.gc_no_rtinit:
    ; Init variable table
    mov qword [rel var_cnt], 0
    mov qword [rel stack_dep], 0
    mov qword [rel array_var_cnt], 0
    mov qword [rel kosh_var_cnt], 0
    mov qword [rel kosh_param_var_cnt], 0
    mov qword [rel float_kosh_var_cnt], 0
    mov qword [rel float_var_cnt], 0
    ; Do NOT reset func_def_cnt — it may have FUNCDEF nodes from top-level parsing
    mov qword [rel patch_count], 0
    mov qword [rel func_count], 0
    mov qword [rel blob_call_cnt], 0
    mov qword [rel in_function], 0
    mov qword [rel current_func_float], 0

    ; Get function body (block node)
    mov rax, [rel root_node]
    mov rax, [rax+8]          ; body = block node

    ; Function prologue: push rbp; push callee-saved; mov rbp, rsp
    mov dil, 0x55             ; push rbp
    call emit_byte
    mov dil, 0x48             ; push rbx
    call emit_byte
    mov dil, 0x53
    call emit_byte
    mov dil, 0x41             ; push r12
    call emit_byte
    mov dil, 0x54
    call emit_byte
    mov dil, 0x41             ; push r13
    call emit_byte
    mov dil, 0x55
    call emit_byte
    mov dil, 0x41             ; push r14
    call emit_byte
    mov dil, 0x56
    call emit_byte
    mov dil, 0x41             ; push r15
    call emit_byte
    mov dil, 0x57
    call emit_byte
    mov dil, 0x48             ; mov rbp, rsp
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xE5
    call emit_byte
    ; Reserve a stable spill area so stack locals survive generated calls.
    ; sub rsp, FUNC_SPILL_BYTES = 48 81 EC imm32
    mov dil, 0x48
    call emit_byte
    mov dil, 0x81
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov edi, FUNC_SPILL_BYTES
    call emit_u32

    ; Generate body
    call gen_block

    ; Function epilogue: mov rsp,rbp; pop callee-saved; pop rbp; sys_exit
    mov dil, 0x48             ; mov rsp, rbp
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov dil, 0x41             ; pop r15
    call emit_byte
    mov dil, 0x5F
    call emit_byte
    mov dil, 0x41             ; pop r14
    call emit_byte
    mov dil, 0x5E
    call emit_byte
    mov dil, 0x41             ; pop r13
    call emit_byte
    mov dil, 0x5D
    call emit_byte
    mov dil, 0x41             ; pop r12
    call emit_byte
    mov dil, 0x5C
    call emit_byte
    mov dil, 0x5B             ; pop rbx
    call emit_byte
    mov dil, 0x5D             ; pop rbp
    call emit_byte
    ; sys_exit(0): mov rax,60; xor rdi,rdi; syscall
    mov dil, 0x48
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    mov edi, 60
    call emit_u32
    xor edi, edi
    call emit_u32
    mov dil, 0x48
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    call emit_syscall

    ; Generate all function bodies after main
    call gen_all_functions
    mov qword [rel in_function], 0   ; back in main context
    mov qword [rel current_func_float], 0
    ; Backpatch all call sites
    call backpatch_calls

    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; funcdef_name_exists(rdi=name ptr) -> rax=1 if a collected definition
; already owns this name.  Used by T4 module collision checks.
funcdef_name_exists:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    xor r12, r12
    mov r13, [rel func_def_cnt]
.fdne_loop:
    cmp r12, r13
    jae .fdne_no
    lea rcx, [rel func_defs]
    mov rcx, [rcx + r12*8]
    mov rdi, rbx
    mov rsi, [rcx+8]
    call strcmp
    test rax, rax
    jz .fdne_yes
    inc r12
    jmp .fdne_loop
.fdne_yes:
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.fdne_no:
    xor rax, rax
    pop r13
    pop r12
    pop rbx
    ret

; gen_all_functions — emit code for all collected FUNCDEF nodes
gen_all_functions:
    push rbx
    push r12
    push r13
    push r14
    xor r12, r12              ; index
.gaf_loop:
    cmp r12, [rel func_def_cnt]
    jae .gaf_done
    ; Get FUNCDEF node
    lea rax, [rel func_defs]
    mov rbx, [rax + r12*8]   ; rbx = FUNCDEF node
    mov rax, [rbx+40]        ; T12 inferred return type
    mov [rel current_func_float], rax
    ; Register function address in func_table
    mov rdx, [rel func_count]
    cmp rdx, FUNC_TABLE_CAP
    jae .gaf_func_table_overflow
    lea rcx, [rel func_table]
    push rdx
    shl rdx, 4
    mov rax, [rbx+8]
    mov [rcx + rdx], rax
    mov rax, [rel code_sz]
    mov [rcx + rdx + 8], rax
    pop rdx
    inc qword [rel func_count]
    ; Reset variable table for function scope
    mov qword [rel var_cnt], 0
    mov qword [rel stack_dep], 0
    mov qword [rel array_var_cnt], 0
    mov qword [rel kosh_var_cnt], 0
    mov qword [rel kosh_param_var_cnt], 0
    mov qword [rel float_kosh_var_cnt], 0
    mov qword [rel float_var_cnt], 0
    mov qword [rel in_function], 1   ; we're inside a user function
    ; Emit function prologue: push rbp; mov rbp, rsp; push rbx
    mov dil, 0x55             ; push rbp
    call emit_byte
    mov dil, 0x48             ; mov rbp, rsp
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xE5
    call emit_byte
    mov dil, 0x53             ; push rbx
    call emit_byte
    ; Parameter handling: push arg registers, register in var_table
    mov r13, [rbx+16]        ; param count
    mov r14, [rbx+32]        ; param buffer end pos
    test r13, r13
    jz .gaf_no_params
    ; Calculate param start
    mov rax, r13
    shl rax, 3
    sub r14, rax              ; r14 = start of params
    ; Push arg registers in reverse order so param 0 is deepest:
    ; rdi, rsi, rdx, rcx, r8, r9 (maximum 6).
    cmp r13, 6
    jb .gaf_p5
    mov dil, 0x41             ; push r9 = 41 51
    call emit_byte
    mov dil, 0x51
    call emit_byte
.gaf_p5:
    cmp r13, 5
    jb .gaf_p4
    mov dil, 0x41             ; push r8 = 41 50
    call emit_byte
    mov dil, 0x50
    call emit_byte
.gaf_p4:
    cmp r13, 4
    jb .gaf_p3
    mov dil, 0x51             ; push rcx
    call emit_byte
.gaf_p3:
    cmp r13, 3
    jb .gaf_p2
    mov dil, 0x52             ; push rdx
    call emit_byte
.gaf_p2:
    cmp r13, 2
    jb .gaf_p1
    mov dil, 0x56             ; push rsi
    call emit_byte
.gaf_p1:
    cmp r13, 1
    jb .gaf_pdone
    mov dil, 0x57             ; push rdi
    call emit_byte
.gaf_pdone:
    ; Register params in var_table with known stack offsets
    ; After push rbp, push rbx, then the active argument-register saves:
    ;   param 0 (rdi) is at [rbp - 8 - param_count*8]
    ;   param i is at [rbp - 8 - (param_count - i)*8]
    xor r15, r15
.gaf_ploop:
    cmp r15, r13
    jae .gaf_no_params
    ; Get param name
    lea rax, [rel func_params]
    add rax, r14
    mov rdi, [rax + r15*8]  ; param name ptr
    ; Calculate stack offset: -(8 + (param_count - param_index) * 8)
    mov rax, r13
    sub rax, r15
    shl rax, 3
    add rax, 8
    neg rax
    ; Manually add to var_table
    push rdi
    mov rdi, [rel var_cnt]
    cmp rdi, VAR_TABLE_CAP
    jae .gaf_var_table_overflow
    imul rdi, rdi, 16
    lea rcx, [rel var_table]
    pop rsi                  ; param name ptr
    mov [rcx + rdi], rsi     ; name
    mov [rcx + rdi + 8], rax  ; location (negative = stack)
    inc qword [rel var_cnt]
    ; T12/T18 typed parameter metadata is compile-time only. Runtime ABI stays
    ; one qword per argument; kosh parameters are pointers with hidden headers.
    mov rax, r14
    shr rax, 3
    add rax, r15
    lea rdx, [rel func_param_types]
    movzx eax, byte [rdx + rax]
    cmp eax, PARAM_DASHAM
    je .gaf_param_scalar_float
    cmp eax, PARAM_KOSH
    je .gaf_param_kosh
    cmp eax, PARAM_KOSH_DASHAM
    je .gaf_param_kosh_float
    jmp .gaf_param_type_done
.gaf_param_scalar_float:
    mov rdi, rsi
    call mark_float_var
    jmp .gaf_param_type_done
.gaf_param_kosh:
    push rsi
    mov rdi, rsi
    call mark_kosh_var
    pop rsi
    mov rdi, rsi
    call mark_kosh_param_var
    jmp .gaf_param_type_done
.gaf_param_kosh_float:
    push rsi
    mov rdi, rsi
    call mark_kosh_var
    pop rsi
    push rsi
    mov rdi, rsi
    call mark_kosh_param_var
    pop rsi
    mov rdi, rsi
    call mark_float_kosh_var
.gaf_param_type_done:
    inc r15
    jmp .gaf_ploop
.gaf_var_table_overflow:
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail
.gaf_no_params:
    ; Stack spill slots must live below saved rbx and all pushed parameters.
    ; stack_dep tracks positive depth from rbp before alloc_var negates it.
    mov rax, r13
    shl rax, 3
    add rax, 8               ; saved rbx + param_count*8
    mov [rel stack_dep], rax
    ; Reserve a stable spill area so later user calls cannot overwrite locals.
    ; sub rsp, FUNC_SPILL_BYTES = 48 81 EC imm32
    mov dil, 0x48
    call emit_byte
    mov dil, 0x81
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov edi, FUNC_SPILL_BYTES
    call emit_u32
    ; Generate function body
    mov rax, [rbx+24]        ; body block node
    call gen_block
    ; Emit function epilogue: lea rsp,[rbp-8]; pop rbx; pop rbp; ret
    mov dil, 0x48             ; lea rsp, [rbp-8]
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x65
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov dil, 0x5B             ; pop rbx
    call emit_byte
    mov dil, 0x5D             ; pop rbp
    call emit_byte
    mov dil, 0xC3             ; ret
    call emit_byte
    inc r12
    jmp .gaf_loop
.gaf_func_table_overflow:
    lea rdi, [rel msg_func_table_overflow]
    jmp capacity_fail
.gaf_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; backpatch_calls — fix up all call rel32 instructions
backpatch_calls:
    push rbx
    push r12
    push r13
    push r14
    xor r12, r12              ; index
.bc_loop:
    cmp r12, [rel patch_count]
    jae .bc_done
    ; Get patch entry
    lea rax, [rel patch_list]
    push r12
    shl r12, 4
    mov r13, [rax + r12]      ; call_site offset
    mov r14, [rax + r12 + 8]  ; function name ptr
    pop r12
    ; Look up function in func_table
    lea rax, [rel func_table]
    xor rcx, rcx
.bc_search:
    cmp rcx, [rel func_count]
    jae .bc_not_found
    mov rdi, r14
    push rcx
    shl rcx, 4
    mov rsi, [rax + rcx]     ; func_table name_ptr
    pop rcx
    push rcx                 ; save counter around strcmp (it clobbers rcx)
    call strcmp               ; rax = 0 if match
    pop rcx                  ; restore counter
    test rax, rax
    jz .bc_found
    lea rax, [rel func_table] ; re-load base (strcmp clobbers rax)
    inc rcx
    jmp .bc_search
.bc_found:
    ; Get function address from func_table[rcx]
    lea rax, [rel func_table]
    push rcx
    shl rcx, 4
    mov rax, [rax + rcx + 8] ; function address (code offset)
    pop rcx
    ; Calculate rel32 = func_addr - (call_site + 4)
    ; call_site is the offset of the rel32 bytes in code_buf
    ; The call instruction is: E8 [rel32] (5 bytes)
    ; call_site = offset of rel32 = offset of E8 + 1
    ; target = call_site + 4 + rel32
    ; rel32 = target - (call_site + 4)
    sub rax, r13              ; func_addr - call_site
    sub rax, 4               ; - 4
    ; Patch code_buf at call_site
    lea rcx, [rel code_buf]
    mov [rcx + r13], eax     ; write rel32 (4 bytes)
    jmp .bc_next
.bc_not_found:
    ; Stage 2: in check mode report every unresolved call backpatch.
    ; Ordinary compilation still exits on the first unresolved name.
    cmp qword [rel r48_mode], 0
    je .bc_old_error
    mov rdi, r14
    call r48_print_undefined_function
    inc qword [rel r48_error_count]
    cmp qword [rel r48_error_count], 8
    jae .bc_check_fail
    jmp .bc_next
.bc_old_error:
    lea rdi, [rel msg_undefined_func]
    call print_str_z
    mov rdi, r14
    call print_str_z
    lea rdi, [rel msg_nl]
    call print_str_z
    mov rdi, 1
    call os_exit
.bc_next:
    inc r12
    jmp .bc_loop
.bc_done:
    cmp qword [rel r48_mode], 0
    je .bc_return
    cmp qword [rel r48_error_count], 0
    jne .bc_check_fail
.bc_return:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
.bc_check_fail:
    lea rdi, [rel r48_msg_errors]
    call print_str_z
    mov rdi, 1
    call os_exit

; gen_block(rax = block node)
gen_block:
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    ; Basic-block entry: do not trust cached XMM values across jumps/merges.
    call xmm_cache_barrier
%endif
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rax              ; block node
    mov r12, [rbx+8]          ; statement count
    xor r13, r13              ; index
.gb_loop:
    cmp r13, r12
    jae .gb_done
    mov rax, [rbx + 16 + r13*8]
    call gen_stmt
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    ; A declaration, call, branch, loop, early return or array store might
    ; clobber volatile XMM2-XMM5 or change control flow. Never cache across it.
    mov rax, [rbx + 16 + r13*8]
    cmp qword [rax], AST_ASSIGN
    je .gb_no_after_barrier
    call xmm_cache_barrier
.gb_no_after_barrier:
%endif
    inc r13
    jmp .gb_loop
.gb_done:
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    call xmm_cache_barrier
%endif
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; gen_stmt(rax = statement node)
gen_stmt:
    push rbx
    mov rbx, rax
    mov rax, [rbx]            ; node type
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    ; Conservative statement barrier. Only simple scalar assignments can
    ; keep cache residency across consecutive statements. Unknown calls,
    ; indexing, loops, conditionals, inline asm and all other statements
    ; invalidate the compile-time cache *before* emitting their code.
    cmp rax, AST_ASSIGN
    je .gs_stage1_assignment
    push rax
    call xmm_cache_barrier
    pop rax
.gs_stage1_assignment:
%endif
    cmp rax, AST_DECL
    je .gs_decl
    cmp rax, AST_ASSIGN
    je .gs_assign
    cmp rax, AST_IF
    je .gs_if
    cmp rax, AST_WHILE
    je .gs_while
    cmp rax, AST_DO_WHILE
    je .gs_do_while
    cmp rax, AST_RETURN
    je .gs_return
    cmp rax, AST_HALT
    je .gs_halt
    cmp rax, AST_WRITEMEM
    je .gs_writemem
    cmp rax, AST_CALL
    je .gs_call
    cmp rax, AST_FUNCDEF
    je .gs_funcdef
    cmp rax, AST_FUNCALL
    je .gs_funcall
    cmp rax, AST_FOR
    je .gs_for
    cmp rax, AST_BREAK
    je .gs_break
    cmp rax, AST_CONTINUE
    je .gs_continue
    cmp rax, AST_ASSERT
    je .gs_assert
    cmp rax, AST_NISHKRIYA
    je .gs_nishkriya
    ; Default: expression
    mov rax, rbx
    call gen_expr
    pop rbx
    ret

.gs_funcdef:
    ; Collect FUNCDEF node for later code generation
    push rax
    mov rcx, [rel func_def_cnt]
    cmp rcx, FUNC_DEFS_CAP
    jae .gs_funcdef_overflow
    lea rax, [rel func_defs]
    mov [rax + rcx*8], rbx
    inc qword [rel func_def_cnt]
    pop rax
    pop rbx
    ret
.gs_funcdef_overflow:
    pop rax
    pop rbx
    lea rdi, [rel msg_func_defs_overflow]
    jmp capacity_fail

.gs_funcall:
    ; [AST_FUNCALL][name_ptr][arg_count][arg1..arg6]
    ; Evaluate arguments and load them into the Sutram user-function registers:
    ;   rdi, rsi, rdx, rcx, r8, r9
    push r15
    push r14
    mov r15, [rbx+16]         ; arg count
    test r15, r15
    jz .gfc_call
    ; Evaluate args in REVERSE order. Use the same typed helper as expression
    ; calls so statement calls cannot bypass dasham/kosh conversion or checks.
    mov r14, r15
.gfc_eval:
    dec r14
    mov rdi, [rbx+8]         ; function name
    mov rsi, r14             ; zero-based argument index
    mov rdx, [rbx + 24 + r14*8]
    call gen_typed_call_arg  ; emits converted value + runtime push
    test r14, r14
    jnz .gfc_eval
    ; Pop into arg registers in forward order (arg0 first)
    xor r14, r14
.gfc_pop:
    cmp r14, r15
    jae .gfc_call
    cmp r14, 0
    je .gfc_p0
    cmp r14, 1
    je .gfc_p1
    cmp r14, 2
    je .gfc_p2
    cmp r14, 3
    je .gfc_p3
    cmp r14, 4
    je .gfc_p4
    ; arg5 -> r9 (41 59)
    mov dil, 0x41
    call emit_byte
    mov dil, 0x59
    call emit_byte
    jmp .gfc_pnext
.gfc_p0:
    mov dil, 0x5F             ; pop rdi  (arg0)
    call emit_byte
    jmp .gfc_pnext
.gfc_p1:
    mov dil, 0x5E             ; pop rsi  (arg1)
    call emit_byte
    jmp .gfc_pnext
.gfc_p2:
    mov dil, 0x5A             ; pop rdx  (arg2)
    call emit_byte
    jmp .gfc_pnext
.gfc_p3:
    mov dil, 0x59             ; pop rcx  (arg3)
    call emit_byte
    jmp .gfc_pnext
.gfc_p4:
    mov dil, 0x41             ; pop r8 = 41 58 (arg4)
    call emit_byte
    mov dil, 0x58
    call emit_byte
.gfc_pnext:
    inc r14
    jmp .gfc_pop
.gfc_call:
    call r46_live_callee_saved_vars
    mov r15, rax
    test r15, r15
    jz .gfc_saves_done
    ; B6: user variables may live in r12-r15. Preserve those compiler-allocated
    ; callee-saved registers across every Sutram user-function call.
    mov dil, 0x41             ; push r12 = 41 54
    call emit_byte
    mov dil, 0x54
    call emit_byte
    mov dil, 0x41             ; push r13 = 41 55
    call emit_byte
    mov dil, 0x55
    call emit_byte
    mov dil, 0x41             ; push r14 = 41 56
    call emit_byte
    mov dil, 0x56
    call emit_byte
    mov dil, 0x41             ; push r15 = 41 57
    call emit_byte
    mov dil, 0x57
    call emit_byte
.gfc_saves_done:
    ; Emit call rel32 (E8 + 4-byte offset, patched later)
    mov dil, 0xE8
    call emit_byte
    ; Record patch site
    mov rax, [rel code_sz]
    mov rdx, [rel patch_count]
    cmp rdx, PATCH_LIST_CAP
    jae .gfc_patch_overflow
    lea rcx, [rel patch_list]
    push rdx
    shl rdx, 4
    mov [rcx + rdx], rax
    mov rax, [rbx+8]
    mov [rcx + rdx + 8], rax
    pop rdx
    inc qword [rel patch_count]
    xor edi, edi
    call emit_u32
    test r15, r15
    jz .gfc_restores_done
    mov dil, 0x41             ; pop r15 = 41 5F
    call emit_byte
    mov dil, 0x5F
    call emit_byte
    mov dil, 0x41             ; pop r14 = 41 5E
    call emit_byte
    mov dil, 0x5E
    call emit_byte
    mov dil, 0x41             ; pop r13 = 41 5D
    call emit_byte
    mov dil, 0x5D
    call emit_byte
    mov dil, 0x41             ; pop r12 = 41 5C
    call emit_byte
    mov dil, 0x5C
    call emit_byte
.gfc_restores_done:
    pop r14
    pop r15
    pop rbx
    ret
.gfc_patch_overflow:
    lea rdi, [rel msg_patch_overflow]
    jmp capacity_fail

.gs_decl:
    ; [AST_DECL][name_ptr][init_ptr][array_size_expr_or_0][type_marker]
    ; PERF2/PERF3: when an integer scalar will occupy one of the first five
    ; register slots, build simple literals/copies/var-binops directly in the
    ; destination register.  Unsupported forms leave allocation untouched.
    mov rdi, rbx
    call try_emit_int_decl_reg
    test rax, rax
    jz .gs_decl_not_fast
    pop rbx
    ret
.gs_decl_not_fast:
    cmp qword [rbx+32], 2
    je .gs_decl_kosh
    cmp qword [rbx+32], 3
    je .gs_decl_kosh
    cmp qword [rbx+24], 0
    jne .gs_decl_array
    ; T12 type marker is compiler-side only; runtime storage remains one qword.
    cmp qword [rbx+32], 1
    jne .gs_decl_type_marked
    mov rdi, [rbx+8]
    call mark_float_var
.gs_decl_type_marked:
    mov rax, [rbx+16]        ; init expr
    test rax, rax
    jz .gs_decl_noinit
    mov rdi, rax
    call expr_is_float
    push rax                  ; source result type
    mov rax, [rbx+16]
    call gen_expr             ; runtime result in RAX
    pop rcx
    cmp qword [rbx+32], 1
    jne .gs_decl_to_int
    test rcx, rcx
    jnz .gs_decl_value_ready
    call emit_i64_to_f64_rax
    jmp .gs_decl_value_ready
.gs_decl_to_int:
    test rcx, rcx
    jz .gs_decl_value_ready
    call emit_f64_to_i64_rax
.gs_decl_value_ready:
    ; Allocate variable and store
    mov rdi, [rbx+8]         ; name ptr
    call alloc_var            ; rax = location
    test rax, rax
    jle .gs_decl_stack
    mov rdi, rax
    call emit_store_reg
    pop rbx
    ret
.gs_decl_stack:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
    pop rbx
    ret
.gs_decl_kosh:
    ; T18 layout: [user-16]=length, [user-8]=capacity, user[0..]=qword elements.
    ; Marker 3 adds compiler-side binary64 element typing; runtime layout is identical.
    mov rdi, [rbx+8]
    call mark_kosh_var
    cmp qword [rbx+32], 3
    jne .gs_decl_kosh_type_done
    mov rdi, [rbx+8]
    call mark_float_kosh_var
.gs_decl_kosh_type_done:
    mov rax, [rbx+24]
    call gen_expr             ; runtime capacity -> rax
    ; Normalize negative capacity to zero.
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x79             ; jns +3
    call emit_byte
    mov dil, 0x03
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x50             ; push capacity
    call emit_byte
    mov dil, 0x48             ; add rax,2 header qwords
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x02
    call emit_byte
    mov dil, 0x48             ; shl rax,3
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x03
    call emit_byte
    call emit_nirmmita_from_rax
    mov dil, 0x59             ; pop cap -> rcx
    call emit_byte
    mov dil, 0x48             ; mov qword [rax],0
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x00
    call emit_byte
    xor edi, edi
    call emit_u32
    mov dil, 0x48             ; mov [rax+8],rcx
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x08
    call emit_byte
    mov dil, 0x48             ; add rax,16 -> user pointer
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov rdi, [rbx+8]
    call alloc_var
    test rax, rax
    jle .gs_decl_kosh_stack
    mov rdi, rax
    call emit_store_reg
    pop rbx
    ret
.gs_decl_kosh_stack:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
    pop rbx
    ret

.gs_decl_array:
    ; Mark this name as a real pankti array in the current generated-function
    ; scope. Raw nirmmita pointers keep their historical unchecked index path.
    mov rdi, [rbx+8]
    call mark_array_var
    ; T8b runtime-header layout:
    ;   allocation base +0  = element count (hidden)
    ;   user array pointer   = allocation base +8 (element 0)
    ; This removes compile-time name collisions and preserves dynamic lengths.
    mov rax, [rbx+24]        ; size expression
    call gen_expr             ; runtime length -> rax
    ; push length while allocation is emitted
    mov dil, 0x50
    call emit_byte
    ; add rax, 1  (header slot + elements)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x01
    call emit_byte
    ; shl rax, 3  (qwords -> bytes)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x03
    call emit_byte
    call emit_nirmmita_from_rax
    ; pop length -> rcx; store header at allocation base
    mov dil, 0x59
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x08             ; mov [rax], rcx
    call emit_byte
    ; user pointer = base + 8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x08
    call emit_byte
    ; Store user pointer in the declared variable.
    mov rdi, [rbx+8]
    call alloc_var
    test rax, rax
    jle .gs_decl_array_stack
    mov rdi, rax
    call emit_store_reg
    pop rbx
    ret
.gs_decl_array_stack:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
    pop rbx
    ret

.gs_decl_noinit:
    mov rdi, [rbx+8]
    call alloc_var
    pop rbx
    ret

.gs_assign:
    ; [AST_ASSIGN][target_ptr][value_ptr]
    ; Check if target is AST_INDEX (array store)
    mov rax, [rbx+8]         ; target node
    mov rcx, [rax]           ; target type
    cmp rcx, AST_INDEX
    je .gs_assign_index
    cmp rcx, AST_FIELD
    je .gs_assign_field
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    ; Stage 1: typed scalar assignments only, exactly 4 available XMM slots.
    ; No calls/indices/subtrees are ever reordered or cached.
    mov rdi, rbx
    call try_emit_xmm_cached_assignment
    test rax, rax
    jnz .gs_assign_fast_done
    ; Fallback is intentionally conservative. The generic scalar generator
    ; can use other SSE temps, so flush metadata before its emission.
    call xmm_cache_barrier
%endif
    ; PERF-F1: float self-updates with two register-resident dasham values.
    ; Transfer both raw binary64 payloads directly to SSE2, perform the native
    ; op, then return the result to its assigned GPR. Avoid runtime stack
    ; traffic; generic path still owns other float expressions and ABI calls.
    mov rdi, rbx
    call try_emit_float_reg_self_update
    test rax, rax
    jnz .gs_assign_fast_done
    ; PERF-F2: float c=a op b, with three scalar dasham register locals.
    ; Load operands into XMM scratch registers before writing the destination,
    ; so even c=b aliases remain safe for subtraction and division.
    mov rdi, rbx
    call try_emit_float_reg_destination
    test rax, rax
    jnz .gs_assign_fast_done
    ; PERF1: integer self-update fast path.  The first five locals live in
    ; callee-saved registers; avoid materializing x=x+y / x=x+imm through
    ; RAX plus a generated push/pop/xchg/store sequence when the destination
    ; can be updated directly.  Stack locals get an in-place imm8 form too.
    mov rdi, rbx
    call try_emit_int_self_update
    test rax, rax
    jnz .gs_assign_fast_done
    ; PERF2: distinct register destination scheduling for integer copies,
    ; constants and var-var +,-,* expressions.
    mov rdi, rbx
    call try_emit_int_reg_assignment
    test rax, rax
    jz .gs_assign_generic
.gs_assign_fast_done:
    pop rbx
    ret
.gs_assign_generic:
    ; Normal assignment with T12 destination/source conversion.
    mov rax, [rbx+8]
    mov rdi, [rax+8]
    call is_float_var
    push rax                  ; target float flag
    mov rdi, [rbx+16]
    call expr_is_float
    push rax                  ; source float flag
    mov rax, [rbx+16]
    call gen_expr             ; runtime result in RAX
    pop rcx                   ; source flag
    pop rdx                   ; target flag
    test rdx, rdx
    jz .gs_assign_target_int
    test rcx, rcx
    jnz .gs_assign_value_ready
    call emit_i64_to_f64_rax
    jmp .gs_assign_value_ready
.gs_assign_target_int:
    test rcx, rcx
    jz .gs_assign_value_ready
    call emit_f64_to_i64_rax
.gs_assign_value_ready:
    ; Get target variable offset
    mov rax, [rbx+8]         ; target node
    mov rax, [rax+8]         ; variable name ptr
    mov rdi, rax
    call lookup_var           ; rax = location
    ; Check if register or stack
    test rax, rax
    jle .gs_assign_stack
    ; Register: emit mov reg, rax
    mov rdi, rax
    call emit_store_reg
    pop rbx
    ret
.gs_assign_stack:
    ; Stack/parameter assignment: mov [rbp+offset], rax.  B1 used to fall
    ; through into array-store generation after only pushing the offset.
    push r12
    mov r12, rax              ; compiler-time stack offset from lookup_var
    mov dil, 0x48             ; 48 89 45 xx = mov [rbp+disp8], rax
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, r12d
    call emit_byte
    pop r12
    pop rbx
    ret

.gs_assign_index:
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    call xmm_cache_barrier
%endif
    ; T8/T18 array store with generated bounds check. For kosh, normalize the
    ; assigned scalar to the declared element type before writing the qword.
    push r12
    push r13
    push r14
    xor r13, r13             ; 0=not kosh, 1=integer kosh, 2=float kosh
    mov rax, [rbx+8]
    mov rdi, [rax+8]
    call is_kosh_var
    test rax, rax
    jz .gs_ai_type_known
    mov r13, 1
    mov rax, [rbx+8]
    mov rdi, [rax+8]
    call is_float_kosh_var
    test rax, rax
    jz .gs_ai_type_known
    mov r13, 2
.gs_ai_type_known:
    mov rdi, [rbx+16]
    call expr_is_float
    mov r14, rax             ; source scalar type
    push r13                 ; gen_expr may use compiler temporaries
    push r14
    mov rax, [rbx+16]        ; value expr
    call gen_expr
    pop r14
    pop r13
    test r13, r13
    jz .gs_ai_value_ready
    mov rdi, r14
    xor esi, esi             ; integer/raw target
    cmp r13, 2
    jne .gs_ai_convert_value
    mov esi, 1               ; binary64 target
.gs_ai_convert_value:
    call emit_scalar_type_conversion
.gs_ai_value_ready:
    mov dil, 0x50            ; push value
    call emit_byte
    mov rax, [rbx+8]
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .gs_ai_stk
    mov rdi, rax
    call emit_load_reg
    jmp .gs_ai_have
.gs_ai_stk:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
.gs_ai_have:
    mov dil, 0x50            ; push base address
    call emit_byte
    ; Fixed pankti keeps length at [ptr-8]; T18 kosh keeps logical length
    ; at [ptr-16] and capacity at [ptr-8]. Raw nirmmita pointers stay unchecked.
    mov rax, [rbx+8]
    mov rdi, [rax+8]
    call is_kosh_var
    test rax, rax
    jz .gs_ai_check_pankti
    mov r12, 2
    mov dil, 0x48             ; mov rcx,[rax-16]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    mov dil, 0x51
    call emit_byte
    jmp .gs_ai_no_len
.gs_ai_check_pankti:
    mov rax, [rbx+8]
    mov rdi, [rax+8]
    call is_array_var
    mov r12, rax
    test r12, r12
    jz .gs_ai_no_len
    mov dil, 0x48             ; mov rcx,[rax-8]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov dil, 0x51
    call emit_byte
.gs_ai_no_len:
    mov rax, [rbx+8]
    mov rax, [rax+16]
    push r12                  ; preserve compiler-time array marker
    call gen_expr             ; runtime index -> rax
    pop r12
    test r12, r12
    jz .gs_ai_no_bounds
    call emit_array_bounds_check
    mov dil, 0x59            ; discard runtime length
    call emit_byte
.gs_ai_no_bounds:
    mov dil, 0x48            ; shl rax,3
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x03
    call emit_byte
    mov dil, 0x59            ; pop base -> rcx
    call emit_byte
    mov dil, 0x48            ; add rax,rcx
    call emit_byte
    mov dil, 0x01
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    mov dil, 0x5A            ; pop value -> rdx
    call emit_byte
    mov dil, 0x48            ; mov [rax],rdx
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x10
    call emit_byte
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.gs_assign_stack_orig:
    ; Stack: mov [rbp+offset], rax
    push rax                  ; save offset

.gs_assign_field:
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
    call xmm_cache_barrier
%endif
    ; obj.field = val
    ; [AST_ASSIGN][target=AST_FIELD][value]
    ; 1. gen_expr(value) → push
    ; 2. lookup_var(name) → load base, push
    ; 3. mov rax, offset
    ; 4. pop rcx (base), add
    ; 5. pop rdx (value), mov [rax], rdx
    mov rax, [rbx+16]        ; value expr
    call gen_expr
    mov dil, 0x50            ; push rax (value)
    call emit_byte
    ; Load base
    mov rax, [rbx+8]         ; target = AST_FIELD
    mov rdi, [rax+8]         ; name ptr
    call lookup_var
    test rax, rax
    jle .gs_af_stk
    mov rdi, rax
    call emit_load_reg
    jmp .gs_af_have
.gs_af_stk:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
.gs_af_have:
    mov dil, 0x50            ; push rax (base)
    call emit_byte
    ; mov rax, offset (48 B8 + 8 bytes of offset, little-endian)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    ; Save field offset in r14 (not used by gen_block/gen_stmt/gen_expr)
    push r14
    mov rax, [rbx+8]         ; AST_FIELD
    mov r14, [rax+16]        ; field offset
    ; Emit 8 bytes of the offset (little-endian)
    mov rdi, r14
    call emit_u32
    shr r14, 32
    mov rdi, r14
    call emit_u32
    pop r14
    ; pop rcx (base)
    mov dil, 0x59
    call emit_byte
    ; add rax, rcx
    mov dil, 0x48
    call emit_byte
    mov dil, 0x01
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    ; pop rdx (value)
    mov dil, 0x5A
    call emit_byte
    ; mov [rax], rdx
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x10
    call emit_byte
    pop rbx
    ret
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x45
    call emit_byte
    pop rax
    mov edi, eax
    call emit_byte
    pop rbx
    ret

.gs_if:
    push r12
    push r13
    ; [AST_IF][cond][then][else]
    ; Check if condition is a comparison
    push rbx
    mov rax, [rbx+8]
    mov rcx, [rax]           ; node type
    cmp rcx, AST_BINOP
    jne .gi_normal_cond
    mov rdi, rax
    call binop_needs_float
    test rax, rax
    jnz .gi_normal_cond
    mov rax, [rbx+8]         ; reload condition after helper
    mov rcx, [rax+8]         ; operator
    cmp rcx, OP_GT
    je .gi_cmp_cond
    cmp rcx, OP_LT
    je .gi_cmp_cond
    cmp rcx, OP_EQ
    je .gi_cmp_cond
    cmp rcx, OP_LE
    je .gi_cmp_cond
    cmp rcx, OP_GE
    je .gi_cmp_cond
    cmp rcx, OP_NE
    je .gi_cmp_cond
.gi_normal_cond:
    pop rbx
    mov rax, [rbx+8]         ; condition
    call gen_expr
    ; test rax, rax
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; je rel32
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x84
    call emit_byte
    mov r12, [rel code_sz]
    xor edi, edi
    call emit_u32
    jmp .gi_then
.gi_cmp_cond:
    pop rbx                  ; restore rbx = if node
    ; PERF1: if both comparison operands are register-resident integer vars,
    ; compare them in place instead of round-tripping through RAX + stack.
    mov rdi, [rbx+8]
    call try_emit_int_reg_cmp
    test rax, rax
    jnz .gi_emit_jcc
    ; Evaluate left -> rax (gen_expr preserves rbx)
    mov rax, [rbx+8]
    mov rax, [rax+16]        ; left
    call gen_expr
    ; Check if right is constant <= 127
    push rbx
    mov rax, [rbx+8]
    mov rax, [rax+24]        ; right node
    mov rcx, [rax]
    cmp rcx, AST_NUM
    jne .gi_full_cmp
    mov rcx, [rax+8]
    cmp rcx, 127
    ja .gi_full_cmp
    ; FAST: cmp rax, imm8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov rax, [rbx+8]
    mov rax, [rax+24]
    mov rax, [rax+8]
    mov dil, al
    call emit_byte
    pop rbx
    jmp .gi_emit_jcc
.gi_full_cmp:
    pop rbx
    ; mov rdx, rax
    mov dil, 0x50            ; push rax (save on stack — call-safe)
    call emit_byte
    ; Evaluate right
    mov rax, [rbx+8]
    mov rax, [rax+24]
    call gen_expr
    mov dil, 0x5A            ; pop rdx (restore saved left)
    call emit_byte
    ; xchg rax, rdx
    mov dil, 0x48
    call emit_byte
    mov dil, 0x87
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    ; cmp rax, rdx
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
.gi_emit_jcc:
    ; Inverted conditional jump
    mov rax, [rbx+8]
    mov rax, [rax+8]         ; operator
    cmp rax, OP_GT
    je .gi_jle
    cmp rax, OP_LT
    je .gi_jge
    cmp rax, OP_LE
    je .gi_jg
    cmp rax, OP_GE
    je .gi_jl
    cmp rax, OP_NE
    je .gi_je
    mov dil, 0x0F            ; jne
    call emit_byte
    mov dil, 0x85
    call emit_byte
    jmp .gi_emit_offset
.gi_jg:
    mov dil, 0x0F            ; jg = 0F 8F (not <=)
    call emit_byte
    mov dil, 0x8F
    call emit_byte
    jmp .gi_emit_offset
.gi_jl:
    mov dil, 0x0F            ; jl = 0F 8C (not >=)
    call emit_byte
    mov dil, 0x8C
    call emit_byte
    jmp .gi_emit_offset
.gi_je:
    mov dil, 0x0F            ; je = 0F 84 (not !=)
    call emit_byte
    mov dil, 0x84
    call emit_byte
    jmp .gi_emit_offset
.gi_jle:
    mov dil, 0x0F            ; jle
    call emit_byte
    mov dil, 0x8E
    call emit_byte
    jmp .gi_emit_offset
.gi_jge:
    mov dil, 0x0F            ; jge
    call emit_byte
    mov dil, 0x8D
    call emit_byte
.gi_emit_offset:
    mov r12, [rel code_sz]
    xor edi, edi
    call emit_u32
.gi_then:
    ; Generate then body
    mov rax, [rbx+16]        ; then block
    call gen_block
    ; Check for else
    mov rax, [rbx+24]        ; else block
    test rax, rax
    jz .gs_if_noelse
    ; jmp rel32 (skip else)
    mov dil, 0xE9
    call emit_byte
    mov r13, [rel code_sz]   ; jmp offset position
    xor edi, edi
    call emit_u32
    ; Patch je to here
    mov rax, [rel code_sz]
    sub rax, r12
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r12], eax
    ; Generate else body
    mov rax, [rbx+24]
    call gen_block
    ; Patch jmp to here
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    mov [rcx + r13], eax
    pop r13
    pop r12
    pop rbx
    ret
.gs_if_noelse:
    ; Patch je to here
    mov rax, [rel code_sz]
    sub rax, r12
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r12], eax
    pop r13
    pop r12
    pop rbx
    ret

.gs_nishkriya:
    ; [AST_NISHKRIYA][hex_str_ptr][0][0]
    ; CRITICAL: preserve r12/r13 (r13 is gen_block's statement index!)
    push r12
    push r13
    mov r12, [rbx+8]         ; r12 = hex string pointer
    ; Skip leading spaces
.gn_skip1:
    cmp byte [r12], ' '
    jne .gn_start
    inc r12
    jmp .gn_skip1
.gn_start:
    cmp byte [r12], 0
    je .gn_done               ; empty string
    ; Parse two hex digits: value = (d1 << 4) | d2
    xor r13, r13              ; r13 = byte value accumulator
    ; First digit (hexval takes char in DIL, returns value in rax)
    movzx edi, byte [r12]
    call hexval
    shl r13, 4
    or r13, rax
    inc r12
    ; Second digit
    movzx edi, byte [r12]
    call hexval
    shl r13, 4
    or r13, rax
    inc r12
    ; Emit the byte
    mov edi, r13d
    call emit_byte
    ; Skip spaces after the byte
.gn_skip2:
    cmp byte [r12], ' '
    jne .gn_check
    inc r12
    jmp .gn_skip2
.gn_check:
    cmp byte [r12], 0
    jne .gn_start
.gn_done:
    pop r13
    pop r12
    pop rbx
    ret

.gs_for:
    ; [AST_FOR][var_name][start_expr][end_expr][body][0]
    ; PERF2: test-at-bottom shape.  Emit one initial jump to the test, then
    ; one backward conditional branch per iteration.  This removes the old
    ; forward-exit + backward-unconditional branch pair from hot loops.
    push r12
    push r13
    push r14
    push r15
    ; --- Direction detection: descending when both bounds are constants
    ;     and start > end (e.g. punaravartana i = 5 to 1) ---
    mov qword [rel for_descend], 0
    mov rax, [rbx+16]
    mov rcx, [rax]
    cmp rcx, AST_NUM
    jne .gf2_dir_done
    mov rax, [rbx+24]
    mov rcx, [rax]
    cmp rcx, AST_NUM
    jne .gf2_dir_done
    mov rax, [rbx+16]
    mov rax, [rax+8]
    mov rcx, [rbx+24]
    mov rcx, [rcx+8]
    cmp rax, rcx
    jle .gf2_dir_done
    mov qword [rel for_descend], 1
.gf2_dir_done:
    ; Preserve outer loop patch ranges.
    mov rax, [rel break_patch_cnt]
    push rax
    mov rax, [rel continue_patch_cnt]
    push rax
    ; Nested loops may change the global direction flag while the body emits.
    push qword [rel for_descend]

    ; Evaluate and store the induction start value.
    mov rax, [rbx+16]
    call gen_expr
    mov rdi, [rbx+8]
    call lookup_var
    test rax, rax
    jz .gf2_fresh_var
    mov r14, rax
    jmp .gf2_have_loc
.gf2_fresh_var:
    mov rdi, [rbx+8]
    call alloc_var
    mov r14, rax
.gf2_have_loc:
    test r14, r14
    jle .gf2_stk_init
    mov rdi, r14
    call emit_store_reg
    jmp .gf2_emit_entry_jump
.gf2_stk_init:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, r14d
    call emit_byte

.gf2_emit_entry_jump:
    ; Zero-iteration correctness: skip the body and test the bounds first.
    mov dil, 0xE9
    call emit_byte
    mov r13, [rel code_sz]       ; rel32 field to patch to the bottom test
    xor edi, edi
    call emit_u32
    mov r12, [rel code_sz]       ; body start

    mov rax, [rbx+32]
    call gen_block

    ; Restore this loop's direction after nested loops in the body.
    pop rax
    mov [rel for_descend], rax

    ; continue in a for-loop means perform the induction update, then test.
    mov r15, [rel code_sz]
    push r15                    ; preserve continue target across patch scratch use
    mov rdi, r14
    mov rsi, OP_ADD
    cmp qword [rel for_descend], 0
    je .gf2_inc_ready
    mov rsi, OP_SUB
.gf2_inc_ready:
    mov rdx, 1
    test r14, r14
    jle .gf2_inc_stack
    call emit_reg_self_update_imm
    jmp .gf2_test_start
.gf2_inc_stack:
    call emit_stack_self_update_imm

.gf2_test_start:
    ; Patch the one-time entry jump to this test position.
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx+r13], eax

    ; Compare induction variable to end bound.  Keep PERF1's direct-reg form.
    test r14, r14
    jle .gf2_cmp_slow
    mov rax, [rbx+24]
    cmp qword [rax], AST_VAR
    jne .gf2_cmp_slow
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .gf2_cmp_slow
    mov rdi, r14
    mov rsi, rax
    call emit_reg_cmp_reg
    jmp .gf2_cmp_ready
.gf2_cmp_slow:
    test r14, r14
    jle .gf2_stk_load
    mov rdi, r14
    call emit_load_reg
    jmp .gf2_have_var
.gf2_stk_load:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, r14d
    call emit_byte
.gf2_have_var:
    mov dil, 0x50
    call emit_byte
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x5A
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x87
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
.gf2_cmp_ready:
    ; Branch backward only while the inclusive range remains valid.
    mov dil, 0x0F
    call emit_byte
    cmp qword [rel for_descend], 0
    jne .gf2_back_jge
    mov dil, 0x8E               ; jle body_start (ascending var <= end)
    jmp .gf2_back_opcode
.gf2_back_jge:
    mov dil, 0x8D               ; jge body_start (descending var >= end)
.gf2_back_opcode:
    call emit_byte
    mov rax, r12
    mov rcx, [rel code_sz]
    add rcx, 4
    sub rax, rcx
    mov edi, eax
    call emit_u32

    ; loop_end is current code_sz. Patch this loop's breaks only.
    mov r14, [rel break_patch_cnt]
    cmp r14, [rsp+16]
    je .gf2_no_brk
    lea r15, [rel break_patch_positions]
    mov rcx, [rel code_sz]
.gf2_brk_loop:
    dec r14
    mov rax, [r15+r14*8]
    mov rdx, rcx
    sub rdx, rax
    sub rdx, 4
    push rcx
    lea rcx, [rel code_buf]
    mov [rcx+rax], edx
    pop rcx
    cmp r14, [rsp+16]
    jne .gf2_brk_loop
.gf2_no_brk:
    mov r14, [rel continue_patch_cnt]
    cmp r14, [rsp+8]
    je .gf2_no_cont
    lea r15, [rel continue_patch_positions]
    mov rcx, [rsp]              ; saved continue/update target
.gf2_cont_loop:
    dec r14
    mov rax, [r15+r14*8]
    mov rdx, rcx
    sub rdx, rax
    sub rdx, 4
    push rcx
    lea rcx, [rel code_buf]
    mov [rcx+rax], edx
    pop rcx
    cmp r14, [rsp+8]
    jne .gf2_cont_loop
.gf2_no_cont:
    mov rax, [rsp+8]
    mov [rel continue_patch_cnt], rax
    mov rax, [rsp+16]
    mov [rel break_patch_cnt], rax
    add rsp, 24
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.gs_break:
    ; Emit: jmp rel32 to loop_end (needs backpatching)
    ; For simplicity, emit a jmp that targets the nearest loop end
    ; We store the patch position in a global for the while/for to fix
    mov dil, 0xE9            ; jmp rel32
    call emit_byte
    ; Store position for backpatching
    mov rax, [rel break_patch_cnt]
    cmp rax, BREAK_PATCH_CAP
    jae .gs_break_overflow
    lea rcx, [rel break_patch_positions]
    mov rdx, [rel code_sz]
    mov [rcx + rax*8], rdx
    inc qword [rel break_patch_cnt]
    xor edi, edi
    call emit_u32
    pop rbx
    ret
.gs_break_overflow:
    lea rdi, [rel msg_break_patch_overflow]
    jmp capacity_fail

.gs_continue:
    ; Emit: jmp rel32 to loop_start (needs backpatching)
    mov dil, 0xE9            ; jmp rel32
    call emit_byte
    mov rax, [rel continue_patch_cnt]
    cmp rax, CONTINUE_PATCH_CAP
    jae .gs_continue_overflow
    lea rcx, [rel continue_patch_positions]
    mov rdx, [rel code_sz]
    mov [rcx + rax*8], rdx
    inc qword [rel continue_patch_cnt]
    xor edi, edi
    call emit_u32
    pop rbx
    ret
.gs_continue_overflow:
    lea rdi, [rel msg_continue_patch_overflow]
    jmp capacity_fail

.gs_assert:
    ; nishedha(cond) — if cond is false, exit with error code 1
    ; Evaluate cond -> rax, test rax, if zero then sys_exit(1)
    mov rax, [rbx+8]
    call gen_expr
    ; test rax, rax
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jnz +12 (skip exit, continue)
    mov dil, 0x75
    call emit_byte
    mov dil, 0x0C
    call emit_byte
    ; mov eax, 60 (sys_exit)
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x3C
    call emit_byte
    xor edi, edi
    call emit_byte
    call emit_byte
    call emit_byte
    ; mov edi, 1 (error code)
    mov dil, 0xBF
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    call emit_byte
    call emit_byte
    ; syscall
    call emit_syscall
    pop rbx
    ret

.gs_while:
    ; [AST_WHILE][cond][body]
    ; PERF2: test-at-bottom layout.  One initial jump preserves zero-iteration
    ; semantics; steady-state iterations use only one backward conditional.
    push r12
    push r13
    push r14
    push r15
    mov rax, [rel break_patch_cnt]
    push rax
    mov rax, [rel continue_patch_cnt]
    push rax

    ; One-time entry jump to the bottom test.
    mov dil, 0xE9
    call emit_byte
    mov r13, [rel code_sz]
    xor edi, edi
    call emit_u32
    mov r12, [rel code_sz]       ; body start

    mov rax, [rbx+16]
    call gen_block
    mov r15, [rel code_sz]       ; continue/test target
    push r15                      ; preserve across condition generation

    ; Patch the one-time entry jump to test_start.
    mov rax, r15
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx+r13], eax

    ; Prefer comparison-aware codegen so the condition can branch directly
    ; back to body without materializing a boolean in RAX.
    mov r14, [rbx+8]
    cmp qword [r14], AST_BINOP
    jne .gw2_normal_cond
    mov rdi, r14
    call binop_needs_float
    test rax, rax
    jnz .gw2_normal_cond
    mov rax, [r14+8]
    cmp rax, OP_GT
    je .gw2_cmp_cond
    cmp rax, OP_LT
    je .gw2_cmp_cond
    cmp rax, OP_EQ
    je .gw2_cmp_cond
    cmp rax, OP_LE
    je .gw2_cmp_cond
    cmp rax, OP_GE
    je .gw2_cmp_cond
    cmp rax, OP_NE
    je .gw2_cmp_cond

.gw2_normal_cond:
    mov rax, [rbx+8]
    call gen_expr
    mov dil, 0x48               ; test rax,rax
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x0F               ; jne body_start
    call emit_byte
    mov dil, 0x85
    call emit_byte
    jmp .gw2_emit_back_offset

.gw2_cmp_cond:
    mov rdi, [rbx+8]
    call try_emit_int_reg_cmp
    test rax, rax
    jnz .gw2_emit_true_jcc
    ; General integer comparison path, retaining the imm8 shortcut.
    mov r14, [rbx+8]
    mov rax, [r14+16]
    call gen_expr
    mov r14, [rbx+8]
    mov rax, [r14+24]
    cmp qword [rax], AST_NUM
    jne .gw2_full_cmp
    mov rcx, [rax+8]
    cmp rcx, 127
    ja .gw2_full_cmp
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov r14, [rbx+8]
    mov rax, [r14+24]
    mov rax, [rax+8]
    mov dil, al
    call emit_byte
    jmp .gw2_emit_true_jcc
.gw2_full_cmp:
    mov dil, 0x50
    call emit_byte
    mov r14, [rbx+8]
    mov rax, [r14+24]
    call gen_expr
    mov dil, 0x5A
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x87
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte

.gw2_emit_true_jcc:
    mov r14, [rbx+8]
    mov rax, [r14+8]
    mov dil, 0x0F
    call emit_byte
    cmp rax, OP_GT
    je .gw2_jg
    cmp rax, OP_LT
    je .gw2_jl
    cmp rax, OP_LE
    je .gw2_jle
    cmp rax, OP_GE
    je .gw2_jge
    cmp rax, OP_NE
    je .gw2_jne
    mov dil, 0x84               ; je
    jmp .gw2_jcc_ready
.gw2_jg:
    mov dil, 0x8F
    jmp .gw2_jcc_ready
.gw2_jl:
    mov dil, 0x8C
    jmp .gw2_jcc_ready
.gw2_jle:
    mov dil, 0x8E
    jmp .gw2_jcc_ready
.gw2_jge:
    mov dil, 0x8D
    jmp .gw2_jcc_ready
.gw2_jne:
    mov dil, 0x85
.gw2_jcc_ready:
    call emit_byte

.gw2_emit_back_offset:
    mov rax, r12
    mov rcx, [rel code_sz]
    add rcx, 4
    sub rax, rcx
    mov edi, eax
    call emit_u32

    ; Patch this loop's breaks to loop_end.
    mov r14, [rel break_patch_cnt]
    cmp r14, [rsp+16]
    je .gw2_no_brk
    lea r15, [rel break_patch_positions]
    mov rcx, [rel code_sz]
.gw2_brk_loop:
    dec r14
    mov rax, [r15+r14*8]
    mov rdx, rcx
    sub rdx, rax
    sub rdx, 4
    push rcx
    lea rcx, [rel code_buf]
    mov [rcx+rax], edx
    pop rcx
    cmp r14, [rsp+16]
    jne .gw2_brk_loop
.gw2_no_brk:
    ; Continue goes to the bottom test, not directly to the body.
    mov r14, [rel continue_patch_cnt]
    cmp r14, [rsp+8]
    je .gw2_no_cont
    lea rax, [rel continue_patch_positions]
    mov rcx, [rsp]              ; preserved test target
.gw2_cont_loop:
    dec r14
    mov rsi, [rax+r14*8]
    mov rdi, rcx
    sub rdi, rsi
    sub rdi, 4
    push rcx
    lea rcx, [rel code_buf]
    mov [rcx+rsi], edi
    pop rcx
    cmp r14, [rsp+8]
    jne .gw2_cont_loop
.gw2_no_cont:
    mov rax, [rsp+8]
    mov [rel continue_patch_cnt], rax
    mov rax, [rsp+16]
    mov [rel break_patch_cnt], rax
    add rsp, 24
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.gs_do_while:
    ; [AST_DO_WHILE][body][condition]
    push r12
    push r13
    push r14
    push r15
    ; Save base patch counts; nested loops append without overwriting outer entries.
    mov rax, [rel break_patch_cnt]
    push rax
    mov rax, [rel continue_patch_cnt]
    push rax
    mov r12, [rel code_sz]        ; body start: executes at least once
    mov rax, [rbx+8]
    call gen_block
    mov r15, [rel code_sz]        ; continue target = condition test
    mov rax, [rbx+16]
    call gen_expr
    ; test rax, rax
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jne rel32 back to body start
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov rax, r12
    mov rcx, [rel code_sz]
    add rcx, 4
    sub rax, rcx
    mov edi, eax
    call emit_u32
    ; Patch break jumps to loop end.
    mov r14, [rel break_patch_cnt]
    cmp r14, [rsp+8]          ; saved break base
    je .gdw_no_brk
    lea r13, [rel break_patch_positions]
.gdw_brk_loop:
    dec r14
    mov rax, [r13 + r14*8]
    mov rdx, [rel code_sz]
    sub rdx, rax
    sub rdx, 4
    lea rcx, [rel code_buf]
    mov [rcx + rax], edx
    cmp r14, [rsp+8]
    jne .gdw_brk_loop
.gdw_no_brk:
    ; Patch continue jumps to condition evaluation.
    mov r14, [rel continue_patch_cnt]
    cmp r14, [rsp]            ; saved continue base
    je .gdw_no_cont
    lea r13, [rel continue_patch_positions]
.gdw_cont_loop:
    dec r14
    mov rax, [r13 + r14*8]
    mov rdx, r15
    sub rdx, rax
    sub rdx, 4
    lea rcx, [rel code_buf]
    mov [rcx + rax], edx
    cmp r14, [rsp]
    jne .gdw_cont_loop
.gdw_no_cont:
    ; Restore enclosing-loop patch counts.
    mov rax, [rsp]
    mov [rel continue_patch_cnt], rax
    mov rax, [rsp+8]
    mov [rel break_patch_cnt], rax
    add rsp, 16
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.gs_return:
    mov rax, [rbx+8]         ; return expr
    test rax, rax
    jz .gs_ret_none
    mov rdi, rax
    call expr_is_float
    push rax                  ; compile-time source type
    mov rax, [rbx+8]
    call gen_expr
    pop rcx                   ; 0=integer/raw, 1=binary64
    ; Main returns an integer process status; truncate an explicit float.
    cmp qword [rel in_function], 0
    jne .gs_ret_func_typed
    test rcx, rcx
    jz .gs_ret_epilogue
    call emit_f64_to_i64_rax
    jmp .gs_ret_epilogue
.gs_ret_func_typed:
    mov rdx, [rel current_func_float]
    cmp rcx, rdx
    je .gs_ret_func
    test rdx, rdx
    jz .gs_ret_func_to_int
    call emit_i64_to_f64_rax
    jmp .gs_ret_func
.gs_ret_func_to_int:
    call emit_f64_to_i64_rax
    jmp .gs_ret_func
.gs_ret_none:
    cmp qword [rel in_function], 0
    jne .gs_ret_func_none     ; in user function → emit ret
    mov dil, 0x48
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    xor edi, edi
    call emit_u32
    xor edi, edi
    call emit_u32
    jmp .gs_ret_epilogue       ; in main → emit sys_exit
.gs_ret_func:
    ; User function return: lea rsp,[rbp-8]; pop rbx; pop rbp; ret
    mov dil, 0x48             ; lea rsp, [rbp-8]
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x65
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov dil, 0x5B             ; pop rbx
    call emit_byte
    mov dil, 0x5D             ; pop rbp
    call emit_byte
    mov dil, 0xC3             ; ret
    call emit_byte
    pop rbx
    ret

.gs_ret_func_none:
    ; User function return with no value: xor rax; lea rsp,[rbp-8]; pop rbx; pop rbp; ret
    mov dil, 0x48             ; xor rax, rax
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48             ; lea rsp, [rbp-8]
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x65
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov dil, 0x5B             ; pop rbx
    call emit_byte
    mov dil, 0x5D             ; pop rbp
    call emit_byte
    mov dil, 0xC3             ; ret
    call emit_byte
    pop rbx
    ret

.gs_ret_epilogue:
    ; mov rsp, rbp; pop rbp; sys_exit
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov dil, 0x5D
    call emit_byte
    ; sys_exit(0)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    mov edi, 60
    call emit_u32
    xor edi, edi
    call emit_u32
    mov dil, 0x48
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    call emit_syscall
    pop rbx
    ret

.gs_halt:
    mov dil, 0xF4             ; hlt
    call emit_byte
    pop rbx
    ret

.gs_writemem:
    ; Statement-level writemem — delegate to gen_expr
    mov rax, rbx
    call gen_expr
    pop rbx
    ret

.gs_call:
    ; Statement-level call — delegate to gen_expr
    mov rax, rbx
    call gen_expr
    pop rbx
    ret

; emit_array_bounds_check
; Runtime index is in rax and runtime length is on top of the generated
; program stack ([rsp]).  Unsigned index < length rejects negative indices too.
emit_array_bounds_check:
    push rbx
    push r13
    ; cmp rax, [rsp] = 48 3B 04 24
    mov dil, 0x48
    call emit_byte
    mov dil, 0x3B
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0x24
    call emit_byte
    ; jb .ok = 0F 82 rel32
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x82
    call emit_byte
    mov r13, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; Failure block: print the portable diagnostic and exit 1.
    call alloc_ast
    mov qword [rax], AST_STR
    lea rcx, [rel msg_array_oob]
    mov [rax+8], rcx
    push rax
    call alloc_ast
    pop rcx
    mov qword [rax], AST_CALL
    mov qword [rax+8], BN_LIKHA
    mov qword [rax+16], 1
    mov [rax+24], rcx
    call gen_expr
    mov dil, 0xB8
    call emit_byte
    mov edi, 60
    call emit_u32
    mov dil, 0xBF
    call emit_byte
    mov edi, 1
    call emit_u32
    call emit_syscall
    ; Patch jb rel32 to success continuation.
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r13], eax
    pop r13
    pop rbx
    ret

emit_kosh_empty_check_r9:
    ; Runtime R9 = current kosh length. Empty pop is a safe runtime error.
    push rbx
    push r13
    mov dil, 0x4D             ; test r9,r9
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    mov dil, 0x0F             ; jnz success rel32
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov r13, [rel code_sz]
    xor edi, edi
    call emit_u32
    call alloc_ast
    mov qword [rax], AST_STR
    lea rcx, [rel msg_kosh_empty]
    mov [rax+8], rcx
    push rax
    call alloc_ast
    pop rcx
    mov qword [rax], AST_CALL
    mov qword [rax+8], BN_LIKHA
    mov qword [rax+16], 1
    mov [rax+24], rcx
    call gen_expr
    mov dil, 0xB8
    call emit_byte
    mov edi, 60
    call emit_u32
    mov dil, 0xBF
    call emit_byte
    mov edi, 1
    call emit_u32
    call emit_syscall
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx+r13], eax
    pop r13
    pop rbx
    ret

; R46 compiler-time call liveness: 1 if any caller local occupies r12..r15.
; Argument parameters in stack slots and rbx do not require these saves.
; No generated runtime code executes this helper.
r46_live_callee_saved_vars:
    xor eax, eax
    xor ecx, ecx
    mov r8, [rel var_cnt]
    lea r9, [rel var_table]
.r46_loop:
    cmp rcx, r8
    jae .r46_done
    mov rdx, rcx
    shl rdx, 4
    mov rdx, [r9+rdx+8]
    cmp rdx, 2
    jb .r46_next
    cmp rdx, 5
    ja .r46_next
    mov eax, 1
    ret
.r46_next:
    inc rcx
    jmp .r46_loop
.r46_done:
    ret

; gen_expr(rax = expression node)
gen_expr:
    push rbx
    mov rbx, rax
    mov rax, [rbx]            ; node type
    cmp rax, AST_NUM
    je .ge_num
    cmp rax, AST_FLOAT
    je .ge_float
    cmp rax, AST_VAR
    je .ge_var
    cmp rax, AST_BINOP
    je .ge_binop
    cmp rax, AST_WRITEMEM
    je .ge_writemem
    cmp rax, AST_HALT
    je .ge_halt
    cmp rax, AST_STR
    je .ge_str
    cmp rax, AST_VEC
    je .ge_vec
    cmp rax, 8               ; AST_CALL
    je .ge_call
    cmp rax, AST_FUNCALL
    je .ge_funcall
    cmp rax, AST_INDEX
    je .ge_index
    cmp rax, AST_FIELD
    je .ge_field
    cmp rax, AST_TERNARY
    je .ge_ternary
    ; Unknown — emit nop
    mov dil, 0x90
    call emit_byte
    pop rbx
    ret

.ge_funcall:
    ; [AST_FUNCALL][name_ptr][arg_count][arg1..arg6]
    ; Evaluate args left-to-right, push each result, then pop them into
    ; rdi, rsi, rdx, rcx, r8, r9 in reverse stack order.
    push r15                  ; save compiler-time r15 for R46
    push r14                  ; save r14 (gen_block uses it)
    mov r14, [rbx+16]        ; arg count
    test r14, r14
    jz .ge_fc_call
    ; Arg 1
    mov rdi, [rbx+8]
    xor esi, esi
    mov rdx, [rbx+24]
    call gen_typed_call_arg
    cmp r14, 2
    jb .ge_fc_pop1
    ; Arg 2
    mov rdi, [rbx+8]
    mov esi, 1
    mov rdx, [rbx+32]
    call gen_typed_call_arg
    cmp r14, 3
    jb .ge_fc_pop2
    ; Arg 3
    mov rdi, [rbx+8]
    mov esi, 2
    mov rdx, [rbx+40]
    call gen_typed_call_arg
    cmp r14, 4
    jb .ge_fc_pop3
    ; Arg 4
    mov rdi, [rbx+8]
    mov esi, 3
    mov rdx, [rbx+48]
    call gen_typed_call_arg
    cmp r14, 5
    jb .ge_fc_pop4
    ; Arg 5
    mov rdi, [rbx+8]
    mov esi, 4
    mov rdx, [rbx+56]
    call gen_typed_call_arg
    cmp r14, 6
    jb .ge_fc_pop5
    ; Arg 6
    mov rdi, [rbx+8]
    mov esi, 5
    mov rdx, [rbx+64]
    call gen_typed_call_arg
    ; Pop 6: arg5->r9, arg4->r8, arg3->rcx, arg2->rdx, arg1->rsi, arg0->rdi
    mov dil, 0x41
    call emit_byte
    mov dil, 0x59            ; pop r9
    call emit_byte
    mov dil, 0x41
    call emit_byte
    mov dil, 0x58            ; pop r8
    call emit_byte
    mov dil, 0x59            ; pop rcx
    call emit_byte
    mov dil, 0x5A            ; pop rdx
    call emit_byte
    mov dil, 0x5E            ; pop rsi
    call emit_byte
    mov dil, 0x5F            ; pop rdi
    call emit_byte
    jmp .ge_fc_call
.ge_fc_pop5:
    mov dil, 0x41
    call emit_byte
    mov dil, 0x58            ; pop r8
    call emit_byte
    mov dil, 0x59            ; pop rcx
    call emit_byte
    mov dil, 0x5A            ; pop rdx
    call emit_byte
    mov dil, 0x5E            ; pop rsi
    call emit_byte
    mov dil, 0x5F            ; pop rdi
    call emit_byte
    jmp .ge_fc_call
.ge_fc_pop4:
    mov dil, 0x59            ; pop rcx
    call emit_byte
    mov dil, 0x5A            ; pop rdx
    call emit_byte
    mov dil, 0x5E            ; pop rsi
    call emit_byte
    mov dil, 0x5F            ; pop rdi
    call emit_byte
    jmp .ge_fc_call
.ge_fc_pop3:
    mov dil, 0x5A            ; pop rdx
    call emit_byte
    mov dil, 0x5E            ; pop rsi
    call emit_byte
    mov dil, 0x5F            ; pop rdi
    call emit_byte
    jmp .ge_fc_call
.ge_fc_pop2:
    mov dil, 0x5E            ; pop rsi
    call emit_byte
    mov dil, 0x5F            ; pop rdi
    call emit_byte
    jmp .ge_fc_call
.ge_fc_pop1:
    mov dil, 0x5F            ; pop rdi
    call emit_byte
.ge_fc_call:
    call r46_live_callee_saved_vars
    mov r15, rax
    test r15, r15
    jz .ge_fc_saves_done
    ; B6: preserve caller variables held in r12-r15 across user calls.
    mov dil, 0x41             ; push r12
    call emit_byte
    mov dil, 0x54
    call emit_byte
    mov dil, 0x41             ; push r13
    call emit_byte
    mov dil, 0x55
    call emit_byte
    mov dil, 0x41             ; push r14
    call emit_byte
    mov dil, 0x56
    call emit_byte
    mov dil, 0x41             ; push r15
    call emit_byte
    mov dil, 0x57
    call emit_byte
.ge_fc_saves_done:
    ; Emit call rel32
    mov dil, 0xE8
    call emit_byte
    mov rax, [rel code_sz]
    mov rdx, [rel patch_count]
    cmp rdx, PATCH_LIST_CAP
    jae .ge_patch_overflow
    lea r8, [rel patch_list]
    push rdx
    shl rdx, 4
    mov [r8 + rdx], rax
    mov rax, [rbx+8]
    mov [r8 + rdx + 8], rax
    pop rdx
    inc qword [rel patch_count]
    xor edi, edi
    call emit_u32
    test r15, r15
    jz .ge_fc_restores_done
    mov dil, 0x41             ; pop r15
    call emit_byte
    mov dil, 0x5F
    call emit_byte
    mov dil, 0x41             ; pop r14
    call emit_byte
    mov dil, 0x5E
    call emit_byte
    mov dil, 0x41             ; pop r13
    call emit_byte
    mov dil, 0x5D
    call emit_byte
    mov dil, 0x41             ; pop r12
    call emit_byte
    mov dil, 0x5C
    call emit_byte
.ge_fc_restores_done:
    pop r14                   ; restore compiler-time r14
    pop r15                   ; restore compiler-time r15
    pop rbx
    ret
.ge_patch_overflow:
    lea rdi, [rel msg_patch_overflow]
    jmp capacity_fail

.ge_ternary:
    ; [AST_TERNARY][cond][true_expr][false_expr]
    push r12
    push r13
    push r14
    push r15
    mov rdi, rbx
    call expr_is_float
    mov r14, rax             ; common result type
    mov rax, [rbx+8]
    call gen_expr
    ; test rax, rax
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; je false
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x84
    call emit_byte
    mov r12, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; true expression
    mov rdi, [rbx+16]
    call expr_is_float
    mov r15, rax
    mov rax, [rbx+16]
    call gen_expr
    mov rdi, r15
    mov rsi, r14
    call emit_scalar_type_conversion
    ; jmp end
    mov dil, 0xE9
    call emit_byte
    mov r13, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; false target
    mov rax, [rel code_sz]
    sub rax, r12
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r12], eax
    mov rdi, [rbx+24]
    call expr_is_float
    mov r15, rax
    mov rax, [rbx+24]
    call gen_expr
    mov rdi, r15
    mov rsi, r14
    call emit_scalar_type_conversion
    ; end target
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r13], eax
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.ge_index:
    ; [AST_INDEX][name_ptr][index_node]
    ; Load variable (address), push base + runtime length, eval index, check.
    push r12
    mov rdi, [rbx+8]         ; variable name ptr
    call lookup_var          ; rax = location
    test rax, rax
    jle .ge_index_stack
    mov rdi, rax
    call emit_load_reg
    jmp .ge_index_have_addr
.ge_index_stack:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
.ge_index_have_addr:
    mov dil, 0x50            ; push rax (save base address)
    call emit_byte
    mov rdi, [rbx+8]
    call is_kosh_var
    test rax, rax
    jz .ge_index_check_pankti
    mov r12, 2               ; kosh length header at [ptr-16]
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    mov dil, 0x51
    call emit_byte
    jmp .ge_index_no_len
.ge_index_check_pankti:
    mov rdi, [rbx+8]
    call is_array_var
    mov r12, rax             ; 1=fixed pankti, 0=raw pointer
    test r12, r12
    jz .ge_index_no_len
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov dil, 0x51
    call emit_byte
.ge_index_no_len:
    mov rax, [rbx+16]
    push r12                  ; preserve compiler-time array marker
    call gen_expr             ; runtime index -> rax
    pop r12
    test r12, r12
    jz .ge_index_no_bounds
    call emit_array_bounds_check
    mov dil, 0x59            ; discard runtime length
    call emit_byte
.ge_index_no_bounds:
    mov dil, 0x48            ; shl rax, 3
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x03
    call emit_byte
    mov dil, 0x59            ; pop rcx (base)
    call emit_byte
    mov dil, 0x48            ; add rax, rcx
    call emit_byte
    mov dil, 0x01
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    mov dil, 0x48            ; mov rax, [rax]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x00
    call emit_byte
    pop r12
    pop rbx
    ret

.ge_field:
    ; [AST_FIELD][var_name][field_offset]
    ; Load var (base addr), add offset, load value
    mov rdi, [rbx+8]
    call lookup_var
    test rax, rax
    jle .ge_field_stk
    mov rdi, rax
    call emit_load_reg
    jmp .ge_field_have
.ge_field_stk:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
.ge_field_have:
    ; push rax (base address)
    mov dil, 0x50
    call emit_byte
    ; mov rax, field_offset (48 B8 + u64)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    ; Save offset in r14 (not used by gen_block/gen_expr)
    push r14
    mov r14, [rbx+16]
    mov rdi, r14
    call emit_u32
    shr r14, 32
    mov rdi, r14
    call emit_u32
    pop r14
    ; pop rcx (base address)
    mov dil, 0x59
    call emit_byte
    ; add rax, rcx (48 01 C8)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x01
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    ; mov rax, [rax] (48 8B 00)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x00
    call emit_byte
    pop rbx
    ret
.ge_field_stk3:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
    pop rbx
    ret

.ge_call:
    ; rbx = AST_CALL node: [8][builtin_id][arg_count][arg1][arg2]
    ; gen_expr emits CODE that leaves the value in rax at runtime.
    ; We emit push/pop to save args between evaluations.
    push r12
    mov r12, [rbx+8]         ; builtin id
    ; Check builtin type
    cmp r12, BN_PAD
    je .ge_call_pad
    cmp r12, BN_BAND
    je .ge_call_band
    cmp r12, BN_DVARAM
    je .ge_call_dvaram
    cmp r12, BN_PAADH
    je .ge_call_paadh
    cmp r12, BN_LIKHA
    je .ge_call_likha
    cmp r12, BN_NETSOCK
    je .ge_call_netsock
    cmp r12, BN_NETBIND
    je .ge_call_netbind
    cmp r12, BN_NETLIST
    je .ge_call_netlist
    cmp r12, BN_NETACC
    je .ge_call_netacc
    cmp r12, BN_NIRMRITA
    je .ge_call_nirm
    cmp r12, BN_LIKH8
    je .ge_call_likh8
    cmp r12, BN_PAD8
    je .ge_call_pad8
    cmp r12, BN_VARTLEN
    je .ge_call_vartlen
    cmp r12, BN_VARTCMP
    je .ge_call_vartcmp
    cmp r12, BN_VARTCAT
    je .ge_call_vartcat
    cmp r12, BN_VECADD
    je .ge_call_vecadd
    cmp r12, BN_VECMUL
    je .ge_call_vecmul
    cmp r12, BN_VECDOT
    je .ge_call_vecdot
    cmp r12, BN_LKFMT
    je .ge_call_lkfmt
    cmp r12, BN_CHARAT
    je .ge_call_charat
    cmp r12, BN_SETCHAR
    je .ge_call_setchar
    cmp r12, BN_CHARCD
    je .ge_call_charcd
    cmp r12, BN_CHARFR
    je .ge_call_charfr
    cmp r12, BN_CHARUP
    je .ge_call_charup
    cmp r12, BN_CHARLO
    je .ge_call_charlo
    cmp r12, BN_LIKH8C
    je .ge_call_likh8c
    cmp r12, BN_PAD8C
    je .ge_call_pad8c
    cmp r12, BN_MEMSET
    je .ge_call_memset
    cmp r12, BN_MEMCPY
    je .ge_call_memcpy
    cmp r12, BN_VARTCP
    je .ge_call_vartcp
    cmp r12, BN_GRAHAN
    je .ge_call_grahan
    cmp r12, BN_LKHB
    je .ge_call_lkhb
    cmp r12, BN_SHABDA
    je .ge_call_shabda
    cmp r12, BN_PANKTILEN
    je .ge_call_panktilen
    cmp r12, BN_KOSHPUSH
    je .ge_call_koshpush
    cmp r12, BN_KOSHPOP
    je .ge_call_koshpop
    cmp r12, BN_KOSHLEN
    je .ge_call_koshlen
    cmp r12, BN_KOSHCAP
    je .ge_call_koshcap
    ; Unknown — nop
    mov dil, 0x90
    call emit_byte
    jmp .ge_call_done

.ge_call_koshlen:
    cmp qword [rbx+16], 1
    jne .ge_call_kosh_bad
    mov rax, [rbx+24]
    cmp qword [rax], AST_VAR
    jne .ge_call_kosh_bad
    mov rdi, [rax+8]
    call is_kosh_var
    test rax, rax
    jz .ge_call_kosh_bad
    mov rax, [rbx+24]
    mov rdi, [rax+8]
    call emit_load_named_var
    mov dil, 0x48             ; mov rax,[rax-16]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x40
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    jmp .ge_call_done

.ge_call_koshcap:
    cmp qword [rbx+16], 1
    jne .ge_call_kosh_bad
    mov rax, [rbx+24]
    cmp qword [rax], AST_VAR
    jne .ge_call_kosh_bad
    mov rdi, [rax+8]
    call is_kosh_var
    test rax, rax
    jz .ge_call_kosh_bad
    mov rax, [rbx+24]
    mov rdi, [rax+8]
    call emit_load_named_var
    mov dil, 0x48             ; mov rax,[rax-8]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x40
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    jmp .ge_call_done

.ge_call_koshpop:
    cmp qword [rbx+16], 1
    jne .ge_call_kosh_bad
    mov rax, [rbx+24]
    cmp qword [rax], AST_VAR
    jne .ge_call_kosh_bad
    mov rdi, [rax+8]
    call is_kosh_var
    test rax, rax
    jz .ge_call_kosh_bad
    mov rax, [rbx+24]
    mov rdi, [rax+8]
    call emit_load_named_var
    mov dil, 0x49             ; mov r8,rax
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x4D             ; mov r9,[r8-16]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    call emit_kosh_empty_check_r9
    mov dil, 0x49             ; dec r9
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    mov dil, 0x4D             ; mov [r8-16],r9
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    mov dil, 0x4B             ; mov rax,[r8+r9*8]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    jmp .ge_call_done

.ge_call_koshpush:
    push r13
    push r14
    push r15
    cmp qword [rbx+16], 2
    jne .ge_call_koshpush_bad
    mov rax, [rbx+24]
    cmp qword [rax], AST_VAR
    jne .ge_call_koshpush_bad
    mov r13, [rax+8]         ; compiler-time kosh variable name
    mov rdi, r13
    call is_kosh_var
    test rax, rax
    jz .ge_call_koshpush_bad
    ; Parameters are pointer-by-value views. A grow operation could replace the
    ; callee's pointer without updating the caller, so kosh_push is rejected on
    ; parameters until a deliberate reference ABI is introduced.
    mov rdi, r13
    call is_kosh_param_var
    test rax, rax
    jnz .ge_call_koshpush_param_bad
    ; Evaluate value first, converting to the kosh element type, then preserve it
    ; on the generated runtime stack while capacity/growth is handled.
    mov rdi, [rbx+32]
    call expr_is_float
    mov r14, rax             ; source type
    mov rdi, r13
    call is_float_kosh_var
    mov r15, rax             ; target type
    push r14                 ; preserve compiler-time types across gen_expr
    push r15
    mov rax, [rbx+32]
    call gen_expr
    pop r15
    pop r14
    mov rdi, r14
    mov rsi, r15
    call emit_scalar_type_conversion
    mov dil, 0x50
    call emit_byte
    mov rdi, r13
    call emit_load_named_var
    ; r8=ptr, r9=len, r10=cap
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x50
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    mov dil, 0x4D             ; cmp r9,r10
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    mov dil, 0x0F             ; jb .space rel32
    call emit_byte
    mov dil, 0x82
    call emit_byte
    mov r15, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; newcap = cap ? cap*2 : 4
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD3
    call emit_byte
    mov dil, 0x49
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    mov dil, 0xE3
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov edi, 4
    call emit_u32
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xDB
    call emit_byte
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x44
    call emit_byte
    mov dil, 0xD8
    call emit_byte
    ; Preserve old pointer, length, and new capacity across allocation.
    mov dil, 0x41
    call emit_byte
    mov dil, 0x50
    call emit_byte
    mov dil, 0x41
    call emit_byte
    mov dil, 0x51
    call emit_byte
    mov dil, 0x41
    call emit_byte
    mov dil, 0x53
    call emit_byte
    mov dil, 0x4C             ; mov rax,r11
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD8
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x02
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x03
    call emit_byte
    call emit_nirmmita_from_rax
    mov dil, 0x41
    call emit_byte
    mov dil, 0x5B
    call emit_byte
    mov dil, 0x41
    call emit_byte
    mov dil, 0x59
    call emit_byte
    mov dil, 0x41
    call emit_byte
    mov dil, 0x58
    call emit_byte
    mov dil, 0x4C             ; mov [rax],r9
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x08
    call emit_byte
    mov dil, 0x4C             ; mov [rax+8],r11
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x58
    call emit_byte
    mov dil, 0x08
    call emit_byte
    mov dil, 0x4C             ; lea r10,[rax+16]
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x50
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov dil, 0x31             ; xor ecx,ecx
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    mov r14, [rel code_sz]
    mov dil, 0x4C             ; cmp rcx,r9
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    mov dil, 0x0F             ; jae copy_done rel32
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov r12, [rel code_sz]
    xor edi, edi
    call emit_u32
    mov dil, 0x49             ; mov rdx,[r8+rcx*8]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x14
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    mov dil, 0x49             ; mov [r10+rcx*8],rdx
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x14
    call emit_byte
    mov dil, 0xCA
    call emit_byte
    mov dil, 0x48             ; inc rcx
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE9             ; jmp copy_loop
    call emit_byte
    mov rax, r14
    sub rax, [rel code_sz]
    sub rax, 4
    mov edi, eax
    call emit_u32
    ; Patch jae to copy_done.
    mov rax, [rel code_sz]
    sub rax, r12
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx+r12], eax
    ; Update Sutram variable to new user pointer.
    mov dil, 0x4C             ; mov rax,r10
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov rdi, r13
    call emit_store_named_var
    mov dil, 0x4D             ; mov r8,r10
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    ; Patch initial jb to append path.
    mov rax, [rel code_sz]
    sub rax, r15
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx+r15], eax
    mov dil, 0x5A             ; pop value -> rdx
    call emit_byte
    mov dil, 0x4B             ; mov [r8+r9*8],rdx
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x14
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    mov dil, 0x49             ; inc r9
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0x4D             ; mov [r8-16],r9
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    mov dil, 0x4C             ; mov rax,r9
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    pop r15
    pop r14
    pop r13
    jmp .ge_call_done
.ge_call_koshpush_param_bad:
    pop r15
    pop r14
    pop r13
    lea rdi, [rel msg_kosh_param_push]
    jmp capacity_fail
.ge_call_koshpush_bad:
    pop r15
    pop r14
    pop r13
.ge_call_kosh_bad:
    lea rdi, [rel msg_kosh_required]
    jmp capacity_fail

.ge_call_lkhb:
    ; lkhb(x) = print number WITHOUT trailing newline
    ; Reuse likha's number code path with the no-newline flag set
    mov qword [rel lk_no_nl], 1
    jmp .ge_lk_3reg

.ge_call_grahan:
    ; Inline integer input parser.  Crucially, emit the read through
    ; emit_syscall so PE output reaches rt_syscall -> kernel32!ReadFile rather
    ; than executing a Linux 0F 05 instruction inside a Windows process.
    push r12
    push r13
    push r14
    lea r12, [rel grahan_prefix_bytes]
    xor r13, r13
.grahan_emit_prefix:
    cmp r13, GRAHAN_PREFIX_LEN
    jge .grahan_emit_read
    mov dil, [r12 + r13]
    call emit_byte
    inc r13
    jmp .grahan_emit_prefix
.grahan_emit_read:
    call emit_syscall
    cmp qword [rel target_pe], 0
    jne .grahan_use_pe_tail
    lea r12, [rel grahan_linux_tail]
    mov r14, GRAHAN_TAIL_LEN
    jmp .grahan_tail_ready
.grahan_use_pe_tail:
    lea r12, [rel grahan_pe_tail]
    mov r14, GRAHAN_PE_TAIL_LEN
.grahan_tail_ready:
    xor r13, r13
.grahan_emit_tail:
    cmp r13, r14
    jge .grahan_emit_done
    mov dil, [r12 + r13]
    call emit_byte
    inc r13
    jmp .grahan_emit_tail
.grahan_emit_done:
    pop r14
    pop r13
    pop r12
    jmp .ge_call_done

.ge_call_pad:
    ; pad(addr) -> byte value at address
    ; gen_expr(arg1) leaves addr in rax at runtime
    mov rax, [rbx+24]
    call gen_expr
    ; emit: mov rdi, rax (48 89 C7)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; emit: movzx rax, byte [rdi] (48 0F B6 07)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0x07
    call emit_byte
    jmp .ge_call_done

.ge_call_band:
    ; band(fd) -> sys_close(fd)=3
    ; gen_expr(arg1) leaves fd in rax at runtime
    mov rax, [rbx+24]
    call gen_expr
    ; emit: mov rdi, rax (48 89 C7)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; emit: mov eax, 3 (B8 03 00 00 00)
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x03
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; emit: syscall (0F 05)
    call emit_syscall
    jmp .ge_call_done

.ge_call_dvaram:
    ; dvaram(path, flags) -> fd (sys_open=2)
    ; gen_expr(arg1) → rax = path, push, gen_expr(arg2) → rax = flags
    mov rax, [rbx+24]
    call gen_expr
    ; emit: push rax (50)
    mov dil, 0x50
    call emit_byte
    ; gen_expr(arg2)
    mov rax, [rbx+32]
    call gen_expr
    ; emit: mov rsi, rax (48 89 C6)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; emit: pop rdi (5F)
    mov dil, 0x5F
    call emit_byte
    ; emit: mov eax, 2 (B8 02 00 00 00)
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x02
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; emit: syscall (0F 05)
    call emit_syscall
    jmp .ge_call_done

.ge_call_paadh:
    ; paadh(fd, buf, count) -> bytes_read (sys_read=0)
    ; 3 args: push arg1, push arg2, eval arg3 into rdx, pop rsi, pop rdi
    ; gen_expr(arg1) -> rax, push rax
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50            ; push rax
    call emit_byte
    ; gen_expr(arg2) -> rax, push rax
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50            ; push rax
    call emit_byte
    ; gen_expr(arg3) -> rax
    mov rax, [rbx+40]
    call gen_expr
    ; emit: mov rdx, rax (48 89 C2)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    ; emit: pop rsi (5E)
    mov dil, 0x5E
    call emit_byte
    ; emit: pop rdi (5F)
    mov dil, 0x5F
    call emit_byte
    ; emit: xor eax, eax (31 C0) — sys_read = 0
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; emit: syscall (0F 05)
    call emit_syscall
    jmp .ge_call_done

.ge_call_likha:
    ; arg counts: 1 = print value, 2 = print two values, 3 = sys_write(fd,buf,len)
    mov rax, [rbx+16]
    cmp rax, 1
    je .ge_lk_str
    cmp rax, 2
    je .ge_lk_two
    ; 3-arg form: likha(fd, buf, count)
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50
    call emit_byte
    mov rax, [rbx+40]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    mov dil, 0x5E
    call emit_byte
    mov dil, 0x5F
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    call emit_syscall
    jmp .ge_call_done
.ge_lk_two:
    ; likha(a, b): print a, then print b — synthesise two 1-arg likha calls
    mov rax, [rbx+24]
    push rax
    call alloc_ast
    pop rcx
    mov qword [rax], 8            ; AST_CALL
    mov qword [rax+8], BN_LIKHA
    mov qword [rax+16], 1
    mov [rax+24], rcx
    call gen_expr                 ; print(a)
    mov rax, [rbx+32]
    push rax
    call alloc_ast
    pop rcx
    mov qword [rax], 8
    mov qword [rax+8], BN_LIKHA
    mov qword [rax+16], 1
    mov [rax+24], rcx
    call gen_expr                 ; print(b)
    jmp .ge_call_done

.ge_call_shabda:
    ; shabda(s): print the NUL-terminated string whose address is in s
    ; (works for string variables, and for literals too)
    mov rax, [rbx+24]         ; arg node
    call gen_expr             ; rax = string address
    ; --- inline runtime printer (fixed 33 bytes) ---
    ; mov rsi, rax
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; xor rcx, rcx
    mov dil, 0x48
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    ; .scan: cmp byte [rsi+rcx], 0
    mov dil, 0x80
    call emit_byte
    mov dil, 0x3C
    call emit_byte
    mov dil, 0x0E
    call emit_byte
    xor edi, edi
    call emit_byte
    ; je .done (74 05)
    mov dil, 0x74
    call emit_byte
    mov dil, 0x05
    call emit_byte
    ; inc rcx
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; jmp .scan (EB F5)
    mov dil, 0xEB
    call emit_byte
    mov dil, 0xF5
    call emit_byte
    ; mov rdi, 1
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov rdx, rcx
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xCA
    call emit_byte
    ; mov rax, 1
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall
    call emit_syscall
    jmp .ge_call_done

.ge_lk_str:
    ; 1-arg string form: likha("text")
    mov rax, [rbx+24]
    mov rcx, [rax]
    cmp rcx, 14
    jne .ge_lk_maybe_float
    ; String literal — emit inline string + sys_write(1, str, len)
    push r12
    push r13
    mov r12, [rax+8]
    ; lea rax,[rip+2]: 48 8D 05 02 00 00 00
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x05
    call emit_byte
    mov dil, 0x02
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; strlen to get length
    mov rdi, r12
    call strlen
    mov r13, rax
    ; jmp rel8 = EB (len+1)
    mov dil, 0xEB
    call emit_byte
    mov edi, r13d
    add edi, 1
    call emit_byte
    ; emit string bytes
.ge_lk_sl:
    test r13, r13
    jz .ge_lk_sd
    movzx edi, byte [r12]
    call emit_byte
    inc r12
    dec r13
    jmp .ge_lk_sl
.ge_lk_sd:
    ; mov rdi, 1 (stdout) = 48 C7 C7 01 00 00 00
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov rsi, rax = 48 89 C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; mov rdx, <len> = BA xx 00 00 00
    mov dil, 0xBA
    call emit_byte
    ; re-compute length
    mov rax, [rbx+24]
    mov rax, [rax+8]
    push r12
    mov rdi, rax
    call strlen
    mov edi, eax
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    pop r12
    ; mov eax, 1 = B8 01 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall = 0F 05
    call emit_syscall
    pop r13
    pop r12
    jmp .ge_call_done
.ge_lk_maybe_float:
    mov rdi, [rbx+24]
    call expr_is_float
    test rax, rax
    jz .ge_lk_3reg
.ge_lk_float:
    mov rax, [rbx+24]
    call gen_expr
    push r12
    push r13
    lea r12, [rel float_print_prefix_bytes]
    xor r13, r13
.glf_prefix:
    cmp r13, FLOAT_PRINT_PREFIX_LEN
    jae .glf_syscall
    movzx edi, byte [r12+r13]
    call emit_byte
    inc r13
    jmp .glf_prefix
.glf_syscall:
    call emit_syscall
    lea r12, [rel float_print_suffix_bytes]
    xor r13, r13
.glf_suffix:
    cmp r13, FLOAT_PRINT_SUFFIX_LEN
    jae .glf_done
    movzx edi, byte [r12+r13]
    call emit_byte
    inc r13
    jmp .glf_suffix
.glf_done:
    pop r13
    pop r12
    jmp .ge_call_done

.ge_lk_3reg:
    ; Number printing: likha(42) or likha(x+1)
    ; Evaluate expression → rax has number at runtime
    mov rax, [rbx+24]
    call gen_expr
    ; Emit inline number-to-decimal + sys_write code
    ; mov r8, rax = 49 89 C0
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; sub rsp, 32 = 48 83 EC 20
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov dil, 0x20
    call emit_byte
    ; Sign check: if r8 is negative, print '-' and negate
    ; test r8, r8 = 4D 85 C0
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jns +28 (skip negation code) = 79 1C
    mov dil, 0x79
    call emit_byte
    mov dil, 0x1C
    call emit_byte
    ; neg r8 = 49 F7 D8
    mov dil, 0x49
    call emit_byte
    mov dil, 0xF7
    call emit_byte
    mov dil, 0xD8
    call emit_byte
    ; mov byte [rsp], 0x2D ('-') = C6 04 24 2D
    mov dil, 0xC6
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x2D
    call emit_byte
    ; mov eax, 1 = B8 01 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    call emit_byte
    call emit_byte
    ; mov edi, 1 = BF 01 00 00 00
    mov dil, 0xBF
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    call emit_byte
    call emit_byte
    ; lea rsi, [rsp] = 48 8D 34 24
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x34
    call emit_byte
    mov dil, 0x24
    call emit_byte
    ; mov edx, 1 = BA 01 00 00 00
    mov dil, 0xBA
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    call emit_byte
    call emit_byte
    ; syscall = 0F 05
    call emit_syscall
    ; lea rsi, [rsp+31] = 48 8D 74 24 1F
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x74
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x1F
    call emit_byte
    ; mov byte [rsi], 10 = C6 06 0A
    mov dil, 0xC6
    call emit_byte
    mov dil, 0x06
    call emit_byte
    mov dil, 0x0A
    call emit_byte
    ; dec rsi = 48 FF CE
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; test r8, r8 = 4D 85 C0
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jnz +8 = 75 08 (skip zero case, jump to loop at offset 31)
    mov dil, 0x75
    call emit_byte
    mov dil, 0x08
    call emit_byte
    ; mov byte [rsi], 0x30 = C6 06 30
    mov dil, 0xC6
    call emit_byte
    mov dil, 0x06
    call emit_byte
    mov dil, 0x30
    call emit_byte
    ; dec rsi = 48 FF CE (match loop's dec pattern)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; jmp +30 = EB 1E (skip to print section)
    mov dil, 0xEB
    call emit_byte
    mov dil, 0x1E
    call emit_byte
    ; --- LOOP START (offset 28) ---
    ; xor rdx, rdx = 48 31 D2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xD2
    call emit_byte
    ; mov rax, r8 = 4C 89 C0
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; mov ecx, 10 = B9 0A 00 00 00
    mov dil, 0xB9
    call emit_byte
    mov dil, 0x0A
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; div rcx = 48 F7 F1
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF7
    call emit_byte
    mov dil, 0xF1
    call emit_byte
    ; mov r8, rax = 49 89 C0
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; add dl, 0x30 = 80 C2 30
    mov dil, 0x80
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    mov dil, 0x30
    call emit_byte
    ; mov [rsi], dl = 88 16
    mov dil, 0x88
    call emit_byte
    mov dil, 0x16
    call emit_byte
    ; dec rsi = 48 FF CE
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; test r8, r8 = 4D 85 C0
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jnz -30 = 75 E2 (back to loop start)
    mov dil, 0x75
    call emit_byte
    mov dil, 0xE2
    call emit_byte
    ; --- PRINT SECTION (offset 58) ---
    ; lea rdx, [rsp+32] = 48 8D 54 24 20
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x54
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x20
    call emit_byte
    ; sub rdx, rsi = 48 29 F2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x29
    call emit_byte
    mov dil, 0xF2
    call emit_byte
    ; dec rdx = 48 FF CA
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCA
    call emit_byte
    ; lkhb: if no-newline flag set, emit one more dec rdx (skip the newline byte)
    cmp qword [rel lk_no_nl], 0
    je .lk_nl_ok
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCA
    call emit_byte
    mov qword [rel lk_no_nl], 0
.lk_nl_ok:
    ; inc rsi = 48 FF C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; mov rdi, 1 = 48 C7 C7 01 00 00 00
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov eax, 1 = B8 01 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall = 0F 05
    call emit_syscall
    ; add rsp, 32 = 48 83 C4 20
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC4
    call emit_byte
    mov dil, 0x20
    call emit_byte
    jmp .ge_call_done

.ge_call_netsock:
    ; netsock() → socket(AF_INET=2, SOCK_STREAM=1, 0)
    ; syscall 41: rdi=domain, rsi=type, rdx=protocol
    mov dil, 0xB8           ; mov eax, 41
    call emit_byte
    mov dil, 41
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov edi, 2 (AF_INET) = BF 02 00 00 00
    mov dil, 0xBF
    call emit_byte
    mov dil, 0x02
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov esi, 1 (SOCK_STREAM) = BE 01 00 00 00
    mov dil, 0xBE
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; xor edx, edx = 31 D2
    mov dil, 0x31
    call emit_byte
    mov dil, 0xD2
    call emit_byte
    ; syscall = 0F 05
    call emit_syscall
    jmp .ge_call_done

.ge_call_netbind:
    ; netbind(fd, port) → bind(fd, sockaddr_in, 16)
    ; Evaluate fd → push
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax
    call emit_byte
    ; Evaluate port → rax
    mov rax, [rbx+32]
    call gen_expr
    ; sub rsp, 16 = 48 83 EC 10
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov dil, 0x10
    call emit_byte
    ; mov word [rsp], 2 (AF_INET) = 66 C7 04 24 02 00
    mov dil, 0x66
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x02
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov cx, ax = 66 89 C1
    mov dil, 0x66
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; xchg cl, ch = 86 E9
    mov dil, 0x86
    call emit_byte
    mov dil, 0xE9
    call emit_byte
    ; mov [rsp+2], cx = 66 89 4C 24 02
    mov dil, 0x66
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x02
    call emit_byte
    ; mov dword [rsp+4], 0 = C7 44 24 04 00 00 00 00
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x44
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x04
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov qword [rsp+8], 0 = 48 C7 44 24 08 00 00 00 00
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x44
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x08
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov rsi, rsp = 48 89 E6
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xE6
    call emit_byte
    ; mov rdi, [rsp+16] = 48 8B 7C 24 10
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x7C
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x10
    call emit_byte
    ; mov edx, 16 = BA 10 00 00 00
    mov dil, 0xBA
    call emit_byte
    mov dil, 0x10
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov eax, 49 (sys_bind) = B8 31 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 49
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall = 0F 05
    call emit_syscall
    ; add rsp, 24 = 48 83 C4 18
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC4
    call emit_byte
    mov dil, 0x18
    call emit_byte
    jmp .ge_call_done

.ge_call_netlist:
    ; netlisten(fd) → listen(fd, 5)
    mov rax, [rbx+24]
    call gen_expr
    ; mov rdi, rax = 48 89 C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; mov esi, 5 = BE 05 00 00 00
    mov dil, 0xBE
    call emit_byte
    mov dil, 0x05
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov eax, 50 (sys_listen) = B8 32 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 50
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall
    call emit_syscall
    jmp .ge_call_done

.ge_call_netacc:
    ; netaccept(fd) → accept(fd, 0, 0)
    mov rax, [rbx+24]
    call gen_expr
    ; mov rdi, rax = 48 89 C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; xor esi, esi = 31 F6
    mov dil, 0x31
    call emit_byte
    mov dil, 0xF6
    call emit_byte
    ; xor edx, edx = 31 D2
    mov dil, 0x31
    call emit_byte
    mov dil, 0xD2
    call emit_byte
    ; mov eax, 43 (sys_accept) = B8 2B 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 43
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall
    call emit_syscall
    jmp .ge_call_done

.ge_call_nirm:
    ; nirmmita(size) → mmap(0, size, 3, 0x22, -1, 0)
    mov rax, [rbx+24]
    call gen_expr
    call emit_nirmmita_from_rax
    jmp .ge_call_done

.ge_call_likh8:
    ; likh8(addr, val) → mov [rdi], rsi
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (save addr)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    ; pop rdi (addr) = 5F
    mov dil, 0x5F
    call emit_byte
    ; mov rsi, rax (val) = 48 89 C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; mov [rdi], rsi = 48 89 37
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x37
    call emit_byte
    jmp .ge_call_done

.ge_call_pad8:
    ; pad8(addr) → mov rax, [rdi]
    mov rax, [rbx+24]
    call gen_expr
    ; mov rdi, rax = 48 89 C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; mov rax, [rdi] = 48 8B 07
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x07
    call emit_byte
    jmp .ge_call_done

.ge_call_panktilen:
    ; T8b: real pankti declarations carry a hidden runtime length header.
    ; Preserve historical behavior for arbitrary/raw pointers: pankti_len(p)
    ; is 0 unless p is a pankti variable in this generated function scope.
    mov rax, [rbx+24]
    cmp qword [rax], AST_VAR
    jne .ge_call_panktilen_zero
    mov rdi, [rax+8]
    call is_array_var
    test rax, rax
    jz .ge_call_panktilen_zero
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x48             ; mov rax, [rax-8]
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x40
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    jmp .ge_call_done
.ge_call_panktilen_zero:
    mov dil, 0x48             ; xor rax, rax
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    jmp .ge_call_done

.ge_call_vartlen:
    ; vartani_len(str) → inline strlen, rax = length
    mov rax, [rbx+24]
    call gen_expr
    ; mov rdi, rax = 48 89 C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; xor ecx, ecx = 31 C9
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    ; cmp byte [rdi], 0 = 80 3F 00
    mov dil, 0x80
    call emit_byte
    mov dil, 0x3F
    call emit_byte
    xor edi, edi
    call emit_byte
    ; je +8 = 74 08
    mov dil, 0x74
    call emit_byte
    mov dil, 0x08
    call emit_byte
    ; inc rdi = 48 FF C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; inc rcx = 48 FF C1
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; jmp -13 = EB F3
    mov dil, 0xEB
    call emit_byte
    mov dil, 0xF3
    call emit_byte
    ; mov rax, rcx = 48 89 C8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    jmp .ge_call_done

.ge_call_vartcmp:
    ; vartani_cmp(s1, s2) → 0 if equal, 1 if not
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (s1)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    ; pop rdi (s1) = 5F
    mov dil, 0x5F
    call emit_byte
    ; mov rsi, rax (s2) = 48 89 C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; movzx ecx, [rdi] = 0F B6 0F
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    ; movzx edx, [rsi] = 0F B6 16
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0x16
    call emit_byte
    ; cmp ecx, edx = 39 D1
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    ; jne +16 = 75 10
    mov dil, 0x75
    call emit_byte
    mov dil, 0x10
    call emit_byte
    ; test ecx, ecx = 85 C9
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    ; jz +8 = 74 08
    mov dil, 0x74
    call emit_byte
    mov dil, 0x08
    call emit_byte
    ; inc rdi = 48 FF C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; inc rsi = 48 FF C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; jmp -22 = EB EA
    mov dil, 0xEB
    call emit_byte
    mov dil, 0xEA
    call emit_byte
    ; xor eax, eax (equal) = 31 C0
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jmp +5 = EB 05
    mov dil, 0xEB
    call emit_byte
    mov dil, 0x05
    call emit_byte
    ; mov eax, 1 (not equal) = B8 01 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    jmp .ge_call_done

.ge_call_vartcat:
    ; vartani_cat(dst, src) → strcat, returns dst
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (dst)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    ; pop rdi (dst) = 5F
    mov dil, 0x5F
    call emit_byte
    ; mov rsi, rax (src) = 48 89 C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; mov r8, rdi (save dst) = 49 89 F8
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    ; cmp byte [rdi], 0 = 80 3F 00
    mov dil, 0x80
    call emit_byte
    mov dil, 0x3F
    call emit_byte
    xor edi, edi
    call emit_byte
    ; je +5 = 74 05
    mov dil, 0x74
    call emit_byte
    mov dil, 0x05
    call emit_byte
    ; inc rdi = 48 FF C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; jmp -10 = EB F6
    mov dil, 0xEB
    call emit_byte
    mov dil, 0xF6
    call emit_byte
    ; movzx ecx, [rsi] = 0F B6 0E
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0x0E
    call emit_byte
    ; mov [rdi], cl = 88 0F
    mov dil, 0x88
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    ; test ecx, ecx = 85 C9
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    ; jz +8 = 74 08
    mov dil, 0x74
    call emit_byte
    mov dil, 0x08
    call emit_byte
    ; inc rdi = 48 FF C7
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    ; inc rsi = 48 FF C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; jmp -17 = EB EF
    mov dil, 0xEB
    call emit_byte
    mov dil, 0xEF
    call emit_byte
    ; mov rax, r8 (return dst) = 4C 89 C0
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    jmp .ge_call_done

.ge_call_vecadd:
    ; sankhya_yog(dst, src1, src2) — vaddps xmm0, xmm1, xmm2
    ; All 3 args are pointers to 16-byte aligned vectors
    ; Evaluate arg1 (dst) → push
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax
    call emit_byte
    ; Evaluate arg2 (src1) → push
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50           ; push rax
    call emit_byte
    ; Evaluate arg3 (src2)
    mov rax, [rbx+40]
    call gen_expr
    ; mov rdx, rax (src2) = 48 89 C2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    ; pop rsi (src1) = 5E
    mov dil, 0x5E
    call emit_byte
    ; pop rdi (dst) = 5F
    mov dil, 0x5F
    call emit_byte
    ; movups xmm0, [rsi] = 0F 10 06
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov dil, 0x06
    call emit_byte
    ; movups xmm1, [rdx] = 0F 10 0A
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov dil, 0x0A
    call emit_byte
    ; addps xmm0, xmm1 = 0F 58 C1
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x58
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; movups [rdi], xmm0 = 0F 11 07
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x11
    call emit_byte
    mov dil, 0x07
    call emit_byte
    ; mov rax, rdi (return dst) = 48 89 F8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    jmp .ge_call_done

.ge_call_vecmul:
    ; sankhya_gunan(dst, src1, src2) — vmulps
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50
    call emit_byte
    mov rax, [rbx+40]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    mov dil, 0x5E
    call emit_byte
    mov dil, 0x5F
    call emit_byte
    ; movups xmm0, [rsi] = 0F 10 06
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov dil, 0x06
    call emit_byte
    ; movups xmm1, [rdx] = 0F 10 0A
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov dil, 0x0A
    call emit_byte
    ; mulps xmm0, xmm1 = 0F 59 C1
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x59
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; movups [rdi], xmm0 = 0F 11 07
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x11
    call emit_byte
    mov dil, 0x07
    call emit_byte
    ; mov rax, rdi
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    jmp .ge_call_done

.ge_call_vecdot:
    ; sankhya_dot(src1, src2) — dot product via dpps
    ; Returns scalar float in xmm0 (low 32 bits)
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    ; mov rdx, rax (src2) = 48 89 C2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    ; pop rsi (src1) = 5E
    mov dil, 0x5E
    call emit_byte
    ; movups xmm0, [rsi] = 0F 10 06
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov dil, 0x06
    call emit_byte
    ; movups xmm1, [rdx] = 0F 10 0A
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x10
    call emit_byte
    mov dil, 0x0A
    call emit_byte
    ; mulps xmm0, xmm1 = 0F 59 C1
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x59
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; haddps xmm0, xmm0 = 66 0F 7C C0
    mov dil, 0x66
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7C
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; haddps xmm0, xmm0 = 66 0F 7C C0
    mov dil, 0x66
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7C
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; movd eax, xmm0 = 66 0F 7E C0
    mov dil, 0x66
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7E
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; Return float bits in rax (as integer representation)
    jmp .ge_call_done

.ge_call_setchar:
    ; R50 set_char(buffer, byte_index, integer_value).
    ; Evaluate each argument exactly once, left-to-right.
    ; 1-byte stride; store ONLY value's low eight bits. Return 0..255.
    ; Caller must provide writable storage and a valid byte offset.
    ; qword-stride buf[i]=v and char_at(...) remain UNCHANGED.
    cmp qword [rbx+16], 3
    jne .ge_call_setchar_arity
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50             ; push rax (buffer)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50             ; push rax (index)
    call emit_byte
    mov rax, [rbx+40]
    call gen_expr
    mov dil, 0x5A             ; pop rdx (index)
    call emit_byte
    mov dil, 0x59             ; pop rcx (buffer)
    call emit_byte
    ; mov byte [rcx+rdx],al: 88 04 11 (SIB: scale1,rdx,rcx)
    mov dil, 0x88
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0x11
    call emit_byte
    ; movzx eax, al — return stored low byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    jmp .ge_call_done
.ge_call_setchar_arity:
    lea rdi, [rel r50_msg_setchar_arity]
    jmp capacity_fail

.ge_call_charat:
    ; char_at(str, index) → byte at str[index] in rax
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (str)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    ; mov rdx, rax (index) = 48 89 C2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    ; pop rdi (str) = 5F
    mov dil, 0x5F
    call emit_byte
    ; movzx eax, byte [rdi+rdx] = 0F B6 04 17
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0x17
    call emit_byte
    jmp .ge_call_done

.ge_call_charcd:
    ; B3: char_code(str, index) returns the indexed byte.  Keep the historical
    ; one-argument form as char_code(str, 0) for compatibility.
    cmp qword [rbx+16], 2
    jb .ge_call_charcd_first
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (str)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x48           ; mov rdx, rax
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    mov dil, 0x5F           ; pop rdi
    call emit_byte
    mov dil, 0x0F           ; movzx eax, byte [rdi+rdx]
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0x17
    call emit_byte
    jmp .ge_call_done
.ge_call_charcd_first:
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x0F           ; movzx eax, byte [rax]
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    xor edi, edi
    call emit_byte
    jmp .ge_call_done

.ge_call_charfr:
    ; char_from(code) → pointer to a char (writes code to a temp buffer)
    ; Uses a static 1-byte buffer in BSS
    mov rax, [rbx+24]
    call gen_expr
    ; lea rdi, [rel char_buf] — we need the runtime address
    ; But lea [rel] in generated code needs the address at link time
    ; Instead: mov [rsp-1], al; lea rax, [rsp-1]
    ; sub rsp, 16 = 48 83 EC 10
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov dil, 0x10
    call emit_byte
    ; mov [rsp], al = 88 04 24
    mov dil, 0x88
    call emit_byte
    mov dil, 0x04
    call emit_byte
    mov dil, 0x24
    call emit_byte
    ; mov byte [rsp+1], 0 = C6 44 24 01 00
    mov dil, 0xC6
    call emit_byte
    mov dil, 0x44
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov rax, rsp = 48 89 E0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    ; add rsp, 8 (preserve the byte for return) = 48 83 C4 08
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC4
    call emit_byte
    mov dil, 0x08
    call emit_byte
    jmp .ge_call_done

.ge_call_charup:
    ; char_upper(ch) → uppercase ASCII letter code
    mov rax, [rbx+24]
    call gen_expr
    ; cmp al, 'a' = 3C 61
    mov dil, 0x3C
    call emit_byte
    mov dil, 0x61
    call emit_byte
    ; jl skip (small letter) = 7C 06
    mov dil, 0x7C
    call emit_byte
    mov dil, 0x06
    call emit_byte
    ; cmp al, 'z' = 3C 7A
    mov dil, 0x3C
    call emit_byte
    mov dil, 0x7A
    call emit_byte
    ; jg skip = 7F 02
    mov dil, 0x7F
    call emit_byte
    mov dil, 0x02
    call emit_byte
    ; sub al, 32 = 2C 20
    mov dil, 0x2C
    call emit_byte
    mov dil, 0x20
    call emit_byte
    jmp .ge_call_done

.ge_call_charlo:
    ; char_lower(ch) → lowercase ASCII letter code
    mov rax, [rbx+24]
    call gen_expr
    ; cmp al, 'A' = 3C 41
    mov dil, 0x3C
    call emit_byte
    mov dil, 0x41
    call emit_byte
    ; jl skip = 7C 06
    mov dil, 0x7C
    call emit_byte
    mov dil, 0x06
    call emit_byte
    ; cmp al, 'Z' = 3C 5A
    mov dil, 0x3C
    call emit_byte
    mov dil, 0x5A
    call emit_byte
    ; jg skip = 7F 02
    mov dil, 0x7F
    call emit_byte
    mov dil, 0x02
    call emit_byte
    ; add al, 32 = 04 20
    mov dil, 0x04
    call emit_byte
    mov dil, 0x20
    call emit_byte
    jmp .ge_call_done

.ge_call_likh8c:
    ; likh8c(addr, val, bound) — bounds-checked write
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (addr)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50           ; push rax (val)
    call emit_byte
    mov rax, [rbx+40]
    call gen_expr
    ; mov rdx, rax (bound) = 48 89 C2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    ; pop rsi (val) = 5E
    mov dil, 0x5E
    call emit_byte
    ; pop rdi (addr) = 5F
    mov dil, 0x5F
    call emit_byte
    ; cmp rdi, rdx = 48 39 D7
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD7
    call emit_byte
    ; jae +3 (skip mov [rdi],rsi) = 73 03
    mov dil, 0x73
    call emit_byte
    mov dil, 0x03
    call emit_byte
    ; mov [rdi], rsi = 48 89 37
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x37
    call emit_byte
    jmp .ge_call_done

.ge_call_pad8c:
    ; pad8c(addr, bound) — bounds-checked read
    ; If addr >= bound, return 0 (prevent out-of-bounds read)
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (addr)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    ; mov rdx, rax (bound) = 48 89 C2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    ; pop rdi (addr) = 5F
    mov dil, 0x5F
    call emit_byte
    ; cmp rdi, rdx = 48 39 D7
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD7
    call emit_byte
    ; jae +8 (skip to xor eax) = 73 08
    mov dil, 0x73
    call emit_byte
    mov dil, 0x08
    call emit_byte
    ; mov rax, [rdi] = 48 8B 07
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x07
    call emit_byte
    ; jmp +2 (skip xor eax) = EB 02
    mov dil, 0xEB
    call emit_byte
    mov dil, 0x02
    call emit_byte
    ; xor eax, eax (out of bounds = 0) = 31 C0
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    jmp .ge_call_done

.ge_call_memset:
    ; smaran(dst, val, count) — fill memory with byte value
    ; Uses rep stosb
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (dst)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50           ; push rax (val)
    call emit_byte
    mov rax, [rbx+40]
    call gen_expr
    ; mov rcx, rax (count) = 48 89 C1
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; pop rax (val) = 58
    mov dil, 0x58
    call emit_byte
    ; pop rdi (dst) = 5F
    mov dil, 0x5F
    call emit_byte
    ; mov al, al (already there) — rep stosb uses al
    ; rep stosb = F3 AA
    mov dil, 0xF3
    call emit_byte
    mov dil, 0xAA
    call emit_byte
    jmp .ge_call_done

.ge_call_memcpy:
    ; smaran_cp(dst, src, count) — copy memory
    ; Uses rep movsb
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (dst)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    mov dil, 0x50           ; push rax (src)
    call emit_byte
    mov rax, [rbx+40]
    call gen_expr
    ; mov rcx, rax (count) = 48 89 C1
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; pop rsi (src) = 5E
    mov dil, 0x5E
    call emit_byte
    ; pop rdi (dst) = 5F
    mov dil, 0x5F
    call emit_byte
    ; rep movsb = F3 A4
    mov dil, 0xF3
    call emit_byte
    mov dil, 0xA4
    call emit_byte
    jmp .ge_call_done

.ge_call_vartcp:
    ; vartani_cp(dst, src) — strcpy (copies until null)
    mov rax, [rbx+24]
    call gen_expr
    mov dil, 0x50           ; push rax (dst)
    call emit_byte
    mov rax, [rbx+32]
    call gen_expr
    ; mov rsi, rax (src) = 48 89 C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; pop rdi (dst) = 5F
    mov dil, 0x5F
    call emit_byte
    ; mov rcx, -1 = 48 C7 C1 FF FF FF FF
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    ; xor eax, eax = 31 C0
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; repne scasb = F2 AE
    mov dil, 0xF2
    call emit_byte
    mov dil, 0xAE
    call emit_byte
    ; not rcx = 48 F7 D1
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF7
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    ; dec rcx = 48 FF C9
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    ; sub rsi, rcx = 48 29 CE (adjust src back)
    mov dil, 0x48
    call emit_byte
    mov dil, 0x29
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; add rsi, rcx = 48 01 CE
    mov dil, 0x48
    call emit_byte
    mov dil, 0x01
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; rep movsb = F3 A4
    mov dil, 0xF3
    call emit_byte
    mov dil, 0xA4
    call emit_byte
    ; mov rax, rdi (return dst) = 48 89 F8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    jmp .ge_call_done

.ge_call_lkfmt:
    ; likha_fmt(fmt, arg1) — simple format: prints fmt string,
    ; replacing {0} with integer arg1 as decimal
    ; For now: print the format string, then print the number
    ; (simplified — no actual substitution, just sequential print)
    ; Check if arg1 is AST_STR
    mov rax, [rbx+24]
    mov rcx, [rax]
    cmp rcx, 14              ; AST_STR
    jne .ge_lkfmt_numonly
    ; It's a string format — print it, then print arg2 as number
    push r12
    push r13
    mov r12, [rax+8]         ; r12 = format string pointer
    ; Emit lea rax,[rip+2] for the format string
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x05
    call emit_byte
    mov dil, 0x02
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; strlen for jmp offset
    mov rdi, r12
    call strlen
    mov r13, rax
    ; jmp rel8
    mov dil, 0xEB
    call emit_byte
    mov edi, r13d
    add edi, 1
    call emit_byte
    ; emit string bytes
.ge_lf_sl:
    test r13, r13
    jz .ge_lf_sd
    movzx edi, byte [r12]
    call emit_byte
    inc r12
    dec r13
    jmp .ge_lf_sl
.ge_lf_sd:
    ; Now emit sys_write for the format string
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    mov dil, 0xBA
    call emit_byte
    mov rax, [rbx+24]
    mov rax, [rax+8]
    push r12
    mov rdi, rax
    call strlen
    mov edi, eax
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    pop r12
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    call emit_syscall
    ; Now print arg2 as number (inline the number printing code)
    mov rax, [rbx+32]
    call gen_expr
    ; mov r8, rax = 49 89 C0
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; sub rsp, 32 = 48 83 EC 20
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov dil, 0x20
    call emit_byte
    ; lea rsi, [rsp+31] = 48 8D 74 24 1F
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x74
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x1F
    call emit_byte
    ; mov byte [rsi], 10 = C6 06 0A
    mov dil, 0xC6
    call emit_byte
    mov dil, 0x06
    call emit_byte
    mov dil, 0x0A
    call emit_byte
    ; dec rsi = 48 FF CE
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; test r8, r8 = 4D 85 C0
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jnz +8 = 75 08
    mov dil, 0x75
    call emit_byte
    mov dil, 0x08
    call emit_byte
    ; mov byte [rsi], 0x30
    mov dil, 0xC6
    call emit_byte
    mov dil, 0x06
    call emit_byte
    mov dil, 0x30
    call emit_byte
    ; dec rsi = 48 FF CE
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; jmp +30 = EB 1E
    mov dil, 0xEB
    call emit_byte
    mov dil, 0x1E
    call emit_byte
    ; xor rdx, rdx = 48 31 D2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xD2
    call emit_byte
    ; mov rax, r8 = 4C 89 C0
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; mov ecx, 10 = B9 0A 00 00 00
    mov dil, 0xB9
    call emit_byte
    mov dil, 0x0A
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; div rcx = 48 F7 F1
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF7
    call emit_byte
    mov dil, 0xF1
    call emit_byte
    ; mov r8, rax = 49 89 C0
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; add dl, 0x30 = 80 C2 30
    mov dil, 0x80
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    mov dil, 0x30
    call emit_byte
    ; mov [rsi], dl = 88 16
    mov dil, 0x88
    call emit_byte
    mov dil, 0x16
    call emit_byte
    ; dec rsi = 48 FF CE
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCE
    call emit_byte
    ; test r8, r8 = 4D 85 C0
    mov dil, 0x4D
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jnz -30 = 75 E2
    mov dil, 0x75
    call emit_byte
    mov dil, 0xE2
    call emit_byte
    ; lea rdx, [rsp+32] = 48 8D 54 24 20
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x54
    call emit_byte
    mov dil, 0x24
    call emit_byte
    mov dil, 0x20
    call emit_byte
    ; sub rdx, rsi = 48 29 F2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x29
    call emit_byte
    mov dil, 0xF2
    call emit_byte
    ; dec rdx = 48 FF CA
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xCA
    call emit_byte
    ; inc rsi = 48 FF C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; mov rdi, 1 = 48 C7 C7 01 00 00 00
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov eax, 1 = B8 01 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x01
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall = 0F 05
    call emit_syscall
    ; add rsp, 32 = 48 83 C4 20
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC4
    call emit_byte
    mov dil, 0x20
    call emit_byte
    pop r13
    pop r12
    jmp .ge_call_done
.ge_lkfmt_numonly:
    ; Non-string first arg — just evaluate as expression
    mov rax, [rbx+24]
    call gen_expr
    jmp .ge_call_done

.ge_call_done:
    pop r12
    pop rbx
    ret

.ge_vec:
    ; rbx = AST_VEC node with 4 integer values at [rbx+16], [rbx+24], [rbx+32], [rbx+40]
    ; Convert to IEEE 754 single-precision floats and emit inline
    ; Then emit vmovups xmm0, [rip+offset] to load them
    ;
    ; Pattern: lea rax, [rip+2]; jmp +18; <16 bytes float data>
    ; Actually we don't need lea — we load into xmm0 directly:
    ; vmovups xmm0, [rip+2]; jmp +18; <16 bytes of float data>
    ;
    ; vmovups xmm0, [rip+disp32] = C5 F8 10 05 <disp32> = 8 bytes
    ; jmp rel8 = EB 12 (skip 18 bytes of float data)
    ; Then 16 bytes of float data (4 x float32)
    push r12
    push r13
    ; Emit vmovups xmm0, [rip+10] — disp32 = 10 (past jmp)
    ; Actually: vmovups is 8 bytes, jmp is 2 bytes = 10 bytes before data
    ; rip at end of vmovups points to jmp, rip+2 points past jmp to data
    mov dil, 0xC5              ; VEX prefix byte 1
    call emit_byte
    mov dil, 0xF8              ; VEX prefix byte 2 (vvvv=1111, L=0, pp=00)
    call emit_byte
    mov dil, 0x10              ; opcode: vmovups
    call emit_byte
    mov dil, 0x05              ; ModRM: mod=00, reg=000(xmm0), rm=101(RIP)
    call emit_byte
    mov dil, 0x02              ; disp32 = 2 (past the 2-byte jmp)
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; Emit jmp rel8 = EB 10 (skip 16 bytes of float data)
    mov dil, 0xEB
    call emit_byte
    mov dil, 0x10              ; 16 bytes to skip
    call emit_byte
    ; Now emit 16 bytes of float data
    ; Convert 4 integers to IEEE 754 single-precision floats
    ; Integer 0 = float 0.0 = 0x00000000
    ; Integer 1 = float 1.0 = 0x3F800000
    ; Integer 2 = float 2.0 = 0x40000000
    ; Integer N = float N.0 (for small integers, we can use a lookup or conversion)
    ;
    ; Simple conversion for small positive integers:
    ; float = sign(0) + exponent(127+bits) + mantissa
    ; For integer N: exponent = 127 + floor(log2(N)), mantissa = shifted fraction
    ; This is complex. Instead, let's emit the raw 32-bit float representation.
    ; We'll use cvtsi2ss at RUNTIME to convert, but that requires an XMM register.
    ;
    ; Simpler approach: emit the 4 integers as-is (they'll be interpreted as floats).
    ; For integer 1: as float bits 0x00000001 = denormalized tiny number ≈ 0
    ; That won't work.
    ;
    ; Best approach: emit code to convert at runtime using cvtsi2ss
    ; But that's complex. For now, let's just emit the 4 raw 32-bit values.
    ; The user will see that AVX loads 4 values in parallel — the values happen to be integers
    ; but they're loaded as 128-bit packed data.
    ;
    ; Actually, the simplest approach: emit the 4 values as 32-bit integers.
    ; They'll be loaded as a 128-bit value. For integer arithmetic (not float),
    ; we can use vpaddd (packed add doubleword) instead of vaddps.
    ; This gives us SIMD integer vector addition!
    ;
    ; Let's use vpaddd for integer vectors:
    ; vpaddd xmm0, xmm1, xmm2 = VEX.128.66.0F.WIG EF /r
    ; pp = 01 (66 prefix), opcode = EF
    ; VEX byte2 = vvvv(inverted) L(0) pp(01)
    ;
    ; For loading: vmovdqa or vmovdqu (aligned/unaligned)
    ; vmovdqu xmm0, [rip+disp32] = VEX.128.F3.0F 6F /r
    ; pp = 10 (F3 prefix)
    ;
    ; Let me redo the load with vmovdqu:
    ; Actually I already emitted vmovups. Let me keep it — it works for both int and float.
    ; vmovups loads 128 bits regardless of interpretation.
    ;
    ; Emit 4 x 32-bit values (little-endian)
    mov r12, [rbx+16]          ; val1
    mov r13, [rbx+24]          ; val2
    ; Emit val1 as 4 bytes (avoid ah — use shift instead)
    mov rax, r12
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    ; Emit val2 as 4 bytes
    mov rax, r13
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    ; Emit val3
    mov rax, [rbx+32]
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    ; Emit val4
    mov rax, [rbx+40]
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    shr rax, 8
    mov dil, al
    call emit_byte
    pop r13
    pop r12
    pop rbx
    ret

.ge_str:
    ; rbx = AST_STR node, [rbx+8] = string pointer
    push r12
    push r13
    mov r12, [rbx+8]          ; r12 = string pointer (preserved by emit_byte)
    ; Emit lea rax,[rip+2]: 48 8D 05 02 00 00 00
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x05
    call emit_byte
    mov dil, 0x02
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; Compute string length for jmp offset
    mov rdi, r12
    call strlen               ; rax = length
    mov r13, rax              ; r13 = length (preserved by emit_byte)
    ; Emit jmp rel8 = EB (length+1)
    mov dil, 0xEB
    call emit_byte
    mov edi, r13d
    add edi, 1
    call emit_byte
    ; Emit string bytes + null terminator
.ge_str_loop:
    test r13, r13
    jz .ge_str_null
    movzx edi, byte [r12]
    call emit_byte
    inc r12
    dec r13
    jmp .ge_str_loop
.ge_str_null:
    xor edi, edi
    call emit_byte
    pop r13
    pop r12
    pop rbx
    ret

.ge_float:
    ; T12: values travel through the existing 64-bit scalar ABI as raw bits.
    mov dil, 0x48            ; mov rax, imm64
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    mov rdi, [rbx+8]
    call emit_u64
    pop rbx
    ret

.ge_num:
    ; PERF3: a non-negative literal that fits uint32 needs one instruction:
    ; mov eax,imm32 (architecturally zero-extends into RAX).  The previous
    ; xor rax,rax + mov al,N sequence was two instructions for small values.
    mov rax, [rbx+8]
    mov rcx, rax
    shr rcx, 32
    jnz .ge_num_full
    mov dil, 0xB8
    call emit_byte
    mov edi, dword [rbx+8]
    call emit_u32
    pop rbx
    ret
.ge_num_full:
    ; mov rax, imm64 (10 bytes)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xB8
    call emit_byte
    mov rdi, [rbx+8]
    call emit_u64
    pop rbx
    ret

.ge_var:
    mov rdi, [rbx+8]         ; name ptr
    call lookup_var           ; rax = location
    ; Check if register or stack
    test rax, rax
    jle .ge_var_stack
    ; Register: emit mov rax, reg
    mov rdi, rax
    call emit_load_reg
    pop rbx
    ret
.ge_var_stack:
    ; Stack: mov rax, [rbp+offset]
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
    pop rbx
    ret

.ge_binop:
    ; [AST_BINOP][op][left][right]
    ; PERF-FC1: register-only scalar float comparisons. Preserve the exact
    ; existing UCOMISD/SETcc semantics but remove the runtime stack spill.
    mov rdi, rbx
    call try_emit_float_reg_compare
    test rax, rax
    jz .ge_binop_general
    pop rbx
    ret
.ge_binop_general:
    ; T12 float arithmetic/comparison is selected before integer fast paths.
    mov rdi, rbx
    call binop_needs_float
    test rax, rax
    jnz .ge_fbinop
    ; Logical && / || require true short-circuit evaluation. Handle them
    ; before the generic binary path, which necessarily evaluates both sides.
    ; All non-logical operators continue through the byte-identical old paths.
    push rbx
    mov rax, [rbx+8]         ; operator
    cmp rax, OP_LAND
    je .ge_binop_land_sc
    cmp rax, OP_LOR
    je .ge_binop_lor_sc
    ; FAST PATH: If right is AST_NUM and op is ADD/SUB, emit add/sub rax, imm8
    mov rax, [rbx+24]        ; right operand node
    mov rcx, [rax]           ; right node type
    cmp rcx, AST_NUM
    jne .ge_binop_generic
    ; Right is a number — check if value fits in imm8 (0-127)
    mov rcx, [rax+8]         ; right value
    cmp rcx, 127
    ja .ge_binop_generic
    ; Check if op is ADD or SUB
    mov rax, [rbx+8]         ; operator
    cmp rax, OP_ADD
    je .ge_binop_add_imm
    cmp rax, OP_SUB
    je .ge_binop_sub_imm
    cmp rax, OP_MUL
    je .ge_binop_mul_imm
    jmp .ge_binop_generic
.ge_binop_land_sc:
    ; Undo .ge_binop's extra save; gen_expr's entry save remains on stack.
    pop rbx
    push r12
    push r13
    ; Evaluate left first.
    mov rax, [rbx+16]
    call gen_expr
    ; test rax, rax
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; je false_label (rel32 patched after the RHS code is emitted)
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x84
    call emit_byte
    mov r12, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; Left was true: only now evaluate the RHS.
    mov rax, [rbx+24]
    call gen_expr
    ; Normalize RHS to 0/1: test rax,rax; setne al; movzx rax,al
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x95
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jmp done (skip the false result materialization)
    mov dil, 0xE9
    call emit_byte
    mov r13, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; false_label: patch JE and produce canonical false (0).
    mov rax, [rel code_sz]
    sub rax, r12
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r12], eax
    ; xor eax, eax
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; done: patch the unconditional jump.
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r13], eax
    pop r13
    pop r12
    pop rbx
    ret

.ge_binop_lor_sc:
    ; Undo .ge_binop's extra save; gen_expr's entry save remains on stack.
    pop rbx
    push r12
    push r13
    ; Evaluate left first.
    mov rax, [rbx+16]
    call gen_expr
    ; test rax, rax
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jne true_label (rel32 patched after the RHS code is emitted)
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov r12, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; Left was false: only now evaluate the RHS.
    mov rax, [rbx+24]
    call gen_expr
    ; Normalize RHS to 0/1.
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x95
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; jmp done (skip the true result materialization)
    mov dil, 0xE9
    call emit_byte
    mov r13, [rel code_sz]
    xor edi, edi
    call emit_u32
    ; true_label: patch JNE and produce canonical true (1).
    mov rax, [rel code_sz]
    sub rax, r12
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r12], eax
    ; mov eax, 1
    mov dil, 0xB8
    call emit_byte
    mov edi, 1
    call emit_u32
    ; done: patch the unconditional jump.
    mov rax, [rel code_sz]
    sub rax, r13
    sub rax, 4
    lea rcx, [rel code_buf]
    mov [rcx + r13], eax
    pop r13
    pop r12
    pop rbx
    ret

.ge_binop_add_imm:
    ; Evaluate left -> RAX
    pop rbx
    mov rax, [rbx+16]
    call gen_expr
    ; Check if value is 1 → use inc rax (48 FF C0, 3 bytes)
    mov rax, [rbx+24]        ; right node
    mov rcx, [rax+8]         ; value
    cmp rcx, 1
    je .ge_add_inc
    ; add rax, imm8 = 48 83 C0 XX (4 bytes)
    ; NOTE: emit_byte clobbers rcx, so reload the value from the AST
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov rax, [rbx+24]        ; right node (rbx preserved by emit_byte)
    mov rax, [rax+8]         ; reload value
    mov dil, al
    call emit_byte
    pop rbx
    ret
.ge_add_inc:
    ; inc rax = 48 FF C0 (3 bytes)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_binop_sub_imm:
    ; Evaluate left -> RAX
    pop rbx
    mov rax, [rbx+16]
    call gen_expr
    ; Check if value is 1 → use dec rax (48 FF C8, 3 bytes)
    mov rax, [rbx+24]        ; right node
    mov rcx, [rax+8]         ; value
    cmp rcx, 1
    je .ge_sub_dec
    ; sub rax, imm8 = 48 83 E8 XX (4 bytes)
    ; NOTE: emit_byte clobbers rcx, so reload the value from the AST
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xE8
    call emit_byte
    mov rax, [rbx+24]        ; right node (rbx preserved by emit_byte)
    mov rax, [rax+8]         ; reload value
    mov dil, al
    call emit_byte
    pop rbx
    ret
.ge_sub_dec:
    ; dec rax = 48 FF C8 (3 bytes)
    mov dil, 0x48
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    pop rbx
    ret
.ge_binop_mul_imm:
    ; Strength reduction: *2,*4,*8,*16,*32,*64 → shl
    ; Follow same pattern as ADD/SUB: pop rbx first, then evaluate left
    pop rbx                  ; restore rbx from .ge_binop push
    ; Check right value (rbx still has AST node ptr)
    mov rax, [rbx+24]        ; right node
    mov rcx, [rax+8]         ; right value
    cmp rcx, 2
    je .ge_mul_s1
    cmp rcx, 4
    je .ge_mul_s2
    cmp rcx, 8
    je .ge_mul_s3
    cmp rcx, 16
    je .ge_mul_s4
    cmp rcx, 32
    je .ge_mul_s5
    cmp rcx, 64
    je .ge_mul_s6
    ; Not power of 2 — re-push rbx and go to generic path
    push rbx
    jmp .ge_binop_generic
.ge_mul_s1:
    ; *2 = shl rax, 1
    mov rax, [rbx+16]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x01
    call emit_byte
    pop rbx
    ret
.ge_mul_s2:
    ; *4 = shl rax, 2
    mov rax, [rbx+16]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x02
    call emit_byte
    pop rbx
    ret
.ge_mul_s3:
    ; *8 = shl rax, 3
    mov rax, [rbx+16]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x03
    call emit_byte
    pop rbx
    ret
.ge_mul_s4:
    ; *16 = shl rax, 4
    mov rax, [rbx+16]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x04
    call emit_byte
    pop rbx
    ret
.ge_mul_s5:
    ; *32 = shl rax, 5
    mov rax, [rbx+16]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x05
    call emit_byte
    pop rbx
    ret
.ge_mul_s6:
    ; *64 = shl rax, 6
    mov rax, [rbx+16]
    call gen_expr
    mov dil, 0x48
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    mov dil, 0x06
    call emit_byte
    pop rbx
    ret
.ge_binop_generic:
    pop rbx
    ; Evaluate left -> RAX
    mov rax, [rbx+16]        ; left
    call gen_expr
    ; mov rdx, rax (save left in rdx)
    mov dil, 0x50            ; push rax (save on stack — call-safe)
    call emit_byte
    ; Evaluate right -> RAX
    mov rax, [rbx+24]        ; right
    call gen_expr
    ; xchg rax, rdx (rax=left, rdx=right)
    mov dil, 0x5A            ; pop rdx (restore saved left)
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x87
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    ; Now rax=left, rdx=right. Emit operation.
    mov rax, [rbx+8]         ; op id
    cmp rax, OP_ADD
    je .ge_add
    cmp rax, OP_SUB
    je .ge_sub
    cmp rax, OP_MUL
    je .ge_mul
    cmp rax, OP_DIV
    je .ge_div
    cmp rax, OP_EQ
    je .ge_eq
    cmp rax, OP_LT
    je .ge_lt
    cmp rax, OP_GT
    je .ge_gt
    cmp rax, OP_LE
    je .ge_le
    cmp rax, OP_GE
    je .ge_ge
    cmp rax, OP_NE
    je .ge_ne
    cmp rax, OP_MOD
    je .ge_mod
    cmp rax, OP_SHL
    je .ge_shl
    cmp rax, OP_SHR
    je .ge_shr
    cmp rax, OP_AND
    je .ge_and
    cmp rax, OP_OR
    je .ge_or
    cmp rax, OP_XOR
    je .ge_xor
    cmp rax, OP_LAND
    je .ge_land
    cmp rax, OP_LOR
    je .ge_lor
    pop rbx
    ret
.ge_fbinop:
    ; Evaluate raw operands through the normal scalar ABI, then convert/promote
    ; to SSE2 binary64. The result returns as raw bits in RAX; comparisons return 0/1.
    push r12
    push r13
    push r14
    push r15
    ; PERF-FG2 (R30): Evaluate effectful/indexed/complex LHS first, then read
    ; a by-value, register-resident float RHS. This preserves all LHS effects
    ; and does NOT reorder an indexed read/write or function call. It avoids
    ; runtime push/pop for the outer binary operation. RHS with indexing,
    ; calls, stack locals, or integer conversion stays on the old path.
    xor r15d, r15d
    mov rax, [rbx+24]
    ; Literal RHS is side-effect-free. Its generated MOV into RAX can happen
    ; after converting the LHS into XMM0, with no runtime stack save.
    cmp qword [rax], AST_FLOAT
    jne .gfb_check_rhs_num
    mov r15, 6
    jmp .gfb_rhs_classified
.gfb_check_rhs_num:
    cmp qword [rax], AST_NUM
    jne .gfb_check_rhs_var
    mov r15, 7
    jmp .gfb_rhs_classified
.gfb_check_rhs_var:
    cmp qword [rax], AST_VAR
    jne .gfb_rhs_classified
    mov rdi, [rax+8]
    call is_float_var
    test rax, rax
    jz .gfb_rhs_classified
    mov rax, [rbx+24]
    mov rdi, [rax+8]
    call lookup_var
    cmp rax, 1
    jb .gfb_rhs_classified
    cmp rax, 5
    ja .gfb_rhs_classified
    mov r15, rax
.gfb_rhs_classified:
    ; PERF-FG1: scalar-left / complex-right float expression.
    ; The left scalar is a by-value local held in a callee-saved GPR.
    ; No function called by the right expression can mutate this local.
    ; Therefore evaluate the right expression first and load the left directly
    ; into XMM0 afterwards, avoiding a runtime push/pop of the left value.
    ; Indexed operands and stack-resident locals deliberately stay generic.
    xor r14d, r14d
    mov rax, [rbx+16]
    cmp qword [rax], AST_VAR
    jne .gfb_classified
    mov rdi, [rax+8]
    call is_float_var
    test rax, rax
    jz .gfb_classified
    mov rax, [rbx+16]
    mov rdi, [rax+8]
    call lookup_var
    cmp rax, 1
    jb .gfb_classified
    cmp rax, 5
    ja .gfb_classified
    mov r14, rax
.gfb_classified:
    mov rdi, [rbx+16]
    call expr_is_float
    mov r12, rax
    mov rdi, [rbx+24]
    call expr_is_float
    mov r13, rax
    test r15, r15
    jnz .gfb_left_first_rhs_reg
    test r14, r14
    jnz .gfb_eval_right_only
    ; Generic, order-preserving path for non-scalar/stack operands.
    mov rax, [rbx+16]
    call gen_expr
    mov dil, 0x50            ; runtime push left raw scalar
    call emit_byte
    jmp .gfb_eval_right_only
.gfb_left_first_rhs_reg:
    ; Left-to-right exactly: evaluate LHS before reading RHS register.
    ; R15 is a compile-time marker; preserve it during recursive codegen.
    push r15
    mov rax, [rbx+16]
    call gen_expr
    pop r15
    ; LHS result is raw binary64 or integer in runtime RAX.
    test r12, r12
    jz .gfb_direct_left_int
    mov dil, 0x66           ; movq xmm0,rax
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x6E
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    jmp .gfb_direct_load_rhs
.gfb_direct_left_int:
    mov dil, 0xF2           ; cvtsi2sd xmm0,rax
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2A
    call emit_byte
    mov dil, 0xC0
    call emit_byte
.gfb_direct_load_rhs:
    ; Marker 1..5: RHS is a callee-saved float scalar GPR.
    ; Markers 6/7: a side-effect-free AST_FLOAT/AST_NUM literal respectively.
    cmp r15, 5
    ja .gfb_direct_rhs_literal
    mov rdi, r15
    mov rsi, 1
    call emit_float_gpr_to_xmm
    jmp .gfb_left_ready
.gfb_direct_rhs_literal:
    push r15
    mov rax, [rbx+24]
    call gen_expr             ; MOV immediate to runtime RAX, preserves XMM0
    pop r15
    test r13, r13
    jz .gfb_direct_rhs_lit_int
    mov dil, 0x66            ; movq xmm1,rax
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x6E
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    jmp .gfb_left_ready
.gfb_direct_rhs_lit_int:
    mov dil, 0xF2            ; cvtsi2sd xmm1,rax
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2A
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    jmp .gfb_left_ready
.gfb_eval_right_only:
    ; Protect the compiler-side live-register marker across nested codegen,
    ; even if a nested codegen helper uses R14 internally.
    push r14
    mov rax, [rbx+24]
    call gen_expr
    pop r14
    ; right -> xmm1
    test r13, r13
    jz .gfb_right_int
    mov dil, 0x66
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x6E
    call emit_byte
    mov dil, 0xC8            ; movq xmm1,rax
    call emit_byte
    jmp .gfb_right_ready
.gfb_right_int:
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2A
    call emit_byte
    mov dil, 0xC8            ; cvtsi2sd xmm1,rax
    call emit_byte
.gfb_right_ready:
    test r14, r14
    jz .gfb_pop_left
    ; PERF-FG1: left variable lives in RBX/R12-R15 across RHS calls.
    ; XMM1 now holds the computed RHS, including mixed integer promotion.
    mov rdi, r14
    xor rsi, rsi
    call emit_float_gpr_to_xmm
    jmp .gfb_left_ready
.gfb_pop_left:
    mov dil, 0x5A            ; runtime pop left -> rdx
    call emit_byte
    test r12, r12
    jz .gfb_left_int
    mov dil, 0x66
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x6E
    call emit_byte
    mov dil, 0xC2            ; movq xmm0,rdx
    call emit_byte
    jmp .gfb_left_ready
.gfb_left_int:
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2A
    call emit_byte
    mov dil, 0xC2            ; cvtsi2sd xmm0,rdx
    call emit_byte
.gfb_left_ready:
    mov rax, [rbx+8]
    cmp rax, OP_ADD
    je .gfb_add
    cmp rax, OP_SUB
    je .gfb_sub
    cmp rax, OP_MUL
    je .gfb_mul
    cmp rax, OP_DIV
    je .gfb_div
    ; comparisons: ucomisd xmm0,xmm1
    mov dil, 0x66
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2E
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov rax, [rbx+8]
    mov dil, 0x0F
    call emit_byte
    cmp rax, OP_EQ
    je .gfb_sete
    cmp rax, OP_NE
    je .gfb_setne
    cmp rax, OP_LT
    je .gfb_setb
    cmp rax, OP_GT
    je .gfb_seta
    cmp rax, OP_LE
    je .gfb_setbe
    ; OP_GE
    mov dil, 0x93            ; setae al
    jmp .gfb_set_emit
.gfb_sete:
    mov dil, 0x94
    jmp .gfb_set_emit
.gfb_setne:
    mov dil, 0x95
    jmp .gfb_set_emit
.gfb_setb:
    mov dil, 0x92
    jmp .gfb_set_emit
.gfb_seta:
    mov dil, 0x97
    jmp .gfb_set_emit
.gfb_setbe:
    mov dil, 0x96
.gfb_set_emit:
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48            ; movzx rax,al
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
.gfb_add:
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x58
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    jmp .gfb_arith_done
.gfb_sub:
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x5C
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    jmp .gfb_arith_done
.gfb_mul:
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x59
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    jmp .gfb_arith_done
.gfb_div:
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x5E
    call emit_byte
    mov dil, 0xC1
    call emit_byte
.gfb_arith_done:
    mov dil, 0x66            ; movq rax,xmm0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7E
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.ge_land:
    ; Short-circuit AND: if left==0, result=0; else result=right
    ; rax=left, rdx=right already evaluated by generic binop
    ; test rax,rax; cmovz rdx, rax (if left=0, result=0)
    ; test rdx,rdx; setne al (normalize to 0/1)
    ; Simplified: and rax, rdx; then normalize
    ; For short-circuit we'd need labels, but simple approach:
    ; result = (left != 0) && (right != 0) = (left & right) but normalized
    ; test rax, rax; setne cl
    ; test rdx, rdx; setne al
    ; and rax, rcx
    ; Actually: just do test+setne for both, then and
    ; test rax, rax = 48 85 C0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; setne cl = 0F 95 C1
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x95
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; test rdx, rdx = 48 85 D2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xD2
    call emit_byte
    ; setne al = 0F 95 C0
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x95
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; and rax, rcx = 48 21 C8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x21
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    ; movzx rax, al = 48 0F B6 C0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_lor:
    ; Short-circuit OR: if left!=0, result=1; else result=(right!=0)
    ; test rax, rax; setne cl
    ; test rdx, rdx; setne al
    ; or rax, rcx; movzx rax, al
    ; test rax, rax = 48 85 C0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; setne cl = 0F 95 C1
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x95
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; test rdx, rdx = 48 85 D2
    mov dil, 0x48
    call emit_byte
    mov dil, 0x85
    call emit_byte
    mov dil, 0xD2
    call emit_byte
    ; setne al = 0F 95 C0
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x95
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ; or rax, rcx = 48 09 C8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x09
    call emit_byte
    mov dil, 0xC8
    call emit_byte
    ; movzx rax, al = 48 0F B6 C0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_mod:
    ; mov rcx, rdx; cqo; idiv rcx; rax=remainder
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    ; cqo (sign-extend rax into rdx:rax) = 48 99
    mov dil, 0x48
    call emit_byte
    mov dil, 0x99
    call emit_byte
    ; idiv rcx = 48 F7 F9
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF7
    call emit_byte
    mov dil, 0xF9
    call emit_byte
    ; mov rax, rdx (remainder) = 48 89 D0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    pop rbx
    ret
.ge_and:
    ; and rax, rdx = 48 21 D0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x21
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    pop rbx
    ret
.ge_or:
    ; or rax, rdx = 48 09 D0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x09
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    pop rbx
    ret
.ge_shl:
    ; rax=left, rdx=count -> mov rcx,rdx ; shl rax,cl
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xD3
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    pop rbx
    ret
.ge_shr:
    ; mov rcx,rdx ; shr rax,cl
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0xD3
    call emit_byte
    mov dil, 0xE8
    call emit_byte
    pop rbx
    ret
.ge_xor:
    ; xor rax, rdx = 48 31 D0
    mov dil, 0x48
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    pop rbx
    ret
.ge_le:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x9E
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_ge:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x9D
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_ne:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x95
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_add:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x01
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    pop rbx
    ret
.ge_sub:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x29
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    pop rbx
    ret
.ge_mul:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xAF
    call emit_byte
    mov dil, 0xC2
    call emit_byte
    pop rbx
    ret
.ge_div:
    ; mov rcx, rdx; cqo; idiv rcx; rax=quotient
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD1
    call emit_byte
    ; cqo (sign-extend) = 48 99
    mov dil, 0x48
    call emit_byte
    mov dil, 0x99
    call emit_byte
    ; idiv rcx = 48 F7 F9
    mov dil, 0x48
    call emit_byte
    mov dil, 0xF7
    call emit_byte
    mov dil, 0xF9
    call emit_byte
    pop rbx
    ret
.ge_eq:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x94
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_lt:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x9C
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_gt:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x39
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x9F
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    pop rbx
    ret
.ge_writemem:
    ; [AST_WRITEMEM][arg_count][arg1_addr_node][arg2_val_node]
    ; Evaluate address -> rax, push, evaluate value -> rax, pop rdi, store
    push r12
    ; Evaluate arg1 (address)
    mov rax, [rbx+16]        ; address node
    call gen_expr             ; rax = address value (runtime)
    ; emit: push rax (50)
    mov dil, 0x50
    call emit_byte
    ; Evaluate arg2 (value)
    mov rax, [rbx+24]        ; value node
    call gen_expr             ; rax = value (runtime)
    ; emit: mov rcx, rax (48 89 C1) — save value in rcx
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    ; emit: pop rdi (5F) — rdi = address
    mov dil, 0x5F
    call emit_byte
    ; emit: mov [rdi], rcx (48 89 0F) — store rcx at [rdi]
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    pop r12
    pop rbx
    ret
.ge_halt:
    mov dil, 0xF4
    call emit_byte
    pop rbx
    ret

; emit_nirmmita_from_rax
; Emit allocation sequence assuming generated-program RAX already holds byte size.
; Leaves the allocated base pointer in generated-program RAX.
emit_nirmmita_from_rax:
    ; mov rsi, rax (length) = 48 89 C6
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    ; xor edi, edi (addr=0) = 31 FF
    mov dil, 0x31
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    ; mov edx, 3 (PROT_READ|PROT_WRITE) = BA 03 00 00 00
    mov dil, 0xBA
    call emit_byte
    mov dil, 0x03
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov r10d, 0x22 (MAP_PRIVATE|MAP_ANONYMOUS) = 41 BA 22 00 00 00
    mov dil, 0x41
    call emit_byte
    mov dil, 0xBA
    call emit_byte
    mov dil, 0x22
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; mov r8, -1 (fd) = 49 C7 C0 FF FF FF FF
    mov dil, 0x49
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    ; xor r9d, r9d (offset=0) = 45 31 C9
    mov dil, 0x45
    call emit_byte
    mov dil, 0x31
    call emit_byte
    mov dil, 0xC9
    call emit_byte
    ; mov eax, 9 (sys_mmap) = B8 09 00 00 00
    mov dil, 0xB8
    call emit_byte
    mov dil, 0x09
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    xor edi, edi
    call emit_byte
    ; syscall
    call emit_syscall
    ret

; ============================================================
; T12 FLOAT TYPE / CONVERSION HELPERS
; ============================================================
mark_float_var:
    ; rdi=name ptr; current generated-function scope only
    push rbx
    push r12
    mov rbx, rdi
    mov r12, [rel float_var_cnt]
    cmp r12, VAR_TABLE_CAP
    jae .mfv_overflow
    lea rcx, [rel float_vars]
    mov [rcx + r12*8], rbx
    inc qword [rel float_var_cnt]
    pop r12
    pop rbx
    ret
.mfv_overflow:
    pop r12
    pop rbx
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail

is_float_var:
    ; rdi=name ptr -> rax=1/0
    push rbx
    push r12
    push r13
    mov rbx, rdi
    xor r12, r12
    mov r13, [rel float_var_cnt]
.ifv_loop:
    cmp r12, r13
    jae .ifv_no
    lea rcx, [rel float_vars]
    mov rdi, [rcx + r12*8]
    mov rsi, rbx
    call strcmp
    test rax, rax
    jz .ifv_yes
    inc r12
    jmp .ifv_loop
.ifv_yes:
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.ifv_no:
    xor rax, rax
    pop r13
    pop r12
    pop rbx
    ret

expr_is_float:
    ; rdi=AST node -> rax=1 only when the expression result itself is binary64.
    push rbx
    push r12
    mov rbx, rdi
    test rbx, rbx
    jz .eif_no
    mov rax, [rbx]
    cmp rax, AST_FLOAT
    je .eif_yes
    cmp rax, AST_VAR
    je .eif_var
    cmp rax, AST_BINOP
    je .eif_binop
    cmp rax, AST_TERNARY
    je .eif_ternary
    cmp rax, AST_FUNCALL
    je .eif_funcall
    cmp rax, AST_INDEX
    je .eif_index
    cmp rax, AST_CALL
    je .eif_builtin
    jmp .eif_no
.eif_var:
    mov rdi, [rbx+8]
    call is_float_var
    jmp .eif_done
.eif_funcall:
    mov rdi, [rbx+8]
    call func_return_is_float
    jmp .eif_done
.eif_index:
    mov rdi, [rbx+8]
    call is_float_kosh_var
    jmp .eif_done
.eif_builtin:
    cmp qword [rbx+8], BN_KOSHPOP
    jne .eif_no
    cmp qword [rbx+16], 1
    jne .eif_no
    mov rax, [rbx+24]
    test rax, rax
    jz .eif_no
    cmp qword [rax], AST_VAR
    jne .eif_no
    mov rdi, [rax+8]
    call is_float_kosh_var
    jmp .eif_done
.eif_binop:
    mov r12, [rbx+8]
    cmp r12, OP_ADD
    je .eif_bin_arith
    cmp r12, OP_SUB
    je .eif_bin_arith
    cmp r12, OP_MUL
    je .eif_bin_arith
    cmp r12, OP_DIV
    jne .eif_no
.eif_bin_arith:
    mov rdi, [rbx+16]
    call expr_is_float
    test rax, rax
    jnz .eif_yes
    mov rdi, [rbx+24]
    call expr_is_float
    test rax, rax
    jnz .eif_yes
    jmp .eif_no
.eif_ternary:
    mov rdi, [rbx+16]
    call expr_is_float
    test rax, rax
    jnz .eif_yes
    mov rdi, [rbx+24]
    call expr_is_float
    test rax, rax
    jnz .eif_yes
    jmp .eif_no
.eif_yes:
    mov rax, 1
    jmp .eif_done
.eif_no:
    xor rax, rax
.eif_done:
    pop r12
    pop rbx
    ret

func_return_is_float:
    ; rdi=function name -> rax=1 when pre-classified return type is binary64.
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rdi
    xor r12, r12
    mov r13, [rel func_def_cnt]
.frif_loop:
    cmp r12, r13
    jae .frif_no
    lea rcx, [rel func_defs]
    mov r14, [rcx + r12*8]
    mov rdi, rbx
    mov rsi, [r14+8]
    call strcmp
    test rax, rax
    jz .frif_found
    inc r12
    jmp .frif_loop
.frif_found:
    cmp qword [r14+40], 0
    setne al
    movzx rax, al
    jmp .frif_done
.frif_no:
    xor rax, rax
.frif_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

func_param_type:
    ; rdi=function name, rsi=zero-based arg index -> rax=PARAM_* type byte.
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    mov r12, rsi
    xor r13, r13
    mov r14, [rel func_def_cnt]
.fpt_loop:
    cmp r13, r14
    jae .fpt_no
    lea rcx, [rel func_defs]
    mov r15, [rcx + r13*8]
    mov rdi, rbx
    mov rsi, [r15+8]
    call strcmp
    test rax, rax
    jz .fpt_found
    inc r13
    jmp .fpt_loop
.fpt_found:
    cmp r12, [r15+16]
    jae .fpt_no
    mov rax, [r15+32]        ; parameter-name buffer end byte offset
    mov rcx, [r15+16]
    shl rcx, 3
    sub rax, rcx             ; start byte offset
    shr rax, 3               ; start slot
    add rax, r12
    lea rcx, [rel func_param_types]
    movzx eax, byte [rcx + rax]
    jmp .fpt_done
.fpt_no:
    xor rax, rax
.fpt_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

mark_func_typed_params:
    ; rdi=FUNCDEF node. Seed float inference from typed parameters. Scalar
    ; dasham marks float_vars; kosh dasham marks float_kosh_vars. Raw kosh does
    ; not affect return-float inference and therefore needs no marker here.
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    xor r12, r12
    mov r13, [rbx+16]        ; count
    mov r14, [rbx+32]        ; end byte offset
    mov rax, r13
    shl rax, 3
    sub r14, rax             ; start byte offset
.mftp_loop:
    cmp r12, r13
    jae .mftp_done
    mov rax, r14
    shr rax, 3
    add rax, r12
    lea rcx, [rel func_param_types]
    movzx r15d, byte [rcx + rax]
    cmp r15d, PARAM_DASHAM
    je .mftp_scalar_float
    cmp r15d, PARAM_KOSH_DASHAM
    je .mftp_kosh_float
    jmp .mftp_next
.mftp_scalar_float:
    mov rax, r12
    shl rax, 3
    add rax, r14
    lea rcx, [rel func_params]
    mov rdi, [rcx + rax]
    call mark_float_var
    jmp .mftp_next
.mftp_kosh_float:
    mov rax, r12
    shl rax, 3
    add rax, r14
    lea rcx, [rel func_params]
    mov rdi, [rcx + rax]
    call mark_float_kosh_var
.mftp_next:
    inc r12
    jmp .mftp_loop
.mftp_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

collect_float_decls:
    ; rdi=statement/block node. Collect scalar dasham and kosh-dasham declarations.
    push rbx
    push r12
    push r13
    mov rbx, rdi
    test rbx, rbx
    jz .cfd_done
    mov rax, [rbx]
    cmp rax, AST_DECL
    je .cfd_decl
    cmp rax, AST_BLOCK
    je .cfd_block
    cmp rax, AST_IF
    je .cfd_if
    cmp rax, AST_WHILE
    je .cfd_while
    cmp rax, AST_DO_WHILE
    je .cfd_do
    cmp rax, AST_FOR
    je .cfd_for
    jmp .cfd_done
.cfd_decl:
    cmp qword [rbx+32], 1
    je .cfd_scalar_float
    cmp qword [rbx+32], 3
    jne .cfd_done
    mov rdi, [rbx+8]
    call mark_float_kosh_var
    jmp .cfd_done
.cfd_scalar_float:
    mov rdi, [rbx+8]
    call mark_float_var
    jmp .cfd_done
.cfd_block:
    xor r12, r12
    mov r13, [rbx+8]
.cfd_block_loop:
    cmp r12, r13
    jae .cfd_done
    mov rdi, [rbx + 16 + r12*8]
    call collect_float_decls
    inc r12
    jmp .cfd_block_loop
.cfd_if:
    mov rdi, [rbx+16]
    call collect_float_decls
    mov rdi, [rbx+24]
    call collect_float_decls
    jmp .cfd_done
.cfd_while:
    mov rdi, [rbx+16]
    call collect_float_decls
    jmp .cfd_done
.cfd_do:
    mov rdi, [rbx+8]
    call collect_float_decls
    jmp .cfd_done
.cfd_for:
    mov rdi, [rbx+40]
    call collect_float_decls
.cfd_done:
    pop r13
    pop r12
    pop rbx
    ret

node_has_float_return:
    ; rdi=statement/block node -> rax=1 if any reachable syntactic return is float.
    push rbx
    push r12
    push r13
    mov rbx, rdi
    test rbx, rbx
    jz .nhfr_no
    mov rax, [rbx]
    cmp rax, AST_RETURN
    je .nhfr_return
    cmp rax, AST_BLOCK
    je .nhfr_block
    cmp rax, AST_IF
    je .nhfr_if
    cmp rax, AST_WHILE
    je .nhfr_while
    cmp rax, AST_DO_WHILE
    je .nhfr_do
    cmp rax, AST_FOR
    je .nhfr_for
    jmp .nhfr_no
.nhfr_return:
    mov rdi, [rbx+8]
    test rdi, rdi
    jz .nhfr_no
    call expr_is_float
    jmp .nhfr_done
.nhfr_block:
    xor r12, r12
    mov r13, [rbx+8]
.nhfr_block_loop:
    cmp r12, r13
    jae .nhfr_no
    mov rdi, [rbx + 16 + r12*8]
    call node_has_float_return
    test rax, rax
    jnz .nhfr_yes
    inc r12
    jmp .nhfr_block_loop
.nhfr_if:
    mov rdi, [rbx+16]
    call node_has_float_return
    test rax, rax
    jnz .nhfr_yes
    mov rdi, [rbx+24]
    call node_has_float_return
    test rax, rax
    jnz .nhfr_yes
    jmp .nhfr_no
.nhfr_while:
    mov rdi, [rbx+16]
    call node_has_float_return
    test rax, rax
    jnz .nhfr_yes
    jmp .nhfr_no
.nhfr_do:
    mov rdi, [rbx+8]
    call node_has_float_return
    test rax, rax
    jnz .nhfr_yes
    jmp .nhfr_no
.nhfr_for:
    mov rdi, [rbx+40]
    call node_has_float_return
    test rax, rax
    jnz .nhfr_yes
    jmp .nhfr_no
.nhfr_yes:
    mov rax, 1
    jmp .nhfr_done
.nhfr_no:
    xor rax, rax
.nhfr_done:
    pop r13
    pop r12
    pop rbx
    ret

classify_float_functions:
    ; Fixed-point inference over all parsed prakriya definitions. [funcdef+40]
    ; becomes 1 when a return expression is binary64. Typed params and local
    ; dasham declarations seed each function's compile-time type environment.
    push rbx
    push r12
    push r13
    push r14
    push r15
    xor r15, r15             ; pass count
.cff_pass:
    mov rax, [rel func_def_cnt]
    cmp r15, rax
    ja .cff_done
    xor r14d, r14d           ; changed this pass
    xor r12, r12
    mov r13, [rel func_def_cnt]
.cff_func_loop:
    cmp r12, r13
    jae .cff_pass_done
    lea rcx, [rel func_defs]
    mov rbx, [rcx + r12*8]
    cmp qword [rbx+40], 0
    jne .cff_next
    mov qword [rel float_var_cnt], 0
    mov qword [rel float_kosh_var_cnt], 0
    mov rdi, rbx
    call mark_func_typed_params
    mov rdi, [rbx+24]
    call collect_float_decls
    mov rdi, [rbx+24]
    call node_has_float_return
    test rax, rax
    jz .cff_next
    mov qword [rbx+40], 1
    mov r14d, 1
.cff_next:
    inc r12
    jmp .cff_func_loop
.cff_pass_done:
    test r14d, r14d
    jz .cff_done
    inc r15
    jmp .cff_pass
.cff_done:
    mov qword [rel float_var_cnt], 0
    mov qword [rel float_kosh_var_cnt], 0
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

gen_typed_call_arg:
    ; rdi=function name, rsi=arg index, rdx=arg AST. Emit the argument value
    ; and runtime push. Scalar params retain T12 conversion. T18 kosh params
    ; keep the one-qword pointer ABI and enforce matching element type at compile
    ; time so a pointer is never accidentally converted as a scalar float.
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rdi
    mov r12, rsi
    mov r13, rdx
    mov rdi, rbx
    mov rsi, r12
    call func_param_type
    mov r14, rax             ; PARAM_* target type
    cmp r14, PARAM_KOSH
    jae .gtca_kosh
    ; Scalar path: infer source scalar type then apply int<->dasham conversion.
    mov rdi, r13
    call expr_is_float
    push rax
    mov rax, r13
    call gen_expr
    pop rdi                  ; source scalar type 0/1
    mov rsi, r14             ; target scalar type 0/1
    call emit_scalar_type_conversion
    jmp .gtca_push
.gtca_kosh:
    ; Typed kosh parameters accept a named kosh variable of the same element
    ; type. The runtime value is already the user pointer, so no conversion.
    cmp qword [r13], AST_VAR
    jne .gtca_kosh_type_fail
    mov rdi, [r13+8]
    call is_kosh_var
    test rax, rax
    jz .gtca_kosh_type_fail
    mov rdi, [r13+8]
    call is_float_kosh_var
    cmp r14, PARAM_KOSH_DASHAM
    je .gtca_need_float_kosh
    ; PARAM_KOSH must not silently reinterpret binary64 elements as integers.
    test rax, rax
    jnz .gtca_kosh_type_fail
    jmp .gtca_emit_kosh
.gtca_need_float_kosh:
    test rax, rax
    jz .gtca_kosh_type_fail
.gtca_emit_kosh:
    mov rax, r13
    call gen_expr
.gtca_push:
    mov dil, 0x50            ; runtime push rax
    call emit_byte
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
.gtca_kosh_type_fail:
    pop r14
    pop r13
    pop r12
    pop rbx
    lea rdi, [rel msg_kosh_param_type]
    jmp capacity_fail

emit_scalar_type_conversion:
    ; rdi=source type, rsi=target type; runtime value is in RAX.
    cmp rdi, rsi
    je .estc_done
    test rsi, rsi
    jz .estc_to_int
    call emit_i64_to_f64_rax
    ret
.estc_to_int:
    call emit_f64_to_i64_rax
.estc_done:
    ret

binop_needs_float:
    ; rdi=AST_BINOP -> rax=1 for supported arithmetic/comparison with a float operand.
    push rbx
    mov rbx, rdi
    mov rax, [rbx+8]
    cmp rax, OP_ADD
    je .bnf_operands
    cmp rax, OP_SUB
    je .bnf_operands
    cmp rax, OP_MUL
    je .bnf_operands
    cmp rax, OP_DIV
    je .bnf_operands
    cmp rax, OP_EQ
    je .bnf_operands
    cmp rax, OP_NE
    je .bnf_operands
    cmp rax, OP_LT
    je .bnf_operands
    cmp rax, OP_GT
    je .bnf_operands
    cmp rax, OP_LE
    je .bnf_operands
    cmp rax, OP_GE
    jne .bnf_no
.bnf_operands:
    mov rdi, [rbx+16]
    call expr_is_float
    test rax, rax
    jnz .bnf_yes
    mov rdi, [rbx+24]
    call expr_is_float
    test rax, rax
    jnz .bnf_yes
.bnf_no:
    xor rax, rax
    pop rbx
    ret
.bnf_yes:
    mov rax, 1
    pop rbx
    ret

emit_i64_to_f64_rax:
    ; Runtime RAX integer -> raw binary64 bits in runtime RAX.
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2A
    call emit_byte
    mov dil, 0xC0            ; cvtsi2sd xmm0,rax
    call emit_byte
    mov dil, 0x66
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7E
    call emit_byte
    mov dil, 0xC0            ; movq rax,xmm0
    call emit_byte
    ret

emit_f64_to_i64_rax:
    ; Raw binary64 bits in runtime RAX -> truncating signed integer in RAX.
    mov dil, 0x66
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x6E
    call emit_byte
    mov dil, 0xC0            ; movq xmm0,rax
    call emit_byte
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2C
    call emit_byte
    mov dil, 0xC0            ; cvttsd2si rax,xmm0
    call emit_byte
    ret

; ============================================================
; VARIABLE TABLE
; ============================================================
; T8b scoped array markers. These are compiler-side only and reset whenever
; code generation enters main or a user function. Runtime length itself lives
; in the hidden qword immediately before a pankti array's element-0 pointer.
; This keeps same-named arrays in different functions independent and avoids
; changing raw nirmmita pointer/index semantics.
mark_array_var:
    ; rdi = name ptr
    push rbx
    push r12
    mov rbx, rdi
    mov r12, [rel array_var_cnt]
    cmp r12, 256
    jae .mav_done
    lea rcx, [rel array_vars]
    mov [rcx + r12*8], rbx
    inc qword [rel array_var_cnt]
.mav_done:
    pop r12
    pop rbx
    ret

is_array_var:
    ; rdi = name ptr -> rax = 1 if marked in current function scope, else 0
    push rbx
    push r12
    push r13
    mov rbx, rdi
    xor r12, r12
    mov r13, [rel array_var_cnt]
.iav_loop:
    cmp r12, r13
    jae .iav_no
    lea rcx, [rel array_vars]
    mov rdi, [rcx + r12*8]
    mov rsi, rbx
    call strcmp
    test rax, rax
    jz .iav_yes
    inc r12
    jmp .iav_loop
.iav_yes:
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.iav_no:
    xor rax, rax
    pop r13
    pop r12
    pop rbx
    ret

mark_kosh_param_var:
    ; rdi=name ptr; current generated-function scope only.
    push rbx
    push r12
    mov rbx, rdi
    mov r12, [rel kosh_param_var_cnt]
    cmp r12, KOSH_PARAM_VAR_CAP
    jae .mkpv_overflow
    lea rcx, [rel kosh_param_vars]
    mov [rcx+r12*8], rbx
    inc qword [rel kosh_param_var_cnt]
    pop r12
    pop rbx
    ret
.mkpv_overflow:
    pop r12
    pop rbx
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail

is_kosh_param_var:
    ; rdi=name ptr -> rax=1 when this kosh is a by-value function parameter.
    push rbx
    push r12
    push r13
    mov rbx, rdi
    xor r12, r12
    mov r13, [rel kosh_param_var_cnt]
.ikpv_loop:
    cmp r12, r13
    jae .ikpv_no
    lea rcx, [rel kosh_param_vars]
    mov rdi, [rcx+r12*8]
    mov rsi, rbx
    call strcmp
    test rax, rax
    jz .ikpv_yes
    inc r12
    jmp .ikpv_loop
.ikpv_yes:
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.ikpv_no:
    xor eax, eax
    pop r13
    pop r12
    pop rbx
    ret

mark_float_kosh_var:
    ; rdi=name ptr; compiler-side marker for kosh dasham element typing.
    push rbx
    push r12
    mov rbx, rdi
    mov r12, [rel float_kosh_var_cnt]
    cmp r12, KOSH_VAR_CAP
    jae .mfkv_overflow
    lea rcx, [rel float_kosh_vars]
    mov [rcx+r12*8], rbx
    inc qword [rel float_kosh_var_cnt]
    pop r12
    pop rbx
    ret
.mfkv_overflow:
    pop r12
    pop rbx
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail

is_float_kosh_var:
    ; rdi=name ptr -> rax=1 when this kosh stores binary64 elements.
    push rbx
    push r12
    push r13
    mov rbx, rdi
    xor r12, r12
    mov r13, [rel float_kosh_var_cnt]
.ifkv_loop:
    cmp r12, r13
    jae .ifkv_no
    lea rcx, [rel float_kosh_vars]
    mov rdi, [rcx+r12*8]
    mov rsi, rbx
    call strcmp
    test rax, rax
    jz .ifkv_yes
    inc r12
    jmp .ifkv_loop
.ifkv_yes:
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.ifkv_no:
    xor eax, eax
    pop r13
    pop r12
    pop rbx
    ret

mark_kosh_var:
    ; rdi=name ptr; compiler-side marker for the current generated function.
    push rbx
    push r12
    mov rbx, rdi
    mov r12, [rel kosh_var_cnt]
    cmp r12, KOSH_VAR_CAP
    jae .mkv_overflow
    lea rcx, [rel kosh_vars]
    mov [rcx+r12*8], rbx
    inc qword [rel kosh_var_cnt]
    pop r12
    pop rbx
    ret
.mkv_overflow:
    pop r12
    pop rbx
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail

is_kosh_var:
    ; rdi=name ptr -> rax=1 if this is a kosh variable in current scope.
    push rbx
    push r12
    push r13
    mov rbx, rdi
    xor r12, r12
    mov r13, [rel kosh_var_cnt]
.ikv_loop:
    cmp r12, r13
    jae .ikv_no
    lea rcx, [rel kosh_vars]
    mov rdi, [rcx+r12*8]
    mov rsi, rbx
    call strcmp
    test rax, rax
    jz .ikv_yes
    inc r12
    jmp .ikv_loop
.ikv_yes:
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.ikv_no:
    xor eax, eax
    pop r13
    pop r12
    pop rbx
    ret

emit_load_named_var:
    ; Compiler-time rdi=name; emit runtime load of variable into RAX.
    call lookup_var
    test rax, rax
    jle .elnv_stack
    mov rdi, rax
    call emit_load_reg
    ret
.elnv_stack:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x8B
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
    ret

emit_store_named_var:
    ; Compiler-time rdi=name; emit runtime store from RAX into variable.
    call lookup_var
    test rax, rax
    jle .esnv_stack
    mov rdi, rax
    call emit_store_reg
    ret
.esnv_stack:
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0x45
    call emit_byte
    mov edi, eax
    call emit_byte
    ret

; alloc_var(rdi = name ptr) → rax = location
; Returns: 1-5 = register (rbx, r12, r13, r14, r15)
;          negative = stack offset (as before)
alloc_var:
    push rbx
    push r12
    mov rbx, rdi              ; name
    ; Check if we have free registers (first 5 variables)
    mov rax, [rel var_cnt]
    cmp rax, 5
    jge .av_stack
    ; Assign a register: var 0→reg 1, var 1→reg 2, etc.
    add rax, 1                ; register ID = var_cnt + 1
    jmp .av_store
.av_stack:
    ; Assign stack slot
    mov rax, [rel stack_dep]
    add rax, 8
    mov [rel stack_dep], rax
    neg rax                   ; offset is negative
.av_store:
    ; Store in table
    mov r12, [rel var_cnt]
    cmp r12, VAR_TABLE_CAP
    jae .av_overflow
    imul r12, r12, 16
    lea rcx, [rel var_table]
    mov [rcx + r12], rbx      ; name ptr
    mov [rcx + r12 + 8], rax  ; location (reg ID or stack offset)
    inc qword [rel var_cnt]
    pop r12
    pop rbx
    ret
.av_overflow:
    pop r12
    pop rbx
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail

; PERF2/PERF3: direct integer register destination scheduling.
; These helpers deliberately accept only proven integer scalar forms and keep
; floats, calls, indexing and complex expressions on the established path.

; try_emit_int_decl_reg(rdi=AST_DECL) -> rax=1 if declaration fully emitted.
; Only fires while the next variable is guaranteed to be register-resident.
try_emit_int_decl_reg:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    cmp qword [rbx], AST_DECL
    jne .teidr_no
    cmp qword [rbx+32], 0       ; integer scalar only
    jne .teidr_no
    cmp qword [rbx+24], 0       ; not pankti
    jne .teidr_no
    mov r13, [rbx+16]
    test r13, r13
    jz .teidr_no
    cmp qword [rel var_cnt], 5  ; next alloc must be rbx/r12-r15
    jae .teidr_no
    ; Integer declarations fed from a float expression need the established
    ; truncating conversion path, so do not bypass it.
    mov rdi, r13
    call expr_is_float
    test rax, rax
    jnz .teidr_no
    mov r13, [rbx+16]
    ; Classify and validate the initializer before allocating the destination,
    ; preserving the old "evaluate then allocate" name-resolution behavior.
    cmp qword [r13], AST_NUM
    je .teidr_num
    cmp qword [r13], AST_VAR
    je .teidr_var
    cmp qword [r13], AST_BINOP
    jne .teidr_no
    mov r15, [r13+8]            ; operator
    cmp r15, OP_ADD
    je .teidr_binop_ok
    cmp r15, OP_SUB
    je .teidr_binop_ok
    cmp r15, OP_MUL
    jne .teidr_no
.teidr_binop_ok:
    mov rax, [r13+16]
    cmp qword [rax], AST_VAR
    jne .teidr_no
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .teidr_no
    mov r14, rax                ; left reg id
    mov rax, [r13+24]
    cmp qword [rax], AST_VAR
    jne .teidr_no
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .teidr_no
    mov r12, rax                ; right reg id
    mov rdi, [rbx+8]
    call alloc_var
    mov r13, rax                ; destination reg id
    ; dst = left, then dst op= right. Newly allocated dst cannot alias sources.
    mov rdi, r13
    mov rsi, r14
    call emit_reg_move_reg
    mov rdi, r13
    mov rsi, r15
    mov rdx, r12
    call emit_reg_binary_update
    jmp .teidr_yes
.teidr_var:
    mov rdi, [r13+8]
    call lookup_var
    test rax, rax
    jle .teidr_no
    mov r14, rax
    mov rdi, [rbx+8]
    call alloc_var
    mov rdi, rax
    mov rsi, r14
    call emit_reg_move_reg
    jmp .teidr_yes
.teidr_num:
    mov r14, [r13+8]
    mov rdi, [rbx+8]
    call alloc_var
    mov rdi, rax
    mov rsi, r14
    call emit_reg_load_imm
.teidr_yes:
    mov rax, 1
    jmp .teidr_done
.teidr_no:
    xor rax, rax
.teidr_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; try_emit_int_reg_assignment(rdi=AST_ASSIGN) -> rax=1 if fully emitted.
try_emit_int_reg_assignment:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    mov rax, [rbx+8]
    cmp qword [rax], AST_VAR
    jne .teira_no
    mov rdi, [rax+8]
    call is_float_var
    test rax, rax
    jnz .teira_no
    mov rax, [rbx+8]
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .teira_no
    mov r12, rax                ; destination reg id
    mov r13, [rbx+16]           ; source expr
    mov rdi, r13
    call expr_is_float
    test rax, rax
    jnz .teira_no
    mov r13, [rbx+16]           ; reload across recursive type helper
    cmp qword [r13], AST_NUM
    je .teira_num
    cmp qword [r13], AST_VAR
    je .teira_var
    cmp qword [r13], AST_BINOP
    jne .teira_no
    mov r15, [r13+8]
    cmp r15, OP_ADD
    je .teira_binop_ok
    cmp r15, OP_SUB
    je .teira_binop_ok
    cmp r15, OP_MUL
    jne .teira_no
.teira_binop_ok:
    mov rax, [r13+16]
    cmp qword [rax], AST_VAR
    jne .teira_no
    ; PERF5: dst = integer_register +/- non-negative signed-imm32.
    ; The two generated instructions are MOV dst,src; ADD/SUB dst,imm.
    ; This is safe when the destination aliases the source (MOV is a no-op),
    ; and preserves 64-bit fallback for literals > 0x7fffffff.
    mov rax, [r13+24]
    cmp qword [rax], AST_NUM
    je .teira_rhs_imm
    mov rax, [r13+16]
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .teira_no
    mov r14, rax                ; left reg id
    mov rax, [r13+24]
    cmp qword [rax], AST_VAR
    jne .teira_no
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .teira_no
    mov rdx, rax                ; right reg id
    cmp r15, OP_SUB
    jne .teira_commutative
    ; For subtraction, dst==right would destroy the RHS before use; fallback.
    cmp r12, rdx
    je .teira_no
    cmp r12, r14
    je .teira_have_left
    push rdx
    mov rdi, r12
    mov rsi, r14
    call emit_reg_move_reg
    pop rdx
.teira_have_left:
    mov rdi, r12
    mov rsi, r15
    call emit_reg_binary_update
    jmp .teira_yes
.teira_commutative:
    ; ADD/MUL can reuse either operand if target aliases one of them.
    cmp r12, r14
    je .teira_comm_left
    cmp r12, rdx
    je .teira_comm_right
    push rdx
    mov rdi, r12
    mov rsi, r14
    call emit_reg_move_reg
    pop rdx
.teira_comm_left:
    mov rdi, r12
    mov rsi, r15
    call emit_reg_binary_update
    jmp .teira_yes
.teira_comm_right:
    mov rcx, r14
    mov rdi, r12
    mov rsi, r15
    mov rdx, rcx
    call emit_reg_binary_update
    jmp .teira_yes
.teira_rhs_imm:
    cmp r15, OP_MUL           ; no IMUL immediate here; leave it generic
    je .teira_no
    mov r14, [rax+8]         ; RHS literal, unsigned in the AST
    cmp r14, 0x7FFFFFFF      ; arithmetic imm32 sign-extends in x86-64
    ja .teira_no
    mov rax, [r13+16]
    mov rdi, [rax+8]
    call lookup_var
    test rax, rax
    jle .teira_no           ; left must already occupy a register
    mov rsi, rax
    mov rdi, r12
    call emit_reg_move_reg   ; preserves r14 literal and r15 operator
    mov rdi, r12
    mov rsi, r15
    mov rdx, r14
    call emit_reg_self_update_imm
    jmp .teira_yes
.teira_var:
    mov rdi, [r13+8]
    call lookup_var
    test rax, rax
    jle .teira_no
    cmp rax, r12
    je .teira_yes
    mov rdi, r12
    mov rsi, rax
    call emit_reg_move_reg
    jmp .teira_yes
.teira_num:
    mov rsi, [r13+8]
    mov rdi, r12
    call emit_reg_load_imm
.teira_yes:
    mov rax, 1
    jmp .teira_done
.teira_no:
    xor rax, rax
.teira_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; emit_reg_move_reg(rdi=dst logical id, rsi=src logical id)
emit_reg_move_reg:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    mov r12, rsi
    cmp rbx, r12
    je .ermr_done
    ; destination low code / REX.B
    cmp rbx, 1
    je .ermr_dst_rbx
    mov r13, rbx
    add r13, 2
    mov rcx, 1
    jmp .ermr_dst_done
.ermr_dst_rbx:
    mov r13, 3
    xor rcx, rcx
.ermr_dst_done:
    ; source low code / REX.R
    cmp r12, 1
    je .ermr_src_rbx
    mov rax, r12
    add rax, 2
    mov rdx, 1
    jmp .ermr_src_done
.ermr_src_rbx:
    mov rax, 3
    xor rdx, rdx
.ermr_src_done:
    mov rdi, 0x48
    test rdx, rdx
    jz .ermr_no_r
    or rdi, 0x04
.ermr_no_r:
    test rcx, rcx
    jz .ermr_no_b
    or rdi, 0x01
.ermr_no_b:
    call emit_byte
    mov dil, 0x89
    call emit_byte
    and rax, 7
    shl rax, 3
    and r13, 7
    or rax, r13
    or rax, 0xC0
    mov dil, al
    call emit_byte
.ermr_done:
    pop r13
    pop r12
    pop rbx
    ret

; emit_reg_binary_update(rdi=dst, rsi=OP_ADD/SUB/MUL, rdx=src)
emit_reg_binary_update:
    cmp rsi, OP_MUL
    je emit_reg_imul_reg
    jmp emit_reg_self_update_reg

; emit_reg_imul_reg(rdi=dst, rdx=src): imul dst,src
emit_reg_imul_reg:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    mov r12, rdx
    ; dst occupies ModRM.reg -> REX.R
    cmp rbx, 1
    je .erir_dst_rbx
    mov r13, rbx
    add r13, 2
    mov rcx, 1
    jmp .erir_dst_done
.erir_dst_rbx:
    mov r13, 3
    xor rcx, rcx
.erir_dst_done:
    ; src occupies ModRM.r/m -> REX.B
    cmp r12, 1
    je .erir_src_rbx
    mov rax, r12
    add rax, 2
    mov rdx, 1
    jmp .erir_src_done
.erir_src_rbx:
    mov rax, 3
    xor rdx, rdx
.erir_src_done:
    mov rdi, 0x48
    test rcx, rcx
    jz .erir_no_r
    or rdi, 0x04
.erir_no_r:
    test rdx, rdx
    jz .erir_no_b
    or rdi, 0x01
.erir_no_b:
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xAF
    call emit_byte
    and r13, 7
    shl r13, 3
    and rax, 7
    or rax, r13
    or rax, 0xC0
    mov dil, al
    call emit_byte
    pop r13
    pop r12
    pop rbx
    ret

; emit_reg_load_imm(rdi=dst logical id, rsi=non-negative integer literal)
emit_reg_load_imm:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    mov r12, rsi
    cmp rbx, 1
    je .erli_rbx
    mov r13, rbx
    add r13, 2                 ; low register code 4..7
    mov rcx, 1                 ; extended register bank
    jmp .erli_mapped
.erli_rbx:
    mov r13, 3
    xor rcx, rcx
.erli_mapped:
    mov rax, r12
    shr rax, 32
    jnz .erli_imm64
    ; mov r32,imm32 zero-extends into the 64-bit destination.
    test rcx, rcx
    jz .erli_emit_opcode32
    mov dil, 0x41
    call emit_byte
.erli_emit_opcode32:
    mov rax, r13
    and rax, 7
    add rax, 0xB8
    mov dil, al
    call emit_byte
    mov edi, r12d
    call emit_u32
    jmp .erli_done
.erli_imm64:
    mov rdi, 0x48
    test rcx, rcx
    jz .erli_rex_ready
    or rdi, 0x01
.erli_rex_ready:
    call emit_byte
    mov rax, r13
    and rax, 7
    add rax, 0xB8
    mov dil, al
    call emit_byte
    mov rdi, r12
    call emit_u64
.erli_done:
    pop r13
    pop r12
    pop rbx
    ret

; PERF1: try_emit_int_reg_cmp(rdi = AST_BINOP) -> rax=1 if a direct
; register-to-register integer comparison was emitted.  Callers already know
; the operator is a comparison; this helper only proves operand/type safety.
try_emit_int_reg_cmp:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    cmp qword [rbx], AST_BINOP
    jne .teirc_no
    mov rdi, rbx
    call binop_needs_float
    test rax, rax
    jnz .teirc_no
    mov r12, [rbx+16]
    mov r13, [rbx+24]
    cmp qword [r12], AST_VAR
    jne .teirc_no
    cmp qword [r13], AST_VAR
    jne .teirc_no
    mov rdi, [r12+8]
    call lookup_var
    test rax, rax
    jle .teirc_no
    mov r12, rax              ; left register id
    mov rdi, [r13+8]
    call lookup_var
    test rax, rax
    jle .teirc_no
    mov rsi, rax              ; right register id
    mov rdi, r12
    call emit_reg_cmp_reg
    mov rax, 1
    jmp .teirc_done
.teirc_no:
    xor rax, rax
.teirc_done:
    pop r13
    pop r12
    pop rbx
    ret

; emit_reg_cmp_reg(rdi=left reg id, rsi=right reg id)
; Emits cmp left,right using 39 /r with the same register map as alloc_var.
emit_reg_cmp_reg:
    push rbx
    push r12
    push r13
    mov rbx, rdi              ; left/destination id
    mov r12, rsi              ; right/source id
    ; left low code -> r13, REX.B -> rcx
    cmp rbx, 1
    je .ercr_left_rbx
    mov r13, rbx
    add r13, 2
    mov rcx, 1
    jmp .ercr_left_done
.ercr_left_rbx:
    mov r13, 3
    xor rcx, rcx
.ercr_left_done:
    ; right low code -> rax, REX.R -> rdx
    cmp r12, 1
    je .ercr_right_rbx
    mov rax, r12
    add rax, 2
    mov rdx, 1
    jmp .ercr_right_done
.ercr_right_rbx:
    mov rax, 3
    xor rdx, rdx
.ercr_right_done:
    mov rdi, 0x48
    test rdx, rdx
    jz .ercr_no_r
    or rdi, 0x04
.ercr_no_r:
    test rcx, rcx
    jz .ercr_no_b
    or rdi, 0x01
.ercr_no_b:
    call emit_byte
    mov dil, 0x39
    call emit_byte
    and rax, 7
    shl rax, 3
    and r13, 7
    or rax, r13
    or rax, 0xC0
    mov dil, al
    call emit_byte
    pop r13
    pop r12
    pop rbx
    ret

; ================================================================
; R31 Stage 1: deliberately opt-in XMM2-XMM5 cache, single basic block.
; These helper routines are *not part of the compiler* when flag is OFF.
; All writes are write-through to the old raw-qword GPR homes, so there
; is never a dirty value to spill, including at recursive prakriya calls.
; Valid/liveness masks are compiler-time metadata; the ABI is unchanged.
; Cache hits only apply to named scalar dasham variables in registers 1-4.
; Fifth and stack locals, array indices, aliased writes, calls and complex
; trees fall back to byte-identical old codegen. No XMM6+ usage.
; ================================================================
%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE
xmm_cache_barrier:
    mov qword [rel xmm_cache_valid_mask], 0
    mov qword [rel xmm_cache_live_mask], 0
    mov qword [rel xmm_cache_dirty_mask], 0
    inc qword [rel xmm_cache_barriers]
    ret

; rdi=logical GPR id 1..4 -> cache xmm2..5. Compiler-time helper.
; It emits a raw MOVQ load only for misses; no FP numerical conversion.
xmm_cache_ensure:
    push rbx
    push r12
    mov rbx, rdi
    mov r12, rdi
    dec r12
    mov rcx, r12
    mov rax, 1
    shl rax, cl
    test [rel xmm_cache_valid_mask], rax
    jnz .xce_hit
    push rax
    mov rsi, rbx
    inc rsi                           ; xmm id = logical GPR + 1
    call emit_float_gpr_to_xmm
    pop rax
    or [rel xmm_cache_valid_mask], rax
    or [rel xmm_cache_live_mask], rax
    inc qword [rel xmm_cache_misses]
    jmp .xce_done
.xce_hit:
    inc qword [rel xmm_cache_hits]
.xce_done:
    mov rax, rbx
    inc rax
    pop r12
    pop rbx
    ret

; rdi=logical GPR destination 1..4, rsi=cached XMM source 2..5.
; Emit MOVQ r64,xmmN, preserving full 64-bit binary64 payload exactly.
; The low three GPR bits and REX.B are mapped like emit_float_xmm0_to_gpr.
xmm_cache_store_gpr:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    mov r12, rsi
    mov r13, 0x49
    cmp rbx, 1
    jne .xcsg_mapped
    mov rbx, 3                       ; RBX encoded as /3
    mov r13, 0x48
    jmp .xcsg_byte
.xcsg_mapped:
    add rbx, 2                       ; R12..15 encoded as /4..7
.xcsg_byte:
    shl r12, 3
    or r12, rbx
    or r12, 0xC0
    mov dil, 0x66
    call emit_byte
    mov dil, r13b
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7E
    call emit_byte
    mov dil, r12b
    call emit_byte
    pop r13
    pop r12
    pop rbx
    ret

; rdi=ASSIGN node. On full match returns 1 and emits optimized code.
; Only AST_VAR float operands and AST_VAR float targets with logical
; registers 1..4 may enter. Evaluation of scalar, by-value locals has no
; side effects. All potentially aliased or side-effecting forms fall back.
try_emit_xmm_cached_assignment:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    cmp qword [rbx], AST_ASSIGN
    jne .txca_no
    mov r12, [rbx+8]
    cmp qword [r12], AST_VAR
    jne .txca_no
    mov r13, [rbx+16]
    cmp qword [r13], AST_BINOP
    jne .txca_no
    mov r15, [r13+8]
    cmp r15, OP_ADD
    je .txca_op_ok
    cmp r15, OP_SUB
    je .txca_op_ok
    cmp r15, OP_MUL
    je .txca_op_ok
    cmp r15, OP_DIV
    jne .txca_no
.txca_op_ok:
    mov r14, [r13+16]
    cmp qword [r14], AST_VAR
    jne .txca_no
    mov r13, [r13+24]
    cmp qword [r13], AST_VAR
    jne .txca_no
    mov rdi, [r12+8]
    call is_float_var
    test rax, rax
    jz .txca_no
    mov rdi, [r14+8]
    call is_float_var
    test rax, rax
    jz .txca_no
    mov rdi, [r13+8]
    call is_float_var
    test rax, rax
    jz .txca_no
    mov rdi, [r12+8]
    call lookup_var
    cmp rax, 1
    jb .txca_no
    cmp rax, 4
    ja .txca_no
    mov r12, rax                     ; destination ID
    mov rdi, [r14+8]
    call lookup_var
    cmp rax, 1
    jb .txca_no
    cmp rax, 4
    ja .txca_no
    mov r14, rax                     ; left ID
    mov rdi, [r13+8]
    call lookup_var
    cmp rax, 1
    jb .txca_no
    cmp rax, 4
    ja .txca_no
    mov r13, rax                     ; right ID

    ; Load both original operands into cache in left-to-right order.
    mov rdi, r14
    call xmm_cache_ensure
    mov rdi, r13
    call xmm_cache_ensure

    cmp r12, r14
    jne .txca_distinct
    ; x = x op y: operate on resident destination; never overwrite the
    ; original RHS unless it aliases x (in which case both operands = x).
    mov r10, r12
    inc r10                           ; xmm index 2..5
    mov r11, r13
    inc r11
    jmp .txca_emit_op
.txca_distinct:
    ; Destination distinct from left: first copy left -> xmm0, so a dest
    ; aliasing right does not corrupt inputs to noncommutative SUB/DIV.
    mov dil, 0x66                     ; movapd xmm0,xmmLeft
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x28
    call emit_byte
    mov rdi, r14
    inc rdi
    or dil, 0xC0
    call emit_byte
    xor r10, r10                      ; result xmm0
    mov r11, r13
    inc r11
.txca_emit_op:
    ; SSE2 arithmetic: addsd/subsd/mulsd/divsd xmmDest,xmmRight.
    push r10
    push r11
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    cmp r15, OP_SUB
    je .txca_op_sub
    cmp r15, OP_MUL
    je .txca_op_mul
    cmp r15, OP_DIV
    je .txca_op_div
    mov dil, 0x58                      ; addsd
    jmp .txca_op_byte
.txca_op_sub:
    mov dil, 0x5C                      ; subsd
    jmp .txca_op_byte
.txca_op_mul:
    mov dil, 0x59                      ; mulsd
    jmp .txca_op_byte
.txca_op_div:
    mov dil, 0x5E                      ; divsd
.txca_op_byte:
    call emit_byte
    pop r11
    pop r10
    shl r10, 3
    or r10, r11
    or r10, 0xC0
    mov dil, r10b
    call emit_byte

    ; For distinct destinations, mirror xmm0 into the target cache slot.
    cmp r12, r14
    je .txca_store
    mov dil, 0x66                     ; movapd xmmTarget,xmm0
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x28
    call emit_byte
    mov rdi, r12
    inc rdi
    shl rdi, 3
    or rdi, 0xC0
    call emit_byte
    mov rdi, r12
    dec rdi
    mov rcx, rdi
    mov rdx, 1
    shl rdx, cl
    or [rel xmm_cache_valid_mask], rdx
    or [rel xmm_cache_live_mask], rdx
.txca_store:
    ; Canonical GPR home is updated immediately; dirty bit stays clear.
    mov rdi, r12
    mov rsi, r12
    inc rsi
    call xmm_cache_store_gpr
    mov rax, 1
    jmp .txca_done
.txca_no:
    xor rax, rax
.txca_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
%endif

; PERF-F1: float x=x+y / x=x-y / x=x*y / x=x/y, where x and y
; are named, scalar dasham locals resident in callee-saved GPRs 1..5.
; Do NOT change the scalar raw-qword ABI. XMM0/XMM1 are scratch here, exactly
; as on the established float path. Branches/calls/arrays/mixed expressions,
; non-self destinations and stack locals keep the existing path unchanged.
try_emit_float_reg_self_update:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    cmp qword [rbx], AST_ASSIGN
    jne .tfrsu_no
    mov r12, [rbx+8]
    cmp qword [r12], AST_VAR
    jne .tfrsu_no
    mov r13, [rbx+16]
    cmp qword [r13], AST_BINOP
    jne .tfrsu_no
    mov r14, [r13+8]
    cmp r14, OP_ADD
    je .tfrsu_op_ok
    cmp r14, OP_SUB
    je .tfrsu_op_ok
    cmp r14, OP_MUL
    je .tfrsu_op_ok
    cmp r14, OP_DIV
    jne .tfrsu_no
.tfrsu_op_ok:
    mov r15, [r13+16]
    cmp qword [r15], AST_VAR
    jne .tfrsu_no
    mov rdi, [r12+8]
    mov rsi, [r15+8]
    call strcmp
    test rax, rax
    jnz .tfrsu_no
    mov rdi, [r12+8]
    call is_float_var
    test rax, rax
    jz .tfrsu_no
    mov r15, [r13+24]
    cmp qword [r15], AST_VAR
    jne .tfrsu_no
    mov rdi, [r15+8]
    call is_float_var
    test rax, rax
    jz .tfrsu_no
    mov rdi, [r12+8]
    call lookup_var
    test rax, rax
    jle .tfrsu_no
    mov r12, rax                 ; destination logical register 1..5
    mov rdi, [r15+8]
    call lookup_var
    test rax, rax
    jle .tfrsu_no
    mov rdx, rax                 ; rhs logical register 1..5
    mov rdi, r12
    mov rsi, r14
    call emit_float_reg_self_update
    mov rax, 1
    jmp .tfrsu_done
.tfrsu_no:
    xor rax, rax
.tfrsu_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; PERF-F2: c=a+b / c=a-b / c=a*b / c=a/b for three scalar dasham
; locals already in callee-saved GPRs. Never modify either input before both
; operands are transferred to XMM0/XMM1; only destination gets the final qword.
; Anything mixed, non-scalar, stack-resident or complex falls back unchanged.
try_emit_float_reg_destination:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi                  ; assignment node
    cmp qword [rbx], AST_ASSIGN
    jne .tfrd_no
    mov r12, [rbx+8]              ; target
    cmp qword [r12], AST_VAR
    jne .tfrd_no
    mov r13, [rbx+16]             ; expression
    cmp qword [r13], AST_BINOP
    jne .tfrd_no
    mov r15, [r13+8]              ; op, preserved across lookups
    cmp r15, OP_ADD
    je .tfrd_op_ok
    cmp r15, OP_SUB
    je .tfrd_op_ok
    cmp r15, OP_MUL
    je .tfrd_op_ok
    cmp r15, OP_DIV
    jne .tfrd_no
.tfrd_op_ok:
    mov r14, [r13+16]             ; left
    cmp qword [r14], AST_VAR
    jne .tfrd_no
    mov r13, [r13+24]             ; right
    cmp qword [r13], AST_VAR
    jne .tfrd_no
    mov rdi, [r12+8]
    call is_float_var
    test rax, rax
    jz .tfrd_no
    mov rdi, [r14+8]
    call is_float_var
    test rax, rax
    jz .tfrd_no
    mov rdi, [r13+8]
    call is_float_var
    test rax, rax
    jz .tfrd_no
    mov rdi, [r12+8]
    call lookup_var
    test rax, rax
    jle .tfrd_no
    mov r12, rax                  ; target logical GPR
    mov rdi, [r14+8]
    call lookup_var
    test rax, rax
    jle .tfrd_no
    mov r14, rax                  ; left logical GPR
    mov rdi, [r13+8]
    call lookup_var
    test rax, rax
    jle .tfrd_no
    mov rdx, rax                  ; right logical GPR
    mov rdi, r14                  ; left
    mov rsi, r15                  ; operation
    mov rcx, r12                  ; target
    call emit_float_reg_binop_to_gpr
    mov rax, 1
    jmp .tfrd_done
.tfrd_no:
    xor rax, rax
.tfrd_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; rdi=logical GPR id (1=rbx 2=r12 3=r13 4=r14 5=r15),
; rsi=XMM destination index 0 or 1. Emit movq xmmN,GPR (66 REX.W 0F 6E /r).
; Scratch r10/r11 only, as in surrounding codegen helpers.
emit_float_gpr_to_xmm:
    mov r10, rdi
    mov r11, 0x49
    cmp r10, 1
    je .efgtx_rbx
    add r10, 2
    jmp .efgtx_mapped
.efgtx_rbx:
    mov r10, 3
    mov r11, 0x48
.efgtx_mapped:
    shl rsi, 3
    or r10, rsi
    or r10, 0xC0
    mov dil, 0x66
    call emit_byte
    mov dil, r11b
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x6E
    call emit_byte
    mov dil, r10b
    call emit_byte
    ret

; rdi=logical destination GPR id. Emit movq GPR,xmm0 (66 REX.W 0F 7E /r).
emit_float_xmm0_to_gpr:
    mov r10, rdi
    mov r11, 0x49
    cmp r10, 1
    je .efxtg_rbx
    add r10, 2
    jmp .efxtg_mapped
.efxtg_rbx:
    mov r10, 3
    mov r11, 0x48
.efxtg_mapped:
    or r10, 0xC0
    mov dil, 0x66
    call emit_byte
    mov dil, r11b
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7E
    call emit_byte
    mov dil, r10b
    call emit_byte
    ret

; PERF-F1 wrapper: x=x op y. Delegate to PERF-F2 emitter, with left=dst.
; rdi=left/destination id, rsi=OP_ADD/SUB/MUL/DIV, rdx=right id.
emit_float_reg_self_update:
    mov rcx, rdi
    jmp emit_float_reg_binop_to_gpr

; PERF-F2 generic register-only float binary operator.
; rdi=left logical GPR, rsi=operator, rdx=right logical GPR, rcx=destination.
; Exactly four runtime instructions, no runtime stack traffic, no ABI change.
emit_float_reg_binop_to_gpr:
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rdi
    mov r12, rsi
    mov r13, rdx
    mov r14, rcx
    mov rdi, rbx
    xor rsi, rsi
    call emit_float_gpr_to_xmm
    mov rdi, r13
    mov rsi, 1
    call emit_float_gpr_to_xmm
    mov dil, 0xF2
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov rdi, r12
    cmp rdi, OP_ADD
    je .efrsu_add
    cmp rdi, OP_SUB
    je .efrsu_sub
    cmp rdi, OP_MUL
    je .efrsu_mul
    mov dil, 0x5E              ; divsd xmm0,xmm1
    jmp .efrsu_opcode
.efrsu_add:
    mov dil, 0x58              ; addsd xmm0,xmm1
    jmp .efrsu_opcode
.efrsu_sub:
    mov dil, 0x5C              ; subsd xmm0,xmm1
    jmp .efrsu_opcode
.efrsu_mul:
    mov dil, 0x59              ; mulsd xmm0,xmm1
.efrsu_opcode:
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov rdi, r14
    call emit_float_xmm0_to_gpr
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; PERF-FC1: register-resident float comparisons a == b, !=, <, >, <=, >=.
; rdi=AST_BINOP node. Emit 2 MOVQ + UCOMISD + SETcc + MOVZX (5 insns).
; Only two named dasham scalar locals in registers 1..5 qualify. NaN handling
; remains byte-identical to the existing T12 UCOMISD/SETcc code path.
; XMM0/XMM1 are already volatile temporaries in the float expression ABI.
try_emit_float_reg_compare:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    cmp qword [rbx], AST_BINOP
    jne .tfrc_no
    mov r15, [rbx+8]
    cmp r15, OP_EQ
    je .tfrc_op_ok
    cmp r15, OP_NE
    je .tfrc_op_ok
    cmp r15, OP_LT
    je .tfrc_op_ok
    cmp r15, OP_GT
    je .tfrc_op_ok
    cmp r15, OP_LE
    je .tfrc_op_ok
    cmp r15, OP_GE
    jne .tfrc_no
.tfrc_op_ok:
    mov r12, [rbx+16]
    mov r13, [rbx+24]
    cmp qword [r12], AST_VAR
    jne .tfrc_no
    cmp qword [r13], AST_VAR
    jne .tfrc_no
    mov rdi, [r12+8]
    call is_float_var
    test rax, rax
    jz .tfrc_no
    mov rdi, [r13+8]
    call is_float_var
    test rax, rax
    jz .tfrc_no
    mov rdi, [r12+8]
    call lookup_var
    test rax, rax
    jle .tfrc_no
    mov r14, rax
    mov rdi, [r13+8]
    call lookup_var
    test rax, rax
    jle .tfrc_no
    mov r13, rax
    mov rdi, r14
    xor rsi, rsi
    call emit_float_gpr_to_xmm
    mov rdi, r13
    mov rsi, 1
    call emit_float_gpr_to_xmm
    mov dil, 0x66              ; ucomisd xmm0,xmm1
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x2E
    call emit_byte
    mov dil, 0xC1
    call emit_byte
    mov dil, 0x0F              ; setcc al; identical to T12
    call emit_byte
    cmp r15, OP_EQ
    je .tfrc_eq
    cmp r15, OP_NE
    je .tfrc_ne
    cmp r15, OP_LT
    je .tfrc_lt
    cmp r15, OP_GT
    je .tfrc_gt
    cmp r15, OP_LE
    je .tfrc_le
    mov dil, 0x93              ; setae: >=
    jmp .tfrc_emit_cc
.tfrc_eq:
    mov dil, 0x94              ; sete
    jmp .tfrc_emit_cc
.tfrc_ne:
    mov dil, 0x95              ; setne
    jmp .tfrc_emit_cc
.tfrc_lt:
    mov dil, 0x92              ; setb
    jmp .tfrc_emit_cc
.tfrc_gt:
    mov dil, 0x97              ; seta
    jmp .tfrc_emit_cc
.tfrc_le:
    mov dil, 0x96              ; setbe
.tfrc_emit_cc:
    call emit_byte
    mov dil, 0xC0              ; al
    call emit_byte
    mov dil, 0x48              ; movzx rax,al
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0xB6
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    mov rax, 1
    jmp .tfrc_done
.tfrc_no:
    xor rax, rax
.tfrc_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; PERF1: try_emit_int_self_update(rdi = AST_ASSIGN node) -> rax=1 if emitted.
; Recognizes integer x=x+imm, x=x-imm, x=x+y and x=x-y.  This is deliberately
; narrow: float expressions, reordered operands, complex RHS expressions and
; unsupported locations fall back to the existing general generator.
try_emit_int_self_update:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rdi
    mov r12, [rbx+8]          ; target
    cmp qword [r12], AST_VAR
    jne .teisu_no
    mov r13, [rbx+16]         ; value
    cmp qword [r13], AST_BINOP
    jne .teisu_no
    mov r14, [r13+8]          ; operator
    cmp r14, OP_ADD
    je .teisu_op_ok
    cmp r14, OP_SUB
    jne .teisu_no
.teisu_op_ok:
    ; Keep every float/mixed expression on the established T12 path.
    mov rdi, [r12+8]
    call is_float_var
    test rax, rax
    jnz .teisu_no
    mov rdi, r13
    call expr_is_float
    test rax, rax
    jnz .teisu_no
    ; Require the left operand to be the same variable as the assignment target.
    mov r15, [r13+16]
    cmp qword [r15], AST_VAR
    jne .teisu_no
    mov rdi, [r12+8]
    mov rsi, [r15+8]
    call strcmp
    test rax, rax
    jnz .teisu_no
    ; Resolve destination location.
    mov rdi, [r12+8]
    call lookup_var
    mov r12, rax              ; >0 register id, <=0 stack offset
    mov r15, [r13+24]         ; RHS node
    cmp qword [r15], AST_NUM
    je .teisu_rhs_imm
    cmp qword [r15], AST_VAR
    jne .teisu_no
    ; Register-to-register form only when both variables are register-resident.
    test r12, r12
    jle .teisu_no
    mov rdi, [r15+8]
    call lookup_var
    test rax, rax
    jle .teisu_no
    mov rdx, rax              ; source register id
    mov rdi, r12              ; destination register id
    mov rsi, r14              ; OP_ADD / OP_SUB
    call emit_reg_self_update_reg
    jmp .teisu_yes
.teisu_rhs_imm:
    mov rdx, [r15+8]
    ; x86-64 sign-extends arithmetic imm32 to 64 bits.  The direct one-
    ; instruction update is valid only for non-negative literals <= INT32_MAX.
    ; Larger literal values must use the generic full-width evaluator.
    cmp rdx, 0x7FFFFFFF
    ja .teisu_no
    test r12, r12
    jle .teisu_stack_imm
    mov rdi, r12              ; destination register id
    mov rsi, r14              ; operator
    call emit_reg_self_update_imm
    jmp .teisu_yes
.teisu_stack_imm:
    ; Existing stack locals use disp8 addressing; optimize only offsets that fit.
    cmp r12, -128
    jl .teisu_no
    mov rdi, r12              ; signed disp8
    mov rsi, r14              ; operator
    call emit_stack_self_update_imm
.teisu_yes:
    mov rax, 1
    jmp .teisu_done
.teisu_no:
    xor rax, rax
.teisu_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; emit_reg_self_update_imm(rdi=reg id 1..5, rsi=OP_ADD/SUB,
;                          rdx=non-negative imm <= signed INT32_MAX)
; Selects compact 83 /digit imm8 for 0..127, otherwise 81 /digit imm32.
; Generated register mapping: 1=rbx, 2=r12, 3=r13, 4=r14, 5=r15.
emit_reg_self_update_imm:
    push rbx
    push r12
    push r13
    mov rbx, rdi              ; register id
    mov r12, rsi              ; operator
    mov r13, rdx              ; immediate
    ; Map logical register id to x86 low register number and REX.B extension.
    cmp rbx, 1
    je .ersui_rbx
    mov rax, rbx
    add rax, 2                ; 2..5 -> low codes 4..7
    mov rcx, 1                ; REX.B
    jmp .ersui_mapped
.ersui_rbx:
    mov rax, 3
    xor rcx, rcx
.ersui_mapped:
    ; +/- 1 uses inc/dec, matching the existing RAX fast path.
    cmp r13, 1
    jne .ersui_imm8
    mov rdx, 0x48
    or rdx, rcx
    mov dil, dl
    call emit_byte
    mov dil, 0xFF
    call emit_byte
    mov rdx, rax
    and rdx, 7
    or rdx, 0xC0              ; /0 INC
    cmp r12, OP_ADD
    je .ersui_emit_modrm
    or rdx, 0x08              ; /1 DEC
.ersui_emit_modrm:
    mov dil, dl
    call emit_byte
    jmp .ersui_done
.ersui_imm8:
    mov rdx, 0x48
    or rdx, rcx
    mov dil, dl
    call emit_byte
    mov dil, 0x83
    cmp r13, 127
    jbe .ersui_emit_opcode
    mov dil, 0x81
.ersui_emit_opcode:
    call emit_byte
    mov rdx, rax
    and rdx, 7
    or rdx, 0xC0              ; /0 ADD
    cmp r12, OP_ADD
    je .ersui_emit_imm_modrm
    or rdx, 0x28              ; /5 SUB
.ersui_emit_imm_modrm:
    mov dil, dl
    call emit_byte
    cmp r13, 127
    ja .ersui_wide_immediate
    mov dil, r13b
    call emit_byte
    jmp .ersui_done
.ersui_wide_immediate:
    mov edi, r13d
    call emit_u32
.ersui_done:
    pop r13
    pop r12
    pop rbx
    ret

; emit_reg_self_update_reg(rdi=dst id, rsi=OP_ADD/SUB, rdx=src id)
emit_reg_self_update_reg:
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rdi              ; dst id
    mov r12, rsi              ; operator
    mov r13, rdx              ; src id
    ; dst low code / extension -> r14 / rcx
    cmp rbx, 1
    je .ersur_dst_rbx
    mov r14, rbx
    add r14, 2
    mov rcx, 1                ; REX.B
    jmp .ersur_dst_done
.ersur_dst_rbx:
    mov r14, 3
    xor rcx, rcx
.ersur_dst_done:
    ; src low code / extension -> rax / rdx
    cmp r13, 1
    je .ersur_src_rbx
    mov rax, r13
    add rax, 2
    mov rdx, 1                ; REX.R
    jmp .ersur_src_done
.ersur_src_rbx:
    mov rax, 3
    xor rdx, rdx
.ersur_src_done:
    ; REX.W plus R(src extension) and B(dst extension).
    mov rdi, 0x48
    test rdx, rdx
    jz .ersur_no_r
    or rdi, 0x04
.ersur_no_r:
    test rcx, rcx
    jz .ersur_no_b
    or rdi, 0x01
.ersur_no_b:
    call emit_byte
    mov dil, 0x01             ; add r/m64,r64
    cmp r12, OP_ADD
    je .ersur_opcode_ready
    mov dil, 0x29             ; sub r/m64,r64
.ersur_opcode_ready:
    call emit_byte
    ; ModRM = 11 | src.low<<3 | dst.low
    and rax, 7
    shl rax, 3
    and r14, 7
    or rax, r14
    or rax, 0xC0
    mov dil, al
    call emit_byte
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; emit_stack_self_update_imm(rdi=negative disp8, rsi=OP_ADD/SUB,
;                            rdx=non-negative imm <= signed INT32_MAX)
; Emits an in-place arithmetic update with an imm8 or imm32 encoding.
emit_stack_self_update_imm:
    push rbx
    push r12
    push r13
    mov rbx, rdi              ; stack displacement
    mov r12, rsi              ; operator
    mov r13, rdx              ; immediate
    mov dil, 0x48
    call emit_byte
    mov dil, 0x83
    cmp r13, 127
    jbe .essui_emit_opcode
    mov dil, 0x81
.essui_emit_opcode:
    call emit_byte
    mov dil, 0x45             ; /0 ADD, [rbp+disp8]
    cmp r12, OP_ADD
    je .essui_modrm_ready
    mov dil, 0x6D             ; /5 SUB, [rbp+disp8]
.essui_modrm_ready:
    call emit_byte
    mov dil, bl
    call emit_byte
    cmp r13, 127
    ja .essui_wide_immediate
    mov dil, r13b
    call emit_byte
    jmp .essui_done
.essui_wide_immediate:
    mov edi, r13d
    call emit_u32
.essui_done:
    pop r13
    pop r12
    pop rbx
    ret

; emit_store_reg(dil = register ID) — emits "mov reg, rax"
emit_store_reg:
    push rbx
    push r12
    mov rbx, rdi              ; register ID
    ; Jump table based on register ID
    cmp rbx, 1
    je .esr_r1
    cmp rbx, 2
    je .esr_r2
    cmp rbx, 3
    je .esr_r3
    cmp rbx, 4
    je .esr_r4
    cmp rbx, 5
    je .esr_r5
    pop r12
    pop rbx
    ret
.esr_r1:   ; mov rbx, rax = 48 89 C3
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC3
    call emit_byte
    pop r12
    pop rbx
    ret
.esr_r2:   ; mov r12, rax = 49 89 C4
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC4
    call emit_byte
    pop r12
    pop rbx
    ret
.esr_r3:   ; mov r13, rax = 49 89 C5
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC5
    call emit_byte
    pop r12
    pop rbx
    ret
.esr_r4:   ; mov r14, rax = 49 89 C6
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC6
    call emit_byte
    pop r12
    pop rbx
    ret
.esr_r5:   ; mov r15, rax = 49 89 C7
    mov dil, 0x49
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xC7
    call emit_byte
    pop r12
    pop rbx
    ret

; emit_load_reg(dil = register ID) — emits "mov rax, reg"
emit_load_reg:
    push rbx
    push r12
    mov rbx, rdi
    cmp rbx, 1
    je .elr_r1
    cmp rbx, 2
    je .elr_r2
    cmp rbx, 3
    je .elr_r3
    cmp rbx, 4
    je .elr_r4
    cmp rbx, 5
    je .elr_r5
    pop r12
    pop rbx
    ret
.elr_r1:   ; mov rax, rbx = 48 89 D8
    mov dil, 0x48
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xD8
    call emit_byte
    pop r12
    pop rbx
    ret
.elr_r2:   ; mov rax, r12 = 4C 89 E0
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xE0
    call emit_byte
    pop r12
    pop rbx
    ret
.elr_r3:   ; mov rax, r13 = 4C 89 E8
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xE8
    call emit_byte
    pop r12
    pop rbx
    ret
.elr_r4:   ; mov rax, r14 = 4C 89 F0
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    pop r12
    pop rbx
    ret
.elr_r5:   ; mov rax, r15 = 4C 89 F8
    mov dil, 0x4C
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xF8
    call emit_byte
    pop r12
    pop rbx
    ret

; is_register(rax = location) → ZF=1 if stack, ZF=0 if register
; Tests if location > 0 (register IDs are 1-5)

; lookup_var(rdi = name ptr) → rax = stack offset
lookup_var:
    push rbx
    push r12
    push r13
    mov rbx, rdi              ; name to find
    mov r13, [rel var_cnt]
    xor r12, r12
.lv_loop:
    cmp r12, r13
    jae .lv_notfound
    imul rcx, r12, 16
    lea rdx, [rel var_table]
    mov rdi, [rdx + rcx]      ; table name ptr
    mov rsi, rbx              ; search name
    push rbx
    push r12
    push r13
    call strcmp
    pop r13
    pop r12
    pop rbx
    test rax, rax
    jz .lv_found
    inc r12
    jmp .lv_loop
.lv_found:
    imul rcx, r12, 16
    lea rdx, [rel var_table]
    mov rax, [rdx + rcx + 8]  ; offset
    pop r13
    pop r12
    pop rbx
    ret
.lv_notfound:
    ; Auto-allocate
    mov rdi, rbx
    call alloc_var
    pop r13
    pop r12
    pop rbx
    ret

; ============================================================
; ELF WRITER
; ============================================================
write_elf:
    ; choose target: Windows build always emits PE; on Linux a .exe
    ; output name selects PE (lets us build/test Windows binaries here).
    cmp qword [rel target_pe], 0
    jne write_pe
    push rbx
    mov rbx, rdi              ; filename
    ; Create file
    mov rsi, 0x241             ; O_WRONLY|O_CREAT|O_TRUNC
    mov rdx, 0o755
    call os_open
    mov [rel out_fd], rax
    ; Build headers on stack
    sub rsp, 64
    ; ELF header
    mov dword [rsp], 0x464C457F
    mov dword [rsp+4], 0x00010102
    xor rax, rax
    mov [rsp+8], rax
    mov word [rsp+16], 2
    mov word [rsp+18], 0x3E
    mov dword [rsp+20], 1
    mov rax, BASE_ADDR + HEADERS_SIZE
    mov [rsp+24], rax
    mov rax, ELF_HDR_SIZE
    mov [rsp+32], rax
    xor rax, rax
    mov [rsp+40], rax
    mov dword [rsp+48], 0
    mov word [rsp+52], 64
    mov word [rsp+54], 56
    mov word [rsp+56], 1
    mov word [rsp+58], 0
    mov word [rsp+60], 0
    mov word [rsp+62], 0
    ; Write ELF header
    mov rdi, [rel out_fd]
    mov rsi, rsp
    mov rdx, 64
    call os_write
    ; Program header
    mov dword [rsp], 1
    mov dword [rsp+4], 7
    mov rax, HEADERS_SIZE
    mov [rsp+8], rax
    mov rax, BASE_ADDR + HEADERS_SIZE
    mov [rsp+16], rax
    mov [rsp+24], rax
    mov rax, [rel code_sz]
    mov [rsp+32], rax         ; p_filesz = code_sz
    mov rax, [rel code_sz]
    add rax, 0x10000          ; p_memsz = code_sz + 64KB (BSS)
    mov [rsp+40], rax
    mov rax, 0x1000
    mov [rsp+48], rax
    ; Write program header
    mov rdi, [rel out_fd]
    mov rsi, rsp
    mov rdx, 56
    call os_write
    add rsp, 64
    ; Write code
    mov rdi, [rel out_fd]
    lea rsi, [rel code_buf]
    mov rdx, [rel code_sz]
    call os_write
    ; Close
    mov rdi, [rel out_fd]
    call os_close
%ifndef WINDOWS
    ; chmod +x
    mov rdi, rbx
    mov rsi, 0o755
    mov rax, 90
    syscall
%endif
    pop rbx
    ret

; ============================================================
; UTILITY FUNCTIONS
; ============================================================
strlen:
    xor rcx, rcx
.sl_loop:
    cmp byte [rdi], 0
    je .sl_done
    inc rdi
    inc rcx
    jmp .sl_loop
.sl_done:
    mov rax, rcx
    ret

strcmp:
.sc_loop:
    movzx ecx, byte [rdi]
    movzx edx, byte [rsi]
    cmp ecx, edx
    jne .sc_diff
    cmp ecx, 0
    je .sc_equal
    inc rdi
    inc rsi
    jmp .sc_loop
.sc_equal:
    xor rax, rax
    ret
.sc_diff:
    sub ecx, edx
    mov eax, ecx
    ret

itoa:
    mov rax, rdi
    mov rcx, 10
    add rsi, 20
    mov byte [rsi], 0
.ia_loop:
    xor rdx, rdx
    div rcx
    add dl, '0'
    dec rsi
    mov [rsi], dl
    test rax, rax
    jnz .ia_loop
    mov rax, rsi
    ret

print_str_z:
    push rdi
    call strlen
    pop rdi
    mov rdx, rax
    mov rsi, rdi
    mov rdi, 1
    call os_write
    ret

is_alpha:
    movzx eax, dil
    cmp eax, 'A'
    jb .ia_check_lower
    cmp eax, 'Z'
    jbe .ia_yes
.ia_check_lower:
    cmp eax, 'a'
    jb .ia_check_under
    cmp eax, 'z'
    jbe .ia_yes
.ia_check_under:
    cmp eax, '_'
    je .ia_yes
    ; Check for Devanagari UTF-8 start byte (0xE0)
    cmp eax, 0xE0
    je .ia_yes
    xor rax, rax
    ret
.ia_yes:
    mov rax, 1
    ret

is_digit:
    movzx eax, dil
    cmp eax, '0'
    jb .id_no
    cmp eax, '9'
    ja .id_no
    mov rax, 1
    ret
.id_no:
    xor rax, rax
    ret

is_hex:
    movzx eax, dil
    cmp eax, '0'
    jb .ih_no
    cmp eax, '9'
    jbe .ih_yes
    cmp eax, 'A'
    jb .ih_no
    cmp eax, 'F'
    jbe .ih_yes
    cmp eax, 'a'
    jb .ih_no
    cmp eax, 'f'
    jbe .ih_yes
.ih_no:
    xor rax, rax
    ret
.ih_yes:
    mov rax, 1
    ret

hexval:
    movzx eax, dil
    cmp eax, '9'
    jbe .hv_dec
    cmp eax, 'F'
    jbe .hv_upper
    sub eax, 'a'
    add eax, 10
    ret
.hv_upper:
    sub eax, 'A'
    add eax, 10
    ret
.hv_dec:
    sub eax, '0'
    ret

is_space:
    movzx eax, dil
    cmp eax, ' '
    je .is_yes
    cmp eax, 9
    je .is_yes
    cmp eax, 10
    je .is_yes
    cmp eax, 13
    je .is_yes
    xor rax, rax
    ret
.is_yes:
    mov rax, 1
    ret

lookup_keyword:
    push rbx
    push r12
    push r13
    mov r13, rdi              ; string to find
    lea rax, [rel kw_table_end]
    lea rcx, [rel kw_table]
    sub rax, rcx
    mov rcx, 24
    xor rdx, rdx
    div rcx                   ; rax = count
    mov rcx, rax
    lea r12, [rel kw_table]
.lk_loop:
    test rcx, rcx
    jz .lk_notfound
    mov rdi, r13
    mov rsi, [r12]
    push rcx
    call strcmp
    pop rcx
    test rax, rax
    jz .lk_found
    add r12, 24
    dec rcx
    jmp .lk_loop
.lk_found:
    mov rdx, [r12+16]         ; keyword id
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.lk_notfound:
    ; Also scan runtime-loaded language pack keywords
    mov rcx, [rel lang_kw_cnt]
    test rcx, rcx
    jz .lk_really_notfound
    lea r12, [rel lang_kw_table]
.lk_lang_loop:
    test rcx, rcx
    jz .lk_really_notfound
    mov rdi, r13
    mov rsi, [r12]
    push rcx
    call strcmp
    pop rcx
    test rax, rax
    jz .lk_found
    add r12, 24
    dec rcx
    jmp .lk_lang_loop
.lk_really_notfound:
    xor rax, rax
    xor rdx, rdx
    pop r13
    pop r12
    pop rbx
    ret

lookup_builtin:
    push rbx
    push r12
    push r13
    mov r13, rdi
    lea rax, [rel bn_table_end]
    lea rcx, [rel bn_table]
    sub rax, rcx
    mov rcx, 24
    xor rdx, rdx
    div rcx
    mov rcx, rax
    lea r12, [rel bn_table]
.lb_loop:
    test rcx, rcx
    jz .lb_notfound
    mov rdi, r13
    mov rsi, [r12]
    push rcx
    call strcmp
    pop rcx
    test rax, rax
    jz .lb_found
    add r12, 24
    dec rcx
    jmp .lb_loop
.lb_found:
    mov rdx, [r12+16]
    mov rax, 1
    pop r13
    pop r12
    pop rbx
    ret
.lb_notfound:
    ; Also scan runtime-loaded builtin aliases
    mov rcx, [rel lang_builtin_cnt]
    test rcx, rcx
    jz .lb_really_notfound
    lea r12, [rel lang_builtin_table]
.lb_lang_loop:
    test rcx, rcx
    jz .lb_really_notfound
    mov rdi, r13
    mov rsi, [r12]
    push rcx
    call strcmp
    pop rcx
    test rax, rax
    jz .lb_found
    add r12, 24
    dec rcx
    jmp .lb_lang_loop
.lb_really_notfound:
    xor rax, rax
    xor rdx, rdx
    pop r13
    pop r12
    pop rbx
    ret

%include "win/rtblob.inc"   ; embedded Win64 runtime bytes

; ============================================================
; PE64 WRITER (Windows target)
;   want_pe(filename) -> 1 if the name ends in .exe
;   write_pe(filename)  -> writes [512B headers][runtime blob][code]
; ============================================================
want_pe:
    push rbx
    push rdi                  ; strlen/strcmp advance rdi — keep the filename
    mov rbx, rdi
    call strlen
    cmp rax, 4
    jb .wp_no
    lea rdi, [rbx + rax - 4]
    lea rsi, [rel str_dot_exe]
    call strcmp
    test rax, rax
    jz .wp_yes
.wp_no:
    xor rax, rax
    pop rdi
    pop rbx
    ret
.wp_yes:
    mov rax, 1
    pop rdi
    pop rbx
    ret

write_pe:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    mov rsi, 0x241
    mov rdx, 0o755
    call os_open
    mov [rel out_fd], rax
    ; --- zero the 512-byte header block ---
    lea rdi, [rel pe_hdr]
    xor eax, eax
    mov ecx, 64
    rep stosq
    lea rdi, [rel pe_hdr]
    ; DOS header
    mov word [rdi], 0x5A4D
    mov dword [rdi+0x3C], 0x40
    ; PE signature + COFF
    mov dword [rdi+0x40], 0x00004550
    mov word [rdi+0x44], 0x8664
    mov word [rdi+0x46], 1
    mov word [rdi+0x54], 0xF0
    mov word [rdi+0x56], 0x0022
    ; Optional header
    mov word [rdi+0x58], 0x20B
    mov rax, [rel code_sz]
    add rax, RT_BLOB_LEN
    mov r12, rax                     ; section virtual size
    mov rcx, rax
    add rcx, 0x1FF
    and rcx, 0xFFFFFFFFFFFFFE00
    mov r13, rcx                     ; aligned raw size
    mov [rdi+0x5C], ecx
    mov eax, 0x1000 + RT_BLOB_LEN
    mov [rdi+0x68], eax
    mov dword [rdi+0x6C], 0x1000
    mov rax, 0x140000000
    mov [rdi+0x70], rax
    mov dword [rdi+0x78], 0x1000
    mov dword [rdi+0x7C], 0x200
    mov word [rdi+0x80], 6
    mov word [rdi+0x88], 6
    mov rax, r13
    add rax, 0x1000
    mov [rdi+0x90], eax
    mov dword [rdi+0x94], 0x200
    mov word [rdi+0x9C], 3
    mov rax, 0x100000
    mov [rdi+0xA0], rax
    mov rax, 0x1000
    mov [rdi+0xA8], rax
    mov rax, 0x100000
    mov [rdi+0xB0], rax
    mov rax, 0x1000
    mov [rdi+0xB8], rax
    mov dword [rdi+0xC4], 16
    ; section header
    mov dword [rdi+0x148], 0x74786574
    mov eax, r12d
    mov [rdi+0x150], eax
    mov dword [rdi+0x154], 0x1000
    mov eax, r13d
    mov [rdi+0x158], eax
    mov dword [rdi+0x15C], 0x200
    mov dword [rdi+0x16C], 0x60000020
    ; --- write headers ---
    mov rdi, [rel out_fd]
    lea rsi, [rel pe_hdr]
    mov rdx, 0x200
    call os_write
    ; --- write runtime blob ---
    mov rdi, [rel out_fd]
    lea rsi, [rel rt_blob]
    mov rdx, RT_BLOB_LEN
    call os_write
    ; --- patch recorded blob-call sites in the code buffer ---
    xor r12, r12
.pp_patch:
    cmp r12, [rel blob_call_cnt]
    jae .pp_patched
    lea rax, [rel blob_calls]
    mov rax, [rax + r12*8]           ; site offset within code buffer
    mov rcx, RT_BLOB_LEN
    add rcx, rax
    add rcx, 4                       ; site is the rel32 field: opcode+4 = next insn
    mov edx, RT_SYSCALL_OFF
    sub rdx, rcx                     ; rel32
    lea rcx, [rel code_buf]
    add rcx, rax
    mov [rcx], edx
    inc r12
    jmp .pp_patch
.pp_patched:
    ; --- write code ---
    mov rdi, [rel out_fd]
    lea rsi, [rel code_buf]
    mov rdx, [rel code_sz]
    call os_write
    ; --- pad to file alignment ---
    mov rax, [rel code_sz]
    add rax, RT_BLOB_LEN
    add rax, 0x1FF
    and rax, 0xFFFFFFFFFFFFFE00
    sub rax, [rel code_sz]
    sub rax, RT_BLOB_LEN
    mov r13, rax
.pp_pad:
    test r13, r13
    jle .pp_done
    mov rdx, r13
    cmp rdx, 0x100
    jbe .pp_pad_go
    mov rdx, 0x100
.pp_pad_go:
    mov rdi, [rel out_fd]
    lea rsi, [rel pe_pad]
    call os_write
    sub r13, rdx
    jmp .pp_pad
.pp_done:
    mov rdi, [rel out_fd]
    call os_close
    pop r13
    pop r12
    pop rbx
    ret

; ============================================================
; OS ABSTRACTION LAYER
;   os_write(fd, buf, len) / os_read(fd, buf, len)
;   os_open(path, flags, mode) -> fd  / os_close(fd) / os_exit(code)
;   os_readlink(path, buf, len)
; Linux: raw syscalls. Windows: kernel32 (see win/winrt.inc).
; ============================================================
%ifndef WINDOWS
os_write:
    mov rax, 1
    syscall
    ret
os_read:
    xor rax, rax
    syscall
    ret
os_open:
    mov rax, 2
    syscall
    ret
os_close:
    mov rax, 3
    syscall
    ret
os_exit:
    mov rax, 60
    syscall
    hlt
os_readlink:
    mov rax, 89
    syscall
    ret
%else
%include "win/winrt.inc"
%endif
