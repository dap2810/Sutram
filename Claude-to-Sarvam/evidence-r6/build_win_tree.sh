#!/bin/sh
# Scratch-only: reproduce windows/native-installer/build-installer.ps1 + build-gui.ps1 on Linux so the
# acceptance script has a real Sutram-Setup.exe to drive under Wine. Not part of the delivery.
set -e
REPO=/home/claude/sutram; R6=$(dirname "$0"); T=$R6/acceptroot; PW=/tmp/claude-0/pwsh/pwsh
rm -rf $T; mkdir -p $T
(cd $REPO && git archive HEAD) | tar -x -C $T
cd $T; mkdir -p build/windows win
# compiler
nasm -f win64 -DWINDOWS=1 -I. src/r68_compiler_entry.asm -o build/windows/c.obj
ld -mi386pep --subsystem console --entry=_start -o win/sutram.exe build/windows/c.obj
# icon include (the real PowerShell function)
$PW -NoProfile -c ". ./windows/build-common.ps1 2>\$null; Write-IconResourceInclude 'icons/sutram.ico' 'build/windows/r73_icon.inc' 'icons/sutram.ico'" || true
test -s build/windows/r73_icon.inc
for n in r67_gui_entry r66_indic_clusters r67_cluster_count; do nasm -f win64 -dR73_ICON -I./ -Ibuild/windows/ windows/gui/$n.asm -o build/windows/$n.obj; done
x86_64-w64-mingw32-ld -mi386pep --subsystem windows --entry=_start -o sutram-ide-gui.exe build/windows/r67_gui_entry.obj build/windows/r66_indic_clusters.obj build/windows/r67_cluster_count.obj -L/usr/x86_64-w64-mingw32/lib -lkernel32 -lshell32 -luser32 -lgdi32
# payload, as build-installer.ps1 lines 4-27
W=build/windows/setup; S=$W/payload; rm -rf $W; mkdir -p $S/bin $S/win $S/assets
cp win/sutram.exe $S/bin/sutram.exe; cp win/sutram.exe $S/win/sutram.exe; cp sutram-ide-gui.exe $S/; cp icons/sutram.ico $S/assets/; cp LICENSE.txt README.md $S/
for f in lang lib examples docs; do cp -r $f $S/; done
for d in bin win; do cp -r lang lib $S/$d/; done
python3 - "$S" <<'PY'
import hashlib,os,sys
s=sys.argv[1]; rows=[]
for dp,dn,fn in os.walk(s):
    for f in fn:
        p=os.path.join(dp,f); rel=os.path.relpath(p,s).replace('/','\\')
        rows.append((p.lower(),hashlib.sha256(open(p,'rb').read()).hexdigest()+' *'+rel))
rows.sort(); open(os.path.join(s,'payload.manifest.sha256'),'w',newline='\r\n').write('\n'.join(r for _,r in rows)+'\n')
PY
(cd $S && python3 -c "
import zipfile,os
z=zipfile.ZipFile('../payload.zip','w',zipfile.ZIP_DEFLATED)
for dp,dn,fn in os.walk('.'):
    for f in fn:
        p=os.path.join(dp,f); z.write(p,os.path.relpath(p,'.'))
z.close()")
cp windows/native-installer/install-core.ps1 windows/native-installer/uninstall-core.ps1 LICENSE.txt $W/
python3 - "$W" <<'PY'
import hashlib,sys,os
w=sys.argv[1]; L=['section .data']
for f,n in [('payload.zip','payload'),('install-core.ps1','install'),('uninstall-core.ps1','uninst'),('LICENSE.txt','license')]:
    h=hashlib.sha256(open(os.path.join(w,f),'rb').read()).hexdigest().upper()
    L.append('hash_'+n+': db '+','.join('0x'+h[i:i+2] for i in range(0,64,2)))
L.append('embedded_hash_table:')
for n in ['payload','install','uninst','license']: L.append(f'dq blob_{n},blob_{n}_end-blob_{n},hash_{n}')
L.append('dq 0,0,0'); open(os.path.join(w,'embedded_hashes.inc'),'w').write('\n'.join(L)+'\n')
PY
cp build/windows/r73_icon.inc $W/
nasm -f win64 -dR73_ICON -I$W/ -I./ windows/native-installer/sutram_wizard.asm -o $W/wizard.obj
x86_64-w64-mingw32-ld -mi386pep --subsystem windows --entry=_start -o Sutram-Setup.exe $W/wizard.obj -L/usr/x86_64-w64-mingw32/lib -lkernel32 -lbcrypt
sha256sum Sutram-Setup.exe | awk '{print $1" *Sutram-Setup.exe"}' > Sutram-Setup.sha256
ls -la Sutram-Setup.exe sutram-ide-gui.exe win/sutram.exe $W/payload.zip
