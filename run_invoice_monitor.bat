@echo off
echo ========================================
echo  Odoo Invoice Monitor and CEO Reporter
echo ========================================
echo.
echo 1. Run one-time sync (recommended for first use)
echo 2. Run continuous monitoring
echo 3. Generate CEO Weekly Report only
echo 4. Exit
echo.
choice /C 1234 /M "Choose an option"

if errorlevel 4 goto :exit
if errorlevel 3 goto :ceo_only
if errorlevel 2 goto :continuous
if errorlevel 1 goto :one_time

:one_time
echo.
echo Running one-time Odoo invoice sync and CEO report generation...
python sync_odoo_invoices_to_ceo_report.py
pause
goto :eof

:continuous
echo.
echo Starting continuous Odoo invoice monitoring...
python monitor_odoo_invoices.py
pause
goto :eof

:ceo_only
echo.
echo Generating CEO Weekly Report only...
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
pause
goto :eof

:exit
echo Exiting...