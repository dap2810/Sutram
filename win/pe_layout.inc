; Shared PE layout: first 1024 data bytes hold language globals.
RT_GLOBAL_BYTES equ 1024
RT_IMPORT_BYTES equ 512
RT_DATA_BYTES equ RT_GLOBAL_BYTES + RT_IMPORT_BYTES
RT_IAT_OFF equ 40
RT_GetStdHandle equ RT_IAT_OFF + 0
RT_WriteFile equ RT_IAT_OFF + 8
RT_ReadFile equ RT_IAT_OFF + 16
RT_CloseHandle equ RT_IAT_OFF + 24
RT_VirtualAlloc equ RT_IAT_OFF + 32
RT_ExitProcess equ RT_IAT_OFF + 40
RT_SetConsoleOutputCP equ RT_IAT_OFF + 48
RT_SetConsoleCP equ RT_IAT_OFF + 56
RT_CreateFileA equ RT_IAT_OFF + 64
RT_GetConsoleOutputCP equ RT_IAT_OFF + 72
RT_ORIGINAL_CP equ 508
