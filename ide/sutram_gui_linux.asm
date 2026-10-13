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
;  SLICE 16: selection + an internal clipboard. Shift+arrows / Shift+Home /
;  Shift+End extend a selection, Ctrl-C and Ctrl-X copy or cut it, Ctrl-V
;  pastes at the caret, Ctrl-A selects the whole buffer, and Escape clears a
;  selection before it quits. With no selection, Ctrl-C / Ctrl-X take the
;  current line. The selection is painted as a highlight behind the text.
;
;  SLICE 18: Ctrl-B opens a directory browser - the entries of the current
;  directory are listed in the editor pane, Up/Down select, Enter opens a file
;  or descends into a directory, Backspace goes up one level, Esc cancels.
;  Ctrl-O (open by path) and Ctrl-N (new buffer) are unchanged.
;
;  SLICE 17: Ctrl-O opens a file by path through an "Open:" prompt, Ctrl-N
;  starts a new empty buffer. This slice also fixes a pre-existing defect: the
;  key loop repainted the editor pane after every key, which overpainted the
;  prompt strip (it lies inside the pane) - so the find prompt had never
;  actually been visible. The repaint is now skipped while a prompt is open.
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
%define ED_VISIBLE      ED_LINES_MAX    ; lines visible before scrolling

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
%define KC_PGUP         104             ; output-pane scroll up
%define KC_PGDN         109             ; output-pane scroll down
%define KC_HOME         102             ; caret to line start
%define KC_END          107             ; caret to line end
%define KC_TAB          23              ; insert an indent
%define KC_CTRL_F       41              ; 'f' keycode, checked with ControlMask
; ---- slice 16: clipboard -----------------------------------------------
%define KC_CTRL_A       38              ; 'a' keycode -> select all
%define KC_CTRL_C       54              ; 'c' keycode -> copy
%define KC_CTRL_X       53              ; 'x' keycode -> cut
%define KC_CTRL_V       55              ; 'v' keycode -> paste
%define MASK_SHIFT      0x0001          ; ShiftMask bit in the event state
%define CLIP_CAP        4096            ; internal clipboard capacity
%define COL_SEL         0x2B4A6B        ; selection highlight
; ---- slice 17: open / new ----------------------------------------------
%define KC_CTRL_O       32              ; 'o' keycode -> open a file
%define KC_CTRL_N       57              ; 'n' keycode -> new buffer
%define OPEN_CAP        512             ; typed path capacity
; ---- slice 18: directory browser ---------------------------------------
%define KC_CTRL_B       56              ; 'b' keycode -> browse the directory
%define SYS_getdents64  217
%define BR_MAX          128             ; most entries we will list
%define BR_NAMES_CAP    8192            ; names storage (NUL-separated)
%define BR_DENTS_CAP    8192            ; raw getdents64 buffer
%define BR_PATH_CAP     512
%define O_DIRECTORY     0x10000
%define FIND_CAP        128             ; find-string capacity
%define INDENT_SPACES   4
%define OUT_VISIBLE     7               ; output lines that fit in the pane
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
    ed_top      resq 1               ; first visible editor line (scroll)
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
    out_top     resq 1               ; first visible output line (scroll)
    find_mode   resq 1               ; 1 while the find prompt is open
    find_len    resq 1
    find_buf    resb FIND_CAP
    want_quit   resd 1
    ; ---- slice 16: selection + internal clipboard ----
    sel_anchor  resq 1               ; selection anchor; -1 when there is none
    clip_buf    resb CLIP_CAP        ; internal clipboard bytes
    clip_len    resq 1               ; bytes held in clip_buf
    ; ---- slice 17: open prompt ----
    open_mode   resq 1               ; 1 while the Open: prompt is open
    open_len    resq 1
    open_buf    resb OPEN_CAP        ; typed path
    ; ---- slice 18: directory browser ----
    br_mode     resq 1               ; 1 while the browser is open
    br_count    resq 1               ; entries listed
    br_sel      resq 1               ; selected index
    br_top      resq 1               ; first visible entry
    br_nlen     resq 1               ; bytes used in br_names
    br_path     resb BR_PATH_CAP     ; the directory being browsed
    br_names    resb BR_NAMES_CAP
    br_off      resq BR_MAX          ; name offset per entry
    br_is       resq BR_MAX          ; 1 if the entry is a directory
    br_dents    resb BR_DENTS_CAP

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
    txt_hint    db "Ctrl-R run  Ctrl-S save  Ctrl-O open  Ctrl-N new  Ctrl-C/X/V clip"
    txt_find    db "Find: "
    txt_find_n  equ $ - txt_find
    txt_open    db "Open: "
    txt_open_n  equ $ - txt_open
    txt_browse  db "Browse: "
    txt_browse_n equ $ - txt_browse
    br_dot      db ".", 0
    br_dotdot   db "..", 0
    br_slash    db "/", 0
    txt_hint_n  equ $ - txt_hint
    msg_openfail db "Sutram IDE: cannot open that file.", 10, 0

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

; ---------------------------------------------------------------- out_clamp
; Keep out_top within [0, max(0, out_nlines - OUT_VISIBLE)].
out_clamp:
    mov rax, [rel out_nlines]
    cmp rax, OUT_VISIBLE
    jbe .zero
    sub rax, OUT_VISIBLE
    cmp [rel out_top], rax
    jbe .ret
    mov [rel out_top], rax
.ret:
    ret
.zero:
    mov qword [rel out_top], 0
    ret

; ---------------------------------------------------------------- out_to_bottom
; Auto-scroll so the newest output is visible (called after a run).
out_to_bottom:
    call out_clamp
    mov rax, [rel out_nlines]
    cmp rax, OUT_VISIBLE
    jbe .done
    sub rax, OUT_VISIBLE
    mov [rel out_top], rax
.done:
    ret

; ---------------------------------------------------------------- out_scroll_up
out_scroll_up:
    mov rax, [rel out_top]
    cmp rax, OUT_VISIBLE
    jb  .zero
    sub rax, OUT_VISIBLE
    mov [rel out_top], rax
    ret
.zero:
    mov qword [rel out_top], 0
    ret

; ---------------------------------------------------------------- out_scroll_down
out_scroll_down:
    mov rax, [rel out_top]
    add rax, OUT_VISIBLE
    mov [rel out_top], rax
    call out_clamp
    ret

; Slice 5/11: render the captured run output in the output pane, one line per
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
    ; advance r14 to the first visible line (index out_top)
    lea r14, [rel out_lines]
    mov rcx, [rel out_top]
.adv0:
    test rcx, rcx
    jz .drawn
.adv0l:
    cmp byte [r14], 0
    je .adv0d
    inc r14
    jmp .adv0l
.adv0d:
    inc r14
    dec rcx
    jmp .adv0
.drawn:
    mov rdi, COL_TEXT
    call set_fg
    xor rbx, rbx                    ; display row 0..OUT_VISIBLE-1
.line:
    cmp rbx, OUT_VISIBLE
    jae .done
    mov rax, [rel out_top]
    add rax, rbx
    cmp rax, r13
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

    cmp qword [rel br_mode], 0
    je  .notbr
    call draw_browser
    jmp .brdone
.notbr:
    call draw_prompt
.brdone:
    pop r13
    pop r12
    ret

; ---------------------------------------------------------------- ed_insert
; rdi = character.  Insert at the cursor, bounded by ED_CAP.
ed_insert:
    push rbx
    push rdi
    cmp  qword [rel sel_anchor], 0
    jl   .no_sel
    call sel_lo
    mov  rdi, rax
    call sel_hi
    mov  rsi, rax
    call ed_delete_range
.no_sel:
    pop  rdi
    push rdi
    call snapshot
    pop  rdi
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
    cmp  qword [rel sel_anchor], 0
    jge  .del_sel
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
.del_sel:
    call sel_lo
    mov  rdi, rax
    call sel_hi
    mov  rsi, rax
    call ed_delete_range
    pop  rbx
    ret


; ---------------------------------------------------------------- ed_ensure_visible
; Scroll so the caret's line is inside [ed_top, ed_top + ED_VISIBLE - 1].
ed_ensure_visible:
    push rbx
    call ed_caret_y
    mov  rbx, rax
    cmp  rbx, [rel ed_top]
    jae  .not_above
    mov  [rel ed_top], rbx          ; caret above the window -> scroll up to it
    jmp  .done
.not_above:
    mov  rax, [rel ed_top]
    add  rax, ED_VISIBLE
    cmp  rbx, rax
    jb   .done
    mov  rax, rbx                   ; caret below the window -> scroll down
    sub  rax, ED_VISIBLE - 1
    mov  [rel ed_top], rax
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
    call ed_ensure_visible
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
    mov  rax, [rel ed_top]
    cmp  r13, rax
    jb   .next_line                 ; above the visible window: skip
    mov  rax, r13
    sub  rax, [rel ed_top]          ; display row
    cmp  rax, ED_VISIBLE
    jae  .after                     ; below the visible window: stop

    ; ---- slice 16: selection highlight, painted under the text --------
    cmp  qword [rel sel_anchor], 0
    jl   .no_hl
    mov  rdi, COL_SEL
    call set_fg
    call sel_lo
    mov  r9, rax                    ; selection low
    call sel_hi
    mov  r10, r14                   ; o0 = max(line start, sel low)
    cmp  r9, r10
    jbe  .hl_o0
    mov  r10, r9
.hl_o0:
    mov  rcx, r15                   ; o1 = min(line end, sel high)
    cmp  rax, rcx
    jae  .hl_o1
    mov  rcx, rax
.hl_o1:
    cmp  rcx, r10
    jbe  .hl_none                   ; nothing of this line is selected
    mov  rsi, r10
    sub  rsi, r14
    imul rsi, 8
    add  rsi, ED_TEXT_X             ; x
    sub  rcx, r10
    imul rcx, 8                     ; width
    mov  rdx, r13
    sub  rdx, [rel ed_top]
    imul rdx, LINE_H
    add  rdx, ED_TEXT_Y
    sub  rdx, 12                    ; y
    mov  r8, 14                     ; height
    call fill_rect
    mov  rdi, r12
    lea  rsi, [reqbuf]
    mov  rdx, 20
    call send_req
.hl_none:
    mov  rdi, COL_TEXT
    call set_fg
.no_hl:

    mov  rdx, r15
    sub  rdx, r14                   ; line length
    test rdx, rdx
    jz   .next_line                 ; empty line: nothing to draw
    mov  rsi, rbx
    add  rsi, r14
    mov  rcx, ED_TEXT_X
    mov  r8,  ED_TEXT_Y
    mov  rax, r13
    sub  rax, [rel ed_top]
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
    mov  rcx, rax
    sub  rcx, [rel ed_top]          ; caret row within the window
    cmp  rcx, ED_VISIBLE
    jae  .no_caret                  ; scrolled off: do not draw it
    imul rcx, LINE_H
    add  rcx, ED_TEXT_Y
    sub  rcx, 12
    mov  rdx, rcx
    mov  rcx, 2
    mov  r8,  14
    call fill_rect
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req
.no_caret:

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
    call out_to_bottom
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
    call out_to_bottom
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


; ---------------------------------------------------------------- find_do
; Search ed_buf for find_buf (find_len bytes) starting at the caret; if not
; found, wrap and search from the start. Moves the caret to a hit.
find_do:
    push rbx
    push r12
    push r13
    push r14
    mov  r12, [rel find_len]
    test r12, r12
    jz   .done
    mov  r13, [rel ed_cursor]
    mov  r14, 1
.pass:
    mov  rbx, r13
.scan:
    mov  rax, rbx
    add  rax, r12
    cmp  rax, [rel ed_len]
    ja   .next_pass
    xor  rcx, rcx
.cmp:
    cmp  rcx, r12
    jae  .found
    mov  rax, rbx
    add  rax, rcx
    lea  rdx, [rel ed_buf]
    movzx edi, byte [rdx + rax]
    lea  rdx, [rel find_buf]
    movzx esi, byte [rdx + rcx]
    cmp  edi, esi
    jne  .mismatch
    inc  rcx
    jmp  .cmp
.mismatch:
    inc  rbx
    jmp  .scan
.found:
    mov  [rel ed_cursor], rbx
    jmp  .done
.next_pass:
    test r14, r14
    jz   .done
    xor  r14, r14
    xor  r13, r13
    jmp  .pass
.done:
    pop  r14
    pop  r13
    pop  r12
    pop  rbx
    ret

; ---------------------------------------------------------------- draw_prompt
; The bottom line: the find prompt while searching, the key hint otherwise.
draw_prompt:
    push rbx
    cmp  qword [rel open_mode], 0
    jne  .open
    cmp  qword [rel find_mode], 0
    je   .hint
    mov  rdi, COL_ACCENT
    call set_fg
    lea  rsi, [rel txt_find]
    mov  rdx, txt_find_n
    mov  rcx, PANE_X + 8
    mov  r8,  ED_Y + ED_H - 12
    call draw_text
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req
    mov  rdi, COL_TEXT
    call set_fg
    lea  rsi, [rel find_buf]
    mov  rdx, [rel find_len]
    mov  rcx, PANE_X + 8 + 48
    mov  r8,  ED_Y + ED_H - 12
    call draw_text
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req
    jmp  .done
.open:
    mov  rdi, COL_ACCENT
    call set_fg
    lea  rsi, [rel txt_open]
    mov  rdx, txt_open_n
    mov  rcx, PANE_X + 8
    mov  r8,  ED_Y + ED_H - 12
    call draw_text
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req
    mov  rdi, COL_TEXT
    call set_fg
    lea  rsi, [rel open_buf]
    mov  rdx, [rel open_len]
    mov  rcx, PANE_X + 8 + 48
    mov  r8,  ED_Y + ED_H - 12
    call draw_text
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req
    jmp  .done
.hint:
    mov  rdi, COL_TEXT
    call set_fg
    lea  rsi, [rel txt_hint]
    mov  rdx, txt_hint_n
    mov  rcx, PANE_X + 8
    mov  r8,  ED_Y + ED_H - 12
    call draw_text
    mov  rdi, r12
    lea  rsi, [reqbuf]
    call send_req
.done:
    pop  rbx
    ret

; ================================================================ slice 16
; Selection + internal clipboard.
;   sel_anchor = -1  -> no selection
;   sel_anchor >= 0  -> the selection spans
;                       [min(cursor,anchor), max(cursor,anchor))
; ========================================================================

; ---- sel_begin : if there is no selection yet, anchor it at the caret -----
sel_begin:
    cmp qword [rel sel_anchor], 0
    jge .done
    mov rax, [rel ed_cursor]
    mov [rel sel_anchor], rax
.done:
    ret

; ---- sel_clear : drop any selection --------------------------------------
sel_clear:
    mov qword [rel sel_anchor], -1
    ret

; ---- sel_lo : rax = low end of the selection (caret if none) -------------
sel_lo:
    mov rax, [rel ed_cursor]
    mov rcx, [rel sel_anchor]
    test rcx, rcx
    js  .done
    cmp rcx, rax
    jae .done
    mov rax, rcx
.done:
    ret

; ---- sel_hi : rax = high end of the selection (caret if none) ------------
sel_hi:
    mov rax, [rel ed_cursor]
    mov rcx, [rel sel_anchor]
    test rcx, rcx
    js  .done
    cmp rcx, rax
    jbe .done
    mov rax, rcx
.done:
    ret

; ---- ed_delete_range : rdi = lo, rsi = hi. Delete [lo,hi); caret to lo ----
ed_delete_range:
    push rbx
    push rdi
    push rsi
    call snapshot
    pop rsi
    pop rdi
    lea rbx, [rel ed_buf]
    mov rax, [rel ed_len]
    mov rcx, rdi                    ; dst
    mov rdx, rsi                    ; src
.shift:
    cmp rdx, rax
    jae .shrink
    mov r8b, [rbx + rdx]
    mov [rbx + rcx], r8b
    inc rcx
    inc rdx
    jmp .shift
.shrink:
    mov rcx, rsi
    sub rcx, rdi                    ; bytes removed
    sub qword [rel ed_len], rcx
    mov [rel ed_cursor], rdi
    mov qword [rel sel_anchor], -1
    pop rbx
    ret

; ---- clip_copy : rdi = lo, rsi = hi. Copy [lo,hi) into clip_buf ----------
clip_copy:
    push rbx
    push r12
    lea rbx, [rel ed_buf]
    lea r12, [rel clip_buf]
    mov rcx, rsi
    sub rcx, rdi
    cmp rcx, CLIP_CAP - 1
    jbe .fit
    mov rcx, CLIP_CAP - 1
.fit:
    mov [rel clip_len], rcx
    xor rdx, rdx
.loop:
    cmp rdx, rcx
    jae .done
    mov al, [rbx + rdi]
    mov [r12 + rdx], al
    inc rdi
    inc rdx
    jmp .loop
.done:
    pop r12
    pop rbx
    ret

; ---- clip_paste : insert clip_buf[0..clip_len) at the caret --------------
clip_paste:
    push rbx
    push r12
    push r13
    push r14
    mov r13, [rel clip_len]
    test r13, r13
    jz .done
    mov rax, [rel ed_len]
    mov rcx, rax
    add rcx, r13
    cmp rcx, ED_CAP - 2
    jbe .room
    mov r13, ED_CAP - 2
    sub r13, rax
    jle .done                       ; no room at all
.room:
    call snapshot
    lea rbx, [rel ed_buf]
    lea r12, [rel clip_buf]
    mov r14, [rel ed_cursor]
    mov rax, [rel ed_len]           ; i = old length
.shift:
    cmp rax, r14
    jbe .copyin
    dec rax
    mov r8b, [rbx + rax]
    lea rcx, [rax + r13]
    mov [rbx + rcx], r8b
    jmp .shift
.copyin:
    mov rdi, r14
    xor rdx, rdx
.cp:
    cmp rdx, r13
    jae .fin
    mov al, [r12 + rdx]
    mov [rbx + rdi], al
    inc rdi
    inc rdx
    jmp .cp
.fin:
    add qword [rel ed_len], r13
    add qword [rel ed_cursor], r13
    mov qword [rel sel_anchor], -1
.done:
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ---- clip_line_bounds : rdi = lo, rsi = hi for the caret's whole line ----
clip_line_bounds:
    push rbx
    mov rdi, [rel ed_cursor]
    call line_start
    mov rbx, rax
    mov rdi, [rel ed_cursor]
    call line_end
    mov rsi, rax
    mov rdi, rbx
    pop rbx
    ret

; ================================================================ slice 17
; Ctrl-O: open a file by path (an "Open:" prompt); Ctrl-N: a new buffer.
; ========================================================================

; ---- open_do : load open_buf into the editor buffer. 0 ok, -1 error ------
open_do:
    push rbx
    push r12
    mov rax, [rel open_len]
    test rax, rax
    jz .fail                        ; an empty path is not an open
    mov rax, SYS_open
    lea rdi, [rel open_buf]
    xor rsi, rsi                    ; O_RDONLY
    xor rdx, rdx
    syscall
    cmp rax, 0
    jl .fail
    mov rbx, rax
    call snapshot                   ; the old buffer is still intact here
    mov rax, SYS_read
    mov rdi, rbx
    lea rsi, [rel ed_buf]
    mov rdx, ED_CAP - 2
    syscall
    cmp rax, 0
    jl .closefail
    mov r12, rax
    mov rax, SYS_close
    mov rdi, rbx
    syscall
    mov [rel ed_len], r12
    mov qword [rel ed_cursor], 0
    mov qword [rel ed_top], 0
    mov qword [rel sel_anchor], -1
    xor rax, rax
    pop r12
    pop rbx
    ret
.closefail:
    mov rax, SYS_close
    mov rdi, rbx
    syscall
.fail:
    call open_error
    mov rax, -1
    pop r12
    pop rbx
    ret

; ---- open_error : report a failed open in the output pane ----------------
open_error:
    push rbx
    push rcx
    push rdi
    push rsi
    lea rsi, [rel msg_openfail]
    lea rdi, [rel run_out]
    xor rcx, rcx
.cp:
    mov al, [rsi]
    test al, al
    jz .fin
    mov [rdi], al
    inc rsi
    inc rdi
    inc rcx
    jmp .cp
.fin:
    mov [rel run_out_len], rcx
    call split_lines
    call out_to_bottom
    pop rsi
    pop rdi
    pop rcx
    pop rbx
    ret

; ================================================================ slice 18
; Directory browser.
; ========================================================================

; ---- br_load : read br_path into br_names/br_off/br_is/br_count --------
; returns 0 on success, -1 on failure.
br_load:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov qword [rel br_nlen], 0
    mov qword [rel br_count], 0
    mov qword [rel br_sel], 0
    mov qword [rel br_top], 0
    mov rax, SYS_open
    lea rdi, [rel br_path]
    mov rsi, O_DIRECTORY
    xor rdx, rdx
    syscall
    cmp rax, 0
    jl .fail
    mov r12, rax
    mov rax, SYS_getdents64
    mov rdi, r12
    lea rsi, [rel br_dents]
    mov rdx, BR_DENTS_CAP
    syscall
    mov r13, rax                    ; bytes read (or -1)
    push r13
    mov rax, SYS_close
    mov rdi, r12
    syscall
    pop r13
    cmp r13, 0
    jle .fail
    lea rbx, [rel br_dents]
    xor r14, r14                    ; walk offset
    xor r15, r15                    ; entry count
.parse:
    cmp r14, r13
    jae .ok
    cmp r15, BR_MAX
    jae .ok
    movzx r9d, word [rbx + r14 + 16] ; d_reclen
    test r9, r9
    jz .ok
    lea rsi, [rbx + r14 + 19]        ; d_name
    ; skip "." and ".."
    cmp byte [rsi], '.'
    jne .keep
    cmp byte [rsi + 1], 0
    je .skip
    cmp byte [rsi + 1], '.'
    jne .keep
    cmp byte [rsi + 2], 0
    je .skip
.keep:
    movzx eax, byte [rbx + r14 + 18] ; d_type
    cmp al, 4                        ; DT_DIR
    sete al
    movzx eax, al
    lea rdi, [rel br_is]
    mov [rdi + r15*8], rax
    lea rdi, [rel br_off]
    mov rax, [rel br_nlen]
    mov [rdi + r15*8], rax
    lea rdi, [rel br_names]
    add rdi, rax
.cp:
    mov dl, [rsi]
    mov [rdi], dl
    inc rsi
    inc rdi
    inc rax
    test dl, dl
    jz .cpd
    jmp .cp
.cpd:
    mov [rel br_nlen], rax
    inc r15
.skip:
    add r14, r9
    jmp .parse
.ok:
    mov [rel br_count], r15
    xor rax, rax
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret
.fail:
    mov rax, -1
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ---- br_open_sel : Enter. If the selection is a directory, descend; -----
; otherwise open the file. Returns 0 ok, -1 error.
br_open_sel:
    push rbx
    push r12
    mov rax, [rel br_sel]
    cmp rax, [rel br_count]
    jae .fail
    lea rdi, [rel br_off]
    mov r12, [rdi + rax*8]          ; name offset
    lea rdi, [rel br_is]
    mov rbx, [rdi + rax*8]          ; is-dir
    ; build the full path into open_buf (reuse the path prompt buffer)
    lea rsi, [rel br_path]
    lea rdi, [rel open_buf]
    xor rcx, rcx
.cpdir:
    mov al, [rsi]
    test al, al
    jz .sep
    mov [rdi], al
    inc rsi
    inc rdi
    inc rcx
    jmp .cpdir
.sep:
    mov byte [rdi], '/'
    inc rdi
    inc rcx
    lea rsi, [rel br_names]
    add rsi, r12
.cpname:
    mov al, [rsi]
    mov [rdi], al
    inc rsi
    inc rdi
    inc rcx
    test al, al
    jz .cped
    jmp .cpname
.cped:
    mov [rel open_len], rcx
    test rbx, rbx
    jz .openfile
    ; ---- directory: make it the new br_path and reload ----
    lea rsi, [rel open_buf]
    lea rdi, [rel br_path]
    xor rcx, rcx
.todir:
    mov al, [rsi]
    mov [rdi], al
    inc rsi
    inc rdi
    test al, al
    jz .reload
    jmp .todir
.reload:
    call br_load
    mov rax, 1                      ; 1 = we descended, stay in the browser
    pop r12
    pop rbx
    ret
.openfile:
    call open_do
    xor rax, rax                    ; 0 = a file was opened, leave the browser
    pop r12
    pop rbx
    ret
.fail:
    mov rax, -1
    pop r12
    pop rbx
    ret

; ---- br_up : Backspace. Drop the last path component and reload. --------
br_up:
    push rbx
    lea rbx, [rel br_path]
    xor rcx, rcx
.findend:
    cmp byte [rbx + rcx], 0
    je .back
    inc rcx
    jmp .findend
.back:
    cmp rcx, 1
    jbe .done
    dec rcx
.trim:
    cmp rcx, 0
    jbe .set
    cmp byte [rbx + rcx], '/'
    je .set
    dec rcx
    jmp .trim
.set:
    test rcx, rcx
    jnz .put
    mov byte [rbx + 1], 0           ; keep at least "/"
    jmp .done
.put:
    mov byte [rbx + rcx], 0
.done:
    call br_load
    pop rbx
    ret

; ---- draw_browser : paint the list into the editor pane -----------------
draw_browser:
    push rbx
    push r12
    push r13
    push r14
    push r15
    ; pane background
    mov rdi, COL_PANE
    call set_fg
    mov rsi, PANE_X
    mov rdx, ED_Y
    mov rcx, ED_W
    mov r8,  ED_H
    call fill_rect
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req
    ; heading
    mov rdi, COL_ACCENT
    call set_fg
    lea rsi, [rel txt_browse]
    mov rdx, txt_browse_n
    mov rcx, ED_TEXT_X
    mov r8,  ED_TEXT_Y
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req
    ; entries
    xor r13, r13                    ; display row
    mov r14, [rel br_top]           ; entry index
.loop:
    cmp r13, ED_VISIBLE - 1
    jae .after
    cmp r14, [rel br_count]
    jae .after
    ; highlight the selected row
    cmp r14, [rel br_sel]
    jne .text
    mov rdi, COL_SEL
    call set_fg
    mov rsi, ED_TEXT_X
    mov rdx, ED_TEXT_Y
    imul rax, r13, LINE_H
    add rdx, rax
    sub rdx, 12
    mov rcx, ED_W - 16
    mov r8, 14
    call fill_rect
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req
.text:
    mov rdi, COL_TEXT
    call set_fg
    ; name = br_names + br_off[i]
    lea rdi, [rel br_off]
    mov rbx, [rdi + r14*8]
    lea rsi, [rel br_names]
    add rsi, rbx
    ; length
    xor rdx, rdx
.len:
    cmp byte [rsi + rdx], 0
    je .lenend
    inc rdx
    cmp rdx, 240
    jae .lenend
    jmp .len
.lenend:
    test rdx, rdx
    jz .next
    mov rcx, ED_TEXT_X
    mov r8,  ED_TEXT_Y
    imul rax, r13, LINE_H
    add r8, rax
    ; mark directories with a trailing '/'
    lea rdi, [rel br_is]
    cmp qword [rdi + r14*8], 0
    je .draw
    lea rdi, [rel br_names]
    add rdi, rbx
    add rdi, rdx
    mov byte [rdi], '/'
    inc rdx
.draw:
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req
.next:
    inc r13
    inc r14
    jmp .loop
.after:
    ; the current directory, in the prompt strip
    mov rdi, COL_ACCENT
    call set_fg
    lea rsi, [rel br_path]
    xor rdx, rdx
.plen:
    cmp byte [rsi + rdx], 0
    je .pend
    inc rdx
    cmp rdx, 200
    jae .pend
    jmp .plen
.pend:
    mov rcx, PANE_X + 8
    mov r8,  ED_Y + ED_H - 12
    call draw_text
    mov rdi, r12
    lea rsi, [reqbuf]
    call send_req
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

; ---- br_start : Ctrl-B. Begin browsing the current directory -----------
br_start:
    mov qword [rel br_mode], 1
    lea rsi, [rel br_dot]
    lea rdi, [rel br_path]
    mov al, '.'
    mov [rdi], al
    mov byte [rdi + 1], 0
    call br_load
    call draw_all
    ret

; ---------------------------------------------------------------- handle_key
; rdi = X11 keycode, rsi = event state (modifier mask).
handle_key:
    push rbx
    mov  rbx, rdi
    cmp  qword [rel br_mode], 0
    jne  .brkey
    cmp  qword [rel open_mode], 0
    jne  .openkey
    cmp  qword [rel find_mode], 0
    jne  .findkey
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
    cmp  rbx, KC_CTRL_F
    je   .findopen
    cmp  rbx, KC_CTRL_A
    je   .selall
    cmp  rbx, KC_CTRL_C
    je   .copy
    cmp  rbx, KC_CTRL_X
    je   .cut
    cmp  rbx, KC_CTRL_V
    je   .paste
    cmp  rbx, KC_CTRL_O
    je   .openopen
    cmp  rbx, KC_CTRL_N
    je   .newbuf
    cmp  rbx, KC_CTRL_B
    je   .browse
    cmp  rbx, KC_HOME
    je   .ctop
    cmp  rbx, KC_END
    je   .cend
    jmp  .done
.nocontrol:
    test rsi, MASK_SHIFT
    jz   .plain
    cmp  rbx, KC_LEFT
    je   .sleft
    cmp  rbx, KC_RIGHT
    je   .sright
    cmp  rbx, KC_UP
    je   .sup
    cmp  rbx, KC_DOWN
    je   .sdown
    cmp  rbx, KC_HOME
    je   .shome
    cmp  rbx, KC_END
    je   .send
.plain:
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
    cmp  rbx, KC_PGUP
    je   .pgup
    cmp  rbx, KC_PGDN
    je   .pgdn
    cmp  rbx, KC_HOME
    je   .home
    cmp  rbx, KC_END
    je   .end
    cmp  rbx, KC_TAB
    je   .tab
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
    call sel_clear
    cmp  qword [rel ed_cursor], 0
    je   .done
    dec  qword [rel ed_cursor]
    jmp  .done
.right:
    call sel_clear
    mov  rax, [rel ed_cursor]
    cmp  rax, [rel ed_len]
    jae  .done
    inc  qword [rel ed_cursor]
    jmp  .done
.up:
    call sel_clear
    call caret_up
    jmp  .done
.down:
    call sel_clear
    call caret_down
    jmp  .done
.pgup:
    call out_scroll_up
    call draw_all
    jmp  .done
.pgdn:
    call out_scroll_down
    call draw_all
    jmp  .done
.home:
    call sel_clear
    mov  rdi, [rel ed_cursor]
    call line_start
    mov  [rel ed_cursor], rax
    jmp  .done
.end:
    call sel_clear
    mov  rdi, [rel ed_cursor]
    call line_end
    mov  [rel ed_cursor], rax
    jmp  .done
.findopen:
    mov  qword [rel find_mode], 1
    mov  qword [rel find_len], 0
    lea  rcx, [rel find_buf]
    mov  byte [rcx], 0
    call draw_all
    jmp  .done
.findkey:
    cmp  rbx, KC_ESCAPE
    je   .fcancel
    cmp  rbx, KC_RETURN
    je   .faccept
    cmp  rbx, KC_BACKSPACE
    je   .fback
    cmp  qword [rel km_ok], 0
    je   .ffallback
    lea  rcx, [rel kc_map]
    cmp  rbx, 255
    ja   .done
    movzx edi, byte [rcx + rbx]
    jmp  .fhave
.ffallback:
    lea  rcx, [rel kc_table]
    cmp  rbx, 125
    ja   .done
    movzx edi, byte [rcx + rbx]
.fhave:
    test edi, edi
    jz   .done
    mov  rax, [rel find_len]
    cmp  rax, FIND_CAP - 1
    jae  .done
    lea  rcx, [rel find_buf]
    mov  [rcx + rax], dil
    inc  rax
    mov  [rel find_len], rax
    mov  byte [rcx + rax], 0
    call draw_all
    jmp  .done
.fcancel:
    mov  qword [rel find_mode], 0
    call draw_all
    jmp  .done
.faccept:
    call find_do
    mov  qword [rel find_mode], 0
    call draw_all
    jmp  .done
.fback:
    mov  rax, [rel find_len]
    test rax, rax
    jz   .done
    dec  rax
    mov  [rel find_len], rax
    lea  rcx, [rel find_buf]
    mov  byte [rcx + rax], 0
    call draw_all
    jmp  .done
.ctop:
    mov  qword [rel ed_cursor], 0
    jmp  .done
.cend:
    mov  rax, [rel ed_len]
    mov  [rel ed_cursor], rax
    jmp  .done
.tab:
    mov  rbx, INDENT_SPACES
.tabloop:
    mov  rdi, 32
    call ed_insert
    dec  rbx
    jnz  .tabloop
    jmp  .done
; ---- slice 16: clipboard + selection --------------------------------
.selall:
    mov  qword [rel sel_anchor], 0
    mov  rax, [rel ed_len]
    mov  [rel ed_cursor], rax
    jmp  .done
.copy:
    cmp  qword [rel sel_anchor], 0
    jge  .copy_sel
    call clip_line_bounds           ; rdi = lo, rsi = hi of the current line
    call clip_copy
    jmp  .done
.copy_sel:
    call sel_lo
    mov  rdi, rax
    call sel_hi
    mov  rsi, rax
    call clip_copy
    call sel_clear
    jmp  .done
.cut:
    cmp  qword [rel sel_anchor], 0
    jge  .cut_sel
    call clip_line_bounds
    cmp  rsi, [rel ed_len]
    jae  .cut_nolines
    inc  rsi                        ; take the trailing newline too
.cut_nolines:
    push rdi
    push rsi
    call clip_copy
    pop  rsi
    pop  rdi
    call ed_delete_range
    jmp  .done
.cut_sel:
    call sel_lo
    mov  rdi, rax
    call sel_hi
    mov  rsi, rax
    push rdi
    push rsi
    call clip_copy
    pop  rsi
    pop  rdi
    call ed_delete_range
    jmp  .done
.paste:
    cmp  qword [rel sel_anchor], 0
    jl   .paste_go
    call sel_lo
    mov  rdi, rax
    call sel_hi
    mov  rsi, rax
    call ed_delete_range
.paste_go:
    call clip_paste
    jmp  .done
.sleft:
    cmp  qword [rel ed_cursor], 0
    je   .done
    call sel_begin
    dec  qword [rel ed_cursor]
    jmp  .done
.sright:
    mov  rax, [rel ed_cursor]
    cmp  rax, [rel ed_len]
    jae  .done
    call sel_begin
    inc  qword [rel ed_cursor]
    jmp  .done
.sup:
    call sel_begin
    call caret_up
    jmp  .done
.sdown:
    call sel_begin
    call caret_down
    jmp  .done
.shome:
    call sel_begin
    mov  rdi, [rel ed_cursor]
    call line_start
    mov  [rel ed_cursor], rax
    jmp  .done
.send:
    call sel_begin
    mov  rdi, [rel ed_cursor]
    call line_end
    mov  [rel ed_cursor], rax
    jmp  .done
; ---- slice 18: directory browser ------------------------------------
.browse:
    call br_start
    jmp  .done
.brkey:
    cmp  rbx, KC_ESCAPE
    je   .brcancel
    cmp  rbx, KC_RETURN
    je   .braccept
    cmp  rbx, KC_BACKSPACE
    je   .brup
    cmp  rbx, KC_UP
    je   .brupsel
    cmp  rbx, KC_DOWN
    je   .brdnsel
    jmp  .done
.brcancel:
    mov  qword [rel br_mode], 0
    call draw_all
    jmp  .done
.braccept:
    call br_open_sel
    cmp  rax, 1
    je   .brstay
    mov  qword [rel br_mode], 0
.brstay:
    call draw_all
    jmp  .done
.brup:
    call br_up
    call draw_all
    jmp  .done
.brupsel:
    cmp  qword [rel br_sel], 0
    je   .brdraw
    dec  qword [rel br_sel]
    ; keep the selection visible
    mov  rax, [rel br_sel]
    cmp  rax, [rel br_top]
    jae  .brdraw
    mov  [rel br_top], rax
.brdraw:
    call draw_all
    jmp  .done
.brdnsel:
    mov  rax, [rel br_sel]
    inc  rax
    cmp  rax, [rel br_count]
    jae  .brdraw
    mov  [rel br_sel], rax
    ; keep the selection visible
    mov  rcx, [rel br_top]
    add  rcx, ED_VISIBLE - 1
    cmp  rax, rcx
    jb   .brdraw
    sub  rax, ED_VISIBLE - 2
    mov  [rel br_top], rax
    jmp  .brdraw

; ---- slice 17: open / new -------------------------------------------
.openopen:
    mov  qword [rel open_mode], 1
    mov  qword [rel open_len], 0
    lea  rcx, [rel open_buf]
    mov  byte [rcx], 0
    call draw_all
    jmp  .done
.newbuf:
    call snapshot
    mov  qword [rel ed_len], 0
    mov  qword [rel ed_cursor], 0
    mov  qword [rel ed_top], 0
    mov  qword [rel sel_anchor], -1
    jmp  .done
.openkey:
    cmp  rbx, KC_ESCAPE
    je   .ocancel
    cmp  rbx, KC_RETURN
    je   .oaccept
    cmp  rbx, KC_BACKSPACE
    je   .oback
    cmp  qword [rel km_ok], 0
    je   .ofallback
    lea  rcx, [rel kc_map]
    cmp  rbx, 255
    ja   .done
    movzx edi, byte [rcx + rbx]
    jmp  .ohave
.ofallback:
    lea  rcx, [rel kc_table]
    cmp  rbx, 125
    ja   .done
    movzx edi, byte [rcx + rbx]
.ohave:
    test edi, edi
    jz   .done
    mov  rax, [rel open_len]
    cmp  rax, OPEN_CAP - 1
    jae  .done
    lea  rcx, [rel open_buf]
    mov  [rcx + rax], dil
    inc  rax
    mov  [rel open_len], rax
    mov  byte [rcx + rax], 0
    call draw_all
    jmp  .done
.ocancel:
    mov  qword [rel open_mode], 0
    call draw_all
    jmp  .done
.oaccept:
    call open_do
    mov  qword [rel open_mode], 0
    call draw_all
    jmp  .done
.oback:
    mov  rax, [rel open_len]
    test rax, rax
    jz   .done
    dec  rax
    mov  [rel open_len], rax
    lea  rcx, [rel open_buf]
    mov  byte [rcx + rax], 0
    call draw_all
    jmp  .done
.esc:
    cmp  qword [rel sel_anchor], 0
    jl   .esc_quit
    call sel_clear                  ; Escape clears a selection before quitting
    jmp  .done
.esc_quit:
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
    mov qword [rel sel_anchor], -1   ; no selection to start

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
    ; slice 17 fix: while a prompt is open the handler has already repainted
    ; the whole window, and draw_editor would overpaint the prompt strip
    ; (it lies inside the editor pane).
    cmp  qword [rel find_mode], 0
    jne  .key_drawn
    cmp  qword [rel open_mode], 0
    jne  .key_drawn
    cmp  qword [rel br_mode], 0
    jne  .key_drawn
    call draw_editor
.key_drawn:
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
