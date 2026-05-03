"""
Automated script to monitor Odoo for new invoices and generate CEO Weekly reports

This script can be run manually or scheduled to run periodically to monitor
Odoo for new paid invoices and automatically generate CEO Weekly reports.
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Skills.Odoo_Integration.odoo_integration import OdooIntegration
from Skills.Ledger_Manager.ledger_manager import LedgerManager
from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator

def sync_odoo_invoices_to_ledger():
    """Sync new paid invoices from Odoo to the local ledger and generate CEO report."""
    print(f"Starting Odoo invoice sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Initialize components
        odoo = OdooIntegration()
        ledger = LedgerManager()
        ceo_generator = CEOBriefingGenerator()

        # Get all paid invoices from Odoo
        print("Fetching paid invoices from Odoo...")

        # Search for all paid invoices
        invoices = odoo.search_read(
            model="account.move",
            domain=[
                ["move_type", "=", "out_invoice"],  # Customer invoices
                ["payment_state", "=", "paid"],     # Only paid invoices
                ["state", "=", "posted"]            # Posted invoices
            ],
            fields=[
                "id", "name", "ref", "invoice_date", "invoice_date_due",
                "amount_total", "amount_untaxed", "amount_tax",
                "partner_id", "payment_state", "state", "create_date", "write_date"
            ],
            order="invoice_date DESC"
        )

        print(f"Found {len(invoices)} paid invoices in Odoo")

        synced_count = 0

        # Process each invoice
        for invoice in invoices:
            try:
                # Check if this invoice already exists in our ledger
                invoice_number = invoice.get("name", "")

                # Look for this invoice in the ledger by checking description
                invoice_exists = any(
                    invoice_number in entry.description
                    for entry in ledger.entries
                )

                if invoice_exists:
                    print(f"  - Skipping existing invoice: {invoice_number}")
                    continue

                # Determine category based on invoice content or partner
                category = "sales"
                partner_name = ""
                if invoice.get("partner_id"):
                    partner_info = odoo.get_partner_info(invoice["partner_id"][0])
                    partner_name = partner_info.get("name", "")

                    # Map categories based on partner or other criteria
                    if "consulting" in (partner_name or "").lower():
                        category = "consulting"

                # Create the ledger entry
                description = f"Odoo Invoice: {invoice_number}"
                if partner_name:
                    description += f" - {partner_name}"

                entry_date = invoice.get("invoice_date") or invoice.get("date") or datetime.now().strftime("%Y-%m-%d")
                amount = float(invoice.get("amount_total", 0))

                # Skip zero or negative amounts
                if amount <= 0:
                    continue

                entry_id = ledger.create_entry(
                    amount=amount,
                    category=category,
                    description=description,
                    entry_type="income",
                    date=entry_date,
                    tags=["odoo_sync", "invoice", "auto_sync"]
                )

                print(f"  - Added invoice {invoice_number} to ledger (Entry ID: {entry_id}) - ${amount:.2f}")
                synced_count += 1

            except Exception as e:
                print(f"  - Error processing invoice {invoice.get('name', 'unknown')}: {e}")
                continue

        print(f"Successfully synced {synced_count} new invoices to the ledger.")

        if synced_count > 0:
            print("Generating updated CEO Weekly Report...")

            # Generate the CEO weekly report based on the updated ledger
            report_files = ceo_generator.generate_weekly_report()

            print(f"CEO Weekly Report generated successfully!")
            for file_path in report_files:
                print(f"  - Report saved to: {file_path}")

            return {
                "status": "success",
                "synced_invoices": synced_count,
                "reports_generated": len(report_files),
                "report_files": report_files
            }
        else:
            print("No new invoices to sync, no report generated.")

            # Still generate a report to show current status
            print("Generating current CEO Weekly Report...")
            report_files = ceo_generator.generate_weekly_report()

            print(f"Current CEO Weekly Report generated successfully!")
            for file_path in report_files:
                print(f"  - Report saved to: {file_path}")

            return {
                "status": "success",
                "synced_invoices": synced_count,
                "reports_generated": len(report_files),
                "report_files": report_files
            }

    except Exception as e:
        print(f"Error in invoice sync process: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error_message": str(e)
        }

def main():
    """Main function to run the invoice sync."""
    print("="*60)
    print("Odoo Invoice to CEO Report Generator")
    print("="*60)

    result = sync_odoo_invoices_to_ledger()

    print("="*60)
    if result["status"] == "success":
        print("Process completed successfully!")
        print(f"Invoices synced: {result['synced_invoices']}")
        print(f"Reports generated: {result['reports_generated']}")
    else:
        print(f"Process failed: {result['error_message']}")
    print("="*60)

if __name__ == "__main__":
    main()