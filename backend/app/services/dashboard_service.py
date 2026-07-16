"""Dashboard service for calculating business metrics."""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, union_all
from sqlalchemy.orm import Session

from app.models.database import (
    Invoice, Payment, Customer, Product, InvoiceLineItem,
    QBInvoice, QBPayment, QBCustomer, QBProduct, QBInvoiceLineItem
)


class DashboardService:
    """Service for calculating dashboard metrics."""

    def __init__(self, db: Session):
        self.db = db

    def get_revenue_metrics(self, days: int = 30) -> dict:
        """Get revenue metrics for the past N days (Zoho + QB)."""
        start_date = datetime.utcnow().date() - timedelta(days=days)

        # Zoho metrics
        zoho_result = self.db.query(
            func.sum(Invoice.total).label("total_revenue"),
            func.count(Invoice.id).label("invoice_count"),
            func.avg(Invoice.total).label("avg_transaction"),
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.status == "sent"
            )
        ).first()

        zoho_revenue = float(zoho_result[0] or 0)
        zoho_count = zoho_result[1] or 0
        zoho_avg = float(zoho_result[2] or 0)

        # QB metrics
        qb_result = self.db.query(
            func.sum(QBInvoice.total_amount).label("total_revenue"),
            func.count(QBInvoice.id).label("invoice_count"),
            func.avg(QBInvoice.total_amount).label("avg_transaction"),
        ).filter(
            and_(
                QBInvoice.metadata_create_time >= start_date,
                QBInvoice.doc_number.isnot(None),
            )
        ).first()

        qb_revenue = float(qb_result[0] or 0)
        qb_count = qb_result[1] or 0
        qb_avg = float(qb_result[2] or 0)

        total_count = zoho_count + qb_count
        total_revenue = zoho_revenue + qb_revenue
        combined_avg = total_revenue / total_count if total_count > 0 else 0

        return {
            "total_revenue": total_revenue,
            "invoice_count": total_count,
            "avg_transaction": combined_avg,
        }

    def get_revenue_trend(self, days: int = 30) -> list:
        """Get daily revenue trend for the past N days (Zoho + QB)."""
        start_date = datetime.utcnow().date() - timedelta(days=days)

        # Zoho revenue trend
        zoho_results = self.db.query(
            Invoice.invoice_date,
            func.sum(Invoice.total).label("daily_revenue"),
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.status == "sent"
            )
        ).group_by(
            Invoice.invoice_date
        ).all()

        # QB revenue trend (using create date cast to date)
        qb_results = self.db.query(
            func.date(QBInvoice.metadata_create_time).label("date"),
            func.sum(QBInvoice.total_amount).label("daily_revenue"),
        ).filter(
            and_(
                QBInvoice.metadata_create_time >= start_date,
                QBInvoice.doc_number.isnot(None),
            )
        ).group_by(
            func.date(QBInvoice.metadata_create_time)
        ).all()

        # Combine results by date
        combined = {}
        for row in zoho_results:
            date_key = str(row[0])
            combined[date_key] = combined.get(date_key, 0) + float(row[1] or 0)

        for row in qb_results:
            date_key = str(row[0])
            combined[date_key] = combined.get(date_key, 0) + float(row[1] or 0)

        # Sort by date and return
        return [
            {
                "date": date_key,
                "revenue": revenue,
            }
            for date_key, revenue in sorted(combined.items())
        ]

    def get_top_products(self, limit: int = 10, period_days: int = 90) -> list:
        """Get top selling products by revenue (Zoho + QB)."""
        start_date = datetime.utcnow().date() - timedelta(days=period_days)

        # Zoho products
        zoho_results = self.db.query(
            Product.name,
            func.sum(InvoiceLineItem.quantity).label("quantity_sold"),
            func.sum(InvoiceLineItem.item_total).label("revenue"),
        ).join(
            InvoiceLineItem,
            InvoiceLineItem.product_id == Product.id
        ).join(
            Invoice,
            Invoice.id == InvoiceLineItem.invoice_id
        ).filter(
            Invoice.invoice_date >= start_date
        ).group_by(
            Product.id,
            Product.name
        ).all()

        # QB products
        qb_results = self.db.query(
            QBProduct.name,
            func.sum(QBInvoiceLineItem.qty).label("quantity_sold"),
            func.sum(QBInvoiceLineItem.amount).label("revenue"),
        ).join(
            QBInvoiceLineItem,
            QBInvoiceLineItem.item_id == QBProduct.id
        ).join(
            QBInvoice,
            QBInvoice.id == QBInvoiceLineItem.invoice_id
        ).filter(
            QBInvoice.metadata_create_time >= start_date
        ).group_by(
            QBProduct.id,
            QBProduct.name
        ).all()

        # Combine by product name
        combined = {}
        for row in zoho_results:
            key = row[0]
            if key not in combined:
                combined[key] = {"qty": 0, "revenue": 0}
            combined[key]["qty"] += float(row[1] or 0)
            combined[key]["revenue"] += float(row[2] or 0)

        for row in qb_results:
            key = row[0]
            if key not in combined:
                combined[key] = {"qty": 0, "revenue": 0}
            combined[key]["qty"] += float(row[1] or 0)
            combined[key]["revenue"] += float(row[2] or 0)

        # Sort by revenue and limit
        sorted_products = sorted(
            combined.items(),
            key=lambda x: x[1]["revenue"],
            reverse=True
        )[:limit]

        return [
            {
                "product_name": name,
                "quantity_sold": data["qty"],
                "revenue": data["revenue"],
            }
            for name, data in sorted_products
        ]

    def get_growth_metrics(self, metric: str = "revenue", period_days: int = 30) -> dict:
        """Calculate growth rate for a metric (Zoho + QB)."""
        today = datetime.utcnow().date()
        period_start = today - timedelta(days=period_days)
        period_mid = period_start + timedelta(days=period_days // 2)

        if metric == "revenue":
            # Zoho first half
            zoho_first = self.db.query(
                func.sum(Invoice.total)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date < period_mid,
                )
            ).scalar() or Decimal(0)

            # QB first half
            qb_first = self.db.query(
                func.sum(QBInvoice.total_amount)
            ).filter(
                and_(
                    QBInvoice.metadata_create_time >= period_start,
                    QBInvoice.metadata_create_time < period_mid,
                    QBInvoice.doc_number.isnot(None),
                )
            ).scalar() or Decimal(0)

            first_half = zoho_first + qb_first

            # Zoho second half
            zoho_second = self.db.query(
                func.sum(Invoice.total)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_mid,
                    Invoice.invoice_date <= today,
                )
            ).scalar() or Decimal(0)

            # QB second half
            qb_second = self.db.query(
                func.sum(QBInvoice.total_amount)
            ).filter(
                and_(
                    QBInvoice.metadata_create_time >= period_mid,
                    QBInvoice.metadata_create_time <= today,
                    QBInvoice.doc_number.isnot(None),
                )
            ).scalar() or Decimal(0)

            second_half = zoho_second + qb_second

            growth_pct = (
                float((second_half - first_half) / first_half * 100)
                if first_half > 0 else 0.0
            )

        elif metric == "invoices":
            # Zoho first half
            zoho_first = self.db.query(
                func.count(Invoice.id)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date < period_mid,
                )
            ).scalar() or 0

            # QB first half
            qb_first = self.db.query(
                func.count(QBInvoice.id)
            ).filter(
                and_(
                    QBInvoice.metadata_create_time >= period_start,
                    QBInvoice.metadata_create_time < period_mid,
                    QBInvoice.doc_number.isnot(None),
                )
            ).scalar() or 0

            first_half = zoho_first + qb_first

            # Zoho second half
            zoho_second = self.db.query(
                func.count(Invoice.id)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_mid,
                    Invoice.invoice_date <= today,
                )
            ).scalar() or 0

            # QB second half
            qb_second = self.db.query(
                func.count(QBInvoice.id)
            ).filter(
                and_(
                    QBInvoice.metadata_create_time >= period_mid,
                    QBInvoice.metadata_create_time <= today,
                    QBInvoice.doc_number.isnot(None),
                )
            ).scalar() or 0

            second_half = zoho_second + qb_second

            growth_pct = (
                (second_half - first_half) / first_half * 100
                if first_half > 0 else 0.0
            )

        elif metric == "customers":
            # Zoho first half
            zoho_first = self.db.query(
                func.count(func.distinct(Invoice.customer_id))
            ).filter(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date < period_mid,
                )
            ).scalar() or 0

            # QB first half
            qb_first = self.db.query(
                func.count(func.distinct(QBInvoice.customer_id))
            ).filter(
                and_(
                    QBInvoice.metadata_create_time >= period_start,
                    QBInvoice.metadata_create_time < period_mid,
                    QBInvoice.doc_number.isnot(None),
                )
            ).scalar() or 0

            first_half = zoho_first + qb_first

            # Zoho second half
            zoho_second = self.db.query(
                func.count(func.distinct(Invoice.customer_id))
            ).filter(
                and_(
                    Invoice.invoice_date >= period_mid,
                    Invoice.invoice_date <= today,
                )
            ).scalar() or 0

            # QB second half
            qb_second = self.db.query(
                func.count(func.distinct(QBInvoice.customer_id))
            ).filter(
                and_(
                    QBInvoice.metadata_create_time >= period_mid,
                    QBInvoice.metadata_create_time <= today,
                    QBInvoice.doc_number.isnot(None),
                )
            ).scalar() or 0

            second_half = zoho_second + qb_second

            growth_pct = (
                (second_half - first_half) / first_half * 100
                if first_half > 0 else 0.0
            )

        return {
            "metric": metric,
            "growth_percentage": round(growth_pct, 2),
            "period_days": period_days,
        }

    def get_key_metrics(self, period_days: int = 30) -> dict:
        """Get all key metrics at once (Zoho + QuickBooks combined)."""
        start_date = datetime.utcnow().date() - timedelta(days=period_days)
        today = datetime.utcnow().date()

        # Revenue from both Zoho and QB
        zoho_revenue = self.db.query(
            func.sum(Invoice.total)
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= today,
            )
        ).scalar() or Decimal(0)

        qb_revenue = self.db.query(
            func.sum(QBInvoice.total_amount)
        ).filter(
            and_(
                QBInvoice.doc_number.isnot(None),
                QBInvoice.metadata_create_time >= start_date,
            )
        ).scalar() or Decimal(0)

        total_revenue = zoho_revenue + qb_revenue

        # Previous period revenue for comparison
        prev_start = start_date - timedelta(days=period_days)
        prev_zoho_revenue = self.db.query(
            func.sum(Invoice.total)
        ).filter(
            and_(
                Invoice.invoice_date >= prev_start,
                Invoice.invoice_date < start_date,
            )
        ).scalar() or Decimal(0)

        prev_qb_revenue = self.db.query(
            func.sum(QBInvoice.total_amount)
        ).filter(
            and_(
                QBInvoice.doc_number.isnot(None),
                QBInvoice.metadata_create_time >= prev_start,
                QBInvoice.metadata_create_time < start_date,
            )
        ).scalar() or Decimal(0)

        prev_revenue = prev_zoho_revenue + prev_qb_revenue

        revenue_change = (
            float((total_revenue - prev_revenue) / prev_revenue * 100)
            if prev_revenue > 0 else 0.0
        )

        # Invoices from both sources
        zoho_invoice_count = self.db.query(
            func.count(Invoice.id)
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= today,
            )
        ).scalar() or 0

        qb_invoice_count = self.db.query(
            func.count(QBInvoice.id)
        ).filter(
            and_(
                QBInvoice.doc_number.isnot(None),
                QBInvoice.metadata_create_time >= start_date,
            )
        ).scalar() or 0

        invoice_count = zoho_invoice_count + qb_invoice_count

        # Customers from both sources
        zoho_customer_count = self.db.query(
            func.count(func.distinct(Invoice.customer_id))
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= today,
            )
        ).scalar() or 0

        qb_customer_count = self.db.query(
            func.count(func.distinct(QBInvoice.customer_id))
        ).filter(
            and_(
                QBInvoice.doc_number.isnot(None),
                QBInvoice.metadata_create_time >= start_date,
            )
        ).scalar() or 0

        customer_count = zoho_customer_count + qb_customer_count

        # Average transaction from both sources
        avg_transaction = Decimal(0)
        if invoice_count > 0:
            avg_transaction = total_revenue / invoice_count

        return {
            "total_revenue": {
                "value": float(total_revenue),
                "change_pct": round(revenue_change, 2),
            },
            "invoice_count": {
                "value": invoice_count,
                "change_pct": 0.0,  # Calculate if needed
            },
            "customer_count": {
                "value": customer_count,
                "change_pct": 0.0,  # Calculate if needed
            },
            "avg_transaction": {
                "value": float(avg_transaction),
                "change_pct": 0.0,  # Calculate if needed
            },
            "period_days": period_days,
        }
