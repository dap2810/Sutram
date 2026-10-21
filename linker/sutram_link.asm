; ===================================================================
; sutram-link - the Sutram linker. ROUND-28. Ours, in NASM, Linux x86-64.
;
;   sutram-link out.bin a.smo [b.smo ...]
;
; Reads Sutram object files (written by `sutram_compiler --object`, the format
; in docs/OBJECT-FORMAT.md), lays their code end to end - the one that defines
; mukhya first, so mukhya is the entry point - fills every relocation with the
; prakriya some object defines, and writes the same kind of executable the
; compiler writes for an ordinary program: one PT_LOAD at 0x400000 + 120.
;
; An ordinary program never comes here: the compiler still writes its
; executable itself, in one pass. This program exists only for programs built
; from separately compiled modules.
;
; Exit 0 on success; 1 with a diagnostic on a bad object, an undefined or
; duplicate prakriya, or no mukhya; 2 on a usage error.
; ===================================================================

BASE_ADDR    equ 0x400000
HEADERS_SIZE equ 120
IN_CAP       equ 16*1024*1024
OUT_CAP      equ 16*1024*1024
OBJ_CAP      equ 64
OBJ_SIZE     equ 64                ; path, code, size, syms, nsyms, relocs, nrelocs, base
SYM_CAP      equ 16384
MAGIC        equ 0x314F4D4152545553   ; "SUTRAMO1"

section .data
    m_usage   db "Prayog: sutram-link nirgat.bin a.smo [b.smo ...]", 10, 0
    m_open    db "Sutram Error: patram na udghatitam: ", 0
    m_bad     db "Sutram Error: vastu-patram na (SUTRAMO1 apekshitam): ", 0
    m_undef   db "Sutram Error: agyat prakriya: ", 0
    m_dup     db "Sutram Error: prakriya dvih paribhashita: ", 0
    m_nomain  db "Sutram Error: kasminnapi vastu-patre mukhya nasti", 10, 0
    m_full    db "Sutram Error: sutram-link seema atikram", 10, 0
    m_ok      db "Siddh: ", 0
    m_bytes   db " baait sankalit", 10, 0
    m_nl      db 10, 0
    s_mukhya  db "mukhya"

section .bss
    argc      resq 1
    argv      resq 1
    in_buf    resb IN_CAP
    in_used   resq 1
    out_code  resb OUT_CAP
    out_size  resq 1
    objs      resb OBJ_CAP*OBJ_SIZE
    nobjs     resq 1
    order     resq OBJ_CAP
    syms      resq SYM_CAP*3        ; name, length, absolute offset
    nsyms     resq 1
    main_obj  resq 1
    hdr       resb 128
    numbuf    resb 32
    fd        resq 1

section .text
global _start

; ---------------------------------------------------------------- helpers
strlen:                     ; rdi -> rax
    xor eax, eax
.l: cmp byte [rdi + rax], 0
    je .d
    inc rax
    jmp .l
.d: ret

puts:                       ; rdi = NUL-terminated, to stdout
    push rdi
    call strlen
    pop rsi
    mov rdx, rax
    mov edi, 1
    mov eax, 1
    syscall
    ret

putn:                       ; rsi = bytes, rdx = length, to stdout
    mov edi, 1
    mov eax, 1
    syscall
    ret

fail:                       ; rdi = message, rsi = name or 0, rdx = name length (0: NUL-terminated)
    push rsi
    push rdx
    call puts
    pop rdx
    pop rsi
    test rsi, rsi
    jz .x
    test rdx, rdx
    jnz .len
    mov rdi, rsi
    call puts
    jmp .nl
.len:
    call putn
.nl:
    lea rdi, [rel m_nl]
    call puts
.x: mov edi, 1
    mov eax, 60
    syscall

; names_equal(rdi, rsi = names, rdx, rcx = lengths) -> rax = 1 if equal
names_equal:
    xor eax, eax
    cmp rdx, rcx
    jne .d
    xor ecx, ecx
.l: cmp rcx, rdx
    jae .y
    mov r8b, [rdi + rcx]
    cmp r8b, [rsi + rcx]
    jne .d
    inc rcx
    jmp .l
.y: mov eax, 1
.d: ret

; ---------------------------------------------------------------- read
; read_object(rbx = object record, path in [rbx]): the file into in_buf, checked
read_object:
    push r12
    push r13
    push r14
    mov rdi, [rbx]
    xor esi, esi                    ; O_RDONLY
    xor edx, edx
    mov eax, 2
    syscall
    test rax, rax
    js .open_fail
    mov [rel fd], rax
    lea r12, [rel in_buf]
    add r12, [rel in_used]          ; where this file goes
    xor r13d, r13d                  ; its length
.rd:
    mov rax, IN_CAP
    sub rax, [rel in_used]
    sub rax, r13
    jle .too_big
    mov rdx, rax
    mov rdi, [rel fd]
    lea rsi, [r12 + r13]
    xor eax, eax
    syscall
    test rax, rax
    js .open_fail
    jz .eof
    add r13, rax
    jmp .rd
.eof:
    mov rdi, [rel fd]
    mov eax, 3
    syscall
    add [rel in_used], r13
    ; header: magic, code size, symbol count, relocation count
    cmp r13, 32
    jb .bad
    mov rax, MAGIC
    cmp [r12], rax
    jne .bad
    mov rax, [r12 + 8]              ; code size
    lea rcx, [rax + 32]
    cmp rcx, r13
    ja .bad
    lea rcx, [r12 + 32]
    mov [rbx + 8], rcx              ; code
    mov [rbx + 16], rax             ; size
    lea r14, [r12 + 32]
    add r14, rax                    ; the symbol table
    lea r13, [r12 + r13]            ; the end of the file
    mov [rbx + 24], r14
    mov rcx, [r12 + 16]
    mov [rbx + 32], rcx
    call skip_entries               ; r14 past the symbols
    mov [rbx + 40], r14
    mov rcx, [r12 + 24]
    mov [rbx + 48], rcx
    call skip_entries               ; r14 past the relocations
    cmp r14, r13
    jne .bad
    pop r14
    pop r13
    pop r12
    ret
.open_fail:
    lea rdi, [rel m_open]
    mov rsi, [rbx]
    xor edx, edx
    jmp fail
.too_big:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
.bad:
    lea rdi, [rel m_bad]
    mov rsi, [rbx]
    xor edx, edx
    jmp fail

; skip_entries(r14 = first entry, rcx = count, r13 = end of file) -> r14 past them.
; An entry is { u64 offset, u64 name length, name }.
skip_entries:
.l: test rcx, rcx
    jz .d
    lea rax, [r14 + 16]
    cmp rax, r13
    ja read_object.bad
    mov rax, [r14 + 8]
    cmp rax, 4096
    ja read_object.bad
    lea r14, [r14 + 16 + rax]
    cmp r14, r13
    ja read_object.bad
    dec rcx
    jmp .l
.d: ret

; ---------------------------------------------------------------- link
; defines_mukhya(rbx = object) -> rax = 1
defines_mukhya:
    push r12
    push r13
    mov r12, [rbx + 24]
    mov r13, [rbx + 32]
.l: test r13, r13
    jz .no
    lea rdi, [r12 + 16]
    lea rsi, [rel s_mukhya]
    mov rdx, [r12 + 8]
    mov ecx, 6
    call names_equal
    test rax, rax
    jnz .yes
    mov rax, [r12 + 8]
    lea r12, [r12 + 16 + rax]
    dec r13
    jmp .l
.yes:
    mov eax, 1
    jmp .out
.no:
    xor eax, eax
.out:
    pop r13
    pop r12
    ret

; find_symbol(rdi = name, rdx = length) -> rax = absolute offset, or -1
find_symbol:
    push r12
    push r13
    push r14
    push r15
    mov r14, rdi
    mov r15, rdx
    xor r12d, r12d
.l: cmp r12, [rel nsyms]
    jae .no
    imul r13, r12, 24
    lea rax, [rel syms]
    add r13, rax
    mov rdi, r14
    mov rsi, [r13]
    mov rdx, r15
    mov rcx, [r13 + 8]
    call names_equal
    test rax, rax
    jnz .yes
    inc r12
    jmp .l
.yes:
    mov rax, [r13 + 16]
    jmp .out
.no:
    mov rax, -1
.out:
    pop r15
    pop r14
    pop r13
    pop r12
    ret

_start:
    mov rax, [rsp]
    mov [rel argc], rax
    lea rax, [rsp + 8]
    mov [rel argv], rax
    cmp qword [rel argc], 3
    jae .args
    lea rdi, [rel m_usage]
    call puts
    mov edi, 2
    mov eax, 60
    syscall
.args:
    ; read every object
    mov r12, 2
.read:
    cmp r12, [rel argc]
    jae .read_done
    mov rax, [rel nobjs]
    cmp rax, OBJ_CAP
    jae .full
    imul rbx, rax, OBJ_SIZE
    lea rcx, [rel objs]
    add rbx, rcx
    mov rcx, [rel argv]
    mov rcx, [rcx + r12*8]
    mov [rbx], rcx
    call read_object
    inc qword [rel nobjs]
    inc r12
    jmp .read
.read_done:
    ; exactly one object defines mukhya; it goes first
    mov qword [rel main_obj], -1
    xor r12d, r12d
.main:
    cmp r12, [rel nobjs]
    jae .main_done
    imul rbx, r12, OBJ_SIZE
    lea rcx, [rel objs]
    add rbx, rcx
    call defines_mukhya
    test rax, rax
    jz .main_next
    cmp qword [rel main_obj], -1
    jne .two_mains
    mov [rel main_obj], r12
.main_next:
    inc r12
    jmp .main
.two_mains:
    lea rdi, [rel m_dup]
    lea rsi, [rel s_mukhya]
    mov edx, 6
    jmp fail
.main_done:
    cmp qword [rel main_obj], -1
    jne .ordered
    lea rdi, [rel m_nomain]
    xor esi, esi
    jmp fail
.ordered:
    ; order: the mukhya object, then the others as given
    lea rdi, [rel order]
    mov rax, [rel main_obj]
    mov [rdi], rax
    mov ecx, 1
    xor r12d, r12d
.ord:
    cmp r12, [rel nobjs]
    jae .lay
    cmp r12, [rel main_obj]
    je .ord_next
    mov [rdi + rcx*8], r12
    inc rcx
.ord_next:
    inc r12
    jmp .ord
.lay:
    ; lay the code out and collect the symbols
    xor r12d, r12d
.lay_l:
    cmp r12, [rel nobjs]
    jae .relocate
    lea rax, [rel order]
    mov rax, [rax + r12*8]
    imul rbx, rax, OBJ_SIZE
    lea rcx, [rel objs]
    add rbx, rcx
    mov rax, [rel out_size]
    mov [rbx + 56], rax             ; base
    mov rdx, [rbx + 16]
    add rax, rdx
    cmp rax, OUT_CAP
    ja .full
    lea rdi, [rel out_code]
    add rdi, [rbx + 56]
    mov rsi, [rbx + 8]
    mov rcx, rdx
    rep movsb
    mov [rel out_size], rax
    ; symbols
    mov r13, [rbx + 24]
    mov r14, [rbx + 32]
.sym:
    test r14, r14
    jz .lay_next
    lea rdi, [r13 + 16]
    mov rdx, [r13 + 8]
    call find_symbol
    cmp rax, -1
    jne .dup
    mov rax, [rel nsyms]
    cmp rax, SYM_CAP
    jae .full
    imul rax, rax, 24
    lea rcx, [rel syms]
    add rcx, rax
    lea rax, [r13 + 16]
    mov [rcx], rax
    mov rax, [r13 + 8]
    mov [rcx + 8], rax
    mov rax, [r13]
    add rax, [rbx + 56]
    mov [rcx + 16], rax
    inc qword [rel nsyms]
    mov rax, [r13 + 8]
    lea r13, [r13 + 16 + rax]
    dec r14
    jmp .sym
.dup:
    lea rdi, [rel m_dup]
    lea rsi, [r13 + 16]
    mov rdx, [r13 + 8]
    jmp fail
.lay_next:
    inc r12
    jmp .lay_l
.relocate:
    ; fill every hole: rel32 = target - (site + 4)
    xor r12d, r12d
.rel_obj:
    cmp r12, [rel nobjs]
    jae .write
    imul rbx, r12, OBJ_SIZE
    lea rcx, [rel objs]
    add rbx, rcx
    mov r13, [rbx + 40]
    mov r14, [rbx + 48]
.rel:
    test r14, r14
    jz .rel_next
    lea rdi, [r13 + 16]
    mov rdx, [r13 + 8]
    call find_symbol
    cmp rax, -1
    je .undef
    mov rcx, [r13]                  ; the site, in its object
    lea rdx, [rcx + 4]
    cmp rdx, [rbx + 16]
    ja .bad_site
    add rcx, [rbx + 56]             ; ... in the output
    lea rdx, [rcx + 4]
    sub rax, rdx
    lea rdx, [rel out_code]
    mov [rdx + rcx], eax
    mov rax, [r13 + 8]
    lea r13, [r13 + 16 + rax]
    dec r14
    jmp .rel
.rel_next:
    inc r12
    jmp .rel_obj
.undef:
    lea rdi, [rel m_undef]
    lea rsi, [r13 + 16]
    mov rdx, [r13 + 8]
    jmp fail
.bad_site:
    lea rdi, [rel m_bad]
    mov rsi, [rbx]
    xor edx, edx
    jmp fail
.full:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
.write:
    ; the executable: the same headers the compiler writes for an ordinary program
    lea rdi, [rel hdr]
    mov dword [rdi], 0x464C457F
    mov dword [rdi + 4], 0x00010102
    mov qword [rdi + 8], 0
    mov word [rdi + 16], 2          ; ET_EXEC
    mov word [rdi + 18], 0x3E       ; x86-64
    mov dword [rdi + 20], 1
    mov rax, BASE_ADDR + HEADERS_SIZE
    mov [rdi + 24], rax             ; entry: mukhya, at the start of the code
    mov qword [rdi + 32], 64        ; program headers
    mov qword [rdi + 40], 0
    mov dword [rdi + 48], 0
    mov word [rdi + 52], 64
    mov word [rdi + 54], 56
    mov word [rdi + 56], 1
    mov word [rdi + 58], 0
    mov word [rdi + 60], 0
    mov word [rdi + 62], 0
    mov dword [rdi + 64], 1         ; PT_LOAD
    mov dword [rdi + 68], 7         ; RWX, as the compiler's
    mov qword [rdi + 72], HEADERS_SIZE
    mov rax, BASE_ADDR + HEADERS_SIZE
    mov [rdi + 80], rax
    mov [rdi + 88], rax
    mov rax, [rel out_size]
    mov [rdi + 96], rax             ; filesz
    add rax, 0x10000
    mov [rdi + 104], rax            ; memsz: + 64 KiB, as the compiler's
    mov qword [rdi + 112], 0x1000
    mov rcx, [rel argv]
    mov rdi, [rcx + 8]              ; argv[1] = output
    mov esi, 0x241                  ; O_WRONLY|O_CREAT|O_TRUNC
    mov edx, 0o755
    mov eax, 2
    syscall
    test rax, rax
    js .out_fail
    mov [rel fd], rax
    mov rdi, rax
    lea rsi, [rel hdr]
    mov edx, HEADERS_SIZE
    mov eax, 1
    syscall
    mov rdi, [rel fd]
    lea rsi, [rel out_code]
    mov rdx, [rel out_size]
    mov eax, 1
    syscall
    mov rdi, [rel fd]
    mov eax, 3
    syscall
    mov rcx, [rel argv]
    mov rdi, [rcx + 8]
    mov esi, 0o755
    mov eax, 90                     ; chmod
    syscall
    ; Siddh: N baait sankalit
    lea rdi, [rel m_ok]
    call puts
    mov rax, [rel out_size]
    lea rsi, [rel numbuf + 31]
    mov byte [rsi], 0
    mov ecx, 10
.num:
    xor edx, edx
    div rcx
    add dl, '0'
    dec rsi
    mov [rsi], dl
    test rax, rax
    jnz .num
    mov rdi, rsi
    call puts
    lea rdi, [rel m_bytes]
    call puts
    xor edi, edi
    mov eax, 60
    syscall
.out_fail:
    lea rdi, [rel m_open]
    mov rcx, [rel argv]
    mov rsi, [rcx + 8]
    xor edx, edx
    jmp fail
