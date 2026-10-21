; ===================================================================
; sutram-elf2smo - a foreign object, read into a Sutram object. ROUND-32.
; Ours, in NASM, Linux x86-64, raw system calls.
;
;   sutram-elf2smo in.o out.smo
;
; Reads one ELF64 relocatable object (ET_REL, x86-64) - a C function compiled
; freestanding, say - and writes a SUTRAMO1 object (docs/OBJECT-FORMAT.md) that
; sutram-link links like any other: its code, and one symbol per function.
;
; Stage 2 (ROUND-33): what real C needs for numbers and strings, and no more.
;   * exactly one non-empty code section: PROGBITS, ALLOC|EXECINSTR, not WRITE;
;   * read-only data sections (PROGBITS, ALLOC, not WRITE, not EXEC; MERGE and
;     STRINGS allowed) - a double constant, a string literal - are placed after
;     the code, each at its alignment (at most 8: the linker lays objects end
;     to end, so a 16-byte constant could not be kept aligned, and is refused);
;   * relocations in the code only (SHT_RELA whose sh_info is the code section),
;     of the two PC-relative kinds R_X86_64_PC32 and R_X86_64_PLT32, against a
;     symbol in the code or in a placed data section: each is resolved here, as
;     S + A - P, checked to fit in 32 bits. Nothing is left for the linker;
;   * no undefined symbol: a foreign function that calls out is still refused
;     (a C function must never call a Sutram prakriya, which does not keep the
;     registers C expects kept);
;   * no writable data, no bss, no unwind tables, no TLS, no absolute or GOT
;     relocation, no SHT_REL - each refused - and SHT_NOTE skipped;
;   * every GLOBAL symbol is a default-visibility FUNC in the code section,
;     inside it, named [A-Za-z_][A-Za-z0-9_]* (at most 127 bytes), once;
;     LOCAL symbols are ignored; WEAK and anything else are refused.
; No program headers, no dynamic section, no libraries: none of that is read,
; and an object that needs it is refused. Every offset and length is checked
; against the file before it is used.
;
; Exit 0 on success; 1 with a diagnostic; 2 on a usage error.
; ===================================================================

IN_CAP  equ 4*1024*1024
SYM_CAP equ 256
SEC_CAP equ 1024
RELA_CAP equ 16
MAGIC   equ 0x314F4D4152545553   ; "SUTRAMO1"

section .data
    m_usage  db "Prayog: sutram-elf2smo videshi.o nirgat.smo", 10, 0
    m_open   db "Sutram Error: patram na udghatitam: ", 0
    m_notelf db "Sutram Error: ELF64 x86-64 ET_REL vastu-patram na", 10, 0
    m_bounds db "Sutram Error: ELF-patram khanditam (seema-bahir)", 10, 0
    m_code   db "Sutram Error: ELF-patre ekam eva sanket-khandam apekshitam", 10, 0
    m_reloc  db "Sutram Error: ELF-patre punahsthapanam asamarthitam", 10, 0
    m_align  db "Sutram Error: ELF-patre 8-baait-adhika samarekhanam asamarthitam", 10, 0
    m_range  db "Sutram Error: ELF-patre punahsthapanam 32-bit-bahih", 10, 0
    m_alloc  db "Sutram Error: ELF-patre sanketat anyat bhara-khandam asamarthitam", 10, 0
    m_symtab db "Sutram Error: ELF-patre ekam eva suchi-khandam apekshitam", 10, 0
    m_undef  db "Sutram Error: ELF-patre agyat sanket: ", 0
    m_global db "Sutram Error: ELF-patre sarvatrik sanket prakriya na: ", 0
    m_name   db "Sutram Error: ELF-patre sanket-nama dushtam", 10, 0
    m_dup    db "Sutram Error: ELF-patre prakriya dvih: ", 0
    m_none   db "Sutram Error: ELF-patre sarvatrik prakriya nasti", 10, 0
    m_full   db "Sutram Error: sutram-elf2smo seema atikram", 10, 0
    m_ok     db "Siddh: ", 0
    m_tail   db " prakriya, ", 0
    m_bytes  db " baait", 10, 0
    m_nl     db 10, 0

section .bss
    buf      resb IN_CAP
    fsize    resq 1
    shoff    resq 1
    shnum    resq 1
    code_off resq 1
    code_sz  resq 1
    code_idx resq 1
    sym_off  resq 1
    sym_sz   resq 1
    str_off  resq 1
    str_sz   resq 1
    syms     resq SYM_CAP*3           ; offset, name pointer, name length
    nsyms    resq 1
    hdr      resq 1
    obuf     resb IN_CAP              ; the code, then the read-only data
    out_sz   resq 1
    base     resq SEC_CAP             ; each section's offset in obuf, or -1
    rodata   resq SEC_CAP             ; the read-only data sections, in order
    nrodata  resq 1
    relas    resq RELA_CAP
    nrelas   resq 1
    sym_idx  resq 1
    numbuf   resb 32
    fd       resq 1
    outpath  resq 1

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
    mov edi, 1
    mov eax, 1
    syscall
.nl:
    lea rdi, [rel m_nl]
    call puts
.x: mov edi, 1
    mov eax, 60
    syscall

putu:                       ; rax = number, to stdout in decimal
    lea rsi, [rel numbuf + 31]
    mov byte [rsi], 0
    mov ecx, 10
.l: xor edx, edx
    div rcx
    add dl, '0'
    dec rsi
    mov [rsi], dl
    test rax, rax
    jnz .l
    mov rdi, rsi
    jmp puts

; in_range(rax = offset, rdx = length): returns only if [offset, offset+length)
; lies inside the file; otherwise fails. Subtraction only, so nothing overflows.
in_range:
    mov rcx, [rel fsize]
    cmp rax, rcx
    ja .bad
    sub rcx, rax
    cmp rdx, rcx
    ja .bad
    ret
.bad:
    lea rdi, [rel m_bounds]
    xor esi, esi
    jmp fail

; write_all(rsi = bytes, rdx = length) to [fd]
write_all:
    test rdx, rdx
    jz .d
    mov rdi, [rel fd]
    mov eax, 1
    syscall
    test rax, rax
    js .bad
    add rsi, rax
    sub rdx, rax
    jmp write_all
.bad:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
.d: ret

put_u64:                    ; rax
    mov [rel hdr], rax
    lea rsi, [rel hdr]
    mov edx, 8
    jmp write_all

; ---------------------------------------------------------------- main
_start:
    mov rax, [rsp]
    cmp rax, 3
    jne .usage
    mov rax, [rsp + 24]
    mov [rel outpath], rax
    ; read the input
    mov rdi, [rsp + 16]
    xor esi, esi
    mov eax, 2
    syscall
    test rax, rax
    js .open_fail
    mov [rel fd], rax
    xor ebx, ebx
.read:
    mov rdi, [rel fd]
    lea rsi, [rel buf]
    add rsi, rbx
    mov edx, IN_CAP
    sub rdx, rbx
    jz .too_big
    xor eax, eax
    syscall
    test rax, rax
    js .open_fail
    jz .read_done
    add rbx, rax
    jmp .read
.too_big:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
.read_done:
    mov [rel fsize], rbx
    mov rdi, [rel fd]
    mov eax, 3
    syscall

    ; ---- the ELF header
    lea rbx, [rel buf]
    cmp qword [rel fsize], 64
    jb .not_elf
    cmp dword [rbx], 0x464C457F           ; 7F 'E' 'L' 'F'
    jne .not_elf
    cmp byte [rbx + 4], 2                 ; ELFCLASS64
    jne .not_elf
    cmp byte [rbx + 5], 1                 ; little endian
    jne .not_elf
    cmp byte [rbx + 6], 1                 ; EV_CURRENT
    jne .not_elf
    cmp word [rbx + 16], 1                ; ET_REL
    jne .not_elf
    cmp word [rbx + 18], 62               ; EM_X86_64
    jne .not_elf
    cmp word [rbx + 56], 0                ; no program headers in an ET_REL
    jne .not_elf
    cmp word [rbx + 58], 64               ; e_shentsize
    jne .not_elf
    movzx eax, word [rbx + 60]            ; e_shnum (0 would mean an extended count)
    test eax, eax
    jz .not_elf
    cmp rax, SEC_CAP
    ja .not_elf
    mov [rel shnum], rax
    mov rax, [rbx + 40]                   ; e_shoff
    mov [rel shoff], rax
    mov rdx, [rel shnum]
    shl rdx, 6
    call in_range

    ; ---- the sections
    mov qword [rel code_idx], 0
    mov qword [rel sym_sz], -1
    xor r12d, r12d
.sec:
    cmp r12, [rel shnum]
    jae .sec_done
    mov r13, r12
    shl r13, 6
    add r13, [rel shoff]
    lea rbx, [rel buf]
    add r13, rbx                          ; r13 -> this section header
    mov r14d, [r13 + 4]                   ; sh_type
    mov r15, [r13 + 32]                   ; sh_size
    test r15, r15
    jz .sec_next                          ; an empty section is nothing
    cmp r14d, 8                           ; SHT_NOBITS has no bytes in the file
    je .sec_bounded
    mov rax, [r13 + 24]
    mov rdx, r15
    call in_range
.sec_bounded:
    cmp r14d, 4                           ; SHT_RELA: checked after the sections
    je .rela_sec
    cmp r14d, 9                           ; SHT_REL
    je .has_reloc
    cmp r14d, 2                           ; SHT_SYMTAB
    je .symtab
    mov rax, [r13 + 8]                    ; sh_flags
    test rax, 2                           ; SHF_ALLOC
    jz .sec_next                          ; not loaded: metadata, skipped
    cmp r14d, 7                           ; SHT_NOTE: nothing reads it
    je .sec_next
    cmp r14d, 1                           ; SHT_PROGBITS
    jne .other_alloc
    test rax, 4                           ; SHF_EXECINSTR
    jz .rodata_sec
    test rax, 1                           ; SHF_WRITE
    jnz .other_alloc
    test rax, ~7                          ; no other flag (TLS, GROUP, ...)
    jnz .other_alloc
    cmp qword [rel code_idx], 0
    jne .two_code
    mov [rel code_idx], r12
    mov rax, [r13 + 24]
    mov [rel code_off], rax
    mov [rel code_sz], r15
    jmp .sec_next
.rodata_sec:                              ; read-only data: ALLOC, MERGE, STRINGS only
    test rax, ~0x32
    jnz .other_alloc
    cmp qword [r13 + 48], 8               ; sh_addralign
    ja .bad_align
    mov rcx, [rel nrodata]
    lea rdx, [rel rodata]
    mov [rdx + rcx*8], r12
    inc qword [rel nrodata]
    jmp .sec_next
.rela_sec:
    cmp qword [r13 + 56], 24              ; sh_entsize, whole entries
    jne .not_elf
    mov rax, r15
    xor edx, edx
    mov ecx, 24
    div rcx
    test rdx, rdx
    jnz .not_elf
    mov rcx, [rel nrelas]
    cmp rcx, RELA_CAP
    jae .full
    lea rdx, [rel relas]
    mov [rdx + rcx*8], r12
    inc qword [rel nrelas]
    jmp .sec_next
.symtab:
    cmp qword [rel sym_sz], -1
    jne .two_symtab
    mov [rel sym_idx], r12
    cmp qword [r13 + 56], 24              ; sh_entsize
    jne .not_elf
    mov rax, r15                          ; whole entries only
    xor edx, edx
    mov ecx, 24
    div rcx
    test rdx, rdx
    jnz .not_elf
    mov rax, [r13 + 24]
    mov [rel sym_off], rax
    mov [rel sym_sz], r15
    mov eax, [r13 + 40]                   ; sh_link: its string table
    cmp rax, [rel shnum]
    jae .not_elf
    shl rax, 6
    add rax, [rel shoff]
    lea rbx, [rel buf]
    add rax, rbx
    cmp dword [rax + 4], 3                ; SHT_STRTAB
    jne .not_elf
    mov rcx, [rax + 24]
    mov [rel str_off], rcx
    mov rdx, [rax + 32]
    mov [rel str_sz], rdx
    mov rax, rcx
    call in_range
.sec_next:
    inc r12
    jmp .sec
.sec_done:
    cmp qword [rel code_idx], 0
    je .no_code
    cmp qword [rel sym_sz], -1
    je .no_symtab

    ; ---- the layout: the code at 0, then each read-only data section
    xor ecx, ecx
    lea rdx, [rel base]
.base_init:
    cmp rcx, [rel shnum]
    jae .base_done
    mov qword [rdx + rcx*8], -1
    inc rcx
    jmp .base_init
.base_done:
    mov rax, [rel code_idx]
    mov qword [rdx + rax*8], 0
    lea rdi, [rel obuf]
    lea rsi, [rel buf]
    add rsi, [rel code_off]
    mov rcx, [rel code_sz]
    cmp rcx, IN_CAP
    ja .full
    rep movsb
    mov rax, [rel code_sz]
    mov [rel out_sz], rax
    xor r12d, r12d
.lay:
    cmp r12, [rel nrodata]
    jae .lay_done
    lea rax, [rel rodata]
    mov r13, [rax + r12*8]                ; its index
    mov r14, r13
    shl r14, 6
    add r14, [rel shoff]
    lea rax, [rel buf]
    add r14, rax                          ; its header
    mov rcx, [r14 + 48]                   ; align (0 or 1: none)
    mov rax, [rel out_sz]
    cmp rcx, 1
    jbe .aligned
    lea rax, [rax + rcx - 1]
    neg rcx
    and rax, rcx
.aligned:
    mov rcx, rax                          ; zero the padding
    sub rcx, [rel out_sz]
    lea rdi, [rel obuf]
    add rdi, [rel out_sz]
    push rax
    xor eax, eax
    rep stosb
    pop rax
    mov rdx, [r14 + 32]                   ; its size
    mov rcx, IN_CAP
    sub rcx, rax
    cmp rdx, rcx
    ja .full
    lea rcx, [rel base]
    mov [rcx + r13*8], rax
    lea rdi, [rel obuf]
    add rdi, rax
    lea rsi, [rel buf]
    add rsi, [r14 + 24]
    mov rcx, rdx
    rep movsb
    add rax, rdx
    mov [rel out_sz], rax
    inc r12
    jmp .lay
.lay_done:

    ; ---- the symbols
    mov qword [rel nsyms], 0
    mov r12d, 1                           ; entry 0 is the null symbol
.sym:
    mov rax, r12
    imul rax, rax, 24
    cmp rax, [rel sym_sz]
    jae .sym_done
    lea r13, [rel buf]
    add r13, [rel sym_off]
    add r13, rax                          ; r13 -> Elf64_Sym
    movzx eax, byte [r13 + 4]             ; st_info
    mov r14d, eax
    shr r14d, 4                           ; binding
    and eax, 0xF                          ; type
    mov r15d, eax
    movzx eax, word [r13 + 6]             ; st_shndx
    test eax, eax
    jnz .sym_defined
    cmp dword [r13], 0                    ; an undefined named symbol: refused
    jne .undefined
.sym_defined:
    test r14d, r14d                       ; STB_LOCAL: ignored
    jz .sym_next
    cmp r14d, 1                           ; only STB_GLOBAL
    jne .bad_global
    cmp r15d, 2                           ; STT_FUNC
    jne .bad_global
    movzx eax, word [r13 + 6]
    cmp rax, [rel code_idx]
    jne .bad_global
    test byte [r13 + 5], 3                ; default visibility
    jnz .bad_global
    mov rax, [r13 + 8]                    ; st_value .. + st_size inside the code
    mov rcx, [rel code_sz]
    cmp rax, rcx
    ja .bad_global
    sub rcx, rax
    cmp [r13 + 16], rcx
    ja .bad_global
    ; the name: inside the string table, NUL-terminated, an identifier
    mov eax, [r13]
    cmp rax, [rel str_sz]
    jae .bad_name
    lea rsi, [rel buf]
    add rsi, [rel str_off]
    add rsi, rax                          ; rsi -> name
    mov rcx, [rel str_sz]
    sub rcx, rax                          ; bytes left in the table
    xor edx, edx
.nm:
    cmp rdx, rcx
    jae .bad_name
    movzx eax, byte [rsi + rdx]
    test eax, eax
    jz .nm_end
    cmp eax, '_'
    je .nm_ok
    cmp eax, '0'
    jb .bad_name
    cmp eax, '9'
    ja .nm_alpha
    test rdx, rdx
    jz .bad_name                          ; not a leading digit
    jmp .nm_ok
.nm_alpha:
    or eax, 0x20
    cmp eax, 'a'
    jb .bad_name
    cmp eax, 'z'
    ja .bad_name
.nm_ok:
    inc rdx
    cmp rdx, 127
    ja .bad_name
    jmp .nm
.nm_end:
    test rdx, rdx
    jz .bad_name
    ; once
    xor ecx, ecx
.dup:
    cmp rcx, [rel nsyms]
    jae .add
    imul r8, rcx, 24
    lea r9, [rel syms]
    add r9, r8
    cmp [r9 + 16], rdx
    jne .dup_next
    mov rdi, [r9 + 8]
    xor r10d, r10d
.cmp:
    cmp r10, rdx
    jae .is_dup
    mov al, [rdi + r10]
    cmp al, [rsi + r10]
    jne .dup_next
    inc r10
    jmp .cmp
.is_dup:
    lea rdi, [rel m_dup]
    jmp fail                              ; rsi, rdx = the name
.dup_next:
    inc rcx
    jmp .dup
.add:
    mov rcx, [rel nsyms]
    cmp rcx, SYM_CAP
    jae .full
    imul r8, rcx, 24
    lea r9, [rel syms]
    add r9, r8
    mov rax, [r13 + 8]
    mov [r9], rax
    mov [r9 + 8], rsi
    mov [r9 + 16], rdx
    inc qword [rel nsyms]
.sym_next:
    inc r12
    jmp .sym
.sym_done:
    cmp qword [rel nsyms], 0
    je .no_func

    ; ---- the relocations: in the code, PC32 or PLT32, to a placed section
    xor r12d, r12d
.rsec:
    cmp r12, [rel nrelas]
    jae .relocs_done
    lea rax, [rel relas]
    mov r13, [rax + r12*8]
    shl r13, 6
    add r13, [rel shoff]
    lea rax, [rel buf]
    add r13, rax                          ; the SHT_RELA header
    mov eax, [r13 + 44]                   ; sh_info: the section it changes
    cmp rax, [rel code_idx]
    jne .has_reloc
    mov eax, [r13 + 40]                   ; sh_link: our symbol table
    cmp rax, [rel sym_idx]
    jne .has_reloc
    mov r14, [r13 + 24]                   ; entries
    mov r15, [r13 + 32]
    add r15, r14                          ; end
.rent:
    cmp r14, r15
    jae .rsec_next
    lea rbx, [rel buf]
    add rbx, r14                          ; Elf64_Rela: offset, info, addend
    mov eax, [rbx + 8]                    ; type
    cmp eax, 2                            ; R_X86_64_PC32
    je .rtype_ok
    cmp eax, 4                            ; R_X86_64_PLT32
    jne .has_reloc
.rtype_ok:
    mov rcx, [rel code_sz]                ; P + 4 inside the code
    cmp rcx, 4
    jb .has_reloc
    sub rcx, 4
    cmp [rbx], rcx
    ja .has_reloc
    mov eax, [rbx + 12]                   ; the symbol's index
    imul rax, rax, 24
    cmp rax, [rel sym_sz]
    jae .has_reloc
    lea rdx, [rel buf]
    add rdx, [rel sym_off]
    add rdx, rax                          ; Elf64_Sym
    movzx eax, word [rdx + 6]             ; its section
    cmp rax, [rel shnum]
    jae .has_reloc                        ; undefined is refused above; ABS, COMMON here
    lea rcx, [rel base]
    mov rax, [rcx + rax*8]
    cmp rax, -1
    je .has_reloc                         ; a section that is not placed
    add rax, [rdx + 8]                    ; S = base + st_value
    add rax, [rbx + 16]                   ; + A
    sub rax, [rbx]                        ; - P
    movsxd rcx, eax
    cmp rcx, rax
    jne .bad_range
    lea rcx, [rel obuf]
    add rcx, [rbx]
    mov [rcx], eax
    add r14, 24
    jmp .rent
.rsec_next:
    inc r12
    jmp .rsec
.relocs_done:

    ; ---- the Sutram object: header, code, symbols, no relocations
    mov rdi, [rel outpath]
    mov esi, 0x241                        ; O_WRONLY|O_CREAT|O_TRUNC
    mov edx, 0o644
    mov eax, 2
    syscall
    test rax, rax
    js .out_fail
    mov [rel fd], rax
    mov rax, MAGIC
    call put_u64
    mov rax, [rel out_sz]
    call put_u64
    mov rax, [rel nsyms]
    call put_u64
    xor eax, eax
    call put_u64
    lea rsi, [rel obuf]
    mov rdx, [rel out_sz]
    call write_all
    xor r12d, r12d
.out_sym:
    cmp r12, [rel nsyms]
    jae .out_done
    imul r13, r12, 24
    lea rax, [rel syms]
    add r13, rax
    mov rax, [r13]
    call put_u64
    mov rax, [r13 + 16]
    call put_u64
    mov rsi, [r13 + 8]
    mov rdx, [r13 + 16]
    call write_all
    inc r12
    jmp .out_sym
.out_done:
    mov rdi, [rel fd]
    mov eax, 3
    syscall
    lea rdi, [rel m_ok]
    call puts
    mov rax, [rel nsyms]
    call putu
    lea rdi, [rel m_tail]
    call puts
    mov rax, [rel out_sz]
    call putu
    lea rdi, [rel m_bytes]
    call puts
    xor edi, edi
    mov eax, 60
    syscall

.usage:
    lea rdi, [rel m_usage]
    call puts
    mov edi, 2
    mov eax, 60
    syscall
.open_fail:
    lea rdi, [rel m_open]
    mov rsi, [rsp + 16]
    xor edx, edx
    jmp fail
.out_fail:
    lea rdi, [rel m_open]
    mov rsi, [rel outpath]
    xor edx, edx
    jmp fail
.not_elf:
    lea rdi, [rel m_notelf]
    xor esi, esi
    jmp fail
.has_reloc:
    lea rdi, [rel m_reloc]
    xor esi, esi
    jmp fail
.bad_align:
    lea rdi, [rel m_align]
    xor esi, esi
    jmp fail
.bad_range:
    lea rdi, [rel m_range]
    xor esi, esi
    jmp fail
.other_alloc:
    lea rdi, [rel m_alloc]
    xor esi, esi
    jmp fail
.two_code:
.no_code:
    lea rdi, [rel m_code]
    xor esi, esi
    jmp fail
.two_symtab:
.no_symtab:
    lea rdi, [rel m_symtab]
    xor esi, esi
    jmp fail
.undefined:
    mov eax, [r13]                        ; name it, if the name is in bounds
    xor esi, esi
    cmp rax, [rel str_sz]
    jae .undef_print
    lea rsi, [rel buf]
    add rsi, [rel str_off]
    add rsi, rax
.undef_print:
    lea rdi, [rel m_undef]
    xor edx, edx
    test rsi, rsi
    jz fail
    ; bound the printed name to the string table
    mov rcx, [rel str_sz]
    sub rcx, rax
.ul: cmp rdx, rcx
    jae fail
    cmp byte [rsi + rdx], 0
    je .ul_d
    inc rdx
    jmp .ul
.ul_d:
    test rdx, rdx
    jnz fail
    xor esi, esi
    jmp fail
.bad_global:
    lea rdi, [rel m_global]
    xor esi, esi
    jmp fail
.bad_name:
    lea rdi, [rel m_name]
    xor esi, esi
    jmp fail
.no_func:
    lea rdi, [rel m_none]
    xor esi, esi
    jmp fail
.full:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
