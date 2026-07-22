"""QuickBooks data sync using Intuit SDK directly."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.models.database import (
    QBCustomer, QBProduct, QBInvoice, QBInvoiceLineItem,
    QBPayment
)
from app.config import get_settings

logger = logging.getLogger(__name__)


class QuickBooksSDKSync:
    """Sync QB data using official Intuit Python SDK."""

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        logger.info("QuickBooksSDKSync initialized")

    async def sync_all(self):
        """Sync all QB data using Intuit SDK."""
        try:
            from intuitlib.client import QuickBooksClient

            logger.info("Starting QB sync via Intuit SDK...")

            # Initialize QB client with credentials
            client = QuickBooksClient(
                auth_client=None,  # We'll set tokens directly
                realm_id=self.settings.qb_realm_id,
                refresh_token=self.settings.qb_refresh_token,
            )

            await self.sync_customers(client)
            await self.sync_products(client)
            await self.sync_invoices(client)
            await self.sync_payments(client)

            logger.info("QB SDK sync completed successfully")

        except Exception as e:
            logger.error(f"QB SDK sync failed: {str(e)}")
            raise

    async def sync_customers(self, client):
        """Sync QB customers."""
        logger.info("Syncing QB customers...")
        try:
            # Use QBOS query
            query = "SELECT * FROM Customer"
            customers_data = client.query(query)

            logger.info(f"Retrieved {len(customers_data)} customers")

            for customer_data in customers_data:
                customer = self._create_or_update_customer(customer_data)
                self.db.add(customer)

            self.db.commit()
            logger.info(f"Synced {len(customers_data)} customers")
        except Exception as e:
            logger.error(f"Customer sync failed: {e}")
            self.db.rollback()

    async def sync_products(self, client):
        """Sync QB products/items."""
        logger.info("Syncing QB products...")
        try:
            query = "SELECT * FROM Item"
            items_data = client.query(query)

            logger.info(f"Retrieved {len(items_data)} items")

            for item_data in items_data:
                product = self._create_or_update_product(item_data)
                self.db.add(product)

            self.db.commit()
            logger.info(f"Synced {len(items_data)} products")
        except Exception as e:
            logger.error(f"Product sync failed: {e}")
            self.db.rollback()

    async def sync_invoices(self, client):
        """Sync QB invoices."""
        logger.info("Syncing QB invoices...")
        try:
            query = "SELECT * FROM Invoice"
            invoices_data = client.query(query)

            logger.info(f"Retrieved {len(invoices_data)} invoices")

            for invoice_data in invoices_data:
                invoice = self._create_or_update_invoice(invoice_data)
                self.db.add(invoice)

            self.db.commit()
            logger.info(f"Synced {len(invoices_data)} invoices")
        except Exception as e:
            logger.error(f"Invoice sync failed: {e}")
            self.db.rollback()

    async def sync_payments(self, client):
        """Sync QB payments."""
        logger.info("Syncing QB payments...")
        try:
            query = "SELECT * FROM Payment"
            payments_data = client.query(query)

            logger.info(f"Retrieved {len(payments_data)} payments")

            for payment_data in payments_data:
                payment = self._create_or_update_payment(payment_data)
                self.db.add(payment)

            self.db.commit()
            logger.info(f"Synced {len(payments_data)} payments")
        except Exception as e:
            logger.error(f"Payment sync failed: {e}")
            self.db.rollback()

    def _create_or_update_customer(self, data: Dict[str, Any]) -> QBCustomer:
        """Create or update a customer."""
        qb_id = str(data.get("id", ""))

        customer = self.db.query(QBCustomer).filter(
            QBCustomer.qb_id == qb_id
        ).first()

        if not customer:
            customer = QBCustomer(qb_id=qb_id)

        customer.name = data.get("displayName", "")

        email_addr = data.get("primaryEmailAddr")
        if isinstance(email_addr, dict):
            customer.email = email_addr.get("address", "")

        phone_data = data.get("phone")
        if isinstance(phone_data, dict):
            customer.phone = phone_data.get("freeFormNumber", "")

        customer.qb_updated_at = datetime.utcnow()
        customer.updated_at = datetime.utcnow()

        return customer

    def _create_or_update_product(self, data: Dict[str, Any]) -> QBProduct:
        """Create or update a product."""
        qb_id = str(data.get("id", ""))

        product = self.db.query(QBProduct).filter(
            QBProduct.qb_id == qb_id
        ).first()

        if not product:
            product = QBProduct(qb_id=qb_id)

        product.name = data.get("name", "")
        product.description = data.get("description", "")
        product.sku = data.get("sku", "")

        unit_price = data.get("unitPrice")
        if unit_price:
            try:
                product.unit_price = Decimal(str(unit_price))
            except:
                product.unit_price = Decimal("0.00")

        product.qb_updated_at = datetime.utcnow()
        product.updated_at = datetime.utcnow()

        return product

    def _create_or_update_invoice(self, data: Dict[str, Any]) -> QBInvoice:
        """Create or update an invoice."""
        qb_id = str(data.get("id", ""))

        invoice = self.db.query(QBInvoice).filter(
            QBInvoice.qb_id == qb_id
        ).first()

        if not invoice:
            invoice = QBInvoice(qb_id=qb_id)

        customer_ref = data.get("customerRef", {})
        if isinstance(customer_ref, dict):
            qb_customer_id = customer_ref.get("value")
            customer = self.db.query(QBCustomer).filter(
                QBCustomer.qb_id == str(qb_customer_id)
            ).first()
            if customer:
                invoice.customer_id = customer.id

        invoice.invoice_number = data.get("docNumber", "")
        invoice.invoice_date = data.get("txnDate")
        invoice.due_date = data.get("dueDate")

        total_amount = data.get("totalAmt", 0)
        tax_amount = data.get("taxTotal", 0)

        try:
            invoice.total = Decimal(str(total_amount))
            invoice.tax = Decimal(str(tax_amount))
        except:
            invoice.total = Decimal("0.00")
            invoice.tax = Decimal("0.00")

        invoice.status = data.get("status", "Draft")
        invoice.currency_code = data.get("currencyCode", "USD")

        invoice.qb_updated_at = datetime.utcnow()
        invoice.updated_at = datetime.utcnow()

        return invoice

    def _create_or_update_payment(self, data: Dict[str, Any]) -> QBPayment:
        """Create or update a payment."""
        qb_id = str(data.get("id", ""))

        payment = self.db.query(QBPayment).filter(
            QBPayment.qb_id == qb_id
        ).first()

        if not payment:
            payment = QBPayment(qb_id=qb_id)

        customer_ref = data.get("customerRef", {})
        if isinstance(customer_ref, dict):
            qb_customer_id = customer_ref.get("value")
            customer = self.db.query(QBCustomer).filter(
                QBCustomer.qb_id == str(qb_customer_id)
            ).first()
            if customer:
                payment.customer_id = customer.id

        total_amount = data.get("totalAmt", 0)
        try:
            payment.amount = Decimal(str(total_amount))
        except:
            payment.amount = Decimal("0.00")

        payment.payment_date = data.get("txnDate")

        payment_method = data.get("paymentMethodRef", {})
        if isinstance(payment_method, dict):
            payment.payment_method = payment_method.get("name", "")

        payment.reference_number = data.get("docNumber", "")

        payment.qb_updated_at = datetime.utcnow()
        payment.updated_at = datetime.utcnow()

        return payment
