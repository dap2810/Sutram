#!/bin/sh
# usage: runwine.sh <outname> [extra args]
R6=<scratch>/r6; S=${R6%/r6}/r4; N=$1; shift
cp /home/claude/sutram/tools/accept-windows.ps1 $R6/${ROOTDIR:-acceptroot}/tools/
export POWERSHELL_TELEMETRY_OPTOUT=1 DISPLAY=:99 WINEDEBUG=-all WINEPREFIX=$S/wineprefix
/usr/lib/wine/wineserver -k 2>/dev/null; sleep 1; rm -rf $R6/$N
timeout 1200 script -q -c "/usr/lib/wine/wine64 powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'Z:$R6/${ROOTDIR:-acceptroot}/tools/accept-windows.ps1' -OutDir 'Z:$R6/$N' $*" $R6/$N.typescript > /dev/null 2>&1
tr -d '\r' < $R6/$N.typescript | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g; s/\x1b\][^\x07]*\x07//g' | grep -v '^\s*$' | grep -v "Read access denied" > $R6/$N.console.txt
