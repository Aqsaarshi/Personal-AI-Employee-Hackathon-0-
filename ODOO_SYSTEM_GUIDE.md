# Odoo Invoice Monitoring System

## Overview
This system automatically monitors your Odoo instance for new paid invoices and generates CEO Weekly Reports with the invoice data.

## How to Use

### Quick Start
1. Double-click on `LAUNCHER.bat` to open the main menu
2. Choose "Option 1" for one-time sync or "Option 2" for continuous monitoring

### Manual Execution
- Run one-time sync: `python sync_odoo_invoices_to_ceo_report.py`
- Run continuous monitoring: `python monitor_odoo_invoices.py`

## Core Files (Essential - DO NOT DELETE)
- `LAUNCHER.bat` - Main menu interface
- `sync_odoo_invoices_to_ceo_report.py` - Core functionality (monitors Odoo, syncs invoices, generates CEO reports)
- `monitor_odoo_invoices.py` - Continuous monitoring script
- `run_invoice_monitor.bat` - Alternative menu

## Generated Reports
- `Reports/CEO_Reports/CEO_Weekly_Briefing_*.md` - CEO reports with invoice data

## Configuration
- `Skills/Odoo_Integration/config.json` - Odoo connection settings (URL, database, credentials)

## What the System Does
1. Connects to your Odoo instance (pre-configured for localhost:8069)
2. Finds new paid invoices in Odoo
3. Adds them to your local financial records
4. Generates CEO Weekly Reports with the financial data
5. Saves reports in the Reports/CEO_Reports/ folder

## Success Indicators
- You see "Connected to Odoo" message when running
- New reports appear in Reports/CEO_Reports/ folder
- Reports contain financial data from your invoices

## Troubleshooting
- If you get permission errors, check your Odoo user permissions
- Make sure Odoo is running at the configured URL
- Verify your database credentials in config.json

## Files You Can Delete (After confirming system works)
- All other .md files except this one
- All test_*.py files in the TEST folder
- Debug files and images
- Setup files for other integrations (LinkedIn, etc.)