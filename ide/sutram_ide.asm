; ============================================================
; Sutram IDE (सूत्रम्) — a zero-dependency full-screen editor + runner
; ------------------------------------------------------------
; Pure NASM x86-64, Linux. No runtime, no Python, no toolkit, no dependencies.
; Standalone: does NOT touch src/sutram_compiler.asm.
;
;   nasm -f elf64 ide/sutram_ide.asm -o /tmp/ide.o && ld -o sutram-ide /tmp/ide.o
;   ./sutram-ide examples/01_hello.sm
;
; Keys:
;   printable        insert
;   Enter            newline
;   Backspace/Del    delete before cursor
;   Arrows/Home/End  move
;   Ctrl-S           save
;   Ctrl-R           run (compile + execute; output shown in the pane)
;   Ctrl-L           load a file (prompt on the status line)
;   Ctrl-Q           quit
;
; Screen layout:
;   row 1            title bar
;   rows 2..R-6      text (with line numbers + syntax highlighting)
;   row R-5          output pane header
;   rows R-4..R-1    program output
;   row R            status bar
; ============================================================
BITS 64
default rel

%define SYS_read    0
%define SYS_write   1
%define SYS_open    2
%define SYS_close   3
%define SYS_ioctl   16
%define SYS_fork    57
%define SYS_execve  59
%define SYS_wait4   61
%define SYS_getdents64 217
%define SYS_exit    60

%define TCGETS      0x5401
%define TCSETS      0x5402
%define TIOCGWINSZ  0x5413
%define ICANON      0x0002
%define ECHO        0x0008
%define ISIG        0x0001
%define IXON        0x0400

%define BUF_CAP     65536
%define UNDO_CAP    4096
%define OUT_CAP     8192
%define PATH_CAP    256

; ------------------------------------------------------------
section .bss
    term_orig   resb 64
    term_raw    resb 64
    winsz       resb 8
    rows        resq 1
    cols        resq 1
    keybuf      resb 8

    buf         resb BUF_CAP
    buf_len     resq 1
    cur         resq 1

    ; ---- undo log (Ctrl-Z) ----
    undo_op     resq UNDO_CAP       ; 1 = a byte was inserted, 2 = a byte was deleted
    undo_pos    resq UNDO_CAP       ; where it happened
    undo_byte   resb UNDO_CAP       ; which byte
    undo_sp     resq 1              ; entries recorded so far

    path        resb PATH_CAP
    path_len    resq 1
    dirty       resq 1

    outbuf      resb OUT_CAP
    out_len     resq 1

    inbuf       resb PATH_CAP
    dirbuf      resb 8192
    ex_index    resq 1

    ; ---- interactive shell pane (the other half of IDLE) ----
    shell_mode  resq 1              ; 0 = edit, 1 = shell
    shell_line  resb 512            ; the line being typed
    shell_len   resq 1
    shell_sess  resb 4096           ; accumulated statements
    sess_len    resq 1
    cmd_src     resb 8192           ; wrapped program handed to the compiler
    shell_tmp   resb 2
    itoa_buf    resb 32

    cmd_buf     resb 512
    argv_run    resq 4

; ------------------------------------------------------------
section .data
    ; escape / control strings
    s_alt_on     db 27,'[?1049h',0
    s_alt_off    db 27,'[?1049l',0
    s_home       db 27,'[H',0
    s_clear      db 27,'[2J',0
    s_clrline    db 27,'[K',0
    s_cur_off    db 27,'[?25l',0
    s_cur_on     db 27,'[?25h',0
    s_reset      db 27,'[0m',0
    s_title      db 27,'[44;97m',0
    s_lineno     db 27,'[90m',0
    s_keyw       db 27,'[95m',0
    s_str        db 27,'[92m',0
    s_comm       db 27,'[90m',0
    s_num        db 27,'[96m',0
    s_status     db 27,'[7m',0
    s_esc_row    db 27,'[',0
    s_semi       db ';',0
    s_H          db 'H',0

    s_banner     db " Sutram IDE - the complete thread", 0
    s_keys       db "  Ctrl-R Run  Ctrl-S Save  Ctrl-Z Undo  Ctrl-L Load  Ctrl-E Examples  Ctrl-T Shell  Ctrl-Q Quit ", 0
    s_outtitle   db " Output", 0
    s_modified   db " [modified]", 0
    s_pad6       db "      ", 0
    s_prompt     db "sutram> ", 0
    s_exdir      db "examples", 0
    s_shellhdr   db " Shell", 0
    s_shellhelp  db "  Enter Run  Ctrl-T Back to editor  Ctrl-Q Quit ", 0
    s_mukhya_br  db "mukhya() {", 10, 0
    s_close_br   db 10, "}", 10, 0
    s_exprefix   db "examples/", 0
    s_dotsm      db ".sm", 0
    s_default    db "untitled.sm", 0
    s_slash_sh   db "/bin/sh", 0
    s_sh         db "sh", 0
    s_dashc      db "-c", 0
    s_cmd_a      db 'C=./sutram_compiler; [ -x "$C" ] || C=sutram; "$C" ', 0
    s_cmd_b      db " /tmp/.sutram_ide.bin > /tmp/.sutram_ide.out 2>&1 && /tmp/.sutram_ide.bin >> /tmp/.sutram_ide.out 2>&1", 0
    s_tmp_sm     db "/tmp/.sutram_ide.sm", 0
    s_tmp_out    db "/tmp/.sutram_ide.out", 0

    ; keyword table
    kw_count     dq 31
    kw_0  db "mukhya",0
    kw_1  db "vitti",0
    kw_2  db "anka",0
    kw_3  db "yadi",0
    kw_4  db "anyatra",0
    kw_5  db "yavat",0
    kw_6  db "punaravartana",0
    kw_7  db "pratiyati",0
    kw_8  db "prakriya",0
    kw_9  db "likha",0
    kw_10 db "purna",0
    kw_11 db "shunya",0
    kw_12 db "sutra",0
    kw_13 db "krama",0
    kw_14 db "uddeshya",0
    kw_15 db "guna",0
    kw_16 db "bhavana",0
    kw_17 db "pankti",0
    kw_18 db "srijana",0
    kw_19 db "nishedha",0
    kw_20 db "rachana",0
    kw_21 db "ayojan",0
    kw_22 db "parigrah",0
    kw_23 db "grahan",0
    kw_24 db "to",0
    kw_25 db "shabda",0
    kw_26 db "dasham",0
    kw_27 db "kosh",0
    kw_28 db "kuru",0
    kw_29 db "nishkriya",0
    kw_30 db "sankhya",0
    kw_ptrs:
    dq kw_0, kw_1, kw_2, kw_3, kw_4, kw_5, kw_6, kw_7, kw_8, kw_9
    dq kw_10, kw_11, kw_12, kw_13, kw_14, kw_15, kw_16, kw_17, kw_18, kw_19
    dq kw_20, kw_21, kw_22, kw_23, kw_24, kw_25, kw_26, kw_27, kw_28, kw_29, kw_30

; ------------------------------------------------------------
section .text
global _start

; ---- strlen: rdi -> rax ----
strlen:
    xor rax, rax
.l: cmp byte [rdi+rax], 0
    je .d
    inc rax
    jmp .l
.d: ret

; ---- write_str: rsi=ptr, rdx=len ----
write_str:
    mov rax, SYS_write
    mov rdi, 1
    syscall
    ret

; ---- write_z: rsi=NUL-terminated ----
write_z:
    push rsi
    mov rdi, rsi
    call strlen
    mov rdx, rax
    pop rsi
    mov rax, SYS_write
    mov rdi, 1
    syscall
    ret

; ---- itoa: rdi=value -> rsi=ptr, rdx=len (buffer itoa_buf) ----
itoa:
    mov rax, rdi
    lea rsi, [itoa_buf+31]
    mov byte [rsi], 0
    mov rcx, 10
    xor r8, r8
    test rax, rax
    jns .pos
    mov r8, 1
    neg rax
.pos:
    dec rsi
    xor rdx, rdx
    div rcx
    add dl, '0'
    mov [rsi], dl
    test rax, rax
    jnz .pos
    test r8, r8
    jz .done
    dec rsi
    mov byte [rsi], '-'
.done:
    lea rdx, [itoa_buf+31]
    sub rdx, rsi
    ret

; ---- emit_cursor: rdi=row, rsi=col ----
emit_cursor:
    push rdi
    push rsi
    mov rsi, s_esc_row
    call write_z
    pop rsi
    pop rdi
    push rsi
    call itoa
    call write_str
    mov rsi, s_semi
    call write_z
    pop rdi
    call itoa
    call write_str
    mov rsi, s_H
    call write_z
    ret

; ---- clear_screen ----
clear_screen:
    mov rsi, s_home
    call write_z
    mov rsi, s_clear
    call write_z
    ret

; ---- set_raw ----
set_raw:
    mov rax, SYS_ioctl
    mov rdi, 0
    mov rsi, TCGETS
    lea rdx, [term_orig]
    syscall
    lea rsi, [term_orig]
    lea rdi, [term_raw]
    mov rcx, 8
.cp:
    mov rax, [rsi]
    mov [rdi], rax
    add rsi, 8
    add rdi, 8
    dec rcx
    jnz .cp
    mov eax, [term_raw+12]
    and eax, ~(ICANON|ECHO|ISIG)
    mov [term_raw+12], eax
    mov eax, [term_raw+0]
    and eax, ~IXON
    mov [term_raw+0], eax
    mov byte [term_raw+22], 0     ; VTIME
    mov byte [term_raw+23], 1     ; VMIN
    mov rax, SYS_ioctl
    mov rdi, 0
    mov rsi, TCSETS
    lea rdx, [term_raw]
    syscall
    ret

; ---- restore_term ----
restore_term:
    mov rax, SYS_ioctl
    mov rdi, 0
    mov rsi, TCSETS
    lea rdx, [term_orig]
    syscall
    ret

; ---- get_winsize ----
get_winsize:
    mov rax, SYS_ioctl
    mov rdi, 0
    mov rsi, TIOCGWINSZ
    lea rdx, [winsz]
    syscall
    movzx rax, word [winsz+2]
    mov [cols], rax
    movzx rax, word [winsz]
    mov [rows], rax
    cmp qword [rows], 10
    jae .r
    mov qword [rows], 24
.r: cmp qword [cols], 40
    jae .c
    mov qword [cols], 80
.c: ret

; ---- text_rows -> rax ----
text_rows:
    mov rax, [rows]
    sub rax, 7
    cmp rax, 1
    jae .ok
    mov rax, 1
.ok: ret

; ---- line_of: rdi=offset -> rax=line, rdx=col ----
line_of:
    xor rax, rax
    xor rdx, rdx
    xor rcx, rcx
.l: cmp rcx, rdi
    jae .d
    mov r8b, [buf+rcx]
    cmp r8b, 10
    jne .n
    inc rax
    xor rdx, rdx
    jmp .nx
.n: inc rdx
.nx:
    inc rcx
    jmp .l
.d: ret

; ---- line_start: rdi=line -> rax=offset ----
line_start:
    xor rax, rax
    xor rcx, rcx
    test rdi, rdi
    jz .ret0
.l: cmp rcx, [buf_len]
    jae .end
    cmp byte [buf+rcx], 10
    jne .n
    inc rax
    cmp rax, rdi
    je .after
.n: inc rcx
    jmp .l
.after:
    lea rax, [rcx+1]
    ret
.end:
    mov rax, [buf_len]
    ret
.ret0:
    xor rax, rax
    ret

; ---- is_keyword: rsi=word, rdx=len -> rax=1/0 ----
is_keyword:
    push rbx
    push r12
    push r13
    push r14
    mov rbx, rsi
    mov r12, rdx
    lea r13, [kw_ptrs]
    xor r14, r14
.loop:
    cmp r14, [kw_count]
    jae .no
    mov rdi, [r13+r14*8]
    push rdi
    call strlen
    pop rdi
    cmp rax, r12
    jne .next
    xor r8, r8
.bc:
    cmp r8, r12
    jae .yes
    mov al, [rdi+r8]
    cmp al, [rbx+r8]
    jne .next
    inc r8
    jmp .bc
.next:
    inc r14
    jmp .loop
.no:
    xor rax, rax
    jmp .done
.yes:
    mov rax, 1
.done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ---- emit_byte_color: dil=byte, rsi=colour string ----
emit_byte_color:
    push rdi
    mov rsi, rsi
    call write_z
    pop rdi
    mov [keybuf], dil
    mov rsi, keybuf
    mov rdx, 1
    call write_str
    mov rsi, s_reset
    call write_z
    ret

; ============================================================
; render
; ============================================================
render:
    cmp qword [shell_mode], 0
    jne render_shell
    call get_winsize
    call clear_screen

    ; --- title ---
    mov rdi, 1
    mov rsi, 1
    call emit_cursor
    mov rsi, s_title
    call write_z
    mov rsi, s_banner
    call write_z
    mov rsi, s_reset
    call write_z

    call text_rows
    mov r13, rax                ; text rows available
    xor r15, r15                ; line index
    mov r14, 2                  ; screen row

.tr_loop:
    cmp r15, r13
    jae .tr_done
    ; stop once past the last real line
    mov rdi, r15
    call line_start
    cmp rax, [buf_len]
    jae .tr_done
    mov rdi, r14
    mov rsi, 1
    call emit_cursor

    ; line number
    mov rsi, s_lineno
    call write_z
    mov rdi, r15
    inc rdi
    call itoa
    call write_str
    mov rsi, s_reset
    call write_z
    mov rsi, s_pad6
    call write_z

    ; line content with highlighting
    mov rdi, r15
    call line_start
    mov rbx, rax
    xor r9, r9                  ; 0 normal, 1 string, 2 comment
.chars:
    cmp rbx, [buf_len]
    jae .eol
    mov al, [buf+rbx]
    cmp al, 10
    je .eol
    cmp al, 13
    je .adv
    cmp r9, 2
    je .cmt
    cmp al, '#'
    jne .cstr
    mov r9, 2
    jmp .cmt
.cstr:
    cmp al, '"'
    jne .cword
    cmp r9, 1
    jne .open
    xor r9, r9
    jmp .str
.open:
    mov r9, 1
.str:
    movzx rdi, al
    mov rsi, s_str
    call emit_byte_color
    jmp .adv
.cmt:
    movzx rdi, al
    mov rsi, s_comm
    call emit_byte_color
    jmp .adv
.cword:
    mov al, [buf+rbx]
    cmp al, 'a'
    jb .cu
    cmp al, 'z'
    jbe .word
.cu:
    cmp al, 'A'
    jb .cd
    cmp al, 'Z'
    jbe .word
.cd:
    cmp al, '0'
    jb .plain
    cmp al, '9'
    jbe .num
    jmp .plain
.word:
    mov r10, rbx
.ws:
    cmp r10, [buf_len]
    jae .wd
    mov al, [buf+r10]
    cmp al, 'a'
    jb .wu
    cmp al, 'z'
    jbe .wn
.wu:
    cmp al, 'A'
    jb .wdg
    cmp al, 'Z'
    jbe .wn
.wdg:
    cmp al, '0'
    jb .wd
    cmp al, '9'
    jbe .wn
    cmp al, '_'
    je .wn
    jmp .wd
.wn:
    inc r10
    jmp .ws
.wd:
    lea rsi, [buf+rbx]
    mov rdx, r10
    sub rdx, rbx
    push rbx
    push r10
    call is_keyword
    pop r10
    pop rbx
    test rax, rax
    jz .wplain
    mov rsi, s_keyw
    jmp .wemit
.wplain:
    mov rsi, s_reset
.wemit:
    call write_z
.wloop:
    cmp rbx, r10
    jae .wdone
    mov al, [buf+rbx]
    mov [keybuf], al
    push rbx
    push r10
    mov rsi, keybuf
    mov rdx, 1
    call write_str
    pop r10
    pop rbx
    inc rbx
    jmp .wloop
.wdone:
    mov rsi, s_reset
    call write_z
    mov rbx, r10
    jmp .chars
.num:
    mov r10, rbx
.ns:
    cmp r10, [buf_len]
    jae .nd
    mov al, [buf+r10]
    cmp al, '0'
    jb .nd
    cmp al, '9'
    ja .nd
    inc r10
    jmp .ns
.nd:
    mov rsi, s_num
    call write_z
.nlm:
    cmp rbx, r10
    jae .ndone
    mov al, [buf+rbx]
    mov [keybuf], al
    push rbx
    push r10
    mov rsi, keybuf
    mov rdx, 1
    call write_str
    pop r10
    pop rbx
    inc rbx
    jmp .nlm
.ndone:
    mov rsi, s_reset
    call write_z
    mov rbx, r10
    jmp .chars
.plain:
    mov al, [buf+rbx]
    mov [keybuf], al
    mov rsi, keybuf
    mov rdx, 1
    call write_str
.adv:
    inc rbx
    jmp .chars
.eol:
    mov rsi, s_reset
    call write_z
    mov rsi, s_clrline
    call write_z
    inc r15
    inc r14
    jmp .tr_loop
.tr_done:

    ; --- output header ---
    mov rdi, [rows]
    sub rdi, 5
    mov rsi, 1
    call emit_cursor
    mov rsi, s_status
    call write_z
    mov rsi, s_outtitle
    call write_z
    mov rsi, s_clrline
    call write_z
    mov rsi, s_reset
    call write_z

    ; --- output body ---
    mov rbx, 0
    mov r14, [rows]
    sub r14, 4
    mov r13, 4
    xor r15, r15
.op:
    cmp r15, r13
    jae .op_done
    mov rdi, r14
    mov rsi, 1
    call emit_cursor
.opc:
    cmp rbx, [out_len]
    jae .ope
    mov al, [outbuf+rbx]
    cmp al, 10
    je .opn
    mov [keybuf], al
    mov rsi, keybuf
    mov rdx, 1
    call write_str
    inc rbx
    jmp .opc
.opn:
    inc rbx
.ope:
    mov rsi, s_clrline
    call write_z
    inc r15
    inc r14
    cmp rbx, [out_len]
    jae .op_done
    jmp .op
.op_done:

    ; --- status bar ---
    mov rdi, [rows]
    mov rsi, 1
    call emit_cursor
    mov rsi, s_status
    call write_z
    lea rsi, [path]
    call write_z
    cmp qword [dirty], 0
    je .nomod
    mov rsi, s_modified
    call write_z
.nomod:
    mov rsi, s_keys
    call write_z
    mov rsi, s_reset
    call write_z
    mov rsi, s_clrline
    call write_z

    ; --- cursor ---
    call text_rows
    mov r13, rax
    mov rdi, [cur]
    call line_of
    cmp rax, r13
    jb .crok
    mov rax, r13
    dec rax
.crok:
    add rax, 2
    add rdx, 6
    mov rdi, rax
    mov rsi, rdx
    call emit_cursor
    ret

; ============================================================
; render_shell — the interactive pane
; ============================================================
render_shell:
    call get_winsize
    call clear_screen

    ; title
    mov rdi, 1
    mov rsi, 1
    call emit_cursor
    mov rsi, s_title
    call write_z
    mov rsi, s_banner
    call write_z
    mov rsi, s_reset
    call write_z

    ; " Shell" header on row 3
    mov rdi, 3
    mov rsi, 1
    call emit_cursor
    mov rsi, s_status
    call write_z
    mov rsi, s_shellhdr
    call write_z
    mov rsi, s_clrline
    call write_z
    mov rsi, s_reset
    call write_z

    ; session output, rows 4..rows-4
    mov rbx, 0
    mov r14, 4
    mov r13, [rows]
    sub r13, 8                  ; how many rows for output
    xor r15, r15
.op:
    cmp r15, r13
    jae .op_done
    mov rdi, r14
    mov rsi, 1
    call emit_cursor
.opc:
    cmp rbx, [out_len]
    jae .ope
    mov al, [outbuf+rbx]
    cmp al, 10
    je .opn
    mov [keybuf], al
    mov rsi, keybuf
    mov rdx, 1
    call write_str
    inc rbx
    jmp .opc
.opn:
    inc rbx
.ope:
    mov rsi, s_clrline
    call write_z
    inc r15
    inc r14
    cmp rbx, [out_len]
    jae .op_done
    jmp .op
.op_done:

    ; the prompt line, on the second-to-last row
    mov rdi, [rows]
    dec rdi
    mov rsi, 1
    call emit_cursor
    mov rsi, s_prompt
    call write_z
    ; the typed line
    xor rcx, rcx
.pl:
    cmp rcx, [shell_len]
    jae .pld
    mov al, [shell_line+rcx]
    mov [keybuf], al
    push rcx
    mov rsi, keybuf
    mov rdx, 1
    call write_str
    pop rcx
    inc rcx
    jmp .pl
.pld:
    mov rsi, s_clrline
    call write_z

    ; status bar
    mov rdi, [rows]
    mov rsi, 1
    call emit_cursor
    mov rsi, s_status
    call write_z
    mov rsi, s_shellhelp
    call write_z
    mov rsi, s_reset
    call write_z
    mov rsi, s_clrline
    call write_z

    ; leave the cursor after the typed text
    mov rdi, [rows]
    dec rdi
    mov rsi, [shell_len]
    add rsi, 9                  ; past "sutram> "
    call emit_cursor
    ret

; ============================================================
; editing
; ============================================================
; insert_byte: dil=byte
insert_byte:
    mov rax, [buf_len]
    cmp rax, BUF_CAP-1
    jae .done
    ; record for undo: a byte is about to be inserted at cur
    push rdi
    movzx rdx, dil
    mov rdi, 1
    mov rsi, [cur]
    call undo_push
    pop rdi
    mov rcx, [buf_len]
.sh:
    cmp rcx, [cur]
    jbe .shd
    mov al, [buf+rcx-1]
    mov [buf+rcx], al
    dec rcx
    jmp .sh
.shd:
    mov rax, [cur]
    mov [buf+rax], dil
    inc qword [buf_len]
    inc qword [cur]
    mov qword [dirty], 1
.done: ret

; delete_before
delete_before:
    cmp qword [cur], 0
    jbe .done
    ; record for undo: the byte at cur-1 is about to be removed
    mov rsi, [cur]
    dec rsi
    movzx rdx, byte [buf+rsi]
    mov rdi, 2
    call undo_push
    mov rcx, [cur]
    dec rcx
.sh:
    cmp rcx, [buf_len]
    jae .shd
    mov al, [buf+rcx+1]
    mov [buf+rcx], al
    inc rcx
    jmp .sh
.shd:
    dec qword [buf_len]
    dec qword [cur]
    mov qword [dirty], 1
.done: ret

; undo_push: rdi=op (1=inserted, 2=deleted), rsi=pos, rdx=byte
undo_push:
    mov rax, [undo_sp]
    cmp rax, UNDO_CAP
    jae .full
    mov [undo_op + rax*8], rdi
    mov [undo_pos + rax*8], rsi
    mov [undo_byte + rax], dl
    inc qword [undo_sp]
.full: ret

; undo_do: step back one recorded edit
undo_do:
    mov rax, [undo_sp]
    test rax, rax
    jz .none
    dec rax
    mov [undo_sp], rax
    mov rdi, [undo_op + rax*8]
    mov rsi, [undo_pos + rax*8]
    movzx rdx, byte [undo_byte + rax]
    cmp rdi, 1
    je .uninsert
    ; op 2: a byte was deleted at pos - put it back
    mov rcx, [buf_len]
.rsh:
    cmp rcx, rsi
    jbe .rwr
    mov al, [buf+rcx-1]
    mov [buf+rcx], al
    dec rcx
    jmp .rsh
.rwr:
    mov [buf+rsi], dl
    inc qword [buf_len]
    mov [cur], rsi
    mov qword [dirty], 1
    ret
.uninsert:
    ; op 1: a byte was inserted at pos - remove it
    mov rcx, rsi
.lsh:
    cmp rcx, [buf_len]
    jae .ldone
    mov al, [buf+rcx+1]
    mov [buf+rcx], al
    inc rcx
    jmp .lsh
.ldone:
    dec qword [buf_len]
    mov [cur], rsi
    mov qword [dirty], 1
.none: ret

; clamp_col
clamp_col:
    mov rcx, [cur]
.c: cmp rcx, [buf_len]
    jae .set
    cmp byte [buf+rcx], 10
    je .set
    inc rcx
    jmp .c
.set:
    mov [cur], rcx
    ret

; move_up
move_up:
    mov rdi, [cur]
    call line_of
    test rax, rax
    jz .done
    push rdx
    dec rax
    mov rdi, rax
    call line_start
    pop rdx
    add rax, rdx
    mov [cur], rax
    call clamp_col
.done: ret

; move_down
move_down:
    mov rdi, [cur]
    call line_of
    push rdx
    inc rax
    mov rdi, rax
    call line_start
    cmp rax, [buf_len]
    jae .restore
    pop rdx
    add rax, rdx
    mov [cur], rax
    call clamp_col
    ret
.restore:
    pop rdx
    ret

; move_left
move_left:
    cmp qword [cur], 0
    jbe .d
    dec qword [cur]
.d: ret

; move_right
move_right:
    mov rax, [cur]
    cmp rax, [buf_len]
    jae .d
    inc qword [cur]
.d: ret

; home
home_key:
    mov rdi, [cur]
    call line_of
    mov rdi, rax
    call line_start
    mov [cur], rax
    ret

; end
end_key:
    mov rdi, [cur]
    call line_of
    mov rdi, rax
    call line_start
    mov rcx, rax
.e: cmp rcx, [buf_len]
    jae .set
    cmp byte [buf+rcx], 10
    je .set
    inc rcx
    jmp .e
.set:
    mov [cur], rcx
    ret

; ============================================================
; file I/O
; ============================================================
load_file:
    mov rax, SYS_open
    lea rdi, [path]
    xor rsi, rsi
    xor rdx, rdx
    syscall
    cmp rax, 0
    jl .fail
    mov r12, rax
    mov rax, SYS_read
    mov rdi, r12
    lea rsi, [buf]
    mov rdx, BUF_CAP-1
    syscall
    cmp rax, 0
    jl .close
    mov [buf_len], rax
    mov qword [cur], 0
    mov qword [dirty], 0
    mov qword [undo_sp], 0        ; a fresh file has no history
.close:
    mov rax, SYS_close
    mov rdi, r12
    syscall
    ret
.fail:
    mov qword [buf_len], 0
    mov qword [cur], 0
    ret

save_file:
    mov rax, SYS_open
    lea rdi, [path]
    mov rsi, 0x241
    mov rdx, 0644o
    syscall
    cmp rax, 0
    jl .done
    mov r12, rax
    mov rax, SYS_write
    mov rdi, r12
    lea rsi, [buf]
    mov rdx, [buf_len]
    syscall
    mov rax, SYS_close
    mov rdi, r12
    syscall
    mov qword [dirty], 0
.done: ret

write_temp_sm:
    mov rax, SYS_open
    lea rdi, [s_tmp_sm]
    mov rsi, 0x241
    mov rdx, 0644o
    syscall
    cmp rax, 0
    jl .done
    mov r12, rax
    mov rax, SYS_write
    mov rdi, r12
    lea rsi, [buf]
    mov rdx, [buf_len]
    syscall
    mov rax, SYS_close
    mov rdi, r12
    syscall
.done: ret

read_temp_out:
    mov qword [out_len], 0
    mov rax, SYS_open
    lea rdi, [s_tmp_out]
    xor rsi, rsi
    xor rdx, rdx
    syscall
    cmp rax, 0
    jl .done
    mov r12, rax
    mov rax, SYS_read
    mov rdi, r12
    lea rsi, [outbuf]
    mov rdx, OUT_CAP-1
    syscall
    cmp rax, 0
    jl .close
    mov [out_len], rax
.close:
    mov rax, SYS_close
    mov rdi, r12
    syscall
.done: ret

; ============================================================
; run: compile + execute the buffer
; ============================================================
run_program:
    call write_temp_sm
    mov rax, SYS_fork
    syscall
    cmp rax, 0
    jl .done
    jne .parent
    lea rdi, [s_slash_sh]
    lea rsi, [argv_run]
    xor rdx, rdx
    mov rax, SYS_execve
    syscall
    mov rax, SYS_exit
    mov rdi, 1
    syscall
.parent:
    mov r12, rax
    mov rax, SYS_wait4
    mov rdi, r12
    xor rsi, rsi
    xor rdx, rdx
    xor r10, r10
    syscall
    call read_temp_out
.done: ret

; build the shell command + argv
build_cmd:
    lea rdi, [cmd_buf]
    lea rsi, [s_cmd_a]
    call scat
    lea rdi, [cmd_buf]
    lea rsi, [s_tmp_sm]
    call scat
    lea rdi, [cmd_buf]
    lea rsi, [s_cmd_b]
    call scat
    lea rax, [s_sh]
    mov [argv_run], rax
    lea rax, [s_dashc]
    mov [argv_run+8], rax
    lea rax, [cmd_buf]
    mov [argv_run+16], rax
    mov qword [argv_run+24], 0
    ret

; scat: rdi=dst base, rsi=src -> append src at the end of dst
scat:
    push rsi
.fe: cmp byte [rdi], 0
    je .cp
    inc rdi
    jmp .fe
.cp:
    pop rsi
.l: mov al, [rsi]
    mov [rdi], al
    inc rdi
    inc rsi
    test al, al
    jnz .l
    ret

; ============================================================
; load prompt
; ============================================================
load_prompt:
    mov rdi, [rows]
    mov rsi, 1
    call emit_cursor
    mov rsi, s_status
    call write_z
    mov rsi, s_prompt
    call write_z
    mov rsi, s_reset
    call write_z
    mov rsi, s_clrline
    call write_z
    xor r12, r12
.loop:
    mov rax, SYS_read
    mov rdi, 0
    lea rsi, [keybuf]
    mov rdx, 1
    syscall
    cmp rax, 1
    jne .done
    mov al, [keybuf]
    cmp al, 10
    je .finish
    cmp al, 13
    je .finish
    cmp al, 127
    je .back
    cmp al, 8
    je .back
    cmp r12, PATH_CAP-1
    jae .loop
    mov [inbuf+r12], al
    inc r12
    mov rsi, keybuf
    mov rdx, 1
    call write_str
    jmp .loop
.back:
    test r12, r12
    jz .loop
    dec r12
    jmp .loop
.finish:
    mov byte [inbuf+r12], 0
    test r12, r12
    jz .done
    xor rcx, rcx
.cp:
    cmp rcx, r12
    jae .cpd
    mov al, [inbuf+rcx]
    mov [path+rcx], al
    inc rcx
    jmp .cp
.cpd:
    mov byte [path+rcx], 0
    mov [path_len], rcx
    call load_file
.done: ret

; ============================================================
; interactive shell pane (Ctrl-T)
; ============================================================
; append_shell_char: dil = byte
append_shell_char:
    cmp qword [shell_len], 500
    jae .d
    mov rax, [shell_len]
    mov [shell_line+rax], dil
    inc qword [shell_len]
.d: ret

back_shell_char:
    cmp qword [shell_len], 0
    jbe .d
    dec qword [shell_len]
.d: ret

; append the current line to the session (plus a newline)
commit_shell_line:
    cmp qword [sess_len], 3900
    jae .skip
    mov rcx, 0
.c: cmp rcx, [shell_len]
    jae .nl
    mov rax, [sess_len]
    mov rdx, [shell_line+rcx]
    mov [shell_sess+rax], dl
    inc qword [sess_len]
    inc rcx
    jmp .c
.nl:
    mov rax, [sess_len]
    mov byte [shell_sess+rax], 10
    inc qword [sess_len]
.skip:
    mov qword [shell_len], 0
    ret

; build "mukhya() {\n<session>\n}\n" into cmd_src and return its length in rax
build_shell_program:
    mov byte [cmd_src], 0       ; scat appends — clear it first
    lea rdi, [cmd_src]
    lea rsi, [s_mukhya_br]
    call scat
    ; session body
    mov rcx, 0
.b: cmp rcx, [sess_len]
    jae .close
    lea rdi, [cmd_src]
    mov rax, [cmd_src]        ; (unused; scat re-derives the end)
    mov rdx, [shell_sess+rcx]
    mov [shell_tmp], dl
    lea rsi, [shell_tmp]
    call scat
    inc rcx
    jmp .b
.close:
    lea rdi, [cmd_src]
    lea rsi, [s_close_br]
    call scat
    lea rdi, [cmd_src]
    call strlen
    ret

; run the accumulated shell session
run_shell:
    call build_shell_program
    ; write cmd_src to the temp .sm
    mov rax, SYS_open
    lea rdi, [s_tmp_sm]
    mov rsi, 0x241
    mov rdx, 0644o
    syscall
    cmp rax, 0
    jl .done
    mov r12, rax
    lea rdi, [cmd_src]
    call strlen
    mov rdx, rax
    mov rax, SYS_write
    mov rdi, r12
    lea rsi, [cmd_src]
    syscall
    mov rax, SYS_close
    mov rdi, r12
    syscall
    ; fork + run the shell command (same path as Ctrl-R)
    mov rax, SYS_fork
    syscall
    cmp rax, 0
    jl .done
    jne .parent
    lea rdi, [s_slash_sh]
    lea rsi, [argv_run]
    xor rdx, rdx
    mov rax, SYS_execve
    syscall
    mov rax, SYS_exit
    mov rdi, 1
    syscall
.parent:
    mov r12, rax
    mov rax, SYS_wait4
    mov rdi, r12
    xor rsi, rsi
    xor rdx, rdx
    xor r10, r10
    syscall
    call read_temp_out
.done: ret

; shell_key: r15 = key code
shell_key:
    cmp r15, 20                 ; Ctrl-T -> back to the editor
    je .exit
    cmp r15, -1
    je .exit
    cmp r15, 3                  ; Ctrl-C -> back to the editor
    je .exit
    cmp r15, 10
    je .enter
    cmp r15, 13
    je .enter
    cmp r15, 127
    je .back
    cmp r15, 8
    je .back
    cmp r15, 32
    jb .ret
    mov rdi, r15
    call append_shell_char
    ret
.enter:
    call commit_shell_line
    call run_shell
    ret
.back:
    call back_shell_char
    ret
.exit:
    mov qword [shell_mode], 0
    ret
.ret: ret

; ============================================================
; examples browser (Ctrl-E cycles through examples/*.sm)
; ============================================================
; name_ends_sm: rsi = NUL-terminated name -> rax = 1 if it ends with ".sm"
name_ends_sm:
    push rsi
    mov rdi, rsi
    call strlen
    pop rsi
    cmp rax, 3
    jb .no
    lea rdi, [rsi+rax-3]
    cmp byte [rdi],   '.'
    jne .no
    cmp byte [rdi+1], 's'
    jne .no
    cmp byte [rdi+2], 'm'
    jne .no
    mov rax, 1
    ret
.no:
    xor rax, rax
    ret

examples_next:
    ; open examples/
    mov rax, SYS_open
    lea rdi, [s_exdir]
    xor rsi, rsi
    xor rdx, rdx
    syscall
    cmp rax, 0
    jl .fail
    mov r12, rax
    mov rax, SYS_getdents64
    mov rdi, r12
    lea rsi, [dirbuf]
    mov rdx, 8000
    syscall
    mov r13, rax
    mov rax, SYS_close
    mov rdi, r12
    syscall
    cmp r13, 0
    jle .fail
    xor r14, r14                ; offset into dirbuf
    xor r15, r15                ; .sm counter
.scan:
    cmp r14, r13
    jae .wrap
    lea rbx, [dirbuf+r14]
    movzx rcx, word [rbx+16]    ; d_reclen
    test rcx, rcx
    jz .wrap
    lea rsi, [rbx+19]           ; d_name
    push rcx
    call name_ends_sm
    pop rcx
    test rax, rax
    jz .next
    ; this is a .sm entry — is it the one we want?
    mov rax, [ex_index]
    cmp r15, rax
    je .take
    inc r15
.next:
    add r14, rcx
    jmp .scan
.take:
    ; build "examples/<name>" into path (clear it first — scat appends)
    mov byte [path], 0
    lea rdi, [path]
    lea rsi, [s_exprefix]
    call scat
    lea rdi, [path]
    lea rsi, [rbx+19]
    call scat
    lea rdi, [path]
    call strlen
    mov [path_len], rax
    call load_file
    inc qword [ex_index]
    ret
.wrap:
    ; no more entries — start over from the first
    cmp qword [ex_index], 0
    je .fail
    mov qword [ex_index], 0
    jmp examples_next
.fail:
    ret

; ============================================================
; input
; ============================================================
; strcpy_z: rdi=dst, rsi=src
strcpy_z:
    xor rcx, rcx
.c: mov al, [rsi+rcx]
    mov [rdi+rcx], al
    inc rcx
    test al, al
    jnz .c
    ret

; read_key -> r15
read_key:
    mov rax, SYS_read
    mov rdi, 0
    lea rsi, [keybuf]
    mov rdx, 1
    syscall
    cmp rax, 1
    jne .eof
    movzx r15, byte [keybuf]
    cmp r15, 27
    jne .done
    mov rax, SYS_read
    mov rdi, 0
    lea rsi, [keybuf]
    mov rdx, 1
    syscall
    cmp rax, 1
    jne .done
    cmp byte [keybuf], '['
    jne .done
    mov rax, SYS_read
    mov rdi, 0
    lea rsi, [keybuf]
    mov rdx, 1
    syscall
    cmp rax, 1
    jne .done
    mov al, [keybuf]
    cmp al, 'A'
    je .up
    cmp al, 'B'
    je .down
    cmp al, 'C'
    je .right
    cmp al, 'D'
    je .left
    cmp al, 'H'
    je .home
    cmp al, 'F'
    je .end
    jmp .done
.up:    mov r15, 256
        ret
.down:  mov r15, 257
        ret
.right: mov r15, 258
        ret
.left:  mov r15, 259
        ret
.home:  mov r15, 260
        ret
.end:   mov r15, 261
        ret
.eof:
    mov r15, -1
.done: ret

; handle_key: r15
handle_key:
    cmp qword [shell_mode], 0
    jne shell_key
    cmp r15, 20                 ; Ctrl-T -> interactive shell pane
    je .shell
    cmp r15, -1
    je .quit
    cmp r15, 256
    je .kup
    cmp r15, 257
    je .kdown
    cmp r15, 258
    je .kright
    cmp r15, 259
    je .kleft
    cmp r15, 260
    je .khome
    cmp r15, 261
    je .kend
    cmp r15, 17
    je .quit
    cmp r15, 19
    je .save
    cmp r15, 18
    je .run
    cmp r15, 5
    je .exnext
    cmp r15, 12
    je .load
    cmp r15, 26
    je .undo
    cmp r15, 127
    je .back
    cmp r15, 8
    je .back
    cmp r15, 10
    je .enter
    cmp r15, 13
    je .enter
    cmp r15, 32
    jb .ret
    mov rdi, r15
    call insert_byte
    ret
.kup:    call move_up
         ret
.kdown:  call move_down
         ret
.kleft:  call move_left
         ret
.kright: call move_right
         ret
.khome:  call home_key
         ret
.kend:   call end_key
         ret
.back:   call delete_before
         ret
.enter:  mov rdi, 10
         call insert_byte
         ret
.save:   call save_file
         ret
.run:    call run_program
         ret
.load:   call load_prompt
         ret
.undo:   call undo_do
         ret
.exnext: call examples_next
         ret
.shell:  mov qword [shell_mode], 1
         ret
.quit:
    mov rsi, s_cur_on
    call write_z
    mov rsi, s_alt_off
    call write_z
    call restore_term
    mov rax, SYS_exit
    xor rdi, rdi
    syscall
.ret: ret

; ============================================================
; main
; ============================================================
_start:
    lea rsi, [s_default]
    lea rdi, [path]
    call strcpy_z
    mov rax, [rsp]
    cmp rax, 2
    jl .noarg
    mov rsi, [rsp+16]
    lea rdi, [path]
    call strcpy_z
.noarg:
    lea rdi, [path]
    call strlen
    mov [path_len], rax
    call load_file
    call set_raw
    mov rsi, s_alt_on
    call write_z
    mov rsi, s_cur_off
    call write_z
    call build_cmd
.loop:
    call render
    call read_key
    call handle_key
    jmp .loop
