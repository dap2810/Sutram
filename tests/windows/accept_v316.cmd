@echo off
rem tests\windows\accept_v316.cmd - R167 WS1: what v316 must do on real Windows before it is merged.
rem Run from anywhere:  tests\windows\accept_v316.cmd      (cmd.exe, an ordinary user, no administrator)
rem It uses this checkout's win\sutram.exe and sutram-link.exe, works in a new folder under %TEMP%, changes nothing
rem else, and installs nothing. Each step prints PASS or FAIL and one line of what it proves; the same lines go to
rem accept-v316-result.txt in the repository's root. The result carries no path and no compiler output (a message
rem can name a folder under your profile), so the file is safe to commit as it is.
rem Exit 0: every step passed. 1: a step failed - do not merge; send the result file.
rem Written without "&&", "||" and bracketed blocks on purpose: every test is "run it, then look at errorlevel".
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0..\.."
set "SC=%ROOT%\win\sutram.exe"
set "LK=%ROOT%\sutram-link.exe"
set "RES=%ROOT%\accept-v316-result.txt"
set "W=%TEMP%\sutram-v316-accept-%RANDOM%%RANDOM%"
set /a PASS=0
set /a FAIL=0
set /a SKIP=0
if not exist "%SC%" goto :nocompiler
mkdir "%W%"
if not exist "%W%\" goto :nowork
mkdir "%W%\lib"
mkdir "%W%\sub"
copy /y "%ROOT%\lib\ganit.smlib" "%W%\lib\ganit.smlib" >nul
pushd "%W%"
> "%RES%" echo Sutram v316 acceptance on Windows - tests\windows\accept_v316.cmd

> a.sm echo mukhya() {
>> a.sm echo     likha(41 + 1)
>> a.sm echo }
copy /y a.sm a0.sm >nul
> m.sm echo yoj ganit
>> m.sm echo mukhya() {
>> m.sm echo     likha(varg(3))
>> m.sm echo }

rem --- 01. it starts: the three new kernel32 functions resolve
"%SC%" --version > o.txt 2>&1
call :has o.txt "(v316)"
set OK=!HAS!
call :say 01 "the compiler starts and is v316 - GetFileInformationByHandle, SetEndOfFile and GetFileType were found"

rem --- 02. an ordinary compile still writes its output, and the program runs
"%SC%" a.sm hello.exe > o.txt 2>&1
set RC=!errorlevel!
call :runs hello.exe 42
set OK=0
if "!RC!"=="0" if "!RUNS!"=="1" set OK=1
call :say 02 "an ordinary compile is not refused on this disk, and its program prints 42"

rem --- 03-08. the output names the source, six ways: refused, exit 1, the source byte for byte as it was
call :refuse 03 a.sm "the source as its own output"
call :refuse 04 .\a.sm "the source as .\name"
call :refuse 05 A.SM "the source in another case, on a file system that ignores case"
call :refuse 06 "%CD%\a.sm" "the source by its full path"
call :refuse 07 sub\..\a.sm "the source through a folder and back"
mklink /H hard.sm a.sm >nul 2>&1
if not exist hard.sm goto :nohard
call :refuse 08 hard.sm "a hard link to the source"
goto :afterhard
:nohard
set /a SKIP+=1
echo SKIP  08 a hard link could not be made here
>> "%RES%" echo SKIP  08 a hard link could not be made here
:afterhard

rem --- 09. --object too
"%SC%" --object a.sm a.sm > o.txt 2>&1
set RC=!errorlevel!
call :has o.txt "E_NIRGAM_NIVESH"
call :same a.sm a0.sm
set OK=0
if "!RC!"=="1" if "!HAS!"=="1" if "!SAME!"=="1" set OK=1
call :say 09 "--object with the source as its output: refused, exit 1, the source unchanged"

rem --- 10-11. a module the compile read
"%SC%" m.sm m.exe > o.txt 2>&1
set RC=!errorlevel!
call :runs m.exe 9
set OK=0
if "!RC!"=="0" if "!RUNS!"=="1" set OK=1
call :say 10 "a program with yoj compiles and prints 9"
"%SC%" m.sm lib\ganit.smlib > o.txt 2>&1
set RC=!errorlevel!
call :has o.txt "E_NIRGAM_NIVESH"
call :same lib\ganit.smlib "%ROOT%\lib\ganit.smlib"
set OK=0
if "!RC!"=="1" if "!HAS!"=="1" if "!SAME!"=="1" set OK=1
call :say 11 "the output naming a yoj module the compile read: refused, exit 1, the module unchanged"

rem --- 12. an existing larger file as the output ends exactly as a fresh build: it is cut, then written
"%SC%" a.sm fresh.exe > o.txt 2>&1
copy /b /y "%SC%" big.exe >nul
"%SC%" a.sm big.exe > o.txt 2>&1
set RC=!errorlevel!
call :same big.exe fresh.exe
set OK=0
if "!RC!"=="0" if "!SAME!"=="1" set OK=1
call :say 12 "an existing larger output is replaced exactly - no old bytes left after the new program"

rem --- 13. an output that cannot be opened is an error; v315 said Siddh, exit 0, and wrote nothing
"%SC%" a.sm no-such-folder\x.exe > o.txt 2>&1
set RC=!errorlevel!
call :has o.txt "E_NIRGAM_PATRA"
set OK=0
if "!RC!"=="1" if "!HAS!"=="1" set OK=1
call :say 13 "an output in a folder that does not exist: an error, exit 1"

rem --- 14. NUL is still an output
"%SC%" a.sm NUL > o.txt 2>&1
set RC=!errorlevel!
set OK=0
if "!RC!"=="0" set OK=1
call :say 14 "NUL as the output still works - a device is written as before"

rem --- 15-17. the linker
"%SC%" --object a.sm a.smo > o.txt 2>&1
copy /y a.smo a0.smo >nul
"%LK%" a.smo a.smo > o.txt 2>&1
set RC=!errorlevel!
call :has o.txt "E_NIRGAM_NIVESH"
call :same a.smo a0.smo
set OK=0
if "!RC!"=="1" if "!HAS!"=="1" if "!SAME!"=="1" set OK=1
call :say 15 "sutram-link with its object as the output: refused, exit 1, the object unchanged"
"%LK%" linked.exe a.smo > o.txt 2>&1
set RC=!errorlevel!
call :runs linked.exe 42
set OK=0
if "!RC!"=="0" if "!RUNS!"=="1" set OK=1
call :say 16 "an ordinary link works and its program prints 42"
copy /b /y "%SC%" big2.exe >nul
"%LK%" big2.exe a.smo > o.txt 2>&1
set RC=!errorlevel!
call :same big2.exe linked.exe
set OK=0
if "!RC!"=="0" if "!SAME!"=="1" set OK=1
call :say 17 "the linker replaces an existing larger output exactly"

rem --- 18. the source is still the source after all of it
call :same a.sm a0.sm
set OK=!SAME!
call :say 18 "after every step the source is byte for byte what it was"

popd
rmdir /s /q "%W%" >nul 2>&1
echo.
echo v316 acceptance: !PASS! passed, !FAIL! failed, !SKIP! skipped
>> "%RES%" echo v316 acceptance: !PASS! passed, !FAIL! failed, !SKIP! skipped
if not "!FAIL!"=="0" exit /b 1
exit /b 0

:nocompiler
echo FAIL  win\sutram.exe is not in this checkout
exit /b 1
:nowork
echo FAIL  could not make a work folder under TEMP
exit /b 1

:refuse
rem %1 number, %2 the output to name, %3 what it is
"%SC%" a.sm %2 > o.txt 2>&1
set RC=!errorlevel!
call :has o.txt "E_NIRGAM_NIVESH"
call :same a.sm a0.sm
set OK=0
if "!RC!"=="1" if "!HAS!"=="1" if "!SAME!"=="1" set OK=1
call :say %1 "%~3: refused, exit 1, the source unchanged"
goto :eof

:has
rem %1 file, %2 text -> HAS=1 if the file has the text
set HAS=0
findstr /c:%2 "%~1" >nul 2>&1
if not errorlevel 1 set HAS=1
goto :eof

:same
rem %1, %2 files -> SAME=1 if they are byte for byte the same: the same size, and fc /b finds no difference
set SAME=0
if not exist "%~1" goto :eof
if not exist "%~2" goto :eof
if not "%~z1"=="%~z2" goto :eof
fc /b "%~1" "%~2" >nul 2>&1
if not errorlevel 1 set SAME=1
goto :eof

:runs
rem %1 program, %2 text its first line must start with -> RUNS=1
set RUNS=0
if not exist "%~1" goto :eof
"%~1" > r.txt 2>&1
findstr /b /c:"%~2" r.txt >nul 2>&1
if not errorlevel 1 set RUNS=1
goto :eof

:say
if "!OK!"=="1" goto :say_pass
set /a FAIL+=1
echo FAIL  %1 %~2
>> "%RES%" echo FAIL  %1 %~2
goto :eof
:say_pass
set /a PASS+=1
echo PASS  %1 %~2
>> "%RES%" echo PASS  %1 %~2
goto :eof
