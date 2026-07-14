#!/usr/bin/env python3
"""Test reports API with real synced data."""
import sys
sys.path.insert(0, 'd:\\AI projects\\BI\\backend')

from app.db.database import SessionLocal
from app.services.reports import ReportsService

db = SessionLocal()
reports = ReportsService(db)

print("=" * 80)
print("TESTING REPORTS WITH SYNCED DATA")
print("=" * 80)

try:
    print("\n[1] Revenue Summary (30 days):")
    rev = reports.get_revenue_summary(30)
    print(f"    Total Revenue: {rev['total_revenue']}")
    print(f"    Total Invoices: {rev['total_invoices']}")
    print(f"    Avg Invoice Value: {rev['avg_invoice_value']}")
    print(f"    By Status: {rev['by_status']}")

    print("\n[2] Top Customers (5):")
    top_cust = reports.get_top_customers(5)
    for c in top_cust:
        print(f"    {c['name']:30} - {c['invoice_count']} invoices, Total: {c['total_spent']}")

    print("\n[3] Product Performance (5):")
    top_prod = reports.get_product_performance(5)
    for p in top_prod:
        print(f"    {p['name']:30} - {p['quantity_sold']} qty, Revenue: {p['total_revenue']}")

    print("\n[4] Invoice Analysis:")
    inv_analysis = reports.get_invoice_analysis()
    print(f"    Total Invoices: {inv_analysis['total_invoices']}")
    print(f"    Total Value: {inv_analysis['total_value']}")
    print(f"    Overdue: {inv_analysis['overdue_count']} ({inv_analysis['overdue_amount']})")
    print(f"    Paid: {inv_analysis['paid_count']}")
    print(f"    Unpaid: {inv_analysis['unpaid_count']}")

    print("\n[5] Daily Revenue (Last 7 days):")
    daily = reports.get_daily_revenue(7)
    for d in daily[-3:]:
        print(f"    {d['date']}: {d['revenue']} ({d['invoice_count']} invoices)")

    print("\n[SUCCESS] All reports working with real data!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

db.close()
