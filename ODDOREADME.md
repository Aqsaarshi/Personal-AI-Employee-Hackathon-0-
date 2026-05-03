# Odoo Invoice Monitoring System

This system automatically monitors your Odoo instance for new paid invoices and generates CEO Weekly Reports with the invoice data.

## How to Use

### Quick Start
Double-click on `LAUNCHER.bat` to open the main menu.

### Alternative Method
Run `run_invoice_monitor.bat` for a simpler menu.

## What It Does

1. **Monitors Odoo**: Checks your Odoo instance for new paid invoices
2. **Syncs Data**: Adds new invoices to your local financial ledger
3. **Generates Reports**: Creates CEO Weekly Reports with financial data
4. **Saves Reports**: Stores reports in `Reports/CEO_Reports/` folder

## Files You Need

- `LAUNCHER.bat` - Main menu to control the system
- `sync_odoo_invoices_to_ceo_report.py` - One-time sync script
- `monitor_odoo_invoices.py` - Continuous monitoring script
- `Reports/CEO_Reports/` - Folder containing generated reports

## Reports

After running the system, check the `Reports/CEO_Reports/` folder for your CEO Weekly Briefing reports. These reports include:
- Financial Summary with income from invoices
- Social Media Performance
- Leads and Opportunities
- Risks and Recommendations
- System Performance Metrics

## Configuration

The system is pre-configured to connect to Odoo at `http://localhost:8069`. If you need to change Odoo settings, edit `Skills/Odoo_Integration/config.json`.