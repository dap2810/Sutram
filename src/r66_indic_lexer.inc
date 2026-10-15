; R66 lexer helpers. Pure NASM; no OS calls or new runtime dependencies.
; R68 adds Odia/Tamil/Telugu/Kannada; Hindi/Marathi reuse Devanagari.
; R67 adds Bengali (U+09E6..09EF) and Gurmukhi (U+0A66..0A6F).
; Decimal recognition is lexical, independent of the active keyword pack.
; Input RDI=current source byte, RSI=exclusive source end (valid ordered range).
; r66_decimal_digit_at: RAX=0..9, EDX=1 or 3; otherwise RAX=-1, EDX=0.
; All other registers, especially RCX and R8-R11 used by lex, are preserved.
; These are compiler-host functions, NOT code emitted into a Sutram program.

section .data
r66_msg_bad_utf8:
    db "Sutram Error [E_UTF8]: invalid or truncated Indic identifier", 10, 0
section .text

r66_decimal_digit_at:
    xor edx, edx
    cmp rdi, rsi
    jae .bad
    movzx eax, byte [rdi]
    cmp eax, 48
    jb .indic
    cmp eax, 57
    ja .indic
    sub eax, 48
    mov edx, 1
    ret
.indic:
    cmp eax, 0xE0
    jne .bad
    mov rax, rsi
    sub rax, rdi
    cmp rax, 3
    jb .bad
    cmp byte [rdi+1], 0xA5    ; U+0966..096F (Devanagari)
    je .last
    cmp byte [rdi+1], 0xAB    ; U+0AE6..0AEF (Gujarati)
    je .last
    cmp byte [rdi+1], 0xA7    ; U+09E6..09EF (Bengali)
    je .last
    cmp byte [rdi+1], 0xA9    ; U+0A66..0A6F (Gurmukhi)
    je .last
    cmp byte [rdi+1], 0xAD    ; U+0B66..0B6F (Odia)
    je .last
    cmp byte [rdi+1], 0xAF    ; U+0BE6..0BEF (Tamil)
    je .last
    cmp byte [rdi+1], 0xB1    ; U+0C66..0C6F (Telugu)
    je .last
    cmp byte [rdi+1], 0xB3    ; U+0CE6..0CEF (Kannada)
    jne .bad
.last:
    movzx eax, byte [rdi+2]
    sub eax, 0xA6
    cmp eax, 9
    ja .bad
    mov edx, 3
    ret
.bad:
    mov rax, -1
    xor edx, edx
    ret

r66_is_danda_at:
    ; RAX=1 only for complete E0 A5 A4/A5. RSI need not have a NUL sentinel.
    xor eax, eax
    cmp rdi, rsi
    jae .no
    mov rax, rsi
    sub rax, rdi
    cmp rax, 3
    jb .zero
    cmp byte [rdi], 0xE0
    jne .zero
    cmp byte [rdi+1], 0xA5
    jne .zero
    cmp byte [rdi+2], 0xA4
    je .yes
    cmp byte [rdi+2], 0xA5
    jne .zero
.yes:
    mov eax, 1
    ret
.zero:
    xor eax, eax
.no:
    ret

r66_indic_scalar_width:
    ; Existing lexer uses E0 as an Indic start. Validate the entire scalar
    ; before copying all three bytes. E0 A0..BF 80..BF excludes overlong UTF-8.
    xor eax, eax
    cmp rdi, rsi
    jae .no
    mov rax, rsi
    sub rax, rdi
    cmp rax, 3
    jb .zero
    cmp byte [rdi], 0xE0
    jne .zero
    cmp byte [rdi+1], 0xA0
    jb .zero
    cmp byte [rdi+1], 0xBF
    ja .zero
    cmp byte [rdi+2], 0x80
    jb .zero
    cmp byte [rdi+2], 0xBF
    ja .zero
    mov eax, 3
    ret
.zero:
    xor eax, eax
.no:
    ret
