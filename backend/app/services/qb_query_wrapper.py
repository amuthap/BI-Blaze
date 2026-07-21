"""QuickBooks query wrapper for Chat integration."""

import logging
from typing import Any, Dict, List, Optional
from app.services.qb_mcp_client import QuickBooksMCPClient

logger = logging.getLogger(__name__)


class QuickBooksQueryWrapper:
    """Wrapper for querying QB data in Chat context."""

    def __init__(self, mcp_client: QuickBooksMCPClient = None):
        self.mcp_client = mcp_client or QuickBooksMCPClient()

    async def get_customer_info(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer details by QB customer ID."""
        logger.info(f"Fetching QB customer info for {customer_id}")
        try:
            customers = await self.mcp_client.query_customers()
            for customer in customers:
                if customer.get("id") == customer_id or customer.get("Id") == customer_id:
                    return customer
        except Exception as e:
            logger.error(f"Failed to fetch QB customer info: {e}")
        return None

    async def get_invoice_details(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice details by QB invoice ID."""
        logger.info(f"Fetching QB invoice details for {invoice_id}")
        try:
            invoices = await self.mcp_client.query_invoices()
            for invoice in invoices:
                if invoice.get("id") == invoice_id or invoice.get("Id") == invoice_id:
                    return invoice
        except Exception as e:
            logger.error(f"Failed to fetch QB invoice details: {e}")
        return None

    async def search_customers(self, query: str) -> List[Dict[str, Any]]:
        """Search for customers by name or email."""
        logger.info(f"Searching QB customers for '{query}'")
        try:
            customers = await self.mcp_client.query_customers()
            query_lower = query.lower()
            results = [
                c for c in customers
                if query_lower in (c.get("displayName", "") or c.get("DisplayName", "")).lower()
                or query_lower in (c.get("primaryEmailAddr", {}).get("address", "") if isinstance(
                    c.get("primaryEmailAddr"), dict) else "").lower()
            ]
            return results[:10]  # Limit to 10 results
        except Exception as e:
            logger.error(f"Failed to search QB customers: {e}")
        return []

    async def get_recent_invoices(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent invoices from QB."""
        logger.info(f"Fetching {limit} recent QB invoices")
        try:
            invoices = await self.mcp_client.query_invoices()
            # Sort by txnDate (most recent first)
            sorted_invoices = sorted(
                invoices,
                key=lambda x: x.get("txnDate") or x.get("TxnDate", ""),
                reverse=True
            )
            return sorted_invoices[:limit]
        except Exception as e:
            logger.error(f"Failed to fetch QB invoices: {e}")
        return []

    async def get_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Get all overdue invoices from QB."""
        logger.info("Fetching overdue QB invoices")
        try:
            from datetime import date
            today = date.today()

            invoices = await self.mcp_client.query_invoices()
            overdue = []

            for invoice in invoices:
                due_date_str = invoice.get("dueDate") or invoice.get("DueDate")
                if due_date_str and due_date_str < str(today):
                    # Only include unpaid invoices
                    if not invoice.get("apmMetaData"):
                        overdue.append(invoice)

            return overdue
        except Exception as e:
            logger.error(f"Failed to fetch overdue QB invoices: {e}")
        return []

    async def get_customer_invoices(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all invoices for a specific customer."""
        logger.info(f"Fetching QB invoices for customer {customer_id}")
        try:
            invoices = await self.mcp_client.query_invoices()
            customer_invoices = [
                i for i in invoices
                if (i.get("customerRef", {}).get("value") == customer_id
                    if isinstance(i.get("customerRef"), dict) else False)
            ]
            return customer_invoices
        except Exception as e:
            logger.error(f"Failed to fetch customer invoices: {e}")
        return []

    async def get_sales_summary(self) -> Dict[str, Any]:
        """Get sales summary from QB invoices."""
        logger.info("Computing QB sales summary")
        try:
            from decimal import Decimal

            invoices = await self.mcp_client.query_invoices()
            total_revenue = Decimal("0")
            total_invoices = len(invoices)
            unpaid_amount = Decimal("0")

            for invoice in invoices:
                total_amt = invoice.get("totalAmt") or invoice.get("TotalAmt", 0)
                try:
                    total_revenue += Decimal(str(total_amt))
                except (ValueError, TypeError):
                    pass

                # Count unpaid invoices
                if not invoice.get("apmMetaData"):
                    try:
                        unpaid_amount += Decimal(str(total_amt))
                    except (ValueError, TypeError):
                        pass

            return {
                "total_revenue": float(total_revenue),
                "total_invoices": total_invoices,
                "unpaid_amount": float(unpaid_amount),
                "paid_percentage": (
                    (float(total_revenue - unpaid_amount) / float(total_revenue) * 100)
                    if total_revenue > 0 else 0
                )
            }
        except Exception as e:
            logger.error(f"Failed to compute sales summary: {e}")
        return {}
