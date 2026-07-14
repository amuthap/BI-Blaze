#!/usr/bin/env python
"""Setup script to populate mock data and test dashboard."""

from app.db.database import SessionLocal, init_db
from app.services.mock_data import populate_mock_data
from app.services.dashboard_service import DashboardService

print("=" * 70)
print("SETTING UP DEMO DATA FOR BI SYSTEM")
print("=" * 70)

# Initialize database
print("\n[STEP 1] Initializing database...")
init_db()
print("  Database initialized with schema")

# Create session
db = SessionLocal()

# Populate mock data
print("\n[STEP 2] Populating mock data...")
mock_data = populate_mock_data(db)
print(f"  Created {len(mock_data['customers'])} customers")
print(f"  Created {len(mock_data['products'])} products")
print(f"  Created {len(mock_data['invoices'])} invoices")
print(f"  Created {len(mock_data['payments'])} payments")

# Test dashboard service
print("\n[STEP 3] Testing dashboard metrics...")
dashboard = DashboardService(db)

metrics = dashboard.get_key_metrics(days=30)
print(f"\n  Key Metrics (Last 30 Days):")
print(f"    Total Revenue: ${metrics['total_revenue']['value']:,.2f}")
print(f"    Invoices: {metrics['invoice_count']['value']}")
print(f"    Customers: {metrics['customer_count']['value']}")
print(f"    Avg Transaction: ${metrics['avg_transaction']['value']:,.2f}")

print(f"\n  Top 5 Products:")
products = dashboard.get_top_products(limit=5, period_days=30)
for i, product in enumerate(products, 1):
    print(f"    {i}. {product['product_name']}: ${product['revenue']:,.2f}")

growth = dashboard.get_growth_metrics(metric="revenue", period_days=30)
print(f"\n  Growth Metrics:")
print(f"    Revenue Growth: {growth['growth_percentage']:+.1f}%")

db.close()

print("\n" + "=" * 70)
print("DEMO SETUP COMPLETE!")
print("=" * 70)
print("""
Next steps:

1. Start the backend server:
   cd backend
   ./venv/Scripts/python.exe -m uvicorn app.main:app --reload

2. Visit the API documentation:
   http://localhost:8000/docs

3. Try these endpoints:
   - GET /api/dashboard/metrics
   - GET /api/dashboard/revenue-trend?days=30
   - GET /api/dashboard/top-products?limit=5
   - GET /api/dashboard/summary
   - POST /api/query/chat (with a question)

4. For custom data:
   POST /dev/populate-mock-data (to regenerate)
""")
