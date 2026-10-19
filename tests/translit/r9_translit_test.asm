; Linux harness for windows/gui/r9_translit.asm (R9, WS6).
; stdin: lines "<pack index> <ascii word>"; stdout: the UTF-16LE result of each,
; followed by U+000A. tests/translit/test_translit.py compares it with
; tools/translit.py.
bits 64
default rel
section .bss
inbuf  resb 1 << 20
outbuf resb 1 << 22
section .text
global _start
%include "windows/gui/r9_translit.asm"
_start:
    ; read all of stdin
    xor r12d, r12d                  ; bytes read
.rd:
    mov eax, 0
    mov edi, 0
    lea rsi, [inbuf + r12]
    mov edx, (1 << 20) - 1
    sub edx, r12d
    syscall
    test rax, rax
    jle .parse
    add r12, rax
    jmp .rd
.parse:
    lea r13, [inbuf]                ; cursor
    lea r14, [inbuf + r12]          ; end
    lea rdi, [outbuf]
.line:
    cmp r13, r14
    jae .write
    ; pack index (decimal)
    xor edx, edx
.num:
    movzx eax, byte [r13]
    cmp al, '0'
    jb .num_end
    cmp al, '9'
    ja .num_end
    imul edx, edx, 10
    sub eax, '0'
    add edx, eax
    inc r13
    jmp .num
.num_end:
    inc r13                         ; the space
    mov rsi, r13
.word:
    cmp r13, r14
    jae .word_end
    cmp byte [r13], 10
    je .word_end
    inc r13
    jmp .word
.word_end:
    mov rcx, r13
    sub rcx, rsi
    test ecx, ecx
    jz .nl
    call r9_tl_phonetic
    lea rdi, [rdi + rax * 2]
.nl:
    mov word [rdi], 10
    add rdi, 2
    inc r13
    jmp .line
.write:
    lea rsi, [outbuf]
    mov rdx, rdi
    sub rdx, rsi
    mov eax, 1
    mov edi, 1
    syscall
    mov eax, 60
    xor edi, edi
    syscall
