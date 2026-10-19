#!/bin/sh
S=<scratch>/r4
export DISPLAY=:99 WINEDEBUG=-all WINEPREFIX=$S/wineprefix
/usr/lib/wine/wineserver -k 2>/dev/null; sleep 1
U=$S/wineprefix/drive_c/users/root
rm -rf "$U/AppData/Local/Programs/Sutram" "$U/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Sutram" "$U/Desktop/Sutram IDE.lnk" $U/Temp/STM*
for k in 'HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram' 'HKCU\Software\Classes\Sutram.Source' 'HKCU\Software\Classes\.sm'; do /usr/lib/wine/wine64 reg delete "$k" /f >/dev/null 2>&1; done
/usr/lib/wine/wine64 reg delete 'HKCU\Environment' /v Path /f >/dev/null 2>&1
/usr/lib/wine/wineserver -w
echo cleaned
