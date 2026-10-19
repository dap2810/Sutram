[CmdletBinding()]
param([switch]$Run)
. (Join-Path $PSScriptRoot '..\build-common.ps1')
$ProjectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$nasm=Get-BuildTool 'nasm.exe'; $linker=Get-BuildTool 'ld.exe'
$build=Join-Path $ProjectRoot 'build\windows'
[void](New-Item -ItemType Directory -Force -Path $build)
# R73: the executable carries the canonical icon as a PE resource, so Explorer,
# the taskbar and the title bar all show the same image (see build-common.ps1).
Write-IconResourceInclude (Join-Path $ProjectRoot 'icons\sutram.ico') (Join-Path $build 'r73_icon.inc') 'icons/sutram.ico'
$objects=@()
foreach ($source in @('r67_gui_entry.asm','r66_indic_clusters.asm','r67_cluster_count.asm')) {
    $obj=Join-Path $build ([IO.Path]::GetFileNameWithoutExtension($source)+'.obj')
    [void](Invoke-BoundedProcess $nasm @('-f','win64','-dR73_ICON',('-I'+$ProjectRoot.Replace('\','/')+'/'),('-I'+$build.Replace('\','/')+'/'),('windows/gui/'+$source),'-o',$obj) $ProjectRoot)
    $objects+=$obj
}
$exe=Join-Path $ProjectRoot 'sutram-ide-gui.exe'
[void](Invoke-BoundedProcess $linker (@('-mi386pep','--subsystem','windows','--entry=_start','-o',$exe)+$objects+@('-lkernel32','-lshell32','-luser32','-lgdi32')) $ProjectRoot)
Assert-Pe64 $exe
$resource=Assert-PeResourceDirectory $exe
Write-Host "GUI built with icon resource ($resource). Rendering and interaction still require the desktop acceptance test."
if ($Run) { Start-Process -FilePath $exe -WorkingDirectory $ProjectRoot }
