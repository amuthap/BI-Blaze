#!/usr/bin/env python3
"""Clean sync with detailed error reporting and dependency handling."""
import sys
sys.path.insert(0, 'd:\\AI projects\\BI\\backend')

from app.db.database import SessionLocal
from app.models.database import (
    Customer, Product, Invoice, InvoiceLineItem, Payment, SyncHistory
)
from app.services.zoho_sync import ZohoSyncService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

db = SessionLocal()

print("\n" + "=" * 80)
print("ZOHO BOOKS DATA SYNC - FRESH START")
print("=" * 80)

# Step 1: Clear all data
print("\n[STEP 1] Clearing existing database records...")
try:
    db.query(Payment).delete()
    db.query(InvoiceLineItem).delete()
    db.query(Invoice).delete()
    db.query(Customer).delete()
    db.query(Product).delete()
    db.commit()
    print("[OK] Database cleared")
except Exception as e:
    print(f"[ERROR] Failed to clear database: {e}")
    db.close()
    sys.exit(1)

# Step 2: Run sync
print("\n[STEP 2] Syncing data from Zoho Books...")
sync_service = ZohoSyncService(db)

results = {
    "products": 0,
    "customers": 0,
    "invoices": 0,
    "payments": 0,
}

sync_steps = [
    ("products", sync_service.sync_products),
    ("customers", sync_service.sync_customers),
    ("invoices", sync_service.sync_invoices),
    ("payments", sync_service.sync_payments),
]

for name, sync_func in sync_steps:
    try:
        print(f"\n  Syncing {name}...")
        count = sync_func(full_sync=True)
        results[name] = count
        print(f"  [OK] {count} {name} synced")
    except Exception as e:
        error_msg = str(e)
        print(f"  [ERROR] {name} sync failed: {error_msg[:100]}")
        if "302" in error_msg:
            print(f"  [HINT] 302 Redirect - Enable Books API in Zoho OAuth app")
        elif "405" in error_msg:
            print(f"  [HINT] 405 Method Not Allowed - endpoint may not support this operation")
        elif "401" in error_msg:
            print(f"  [HINT] 401 Unauthorized - run OAuth flow again")

# Step 3: Verify results
print("\n[STEP 3] Verifying sync results...")
print("-" * 80)

counts = {
    "Customers": db.query(Customer).count(),
    "Products": db.query(Product).count(),
    "Invoices": db.query(Invoice).count(),
    "Line Items": db.query(InvoiceLineItem).count(),
    "Payments": db.query(Payment).count(),
}

for label, count in counts.items():
    print(f"  {label:20}: {count:>6,} records")

# Step 4: Summary
print("\n" + "=" * 80)
print("SYNC SUMMARY")
print("=" * 80)

total_records = sum(counts.values())

if counts["Customers"] == 0 and counts["Invoices"] > 0:
    print("[WARNING] Invoices exist but no customers found!")
    print("         This indicates invoices couldn't be inserted due to missing customers.")
    print("         Check Zoho Books - does your account have customer records?")
elif counts["Invoices"] == 0 and counts["Products"] > 0:
    print("[WARNING] Products synced but no invoices found!")
    print("         This is OK if your Zoho Books account has no invoices.")
elif counts["Customers"] > 0 and counts["Invoices"] == 0:
    print("[WARNING] Customers synced but no invoices found!")
    print("         Check Zoho Books - does your account have invoice records?")

if counts["Customers"] > 0 and counts["Invoices"] > 0:
    print("[OK] Main data synced successfully!")
    print(f"     Total records: {total_records:,}")

if counts["Payments"] == 0 and counts["Invoices"] > 0:
    print("[INFO] No payments synced")
    print("       Payment information can be obtained from invoice payment_status field")

db.close()
print("\n" + "=" * 80)
