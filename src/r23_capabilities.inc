; ===================================================================
; ROUND-23: language capabilities, the smallest working versions.
;
; WS1  a function is a value. A bare `prakriya` name in an expression is the
;      function's address (AST_FUNCREF: lea rax,[rip+disp32], patched with the
;      calls). A call through a name that is not a function but a variable
;      (`cmp(a, b)` where cmp is a parameter) is an indirect call (call rax).
;      No closures: a function value is a code address, nothing captured.
; WS2  methods: `prakriya Bindu.dur(p, ...)` declares a method of rachana
;      Bindu; `q.dur(...)` calls it with q as the first argument. A method is
;      found by its name, as a field is (the compiler has no static types).
; WS3  slices: `a[lo:hi]` is a view of elements lo..hi-1 of a mala, a kosh or
;      another slice: a two-qword descriptor (element pointer, length) in the
;      frame of the function that makes it. `vibhag s` declares a slice
;      parameter; s[i] is bounds-checked against the slice's own length.
; ===================================================================

section .bss
    r23_pend_node   resq R4_PEND_CAP   ; WS1: the AST_VAR node of each pending read
    r23_tmp_var     resb AST_NODE_SIZE ; WS1: scratch AST_VAR for loading a callee
    r23_methods     resq R23_METHOD_CAP*3   ; WS2: (rachana name, method name, full name)
    r23_method_count resq 1
    r23_mname_pool  resb R23_METHOD_CAP*64  ; WS2: "Rachana.method\0" strings
    r23_mcalls      resq R23_MCALL_CAP*4    ; WS2: (node, method name, token, r7 call index)
    r23_mcall_count resq 1
section .text

; r23_is_defined_func(rdi = name) -> rax = 1 if the program defines a prakriya
; of that name (r7_defs: every definition, including modules). Preserves the rest.
r23_is_defined_func:
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r12
    mov rbx, rdi
    xor r12d, r12d
.l:
    cmp r12, [rel r7_def_count]
    jae .no
    mov rax, r12
    shl rax, 4
    lea rdx, [rel r7_defs]
    mov rsi, [rdx + rax]
    mov rdi, rbx
    call strcmp
    test rax, rax
    jz .yes
    inc r12
    jmp .l
.yes:
    mov eax, 1
    jmp .out
.no:
    xor eax, eax
.out:
    pop r12
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret

; r23_var_known(rdi = name) -> rax = 1 if it is a variable of the function being
; generated (var_table) or a module-level global. Never allocates. Preserves the rest.
r23_var_known:
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r12
    mov rbx, rdi
    xor r12d, r12d
.l:
    cmp r12, [rel var_cnt]
    jae .glob
    mov rax, r12
    shl rax, 4
    lea rdx, [rel var_table]
    mov rsi, [rdx + rax]
    mov rdi, rbx
    call strcmp
    test rax, rax
    jz .yes
    inc r12
    jmp .l
.glob:
    xor r12d, r12d
.g:
    cmp r12, [rel r56_global_count]
    jae .no
    lea rdx, [rel r56_global_names]
    mov rsi, [rdx + r12*8]
    mov rdi, rbx
    call strcmp
    test rax, rax
    jz .yes
    inc r12
    jmp .g
.yes:
    mov eax, 1
    jmp .out
.no:
    xor eax, eax
.out:
    pop r12
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret

; r23_call_is_indirect(rdi = callee name) -> rax = 1 when the call goes through
; a variable: the name is not a prakriya and is a variable. A prakriya wins, so
; every program that compiled before R23 calls what it called before.
r23_call_is_indirect:
    call r23_is_defined_func
    test rax, rax
    jnz .no
    call r23_var_known
    ret
.no:
    xor eax, eax
    ret

; r23_emit_rip_patch(rdi = function name): emit a zero disp32 and record it in
; patch_list like a call's rel32. backpatch_calls writes target - (site + 4),
; which is the RIP-relative displacement of an instruction ending at site + 4.
r23_emit_rip_patch:
    push rbx
    push rcx
    push rdx
    push r8
    mov rbx, rdi
    mov rax, [rel code_sz]
    mov rdx, [rel patch_count]
    cmp rdx, PATCH_LIST_CAP
    jae .overflow
    lea r8, [rel patch_list]
    shl rdx, 4
    mov [r8 + rdx], rax
    mov [r8 + rdx + 8], rbx
    inc qword [rel patch_count]
    xor edi, edi
    call emit_u32
    pop r8
    pop rdx
    pop rcx
    pop rbx
    ret
.overflow:
    lea rdi, [rel msg_patch_overflow]
    jmp capacity_fail

; r23_gen_funcref(rbx = AST_FUNCREF node): rax = the function's address.
r23_gen_funcref:
    mov dil, 0x48             ; lea rax, [rip + disp32]
    call emit_byte
    mov dil, 0x8D
    call emit_byte
    mov dil, 0x05
    call emit_byte
    mov rdi, [rbx + 8]
    call r23_emit_rip_patch
    ret

; r23_emit_indirect_call(rdi = variable name): load it into rax, call rax.
; Emitted after the arguments are in rdi..r9 and r12-r15 are saved; loading a
; variable writes only rax. Preserves the compiler's registers.
r23_emit_indirect_call:
    push rbx
    push r12
    push r13
    push r14
    push r15
    lea rax, [rel r23_tmp_var]
    mov qword [rax], AST_VAR
    mov [rax + 8], rdi
    mov qword [rax + 16], 0
    mov qword [rax + 24], 0
    call gen_expr
    mov dil, 0xFF             ; call rax
    call emit_byte
    mov dil, 0xD0
    call emit_byte
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; r23_resolve_pending_read(r12 = pending index, rbx = its token) -> rax = 1 when
; the unresolved bare read is a prakriya name: its node becomes AST_FUNCREF.
r23_resolve_pending_read:
    lea rax, [rel r23_pend_node]
    mov rax, [rax + r12*8]
    test rax, rax
    jz .no                    ; not a read from parse_primary (an assignment target)
    mov rdi, [rbx + 8]
    call r23_is_defined_func
    test rax, rax
    jz .no
    lea rax, [rel r23_pend_node]
    mov rax, [rax + r12*8]
    mov qword [rax], AST_FUNCREF
    mov eax, 1
    ret
.no:
    xor eax, eax
    ret

; ------------------------------------------------------------------- WS2
; r23_parse_method_def(rbx = the name after `prakriya`; the current token is
; '.') -> rbx = "Rachana.method", registered as a method of that rachana.
; The rachana must be declared before its methods, as before its field uses.
r23_parse_method_def:
    push r12
    push r13
    ; the rachana name token is the one before '.'
    mov rax, [rel token_idx]
    dec rax
    imul rax, rax, TOKEN_SIZE
    lea rcx, [rel token_arr]
    add rax, rcx
    mov r13, rax                ; rachana name token
    xor r12d, r12d
.find:
    cmp r12, [rel rachana_cnt]
    jae .unknown_rachana
    mov rax, r12
    shl rax, 8
    lea rcx, [rel rachana_defs]
    mov rsi, [rcx + rax]
    mov rdi, rbx
    call strcmp
    test rax, rax
    jz .found
    inc r12
    jmp .find
.unknown_rachana:
    mov rbx, r13
    call r4_report              ; unknown name 'Rachana'
    mov rdi, 1
    call os_exit
.found:
    call advance_tok            ; consume '.'
    call cur_tok
    cmp qword [rax], TOK_IDENT
    jne parse_error
    mov r12, [rax + 8]          ; method name
    call advance_tok
    mov rax, [rel r23_method_count]
    cmp rax, R23_METHOD_CAP
    jae .full
    ; full name = rachana + "." + method, at most 63 bytes
    imul rdi, rax, 64
    lea rcx, [rel r23_mname_pool]
    add rdi, rcx
    mov r13, rdi                ; full name
    mov rsi, rbx
    xor ecx, ecx
.c1:
    mov dl, [rsi]
    test dl, dl
    jz .dot
    cmp ecx, 62
    jae parse_error
    mov [rdi + rcx], dl
    inc rsi
    inc ecx
    jmp .c1
.dot:
    mov byte [rdi + rcx], '.'
    inc ecx
    mov rsi, r12
.c2:
    mov dl, [rsi]
    test dl, dl
    jz .end
    cmp ecx, 63
    jae parse_error
    mov [rdi + rcx], dl
    inc rsi
    inc ecx
    jmp .c2
.end:
    mov byte [rdi + rcx], 0
    mov rax, [rel r23_method_count]
    imul rax, rax, 24
    lea rcx, [rel r23_methods]
    mov [rcx + rax], rbx        ; rachana
    mov [rcx + rax + 8], r12    ; method
    mov [rcx + rax + 16], r13   ; full name
    inc qword [rel r23_method_count]
    mov rbx, r13
    pop r13
    pop r12
    ret
.full:
    lea rdi, [rel msg_func_table_overflow]
    jmp capacity_fail

; r23_note_method_call(rax = AST_FUNCALL node, rbx = method name, rcx = token).
; Remembered until the whole program is parsed; methods may be defined later.
; Preserves every register.
r23_note_method_call:
    push rdx
    push r8
    mov rdx, [rel r23_mcall_count]
    cmp rdx, R23_MCALL_CAP
    jae .full
    shl rdx, 5
    lea r8, [rel r23_mcalls]
    mov [r8 + rdx], rax
    mov [r8 + rdx + 8], rbx
    mov [r8 + rdx + 16], rcx
    push rax
    mov rax, [rel r7_call_count]   ; r7_note_call is about to store this call here
    mov [r8 + rdx + 24], rax
    pop rax
    inc qword [rel r23_mcall_count]
    pop r8
    pop rdx
    ret
.full:
    lea rdi, [rel msg_func_table_overflow]
    jmp capacity_fail

; r23_resolve_methods: after the parse, before the arity check. Each q.m(...)
; becomes a call of the one "R.m" whose method name is m. No method m: the
; unknown-field diagnostic at m; methods m of two rachanas: the ambiguous-field one.
r23_resolve_methods:
    push rbx
    push r12
    push r13
    push r14
    push r15
    xor r12d, r12d
.call:
    cmp r12, [rel r23_mcall_count]
    jae .done
    mov rax, r12
    shl rax, 5
    lea rbx, [rel r23_mcalls]
    add rbx, rax                ; rbx -> (node, method, token, r7 index)
    xor r13d, r13d              ; method index
    xor r14d, r14d              ; matches
    xor r15d, r15d              ; full name of the first match
.m:
    cmp r13, [rel r23_method_count]
    jae .judge
    imul rax, r13, 24
    lea rcx, [rel r23_methods]
    mov rsi, [rcx + rax + 8]
    mov rdi, [rbx + 8]
    call strcmp
    test rax, rax
    jnz .mnext
    inc r14
    test r15, r15
    jnz .mnext
    imul rax, r13, 24
    lea rcx, [rel r23_methods]
    mov r15, [rcx + rax + 16]
.mnext:
    inc r13
    jmp .m
.judge:
    mov rax, [rbx + 16]
    mov [rel r5_field_tok], rax
    test r14, r14
    jz r5_unknown_field
    cmp r14, 1
    ja r7_report_ambiguous_field
    mov rax, [rbx]
    mov [rax + 8], r15          ; the node calls "R.m"
    mov rax, [rbx + 24]
    cmp rax, [rel r7_call_count]
    jae .next
    imul rax, rax, 24
    lea rcx, [rel r7_calls]
    mov [rcx + rax], r15        ; and the arity check checks "R.m"
.next:
    inc r12
    jmp .call
.done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ------------------------------------------------------------------- WS3
section .bss
    r23_slice_vars     resq 256    ; slice names in the function being generated
    r23_slice_var_cnt  resq 1
section .text

; r23_mark_slice_var(rdi = name). Preserves every register.
r23_mark_slice_var:
    push rax
    push rcx
    mov rax, [rel r23_slice_var_cnt]
    cmp rax, 256
    jae .full
    lea rcx, [rel r23_slice_vars]
    mov [rcx + rax*8], rdi
    inc qword [rel r23_slice_var_cnt]
    pop rcx
    pop rax
    ret
.full:
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail

; r23_is_slice_var(rdi = name) -> rax = 1 if marked. Preserves the rest.
r23_is_slice_var:
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r12
    mov rbx, rdi
    xor r12d, r12d
.l:
    cmp r12, [rel r23_slice_var_cnt]
    jae .no
    lea rdx, [rel r23_slice_vars]
    mov rsi, [rdx + r12*8]
    mov rdi, rbx
    call strcmp
    test rax, rax
    jz .yes
    inc r12
    jmp .l
.yes:
    mov eax, 1
    jmp .out
.no:
    xor eax, eax
.out:
    pop r12
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret

; r23_expr_is_slice(rdi = AST) -> rax = 1 for a slice expression or a slice variable.
r23_expr_is_slice:
    test rdi, rdi
    jz .no
    cmp qword [rdi], AST_SLICE
    je .yes
    cmp qword [rdi], AST_VAR
    jne .no
    mov rdi, [rdi + 8]
    jmp r23_is_slice_var
.yes:
    mov eax, 1
    ret
.no:
    xor eax, eax
    ret

; r23_mark_slice_decl(rdi = AST_DECL): `vitti s = a[lo:hi]` and `vitti t = s`
; declare slices. Preserves every register.
r23_mark_slice_decl:
    push rax
    push rdi
    push rsi
    mov rsi, rdi
    mov rdi, [rsi + 16]          ; initializer
    call r23_expr_is_slice
    test rax, rax
    jz .done
    mov rdi, [rsi + 8]
    call r23_mark_slice_var
.done:
    pop rsi
    pop rdi
    pop rax
    ret

; r23_check_return(rdi = return expression): a slice lives in the frame of the
; function that made it, so returning one is an error.
r23_check_return:
    push rax
    push rdi
    call r23_expr_is_slice
    test rax, rax
    jnz .bad
    pop rdi
    pop rax
    ret
.bad:
    lea rdi, [rel r23_msg_slice_return]
    jmp capacity_fail            ; print_str_z translates it

; r23_slice_base_fail: the base of a[lo:hi], or the argument of a vibhag
; parameter, is not a mala, an integer kosh or a slice.
r23_slice_base_fail:
    lea rdi, [rel r23_msg_slice_base]
    jmp capacity_fail            ; print_str_z translates it

; r23_emit_load_name(rdi = variable name): rax = its value at run time.
r23_emit_load_name:
    push rbx
    push rdi
    call alloc_ast
    pop rdi
    mov qword [rax], AST_VAR
    mov [rax + 8], rdi
    call gen_expr
    pop rbx
    ret

; r23_emit_bytes(rsi = byte string, rcx = count)
r23_emit_bytes:
    push rbx
    push r12
    mov rbx, rsi
    mov r12, rcx
.l:
    test r12, r12
    jz .done
    movzx edi, byte [rbx]
    call emit_byte
    inc rbx
    dec r12
    jmp .l
.done:
    pop r12
    pop rbx
    ret

%macro R23_EMIT 1+
    jmp %%skip
%%bytes: db %1
%%end:
%%skip:
    lea rsi, [rel %%bytes]
    mov ecx, %%end - %%bytes
    call r23_emit_bytes
%endmacro

; r23_gen_slice(rbx = AST_SLICE [type][base name][lo or 0][hi or 0]):
; rax = the address of a two-qword descriptor (element pointer, length) in a
; frame slot of this site. Checks 0 <= lo <= hi <= the base's length at run
; time, with the index-bounds diagnostic.
r23_gen_slice:
    push r12
    push r13
    mov r12, [rbx + 8]           ; base name
    ; kind of the base, at compile time
    mov rdi, r12
    call r23_is_slice_var
    test rax, rax
    jnz .k_slice
    mov rdi, r12
    call is_kosh_var
    test rax, rax
    jnz .k_kosh
    mov rdi, r12
    call is_array_var
    test rax, rax
    jnz .k_mala
    jmp r23_slice_base_fail
.k_kosh:
    mov rdi, r12
    call is_float_kosh_var
    test rax, rax
    jnz r23_slice_base_fail      ; a kosh dasham holds binary64: not this version
    mov r13d, 2
    jmp .load
.k_mala:
    mov r13d, 1
    jmp .load
.k_slice:
    mov r13d, 3
.load:
    mov rdi, r12
    call r23_emit_load_name      ; rax = base value
    cmp r13d, 1
    je .len_mala
    cmp r13d, 2
    je .len_kosh
    R23_EMIT 0x48,0x8B,0x48,0x08       ; mov rcx,[rax+8]    slice length
    R23_EMIT 0x48,0x8B,0x00            ; mov rax,[rax]      slice elements
    jmp .have
.len_mala:
    R23_EMIT 0x48,0x8B,0x48,0xF8       ; mov rcx,[rax-8]
    jmp .have
.len_kosh:
    R23_EMIT 0x48,0x8B,0x48,0xF0       ; mov rcx,[rax-16]
.have:
    R23_EMIT 0x50,0x51                 ; push rax (elements); push rcx (length)
    ; lo -> push
    mov rax, [rbx + 16]
    test rax, rax
    jz .lo0
    call gen_expr
    jmp .lo_done
.lo0:
    R23_EMIT 0x31,0xC0                 ; xor eax,eax
.lo_done:
    R23_EMIT 0x50                      ; push rax (lo)
    ; hi -> rax (omitted: the length)
    mov rax, [rbx + 24]
    test rax, rax
    jz .hi_len
    call gen_expr
    jmp .hi_done
.hi_len:
    R23_EMIT 0x48,0x8B,0x44,0x24,0x08  ; mov rax,[rsp+8]
.hi_done:
    ; hi <= length: hi < length + 1 (unsigned, so a negative hi fails too)
    R23_EMIT 0x48,0x8B,0x4C,0x24,0x08  ; mov rcx,[rsp+8]
    R23_EMIT 0x48,0xFF,0xC1            ; inc rcx
    R23_EMIT 0x51                      ; push rcx
    call emit_array_bounds_check
    R23_EMIT 0x59                      ; pop rcx
    ; lo <= hi: lo < hi + 1
    R23_EMIT 0x48,0x89,0xC2            ; mov rdx,rax        hi
    R23_EMIT 0x48,0x8D,0x48,0x01       ; lea rcx,[rax+1]
    R23_EMIT 0x51                      ; push rcx
    R23_EMIT 0x48,0x8B,0x44,0x24,0x08  ; mov rax,[rsp+8]    lo
    call emit_array_bounds_check
    R23_EMIT 0x59                      ; pop rcx
    R23_EMIT 0x48,0x89,0xC1            ; mov rcx,rax        lo
    R23_EMIT 0x48,0x29,0xCA            ; sub rdx,rcx        hi - lo
    R23_EMIT 0x58,0x58,0x58            ; pop lo, pop length, pop elements -> rax
    R23_EMIT 0x4C,0x8D,0x04,0xC8       ; lea r8,[rax+rcx*8]
    ; this site's descriptor: 16 bytes of the frame
    mov rax, [rel stack_dep]
    add rax, 16
    cmp rax, FUNC_SPILL_BYTES - 16
    ja .no_room
    mov [rel stack_dep], rax
    neg rax
    push rax
    R23_EMIT 0x48,0x8D                 ; lea rax,[rbp+disp]
    pop rax
    push rsi
    mov esi, eax
    mov dil, 0x45
    call emit_rbp_modrm_disp
    pop rsi
    R23_EMIT 0x4C,0x89,0x00            ; mov [rax],r8       elements
    R23_EMIT 0x48,0x89,0x50,0x08       ; mov [rax+8],rdx    length
    pop r13
    pop r12
    ret
.no_room:
    lea rdi, [rel msg_var_table_overflow]
    jmp capacity_fail

; r23_index_slice(rdi = variable name) -> rax = 1 when it is a slice: then the
; code emitted turns the value in rax (the descriptor) into the element pointer,
; pushed, and its length, pushed: the same two stack words as a mala's.
r23_index_slice:
    call r23_is_slice_var
    test rax, rax
    jz .no
    R23_EMIT 0x48,0x8B,0x48,0x08       ; mov rcx,[rax+8]    length
    R23_EMIT 0x48,0x8B,0x00            ; mov rax,[rax]      elements
    R23_EMIT 0x50,0x51                 ; push rax; push rcx
    mov eax, 1
    ret
.no:
    xor eax, eax
    ret
