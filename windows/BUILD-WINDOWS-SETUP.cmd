@echo off
setlocal
cd /d "%~dp0"
echo Sutram standard-user native build candidate
powershell.exe -NoProfile -NonInteractive -File "%~dp0build-windows-setup.ps1" %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" echo BUILD REFUSED OR FAILED. Preserve the complete log.
if "%RC%"=="0" echo Candidate produced; Windows GUI and install/uninstall acceptance still required.
exit /b %RC%
