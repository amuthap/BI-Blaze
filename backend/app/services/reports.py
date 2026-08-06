"""Reports generation service for BI analytics."""
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.database import Customer, Invoice, Product, InvoiceLineItem, Payment


class ReportsService:
    """Generate business intelligence reports from database."""

    DEFAULT_EXCHANGE_RATE = 95.5  # USD to INR

    def __init__(self, db: Session):
        self.db = db

    def _convert_to_inr(self, amount: float, currency: str = "USD", exchange_rate: float = None) -> float:
        """Convert amount to INR."""
        if currency.upper() == "INR":
            return amount
        rate = exchange_rate or self.DEFAULT_EXCHANGE_RATE
        return amount * rate

    def get_revenue_summary(self, days: int = 30):
        """Get revenue summary for last N days."""
        start_date = datetime.utcnow().date() - timedelta(days=days)

        invoices = self.db.query(Invoice).filter(
            Invoice.invoice_date >= start_date,
            Invoice.status != 'draft'
        ).all()

        total_revenue = sum(float(inv.total) for inv in invoices) if invoices else 0
        total_revenue_inr = sum(
            self._convert_to_inr(float(inv.total), inv.currency_code or "USD", float(inv.exchange_rate or self.DEFAULT_EXCHANGE_RATE))
            for inv in invoices
        ) if invoices else 0

        total_invoices = len(invoices)
        avg_invoice_value = total_revenue / total_invoices if total_invoices > 0 else 0
        avg_invoice_value_inr = total_revenue_inr / total_invoices if total_invoices > 0 else 0

        # By status
        by_status = {}
        for status in ['paid', 'unpaid', 'overdue']:
            filtered = [i for i in invoices if i.payment_status == status]
            count = len(filtered)
            amount = sum(float(i.total) for i in filtered)
            amount_inr = sum(
                self._convert_to_inr(float(i.total), i.currency_code or "USD", float(i.exchange_rate or self.DEFAULT_EXCHANGE_RATE))
                for i in filtered
            )
            by_status[status] = {
                'count': count,
                'amount_usd': round(amount, 2),
                'amount_inr': round(amount_inr, 2)
            }

        return {
            'total_revenue_usd': round(total_revenue, 2),
            'total_revenue_inr': round(total_revenue_inr, 2),
            'total_invoices': total_invoices,
            'avg_invoice_value_usd': round(avg_invoice_value, 2),
            'avg_invoice_value_inr': round(avg_invoice_value_inr, 2),
            'by_status': by_status,
            'period_days': days
        }

    def get_top_customers(self, limit: int = 10):
        """Get top customers by revenue."""
        top_customers = self.db.query(
            Customer.id,
            Customer.name,
            func.count(Invoice.id).label('invoice_count'),
            func.sum(Invoice.total).label('total_spent')
        ).join(Invoice).filter(
            Invoice.status != 'draft'
        ).group_by(Customer.id, Customer.name).order_by(
            desc('total_spent')
        ).limit(limit).all()

        return [
            {
                'customer_id': c[0],
                'name': c[1],
                'invoice_count': c[2],
                'total_spent': float(c[3]) if c[3] else 0
            }
            for c in top_customers
        ]

    def get_product_performance(self, limit: int = 10):
        """Get top products by revenue."""
        top_products = self.db.query(
            Product.id,
            Product.name,
            Product.sku,
            func.count(InvoiceLineItem.id).label('quantity_sold'),
            func.sum(InvoiceLineItem.item_total).label('total_revenue')
        ).join(InvoiceLineItem).group_by(
            Product.id, Product.name, Product.sku
        ).order_by(desc('total_revenue')).limit(limit).all()

        return [
            {
                'product_id': p[0],
                'name': p[1],
                'sku': p[2],
                'quantity_sold': p[3] or 0,
                'total_revenue': float(p[4]) if p[4] else 0
            }
            for p in top_products
        ]

    def get_invoice_analysis(self):
        """Get invoice analytics."""
        total_invoices = self.db.query(func.count(Invoice.id)).scalar() or 0
        total_value = self.db.query(func.sum(Invoice.total)).scalar() or 0

        # Overdue invoices
        overdue_invoices = self.db.query(Invoice).filter(
            Invoice.due_date < datetime.utcnow().date(),
            Invoice.payment_status != 'paid'
        ).all()

        # Average days to pay
        paid_invoices = self.db.query(Invoice).filter(
            Invoice.payment_status == 'paid'
        ).all()

        days_to_pay = []
        if paid_invoices:
            for inv in paid_invoices:
                if inv.due_date:
                    days = (inv.zoho_updated_at.date() - inv.due_date).days
                    days_to_pay.append(max(0, days))

        avg_days_to_pay = sum(days_to_pay) / len(days_to_pay) if days_to_pay else 0

        return {
            'total_invoices': total_invoices,
            'total_value': float(total_value) if total_value else 0,
            'overdue_count': len(overdue_invoices),
            'overdue_amount': sum(float(i.total) for i in overdue_invoices) if overdue_invoices else 0,
            'avg_days_to_pay': round(avg_days_to_pay, 1),
            'paid_count': len(paid_invoices),
            'unpaid_count': total_invoices - len(paid_invoices)
        }

    def get_daily_revenue(self, days: int = 30):
        """Get daily revenue trend."""
        start_date = datetime.utcnow().date() - timedelta(days=days)

        daily_data = self.db.query(
            Invoice.invoice_date,
            func.sum(Invoice.total).label('daily_total'),
            func.count(Invoice.id).label('invoice_count')
        ).filter(
            Invoice.invoice_date >= start_date,
            Invoice.status != 'draft'
        ).group_by(Invoice.invoice_date).order_by(Invoice.invoice_date).all()

        return [
            {
                'date': d[0].isoformat(),
                'revenue': float(d[1]) if d[1] else 0,
                'invoice_count': d[2]
            }
            for d in daily_data
        ]

    def get_customer_analysis(self):
        """Get customer analytics."""
        total_customers = self.db.query(func.count(Customer.id)).scalar() or 0

        # Customers with invoices
        customers_with_invoices = self.db.query(
            func.count(func.distinct(Invoice.customer_id))
        ).scalar() or 0

        # Average customer value
        avg_value = self.db.query(
            func.avg(func.sum(Invoice.total))
        ).select_entity_from(Invoice).group_by(Invoice.customer_id).scalar() or 0

        return {
            'total_customers': total_customers,
            'customers_with_invoices': customers_with_invoices,
            'avg_customer_value': float(avg_value),
            'new_customers_this_month': 0  # Would need payment history for this
        }

    def get_invoice_by_status(self):
        """Get invoices breakdown by status."""
        statuses = ['draft', 'sent', 'viewed', 'accepted', 'declined']

        result = {}
        for status in statuses:
            invoices = self.db.query(Invoice).filter(
                Invoice.status == status
            ).all()
            result[status] = {
                'count': len(invoices),
                'amount': sum(float(i.total) for i in invoices) if invoices else 0
            }

        return result

    def get_payment_status_breakdown(self):
        """Get invoices by payment status."""
        payment_statuses = self.db.query(
            Invoice.payment_status,
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.total).label('amount')
        ).group_by(Invoice.payment_status).all()

        return [
            {
                'status': p[0],
                'count': p[1],
                'amount': float(p[2]) if p[2] else 0
            }
            for p in payment_statuses
        ]

    def get_customer_segmentation(self):
        """Segment customers by revenue value."""
        customer_totals = self.db.query(
            Customer.id,
            Customer.name,
            func.count(Invoice.id).label('invoice_count'),
            func.sum(Invoice.total).label('total_value')
        ).join(Invoice).filter(
            Invoice.status != 'draft'
        ).group_by(Customer.id, Customer.name).all()

        if not customer_totals:
            return {'high': [], 'medium': [], 'low': []}

        # Calculate quartiles
        values = [float(c[3]) if c[3] else 0 for c in customer_totals]
        values.sort()
        q3 = values[int(len(values) * 0.75)] if values else 0
        q1 = values[int(len(values) * 0.25)] if values else 0

        high = []
        medium = []
        low = []

        for c in customer_totals:
            total = float(c[3]) if c[3] else 0
            customer_data = {
                'name': c[1],
                'invoices': c[2],
                'total_value': total,
                'avg_invoice': total / c[2] if c[2] > 0 else 0
            }
            if total >= q3:
                high.append(customer_data)
            elif total >= q1:
                medium.append(customer_data)
            else:
                low.append(customer_data)

        return {
            'high_value': sorted(high, key=lambda x: x['total_value'], reverse=True)[:10],
            'medium_value': sorted(medium, key=lambda x: x['total_value'], reverse=True)[:10],
            'low_value': sorted(low, key=lambda x: x['total_value'], reverse=True)[:10],
            'summary': {
                'high_count': len(high),
                'medium_count': len(medium),
                'low_count': len(low),
                'high_revenue': sum(c['total_value'] for c in high),
                'medium_revenue': sum(c['total_value'] for c in medium),
                'low_revenue': sum(c['total_value'] for c in low),
            }
        }

    def get_invoice_aging(self):
        """Analyze invoice aging (how old they are by status)."""
        today = datetime.utcnow().date()
        invoices = self.db.query(Invoice).filter(
            Invoice.status != 'draft'
        ).all()

        aging_buckets = {
            '0-30_days': [],
            '31-60_days': [],
            '61-90_days': [],
            '90_plus_days': []
        }

        for inv in invoices:
            days_old = (today - inv.invoice_date).days
            amount = float(inv.total)
            is_overdue = inv.due_date and inv.due_date < today and inv.payment_status != 'paid'

            if days_old <= 30:
                aging_buckets['0-30_days'].append({
                    'invoice_number': inv.invoice_number,
                    'customer': self.db.query(Customer).filter_by(id=inv.customer_id).first().name,
                    'amount': amount,
                    'status': inv.payment_status,
                    'days_old': days_old,
                    'is_overdue': is_overdue
                })
            elif days_old <= 60:
                aging_buckets['31-60_days'].append({'amount': amount, 'status': inv.payment_status, 'days_old': days_old, 'is_overdue': is_overdue})
            elif days_old <= 90:
                aging_buckets['61-90_days'].append({'amount': amount, 'status': inv.payment_status, 'days_old': days_old, 'is_overdue': is_overdue})
            else:
                aging_buckets['90_plus_days'].append({'amount': amount, 'status': inv.payment_status, 'days_old': days_old, 'is_overdue': is_overdue})

        return {
            'aging_distribution': {
                bucket: {
                    'count': len(items),
                    'amount': sum(float(item['amount']) for item in items),
                    'overdue_count': len([i for i in items if i.get('is_overdue', False)])
                }
                for bucket, items in aging_buckets.items()
            },
            'oldest_invoices': sorted(
                [inv for inv in invoices if inv.status != 'draft'],
                key=lambda x: (today - x.invoice_date).days,
                reverse=True
            )[:10]
        }

    def get_payment_health(self):
        """Analyze payment collection health."""
        total_invoices = self.db.query(Invoice).filter(
            Invoice.status != 'draft'
        ).count()

        paid = self.db.query(Invoice).filter(
            Invoice.payment_status == 'paid'
        ).count()

        unpaid = self.db.query(Invoice).filter(
            Invoice.payment_status == 'unpaid'
        ).count()

        overdue = self.db.query(Invoice).filter(
            Invoice.payment_status == 'overdue'
        ).count()

        # Calculate DSO (Days Sales Outstanding)
        paid_invoices = self.db.query(Invoice).filter(
            Invoice.payment_status == 'paid'
        ).all()

        dso_days = []
        for inv in paid_invoices:
            if inv.due_date and inv.zoho_updated_at:
                days = (inv.zoho_updated_at.date() - inv.due_date).days
                dso_days.append(max(0, days))

        avg_dso = sum(dso_days) / len(dso_days) if dso_days else 0

        return {
            'collection_rate': round(paid / total_invoices * 100, 2) if total_invoices > 0 else 0,
            'status_breakdown': {
                'paid': paid,
                'unpaid': unpaid,
                'overdue': overdue,
                'total': total_invoices
            },
            'days_sales_outstanding': round(avg_dso, 1),
            'at_risk_amount': float(self.db.query(
                func.sum(Invoice.total)
            ).filter(
                Invoice.payment_status.in_(['unpaid', 'overdue'])
            ).scalar() or 0)
        }

    def get_product_analysis(self):
        """Analyze product/service performance."""
        products = self.db.query(
            Product.id,
            Product.name,
            Product.sku,
            func.count(InvoiceLineItem.id).label('qty_sold'),
            func.sum(InvoiceLineItem.item_total).label('revenue'),
            func.avg(InvoiceLineItem.unit_price).label('avg_price')
        ).join(InvoiceLineItem).group_by(
            Product.id, Product.name, Product.sku
        ).all()

        if not products:
            return {'top_performers': [], 'bottom_performers': [], 'total_products': 0, 'avg_revenue_per_product': 0}

        sorted_products = sorted(
            [
                {
                    'name': p[1],
                    'sku': p[2],
                    'quantity_sold': p[3] or 0,
                    'revenue': float(p[4]) if p[4] else 0,
                    'avg_price': float(p[5]) if p[5] else 0,
                }
                for p in products
            ],
            key=lambda x: x['revenue'],
            reverse=True
        )

        return {
            'top_performers': sorted_products[:10],
            'bottom_performers': sorted_products[-10:] if len(sorted_products) > 10 else sorted_products,
            'total_products': len(sorted_products),
            'avg_revenue_per_product': sum(p['revenue'] for p in sorted_products) / len(sorted_products) if sorted_products else 0
        }

    def get_monthly_comparison(self):
        """Compare revenue month-over-month."""
        months = {}
        invoices = self.db.query(Invoice).filter(
            Invoice.status != 'draft'
        ).all()

        for inv in invoices:
            month_key = inv.invoice_date.strftime('%Y-%m')
            if month_key not in months:
                months[month_key] = {
                    'revenue': 0,
                    'invoices': 0,
                    'customers': set()
                }
            months[month_key]['revenue'] += float(inv.total)
            months[month_key]['invoices'] += 1
            months[month_key]['customers'].add(inv.customer_id)

        sorted_months = sorted(months.items())
        growth_data = []

        for i, (month, data) in enumerate(sorted_months):
            month_obj = {
                'month': month,
                'revenue': data['revenue'],
                'invoices': data['invoices'],
                'unique_customers': len(data['customers']),
                'avg_invoice': data['revenue'] / data['invoices'] if data['invoices'] > 0 else 0,
                'growth_pct': 0
            }

            if i > 0:
                prev_revenue = sorted_months[i-1][1]['revenue']
                if prev_revenue > 0:
                    growth = ((data['revenue'] - prev_revenue) / prev_revenue) * 100
                    month_obj['growth_pct'] = round(growth, 2)

            growth_data.append(month_obj)

        return {
            'monthly_trends': growth_data,
            'best_month': max(growth_data, key=lambda x: x['revenue']) if growth_data else None,
            'latest_month': growth_data[-1] if growth_data else None
        }
