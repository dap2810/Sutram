; R66 scoped Indic editor clusters, NOT a glyph shaper or complete UAX #29.
; Devanagari/Gujarati base+marks, virama-linked same-script consonants,
; ZWJ continuation and ZWNJ visible-virama boundary; strict UTF-8 decoding.
; Windows x64 callable ABI:
;   RCX = start byte, RDX = exclusive end -> RAX = next cluster byte pointer.
; Never split a valid UTF-8 scalar. Malformed input advances ONE byte.
; Empty range returns start. Does not dereference start when start >= end.
; Does not compute pixels, glyph IDs, visual caret order or font fallback.
; Build separately with nasm -f win64; not linked to the current GUI yet.

bits 64
default rel
section .text
global r66_next_indic_cluster

r66_next_indic_cluster:
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    sub rsp, 32               ; aligned Win64 call frame, shadow space
    mov rbx, rcx
    mov r12, rdx
    cmp rbx, r12
    jae .empty
    call r66_decode_utf8
    lea r13, [rbx+r8]          ; next byte
    mov edi, eax              ; initial scalar
    xor r14d, r14d            ; script: 0=other, 1=Devanagari, 2=Gujarati
    cmp eax, 0x0900
    jb .not_dev
    cmp eax, 0x097F
    ja .not_dev
    mov r14d, 1
.not_dev:
    cmp eax, 0x0A80
    jb .scope_ready
    cmp eax, 0x0AFF
    ja .scope_ready
    mov r14d, 2
.scope_ready:
    xor r15d, r15d            ; virama/linker pending
    mov eax, edi
    call r66_is_consonant
    mov esi, eax             ; initial cluster may form a consonant chain
    cmp edi, 13
    jne .loop
    cmp r13, r12
    jae .done
    cmp byte [r13], 10        ; CR LF editor cluster
    jne .done
    inc r13
    jmp .done
.loop:
    ; Do not absorb marks across ASCII control/newline boundaries.
    cmp edi, 32
    jb .done
    cmp edi, 127
    je .done
    cmp r13, r12
    jae .done
    mov rcx, r13
    mov rdx, r12
    call r66_decode_utf8
    mov ebx, eax
    cmp eax, 0x200C           ; ZWNJ attaches but ends conjunct linking
    je .zwnj
    cmp eax, 0x200D           ; ZWJ attaches, keeps existing virama link
    je .consume
    cmp r14d, 1
    jne .gujarati
    cmp eax, 0x094D
    je .virama
    cmp eax, 0x0900
    jb .after_marks
    cmp eax, 0x0903
    jbe .consume
    cmp eax, 0x093A
    jb .after_marks
    cmp eax, 0x093C
    jbe .consume
    cmp eax, 0x093E
    jb .after_marks
    cmp eax, 0x094F
    jbe .consume
    cmp eax, 0x0951
    jb .after_marks
    cmp eax, 0x0957
    jbe .consume
    cmp eax, 0x0962
    je .consume
    cmp eax, 0x0963
    je .consume
    jmp .after_marks
.gujarati:
    cmp r14d, 2
    jne .after_marks
    cmp eax, 0x0ACD
    je .virama
    cmp eax, 0x0A81
    jb .after_marks
    cmp eax, 0x0A83
    jbe .consume
    cmp eax, 0x0ABC
    je .consume
    cmp eax, 0x0ABE
    jb .after_marks
    cmp eax, 0x0AC5
    jbe .consume
    cmp eax, 0x0AC7
    jb .after_marks
    cmp eax, 0x0AC9
    jbe .consume
    cmp eax, 0x0ACB
    je .consume
    cmp eax, 0x0ACC
    je .consume
    cmp eax, 0x0AE2
    je .consume
    cmp eax, 0x0AE3
    je .consume
    cmp eax, 0x0AFA
    jb .after_marks
    cmp eax, 0x0AFF
    jbe .consume
.after_marks:
    ; Combining Diacritical Marks block is a small deliberate extension,
    ; not a claim of complete Unicode grapheme-property table coverage.
    cmp eax, 0x0300
    jb .after_common
    cmp eax, 0x036F
    jbe .consume
.after_common:
    test r15d, r15d
    jz .done
    mov eax, ebx
    call r66_is_consonant
    test eax, eax
    jz .done
    xor r15d, r15d
    jmp .consume
.virama:
    mov r15d, esi
    jmp .consume
.zwnj:
    xor r15d, r15d
.consume:
    add r13, r8
    jmp .loop
.empty:
    mov r13, rbx
.done:
    mov rax, r13
    add rsp, 32
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    ret

r66_is_consonant:
    ; EAX=scalar, R14D=cluster script. Return EAX=0/1; preserve R8 width.
    cmp r14d, 1
    jne .guj
    cmp eax, 0x0915
    jb .no
    cmp eax, 0x0939
    jbe .yes
    cmp eax, 0x0958
    jb .no
    cmp eax, 0x095F
    jbe .yes
    cmp eax, 0x0978
    jb .no
    cmp eax, 0x097F
    jbe .yes
    jmp .no
.guj:
    cmp r14d, 2
    jne .no
    cmp eax, 0x0A95
    jb .no
    cmp eax, 0x0AA8
    jbe .yes
    cmp eax, 0x0AAA
    jb .no
    cmp eax, 0x0AB0
    jbe .yes
    cmp eax, 0x0AB2
    je .yes
    cmp eax, 0x0AB3
    je .yes
    cmp eax, 0x0AB5
    jb .no
    cmp eax, 0x0AB9
    jbe .yes
    cmp eax, 0x0AF9
    je .yes
.no:
    xor eax, eax
    ret
.yes:
    mov eax, 1
    ret

r66_decode_utf8:
    ; RCX=byte pointer, RDX=end. EAX=scalar, R8=width. R9/R10 scratch.
    ; Called only within this object. Nonvolatile registers are untouched.
    xor r8d, r8d
    cmp rcx, rdx
    jae .empty
    mov r8d, 1
    movzx eax, byte [rcx]
    cmp eax, 0x80
    jb .return
    cmp eax, 0xC2
    jb .bad
    cmp eax, 0xF4
    ja .bad
    mov r9, rdx
    sub r9, rcx
    cmp eax, 0xDF
    jbe .two
    cmp eax, 0xEF
    jbe .three
    cmp r9, 4
    jb .bad
    movzx r10d, byte [rcx+1]
    cmp r10d, 0x80
    jb .bad
    cmp r10d, 0xBF
    ja .bad
    cmp eax, 0xF0
    jne .not_f0
    cmp r10d, 0x90
    jb .bad
.not_f0:
    cmp eax, 0xF4
    jne .four_base
    cmp r10d, 0x8F
    ja .bad
.four_base:
    and eax, 7
    shl eax, 6
    and r10d, 63
    or eax, r10d
    movzx r10d, byte [rcx+2]
    cmp r10d, 0x80
    jb .bad
    cmp r10d, 0xBF
    ja .bad
    shl eax, 6
    and r10d, 63
    or eax, r10d
    movzx r10d, byte [rcx+3]
    cmp r10d, 0x80
    jb .bad
    cmp r10d, 0xBF
    ja .bad
    shl eax, 6
    and r10d, 63
    or eax, r10d
    mov r8d, 4
    ret
.three:
    cmp r9, 3
    jb .bad
    movzx r10d, byte [rcx+1]
    cmp r10d, 0x80
    jb .bad
    cmp r10d, 0xBF
    ja .bad
    cmp eax, 0xE0
    jne .not_e0
    cmp r10d, 0xA0
    jb .bad
.not_e0:
    cmp eax, 0xED
    jne .three_base
    cmp r10d, 0x9F
    ja .bad
.three_base:
    and eax, 15
    shl eax, 6
    and r10d, 63
    or eax, r10d
    movzx r10d, byte [rcx+2]
    cmp r10d, 0x80
    jb .bad
    cmp r10d, 0xBF
    ja .bad
    shl eax, 6
    and r10d, 63
    or eax, r10d
    mov r8d, 3
    ret
.two:
    cmp r9, 2
    jb .bad
    movzx r10d, byte [rcx+1]
    cmp r10d, 0x80
    jb .bad
    cmp r10d, 0xBF
    ja .bad
    and eax, 31
    shl eax, 6
    and r10d, 63
    or eax, r10d
    mov r8d, 2
.return:
    ret
.bad:
    mov eax, 0xFFFD
    mov r8d, 1
    ret
.empty:
    mov eax, 0xFFFD
    ret
