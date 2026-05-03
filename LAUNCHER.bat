@echo off
echo.
echo =====================================================
echo    ODoo Invoice Monitoring System - Quick Launcher
echo =====================================================
echo.
echo This system automatically:
echo   - Monitors Odoo for new paid invoices
echo   - Adds them to your financial records
echo   - Generates CEO Weekly Reports with invoice data
echo.
echo Select an option:
echo.
echo [1] Run One-Time Invoice Sync & Report Generation
echo [2] Start Continuous Invoice Monitoring
echo [3] Generate CEO Report Only
echo [4] View Latest CEO Report
echo [5] Exit
echo.
choice /C 12345 /M "Enter your choice (1-5)"

if errorlevel 5 goto :exit
if errorlevel 4 goto :view_report
if errorlevel 3 goto :ceo_only
if errorlevel 2 goto :continuous
if errorlevel 1 goto :one_time

:one_time
echo.
echo Running one-time Odoo invoice sync and CEO report generation...
echo.
python sync_odoo_invoices_to_ceo_report.py
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:continuous
echo.
echo Starting continuous Odoo invoice monitoring...
echo.
python monitor_odoo_invoices.py
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:ceo_only
echo.
echo Generating CEO Weekly Report only...
echo.
python -c "
import sys
sys.path.append('.')
from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator
generator = CEOBriefingGenerator()
print('Generating CEO Weekly Report...')
report_files = generator.generate_weekly_report()
print('CEO Weekly Report generated successfully!')
for file_path in report_files:
    print(f'  - Report saved to: {file_path}')
"
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:view_report
echo.
echo Looking for latest CEO report...
for /f "delims=" %%i in ('dir "Reports\CEO_Reports\*.md" /o:d /t:c /b') do set "latest_report=%%i"
if defined latest_report (
    echo Latest report: Reports\CEO_Reports\%latest_report%
    echo.
    echo Opening report...
    start "" "Reports\CEO_Reports\%latest_report%"
) else (
    echo No CEO reports found. Run option 1 or 3 first.
)
echo.
echo Press any key to return to menu...
pause >nul
goto :menu

:exit
echo.
echo Thank you for using the Odoo Invoice Monitoring System!
echo.
exit /b

:menu
cls
goto :begin