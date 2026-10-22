; ===================================================================
; sutram-link - the Sutram linker. ROUND-28. Ours, in NASM.
;
;   sutram-link out.bin a.smo [b.smo ...]
;
; Reads Sutram object files (written by `sutram_compiler --object`, the format
; in docs/OBJECT-FORMAT.md), lays their code end to end - the one that defines
; mukhya first, so mukhya is the entry point - fills every relocation with the
; prakriya some object defines, and writes the same kind of executable the
; compiler writes for an ordinary program.
;
; R34: two targets, chosen by the objects' magic, never mixed:
;   SUTRAMO1 (the Linux compiler's)   -> an ELF: one PT_LOAD at 0x400000 + 120.
;   SUTRAMO2 (the Windows compiler's) -> a PE, laid out as the compiler's
;       write_pe lays it out: [headers][runtime blob][code], then the .data
;       section with the vitti and the kernel32 imports. The blob's two
;       entries are the symbols "rt:init" and "rt:syscall"; a "vitti:<name>"
;       symbol is an offset in its object's data, placed in .data.
; And two hosts: this file builds as a Linux program (raw syscalls) and, with
; -DWINDOWS, as a Windows one (kernel32 through win/winrt.inc). Either host
; links either target.
;
; An ordinary program never comes here: the compiler still writes its
; executable itself, in one pass. This program exists only for programs built
; from separately compiled modules.
;
; Exit 0 on success; 1 with a diagnostic on a bad object, an undefined or
; duplicate prakriya, no mukhya, or mixed targets; 2 on a usage error.
; ===================================================================

BASE_ADDR    equ 0x400000
HEADERS_SIZE equ 120
IN_CAP       equ 16*1024*1024
OUT_CAP      equ 16*1024*1024
OBJ_CAP      equ 64
OBJ_SIZE     equ 80                ; path, code, size, syms, nsyms, relocs, nrelocs, base, data base, data size
SYM_CAP      equ 16384
SYM_SIZE     equ 32                ; name, length, value, kind
KIND_CODE    equ 0                 ; value: an offset from the start of the output's code
KIND_DATA    equ 1                 ; value: an offset in the PE's .data
MAGIC        equ 0x314F4D4152545553   ; "SUTRAMO1"
MAGIC_W      equ 0x324F4D4152545553   ; "SUTRAMO2" (R34): version 2, a PE program's code
ARGS_CAP     equ OBJ_CAP + 4
ARGBUF_CAP   equ 32768

%include "win/pe_layout.inc"

section .data
    m_usage   db "Prayog: sutram-link nirgat.bin a.smo [b.smo ...]", 10, 0
    m_open    db "Sutram Error: patram na udghatitam: ", 0
    m_bad     db "Sutram Error: vastu-patram na (SUTRAMO1 apekshitam): ", 0
    m_undef   db "Sutram Error: agyat prakriya: ", 0
    m_dup     db "Sutram Error: prakriya dvih paribhashita: ", 0
    m_nomain  db "Sutram Error: kasminnapi vastu-patre mukhya nasti", 10, 0
    m_full    db "Sutram Error: sutram-link seema atikram", 10, 0
    m_mixed   db "Sutram Error: vastu-patrani bhinna-lakshyani (SUTRAMO1 SUTRAMO2 ca): ", 0
    m_gfull   db "Sutram Error: ghatak-star vitti seema atikram", 10, 0
    m_ok      db "Siddh: ", 0
    m_bytes   db " baait sankalit", 10, 0
    m_nl      db 10, 0
    s_mukhya  db "mukhya"
    s_vitti   db "vitti:"
    s_rt_init db "rt:init"
    s_rt_sys  db "rt:syscall"

section .bss
    argc      resq 1
    argv      resq 1
    in_buf    resb IN_CAP
    in_used   resq 1
    out_code  resb OUT_CAP
    out_size  resq 1
    data_size resq 1                ; R34: the vitti the PE's .data holds
    objs      resb OBJ_CAP*OBJ_SIZE
    nobjs     resq 1
    order     resq OBJ_CAP
    syms      resb SYM_CAP*SYM_SIZE
    nsyms     resq 1
    main_obj  resq 1
    target_w  resq 1                ; R34: 1 = SUTRAMO2 objects, a PE
    hdr       resb 128
    pe_hdr    resb 512
    pe_pad    resb 256
    numbuf    resb 32
    fd        resq 1
%ifdef WINDOWS
    orig_rsp  resq 1                ; win/winrt.inc's win_build_argv names it; unused here
    wl_argv   resq ARGS_CAP + 1
    wl_args   resb ARGBUF_CAP
%endif

section .text
global _start

; ---------------------------------------------------------------- the host
; os_write(rdi = fd, rsi, rdx) / os_read(rdi, rsi, rdx) -> rax
; os_open(rdi = path, rsi = flags: 0 read, else create) -> rax, negative on failure
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

; wl_build_argv: GetCommandLineA split into argv, by win_build_argv's rule
; (spaces and tabs separate; a double quote groups), with room for OBJ_CAP
; objects. A command line that does not fit is a usage error.
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
    mov r12, rax                     ; source
    lea r13, [rel wl_args]           ; token storage
    lea r14, [rel wl_argv]
    xor r15d, r15d                   ; argc
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
.put:                                ; copy [r12] to [r13], both advance
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

putn:                       ; rsi = bytes, rdx = length, to stdout
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
    call putn
.nl:
    lea rdi, [rel m_nl]
    call puts
.x: mov edi, 1
    call os_exit

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

; is_vitti(rdi = name, rdx = length) -> rax = 1 when it starts "vitti:"
is_vitti:
    xor eax, eax
    cmp rdx, 6
    jb .d
    push rdx
    lea rsi, [rel s_vitti]
    mov edx, 6
    mov ecx, 6
    call names_equal
    pop rdx
.d: ret

; ---------------------------------------------------------------- read
; read_object(rbx = object record, path in [rbx]): the file into in_buf, checked
read_object:
    push r12
    push r13
    push r14
    mov rdi, [rbx]
    xor esi, esi                    ; read
    xor edx, edx
    call os_open
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
    call os_read
    test rax, rax
    js .open_fail
    jz .eof
    add r13, rax
    jmp .rd
.eof:
    mov rdi, [rel fd]
    call os_close
    add [rel in_used], r13
    ; header: magic, code size, symbol count, relocation count
    cmp r13, 32
    jb .bad
    xor ecx, ecx                    ; R34: this object's target
    mov rax, MAGIC
    cmp [r12], rax
    je .magic_ok
    inc ecx
    mov rax, MAGIC_W
    cmp [r12], rax
    jne .bad
.magic_ok:
    cmp qword [rel nobjs], 0        ; the first object decides; the rest agree
    jne .same
    mov [rel target_w], rcx
    jmp .target_ok
.same:
    cmp rcx, [rel target_w]
    jne .mixed
.target_ok:
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
.mixed:
    lea rdi, [rel m_mixed]
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

; find_symbol(rdi = name, rdx = length) -> rax = its entry, or 0
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
    mov r13, r12
    shl r13, 5                      ; SYM_SIZE
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
    mov rax, r13
    jmp .out
.no:
    xor eax, eax
.out:
    pop r15
    pop r14
    pop r13
    pop r12
    ret

; add_symbol(rdi = name, rdx = length, rax = value, rcx = kind). A name
; defined twice is an error.
add_symbol:
    push rax
    push rcx
    push rdi
    push rdx
    call find_symbol
    test rax, rax
    jnz .dup
    mov rax, [rel nsyms]
    cmp rax, SYM_CAP
    jae .full
    shl rax, 5
    lea rsi, [rel syms]
    add rsi, rax
    pop rdx
    pop rdi
    pop rcx
    pop rax
    mov [rsi], rdi
    mov [rsi + 8], rdx
    mov [rsi + 16], rax
    mov [rsi + 24], rcx
    inc qword [rel nsyms]
    ret
.dup:
    pop rdx
    pop rsi
    lea rdi, [rel m_dup]
    jmp fail
.full:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail

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
    jae .args
    lea rdi, [rel m_usage]
    call puts
    mov edi, 2
    call os_exit
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
    jae .runtime
    cmp r12, [rel main_obj]
    je .ord_next
    mov [rdi + rcx*8], r12
    inc rcx
.ord_next:
    inc r12
    jmp .ord
.runtime:
    ; R34: a PE's runtime blob sits just before the code; its two entries
    cmp qword [rel target_w], 0
    je .lay
    lea rdi, [rel s_rt_init]
    mov edx, 7
    mov rax, RT_INIT_OFF - RT_BLOB_LEN
    mov ecx, KIND_CODE
    call add_symbol
    lea rdi, [rel s_rt_sys]
    mov edx, 10
    mov rax, RT_SYSCALL_OFF - RT_BLOB_LEN
    mov ecx, KIND_CODE
    call add_symbol
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
    ; R34: a PE object's data - 8 bytes for each vitti it holds - follows the
    ; data of the objects before it in .data
    mov rax, [rel data_size]
    mov [rbx + 64], rax             ; data base
    mov qword [rbx + 72], 0         ; data size
    cmp qword [rel target_w], 0
    je .syms_go
    mov r13, [rbx + 24]
    mov r14, [rbx + 32]
.dcount:
    test r14, r14
    jz .dcounted
    lea rdi, [r13 + 16]
    mov rdx, [r13 + 8]
    call is_vitti
    test rax, rax
    jz .dnext
    add qword [rbx + 72], 8
.dnext:
    mov rax, [r13 + 8]
    lea r13, [r13 + 16 + rax]
    dec r14
    jmp .dcount
.dcounted:
    mov rax, [rbx + 72]
    add rax, [rel data_size]
    cmp rax, RT_GLOBAL_BYTES
    ja .gfull
    mov [rel data_size], rax
.syms_go:
    ; symbols
    mov r13, [rbx + 24]
    mov r14, [rbx + 32]
.sym:
    test r14, r14
    jz .lay_next
    lea rdi, [r13 + 16]
    mov rdx, [r13 + 8]
    mov rax, [r13]
    add rax, [rbx + 56]             ; a code symbol: its offset in the output
    mov ecx, KIND_CODE
    cmp qword [rel target_w], 0
    je .sym_add
    call is_vitti
    test rax, rax
    jz .sym_code
    mov rax, [r13]                  ; a PE vitti: inside its object's data
    lea rcx, [rax + 8]
    cmp rcx, [rbx + 72]
    ja .bad_obj
    test al, 7
    jnz .bad_obj
    add rax, [rbx + 64]
    mov ecx, KIND_DATA
    lea rdi, [r13 + 16]
    mov rdx, [r13 + 8]
    jmp .sym_add
.sym_code:
    mov rax, [r13]
    add rax, [rbx + 56]
    mov ecx, KIND_CODE
.sym_add:
    call add_symbol
    mov rax, [r13 + 8]
    lea r13, [r13 + 16 + rax]
    dec r14
    jmp .sym
.lay_next:
    inc r12
    jmp .lay_l
.relocate:
    ; R34: in a PE, .data starts at the next page after [blob][code]; this is
    ; its distance from the start of the code, as the compiler's r56 computes
    mov r15, [rel out_size]
    add r15, RT_BLOB_LEN + 0xFFF
    and r15, -0x1000
    sub r15, RT_BLOB_LEN
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
    test rax, rax
    jz .undef
    mov rcx, [rax + 24]             ; kind
    mov rax, [rax + 16]             ; value
    cmp rcx, KIND_DATA
    jne .target
    add rax, r15                    ; a vitti: in .data
.target:
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
.bad_obj:
.bad_site:
    lea rdi, [rel m_bad]
    mov rsi, [rbx]
    xor edx, edx
    jmp fail
.gfull:
    lea rdi, [rel m_gfull]
    xor esi, esi
    jmp fail
.full:
    lea rdi, [rel m_full]
    xor esi, esi
    jmp fail
.write:
    mov rcx, [rel argv]
    mov rdi, [rcx + 8]              ; argv[1] = output
    mov esi, 0x241                  ; O_WRONLY|O_CREAT|O_TRUNC
    mov edx, 0o755
    call os_open
    test rax, rax
    js .out_fail
    mov [rel fd], rax
    cmp qword [rel target_w], 0
    je .write_elf
    call write_pe
    jmp .written
.write_elf:
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
    mov rdi, [rel fd]
    lea rsi, [rel hdr]
    mov edx, HEADERS_SIZE
    call os_write
    mov rdi, [rel fd]
    lea rsi, [rel out_code]
    mov rdx, [rel out_size]
    call os_write
.written:
    mov rdi, [rel fd]
    call os_close
%ifndef WINDOWS
    mov rcx, [rel argv]
    mov rdi, [rcx + 8]
    mov esi, 0o755
    mov eax, 90                     ; chmod
    syscall
%endif
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
    call os_exit
.out_fail:
    lea rdi, [rel m_open]
    mov rcx, [rel argv]
    mov rsi, [rcx + 8]
    xor edx, edx
    jmp fail

; ---------------------------------------------------------------- the PE
; write_pe: [fd] is open. Writes the PE the compiler's write_pe writes for a
; code of out_size bytes, field for field: the 512-byte headers, the runtime
; blob, the code, padding to 512, then .data (the vitti, zero, and the import
; block). tests/r34/test_link_windows.py holds the two to the same bytes.
write_pe:
    push rbx
    push r12
    push r13
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
    mov word [rdi+0x46], 2          ; RX code and RW data/imports
    mov word [rdi+0x54], 0xF0
    mov word [rdi+0x56], 0x0022
    ; Optional header
    mov word [rdi+0x58], 0x20B
    mov rax, [rel out_size]
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
    ; .data: RVA = 0x1000 + round_up(.text virtual size, 0x1000)
    mov rax, r12
    add rax, 0xFFF
    and rax, -0x1000
    add rax, 0x1000
    mov [rdi+0x17C], eax      ; .data virtual address
    add rax, 0x1000
    mov [rdi+0x90], eax       ; SizeOfImage
    mov dword [rdi+0x170], 0x7461642E  ; '.dat'
    mov word [rdi+0x174], 0x0061       ; 'a', NUL
    mov eax, RT_DATA_BYTES
    mov [rdi+0x178], eax      ; .data virtual size
    add rax, 0x1FF
    and rax, -0x200
    mov [rdi+0x180], eax      ; aligned .data raw size
    mov [rdi+0x60], eax       ; SizeOfInitializedData
    mov eax, r13d
    add eax, 0x200
    mov [rdi+0x184], eax      ; .data raw pointer after .text
    mov dword [rdi+0x194], 0xC0000040  ; initialized, read/write
    mov eax, [rdi+0x17C]
    add eax, RT_GLOBAL_BYTES
    mov [rdi+0xD0], eax
    mov dword [rdi+0xD4], 40
    add eax, RT_IAT_OFF
    mov [rdi+0x128], eax
    mov dword [rdi+0x12C], 88
    sub eax, RT_IAT_OFF
    call pe_prepare_imports
    ; headers, blob, code
    mov rdi, [rel fd]
    lea rsi, [rel pe_hdr]
    mov edx, 0x200
    call os_write
    mov rdi, [rel fd]
    lea rsi, [rel rt_blob]
    mov edx, RT_BLOB_LEN
    call os_write
    mov rdi, [rel fd]
    lea rsi, [rel out_code]
    mov rdx, [rel out_size]
    call os_write
    ; pad to file alignment, then .data's vitti: all zero
    mov r12, r13
    sub r12, [rel out_size]
    sub r12, RT_BLOB_LEN
    add r12, RT_GLOBAL_BYTES
.pad:
    test r12, r12
    jle .imports
    mov rdx, r12
    cmp rdx, 0x100
    jbe .pad_go
    mov edx, 0x100
.pad_go:
    push rdx
    push rdx
    mov rdi, [rel fd]
    lea rsi, [rel pe_pad]
    call os_write
    pop rdx
    pop rdx
    sub r12, rdx
    jmp .pad
.imports:
    mov rdi, [rel fd]
    lea rsi, [rel pe_import_output]
    mov edx, RT_IMPORT_BYTES
    call os_write
    pop r13
    pop r12
    pop rbx
    ret

; The compiler's PE import template, with its parity: the compiler places it
; one byte past a 16-byte boundary (R28_PE_PAD), and its `align 2` entries are
; absolute, so the bytes it writes depend on that.
section .data
    align 16, db 0
    db 0
section .text
%include "win/pe_imports.inc"
%include "win/rtblob.inc"
