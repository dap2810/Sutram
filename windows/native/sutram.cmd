@echo off
REM ============================================================
REM  Sutram for Windows - native wrapper
REM ============================================================
REM  Calls sutram.exe directly. No WSL, no Linux, no toolchain.
REM
REM    sutram input.sm output.exe      compile to a Windows program
REM    sutram input.sm output          compile to a Linux binary
REM    sutram -i                       interactive shell
REM    sutram --version                version
REM    sutram --lang hindi in.sm out   with a language pack
REM
REM  Set SUTRAM_LANG=hindi (or telugu, tamil, ...) for a default language.
REM ============================================================
setlocal enabledelayedexpansion
set "SUTRAM_DIR=%~dp0"
set "EXE=%SUTRAM_DIR%sutram.exe"

if not exist "%EXE%" (
    echo Error: sutram.exe not found next to this script.
    echo Expected: %EXE%
    exit /b 1
)

set "LANG_ARGS="
if defined SUTRAM_LANG set "LANG_ARGS=--lang !SUTRAM_LANG!"

if "%~1"=="" (
    "%EXE%" %LANG_ARGS%
    exit /b %errorlevel%
)
if "%~1"=="-i" (
    "%EXE%" -i
    exit /b %errorlevel%
)
if "%~1"=="--shell" (
    "%EXE%" -i
    exit /b %errorlevel%
)

"%EXE%" %LANG_ARGS% %*
exit /b %errorlevel%
