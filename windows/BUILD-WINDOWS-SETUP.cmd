@echo off
setlocal
cd /d "%~dp0"
echo Sutram Windows native release build
echo ==================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build-windows-setup.ps1"
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
  echo BUILD FAILED with exit code %RC%.
  echo Copy the complete output if support is needed.
) else (
  echo BUILD PASSED.
  echo Installer: Sutram-Setup.exe
)
echo.
pause
exit /b %RC%
