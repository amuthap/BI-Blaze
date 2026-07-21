"""QuickBooks data sync via MCP server."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.models.database import (
    QBCustomer, QBProduct, QBInvoice, QBInvoiceLineItem,
    QBPayment
)
from app.services.qb_mcp_client import QuickBooksMCPClient

logger = logging.getLogger(__name__)


class QuickBooksMCPSync:
    """Sync QB data using the QuickBooks MCP server."""

    def __init__(self, db: Session, mcp_client: QuickBooksMCPClient = None):
        self.db = db
        self.mcp_client = mcp_client or QuickBooksMCPClient()
        logger.info("QuickBooksMCPSync initialized")

    async def sync_all(self):
        """Sync all QB data via MCP."""
        try:
            logger.info("Starting QB sync via MCP...")
            await self.mcp_client.connect()

            await self.sync_customers()
            await self.sync_products()
            await self.sync_invoices()
            await self.sync_payments()

            logger.info("QB MCP sync completed successfully")

        except Exception as e:
            logger.error(f"QB MCP sync failed: {str(e)}")
            raise
        finally:
            await self.mcp_client.disconnect()

    async def sync_customers(self):
        """Sync QB customers via MCP."""
        logger.info("Syncing QB customers via MCP...")
        try:
            customers = await self.mcp_client.query_customers()
            logger.info(f"Retrieved {len(customers)} customers from QB")

            for customer_data in customers:
                customer = self._create_or_update_customer(customer_data)
                self.db.add(customer)

            self.db.commit()
            logger.info(f"Synced {len(customers)} QB customers")

        except Exception as e:
            logger.error(f"Customer sync failed: {e}")
            self.db.rollback()
            raise

    async def sync_products(self):
        """Sync QB products via MCP."""
        logger.info("Syncing QB products via MCP...")
        try:
            items = await self.mcp_client.query_items()
            logger.info(f"Retrieved {len(items)} items from QB")

            for item_data in items:
                product = self._create_or_update_product(item_data)
                self.db.add(product)

            self.db.commit()
            logger.info(f"Synced {len(items)} QB products")

        except Exception as e:
            logger.error(f"Product sync failed: {e}")
            self.db.rollback()
            raise

    async def sync_invoices(self):
        """Sync QB invoices via MCP."""
        logger.info("Syncing QB invoices via MCP...")
        try:
            invoices = await self.mcp_client.query_invoices()
            logger.info(f"Retrieved {len(invoices)} invoices from QB")

            for invoice_data in invoices:
                invoice = self._create_or_update_invoice(invoice_data)
                self.db.add(invoice)

            self.db.commit()
            logger.info(f"Synced {len(invoices)} QB invoices")

        except Exception as e:
            logger.error(f"Invoice sync failed: {e}")
            self.db.rollback()
            raise

    async def sync_payments(self):
        """Sync QB payments via MCP."""
        logger.info("Syncing QB payments via MCP...")
        try:
            payments = await self.mcp_client.query_payments()
            logger.info(f"Retrieved {len(payments)} payments from QB")

            for payment_data in payments:
                payment = self._create_or_update_payment(payment_data)
                self.db.add(payment)

            self.db.commit()
            logger.info(f"Synced {len(payments)} QB payments")

        except Exception as e:
            logger.error(f"Payment sync failed: {e}")
            self.db.rollback()
            raise

    def _create_or_update_customer(self, data: Dict[str, Any]) -> QBCustomer:
        """Create or update a customer from QB data."""
        qb_id = str(data.get("id") or data.get("Id", ""))

        customer = self.db.query(QBCustomer).filter(
            QBCustomer.qb_id == qb_id
        ).first()

        if not customer:
            customer = QBCustomer(qb_id=qb_id)

        customer.name = data.get("displayName") or data.get("DisplayName", "")

        # Extract email from primaryEmailAddr object
        email_addr = data.get("primaryEmailAddr")
        if isinstance(email_addr, dict):
            customer.email = email_addr.get("address", "")
        else:
            customer.email = ""

        # Extract phone
        phone_data = data.get("phone")
        if isinstance(phone_data, dict):
            customer.phone = phone_data.get("freeFormNumber", "")
        else:
            customer.phone = str(phone_data) if phone_data else ""

        customer.qb_updated_at = datetime.utcnow()
        customer.updated_at = datetime.utcnow()

        return customer

    def _create_or_update_product(self, data: Dict[str, Any]) -> QBProduct:
        """Create or update a product from QB item data."""
        qb_id = str(data.get("id") or data.get("Id", ""))

        product = self.db.query(QBProduct).filter(
            QBProduct.qb_id == qb_id
        ).first()

        if not product:
            product = QBProduct(qb_id=qb_id)

        product.name = data.get("name") or data.get("Name", "")
        product.description = data.get("description") or data.get("Description") or ""
        product.sku = data.get("sku") or data.get("SKU") or ""

        # Extract unit price
        unit_price = data.get("unitPrice") or data.get("UnitPrice")
        if unit_price:
            try:
                product.unit_price = Decimal(str(unit_price))
            except (ValueError, TypeError):
                product.unit_price = Decimal("0.00")
        else:
            product.unit_price = Decimal("0.00")

        product.qb_updated_at = datetime.utcnow()
        product.updated_at = datetime.utcnow()

        return product

    def _create_or_update_invoice(self, data: Dict[str, Any]) -> QBInvoice:
        """Create or update an invoice from QB data."""
        qb_id = str(data.get("id") or data.get("Id", ""))

        invoice = self.db.query(QBInvoice).filter(
            QBInvoice.qb_id == qb_id
        ).first()

        if not invoice:
            invoice = QBInvoice(qb_id=qb_id)

        # Extract customer ID from customerRef
        customer_ref = data.get("customerRef", {})
        if isinstance(customer_ref, dict):
            qb_customer_id = customer_ref.get("value")
            # Find the customer by qb_id
            customer = self.db.query(QBCustomer).filter(
                QBCustomer.qb_id == str(qb_customer_id)
            ).first()
            if customer:
                invoice.customer_id = customer.id

        invoice.invoice_number = data.get("docNumber") or data.get("DocNumber", "")

        # Extract dates
        invoice_date = data.get("txnDate") or data.get("TxnDate")
        if invoice_date:
            invoice.invoice_date = invoice_date
        due_date = data.get("dueDate") or data.get("DueDate")
        if due_date:
            invoice.due_date = due_date

        # Extract amounts
        total_amount = data.get("totalAmt") or data.get("TotalAmt", 0)
        tax_amount = data.get("taxTotal") or data.get("TaxTotal", 0)

        try:
            invoice.total = Decimal(str(total_amount))
            invoice.tax = Decimal(str(tax_amount))
        except (ValueError, TypeError):
            invoice.total = Decimal("0.00")
            invoice.tax = Decimal("0.00")

        # Map QB status to payment_status
        invoice.status = data.get("status") or data.get("Status", "Draft")
        invoice.payment_status = self._map_payment_status(data)
        invoice.currency_code = data.get("currencyCode") or data.get("CurrencyCode", "USD")

        invoice.qb_updated_at = datetime.utcnow()
        invoice.updated_at = datetime.utcnow()

        return invoice

    def _map_payment_status(self, invoice_data: Dict[str, Any]) -> str:
        """Map QB invoice payment status."""
        # Check if invoice has a metadata field indicating payment status
        if invoice_data.get("apmMetaData"):
            return "paid"
        return "unpaid"

    def _create_or_update_payment(self, data: Dict[str, Any]) -> QBPayment:
        """Create or update a payment from QB data."""
        qb_id = str(data.get("id") or data.get("Id", ""))

        payment = self.db.query(QBPayment).filter(
            QBPayment.qb_id == qb_id
        ).first()

        if not payment:
            payment = QBPayment(qb_id=qb_id)

        # Extract customer ID
        customer_ref = data.get("customerRef", {})
        if isinstance(customer_ref, dict):
            qb_customer_id = customer_ref.get("value")
            customer = self.db.query(QBCustomer).filter(
                QBCustomer.qb_id == str(qb_customer_id)
            ).first()
            if customer:
                payment.customer_id = customer.id

        # Extract invoice ID from linked txns
        txn_ref = data.get("txnRef", [])
        if isinstance(txn_ref, list) and len(txn_ref) > 0:
            invoice_ref = txn_ref[0].get("value")
            invoice = self.db.query(QBInvoice).filter(
                QBInvoice.qb_id == str(invoice_ref)
            ).first()
            if invoice:
                payment.invoice_id = invoice.id

        # Extract payment amount
        total_amount = data.get("totalAmt") or data.get("TotalAmt", 0)
        try:
            payment.amount = Decimal(str(total_amount))
        except (ValueError, TypeError):
            payment.amount = Decimal("0.00")

        # Extract payment date
        payment_date = data.get("txnDate") or data.get("TxnDate")
        if payment_date:
            payment.payment_date = payment_date

        # Extract payment method
        payment_method = data.get("paymentMethodRef", {})
        if isinstance(payment_method, dict):
            payment.payment_method = payment_method.get("name", "")

        # Extract reference number
        payment.reference_number = data.get("docNumber") or data.get("DocNumber", "")

        payment.qb_updated_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()

        return payment
