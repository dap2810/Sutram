# Environment audit: before and after old-install cleanup

The old v1.4.0 and canonical v303 bin directories were both in the **user PATH**.
The old entry appeared earlier. Neither was in the machine PATH. Fresh command
processes reconstructed their PATH from those persisted values rather than
inheriting the agent's original PATH. The machine PATH was unchanged; the only
final user PATH difference is removal of the old `AppData\Local\Sutram\bin` entry.

## Cleanup performed

1. Verified the exact resolved old folder, its compiler SHA-256, and absence of
   reparse points. Used its own `uninstall.exe /uninstall` and confirmed removal.
2. The uninstaller exited 0 and displayed success, but left its own executable
   and the old user PATH entry. The initial cleanup check recorded that failure.
3. Inspected the remainder: only the expected `uninstall.exe` remained. Verified
   its hash, deleted that file, then removed the empty directory using literal
   paths. No recursive deletion or other application directory was used.
4. Removed only the exact old bin entry from the user PATH. The remaining
   canonical compiler's SHA-256 stayed
   `4c05d5cbad99b32be1a38459f1b4b794e00f8b34f89a662ef1ca363c92ec1603`.
5. A new cmd process finds exactly one compiler and reports v303, as expected
   because v305 was not installed. Part B uses the explicit repository v305 binary.
6. The final exact before/after comparison detected the unrelated first PATH
   entry, `C:\Users\dmech\AppData\Local\Programs\OpenAI\Codex\bin`, missing
   after the old uninstaller and cleanup. Preserved that intermediate record,
   then restored only this entry to its original first position, with a guard
   against concurrent PATH changes. Repeated the fresh-shell audit and verified
   that the final PATH equals the original with only the old Sutram entry removed.

**Installer-state caveat:** the old uninstaller removed the shared
`HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram` key, which
previously pointed to the canonical installation. The old folder is absent and
the remaining compiler works, but this does not repair or accept the earlier
incomplete v303 installation. A later installer must recreate its registration.
No HKLM writes, new installer execution, or PATH redirection to repository builds
was performed. The agent's already-running parent retains its inherited old PATH;
the after-check deliberately used fresh persisted values.

Raw records: [environment-before.json](environment-before.json),
[environment-after.json](environment-after.json), [cleanup.json](cleanup.json),
and [cleanup-finish.json](cleanup-finish.json). The intermediate audit and repair
are [environment-after-uninstaller.json](environment-after-uninstaller.json) and
[path-restoration.json](path-restoration.json).

## Before

Captured: `2026-11-06T18:51:49.3120392-05:00`.

`where sutram` — exit 0:

```text
C:\Users\dmech\AppData\Local\Sutram\bin\sutram.exe
C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe
```

`sutram --version` — exit 0:

```text
Sutram 1.4.0
```

`echo %PATH%` — exit 0:

```text
C:\Python314\Scripts\;C:\Python314\;C:\Program Files\Lapce\;C:\Program Files\Python313\Scripts\;C:\Program Files\Python313\;c:\windows\system32;c:\windows;c:\windows\system32\wbem;c:\windows\system32\windowspowershell\v1.0\;c:\windows\system32\openssh\;c:\program files\microsoft sql server\client sdk\odbc\110\tools\binn\;c:\program files (x86)\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\dts\binn\;c:\tdm-gcc-64\bin;c:\program files\dotnet\;c:\program files\nvidia corporation\nvidia app\nvdlisr;c:\program files (x86)\windows kits\10\windows performance toolkit\;c:\program files\crucial\crucial storage executive;c:\program files\microsoft sql server\150\tools\binn\;c:\program files\microsoft sql server\client sdk\odbc\170\tools\binn\;c:\mingw\bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files (x86)\Common Files\Acronis\SnapAPI\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile64\;C:\Program Files (x86)\Common Files\Acronis\FileProtector\;C:\Program Files (x86)\Common Files\Acronis\FileProtector64\;C:\msys64\mingw64\bin;C:\libs\libharu\include;C:\libs\libharu\build\src;C:\libs\libharu\build\include;C:\TDM-GCC-64\bin;C:\Users\dmech\AppData\Local\Programs\Swift\Toolchains\6.0.2+Asserts\usr\bin\swift.exe;C:\Webdrivers;C:\Program Files\Mozilla Firefox;C:\Program Files\Go\bin;C:\Program Files\mingw64\bin;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\Program Files\Git\cmd;C:\Program Files\nodejs\;C:\ProgramData\chocolatey\bin;C:\Program Files\WSL\;C:\Program Files\Kraken Desktop\;C:\Users\dmech\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\dmech\.cargo\bin;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;\msys64\mingw64\bin;C:\msys64;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;C:\Program Files\Mozilla Firefox;C:\Users\dmech\go\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\dmech\AppData\Roaming\Python\Python311\Scripts;C:\Users\dmech\AppData\Roaming\Python\Python313\Scripts;C:\Users\dmech\AppData\Local\Python\bin;C:\Users\dmech\miniconda3\Scripts;C:\Users\dmech\AppData\Local\Programs\MovieBox-Tui\bin;C:\Users\dmech\AppData\Local\Programs\Zed\bin;C:\Users\dmech\AppData\Roaming\npm;C:\Users\dmech\AppData\Local\Programs\Ollama;C:\Users\dmech\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Users\dmech\AppData\Local\Sutram\bin;C:\Users\dmech\.local\bin;C:\Users\dmech\AppData\Local\Programs\Sutram\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin\copilot-shim
```

`reg query HKLM environment /v Path` — exit 0:

```text

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment
    Path    REG_EXPAND_SZ    C:\Python314\Scripts\;C:\Python314\;C:\Program Files\Lapce\;C:\Program Files\Python313\Scripts\;C:\Program Files\Python313\;c:\windows\system32;c:\windows;c:\windows\system32\wbem;c:\windows\system32\windowspowershell\v1.0\;c:\windows\system32\openssh\;c:\program files\microsoft sql server\client sdk\odbc\110\tools\binn\;c:\program files (x86)\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\dts\binn\;c:\tdm-gcc-64\bin;c:\program files\dotnet\;c:\program files\nvidia corporation\nvidia app\nvdlisr;c:\program files (x86)\windows kits\10\windows performance toolkit\;c:\program files\crucial\crucial storage executive;c:\program files\microsoft sql server\150\tools\binn\;c:\program files\microsoft sql server\client sdk\odbc\170\tools\binn\;c:\mingw\bin;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\;%SYSTEMROOT%\System32\OpenSSH\;C:\Program Files (x86)\Common Files\Acronis\SnapAPI\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile64\;C:\Program Files (x86)\Common Files\Acronis\FileProtector\;C:\Program Files (x86)\Common Files\Acronis\FileProtector64\;C:\msys64\mingw64\bin;C:\libs\libharu\include;C:\libs\libharu\build\src;C:\libs\libharu\build\include;C:\TDM-GCC-64\bin;C:\Users\dmech\AppData\Local\Programs\Swift\Toolchains\6.0.2+Asserts\usr\bin\swift.exe;C:\Webdrivers;C:\Program Files\Mozilla Firefox;C:\Program Files\Go\bin;C:\Program Files\mingw64\bin;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\Program Files\Git\cmd;C:\Program Files\nodejs\;C:\ProgramData\chocolatey\bin;C:\Program Files\WSL\;C:\Program Files\Kraken Desktop\
```

`reg query HKCU environment /v Path` — exit 0:

```text

HKEY_CURRENT_USER\Environment
    Path    REG_EXPAND_SZ    C:\Users\dmech\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\dmech\.cargo\bin;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;\msys64\mingw64\bin;C:\msys64;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;C:\Program Files\Mozilla Firefox;C:\Users\dmech\go\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\dmech\AppData\Roaming\Python\Python311\Scripts;C:\Users\dmech\AppData\Roaming\Python\Python313\Scripts;C:\Users\dmech\AppData\Local\Python\bin;C:\Users\dmech\miniconda3\Scripts;C:\Users\dmech\AppData\Local\Programs\MovieBox-Tui\bin;C:\Users\dmech\AppData\Local\Programs\Zed\bin;C:\Users\dmech\AppData\Roaming\npm;C:\Users\dmech\AppData\Local\Programs\Ollama;C:\Users\dmech\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Users\dmech\AppData\Local\Sutram\bin;C:\Users\dmech\.local\bin;C:\Users\dmech\AppData\Local\Programs\Sutram\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin\copilot-shim
```

Every executable found:

- Path: `C:\Users\dmech\AppData\Local\Sutram\bin\sutram.exe`
- SHA-256: `441db69c3bcc04576bebfc4d87b1d43a53d3b1e7497ccaeb7a00bfac6e78c2a8`
- Absolute-path `--version`, exit 0:

```text
Sutram 1.4.0
```

- Path: `C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe`
- SHA-256: `4c05d5cbad99b32be1a38459f1b4b794e00f8b34f89a662ef1ca363c92ec1603`
- Absolute-path `--version`, exit 0:

```text
Sutram 1.0 (v303) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

## After

Captured: `2026-11-06T19:04:54.5442030-05:00`.

`where sutram` — exit 0:

```text
C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe
```

`sutram --version` — exit 0:

```text
Sutram 1.0 (v303) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

`echo %PATH%` — exit 0:

```text
C:\Python314\Scripts\;C:\Python314\;C:\Program Files\Lapce\;C:\Program Files\Python313\Scripts\;C:\Program Files\Python313\;c:\windows\system32;c:\windows;c:\windows\system32\wbem;c:\windows\system32\windowspowershell\v1.0\;c:\windows\system32\openssh\;c:\program files\microsoft sql server\client sdk\odbc\110\tools\binn\;c:\program files (x86)\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\dts\binn\;c:\tdm-gcc-64\bin;c:\program files\dotnet\;c:\program files\nvidia corporation\nvidia app\nvdlisr;c:\program files (x86)\windows kits\10\windows performance toolkit\;c:\program files\crucial\crucial storage executive;c:\program files\microsoft sql server\150\tools\binn\;c:\program files\microsoft sql server\client sdk\odbc\170\tools\binn\;c:\mingw\bin;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files (x86)\Common Files\Acronis\SnapAPI\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile64\;C:\Program Files (x86)\Common Files\Acronis\FileProtector\;C:\Program Files (x86)\Common Files\Acronis\FileProtector64\;C:\msys64\mingw64\bin;C:\libs\libharu\include;C:\libs\libharu\build\src;C:\libs\libharu\build\include;C:\TDM-GCC-64\bin;C:\Users\dmech\AppData\Local\Programs\Swift\Toolchains\6.0.2+Asserts\usr\bin\swift.exe;C:\Webdrivers;C:\Program Files\Mozilla Firefox;C:\Program Files\Go\bin;C:\Program Files\mingw64\bin;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\Program Files\Git\cmd;C:\Program Files\nodejs\;C:\ProgramData\chocolatey\bin;C:\Program Files\WSL\;C:\Program Files\Kraken Desktop\;C:\Users\dmech\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\dmech\.cargo\bin;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;\msys64\mingw64\bin;C:\msys64;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;C:\Program Files\Mozilla Firefox;C:\Users\dmech\go\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\dmech\AppData\Roaming\Python\Python311\Scripts;C:\Users\dmech\AppData\Roaming\Python\Python313\Scripts;C:\Users\dmech\AppData\Local\Python\bin;C:\Users\dmech\miniconda3\Scripts;C:\Users\dmech\AppData\Local\Programs\MovieBox-Tui\bin;C:\Users\dmech\AppData\Local\Programs\Zed\bin;C:\Users\dmech\AppData\Roaming\npm;C:\Users\dmech\AppData\Local\Programs\Ollama;C:\Users\dmech\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Users\dmech\.local\bin;C:\Users\dmech\AppData\Local\Programs\Sutram\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin\copilot-shim
```

`reg query HKLM environment /v Path` — exit 0:

```text

HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment
    Path    REG_EXPAND_SZ    C:\Python314\Scripts\;C:\Python314\;C:\Program Files\Lapce\;C:\Program Files\Python313\Scripts\;C:\Program Files\Python313\;c:\windows\system32;c:\windows;c:\windows\system32\wbem;c:\windows\system32\windowspowershell\v1.0\;c:\windows\system32\openssh\;c:\program files\microsoft sql server\client sdk\odbc\110\tools\binn\;c:\program files (x86)\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\tools\binn\;c:\program files\microsoft sql server\120\dts\binn\;c:\tdm-gcc-64\bin;c:\program files\dotnet\;c:\program files\nvidia corporation\nvidia app\nvdlisr;c:\program files (x86)\windows kits\10\windows performance toolkit\;c:\program files\crucial\crucial storage executive;c:\program files\microsoft sql server\150\tools\binn\;c:\program files\microsoft sql server\client sdk\odbc\170\tools\binn\;c:\mingw\bin;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\;%SYSTEMROOT%\System32\OpenSSH\;C:\Program Files (x86)\Common Files\Acronis\SnapAPI\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile\;C:\Program Files (x86)\Common Files\Acronis\VirtualFile64\;C:\Program Files (x86)\Common Files\Acronis\FileProtector\;C:\Program Files (x86)\Common Files\Acronis\FileProtector64\;C:\msys64\mingw64\bin;C:\libs\libharu\include;C:\libs\libharu\build\src;C:\libs\libharu\build\include;C:\TDM-GCC-64\bin;C:\Users\dmech\AppData\Local\Programs\Swift\Toolchains\6.0.2+Asserts\usr\bin\swift.exe;C:\Webdrivers;C:\Program Files\Mozilla Firefox;C:\Program Files\Go\bin;C:\Program Files\mingw64\bin;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\Program Files\Git\cmd;C:\Program Files\nodejs\;C:\ProgramData\chocolatey\bin;C:\Program Files\WSL\;C:\Program Files\Kraken Desktop\
```

`reg query HKCU environment /v Path` — exit 0:

```text

HKEY_CURRENT_USER\Environment
    Path    REG_SZ    C:\Users\dmech\AppData\Local\Programs\OpenAI\Codex\bin;C:\Users\dmech\.cargo\bin;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;\msys64\mingw64\bin;C:\msys64;C:\Users\dmech\AppData\Local\Microsoft\WindowsApps;C:\Program Files\Mozilla Firefox;C:\Users\dmech\go\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\dmech\AppData\Roaming\Python\Python311\Scripts;C:\Users\dmech\AppData\Roaming\Python\Python313\Scripts;C:\Users\dmech\AppData\Local\Python\bin;C:\Users\dmech\miniconda3\Scripts;C:\Users\dmech\AppData\Local\Programs\MovieBox-Tui\bin;C:\Users\dmech\AppData\Local\Programs\Zed\bin;C:\Users\dmech\AppData\Roaming\npm;C:\Users\dmech\AppData\Local\Programs\Ollama;C:\Users\dmech\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Users\dmech\.local\bin;C:\Users\dmech\AppData\Local\Programs\Sutram\bin;C:\Users\dmech\AppData\Local\Programs\Microsoft VS Code\bin\copilot-shim
```

Every executable found:

- Path: `C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe`
- SHA-256: `4c05d5cbad99b32be1a38459f1b4b794e00f8b34f89a662ef1ca363c92ec1603`
- Absolute-path `--version`, exit 0:

```text
Sutram 1.0 (v303) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

The full inherited agent-process PATH is retained separately in both JSON records.
