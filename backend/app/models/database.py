from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Date, Numeric, Boolean, Text, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class SyncTypeEnum(str, enum.Enum):
    full = "full"
    delta = "delta"


class SyncStatusEnum(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(BigInteger, primary_key=True)
    zoho_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    billing_address_street = Column(String(500))
    billing_address_city = Column(String(100))
    billing_address_state = Column(String(100))
    billing_address_zip = Column(String(20))
    billing_address_country = Column(String(100))
    shipping_address_street = Column(String(500))
    shipping_address_city = Column(String(100))
    shipping_address_state = Column(String(100))
    shipping_address_zip = Column(String(20))
    shipping_address_country = Column(String(100))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    zoho_created_at = Column(DateTime)
    zoho_updated_at = Column(DateTime, index=True)

    invoices = relationship("Invoice", back_populates="customer")
    payments = relationship("Payment", back_populates="customer")

    __table_args__ = (
        Index("idx_customer_zoho_id", "zoho_id"),
        Index("idx_customer_updated_at", "zoho_updated_at"),
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True)
    zoho_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(100))
    category = Column(String(100))
    unit = Column(String(50))
    purchase_price = Column(Numeric(12, 2))
    selling_price = Column(Numeric(12, 2))
    tax_percentage = Column(Numeric(5, 2), default=0)
    track_inventory = Column(Boolean, default=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    zoho_created_at = Column(DateTime)
    zoho_updated_at = Column(DateTime, index=True)

    line_items = relationship("InvoiceLineItem", back_populates="product")
    sales = relationship("ProductSale", back_populates="product")

    __table_args__ = (
        Index("idx_product_zoho_id", "zoho_id"),
        Index("idx_product_updated_at", "zoho_updated_at"),
    )


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(BigInteger, primary_key=True)
    zoho_id = Column(String(50), unique=True, nullable=False, index=True)
    invoice_number = Column(String(100), nullable=False)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date)
    total = Column(Numeric(12, 2), nullable=False)
    tax = Column(Numeric(12, 2), default=0)
    shipping = Column(Numeric(12, 2), default=0)
    discount = Column(Numeric(12, 2), default=0)
    status = Column(String(50), default="draft")
    payment_status = Column(String(50), default="unpaid")
    currency_code = Column(String(10), default="USD")
    exchange_rate = Column(Numeric(12, 6), default=1)  # Rate to INR
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    zoho_created_at = Column(DateTime)
    zoho_updated_at = Column(DateTime, index=True)

    customer = relationship("Customer", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")

    __table_args__ = (
        Index("idx_invoice_zoho_id", "zoho_id"),
        Index("idx_invoice_customer_id", "customer_id"),
        Index("idx_invoice_date", "invoice_date"),
        Index("idx_invoice_updated_at", "zoho_updated_at"),
    )


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id = Column(BigInteger, primary_key=True)
    zoho_id = Column(String(50), unique=True, nullable=False, index=True)
    invoice_id = Column(BigInteger, ForeignKey("invoices.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), index=True)
    description = Column(Text)
    quantity = Column(Numeric(12, 4), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    item_tax = Column(Numeric(12, 2), default=0)
    item_total = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("Invoice", back_populates="line_items")
    product = relationship("Product", back_populates="line_items")

    __table_args__ = (
        Index("idx_line_item_invoice_id", "invoice_id"),
        Index("idx_line_item_product_id", "product_id"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True)
    zoho_id = Column(String(50), unique=True, nullable=False, index=True)
    invoice_id = Column(BigInteger, ForeignKey("invoices.id"), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50))
    reference_number = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    zoho_created_at = Column(DateTime)
    zoho_updated_at = Column(DateTime, index=True)

    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")

    __table_args__ = (
        Index("idx_payment_zoho_id", "zoho_id"),
        Index("idx_payment_invoice_id", "invoice_id"),
        Index("idx_payment_date", "payment_date"),
        Index("idx_payment_updated_at", "zoho_updated_at"),
    )


class DailyRevenue(Base):
    __tablename__ = "daily_revenue"

    date = Column(Date, primary_key=True)
    total_revenue = Column(Numeric(12, 2), nullable=False)
    invoice_count = Column(Integer, nullable=False)
    customer_count = Column(Integer, nullable=False)
    average_transaction = Column(Numeric(12, 2))
    calculated_at = Column(DateTime, default=datetime.utcnow)


class ProductSale(Base):
    __tablename__ = "product_sales"

    product_id = Column(BigInteger, ForeignKey("products.id"), primary_key=True)
    month_year = Column(String(7), primary_key=True)  # YYYY-MM
    quantity_sold = Column(Numeric(12, 4), nullable=False)
    revenue = Column(Numeric(12, 2), nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="sales")


class SyncHistory(Base):
    __tablename__ = "sync_history"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), nullable=False)
    sync_type = Column(Enum(SyncTypeEnum), nullable=False)
    records_synced = Column(Integer)
    errors_count = Column(Integer, default=0)
    last_sync_at = Column(DateTime)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(Enum(SyncStatusEnum), default=SyncStatusEnum.in_progress)
    error_message = Column(Text)

    __table_args__ = (
        Index("idx_sync_entity_type", "entity_type"),
        Index("idx_sync_status", "status"),
    )


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100))
    natural_language_query = Column(Text, nullable=False)
    generated_sql = Column(Text)
    execution_time_ms = Column(Integer)
    rows_returned = Column(Integer)
    status = Column(String(20))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True)
    provider = Column(String(50), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============= QuickBooks Tables (Virtunest Account) =============

class QBCustomer(Base):
    __tablename__ = "qb_customers"

    id = Column(BigInteger, primary_key=True)
    qb_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    billing_address = Column(Text)
    shipping_address = Column(Text)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    qb_created_at = Column(DateTime)
    qb_updated_at = Column(DateTime, index=True)

    invoices = relationship("QBInvoice", back_populates="customer")
    payments = relationship("QBPayment", back_populates="customer")

    __table_args__ = (
        Index("idx_qb_customer_qb_id", "qb_id"),
        Index("idx_qb_customer_updated_at", "qb_updated_at"),
    )


class QBProduct(Base):
    __tablename__ = "qb_products"

    id = Column(BigInteger, primary_key=True)
    qb_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(100))
    unit_price = Column(Numeric(12, 2))
    tax_included = Column(Boolean, default=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    qb_created_at = Column(DateTime)
    qb_updated_at = Column(DateTime, index=True)

    line_items = relationship("QBInvoiceLineItem", back_populates="product")

    __table_args__ = (
        Index("idx_qb_product_qb_id", "qb_id"),
        Index("idx_qb_product_updated_at", "qb_updated_at"),
    )


class QBInvoice(Base):
    __tablename__ = "qb_invoices"

    id = Column(BigInteger, primary_key=True)
    qb_id = Column(String(50), unique=True, nullable=False, index=True)
    invoice_number = Column(String(100), nullable=False)
    customer_id = Column(BigInteger, ForeignKey("qb_customers.id"), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date)
    total = Column(Numeric(12, 2), nullable=False)
    tax = Column(Numeric(12, 2), default=0)
    discount = Column(Numeric(12, 2), default=0)
    status = Column(String(50), default="draft")
    payment_status = Column(String(50), default="unpaid")
    currency_code = Column(String(10), default="USD")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    qb_created_at = Column(DateTime)
    qb_updated_at = Column(DateTime, index=True)

    customer = relationship("QBCustomer", back_populates="invoices")
    line_items = relationship("QBInvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("QBPayment", back_populates="invoice")

    __table_args__ = (
        Index("idx_qb_invoice_qb_id", "qb_id"),
        Index("idx_qb_invoice_customer_id", "customer_id"),
        Index("idx_qb_invoice_date", "invoice_date"),
        Index("idx_qb_invoice_updated_at", "qb_updated_at"),
    )


class QBInvoiceLineItem(Base):
    __tablename__ = "qb_invoice_line_items"

    id = Column(BigInteger, primary_key=True)
    qb_id = Column(String(50), unique=True, nullable=False, index=True)
    invoice_id = Column(BigInteger, ForeignKey("qb_invoices.id"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("qb_products.id"), index=True)
    description = Column(Text)
    quantity = Column(Numeric(12, 4), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    item_total = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice = relationship("QBInvoice", back_populates="line_items")
    product = relationship("QBProduct", back_populates="line_items")

    __table_args__ = (
        Index("idx_qb_line_item_invoice_id", "invoice_id"),
        Index("idx_qb_line_item_product_id", "product_id"),
    )


class QBPayment(Base):
    __tablename__ = "qb_payments"

    id = Column(BigInteger, primary_key=True)
    qb_id = Column(String(50), unique=True, nullable=False, index=True)
    invoice_id = Column(BigInteger, ForeignKey("qb_invoices.id"), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey("qb_customers.id"), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String(50))
    reference_number = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    qb_created_at = Column(DateTime)
    qb_updated_at = Column(DateTime, index=True)

    invoice = relationship("QBInvoice", back_populates="payments")
    customer = relationship("QBCustomer", back_populates="payments")

    __table_args__ = (
        Index("idx_qb_payment_qb_id", "qb_id"),
        Index("idx_qb_payment_invoice_id", "invoice_id"),
        Index("idx_qb_payment_date", "payment_date"),
        Index("idx_qb_payment_updated_at", "qb_updated_at"),
    )
