# Odoo Invoice Monitoring System - Organized Files List

## 🚀 LAUNCH FILES (START HERE)
- `LAUNCHER.bat` ← Main menu to control the system (DOUBLE-CLICK THIS FIRST!)
- `run_invoice_monitor.bat` ← Alternative menu option
- `README.md` ← Quick overview of the system

## 📊 MAIN SCRIPTS (Core functionality)
- `sync_odoo_invoices_to_ceo_report.py` ← One-time invoice sync + report
- `monitor_odoo_invoices.py` ← Continuous monitoring

## 📈 GENERATED REPORTS (Results of the system)
- `Reports/CEO_Reports/CEO_Weekly_Briefing_*.md` ← CEO reports with invoice data

## ⚙️ CONFIGURATION FILES (Settings)
- `Skills/Odoo_Integration/config.json` ← Odoo connection settings
- `Skills/Ledger_Manager/config.json` ← Financial ledger settings
- `Skills/CEO_Briefing_Generator/config.json` ← Report settings

## 📋 DOCUMENTATION (Guides)
- `QUICK_START_GUIDE.md` ← Step-by-step instructions
- `SYSTEM_ORGANIZATION.md` ← Complete file organization guide

## 🔧 CORE SKILLS (System components - already working)
- `Skills/Odoo_Integration/odoo_integration.py` ← Connects to Odoo
- `Skills/Ledger_Manager/ledger_manager.py` ← Manages financial records
- `Skills/CEO_Briefing_Generator/ceo_briefing_generator.py` ← Creates reports

---

## 🎯 TO USE THE SYSTEM:
1. **DOUBLE-CLICK**: `LAUNCHER.bat` ← Start here
2. **OR RUN**: `run_invoice_monitor.bat` ← Alternative start
3. **CHECK RESULTS**: Look in `Reports/CEO_Reports/` folder

## ✅ SUCCESS INDICATORS:
- ✅ You see "Connected to Odoo" message
- ✅ New reports appear in Reports/CEO_Reports/ folder
- ✅ Reports contain financial data from your invoices
- ✅ System runs without errors

## 🗂️ FILES YOU CAN IGNORE (Not needed for basic operation):
- All files starting with: test_, debug_, alternative_, hitl_, reasoning_
- Files in: addons/, backups/, mcp_servers/, watchers/ folders
- Most other root directory files