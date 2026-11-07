$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;$Root=Split-Path (Split-Path $OutDir -Parent) -Parent
. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram';$work=Join-Path $Root 'build\native-v311-acceptance\ide-probes'
if(Test-Path $work){throw 'Use a fresh IDE probe directory'};[void][IO.Directory]::CreateDirectory($work)
$utf8=[Text.UTF8Encoding]::new($false)
$syntax=Join-Path $work 'syntax.sm';$arith=Join-Path $work 'arithmetic.sm';$big=Join-Path $work 'too-large.sm'
[IO.File]::WriteAllText($syntax,"mukhya() {`n    vitti =`n}`n",$utf8)
[IO.File]::WriteAllText($arith,"mukhya() {`n    kosh k[1]`n    kosh_kship(k, 7)`n    likha(k[0:1] + 0)`n}`n",$utf8)
[IO.File]::WriteAllText($big,("# too large for the editor`n"*3000),$utf8)
foreach($f in @($syntax,$arith,$big)){Copy-Item -LiteralPath $f -Destination $OutDir}
$link=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram\Sutram IDE.lnk';$shortcut=(New-Object -ComObject WScript.Shell).CreateShortcut($link)
if($shortcut.TargetPath -ne (Join-Path $install 'sutram-ide-gui.exe')){throw 'Start Menu shortcut points elsewhere'}
$hello=Join-Path $install 'examples\01_hello.sm';$before=Get-FileHash -LiteralPath $hello
$existing=@(Get-Process -Name sutram-ide-gui -ErrorAction SilentlyContinue|ForEach-Object {$_.Id})
$r=[ordered]@{started=[DateTime]::Now.ToString('o');launch='Start Menu shortcut';shortcut=$link;shortcut_target=$shortcut.TargetPath;shortcut_working_directory=$shortcut.WorkingDirectory;scenarios=@();protected_hello_before=$before.Hash;large_file_bytes=(Get-Item $big).Length}
$ip=$null
function Save{[IO.File]::WriteAllText((Join-Path $OutDir 'ide.json'),($r|ConvertTo-Json -Depth 8),$utf8)}
function Snapshot([string]$Name){$s=[ordered]@{name=$Name;title=[SutramIde]::Text($main);editor=[SutramIde]::Text($editor);output=[SutramIde]::Text($output);status=[SutramIde]::Text($status);screenshot=(Shot $main $Name)};$r.scenarios+=,$s;Save;return $s}
function Open-File([string]$Path){
 [void][SutramIde]::PostMessageW($main,0x111,[IntPtr]2001,[IntPtr]::Zero)
 $dialog=Wait-Until {[SutramIde]::WindowsOf($ip.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)}|Select-Object -First 1} 5000
 if(-not $dialog){throw 'IDE Open dialog missing'}
 Foreground $dialog;[Windows.Forms.SendKeys]::SendWait('%n');[Windows.Forms.SendKeys]::SendWait('^a');[Windows.Forms.SendKeys]::SendWait('"'+$Path+'"');[Windows.Forms.SendKeys]::SendWait('{ENTER}');Start-Sleep -Milliseconds 600
}
function Run{[void][SutramIde]::Send($main,0x111,2010,0,30000);Start-Sleep -Milliseconds 300}
try{
 Start-Process -FilePath $link -WindowStyle Normal
 $ip=Wait-Until {Get-Process -Name sutram-ide-gui -ErrorAction SilentlyContinue|Where-Object {$_.Id -notin $existing -and $_.Path -eq $shortcut.TargetPath}|Select-Object -First 1} 10000
 if(-not $ip){throw 'Start Menu shortcut did not launch IDE'};[void]$ip.Handle;$r.pid=$ip.Id;$r.process_started=$ip.StartTime.ToString('o')
 $main=Wait-Until {[SutramIde]::WindowsOf($ip.Id,'SutramNativeGUIWindow')|Select-Object -First 1} 10000
 if(-not $main){throw 'IDE window missing'}
 [void][SutramIde]::ShowWindow($main,9);[void][AcceptanceWindow]::SetWindowPos($main,[IntPtr]::Zero,10,20,1200,800,0x0040)
 $editor=[SutramIde]::GetDlgItem($main,201);$output=[SutramIde]::GetDlgItem($main,203);$status=[SutramIde]::GetDlgItem($main,206);$list=[SutramIde]::GetDlgItem($main,205)
 $index=[SutramIde]::ListFind($list,'01_hello.sm');if($index -lt 0){throw 'Hello example not found'}
 [void][SutramIde]::Send($list,0x186,$index,0,3000);[void][SutramIde]::Send($main,0x111,((2 -shl 16) -bor 205),$list.ToInt64(),10000)
 Run;$b1=Snapshot 'B1-hello';$r.b1_pass=$b1.output.Contains('Namaste, Sutram!')
 Open-File $syntax;Run;$b2=Snapshot 'B2-syntax';$r.b2_pass=$b2.output.Contains('Sutram truti') -and $b2.output.Contains('pankti') -and -not $b2.output.Contains('Namaste, Sutram!')
 Open-File $arith;Run;$b3=Snapshot 'B3-arithmetic';$r.b3_pass=$b3.output.Contains('E_VIBHAG_ANKA') -and -not $b3.output.Contains('Namaste, Sutram!') -and -not $b3.output.Contains('vyakaran dosh')
 Open-File $big;$b4=Snapshot 'B4-large-file';$r.b4_pass=$b4.editor -eq $b3.editor -and $b4.title.Contains('arithmetic.sm') -and $b4.output.Contains('patram na udghatitam') -and $b4.output.Contains('purvam patram eva asti') -and -not $b4.output.Contains('E_VIBHAG_ANKA')
}catch{$r.observer_error=$_.Exception.ToString();throw}
finally{
 if($ip -and -not $ip.HasExited){if($main){[void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero)};if(-not $ip.WaitForExit(5000)){$ip.Kill();[void]$ip.WaitForExit(5000);$r.forced_cleanup=$true}}
 $r.process_exited=($ip -and $ip.HasExited);$r.protected_hello_after=(Get-FileHash -LiteralPath $hello).Hash;$r.hello_unchanged=$r.protected_hello_before -eq $r.protected_hello_after;$r.capture_warnings=@($script:captureWarnings);Save
}
Write-Host "IDE B1=$($r.b1_pass) B2=$($r.b2_pass) B3=$($r.b3_pass) B4=$($r.b4_pass); original hello unchanged=$($r.hello_unchanged)"
if(-not($r.b1_pass -and $r.b2_pass -and $r.b3_pass -and $r.b4_pass -and $r.hello_unchanged)){throw 'An IDE expectation failed; see exact snapshots'}
