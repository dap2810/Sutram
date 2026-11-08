$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$r=Get-Content -LiteralPath (Join-Path $OutDir 'initial-install.json') -Raw|ConvertFrom-Json
$p=Get-Process -Id $r.pid;if($p.StartTime.ToString('o') -ne $r.process_started -or $r.phase -ne 'licence'){throw 'Not the paused licence page'}
$main=[IntPtr]$r.handle;$edit=[SutramIde]::GetDlgItem($main,2012)
Add-Type -TypeDefinition @'
using System;using System.Runtime.InteropServices;
public class LicenceFont {
 [DllImport("gdi32.dll",CharSet=CharSet.Unicode)] static extern int GetObjectW(IntPtr h,int n,byte[] data);
 public static string Read(IntPtr h){byte[] b=new byte[92];if(GetObjectW(h,b.Length,b)==0)return "unavailable";return System.Text.Encoding.Unicode.GetString(b,28,64).TrimEnd('\0')+"; logical height "+BitConverter.ToInt32(b,0);}
}
'@
$o=[ordered]@{time=[DateTime]::Now.ToString('o');font=[LicenceFont]::Read([IntPtr][SutramIde]::Send($edit,0x31,0,0,3000));visible_text=[AcceptanceWindow]::VisibleTexts($main);screens=@()}
foreach($line in @(7,14,27,33,39)){
 [void][SutramIde]::Send($edit,0xB6,0,-10000,3000);[void][SutramIde]::Send($edit,0xB6,0,$line,3000)
 Start-Sleep -Milliseconds 200;Foreground $main
 $o.screens+=@{first_visible_line=[SutramIde]::Send($edit,0xCE,0,0,3000);file=(Shot $main ('licence-line-'+$line))}
}
$o.capture_warnings=@($script:captureWarnings)
[IO.File]::WriteAllText((Join-Path $OutDir 'licence-details.json'),($o|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
$o|ConvertTo-Json -Depth 4
