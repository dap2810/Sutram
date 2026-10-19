/* Wine-harness only: Wine's powershell.exe is a stub that exits 0. This shim forwards the command line
   to PowerShell 7 in C:\pwsh72 (outside System32\WindowsPowerShell, so its modules load as its own). */
#include <windows.h>
#include <wchar.h>
int wmain(void) {
    wchar_t *cl = GetCommandLineW(), *rest = cl;
    if (*rest == L'"') { rest++; while (*rest && *rest != L'"') rest++; if (*rest) rest++; }
    else { while (*rest && *rest != L' ') rest++; }
    static wchar_t cmd[32768];
    swprintf(cmd, 32768, L"\"C:\\pwsh72\\pwsh.exe\"%ls", rest);
    STARTUPINFOW si; PROCESS_INFORMATION pi; ZeroMemory(&si, sizeof si); si.cb = sizeof si;
    if (!CreateProcessW(NULL, cmd, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)) return 9009;
    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 1; GetExitCodeProcess(pi.hProcess, &code);
    return (int)code;
}
