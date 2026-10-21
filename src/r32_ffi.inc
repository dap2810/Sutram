; ===================================================================
; ROUND-32: the FFI, the compiler's half - a checked foreign declaration.
;
;   sutram_compiler --ffi decls.sffi --object   in.sm out.smo
;   sutram_compiler --ffi decls.sffi --separate in.sm out.smo [root.sm]
;
; The sidecar (ChatGPT ROUND-97 WS1, v1) declares foreign functions without a
; Sutram body, so no parser change, no keyword, no pack:
;
;   sutram-ffi-v1|linux-x86_64-sysv
;   s_add|2|i64,i64|i64|sutram_ffi_add
;
; one LF-terminated line per declaration: local name | arity | argument kinds |
; return kind | the foreign symbol. R33: the argument kinds are i64, f64 and
; ptr; the result is i64, f64, ptr or void (R32 accepted i64 only). ASCII, no spaces, no CR, at most 8192 bytes and 64 declarations.
;
; What a declaration does, and what it never does:
;   * the sidecar is read once, after parsing (in SUTRAM_LANG's language) and
;     before any code; a malformed one is refused with its line;
;   * a call to the local name with the wrong number of arguments is E_ARITY,
;     with the call's own file:line:col, at the same point (after parsing,
;     before any code) as for a prakriya - so no object is written;
;   * a call with the right number becomes an R28 relocation carrying the
;     FOREIGN name, with the stack aligned to 16 bytes for the C ABI;
;   * it is NOT a prakriya: no FUNCDEF, no body, no stub, nothing exported; a
;     prakriya, builtin or keyword with either name is an error;
;   * without --ffi nothing here runs, and --ffi is accepted only with
;     --object or --separate: the ordinary compile never reads a sidecar.
; ===================================================================

R32_CAP      equ 64
R32_FILE_CAP equ 8192

section .bss
    r32_ffi_path  resq 1
    r32_ffi_count resq 1
    r32_ffi_rec   resq R32_CAP*4      ; (local name, arity, foreign symbol, R33 kinds)
    r33_kinds     resq 1
    r33_call_nodes resq R7_CALL_CAP   ; R33: the AST_FUNCALL of each r7 call (with --ffi)
    r32_buf       resb R32_FILE_CAP + 8
    r32_len       resq 1
    r32_line      resq 1

section .data
    r32_header    db "sutram-ffi-v1|linux-x86_64-sysv", 10
    r32_header_len equ $ - r32_header

section .text

; r32_bad: the sidecar is malformed at line r32_line (0: the file itself).
r32_bad:
    lea rdi, [rel r32_msg_ffi_bad]
    call print_str_z
    mov rax, [rel r32_line]
    call mg_print_uint
    lea rdi, [rel msg_nl]
    call print_str_z
    mov rdi, 1
    call os_exit

; r32_is_ident(rdi = NUL-terminated, rsi = max length) -> rax = 1 when
; [A-Za-z_][A-Za-z0-9_]* and 1..max bytes. Clobbers rcx, rdx.
r32_is_ident:
    xor ecx, ecx
.l: movzx edx, byte [rdi + rcx]
    test edx, edx
    jz .end
    cmp edx, '_'
    je .ok
    cmp edx, '0'
    jb .no
    cmp edx, '9'
    ja .alpha
    test rcx, rcx
    jz .no
    jmp .ok
.alpha:
    or edx, 0x20
    cmp edx, 'a'
    jb .no
    cmp edx, 'z'
    ja .no
.ok:
    inc rcx
    cmp rcx, rsi
    ja .no
    jmp .l
.end:
    test rcx, rcx
    jz .no
    mov eax, 1
    ret
.no:
    xor eax, eax
    ret

; r32_field(rsi = cursor) -> rax = the field (NUL-terminated in place),
; dl = what ended it ('|' or LF), rsi = past it. A byte outside 0x21..0x7E
; that is not '|' or LF, or the end of the buffer, is malformed.
r32_field:
    mov rax, rsi
    lea rcx, [rel r32_buf]
    add rcx, [rel r32_len]
.l: cmp rsi, rcx
    jae r32_bad
    movzx edx, byte [rsi]
    cmp edx, '|'
    je .end
    cmp edx, 10
    je .end
    cmp edx, 0x21
    jb r32_bad
    cmp edx, 0x7E
    ja r32_bad
    inc rsi
    jmp .l
.end:
    mov byte [rsi], 0
    inc rsi
    ret

; r32_load_sidecar: read and check the whole sidecar at [r32_ffi_path]. Called
; once, after parsing and before the arity check and any code, so a fault is
; reported in SUTRAM_LANG's language and no object is written. Any fault: a
; diagnostic with the line, exit 1.
r32_load_sidecar:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov qword [rel r32_line], 0
    mov rdi, [rel r32_ffi_path]
    xor esi, esi
    call os_open
    test rax, rax
    js r32_bad
    mov rbx, rax
    mov rdi, rbx
    lea rsi, [rel r32_buf]
    mov edx, R32_FILE_CAP + 1         ; one byte more than allowed: too big is seen
    call os_read
    mov r12, rax
    mov rdi, rbx
    call os_close
    test r12, r12
    jle r32_bad
    cmp r12, R32_FILE_CAP
    ja r32_bad
    mov [rel r32_len], r12
    lea rsi, [rel r32_buf]
    cmp byte [rsi + r12 - 1], 10      ; ends with LF
    jne r32_bad
    ; the header, exactly
    mov qword [rel r32_line], 1
    cmp r12, r32_header_len
    jb r32_bad
    lea rdi, [rel r32_header]
    xor ecx, ecx
.hdr:
    cmp rcx, r32_header_len
    jae .hdr_ok
    mov al, [rsi + rcx]
    cmp al, [rdi + rcx]
    jne r32_bad
    inc rcx
    jmp .hdr
.hdr_ok:
    add rsi, r32_header_len
    mov qword [rel r32_ffi_count], 0
.decl:
    lea rax, [rel r32_buf]
    add rax, [rel r32_len]
    cmp rsi, rax
    jae .done
    inc qword [rel r32_line]
    cmp qword [rel r32_ffi_count], R32_CAP
    jae r32_bad
    ; name | arity | kinds | return | symbol LF
    call r32_field
    cmp dl, '|'
    jne r32_bad
    mov r12, rax                      ; name
    call r32_field
    cmp dl, '|'
    jne r32_bad
    mov r13, rax                      ; arity
    call r32_field
    cmp dl, '|'
    jne r32_bad
    mov r14, rax                      ; kinds
    call r32_field
    cmp dl, '|'
    jne r32_bad
    mov r15, rax                      ; return
    call r32_field
    cmp dl, 10
    jne r32_bad
    mov rbx, rax                      ; symbol
    push rsi
    ; the local name and the symbol are identifiers
    mov rdi, r12
    mov esi, 63
    call r32_is_ident
    test eax, eax
    jz .bad_pop
    mov rdi, rbx
    mov esi, 127
    call r32_is_ident
    test eax, eax
    jz .bad_pop
    ; the arity: one digit, 0..6
    movzx eax, byte [r13]
    cmp byte [r13 + 1], 0
    jne .bad_pop
    sub eax, '0'
    cmp eax, 6
    ja .bad_pop
    mov r13, rax
    ; R33: the kinds: exactly arity times i64, f64 or ptr, comma-separated;
    ; the result: i64, f64, ptr or void. One byte each in r33_kinds (0 i64,
    ; 1 f64, 2 ptr, 3 void): bytes 0..5 the arguments, byte 6 the result.
    mov qword [rel r33_kinds], 0
    mov rdi, r14
    xor ecx, ecx                      ; kinds seen
.kind:
    cmp rcx, r13
    jae .kinds_end
    test rcx, rcx
    jz .kind_one
    cmp byte [rdi], ','
    jne .bad_pop
    inc rdi
.kind_one:
    call r33_kind3
    cmp eax, 2
    ja .bad_pop
    lea rdx, [rel r33_kinds]
    mov [rdx + rcx], al
    add rdi, 3
    inc rcx
    jmp .kind
.kinds_end:
    cmp byte [rdi], 0
    jne .bad_pop
    mov rdi, r15                      ; the result
    cmp dword [rdi], 0x64696F76       ; "void"
    jne .ret3
    cmp byte [rdi + 4], 0
    jne .bad_pop
    mov eax, 3
    jmp .ret_ok
.ret3:
    call r33_kind3
    cmp eax, 2
    ja .bad_pop
    cmp byte [rdi + 3], 0
    jne .bad_pop
.ret_ok:
    mov [rel r33_kinds + 6], al
    ; no name and no symbol twice
    xor r15d, r15d
.uniq:
    cmp r15, [rel r32_ffi_count]
    jae .store
    imul rax, r15, 32
    lea rcx, [rel r32_ffi_rec]
    add rcx, rax
    push rcx
    mov rdi, r12
    mov rsi, [rcx]
    call strcmp
    pop rcx
    test rax, rax
    jz .bad_pop
    push rcx
    mov rdi, rbx
    mov rsi, [rcx + 16]
    call strcmp
    pop rcx
    test rax, rax
    jz .bad_pop
    inc r15
    jmp .uniq
.store:
    mov rax, [rel r32_ffi_count]
    imul rax, rax, 32
    lea rcx, [rel r32_ffi_rec]
    add rcx, rax
    mov [rcx], r12
    mov [rcx + 8], r13
    mov [rcx + 16], rbx
    mov rax, [rel r33_kinds]
    mov [rcx + 24], rax
    inc qword [rel r32_ffi_count]
    pop rsi
    jmp .decl
.bad_pop:
    pop rsi
    jmp r32_bad
.done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; r32_ffi_find(rdi = local name) -> rax = its record, or 0. Preserves rbx, r12-r15.
r32_ffi_find:
    push rbx
    push r12
    mov rbx, rdi
    xor r12d, r12d
.l: cmp r12, [rel r32_ffi_count]
    jae .no
    imul rax, r12, 32
    lea rsi, [rel r32_ffi_rec]
    add rsi, rax
    push rsi
    mov rdi, rbx
    mov rsi, [rsi]
    call strcmp
    pop rsi
    test rax, rax
    jz .yes
    inc r12
    jmp .l
.yes:
    mov rax, rsi
    pop r12
    pop rbx
    ret
.no:
    xor eax, eax
    pop r12
    pop rbx
    ret

; r32_check_clashes: after parsing. A declared foreign function is not a
; prakriya: a prakriya (any module's), a builtin or a keyword with its local
; name or its foreign symbol is an error.
r32_check_clashes:
    push rbx
    push r12
    push r13
    xor r12d, r12d
.decl:
    cmp r12, [rel r32_ffi_count]
    jae .done
    imul rbx, r12, 32
    lea rax, [rel r32_ffi_rec]
    add rbx, rax
    xor r13d, r13d                    ; 0: the local name, 16: the symbol
.name:
    mov rdi, [rbx + r13]
    call lookup_builtin
    test rax, rax
    jnz .clash
    mov rdi, [rbx + r13]
    call lookup_keyword
    test rax, rax
    jnz .clash
    xor ecx, ecx
.def:
    cmp rcx, [rel r7_def_count]
    jae .name_next
    mov rax, rcx
    shl rax, 4
    lea rdx, [rel r7_defs]
    push rcx
    mov rdi, [rbx + r13]
    mov rsi, [rdx + rax]
    call strcmp
    pop rcx
    test rax, rax
    jz .clash
    inc rcx
    jmp .def
.name_next:
    add r13, 16
    cmp r13, 16
    jbe .name
    inc r12
    jmp .decl
.clash:
    lea rdi, [rel r32_msg_ffi_clash]
    call print_str_z
    mov rdi, [rbx + r13]
    call print_str_z
    lea rdi, [rel msg_nl]
    call print_str_z
    mov rdi, 1
    call os_exit
.done:
    pop r13
    pop r12
    pop rbx
    ret

; r32_gen_foreign_call(rsi = record): the arguments are already in rdi..r9.
;   mov r11, rsp / and rsp, -16 / push r11 / sub rsp, 8   ; rsp = 0 mod 16
;   call <foreign symbol>                                   ; an R28 relocation
;   add rsp, 8 / pop rsp                                    ; rsp as it was
; The patch names the foreign symbol, which no prakriya may have, so in an
; object it is always a hole. Preserves rbx, r12-r15.
r32_gen_foreign_call:
    push rbx
    mov rbx, rsi
    mov dil, 0x49                     ; mov r11, rsp
    call emit_byte
    mov dil, 0x89
    call emit_byte
    mov dil, 0xE3
    call emit_byte
    mov dil, 0x48                     ; and rsp, -16
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xE4
    call emit_byte
    mov dil, 0xF0
    call emit_byte
    mov dil, 0x41                     ; push r11
    call emit_byte
    mov dil, 0x53
    call emit_byte
    mov dil, 0x48                     ; sub rsp, 8
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xEC
    call emit_byte
    mov dil, 0x08
    call emit_byte
    mov dil, 0xE8                     ; call rel32
    call emit_byte
    mov rax, [rel code_sz]
    mov rdx, [rel patch_count]
    cmp rdx, PATCH_LIST_CAP
    jae .overflow
    lea r8, [rel patch_list]
    shl rdx, 4
    mov [r8 + rdx], rax
    mov rax, [rbx + 16]               ; the foreign symbol
    mov [r8 + rdx + 8], rax
    inc qword [rel patch_count]
    xor edi, edi
    call emit_u32
    mov dil, 0x48                     ; add rsp, 8
    call emit_byte
    mov dil, 0x83
    call emit_byte
    mov dil, 0xC4
    call emit_byte
    mov dil, 0x08
    call emit_byte
    mov dil, 0x5C                     ; pop rsp
    call emit_byte
    pop rbx
    ret
.overflow:
    lea rdi, [rel msg_patch_overflow]
    jmp capacity_fail

; -------------------------------------------------------------------
; ROUND-33: the FFI's kinds. A declared foreign call is generated here, with
; each argument checked against its declared kind:
;   i64  an integer: a dasham, a string or a kosh is an error (never truncated)
;   f64  a dasham, or an integer converted to dasham; a string or kosh: error
;   ptr  a string, a kosh (its elements' address) or an integer: a dasham: error
; Integer and pointer arguments go to rdi, rsi, rdx, rcx, r8, r9 in order;
; f64 arguments to xmm0..xmm5 in order (the System V rule: the two sequences
; are counted separately). The result: i64/ptr in rax; f64 from xmm0, and the
; call is a dasham to the rest of the compiler; a void call is a statement only
; (its value used anywhere is E_FFI_KIND, never a made-up 0).
; -------------------------------------------------------------------

; r33_kind3(rdi -> 3 bytes) -> eax = 0 i64, 1 f64, 2 ptr, or 9. Preserves the rest.
r33_kind3:
    cmp word [rdi], 0x3669             ; "i6"
    jne .f
    cmp byte [rdi + 2], '4'
    jne .no
    xor eax, eax
    ret
.f: cmp word [rdi], 0x3666             ; "f6"
    jne .p
    cmp byte [rdi + 2], '4'
    jne .no
    mov eax, 1
    ret
.p: cmp word [rdi], 0x7470             ; "pt"
    jne .no
    cmp byte [rdi + 2], 'r'
    jne .no
    mov eax, 2
    ret
.no:
    mov eax, 9
    ret

; r33_note_node(rax = the AST_FUNCALL, index = r7_call_count before it grows).
; Called from r7_note_call only when --ffi was given. Preserves every register.
r33_note_node:
    push rcx
    push rdx
    mov rcx, [rel r7_call_count]
    cmp rcx, R7_CALL_CAP
    jae .done
    lea rdx, [rel r33_call_nodes]
    mov [rdx + rcx*8], rax
.done:
    pop rdx
    pop rcx
    ret

; r33_return_is_float(rdi = name) -> rax = 1 when it is a declared foreign
; function whose result is f64.
r33_return_is_float:
    call r32_ffi_find
    test rax, rax
    jz .no
    cmp byte [rax + 24 + 6], 1
    jne .no
    mov eax, 1
    ret
.no:
    xor eax, eax
    ret

; r33_kind_error(rbx = the AST_FUNCALL, r13 = the argument index): located,
; like E_ARITY, at the call; then exit 1 (no object is written).
r33_kind_error:
    xor r12d, r12d
.find:
    cmp r12, [rel r7_call_count]
    jae .unlocated
    lea rax, [rel r33_call_nodes]
    cmp [rax + r12*8], rbx
    je .located
    inc r12
    jmp .find
.located:
    imul rax, r12, 24
    lea rcx, [rel r7_calls]
    mov rax, [rcx + rax + 16]         ; the name token
    mov rdi, [rax + 32]
    call r51_print_origin
    lea rdi, [rel r51_colon_space]
    call print_str_z
.unlocated:
    lea rdi, [rel r33_msg_ffi_kind]
    call print_str_z
    mov rdi, [rbx + 8]
    call print_str_z
    cmp r13, -1
    je .void_value
    lea rdi, [rel r33_msg_ffi_kind2]
    call print_str_z
    lea rax, [r13 + 1]
    call mg_print_uint
    lea rdi, [rel msg_nl]
    call print_str_z
    jmp .context
.void_value:
    lea rdi, [rel r33_msg_ffi_void]
    call print_str_z
.context:
    cmp r12, [rel r7_call_count]
    jae .exit
    call r51_print_original_context
.exit:
    mov rdi, 1
    call os_exit

; r33_gen_foreign_funcall(rbx = the AST_FUNCALL, rsi = its record, rdx = 1 when
; its value is used). A void function's value cannot be used: E_FFI_KIND.
r33_gen_foreign_funcall:
    push r12
    push r13
    push r14
    push r15
    mov r14, rsi
    test rdx, rdx
    jz .value_ok
    cmp byte [r14 + 24 + 6], 3
    jne .value_ok
    mov r13, -1                       ; "argument 0": the result
    jmp r33_kind_error
.value_ok:
    mov r15, [rbx + 16]               ; argc (the arity check has passed)
    xor r13d, r13d
.arg:
    cmp r13, r15
    jae .args_done
    mov r12, [rbx + 24 + r13*8]       ; the argument
    movzx eax, byte [r14 + 24 + r13]  ; its declared kind
    cmp eax, 2
    je .ptr
    ; i64 or f64: not a string, not a kosh
    cmp qword [r12], AST_STR
    je .bad
    cmp qword [r12], AST_VAR
    jne .scalar
    mov rdi, [r12 + 8]
    call is_kosh_var
    test rax, rax
    jnz .bad
.scalar:
    mov rdi, r12
    call expr_is_float
    movzx ecx, byte [r14 + 24 + r13]
    test ecx, ecx
    jnz .f64
    test rax, rax                     ; i64: a dasham is an error
    jnz .bad
    jmp .gen
.f64:
    push rax
    mov rax, r12
    call gen_expr
    pop rax
    test rax, rax
    jnz .push
    call emit_i64_to_f64_rax          ; an integer, as dasham
    jmp .push
.ptr:
    mov rdi, r12                      ; ptr: a dasham is an error
    call expr_is_float
    test rax, rax
    jnz .bad
.gen:
    mov rax, r12
    call gen_expr
.push:
    mov dil, 0x50                     ; push rax
    call emit_byte
    inc r13
    jmp .arg
.bad:
    jmp r33_kind_error
.args_done:
    ; pop them, the last first, into their registers
    xor ecx, ecx                      ; integers before argument k
    xor edx, edx                      ; f64s before argument k
    xor r13d, r13d
    lea rdi, [rel r33_slot]
.count:
    cmp r13, r15
    jae .counted
    movzx eax, byte [r14 + 24 + r13]
    cmp eax, 1
    je .count_f
    mov [rdi + r13], cl
    inc ecx
    jmp .count_next
.count_f:
    lea eax, [rdx + 0x80]             ; 0x80 | xmm number
    mov [rdi + r13], al
    inc edx
.count_next:
    inc r13
    jmp .count
.counted:
    mov r13, r15
.pop:
    test r13, r13
    jz .call
    dec r13
    lea rax, [rel r33_slot]
    movzx eax, byte [rax + r13]
    test eax, 0x80
    jnz .pop_xmm
    lea rcx, [rel r33_pop_int]
    movzx edi, word [rcx + rax*2]     ; the pop instruction, as two bytes
    test edi, 0xFF00
    jz .pop_one
    push rdi
    call emit_byte                    ; 0x41 prefix
    pop rdi
    shr edi, 8
.pop_one:
    call emit_byte
    jmp .pop
.pop_xmm:
    and eax, 0x7F
    push rax
    mov dil, 0x58                     ; pop rax
    call emit_byte
    mov dil, 0x66                     ; movq xmmN, rax = 66 48 0F 6E (C0 + 8N)
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x6E
    call emit_byte
    pop rax
    lea edi, [0xC0 + rax*8]
    call emit_byte
    jmp .pop
.call:
    mov rsi, r14
    call r32_gen_foreign_call
    movzx eax, byte [r14 + 24 + 6]
    cmp eax, 1
    jne .done                         ; i64, ptr: rax; void: a statement, unused
.ret_f64:
    mov dil, 0x66                     ; movq rax, xmm0 = 66 48 0F 7E C0
    call emit_byte
    mov dil, 0x48
    call emit_byte
    mov dil, 0x0F
    call emit_byte
    mov dil, 0x7E
    call emit_byte
    mov dil, 0xC0
    call emit_byte
.done:
    pop r15
    pop r14
    pop r13
    pop r12
    ret

section .data
    ; pop rdi, rsi, rdx, rcx, r8, r9 (a word: low byte first emitted; 0 high = one byte)
    r33_pop_int dw 0x005F, 0x005E, 0x005A, 0x0059, 0x5841, 0x5941
section .bss
    r33_slot resb 8
section .text
