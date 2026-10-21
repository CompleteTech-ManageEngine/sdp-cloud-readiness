@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
call "%~dp0Run-Assessment.cmd" --all-portals %*
set "SDP_ALL_EXIT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %SDP_ALL_EXIT%
