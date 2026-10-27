; ===================================================================
; sutram-coff2smo - a Windows foreign object, read into a Sutram object. ROUND-35.
; Ours, in NASM: the Windows counterpart of sutram-elf2smo.
;
;   sutram-coff2smo in.obj out.smo
;
; Reads one COFF x64 object (Machine 0x8664, no optional header) - a C function
; compiled for Windows (the Microsoft x64 ABI), say
;   gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-stack-protector f.c
; - and writes a SUTRAMO2 object (docs/OBJECT-FORMAT.md, version 2: a PE
; program's code) that sutram-link links like any other: its code, and one
; symbol per function. SUTRAMO2 is unchanged: no field was needed.
;
; sutram-elf2smo's rules, for COFF:
;   * exactly one non-empty code section (CNT_CODE or MEM_EXECUTE, not WRITE);
;   * read-only data sections (INITIALIZED_DATA, not WRITE, not EXECUTE) - a
;     double constant, a string literal - placed after the code, each at its
;     alignment, at most 16: in a PE, sutram-link starts every object after the
;     first on a 16-byte boundary of the image, so a 16-byte constant (what
;     xorpd/andpd read) stays aligned;
;   * relocations in the code only, of the PC-relative kinds IMAGE_REL_AMD64_REL32
;     and REL32_1..REL32_5, against a symbol in the code or in a placed data
;     section; each is resolved here (S + A - (P + 4 + k), A in place, as COFF
;     keeps it). Nothing is left for the linker;
;   * no undefined symbol: a foreign function that calls out is refused (a C
;     function must never call a Sutram prakriya);
;   * refused: writable data, bss, unwind tables (.pdata, .xdata), linker
;     directives (.drectve and any LNK_INFO section), relocations in data, a
;     weak external, an absolute or any other relocation. Discardable sections
;     (debug information) are skipped;
;   * every EXTERNAL symbol defined in the code section is exported, named
;     [A-Za-z_][A-Za-z0-9_]* (at most 127 bytes), once; an EXTERNAL defined
;     elsewhere is refused; STATIC, LABEL, FUNCTION and FILE symbols are not
;     exported.
; Every offset and length is checked against the file before it is used. Like
; sutram-link, one source builds for Linux (raw syscalls) and, with -DWINDOWS,
; for Windows (kernel32 through win/winrt.inc).
;
; Exit 0 on success; 1 with a diagnostic; 2 on a usage error.
; ===================================================================

IN_CAP  equ 4*1024*1024
SYM_CAP equ 256
SEC_CAP equ 256
MAGIC_W equ 0x324F4D4152545553   ; "SUTRAMO2"
ARGS_CAP equ 8
ARGBUF_CAP equ 8192

section .data
    m_usage  db "Prayog: sutram-coff2smo videshi.obj nirgat.smo", 10, 0
    m_open   db "Sutram Error: patram na udghatitam: ", 0
    m_notcoff db "Sutram Error: COFF x64 vastu-patram na", 10, 0
    m_bounds db "Sutram Error: COFF-patram khanditam (seema-bahir)", 10, 0
    m_code   db "Sutram Error: COFF-patre ekam eva sanket-khandam apekshitam", 10, 0
    m_reloc  db "Sutram Error: COFF-patre punahsthapanam asamarthitam", 10, 0
    m_unwind db "Sutram Error: COFF-patre punahsthapanam asamarthitam (.pdata/.xdata)", 10, 0
    m_align  db "Sutram Error: COFF-patre 16-baait-adhika samarekhanam asamarthitam", 10, 0
    m_range  db "Sutram Error: COFF-patre punahsthapanam 32-bit-bahih", 10, 0
    m_alloc  db "Sutram Error: COFF-patre sanketat anyat bhara-khandam asamarthitam", 10, 0
    m_undef  db "Sutram Error: COFF-patre agyat sanket: ", 0
    m_global db "Sutram Error: COFF-patre sarvatrik sanket prakriya na: ", 0
    m_name   db "Sutram Error: COFF-patre sanket-nama dushtam", 10, 0
    m_dup    db "Sutram Error: COFF-patre prakriya dvih: ", 0
    m_none   db "Sutram Error: COFF-patre sarvatrik prakriya nasti", 10, 0
    m_full   db "Sutram Error: sutram-coff2smo seema atikram", 10, 0
    m_ok     db "Siddh: ", 0
    m_tail   db " prakriya, ", 0
    m_bytes  db " baait", 10, 0
    m_nl     db 10, 0
    s_pdata  db ".pdata", 0, 0
    s_xdata  db ".xdata", 0, 0

section .bss
    argc     resq 1
    argv     resq 1
    buf      resb IN_CAP
    fsize    resq 1
    nsec     resq 1
    symptr   resq 1
    nsym     resq 1
    strtab   resq 1                   ; file offset of the string table
    strsz    resq 1
    code_sec resq 1                   ; the code section's number (1-based), or 0
    code_ptr resq 1
    code_raw resq 1
    code_rel resq 1                   ; its relocations: file offset, count
    code_nrel resq 1
    base     resq SEC_CAP             ; each section's offset in obuf, or -1
    syms     resq SYM_CAP*3           ; offset, name pointer, name length
    nsyms    resq 1
    hdr      resq 1
    obuf     resb IN_CAP              ; the code, then the read-only data
    out_sz   resq 1
    numbuf   resb 32
    fd       resq 1
%ifdef WINDOWS
    orig_rsp resq 1                   ; win/winrt.inc's win_build_argv names it; unused here
    wl_argv  resq ARGS_CAP + 1
    wl_args  resb ARGBUF_CAP
%endif

section .text
global _start

; ---------------------------------------------------------------- the host
; os_write(rdi = fd, rsi, rdx) / os_read(rdi, rsi, rdx) -> rax
; os_open(rdi = path, rsi = flags: 0 read, else create, rdx = mode) -> rax, negative on failure
; os_close(rdi) / os_exit(rdi)
%ifndef WINDOWS
os_write:
    mov eax, 1
    syscall
    ret
os_read:
    xor eax, eax
    syscall
    ret
os_open:
    mov eax, 2
    syscall
    ret
os_close:
    mov eax, 3
    syscall
    ret
os_exit:
    mov eax, 60
    syscall
%else
%include "win/winrt.inc"
section .text

; wl_build_argv: GetCommandLineA split into argv (spaces and tabs separate; a
; double quote groups), as sutram-link does. Too long a command line is a usage error.
wl_build_argv:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov rbx, rsp
    and rsp, -16
    sub rsp, 32
    call qword [rel p_cmdline]
    mov rsp, rbx
    test rax, rax
    jz .finish0
    mov r12, rax
    lea r13, [rel wl_args]
    lea r14, [rel wl_argv]
    xor r15d, r15d
.skip:
    mov al, [r12]
    test al, al
    jz .finish
    cmp al, ' '
    je .adv
    cmp al, 9
    je .adv
    cmp r15, ARGS_CAP
    jae .reject
    mov [r14 + r15*8], r13
    inc r15
.tok:
    mov al, [r12]
    test al, al
    jz .end
    cmp al, ' '
    je .end
    cmp al, 9
    je .end
    cmp al, '"'
    je .open
    call .put
    jmp .tok
.open:
    inc r12
.q:
    mov al, [r12]
    test al, al
    jz .end
    cmp al, '"'
    je .qend
    call .put
    jmp .q
.qend:
    inc r12
    jmp .tok
.end:
    lea rax, [rel wl_args + ARGBUF_CAP - 1]
    cmp r13, rax
    ja .reject
    mov byte [r13], 0
    inc r13
    jmp .skip
.adv:
    inc r12
    jmp .skip
.put:
    lea rax, [rel wl_args + ARGBUF_CAP - 2]
    cmp r13, rax
    ja .reject_pop
    mov al, [r12]
    mov [r13], al
    inc r13
    inc r12
    ret
.reject_pop:
    add rsp, 8
.reject:
    mov edi, 2
    call os_exit
.finish0:
    xor r15d, r15d
.finish:
    mov qword [r14 + r15*8], 0
    mov [rel argc], r15
    mov [rel argv], r14
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
%endif

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
    jmp os_write

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
    call os_write
.nl:
    lea rdi, [rel m_nl]
    call puts
.x: mov edi, 1
    call os_exit

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

; need(rdi = file offset, rsi = length): both inside the file, or fail.
need:
    mov rax, rdi
    add rax, rsi
    jc .bad
    cmp rax, [rel fsize]
    ja .bad
    ret
.bad:
    lea rdi, [rel m_bounds]
    xor esi, esi
    jmp fail

; sym_entry(rax = symbol index) -> rax = its address in buf (checked in range).
sym_entry:
    cmp rax, [rel nsym]
    jae .bad
    imul rax, rax, 18
    add rax, [rel symptr]
    lea rcx, [rel buf]
    add rax, rcx
    ret
.bad:
    lea rdi, [rel m_reloc]
    xor esi, esi
    jmp fail

; sym_name(rbx = symbol entry) -> rsi = name, rdx = length (checked).
sym_name:
    cmp dword [rbx], 0
    je .long
    mov rsi, rbx                    ; short: up to 8 bytes, NUL-padded
    xor edx, edx
.s: cmp edx, 8
    jae .done
    cmp byte [rsi + rdx], 0
    je .done
    inc edx
    jmp .s
.long:
    mov eax, [rbx + 4]              ; offset into the string table
    cmp rax, 4
    jb .bad
    cmp rax, [rel strsz]
    jae .bad
    lea rsi, [rel buf]
    add rsi, [rel strtab]
    mov rcx, [rel strsz]
    sub rcx, rax                    ; bytes left in the table
    add rsi, rax
    xor edx, edx
.l: cmp rdx, rcx
    jae .bad                        ; no NUL before the table ends
    cmp byte [rsi + rdx], 0
    je .done
    inc rdx
    jmp .l
.done:
    ret
.bad:
    lea rdi, [rel m_name]
    xor esi, esi
    jmp fail

; valid_name(rsi = name, rdx = length) -> ZF = 1 when [A-Za-z_][A-Za-z0-9_]*, 1..127.
valid_name:
    test rdx, rdx
    jz .no
    cmp rdx, 127
    ja .no
    xor ecx, ecx
.l: cmp rcx, rdx
    jae .yes
    movzx eax, byte [rsi + rcx]
    cmp al, '_'
    je .ok
    cmp al, '0'
    jb .no
    cmp al, '9'
    ja .alpha
    test rcx, rcx
    jz .no
    jmp .ok
.alpha:
    or al, 0x20
    cmp al, 'a'
    jb .no
    cmp al, 'z'
    ja .no
.ok:
    inc rcx
    jmp .l
.yes:
    xor eax, eax
    ret
.no:
    or eax, 1
    ret

; ---------------------------------------------------------------- main
_start:
%ifdef WINDOWS
    call rt_init
    call wl_build_argv
%else
    mov rax, [rsp]
    mov [rel argc], rax
    lea rax, [rsp + 8]
    mov [rel argv], rax
%endif
    cmp qword [rel argc], 3
    je .args
    lea rdi, [rel m_usage]
    call puts
    mov edi, 2
    call os_exit
.args:
    ; the whole object into buf
    mov rcx, [rel argv]
    mov rdi, [rcx + 8]
    xor esi, esi
    xor edx, edx
    call os_open
    test rax, rax
    js .open_fail
    mov [rel fd], rax
.rd:
    mov rdx, IN_CAP
    sub rdx, [rel fsize]
    jz .too_big
    mov rdi, [rel fd]
    lea rsi, [rel buf]
    add rsi, [rel fsize]
    call os_read
    test rax, rax
    js .open_fail
    jz .eof
    add [rel fsize], rax
    jmp .rd
.too_big:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
.open_fail:
    lea rdi, [rel m_open]
    mov rcx, [rel argv]
    mov rsi, [rcx + 8]
    xor edx, edx
    jmp fail
.eof:
    mov rdi, [rel fd]
    call os_close

    ; the file header: AMD64, no optional header
    cmp qword [rel fsize], 20
    jb .notcoff
    lea rbx, [rel buf]
    cmp word [rbx], 0x8664
    jne .notcoff
    cmp word [rbx + 16], 0
    jne .notcoff
    movzx eax, word [rbx + 2]
    cmp rax, SEC_CAP
    ja .full
    mov [rel nsec], rax
    mov eax, [rbx + 8]
    mov [rel symptr], rax
    mov eax, [rbx + 12]
    mov [rel nsym], rax
    ; the section table
    mov rdi, 20
    imul rsi, [rel nsec], 40
    call need
    ; the symbol table, then the string table right after it
    mov rdi, [rel symptr]
    imul rsi, [rel nsym], 18
    call need
    imul rax, [rel nsym], 18
    add rax, [rel symptr]
    mov [rel strtab], rax
    mov rdi, rax
    mov esi, 4
    call need
    mov rax, [rel strtab]
    lea rcx, [rel buf]
    mov eax, [rcx + rax]
    cmp rax, 4
    jb .bounds
    mov [rel strsz], rax
    mov rdi, [rel strtab]
    mov rsi, rax
    call need

    ; ------------------------------------------------ the sections
    xor r12d, r12d
.sec:
    cmp r12, [rel nsec]
    jae .sec_done
    lea rcx, [rel base]
    mov qword [rcx + r12*8], -1
    imul rbx, r12, 40
    lea rax, [rel buf + 20]
    add rbx, rax                    ; the section header
    mov r13d, [rbx + 36]            ; characteristics
    mov r14d, [rbx + 16]            ; SizeOfRawData
    test r13d, 0x01000000           ; LNK_NRELOC_OVFL
    jnz .reloc_bad
    mov rax, [rbx]                  ; unwind tables are refused, as by sutram-elf2smo
    cmp rax, [rel s_pdata]
    je .unwind
    cmp rax, [rel s_xdata]
    je .unwind
    test r13d, 0x02000000           ; DISCARDABLE (debug information): skipped
    jnz .sec_next
    test r13d, 0x00000800           ; LNK_REMOVE: skipped
    jnz .sec_next
    test r14, r14
    jz .sec_next                    ; empty: nothing to place
    test r13d, 0x00000200           ; LNK_INFO (.drectve): refused
    jnz .alloc_bad
    test r13d, 0x00000080           ; bss
    jnz .alloc_bad
    test r13d, 0x80000000           ; writable
    jnz .alloc_bad
    mov edi, [rbx + 20]             ; its bytes are in the file
    mov rsi, r14
    call need
    test r13d, 0x20000020           ; code
    jz .data
    cmp qword [rel code_sec], 0
    jne .code_bad
    lea rax, [r12 + 1]
    mov [rel code_sec], rax
    mov eax, [rbx + 20]
    mov [rel code_ptr], rax
    mov [rel code_raw], r14
    mov eax, [rbx + 24]
    mov [rel code_rel], rax
    movzx eax, word [rbx + 32]
    mov [rel code_nrel], rax
    jmp .sec_next
.data:
    test r13d, 0x00000040           ; initialized data, not code: read-only data
    jz .alloc_bad
    cmp word [rbx + 32], 0          ; no relocations in data
    jne .reloc_bad
.sec_next:
    inc r12
    jmp .sec
.sec_done:
    cmp qword [rel code_sec], 0
    je .code_bad

    ; ------------------------------------------------ the layout: code, then data
    mov rcx, [rel code_raw]
    lea rdi, [rel obuf]
    lea rsi, [rel buf]
    add rsi, [rel code_ptr]
    rep movsb
    mov rax, [rel code_raw]
    mov [rel out_sz], rax
    mov rax, [rel code_sec]
    lea rcx, [rel base]
    mov qword [rcx + rax*8 - 8], 0
    xor r12d, r12d
.place:
    cmp r12, [rel nsec]
    jae .placed
    lea rax, [r12 + 1]
    cmp rax, [rel code_sec]
    je .place_next
    imul rbx, r12, 40
    lea rax, [rel buf + 20]
    add rbx, rax
    mov r13d, [rbx + 36]
    mov r14d, [rbx + 16]
    test r13d, 0x02000800           ; skipped above
    jnz .place_next
    test r14, r14
    jz .place_next
    mov rax, [rbx]
    cmp rax, [rel s_pdata]
    je .place_next
    ; its alignment: (characteristics >> 20) & 15 = n -> 2^(n-1); 0: 16
    mov ecx, r13d
    shr ecx, 20
    and ecx, 15
    mov eax, 16
    jz .align
    cmp ecx, 5
    ja .align_bad
    dec ecx
    mov eax, 1
    shl eax, cl
.align:
    mov rcx, [rel out_sz]
    dec rax
    add rcx, rax
    not rax
    and rcx, rax                    ; out_sz rounded up (the gap stays zero)
    mov [rel out_sz], rcx
    lea rax, [rel base]
    mov [rax + r12*8], rcx
    lea rdx, [rcx + r14]
    cmp rdx, IN_CAP
    ja .full
    lea rdi, [rel obuf]
    add rdi, rcx
    mov esi, [rbx + 20]
    lea rax, [rel buf]
    add rsi, rax
    mov rcx, r14
    rep movsb
    add [rel out_sz], r14
.place_next:
    inc r12
    jmp .place
.placed:

    ; ------------------------------------------------ the symbols
    xor r12d, r12d
.sym:
    cmp r12, [rel nsym]
    jae .sym_done
    mov rax, r12
    call sym_entry
    mov rbx, rax
    movzx r13d, byte [rbx + 17]     ; aux records that follow it
    movzx eax, byte [rbx + 16]      ; storage class
    cmp eax, 2
    je .external
    cmp eax, 3                      ; STATIC (sections, static functions)
    je .sym_next
    cmp eax, 6                      ; LABEL
    je .sym_next
    cmp eax, 101                    ; FUNCTION (.bf, .ef)
    je .sym_next
    cmp eax, 103                    ; FILE
    je .sym_next
    call sym_name                   ; a weak external or anything else
    lea rdi, [rel m_global]
    jmp fail
.external:
    movsx eax, word [rbx + 12]      ; section number
    test eax, eax
    jnz .defined
    call sym_name                   ; undefined: the C code calls out
    lea rdi, [rel m_undef]
    jmp fail
.defined:
    cmp rax, [rel code_sec]
    je .export
    call sym_name                   ; a global that is data, or absolute
    lea rdi, [rel m_global]
    jmp fail
.export:
    call sym_name
    push rsi
    push rdx
    call valid_name
    pop rdx
    pop rsi
    jnz .name_bad
    mov eax, [rbx + 8]              ; its offset, inside the code
    cmp rax, [rel code_raw]
    jae .reloc_bad
    ; once
    xor ecx, ecx
.uniq:
    cmp rcx, [rel nsyms]
    jae .add
    imul r8, rcx, 24
    lea r9, [rel syms]
    add r8, r9
    cmp rdx, [r8 + 16]
    jne .uniq_next
    push rcx
    push rsi
    mov rdi, [r8 + 8]
    mov rcx, rdx
    repe cmpsb
    pop rsi
    pop rcx
    je .dup
.uniq_next:
    inc rcx
    jmp .uniq
.add:
    mov rcx, [rel nsyms]
    cmp rcx, SYM_CAP
    jae .full
    imul r8, rcx, 24
    lea r9, [rel syms]
    add r8, r9
    mov eax, [rbx + 8]
    mov [r8], rax
    mov [r8 + 8], rsi
    mov [r8 + 16], rdx
    inc qword [rel nsyms]
.sym_next:
    lea r12, [r12 + 1 + r13]
    jmp .sym
.dup:
    lea rdi, [rel m_dup]
    jmp fail
.sym_done:
    cmp qword [rel nsyms], 0
    je .none

    ; ------------------------------------------------ the code's relocations, resolved
    mov rdi, [rel code_rel]
    imul rsi, [rel code_nrel], 10
    call need
    xor r12d, r12d
.rel:
    cmp r12, [rel code_nrel]
    jae .rel_done
    imul rbx, r12, 10
    add rbx, [rel code_rel]
    lea rax, [rel buf]
    add rbx, rax                    ; the relocation record
    movzx r13d, word [rbx + 8]      ; type: REL32 (4) .. REL32_5 (9)
    cmp r13d, 4
    jb .reloc_bad
    cmp r13d, 9
    ja .reloc_bad
    sub r13d, 4                     ; k: bytes after the field
    mov r14d, [rbx]                 ; P: the field's offset in the code
    lea rax, [r14 + 4]
    cmp rax, [rel code_raw]
    ja .reloc_bad
    mov eax, [rbx + 4]              ; its symbol
    call sym_entry
    mov r15, rax
    movsx eax, word [r15 + 12]
    test eax, eax
    jg .rel_sec
    jnz .reloc_bad                  ; absolute or debug
    mov rbx, r15                    ; undefined: the C code calls out
    call sym_name
    lea rdi, [rel m_undef]
    jmp fail
.rel_sec:
    cmp rax, [rel nsec]
    ja .reloc_bad
    lea rcx, [rel base]
    mov rcx, [rcx + rax*8 - 8]
    cmp rcx, -1
    je .reloc_bad                   ; a section that was not placed
    mov eax, [r15 + 8]
    add rcx, rax                    ; S
    lea rdx, [rel obuf]
    movsxd rax, dword [rdx + r14]   ; A, in place
    add rcx, rax
    lea rax, [r14 + 4 + r13]
    sub rcx, rax                    ; S + A - (P + 4 + k)
    movsxd rax, ecx
    cmp rax, rcx
    jne .range
    mov [rdx + r14], ecx
    inc r12
    jmp .rel
.rel_done:

    ; ------------------------------------------------ the SUTRAMO2 object
    mov rcx, [rel argv]
    mov rdi, [rcx + 16]
    mov esi, 0x241                  ; O_WRONLY|O_CREAT|O_TRUNC
    mov edx, 0o644
    call os_open
    test rax, rax
    js .out_fail
    mov [rel fd], rax
    mov rax, MAGIC_W
    call put_u64
    mov rax, [rel out_sz]
    call put_u64
    mov rax, [rel nsyms]
    call put_u64
    xor eax, eax
    call put_u64
    mov rdi, [rel fd]
    lea rsi, [rel obuf]
    mov rdx, [rel out_sz]
    call os_write
    xor r12d, r12d
.out_sym:
    cmp r12, [rel nsyms]
    jae .out_done
    imul rbx, r12, 24
    lea rax, [rel syms]
    add rbx, rax
    mov rax, [rbx]
    call put_u64
    mov rax, [rbx + 16]
    call put_u64
    mov rdi, [rel fd]
    mov rsi, [rbx + 8]
    mov rdx, [rbx + 16]
    call os_write
    inc r12
    jmp .out_sym
.out_done:
    mov rdi, [rel fd]
    call os_close
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
    call os_exit

.out_fail:
    lea rdi, [rel m_open]
    mov rcx, [rel argv]
    mov rsi, [rcx + 16]
    xor edx, edx
    jmp fail
.notcoff:
    lea rdi, [rel m_notcoff]
    xor esi, esi
    jmp fail
.bounds:
    lea rdi, [rel m_bounds]
    xor esi, esi
    jmp fail
.full:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
.code_bad:
    lea rdi, [rel m_code]
    xor esi, esi
    jmp fail
.reloc_bad:
    lea rdi, [rel m_reloc]
    xor esi, esi
    jmp fail
.unwind:
    lea rdi, [rel m_unwind]
    xor esi, esi
    jmp fail
.align_bad:
    lea rdi, [rel m_align]
    xor esi, esi
    jmp fail
.alloc_bad:
    lea rdi, [rel m_alloc]
    xor esi, esi
    jmp fail
.range:
    lea rdi, [rel m_range]
    xor esi, esi
    jmp fail
.name_bad:
    lea rdi, [rel m_name]
    xor esi, esi
    jmp fail
.none:
    lea rdi, [rel m_none]
    xor esi, esi
    jmp fail

; put_u64(rax) to [fd]
put_u64:
    mov [rel hdr], rax
    mov rdi, [rel fd]
    lea rsi, [rel hdr]
    mov edx, 8
    jmp os_write
