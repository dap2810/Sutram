; ===================================================================
; ROUND-52 WS3: the `yoj` hint.
;
; When a call names no function the program defines or brings in, the compiler
; already says `agyat prakriya: <name>`. If <name> is a library prakriya, it now
; adds, for each module that has it, one line:
;
;   Sutram Error: agyat prakriya: brihat_yuj
;     Sanket: 'brihat_yuj' 'brihat' ghatake asti; 'yoj brihat' iti likhatu
;
; The names come from src/r52_lib_index.inc, which tools/lib_index.py generates
; from lib/*.smlib (gate "R52 lib index" keeps it in step). The hint is a default
; message only - not one of the per-pack sandesh keys - so the ten frozen packs
; are not touched; under --lang it prints in the default (romanised Sanskrit).
; Nothing changes for a program that compiles.
; ===================================================================

%include "src/r52_lib_index.inc"

section .data
    r52_hint_a db "  Sanket: '", 0
    r52_hint_b db "' '", 0
    r52_hint_c db "' ghatake asti; 'yoj ", 0
    r52_hint_d db "' iti likhatu", 10, 0
    r52_w_arabhya   db "arabhya", 0    ; R52 WS4: chakra i = a arabhya b paryantam
    r52_w_paryantam db "paryantam", 0
section .text

; r52_print_yoj_hint(rdi = name). Prints one hint line per module that has a
; library prakriya of that name; nothing if there is none. Preserves rbx, r12-r15.
r52_print_yoj_hint:
    push rbx
    push r12
    push r13
    mov r12, rdi
    lea rbx, [rel r52_lib_index]
.next:
    mov rsi, [rbx]
    test rsi, rsi
    jz .done
    mov rdi, r12
    call strcmp
    test rax, rax
    jnz .skip
    mov r13, [rbx + 8]             ; the module
    lea rdi, [rel r52_hint_a]
    call print_str_z
    mov rdi, r12
    call print_str_z
    lea rdi, [rel r52_hint_b]
    call print_str_z
    mov rdi, r13
    call print_str_z
    lea rdi, [rel r52_hint_c]
    call print_str_z
    mov rdi, r13
    call print_str_z
    lea rdi, [rel r52_hint_d]
    call print_str_z
.skip:
    add rbx, 16
    jmp .next
.done:
    pop r13
    pop r12
    pop rbx
    ret
