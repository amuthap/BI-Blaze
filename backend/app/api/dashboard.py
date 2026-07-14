"""Dashboard API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.dashboard_service import DashboardService
from app.models.schemas import (
    DashboardMetrics,
    RevenueTrend,
    TopProducts,
    GrowthMetric,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics(
    period: str = Query("month", regex="^(today|week|month|quarter|year)$"),
    db: Session = Depends(get_db),
):
    """Get key dashboard metrics."""
    period_days = {
        "today": 1,
        "week": 7,
        "month": 30,
        "quarter": 90,
        "year": 365,
    }[period]

    service = DashboardService(db)
    metrics = service.get_key_metrics(period_days=period_days)

    return DashboardMetrics(
        total_revenue=metrics["total_revenue"],
        invoice_count=metrics["invoice_count"],
        customer_count=metrics["customer_count"],
        avg_transaction=metrics["avg_transaction"],
        period_days=period_days,
    )


@router.get("/revenue-trend", response_model=RevenueTrend)
async def get_revenue_trend(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get revenue trend over time."""
    service = DashboardService(db)
    trend_data = service.get_revenue_trend(days=days)

    return RevenueTrend(
        data=trend_data,
        period_days=days,
    )


@router.get("/top-products", response_model=TopProducts)
async def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    period: str = Query("month", regex="^(week|month|quarter|year)$"),
    db: Session = Depends(get_db),
):
    """Get top selling products."""
    period_days = {
        "week": 7,
        "month": 30,
        "quarter": 90,
        "year": 365,
    }[period]

    service = DashboardService(db)
    products = service.get_top_products(limit=limit, period_days=period_days)

    return TopProducts(
        data=products,
        limit=limit,
        period_days=period_days,
    )


@router.get("/growth-rate", response_model=GrowthMetric)
async def get_growth_rate(
    metric: str = Query("revenue", regex="^(revenue|invoices|customers)$"),
    period_days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """Get growth rate for a specific metric."""
    service = DashboardService(db)
    growth = service.get_growth_metrics(metric=metric, period_days=period_days)

    return GrowthMetric(
        metric=metric,
        growth_percentage=growth["growth_percentage"],
        period_days=period_days,
    )


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    """Get complete dashboard summary."""
    service = DashboardService(db)

    return {
        "metrics": service.get_key_metrics(period_days=30),
        "revenue_trend": service.get_revenue_trend(days=30),
        "top_products": service.get_top_products(limit=5, period_days=30),
        "growth": service.get_growth_metrics(metric="revenue", period_days=30),
        "generated_at": str(__import__("datetime").datetime.utcnow()),
    }
