; PE import template. RVAs patched from relative offsets per emission.
section .data
pe_import_template:
dd pe_import_int-pe_import_template,0,0,pe_import_dll-pe_import_template,RT_IAT_OFF
times 20 db 0
pe_import_iat:
dq pe_name_GetStdHandle-pe_import_template
dq pe_name_WriteFile-pe_import_template
dq pe_name_ReadFile-pe_import_template
dq pe_name_CloseHandle-pe_import_template
dq pe_name_VirtualAlloc-pe_import_template
dq pe_name_ExitProcess-pe_import_template
dq pe_name_SetConsoleOutputCP-pe_import_template
dq pe_name_SetConsoleCP-pe_import_template
dq pe_name_CreateFileA-pe_import_template
dq pe_name_GetConsoleOutputCP-pe_import_template
dq 0
pe_import_int:
dq pe_name_GetStdHandle-pe_import_template
dq pe_name_WriteFile-pe_import_template
dq pe_name_ReadFile-pe_import_template
dq pe_name_CloseHandle-pe_import_template
dq pe_name_VirtualAlloc-pe_import_template
dq pe_name_ExitProcess-pe_import_template
dq pe_name_SetConsoleOutputCP-pe_import_template
dq pe_name_SetConsoleCP-pe_import_template
dq pe_name_CreateFileA-pe_import_template
dq pe_name_GetConsoleOutputCP-pe_import_template
dq 0
pe_name_GetStdHandle: dw 0
db "GetStdHandle",0
align 2, db 0
pe_name_WriteFile: dw 0
db "WriteFile",0
align 2, db 0
pe_name_ReadFile: dw 0
db "ReadFile",0
align 2, db 0
pe_name_CloseHandle: dw 0
db "CloseHandle",0
align 2, db 0
pe_name_VirtualAlloc: dw 0
db "VirtualAlloc",0
align 2, db 0
pe_name_ExitProcess: dw 0
db "ExitProcess",0
align 2, db 0
pe_name_SetConsoleOutputCP: dw 0
db "SetConsoleOutputCP",0
align 2, db 0
pe_name_SetConsoleCP: dw 0
db "SetConsoleCP",0
align 2, db 0
pe_name_CreateFileA: dw 0
db "CreateFileA",0
align 2, db 0
pe_name_GetConsoleOutputCP: dw 0
db "GetConsoleOutputCP",0
align 2, db 0
pe_import_dll: db "KERNEL32.dll",0
times RT_IMPORT_BYTES-($-pe_import_template) db 0
pe_import_fixups:
dd 0,12,16
dd pe_import_iat-pe_import_template+0,pe_import_int-pe_import_template+0
dd pe_import_iat-pe_import_template+8,pe_import_int-pe_import_template+8
dd pe_import_iat-pe_import_template+16,pe_import_int-pe_import_template+16
dd pe_import_iat-pe_import_template+24,pe_import_int-pe_import_template+24
dd pe_import_iat-pe_import_template+32,pe_import_int-pe_import_template+32
dd pe_import_iat-pe_import_template+40,pe_import_int-pe_import_template+40
dd pe_import_iat-pe_import_template+48,pe_import_int-pe_import_template+48
dd pe_import_iat-pe_import_template+56,pe_import_int-pe_import_template+56
dd pe_import_iat-pe_import_template+64,pe_import_int-pe_import_template+64
dd pe_import_iat-pe_import_template+72,pe_import_int-pe_import_template+72
dd -1
section .bss
pe_import_output: resb RT_IMPORT_BYTES
section .text

pe_prepare_imports:
    ; EAX = import-block RVA. Recopy for repeated shell compilations.
    push rbx
    push rsi
    push rdi
    mov ebx,eax
    lea rsi,[rel pe_import_template]
    lea rdi,[rel pe_import_output]
    mov ecx,RT_IMPORT_BYTES/8
    rep movsq
    lea rsi,[rel pe_import_fixups]
    lea rdi,[rel pe_import_output]
.next:
    lodsd
    cmp eax,-1
    je .done
    add dword [rdi+rax],ebx
    jmp .next
.done:
    pop rdi
    pop rsi
    pop rbx
    ret

