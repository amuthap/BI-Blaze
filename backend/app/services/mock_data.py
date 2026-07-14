"""Mock data generator for testing dashboard without Zoho API."""

from datetime import datetime, timedelta
from decimal import Decimal
from random import randint, choice, uniform
from sqlalchemy.orm import Session

from app.models.database import Customer, Product, Invoice, InvoiceLineItem, Payment


def generate_mock_customers(db: Session, count: int = 15) -> list:
    """Generate mock customer data."""
    customers = []
    company_names = [
        "Acme Corp", "TechFlow Inc", "DataViz Ltd", "CloudSync Solutions",
        "ByteWorks", "NeuralNet Systems", "PixelStudio", "VectorSpace Analytics",
        "InfoStream", "CyberCore", "GigaScale", "NovaLogic"
    ]

    for i in range(count):
        customer = Customer(
            zoho_id=f"CUST{i+1:04d}",
            name=company_names[i % len(company_names)] + f" {i+1}",
            email=f"contact{i+1}@company{i+1}.com",
            phone=f"+91-{randint(9000000000, 9999999999)}",
            billing_address_street=f"{randint(100, 9999)} Business Street",
            billing_address_city=choice(["Mumbai", "Bangalore", "Delhi", "Hyderabad", "Chennai"]),
            billing_address_state=choice(["MH", "KA", "DL", "TS", "TN"]),
            billing_address_zip=f"{randint(100000, 999999)}",
            billing_address_country="India",
            status="active",
            zoho_created_at=datetime.utcnow() - timedelta(days=randint(30, 365)),
            zoho_updated_at=datetime.utcnow() - timedelta(days=randint(0, 30)),
        )
        db.add(customer)
        customers.append(customer)

    db.commit()
    return customers


def generate_mock_products(db: Session, count: int = 12) -> list:
    """Generate mock product data."""
    products = []
    product_names = [
        "Premium Analytics Package", "Cloud Storage Pro", "Data Mining Suite",
        "API Integration Kit", "Dashboard Builder", "Report Generator",
        "Security Scanner", "Performance Monitor", "Backup Manager", "AI Assistant",
        "Mobile App", "Enterprise License"
    ]

    for i in range(count):
        product = Product(
            zoho_id=f"PROD{i+1:04d}",
            name=product_names[i % len(product_names)],
            description=f"High-quality product for enterprise use",
            sku=f"SKU-{i+1:05d}",
            category=choice(["Software", "Service", "Support", "License"]),
            unit="units",
            purchase_price=Decimal(str(randint(100, 5000))),
            selling_price=Decimal(str(randint(500, 10000))),
            status="active",
            zoho_created_at=datetime.utcnow() - timedelta(days=randint(60, 365)),
            zoho_updated_at=datetime.utcnow() - timedelta(days=randint(0, 30)),
        )
        db.add(product)
        products.append(product)

    db.commit()
    return products


def generate_mock_invoices(db: Session, customers: list, products: list, count: int = 50) -> list:
    """Generate mock invoice data."""
    invoices = []

    for i in range(count):
        customer = choice(customers)
        invoice_date = datetime.utcnow() - timedelta(days=randint(0, 90))

        total = Decimal("0")
        tax = Decimal(str(randint(500, 2000)))
        discount = Decimal(str(randint(0, 5000)))

        invoice = Invoice(
            zoho_id=f"INV{i+1:06d}",
            invoice_number=f"INV-{i+1:05d}",
            customer_id=customer.id,
            invoice_date=invoice_date.date(),
            due_date=(invoice_date + timedelta(days=30)).date(),
            total=Decimal(str(randint(5000, 50000))),
            tax=tax,
            discount=discount,
            status=choice(["sent", "viewed", "paid"]),
            payment_status=choice(["unpaid", "partially_paid", "paid"]),
            zoho_created_at=invoice_date,
            zoho_updated_at=invoice_date + timedelta(days=randint(0, 10)),
        )
        db.add(invoice)
        db.flush()

        # Add line items
        num_items = randint(1, 4)
        for j in range(num_items):
            product = choice(products)
            quantity = Decimal(str(randint(1, 10)))
            unit_price = product.selling_price
            item_total = quantity * unit_price

            line_item = InvoiceLineItem(
                zoho_id=f"LI{i+1:06d}{j+1:02d}",
                invoice_id=invoice.id,
                product_id=product.id,
                description=product.name,
                quantity=quantity,
                unit_price=unit_price,
                item_total=item_total,
            )
            db.add(line_item)

        invoices.append(invoice)

    db.commit()
    return invoices


def generate_mock_payments(db: Session, invoices: list) -> list:
    """Generate mock payment data."""
    payments = []

    for invoice in invoices:
        if invoice.payment_status in ["paid", "partially_paid"]:
            payment_amount = invoice.total * Decimal("0.5") if invoice.payment_status == "partially_paid" else invoice.total
            payment_date = invoice.invoice_date + timedelta(days=randint(1, 20))

            payment = Payment(
                zoho_id=f"PAY{invoice.zoho_id}",
                invoice_id=invoice.id,
                customer_id=invoice.customer_id,
                payment_date=payment_date,
                amount=payment_amount,
                payment_method=choice(["Credit Card", "Bank Transfer", "UPI", "Cheque"]),
                reference_number=f"REF{randint(100000, 999999)}",
                zoho_created_at=datetime.fromisoformat(str(payment_date)),
                zoho_updated_at=datetime.fromisoformat(str(payment_date)),
            )
            db.add(payment)
            payments.append(payment)

    db.commit()
    return payments


def populate_mock_data(db: Session) -> dict:
    """Populate database with all mock data."""
    print("\n[MOCK DATA] Generating customers...")
    customers = generate_mock_customers(db, count=15)
    print(f"  Created {len(customers)} customers")

    print("[MOCK DATA] Generating products...")
    products = generate_mock_products(db, count=12)
    print(f"  Created {len(products)} products")

    print("[MOCK DATA] Generating invoices...")
    invoices = generate_mock_invoices(db, customers, products, count=50)
    print(f"  Created {len(invoices)} invoices")

    print("[MOCK DATA] Generating payments...")
    payments = generate_mock_payments(db, invoices)
    print(f"  Created {len(payments)} payments")

    return {
        "customers": customers,
        "products": products,
        "invoices": invoices,
        "payments": payments,
    }
