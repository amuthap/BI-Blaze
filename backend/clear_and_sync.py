#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

# Reload environment variables from .env file
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from app.db.database import SessionLocal
from app.models.database import (
    Customer, Product, Invoice, InvoiceLineItem,
    Payment, DailyRevenue, ProductSale, SyncHistory, QueryHistory
)
from app.services.zoho_sync import ZohoSyncService
from app.config import get_settings

print("=" * 60)
print("CLEARING MOCK DATA AND SYNCING ZOHO BOOKS")
print("=" * 60)

db = SessionLocal()
settings = get_settings()

try:
    # Step 1: Clear mock data
    print("\n[STEP 1] Clearing mock data...")
    print("  Deleting query history...")
    db.query(QueryHistory).delete()

    print("  Deleting sync history...")
    db.query(SyncHistory).delete()

    print("  Deleting product sales...")
    db.query(ProductSale).delete()

    print("  Deleting daily revenue...")
    db.query(DailyRevenue).delete()

    print("  Deleting invoice line items...")
    db.query(InvoiceLineItem).delete()

    print("  Deleting payments...")
    db.query(Payment).delete()

    print("  Deleting invoices...")
    db.query(Invoice).delete()

    print("  Deleting products...")
    db.query(Product).delete()

    print("  Deleting customers...")
    db.query(Customer).delete()

    db.commit()
    print("[OK] Mock data cleared!")

    # Step 2: Trigger Zoho Books sync
    print("\n[STEP 2] Initiating Zoho Books sync...")

    from app.models.database import OAuthToken

    # Check if refresh token exists in database
    oauth_token = db.query(OAuthToken).filter(OAuthToken.provider == "zoho").first()

    if oauth_token and oauth_token.refresh_token:
        print(f"[OK] Found refresh token in database: {oauth_token.refresh_token[:30]}...")
        sync_service = ZohoSyncService(db)
        result = sync_service.sync_all()

        print("[OK] Sync completed!")
        print(f"  Customers synced: {result.get('customers', 0)}")
        print(f"  Products synced: {result.get('products', 0)}")
        print(f"  Invoices synced: {result.get('invoices', 0)}")
        print(f"  Payments synced: {result.get('payments', 0)}")
        print("")
        print(f"Total records synced: {sum(result.values())}")
    else:
        print("[FAILED] Refresh token not found in database!")
        print("   Please complete OAuth authorization first")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 60)
print("[OK] PROCESS COMPLETE - Refresh dashboard at http://localhost:3000")
print("=" * 60)
