@echo off
title Sutram v311 acceptance - first program
call :run > first-cli.log 2>&1
type first-cli.log
echo.
echo First-program check finished.
goto :eof
:run
echo ^> where sutram
where sutram
echo ^> sutram --version
sutram --version
echo ^> sutram first.sm first.exe
sutram first.sm first.exe
set "compileExit=%errorlevel%"
echo Compile exit: %compileExit%
if not "%compileExit%"=="0" goto :done
echo ^> first.exe
first.exe
set "runExit=%errorlevel%"
echo.
echo Run exit: %runExit%
:done
echo complete > first-cli.done
exit /b