#!/usr/bin/env python3
"""Check what's in the invoice data from Zoho API."""
import sys
sys.path.insert(0, 'd:\\AI projects\\BI\\backend')

from app.services.zoho_api_client import ZohoAPIClient
import json

client = ZohoAPIClient()

print("=" * 80)
print("CHECKING INVOICE DATA STRUCTURE FROM ZOHO API")
print("=" * 80)

try:
    # Get first invoice
    invoices = client.get_records("invoices", page=1, per_page=1)

    if invoices:
        inv = invoices[0]
        print("\nInvoice fields available:")
        for key in inv.keys():
            value = inv[key]
            if isinstance(value, (list, dict)):
                if isinstance(value, list):
                    print(f"  {key}: LIST with {len(value)} items")
                    if value and isinstance(value[0], dict):
                        print(f"           -> {list(value[0].keys())}")
                else:
                    print(f"  {key}: DICT with keys {list(value.keys())}")
            else:
                print(f"  {key}: {type(value).__name__}")

        # Check line items specifically
        print(f"\nLine items in response: {len(inv.get('line_items', []))}")
        if inv.get('line_items'):
            first_line = inv['line_items'][0]
            print(f"First line item keys: {list(first_line.keys())}")
            print(f"First line item: {json.dumps(first_line, indent=2, default=str)[:500]}")
    else:
        print("No invoices returned!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
