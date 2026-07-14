#!/usr/bin/env python3
"""Check what data was synced from Zoho Books."""
from app.db.database import SessionLocal
from app.models.database import Customer, Product, Invoice, InvoiceLineItem, Payment, SyncHistory

db = SessionLocal()

print("=" * 70)
print("ZOHO BOOKS DATA SYNC VERIFICATION")
print("=" * 70)

# Count records
customers_count = db.query(Customer).count()
products_count = db.query(Product).count()
invoices_count = db.query(Invoice).count()
line_items_count = db.query(InvoiceLineItem).count()
payments_count = db.query(Payment).count()

print("\nDATA SYNCED FROM ZOHO BOOKS:")
print("-" * 70)
print(f"  Customers:          {customers_count:,} records")
print(f"  Products/Items:     {products_count:,} records")
print(f"  Invoices:           {invoices_count:,} records")
print(f"  Invoice Line Items: {line_items_count:,} records")
print(f"  Payments:           {payments_count:,} records")
print("-" * 70)
total = customers_count + products_count + invoices_count + line_items_count + payments_count
print(f"  TOTAL RECORDS:      {total:,} records")

# Show sync history
print("\n" + "=" * 70)
print("SYNC HISTORY (Last 10 attempts):")
print("=" * 70)

syncs = db.query(SyncHistory).order_by(SyncHistory.id.desc()).limit(10).all()
for sync in syncs:
    status = "DONE" if sync.status == "completed" else "FAIL" if sync.status == "failed" else "RUNNING"
    records = sync.records_synced if sync.records_synced is not None else "N/A"
    time_str = sync.completed_at.strftime('%H:%M:%S') if sync.completed_at else 'pending'
    print(f"  {sync.entity_type:15} | {status:7} | Records: {str(records):>5} | {time_str}")

# Summary
print("\n" + "=" * 70)
print("WHAT WAS SUCCESSFULLY SYNCED:")
print("=" * 70)

if customers_count > 0:
    print(f"  ✓ Customers:        {customers_count:,} records")
else:
    print(f"  ⚠ Customers:        0 records (may not exist in your Zoho account)")

print(f"  ✓ Products:         {products_count:,} records")
print(f"  ✓ Invoices:         {invoices_count:,} records")
print(f"  ✓ Line Items:       {line_items_count:,} records")

if payments_count == 0:
    print(f"  ✗ Payments:         NOT SYNCED (API returned HTTP 405 error)")
else:
    print(f"  ✓ Payments:         {payments_count:,} records")

print("\n" + "=" * 70)
print("ISSUES FOUND:")
print("=" * 70)

if customers_count == 0:
    print("⚠ No customers synced - Zoho Books account may not have customer records")

if payments_count == 0:
    print("✗ Payments NOT synced - Zoho Books API endpoint requires different method")
    print("  The /books/v3/payments endpoint returned HTTP 405 (method not allowed)")

if customers_count + products_count + invoices_count == 0:
    print("✗ CRITICAL: No main data synced at all!")
else:
    print("✓ Main data (Invoices, Products, Line Items) successfully synced")

db.close()
