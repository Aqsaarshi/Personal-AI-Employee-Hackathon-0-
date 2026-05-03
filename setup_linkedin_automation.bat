@echo off
REM LinkedIn Automation - Windows Task Scheduler Setup
REM Creates scheduled task to run LinkedIn workflow every 24 hours

echo ============================================
echo  LinkedIn Automation - Task Scheduler Setup
echo ============================================
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%linkedin_workflow.py

REM Find Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

for %%i in (python.exe) do set PYTHON_PATH=%%~$PATH:i

echo Python: %PYTHON_PATH%
echo Script: %PYTHON_SCRIPT%
echo.

REM Delete existing task
schtasks /Delete /TN "LinkedIn Automation" /F >nul 2>&1

REM Create task
echo Creating scheduled task...
echo Task: LinkedIn Automation
echo Schedule: Every 24 hours at 9:00 AM
echo.

schtasks /Create /TN "LinkedIn Automation" ^
    /TR "\"%PYTHON_PATH%\" \"%PYTHON_SCRIPT%\" --run" ^
    /SC DAILY ^
    /ST 09:00 ^
    /RL HIGHEST ^
    /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo  SUCCESS!
    echo ============================================
    echo.
    echo LinkedIn workflow will run daily at 9:00 AM
    echo.
    echo To run manually:
    echo   schtasks /Run /TN "LinkedIn Automation"
    echo.
    echo To view: Task Scheduler ^> LinkedIn Automation
    echo.
) else (
    echo.
    echo ============================================
    echo  ERROR! Run as Administrator
    echo ============================================
)

pause
