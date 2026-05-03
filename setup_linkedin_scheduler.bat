@echo off
REM LinkedIn Auto Poster - Windows Task Scheduler Setup
REM This script creates a scheduled task to post daily at 9 AM

echo ============================================
echo  LinkedIn Auto Poster - Task Scheduler Setup
echo ============================================
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%auto_linkedin_poster.py

REM Find Python executable
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH!
    echo Please install Python or add it to your system PATH.
    pause
    exit /b 1
)

REM Get full Python path
for %%i in (python.exe) do set PYTHON_PATH=%%~$PATH:i

echo Python found: %PYTHON_PATH%
echo Script location: %PYTHON_SCRIPT%
echo.

REM Delete existing task if it exists
schtasks /Delete /TN "LinkedIn Auto Poster" /F >nul 2>&1

REM Create the scheduled task
echo Creating scheduled task...
echo Task: LinkedIn Auto Poster
echo Schedule: Daily at 9:00 AM
echo.

schtasks /Create /TN "LinkedIn Auto Poster" ^
    /TR "\"%PYTHON_PATH%\" \"%PYTHON_SCRIPT%\"" ^
    /SC DAILY ^
    /ST 09:00 ^
    /RL HIGHEST ^
    /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo  SUCCESS! Task created successfully.
    echo ============================================
    echo.
    echo Your LinkedIn posts will be published daily at 9:00 AM.
    echo.
    echo To run the task manually:
    echo   schtasks /Run /TN "LinkedIn Auto Poster"
    echo.
    echo To view task history:
    echo   Open Task Scheduler ^> Task Scheduler Library ^> LinkedIn Auto Poster ^> History
    echo.
    echo To remove the task:
    echo   schtasks /Delete /TN "LinkedIn Auto Poster"
    echo.
) else (
    echo.
    echo ============================================
    echo  ERROR! Failed to create task.
    echo ============================================
    echo.
    echo Please run this script as Administrator.
    echo.
)

pause
