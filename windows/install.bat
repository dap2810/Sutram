@echo off
REM ============================================================
REM  Sutram for Windows — Direct Installer
REM ============================================================
REM  No NSIS needed - this batch file does everything:
REM    1. Installs to %LOCALAPPDATA%\Sutram (no admin needed)
REM    2. Adds to PATH
REM    3. Associates .sm files with the Sutram icon
REM    4. Creates Start Menu shortcuts
REM
REM  Double-click this file to install!
REM ============================================================

setlocal enabledelayedexpansion
title Sutram Installer

echo.
echo  ================================================
echo         Sutram — the complete thread
echo         Sanskrit-keyword Programming Language
echo  ================================================
echo.
echo  This will install Sutram to:
echo    %LOCALAPPDATA%\Sutram
echo.
echo  Features:
echo    - Adds 'sutram' to your PATH
echo    - .sm files get the Sutram icon
echo    - Start Menu shortcuts included
echo    - 6 books (English, Hindi, Sanskrit, Telugu, Tamil, Gujarati)
echo.
echo  Native Windows build. No WSL, no admin rights, no toolchain.
echo.
echo  Press any key to install, or Ctrl+C to cancel...
pause >nul

REM --- Install directory ---
set "INSTALL_DIR=%LOCALAPPDATA%\Sutram"
set "SCRIPT_DIR=%~dp0"

echo.
echo  [1/7] Creating directories...
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\bin" 2>nul
mkdir "%INSTALL_DIR%\lang" 2>nul
mkdir "%INSTALL_DIR%\examples" 2>nul
mkdir "%INSTALL_DIR%\lib" 2>nul
mkdir "%INSTALL_DIR%\docs" 2>nul
mkdir "%INSTALL_DIR%\icons" 2>nul
mkdir "%INSTALL_DIR%\src" 2>nul
echo        Done.

echo  [2/7] Copying compiler...
if exist "%SCRIPT_DIR%win\sutram.exe" (
    copy /Y "%SCRIPT_DIR%win\sutram.exe" "%INSTALL_DIR%\bin\" >nul
) else (
    if exist "%SCRIPT_DIR%sutram.exe" (
        copy /Y "%SCRIPT_DIR%sutram.exe" "%INSTALL_DIR%\bin\" >nul
    ) else (
        echo        WARNING: sutram.exe (native Windows build) not found.
    )
)
if exist "%SCRIPT_DIR%windows\sutram.cmd" (
    copy /Y "%SCRIPT_DIR%windows\sutram.cmd" "%INSTALL_DIR%\bin\" >nul
) else (
    if exist "%SCRIPT_DIR%bin\sutram.cmd" (
        copy /Y "%SCRIPT_DIR%bin\sutram.cmd" "%INSTALL_DIR%\bin\" >nul
    )
)
if exist "%SCRIPT_DIR%src\sutram_compiler.asm" (
    copy /Y "%SCRIPT_DIR%src\sutram_compiler.asm" "%INSTALL_DIR%\src\" >nul
)
echo        Done.

echo  [3/7] Installing language packs...
if exist "%SCRIPT_DIR%lang" (
    copy /Y "%SCRIPT_DIR%lang\*.lang" "%INSTALL_DIR%\lang\" >nul
    echo        10 language packs installed
) else (
    echo        No language packs found
)

echo  [4/7] Installing icon and file association...
if exist "%SCRIPT_DIR%icons\sutram.ico" (
    copy /Y "%SCRIPT_DIR%icons\sutram.ico" "%INSTALL_DIR%\icons\" >nul
    copy /Y "%SCRIPT_DIR%icons\sutram-icon.svg" "%INSTALL_DIR%\icons\" >nul
    copy /Y "%SCRIPT_DIR%icons\sutram-256.png" "%INSTALL_DIR%\icons\" >nul

    REM --- Associate .sm with Sutram icon ---
    REM This uses the registry to set the default icon for .sm files
    reg add "HKCU\Software\Classes\.sm" /ve /d "Sutram.SourceFile" /f >nul
    reg add "HKCU\Software\Classes\Sutram.SourceFile" /ve /d "Sutram Source File" /f >nul
    reg add "HKCU\Software\Classes\Sutram.SourceFile\DefaultIcon" /ve /d "%INSTALL_DIR%\icons\sutram.ico" /f >nul
    reg add "HKCU\Software\Classes\Sutram.SourceFile\shell\open\command" /ve /d "\"%INSTALL_DIR%\bin\sutram.cmd\" \"compile\" \"%%1\"" /f >nul
    echo        .sm files now have the Sutram icon
) else (
    echo        Icon files not found
)

echo  [5/7] Copying examples and libraries...
if exist "%SCRIPT_DIR%examples" (
    copy /Y "%SCRIPT_DIR%examples\*.sm" "%INSTALL_DIR%\examples\" >nul
    echo        Examples installed
)
if exist "%SCRIPT_DIR%lib" (
    copy /Y "%SCRIPT_DIR%lib\*.smlib" "%INSTALL_DIR%\lib\" >nul
    echo        Libraries installed
)

echo  [6/7] Copying books...
if exist "%SCRIPT_DIR%docs" (
    copy /Y "%SCRIPT_DIR%docs\*.html" "%INSTALL_DIR%\docs\" >nul
    echo        6 books installed
) else (
    if exist "%SCRIPT_DIR%books" (
        copy /Y "%SCRIPT_DIR%books\*.html" "%INSTALL_DIR%\docs\" >nul
        echo        Books installed
    )
)

echo  [7/7] Adding to PATH...
REM --- Add to user PATH (safe, doesn't need admin) ---
REM First, read current PATH
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"

REM --- Check if already in PATH ---
echo "%USER_PATH%" | find /i "%INSTALL_DIR%\bin" >nul
if errorlevel 1 (
    REM --- Not in PATH, add it ---
    REM Use PowerShell to safely modify the PATH (avoids truncation issues)
    powershell -Command ^
        "$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User');" ^
        "if ($currentPath -notlike '*Sutram\bin*') { ^
            [Environment]::SetEnvironmentVariable('Path', ^
                \"$currentPath;%INSTALL_DIR%\bin\", 'User'); ^
            Write-Host '        PATH updated'; ^
        } else { ^
            Write-Host '        Already in PATH'; ^
        }"
) else (
    echo        Already in PATH
)

REM --- Create Start Menu shortcuts ---
echo.
echo  Creating Start Menu shortcuts...
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Sutram"
mkdir "%STARTMENU_DIR%" 2>nul

if exist "%INSTALL_DIR%\icons\sutram.ico" (
    powershell -Command ^
        "$ws = New-Object -ComObject WScript.Shell;" ^
        "$lnk = $ws.CreateShortcut('%STARTMENU_DIR%\Sutram Shell.lnk');" ^
        "$lnk.TargetPath = '%INSTALL_DIR%\bin\sutram.cmd';" ^
        "$lnk.Arguments = '-i';" ^
        "$lnk.IconLocation = '%INSTALL_DIR%\icons\sutram.ico';" ^
        "$lnk.Save();" ^
        "$lnk2 = $ws.CreateShortcut('%STARTMENU_DIR%\Sutram Book.lnk');" ^
        "$lnk2.TargetPath = '%INSTALL_DIR%\docs\sutram-book-english.html';" ^
        "$lnk2.Save();" ^
        "Write-Host '        Shortcuts created'"
    echo        Start Menu shortcuts created
) else (
    echo        Skipping shortcuts (no icon)
)

REM --- Done ---
echo.
echo  ================================================
echo         Installation Complete!
echo  ================================================
echo.
echo  Sutram is installed at:
echo    %INSTALL_DIR%
echo.
echo  To use it, open a NEW Command Prompt or PowerShell:
echo    sutram --version
echo    sutram -i
echo.
echo  Try compiling:
echo    sutram %INSTALL_DIR%\examples\01_hello.sm %%TEMP%%\hello.bin
echo.
echo  To set your language (Hindi, Tamil, Telugu, etc.):
echo    set SUTRAM_LANG=hindi
echo    (add this to your PowerShell profile for permanent)
echo.
echo  Press any key to exit...
pause >nul
