; R4 repro: send WM_COMMAND(IDC_NEXT, BN_SETFOCUS) -- a focus notification, NOT a click -- to the wizard.
default rel
extern __imp_FindWindowW, __imp_SendMessageW, __imp_ExitProcess
global _start
section .data
cls: dw __utf16__('SutramWizardWindow'),0
section .text
_start:
    sub rsp, 40
    lea rcx, [cls]
    xor edx, edx
    call [__imp_FindWindowW]
    test rax, rax
    jz .none
    mov rcx, rax
    mov edx, 0x111                 ; WM_COMMAND
    mov r8d, (6 << 16) | 2002      ; HIWORD = BN_SETFOCUS (6), LOWORD = IDC_NEXT
    xor r9d, r9d
    call [__imp_SendMessageW]
    xor ecx, ecx
    call [__imp_ExitProcess]
.none:
    mov ecx, 2
    call [__imp_ExitProcess]
