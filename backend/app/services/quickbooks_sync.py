"""QuickBooks data sync service."""

import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal

from app.config import get_settings
from app.models.database import (
    QBCustomer, QBProduct, QBInvoice, QBInvoiceLineItem,
    QBPayment, OAuthToken, SyncHistory, SyncStatusEnum
)
from app.services.quickbooks_oauth_v2 import QuickBooksOAuthV2

logger = logging.getLogger(__name__)
settings = get_settings()

# Use production environment for Virtunest QB account
ENVIRONMENT = "production"
QB_API_BASE = "https://quickbooks.api.intuit.com" if ENVIRONMENT == "production" else "https://sandbox-quickbooks.api.intuit.com"


class QuickBooksSync:
    """Sync data from QuickBooks Online."""

    def __init__(self, db: Session):
        self.db = db
        self.oauth = QuickBooksOAuthV2()
        # Get realm_id from database token
        token = db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()
        if token and token.realm_id:
            self.realm_id = token.realm_id
        else:
            self.realm_id = settings.qb_realm_id
        self.access_token = None
        logger.info(f"QuickBooksSync initialized with realm_id: {self.realm_id}")

    async def sync_all(self):
        """Sync all data from QuickBooks."""
        try:
            # Get token and refresh if expired
            token = self.db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()
            if not token:
                logger.error("No QuickBooks token found")
                return

            logger.info(f"Found QB token - Access token length: {len(token.access_token) if token.access_token else 0}, Realm ID: {token.realm_id}")

            # Check if token is expired and refresh if needed
            from datetime import datetime, timedelta
            if token.expires_at and datetime.utcnow() > token.expires_at - timedelta(minutes=5):
                logger.info("Token expired or expiring soon, refreshing...")
                try:
                    new_token_data = self.oauth.refresh_token(token.refresh_token, token.realm_id)
                    self.oauth.save_token(self.db, new_token_data)
                    token = self.db.query(OAuthToken).filter(OAuthToken.provider == "quickbooks").first()
                    logger.info("Token refreshed successfully")
                except Exception as e:
                    logger.error(f"Token refresh failed: {str(e)}")
                    raise

            self.access_token = token.access_token

            logger.info("Starting QuickBooks sync...")

            # Sync customers
            await self.sync_customers()

            # Sync products
            await self.sync_products()

            # Sync invoices
            await self.sync_invoices()

            # Sync payments
            await self.sync_payments()

            logger.info("QuickBooks sync completed successfully")

        except Exception as e:
            logger.error(f"QuickBooks sync failed: {str(e)}")
            raise

    async def _make_request(self, endpoint: str, query: str = None) -> dict:
        """Make authenticated request to QuickBooks API with retry logic."""
        logger.info(f"Making QB request - Token exists: {bool(self.access_token)}, Token length: {len(self.access_token) if self.access_token else 0}, Realm ID: {self.realm_id}")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        url = f"{QB_API_BASE}/v2/company/{self.realm_id}/query"

        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        params={"query": query},
                        headers=headers,
                        timeout=30.0,
                        follow_redirects=False
                    )

                    # Capture intuit_tid for debugging
                    intuit_tid = response.headers.get("intuit_tid", "N/A")

                    if response.status_code == 403:
                        logger.error(f"QB API 403 Forbidden (intuit_tid: {intuit_tid})")
                        logger.error(f"URL: {url}")
                        logger.error(f"Response: {response.text}")
                        logger.error(f"Headers: {dict(response.headers)}")
                        response.raise_for_status()

                    if response.status_code == 500:
                        logger.warning(f"QB API 500 error (intuit_tid: {intuit_tid}, attempt {attempt+1}/{max_retries})")
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                            import asyncio
                            await asyncio.sleep(wait_time)
                            continue
                        logger.error(f"QB API failed after {max_retries} attempts")
                        response.raise_for_status()

                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPError as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                import asyncio
                await asyncio.sleep(wait_time)

    async def sync_customers(self):
        """Sync QuickBooks customers."""
        logger.info("Syncing QuickBooks customers...")

        try:
            query = "select * from Customer maxresults 1000"
            data = await self._make_request("customer", query)

            if "QueryResponse" in data and "Customer" in data["QueryResponse"]:
                customers = data["QueryResponse"]["Customer"]
                if not isinstance(customers, list):
                    customers = [customers]

                for cust_data in customers:
                    qb_id = cust_data.get("Id")
                    if not qb_id:
                        continue

                    # Check if customer exists
                    customer = self.db.query(QBCustomer).filter(QBCustomer.qb_id == qb_id).first()

                    name = cust_data.get("DisplayName", "Unknown")
                    email = None
                    phone = None

                    if "PrimaryEmailAddr" in cust_data:
                        email = cust_data["PrimaryEmailAddr"].get("Address")
                    if "PrimaryPhone" in cust_data:
                        phone = cust_data["PrimaryPhone"].get("FreeFormNumber")

                    if customer:
                        customer.name = name
                        customer.email = email
                        customer.phone = phone
                        customer.qb_updated_at = datetime.utcnow()
                    else:
                        customer = QBCustomer(
                            qb_id=qb_id,
                            name=name,
                            email=email,
                            phone=phone,
                            qb_created_at=datetime.utcnow(),
                            qb_updated_at=datetime.utcnow()
                        )
                        self.db.add(customer)

                self.db.commit()
                logger.info(f"Synced {len(customers)} QuickBooks customers")

        except Exception as e:
            logger.error(f"Error syncing customers: {str(e)}")
            raise

    async def sync_products(self):
        """Sync QuickBooks products."""
        logger.info("Syncing QuickBooks products...")

        try:
            query = "select * from Item maxresults 1000"
            data = await self._make_request("product", query)

            if "QueryResponse" in data and "Item" in data["QueryResponse"]:
                products = data["QueryResponse"]["Item"]
                if not isinstance(products, list):
                    products = [products]

                for prod_data in products:
                    qb_id = prod_data.get("Id")
                    if not qb_id:
                        continue

                    product = self.db.query(QBProduct).filter(QBProduct.qb_id == qb_id).first()

                    name = prod_data.get("Name", "Unknown")
                    unit_price = None

                    if "UnitPrice" in prod_data:
                        unit_price = Decimal(str(prod_data["UnitPrice"]))

                    if product:
                        product.name = name
                        product.unit_price = unit_price
                        product.qb_updated_at = datetime.utcnow()
                    else:
                        product = QBProduct(
                            qb_id=qb_id,
                            name=name,
                            unit_price=unit_price,
                            qb_created_at=datetime.utcnow(),
                            qb_updated_at=datetime.utcnow()
                        )
                        self.db.add(product)

                self.db.commit()
                logger.info(f"Synced {len(products)} QuickBooks products")

        except Exception as e:
            logger.error(f"Error syncing products: {str(e)}")
            raise

    async def sync_invoices(self):
        """Sync QuickBooks invoices."""
        logger.info("Syncing QuickBooks invoices...")

        try:
            query = "select * from Invoice maxresults 1000"
            data = await self._make_request("invoice", query)

            if "QueryResponse" in data and "Invoice" in data["QueryResponse"]:
                invoices = data["QueryResponse"]["Invoice"]
                if not isinstance(invoices, list):
                    invoices = [invoices]

                for inv_data in invoices:
                    qb_id = inv_data.get("Id")
                    if not qb_id:
                        continue

                    # Get customer
                    cust_qb_id = inv_data.get("CustomerRef", {}).get("value")
                    customer = self.db.query(QBCustomer).filter(QBCustomer.qb_id == cust_qb_id).first()

                    if not customer:
                        continue

                    invoice = self.db.query(QBInvoice).filter(QBInvoice.qb_id == qb_id).first()

                    invoice_number = inv_data.get("DocNumber", "")
                    invoice_date = inv_data.get("TxnDate")
                    due_date = inv_data.get("DueDate")
                    total = Decimal(str(inv_data.get("TotalAmt", 0)))
                    tax = Decimal(str(inv_data.get("TaxTotal", 0)))

                    if invoice:
                        invoice.invoice_number = invoice_number
                        invoice.invoice_date = invoice_date
                        invoice.due_date = due_date
                        invoice.total = total
                        invoice.tax = tax
                        invoice.qb_updated_at = datetime.utcnow()
                    else:
                        invoice = QBInvoice(
                            qb_id=qb_id,
                            invoice_number=invoice_number,
                            customer_id=customer.id,
                            invoice_date=invoice_date,
                            due_date=due_date,
                            total=total,
                            tax=tax,
                            qb_created_at=datetime.utcnow(),
                            qb_updated_at=datetime.utcnow()
                        )
                        self.db.add(invoice)
                        self.db.flush()

                    # Sync line items
                    if "Line" in inv_data:
                        for line in inv_data["Line"]:
                            if line.get("DetailType") == "SalesItemLineDetail":
                                line_qb_id = f"{qb_id}_{line.get('Id')}"
                                item_ref = line.get("SalesItemLineDetail", {}).get("ItemRef", {}).get("value")

                                line_item = self.db.query(QBInvoiceLineItem).filter(
                                    QBInvoiceLineItem.qb_id == line_qb_id
                                ).first()

                                quantity = Decimal(str(line.get("SalesItemLineDetail", {}).get("Qty", 0)))
                                unit_price = Decimal(str(line.get("SalesItemLineDetail", {}).get("UnitPrice", 0)))
                                item_total = Decimal(str(line.get("Amount", 0)))

                                product = None
                                if item_ref:
                                    product = self.db.query(QBProduct).filter(QBProduct.qb_id == item_ref).first()

                                if line_item:
                                    line_item.quantity = quantity
                                    line_item.unit_price = unit_price
                                    line_item.item_total = item_total
                                else:
                                    line_item = QBInvoiceLineItem(
                                        qb_id=line_qb_id,
                                        invoice_id=invoice.id,
                                        product_id=product.id if product else None,
                                        quantity=quantity,
                                        unit_price=unit_price,
                                        item_total=item_total
                                    )
                                    self.db.add(line_item)

                self.db.commit()
                logger.info(f"Synced {len(invoices)} QuickBooks invoices")

        except Exception as e:
            logger.error(f"Error syncing invoices: {str(e)}")
            raise

    async def sync_payments(self):
        """Sync QuickBooks payments."""
        logger.info("Syncing QuickBooks payments...")

        try:
            query = "select * from Payment maxresults 1000"
            data = await self._make_request("payment", query)

            if "QueryResponse" in data and "Payment" in data["QueryResponse"]:
                payments = data["QueryResponse"]["Payment"]
                if not isinstance(payments, list):
                    payments = [payments]

                for pmt_data in payments:
                    qb_id = pmt_data.get("Id")
                    if not qb_id:
                        continue

                    # Get customer
                    cust_qb_id = pmt_data.get("CustomerRef", {}).get("value")
                    customer = self.db.query(QBCustomer).filter(QBCustomer.qb_id == cust_qb_id).first()

                    if not customer:
                        continue

                    # Get invoice reference
                    invoice_ref = None
                    if "Line" in pmt_data:
                        for line in pmt_data["Line"]:
                            if "LinkedTxn" in line:
                                for linked in line["LinkedTxn"]:
                                    if linked.get("TxnType") == "Invoice":
                                        invoice_ref = linked.get("TxnId")

                    invoice = None
                    if invoice_ref:
                        invoice = self.db.query(QBInvoice).filter(QBInvoice.qb_id == invoice_ref).first()

                    payment = self.db.query(QBPayment).filter(QBPayment.qb_id == qb_id).first()

                    payment_date = pmt_data.get("TxnDate")
                    amount = Decimal(str(pmt_data.get("TotalAmt", 0)))

                    if payment:
                        payment.payment_date = payment_date
                        payment.amount = amount
                        payment.qb_updated_at = datetime.utcnow()
                    else:
                        payment = QBPayment(
                            qb_id=qb_id,
                            customer_id=customer.id,
                            invoice_id=invoice.id if invoice else None,
                            payment_date=payment_date,
                            amount=amount,
                            qb_created_at=datetime.utcnow(),
                            qb_updated_at=datetime.utcnow()
                        )
                        self.db.add(payment)

                self.db.commit()
                logger.info(f"Synced {len(payments)} QuickBooks payments")

        except Exception as e:
            logger.error(f"Error syncing payments: {str(e)}")
            raise
