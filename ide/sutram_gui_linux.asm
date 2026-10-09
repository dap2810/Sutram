; ============================================================================
;  sutram_gui_linux.asm  —  Sutram GUI IDE for Linux  (X11, pure NASM)
;
;  A native X11 client written directly against the X protocol over the Unix
;  socket. No toolkit, no libX11, no runtime. Same principle as the Windows
;  GUI: one hand-written assembly source.
;
;  SLICE 2: graphics context, an Expose-driven repaint that draws two panes
;  with labels, and a key/close event loop.
;
;  FIXED IN SLICE 2: the CreateWindow request carries a value-mask and one
;  value, so its body is 36 bytes = 9 four-byte units. Slice 1 declared 8.
;  A real server would have misparsed the request. The mock test asserted 8,
;  so it agreed with the bug; it now derives the expected length from the
;  bytes actually received.
;
;  Build:
;     nasm -f elf64 ide/sutram_gui_linux.asm -o /tmp/gui.o
;     ld -o sutram-gui /tmp/gui.o
;
;  Run (needs a display):  ./sutram-gui
; ============================================================================

%define SYS_read        0
%define SYS_write       1
%define SYS_socket      41
%define SYS_connect     42
%define SYS_exit        60
%define SYS_readlink    89
%define SYS_open        2
%define SYS_close       3
%define SYS_pipe        22
%define SYS_dup2        33
%define SYS_fork        57
%define SYS_execve      59
%define SYS_wait4       61

%define AF_UNIX         1
%define SOCK_STREAM     1

; ---- X11 protocol opcodes -------------------------------------------------
%define X_CreateWindow  1
%define X_MapWindow     8
%define X_CreateGC      55
%define X_PolyFillRect  70
%define X_ImageText8    76
%define X_GetKeyboardMapping 101

; ---- X11 event codes ------------------------------------------------------
%define EV_KeyPress     2
%define EV_Expose       12

; ---- window class / GC value masks ----------------------------------------
%define InputOutput     1
%define CopyFromParent  0
%define GCForeground    0x00000004
%define GCBackground    0x00000008

; ---- layout and colours ---------------------------------------------------
%define WIN_W           900
%define WIN_H           620

%define PANE_X          10
%define ED_Y            44
%define ED_W            880
%define ED_H            400
%define OUT_Y           468
%define OUT_H           132

%define COL_BG          0x0F1720        ; window background
%define COL_PANE        0x16202B        ; editor pane
%define COL_OUT         0x111A22        ; output pane
%define COL_RULE        0x1A4A5C        ; teal separator
%define COL_TEXT        0xDFE7EE        ; body text
%define COL_ACCENT      0xE86D11        ; orange heading
%define COL_CARET       0xE86D11        ; cursor

; ---- editor ---------------------------------------------------------------
%define ED_CAP          8192            ; editor buffer capacity
%define LINE_H          16
%define ED_TEXT_X       (PANE_X + 8)
%define ED_TEXT_Y       (ED_Y + 30)
%define ED_LINES_MAX    23              ; visible lines in the pane

; ---- X11 keys -------------------------------------------------------------
%define KC_ESCAPE       9
%define KC_BACKSPACE    22
%define KC_RETURN       36
%define KC_LEFT         113
%define KC_RIGHT        114
%define KC_UP           111
%define KC_DOWN         116
%define KC_CTRL_R       27              ; 'r' keycode, checked with ControlMask
%define KC_CTRL_S       39              ; 's' keycode
%define KC_CTRL_L       46              ; 'l' keycode
%define KC_CTRL_Z       52              ; 'z' keycode
%define SAVE_PATH       "/tmp/.sutram_gui_saved.sm"
%define UNDO_LEVELS     8
%define MASK_CONTROL    0x0004

; ---- keyboard mapping (slice 4) -------------------------------------------
%define KM_FIRST        8               ; first keycode we ask about
%define KM_COUNT        119             ; keycodes 8..126
%define KM_SYMS_CAP     4096            ; reply keysym bytes we will accept

; ---- run path (slice 5) ---------------------------------------------------
%define RUN_SRC         "/tmp/.sutram_gui_run.sm"
%define RUN_BIN         "/tmp/.sutram_gui_run.bin"
%define RUN_CAP         4096            ; captured child output bytes
%define O_WRONLY        1
%define O_CREAT         64
%define O_TRUNC         512
%define MASK_CONTROL_ST 0x0004

section .data
; Standard US-QWERTY XKB keycode -> ASCII. This is the common layout on every
; mainstream X server. A non-US layout would need the server's own mapping,
; fetched with GetKeyboardMapping (opcode 101) — that is the next slice.
; 0 means "no printable character".
kc_table:
    times 10 db 0                       ; 0..9
    db '1','2','3','4','5','6','7','8','9','0'   ; 10..19
    db '-','='                          ; 20..21
    db 0,0                              ; 22 (backspace), 23 (tab)
    db 'q','w','e','r','t','y','u','i','o','p'   ; 24..33
    db '[',']'                          ; 34..35
    db 0,0                              ; 36 (return), 37 (ctrl)
    db 'a','s','d','f','g','h','j','k','l'       ; 38..46
    db ';',0x27                         ; 47..48
    db '`'                              ; 49
    db 0,0                              ; 50,51
    db 'z','x','c','v','b','n','m'      ; 52..58
    db ',','.','/'                      ; 59..61
    db 0,0,0                            ; 62..64
    db ' '                              ; 65
    times 60 db 0                       ; 66..125
section .text

section .bss
    sockaddr    resb 128
    setup       resb 32768
    root_win    resq 1
    our_win     resq 1
    gc          resq 1
    event       resb 64
    rid_base    resq 1
    rid_mask    resq 1
    next_id     resq 1
    reqbuf      resb 1024

; --- editor state ---
    ed_buf      resb ED_CAP
    ed_len      resq 1
    ed_cursor   resq 1
    key_char    resb 8
    ; ---- slice 4: server keymap ----
    km_reply    resb 32             ; GetKeyboardMapping reply header
    km_syms     resb 4096           ; keysym array
    kc_map      resb 256            ; keycode -> ASCII from the server
    km_ok       resq 1              ; 1 once a keymap has been fetched
    ; ---- slice 8: bounded undo stack (8 levels) ----
    undo_stack  resb UNDO_LEVELS * ED_CAP   ; slot i = snapshot i
    undo_slen   resq UNDO_LEVELS            ; saved length per slot
    undo_scur   resq UNDO_LEVELS            ; saved cursor per slot
    undo_depth  resq 1                      ; number of live snapshots
    ; ---- slice 5: run path ----
    pipefd      resd 2
    comp_path   resb 512            ; resolved compiler path
    run_out     resb RUN_CAP        ; captured output from the last run
    run_out_len resq 1
    run_argv    resq 8              ; execve argv for the compiler
    run_envp    resq 2              ; empty environment
    out_lines   resb 1024           ; run_out split into display lines
    out_nlines  resq 1
    want_quit   resd 1

section .data
    xsock_path  db "/tmp/.X11-unix/X0", 0
    str_procself db "/proc/self/exe", 0
    comp_suffix  db "/sutram_compiler", 0
    run_src_z    db RUN_SRC, 0
    run_bin_z    db RUN_BIN, 0
    save_z       db SAVE_PATH, 0
    msg_run      db "Sutram GUI: run (Ctrl-R)", 10, 0

    handshake   db 0x6C, 0x00
                dw 11
                dw 0
                dw 0
                dw 0
                db 0, 0
    handshake_len equ $ - handshake

    txt_title   db "Sutram IDE"
    txt_title_n equ $ - txt_title
    txt_editor  db "Editor"
    txt_editor_n equ $ - txt_editor
    txt_output  db "Output"
    txt_output_n equ $ - txt_output
    txt_hint    db "Ctrl-R run   Ctrl-S save   Ctrl-Z undo"
    txt_hint_n  equ $ - txt_hint

    msg_ok      db "Sutram GUI: connected to X, window created.", 10, 0
    msg_nox     db "Sutram GUI: cannot reach an X server (no DISPLAY).", 10, 0
    msg_hand    db "Sutram GUI: handshake failed.", 10, 0

section .text
    global _start

; ---------------------------------------------------------------- write_z
; rsi = NUL-terminated string
write_z:
    push rsi
    xor rdx, rdx
.c: cmp byte [rsi+rdx], 0
    je .go
    inc rdx
    jmp .c
.go:
    mov rax, SYS_write
    mov rdi, 1
    pop rsi
    syscall
    ret

; ---------------------------------------------------------------- send
; rdi = fd, rsi = buffer, rdx = length.  returns 0 ok, -1 short write.
send_req:
    mov rax, SYS_write
    syscall
    cmp rax, rdx
    jne .bad
    xor rax, rax
    ret
.bad:
    mov rax, -1
    ret

; ---------------------------------------------------------------- connect_x
connect_x:
    mov rax, SYS_socket
    mov rdi, AF_UNIX
    mov rsi, SOCK_STREAM
    xor rdx, rdx
    syscall
    cmp rax, 0
    jl .fail
    mov r15, rax

    lea rdi, [sockaddr]
    mov word [rdi], AF_UNIX
    lea rsi, [xsock_path]
    add rdi, 2
.copy:
    mov al, [rsi]
    mov [rdi], al
    test al, al
    jz .copied
    inc rsi
    inc rdi
    jmp .copy
.copied:
    mov rax, SYS_connect
    mov rdi, r15
    lea rsi, [sockaddr]
    mov rdx, 110
    syscall
    cmp rax, 0
    jl .fail
    mov rax, r15
    ret
.fail:
    mov rax, -1
    ret

; ---------------------------------------------------------------- handshake
do_handshake:
    push rdi
    mov rax, SYS_write
    lea rsi, [handshake]
    mov rdx, handshake_len
    syscall
    cmp rax, handshake_len
    jne .bad

    pop rdi
    push rdi
    mov rax, SYS_read
    lea rsi, [setup]
    mov rdx, 8
    syscall
    cmp rax, 8
    jl .bad
    cmp byte [setup], 1
    jne .bad

    movzx rdx, word [setup+6]
    shl rdx, 2
    cmp rdx, 32768
    ja .bad
    sub rdx, 8
    mov rax, SYS_read
    lea rsi, [setup+8]
    syscall
    pop rdi
    xor rax, rax
    ret
.bad:
    pop rdi
    mov rax, -1
    ret

; ---------------------------------------------------------------- parse_setup
parse_setup:
    mov eax, [setup+12]
    mov [rid_base], rax
    mov eax, [setup+16]
    mov [rid_mask], rax
    movzx rcx, word [setup+24]      ; vendor length
    add rcx, 3
    and rcx, ~3
    movzx rdx, byte [setup+29]      ; pixmap formats
    shl rdx, 3
    lea rsi, [setup+40]
    add rsi, rcx
    add rsi, rdx
    mov eax, [rsi]                  ; SCREEN.root
    mov [root_win], rax
    ret

; ---------------------------------------------------------------- new_id
; return the next free resource id in rax.
; X11 ids are base | (n & mask) — the base must NOT be masked away.
new_id:
    mov rax, [rid_base]
    mov rcx, [next_id]
    and rcx, [rid_mask]
    or rax, rcx
    inc qword [next_id]
    ret

; ---------------------------------------------------------------- create_win
create_win:
    lea rdi, [reqbuf]
    mov byte [rdi], X_CreateWindow
    mov byte [rdi+1], 0             ; depth = CopyFromParent
    mov word [rdi+2], 9             ; 36 bytes = 9 units (was 8: a real bug)
    call new_id
    mov [our_win], rax
    mov [rdi+4], rax
    mov rax, [root_win]
    mov [rdi+8], rax
    mov word [rdi+12], 0
    mov word [rdi+14], 0
    mov word [rdi+16], WIN_W
    mov word [rdi+18], WIN_H
    mov word [rdi+20], 0
    mov word [rdi+22], InputOutput
    mov dword [rdi+24], CopyFromParent
    mov dword [rdi+28], 0x00000800  ; CWEventMask
    mov dword [rdi+32], 0x00008003  ; Exposure | KeyPress | StructureNotify
    ret

; ---------------------------------------------------------------- create_gc
; one GC, foreground + background, used for every draw below.
create_gc:
    lea rdi, [reqbuf]
    mov byte [rdi], X_CreateGC
    mov byte [rdi+1], 0
    mov word [rdi+2], 6             ; 24 bytes = 6 units
    call new_id
    mov [gc], rax
    mov [rdi+4], rax                ; cid
    mov rax, [our_win]
    mov [rdi+8], rax                ; drawable
    mov dword [rdi+12], GCForeground | GCBackground
    mov dword [rdi+16], COL_BG      ; foreground
    mov dword [rdi+20], COL_PANE    ; background
    ret

; ---------------------------------------------------------------- set_fg
; rdi = colour.  Builds AND SENDS a ChangeGC (opcode 56) setting the GC's
; foreground.  Body is 16 bytes = 4 four-byte units.
set_fg:
    mov r11d, edi
    lea rdi, [reqbuf]
    mov byte [rdi], 56
    mov byte [rdi+1], 0
    mov word [rdi+2], 4             ; 16 bytes = 4 units (was 3: a real bug)
    mov rax, [gc]
    mov [rdi+4], rax
    mov dword [rdi+8], GCForeground
    mov [rdi+12], r11d
    mov rdi, r12
    lea rsi, [reqbuf]
    mov rdx, 16
    call send_req
    ret

; ---------------------------------------------------------------- fill_rect
; rsi = x, rdx = y, rcx = w, r8 = h  -> builds a PolyFillRect request.
; returns the request length in rdx.
fill_rect:
    push rsi
    lea rdi, [reqbuf]
    mov byte [rdi], X_PolyFillRect
    mov byte [rdi+1], 0
    mov word [rdi+2], 5             ; 12 + 8 = 20 bytes = 5 units
    mov rax, [our_win]
    mov [rdi+4], rax
    mov rax, [gc]
    mov [rdi+8], rax
    pop rsi
    mov [rdi+12], si                ; rect.x
    mov [rdi+14], dx                ; rect.y
    mov [rdi+16], cx                ; rect.width
    mov [rdi+18], r8w               ; rect.height
    mov rdx, 20
    ret

; ---------------------------------------------------------------- draw_text
; rsi = string ptr, rdx = length, rcx = x, r8 = y
; builds an ImageText8 request. returns length in rdx.
draw_text:
    push rbx
    mov rbx, rdi                    ; keep nothing; rdi unused here
    lea rdi, [reqbuf]
    mov byte [rdi], X_ImageText8
    mov [rdi+1], dl                 ; n = string length (<=255)
    ; request length: (16 + n + 3) / 4
    mov r9, rdx
    add r9, 16
    add r9, 3
    shr r9, 2
    mov [rdi+2], r9w
    mov rax, [our_win]
    mov [rdi+4], rax
    mov rax, [gc]
    mov [rdi+8], rax
    mov [rdi+12], cx                ; x
    mov [rdi+14], r8w               ; y
    ; copy the bytes, then pad to a 4-byte boundary
    push rsi
    add rdi, 16
    mov r9, rdx
.cp:
    test r9, r9
    jz .pad
    mov al, [rsi]
    mov [rdi], al
    inc rsi
    inc rdi
    dec r9
    jmp .cp
.pad:
    mov r9, rdx
    add r9, 3
    and r9, ~3
    sub r9, rdx                     ; padding bytes needed
.padl:
    test r9, r9
    jz .done
    mov byte [rdi], 0
    inc rdi
    dec r9
    jmp .padl
.done:
    mov r9, rdx
    add r9, 16
    add r9, 3
    shr r9, 2
    shl r9, 2                       ; padded request length in bytes
    mov rdx, r9
    pop rsi
    pop rbx
    ret


; ---------------------------------------------------------------- draw_output
; Slice 5: render the captured run output in the output pane, one line per
; LINE_H. Up to 7 lines fit; extra lines are dropped (the pane scrolls in a
; later slice). Uses r14 for the line cursor so it never disturbs r12 (the
; socket fd).
draw_output:
    push rbx
    push r13
    push r14
    mov r13, [rel out_nlines]
    test r13, r13
    jz .done
    cmp r13, 7
    jbe .clamped
    mov r13, 7
.clamped:
    mov rdi, COL_TEXT
    call set_fg
    xor rbx, rbx
    lea r14, [rel out_lines]
.line:
    cmp rbx, r13
    jae .done
    xor rcx, rcx
.len:
    cmp byte [r14 + rcx], 0
    je .have
    inc rcx
    jmp .len
.have:
    mov rsi, r14
    mov rdx, rcx
    mov rcx, PANE_X + 8
    mov r8, rbx
    imul r8, LINE_H
    add r8, OUT_Y + 24
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req
    ; advance past this line's NUL
.adv:
    cmp byte [r14], 0
    je .adv_done
    inc r14
    jmp .adv
.adv_done:
    inc r14
    inc rbx
    jmp .line
.done:
    pop r14
    pop r13
    pop rbx
    ret

; ---------------------------------------------------------------- draw_all
; the Expose repaint: background, two panes, a rule, and the labels.
draw_all:
    push r12
    push r13

    ; whole window background
    mov rdi, COL_BG
    call set_fg
    xor rsi, rsi
    xor rdx, rdx
    mov rcx, WIN_W
    mov r8, WIN_H
    call fill_rect
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req

    ; editor pane
    mov rdi, COL_PANE
    call set_fg
    mov rsi, PANE_X
    mov rdx, ED_Y
    mov rcx, ED_W
    mov r8, ED_H
    call fill_rect
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req

    ; output pane
    mov rdi, COL_OUT
    call set_fg
    mov rsi, PANE_X
    mov rdx, OUT_Y
    mov rcx, ED_W
    mov r8, OUT_H
    call fill_rect
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req

    ; teal rule under the heading
    mov rdi, COL_RULE
    call set_fg
    mov rsi, PANE_X
    mov rdx, 36
    mov rcx, ED_W
    mov r8, 2
    call fill_rect
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req

    ; ---- labels ----------------------------------------------------------
    mov rdi, COL_ACCENT
    call set_fg
    lea rsi, [txt_title]
    mov rdx, txt_title_n
    mov rcx, PANE_X
    mov r8, 26
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req

    mov rdi, COL_TEXT
    call set_fg
    lea rsi, [txt_editor]
    mov rdx, txt_editor_n
    mov rcx, PANE_X + 8
    mov r8, ED_Y + 18
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req

    lea rsi, [txt_output]
    mov rdx, txt_output_n
    mov rcx, PANE_X + 8
    mov r8, OUT_Y + 18
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req
    call draw_output

    lea rsi, [txt_hint]
    mov rdx, txt_hint_n
    mov rcx, PANE_X + 8
    mov r8, ED_Y + ED_H - 12
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req

    pop r13
    pop r12
    ret

; ---------------------------------------------------------------- ed_insert
; rdi = character.  Insert at the cursor, bounded by ED_CAP.
ed_insert:
    push rbx
    push rdi
    call snapshot
    pop rdi
    lea  rbx, [rel ed_buf]
    mov  rax, [rel ed_len]
    cmp  rax, ED_CAP - 2
    jae  .done
    mov  rcx, [rel ed_cursor]
    mov  rdx, rax
.shift:
    cmp  rdx, rcx
    jbe  .place
    mov  r8b, [rbx + rdx - 1]
    mov  [rbx + rdx], r8b
    dec  rdx
    jmp  .shift
.place:
    mov  [rbx + rcx], dil
    inc  qword [rel ed_len]
    inc  qword [rel ed_cursor]
.done:
    pop  rbx
    ret

; ---------------------------------------------------------------- ed_backspace
ed_backspace:
    push rbx
    call snapshot
    lea  rbx, [rel ed_buf]
    mov  rcx, [rel ed_cursor]
    test rcx, rcx
    jz   .done
    dec  rcx
    mov  rax, [rel ed_len]
.shift:
    mov  rdx, rcx
    inc  rdx
    cmp  rdx, rax
    jae  .shrink
    mov  r8b, [rbx + rdx]
    mov  [rbx + rdx - 1], r8b
    inc  rcx
    jmp  .shift
.shrink:
    dec  qword [rel ed_len]
    dec  qword [rel ed_cursor]
.done:
    pop  rbx
    ret

; ---------------------------------------------------------------- ed_caret_x
; Compute the caret's column (0-based) on its current line -> rax.
ed_caret_x:
    push rbx
    lea  rbx, [rel ed_buf]
    mov  rcx, [rel ed_cursor]
    xor  rax, rax
.loop:
    test rcx, rcx
    jz   .done
    dec  rcx
    cmp  byte [rbx + rcx], 10
    je   .done
    inc  rax
    jmp  .loop
.done:
    pop  rbx
    ret

; ---------------------------------------------------------------- ed_caret_y
; Compute the caret's line index (0-based) -> rax.
ed_caret_y:
    push rbx
    lea  rbx, [rel ed_buf]
    mov  rcx, [rel ed_cursor]
    xor  rax, rax
    xor  rdx, rdx
.loop:
    cmp  rdx, rcx
    jae  .done
    cmp  byte [rbx + rdx], 10
    jne  .next
    inc  rax
.next:
    inc  rdx
    jmp  .loop
.done:
    pop  rbx
    ret

; ---------------------------------------------------------------- draw_editor
; Repaint the editor pane background and its text, then the caret.
draw_editor:
    push rbx
    push r12
    push r13
    push r14
    push r15
    lea  rbx, [rel ed_buf]

    ; pane background
    mov  rdi, COL_PANE
    call set_fg
    mov  rsi, PANE_X
    mov  rdx, ED_Y
    mov  rcx, ED_W
    mov  r8,  ED_H
    call fill_rect
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req

    ; walk the buffer a line at a time
    mov  rdi, COL_TEXT
    call set_fg

    xor  r13, r13                   ; line index
    xor  r14, r14                   ; line start offset
    xor  r15, r15                   ; scan offset
.line:
    cmp  r15, [rel ed_len]
    ja   .after
    ; is this the end of a line (newline or end of buffer)?
    mov  rax, [rel ed_len]
    cmp  r15, rax
    je   .emit
    cmp  byte [rbx + r15], 10
    jne  .advance
.emit:
    cmp  r13, ED_LINES_MAX
    jae  .after
    mov  rdx, r15
    sub  rdx, r14                   ; line length
    test rdx, rdx
    jz   .next_line                 ; empty line: nothing to draw
    mov  rsi, rbx
    add  rsi, r14
    mov  rcx, ED_TEXT_X
    mov  r8,  ED_TEXT_Y
    mov  rax, r13
    imul rax, LINE_H
    add  r8,  rax
    call draw_text
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req
    mov  rdi, COL_TEXT
    call set_fg
.next_line:
    inc  r13
    mov  r14, r15
    inc  r14                        ; skip the newline
    inc  r15
    jmp  .line
.advance:
    inc  r15
    jmp  .line

.after:
    ; caret: a 2x14 bar at the cursor
    mov  rdi, COL_CARET
    call set_fg
    call ed_caret_x
    imul rax, 8                     ; approximate advance per character
    add  rax, ED_TEXT_X
    mov  rsi, rax
    call ed_caret_y
    imul rax, LINE_H
    add  rax, ED_TEXT_Y
    sub  rax, 12
    mov  rdx, rax
    mov  rcx, 2
    mov  r8,  14
    call fill_rect
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req

    pop  r15
    pop  r14
    pop  r13
    pop  r12
    pop  rbx
    ret


; ---------------------------------------------------------------- fetch_keymap
; Slice 4: ask the server for its real keyboard mapping (opcode 101) and build
; kc_map[keycode] = ASCII from keysym index 0. A non-US layout then types
; correctly, instead of relying on the hardcoded US table. On any protocol
; problem km_ok stays 0 and handle_key falls back to kc_table.
fetch_keymap:
    push rbx
    push r12
    push r13
    ; ---- request: first_keycode, count ----
    lea rdi, [reqbuf]
    mov byte [rdi], X_GetKeyboardMapping
    mov byte [rdi+1], 0
    mov word [rdi+2], 2             ; 8 bytes = 2 units
    mov byte [rdi+4], KM_FIRST
    mov byte [rdi+5], KM_COUNT
    mov word [rdi+6], 0
    mov rdi, r12
    lea rsi, [reqbuf]
    mov rdx, 8
    call send_req
    ; ---- reply header ----
    mov rax, SYS_read
    mov rdi, r12
    lea rsi, [km_reply]
    mov rdx, 32
    syscall
    cmp rax, 32
    jl .fail
    cmp byte [km_reply], 1
    jne .fail
    movzx r13, byte [km_reply+1]    ; keysyms_per_keycode
    test r13, r13
    jz .fail
    ; ---- read the keysym array ----
    mov rax, r13
    imul rax, KM_COUNT*4
    cmp rax, KM_SYMS_CAP
    ja .fail
    mov rdx, rax
    mov rax, SYS_read
    mov rdi, r12
    lea rsi, [km_syms]
    syscall
    cmp rax, rdx
    jl .fail
    ; ---- build kc_map ----
    xor rbx, rbx
.build:
    cmp rbx, KM_COUNT
    jae .ok
    mov rax, rbx
    imul rax, r13
    shl rax, 2                      ; byte offset of keysym[0]
    lea rcx, [rel km_syms]
    mov ecx, dword [rcx + rax]
    cmp ecx, 0x20
    jb .zero
    cmp ecx, 0x7e
    ja .zero
    jmp .store
.zero:
    xor ecx, ecx
.store:
    lea rdx, [rel kc_map]
    mov byte [rdx + rbx + KM_FIRST], cl
    inc rbx
    jmp .build
.ok:
    mov qword [rel km_ok], 1
    pop r13
    pop r12
    pop rbx
    ret
.fail:
    mov qword [rel km_ok], 0
    pop r13
    pop r12
    pop rbx
    ret


; ---------------------------------------------------------------- save_buffer
; Write the editor buffer to RUN_SRC. Returns 0 ok, -1 on error.
save_buffer:
    push rbx
    mov rax, SYS_open
    lea rdi, [rel run_src_z]
    mov rsi, O_WRONLY | O_CREAT | O_TRUNC
    mov rdx, 0o644
    syscall
    cmp rax, 0
    jl .fail
    mov rbx, rax
    mov rdx, [rel ed_len]
    test rdx, rdx
    jz .close
    mov rax, SYS_write
    mov rdi, rbx
    lea rsi, [rel ed_buf]
    syscall
.close:
    mov rax, SYS_close
    mov rdi, rbx
    syscall
    xor rax, rax
    pop rbx
    ret
.fail:
    mov rax, -1
    pop rbx
    ret

; ---------------------------------------------------------------- find_compiler
; Resolve the compiler as "<dir of this executable>/sutram_compiler" using
; /proc/self/exe, the same trick the compiler itself uses for language packs.
; The IDE and compiler ship together, so this needs no configuration.
find_compiler:
    push rbx
    push r12
    mov rax, SYS_readlink
    lea rdi, [rel str_procself]
    lea rsi, [rel comp_path]
    mov rdx, 500
    syscall
    cmp rax, 0
    jle .fail
    lea rbx, [rel comp_path]
    add rbx, rax
    mov byte [rbx], 0
.sb:
    dec rbx
    lea rcx, [rel comp_path]
    cmp rbx, rcx
    jbe .fail
    cmp byte [rbx], '/'
    jne .sb
    lea rsi, [rel comp_suffix]
.copy:
    mov al, [rsi]
    mov [rbx], al
    test al, al
    jz .done
    inc rbx
    inc rsi
    jmp .copy
.done:
    xor rax, rax
    pop r12
    pop rbx
    ret
.fail:
    mov rax, -1
    pop r12
    pop rbx
    ret

; ---------------------------------------------------------------- exec_capture
; Fork, run r13 = path with r14 = argv (NULL-terminated) and an empty envp,
; capture stdout+stderr into run_out. Sets run_out_len. Waits for the child.
exec_capture:
    push rbx
    push r12
    push r15
    ; pipe
    lea rdi, [rel pipefd]
    mov rax, SYS_pipe
    syscall
    cmp rax, 0
    jl .fail
    ; fork
    mov rax, SYS_fork
    syscall
    cmp rax, 0
    jl .fail
    jne .parent
    ; ---- child: stdout+stderr -> pipe write end ----
    mov rdi, [rel pipefd+4]
    mov rsi, 1
    mov rax, SYS_dup2
    syscall
    mov rdi, [rel pipefd+4]
    mov rsi, 2
    mov rax, SYS_dup2
    syscall
    mov rdi, [rel pipefd]
    mov rax, SYS_close
    syscall
    mov rdi, [rel pipefd+4]
    mov rax, SYS_close
    syscall
    mov rdi, r13
    mov rsi, r14
    lea rdx, [rel run_envp]
    mov rax, SYS_execve
    syscall
    mov rdi, 127
    mov rax, SYS_exit
    syscall
.parent:
    mov rdi, [rel pipefd+4]
    mov rax, SYS_close
    syscall
    mov r12, [rel run_out_len]      ; append, so compiler output survives the run
    cmp r12, RUN_CAP
    jb .read
    mov r12, RUN_CAP
.read:
    mov rax, SYS_read
    mov rdi, [rel pipefd]
    lea rsi, [rel run_out]
    add rsi, r12
    mov rdx, RUN_CAP
    sub rdx, r12
    syscall
    cmp rax, 0
    jle .drained
    add r12, rax
    cmp r12, RUN_CAP
    jb .read
.drained:
    mov [rel run_out_len], r12
    mov rdi, [rel pipefd]
    mov rax, SYS_close
    syscall
    mov rax, SYS_wait4
    mov rdi, -1
    xor rsi, rsi
    xor rdx, rdx
    xor r10, r10
    syscall
    pop r15
    pop r12
    pop rbx
    xor rax, rax
    ret
.fail:
    mov qword [rel run_out_len], 0
    pop r15
    pop r12
    pop rbx
    mov rax, -1
    ret

; ---------------------------------------------------------------- split_lines
; Turn run_out into out_lines (out_nlines lines, each NUL-terminated, CR
; stripped) for the output pane.
split_lines:
    push rbx
    push r12
    push r13
    xor rbx, rbx                    ; src index
    xor r12, r12                    ; dst index
    xor r13, r13                    ; line count
    lea rdi, [rel out_lines]
.next:
    cmp rbx, [rel run_out_len]
    jae .end
    cmp r13, 60
    jae .end
    lea rsi, [rel run_out]
    add rsi, rbx
    mov al, [rsi]
    cmp al, 10
    je .eol
    cmp al, 13
    je .skip
    mov [rdi], al
    inc rdi
    inc r12
.skip:
    inc rbx
    jmp .next
.eol:
    mov byte [rdi], 0
    inc rdi
    inc r12
    inc r13
    inc rbx
    jmp .next
.end:
    mov byte [rdi], 0
    inc r13
    mov [rel out_nlines], r13
    pop r13
    pop r12
    pop rbx
    ret

; ---------------------------------------------------------------- do_run
; Ctrl-R: save the buffer, compile it, and if that succeeds run the result.
; Output (compiler messages, then program output) lands in the output pane.
do_run:
    push rbx
    mov qword [rel run_out_len], 0
    call save_buffer
    cmp rax, 0
    jl .done
    call find_compiler
    cmp rax, 0
    jl .done
    ; ---- argv for the compiler: [comp, src, bin, NULL] ----
    lea rax, [rel comp_path]
    mov [rel run_argv], rax
    lea rax, [rel run_src_z]
    mov [rel run_argv+8], rax
    lea rax, [rel run_bin_z]
    mov [rel run_argv+16], rax
    mov qword [rel run_argv+24], 0
    lea r13, [rel comp_path]
    lea r14, [rel run_argv]
    call exec_capture
    mov byte [rel run_out+4095], 0    ; NUL-terminate without overrunning the buffer
    call split_lines
    ; ---- if the compiler succeeded (no output, exit 0) run the binary ----
    ; The compiler prints "OK: compiled N bytes" on success; treat any
    ; non-empty output that contains "Error" as failure and stop.
    cmp qword [rel run_out_len], 0
    je .run_bin
    ; scan for the substring "Error"
    call has_error
    cmp rax, 0
    jne .done
.run_bin:
    lea rax, [rel run_bin_z]
    mov [rel run_argv], rax
    mov qword [rel run_argv+8], 0
    lea r13, [rel run_bin_z]
    lea r14, [rel run_argv]
    call exec_capture
    call split_lines
.done:
    pop rbx
    ret

; ---------------------------------------------------------------- has_error
; rax = 1 if run_out contains "Error", else 0.
has_error:
    push rbx
    push rcx
    xor rbx, rbx
.scan:
    mov rax, [rel run_out_len]
    sub rax, 5
    cmp rbx, rax
    ja .no
    lea rsi, [rel run_out]
    add rsi, rbx
    cmp byte [rsi], 'E'
    jne .next
    cmp byte [rsi+1], 'r'
    jne .next
    cmp byte [rsi+2], 'r'
    jne .next
    cmp byte [rsi+3], 'o'
    jne .next
    cmp byte [rsi+4], 'r'
    jne .next
    mov rax, 1
    pop rcx
    pop rbx
    ret
.next:
    inc rbx
    jmp .scan
.no:
    xor rax, rax
    pop rcx
    pop rbx
    ret


; ---------------------------------------------------------------- save_saved
; Ctrl-S: write the editor buffer to SAVE_PATH. 0 ok, -1 error.
save_saved:
    push rbx
    mov rax, SYS_open
    lea rdi, [rel save_z]
    mov rsi, O_WRONLY | O_CREAT | O_TRUNC
    mov rdx, 0o644
    syscall
    cmp rax, 0
    jl .fail
    mov rbx, rax
    mov rdx, [rel ed_len]
    test rdx, rdx
    jz .close
    mov rax, SYS_write
    mov rdi, rbx
    lea rsi, [rel ed_buf]
    syscall
.close:
    mov rax, SYS_close
    mov rdi, rbx
    syscall
    xor rax, rax
    pop rbx
    ret
.fail:
    mov rax, -1
    pop rbx
    ret

; ---------------------------------------------------------------- load_saved
; Ctrl-L: read SAVE_PATH into the editor buffer, replacing its contents.
load_saved:
    push rbx
    push r12
    mov rax, SYS_open
    lea rdi, [rel save_z]
    xor rsi, rsi                    ; O_RDONLY
    xor rdx, rdx
    syscall
    cmp rax, 0
    jl .fail
    mov rbx, rax
    mov rax, SYS_read
    mov rdi, rbx
    lea rsi, [rel ed_buf]
    mov rdx, ED_CAP - 2
    syscall
    cmp rax, 0
    jl .fail
    mov r12, rax
    mov rax, SYS_close
    mov rdi, rbx
    syscall
    mov [rel ed_len], r12
    mov [rel ed_cursor], r12
    xor rax, rax
    pop r12
    pop rbx
    ret
.fail:
    mov rax, SYS_close
    mov rdi, rbx
    syscall
    pop r12
    pop rbx
    mov rax, -1
    ret



; ---------------------------------------------------------------- snapshot
; Slice 8: push the current buffer onto a bounded undo stack before an edit.
; When the stack is full the oldest slot is dropped (a 7-slot memmove), so the
; most recent UNDO_LEVELS-1 edits are always recoverable.
snapshot:
    push rbx
    push rcx
    push rdi
    push rsi
    ; if full, shift slots 1..N-1 down to 0..N-2
    mov rax, [rel undo_depth]
    cmp rax, UNDO_LEVELS
    jb .push
    lea rsi, [rel undo_stack + ED_CAP]      ; source: slot 1
    lea rdi, [rel undo_stack]               ; dest:   slot 0
    mov rcx, (UNDO_LEVELS - 1) * ED_CAP
    rep movsb
    lea rsi, [rel undo_slen + 8]
    lea rdi, [rel undo_slen]
    mov rcx, UNDO_LEVELS - 1
    rep movsq
    lea rsi, [rel undo_scur + 8]
    lea rdi, [rel undo_scur]
    mov rcx, UNDO_LEVELS - 1
    rep movsq
    mov rax, UNDO_LEVELS - 1
    mov [rel undo_depth], rax
.push:
    mov rax, [rel undo_depth]
    mov rcx, rax
    imul rcx, ED_CAP
    lea rdi, [rel undo_stack]
    add rdi, rcx
    lea rsi, [rel ed_buf]
    mov rcx, [rel ed_len]
    test rcx, rcx
    jz .meta
    rep movsb
.meta:
    mov rax, [rel undo_depth]
    lea rdi, [rel undo_slen]
    mov rcx, [rel ed_len]
    mov [rdi + rax*8], rcx
    lea rdi, [rel undo_scur]
    mov rcx, [rel ed_cursor]
    mov [rdi + rax*8], rcx
    inc rax
    mov [rel undo_depth], rax
    pop rsi
    pop rdi
    pop rcx
    pop rbx
    ret

; ---------------------------------------------------------------- undo_restore
; Ctrl-Z: pop the most recent snapshot back into the buffer.
undo_restore:
    push rbx
    push rcx
    push rdi
    push rsi
    mov rax, [rel undo_depth]
    test rax, rax
    jz .done
    dec rax
    mov [rel undo_depth], rax
    mov rcx, rax
    imul rcx, ED_CAP
    lea rsi, [rel undo_stack]
    add rsi, rcx
    lea rdi, [rel ed_buf]
    lea rcx, [rel undo_slen]
    mov rcx, [rcx + rax*8]
    mov [rel ed_len], rcx
    lea rdx, [rel undo_scur]
    mov rdx, [rdx + rax*8]
    mov [rel ed_cursor], rdx
    test rcx, rcx
    jz .done
    rep movsb
.done:
    pop rsi
    pop rdi
    pop rcx
    pop rbx
    ret


; ---------------------------------------------------------------- line_start
; rdi = index. Returns in rax the index of the first char of that line.
line_start:
    mov rax, rdi
.ls_back:
    test rax, rax
    jz .ls_done
    lea rcx, [rel ed_buf]
    cmp byte [rcx + rax - 1], 10
    je .ls_done
    dec rax
    jmp .ls_back
.ls_done:
    ret

; ---------------------------------------------------------------- line_end
; rdi = index. Returns in rax the index of the newline ending that line
; (or ed_len at end of buffer).
line_end:
    mov rax, rdi
.le_fwd:
    cmp rax, [rel ed_len]
    jae .le_done
    lea rcx, [rel ed_buf]
    cmp byte [rcx + rax], 10
    je .le_done
    inc rax
    jmp .le_fwd
.le_done:
    ret

; ---------------------------------------------------------------- caret_up
; Move the caret one line up, keeping the column where possible.
caret_up:
    push rbx
    push r12
    mov rdi, [rel ed_cursor]
    call line_start
    mov rbx, rax                    ; current line start
    test rbx, rbx
    jz .cu_done                     ; already on the first line
    mov rdi, [rel ed_cursor]
    sub rdi, rbx                    ; column
    mov r12, rdi
    mov rdi, rbx
    dec rdi                         ; the newline above
    call line_start
    mov rbx, rax                    ; previous line start
    mov rdi, rbx
    call line_end
    add rbx, r12                    ; start + column
    cmp rbx, rax
    jbe .cu_set
    mov rbx, rax                    ; clamp to end of the previous line
.cu_set:
    mov [rel ed_cursor], rbx
.cu_done:
    pop r12
    pop rbx
    ret

; ---------------------------------------------------------------- caret_down
; Move the caret one line down, keeping the column where possible.
caret_down:
    push rbx
    push r12
    mov rdi, [rel ed_cursor]
    call line_start
    mov rbx, rax
    mov rdi, [rel ed_cursor]
    sub rdi, rbx                    ; column
    mov r12, rdi
    mov rdi, [rel ed_cursor]
    call line_end
    cmp rax, [rel ed_len]
    jae .cd_done                    ; already on the last line
    inc rax                         ; start of the next line
    mov rbx, rax
    mov rdi, rbx
    call line_end
    add rbx, r12
    cmp rbx, rax
    jbe .cd_set
    mov rbx, rax
.cd_set:
    mov [rel ed_cursor], rbx
.cd_done:
    pop r12
    pop rbx
    ret

; ---------------------------------------------------------------- handle_key
; rdi = X11 keycode, rsi = event state (modifier mask).
handle_key:
    push rbx
    mov  rbx, rdi
    test rsi, MASK_CONTROL_ST
    jz   .nocontrol
    cmp  rbx, KC_CTRL_R
    je   .run
    cmp  rbx, KC_CTRL_S
    je   .save
    cmp  rbx, KC_CTRL_L
    je   .load
    cmp  rbx, KC_CTRL_Z
    je   .undo
.nocontrol:
    cmp  rbx, KC_ESCAPE
    je   .esc
    cmp  rbx, KC_BACKSPACE
    je   .bs
    cmp  rbx, KC_RETURN
    je   .nl
    cmp  rbx, KC_LEFT
    je   .left
    cmp  rbx, KC_RIGHT
    je   .right
    cmp  rbx, KC_UP
    je   .up
    cmp  rbx, KC_DOWN
    je   .down
    cmp  qword [rel km_ok], 0
    je   .fallback
    lea  rcx, [rel kc_map]
    cmp  rbx, 255
    ja   .done
    movzx edi, byte [rcx + rbx]
    jmp  .have
.fallback:
    lea  rcx, [rel kc_table]
    cmp  rbx, 125
    ja   .done
    movzx edi, byte [rcx + rbx]
.have:
    test edi, edi
    jz   .done
    call ed_insert
    jmp  .done
.bs:
    call ed_backspace
    jmp  .done
.nl:
    mov  rdi, 10
    call ed_insert
    jmp  .done
.run:
    call do_run
    call draw_all
    jmp  .done
.save:
    call save_saved
    jmp  .done
.load:
    call load_saved
    call draw_editor
    jmp  .done
.undo:
    call undo_restore
    call draw_editor
    jmp  .done
.left:
    cmp  qword [rel ed_cursor], 0
    je   .done
    dec  qword [rel ed_cursor]
    jmp  .done
.right:
    mov  rax, [rel ed_cursor]
    cmp  rax, [rel ed_len]
    jae  .done
    inc  qword [rel ed_cursor]
    jmp  .done
.up:
    call caret_up
    jmp  .done
.down:
    call caret_down
    jmp  .done
.esc:
    mov  dword [rel want_quit], 1
.done:
    pop  rbx
    ret

; ---------------------------------------------------------------- _start
_start:
    call connect_x
    cmp rax, -1
    je .nox
    mov r12, rax                    ; socket fd (kept in r12 throughout)

    mov rdi, r12
    call do_handshake
    cmp rax, -1
    je .badhand

    call parse_setup
    mov qword [next_id], 1

    ; ---- window ----------------------------------------------------------
    call create_win
    mov rdi, r12
    lea rsi, [reqbuf]
    mov rdx, 36
    call send_req

    ; ---- graphics context ------------------------------------------------
    call create_gc
    mov rdi, r12
    lea rsi, [reqbuf]
    mov rdx, 24
    call send_req

    ; ---- map -------------------------------------------------------------
    mov byte [reqbuf], X_MapWindow
    mov byte [reqbuf+1], 0
    mov word [reqbuf+2], 2
    mov rax, [our_win]
    mov [reqbuf+4], rax
    mov rdi, r12
    lea rsi, [reqbuf]
    mov rdx, 8
    call send_req

    ; ---- keyboard mapping (slice 4) --------------------------------------
    mov rdi, r12
    call fetch_keymap

    lea rsi, [msg_ok]
    call write_z

    ; ---- event loop ------------------------------------------------------
.loop:
    mov rax, SYS_read
    mov rdi, r12
    lea rsi, [event]
    mov rdx, 32
    syscall
    cmp rax, 32
    jl .done

    movzx r13, byte [event]
    cmp r13, EV_Expose
    je .expose
    cmp r13, EV_KeyPress
    je .key
    jmp .loop

.key:
    movzx rdi, byte [event+1]       ; detail = keycode
    movzx rsi, word [event+28]      ; state (modifier mask)
    call handle_key
    call draw_editor
    cmp  dword [rel want_quit], 0
    jne  .done
    jmp  .loop

.expose:
    call draw_all
    jmp .loop

.done:
    mov rax, SYS_exit
    xor rdi, rdi
    syscall

.nox:
    lea rsi, [msg_nox]
    call write_z
    mov rax, SYS_exit
    mov rdi, 1
    syscall

.badhand:
    lea rsi, [msg_hand]
    call write_z
    mov rax, SYS_exit
    mov rdi, 1
    syscall
