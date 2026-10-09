; ---------------------------------------------------------------------------
; winapi.asm — Sutram Windows port: self-contained Win64 API access
;
; Why this exists: the Linux compiler talks to the kernel with `syscall`.
; On Windows there is no such instruction for file I/O; the code must call
; kernel32 (CreateFileA, ReadFile, WriteFile, CloseHandle, ExitProcess,
; VirtualAlloc). Linking against kernel32 normally needs an import library
; (.a), which we do not have here. Instead we locate kernel32 at runtime by
; walking the PEB's loader lists and parse its export table ourselves — the
; same technique used by position-independent Windows shellcode. No import
; table, no external libraries.
;
; Build (proves the port toolchain):
;   nasm -f win64 winapi.asm -o winapi.obj
;   ld -mi386pep --entry=_start -o winapi.exe winapi.obj
;
; NOTE: assembled and linked here, structure verified with objdump.
; Runtime behaviour must be confirmed on a real Windows machine (no
; Windows/wine in this build environment).
; ---------------------------------------------------------------------------

bits 64
default rel

global _start
global win_kernel32
global win_resolve

section .text

; ---------------------------------------------------------------------------
; _start — demo entry: resolve ExitProcess and exit with code 42.
; ---------------------------------------------------------------------------
_start:
    lea rdi, [rel name_exit]
    call win_resolve            ; rax = ExitProcess address
    test rax, rax
    jz .halt
    mov ecx, 42                 ; exit code
    call rax                    ; ExitProcess(42)
.halt:
    jmp $                       ; never reached if ExitProcess worked

; ---------------------------------------------------------------------------
; win_kernel32 — find kernel32.dll base address by walking the PEB.
;   out: rax = DllBase (0 on failure)
; ---------------------------------------------------------------------------
win_kernel32:
    mov rax, [gs:0x60]          ; PEB
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x18]         ; PEB->Ldr (PEB_LDR_DATA)
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x20]         ; InMemoryOrderModuleList.Flink -> 1st entry (exe)
    test rax, rax
    jz .k_fail
    mov rax, [rax]              ; 2nd entry -> ntdll.dll
    test rax, rax
    jz .k_fail
    mov rax, [rax]              ; 3rd entry -> kernel32.dll
    test rax, rax
    jz .k_fail
    mov rax, [rax+0x20]         ; DllBase (InMemoryOrderLinks at +0x10, DllBase at +0x30)
    ret
.k_fail:
    xor rax, rax
    ret

; ---------------------------------------------------------------------------
; win_resolve — get the address of an exported function from kernel32.
;   in : rdi = pointer to a NUL-terminated ASCII name (case sensitive)
;   out: rax = function address (0 if not found)
; ---------------------------------------------------------------------------
win_resolve:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r14, rdi                ; r14 = wanted name
    call win_kernel32
    test rax, rax
    jz .r_fail
    mov rbx, rax                ; rbx = kernel32 base
    ; --- DOS header -> PE header ---
    mov eax, [rbx+0x3C]         ; e_lfanew
    add rax, rbx                ; rax = PE header
    ; OptionalHeader starts at PE sig + 24
    ; DataDirectory[0] (export table) at OptionalHeader + 0x70 (PE32+)
    mov r12d, [rax+24+0x70]     ; export dir RVA
    test r12d, r12d
    jz .r_fail
    add r12, rbx                ; r12 = IMAGE_EXPORT_DIRECTORY
    mov r13d, [r12+0x20]        ; AddressOfNames RVA
    add r13, rbx                ; r13 = array of name RVAs
    mov r15d, [r12+0x18]        ; NumberOfNames
    test r15d, r15d
    jz .r_fail
    xor rcx, rcx                ; index
.r_loop:
    cmp rcx, r15
    jae .r_fail
    mov eax, [r13 + rcx*4]      ; name RVA
    add rax, rbx                ; rax = current name ptr
    ; compare with wanted name
    push rcx
    push rax
    mov rsi, rax
    mov rdi, r14
.r_cmp:
    mov al, [rsi]
    mov dl, [rdi]
    cmp al, dl
    jne .r_next
    test al, al
    jz .r_found
    inc rsi
    inc rdi
    jmp .r_cmp
.r_next:
    pop rax
    pop rcx
    inc rcx
    jmp .r_loop
.r_found:
    pop rax
    pop rcx
    ; ordinal index -> AddressOfNameOrdinals -> AddressOfFunctions
    mov r13d, [r12+0x24]        ; AddressOfNameOrdinals RVA
    add r13, rbx
    movzx ecx, word [r13 + rcx*2]; ordinal
    mov r13d, [r12+0x1C]        ; AddressOfFunctions RVA
    add r13, rbx
    mov eax, [r13 + rcx*4]      ; function RVA
    add rax, rbx                ; function address
    jmp .r_done
.r_fail:
    xor rax, rax
.r_done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

section .data
name_exit: db "ExitProcess", 0
