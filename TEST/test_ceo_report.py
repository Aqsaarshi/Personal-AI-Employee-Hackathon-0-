"""
Test CEO Weekly Report Generation
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ceo_report():
    """Test the CEO Weekly Report generation."""
    from Skills.CEO_Briefing_Generator.ceo_briefing_generator import CEOBriefingGenerator

    print("=" * 60)
    print("CEO Weekly Report Test")
    print("=" * 60)

    try:
        # Initialize the CEO Briefing Generator
        print("\n1. Initializing CEO Briefing Generator...")
        ceo_generator = CEOBriefingGenerator()
        print("   [SUCCESS] CEO Briefing Generator initialized")

        # Generate weekly report
        print("\n2. Generating weekly report...")
        report = ceo_generator.generate_weekly_report()

        # Display key financial data
        print("\n3. Financial Summary:")
        financial_summary = report.get('financial_summary', {})
        total_income = financial_summary.get('total_income', 0)
        total_expenses = financial_summary.get('total_expenses', 0)
        profit_loss = financial_summary.get('profit_loss', 0)

        print(f"   Total Income: ${total_income:.2f}")
        print(f"   Total Expenses: ${total_expenses:.2f}")
        print(f"   Net Profit/Loss: ${profit_loss:.2f}")

        # Check category breakdowns
        print("\n4. Income by Category:")
        income_by_category = financial_summary.get('income_by_category', {})
        for category, amount in income_by_category.items():
            print(f"   {category}: ${amount:.2f}")

        print("\n5. Expenses by Category:")
        expenses_by_category = financial_summary.get('expenses_by_category', {})
        for category, amount in expenses_by_category.items():
            print(f"   {category}: ${amount:.2f}")

        # Check if Odoo invoice appears
        print("\n6. Checking for Odoo invoice entry...")
        for category, amount in income_by_category.items():
            if amount == 230.0:  # The invoice we synced
                print(f"   [FOUND] Invoice found in category '{category}': ${amount:.2f}")
                break

        print("\n" + "=" * 60)
        print("[SUCCESS] CEO Weekly Report generated successfully!")
        print("=" * 60)

        # Display full report path if generated
        if 'report_path' in report:
            print(f"\nReport saved to: {report['report_path']}")

        return True

    except Exception as e:
        print(f"[FAIL] Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ceo_report()
