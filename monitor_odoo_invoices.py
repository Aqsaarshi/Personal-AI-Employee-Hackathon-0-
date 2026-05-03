"""
Monitor Odoo for new invoices and automatically generate CEO Weekly reports

This script continuously monitors Odoo for new paid invoices and automatically
generates CEO Weekly reports when new invoices are detected.
"""

import sys
import os
import time
from datetime import datetime, timedelta
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Skills.Odoo_Integration.odoo_integration import OdooIntegration
from Skills.Ledger_Manager.ledger_manager import LedgerManager
from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator

class OdooInvoiceMonitor:
    def __init__(self):
        """Initialize the Odoo invoice monitor."""
        print("Initializing Odoo Invoice Monitor...")

        # Initialize components
        self.odoo = OdooIntegration()
        self.ledger = LedgerManager()
        self.ceo_generator = CEOBriefingGenerator()

        # Track last checked time
        self.last_check_time = datetime.now() - timedelta(days=1)  # Start by checking last day

        print("Odoo Invoice Monitor initialized successfully!")

    def get_new_paid_invoices(self):
        """Get paid invoices that were created/updated since last check."""
        try:
            # Format the date to search for invoices since last check
            date_from = self.last_check_time.strftime("%Y-%m-%d")

            # Search for paid invoices from the last check time
            invoices = self.odoo.search_read(
                model="account.move",
                domain=[
                    ["move_type", "=", "out_invoice"],  # Customer invoices
                    ["payment_state", "=", "paid"],     # Only paid invoices
                    ["state", "=", "posted"],           # Posted invoices
                    ["invoice_date", ">=", date_from]  # From last check time
                ],
                fields=[
                    "id", "name", "ref", "invoice_date", "invoice_date_due",
                    "amount_total", "amount_untaxed", "amount_tax",
                    "partner_id", "payment_state", "state", "create_date", "write_date"
                ],
                order="invoice_date DESC, create_date DESC"
            )

            return invoices
        except Exception as e:
            print(f"Error fetching invoices: {e}")
            return []

    def sync_new_invoices_to_ledger(self):
        """Sync any new paid invoices from Odoo to the local ledger."""
        print(f"Checking for new paid invoices since {self.last_check_time}...")

        new_invoices = self.get_new_paid_invoices()
        synced_count = 0

        for invoice in new_invoices:
            try:
                # Check if this invoice already exists in our ledger
                invoice_number = invoice.get("name", "")

                # Look for this invoice in the ledger by checking description
                invoice_exists = any(
                    invoice_number in entry.description
                    for entry in self.ledger.entries
                )

                if invoice_exists:
                    print(f"  - Skipping existing invoice: {invoice_number}")
                    continue

                # Determine category based on invoice content or partner
                category = "sales"
                partner_name = ""
                if invoice.get("partner_id"):
                    partner_info = self.odoo.get_partner_info(invoice["partner_id"][0])
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

                entry_id = self.ledger.create_entry(
                    amount=amount,
                    category=category,
                    description=description,
                    entry_type="income",
                    date=entry_date,
                    tags=["odoo_sync", "invoice", "auto_sync"]
                )

                print(f"  - Synced invoice {invoice_number} to ledger (Entry ID: {entry_id})")
                synced_count += 1

            except Exception as e:
                print(f"  - Error syncing invoice {invoice.get('name', 'unknown')}: {e}")
                continue

        if synced_count > 0:
            print(f"Successfully synced {synced_count} new invoices to the ledger.")
            return True
        else:
            print("No new invoices to sync.")
            return False

    def generate_ceo_weekly_report(self):
        """Generate CEO weekly report based on latest data."""
        print("Generating CEO Weekly Report...")

        try:
            # Generate the report
            report_files = self.ceo_generator.generate_weekly_report()

            print(f"CEO Weekly Report generated successfully!")
            for file_path in report_files:
                print(f"  - Report saved to: {file_path}")

            return report_files

        except Exception as e:
            print(f"Error generating CEO report: {e}")
            return []

    def update_last_check_time(self):
        """Update the last check time to now."""
        self.last_check_time = datetime.now()

    def run_monitoring_cycle(self):
        """Run a single cycle of monitoring and report generation."""
        print(f"\n{'='*60}")
        print(f"Starting monitoring cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # Sync new invoices to ledger
        new_invoices_synced = self.sync_new_invoices_to_ledger()

        # Generate CEO report if new invoices were synced or periodically anyway
        if new_invoices_synced:
            print("\nNew invoices synced - Generating updated CEO Weekly Report...")
            self.generate_ceo_weekly_report()
        else:
            print("\nNo new invoices found, skipping report generation for this cycle.")

        # Update the last check time
        self.update_last_check_time()

        print(f"Monitoring cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

    def start_monitoring(self, interval_minutes=30):
        """Start continuous monitoring with specified interval."""
        print(f"\nStarting continuous monitoring (checking every {interval_minutes} minutes)...")
        print("Press Ctrl+C to stop monitoring.")

        try:
            while True:
                self.run_monitoring_cycle()

                # Wait for the specified interval
                print(f"Waiting {interval_minutes} minutes until next check...")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")

def main():
    """Main function to run the Odoo invoice monitor."""
    try:
        monitor = OdooInvoiceMonitor()

        # Run a single cycle to test
        print("Running initial monitoring cycle...")
        monitor.run_monitoring_cycle()

        # Ask if user wants to start continuous monitoring
        response = input("\nDo you want to start continuous monitoring? (y/n): ").strip().lower()

        if response in ['y', 'yes']:
            interval = input("Enter check interval in minutes (default 30): ").strip()
            try:
                interval = int(interval) if interval else 30
            except ValueError:
                interval = 30

            monitor.start_monitoring(interval)
        else:
            print("Exiting. You can run this script again to check for new invoices.")

    except Exception as e:
        print(f"Error initializing Odoo Invoice Monitor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()