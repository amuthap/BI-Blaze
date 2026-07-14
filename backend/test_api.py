#!/usr/bin/env python3
"""Test Zoho Books API endpoints to diagnose issues."""
import sys
sys.path.insert(0, 'd:\\AI projects\\BI\\backend')

from app.services.zoho_api_client import ZohoAPIClient
from app.config import get_settings

settings = get_settings()
client = ZohoAPIClient()

print("=" * 80)
print("ZOHO BOOKS API ENDPOINT TEST")
print("=" * 80)

endpoints = [
    ("customers", "Customers"),
    ("items", "Products/Items"),
    ("invoices", "Invoices"),
    ("payments", "Payments"),
]

for endpoint, label in endpoints:
    print(f"\n[TEST] {label} ({endpoint})")
    print("-" * 80)
    try:
        result = client._make_request("GET", f"/{endpoint}", params={"page": 1, "per_page": 1})

        # Count records in response
        records = result.get(endpoint, [])
        count = len(records)
        total = result.get("page_context", {}).get("total", "?")

        print(f"  Status: OK")
        print(f"  Records returned: {count}")
        print(f"  Total available: {total}")

        if records:
            first_key = list(records[0].keys())[0]
            print(f"  First record sample: {first_key}={records[0].get(first_key)}")

    except Exception as e:
        error_msg = str(e)
        print(f"  Status: FAILED")
        print(f"  Error: {error_msg}")
        if "302" in error_msg:
            print(f"  [ISSUE] 302 Redirect - OAuth app may not have API access enabled")
        elif "405" in error_msg:
            print(f"  [ISSUE] 405 Method Not Allowed - endpoint may not support GET")
        elif "401" in error_msg:
            print(f"  [ISSUE] 401 Unauthorized - token may be invalid or expired")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("If you see 302 errors: Enable Books API in Zoho OAuth app settings")
print("If you see 405 errors: This endpoint may not support list operations")
print("If you see 401 errors: Re-authenticate by running OAuth flow")
