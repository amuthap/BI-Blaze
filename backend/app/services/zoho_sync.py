import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.db.database import SessionLocal
from app.models.database import (
    Customer, Product, Invoice, InvoiceLineItem, Payment,
    SyncHistory, SyncTypeEnum, SyncStatusEnum
)
from app.services.zoho_api_client import ZohoAPIClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ZohoSyncService:
    """Service for syncing data from Zoho Books to PostgreSQL."""

    ENTITIES = ["customers", "items", "invoices", "payments"]

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()
        self.zoho_client = ZohoAPIClient()

    def get_last_sync_time(self, entity_type: str) -> Optional[datetime]:
        """Get the timestamp of the last successful sync for an entity."""
        last_sync = (
            self.db.query(SyncHistory)
            .filter(
                and_(
                    SyncHistory.entity_type == entity_type,
                    SyncHistory.status == SyncStatusEnum.completed,
                )
            )
            .order_by(desc(SyncHistory.completed_at))
            .first()
        )

        if last_sync and last_sync.last_sync_at:
            return last_sync.last_sync_at

        return None

    def create_sync_record(
        self,
        entity_type: str,
        sync_type: SyncTypeEnum,
    ) -> SyncHistory:
        """Create a new sync history record."""
        sync_record = SyncHistory(
            entity_type=entity_type,
            sync_type=sync_type,
            status=SyncStatusEnum.in_progress,
            started_at=datetime.utcnow(),
        )
        self.db.add(sync_record)
        self.db.commit()
        return sync_record

    def update_sync_record(
        self,
        sync_record: SyncHistory,
        records_synced: int,
        errors_count: int = 0,
        error_message: Optional[str] = None,
        status: SyncStatusEnum = SyncStatusEnum.completed,
    ):
        """Update sync history record after sync completes."""
        sync_record.records_synced = records_synced
        sync_record.errors_count = errors_count
        sync_record.status = status
        sync_record.completed_at = datetime.utcnow()
        sync_record.last_sync_at = datetime.utcnow()
        sync_record.error_message = error_message

        self.db.commit()
        logger.info(
            f"Sync {sync_record.id} completed: {records_synced} records, "
            f"{errors_count} errors, status={status}"
        )

    def sync_customers(self, full_sync: bool = False) -> int:
        """Sync customers from Zoho to database."""
        logger.info(f"Starting customer sync (full={full_sync})")
        sync_record = self.create_sync_record("customers", SyncTypeEnum.full if full_sync else SyncTypeEnum.delta)

        try:
            last_sync_time = None if full_sync else self.get_last_sync_time("customers")

            # Fetch from Zoho
            zoho_customers = self.zoho_client.get_customers(modified_since=last_sync_time)
            logger.info(f"Fetched {len(zoho_customers)} customers from Zoho")

            errors = 0
            successful = 0
            for customer_data in zoho_customers:
                try:
                    self._upsert_customer(customer_data)
                    successful += 1
                except Exception as e:
                    logger.error(f"Error syncing customer {customer_data.get('customer_id')}: {e}")
                    errors += 1

            self.update_sync_record(sync_record, successful, errors_count=errors)
            return successful

        except Exception as e:
            logger.error(f"Customer sync failed: {e}")
            self.update_sync_record(
                sync_record,
                records_synced=0,
                error_message=str(e),
                status=SyncStatusEnum.failed,
            )
            raise

    def _upsert_customer(self, data: Dict[str, Any]):
        """Insert or update a customer."""
        zoho_id = data.get("customer_id")
        customer = self.db.query(Customer).filter_by(zoho_id=zoho_id).first()

        customer_obj = customer or Customer(zoho_id=zoho_id)
        customer_obj.name = data.get("customer_name", "")
        customer_obj.email = data.get("email")
        customer_obj.phone = data.get("phone")
        customer_obj.status = data.get("status", "active")

        # Billing address
        if data.get("billing_address"):
            addr = data["billing_address"]
            customer_obj.billing_address_street = addr.get("street1")
            customer_obj.billing_address_city = addr.get("city")
            customer_obj.billing_address_state = addr.get("state")
            customer_obj.billing_address_zip = addr.get("zip")
            customer_obj.billing_address_country = addr.get("country")

        # Shipping address
        if data.get("shipping_address"):
            addr = data["shipping_address"]
            customer_obj.shipping_address_street = addr.get("street1")
            customer_obj.shipping_address_city = addr.get("city")
            customer_obj.shipping_address_state = addr.get("state")
            customer_obj.shipping_address_zip = addr.get("zip")
            customer_obj.shipping_address_country = addr.get("country")

        # Timestamps
        if data.get("created_time"):
            customer_obj.zoho_created_at = datetime.fromisoformat(data["created_time"].replace("Z", "+00:00"))
        if data.get("modified_time"):
            customer_obj.zoho_updated_at = datetime.fromisoformat(data["modified_time"].replace("Z", "+00:00"))

        self.db.add(customer_obj)
        self.db.commit()

    def sync_products(self, full_sync: bool = False) -> int:
        """Sync products (items) from Zoho to database."""
        logger.info(f"Starting product sync (full={full_sync})")
        sync_record = self.create_sync_record("items", SyncTypeEnum.full if full_sync else SyncTypeEnum.delta)

        try:
            last_sync_time = None if full_sync else self.get_last_sync_time("items")

            # Fetch from Zoho
            zoho_products = self.zoho_client.get_products(modified_since=last_sync_time)
            logger.info(f"Fetched {len(zoho_products)} products from Zoho")

            errors = 0
            successful = 0
            for product_data in zoho_products:
                try:
                    self._upsert_product(product_data)
                    successful += 1
                except Exception as e:
                    logger.error(f"Error syncing product {product_data.get('item_id')}: {e}")
                    errors += 1

            self.update_sync_record(sync_record, successful, errors_count=errors)
            return successful

        except Exception as e:
            logger.error(f"Product sync failed: {e}")
            self.update_sync_record(
                sync_record,
                records_synced=0,
                error_message=str(e),
                status=SyncStatusEnum.failed,
            )
            raise

    def _upsert_product(self, data: Dict[str, Any]):
        """Insert or update a product."""
        zoho_id = data.get("item_id")
        product = self.db.query(Product).filter_by(zoho_id=zoho_id).first()

        product_obj = product or Product(zoho_id=zoho_id)
        product_obj.name = data.get("name", "")
        product_obj.description = data.get("description")
        product_obj.sku = data.get("sku")
        product_obj.category = data.get("item_type")
        product_obj.unit = data.get("unit")
        product_obj.purchase_price = Decimal(str(data.get("purchase_price", 0)))
        product_obj.selling_price = Decimal(str(data.get("rate", 0)))
        product_obj.status = "active"

        if data.get("created_time"):
            product_obj.zoho_created_at = datetime.fromisoformat(data["created_time"].replace("Z", "+00:00"))
        if data.get("modified_time"):
            product_obj.zoho_updated_at = datetime.fromisoformat(data["modified_time"].replace("Z", "+00:00"))

        self.db.add(product_obj)
        self.db.commit()

    def sync_invoices(self, full_sync: bool = False) -> int:
        """Sync invoices from Zoho to database."""
        logger.info(f"Starting invoice sync (full={full_sync})")
        sync_record = self.create_sync_record("invoices", SyncTypeEnum.full if full_sync else SyncTypeEnum.delta)

        try:
            last_sync_time = None if full_sync else self.get_last_sync_time("invoices")

            # Fetch from Zoho
            zoho_invoices = self.zoho_client.get_invoices(modified_since=last_sync_time)
            logger.info(f"Fetched {len(zoho_invoices)} invoices from Zoho")

            errors = 0
            successful = 0
            for invoice_data in zoho_invoices:
                try:
                    self._upsert_invoice(invoice_data)
                    successful += 1
                except Exception as e:
                    logger.error(f"Error syncing invoice {invoice_data.get('invoice_id')}: {e}")
                    errors += 1

            self.update_sync_record(sync_record, successful, errors_count=errors)
            return successful

        except Exception as e:
            logger.error(f"Invoice sync failed: {e}")
            self.update_sync_record(
                sync_record,
                records_synced=0,
                error_message=str(e),
                status=SyncStatusEnum.failed,
            )
            raise

    def _get_or_create_customer_from_invoice(self, invoice_data: Dict[str, Any]) -> Customer:
        """Extract customer info from invoice data and create/update customer."""
        customer_zoho_id = invoice_data.get("customer_id")
        if not customer_zoho_id:
            return None

        customer = self.db.query(Customer).filter_by(zoho_id=customer_zoho_id).first()
        if customer:
            return customer

        # Create new customer from invoice data
        customer = Customer(
            zoho_id=customer_zoho_id,
            name=invoice_data.get("customer_name", "Unknown"),
            email=invoice_data.get("email"),
            phone=invoice_data.get("phone"),
            status="active"
        )
        self.db.add(customer)
        self.db.flush()
        logger.info(f"Created customer {customer.name} (ID: {customer_zoho_id}) from invoice")
        return customer

    def _upsert_invoice(self, data: Dict[str, Any]):
        """Insert or update an invoice with line items."""
        zoho_id = data.get("invoice_id")
        invoice = self.db.query(Invoice).filter_by(zoho_id=zoho_id).first()

        # Get or create customer from invoice data
        customer = self._get_or_create_customer_from_invoice(data)
        if not customer:
            logger.warning(f"No customer data in invoice {zoho_id}")
            return

        invoice_obj = invoice or Invoice(zoho_id=zoho_id)
        invoice_obj.invoice_number = data.get("invoice_number", "")
        invoice_obj.customer_id = customer.id

        # Handle invoice_date - Zoho uses "date" field, not "invoice_date"
        invoice_date_str = data.get("date") or data.get("invoice_date") or data.get("issued_date", "")
        if invoice_date_str:
            invoice_obj.invoice_date = datetime.fromisoformat(invoice_date_str).date()
        else:
            logger.warning(f"No invoice date found for invoice {zoho_id}, using today's date")
            invoice_obj.invoice_date = datetime.utcnow().date()

        # Handle due_date - optional
        due_date_str = data.get("due_date") or data.get("payment_expected_date", "")
        if due_date_str:
            invoice_obj.due_date = datetime.fromisoformat(due_date_str).date()

        invoice_obj.total = Decimal(str(data.get("total", 0)))
        invoice_obj.tax = Decimal(str(data.get("tax_total", 0)))
        invoice_obj.discount = Decimal(str(data.get("discount", 0)))

        # Zoho "status" field contains PAYMENT status (paid, unpaid, overdue)
        # Map to payment_status
        zoho_status = data.get("status", "unpaid").lower()
        invoice_obj.payment_status = zoho_status

        # Invoice status (lifecycle: draft, sent, viewed, accepted, declined)
        # Zoho doesn't provide this, so infer from payment status
        if zoho_status == "paid":
            invoice_obj.status = "accepted"
        else:
            invoice_obj.status = "sent"

        # Store currency and exchange rate
        invoice_obj.currency_code = data.get("currency_code", "USD")
        invoice_obj.exchange_rate = Decimal(str(data.get("exchange_rate", 1)))

        if data.get("created_time"):
            invoice_obj.zoho_created_at = datetime.fromisoformat(data["created_time"].replace("Z", "+00:00"))
        if data.get("modified_time"):
            invoice_obj.zoho_updated_at = datetime.fromisoformat(data["modified_time"].replace("Z", "+00:00"))

        self.db.add(invoice_obj)
        self.db.flush()

        # Sync line items
        existing_line_items = self.db.query(InvoiceLineItem).filter_by(invoice_id=invoice_obj.id).all()
        existing_ids = {li.zoho_id for li in existing_line_items}

        for line_item_data in data.get("line_items", []):
            zoho_line_id = line_item_data.get("line_item_id")
            if zoho_line_id in existing_ids:
                continue

            # Find product if it exists
            sku = line_item_data.get("sku")
            product = None
            if sku:
                product = self.db.query(Product).filter_by(sku=sku).first()

            line_item = InvoiceLineItem(
                zoho_id=zoho_line_id,
                invoice_id=invoice_obj.id,
                product_id=product.id if product else None,
                description=line_item_data.get("name"),
                quantity=Decimal(str(line_item_data.get("quantity", 0))),
                unit_price=Decimal(str(line_item_data.get("rate", 0))),
                item_tax=Decimal(str(line_item_data.get("tax", 0))),
                item_total=Decimal(str(line_item_data.get("item_total", 0))),
            )
            self.db.add(line_item)

        self.db.commit()

    def sync_payments(self, full_sync: bool = False) -> int:
        """Sync payments from Zoho to database."""
        logger.info(f"Starting payment sync (full={full_sync})")
        sync_record = self.create_sync_record("payments", SyncTypeEnum.full if full_sync else SyncTypeEnum.delta)

        try:
            last_sync_time = None if full_sync else self.get_last_sync_time("payments")

            # Fetch from Zoho
            zoho_payments = self.zoho_client.get_payments(modified_since=last_sync_time)
            logger.info(f"Fetched {len(zoho_payments)} payments from Zoho")

            errors = 0
            successful = 0
            for payment_data in zoho_payments:
                try:
                    self._upsert_payment(payment_data)
                    successful += 1
                except Exception as e:
                    logger.error(f"Error syncing payment {payment_data.get('payment_id')}: {e}")
                    errors += 1

            self.update_sync_record(sync_record, successful, errors_count=errors)
            return successful

        except Exception as e:
            logger.error(f"Payment sync failed: {e}")
            self.update_sync_record(
                sync_record,
                records_synced=0,
                error_message=str(e),
                status=SyncStatusEnum.failed,
            )
            raise

    def _upsert_payment(self, data: Dict[str, Any]):
        """Insert or update a payment."""
        zoho_id = data.get("payment_id")
        payment = self.db.query(Payment).filter_by(zoho_id=zoho_id).first()

        # Get invoice and customer
        invoice_zoho_id = data.get("invoice_id")
        invoice = self.db.query(Invoice).filter_by(zoho_id=invoice_zoho_id).first()
        if not invoice:
            logger.warning(f"Invoice {invoice_zoho_id} not found for payment {zoho_id}")
            return

        payment_obj = payment or Payment(zoho_id=zoho_id)
        payment_obj.invoice_id = invoice.id
        payment_obj.customer_id = invoice.customer_id
        payment_obj.payment_date = datetime.fromisoformat(data.get("date", "")).date()
        payment_obj.amount = Decimal(str(data.get("amount", 0)))
        payment_obj.payment_method = data.get("payment_mode")

        if data.get("created_time"):
            payment_obj.zoho_created_at = datetime.fromisoformat(data["created_time"].replace("Z", "+00:00"))
        if data.get("modified_time"):
            payment_obj.zoho_updated_at = datetime.fromisoformat(data["modified_time"].replace("Z", "+00:00"))

        self.db.add(payment_obj)
        self.db.commit()

    def sync_all(self, full_sync: bool = False) -> Dict[str, int]:
        """Sync all entities from Zoho."""
        logger.info(f"Starting full data sync (full={full_sync})")
        results = {}

        try:
            # Sync products first (no dependencies)
            results["products"] = self.sync_products(full_sync=full_sync)
            # Then customers (no dependencies)
            results["customers"] = self.sync_customers(full_sync=full_sync)
            # Then invoices (depends on customers)
            results["invoices"] = self.sync_invoices(full_sync=full_sync)
            # Finally payments (depends on invoices)
            results["payments"] = self.sync_payments(full_sync=full_sync)

            logger.info(f"Sync completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise

        finally:
            self.db.close()
