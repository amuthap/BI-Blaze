#!/usr/bin/env python
"""Test script to run Zoho sync and verify data."""

from app.services.zoho_sync import ZohoSyncService

print("=" * 60)
print("STARTING ZOHO SYNC TEST")
print("=" * 60)

try:
    sync = ZohoSyncService()
    print("\nFetching data from Zoho Books...")
    result = sync.sync_all(full_sync=True)

    print("\n" + "=" * 60)
    print("SYNC COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"  Customers synced: {result.get('customers', 0)}")
    print(f"  Products synced:  {result.get('products', 0)}")
    print(f"  Invoices synced:  {result.get('invoices', 0)}")
    print(f"  Payments synced:  {result.get('payments', 0)}")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] Sync failed: {e}")
    import traceback
    traceback.print_exc()
