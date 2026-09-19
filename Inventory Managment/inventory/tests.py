"""Basic tests for the inventory app's models and views."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, StockTransaction, Supplier


class ProductModelTests(TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="USB Cable",
            sku="USB-001",
            category=self.category,
            price=Decimal("5.99"),
            quantity=20,
            reorder_level=5,
        )

    def test_is_low_stock_false_when_quantity_above_reorder_level(self) -> None:
        self.assertFalse(self.product.is_low_stock)

    def test_is_low_stock_true_when_quantity_at_or_below_reorder_level(self) -> None:
        self.product.quantity = 5
        self.product.save()
        self.assertTrue(self.product.is_low_stock)

    def test_total_stock_value(self) -> None:
        expected = Decimal("5.99") * 20
        self.assertEqual(self.product.total_stock_value, expected)

    def test_adjust_stock_increases_quantity(self) -> None:
        self.product.adjust_stock(10)
        self.assertEqual(self.product.quantity, 30)

    def test_adjust_stock_raises_on_negative_result(self) -> None:
        with self.assertRaises(ValueError):
            self.product.adjust_stock(-100)


class StockTransactionModelTests(TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Stationery")
        self.product = Product.objects.create(
            name="Notebook", sku="NB-001", category=self.category,
            price=Decimal("2.50"), quantity=10, reorder_level=3,
        )

    def test_stock_in_increases_product_quantity(self) -> None:
        StockTransaction.objects.create(
            product=self.product,
            transaction_type=StockTransaction.TransactionType.STOCK_IN,
            quantity=5,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 15)

    def test_stock_out_decreases_product_quantity(self) -> None:
        StockTransaction.objects.create(
            product=self.product,
            transaction_type=StockTransaction.TransactionType.STOCK_OUT,
            quantity=4,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 6)


class ViewTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="tester", password="testpass123")
        self.category = Category.objects.create(name="Tools")
        self.supplier = Supplier.objects.create(name="Acme Supplies")
        self.product = Product.objects.create(
            name="Hammer", sku="TL-001", category=self.category,
            supplier=self.supplier, price=Decimal("12.00"),
            quantity=8, reorder_level=10,
        )

    def test_dashboard_loads(self) -> None:
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_product_list_loads(self) -> None:
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hammer")

    def test_product_detail_loads(self) -> None:
        response = self.client.get(reverse("product-detail", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)

    def test_product_create_requires_login(self) -> None:
        response = self.client.get(reverse("product-add"))
        self.assertEqual(response.status_code, 302)  # redirected to login

    def test_product_create_works_when_logged_in(self) -> None:
        self.client.login(username="tester", password="testpass123")
        response = self.client.post(reverse("product-add"), {
            "name": "Screwdriver",
            "sku": "TL-002",
            "category": self.category.pk,
            "price": "7.50",
            "quantity": 15,
            "reorder_level": 5,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(sku="TL-002").exists())
