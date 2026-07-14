#!/usr/bin/env python3
"""Test advanced reports API with real synced data."""
import sys
sys.path.insert(0, 'd:\\AI projects\\BI\\backend')

from app.db.database import SessionLocal
from app.services.reports import ReportsService

db = SessionLocal()
reports = ReportsService(db)

print("=" * 80)
print("TESTING ADVANCED REPORTS WITH SYNCED DATA")
print("=" * 80)

try:
    print("\n[1] Customer Segmentation:")
    seg = reports.get_customer_segmentation()
    print(f"    High Value: {seg['summary']['high_count']} customers, INR {seg['summary']['high_revenue']:,.0f}")
    print(f"    Medium Value: {seg['summary']['medium_count']} customers, INR {seg['summary']['medium_revenue']:,.0f}")
    print(f"    Low Value: {seg['summary']['low_count']} customers, INR {seg['summary']['low_revenue']:,.0f}")
    if seg.get('high_value'):
        print(f"    Top High-Value: {seg['high_value'][0]['name']} - INR {seg['high_value'][0]['total_value']:,.0f}")

    print("\n[2] Invoice Aging:")
    aging = reports.get_invoice_aging()
    for bucket, data in aging['aging_distribution'].items():
        print(f"    {bucket}: {data['count']} invoices, INR {data['amount']:,.0f}, {data['overdue_count']} overdue")

    print("\n[3] Payment Health:")
    health = reports.get_payment_health()
    print(f"    Collection Rate: {health['collection_rate']}%")
    print(f"    Days Sales Outstanding: {health['days_sales_outstanding']} days")
    print(f"    Paid: {health['status_breakdown']['paid']}, Unpaid: {health['status_breakdown']['unpaid']}, Overdue: {health['status_breakdown']['overdue']}")
    print(f"    At Risk Amount: INR {health['at_risk_amount']:,.0f}")

    print("\n[4] Product Analysis:")
    analysis = reports.get_product_analysis()
    print(f"    Total Products: {analysis['total_products']}")
    print(f"    Avg Revenue/Product: INR {analysis['avg_revenue_per_product']:,.0f}")
    if analysis.get('top_performers'):
        print(f"    Top Performer: {analysis['top_performers'][0]['name']} - INR {analysis['top_performers'][0]['revenue']:,.0f}")
    if analysis.get('bottom_performers'):
        print(f"    Bottom Performer: {analysis['bottom_performers'][0]['name']} - INR {analysis['bottom_performers'][0]['revenue']:,.0f}")

    print("\n[5] Monthly Comparison:")
    monthly = reports.get_monthly_comparison()
    print(f"    Months Tracked: {len(monthly['monthly_trends'])}")
    if monthly.get('monthly_trends'):
        for m in monthly['monthly_trends'][-3:]:  # Show last 3 months
            print(f"    {m['month']}: INR {m['revenue']:,.0f}, {m['invoices']} invoices, {m['growth_pct']:.1f}% growth")

    print("\n[SUCCESS] All advanced reports working with real data!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

db.close()
