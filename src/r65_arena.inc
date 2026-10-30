; ============================================================
; ROUND-65 (Step 1): nirmmita becomes a contiguous bump; kosh grows in place.
;
; Linux ELF, ordinary (non --object) builds only. PE output and object mode keep
; the per-call mmap sequence unchanged (Windows is the owner's work).
;
; Two hidden module globals, registered at the FIRST nirmmita emission so that a
; program which never allocates gets no new storage and the same bytes as before:
;   0kshetra_cur  the bump cursor (0 until the arena is reserved)
;   0kshetra_end  one past the arena
; The arena is one mmap of R65_ARENA bytes with MAP_NORESERVE at the first
; nirmmita; pages cost only when touched, so small blocks share pages (the
; measured cost today is one page fault + 4 KiB zeroed per allocation).
;
; Emitted at every nirmmita site (rax = size on entry, rax = block on exit):
;   fast path:  room = end - cur; if cur != 0 and size != 0 and size <= room:
;               block = cur; cur = align16(cur + size)         - 6 instructions
;   reserve:    cur == 0: mmap the arena; success -> set cur/end, retry;
;               failure -> cur = end = 16 (room 0 forever) and fall through
;   fallback:   today's sequence, unchanged (mmap per call, -errno -> 0), so
;               nirmmita(0) still gives 0 (EINVAL) and the worst case is today.
; Memory from the arena is never reused, so it arrives zeroed like mmap memory.
;
; kosh growth (r65_emit_kosh_extend, before the copy path): if the kosh's data
; ends at the cursor, the cursor moves and the capacity field changes - no copy,
; no new block, and every alias of the buffer stays valid because nothing moved.
;
; ROUND-69 (Step 2, dvi-mukha): one range, two opposing cursors.
;   0kshetra_cur   the persistent cursor: grows UP from the start of the range
;   0kshetra_end   the scratch cursor: grows DOWN from the end of the range. It is
;                  also the persistent side's limit, so the persistent fast path
;                  is the same comparison as in Step 1: room = end - cur.
;   0kshetra_sima  the range's true end: the scratch side's own limit when it
;                  is ever full (end == sima means the scratch side is empty).
; Nothing moves 0kshetra_end yet - the mandapa block that would (Step 3) does
; not exist - so in v264 the scratch cursor is reserved, initialised and unused,
; and every program allocates exactly as in Step 1. Because the persistent side
; is bounded by the scratch cursor, a kosh growing on the persistent side can
; never extend into scratch memory: the R61 case 4b cannot be expressed.
; The reservation now sits before the fast path (the fast path jumps over it
; once the arena exists), so no jump in the sequence needs more than rel8.
;
; GUARD_PAGES (nasm -dGUARD_PAGES; tools/guard_page.py, never shipped): every
; nirmmita is its own mmap whose block ends flush against a PROT_NONE page, so
; one byte read or written past any block is SIGSEGV. No arena, no kosh extension.
; ============================================================

R65_ARENA equ 0x40000000            ; 1 GiB of address space; pages are committed on touch

section .data
    r65_name_cur db "0kshetra_cur", 0
    r65_name_end db "0kshetra_end", 0
    r65_name_sima db "0kshetra_sima", 0
    ; fast path, part 1 (before the first global load):  mov rsi,rax
    r65_t1 db 0x48,0x89,0xC6
    ; after mov [cur],rax:  mov rax,rdx ; jmp .done (rel32, patched to the end of the fallback)
    r65_t4 db 0x48,0x89,0xD0, 0xE9
    ; .reserve: push rsi ; xor edi,edi ; mov esi,ARENA ; mov edx,3 ; mov r10d,0x4022 ;
    ;           mov r8,-1 ; xor r9d,r9d ; mov eax,9
    r65_t5 db 0x56, 0x31,0xFF, 0xBE,0x00,0x00,0x00,0x40, 0xBA,0x03,0x00,0x00,0x00
    db 0x41,0xBA,0x22,0x40,0x00,0x00, 0x49,0xC7,0xC0,0xFF,0xFF,0xFF,0xFF, 0x45,0x31,0xC9
    db 0xB8,0x09,0x00,0x00,0x00
    ; .mmap:  mov rax,rsi   - then the old sequence
    r65_t9 db 0x48,0x89,0xF0
    ; kosh extension, after newcap is in r11 (r8 = user ptr, r9 = len, r10 = cap):
    ;   lea rax,[r8+r10*8] ; add rax,15 ; and rax,-16 ; mov rdx,rax
    r65_k1 db 0x4B,0x8D,0x04,0xD0, 0x48,0x83,0xC0,0x0F, 0x48,0x83,0xE0,0xF0, 0x48,0x89,0xC2
    ;   (mov rax,[cur])  cmp rax,rdx ; jne .no_ext(+46) ; new cursor = align16(user + newcap*8):
    ;   lea rdx,[r8+r11*8] ; add rdx,15 ; and rdx,-16
    r65_k2 db 0x48,0x39,0xD0, 0x75,0x2E, 0x4B,0x8D,0x14,0xD8, 0x48,0x83,0xC2,0x0F, 0x48,0x83,0xE2,0xF0
    ;   (mov rax,[end])  cmp rdx,rax ; ja .no_ext(+22) ; mov rax,rdx
    r65_k3 db 0x48,0x39,0xC2, 0x77,0x16, 0x48,0x89,0xD0
    ;   (mov [cur],rax)  mov [r8-8],r11 ; mov r10,r11 ; jmp .space (rel32, patched)
    r65_k4 db 0x4D,0x89,0x58,0xF8, 0x4D,0x89,0xDA, 0xE9
    ; ROUND-69 sequence (rax = size on entry):
    ;   mov rsi,rax ; mov rax,[cur] ; test rax,rax ; jnz .have (rel8, patched)
    r69_n2 db 0x48,0x85,0xC0, 0x75,0x00
    ; .reserve: r65_t5 (push rsi; mmap arguments; mov eax,9) ; syscall ; then
    ;   pop rsi ; mov edx,ARENA ; cmp rax,-4095 ; jb .ok(+7) ; mov eax,16 ; xor edx,edx
    r69_n3 db 0x5E, 0xBA,0x00,0x00,0x00,0x40, 0x48,0x3D,0x01,0xF0,0xFF,0xFF, 0x72,0x07
    db 0xB8,0x10,0x00,0x00,0x00, 0x31,0xD2
    ; .ok: mov [cur],rax ; mov rcx,rax ; add rax,rdx ; mov [end],rax ; mov [sima],rax ; mov rax,rcx
    r69_n4 db 0x48,0x89,0xC1, 0x48,0x01,0xD0
    r69_n5 db 0x48,0x89,0xC8
    ; .have: mov rdx,rax ; mov rax,[end] ; then r69_n7
    r69_n6 db 0x48,0x89,0xC2
    ; sub rax,rdx ; cmp rax,rsi ; jb .mmap ; test rsi,rsi ; jz .mmap ; lea rax,[rdx+rsi+15] ; and rax,-16
    r69_n7 db 0x48,0x29,0xD0, 0x48,0x39,0xF0, 0x72,0x00, 0x48,0x85,0xF6, 0x74,0x00
    db 0x48,0x8D,0x44,0x32,0x0F, 0x48,0x83,0xE0,0xF0
%ifdef GUARD_PAGES
    ; rax = size: mmap(size rounded up to pages + one page), mprotect the last page
    ; PROT_NONE, return guard - size; size 0 or a failed mmap -> 0.
    r69_guard_seq db 0x53,0x48,0x89,0xC3,0x48,0x85,0xC0,0x74,0x52,0x48,0x8D,0xB0,0xFF,0x1F,0x00,0x00
    db 0x48,0x81,0xE6,0x00,0xF0,0xFF,0xFF,0x31,0xFF,0xBA,0x03,0x00,0x00,0x00,0x41,0xBA
    db 0x22,0x00,0x00,0x00,0x49,0xC7,0xC0,0xFF,0xFF,0xFF,0xFF,0x45,0x31,0xC9,0xB8,0x09
    db 0x00,0x00,0x00,0x0F,0x05,0x48,0x3D,0x01,0xF0,0xFF,0xFF,0x73,0x1E,0x48,0x8D,0xBC
    db 0x30,0x00,0xF0,0xFF,0xFF,0xBE,0x00,0x10,0x00,0x00,0x31,0xD2,0xB8,0x0A,0x00,0x00
    db 0x00,0x57,0x0F,0x05,0x58,0x48,0x29,0xD8,0x5B,0xEB,0x03,0x31,0xC0,0x5B
r69_guard_len equ 94
%endif

section .bss
    r65_ready     resq 1              ; the two globals are registered
    r65_idx_cur   resq 1              ; 0-based global indices for r56_emit_global_*
    r65_idx_end   resq 1
    r65_idx_sima  resq 1
    r65_ext_patch resq 1              ; rel32 field of the extension's jmp .space, or -1

section .text

; r65_active -> rax = 1 when the arena path applies to this build: a Linux ELF target.
; --object / --separate builds take the same path, so that an object linked by sutram-link
; is byte-identical to the direct compile (R28/R29); the two globals are then ordinary
; module vitti of the object - defined by the root, extern in a module object.
r65_active:
    xor eax, eax
%ifndef GUARD_PAGES
    cmp qword [rel target_pe], 0
    jne .no
    mov eax, 1
.no:
%endif
    ret

%ifdef GUARD_PAGES
; r69_emit_guard: the guard-page allocation sequence (rax = size -> rax = block or 0).
r69_emit_guard:
    lea rsi, [rel r69_guard_seq]
    mov rcx, r69_guard_len
    call r23_emit_bytes
    ret
%endif

; r65_root_globals: at the start of code generation. In --separate, a root with modules
; defines the two globals whether or not its own code allocates, because a module object
; that allocates refers to them as extern "vitti:0kshetra_cur" / "vitti:0kshetra_end".
; A root without modules registers them lazily like a direct compile, so it stays
; byte-identical to it.
r65_root_globals:
    cmp qword [rel r29_separate_mode], 0
    je .no
    cmp qword [rel r28_no_mukhya], 0
    jne .no
    cmp qword [rel mg_rec_n], 1        ; record 0 is the program itself; a module is a second record
    jbe .no
    call r65_active
    test rax, rax
    jz .no
    call r65_ensure_globals
.no:
    ret

; r65_ensure_globals: register the two hidden module globals once, and keep their indices.
r65_ensure_globals:
    cmp qword [rel r65_ready], 0
    jne .done
    push rbx
    lea rdi, [rel r65_name_cur]
    call .register
    lea rdi, [rel r65_name_end]
    call .register
    lea rdi, [rel r65_name_sima]
    call .register
    lea rdi, [rel r65_name_cur]
    call r56_global_index
    dec rax
    mov [rel r65_idx_cur], rax
    lea rdi, [rel r65_name_end]
    call r56_global_index
    dec rax
    mov [rel r65_idx_end], rax
    lea rdi, [rel r65_name_sima]
    call r56_global_index
    dec rax
    mov [rel r65_idx_sima], rax
    mov qword [rel r65_ready], 1
    ; an object without mukhya (a module) does not own the arena: its two globals are extern
    cmp qword [rel r28_object_mode], 0
    je .owned
    cmp qword [rel r28_no_mukhya], 0
    je .owned
    lea rcx, [rel r30_gextern]
    mov rax, [rel r65_idx_cur]
    mov byte [rcx + rax], 1
    mov rax, [rel r65_idx_end]
    mov byte [rcx + rax], 1
    mov rax, [rel r65_idx_sima]
    mov byte [rcx + rax], 1
.owned:
    pop rbx
.done:
    ret
.register:                             ; rdi = name: a module vitti with no initializer
    mov rbx, rdi                       ; (storage is zero; a library object may hold it)
    call alloc_ast
    mov qword [rax], AST_DECL
    mov [rax + 8], rbx
    mov qword [rax + 16], 0
    call r56_register_global
    ret

%macro R65_BYTES 1
    lea rsi, [rel %1]
    mov rcx, %1_len
    call r23_emit_bytes
%endmacro
r65_t1_len equ 3
r65_t4_len equ 4
r65_t5_len equ 34
r65_t9_len equ 3
r65_k1_len equ 15
r65_k2_len equ 17
r65_k3_len equ 8
r65_k4_len equ 8
r69_n2_len equ 5
r69_n3_len equ 21
r69_n4_len equ 6
r69_n5_len equ 3
r69_n6_len equ 3
r69_n7_len equ 22

; r69_patch8: rdi = offset of a rel8 field in code_buf; the target is the current end of
; code. The distance must fit a signed byte; the sequence is laid out so that it does.
r69_patch8:
    mov rax, [rel code_sz]
    sub rax, rdi
    dec rax
    lea rdx, [rel code_buf]
    mov [rdx + rdi], al
    ret

; r65_emit_nirm: the arena sequence (R69 layout); ends by emitting the old sequence as
; the fallback. Generated-program rax = size on entry; rax = block (or 0) at .done.
;   mov rsi,rax ; mov rax,[cur] ; test rax,rax ; jnz .have
; .reserve (first call only):  mmap(0, ARENA, RW, PRIVATE|ANONYMOUS|NORESERVE)
;   success: cur = base, end = sima = base + ARENA   (end = the scratch cursor, at the top)
;   failure: cur = end = sima = 16                   (room 0 forever -> the old sequence)
;   rax = cur, fall into .have
; .have: rdx = cur ; room = end - cur ; size > room or size == 0 -> .mmap
;   cur = align16(cur + size) ; rax = old cur ; jmp .done
; .mmap: the old sequence, unchanged
r65_emit_nirm:
    call r65_ensure_globals
    R65_BYTES r65_t1                   ; mov rsi,rax
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_load          ; mov rax,[cur]
    R65_BYTES r69_n2                   ; test rax,rax ; jnz .have
    mov rax, [rel code_sz]
    dec rax
    push rax                           ; [rsp] = rel8 of jnz .have
    R65_BYTES r65_t5                   ; .reserve: push rsi ; the mmap arguments
    call emit_syscall
    R65_BYTES r69_n3                   ; pop rsi ; edx = ARENA ; failure -> eax = 16, edx = 0
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_store         ; .ok: mov [cur],rax
    R65_BYTES r69_n4                   ; mov rcx,rax ; add rax,rdx
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_store         ; mov [end],rax   - the scratch cursor starts at the top
    mov rdi, [rel r65_idx_sima]
    call r56_emit_global_store         ; mov [sima],rax  - the range's true end
    R65_BYTES r69_n5                   ; mov rax,rcx
    pop rdi
    call r69_patch8                    ; jnz .have lands here
    R65_BYTES r69_n6                   ; .have: mov rdx,rax
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_load          ; mov rax,[end]
    R65_BYTES r69_n7                   ; room check ; new cursor
    mov rax, [rel code_sz]
    push rax                           ; end of r69_n7: jb rel8 at -15, jz rel8 at -10
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_store         ; mov [cur],rax
    R65_BYTES r65_t4                   ; mov rax,rdx ; jmp .done (E9)
    mov rax, [rel code_sz]
    push rax                           ; the rel32 field of jmp .done
    xor edi, edi
    call emit_u32
    pop rcx                            ; rel32 offset
    pop rax                            ; end of r69_n7
    push rcx
    push rax
    lea rdi, [rax - 15]                ; jb .mmap rel8
    call r69_patch8
    mov rax, [rsp]
    lea rdi, [rax - 10]                ; jz .mmap rel8
    call r69_patch8
    pop rax
    R65_BYTES r65_t9                   ; .mmap: mov rax,rsi
    call r38_nirm_mmap                 ; the old sequence, unchanged; its end is .done
    pop rcx                            ; patch jmp .done
    mov rax, [rel code_sz]
    sub rax, rcx
    sub rax, 4
    lea rdx, [rel code_buf]
    mov [rdx + rcx], eax
    ret

; r65_emit_kosh_extend: emitted in kosh growth after newcap is in r11 (r8 user ptr,
; r9 len, r10 cap). On success the capacity field is updated, r10 = newcap, and the
; code jumps to the append path; the rel32 field is recorded in r65_ext_patch for
; the caller to patch together with the `jb .space`. Does nothing (and sets
; r65_ext_patch = -1) when the arena path does not apply.
r65_emit_kosh_extend:
    mov qword [rel r65_ext_patch], -1
    call r65_active
    test rax, rax
    jz .done
    call r65_ensure_globals
    R65_BYTES r65_k1
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_load          ; mov rax,[cur]
    R65_BYTES r65_k2
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_load          ; mov rax,[end]
    R65_BYTES r65_k3
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_store         ; mov [cur],rax
    R65_BYTES r65_k4                   ; ... ; E9
    mov rax, [rel code_sz]
    mov [rel r65_ext_patch], rax
    xor edi, edi
    call emit_u32                      ; rel32 to .space, patched by the caller
.done:
    ret

; ROUND-73: the scratch side of nirmmita (see r72_parse_mandapa in sutram_compiler.asm).
section .data
    ; mov rsi,rax ; test rsi,rsi ; jle .zero (rel32) - R74: a negative size is 0, as on the
    ; ordinary path (R146 F4: with jz, -1 rounded to 0 bytes and the zeroing wrote one qword
    ; into the block above)
    r73_s1 db 0x48,0x89,0xC6, 0x48,0x85,0xF6, 0x0F,0x8E
    ; (mov rax,[end]) lea rdx,[rsi+15] ; and rdx,-16 ; sub rax,rdx ; jb .full (rel32)
    r73_s2 db 0x48,0x8D,0x56,0x0F, 0x48,0x83,0xE2,0xF0, 0x48,0x29,0xD0, 0x0F,0x82
    ; mov rdx,rax
    r73_s3 db 0x48,0x89,0xC2
    ; (mov rax,[cur]) cmp rdx,rax ; jb .full (rel32)
    r73_s4 db 0x48,0x39,0xC2, 0x0F,0x82
    ; mov rax,rdx
    r73_s5 db 0x48,0x89,0xD0
    ; (mov [end],rax) zero it, a qword at a time (rep stosb measured ~110 ns per 64-byte
    ; block on the test machine; this loop ~4 ns):
    ; lea rcx,[rsi+7] ; shr rcx,3 ; xor edx,edx ; .z: mov qword [rax+rdx*8],0 ; inc rdx ;
    ; cmp rdx,rcx ; jb .z ; jmp .done (rel32)
    r73_s6 db 0x48,0x8D,0x4E,0x07, 0x48,0xC1,0xE9,0x03, 0x31,0xD2
    db 0x48,0xC7,0x04,0xD0,0x00,0x00,0x00,0x00, 0x48,0xFF,0xC2, 0x48,0x39,0xCA, 0x72,0xF0, 0xE9
    ; .zero: xor eax,eax ; jmp .done (rel32)
    r73_s7 db 0x31,0xC0, 0xE9
section .text
r73_s1_len equ 8
r73_s2_len equ 13
r73_s3_len equ 3
r73_s4_len equ 5
r73_s5_len equ 3
r73_s6_len equ 27
r73_s7_len equ 3

; ---- code generation ----
; r73_gen_scrcur: the scratch cursor's value at block entry, reserving the arena first if
; this is the program's first use of it. Not a Linux ELF build: 0 (the block is inert).
r73_gen_scrcur:
    call r65_active
    test rax, rax
    jnz .live
    mov dil, 0x31                  ; xor eax, eax
    call emit_byte
    mov dil, 0xC0
    call emit_byte
    ret
.live:
    call r65_ensure_globals
    call r73_emit_reserve
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_load      ; mov rax,[end]
    ret

; r73_emit_reserve: if the arena has not been reserved, reserve it (Step 2's sequence).
r73_emit_reserve:
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_load      ; mov rax,[cur]
    R65_BYTES r69_n2               ; test rax,rax ; jnz .have
    mov rax, [rel code_sz]
    dec rax
    push rax
    R65_BYTES r65_t5
    call emit_syscall
    R65_BYTES r69_n3
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_store
    R65_BYTES r69_n4
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_store
    mov rdi, [rel r65_idx_sima]
    call r56_emit_global_store
    pop rdi
    call r69_patch8                ; .have
    ret

; r73_gen_rewind(rbx = AST_REWIND): end = the mark. Not Linux ELF: nothing.
r73_gen_rewind:
    call r65_active
    test rax, rax
    jz .r
    call r65_ensure_globals
    mov rax, [rbx+8]
    call gen_expr                  ; rax = the mark
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_store
.r:
    ret

; r73_gen_scratch_nirm: rax (generated) = size -> rax = a zeroed block on the scratch side.
;   mov rsi,rax ; test rsi,rsi ; jle .zero ; mov rax,[end] ; lea rdx,[rsi+15] ; and rdx,-16
;   sub rax,rdx ; jb .full ; mov rdx,rax ; mov rax,[cur] ; cmp rdx,rax ; jb .full
;   mov rax,rdx ; mov [end],rax ; mov rdi,rax ; mov rcx,rsi ; mov rdx,rax ; xor eax,eax
;   rep stosb ; mov rax,rdx ; jmp .done
;   .zero: xor eax,eax ; jmp .done
;   .full: likha(kshetra purnam) ; exit(1)
r73_gen_scratch_nirm:
    call r65_ensure_globals
    R65_BYTES r73_s1               ; mov rsi,rax ; test rsi,rsi ; jle .zero
    call .rel32                    ; A
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_load      ; mov rax,[end]
    R65_BYTES r73_s2               ; rdx = align16(size) ; end - rdx ; jb .full
    call .rel32                    ; B
    R65_BYTES r73_s3               ; mov rdx,rax
    mov rdi, [rel r65_idx_cur]
    call r56_emit_global_load      ; mov rax,[cur]
    R65_BYTES r73_s4               ; cmp rdx,rax ; jb .full (would meet the persistent side)
    call .rel32                    ; C
    R65_BYTES r73_s5               ; mov rax,rdx
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_store     ; mov [end],rax
    R65_BYTES r73_s6               ; zero it (memory is reused) ; jmp .done
    call .rel32                    ; D
    mov rdi, [rsp + 24]            ; .zero: A
    call r73_patch32
    R65_BYTES r73_s7               ; xor eax,eax ; jmp .done
    call .rel32                    ; E
    mov rdi, [rsp + 24]            ; .full: B
    call r73_patch32
    mov rdi, [rsp + 16]            ; .full: C
    call r73_patch32
    push rbx
    call alloc_ast
    mov qword [rax], AST_STR
    lea rcx, [rel r73_msg_full]
    call r11_tr_rcx
    mov [rax+8], rcx
    push rax
    call alloc_ast
    pop rcx
    mov qword [rax], AST_CALL
    mov qword [rax+8], BN_LIKHA
    mov qword [rax+16], 1
    mov [rax+24], rcx
    call gen_expr
    pop rbx
    mov dil, 0xB8                  ; mov eax,60 ; mov edi,1 ; syscall
    call emit_byte
    mov edi, 60
    call emit_u32
    mov dil, 0xBF
    call emit_byte
    mov edi, 1
    call emit_u32
    call emit_syscall
    pop rdi                        ; .done: E
    call r73_patch32
    pop rdi                        ; .done: D
    call r73_patch32
    add rsp, 24                    ; C, B, A
    ret
.rel32:                            ; push the offset of a rel32 field and emit it (0)
    pop rcx                        ; return address
    mov rax, [rel code_sz]
    push rax
    push rcx
    xor edi, edi
    jmp emit_u32                   ; returns to our caller with the offset on its stack

; r73_patch32(rdi = offset of a rel32 field): its target is the current end of code.
r73_patch32:
    mov rax, [rel code_sz]
    sub rax, rdi
    sub rax, 4
    lea rdx, [rel code_buf]
    mov [rdx + rdi], eax
    ret

; r73_gen_ret_rewind(rbx = AST_RETURN): a nivartanam inside a block rewinds to the
; outermost block's mark of its prakriya, after the value is in rax.
r73_gen_ret_rewind:
    cmp qword [rbx+48], 0
    je .r
    call r65_active
    test rax, rax
    jz .r
    mov dil, 0x50                  ; push rax (the value)
    call emit_byte
    push rbx
    mov rax, [rbx+48]
    call gen_expr                  ; rax = the mark
    mov rdi, [rel r65_idx_end]
    call r56_emit_global_store
    pop rbx
    mov dil, 0x58                  ; pop rax
    call emit_byte
.r:
    ret
