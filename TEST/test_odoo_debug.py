"""
Debug Odoo connection without Unicode
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_odoo():
    """Test Odoo connection."""
    from Skills.Odoo_Integration.odoo_integration import OdooIntegration

    print("Testing Odoo connection...")
    try:
        odoo = OdooIntegration()
        print(f"Connected to Odoo (User ID: {odoo.uid})")

        # Simple search
        print("\nTesting simple search...")
        result = odoo.search_read("res.partner", [], ["id", "name"], 0, 5)
        print(f"Found {len(result)} partners")
        for partner in result[:3]:
            print(f"  - {partner.get('id')}: {partner.get('name')}")

        # Test invoices
        print("\nTesting invoice search...")
        domain = [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"]
        ]
        invoice_result = odoo.search_read("account.move", domain, ["id", "name"], 0, 3)
        print(f"Found {len(invoice_result)} invoices")
        for inv in invoice_result:
            print(f"  - {inv.get('id')}: {inv.get('name')}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_odoo()
