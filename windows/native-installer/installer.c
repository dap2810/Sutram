#define UNICODE
#define _UNICODE
#include <windows.h>
#include <commctrl.h>
#include <shlobj.h>
#include <shellapi.h>
#include <stdio.h>
#include <wchar.h>
#include <stdint.h>
#include <string.h>
#include <wincrypt.h>

#define APP_NAME L"Sutram Setup"
#define APP_VERSION L"0.1.0"
#define PART_PAYLOAD 1
#define PART_INSTALL_PS1 2
#define PART_UNINSTALL_PS1 3
#define PART_ICON 4
#define WM_INSTALL_DONE (WM_APP + 1)

#define IDC_TITLE 1001
#define IDC_BODY 1002
#define IDC_PATH 1003
#define IDC_BROWSE 1004
#define IDC_ADDPATH 1005
#define IDC_DESKTOP 1006
#define IDC_ACCEPT 1007
#define IDC_SUMMARY 1008
#define IDC_PROGRESS 1009
#define IDC_FINISH_TERMINAL 1010
#define IDC_BACK 1101
#define IDC_NEXT 1102
#define IDC_CANCEL 1103

static HINSTANCE g_hInst;
static HWND g_hwnd;
static HWND g_title, g_body, g_path, g_browse, g_addPath, g_desktop, g_accept, g_summary, g_progress, g_finishTerminal;
static HWND g_back, g_next, g_cancel;
static HFONT g_font, g_titleFont;
static int g_page = 0;
static int g_installResult = -1;
static BOOL g_optionAddPath = TRUE;
static BOOL g_optionDesktop = FALSE;
static WCHAR g_installDir[4096];
static WCHAR g_tempRoot[4096];
static WCHAR g_logPath[4096];

static void SetVisible(HWND h, BOOL show) { ShowWindow(h, show ? SW_SHOW : SW_HIDE); }
static void SetText(HWND h, const WCHAR *s) { SetWindowTextW(h, s); }

static BOOL GetPerUserProgramsRoot(WCHAR *out, DWORD chars) {
    WCHAR base[4096];
    DWORD n;
    if (!out || chars < 16) return FALSE;
    n = GetEnvironmentVariableW(L"LOCALAPPDATA", base, (DWORD)(sizeof(base)/sizeof(base[0])));
    if (!n || n >= (DWORD)(sizeof(base)/sizeof(base[0]))) {
        if (FAILED(SHGetFolderPathW(NULL, CSIDL_LOCAL_APPDATA, NULL, SHGFP_TYPE_CURRENT, base))) return FALSE;
    }
    _snwprintf(out, chars - 1, L"%s\\Programs", base);
    out[chars - 1] = 0;
    return TRUE;
}

static BOOL IsPathUnderRoot(const WCHAR *path, const WCHAR *root) {
    size_t rootLen;
    if (!path || !root) return FALSE;
    rootLen = wcslen(root);
    if (_wcsnicmp(path, root, rootLen) != 0) return FALSE;
    return path[rootLen] == 0 || path[rootLen] == L'\\' || path[rootLen] == L'/';
}

static BOOL IsSupportedInstallPath(const WCHAR *path, BOOL addPath, const WCHAR **reason) {
    size_t len;
    WCHAR userPrograms[4096];
    if (!path || !path[0]) { if (reason) *reason=L"Choose an installation folder."; return FALSE; }
    len = wcslen(path);
    if (len > 220) { if (reason) *reason=L"The installation path is too long. Choose a shorter folder."; return FALSE; }
    if (len < 3 || path[1] != L':' || (path[2] != L'\\' && path[2] != L'/')) { if (reason) *reason=L"Choose an absolute folder on a local Windows drive."; return FALSE; }
    if (wcspbrk(path,L"%&|<>^!")) { if (reason) *reason=L"The installation path contains shell metacharacters that are not supported."; return FALSE; }
    if (addPath && wcschr(path,L';')) { if (reason) *reason=L"The installation path cannot contain a semicolon when Add to PATH is selected."; return FALSE; }
    if (!GetPerUserProgramsRoot(userPrograms, (DWORD)(sizeof(userPrograms)/sizeof(userPrograms[0])))) {
        if (reason) *reason=L"Windows could not resolve your per-user Programs folder.";
        return FALSE;
    }
    if (!IsPathUnderRoot(path, userPrograms) || _wcsicmp(path, userPrograms) == 0) {
        if (reason) *reason=L"Sutram uses a per-user install. Choose a folder under %LOCALAPPDATA%\\Programs (the default is recommended).";
        return FALSE;
    }
    return TRUE;
}

#pragma pack(push,1)
typedef struct PackageFooter {
    char magic[8];
    uint32_t version;
    uint32_t reserved;
    uint64_t payloadOffset;
    uint64_t payloadSize;
    uint64_t installOffset;
    uint64_t installSize;
    uint64_t uninstallOffset;
    uint64_t uninstallSize;
    uint64_t iconOffset;
    uint64_t iconSize;
    unsigned char payloadSha256[32];
    unsigned char installSha256[32];
    unsigned char uninstallSha256[32];
    unsigned char iconSha256[32];
} PACKAGE_FOOTER;
#pragma pack(pop)

_Static_assert(sizeof(PACKAGE_FOOTER) == 208, "Unexpected package footer size");

static BOOL GetSelfPath(WCHAR *path, DWORD chars) {
    DWORD n = GetModuleFileNameW(NULL, path, chars);
    return n > 0 && n < chars;
}

static BOOL HashFileRange(HANDLE file, uint64_t offset, uint64_t size, unsigned char outHash[32]) {
    HCRYPTPROV provider = 0;
    HCRYPTHASH hash = 0;
    LARGE_INTEGER pos;
    unsigned char buffer[65536];
    uint64_t remaining = size;
    BOOL ok = FALSE;
    if (!CryptAcquireContextW(&provider, NULL, NULL, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) return FALSE;
    if (!CryptCreateHash(provider, CALG_SHA_256, 0, 0, &hash)) goto done;
    pos.QuadPart = (LONGLONG)offset;
    if (!SetFilePointerEx(file, pos, NULL, FILE_BEGIN)) goto done;
    while (remaining > 0) {
        DWORD want = (remaining > sizeof(buffer)) ? (DWORD)sizeof(buffer) : (DWORD)remaining;
        DWORD got = 0;
        if (!ReadFile(file, buffer, want, &got, NULL) || got != want) goto done;
        if (!CryptHashData(hash, buffer, got, 0)) goto done;
        remaining -= got;
    }
    {
        DWORD hashSize = 32;
        if (!CryptGetHashParam(hash, HP_HASHVAL, outHash, &hashSize, 0) || hashSize != 32) goto done;
    }
    ok = TRUE;
done:
    if (hash) CryptDestroyHash(hash);
    if (provider) CryptReleaseContext(provider, 0);
    return ok;
}

static BOOL ReadPackageFooter(PACKAGE_FOOTER *footer, uint64_t *footerStart) {
    WCHAR self[4096];
    HANDLE file;
    LARGE_INTEGER fileSize, pos;
    DWORD got = 0;
    uint64_t end;
    if (!GetSelfPath(self, 4096)) return FALSE;
    file = CreateFileW(self, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_DELETE, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    if (!GetFileSizeEx(file, &fileSize) || fileSize.QuadPart < (LONGLONG)sizeof(PACKAGE_FOOTER)) { CloseHandle(file); return FALSE; }
    end = (uint64_t)fileSize.QuadPart - (uint64_t)sizeof(PACKAGE_FOOTER);
    pos.QuadPart = (LONGLONG)end;
    if (!SetFilePointerEx(file, pos, NULL, FILE_BEGIN) || !ReadFile(file, footer, sizeof(*footer), &got, NULL) || got != sizeof(*footer)) {
        CloseHandle(file); return FALSE;
    }
    CloseHandle(file);
    if (memcmp(footer->magic, "SUTPKG10", 8) != 0 || footer->version != 1 || footer->reserved != 0) return FALSE;
    if (footer->payloadSize < 1024 || footer->installSize < 256 || footer->uninstallSize < 256 || footer->iconSize < 128) return FALSE;
    if (footer->payloadOffset > end || footer->payloadSize > end - footer->payloadOffset) return FALSE;
    if (footer->installOffset > end || footer->installSize > end - footer->installOffset) return FALSE;
    if (footer->uninstallOffset > end || footer->uninstallSize > end - footer->uninstallOffset) return FALSE;
    if (footer->iconOffset > end || footer->iconSize > end - footer->iconOffset) return FALSE;
    if (footer->payloadOffset + footer->payloadSize != footer->installOffset) return FALSE;
    if (footer->installOffset + footer->installSize != footer->uninstallOffset) return FALSE;
    if (footer->uninstallOffset + footer->uninstallSize != footer->iconOffset) return FALSE;
    if (footer->iconOffset + footer->iconSize != end) return FALSE;
    if (footerStart) *footerStart = end;
    return TRUE;
}

static BOOL GetPartInfo(const PACKAGE_FOOTER *footer, int part, uint64_t *offset, uint64_t *size, const unsigned char **hash) {
    if (part == PART_PAYLOAD) { *offset=footer->payloadOffset; *size=footer->payloadSize; *hash=footer->payloadSha256; return TRUE; }
    if (part == PART_INSTALL_PS1) { *offset=footer->installOffset; *size=footer->installSize; *hash=footer->installSha256; return TRUE; }
    if (part == PART_UNINSTALL_PS1) { *offset=footer->uninstallOffset; *size=footer->uninstallSize; *hash=footer->uninstallSha256; return TRUE; }
    if (part == PART_ICON) { *offset=footer->iconOffset; *size=footer->iconSize; *hash=footer->iconSha256; return TRUE; }
    return FALSE;
}

static BOOL ValidatePackage(void) {
    WCHAR self[4096];
    PACKAGE_FOOTER footer;
    HANDLE file;
    int part;
    if (!ReadPackageFooter(&footer, NULL) || !GetSelfPath(self, 4096)) return FALSE;
    file = CreateFileW(self, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_DELETE, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    for (part = PART_PAYLOAD; part <= PART_ICON; part++) {
        uint64_t offset, size;
        const unsigned char *expected;
        unsigned char actual[32];
        if (!GetPartInfo(&footer, part, &offset, &size, &expected) || !HashFileRange(file, offset, size, actual) || memcmp(actual, expected, 32) != 0) {
            CloseHandle(file); return FALSE;
        }
    }
    CloseHandle(file);
    return TRUE;
}

static BOOL WritePackagePart(int part, const WCHAR *path) {
    WCHAR self[4096];
    PACKAGE_FOOTER footer;
    uint64_t offset, size, remaining;
    const unsigned char *expected;
    unsigned char actual[32];
    unsigned char buffer[65536];
    HANDLE input = INVALID_HANDLE_VALUE, output = INVALID_HANDLE_VALUE;
    LARGE_INTEGER pos;
    BOOL ok = FALSE;
    HCRYPTPROV provider = 0;
    HCRYPTHASH hash = 0;
    if (!ReadPackageFooter(&footer, NULL) || !GetPartInfo(&footer, part, &offset, &size, &expected) || !GetSelfPath(self, 4096)) return FALSE;
    input = CreateFileW(self, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_DELETE, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (input == INVALID_HANDLE_VALUE) goto done;
    output = CreateFileW(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (output == INVALID_HANDLE_VALUE) goto done;
    if (!CryptAcquireContextW(&provider, NULL, NULL, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) goto done;
    if (!CryptCreateHash(provider, CALG_SHA_256, 0, 0, &hash)) goto done;
    pos.QuadPart = (LONGLONG)offset;
    if (!SetFilePointerEx(input, pos, NULL, FILE_BEGIN)) goto done;
    remaining = size;
    while (remaining > 0) {
        DWORD want = (remaining > sizeof(buffer)) ? (DWORD)sizeof(buffer) : (DWORD)remaining;
        DWORD got = 0, written = 0;
        if (!ReadFile(input, buffer, want, &got, NULL) || got != want) goto done;
        if (!WriteFile(output, buffer, got, &written, NULL) || written != got) goto done;
        if (!CryptHashData(hash, buffer, got, 0)) goto done;
        remaining -= got;
    }
    {
        DWORD hashSize = 32;
        if (!CryptGetHashParam(hash, HP_HASHVAL, actual, &hashSize, 0) || hashSize != 32) goto done;
    }
    if (memcmp(actual, expected, 32) != 0) goto done;
    FlushFileBuffers(output);
    ok = TRUE;
done:
    if (hash) CryptDestroyHash(hash);
    if (provider) CryptReleaseContext(provider, 0);
    if (input != INVALID_HANDLE_VALUE) CloseHandle(input);
    if (output != INVALID_HANDLE_VALUE) CloseHandle(output);
    if (!ok) DeleteFileW(path);
    return ok;
}

static void QuoteArg(const WCHAR *in, WCHAR *out, size_t cap) {
    size_t i = 0, j = 0;
    if (!out || cap < 3) return;
    out[j++] = L'"';
    while (in && in[i] && j + 4 < cap) {
        size_t slashes = 0, k;
        while (in[i] == L'\\') { slashes++; i++; }
        if (in[i] == L'"') {
            for (k = 0; k < slashes * 2 + 1 && j + 2 < cap; k++) out[j++] = L'\\';
            out[j++] = L'"';
            i++;
        } else if (in[i] == 0) {
            for (k = 0; k < slashes * 2 && j + 2 < cap; k++) out[j++] = L'\\';
            break;
        } else {
            for (k = 0; k < slashes && j + 2 < cap; k++) out[j++] = L'\\';
            out[j++] = in[i++];
        }
    }
    if (j + 1 < cap) out[j++] = L'"';
    out[j < cap ? j : cap - 1] = 0;
}

static BOOL RunProcessAndWait(const WCHAR *exe, WCHAR *cmdline, DWORD *exitCode) {
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    BOOL ok;
    ZeroMemory(&si, sizeof(si));
    ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);
    ok = CreateProcessW(exe, cmdline, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    if (!ok) return FALSE;
    WaitForSingleObject(pi.hProcess, INFINITE);
    if (!GetExitCodeProcess(pi.hProcess, exitCode)) *exitCode = 1;
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return TRUE;
}

static BOOL EnsureTempRoot(void) {
    WCHAR temp[4096];
    DWORD pid = GetCurrentProcessId();
    if (!GetTempPathW((DWORD)(sizeof(temp)/sizeof(temp[0])), temp)) return FALSE;
    _snwprintf(g_tempRoot, (sizeof(g_tempRoot)/sizeof(g_tempRoot[0])) - 1, L"%sSutram-Setup-%lu", temp, (unsigned long)pid);
    g_tempRoot[(sizeof(g_tempRoot)/sizeof(g_tempRoot[0])) - 1] = 0;
    if (!CreateDirectoryW(g_tempRoot, NULL) && GetLastError() != ERROR_ALREADY_EXISTS) return FALSE;
    _snwprintf(g_logPath, (sizeof(g_logPath)/sizeof(g_logPath[0])) - 1, L"%s\\install.log", g_tempRoot);
    g_logPath[(sizeof(g_logPath)/sizeof(g_logPath[0])) - 1] = 0;
    return TRUE;
}

static void RemoveTempRoot(void) {
    WCHAR cmd[8192];
    if (!g_tempRoot[0]) return;
    _snwprintf(cmd, (sizeof(cmd)/sizeof(cmd[0])) - 1, L"cmd.exe /c rmdir /s /q \"%s\"", g_tempRoot);
    cmd[(sizeof(cmd)/sizeof(cmd[0])) - 1] = 0;
    {
        STARTUPINFOW si; PROCESS_INFORMATION pi;
        ZeroMemory(&si, sizeof(si)); ZeroMemory(&pi, sizeof(pi)); si.cb = sizeof(si);
        if (CreateProcessW(NULL, cmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
            WaitForSingleObject(pi.hProcess, 10000);
            CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
        }
    }
}

static int InvokeInstallScript(void) {
    WCHAR payload[4096], script[4096], exePath[4096], ps[4096];
    WCHAR qScript[8192], qPayload[8192], qDir[8192], qExe[8192], qLog[8192];
    WCHAR cmd[32768];
    DWORD code = 1;
    BOOL addPath = g_optionAddPath;
    BOOL desktop = g_optionDesktop;
    if (!EnsureTempRoot()) return 10;
    _snwprintf(payload, 4095, L"%s\\payload.zip", g_tempRoot);
    _snwprintf(script, 4095, L"%s\\install-core.ps1", g_tempRoot);
    if (!WritePackagePart(PART_PAYLOAD, payload) || !WritePackagePart(PART_INSTALL_PS1, script)) return 11;
    if (!GetModuleFileNameW(NULL, exePath, 4096)) return 12;
    _snwprintf(ps, 4095, L"%s\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", L"C:\\Windows");
    {
        WCHAR winDir[4096];
        if (GetWindowsDirectoryW(winDir, 4096)) _snwprintf(ps, 4095, L"%s\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", winDir);
    }
    QuoteArg(script, qScript, 8192);
    QuoteArg(payload, qPayload, 8192);
    QuoteArg(g_installDir, qDir, 8192);
    QuoteArg(exePath, qExe, 8192);
    QuoteArg(g_logPath, qLog, 8192);
    _snwprintf(cmd, 32767,
        L"powershell.exe -NoProfile -ExecutionPolicy Bypass -File %s -PayloadZip %s -InstallDir %s -SetupExePath %s -LogPath %s%s%s",
        qScript, qPayload, qDir, qExe, qLog,
        addPath ? L" -AddPath" : L"",
        desktop ? L" -DesktopShortcut" : L"");
    cmd[32767] = 0;
    if (!RunProcessAndWait(ps, cmd, &code)) return 13;
    if (code == 0) RemoveTempRoot();
    return (int)code;
}

static DWORD WINAPI InstallThread(LPVOID unused) {
    int result;
    (void)unused;
    result = InvokeInstallScript();
    g_installResult = result;
    PostMessageW(g_hwnd, WM_INSTALL_DONE, (WPARAM)result, 0);
    return 0;
}

static int InvokeUninstall(void) {
    WCHAR exePath[4096], installDir[4096], temp[4096], script[4096], log[4096], ps[4096];
    WCHAR qScript[8192], qDir[8192], qExe[8192], qLog[8192], cmd[32768];
    WCHAR *slash;
    DWORD code = 1;
    if (!GetModuleFileNameW(NULL, exePath, 4096)) return 20;
    wcscpy(installDir, exePath);
    slash = wcsrchr(installDir, L'\\');
    if (!slash) return 21;
    *slash = 0;
    if (!GetTempPathW(4096, temp)) return 22;
    _snwprintf(script, 4095, L"%sSutram-Uninstall-%lu.ps1", temp, (unsigned long)GetCurrentProcessId());
    _snwprintf(log, 4095, L"%sSutram-Uninstall-%lu.log", temp, (unsigned long)GetCurrentProcessId());
    if (!WritePackagePart(PART_UNINSTALL_PS1, script)) return 23;
    {
        WCHAR winDir[4096];
        if (!GetWindowsDirectoryW(winDir, 4096)) return 24;
        _snwprintf(ps, 4095, L"%s\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", winDir);
    }
    QuoteArg(script, qScript, 8192);
    QuoteArg(installDir, qDir, 8192);
    QuoteArg(exePath, qExe, 8192);
    QuoteArg(log, qLog, 8192);
    _snwprintf(cmd, 32767, L"powershell.exe -NoProfile -ExecutionPolicy Bypass -File %s -InstallDir %s -SelfPath %s -LogPath %s", qScript, qDir, qExe, qLog);
    cmd[32767] = 0;
    if (!RunProcessAndWait(ps, cmd, &code)) return 25;
    DeleteFileW(script);
    return (int)code;
}

static void EscapePowerShellLiteral(const WCHAR *in, WCHAR *out, size_t cap) {
    size_t i = 0, j = 0;
    if (!out || cap == 0) return;
    while (in && in[i] && j + 2 < cap) {
        if (in[i] == L'\'') out[j++] = L'\'';
        out[j++] = in[i++];
    }
    out[j] = 0;
}

static void ScheduleSelfDelete(const WCHAR *selfPath, const WCHAR *installDir) {
    WCHAR temp[4096], scriptPath[4096], ps[4096], qScript[8192], cmd[12000];
    WCHAR safeSelf[8192], safeDir[8192], script[20000];
    WCHAR winDir[4096];
    HANDLE f;
    DWORD written;
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    const WORD bom = 0xFEFF;
    if (!GetTempPathW(4096, temp)) return;
    if (!GetWindowsDirectoryW(winDir, 4096)) return;
    _snwprintf(scriptPath, 4095, L"%sSutram-Cleanup-%lu.ps1", temp, (unsigned long)GetCurrentProcessId());
    _snwprintf(ps, 4095, L"%s\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", winDir);
    EscapePowerShellLiteral(selfPath, safeSelf, 8192);
    EscapePowerShellLiteral(installDir, safeDir, 8192);
    _snwprintf(script, 19999,
        L"$ErrorActionPreference='SilentlyContinue'\r\n"
        L"$self='%s'\r\n$dir='%s'\r\n"
        L"for($i=0;$i -lt 120;$i++){Remove-Item -LiteralPath $self -Force -ErrorAction SilentlyContinue;if(-not(Test-Path -LiteralPath $self)){break};Start-Sleep -Milliseconds 500}\r\n"
        L"Remove-Item -LiteralPath $dir -Force -ErrorAction SilentlyContinue\r\n"
        L"Remove-Item -LiteralPath $PSCommandPath -Force -ErrorAction SilentlyContinue\r\n",
        safeSelf, safeDir);
    script[19999] = 0;
    f = CreateFileW(scriptPath, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_HIDDEN, NULL);
    if (f == INVALID_HANDLE_VALUE) return;
    WriteFile(f, &bom, sizeof(bom), &written, NULL);
    WriteFile(f, script, (DWORD)(wcslen(script) * sizeof(WCHAR)), &written, NULL);
    CloseHandle(f);
    QuoteArg(scriptPath, qScript, 8192);
    _snwprintf(cmd, 11999, L"powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File %s", qScript);
    ZeroMemory(&si, sizeof(si)); ZeroMemory(&pi, sizeof(pi)); si.cb = sizeof(si);
    if (CreateProcessW(ps, cmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
        CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    }
}

static void DefaultInstallDir(void) {
    WCHAR base[4096];
    if (GetPerUserProgramsRoot(base, (DWORD)(sizeof(base)/sizeof(base[0])))) {
        _snwprintf(g_installDir, 4095, L"%s\\Sutram", base);
    } else {
        DWORD n = GetEnvironmentVariableW(L"LOCALAPPDATA", base, 4096);
        if (!n || n >= 4096) base[0] = 0;
        _snwprintf(g_installDir, 4095, L"%s\\Programs\\Sutram", base);
    }
    g_installDir[4095] = 0;
}

static void BrowseFolder(void) {
    BROWSEINFOW bi;
    PIDLIST_ABSOLUTE pidl;
    WCHAR path[4096];
    ZeroMemory(&bi, sizeof(bi));
    bi.hwndOwner = g_hwnd;
    bi.lpszTitle = L"Choose the folder where Sutram should be installed";
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE;
    pidl = SHBrowseForFolderW(&bi);
    if (pidl) {
        if (SHGetPathFromIDListW(pidl, path)) {
            WCHAR finalPath[4096];
            size_t len = wcslen(path);
            size_t suffixLen = wcslen(L"\\Sutram");
            if (len >= suffixLen && _wcsicmp(path + len - suffixLen, L"\\Sutram") == 0) wcscpy(finalPath, path);
            else _snwprintf(finalPath, 4095, L"%s\\Sutram", path);
            finalPath[4095] = 0;
            SetWindowTextW(g_path, finalPath);
        }
        CoTaskMemFree(pidl);
    }
}

static void UpdateSummary(void) {
    WCHAR path[4096];
    WCHAR summary[10000];
    GetWindowTextW(g_path, path, 4096);
    _snwprintf(summary, 9999,
        L"Sutram is ready to install for your Windows account.\r\n\r\nInstallation folder:\r\n%s\r\n\r\nAdd to user PATH: %s\r\nDesktop shortcut: %s\r\n\r\nNo administrator permission is required. Click Install to continue.",
        path,
        SendMessageW(g_addPath, BM_GETCHECK, 0, 0) == BST_CHECKED ? L"Yes" : L"No",
        SendMessageW(g_desktop, BM_GETCHECK, 0, 0) == BST_CHECKED ? L"Yes" : L"No");
    summary[9999] = 0;
    SetText(g_summary, summary);
}

static void ShowPage(int page) {
    g_page = page;
    SetVisible(g_path, page == 2);
    SetVisible(g_browse, page == 2);
    SetVisible(g_addPath, page == 2);
    SetVisible(g_desktop, page == 2);
    SetVisible(g_accept, page == 1);
    SetVisible(g_summary, page == 3);
    SetVisible(g_progress, page == 4);
    SetVisible(g_finishTerminal, page == 5);
    EnableWindow(g_back, page > 0 && page < 4);
    EnableWindow(g_cancel, page < 4);
    SetVisible(g_back, page < 5);
    SetVisible(g_cancel, page < 5);

    if (page == 0) {
        SetText(g_title, L"Welcome to Sutram Setup");
        SetText(g_body, L"This wizard installs Sutram only for your Windows account and never requests administrator permission.\r\n\r\nNo WSL, Linux, Python, NASM, MinGW, Visual Studio, or other development tools are required to use Sutram after installation.");
        SetText(g_next, L"Next >"); EnableWindow(g_next, TRUE);
    } else if (page == 1) {
        SetText(g_title, L"License Agreement");
        SetText(g_body, L"Please review the LICENSE.txt included with Sutram. By continuing, you confirm that you accept the license terms for this package.");
        SetText(g_accept, L"I accept the license terms");
        EnableWindow(g_next, SendMessageW(g_accept, BM_GETCHECK, 0, 0) == BST_CHECKED);
        SetText(g_next, L"Next >");
    } else if (page == 2) {
        SetText(g_title, L"Installation Options");
        SetText(g_body, L"Sutram installs under your per-user %LOCALAPPDATA%\\Programs folder. Choose the user-level Windows integration options you want.");
        SetText(g_next, L"Next >"); EnableWindow(g_next, TRUE);
    } else if (page == 3) {
        SetText(g_title, L"Ready to Install");
        SetText(g_body, L"");
        UpdateSummary();
        SetText(g_next, L"Install"); EnableWindow(g_next, TRUE);
    } else if (page == 4) {
        SetText(g_title, L"Installing Sutram");
        SetText(g_body, L"Installing and validating Sutram. This normally completes quickly.\r\n\r\nPlease do not close this window.");
        SetText(g_next, L"Installing..."); EnableWindow(g_next, FALSE);
        SendMessageW(g_progress, PBM_SETMARQUEE, TRUE, 35);
    } else if (page == 5) {
        SetText(g_title, g_installResult == 0 ? L"Sutram Setup Complete" : L"Sutram Setup Failed");
        if (g_installResult == 0) {
            SetText(g_body, L"Sutram was installed and validated successfully.\r\n\r\nOpen a new Command Prompt or PowerShell window and run:\r\n\r\n    sutram --version\r\n    sutram --help");
            SetText(g_finishTerminal, L"Open Sutram Terminal when I click Finish");
            SendMessageW(g_finishTerminal, BM_SETCHECK, BST_CHECKED, 0);
        } else {
            WCHAR msg[9000];
            _snwprintf(msg, 8999, L"Installation failed with exit code %d.\r\n\r\nThe diagnostic log was retained at:\r\n%s", g_installResult, g_logPath[0] ? g_logPath : L"(log unavailable)");
            SetText(g_body, msg);
            SetVisible(g_finishTerminal, FALSE);
        }
        SetVisible(g_next, TRUE);
        SetText(g_next, L"Finish"); EnableWindow(g_next, TRUE);
    }
}

static void LaunchTerminal(void) {
    WCHAR args[10000];
    WCHAR bin[4096];
    _snwprintf(bin, 4095, L"%s\\bin", g_installDir);
    _snwprintf(args, 9999, L"/K \"set \"PATH=%s;%%PATH%%\" && sutram --version\"", bin);
    ShellExecuteW(NULL, L"open", L"cmd.exe", args, NULL, SW_SHOWNORMAL);
}

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE: {
            LOGFONTW lf;
            ZeroMemory(&lf, sizeof(lf));
            lf.lfHeight = -18; wcscpy(lf.lfFaceName, L"Segoe UI");
            g_font = CreateFontIndirectW(&lf);
            lf.lfHeight = -28; lf.lfWeight = FW_SEMIBOLD;
            g_titleFont = CreateFontIndirectW(&lf);
            g_title = CreateWindowW(L"STATIC", L"", WS_CHILD|WS_VISIBLE, 34, 26, 560, 42, hwnd, (HMENU)IDC_TITLE, g_hInst, NULL);
            g_body = CreateWindowW(L"STATIC", L"", WS_CHILD|WS_VISIBLE, 36, 82, 556, 140, hwnd, (HMENU)IDC_BODY, g_hInst, NULL);
            g_accept = CreateWindowW(L"BUTTON", L"", WS_CHILD|BS_AUTOCHECKBOX, 38, 230, 520, 28, hwnd, (HMENU)IDC_ACCEPT, g_hInst, NULL);
            g_path = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"", WS_CHILD|ES_AUTOHSCROLL, 38, 170, 455, 28, hwnd, (HMENU)IDC_PATH, g_hInst, NULL);
            g_browse = CreateWindowW(L"BUTTON", L"Browse...", WS_CHILD|BS_PUSHBUTTON, 505, 170, 88, 28, hwnd, (HMENU)IDC_BROWSE, g_hInst, NULL);
            g_addPath = CreateWindowW(L"BUTTON", L"Add Sutram to your user PATH (recommended)", WS_CHILD|BS_AUTOCHECKBOX, 40, 220, 500, 28, hwnd, (HMENU)IDC_ADDPATH, g_hInst, NULL);
            g_desktop = CreateWindowW(L"BUTTON", L"Create a Desktop shortcut for Sutram Terminal", WS_CHILD|BS_AUTOCHECKBOX, 40, 254, 500, 28, hwnd, (HMENU)IDC_DESKTOP, g_hInst, NULL);
            g_summary = CreateWindowW(L"STATIC", L"", WS_CHILD, 38, 100, 550, 210, hwnd, (HMENU)IDC_SUMMARY, g_hInst, NULL);
            g_progress = CreateWindowExW(0, PROGRESS_CLASSW, L"", WS_CHILD|PBS_MARQUEE, 38, 240, 550, 24, hwnd, (HMENU)IDC_PROGRESS, g_hInst, NULL);
            g_finishTerminal = CreateWindowW(L"BUTTON", L"", WS_CHILD|BS_AUTOCHECKBOX, 38, 250, 520, 28, hwnd, (HMENU)IDC_FINISH_TERMINAL, g_hInst, NULL);
            g_back = CreateWindowW(L"BUTTON", L"< Back", WS_CHILD|WS_VISIBLE|BS_PUSHBUTTON, 330, 336, 88, 30, hwnd, (HMENU)IDC_BACK, g_hInst, NULL);
            g_next = CreateWindowW(L"BUTTON", L"Next >", WS_CHILD|WS_VISIBLE|BS_DEFPUSHBUTTON, 425, 336, 88, 30, hwnd, (HMENU)IDC_NEXT, g_hInst, NULL);
            g_cancel = CreateWindowW(L"BUTTON", L"Cancel", WS_CHILD|WS_VISIBLE|BS_PUSHBUTTON, 520, 336, 88, 30, hwnd, (HMENU)IDC_CANCEL, g_hInst, NULL);
            {
                HWND ctrls[] = {g_title,g_body,g_accept,g_path,g_browse,g_addPath,g_desktop,g_summary,g_progress,g_finishTerminal,g_back,g_next,g_cancel};
                size_t i;
                for (i=0;i<sizeof(ctrls)/sizeof(ctrls[0]);i++) SendMessageW(ctrls[i], WM_SETFONT, (WPARAM)(ctrls[i]==g_title?g_titleFont:g_font), TRUE);
            }
            DefaultInstallDir();
            SetWindowTextW(g_path, g_installDir);
            SendMessageW(g_addPath, BM_SETCHECK, BST_CHECKED, 0);
            ShowPage(0);
            return 0;
        }
        case WM_COMMAND: {
            int id = LOWORD(wParam);
            if (id == IDC_BROWSE) { BrowseFolder(); return 0; }
            if (id == IDC_ACCEPT) { EnableWindow(g_next, SendMessageW(g_accept, BM_GETCHECK, 0, 0) == BST_CHECKED); return 0; }
            if (id == IDC_BACK && g_page > 0 && g_page < 4) { ShowPage(g_page - 1); return 0; }
            if (id == IDC_CANCEL) { if (MessageBoxW(hwnd, L"Cancel Sutram Setup?", APP_NAME, MB_YESNO|MB_ICONQUESTION) == IDYES) DestroyWindow(hwnd); return 0; }
            if (id == IDC_NEXT) {
                if (g_page == 0) { ShowPage(1); return 0; }
                if (g_page == 1) { if (SendMessageW(g_accept, BM_GETCHECK,0,0)==BST_CHECKED) ShowPage(2); return 0; }
                if (g_page == 2) {
                    GetWindowTextW(g_path, g_installDir, 4096);
                    if (!g_installDir[0]) { MessageBoxW(hwnd,L"Choose an installation folder.",APP_NAME,MB_OK|MB_ICONWARNING); return 0; }
                    ShowPage(3); return 0;
                }
                if (g_page == 3) {
                    GetWindowTextW(g_path, g_installDir, 4096);
                    g_optionAddPath = (SendMessageW(g_addPath, BM_GETCHECK, 0, 0) == BST_CHECKED);
                    g_optionDesktop = (SendMessageW(g_desktop, BM_GETCHECK, 0, 0) == BST_CHECKED);
                    {
                        const WCHAR *pathReason = NULL;
                        if (!IsSupportedInstallPath(g_installDir,g_optionAddPath,&pathReason)) { MessageBoxW(hwnd,pathReason ? pathReason : L"Choose a valid installation folder.",APP_NAME,MB_OK|MB_ICONWARNING); ShowPage(2); return 0; }
                    }
                    ShowPage(4);
                    if (!CreateThread(NULL,0,InstallThread,NULL,0,NULL)) { g_installResult = 99; ShowPage(5); }
                    return 0;
                }
                if (g_page == 5) {
                    if (g_installResult == 0 && IsWindowVisible(g_finishTerminal) && SendMessageW(g_finishTerminal,BM_GETCHECK,0,0)==BST_CHECKED) LaunchTerminal();
                    DestroyWindow(hwnd); return 0;
                }
            }
            break;
        }
        case WM_INSTALL_DONE:
            SendMessageW(g_progress, PBM_SETMARQUEE, FALSE, 0);
            ShowPage(5);
            return 0;
        case WM_CLOSE:
            if (g_page == 4) return 0;
            DestroyWindow(hwnd); return 0;
        case WM_DESTROY:
            if (g_font) DeleteObject(g_font);
            if (g_titleFont) DeleteObject(g_titleFont);
            PostQuitMessage(0); return 0;
    }
    return DefWindowProcW(hwnd,msg,wParam,lParam);
}

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrev, PWSTR cmdLine, int nCmdShow) {
    int argc = 0, i;
    LPWSTR *argv;
    BOOL selfTest = FALSE, uninstall = FALSE;
    INITCOMMONCONTROLSEX icc;
    WNDCLASSEXW wc;
    MSG msg;
    (void)hPrev; (void)cmdLine; (void)nCmdShow;
    g_hInst = hInstance;
    argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (argv) {
        for (i=1;i<argc;i++) {
            if (_wcsicmp(argv[i],L"--self-test")==0) selfTest=TRUE;
            else if (_wcsicmp(argv[i],L"--uninstall")==0) uninstall=TRUE;
        }
        LocalFree(argv);
    }
    if (selfTest) {
        if (!ValidatePackage()) return 41;
        return 0;
    }
    if (uninstall) {
        int answer = MessageBoxW(NULL,L"Remove Sutram from this computer?\r\n\r\nUser-created files inside the Sutram folder will be preserved.",L"Uninstall Sutram",MB_YESNO|MB_ICONQUESTION);
        int rc;
        if (answer != IDYES) return 0;
        rc = InvokeUninstall();
        if (rc == 0) {
            WCHAR selfPath[4096], installDir[4096], *slash;
            MessageBoxW(NULL,L"Sutram was uninstalled successfully. User-created files, if any, were preserved.",L"Uninstall Sutram",MB_OK|MB_ICONINFORMATION);
            if (GetModuleFileNameW(NULL,selfPath,4096)) {
                wcscpy(installDir,selfPath); slash=wcsrchr(installDir,L'\\');
                if (slash) { *slash=0; ScheduleSelfDelete(selfPath,installDir); }
            }
        } else MessageBoxW(NULL,L"Sutram uninstall encountered an error. Check the temporary uninstall log for details.",L"Uninstall Sutram",MB_OK|MB_ICONERROR);
        return rc;
    }
    if (!ValidatePackage()) {
        MessageBoxW(NULL,L"This setup package is incomplete or corrupted.",APP_NAME,MB_OK|MB_ICONERROR);
        return 42;
    }
    CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
    icc.dwSize = sizeof(icc); icc.dwICC = ICC_PROGRESS_CLASS | ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icc);
    ZeroMemory(&wc,sizeof(wc));
    wc.cbSize=sizeof(wc); wc.lpfnWndProc=WndProc; wc.hInstance=hInstance;
    wc.hIcon=LoadIconW(NULL,IDI_APPLICATION); wc.hIconSm=wc.hIcon;
    wc.hCursor=LoadCursorW(NULL,IDC_ARROW); wc.hbrBackground=(HBRUSH)(COLOR_WINDOW+1);
    wc.lpszClassName=L"SutramSetupWindow";
    if (!RegisterClassExW(&wc)) return 43;
    g_hwnd = CreateWindowExW(0,wc.lpszClassName,APP_NAME,WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX,
        CW_USEDEFAULT,CW_USEDEFAULT,650,420,NULL,NULL,hInstance,NULL);
    if (!g_hwnd) return 44;
    ShowWindow(g_hwnd,SW_SHOW); UpdateWindow(g_hwnd);
    while (GetMessageW(&msg,NULL,0,0)>0) { TranslateMessage(&msg); DispatchMessageW(&msg); }
    CoUninitialize();
    return 0;
}
