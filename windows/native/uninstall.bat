@echo off
setlocal
set "DEST=%LOCALAPPDATA%\Programs\Sutram"
echo Removing Sutram from %DEST% ...
powershell -NoProfile -Command "$p=[Environment]::GetEnvironmentVariable('Path','User'); $n=($p -split ';' | Where-Object { $_ -notlike '*Programs\Sutram\bin*' }) -join ';'; [Environment]::SetEnvironmentVariable('Path',$n,'User')" >nul 2>&1
reg delete "HKCU\Software\Classes\.sm" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Sutram.SourceFile" /f >nul 2>&1
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Sutram\Sutram Shell.lnk" >nul 2>&1
rmdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Sutram" >nul 2>&1
rmdir /S /Q "%DEST%" >nul 2>&1
echo Uninstalled. Your PATH and registry entries were removed.
pause
