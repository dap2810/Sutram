; Sutram Windows GUI IDE — experimental native Win64 proof-of-implementation
; Pure NASM -> Win64 PE, Win32 API and MSFTEDIT RichEdit (Windows system DLL).
; NO C/C++/Python or GUI framework in executable. Standard-user only.
; Build: powershell -NoProfile -File windows/gui/build-gui.ps1 (R67 entrypoint).
; Placement: project root alongside win/sutram.exe and examples/.
; Native execution evidence is included in the Windows delivery review.

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
; ---- IDLE-style menu bar (slice 19) ----
%define MF_STRING 0x00000000
%define MF_POPUP  0x00000010
%define MID_OPEN   2001
%define MID_SAVE   2002
%define MID_EXIT   2003
%define MID_RUN    2010
%define MID_CLEAR  2011
%define MID_ABOUT  2020
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
%define EM_SETBKGNDCOLOR 0x443
; COLORREF is 0x00BBGGRR (BGR!).  Palette matches the approved mockup.
%define COL_BG       0x001E1E1E   ; dark canvas
%define COL_TEXT     0x00D4D4D4   ; default foreground
%define COL_KEYWORD  0x00116DE8   ; orange  #E86D11
%define COL_BUILTIN  0x00B0C94E   ; teal    #4EC9B0
%define COL_STRING   0x0055996A   ; green   #6A9955
%define COL_NUMBER   0x00E886B5   ; purple  #B586E8
%define COL_COMMENT  0x006A6A6A   ; grey    #6A6A6A
%define COL_FUNCTION 0x0027A2C9   ; yellow  #C9A227
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
%define MAX_NATIVE_KEYWORDS 512        ; R9: 384 dropped the last Telugu keywords (392 in all)
%define NATIVE_KEYWORD_UNITS 64
%define MAX_LANG_FILE 8191
; ---- R73: Sanskrit interface, editor keys, status line, language packs ----
%define WM_NOTIFY 0x4E
%define WM_CTLCOLOREDIT 0x133
%define WM_CTLCOLORLISTBOX 0x134
%define WM_CTLCOLORSTATIC 0x138
%define WM_CUT 0x300
%define WM_COPY 0x301
%define WM_PASTE 0x302
%define VK_TAB 9
%define VK_SHIFT 0x10
%define VK_F3 0x72
%define EM_LINEFROMCHAR 0xC9
%define EM_LINEINDEX 0xBB
%define EM_GETLINE 0xC4
%define EM_UNDO 0xC7
%define EM_EXSETSEL 0x437
%define EM_FINDTEXTEXW 0x47C
%define ENM_CHANGE 1
%define ENM_SELCHANGE 0x80000
%define EN_SELCHANGE 0x702
%define FR_DOWN 1
%define MF_SEPARATOR 0x800
%define MF_BYCOMMAND 0
%define MB_YESNOCANCEL 3
%define MB_ICONQUESTION 0x20
%define IDCANCEL 2
%define IDYES 6
%define IDNO 7
%define LR_SHARED 0x8000
%define ID_STATUS 206
%define ID_FIND 207
%define ID_FINDLABEL 208
%define MID_NEW 2004
%define MID_SAVEAS 2005
%define MID_SEND 2012
%define MID_KEYS 2021
%define MID_UNDO 2030
%define MID_CUT 2031
%define MID_COPY 2032
%define MID_PASTE 2033
%define MID_SELALL 2034
%define MID_FIND 2036
%define MID_FINDNEXT 2037
%define MID_INDENT 2038
%define MID_UNINDENT 2039
%define MID_LANG_AUTO 2040
%define MID_LANG_CORE 2041
%define MID_LANG_SANSKRIT 2042
%define LANG_AUTO 0
%define LANG_CORE 1
%define LANG_SANSKRIT 2
; R9 (WS6): the other ten packs follow Sanskrit, in kw_pack_paths order
; (bengali .. telugu): lang_mode 3..12, menu ids 2043..2052. For lang_mode >= 2
; the pack index is lang_mode - 2.
%define MID_LANG_LAST 2052
%define MID_TRANSLIT 2053
%define CFM_FACE 0x20000000
%define MF_CHECKED 8
%define R9_MAX_PAIRS 768
%define COL_GUTTER 0x00858585
%define COL_STATUS 0x00B5D8A8

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
app_title db 'Sutram sampadak',0
; R73 made every visible word Sanskrit. R5 (owner's decision, ROUND-05): menus, buttons,
; the find label, the two Help dialogs and the messages that name a control are English.
; The status line and the output messages stay as R73 left them. UTF-16 for Unicode APIs.
align 2
app_class_w:    dw __utf16__("SutramNativeGUIWindow"),0
app_title_w:    dw __utf16__("Sutram sampadak"),0
title_suffix_w: dw __utf16__(" - Sutram sampadak"),0
title_new_w:    dw __utf16__("Untitled"),0
title_mod_w:    dw __utf16__(" *"),0
mn_patra:       dw __utf16__("File"),0
mn_sampad:      dw __utf16__("Edit"),0
mn_chal:        dw __utf16__("Shell"),0
mn_bhasha:      dw __utf16__("Language"),0
mn_sahay:       dw __utf16__("Help"),0
mi_nava:        dw __utf16__("New"),9,__utf16__("Ctrl+N"),0
mi_khol:        dw __utf16__("Open..."),9,__utf16__("Ctrl+O"),0
mi_sanchay:     dw __utf16__("Save"),9,__utf16__("Ctrl+S"),0
mi_saveas:      dw __utf16__("Save As..."),0
mi_nishkas:     dw __utf16__("Exit"),0
mi_punah:       dw __utf16__("Undo"),9,__utf16__("Ctrl+Z"),0
mi_chhid:       dw __utf16__("Cut"),9,__utf16__("Ctrl+X"),0
mi_pratilip:    dw __utf16__("Copy"),9,__utf16__("Ctrl+C"),0
mi_sanyoj:      dw __utf16__("Paste"),9,__utf16__("Ctrl+V"),0
mi_sarvagrah:   dw __utf16__("Select All"),9,__utf16__("Ctrl+A"),0
mi_anwesh:      dw __utf16__("Find..."),9,__utf16__("Ctrl+F"),0
mi_anwesh_agrim: dw __utf16__("Find Next"),9,__utf16__("F3"),0
mi_antar:       dw __utf16__("Indent (4 spaces)"),9,__utf16__("Tab"),0
mi_antar_hatao: dw __utf16__("Dedent"),9,__utf16__("Shift+Tab"),0
mi_chal:        dw __utf16__("Run module"),9,__utf16__("F5"),0
mi_presh:       dw __utf16__("Send (shell line)"),9,__utf16__("Enter"),0
mi_phal_rikta:  dw __utf16__("Clear shell"),0
mi_swayam:      dw __utf16__("Auto (detect script)"),0
mi_mool:        dw __utf16__("Core (Latin keywords)"),0
mi_sanskrit:    dw __utf16__("sanskrit  "),0x0938,0x0902,0x0938,0x094D,0x0915,0x0943,0x0924,0x092E,0x094D,0
; R9 (WS6): the other ten language packs, and the typing mode
mi_lang_bengali:   dw __utf16__("bengali  বাংলা"),0
mi_lang_gujarati:  dw __utf16__("gujarati  ગુજરાતી"),0
mi_lang_hindi:     dw __utf16__("hindi  हिन्दी"),0
mi_lang_kannada:   dw __utf16__("kannada  ಕನ್ನಡ"),0
mi_lang_malayalam: dw __utf16__("malayalam  മലയാളം"),0
mi_lang_marathi:   dw __utf16__("marathi  मराठी"),0
mi_lang_odia:      dw __utf16__("odia  ଓଡ଼ିଆ"),0
mi_lang_punjabi:   dw __utf16__("punjabi  ਪੰਜਾਬੀ"),0
mi_lang_tamil:     dw __utf16__("tamil  தமிழ்"),0
mi_lang_telugu:    dw __utf16__("telugu  తెలుగు"),0
mi_translit:    dw __utf16__("Type Latin, get the script"),9,__utf16__("Ctrl+T"),0
st_lipi_w:      dw __utf16__("   |   lipi: "),0
lang_flag_prefix_w: dw __utf16__(" --lang "),0
; pack names, kw_pack_paths order (the --lang argument and the status line)
pn_sanskrit_w:  dw __utf16__("sanskrit"),0
pn_bengali_w:   dw __utf16__("bengali"),0
pn_gujarati_w:  dw __utf16__("gujarati"),0
pn_hindi_w:     dw __utf16__("hindi"),0
pn_kannada_w:   dw __utf16__("kannada"),0
pn_malayalam_w: dw __utf16__("malayalam"),0
pn_marathi_w:   dw __utf16__("marathi"),0
pn_odia_w:      dw __utf16__("odia"),0
pn_punjabi_w:   dw __utf16__("punjabi"),0
pn_tamil_w:     dw __utf16__("tamil"),0
pn_telugu_w:    dw __utf16__("telugu"),0
mi_kunji:       dw __utf16__("Shortcut keys"),0
mi_parichay:    dw __utf16__("About Sutram"),0
st_pankti_w:    dw __utf16__("pankti "),0
st_stambh_w:    dw __utf16__("   stambh "),0
st_bhasha_w:    dw __utf16__("   |   bhasha: "),0
st_akshara_w:   dw __utf16__("   |   akshara: "),0
st_sep_w:       dw __utf16__("   |   "),0
st_sanchit_w:   dw __utf16__("sanchit"),0
st_asanchit_w:  dw __utf16__("asanchit *"),0
st_notfound_w:  dw __utf16__("anwesh: nahi mila"),0
lang_swayam_w:  dw __utf16__("swayam"),0
lang_swayam_sk_w: dw __utf16__("swayam (sanskrit)"),0
lang_mool_w:    dw __utf16__("mool"),0
lang_sanskrit_w: dw __utf16__("sanskrit"),0
lang_flag_w:    dw __utf16__(" --lang sanskrit"),0
space_quote_w:  dw ' ','"',0
indent4_w:      dw __utf16__("    "),0
empty_w:        dw 0
msg_unsaved_w:  dw __utf16__("The file has changed. Save it?"),0
about_w:        dw __utf16__("Sutram sampadak (Windows)"),13,10,__utf16__("Sanskrit-keyword language -> x86-64 machine code."),13,10,13,10,__utf16__("Shell > Run module (F5) compiles and runs the editor's program."),13,10,__utf16__("For a Devanagari program choose Language > Auto or sanskrit."),13,10,__utf16__("Files are UTF-8. Send replays the shell history."),0
keys_w:         dw __utf16__("F5 / Ctrl+R  Run module"),13,10,__utf16__("Ctrl+N  New     Ctrl+O  Open     Ctrl+S  Save"),13,10,__utf16__("Tab  Indent (4 spaces)     Shift+Tab  Dedent"),13,10,__utf16__("Enter  new line, keeps the indent; +4 after '{'"),13,10,__utf16__("}  on an empty line: indent -4"),13,10,__utf16__("Ctrl+F  Find     F3  Find Next"),13,10,__utf16__("Ctrl+T  type Latin, get the language's script (mukhya -> मुख्य)"),13,10,__utf16__("Ctrl+Z  Undo    Ctrl+X/C/V  Cut/Copy/Paste    Ctrl+A  Select All"),0
find_label_w:   dw __utf16__("Find:"),0
class_button db 'BUTTON',0
class_edit db 'EDIT',0
class_static db 'STATIC',0
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
n_CreateMenu db 'CreateMenu',0
n_CreatePopupMenu db 'CreatePopupMenu',0
n_AppendMenuA db 'AppendMenuA',0
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
; R73: Unicode window class/loop (Devanagari typing), Unicode menus, status
n_RegisterClassExW db 'RegisterClassExW',0
n_CreateWindowExW db 'CreateWindowExW',0
n_DefWindowProcW db 'DefWindowProcW',0
n_GetMessageW db 'GetMessageW',0
n_DispatchMessageW db 'DispatchMessageW',0
n_SetWindowLongPtrW db 'SetWindowLongPtrW',0
n_CallWindowProcW db 'CallWindowProcW',0
n_AppendMenuW db 'AppendMenuW',0
n_CheckMenuRadioItem db 'CheckMenuRadioItem',0
n_MessageBoxW db 'MessageBoxW',0
n_SetFocus db 'SetFocus',0

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
    IMPORTS CreateMenu
    IMPORTS CreatePopupMenu
    IMPORTS AppendMenuA
    IMPORTS RegisterClassExW
    IMPORTS CreateWindowExW
    IMPORTS DefWindowProcW
    IMPORTS GetMessageW
    IMPORTS DispatchMessageW
    IMPORTS SetWindowLongPtrW
    IMPORTS CallWindowProcW
    IMPORTS AppendMenuW
    IMPORTS CheckMenuRadioItem
    IMPORTS MessageBoxW
    IMPORTS SetFocus
    dq 0,0
comdlg_table:
    IMPORTS GetOpenFileNameA
    IMPORTS GetOpenFileNameW
    IMPORTS GetSaveFileNameA
    IMPORTS GetSaveFileNameW
    dq 0,0

; R5: the owner's decision (ROUND-05): the interface labels are English.
; Buttons are the 13/18 Oct words, menus follow the 13 Oct build where it had one.
label_run db 'Run',0
label_open db 'Open',0
label_save db 'Save',0
label_example db 'Load example',0
label_send db 'Send',0
label_clear db 'Clear shell',0
label_output db 'sankalan / chalan ka phal',0
label_shell db '>>>',0
label_examples db 'udaharan (do baar click)',0
err_init db 'Windows API load nahi hui. sampadak shuru nahi ho saka.',0
err_title db 'Sutram sampadak',0
msg_ready db 'Ready. Run (F5) compiles and runs the program in the editor.',13,10,0
msg_compile_failed db '[sankalan asaphal]',13,10,0
msg_run_failed db '[karyakram asamanya roop se samapt]',13,10,0
msg_file_failed db '[patra padhne/likhne me asaphal]',13,10,0
msg_input_large db '[patra bahut bada; sampadak seema 64 KiB]',13,10,0
msg_shell_limit db '[shell history is full; use Clear shell]',13,10,0
msg_timeout db '[prakriya 10 sekand se adhik; samapt ki gayi]',13,10,0
msg_missing_compiler db '[win\sutram.exe nahi mila: pahle sankalak banayein]',13,10,0
msg_missing_lang db '[deshi shabda-pak anupalabdh: lang\*.lang dekhein; Latin shabda kaam karte hain]',13,10,0
msg_partial_lang db '[kuchh shabda-pak anupalabdh ya ashuddh: lang\*.lang dekhein]',13,10,0
msg_pipe_fail db '[prakriya ya pipe nirman asaphal]',13,10,0
msg_more_output db '[phal 32 KiB par kata]',13,10,0
prefix_s db 'mukhya()',13,10,0
indent_s db '    ',0
newline db 13,10,0
file_filter db 'Sutram patra (*.sm)',0,'*.sm',0,'sabhi patra (*.*)',0,'*.*',0,0
align 2
file_filter_w: dw __utf16__("Sutram patra (*.sm)"),0,__utf16__("*.sm"),0,__utf16__("sabhi patra (*.*)"),0,__utf16__("*.*"),0,0
examples_glob db 'examples\*.sm',0
examples_dir db 'examples\',0
compiler_rel db 'win\sutram.exe',0
prefix_gui db 'STG',0
caption_editor db 'Editor',0
; builtins: colour teal, matched the same way as keywords.
; R5: both tables are the compiler's own names (bn_* and kw_* in src/sutram_compiler.asm);
; until R5 they held the pre-v157 names, so vitti/chakra/prati/tak/anya/agrim and the
; renamed builtins were not coloured. tests/gui/test_win_gui_colour_tables.py keeps them equal.
bi_words db 'likh',0,'sthagita',0,'pad',0,'dvaram',0,'paadh',0,'likha',0,'band',0,'netsock',0,\
            'netbind',0,'netlisten',0,'netaccept',0,'nirmmita',0,'likh8',0,'pad8',0,'vartani_len',0,\
            'vartani_cmp',0,'vartani_cat',0,'sankhya_yog',0,'sankhya_gunan',0,'sankhya_dot',0,\
            'likha_fmt',0,'akshar',0,'akshar_rakh',0,'aksharank',0,'pankti_len',0,'kosh_push',0,\
            'kosh_pop',0,'kosh_len',0,'kosh_cap',0,'kosh_clear',0,'kosh_empty',0,'kosh_peek',0,\
            'kosh_enqueue',0,'kosh_dequeue',0,'char_from',0,'char_upper',0,'char_lower',0,\
            'likh8c',0,'pad8c',0,'smaran',0,'smaran_cp',0,'vartani_cp',0,'grahan',0,'lkhb',0,\
            'shabda',0,0
kw_words db 'mukhya',0,'vitti',0,'anka',0,'yadi',0,'yavat',0,'prati',0,'sankhya',0,'anya',0,\
            'prakriya',0,'yoj',0,'rachana',0,'chakra',0,'tak',0,'sutra',0,'abhava',0,'krama',0,\
            'agrim',0,'purna',0,'shunya',0,'satya',0,'ganana',0,'guna',0,'bhavana',0,'mala',0,\
            'yantra',0,'kuru',0,'dasham',0,'kosh',0,0
; Import-table label expansion: function-name symbols n_* via macro.
%unmacro IMPORTS 1
%macro IMPORTS 1
p_%1: resq 1
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
; R73: the Sanskrit (Devanagari) pack is loaded too, so Devanagari Sanskrit keywords colour.
kw_pack_sanskrit_w: dw __utf16__("lang\sanskrit.lang"),0
align 8
r9_pack_names: dq pn_sanskrit_w,pn_bengali_w,pn_gujarati_w,pn_hindi_w,pn_kannada_w,pn_malayalam_w,pn_marathi_w,pn_odia_w,pn_punjabi_w,pn_tamil_w,pn_telugu_w
kw_pack_paths: dq kw_pack_sanskrit_w,kw_pack_bengali_w,kw_pack_gujarati_w,kw_pack_hindi_w,kw_pack_kannada_w,kw_pack_malayalam_w,kw_pack_marathi_w,kw_pack_odia_w,kw_pack_punjabi_w,kw_pack_tamil_w,kw_pack_telugu_w,0
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
; R9 (WS6) typing mode state and the per-pack keyword pairs
r9_tl_on resd 1
r9_cur_pack resd 1
r9_pair_count resd 1
r9_indic_ok resd 1
r9_tmp_sel resd 2
r9_pair_pack resb R9_MAX_PAIRS
r9_pair_roman resb R9_MAX_PAIRS*32
alignb 2
r9_pair_native resw R9_MAX_PAIRS*NATIVE_KEYWORD_UNITS
r9_line_buf resw 2052
r9_out_w resw 512
alignb 4
face_fmt resb 92
native_pack_count resd 1
native_pack_errors resd 1
native_keyword_storage resw MAX_NATIVE_KEYWORDS*NATIVE_KEYWORD_UNITS
native_pack_bytes resb MAX_LANG_FILE+1
native_pack_word resb 256
is_lineupdating resd 1
is_shellrunning resd 1
last_shell_out resd 1
last_exit_code resd 1
last_fail_stage resd 1   ; R4: 1 compile, 2 run, 3 temp file (set by compile_run)
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
h_menu resq 1
pipe_available resd 1
pi_struct resb 24
si_struct resb 104
sa_struct resb 24
pipe_rd resq 1
pipe_wr resq 1
process_start resq 1
; R73 state
h_status resq 1
h_find resq 1
h_find_label resq 1
h_menu_bhasha resq 1
old_editor_proc resq 1
old_find_proc resq 1
bg_brush resq 1
is_modified resd 1
is_loading resd 1
lang_mode resd 1
use_pack resd 1
last_pack resd 1
cluster_count resd 1
title_utf16 resw 1200
status_utf16 resw 512
line_utf16 resw 4096
find_utf16 resw 512
indent_buf resw 160
num_scratch resw 24
findtext resb 32
sel_pos resd 2

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
IMPORTS CreateMenu
IMPORTS CreatePopupMenu
IMPORTS AppendMenuA
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
IMPORTS RegisterClassExW
IMPORTS CreateWindowExW
IMPORTS DefWindowProcW
IMPORTS GetMessageW
IMPORTS DispatchMessageW
IMPORTS SetWindowLongPtrW
IMPORTS CallWindowProcW
IMPORTS AppendMenuW
IMPORTS CheckMenuRadioItem
IMPORTS MessageBoxW
IMPORTS SetFocus
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
    call read_startup_file
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
    mov rax,[rel __imp_LoadLibraryA]
    mov [rel p_LoadLibraryA],rax
    mov rax,[rel __imp_GetProcAddress]
    mov [rel p_GetProcAddress],rax
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
    ; R73: one dark brush for the window background, gutter, shell, list and status.
    mov ecx,COL_BG
    call qword [rel __imp_CreateSolidBrush]
    mov [rel bg_brush],rax
    mov dword [rel cluster_count],-1
    mov dword [rel lang_mode],LANG_AUTO
    ; R73: the icon comes from the executable's own resource (r73_icon.inc);
    ; a resource-less build falls back to the icon file in set_project_icon.
    mov rcx,[rel h_instance]
    mov edx,1
    mov r8d,IMAGE_ICON
    mov r9d,32
    mov qword [rsp+32],32
    mov qword [rsp+40],LR_SHARED
    API LoadImageW
    mov [rbp-16],rax               ; big icon or 0
    mov rcx,[rel h_instance]
    mov edx,1
    mov r8d,IMAGE_ICON
    mov r9d,16
    mov qword [rsp+32],16
    mov qword [rsp+40],LR_SHARED
    API LoadImageW
    mov [rbp-24],rax               ; small icon or 0
    PTR r10,wc_struct
    mov dword [r10],80
    mov dword [r10+4],3          ; CS_HREDRAW | CS_VREDRAW
    PTR r11,wnd_proc
    mov [r10+8],r11
    mov r11,[rel h_instance]
    mov [r10+24],r11
    mov r11,[rbp-16]
    mov [r10+32],r11               ; hIcon
    mov r11,[rbp-8]
    mov [r10+40],r11               ; hCursor
    mov r11,[rel bg_brush]
    mov [r10+48],r11               ; hbrBackground: dark canvas
    PTR r11,app_class_w
    mov [r10+64],r11
    mov r11,[rbp-24]
    mov [r10+72],r11               ; hIconSm
    mov rcx,r10
    ; Unicode class + Unicode message loop: typed Devanagari reaches the
    ; RichEdit as UTF-16 instead of being squeezed through the ANSI code page.
    API RegisterClassExW
    test ax,ax
    jz .end
    call build_menu
    xor ecx,ecx
    PTR rdx,app_class_w
    PTR r8,app_title_w
    mov r9d,WS_OVERLAPPEDWINDOW | WS_VISIBLE
    mov qword [rsp+32],100
    mov qword [rsp+40],50
    mov qword [rsp+48],1180
    mov qword [rsp+56],800
    mov qword [rsp+64],0
    mov rax,[rel h_menu]
    mov [rsp+72],rax
    mov rax,[rel h_instance]
    mov [rsp+80],rax
    mov qword [rsp+88],0
    API CreateWindowExW
    mov [rel h_main],rax
    test rax,rax
    jz .end
    mov rcx,rax
    mov edx,SW_SHOW
    API ShowWindow
    mov rcx,[rel h_main]
    API UpdateWindow
    cmp word [rel current_file],0
    je .fresh
    PTR rcx,current_file
    call load_file
.fresh:
    call set_lang_check
    call update_title
    call update_status
.msg:
    PTR rcx,msg_struct
    xor edx,edx
    xor r8d,r8d
    xor r9d,r9d
    API GetMessageW
    test eax,eax
    jle .end
    call handle_shortcut
    test eax,eax
    jnz .msg
    PTR rcx,msg_struct
    API TranslateMessage
    PTR rcx,msg_struct
    API DispatchMessageW
    jmp .msg
.end:
    EPILOG

; ---- build_menu: an IDLE-style menu bar, stored in h_menu ----------------
; R73: Sanskrit menu bar (patra / sampad / chal / bhasha / sahay), Unicode items.
%macro MENUITEM 2
    mov rcx,[rbp-8]
    mov edx,MF_STRING
    mov r8d,%1
    PTR r9,%2
    API AppendMenuW
%endmacro
%macro MENUSEP 0
    mov rcx,[rbp-8]
    mov edx,MF_SEPARATOR
    xor r8d,r8d
    xor r9d,r9d
    API AppendMenuW
%endmacro
%macro MENUPOPUP 1
    mov rcx,[rel h_menu]
    mov edx,MF_POPUP
    mov r8,[rbp-8]
    PTR r9,%1
    API AppendMenuW
%endmacro
build_menu:
    PROLOG 64
    API CreateMenu
    mov [rel h_menu],rax
    test rax,rax
    jz .bm_done
    ; --- patra ---
    API CreatePopupMenu
    mov [rbp-8],rax
    MENUITEM MID_NEW,mi_nava
    MENUITEM MID_OPEN,mi_khol
    MENUITEM MID_SAVE,mi_sanchay
    MENUITEM MID_SAVEAS,mi_saveas
    MENUSEP
    MENUITEM MID_EXIT,mi_nishkas
    MENUPOPUP mn_patra
    ; --- sampad ---
    API CreatePopupMenu
    mov [rbp-8],rax
    MENUITEM MID_UNDO,mi_punah
    MENUSEP
    MENUITEM MID_CUT,mi_chhid
    MENUITEM MID_COPY,mi_pratilip
    MENUITEM MID_PASTE,mi_sanyoj
    MENUITEM MID_SELALL,mi_sarvagrah
    MENUSEP
    MENUITEM MID_FIND,mi_anwesh
    MENUITEM MID_FINDNEXT,mi_anwesh_agrim
    MENUSEP
    MENUITEM MID_INDENT,mi_antar
    MENUITEM MID_UNINDENT,mi_antar_hatao
    MENUPOPUP mn_sampad
    ; --- chal ---
    API CreatePopupMenu
    mov [rbp-8],rax
    MENUITEM MID_RUN,mi_chal
    MENUITEM MID_SEND,mi_presh
    MENUITEM MID_CLEAR,mi_phal_rikta
    MENUPOPUP mn_chal
    ; --- bhasha (language pack used by chal) ---
    API CreatePopupMenu
    mov [rbp-8],rax
    mov [rel h_menu_bhasha],rax
    MENUITEM MID_LANG_AUTO,mi_swayam
    MENUITEM MID_LANG_CORE,mi_mool
    MENUITEM MID_LANG_SANSKRIT,mi_sanskrit
    MENUITEM 2043,mi_lang_bengali
    MENUITEM 2044,mi_lang_gujarati
    MENUITEM 2045,mi_lang_hindi
    MENUITEM 2046,mi_lang_kannada
    MENUITEM 2047,mi_lang_malayalam
    MENUITEM 2048,mi_lang_marathi
    MENUITEM 2049,mi_lang_odia
    MENUITEM 2050,mi_lang_punjabi
    MENUITEM 2051,mi_lang_tamil
    MENUITEM 2052,mi_lang_telugu
    MENUSEP
    MENUITEM MID_TRANSLIT,mi_translit
    MENUPOPUP mn_bhasha
    ; --- sahay ---
    API CreatePopupMenu
    mov [rbp-8],rax
    MENUITEM MID_KEYS,mi_kunji
    MENUITEM MID_ABOUT,mi_parichay
    MENUPOPUP mn_sahay
.bm_done:
    EPILOG
%unmacro MENUITEM 2
%unmacro MENUSEP 0
%unmacro MENUPOPUP 1

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
    cmp edx,WM_NOTIFY
    je .notify
    cmp edx,WM_CTLCOLORSTATIC
    je .ctlcolor
    cmp edx,WM_CTLCOLOREDIT
    je .ctlcolor
    cmp edx,WM_CTLCOLORLISTBOX
    je .ctlcolor
    cmp edx,WM_CLOSE
    je .close
    cmp edx,WM_DESTROY
    je .destroy
    jmp .def
.notify:
    ; NMHDR: hwndFrom +0, idFrom +8, code +16. Caret moves refresh the status line.
    mov r10,[rbp-32]
    cmp qword [r10+8],ID_EDITOR
    jne .donezero
    cmp dword [r10+16],EN_SELCHANGE
    jne .donezero
    call update_status
    jmp .donezero
.ctlcolor:
    ; wParam = HDC, lParam = child. Dark canvas everywhere; grey gutter digits.
    mov rcx,[rbp-24]
    mov edx,COL_TEXT
    mov rax,[rbp-32]
    cmp rax,[rel h_gutter]
    jne .ctl_status
    mov edx,COL_GUTTER
    jmp .ctl_text
.ctl_status:
    cmp rax,[rel h_status]
    jne .ctl_text
    mov edx,COL_STATUS
.ctl_text:
    call qword [rel __imp_SetTextColor]
    mov rcx,[rbp-24]
    mov edx,COL_BG
    call qword [rel __imp_SetBkColor]
    mov rax,[rel bg_brush]
    jmp .done
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
    movzx ecx,r10w               ; control / menu id
    shr r10,16                   ; notification code
    cmp ecx,200
    jb .action
    cmp ecx,300
    jb .ctl_notify
.action:
    ; R73: a button acts only on BN_CLICKED (0); menus also send 0. A focus
    ; notification (Tab onto a button) must never run or open anything.
    test r10d,r10d
    jnz .donezero
    cmp ecx,MID_RUN
    je .run
    cmp ecx,MID_OPEN
    je .open
    cmp ecx,MID_SAVE
    je .save
    cmp ecx,MID_SAVEAS
    je .saveas
    cmp ecx,MID_NEW
    je .new
    cmp ecx,MID_EXIT
    je .close
    cmp ecx,MID_CLEAR
    je .clear
    cmp ecx,MID_SEND
    je .shell
    cmp ecx,MID_ABOUT
    je .about
    cmp ecx,MID_KEYS
    je .keys
    cmp ecx,MID_UNDO
    je .undo
    cmp ecx,MID_CUT
    je .cut
    cmp ecx,MID_COPY
    je .copy
    cmp ecx,MID_PASTE
    je .paste
    cmp ecx,MID_SELALL
    je .selall
    cmp ecx,MID_FIND
    je .find
    cmp ecx,MID_FINDNEXT
    je .findnext
    cmp ecx,MID_INDENT
    je .indent
    cmp ecx,MID_UNINDENT
    je .unindent
    cmp ecx,MID_LANG_AUTO
    je .lang
    cmp ecx,MID_LANG_CORE
    je .lang
    cmp ecx,MID_LANG_SANSKRIT
    jb .r9_not_lang
    cmp ecx,MID_LANG_LAST
    jbe .lang
.r9_not_lang:
    cmp ecx,MID_TRANSLIT
    je .translit
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
    jmp .donezero
.ctl_notify:
    cmp ecx,ID_EDITOR
    je .edit_changed
    cmp ecx,ID_LIST
    je .list_changed
    jmp .donezero
.about:
    mov rcx,[rel h_main]
    PTR rdx,about_w
    PTR r8,app_title_w
    xor r9d,r9d
    API MessageBoxW
    jmp .donezero
.keys:
    mov rcx,[rel h_main]
    PTR rdx,keys_w
    PTR r8,app_title_w
    xor r9d,r9d
    API MessageBoxW
    jmp .donezero
.run:
    call run_editor
    jmp .donezero
.open:
    call open_dialog
    jmp .donezero
.save:
    call save_current
    jmp .donezero
.saveas:
    call save_dialog
    jmp .donezero
.new:
    call new_file
    jmp .donezero
.example:
    call load_example
    jmp .donezero
.shell:
    call shell_submit
    jmp .donezero
.clear:
    mov byte [rel shell_history],0
    mov dword [rel last_shell_out],0
    mov rcx,[rel h_output]
    PTR rdx,msg_ready
    API SetWindowTextA
    jmp .donezero
.undo:
    mov rcx,[rel h_editor]
    mov edx,EM_UNDO
    xor r8d,r8d
    xor r9d,r9d
    call send_message
    jmp .donezero
.cut:
    mov rcx,[rel h_editor]
    mov edx,WM_CUT
    xor r8d,r8d
    xor r9d,r9d
    call send_message
    jmp .donezero
.copy:
    mov rcx,[rel h_editor]
    mov edx,WM_COPY
    xor r8d,r8d
    xor r9d,r9d
    call send_message
    jmp .donezero
.paste:
    mov rcx,[rel h_editor]
    mov edx,WM_PASTE
    xor r8d,r8d
    xor r9d,r9d
    call send_message
    jmp .donezero
.selall:
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    xor r8d,r8d
    mov r9d,-1
    call send_message
    mov rcx,[rel h_editor]
    API SetFocus
    jmp .donezero
.find:
    call focus_find
    jmp .donezero
.findnext:
    call find_next
    jmp .donezero
.indent:
    call editor_indent
    mov rcx,[rel h_editor]
    API SetFocus
    jmp .donezero
.unindent:
    call editor_unindent
    mov rcx,[rel h_editor]
    API SetFocus
    jmp .donezero
.lang:
    sub ecx,MID_LANG_AUTO
    mov [rel lang_mode],ecx
    call set_lang_check
    call update_status
    jmp .donezero
.translit:
    call r9_toggle_translit
    jmp .donezero
.edit_changed:
    cmp r10d,EN_CHANGE
    jne .donezero
    cmp dword [rel is_highlighting],0
    jne .donezero
    call update_lines
    call highlight_editor
    cmp dword [rel is_loading],0
    jne .donezero
    cmp dword [rel is_modified],0
    jne .edit_status
    mov dword [rel is_modified],1
    call update_title
.edit_status:
    call update_status
.donezero:
    xor eax,eax
    jmp .done
.list_changed:
    cmp r10d,LBN_DBLCLK
    jne .donezero
    call load_example
    jmp .donezero
.close:
    call confirm_discard
    test eax,eax
    jz .donezero
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
    API DefWindowProcW
.done:
    EPILOG


set_project_icon:
    PROLOG 96
    ; R73: resource icon first (same image Explorer and the taskbar show),
    ; then the icon file beside the executable, then the installed assets copy.
    mov rcx,[rel h_instance]
    mov edx,1
    mov r8d,IMAGE_ICON
    xor r9d,r9d
    mov qword [rsp+32],0
    mov qword [rsp+40],LR_DEFAULTSIZE|LR_SHARED
    API LoadImageW
    test rax,rax
    jnz .apply
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
    CHILD class_edit,empty_text,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_MULTILINE|ES_READONLY|ES_AUTOHSCROLL,ID_GUTTER,10,45,50,420,h_gutter
    CHILD class_richedit,example_start,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_MULTILINE|ES_AUTOVSCROLL|ES_WANTRETURN|WS_VSCROLL,ID_EDITOR,62,45,780,420,h_editor
    CHILD class_list,empty_text,WS_CHILD|WS_VISIBLE|WS_BORDER|WS_VSCROLL|LBS_NOTIFY,ID_LIST,848,45,290,420,h_examples
    CHILD class_richedit,msg_ready,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_MULTILINE|ES_AUTOVSCROLL|ES_READONLY|WS_VSCROLL,ID_OUTPUT,10,500,1120,145,h_output
    CHILD class_edit,empty_text,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_AUTOHSCROLL,ID_SHELL,10,659,1120,30,h_shell
    ; R73: find box in the toolbar and a status line along the bottom.
    CHILD class_static,empty_text,WS_CHILD|WS_VISIBLE,ID_FINDLABEL,672,13,62,22,h_find_label
    CHILD class_edit,empty_text,WS_CHILD|WS_VISIBLE|WS_BORDER|ES_AUTOHSCROLL,ID_FIND,736,8,200,27,h_find
    CHILD class_static,empty_text,WS_CHILD|WS_VISIBLE,ID_STATUS,10,700,1120,22,h_status
%unmacro CHILD 9
    mov rcx,[rel h_find_label]
    PTR rdx,find_label_w
    API SetWindowTextW
    ; RichEdit: EN_CHANGE for syntax/line refresh, EN_SELCHANGE for the status line.
    mov rcx,[rel h_editor]
    mov edx,EM_SETEVENTMASK
    xor r8d,r8d
    mov r9d,ENM_CHANGE|ENM_SELCHANGE
    call send_message
    ; Shell Enter key invokes compilation, while default EDIT procedure
    ; continues to handle non-Enter keys normally. Unicode subclassing keeps
    ; typed Devanagari intact (an ANSI subclass would convert WM_CHAR).
    mov rcx,[rel h_shell]
    mov edx,GWLP_WNDPROC
    PTR r8,shell_proc
    API SetWindowLongPtrW
    mov [rel old_shell_proc],rax
    ; Editor keys: Tab / Shift+Tab indent, Enter auto-indents, '}' dedents.
    mov rcx,[rel h_editor]
    mov edx,GWLP_WNDPROC
    PTR r8,editor_proc
    API SetWindowLongPtrW
    mov [rel old_editor_proc],rax
    ; Find box: Enter searches forward from the caret.
    mov rcx,[rel h_find]
    mov edx,GWLP_WNDPROC
    PTR r8,find_proc
    API SetWindowLongPtrW
    mov [rel old_find_proc],rax
    call apply_readable_fonts
    call r9_check_indic_font
    call fill_examples
    call update_lines
    call highlight_editor
    ; R73: the sample program is not an edit; a fresh window starts clean.
    mov dword [rel is_modified],0
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
    sub eax,276                 ; R73: 26 px reserved for the status line
    mov [rbp-16],eax            ; editor height
    mov eax,[rbp-12]
    sub eax,300
    mov [rbp-20],eax            ; editor width (before gutter)
    ; buttons fixed; editor and list resize.
    mov rcx,[rel h_gutter]
    mov edx,8
    mov r8d,42
    mov r9d,45
    mov eax,[rbp-16]
    mov [rsp+32],rax
    mov qword [rsp+40],1
    API MoveWindow
    mov rcx,[rel h_editor]
    mov edx,58
    mov r8d,42
    mov r9d,[rbp-20]
    sub r9d,48
    mov eax,[rbp-16]
    mov [rsp+32],rax
    mov qword [rsp+40],1
    API MoveWindow
    mov rcx,[rel h_examples]
    mov edx,[rbp-20]
    add edx,16
    mov r8d,42
    mov r9d,280
    mov eax,[rbp-16]
    mov [rsp+32],rax
    mov qword [rsp+40],1
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
    ; R73: status line under the shell, full width.
    mov rcx,[rel h_status]
    mov edx,10
    mov eax,[rbp-16]
    add eax,241
    mov r8d,eax
    mov r9d,[rbp-12]
    sub r9d,28
    mov qword [rsp+32],22
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
    mov rax,[rbp-8]               ; R9: pack index = slot in kw_pack_paths
    PTR rdx,kw_pack_paths
    sub rax,rdx
    shr rax,3
    mov [rel r9_cur_pack],eax
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
    mov [rbp-16],rcx            ; R9: first token length (the native word)
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
    ; R9: also keep (pack, roman keyword) -> native word for the typing mode
    mov ecx,[rel native_keyword_count]
    shl rcx,7
    PTR rax,native_keyword_storage
    add rcx,rax
    mov rdx,[rbp-8]
    add rdx,[rbp-16]
    call r9_store_pair
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
    ; WM_GETTEXT expands paragraph breaks to CRLF, while RichEdit character
    ; positions count one CR. Compact the scanner copy to the same units.
    PTR r10,editor_utf16
    mov r11,r10
.compact_lines:
    mov ax,[r10]
    mov [r11],ax
    test ax,ax
    jz .compact_done
    add r10,2
    add r11,2
    cmp ax,13
    jne .compact_lines
    cmp word [r10],10
    jne .compact_lines
    add r10,2
    jmp .compact_lines
.compact_done:
    ; Save selection: don't move user's cursor while recoloring.
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,ch_start
    PTR r9,ch_end
    call send_message
    mov dword [rel char_fmt],60
    mov dword [rel char_fmt+4],CFM_COLOR
    mov dword [rel char_fmt+8],0
    mov dword [rel char_fmt+20],COL_TEXT
    ; dark canvas for the whole editor, matching the approved design
    mov rcx,[rel h_editor]
    mov edx,EM_SETBKGNDCOLOR
    xor r8d,r8d
    mov r9d,COL_BG
    call send_message
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
    cmp dx,0x0964
    je .danda
    cmp dx,0x0965
    je .danda
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
    mov al,dl
    cmp al,'0'
    jb .kw_begin
    cmp al,'9'
    ja .kw_begin
    mov eax,[rbp-24]
    mov [rbp-56],eax              ; number start index
.num_loop:
    mov r10,[rbp-16]
    mov ax,[r10]
    cmp ax,'0'
    jb .num_dot
    cmp ax,'9'
    jbe .num_adv
.num_dot:
    cmp ax,'.'
    jne .num_hex
    ; only one '.' allowed in a decimal literal
    mov r11,[rbp-56]
    mov ecx,[rbp-24]
    sub ecx,r11d
    mov r10,[rbp-16]
.num_dot_scan:
    test ecx,ecx
    jz .num_adv
    mov ax,[r10]
    cmp ax,'.'
    je .num_end
    add r10,2
    dec ecx
    jmp .num_dot_scan
.num_hex:
    ; allow hex digits a-f only when the literal starts 0x / 0X
    mov r11,[rbp-16]
    mov ax,[r11]
    cmp ax,'x'
    je .num_adv
    cmp ax,'X'
    je .num_adv
    cmp ax,'a'
    jb .num_end
    cmp ax,'f'
    jbe .num_adv
    cmp ax,'A'
    jb .num_end
    cmp ax,'F'
    jbe .num_adv
    jmp .num_end
.num_adv:
    add qword [rbp-16],2
    inc dword [rbp-24]
    jmp .num_loop
.num_end:
    mov r8d,[rbp-56]
    mov r9d,[rbp-24]
    sub r9d,r8d
    test r9d,r9d
    jz .advance
    mov r10d,COL_NUMBER
    call paint_range
    jmp .advance
.kw_begin:
    ; builtin?  (teal)
    PTR r11,bi_words
    mov [rbp-64],r11
.bi_loop:
    mov r11,[rbp-64]
    cmp byte [r11],0
    je .kw_begin2
    mov [rbp-40],r11
    mov r10,[rbp-16]
    xor ecx,ecx
.bi_cmp:
    mov r11,[rbp-40]
    movzx eax,byte [r11+rcx]
    test eax,eax
    jz .bi_found
    cmp ax,[r10+rcx*2]
    jne .bi_next
    inc ecx
    cmp ecx,32
    jl .bi_cmp
    jmp .bi_next
.bi_found:
    mov ax,[r10+rcx*2]
    call is_ident_u16
    test eax,eax
    jnz .bi_next
    mov [rbp-44],ecx
    mov r10d,COL_BUILTIN
    jmp .paint_tok
.bi_next:
    mov r11,[rbp-64]
.bi_skip:
    cmp byte [r11],0
    je .bi_nk
    inc r11
    jmp .bi_skip
.bi_nk:
    inc r11
    mov [rbp-64],r11
    jmp .bi_loop
.kw_begin2:
    PTR r11,kw_words
    mov [rbp-32],r11
.kw_loop:
    mov r11,[rbp-32]
    cmp byte [r11],0
    je .function_word
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
    mov r10d,COL_KEYWORD
    jmp .paint_tok
.danda:
    mov dword [rbp-44],1
    mov r10d,0x00E6D45C
    jmp .paint_tok
.function_word:
    mov r11,[rbp-16]
    xor ecx,ecx
.function_scan:
    mov ax,[r11+rcx*2]
    call is_ident_u16
    test eax,eax
    jz .function_end
    inc ecx
    jmp .function_scan
.function_end:
    mov [rbp-44],ecx
.function_space:
    mov ax,[r11+rcx*2]
    cmp ax,' '
    je .function_next
    cmp ax,9
    jne .function_check
.function_next:
    inc ecx
    jmp .function_space
.function_check:
    cmp ax,'('
    jne .advance
    mov r10d,COL_FUNCTION
    jmp .paint_tok
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
    mov r10d,COL_KEYWORD
.paint_tok:
    ; index is measured in UTF-16 code units, including surrogate pairs.
    mov [rbp-72],r10d
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,[rbp-24]
    mov r9d,r8d
    add r9d,[rbp-44]
    call send_message
    mov eax,[rbp-72]
    mov dword [rel char_fmt+20],eax
    mov rcx,[rel h_editor]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_SELECTION
    PTR r9,char_fmt
    call send_message
    mov dword [rel char_fmt+20],COL_TEXT
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
    mov eax,[rbp-24]
    mov [rbp-56],eax              ; string start index
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
    mov r8d,[rbp-56]
    mov r9d,[rbp-24]
    inc r9d                       ; include closing quote
    sub r9d,r8d
    mov r10d,COL_STRING
    call paint_range
    jmp .advance
.comment:
    mov eax,[rbp-24]
    mov [rbp-56],eax              ; comment start index
.comment_loop:
    mov r10,[rbp-16]
    cmp word [r10],10
    je .comment_end
    cmp word [r10],13
    je .comment_end
    cmp word [r10],0
    je .comment_end
    add qword [rbp-16],2
    inc dword [rbp-24]
    jmp .comment_loop
.comment_end:
    mov r8d,[rbp-56]
    mov r9d,[rbp-24]
    sub r9d,r8d
    test r9d,r9d
    jz .advance
    mov r10d,COL_COMMENT
    call paint_range
    jmp .advance
.advance:
    add qword [rbp-16],2
    inc dword [rbp-24]
    jmp .scan
.restore:
    mov rcx,[rel h_editor]       ; R9 (WS5): Indic runs in Nirmala UI
    PTR rdx,editor_utf16
    call r9_apply_script_faces
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,[rel ch_start]
    mov r9d,[rel ch_end]
    call send_message
    mov dword [rel is_highlighting],0
.done:
    EPILOG

; paint_range: colour editor chars [r8d, r8d+r9d). r10d = COLORREF.
paint_range:
    PROLOG 64
    mov [rbp-8],r8d
    mov [rbp-12],r9d
    mov [rbp-16],r10d
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,[rbp-8]
    mov r9d,r8d
    add r9d,[rbp-12]
    call send_message
    mov eax,[rbp-16]
    mov dword [rel char_fmt+20],eax
    mov rcx,[rel h_editor]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_SELECTION
    PTR r9,char_fmt
    call send_message
    mov dword [rel char_fmt+20],COL_TEXT
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
    call confirm_discard         ; R73: never drop unsaved work silently
    test eax,eax
    jz .end
    call dialog_common
    PTR rcx,ofn_struct
    API GetOpenFileNameW
    test eax,eax
    jz .end
    PTR rcx,current_file
    call load_file
.end:
    EPILOG
; eax = 1 when the patra was written, 0 when cancelled or failed
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
; sanchay: write to the current patra, or ask for a name when there is none
save_current:
    PROLOG 48
    cmp word [rel current_file],0
    je .ask
    PTR rcx,current_file
    call save_file
    jmp .done
.ask:
    call save_dialog
.done:
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
    mov dword [rel is_loading],1
    PTR rcx,file_buffer
    call editor_set_utf8
    mov dword [rel is_loading],0
    test eax,eax
    jz .fail
    ; R73: a freshly loaded patra is clean; the title and status say so.
    mov dword [rel is_modified],0
    call update_title
    call update_status
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
    test eax,eax
    jz .done
    ; R73: saved -> clean
    mov dword [rel is_modified],0
    call update_title
    call update_status
    mov eax,1
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
    call r9_output_restyle
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
    PTR rdx,quote_only_w
    call wide_command_concat
    ; R73: "<compiler>" [ --lang <pack>] "<source>" "<binary>"
    cmp dword [rel use_pack],0
    je .no_pack
    PTR rcx,command_line
    PTR rdx,lang_flag_prefix_w
    call wide_command_concat
    mov eax,[rel use_pack]
    dec eax
    PTR rdx,r9_pack_names
    mov rdx,[rdx+rax*8]
    PTR rcx,command_line
    call wide_command_concat
.no_pack:
    PTR rcx,command_line
    PTR rdx,space_quote_w
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

; R4: rcx = the message for the stage compile_run last failed in.
; Before R4 the editor said "program ended abnormally" for a compile error and
; the shell said "compile failed" for a runtime error.
stage_fail_message:
    PTR rcx,msg_run_failed
    cmp dword [rel last_fail_stage],1
    jne .not_compile
    PTR rcx,msg_compile_failed
.not_compile:
    cmp dword [rel last_fail_stage],3
    jne .done
    PTR rcx,msg_file_failed
.done:
    ret

; Compiler+run; rcx -> Sutram source; output_buffer captures only the
; *last* subprocess (compiler error OR program stdout/stderr).
compile_run:
    PROLOG 80
    mov [rbp-8],rcx
    mov dword [rel last_fail_stage],3
    call write_temp
    test eax,eax
    jz .failed
    mov dword [rel last_fail_stage],1    ; R4: a failure from here on is the compiler's
    call compose_compile
    PTR rcx,command_line
    call spawn_capture
    test eax,eax
    jz .failed
    mov dword [rel last_fail_stage],2    ; R4: ... and from here on the program's
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
    ; R73: choose the language pack for this run (bhasha menu / Devanagari detection)
    PTR rcx,editor_utf16
    call detect_devanagari
    mov ecx,eax
    call select_pack
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
    call r9_output_restyle       ; R9: readable colour, Indic face
    cmp dword [rbp-4],0
    jne .end
    call stage_fail_message      ; R4: rcx = compile / run / file message
    call output_append
    jmp .end
.failed_unicode:
    PTR rcx,msg_file_failed
    call output_append
.end:
    call update_status           ; R73: shows which pack this run used
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
    API CallWindowProcW
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
    ; R73: the replayed source may hold Devanagari from earlier lines too
    PTR rcx,file_buffer
    call detect_devanagari_utf8
    mov ecx,eax
    call select_pack
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
    call stage_fail_message      ; R4: was always "sankalan asaphal", even for a runtime failure
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

extern __imp_LoadLibraryA, __imp_GetProcAddress

extern __imp_GetCommandLineW, __imp_CommandLineToArgvW, __imp_LocalFree
extern __imp_GetFullPathNameW, __imp_GetKeyState
section .data
delivery_about_text: db 'Sutram Native IDE',13,10,'F5 / Ctrl+R: Run   Ctrl+O: Open   Ctrl+S: Save',13,10,'Files are UTF-8. Shell submissions replay session history.',0
section .text
read_startup_file:
    PROLOG 80
    call qword [rel __imp_GetCommandLineW]
    mov rcx,rax
    lea rdx,[rbp-16]
    call qword [rel __imp_CommandLineToArgvW]
    test rax,rax
    jz .done
    mov [rbp-8],rax
    cmp dword [rbp-16],2
    jne .free
    mov rcx,[rax+8]
    mov edx,520
    PTR r8,current_file
    xor r9d,r9d
    call qword [rel __imp_GetFullPathNameW]
    test eax,eax
    jz .invalid
    cmp eax,520
    jb .free
.invalid:
    mov word [rel current_file],0
.free:
    mov rcx,[rbp-8]
    call qword [rel __imp_LocalFree]
.done:
    EPILOG
handle_shortcut:
    PROLOG 48
    cmp dword [rel msg_struct+8],WM_KEYDOWN
    jne .no
    cmp dword [rel msg_struct+16],0x74
    je .run
    cmp dword [rel msg_struct+16],VK_F3
    je .findnext
    mov ecx,0x11
    call qword [rel __imp_GetKeyState]
    test ax,0x8000
    jz .no
    mov eax,[rel msg_struct+16]
    cmp eax,'R'
    je .run
    cmp eax,'O'
    je .open
    cmp eax,'S'
    je .save
    cmp eax,'N'
    je .new
    cmp eax,'F'
    je .find
    cmp eax,'T'
    je .translit
.no:
    xor eax,eax
    EPILOG
.run:
    call run_editor
    jmp .yes
.open:
    call open_dialog
    jmp .yes
.save:
    call save_current
    jmp .yes
.new:
    call new_file
    jmp .yes
.find:
    call focus_find
    jmp .yes
.findnext:
    call find_next
    jmp .yes
.translit:
    call r9_toggle_translit
.yes:
    mov eax,1
    EPILOG

; ============================================================================
; R73 — editor keys, status line, title, find, language pack, new patra.
; Every routine keeps the Win64 ABI: 16-byte aligned frames, 32-byte shadow.
; ============================================================================
extern __imp_CreateSolidBrush, __imp_SetTextColor, __imp_SetBkColor
section .text

; --- editor subclass: Tab / Shift+Tab, Enter auto-indent, '}' dedent ----------
editor_proc:
    PROLOG 96
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    mov [rbp-24],r8
    mov [rbp-32],r9
    cmp edx,WM_KEYDOWN
    je .keydown
    cmp edx,WM_CHAR
    je .char
    jmp .def
.keydown:
    cmp r8d,VK_TAB
    je .tab
    cmp r8d,VK_RETURN
    je .enter
    jmp .def
.tab:
    call r9_tl_convert           ; R9: a word ends at Tab too
    mov ecx,VK_SHIFT
    call qword [rel __imp_GetKeyState]
    test ax,0x8000
    jnz .unindent
    call editor_indent
    jmp .eat
.unindent:
    call editor_unindent
    jmp .eat
.enter:
    call r9_tl_convert           ; R9: and at Enter
    call editor_newline
    jmp .eat
.char:
    cmp r8d,9
    je .eat                      ; already handled on WM_KEYDOWN
    ; R9 (WS6): in the typing mode, a printable character that cannot be part of
    ; a Latin word (space, punctuation) ends the word before the caret: convert it
    ; first, then let the character through.
    cmp dword [rel r9_tl_on],0
    je .r9_char_done
    cmp r8d,32
    jb .r9_char_done
    cmp r8d,127
    jae .r9_char_done
    mov eax,r8d
    call r9_is_word_char
    test eax,eax
    jnz .r9_char_done
    call r9_tl_convert
    mov r8,[rbp-24]
.r9_char_done:
    cmp r8d,13
    je .eat
    cmp r8d,10
    je .eat
    cmp r8d,'}'
    jne .def
    call editor_close_brace
    test eax,eax
    jnz .eat
    jmp .def
.eat:
    xor eax,eax
    jmp .done
.def:
    mov rcx,[rel old_editor_proc]
    mov rdx,[rbp-8]
    mov r8,[rbp-16]
    mov r9,[rbp-24]
    mov rax,[rbp-32]
    mov [rsp+32],rax
    API CallWindowProcW
.done:
    EPILOG

; --- find box subclass: Enter = agrim anwesh ---------------------------------
find_proc:
    PROLOG 96
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    mov [rbp-24],r8
    mov [rbp-32],r9
    cmp edx,WM_KEYDOWN
    je .key
    cmp edx,WM_CHAR
    jne .def
    cmp r8d,13
    je .eat
    jmp .def
.key:
    cmp r8d,VK_RETURN
    jne .def
    call find_next
.eat:
    xor eax,eax
    jmp .done
.def:
    mov rcx,[rel old_find_proc]
    mov rdx,[rbp-8]
    mov r8,[rbp-16]
    mov r9,[rbp-24]
    mov rax,[rbp-32]
    mov [rsp+32],rax
    API CallWindowProcW
.done:
    EPILOG

; --- selection -> [rbp-4] first line, [rbp-8] last line (caller frame) --------
; Shared helper: fills ch_start/ch_end and returns eax=first line, edx=last line.
; If the selection ends at column 0 of the last line, that line is excluded.
selection_lines:
    PROLOG 64
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,ch_start
    PTR r9,ch_end
    call send_message
    mov rcx,[rel h_editor]
    mov edx,EM_LINEFROMCHAR
    mov r8d,[rel ch_start]
    xor r9d,r9d
    call send_message
    mov [rbp-4],eax
    mov rcx,[rel h_editor]
    mov edx,EM_LINEFROMCHAR
    mov r8d,[rel ch_end]
    xor r9d,r9d
    call send_message
    mov [rbp-8],eax
    cmp eax,[rbp-4]
    je .ret
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,[rbp-8]
    xor r9d,r9d
    call send_message
    cmp eax,[rel ch_end]
    jne .ret
    dec dword [rbp-8]
.ret:
    mov eax,[rbp-4]
    mov edx,[rbp-8]
    EPILOG

; Tab: four spaces at the caret, or in front of every selected line.
editor_indent:
    PROLOG 64
    call selection_lines
    mov [rbp-4],eax
    mov [rbp-8],edx
    mov ecx,[rel ch_end]
    mov [rbp-20],ecx             ; private copy: each insert re-highlights and reuses ch_*
    cmp ecx,[rel ch_start]
    je .single
    cmp eax,edx
    je .single
    mov [rbp-12],edx
.loop:
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,[rbp-12]
    xor r9d,r9d
    call send_message
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,eax
    mov r9d,eax
    call send_message
    mov rcx,[rel h_editor]
    mov edx,EM_REPLACESEL
    mov r8d,1
    PTR r9,indent4_w
    API SendMessageW
    dec dword [rbp-12]
    mov eax,[rbp-12]
    cmp eax,[rbp-4]
    jge .loop
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,[rbp-4]
    xor r9d,r9d
    call send_message
    mov [rbp-16],eax
    mov eax,[rbp-8]
    sub eax,[rbp-4]
    inc eax
    shl eax,2
    add eax,[rbp-20]
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,[rbp-16]
    mov r9d,eax
    call send_message
    jmp .done
.single:
    mov rcx,[rel h_editor]
    mov edx,EM_REPLACESEL
    mov r8d,1
    PTR r9,indent4_w
    API SendMessageW
.done:
    EPILOG

; Shift+Tab: remove up to four leading spaces from each selected line.
editor_unindent:
    PROLOG 80
    call selection_lines
    mov [rbp-4],eax
    mov [rbp-8],edx
    mov eax,[rel ch_start]
    mov [rbp-20],eax
    mov eax,[rel ch_end]
    mov [rbp-24],eax
    mov dword [rbp-28],0         ; spaces removed in total
    mov eax,[rbp-8]
    mov [rbp-12],eax
.loop:
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,[rbp-12]
    xor r9d,r9d
    call send_message
    mov [rbp-16],eax             ; line start
    PTR r10,line_utf16
    mov word [r10],8
    mov rcx,[rel h_editor]
    mov edx,EM_GETLINE
    mov r8d,[rbp-12]
    PTR r9,line_utf16
    API SendMessageW
    xor ecx,ecx
.count:
    cmp ecx,eax
    jae .counted
    cmp ecx,4
    jae .counted
    PTR r10,line_utf16
    cmp word [r10+rcx*2],' '
    jne .counted
    inc ecx
    jmp .count
.counted:
    test ecx,ecx
    jz .next
    mov [rbp-32],ecx
    mov r8d,[rbp-16]
    mov r9d,r8d
    add r9d,ecx
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    call send_message
    mov rcx,[rel h_editor]
    mov edx,EM_REPLACESEL
    mov r8d,1
    PTR r9,empty_w
    API SendMessageW
    mov eax,[rbp-32]
    add [rbp-28],eax
.next:
    dec dword [rbp-12]
    mov eax,[rbp-12]
    cmp eax,[rbp-4]
    jge .loop
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,[rbp-4]
    xor r9d,r9d
    call send_message
    mov [rbp-16],eax             ; first line start
    mov eax,[rbp-20]
    cmp eax,[rbp-24]
    jne .block
    sub eax,[rbp-28]
    cmp eax,[rbp-16]
    jge .caret
    mov eax,[rbp-16]
.caret:
    mov r8d,eax
    mov r9d,eax
    jmp .setsel
.block:
    mov r8d,[rbp-16]
    mov eax,[rbp-24]
    sub eax,[rbp-28]
    mov r9d,eax
.setsel:
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    call send_message
    EPILOG

; Enter: new line with the current line's indentation, +4 after a '{'.
editor_newline:
    PROLOG 96
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,ch_start
    PTR r9,ch_end
    call send_message
    mov rcx,[rel h_editor]
    mov edx,EM_LINEFROMCHAR
    mov r8d,[rel ch_start]
    xor r9d,r9d
    call send_message
    mov [rbp-4],eax
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,eax
    xor r9d,r9d
    call send_message
    mov [rbp-8],eax
    PTR r10,line_utf16
    mov word [r10],4000
    mov rcx,[rel h_editor]
    mov edx,EM_GETLINE
    mov r8d,[rbp-4]
    PTR r9,line_utf16
    API SendMessageW
    mov ecx,[rel ch_start]
    sub ecx,[rbp-8]
    cmp ecx,eax
    jbe .lim
    mov ecx,eax
.lim:
    mov [rbp-16],ecx             ; code units before the caret
    xor ecx,ecx
.lead:
    cmp ecx,[rbp-16]
    jae .leaded
    PTR r10,line_utf16
    cmp word [r10+rcx*2],' '
    jne .leaded
    inc ecx
    jmp .lead
.leaded:
    cmp ecx,120
    jbe .ok
    mov ecx,120
.ok:
    mov [rbp-20],ecx             ; indentation to copy
    mov ecx,[rbp-16]
.back:
    test ecx,ecx
    jz .compose
    dec ecx
    PTR r10,line_utf16
    movzx eax,word [r10+rcx*2]
    cmp ax,' '
    je .back
    cmp ax,9
    je .back
    cmp ax,'{'
    jne .compose
    add dword [rbp-20],4
.compose:
    PTR r10,indent_buf
    mov word [r10],13
    add r10,2
    mov ecx,[rbp-20]
.fill:
    test ecx,ecx
    jz .term
    mov word [r10],' '
    add r10,2
    dec ecx
    jmp .fill
.term:
    mov word [r10],0
    mov rcx,[rel h_editor]
    mov edx,EM_REPLACESEL
    mov r8d,1
    PTR r9,indent_buf
    API SendMessageW
    EPILOG

; '}' typed on a whitespace-only line: pull it back by four. eax=1 if handled.
editor_close_brace:
    PROLOG 80
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,ch_start
    PTR r9,ch_end
    call send_message
    mov eax,[rel ch_start]
    cmp eax,[rel ch_end]
    jne .no
    mov rcx,[rel h_editor]
    mov edx,EM_LINEFROMCHAR
    mov r8d,[rel ch_start]
    xor r9d,r9d
    call send_message
    mov [rbp-4],eax
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,eax
    xor r9d,r9d
    call send_message
    mov [rbp-8],eax
    mov ecx,[rel ch_start]
    sub ecx,eax
    cmp ecx,4
    jb .no
    mov [rbp-12],ecx
    PTR r10,line_utf16
    mov word [r10],4000
    mov rcx,[rel h_editor]
    mov edx,EM_GETLINE
    mov r8d,[rbp-4]
    PTR r9,line_utf16
    API SendMessageW
    cmp eax,[rbp-12]
    jb .no
    xor ecx,ecx
.scan:
    cmp ecx,[rbp-12]
    jae .dedent
    PTR r10,line_utf16
    cmp word [r10+rcx*2],' '
    jne .no
    inc ecx
    jmp .scan
.dedent:
    mov r8d,[rel ch_start]
    sub r8d,4
    mov r9d,[rel ch_start]
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    call send_message
    PTR r10,indent_buf
    mov word [r10],'}'
    mov word [r10+2],0
    mov rcx,[rel h_editor]
    mov edx,EM_REPLACESEL
    mov r8d,1
    PTR r9,indent_buf
    API SendMessageW
    mov eax,1
    jmp .done
.no:
    xor eax,eax
.done:
    EPILOG

; --- title: "<patra>[ *] - Sutram sampadak" --------------------------------
wide_basename:
    mov rax,rcx
    mov r10,rcx
.scan:
    movzx edx,word [r10]
    test dx,dx
    jz .done
    add r10,2
    cmp dx,'\'
    je .mark
    cmp dx,'/'
    jne .scan
.mark:
    mov rax,r10
    jmp .scan
.done:
    ret

update_title:
    PROLOG 48
    cmp word [rel current_file],0
    je .fresh
    PTR rcx,current_file
    call wide_basename
    mov rcx,rax
    PTR rdx,title_utf16
    call wide_string_copy
    jmp .mod
.fresh:
    PTR rcx,title_new_w
    PTR rdx,title_utf16
    call wide_string_copy
.mod:
    cmp dword [rel is_modified],0
    je .suffix
    PTR rcx,title_utf16
    PTR rdx,title_mod_w
    call wide_string_concat
.suffix:
    PTR rcx,title_utf16
    PTR rdx,title_suffix_w
    call wide_string_concat
    mov rcx,[rel h_main]
    test rcx,rcx
    jz .done
    PTR rdx,title_utf16
    API SetWindowTextW
.done:
    EPILOG

; --- status line: pankti / stambh / bhasha / akshara / sanchit ---------------
; rcx = unsigned value, rdx = UTF-16 destination; returns rax -> terminating NUL
utoa16:
    mov r9,rdx
    mov eax,ecx
    PTR r8,num_scratch+46
    mov word [r8],0
    mov r11d,10
.digit:
    xor edx,edx
    div r11d
    add dl,'0'
    sub r8,2
    mov [r8],dx
    test eax,eax
    jnz .digit
.copy:
    mov ax,[r8]
    mov [r9],ax
    test ax,ax
    jz .done
    add r8,2
    add r9,2
    jmp .copy
.done:
    mov rax,r9
    ret

; rcx = value, rdx = UTF-16 buffer: append the decimal digits
wide_append_num:
    push rbx
    sub rsp,16
    mov rbx,rdx
    mov r8,rcx
    mov rcx,rbx
    call wide_string_length
    lea rdx,[rbx+rax*2]
    mov rcx,r8
    call utoa16
    add rsp,16
    pop rbx
    ret

lang_mode_name:
    mov eax,[rel lang_mode]
    cmp eax,LANG_CORE
    je .core
    cmp eax,LANG_SANSKRIT
    je .sanskrit
    ja .r9_pack
    cmp dword [rel last_pack],0
    jne .auto_sk
    PTR rax,lang_swayam_w
    ret
.auto_sk:
    PTR rax,lang_swayam_sk_w
    ret
.core:
    PTR rax,lang_mool_w
    ret
.sanskrit:
    PTR rax,lang_sanskrit_w
    ret
.r9_pack:
    sub eax,2
    PTR rdx,r9_pack_names
    mov rax,[rdx+rax*8]
    ret

update_status:
    PROLOG 64
    cmp qword [rel h_status],0
    je .done
    cmp qword [rel h_editor],0
    je .done
    ; The highlighter moves the selection once per token; those are not caret
    ; moves, and ch_start/ch_end belong to it while it runs. Private copies here.
    cmp dword [rel is_highlighting],0
    jne .done
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,sel_pos
    PTR r9,sel_pos+4
    call send_message
    mov rcx,[rel h_editor]
    mov edx,EM_LINEFROMCHAR
    mov r8d,[rel sel_pos]
    xor r9d,r9d
    call send_message
    mov [rbp-4],eax
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,eax
    xor r9d,r9d
    call send_message
    mov ecx,[rel sel_pos]
    sub ecx,eax
    inc ecx
    mov [rbp-8],ecx
    PTR rcx,st_pankti_w
    PTR rdx,status_utf16
    call wide_string_copy
    mov ecx,[rbp-4]
    inc ecx
    PTR rdx,status_utf16
    call wide_append_num
    PTR rcx,status_utf16
    PTR rdx,st_stambh_w
    call wide_string_concat
    mov ecx,[rbp-8]
    PTR rdx,status_utf16
    call wide_append_num
    PTR rcx,status_utf16
    PTR rdx,st_bhasha_w
    call wide_string_concat
    call lang_mode_name
    PTR rcx,status_utf16
    mov rdx,rax
    call wide_string_concat
    ; R9: "lipi: <pack>" while the typing mode is on
    cmp dword [rel r9_tl_on],0
    je .no_lipi
    PTR rcx,status_utf16
    PTR rdx,st_lipi_w
    call wide_string_concat
    call r9_tl_pack
    PTR rdx,r9_pack_names
    mov rdx,[rdx+rax*8]
    PTR rcx,status_utf16
    call wide_string_concat
.no_lipi:
    cmp dword [rel cluster_count],-1
    je .state
    PTR rcx,status_utf16
    PTR rdx,st_akshara_w
    call wide_string_concat
    mov ecx,[rel cluster_count]
    PTR rdx,status_utf16
    call wide_append_num
.state:
    PTR rcx,status_utf16
    PTR rdx,st_sep_w
    call wide_string_concat
    cmp dword [rel is_modified],0
    je .clean
    PTR rdx,st_asanchit_w
    jmp .write
.clean:
    PTR rdx,st_sanchit_w
.write:
    PTR rcx,status_utf16
    call wide_string_concat
    mov rcx,[rel h_status]
    PTR rdx,status_utf16
    API SetWindowTextW
.done:
    EPILOG

; --- anwesh: find forward from the caret, wrapping once ---------------------
focus_find:
    PROLOG 48
    mov rcx,[rel h_find]
    mov edx,EM_SETSEL
    xor r8d,r8d
    mov r9d,-1
    call send_message
    mov rcx,[rel h_find]
    API SetFocus
    EPILOG

find_next:
    PROLOG 96
    mov rcx,[rel h_find]
    PTR rdx,find_utf16
    mov r8d,512
    API GetWindowTextW
    test eax,eax
    jz .done
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,ch_start
    PTR r9,ch_end
    call send_message
    PTR r10,findtext
    mov eax,[rel ch_end]
    mov [r10],eax                ; chrg.cpMin
    mov dword [r10+4],-1         ; chrg.cpMax
    PTR rax,find_utf16
    mov [r10+8],rax              ; lpstrText
    mov rcx,[rel h_editor]
    mov edx,EM_FINDTEXTEXW
    mov r8d,FR_DOWN
    mov r9,r10
    API SendMessageW
    cmp eax,-1
    jne .found
    PTR r10,findtext
    mov dword [r10],0
    mov dword [r10+4],-1
    mov rcx,[rel h_editor]
    mov edx,EM_FINDTEXTEXW
    mov r8d,FR_DOWN
    mov r9,r10
    API SendMessageW
    cmp eax,-1
    je .notfound
.found:
    PTR r10,findtext
    lea r9,[r10+16]              ; chrgText
    mov rcx,[rel h_editor]
    mov edx,EM_EXSETSEL
    xor r8d,r8d
    API SendMessageW
    mov rcx,[rel h_editor]
    API SetFocus
    jmp .done
.notfound:
    mov rcx,[rel h_status]
    PTR rdx,st_notfound_w
    API SetWindowTextW
.done:
    EPILOG

; --- language pack selection ------------------------------------------------
; rcx = UTF-16 text; eax=1 when any Devanagari code unit (U+0900..U+097F) occurs
detect_devanagari:
    xor eax,eax
.scan:
    movzx edx,word [rcx]
    test dx,dx
    jz .done
    add rcx,2
    cmp dx,0x0900
    jb .scan
    cmp dx,0x097F
    ja .scan
    mov eax,1
.done:
    ret

; rcx = UTF-8 text; eax=1 when a Devanagari sequence (E0 A4..A5 xx) occurs
detect_devanagari_utf8:
    xor eax,eax
.scan:
    movzx edx,byte [rcx]
    test dl,dl
    jz .done
    inc rcx
    cmp dl,0xE0
    jne .scan
    movzx edx,byte [rcx]
    cmp dl,0xA4
    je .yes
    cmp dl,0xA5
    jne .scan
.yes:
    mov eax,1
.done:
    ret

; ecx = detection result; applies the bhasha menu choice to use_pack
select_pack:
    mov eax,[rel lang_mode]
    cmp eax,LANG_CORE
    je .none
    cmp eax,LANG_SANSKRIT
    je .sanskrit
    ja .r9_pack                  ; R9: one of the other ten packs

    mov [rel use_pack],ecx
    mov [rel last_pack],ecx
    ret
.none:
    mov dword [rel use_pack],0
    ret
.sanskrit:
    mov dword [rel use_pack],1
    ret
.r9_pack:
    dec eax                      ; use_pack = pack index + 1
    mov [rel use_pack],eax
    ret

set_lang_check:
    PROLOG 48
    mov rcx,[rel h_menu_bhasha]
    test rcx,rcx
    jz .done
    mov edx,MID_LANG_AUTO
    mov r8d,MID_LANG_LAST
    mov r9d,[rel lang_mode]
    add r9d,MID_LANG_AUTO
    mov qword [rsp+32],MF_BYCOMMAND
    API CheckMenuRadioItem
    ; R9: the typing-mode tick
    mov rcx,[rel h_menu_bhasha]
    mov edx,MID_TRANSLIT
    xor r8d,r8d
    cmp dword [rel r9_tl_on],0
    je .tl_off
    mov r8d,MF_CHECKED
.tl_off:
    call qword [rel __imp_CheckMenuItem]
.done:
    EPILOG

; --- unsaved work guard and nava patra -------------------------------------
; eax=1: proceed (clean, saved on request, or discarded); eax=0: cancelled
confirm_discard:
    PROLOG 48
    cmp dword [rel is_modified],0
    je .yes
    mov rcx,[rel h_main]
    PTR rdx,msg_unsaved_w
    PTR r8,app_title_w
    mov r9d,MB_YESNOCANCEL|MB_ICONQUESTION
    API MessageBoxW
    cmp eax,IDYES
    je .save
    cmp eax,IDNO
    je .yes
    xor eax,eax
    jmp .done
.save:
    call save_current
    test eax,eax
    jz .done
.yes:
    mov eax,1
.done:
    EPILOG

new_file:
    PROLOG 48
    call confirm_discard
    test eax,eax
    jz .done
    mov dword [rel is_loading],1
    mov rcx,[rel h_editor]
    PTR rdx,empty_w
    API SetWindowTextW
    mov dword [rel is_loading],0
    mov word [rel current_file],0
    mov dword [rel is_modified],0
    call update_title
    call update_status
    mov rcx,[rel h_editor]
    API SetFocus
.done:
    EPILOG

extern __imp_CreateFontW
section .data
font_code: dw 'C','o','n','s','o','l','a','s',0
font_ui: dw 'S','e','g','o','e',' ','U','I',0
; R9 (WS5): Consolas has no Indic glyphs. Runs of Indic text in the editor and
; the output are given this face (it ships with Windows 10/11 and covers all
; eleven scripts); Latin stays Consolas, so code still lines up.
font_indic: dw 'N','i','r','m','a','l','a',' ','U','I',0
ui_font_controls: dq h_btn_run,h_btn_open,h_btn_save,h_btn_example,h_btn_send,h_btn_clear,h_find_label,h_status,0
code_font_controls: dq h_editor,h_gutter,h_output,h_shell,h_examples,h_find,0
section .text
make_readable_font:
    PROLOG 128
    mov [rbp-8],rdx
    xor edx,edx
    xor r8d,r8d
    xor r9d,r9d
    mov qword [rsp+32],400
    mov qword [rsp+40],0
    mov qword [rsp+48],0
    mov qword [rsp+56],0
    mov qword [rsp+64],1
    mov qword [rsp+72],0
    mov qword [rsp+80],0
    mov qword [rsp+88],5
    mov qword [rsp+96],0
    mov rax,[rbp-8]
    mov [rsp+104],rax
    call qword [rel __imp_CreateFontW]
    EPILOG
apply_readable_fonts:
    PROLOG 96
    mov ecx,-18
    PTR rdx,font_code
    call make_readable_font
    mov [rbp-8],rax
    PTR rax,code_font_controls
    mov [rbp-16],rax
    call .apply
    mov ecx,-16
    PTR rdx,font_ui
    call make_readable_font
    mov [rbp-8],rax
    PTR rax,ui_font_controls
    mov [rbp-16],rax
    call .apply
    mov rcx,[rel h_output]
    mov edx,EM_SETBKGNDCOLOR
    xor r8d,r8d
    mov r9d,COL_BG
    API SendMessageW
    mov dword [rel char_fmt],60
    mov dword [rel char_fmt+4],CFM_COLOR
    mov dword [rel char_fmt+20],0x00B5D8A8
    mov rcx,[rel h_output]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_ALL
    PTR r9,char_fmt
    API SendMessageW
    EPILOG
.apply:
    ; This helper shares the caller frame; adjust shadow space for nested call.
    sub rsp,40
.next:
    mov r10,[rbp-16]
    mov r10,[r10]
    test r10,r10
    jz .done
    mov rcx,[r10]
    mov edx,WM_SETFONT
    mov r8,[rbp-8]
    mov r9d,1
    API SendMessageW
    add qword [rbp-16],8
    jmp .next
.done:
    add rsp,40
    ret

; R73: icon resource (RT_GROUP_ICON 1 + RT_ICON 1..N) generated by build-gui.ps1
%ifdef R73_ICON
%include "r73_icon.inc"
%endif

; ============================================================================
; R9 (WS5, WS6): the Indic font for Indic runs, and the typing mode.
; Win64 ABI throughout: PROLOG frames keep 16-byte alignment and shadow space.
; ============================================================================
extern __imp_GetDC, __imp_ReleaseDC, __imp_SelectObject, __imp_GetTextFaceW
extern __imp_DeleteObject, __imp_CheckMenuItem

section .bss
r9_word resb 64
alignb 4
r9_col_fmt resb 60
alignb 2
r9_out_text resw 32770
section .text

%include "windows/gui/r9_translit.asm"

; eax = UTF-16 unit -> eax = 1 when it can be part of a Latin word being typed
; ([A-Za-z0-9_~]; '~' starts ~N and ~n). Uses only eax.
r9_is_word_char:
    cmp eax,'~'
    je .yes
    cmp eax,'_'
    je .yes
    cmp eax,'0'
    jb .no
    cmp eax,'9'
    jbe .yes
    cmp eax,'A'
    jb .no
    cmp eax,'Z'
    jbe .yes
    cmp eax,'a'
    jb .no
    cmp eax,'z'
    jbe .yes
.no:
    xor eax,eax
    ret
.yes:
    mov eax,1
    ret

; eax = the pack the typing mode writes in: the selected language pack, or
; Sanskrit (Devanagari) when the language is Auto or Core.
r9_tl_pack:
    mov eax,[rel lang_mode]
    cmp eax,LANG_SANSKRIT
    jb .sk
    sub eax,2
    ret
.sk:
    xor eax,eax
    ret

r9_toggle_translit:
    PROLOG 48
    xor dword [rel r9_tl_on],1
    call set_lang_check
    call update_status
    EPILOG

; rcx = the native word just stored (UTF-16, 64 units), rdx = the rest of its
; pack line. Stores (pack, roman keyword, native word); the first line for a
; roman keyword wins, as in tools/translit.py.
r9_store_pair:
    PROLOG 48
    mov [rbp-8],rcx
    mov eax,[rel r9_pair_count]
    cmp eax,R9_MAX_PAIRS
    jae .done
.skip:
    mov al,[rdx]
    cmp al,' '
    je .adv
    cmp al,9
    je .adv
    jmp .tok
.adv:
    inc rdx
    jmp .skip
.tok:
    mov r9d,[rel r9_pair_count]
    mov rcx,r9
    shl rcx,5
    PTR r10,r9_pair_roman
    add r10,rcx                  ; this pair's roman slot
    xor r11d,r11d
.cp:
    movzx eax,byte [rdx+r11]
    cmp eax,32
    jbe .end
    cmp eax,127
    jae .done
    cmp r11d,31
    jae .done
    mov [r10+r11],al
    inc r11d
    jmp .cp
.end:
    test r11d,r11d
    jz .done
    mov byte [r10+r11],0
    xor ecx,ecx                  ; already stored for this pack?
.dup:
    cmp ecx,r9d
    jae .new
    PTR rax,r9_pair_pack
    movzx eax,byte [rax+rcx]
    cmp eax,[rel r9_cur_pack]
    jne .dnext
    mov rax,rcx
    shl rax,5
    PTR rdx,r9_pair_roman
    add rdx,rax
    xor r8d,r8d
.dcmp:
    mov al,[rdx+r8]
    cmp al,[r10+r8]
    jne .dnext
    test al,al
    jz .done                     ; same word: keep the first
    inc r8d
    jmp .dcmp
.dnext:
    inc ecx
    jmp .dup
.new:
    mov eax,[rel r9_cur_pack]
    PTR rdx,r9_pair_pack
    mov [rdx+r9],al
    mov rax,r9
    shl rax,7
    PTR rdx,r9_pair_native
    add rdx,rax
    mov r8,[rbp-8]
    xor ecx,ecx
.ncp:
    mov ax,[r8+rcx*2]
    mov [rdx+rcx*2],ax
    inc ecx
    cmp ecx,NATIVE_KEYWORD_UNITS
    jb .ncp
    inc dword [rel r9_pair_count]
.done:
    EPILOG

; Convert the Latin word that ends at the caret, if the typing mode is on, there
; is no selection, and the caret is not inside a string or a comment.
r9_tl_convert:
    PROLOG 112
    cmp dword [rel r9_tl_on],0
    je .done
    cmp qword [rel h_editor],0
    je .done
    mov rcx,[rel h_editor]
    mov edx,EM_GETSEL
    PTR r8,r9_tmp_sel
    PTR r9,r9_tmp_sel+4
    call send_message
    mov eax,[rel r9_tmp_sel]
    cmp eax,[rel r9_tmp_sel+4]
    jne .done
    mov [rbp-4],eax              ; caret
    mov rcx,[rel h_editor]
    mov edx,EM_LINEFROMCHAR
    mov r8d,eax
    xor r9d,r9d
    call send_message
    mov [rbp-8],eax              ; line
    mov rcx,[rel h_editor]
    mov edx,EM_LINEINDEX
    mov r8d,eax
    xor r9d,r9d
    call send_message
    mov [rbp-12],eax             ; line start
    mov ecx,[rbp-4]
    sub ecx,eax
    mov [rbp-16],ecx             ; column of the caret
    cmp ecx,0
    jle .done
    cmp ecx,2000
    ja .done
    PTR rax,r9_line_buf
    mov word [rax],2048
    mov rcx,[rel h_editor]
    mov edx,EM_GETLINE
    mov r8d,[rbp-8]
    PTR r9,r9_line_buf
    API SendMessageW
    cmp eax,[rbp-16]
    jb .done
    ; inside a string or after a comment marker? then leave it as typed
    PTR r10,r9_line_buf
    xor ecx,ecx
    xor r11d,r11d                ; open quote character, 0 = none
.scan:
    cmp ecx,[rbp-16]
    jae .scanned
    movzx eax,word [r10+rcx*2]
    test r11d,r11d
    jz .outside
    cmp eax,92                   ; backslash escape inside a string
    jne .q2
    inc ecx
    jmp .snext
.q2:
    cmp eax,r11d
    jne .snext
    xor r11d,r11d
    jmp .snext
.outside:
    cmp eax,'"'
    je .open
    cmp eax,39
    je .open
    cmp eax,'#'
    je .done
    cmp eax,'/'
    jne .snext
    lea edx,[ecx+1]
    cmp edx,[rbp-16]
    jae .snext
    cmp word [r10+rdx*2],'/'
    je .done
    jmp .snext
.open:
    mov r11d,eax
.snext:
    inc ecx
    jmp .scan
.scanned:
    test r11d,r11d
    jnz .done
    ; the word: back from the caret over [A-Za-z0-9_~]
    mov ecx,[rbp-16]
.back:
    test ecx,ecx
    jz .ws
    movzx eax,word [r10+rcx*2-2]
    call r9_is_word_char
    test eax,eax
    jz .ws
    dec ecx
    jmp .back
.ws:
    mov [rbp-20],ecx             ; word start column
    test ecx,ecx
    jz .wok
    movzx eax,word [r10+rcx*2-2] ; glued to a word in another script: leave it
    cmp eax,0x0900
    jb .wok
    cmp eax,0x0DFF
    jbe .done
.wok:
    mov eax,[rbp-16]
    sub eax,ecx
    mov [rbp-24],eax             ; word length
    test eax,eax
    jz .done
    cmp eax,63
    ja .done
    movzx eax,word [r10+rcx*2]   ; must start with a letter
    or eax,0x20
    cmp eax,'a'
    jb .done
    cmp eax,'z'
    ja .done
    ; narrow to bytes
    xor edx,edx
    PTR r11,r9_word
.narrow:
    cmp edx,[rbp-24]
    jae .narrowed
    lea eax,[ecx+edx]
    mov ax,[r10+rax*2]
    mov [r11+rdx],al
    inc edx
    jmp .narrow
.narrowed:
    mov byte [r11+rdx],0
    ; 1. a keyword of the pack -> the pack's own word
    call r9_tl_pack
    mov [rbp-28],eax
    xor ecx,ecx
.kw:
    cmp ecx,[rel r9_pair_count]
    jae .phonetic
    PTR rax,r9_pair_pack
    movzx eax,byte [rax+rcx]
    cmp eax,[rbp-28]
    jne .kwnext
    mov rax,rcx
    shl rax,5
    PTR rdx,r9_pair_roman
    add rdx,rax
    PTR r11,r9_word
    xor r8d,r8d
.kwcmp:
    mov al,[rdx+r8]
    cmp al,[r11+r8]
    jne .kwnext
    test al,al
    jz .kwfound
    inc r8d
    jmp .kwcmp
.kwnext:
    inc ecx
    jmp .kw
.kwfound:
    mov rax,rcx
    shl rax,7
    PTR rdx,r9_pair_native
    add rdx,rax
    PTR r8,r9_out_w
    xor ecx,ecx
.kwcopy:
    mov ax,[rdx+rcx*2]
    mov [r8+rcx*2],ax
    test ax,ax
    jz .replace
    inc ecx
    cmp ecx,NATIVE_KEYWORD_UNITS
    jb .kwcopy
    jmp .done
.phonetic:
    ; 2. otherwise spell it in the pack's script (tools/translit.py is the reference)
    mov [rbp-40],rsi
    mov [rbp-48],rdi
    PTR rsi,r9_word
    mov ecx,[rbp-24]
    mov edx,[rbp-28]
    PTR rdi,r9_out_w
    call r9_tl_phonetic
    mov rsi,[rbp-40]
    mov rdi,[rbp-48]
    PTR r8,r9_out_w
    mov word [r8+rax*2],0
    ; unchanged (no letter converted)? then leave the text alone
    cmp eax,[rbp-24]
    jne .replace
    PTR r11,r9_word
    xor ecx,ecx
.same:
    cmp ecx,eax
    jae .done
    movzx edx,word [r8+rcx*2]
    movzx r9d,byte [r11+rcx]
    cmp edx,r9d
    jne .replace
    inc ecx
    jmp .same
.replace:
    mov rcx,[rel h_editor]
    mov edx,EM_SETSEL
    mov r8d,[rbp-12]
    add r8d,[rbp-20]
    mov r9d,[rbp-4]
    call send_message
    mov rcx,[rel h_editor]
    mov edx,EM_REPLACESEL
    mov r8d,1                    ; can be undone with Ctrl+Z
    PTR r9,r9_out_w
    API SendMessageW
.done:
    EPILOG

; Is the Indic face installed? Selects it into a screen DC and reads back the
; face Windows actually chose. r9_indic_ok = 1 only on an exact match, so on a
; system without Nirmala UI nothing is forced and Windows' own fallback stays.
r9_check_indic_font:
    PROLOG 96
    mov dword [rel r9_indic_ok],0
    xor ecx,ecx
    call qword [rel __imp_GetDC]
    test rax,rax
    jz .done
    mov [rbp-8],rax
    mov ecx,-18
    PTR rdx,font_indic
    call make_readable_font
    test rax,rax
    jz .release
    mov [rbp-16],rax
    mov rcx,[rbp-8]
    mov rdx,rax
    call qword [rel __imp_SelectObject]
    mov [rbp-24],rax
    mov rcx,[rbp-8]
    mov edx,32
    PTR r8,r9_line_buf
    call qword [rel __imp_GetTextFaceW]
    PTR r10,r9_line_buf
    PTR r11,font_indic
    xor ecx,ecx
.cmp:
    mov ax,[r10+rcx*2]
    cmp ax,[r11+rcx*2]
    jne .restore
    test ax,ax
    jz .match
    inc ecx
    jmp .cmp
.match:
    mov dword [rel r9_indic_ok],1
.restore:
    mov rcx,[rbp-8]
    mov rdx,[rbp-24]
    call qword [rel __imp_SelectObject]
    mov rcx,[rbp-16]
    call qword [rel __imp_DeleteObject]
.release:
    xor ecx,ecx
    mov rdx,[rbp-8]
    call qword [rel __imp_ReleaseDC]
.done:
    EPILOG

; rcx = a RichEdit window, rdx = its text as RichEdit counts it (one unit per
; paragraph break). Everything gets the code face (Consolas); every run of Indic
; text (U+0900..U+0DFF, ZWJ, ZWNJ) gets Nirmala UI. The caller restores the
; selection afterwards.
r9_apply_script_faces:
    PROLOG 96
    cmp dword [rel r9_indic_ok],0
    je .done
    mov [rbp-8],rcx
    mov [rbp-16],rdx
    PTR rdx,font_code
    call .face
    mov rcx,[rbp-8]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_ALL
    PTR r9,face_fmt
    API SendMessageW
    PTR rdx,font_indic
    call .face
    mov dword [rbp-20],0         ; index
    mov dword [rbp-24],-1        ; run start, -1 = not in a run
.scan:
    mov r10,[rbp-16]
    mov ecx,[rbp-20]
    movzx eax,word [r10+rcx*2]
    test eax,eax
    jz .last
    cmp eax,0x200C
    je .indic
    cmp eax,0x200D
    je .indic
    cmp eax,0x0900
    jb .other
    cmp eax,0x0DFF
    ja .other
.indic:
    cmp dword [rbp-24],-1
    jne .next
    mov [rbp-24],ecx
    jmp .next
.other:
    cmp dword [rbp-24],-1
    je .next
    call .paint
.next:
    inc dword [rbp-20]
    jmp .scan
.last:
    cmp dword [rbp-24],-1
    je .done
    call .paint
.done:
    EPILOG
; fill face_fmt with CFM_FACE and the face at rdx (internal, no frame of its own)
.face:
    PTR r8,face_fmt
    mov dword [r8],92
    mov dword [r8+4],CFM_FACE
    mov dword [r8+8],0
    xor ecx,ecx
.fcp:
    mov ax,[rdx+rcx*2]
    mov [r8+26+rcx*2],ax
    test ax,ax
    jz .fdone
    inc ecx
    cmp ecx,31
    jb .fcp
    mov word [r8+26+rcx*2],0
.fdone:
    ret
; select [run start, index) and give it face_fmt (internal; aligns its own calls)
.paint:
    sub rsp,40
    mov rcx,[rbp-8]
    mov edx,EM_SETSEL
    mov r8d,[rbp-24]
    mov r9d,[rbp-20]
    call send_message
    mov rcx,[rbp-8]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_SELECTION
    PTR r9,face_fmt
    API SendMessageW
    mov dword [rbp-24],-1
    add rsp,40
    ret

; R9: after the output pane's text is replaced, RichEdit gives the new text the
; default colour, which was dark on the dark background (seen under Wine with the
; v188 IDE too: a run's output was nearly invisible). Re-apply the output colour
; to all of it, and the Indic face to Indic runs, as the editor does.
r9_output_restyle:
    PROLOG 64
    cmp qword [rel h_output],0
    je .done
    PTR r8,r9_col_fmt
    mov dword [r8],60
    mov dword [r8+4],CFM_COLOR
    mov dword [r8+8],0
    mov dword [r8+20],0x00B5D8A8
    mov rcx,[rel h_output]
    mov edx,EM_SETCHARFORMAT
    mov r8d,SCF_ALL
    PTR r9,r9_col_fmt
    call send_message
    mov rcx,[rel h_output]
    PTR rdx,r9_out_text
    mov r8d,32768
    API GetWindowTextW
    PTR r10,r9_out_text           ; CRLF -> one unit, as RichEdit counts
    mov r11,r10
.compact:
    mov ax,[r10]
    mov [r11],ax
    test ax,ax
    jz .compacted
    add r10,2
    add r11,2
    cmp ax,13
    jne .compact
    cmp word [r10],10
    jne .compact
    add r10,2
    jmp .compact
.compacted:
    mov rcx,[rel h_output]
    PTR rdx,r9_out_text
    call r9_apply_script_faces
    mov rcx,[rel h_output]
    mov edx,EM_SETSEL
    mov r8d,-1
    mov r9d,-1
    call send_message
.done:
    EPILOG
