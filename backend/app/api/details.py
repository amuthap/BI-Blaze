"""Detailed data endpoints for drilling down into records."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.database import get_db
from app.models.database import Invoice, Payment, Customer, InvoiceLineItem

router = APIRouter(prefix="/api/details", tags=["details"])


@router.get("/invoices")
async def get_invoices_list(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get detailed invoice list with customer info."""
    try:
        invoices = db.query(Invoice).order_by(desc(Invoice.invoice_date)).limit(limit).offset(offset).all()
        total = db.query(Invoice).count()

        return {
            "data": [
                {
                    "id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "date": str(inv.invoice_date),
                    "amount": float(inv.total),
                    "status": inv.status,
                    "customer_name": inv.customer.name if inv.customer else "Unknown",
                    "email": inv.customer.email if inv.customer else "",
                }
                for inv in invoices
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        import logging
        logging.error(f"Error fetching invoices: {e}")
        return {
            "data": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "error": str(e),
        }


@router.get("/payments")
async def get_payments_list(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get detailed payment list."""
    try:
        payments = db.query(Payment).order_by(desc(Payment.payment_date)).limit(limit).offset(offset).all()
        total = db.query(Payment).count()

        return {
            "data": [
                {
                    "id": pmt.id,
                    "reference_number": pmt.reference_number,
                    "date": str(pmt.payment_date),
                    "amount": float(pmt.amount),
                    "method": pmt.payment_method,
                    "customer_name": pmt.customer.name if pmt.customer else "Unknown",
                    "invoice_number": pmt.invoice.invoice_number if pmt.invoice else "",
                }
                for pmt in payments
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        import logging
        logging.error(f"Error fetching payments: {e}")
        return {
            "data": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "error": str(e),
        }


@router.get("/customers")
async def get_customers_list(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get detailed customer list with invoice counts."""
    try:
        from sqlalchemy import func

        customers = db.query(Customer).order_by(desc(Customer.id)).limit(limit).offset(offset).all()
        total = db.query(Customer).count()

        return {
            "data": [
                {
                    "id": cust.id,
                    "name": cust.name,
                    "email": cust.email,
                    "phone": cust.phone or "",
                    "city": cust.billing_address_city or "",
                    "invoices": len(cust.invoices) if cust.invoices else 0,
                    "total_spent": sum(float(inv.total) for inv in cust.invoices) if cust.invoices else 0.0,
                }
                for cust in customers
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        import logging
        logging.error(f"Error fetching customers: {e}")
        return {
            "data": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "error": str(e),
        }


@router.get("/invoice-items/{invoice_id}")
async def get_invoice_items(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    """Get line items for a specific invoice."""
    items = (
        db.query(
            InvoiceLineItem.id,
            InvoiceLineItem.description,
            InvoiceLineItem.quantity,
            InvoiceLineItem.unit_price,
            InvoiceLineItem.line_total,
        )
        .filter(InvoiceLineItem.invoice_id == invoice_id)
        .all()
    )

    return {
        "data": [
            {
                "id": item[0],
                "description": item[1],
                "quantity": float(item[2]),
                "unit_price": float(item[3]),
                "total": float(item[4]),
            }
            for item in items
        ],
    }
