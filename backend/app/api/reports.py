"""Reports API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.reports import ReportsService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/revenue-summary")
async def get_revenue_summary(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get revenue summary for specified period."""
    service = ReportsService(db)
    return service.get_revenue_summary(days)


@router.get("/top-customers")
async def get_top_customers(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get top customers by revenue."""
    service = ReportsService(db)
    return service.get_top_customers(limit)


@router.get("/product-performance")
async def get_product_performance(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Get top products by revenue."""
    service = ReportsService(db)
    return service.get_product_performance(limit)


@router.get("/invoice-analysis")
async def get_invoice_analysis(db: Session = Depends(get_db)):
    """Get invoice analytics."""
    service = ReportsService(db)
    return service.get_invoice_analysis()


@router.get("/daily-revenue")
async def get_daily_revenue(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get daily revenue trend."""
    service = ReportsService(db)
    return service.get_daily_revenue(days)


@router.get("/customer-analysis")
async def get_customer_analysis(db: Session = Depends(get_db)):
    """Get customer analytics."""
    service = ReportsService(db)
    return service.get_customer_analysis()


@router.get("/invoice-by-status")
async def get_invoice_by_status(db: Session = Depends(get_db)):
    """Get invoices breakdown by status."""
    service = ReportsService(db)
    return service.get_invoice_by_status()


@router.get("/payment-status")
async def get_payment_status(db: Session = Depends(get_db)):
    """Get invoices by payment status."""
    service = ReportsService(db)
    return service.get_payment_status_breakdown()


@router.get("/customer-segmentation")
async def get_customer_segmentation(db: Session = Depends(get_db)):
    """Segment customers by revenue value (high/medium/low)."""
    service = ReportsService(db)
    data = service.get_customer_segmentation()
    return {"success": True, "data": data}


@router.get("/invoice-aging")
async def get_invoice_aging(db: Session = Depends(get_db)):
    """Get invoice aging analysis (how old invoices are by status)."""
    service = ReportsService(db)
    data = service.get_invoice_aging()
    return {"success": True, "data": data}


@router.get("/payment-health")
async def get_payment_health(db: Session = Depends(get_db)):
    """Get payment collection health metrics (collection rate, DSO, at-risk amount)."""
    service = ReportsService(db)
    data = service.get_payment_health()
    return {"success": True, "data": data}


@router.get("/product-analysis")
async def get_product_analysis(db: Session = Depends(get_db)):
    """Analyze product/service performance (top and bottom performers)."""
    service = ReportsService(db)
    data = service.get_product_analysis()
    return {"success": True, "data": data}


@router.get("/monthly-comparison")
async def get_monthly_comparison(db: Session = Depends(get_db)):
    """Compare revenue month-over-month with growth percentages."""
    service = ReportsService(db)
    data = service.get_monthly_comparison()
    return {"success": True, "data": data}
