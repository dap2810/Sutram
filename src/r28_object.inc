; ===================================================================
; ROUND-28: the object file (`--object`), the compiler's half of our linker.
;
;   sutram_compiler --object in.sm out.smo
;
; compiles one module exactly as an ordinary compile does - the same parser,
; the same code generator, the same bytes - but instead of a finished
; executable it writes the code with its holes: every call to a prakriya this
; module does not define becomes a relocation for tools/../linker/sutram-link
; to fill. Off by default: without --object nothing here runs, and the
; ordinary one-pass path is the one every program has always taken.
;
; The format (docs/OBJECT-FORMAT.md), every number a little-endian u64:
;   0   "SUTRAMO1"                     magic
;   8   code_size
;   16  symbol_count                   prakriyas this module defines
;   24  relocation_count               rel32 holes this module leaves
;   32  code                           code_size bytes; mukhya (if any) at offset 0
;       symbols:     { offset, name_length, name bytes } x symbol_count
;       relocations: { offset of the rel32, name_length, name bytes } x relocation_count
; A relocation's rel32 is filled with  target - (offset + 4), as a call's is.
; A module with no mukhya is allowed in --object mode; it exports no mukhya.
; ===================================================================

R30_NAME_LEN equ 80

section .bss
    r28_object_mode  resq 1
    r29_separate_mode resq 1            ; R29 --separate
    r29_yoj_root     resq 1             ; --separate's argv[4], or 0
    r29_decl_src     resq 1             ; source pointer of the top-level declaration
    r29_extern       resb FUNC_DEFS_CAP ; 1: func_defs[i] came from a yoj module
    r30_gextern      resb R56_GLOBAL_CAP ; 1: global i came from a yoj module (--separate)
    r30_gslot        resq R56_GLOBAL_CAP ; offset of global i's 8 bytes in this object's code
    r30_gnames       resb R56_GLOBAL_CAP * R30_NAME_LEN ; "vitti:<name>", its link name
    r30_data_count   resq 1             ; the globals this object holds
    r28_no_mukhya    resq 1
    r28_relocs       resq R28_RELOC_CAP*2   ; (site, name)
    r28_reloc_count  resq 1
    r28_hdr          resq 4
section .text

; r28_add_reloc(rdi = site of the rel32, rsi = callee name). Preserves the rest.
r28_add_reloc:
    push rax
    push rcx
    mov rax, [rel r28_reloc_count]
    cmp rax, R28_RELOC_CAP
    jae .full
    shl rax, 4
    lea rcx, [rel r28_relocs]
    mov [rcx + rax], rdi
    mov [rcx + rax + 8], rsi
    inc qword [rel r28_reloc_count]
    pop rcx
    pop rax
    ret
.full:
    lea rdi, [rel msg_patch_overflow]
    jmp capacity_fail

; r28_put(rsi = bytes, rdx = length) to out_fd
r28_put:
    test rdx, rdx
    jz .done
    mov rdi, [rel out_fd]
    call os_write
.done:
    ret

; r28_put_u64(rax)
r28_put_u64:
    mov [rel r28_hdr], rax
    lea rsi, [rel r28_hdr]
    mov edx, 8
    jmp r28_put

; r28_put_name(rdi = NUL-terminated name): its length, then its bytes
r28_put_name:
    push rbx
    push r12
    mov rbx, rdi
    call strlen
    mov r12, rax
    call r28_put_u64
    mov rsi, rbx
    mov rdx, r12
    call r28_put
    pop r12
    pop rbx
    ret

; r28_write_object(rdi = output path)
r28_write_object:
    push rbx
    push r12
    mov rbx, rdi
    mov rdi, rbx
    mov rsi, 0x241                  ; O_WRONLY|O_CREAT|O_TRUNC
    mov rdx, 0o644
    call os_open
    test rax, rax
    js .done
    mov [rel out_fd], rax
    ; header
    mov rax, 0x314F4D4152545553     ; "SUTRAMO1"
    call r28_put_u64
    mov rax, [rel code_sz]
    call r28_put_u64
    mov rax, [rel func_count]
    add rax, [rel r30_data_count]   ; R30: and every vitti this object holds
    cmp qword [rel r28_no_mukhya], 0
    jne .n
    inc rax                         ; and mukhya
.n:
    call r28_put_u64
    mov rax, [rel r28_reloc_count]
    call r28_put_u64
    ; code
    lea rsi, [rel code_buf]
    mov rdx, [rel code_sz]
    call r28_put
    ; symbols: mukhya at 0, then every prakriya at its offset
    cmp qword [rel r28_no_mukhya], 0
    jne .syms
    xor eax, eax
    call r28_put_u64
    lea rdi, [rel kw_mukhya]
    call r28_put_name
.syms:
    xor r12d, r12d
.sl:
    cmp r12, [rel func_count]
    jae .relocs
    mov rax, r12
    shl rax, 4
    lea rcx, [rel func_table]
    mov rax, [rcx + rax + 8]        ; offset
    call r28_put_u64
    mov rax, r12
    shl rax, 4
    lea rcx, [rel func_table]
    mov rdi, [rcx + rax]            ; name
    call r28_put_name
    inc r12
    jmp .sl
.relocs:
    xor r12d, r12d                  ; R30: each vitti, as "vitti:<name>"
.dl:
    cmp r12, [rel r56_global_count]
    jae .dl_done
    lea rcx, [rel r30_gextern]
    cmp byte [rcx + r12], 0
    jne .dl_next
    lea rcx, [rel r30_gslot]
    mov rax, [rcx + r12*8]
    call r28_put_u64
    imul rdi, r12, R30_NAME_LEN
    lea rcx, [rel r30_gnames]
    add rdi, rcx
    call r28_put_name
.dl_next:
    inc r12
    jmp .dl
.dl_done:
    xor r12d, r12d
    xor r12d, r12d
.rl:
    cmp r12, [rel r28_reloc_count]
    jae .close
    mov rax, r12
    shl rax, 4
    lea rcx, [rel r28_relocs]
    mov rax, [rcx + rax]
    call r28_put_u64
    mov rax, r12
    shl rax, 4
    lea rcx, [rel r28_relocs]
    mov rdi, [rcx + rax + 8]
    call r28_put_name
    inc r12
    jmp .rl
.close:
    mov rdi, [rel out_fd]
    call os_close
.done:
    pop r12
    pop rbx
    ret

; r28_empty_mukhya: --object mode, the module ends with no mukhya. rax = an
; empty block for mukhya's body (it compiles to the usual exit, and is not
; exported, so no other module can reach it).
r28_empty_mukhya:
    mov qword [rel r28_no_mukhya], 1
    call alloc_ast
    mov qword [rax], AST_BLOCK
    mov qword [rax + 8], 0
    ret

; -------------------------------------------------------------------
; ROUND-29: separate compilation (--separate). Only that flag reaches these.
; -------------------------------------------------------------------
section .text

; r29_note_decl: remember where the top-level declaration about to be parsed
; starts in the flattened source. Clobbers rax, rcx.
r29_note_decl:
    call cur_tok
    mov rax, [rax+32]
    mov [rel r29_decl_src], rax
    ret

; r29_mark_extern(rdx = func_defs index): when the declaration noted by
; r29_note_decl came from a module (its origin is not the file being
; compiled), mark it: it is parsed and checked, but generates no code.
r29_mark_extern:
    push rax
    push rcx
    call r29_decl_from_module
    test rax, rax
    jz .done
    lea rcx, [rel r29_extern]
    mov byte [rcx + rdx], 1
.done:
    pop rcx
    pop rax
    ret

; r29_decl_from_module -> rax = 1 when the declaration noted by r29_note_decl
; came from a file other than the one being compiled. Clobbers rcx.
r29_decl_from_module:
    mov rax, [rel r29_decl_src]
    lea rcx, [rel source_buf]
    sub rax, rcx
    jb .no
    cmp rax, IMPORT_BUF_CAP
    jae .no
    lea rcx, [rel r51_src_file]
    mov rax, [rcx + rax*8]
    test rax, rax
    jz .no
    cmp rax, [rel source_path_ptr]
    je .no
    mov eax, 1
    ret
.no:
    xor eax, eax
    ret

; -------------------------------------------------------------------
; ROUND-30: a module-level vitti in an object.
;
; Each object holds the 8 bytes of every vitti declared in it, after its code
; (where the one-pass compile puts them), and exports each one as the symbol
; "vitti:<name>" - a name no prakriya can have. In --separate, a vitti that a
; yoj brought in is not held here: every access to it is a rel32 relocation to
; "vitti:<name>", the same arithmetic as a call (the displacement is the last
; four bytes of the instruction). The program's root initializes every vitti,
; its modules' too, at the start of mukhya, in source order - as the one-pass
; compile does. So a library object compiled with plain --object (no root)
; refuses a vitti with an initializer: nobody would run it.
; -------------------------------------------------------------------

; r30_mark_global_extern: --separate; the global just registered (the last)
; came from a module: mark it.
r30_mark_global_extern:
    push rax
    push rcx
    push rdx
    call r29_decl_from_module
    test rax, rax
    jz .done
    mov rdx, [rel r56_global_count]
    dec rdx
    lea rcx, [rel r30_gextern]
    mov byte [rcx + rdx], 1
.done:
    pop rdx
    pop rcx
    pop rax
    ret

; r30_object_globals: r56_patch_global_storage in --object / --separate mode
; (ELF only; the Windows compiler has no object mode).
r30_object_globals:
    push rbx
    push r12
    push r13
    push r14
    ; 1. names and slots; and the refusal
    mov r14, [rel code_sz]           ; the next slot
    xor r12d, r12d
.ng:
    cmp r12, [rel r56_global_count]
    jae .ng_done
    cmp qword [rel r29_separate_mode], 0
    jne .ng_ok
    cmp qword [rel r28_no_mukhya], 0
    je .ng_ok
    lea rcx, [rel r56_global_nodes]  ; plain --object, no mukhya, an initializer
    mov rcx, [rcx + r12*8]
    cmp qword [rcx + 16], 0
    je .ng_ok
    lea rdi, [rel r28_msg_object_globals]
    jmp capacity_fail
.ng_ok:
    lea rcx, [rel r56_global_names]  ; "vitti:" + name
    mov rsi, [rcx + r12*8]
    imul rdi, r12, R30_NAME_LEN
    lea rcx, [rel r30_gnames]
    add rdi, rcx
    mov dword [rdi], 0x74746976      ; "vitt"
    mov word [rdi+4], 0x3A69         ; "i:"
    add rdi, 6
    mov ecx, R30_NAME_LEN - 7
.ng_copy:
    mov al, [rsi]
    mov [rdi], al
    test al, al
    jz .ng_named
    inc rsi
    inc rdi
    dec ecx
    jnz .ng_copy
    lea rdi, [rel r56_msg_global_capacity]
    jmp capacity_fail
.ng_named:
    lea rcx, [rel r30_gextern]
    cmp byte [rcx + r12], 0
    jne .ng_next
    lea rcx, [rel r30_gslot]
    mov [rcx + r12*8], r14
    add r14, 8
    inc qword [rel r30_data_count]
.ng_next:
    inc r12
    jmp .ng
.ng_done:
    ; 2. every access: a held vitti is patched here; another module's is a hole
    xor r13d, r13d
.pt:
    cmp r13, [rel r56_patch_count]
    jae .pt_done
    lea rdx, [rel r56_patches]
    mov rcx, r13
    shl rcx, 4
    mov rbx, [rdx + rcx]             ; the rel32's offset
    mov r12, [rdx + rcx + 8]         ; the global's index
    lea rcx, [rel r30_gextern]
    cmp byte [rcx + r12], 0
    jne .pt_hole
    lea rcx, [rel r30_gslot]
    mov rax, [rcx + r12*8]
    sub rax, rbx
    sub rax, 4
    lea rdx, [rel code_buf]
    mov [rdx + rbx], eax
    jmp .pt_next
.pt_hole:
    mov rdi, rbx
    imul rsi, r12, R30_NAME_LEN
    lea rcx, [rel r30_gnames]
    add rsi, rcx
    call r28_add_reloc
.pt_next:
    inc r13
    jmp .pt
.pt_done:
    ; 3. the held vitti's storage, zero, after the code
    xor r13d, r13d
.st:
    cmp r13, [rel r30_data_count]
    jae .st_done
    xor edi, edi
    call emit_u32
    xor edi, edi
    call emit_u32
    inc r13
    jmp .st
.st_done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
