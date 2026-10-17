@echo off
setlocal
set "APP=C:\Program Files\Stata17\StataMP-64.exe"
set "BASE=D:\AI_Innovation_Stata_Ready"
if not exist "%APP%" (
  echo ERROR: Existing Stata 17 binary not found.
  pause
  exit /b 1
)
if not exist "%BASE%\stata\TABLET_RUN.do" (
  echo ERROR: AI project not staged in Winlator Downloads D:.
  pause
  exit /b 2
)
cd /d "%BASE%"
"%APP%" /e do "%BASE%\stata\TABLET_RUN.do"
echo Stata returned %ERRORLEVEL%
echo Review D:\AI_Innovation_Stata_Ready\outputs\stata\TABLET_FINISH_STATUS.log
pause
endlocal
