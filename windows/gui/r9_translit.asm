; R9 (WS6): the IDE's transliteration engine. %include'd by sutram_gui.asm and by
; tests/translit/r9_translit_test.asm (a Linux harness that checks it against
; tools/translit.py, the reference). Data: r9_translit_data.inc (generated).
;
; r9_tl_phonetic
;   in:  rsi = ASCII word, ecx = its length (1..63), edx = pack index 0..10
;        (kw_pack_paths order), rdi = UTF-16 output (room for 4 * length units)
;   out: eax = UTF-16 units written
; It makes no API calls and takes no stack arguments (its one internal helper is
; reached with a near call), and it saves every register it uses except rax, so it
; is safe under both the Win64 and the System V conventions.

%include "windows/gui/r9_translit_data.inc"

section .text
r9_tl_phonetic:
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push r8
    push r9
    push r10
    push r11
    push r12
    push r13
    push r14
    push r15
    mov r15, rdi                    ; output start
    lea r12, [rsi + rcx]            ; input end
    lea rbx, [rel r9_tl_scripts]
    imul edx, edx, R9_TL_SCRIPT_BYTES
    add rbx, rdx                    ; rbx -> this pack's script record
    xor r13d, r13d                  ; state: 1 = a consonant still waiting for its vowel
.next:
    cmp rsi, r12
    jae .end
    ; find the longest token that matches at rsi (the table is longest-first)
    lea r8, [rel r9_tl_tokens]
.tok:
    movzx ecx, byte [r8]            ; token length, 0 ends the table
    test ecx, ecx
    jz .literal
    mov rax, r12
    sub rax, rsi
    cmp rax, rcx
    jb .tok_skip                    ; not enough input left
    xor r9d, r9d
.cmp:
    mov al, [r8 + 4 + r9]
    cmp al, [rsi + r9]
    jne .tok_skip
    inc r9d
    cmp r9d, ecx
    jb .cmp
    jmp .matched
.tok_skip:
    lea r8, [r8 + 4 + rcx]
    jmp .tok
.literal:
    movzx eax, byte [rsi]
    mov [rdi], ax
    add rdi, 2
    inc rsi
    xor r13d, r13d
    jmp .next
.matched:
    add rsi, rcx
    movzx r10d, byte [r8 + 2]       ; off1
    movzx r11d, byte [r8 + 3]       ; off2
    movzx eax, byte [r8 + 1]        ; kind
    cmp eax, 1
    je .vowel
    cmp eax, 2
    je .consonant
    ; sign (anusvara / visarga)
    mov r14d, r10d
    call .emit
    xor r13d, r13d
    jmp .next
.vowel:
    test r13d, r13d
    jz .vowel_free
    xor r13d, r13d
    test r11d, r11d                 ; inherent a: nothing to write
    jz .next
    mov r14d, r11d
    call .emit
    jmp .next
.vowel_free:
    mov r14d, r10d
    call .emit
    jmp .next
.consonant:
    test r13d, r13d
    jz .c1
    mov r14d, 0x4D                  ; virama between consonants
    call .emit
.c1:
    mov r14d, r10d
    call .emit
    mov r13d, 1
    test r11d, r11d
    jz .next
    mov r14d, 0x4D
    call .emit
    mov r14d, r11d
    call .emit
    jmp .next
.end:
    test r13d, r13d
    jz .done
    mov r14d, 0x4D                  ; a final consonant keeps its virama
    call .emit
.done:
    mov rax, rdi
    sub rax, r15
    shr rax, 1
    pop r15
    pop r14
    pop r13
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    ret

; emit offset r14d through this script's substitution table (internal; uses the
; return address slot only, so it is still a leaf as far as callers see)
.emit:
    movzx eax, byte [rbx + 2 + r14]
    cmp eax, 0xFF
    je .emit_ret                    ; the script has no such letter: drop it
    test eax, eax
    jnz .emit_have
    mov eax, r14d
.emit_have:
    movzx edx, word [rbx]
    add eax, edx
    mov [rdi], ax
    add rdi, 2
.emit_ret:
    ret
