@echo off
REM ============================================================
REM  Sutram for Windows - native installer
REM ============================================================
REM  Per-user, least privilege. No admin, no UAC, no WSL.
REM    * installs to %LOCALAPPDATA%\Programs\Sutram
REM    * adds that folder to YOUR PATH (HKCU only)
REM    * associates .sm files with the Sutram icon (HKCU only)
REM    * creates a Start Menu shortcut
REM  Double-click to install. Double-click uninstall.bat to remove.
REM ============================================================
setlocal enabledelayedexpansion
title Sutram Installer
set "SRC=%~dp0"
set "DEST=%LOCALAPPDATA%\Programs\Sutram"

echo.
echo   Sutram - the complete thread
echo   Sanskrit-keyword language, native x86-64, no runtime
echo.
echo   Installing to: %DEST%
echo   No administrator rights needed. Press a key to continue...
pause >nul

echo [1/6] Creating folders...
mkdir "%DEST%" 2>nul
mkdir "%DEST%\bin" 2>nul
mkdir "%DEST%\examples" 2>nul
mkdir "%DEST%\lang" 2>nul
mkdir "%DEST%\lib" 2>nul
mkdir "%DEST%\docs" 2>nul
mkdir "%DEST%\icons" 2>nul

echo [2/6] Installing the compiler...
if not exist "%SRC%sutram.exe" (
    echo   ERROR: sutram.exe not found beside this installer.
    pause
    exit /b 1
)
copy /Y "%SRC%sutram.exe" "%DEST%\bin\" >nul
copy /Y "%SRC%sutram.cmd" "%DEST%\bin\" >nul
echo   sutram.exe installed

echo [3/6] Installing language packs...
if exist "%SRC%lang" copy /Y "%SRC%lang\*.lang" "%DEST%\lang\" >nul
echo   done

echo [4/6] Installing examples and libraries...
if exist "%SRC%examples" copy /Y "%SRC%examples\*.sm" "%DEST%\examples\" >nul
if exist "%SRC%lib" copy /Y "%SRC%lib\*.smlib" "%DEST%\lib\" >nul
echo   done

echo [5/6] Installing books and docs...
if exist "%SRC%docs" copy /Y "%SRC%docs\*.html" "%DEST%\docs\" >nul
if exist "%SRC%icons" copy /Y "%SRC%icons\*" "%DEST%\icons\" >nul
echo   done

echo [6/6] PATH, file association, shortcut...
powershell -NoProfile -Command "$p=[Environment]::GetEnvironmentVariable('Path','User'); if ($p -notlike '*Programs\Sutram\bin*') { [Environment]::SetEnvironmentVariable('Path', $p + ';%DEST%\bin', 'User'); Write-Host '  PATH updated' } else { Write-Host '  already in PATH' }"

if exist "%DEST%\icons\sutram.ico" (
    reg add "HKCU\Software\Classes\.sm" /ve /d "Sutram.SourceFile" /f >nul 2>&1
    reg add "HKCU\Software\Classes\Sutram.SourceFile" /ve /d "Sutram Source File" /f >nul 2>&1
    reg add "HKCU\Software\Classes\Sutram.SourceFile\DefaultIcon" /ve /d "%DEST%\icons\sutram.ico" /f >nul 2>&1
    echo   .sm files associated
)
powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $sm=Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Sutram'; New-Item -ItemType Directory -Force -Path $sm | Out-Null; $l=$ws.CreateShortcut((Join-Path $sm 'Sutram Shell.lnk')); $l.TargetPath='%DEST%\bin\sutram.cmd'; $l.Arguments='-i'; if (Test-Path '%DEST%\icons\sutram.ico') { $l.IconLocation='%DEST%\icons\sutram.ico' }; $l.Save(); Write-Host '  shortcut created'"

echo.
echo   Done. Open a NEW Command Prompt and type:
echo       sutram --version
echo       sutram -i
echo       sutram "%DEST%\examples\01_hello.sm" hello.exe
echo.
pause
