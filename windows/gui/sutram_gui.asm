; Sutram Windows GUI IDE — experimental native Win64 proof-of-implementation
; Pure NASM -> Win64 PE, Win32 API and MSFTEDIT RichEdit (Windows system DLL).
; NO C/C++/Python or GUI framework in executable. Standard-user only.
; Build: nasm -f win64 windows/gui/sutram_gui.asm -o sutram_gui.obj
;        ld -mi386pep --subsystem windows --entry=_start -o sutram-ide-gui.exe sutram_gui.obj
; Placement: project root alongside win\sutram.exe and examples\*.sm.
; Native language-pack highlighting source-stage; Windows runtime is UNVERIFIED.

bits 64
default rel

global _start

%define WM_CREATE 1
%define WM_SETICON 0x80
%define IMAGE_ICON 1
%define LR_LOADFROMFILE 0x10
%define LR_DEFAULTSIZE 0x40
%define WM_DESTROY 2
%define WM_SIZE 5
%define WM_CLOSE 16
%define WM_COMMAND 0x111
%define WM_KEYDOWN 0x100
%define WM_CHAR 0x102
%define VK_RETURN 13
%define WM_GETTEXT 13
%define WM_SETTEXT 12
%define WM_GETTEXTLENGTH 14
%define WM_SETFONT 0x30
%define EM_GETSEL 0xB0
%define EM_SETSEL 0xB1
%define EM_GETLINECOUNT 0xBA
%define EM_GETFIRSTVISIBLELINE 0xCE
%define EM_LINESCROLL 0xB6
%define EM_REPLACESEL 0xC2
%define EM_SETREADONLY 0xCF
%define EM_SETCHARFORMAT 0x444
%define EM_GETEVENTMASK 0x43B
%define EM_SETEVENTMASK 0x445
%define SCF_ALL 4
%define SCF_SELECTION 1
%define CFM_COLOR 0x40000000
%define WS_OVERLAPPEDWINDOW 0x00CF0000
%define WS_VISIBLE 0x10000000
%define WS_CHILD 0x40000000
%define WS_BORDER 0x00800000
%define WS_VSCROLL 0x00200000
%define ES_MULTILINE 4
%define ES_AUTOVSCROLL 0x40
%define ES_AUTOHSCROLL 0x80
%define ES_READONLY 0x800
%define ES_WANTRETURN 0x1000
%define LBS_NOTIFY 1
%define LB_ADDSTRING 0x180
%define LB_GETCURSEL 0x188
%define LB_GETTEXT 0x189
%define LBN_DBLCLK 2
%define EN_CHANGE 0x300
%define GWLP_WNDPROC -4
%define SW_SHOW 5
%define SWP_NOZORDER 4
%define ID_RUN 101
%define ID_OPEN 102
%define ID_SAVE 103
%define ID_EXAMPLE 104
%define ID_SEND 105
%define ID_CLEAR 106
%define ID_EDITOR 201
%define ID_GUTTER 202
%define ID_OUTPUT 203
%define ID_SHELL 204
%define ID_LIST 205
%define GENERIC_READ 0x80000000
%define GENERIC_WRITE 0x40000000
%define OPEN_EXISTING 3
%define CREATE_ALWAYS 2
%define FILE_ATTRIBUTE_NORMAL 0x80
%define FILE_SHARE_READ 1
%define INVALID_HANDLE -1
%define CREATE_NO_WINDOW 0x08000000
%define STARTF_USESTDHANDLES 0x100
%define HANDLE_FLAG_INHERIT 1
%define WAIT_OBJECT_0 0
%define OFN_PATHMUSTEXIST 0x800
%define OFN_FILEMUSTEXIST 0x1000
%define OFN_OVERWRITEPROMPT 2
%define OFN_NOCHANGEDIR 8
%define OFN_EXPLORER 0x80000
%define MAX_EDIT 65534
%define MAX_OUTPUT 32767
%define MAX_NATIVE_KEYWORDS 384
%define NATIVE_KEYWORD_UNITS 64
%define MAX_LANG_FILE 8191

%macro PROLOG 1
    push rbp
    mov rbp,rsp
    sub rsp,%1
%endmacro
%macro EPILOG 0
    leave
    ret
%endmacro
%macro API 1
    call qword [rel p_%1]
%endmacro
%macro PTR 2
    lea %1,[rel %2]
%endmacro

section .data
app_class db 'SutramNativeGUIWindow',0
app_title db 'Sutram - Native Windows IDE (Preview)',0
class_button db 'BUTTON',0
class_edit db 'EDIT',0
class_list db 'LISTBOX',0
class_richedit db 'RICHEDIT50W',0
richedit_dll db 'Msftedit.dll',0
user32_dll db 'user32.dll',0
comdlg32_dll db 'comdlg32.dll',0
name_ker32 db 'kernel32.dll',0

; Kernel API export names (resolved through same pure-NASM mechanism as win/winapi.asm)
n_GetModuleFileNameW db 'GetModuleFileNameW',0
n_SetCurrentDirectoryW db 'SetCurrentDirectoryW',0
n_GetTempPathW db 'GetTempPathW',0
n_GetTempFileNameW db 'GetTempFileNameW',0
n_CreateProcessW db 'CreateProcessW',0
n_DeleteFileW db 'DeleteFileW',0
n_SendMessageW db 'SendMessageW',0
n_LoadImageW db 'LoadImageW',0
n_LoadLibraryA db 'LoadLibraryA',0
n_GetProcAddress db 'GetProcAddress',0
n_GetModuleHandleA db 'GetModuleHandleA',0
n_GetModuleFileNameA db 'GetModuleFileNameA',0
n_SetCurrentDirectoryA db 'SetCurrentDirectoryA',0
n_ExitProcess db 'ExitProcess',0
n_CreateFileA db 'CreateFileA',0
n_ReadFile db 'ReadFile',0
n_WriteFile db 'WriteFile',0
n_CloseHandle db 'CloseHandle',0
n_DeleteFileA db 'DeleteFileA',0
n_GetTempPathA db 'GetTempPathA',0
n_GetTempFileNameA db 'GetTempFileNameA',0
n_MultiByteToWideChar db 'MultiByteToWideChar',0
n_WideCharToMultiByte db 'WideCharToMultiByte',0
n_GetWindowTextW db 'GetWindowTextW',0
n_SetWindowTextW db 'SetWindowTextW',0
n_GetOpenFileNameW db 'GetOpenFileNameW',0
n_GetSaveFileNameW db 'GetSaveFileNameW',0
n_CreateFileW db 'CreateFileW',0
n_CreatePipe db 'CreatePipe',0
n_SetHandleInformation db 'SetHandleInformation',0
n_CreateProcessA db 'CreateProcessA',0
n_WaitForSingleObject db 'WaitForSingleObject',0
n_PeekNamedPipe db 'PeekNamedPipe',0
n_GetExitCodeProcess db 'GetExitCodeProcess',0
n_TerminateProcess db 'TerminateProcess',0
n_GetTickCount64 db 'GetTickCount64',0
n_FindFirstFileA db 'FindFirstFileA',0
n_FindNextFileA db 'FindNextFileA',0
n_FindClose db 'FindClose',0
n_MessageBoxA db 'MessageBoxA',0
n_RegisterClassExA db 'RegisterClassExA',0
n_LoadCursorA db 'LoadCursorA',0
n_CreateWindowExA db 'CreateWindowExA',0
n_ShowWindow db 'ShowWindow',0
n_UpdateWindow db 'UpdateWindow',0
n_DefWindowProcA db 'DefWindowProcA',0
n_GetMessageA db 'GetMessageA',0
n_TranslateMessage db 'TranslateMessage',0
n_DispatchMessageA db 'DispatchMessageA',0
n_PostQuitMessage db 'PostQuitMessage',0
n_DestroyWindow db 'DestroyWindow',0
n_SendMessageA db 'SendMessageA',0
n_MoveWindow db 'MoveWindow',0
n_GetWindowTextA db 'GetWindowTextA',0
n_SetWindowTextA db 'SetWindowTextA',0
n_GetWindowTextLengthA db 'GetWindowTextLengthA',0
n_SetWindowLongPtrA db 'SetWindowLongPtrA',0
n_CallWindowProcA db 'CallWindowProcA',0
n_GetClientRect db 'GetClientRect',0
n_GetStockObject db 'GetStockObject',0
n_GetOpenFileNameA db 'GetOpenFileNameA',0
n_GetSaveFileNameA db 'GetSaveFileNameA',0

; DLL lookup table: pairs of name pointer + slot address, zero terminated.
%macro IMPORTS 1
    dq n_%1,p_%1
%endmacro
kernel_table:
    IMPORTS DeleteFileW
    IMPORTS CreateProcessW
    IMPORTS GetTempFileNameW
    IMPORTS GetTempPathW
    IMPORTS SetCurrentDirectoryW
    IMPORTS GetModuleFileNameW
    IMPORTS GetModuleHandleA
    IMPORTS GetModuleFileNameA
    IMPORTS SetCurrentDirectoryA
    IMPORTS ExitProcess
    IMPORTS CreateFileA
    IMPORTS ReadFile
    IMPORTS WriteFile
    IMPORTS CloseHandle
    IMPORTS DeleteFileA
    IMPORTS GetTempPathA
    IMPORTS GetTempFileNameA
    IMPORTS MultiByteToWideChar
    IMPORTS WideCharToMultiByte
    IMPORTS CreateFileW
    IMPORTS CreatePipe
    IMPORTS SetHandleInformation
    IMPORTS CreateProcessA
    IMPORTS WaitForSingleObject
    IMPORTS PeekNamedPipe
    IMPORTS GetExitCodeProcess
    IMPORTS TerminateProcess
    IMPORTS GetTickCount64
    IMPORTS FindFirstFileA
    IMPORTS FindNextFileA
    IMPORTS FindClose
    dq 0,0
user_table:
    IMPORTS SendMessageW
    IMPORTS LoadImageW
    IMPORTS MessageBoxA
    IMPORTS RegisterClassExA
    IMPORTS LoadCursorA
    IMPORTS CreateWindowExA
    IMPORTS ShowWindow
    IMPORTS UpdateWindow
    IMPORTS DefWindowProcA
    IMPORTS GetMessageA
    IMPORTS TranslateMessage
    IMPORTS DispatchMessageA
    IMPORTS PostQuitMessage
    IMPORTS DestroyWindow
    IMPORTS SendMessageA
    IMPORTS MoveWindow
    IMPORTS GetWindowTextA
    IMPORTS GetWindowTextW
    IMPORTS SetWindowTextA
    IMPORTS SetWindowTextW
    IMPORTS GetWindowTextLengthA
    IMPORTS SetWindowLongPtrA
    IMPORTS CallWindowProcA
    IMPORTS GetClientRect
    dq 0,0
comdlg_table:
    IMPORTS GetOpenFileNameA
    IMPORTS GetOpenFileNameW
    IMPORTS GetSaveFileNameA
    IMPORTS GetSaveFileNameW
    dq 0,0

label_run db 'Run',0
label_open db 'Open',0
label_save db 'Save',0
label_example db 'Load example',0
label_send db 'Send',0
label_clear db 'Clear shell',0
label_output db 'Compile / run output',0
label_shell db 'Sutram shell (one statement per Enter)',0
label_examples db 'Examples (double click)',0
err_init db 'Windows APIs could not be loaded. IDE cannot start.',0
err_title db 'Sutram IDE',0
msg_ready db 'Ready. Run compiles the editor buffer.',13,10,0
msg_compile_failed db '[compiler failed]',13,10,0
msg_run_failed db '[program exited abnormally]',13,10,0
msg_file_failed db '[unable to read/write file]',13,10,0
msg_input_large db '[file too large; editor limit 64 KiB]',13,10,0
msg_shell_limit db '[shell history limit reached; clear shell]',13,10,0
msg_timeout db '[process exceeded 10 seconds; terminated]',13,10,0
msg_missing_compiler db '[missing win\sutram.exe: compile native compiler first]',13,10,0
msg_missing_lang db '[native keyword packs unavailable: check lang\*.lang; Latin keywords still work]',13,10,0
msg_partial_lang db '[some native keyword packs missing or invalid: check lang\*.lang]',13,10,0
msg_pipe_fail db '[process or pipe creation failed]',13,10,0
msg_more_output db '[output truncated at 32 KiB]',13,10,0
prefix_s db 'mukhya()',13,10,0
indent_s db '    ',0
newline db 13,10,0
file_filter db 'Sutram files (*.sm)',0,'*.sm',0,'All files (*.*)',0,'*.*',0,0
file_filter_w: dw 83,117,116,114,97,109,32,102,105,108,101,115,32,40,42,46,115,109,41,0,42,46,115,109,0,65,108,108,32,102,105,108,101,115,32,40,42,46,42,41,0,42,46,42,0,0
examples_glob db 'examples\*.sm',0
examples_dir db 'examples\',0
compiler_rel db 'win\sutram.exe',0
prefix_gui db 'STG',0
caption_editor db 'Editor',0
kw_words db 'mukhya',0,'likha',0,'ayojan',0,'prakriya',0,'dasham',0,'kosh',0,'kuru',0,'nishkriya',0,'yadi',0,'anyatha',0,'yavat',0,'punar',0,'satya',0,'asatya',0,'phala',0,'pratiyati',0,'grahan',0,0
; Import-table label expansion: function-name symbols n_* via macro.
%unmacro IMPORTS 1
%macro IMPORTS 1
p_%1: dq 0
%endmacro

compiler_rel_w: dw 119,105,110,92,115,117,116,114,97,109,46,101,120,101,0

suffix_exe_w: dw 46,101,120,101,0

prefix_gui_w: dw 83,84,71,0

quote_only_w: dw 34,0

quote_space_quote_w: dw 34,32,34,0

gui_icon_w: dw 105,99,111,110,115,92,115,117,116,114,97,109,46,105,99,111,0
gui_icon_installed_w: dw 97,115,115,101,116,115,92,115,117,116,114,97,109,46,105,99,111,0

; Each language pack is read as UTF-8 at GUI startup. The names are UTF-16 paths.
kw_pack_bengali_w: dw 108,97,110,103,92,98,101,110,103,97,108,105,46,108,97,110,103,0
kw_pack_gujarati_w: dw 108,97,110,103,92,103,117,106,97,114,97,116,105,46,108,97,110,103,0
kw_pack_hindi_w: dw 108,97,110,103,92,104,105,110,100,105,46,108,97,110,103,0
kw_pack_kannada_w: dw 108,97,110,103,92,107,97,110,110,97,100,97,46,108,97,110,103,0
kw_pack_malayalam_w: dw 108,97,110,103,92,109,97,108,97,121,97,108,97,109,46,108,97,110,103,0
kw_pack_marathi_w: dw 108,97,110,103,92,109,97,114,97,116,104,105,46,108,97,110,103,0
kw_pack_odia_w: dw 108,97,110,103,92,111,100,105,97,46,108,97,110,103,0
kw_pack_punjabi_w: dw 108,97,110,103,92,112,117,110,106,97,98,105,46,108,97,110,103,0
kw_pack_tamil_w: dw 108,97,110,103,92,116,97,109,105,108,46,108,97,110,103,0
kw_pack_telugu_w: dw 108,97,110,103,92,116,101,108,117,103,117,46,108,97,110,103,0
kw_pack_paths: dq kw_pack_bengali_w,kw_pack_gujarati_w,kw_pack_hindi_w,kw_pack_kannada_w,kw_pack_malayalam_w,kw_pack_marathi_w,kw_pack_odia_w,kw_pack_punjabi_w,kw_pack_tamil_w,kw_pack_telugu_w,0
section .bss
h_kernel resq 1
h_user resq 1
h_dialog resq 1
h_richedit resq 1
h_instance resq 1
h_main resq 1
h_editor resq 1
h_gutter resq 1
h_output resq 1
h_shell resq 1
h_examples resq 1
h_btn_run resq 1
h_btn_open resq 1
h_btn_save resq 1
h_btn_example resq 1
h_btn_send resq 1
h_btn_clear resq 1
old_shell_proc resq 1
is_highlighting resd 1
native_keyword_count resd 1
native_pack_count resd 1
native_pack_errors resd 1
native_keyword_storage resw MAX_NATIVE_KEYWORDS*NATIVE_KEYWORD_UNITS
native_pack_bytes resb MAX_LANG_FILE+1
native_pack_word resb 256
is_lineupdating resd 1
is_shellrunning resd 1
last_shell_out resd 1
last_exit_code resd 1
current_file resb 1040
editor_utf16 resw 65536
output_utf16 resw 32768
path_utf16 resw 1040
utf8_status resd 1
rootpath resb 1040
temp_path resb 1040
temp_binary resb 1060
tmp_dir resb 1040
compiler_path resb 1200
command_line resb 4000
file_buffer resb 65536
edit_buffer resb 65536
shell_history resb 32768
shell_input resb 4096
output_buffer resb 32768
output_scratch resb 32768
line_text resb 10000
example_name resb 520
client_rect resb 16
msg_struct resb 64
wc_struct resb 80
find_data resb 320
ofn_struct resb 152
char_fmt resb 60
ch_start resd 1
ch_end resd 1
bytes_count resd 1
pipe_available resd 1
pi_struct resb 24
si_struct resb 104
sa_struct resb 24
pipe_rd resq 1
pipe_wr resq 1
process_start resq 1

; Function pointers
IMPORTS LoadLibraryA
IMPORTS GetProcAddress
IMPORTS GetModuleHandleA
IMPORTS GetModuleFileNameA
IMPORTS SetCurrentDirectoryA
IMPORTS ExitProcess
IMPORTS CreateFileA
IMPORTS ReadFile
IMPORTS WriteFile
IMPORTS CloseHandle
IMPORTS DeleteFileA
IMPORTS GetTempPathA
IMPORTS GetTempFileNameA
IMPORTS CreatePipe
IMPORTS SetHandleInformation
IMPORTS CreateProcessA
IMPORTS WaitForSingleObject
IMPORTS PeekNamedPipe
IMPORTS GetExitCodeProcess
IMPORTS TerminateProcess
IMPORTS GetTickCount64
IMPORTS FindFirstFileA
IMPORTS FindNextFileA
IMPORTS FindClose
IMPORTS MessageBoxA
IMPORTS RegisterClassExA
IMPORTS LoadCursorA
IMPORTS CreateWindowExA
IMPORTS ShowWindow
IMPORTS UpdateWindow
IMPORTS DefWindowProcA
IMPORTS GetMessageA
IMPORTS TranslateMessage
IMPORTS DispatchMessageA
IMPORTS PostQuitMessage
IMPORTS DestroyWindow
IMPORTS SendMessageA
IMPORTS MoveWindow
IMPORTS GetWindowTextA
IMPORTS SetWindowTextA
IMPORTS GetWindowTextLengthA
IMPORTS SetWindowLongPtrA
IMPORTS CallWindowProcA
IMPORTS GetClientRect
IMPORTS GetOpenFileNameA
IMPORTS GetSaveFileNameA

IMPORTS GetModuleFileNameW
IMPORTS SetCurrentDirectoryW
IMPORTS GetTempPathW
IMPORTS GetTempFileNameW
IMPORTS CreateProcessW
IMPORTS DeleteFileW
IMPORTS MultiByteToWideChar
IMPORTS WideCharToMultiByte
IMPORTS GetWindowTextW
IMPORTS SetWindowTextW
IMPORTS GetOpenFileNameW
IMPORTS GetSaveFileNameW
IMPORTS CreateFileW
IMPORTS SendMessageW
IMPORTS LoadImageW
section .text

; Implementation note: all calls into Win64 APIs reserve 32 bytes of shadow
; space in each callee's >=160-byte aligned frame, even for <=4 arguments.
; For 5+ arguments, [rsp+32], [rsp+40], etc. are populated immediately
; before the API call. No foreign CRT dependencies.

_start:
    and rsp,-16
    sub rsp,256
    call init_apis
    test eax,eax
    jz .quit
    call init_paths
    call load_native_keyword_packs
    call gui_loop
.quit:
    xor ecx,ecx
    cmp qword [rel p_ExitProcess],0
    je .spin
    API ExitProcess
.spin:
    jmp .spin

; Initialize using the existing project's small kernel32 PEB export resolver.
; DLL lookups use Windows GetProcAddress and LoadLibraryA; no OS protections
; are bypassed or disabled. Caller resolves only explicit Windows system DLLs.
init_apis:
    PROLOG 64
    PTR rdi,n_LoadLibraryA
    call win_resolve
    mov [rel p_LoadLibraryA],rax
    test rax,rax
    jz .fail
    PTR rdi,n_GetProcAddress
    call win_resolve
    mov [rel p_GetProcAddress],rax
    test rax,rax
    jz .fail
    PTR rcx,name_ker32
    API LoadLibraryA
    mov [rel h_kernel],rax
    test rax,rax
    jz .fail
    mov rcx,rax
    PTR rdx,kernel_table
    call fill_table
    test eax,eax
    jz .fail
    PTR rcx,user32_dll
    API LoadLibraryA
    mov [rel h_user],rax
    test rax,rax
    jz .fail
    mov rcx,rax
    PTR rdx,user_table
    call fill_table
    test eax,eax
    jz .fail
    PTR rcx,comdlg32_dll
    API LoadLibraryA
    mov [rel h_dialog],rax
    test rax,rax
    jz .fail
    mov rcx,rax
    PTR rdx,comdlg_table
    call fill_table
    test eax,eax
    jz .fail
    PTR rcx,richedit_dll
    API LoadLibraryA
    mov [rel h_richedit],rax
    test rax,rax
    jz .fail
    mov eax,1
    jmp .end
.fail:
    xor eax,eax
.end:
    EPILOG

; rcx = dll handle, rdx=table with pointer-to-name + pointer-to-slot pairs.
fill_table:
    PROLOG 80
    mov [rbp-8],rcx
    mov [rbp-16],rdx
.loop:
    mov r10,[rbp-16]
    mov rdx,[r10]
    test rdx,rdx
    jz .ok
    mov rcx,[rbp-8]
    API GetProcAddress
    test rax,rax
    jz .fail
    mov r10,[rbp-16]
    mov r11,[r10+8]
    mov [r11],rax
    add qword [rbp-16],16
    jmp .loop
.ok:
    mov eax,1
    jmp .done
.fail:
    xor eax,eax
.done:
    EPILOG

; NOTE: Windows executable uses its own directory as project root. Place
; sutram-ide-gui.exe in root; leave core win\sutram.exe and examples\ intact.
init_paths:
    PROLOG 128
    xor ecx,ecx
    PTR rdx,rootpath
    mov r8d,520
    API GetModuleFileNameW
    test eax,eax
    jz .done
    cmp eax,520
    jae .done
    PTR rcx,rootpath
    lea r11,[rcx+rax*2-2]
.scan:
    cmp r11,rcx
    jb .done
    cmp word [r11],'\'
    je .cut
    cmp word [r11],'/'
    je .cut
    sub r11,2
    jmp .scan
.cut:
    mov word [r11],0
    PTR rcx,rootpath
    API SetCurrentDirectoryW
.done:
    mov ecx,520
    PTR rdx,tmp_dir
    API GetTempPathW
    test eax,eax
    jz .end
    cmp eax,520
    jae .end
    PTR rcx,tmp_dir
    PTR rdx,prefix_gui_w
    xor r8d,r8d
    PTR r9,temp_path
    API GetTempFileNameW
    test eax,eax
    jz .end
    PTR rcx,temp_path
    PTR rdx,temp_binary
    call wide_string_copy
    PTR rcx,temp_binary
    PTR rdx,suffix_exe_w
    call wide_string_concat
    PTR rcx,compiler_rel_w
    PTR rdx,compiler_path
    call wide_string_copy
.end:
    EPILOG

; Wide helpers: paths have 520-char bound, callers guarantee UTF16 capacity.
wide_string_length:
    xor eax,eax
.wlen:
    cmp word [rcx+rax*2],0
    je .done
    inc eax
    cmp eax,519
    jl .wlen
.done:
    ret
wide_string_copy:
    xor r10d,r10d
.wcopy:
    mov ax,[rcx+r10*2]
    mov [rdx+r10*2],ax
    test ax,ax
    jz .end
    inc r10
    cmp r10,519
    jl .wcopy
    mov word [rdx+r10*2],0
.end:
    ret
wide_string_concat:
    push rbx
    mov rbx,rdx
    mov rdx,rcx
    call wide_string_length
    lea rdx,[rdx+rax*2]
    mov rcx,rbx
    call wide_string_copy
    pop rbx
    ret

; 2000 UTF-16 code-unit command line buffer; unlike path buffers, it
; must hold THREE quoted paths. Callers never append untrusted command text.
wide_command_concat:
    push rbx
    mov rbx,rdx
    mov rdx,rcx
    xor eax,eax
.length:
    cmp word [rdx+rax*2],0
    je .room
    inc eax
    cmp eax,1999
    jb .length
    jmp .end
.room:
    mov r10d,eax
    xor eax,eax
.copy:
    cmp r10d,1998
    jae .stop
    mov cx,[rbx+rax*2]
    mov [rdx+r10*2],cx
    test cx,cx
    jz .end
    inc r10d
    inc eax
    jmp .copy
.stop:
    mov word [rdx+r10*2],0
.end:
    pop rbx
    ret

; rcx = nul-terminated string; return byte count in rax
string_length:
    xor eax,eax
.len:
    cmp byte [rcx+rax],0
    je .done
    inc eax
    cmp eax,65534
    jb .len
.done:
    ret
; rcx source, rdx target. Caller guarantees capacity.
string_copy:
    xor r10d,r10d
.lp:
    mov al,[rcx+r10]
    mov [rdx+r10],al
    inc r10
    test al,al
    jnz .lp
    ret
; rcx destination, rdx source. Caller guarantees capacity.
string_concat:
    push rbx
    sub rsp,8
    mov rbx,rdx
    call string_length
    lea rcx,[rcx+rax]
    mov rdx,rcx
    mov rcx,rbx
    call string_copy
    add rsp,8
    pop rbx
    ret

; Base GUI window registration / message loop.
gui_loop:
    PROLOG 160
    xor ecx,ecx
    API GetModuleHandleA
    mov [rel h_instance],rax
    xor ecx,ecx
    mov edx,32512                  ; IDC_ARROW system cursor
    API LoadCursorA
    mov [rbp-8],rax
    PTR r10,wc_struct
    mov dword [r10],80
    mov dword [r10+4],3          ; CS_HREDRAW | CS_VREDRAW
    PTR r11,wnd_proc
    mov [r10+8],r11
    mov r11,[rel h_instance]
    mov [r10+24],r11
    mov r11,[rbp-8]
    mov [r10+40],r11               ; hCursor
    mov qword [r10+48],6         ; COLOR_WINDOW+1
    PTR r11,app_class
    mov [r10+64],r11
    mov rcx,r10
    API RegisterClassExA
    test ax,ax
    jz .end
    xor ecx,ecx
    PTR rdx,app_class
    PTR r8,app_title
    mov r9d,WS_OVERLAPPEDWINDOW | WS_VISIBLE
    mov qword [rsp+32],100
    mov qword [rsp+40],50
    mov qword [rsp+48],1180
    mov qword [rsp+56],800
    mov qword [rsp+64],0
    mov qword [rsp+72],0
    mov rax,[rel h_instance]
    mov [rsp+80],rax
    mov qword [rsp+88],0
    API CreateWindowExA
    mov [rel h_main],rax
    test rax,rax
    jz .end
    mov rcx,rax
    mov edx,SW_SHOW
    API ShowWindow
    mov rcx,[rel h_main]
    API UpdateWindow
.msg:
    PTR rcx,msg_struct
    xor edx,edx
    xor r8d,r8d
    xor r9d,r9d
    API GetMessageA
    test eax,eax
    jle .end
    PTR rcx,msg_struct
    API TranslateMessage
    PTR rcx,msg_struct
    API DispatchMessageA
    jmp .msg
.end:
    EPILOG

; Create child controls. rcx=class,rdx=caption,r8=style,r9=id,
; extra x,y,w,h passed via caller's stack frame [rsp+32,...].
create_child:
    PROLOG 160
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    mov [rbp-24],r8
    mov [rbp-32],r9
    xor ecx,ecx
    mov rdx,[rbp-8]
    mov r8,[rbp-16]
    mov r9,[rbp-24]
    mov rax,[rbp+48]
    mov [rsp+32],rax             ; x from caller's arg5
    mov rax,[rbp+56]
    mov [rsp+40],rax             ; y
    mov rax,[rbp+64]
    mov [rsp+48],rax             ; w
    mov rax,[rbp+72]
    mov [rsp+56],rax             ; h
    mov rax,[rel h_main]
    mov [rsp+64],rax
    mov rax,[rbp-32]
    mov [rsp+72],rax
    mov rax,[rel h_instance]
    mov [rsp+80],rax
    mov qword [rsp+88],0
    API CreateWindowExA
    EPILOG

; SetWindowText/edit and SendMessage wrapper as Win64 internal calls.
send_message:
    PROLOG 48
    API SendMessageA
    EPILOG

wnd_proc:
    PROLOG 224
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    mov [rbp-24],r8
    mov [rbp-32],r9
    cmp edx,WM_CREATE
    je .create
    cmp edx,WM_SIZE
    je .resize
    cmp edx,WM_COMMAND
    je .command
    cmp edx,WM_CLOSE
    je .close
    cmp edx,WM_DESTROY
    je .destroy
    jmp .def
.create:
    mov r10,[rbp-8]
    mov [rel h_main],r10
    call create_controls
    call set_project_icon
    ; A missing installed lang/ directory must never masquerade as full support.
    cmp dword [rel native_pack_count],0
    jne .check_partial_lang
    mov rcx,[rel h_output]
    PTR rdx,msg_missing_lang
    API SetWindowTextA
    jmp .created
.check_partial_lang:
    cmp dword [rel native_pack_errors],0
    je .created
    mov rcx,[rel h_output]
    PTR rdx,msg_partial_lang
    API SetWindowTextA
.created:
    xor eax,eax
    jmp .done
.resize:
    mov rcx,[rbp-8]
    call layout_controls
    xor eax,eax
    jmp .done
.command:
    mov r10,[rbp-24]
    movzx ecx,r10w
    cmp ecx,ID_RUN
    je .run
    cmp ecx,ID_OPEN
    je .open
    cmp ecx,ID_SAVE
    je .save
    cmp ecx,ID_EXAMPLE
    je .example
    cmp ecx,ID_SEND
    je .shell
    cmp ecx,ID_CLEAR
    je .clear
    cmp ecx,ID_EDITOR
    je .edit_changed
    cmp ecx,ID_LIST
    je .list_changed
    xor eax,eax
    jmp .done
.run:
    call run_editor
    xor eax,eax
    jmp .done
.open:
    call open_dialog
    xor eax,eax
    jmp .done
.save:
    call save_dialog
    xor eax,eax
    jmp .done
.example:
    call load_example
    xor eax,eax
    jmp .done
.shell:
    call shell_submit
    xor eax,eax
    jmp .done
.clear:
    mov byte [rel shell_history],0
    mov dword [rel last_shell_out],0
    mov rcx,[rel h_output]
    PTR rdx,msg_ready
    API SetWindowTextA
    xor eax,eax
    jmp .done
.edit_changed:
    mov r10,[rbp-24]
    shr r10,16
    cmp r10d,EN_CHANGE
    jne .donezero
    cmp dword [rel is_highlighting],0
    jne .donezero
    call update_lines
    call highlight_editor
.donezero:
    xor eax,eax
    jmp .done
.list_changed:
    mov r10,[rbp-24]
    shr r10,16
    cmp r10d,LBN_DBLCLK
    jne .donezero
    call load_example
    xor eax,eax
    jmp .done
.close:
    mov rcx,[rbp-8]
    API DestroyWindow
    xor eax,eax
    jmp .done
.destroy:
    PTR rcx,temp_path
    API DeleteFileW
    PTR rcx,temp_binary
    API DeleteFileW
    xor ecx,ecx
    API PostQuitMessage
    xor eax,eax
    jmp .done
.def:
    mov rcx,[rbp-8]
    mov rdx,[rbp-16]
    mov r8,[rbp-24]
    mov r9,[rbp-32]
    API DefWindowProcA
.done:
    EPILOG


set_project_icon:
    PROLOG 96
    xor ecx,ecx
    PTR rdx,gui_icon_w
    mov r8d,IMAGE_ICON
    xor r9d,r9d
    mov qword [rsp+32],0
    mov qword [rsp+40],LR_LOADFROMFILE|LR_DEFAULTSIZE
    API LoadImageW
    test rax,rax
    jnz .apply
    xor ecx,ecx
    PTR rdx,gui_icon_installed_w
    mov r8d,IMAGE_ICON
    xor r9d,r9d
    mov qword [rsp+32],0
    mov qword [rsp+40],LR_LOADFROMFILE|LR_DEFAULTSIZE
    API LoadImageW
    test rax,rax
    jz .end
.apply:
    mov [rbp-8],rax
    mov rcx,[rel h_main]
    mov edx,WM_SETICON
    mov r8d,1
    mov r9,[rbp-8]
    call send_message
    mov rcx,[rel h_main]
    mov edx,WM_SETICON
    xor r8d,r8d
    mov r9,[rbp-8]
    call send_message
.end:
    EPILOG

create_controls:
    PROLOG 144
    ; Four toolbar buttons and two further actions.
%macro CHILD 9
    PTR rcx,%1
    PTR rdx,%2
    mov r8d,%3
    mov r9d,%4
    mov qword [rsp+32],%5
    mov qword [rsp+40],%6
    mov qword [rsp+48],%7
    mov qword [rsp+56],%8
    call create_child
    mov [rel %9],rax
%endmacro
    CHILD class_button,label_run,WS_CHILD|WS_VISIBLE,ID_RUN,8,8,100,27,h_btn_run
    CHILD class_button,label_open,WS_CHILD|WS_VISIBLE,ID_OPEN,114,8,100,27,h_btn_open
    CHILD class_button,label_save,WS_CHILD|WS_VISIBLE,ID_SAVE,220,8,100,27,h_btn_save
    CHILD class_button,label_example,WS_CHILD|WS_VISIBLE,ID_EXAMPLE,326,8,125,27,h_btn_example
    CHILD class_button,label_send,WS_CHILD|WS_VISIBLE,ID_SEND,458,8,75,27,h_btn_send
    CHILD class_button,label_clear,WS_CHILD|WS_VISIBLE,ID_CLEAR,539,8,120,27,h_btn_clear
    CHILD class_edit,empty_text,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_MULTILINE|ES_READONLY|WS_VSCROLL,ID_GUTTER,10,45,50,420,h_gutter
    CHILD class_richedit,example_start,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_MULTILINE|ES_AUTOVSCROLL|ES_WANTRETURN|WS_VSCROLL,ID_EDITOR,62,45,780,420,h_editor
    CHILD class_list,empty_text,WS_CHILD|WS_VISIBLE|WS_BORDER|WS_VSCROLL|LBS_NOTIFY,ID_LIST,848,45,290,420,h_examples
    CHILD class_edit,msg_ready,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_MULTILINE|ES_AUTOVSCROLL|ES_READONLY|WS_VSCROLL,ID_OUTPUT,10,500,1120,145,h_output
    CHILD class_edit,empty_text,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_AUTOHSCROLL,ID_SHELL,10,659,1120,30,h_shell
%unmacro CHILD 9
    ; RichEdit enables EN_CHANGE notifications for syntax/line refresh.
    mov rcx,[rel h_editor]
    mov edx,EM_SETEVENTMASK
    xor r8d,r8d
    mov r9d,1                    ; ENM_CHANGE
    call send_message
    ; Shell Enter key invokes compilation, while default EDIT procedure
    ; continues to handle non-Enter keys normally.
    mov rcx,[rel h_shell]
    mov edx,GWLP_WNDPROC
    PTR r8,shell_proc
    API SetWindowLongPtrA
    mov [rel old_shell_proc],rax
    call fill_examples
    call update_lines
    call highlight_editor
    EPILOG

; Layout uses available client space; output and shell remain beneath editor.
; rcx hwnd.
layout_controls:
    PROLOG 176
    PTR rdx,client_rect
    API GetClientRect
    PTR r10,client_rect
    mov eax,[r10+8]
    mov [rbp-4],eax             ; width
    mov eax,[r10+12]
    mov [rbp-8],eax             ; height
    mov eax,[rbp-4]
    cmp eax,560
    jge .wide
    mov eax,560
.wide:
    mov [rbp-12],eax
    mov eax,[rbp-8]
    cmp eax,420
    jge .tall
    mov eax,420
.tall:
    sub eax,250
    mov [rbp-16],eax            ; editor height
    mov eax,[rbp-12]
    sub eax,300
    mov [rbp-20],eax            ; editor width (before gutter)
    ; buttons fixed; editor and list resize.
    mov rcx,[rel h_gutter]
    mov edx,8
    mov r8d,42
    mov r9d,45
    mov qword [rsp+32],48
    mov eax,[rbp-16]
    mov [rsp+40],rax
    mov qword [rsp+48],1
    API MoveWindow
    mov rcx,[rel h_editor]
    mov edx,58
    mov r8d,42
    mov r9d,[rbp-20]
    sub r9d,48
    mov eax,[rbp-16]
    mov [rsp+40],rax
    mov qword [rsp+32],0
    mov qword [rsp+48],1
    API MoveWindow
    mov rcx,[rel h_examples]
    mov edx,[rbp-20]
    add edx,16
    mov r8d,42
    mov r9d,280
    mov eax,[rbp-16]
    mov [rsp+40],rax
    mov qword [rsp+32],280
    mov qword [rsp+48],1
    API MoveWindow
    mov rcx,[rel h_output]
    mov edx,8
    mov eax,[rbp-16]
    add eax,55
    mov r8d,eax
    mov r9d,[rbp-12]
    sub r9d,24
    mov qword [rsp+32],145
    mov qword [rsp+40],1
    API MoveWindow
    mov rcx,[rel h_shell]
    mov edx,8
    mov eax,[rbp-16]
    add eax,208
    mov r8d,eax
    mov r9d,[rbp-12]
    sub r9d,24
    mov qword [rsp+32],27
    mov qword [rsp+40],1
    API MoveWindow
    EPILOG

; UPDATE_LINES: line numbers reflect editor line count after every edit.
; Plain EDIT gutter is currently not scroll-synchronized on all mouse events;
; tracked in manual checklist (not claimed production-grade).
update_lines:
    PROLOG 96
    cmp dword [rel is_lineupdating],0
    jne .end
    mov dword [rel is_lineupdating],1
    mov rcx,[rel h_editor]
    mov edx,EM_GETLINECOUNT
    xor r8d,r8d
    xor r9d,r9d
    call send_message
    cmp eax,1
    jge .min
    mov eax,1
.min:
    cmp eax,999
    jle .cap
    mov eax,999
.cap:
    mov [rbp-4],eax
    PTR r10,line_text
    mov [rbp-16],r10
    mov dword [rbp-8],1
.next:
    mov eax,[rbp-8]
    mov r10,[rbp-16]
    call append_decimal_crlf
    mov [rbp-16],r10
    inc dword [rbp-8]
    mov eax,[rbp-8]
    cmp eax,[rbp-4]
    jle .next
    mov byte [r10],0
    mov rcx,[rel h_gutter]
    PTR rdx,line_text
    API SetWindowTextA
    mov dword [rel is_lineupdating],0
.end:
    EPILOG

; eax unsigned 1..999; r10 buffer pointer; returns updated r10.
append_decimal_crlf:
    mov edx,0
    mov ecx,100
    div ecx
    add al,'0'
    mov [r10],al
    inc r10
    mov eax,edx
    xor edx,edx
    mov ecx,10
    div ecx
    add al,'0'
    mov [r10],al
    inc r10
    add dl,'0'
    mov [r10],dl
    mov word [r10+1],0x0A0D
    add r10,3
    ret

; Language pack loader (compile-time independent, only at GUI startup).
; All ten official UTF-8 *.lang files are read, so users can mix native scripts.
; The stable pack format is "<native token> <romanized token>" with # comments.
; Capacity is bounded: 384 tokens * 64 UTF-16 code units, 8191-byte pack.
; The pack never contributes generated instructions or changes Sutram's ABI.
load_native_keyword_packs:
    PROLOG 160
    PTR rax,kw_pack_paths
    mov [rbp-8],rax
.next_pack:
    mov r10,[rbp-8]
    mov rcx,[r10]
    test rcx,rcx
    jz .done
    mov edx,GENERIC_READ
    mov r8d,FILE_SHARE_READ
    xor r9d,r9d
    mov qword [rsp+32],OPEN_EXISTING
    mov qword [rsp+40],FILE_ATTRIBUTE_NORMAL
    mov qword [rsp+48],0
    API CreateFileW
    cmp rax,INVALID_HANDLE
    je .missing
    mov [rbp-16],rax
    mov rcx,rax
    PTR rdx,native_pack_bytes
    mov r8d,MAX_LANG_FILE
    PTR r9,bytes_count
    mov qword [rsp+32],0
    API ReadFile
    mov [rbp-20],eax
    mov rcx,[rbp-16]
    API CloseHandle
    cmp dword [rbp-20],0
    je .missing
    mov eax,[rel bytes_count]
    test eax,eax
    jz .missing
    cmp eax,MAX_LANG_FILE
    jae .missing               ; reject possibly truncated pack
    PTR rdx,native_pack_bytes
    mov byte [rdx+rax],0
    call parse_native_keyword_pack
    inc dword [rel native_pack_count]
    jmp .advance
.missing:
    inc dword [rel native_pack_errors]
.advance:
    add qword [rbp-8],8
    jmp .next_pack
.done:
    EPILOG

; Bounded UTF-8 line parser. Reads only the first whitespace-delimited token
; from every non-comment line; never consumes/changes the source editor buffer.
parse_native_keyword_pack:
    PROLOG 144
    PTR rax,native_pack_bytes
    mov [rbp-8],rax             ; scan pointer
.line:
    mov r10,[rbp-8]
    movzx eax,byte [r10]
    test al,al
    jz .done
    cmp al,'#'
    je .skip_line
    cmp al,13
    je .skip_line
    cmp al,10
    je .skip_line
    cmp al,' '
    je .skip_line
    cmp al,9
    je .skip_line
    PTR r11,native_pack_word
    xor ecx,ecx
.copy_word:
    mov r10,[rbp-8]
    movzx eax,byte [r10+rcx]
    test al,al
    jz .end_word
    cmp al,32
    jbe .end_word
    cmp ecx,254
    jae .skip_line             ; malformed token: do not truncate
    mov [r11+rcx],al
    inc ecx
    jmp .copy_word
.end_word:
    test ecx,ecx
    jz .skip_line
    mov byte [r11+rcx],0
    mov eax,[rel native_keyword_count]
    cmp eax,MAX_NATIVE_KEYWORDS
    jae .skip_line
    shl rax,7                 ; 64 UTF-16 units per slot
    PTR rdx,native_keyword_storage
    add rdx,rax
    PTR rcx,native_pack_word
    mov r8d,NATIVE_KEYWORD_UNITS
    call utf8_to_utf16        ; strict UTF-8, no replacement code points
    test eax,eax
    jz .skip_line
    inc dword [rel native_keyword_count]
.skip_line:
    mov r10,[rbp-8]
.skip_chars:
    mov al,[r10]
    test al,al
    jz .done
    inc r10
    cmp al,10
    jne .skip_chars
    mov [rbp-8],r10
    jmp .line
.done:
    EPILOG

; rcx is a pointer into UTF-16 editor source at a script identifier start.
; Return keyword length in UTF-16 code units or zero. Whole-token matching.
native_keyword_match:
    PROLOG 96
    mov [rbp-8],rcx
    xor r10d,r10d
.token:
    cmp r10d,[rel native_keyword_count]
    jae .not_found
    mov r11,r10
    shl r11,7
    PTR r9,native_keyword_storage
    add r9,r11
    mov r8,[rbp-8]
    xor ecx,ecx
.compare:
    movzx eax,word [r9+rcx*2]
    test ax,ax
    jz .matched
    cmp ax,[r8+rcx*2]
    jne .next
    inc ecx
    cmp ecx,NATIVE_KEYWORD_UNITS-1
    jb .compare
    jmp .next
.matched:
    movzx eax,word [r8+rcx*2]
    call is_ident_u16
    test eax,eax
    jnz .next
    mov eax,ecx
    jmp .done
.next:
    inc r10d
    jmp .token
.not_found:
    xor eax,eax
.done:
    EPILOG

; EAX=1 for Latin identifier characters or Brahmic-script characters/marks.
; Count full UTF-16 code units, including combining signs (virama/matra).
; This is a conservative scanner for U+0900..U+0DFF, not a Unicode UAX#29 lexer.
is_ident_u16:
    cmp ax,0x0900
    jb .latin
    cmp ax,0x0DFF
    jbe .yes
    cmp ax,0x200C               ; ZWNJ / ZWJ inside orthographic clusters
    je .yes
    cmp ax,0x200D
    je .yes
    xor eax,eax
    ret
.latin:
    jmp is_ident_byte
.yes:
    mov eax,1
    ret

; Native RichEdit keyword coloring. The lexer intentionally skips quoted
; strings, # line comments and // line comments. Latin built-ins and all
; loaded native *.lang tokens share the same UTF-16 RichEdit colour path.
highlight_editor:
    PROLOG 176
    cmp dword [rel is_highlighting],0
    jne .done
    mov dword [rel is_highlighting],1
    mov rcx,[rel h_editor]
    PTR rdx,editor_utf16
    mov r8d,65536
    API GetWindowTextW
    mov [rbp-8],eax
    ; Save selection: don't move user's cursor while recoloring.
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,ch_start
    PTR r9,ch_end
    call send_message
    mov dword [rel char_fmt],60
    mov dword [rel char_fmt+4],CFM_COLOR
    mov dword [rel char_fmt+8],0
    mov dword [rel char_fmt+20],0x202020
    mov rcx,[rel h_editor]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_ALL
    PTR r9,char_fmt
    call send_message
    PTR r10,editor_utf16
    mov [rbp-16],r10
    mov dword [rbp-24],0
.scan:
    mov r10,[rbp-16]
    mov dx,[r10]
    test dx,dx
    jz .restore
    cmp dx,'"'
    je .quoted
    cmp dx,39
    je .quoted
    cmp dx,'#'
    je .comment
    cmp dx,'/'
    jne .word
    cmp word [r10+2],'/'
    je .comment
.word:
    ; Match only at word start, then whole-keyword boundary.
    cmp dx,127
    ja .native_word
    mov al,dl
    call is_ident_byte
    test eax,eax
    jz .advance
    mov eax,[rbp-24]
    test eax,eax
    jz .try_words
    mov r11,[rbp-16]
    mov ax,[r11-2]
    call is_ident_u16
    test eax,eax
    jnz .advance
.try_words:
    PTR r11,kw_words
    mov [rbp-32],r11
.kw_loop:
    mov r11,[rbp-32]
    cmp byte [r11],0
    je .advance
    mov [rbp-40],r11
    mov r10,[rbp-16]
    xor ecx,ecx
.kw_cmp:
    mov r11,[rbp-40]
    movzx eax,byte [r11+rcx]
    test eax,eax
    jz .kw_found
    cmp ax,[r10+rcx*2]
    jne .kw_next
    inc ecx
    cmp ecx,32
    jl .kw_cmp
    jmp .kw_next
.kw_found:
    mov ax,[r10+rcx*2]
    call is_ident_u16
    test eax,eax
    jnz .kw_next
    mov [rbp-44],ecx
    jmp .paint_keyword
.native_word:
    ; Existing left-to-right lexer already excluded quoted strings/comments.
    mov ax,[r10]
    call is_ident_u16
    test eax,eax
    jz .advance
    cmp dword [rbp-24],0
    jz .native_start
    mov r11,[rbp-16]
    mov ax,[r11-2]
    call is_ident_u16
    test eax,eax
    jnz .advance
.native_start:
    mov rcx,[rbp-16]
    call native_keyword_match
    test eax,eax
    jz .advance
    mov [rbp-44],eax
.paint_keyword:
    ; index is measured in UTF-16 code units, including surrogate pairs.
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,[rbp-24]
    mov r9d,r8d
    add r9d,[rbp-44]
    call send_message
    mov dword [rel char_fmt+20],0xB56817 ; blue-ish COLORREF
    mov rcx,[rel h_editor]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_SELECTION
    PTR r9,char_fmt
    call send_message
    mov dword [rel char_fmt+20],0x202020
    jmp .advance
.kw_next:
    mov r11,[rbp-32]
.skip:
    cmp byte [r11],0
    je .nextkw
    inc r11
    jmp .skip
.nextkw:
    inc r11
    mov [rbp-32],r11
    jmp .kw_loop
.quoted:
    mov [rbp-48],dx
    add qword [rbp-16],2
    inc dword [rbp-24]
.quote_loop:
    mov r10,[rbp-16]
    mov ax,[r10]
    test ax,ax
    jz .restore
    cmp ax,'\'
    je .escape
    cmp ax,[rbp-48]
    je .quote_end
    add qword [rbp-16],2
    inc dword [rbp-24]
    jmp .quote_loop
.escape:
    add qword [rbp-16],2
    inc dword [rbp-24]
    mov r10,[rbp-16]
    cmp word [r10],0
    je .restore
    add qword [rbp-16],2
    inc dword [rbp-24]
    jmp .quote_loop
.quote_end:
    jmp .advance
.comment:
    mov r10,[rbp-16]
    cmp word [r10],10
    je .advance
    cmp word [r10],13
    je .advance
    cmp word [r10],0
    je .restore
    add qword [rbp-16],2
    inc dword [rbp-24]
    jmp .comment
.advance:
    add qword [rbp-16],2
    inc dword [rbp-24]
    jmp .scan
.restore:
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,[rel ch_start]
    mov r9d,[rel ch_end]
    call send_message
    mov dword [rel is_highlighting],0
.done:
    EPILOG

; Input AL: ASCII identifier? letters/digits/_ . eax boolean.
is_ident_byte:
    cmp al,'_'
    je .yes
    cmp al,'0'
    jb .no
    cmp al,'9'
    jbe .yes
    cmp al,'A'
    jb .no
    cmp al,'Z'
    jbe .yes
    cmp al,'a'
    jb .no
    cmp al,'z'
    jbe .yes
.no:
    xor eax,eax
    ret
.yes:
    mov eax,1
    ret


; STRICT Unicode bridges. Source is nul-terminated, output capacity includes nul.
; Conversion uses Windows' installed ntdll/kernel32 Unicode services, no CRT.
; Invalid UTF-8, isolated surrogates, or truncation returns eax=0.
; Win64 shadow space + fifth/sixth args are present in PROLOG 128 frame.
utf8_to_utf16:
    PROLOG 128
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    mov [rbp-20],r8d
    mov ecx,65001                 ; CP_UTF8
    mov edx,8                     ; MB_ERR_INVALID_CHARS
    mov r8,[rbp-8]
    mov r9d,-1                    ; source nul-terminated
    mov rax,[rbp-16]
    mov [rsp+32],rax
    mov eax,[rbp-20]
    mov [rsp+40],rax
    API MultiByteToWideChar
    EPILOG

utf16_to_utf8:
    PROLOG 128
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    mov [rbp-20],r8d
    mov ecx,65001                 ; CP_UTF8
    mov edx,0x80                  ; WC_ERR_INVALID_CHARS
    mov r8,[rbp-8]
    mov r9d,-1
    mov rax,[rbp-16]
    mov [rsp+32],rax
    mov eax,[rbp-20]
    mov [rsp+40],rax
    mov qword [rsp+48],0
    mov qword [rsp+56],0
    API WideCharToMultiByte
    EPILOG

; Editor UTF-16 to native Sutram UTF-8. eax=1 success, 0 error.
editor_read_utf8:
    PROLOG 96
    mov rcx,[rel h_editor]
    PTR rdx,editor_utf16
    mov r8d,65536
    API GetWindowTextW
    test eax,eax
    jz .maybe_empty
    cmp eax,65534
    jae .fail
.convert:
    PTR rcx,editor_utf16
    PTR rdx,edit_buffer
    mov r8d,MAX_EDIT
    call utf16_to_utf8
    test eax,eax
    setnz al
    movzx eax,al
    jmp .done
.maybe_empty:
    ; A zero-length editor is valid, but a conversion error is not.
    PTR r10,editor_utf16
    mov word [r10],0
    jmp .convert
.fail:
    xor eax,eax
.done:
    EPILOG

; rcx: validated UTF-8 text, display in Unicode RichEdit (not ANSI).
editor_set_utf8:
    PROLOG 96
    PTR rdx,editor_utf16
    mov r8d,65536
    call utf8_to_utf16
    test eax,eax
    jz .fail
    mov rcx,[rel h_editor]
    PTR rdx,editor_utf16
    API SetWindowTextW
    jmp .done
.fail:
    xor eax,eax
.done:
    EPILOG

; File dialogs (Win32 common dialogs, not third party).
open_dialog:
    PROLOG 96
    call dialog_common
    PTR rcx,ofn_struct
    API GetOpenFileNameW
    test eax,eax
    jz .end
    PTR rcx,current_file
    call load_file
.end:
    EPILOG
save_dialog:
    PROLOG 96
    call dialog_common
    PTR r10,ofn_struct
    or dword [r10+96],OFN_OVERWRITEPROMPT
    PTR rcx,ofn_struct
    API GetSaveFileNameW
    test eax,eax
    jz .end
    PTR rcx,current_file
    call save_file
.end:
    EPILOG

dialog_common:
    PROLOG 64
    PTR r10,ofn_struct
    mov dword [r10],152
    mov r11,[rel h_main]
    mov [r10+8],r11
    PTR r11,file_filter_w
    mov [r10+24],r11
    PTR r11,current_file
    mov [r10+48],r11
    mov dword [r10+56],520
    mov dword [r10+96],OFN_EXPLORER|OFN_NOCHANGEDIR|OFN_PATHMUSTEXIST
    EPILOG

; Read up to 64 KiB, reject larger file, never silently truncate.
; rcx path, return eax=1 success, 0 failure.
load_file:
    PROLOG 112
    mov [rbp-8],rcx
    mov edx,GENERIC_READ
    mov r8d,FILE_SHARE_READ
    xor r9d,r9d
    mov qword [rsp+32],OPEN_EXISTING
    mov qword [rsp+40],FILE_ATTRIBUTE_NORMAL
    mov qword [rsp+48],0
    API CreateFileW
    cmp rax,INVALID_HANDLE
    je .fail
    mov [rbp-16],rax
    mov rcx,rax
    PTR rdx,file_buffer
    mov r8d,MAX_EDIT
    PTR r9,bytes_count
    mov qword [rsp+32],0
    API ReadFile
    mov [rbp-24],rax
    mov rcx,[rbp-16]
    API CloseHandle
    cmp dword [rbp-24],0
    je .fail
    mov ecx,[rel bytes_count]
    cmp ecx,MAX_EDIT
    jae .too_big
    PTR r10,file_buffer
    mov byte [r10+rcx],0
    PTR rcx,file_buffer
    call editor_set_utf8
    test eax,eax
    jz .fail
    mov eax,1
    jmp .end
.too_big:
    PTR rcx,msg_input_large
    call output_append
.fail:
    xor eax,eax
.end:
    EPILOG

; Save full editor text. rcx path, eax success/fail.
save_file:
    PROLOG 128
    mov [rbp-8],rcx
    call editor_read_utf8
    test eax,eax
    jz .fail
    PTR rcx,edit_buffer
    call string_length
    mov [rbp-12],eax
    mov rcx,[rbp-8]
    mov edx,GENERIC_WRITE
    xor r8d,r8d
    xor r9d,r9d
    mov qword [rsp+32],CREATE_ALWAYS
    mov qword [rsp+40],FILE_ATTRIBUTE_NORMAL
    mov qword [rsp+48],0
    API CreateFileW
    cmp rax,INVALID_HANDLE
    je .fail
    mov [rbp-24],rax
    mov rcx,rax
    PTR rdx,edit_buffer
    mov r8d,[rbp-12]
    PTR r9,bytes_count
    mov qword [rsp+32],0
    API WriteFile
    mov [rbp-28],eax
    mov rcx,[rbp-24]
    API CloseHandle
    mov eax,[rbp-28]
    test eax,eax
    jz .fail
    mov eax,[rbp-12]
    cmp eax,[rel bytes_count]
    sete al
    movzx eax,al
    jmp .done
.fail:
    xor eax,eax
    PTR rcx,msg_file_failed
    call output_append
.done:
    EPILOG

; Populate listbox from examples folder; no recursive directory traversal.
fill_examples:
    PROLOG 112
    PTR rcx,examples_glob
    PTR rdx,find_data
    API FindFirstFileA
    cmp rax,INVALID_HANDLE
    je .end
    mov [rbp-8],rax
.next:
    PTR r10,find_data
    test dword [r10],0x10          ; FILE_ATTRIBUTE_DIRECTORY
    jnz .skip
    mov rcx,[rel h_examples]
    mov edx,LB_ADDSTRING
    xor r8d,r8d
    PTR r9,find_data
    add r9,44
    call send_message
.skip:
    mov rcx,[rbp-8]
    PTR rdx,find_data
    API FindNextFileA
    test eax,eax
    jnz .next
    mov rcx,[rbp-8]
    API FindClose
.end:
    EPILOG

load_example:
    PROLOG 112
    mov rcx,[rel h_examples]
    mov edx,LB_GETCURSEL
    xor r8d,r8d
    xor r9d,r9d
    call send_message
    cmp eax,-1
    je .end
    mov [rbp-8],eax
    mov rcx,[rel h_examples]
    mov edx,LB_GETTEXT
    mov r8d,[rbp-8]
    PTR r9,example_name
    call send_message
    PTR rcx,examples_dir
    PTR rdx,example_name
    ; Construct examples relative pathname without losing Unicode dialog state.
    ; Stage ASCII folder and list name in a bounded UTF-8 scratch buffer.
    PTR rdx,edit_buffer
    call string_copy
    PTR rcx,edit_buffer
    PTR rdx,example_name
    call string_concat
    PTR rcx,edit_buffer
    PTR rdx,current_file
    mov r8d,520
    call utf8_to_utf16
    test eax,eax
    jz .end
    PTR rcx,current_file
    call load_file
.end:
    EPILOG

; Append a string to output control without moving existing user text.
; rcx = nul-terminated string.
output_append:
    PROLOG 64
    mov [rbp-8],rcx
    mov rcx,[rel h_output]
    mov edx,EM_SETREADONLY
    xor r8d,r8d
    xor r9d,r9d
    call send_message
    mov rcx,[rel h_output]
    mov edx,EM_SETSEL
    mov r8d,-1
    mov r9d,-1
    call send_message
    mov rcx,[rbp-8]
    PTR rdx,output_utf16
    mov r8d,32768
    call utf8_to_utf16
    test eax,eax
    jz .legacy_text
    mov rcx,[rel h_output]
    mov edx,EM_REPLACESEL
    xor r8d,r8d
    PTR r9,output_utf16
    API SendMessageW
    jmp .restore_readonly
.legacy_text:
    ; Non-UTF8 subprocess output falls back to documented ANSI presentation.
    mov rcx,[rel h_output]
    mov edx,EM_REPLACESEL
    xor r8d,r8d
    mov r9,[rbp-8]
    call send_message
.restore_readonly:
    mov rcx,[rel h_output]
    mov edx,EM_SETREADONLY
    mov r8d,1
    xor r9d,r9d
    call send_message
    EPILOG

; Write a generated Sutram source buffer to temporary file.
; rcx source, returns eax=1/0. Used by both Run and accumulated shell.
write_temp:
    PROLOG 128
    mov [rbp-8],rcx
    call string_length
    mov [rbp-12],eax
    PTR rcx,temp_path
    mov edx,GENERIC_WRITE
    xor r8d,r8d
    xor r9d,r9d
    mov qword [rsp+32],CREATE_ALWAYS
    mov qword [rsp+40],FILE_ATTRIBUTE_NORMAL
    mov qword [rsp+48],0
    API CreateFileW
    cmp rax,INVALID_HANDLE
    je .fail
    mov [rbp-24],rax
    mov rcx,rax
    mov rdx,[rbp-8]
    mov r8d,[rbp-12]
    PTR r9,bytes_count
    mov qword [rsp+32],0
    API WriteFile
    mov [rbp-28],eax
    mov rcx,[rbp-24]
    API CloseHandle
    mov eax,[rbp-28]
    test eax,eax
    jz .fail
    mov eax,[rel bytes_count]
    cmp eax,[rbp-12]
    jne .fail
    mov eax,1
    jmp .end
.fail:
    xor eax,eax
.end:
    EPILOG

; Build CreateProcess command line with quoted pathname arguments.
; Compiler path and user-data file names are quotes-only, no cmd.exe shell.
; Precondition: all paths <=520 bytes and do not contain embedded quotes.
; Windows paths may contain Unicode unavailable to ANSI APIs; this preview
; will reject these in the future UTF16 version.
compose_compile:
    PROLOG 80
    PTR r10,command_line
    mov word [r10],'"'
    mov word [r10+2],0
    PTR rcx,command_line
    PTR rdx,compiler_path
    call wide_command_concat
    PTR rcx,command_line
    PTR rdx,quote_space_quote_w
    call wide_command_concat
    PTR rcx,command_line
    PTR rdx,temp_path
    call wide_command_concat
    PTR rcx,command_line
    PTR rdx,quote_space_quote_w
    call wide_command_concat
    PTR rcx,command_line
    PTR rdx,temp_binary
    call wide_command_concat
    PTR rcx,command_line
    PTR rdx,quote_only_w
    call wide_command_concat
    EPILOG

; spawn_capture: rcx mutable command line; output_buffer receives captured
; stdout+stderr, bounded at 32KiB. On timeout, terminate only spawned child.
; eax=1 on exit code 0, 0 on error/timeout; last_exit_code captures status.
; This is a synchronous *preview* implementation; UI pauses during execution.
spawn_capture:
    PROLOG 224
    mov [rbp-8],rcx
    PTR r10,output_buffer
    mov byte [r10],0
    mov dword [rbp-12],0            ; accumulated stdout bytes
    mov dword [rel last_exit_code],-1
    PTR r10,sa_struct
    mov dword [r10],24
    mov qword [r10+8],0
    mov dword [r10+16],1
    PTR rcx,pipe_rd
    PTR rdx,pipe_wr
    PTR r8,sa_struct
    xor r9d,r9d
    API CreatePipe
    test eax,eax
    jz .failed
    mov rcx,[rel pipe_rd]
    mov edx,HANDLE_FLAG_INHERIT
    xor r8d,r8d
    API SetHandleInformation
    ; Use redirected stdout and stderr, never expose console window.
    PTR r10,si_struct
    mov dword [r10],104
    mov dword [r10+60],STARTF_USESTDHANDLES
    mov qword [r10+80],0
    mov r11,[rel pipe_wr]
    mov [r10+88],r11
    mov [r10+96],r11
    xor ecx,ecx
    mov rdx,[rbp-8]
    xor r8d,r8d
    xor r9d,r9d
    mov qword [rsp+32],1
    mov qword [rsp+40],CREATE_NO_WINDOW
    mov qword [rsp+48],0
    mov qword [rsp+56],0
    PTR r10,si_struct
    mov [rsp+64],r10
    PTR r10,pi_struct
    mov [rsp+72],r10
    API CreateProcessW
    mov [rbp-16],eax
    mov rcx,[rel pipe_wr]
    API CloseHandle
    mov qword [rel pipe_wr],0
    cmp dword [rbp-16],0
    je .close_read
    mov rcx,[rel pi_struct+8]    ; hThread
    API CloseHandle
    API GetTickCount64
    mov [rel process_start],rax
.poll:
    ; Check for captured bytes without blocking while process is live.
    mov rcx,[rel pipe_rd]
    xor edx,edx
    xor r8d,r8d
    xor r9d,r9d
    ; PeekNamedPipe's 5th arg is lpTotalBytesAvail, 6th is
    ; lpBytesLeftThisMessage (always 0 for anonymous pipes).
    ; The old source put pipe_available in arg6 and therefore
    ; never observed pending stdout/stderr bytes.
    PTR r10,pipe_available
    mov [rsp+32],r10
    mov qword [rsp+40],0
    API PeekNamedPipe
    test eax,eax
    jz .process_state
    mov eax,[rel pipe_available]
    test eax,eax
    jz .process_state
    mov edx,MAX_OUTPUT
    sub edx,[rbp-12]
    jle .discard_limit
    cmp eax,edx
    jbe .readsize
    mov eax,edx
.readsize:
    mov [rbp-20],eax
    mov rcx,[rel pipe_rd]
    PTR rdx,output_buffer
    mov eax,[rbp-12]
    add rdx,rax
    mov r8d,[rbp-20]
    PTR r9,bytes_count
    mov qword [rsp+32],0
    API ReadFile
    test eax,eax
    jz .process_state
    mov eax,[rel bytes_count]
    add [rbp-12],eax
    PTR r10,output_buffer
    mov ecx,[rbp-12]
    mov byte [r10+rcx],0
    jmp .process_state
.discard_limit:
    ; Child can block if pipe fills. Terminate and clearly report truncated.
    PTR rcx,msg_more_output
    call output_append
    mov rcx,[rel pi_struct]
    mov edx,1
    API TerminateProcess
    jmp .finish
.process_state:
    mov rcx,[rel pi_struct]
    mov edx,25
    API WaitForSingleObject
    cmp eax,WAIT_OBJECT_0
    je .drain
    API GetTickCount64
    sub rax,[rel process_start]
    cmp rax,10000
    jb .poll
    mov rcx,[rel pi_struct]
    mov edx,124
    API TerminateProcess
    PTR rcx,msg_timeout
    call output_append
    jmp .finish
.drain:
    ; One final pipe read before closing; cap applies here as well.
    mov rcx,[rel pipe_rd]
    xor edx,edx
    xor r8d,r8d
    xor r9d,r9d
    ; PeekNamedPipe's 5th arg is lpTotalBytesAvail, 6th is
    ; lpBytesLeftThisMessage (always 0 for anonymous pipes).
    ; The old source put pipe_available in arg6 and therefore
    ; never observed pending stdout/stderr bytes.
    PTR r10,pipe_available
    mov [rsp+32],r10
    mov qword [rsp+40],0
    API PeekNamedPipe
    test eax,eax
    jz .exit_code
    mov eax,[rel pipe_available]
    test eax,eax
    jz .exit_code
    mov edx,MAX_OUTPUT
    sub edx,[rbp-12]
    cmp eax,edx
    jbe .drain_size
    mov eax,edx
.drain_size:
    test eax,eax
    jz .exit_code
    mov r8d,eax
    mov rcx,[rel pipe_rd]
    PTR rdx,output_buffer
    mov eax,[rbp-12]
    add rdx,rax
    PTR r9,bytes_count
    mov qword [rsp+32],0
    API ReadFile
    test eax,eax
    jz .exit_code
    mov eax,[rel bytes_count]
    add [rbp-12],eax
    PTR r10,output_buffer
    mov ecx,[rbp-12]
    mov byte [r10+rcx],0
.exit_code:
    mov rcx,[rel pi_struct]
    PTR rdx,last_exit_code
    API GetExitCodeProcess
.finish:
    mov rcx,[rel pi_struct]
    API CloseHandle
.close_read:
    mov rcx,[rel pipe_rd]
    API CloseHandle
    mov eax,[rel last_exit_code]
    test eax,eax
    setz al
    movzx eax,al
    jmp .end
.failed:
    PTR rcx,msg_pipe_fail
    call output_append
    xor eax,eax
.end:
    EPILOG

; Compiler+run; rcx -> Sutram source; output_buffer captures only the
; *last* subprocess (compiler error OR program stdout/stderr).
compile_run:
    PROLOG 80
    mov [rbp-8],rcx
    call write_temp
    test eax,eax
    jz .failed
    call compose_compile
    PTR rcx,command_line
    call spawn_capture
    test eax,eax
    jz .failed
    PTR r10,command_line
    mov word [r10],'"'
    mov word [r10+2],0
    PTR rcx,command_line
    PTR rdx,temp_binary
    call wide_command_concat
    PTR rcx,command_line
    PTR rdx,quote_only_w
    call wide_command_concat
    PTR rcx,command_line
    call spawn_capture
    jmp .end
.failed:
    xor eax,eax
.end:
    EPILOG

run_editor:
    PROLOG 80
    call editor_read_utf8
    test eax,eax
    jz .failed_unicode
    PTR rcx,edit_buffer
    call compile_run
    mov [rbp-4],eax
    PTR rcx,output_buffer
    PTR rdx,output_utf16
    mov r8d,32768
    call utf8_to_utf16
    test eax,eax
    jz .ansi_stdout
    mov rcx,[rel h_output]
    PTR rdx,output_utf16
    API SetWindowTextW
    jmp .printed
.ansi_stdout:
    mov rcx,[rel h_output]
    PTR rdx,output_buffer
    API SetWindowTextA
.printed:
    cmp dword [rbp-4],0
    jne .end
    PTR rcx,msg_run_failed
    call output_append
    jmp .end
.failed_unicode:
    PTR rcx,msg_file_failed
    call output_append
.end:
    EPILOG

shell_proc:
    PROLOG 96
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    mov [rbp-24],r8
    mov [rbp-32],r9
    cmp edx,WM_KEYDOWN
    je .key_check
    cmp edx,WM_CHAR
    jne .def
    cmp r8d,VK_RETURN
    je .consume_char
    jmp .def
.key_check:
    cmp r8d,VK_RETURN
    jne .def
    call shell_submit
.consume_char:
    xor eax,eax
    jmp .done
.def:
    mov rcx,[rel old_shell_proc]
    mov rdx,[rbp-8]
    mov r8,[rbp-16]
    mov r9,[rbp-24]
    mov rax,[rbp-32]
    mov [rsp+32],rax
    API CallWindowProcA
.done:
    EPILOG

; Shell: replay previous statements from a generated mukhya() on each Enter.
; Display only the *new* output suffix. Safe for deterministic code, but NOT
; a persistent in-memory REPL; earlier effects are executed again. This is
; disclosed to users. Failed submissions are not committed to session.
shell_submit:
    PROLOG 160
    cmp dword [rel is_shellrunning],0
    jne .end
    mov dword [rel is_shellrunning],1
    mov rcx,[rel h_shell]
    PTR rdx,editor_utf16
    mov r8d,4096
    API GetWindowTextW
    test eax,eax
    jz .endreset
    PTR rcx,editor_utf16
    PTR rdx,shell_input
    mov r8d,4096
    call utf16_to_utf8
    test eax,eax
    jz .limit
    cmp eax,3500
    jg .limit
    ; Construct source in file_buffer: prefix, history, next statement.
    PTR rcx,prefix_s
    PTR rdx,file_buffer
    call string_copy
    PTR rcx,file_buffer
    PTR rdx,shell_history
    call string_concat
    PTR rcx,file_buffer
    PTR rdx,indent_s
    call string_concat
    PTR rcx,file_buffer
    PTR rdx,shell_input
    call string_concat
    PTR rcx,file_buffer
    PTR rdx,newline
    call string_concat
    PTR rcx,file_buffer
    call string_length
    cmp eax,32700
    jae .limit
    PTR rcx,file_buffer
    call compile_run
    test eax,eax
    jz .error
    ; Replay stdout prefix is hidden; only newly emitted suffix is appended.
    PTR rcx,output_buffer
    call string_length
    mov [rbp-8],eax
    mov edx,[rel last_shell_out]
    cmp edx,eax
    ja .full_result
    PTR rcx,output_buffer
    add rcx,rdx
    call output_append
    jmp .commit
.full_result:
    PTR rcx,output_buffer
    call output_append
.commit:
    mov eax,[rbp-8]
    mov [rel last_shell_out],eax
    PTR rcx,shell_history
    PTR rdx,indent_s
    call string_concat
    PTR rcx,shell_history
    PTR rdx,shell_input
    call string_concat
    PTR rcx,shell_history
    PTR rdx,newline
    call string_concat
    mov rcx,[rel h_shell]
    PTR rdx,empty_text
    API SetWindowTextA
    jmp .endreset
.error:
    PTR rcx,output_buffer
    call output_append
    PTR rcx,msg_compile_failed
    call output_append
    jmp .endreset
.limit:
    PTR rcx,msg_shell_limit
    call output_append
.endreset:
    mov dword [rel is_shellrunning],0
.end:
    EPILOG

; PEB kernel32 export resolver included below. Caller-saved local scratch;
; specifically NO manual loading/injection or security-policy modification.
win_kernel32:
    mov rax,[gs:0x60]
    test rax,rax
    jz .fail
    mov rax,[rax+0x18]
    test rax,rax
    jz .fail
    mov rax,[rax+0x20]
    test rax,rax
    jz .fail
    mov rax,[rax]
    test rax,rax
    jz .fail
    mov rax,[rax]
    test rax,rax
    jz .fail
    mov rax,[rax+0x20]
    ret
.fail:
    xor eax,eax
    ret

; rdi = requested kernel32 export, rax = address or 0.
win_resolve:
    ; Windows x64 requires RSI and RDI preserved by callees.
    ; The export-name comparison writes both registers.
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r14
    push r15
    mov r14,rdi
    call win_kernel32
    test rax,rax
    jz .fail
    mov rbx,rax
    mov eax,[rbx+0x3c]
    add rax,rbx
    mov r12d,[rax+24+0x70]
    test r12d,r12d
    jz .fail
    add r12,rbx
    mov r13d,[r12+0x20]
    add r13,rbx
    mov r15d,[r12+0x18]
    xor ecx,ecx
.name:
    cmp ecx,r15d
    jae .fail
    mov eax,[r13+rcx*4]
    add rax,rbx
    mov rsi,rax
    mov rdi,r14
.cmp:
    mov al,[rsi]
    cmp al,[rdi]
    jne .next
    test al,al
    jz .found
    inc rsi
    inc rdi
    jmp .cmp
.next:
    inc ecx
    jmp .name
.found:
    mov r13d,[r12+0x24]
    add r13,rbx
    movzx ecx,word [r13+rcx*2]
    mov r13d,[r12+0x1c]
    add r13,rbx
    mov eax,[r13+rcx*4]
    add rax,rbx
    jmp .done
.fail:
    xor eax,eax
.done:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    ret

section .data
suffix_exe db '.exe',0
quote_space_quote db '" "',0
quote_only db '"',0
empty_text db 0
example_start db 'mukhya()',13,10,'    likha("Namaste, Sutram!\n")',13,10,0
