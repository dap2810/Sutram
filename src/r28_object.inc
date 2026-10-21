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

section .bss
    r28_object_mode  resq 1
    r29_separate_mode resq 1            ; R29 --separate
    r29_yoj_root     resq 1             ; --separate's argv[4], or 0
    r29_decl_src     resq 1             ; source pointer of the top-level declaration
    r29_extern       resb FUNC_DEFS_CAP ; 1: func_defs[i] came from a yoj module
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
    cmp qword [rel r56_global_count], 0
    jne .globals
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
.globals:
    lea rdi, [rel r28_msg_object_globals]
    jmp capacity_fail

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
    mov rax, [rel r29_decl_src]
    lea rcx, [rel source_buf]
    sub rax, rcx
    jb .done
    cmp rax, IMPORT_BUF_CAP
    jae .done
    lea rcx, [rel r51_src_file]
    mov rax, [rcx + rax*8]
    test rax, rax
    jz .done
    cmp rax, [rel source_path_ptr]
    je .done
    lea rcx, [rel r29_extern]
    mov byte [rcx + rdx], 1
.done:
    pop rcx
    pop rax
    ret
