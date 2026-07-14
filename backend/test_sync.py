from app.services.zoho_sync import ZohoSyncService
import sys

print("====== STARTING ZOHO SYNC ======")
try:
    sync = ZohoSyncService()
    result = sync.sync_all(full_sync=True)
    print("? SYNC COMPLETED")
    print(f"  Customers: {result.get('customers', 0)}")
    print(f"  Products: {result.get('products', 0)}")
    print(f"  Invoices: {result.get('invoices', 0)}")
    print(f"  Payments: {result.get('payments', 0)}")
except Exception as e:
    print(f"? SYNC FAILED: {e}")
    import traceback
    traceback.print_exc()
