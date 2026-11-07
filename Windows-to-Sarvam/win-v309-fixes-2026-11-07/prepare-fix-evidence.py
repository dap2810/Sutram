from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[2]
old=root/'Windows-to-Sarvam/win-v309-2026-11-07'
new=root/'Windows-to-Sarvam/win-v309-fixes-2026-11-07'
new.mkdir(exist_ok=True)
(root/'build/native-v309-fix').mkdir(exist_ok=True)
(new/'.gitattributes').write_text('* -text\n',encoding='utf8')
for name in ['ui-helper.ps1','preserve.ps1','run-install.ps1','recovery-tests.ps1','identity.py','verify-saved.ps1']:
    text=(old/name).read_text(encoding='utf-8-sig')
    text=text.replace('Sutram-v309-','Sutram-v309-fix-')
    text=text.replace('build/windows-v309-2026-11-07','build/native-v309-fix').replace('build\\windows-v309-2026-11-07','build\\native-v309-fix')
    if name=='run-install.ps1':
        text=text.replace("if((Get-FileHash -LiteralPath $setup).Hash -ne '9D046B4E1B3D95222523E78304E48CB5BC10A69F951B33822A2673F0DC3BB533')", "if((Get-FileHash -LiteralPath $setup).Hash -ne (Get-Content (Join-Path $OutDir 'candidate.json') -Raw|ConvertFrom-Json).setup_sha256)")
        text=text.replace('[void][SutramIde]::Send($h,0xF5,0,0,3000);Start-Sleep', "if(-not [SutramIde]::PostMessageW($h,0xF5,[IntPtr]::Zero,[IntPtr]::Zero)){throw 'Button click could not be posted'};Start-Sleep")
        text=text.replace('[void][SutramIde]::Send([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,0,0,3000);break', "if(-not [SutramIde]::PostMessageW([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,[IntPtr]::Zero,[IntPtr]::Zero)){throw 'Dialog acknowledgement could not be posted'};$r.dialog_closed=$wizard.WaitForExit(5000);break")
    elif name=='ui-helper.ps1':
        text=text.replace('[DllImport("user32.dll")] public static extern bool IsWindowVisible', '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int command);\n    [DllImport("user32.dll")] public static extern bool IsWindowVisible')
        text=text.replace("    $bmp = Join-Path $OutDir", "    [void][SutramIde]::ShowWindow($H,9)\n    [void][SutramIde]::SetForegroundWindow($H)\n    Start-Sleep -Milliseconds 500\n    $rect=[SutramIde+RECT]::new()\n    if(-not [SutramIde]::GetWindowRect($H,[ref]$rect) -or ($rect.Bottom-$rect.Top) -lt 100){throw 'Capture window has not been restored'}\n    $bmp = Join-Path $OutDir")
    elif name=='verify-saved.ps1':
        text=text.replace("'initial-observer-error',",'')
    elif name=='recovery-tests.ps1':
        text=text.replace("if($d1.status -ne 'INTERRUPTED' -or $d1.payload_files_present -ne 0)","if($d1.status -ne 'INTERRUPTED' -or $d1.payload_files_present -ne 0 -or $d1.engine_age_seconds -ge 1)")
        text=text.replace("MustFinish 'd2-retry'", "MustFinish 'd2-retry'\n        $log=[IO.File]::ReadAllText((Join-Path $out 'd2-retry-engine.log'))\n        if([regex]::Matches($log,'Already installed ').Count -ne 657 -or [regex]::Matches($log,'\\] START ').Count -ne 0){throw 'Late recovery recopied payload files'}")
        text=text.replace("    $result|ConvertTo-Json -Depth 4", "    if(-not $result.edit_preserved -or $result.child_exit -ne 1 -or $result.retry_status -ne 'ERROR_DIALOG'){throw 'Edited-file protection or observer failed'}\n    $result|ConvertTo-Json -Depth 4")
    (new/name).write_text(text,encoding='utf8',newline='\n')
print(new)
