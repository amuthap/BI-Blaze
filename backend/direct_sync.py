#!/usr/bin/env python3
"""Direct sync test - sync from database connection directly."""
import sys
sys.path.insert(0, 'd:\\AI projects\\BI\\backend')

from app.db.database import SessionLocal
from app.models.database import Customer, Product, Invoice, InvoiceLineItem, Payment
from app.services.zoho_sync import ZohoSyncService
from app.services.zoho_api_client import ZohoAPIClient
import logging

logging.basicConfig(level=logging.WARNING)

db = SessionLocal()

print("=" * 80)
print("DIRECT SYNC TEST")
print("=" * 80)

# Clear database
print("\n[1] Clearing database...")
db.query(Payment).delete()
db.query(InvoiceLineItem).delete()
db.query(Invoice).delete()
db.query(Customer).delete()
db.query(Product).delete()
db.commit()
print("[OK] Database cleared")

# Run sync using passed db session
print("\n[2] Running sync...")
sync = ZohoSyncService(db=db)

print("\n  Products...")
p_count = sync.sync_products(full_sync=True)
print(f"    -> {p_count} products")

print("\n  Customers...")
c_count = sync.sync_customers(full_sync=True)
print(f"    -> {c_count} customers")

print("\n  Invoices...")
i_count = sync.sync_invoices(full_sync=True)
print(f"    -> {i_count} invoices")

print("\n  Payments...")
try:
    py_count = sync.sync_payments(full_sync=True)
    print(f"    -> {py_count} payments")
except Exception as e:
    print(f"    -> FAILED: {str(e)[:100]}")

# Final check
print("\n[3] Final counts:")
customers = db.query(Customer).count()
products = db.query(Product).count()
invoices = db.query(Invoice).count()
line_items = db.query(InvoiceLineItem).count()
payments = db.query(Payment).count()

print(f"  Customers:   {customers}")
print(f"  Products:    {products}")
print(f"  Invoices:    {invoices}")
print(f"  Line Items:  {line_items}")
print(f"  Payments:    {payments}")
print(f"  TOTAL:       {customers + products + invoices + line_items + payments}")

if invoices > 0:
    print(f"\n[SUCCESS] {invoices} invoices synced!")
    first_invoice = db.query(Invoice).first()
    if first_invoice:
        print(f"  Sample: Invoice #{first_invoice.invoice_number} - Total: {first_invoice.total}")
elif products > 0 and customers > 0:
    print(f"\n[INFO] Products and customers exist but no invoices in Zoho account")
else:
    print(f"\n[WARNING] Sync completed but limited data")

db.close()
