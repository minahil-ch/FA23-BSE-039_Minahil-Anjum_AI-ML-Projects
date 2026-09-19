"""
Management command that populates the database with sample data so the
project can be explored immediately after `migrate` without manual data
entry.

Usage:
    python manage.py seed_demo_data
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from inventory.models import Category, Product, StockTransaction, Supplier


class Command(BaseCommand):
    help = "Seed the database with demo categories, suppliers, and products."

    def handle(self, *args, **options) -> None:
        if Product.objects.exists():
            self.stdout.write(self.style.WARNING("Demo data already present, skipping."))
            return

        electronics = Category.objects.create(name="Electronics", description="Gadgets and devices")
        stationery = Category.objects.create(name="Stationery", description="Office and school supplies")
        tools = Category.objects.create(name="Tools", description="Hand and power tools")

        acme = Supplier.objects.create(name="Acme Supplies", contact_person="John Doe", email="john@acme.example", phone="555-0100")
        globex = Supplier.objects.create(name="Globex Corp", contact_person="Jane Roe", email="jane@globex.example", phone="555-0200")

        products = [
            dict(name="Wireless Mouse", sku="EL-001", category=electronics, supplier=acme, price=Decimal("15.99"), quantity=50, reorder_level=10),
            dict(name="USB-C Cable", sku="EL-002", category=electronics, supplier=acme, price=Decimal("5.49"), quantity=8, reorder_level=15),
            dict(name="Notebook A5", sku="ST-001", category=stationery, supplier=globex, price=Decimal("2.99"), quantity=120, reorder_level=30),
            dict(name="Ballpoint Pen (Box of 10)", sku="ST-002", category=stationery, supplier=globex, price=Decimal("3.49"), quantity=6, reorder_level=10),
            dict(name="Claw Hammer", sku="TL-001", category=tools, supplier=acme, price=Decimal("14.00"), quantity=25, reorder_level=5),
        ]

        created_products = [Product.objects.create(**data) for data in products]

        StockTransaction.objects.create(
            product=created_products[0], transaction_type=StockTransaction.TransactionType.STOCK_IN,
            quantity=20, note="Initial stock delivery",
        )
        StockTransaction.objects.create(
            product=created_products[1], transaction_type=StockTransaction.TransactionType.STOCK_OUT,
            quantity=5, note="Sold to customer #1042",
        )

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(created_products)} products across "
            f"{Category.objects.count()} categories and {Supplier.objects.count()} suppliers."
        ))
