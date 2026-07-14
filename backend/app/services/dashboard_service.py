"""Dashboard service for calculating business metrics."""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models.database import Invoice, Payment, Customer, Product, InvoiceLineItem


class DashboardService:
    """Service for calculating dashboard metrics."""

    def __init__(self, db: Session):
        self.db = db

    def get_revenue_metrics(self, days: int = 30) -> dict:
        """Get revenue metrics for the past N days."""
        start_date = datetime.utcnow().date() - timedelta(days=days)

        result = self.db.query(
            func.sum(Invoice.total).label("total_revenue"),
            func.count(Invoice.id).label("invoice_count"),
            func.avg(Invoice.total).label("avg_transaction"),
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.status == "sent"
            )
        ).first()

        return {
            "total_revenue": float(result[0] or 0),
            "invoice_count": result[1] or 0,
            "avg_transaction": float(result[2] or 0),
        }

    def get_revenue_trend(self, days: int = 30) -> list:
        """Get daily revenue trend for the past N days."""
        start_date = datetime.utcnow().date() - timedelta(days=days)

        results = self.db.query(
            Invoice.invoice_date,
            func.sum(Invoice.total).label("daily_revenue"),
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.status == "sent"
            )
        ).group_by(
            Invoice.invoice_date
        ).order_by(
            Invoice.invoice_date
        ).all()

        return [
            {
                "date": str(row[0]),
                "revenue": float(row[1] or 0),
            }
            for row in results
        ]

    def get_top_products(self, limit: int = 10, period_days: int = 90) -> list:
        """Get top selling products by revenue."""
        start_date = datetime.utcnow().date() - timedelta(days=period_days)

        results = self.db.query(
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
        ).order_by(
            func.sum(InvoiceLineItem.item_total).desc()
        ).limit(limit).all()

        return [
            {
                "product_name": row[0],
                "quantity_sold": float(row[1] or 0),
                "revenue": float(row[2] or 0),
            }
            for row in results
        ]

    def get_growth_metrics(self, metric: str = "revenue", period_days: int = 30) -> dict:
        """Calculate growth rate for a metric."""
        today = datetime.utcnow().date()
        period_start = today - timedelta(days=period_days)
        period_mid = period_start + timedelta(days=period_days // 2)

        if metric == "revenue":
            first_half = self.db.query(
                func.sum(Invoice.total)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date < period_mid,
                )
            ).scalar() or Decimal(0)

            second_half = self.db.query(
                func.sum(Invoice.total)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_mid,
                    Invoice.invoice_date <= today,
                )
            ).scalar() or Decimal(0)

            growth_pct = (
                float((second_half - first_half) / first_half * 100)
                if first_half > 0 else 0.0
            )

        elif metric == "invoices":
            first_half = self.db.query(
                func.count(Invoice.id)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date < period_mid,
                )
            ).scalar() or 0

            second_half = self.db.query(
                func.count(Invoice.id)
            ).filter(
                and_(
                    Invoice.invoice_date >= period_mid,
                    Invoice.invoice_date <= today,
                )
            ).scalar() or 0

            growth_pct = (
                (second_half - first_half) / first_half * 100
                if first_half > 0 else 0.0
            )

        elif metric == "customers":
            first_half = self.db.query(
                func.count(func.distinct(Invoice.customer_id))
            ).filter(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date < period_mid,
                )
            ).scalar() or 0

            second_half = self.db.query(
                func.count(func.distinct(Invoice.customer_id))
            ).filter(
                and_(
                    Invoice.invoice_date >= period_mid,
                    Invoice.invoice_date <= today,
                )
            ).scalar() or 0

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
        """Get all key metrics at once."""
        start_date = datetime.utcnow().date() - timedelta(days=period_days)
        today = datetime.utcnow().date()

        # Revenue
        total_revenue = self.db.query(
            func.sum(Invoice.total)
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= today,
            )
        ).scalar() or Decimal(0)

        # Previous period revenue for comparison
        prev_start = start_date - timedelta(days=period_days)
        prev_revenue = self.db.query(
            func.sum(Invoice.total)
        ).filter(
            and_(
                Invoice.invoice_date >= prev_start,
                Invoice.invoice_date < start_date,
            )
        ).scalar() or Decimal(0)

        revenue_change = (
            float((total_revenue - prev_revenue) / prev_revenue * 100)
            if prev_revenue > 0 else 0.0
        )

        # Invoices
        invoice_count = self.db.query(
            func.count(Invoice.id)
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= today,
            )
        ).scalar() or 0

        # Customers
        customer_count = self.db.query(
            func.count(func.distinct(Invoice.customer_id))
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= today,
            )
        ).scalar() or 0

        # Average transaction
        avg_transaction = self.db.query(
            func.avg(Invoice.total)
        ).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= today,
            )
        ).scalar() or Decimal(0)

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
