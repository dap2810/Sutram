; R68 bounded UTF-8 helpers. Pure NASM, no allocation, I/O or OS calls.
; RDI=first byte, RSI=exclusive end. RAX=scalar width (1..4) or 0 invalid.
; Only RAX/RDX are clobbered; do not read a continuation before range proof.
section .text
r68_utf8_width:
    xor eax,eax
    cmp rdi,rsi
    jae .no
    movzx eax,byte [rdi]
    cmp eax,0x80
    jb .one
    cmp eax,0xC2
    jb .zero
    cmp eax,0xDF
    jbe .two
    cmp eax,0xEF
    jbe .three
    cmp eax,0xF4
    jbe .four
.zero:
    xor eax,eax
.no:
    ret
.one:
    mov eax,1
    ret
.two:
    mov rdx,rsi
    sub rdx,rdi
    cmp rdx,2
    jb .zero
    movzx edx,byte [rdi+1]
    sub edx,0x80
    cmp edx,0x3F
    ja .zero
    mov eax,2
    ret
.three:
    mov rdx,rsi
    sub rdx,rdi
    cmp rdx,3
    jb .zero
    movzx edx,byte [rdi+1]
    cmp edx,0x80
    jb .zero
    cmp edx,0xBF
    ja .zero
    cmp eax,0xE0
    jne .surrogate
    cmp edx,0xA0
    jb .zero
.surrogate:
    cmp eax,0xED
    jne .third
    cmp edx,0xA0
    jae .zero
.third:
    movzx edx,byte [rdi+2]
    sub edx,0x80
    cmp edx,0x3F
    ja .zero
    mov eax,3
    ret
.four:
    mov rdx,rsi
    sub rdx,rdi
    cmp rdx,4
    jb .zero
    movzx edx,byte [rdi+1]
    cmp edx,0x80
    jb .zero
    cmp edx,0xBF
    ja .zero
    cmp eax,0xF0
    jne .max_scalar
    cmp edx,0x90
    jb .zero
.max_scalar:
    cmp eax,0xF4
    jne .four_tail
    cmp edx,0x90
    jae .zero
.four_tail:
    movzx edx,byte [rdi+2]
    sub edx,0x80
    cmp edx,0x3F
    ja .zero
    movzx edx,byte [rdi+3]
    sub edx,0x80
    cmp edx,0x3F
    ja .zero
    mov eax,4
    ret

; Exact terminal signs currently used by reviewed packs; not prefix expansion.
; RDI/RSI bounded lexeme; EAX=1 for U+0970/09FD/0A76/0AF0 suffix, else 0.
r68_ends_abbreviation:
    xor eax,eax
    cmp rdi,rsi
    jae .no
    mov rdx,rsi
    sub rdx,rdi
    cmp rdx,3
    jb .no
    cmp byte [rsi-3],0xE0
    jne .no
    movzx edx,byte [rsi-2]
    cmp edx,0xA5
    je .b0
    cmp edx,0xAB
    je .b0
    cmp edx,0xA7
    je .bd
    cmp edx,0xA9
    jne .no
    cmp byte [rsi-1],0xB6
    je .yes
    ret
.b0:
    cmp byte [rsi-1],0xB0
    je .yes
    ret
.bd:
    cmp byte [rsi-1],0xBD
    jne .no
.yes:
    mov eax,1
.no:
    ret
