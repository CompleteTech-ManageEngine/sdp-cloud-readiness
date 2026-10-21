@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
rem Prefer the self-contained runner so stale neighboring source cannot shadow it.
set "SDP_ASSESSMENT_ENTRY=sdp_cloud_readiness.pyz"
if not exist "%SDP_ASSESSMENT_ENTRY%" set "SDP_ASSESSMENT_ENTRY=sdp_cloud_readiness.py"
if not exist "%SDP_ASSESSMENT_ENTRY%" (
  echo Assessment entry point missing. Extract the full distribution or place the portable pyz beside this launcher.
  exit /b 1
)
echo Starting %SDP_ASSESSMENT_ENTRY%
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%SDP_ASSESSMENT_ENTRY%" %*
) else (
  python "%SDP_ASSESSMENT_ENTRY%" %*
)
set "SDP_ASSESSMENT_EXIT=%ERRORLEVEL%"
echo.
if "%SDP_ASSESSMENT_EXIT%"=="1" echo Run ended with a startup or local report-output error. Review the diagnostic lines above.
if "%SDP_ASSESSMENT_EXIT%"=="2" echo Source assessment is incomplete or stopped. This is not a migration-readiness approval.
if "%~1"=="" pause
exit /b %SDP_ASSESSMENT_EXIT%
