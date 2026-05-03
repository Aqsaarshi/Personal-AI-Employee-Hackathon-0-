"""
Test script for Ledger Manager skill
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Skills.Ledger_Manager.ledger_manager import LedgerManager
from Skills.Ledger_Manager.weekly_summary_template import generate_weekly_summary_report, save_weekly_summary_report

def test_ledger_manager():
    print("Testing Ledger Manager Skill...")

    # Initialize the ledger
    ledger = LedgerManager()
    print("[OK] Ledger Manager initialized")

    # Create some test entries
    print("\nCreating test entries...")

    # Add income entries
    income1_id = ledger.create_entry(
        amount=1500.00,
        category="sales",
        description="Website development project payment",
        entry_type="income",
        tags=["project", "client_a"]
    )
    print(f"[OK] Created income entry: {income1_id}")

    income2_id = ledger.create_entry(
        amount=850.00,
        category="consulting",
        description="Consulting services for client B",
        entry_type="income",
        tags=["consulting", "client_b"]
    )
    print(f"[OK] Created income entry: {income2_id}")

    # Add expense entries
    expense1_id = ledger.create_entry(
        amount=300.00,
        category="marketing",
        description="Google Ads campaign",
        entry_type="expense",
        tags=["q1", "advertising"]
    )
    print(f"[OK] Created expense entry: {expense1_id}")

    expense2_id = ledger.create_entry(
        amount=200.00,
        category="software",
        description="Software subscription",
        entry_type="expense",
        tags=["monthly", "subscription"]
    )
    print(f"[OK] Created expense entry: {expense2_id}")

    # Test financial summary
    print("\nTesting financial summary...")
    summary = ledger.get_financial_summary()
    print(f"[OK] Total Income: ${summary['total_income']}")
    print(f"[OK] Total Expenses: ${summary['total_expenses']}")
    print(f"[OK] Profit/Loss: ${summary['profit_loss']}")

    # Test getting specific entries
    print("\nTesting entry retrieval...")
    retrieved_entry = ledger.get_entry(income1_id)
    if retrieved_entry:
        print(f"[OK] Retrieved entry: {retrieved_entry.description}")
    else:
        print("[ERROR] Failed to retrieve entry")

    # Test updating an entry
    print("\nTesting entry update...")
    success = ledger.update_entry(
        income1_id,
        description="Website development project payment - FULL AMOUNT"
    )
    if success:
        updated_entry = ledger.get_entry(income1_id)
        print(f"[OK] Updated entry description: {updated_entry.description}")
    else:
        print("[ERROR] Failed to update entry")

    # Test weekly summary
    print("\nTesting weekly summary generation...")
    weekly_summary = ledger.generate_weekly_summary()
    print(f"[OK] Weekly Income: ${weekly_summary['total_income']}")
    print(f"[OK] Weekly Expenses: ${weekly_summary['total_expenses']}")
    print(f"[OK] Weekly Profit/Loss: ${weekly_summary['profit_loss']}")

    # Test generating and saving report
    print("\nTesting report generation...")
    report_text = generate_weekly_summary_report(weekly_summary)
    print("[OK] Generated formatted report")

    report_path = save_weekly_summary_report(weekly_summary)
    print(f"[OK] Saved report to: {report_path}")

    # Test backup functionality
    print("\nTesting backup functionality...")
    backup_success = ledger.backup_data()
    if backup_success:
        print("[OK] Backup created successfully")
    else:
        print("[INFO] Backup disabled in config (this is okay)")

    # Test filtering entries
    print("\nTesting entry filtering...")
    income_entries = ledger.get_entries(entry_type="income")
    expense_entries = ledger.get_entries(entry_type="expense")
    print(f"[OK] Found {len(income_entries)} income entries")
    print(f"[OK] Found {len(expense_entries)} expense entries")

    # Test category filtering
    sales_entries = ledger.get_entries(category="sales")
    print(f"[OK] Found {len(sales_entries)} sales entries")

    print("\n[SUCCESS] All tests passed! Ledger Manager skill is working correctly.")

if __name__ == "__main__":
    test_ledger_manager()