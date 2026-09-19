"""
Domain models for the Inventory Management System.

Design notes (OOP + typing):
    * `TimeStampedModel` is an abstract base class used via inheritance so
      every concrete model automatically gets `created_at` / `updated_at`
      fields (classic OOP "don't repeat yourself" via a mixin).
    * Python's `typing` module is used on plain methods/properties so the
      business logic is self-documenting, even though Django's ORM fields
      themselves are declared using Django's own field classes.
    * `Product.is_low_stock` and `Product.total_stock_value` are examples
      of encapsulating derived/business data behind a property instead of
      recomputing it ad-hoc in views/templates.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base class that adds created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """A product category, e.g. 'Electronics' or 'Stationery'."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("category-list")

    @property
    def product_count(self) -> int:
        """Number of products currently assigned to this category."""
        return self.products.count()


class Supplier(TimeStampedModel):
    """A company or person that supplies products to the warehouse."""

    name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("supplier-list")


class Product(TimeStampedModel):
    """A single stock-keeping unit (SKU) tracked in the warehouse."""

    name = models.CharField(max_length=200)
    sku = models.CharField("SKU", max_length=50, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(
        default=10,
        help_text="Quantity at or below which this product is considered low stock.",
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self) -> str:
        return reverse("product-detail", kwargs={"pk": self.pk})

    @property
    def is_low_stock(self) -> bool:
        """True when the on-hand quantity has fallen to/below reorder level."""
        return self.quantity <= self.reorder_level

    @property
    def total_stock_value(self) -> Decimal:
        """Monetary value of the current quantity on hand (price * qty)."""
        return self.price * self.quantity

    def adjust_stock(self, delta: int) -> None:
        """
        Adjust the on-hand quantity by `delta` (positive to add stock,
        negative to remove stock) and persist the change.

        This is the single place stock levels should be mutated from, so
        that side effects (e.g. future notifications) stay in one spot.
        """
        new_quantity = self.quantity + delta
        if new_quantity < 0:
            raise ValueError("Resulting stock quantity cannot be negative.")
        self.quantity = new_quantity
        self.save(update_fields=["quantity", "updated_at"])


class StockTransaction(TimeStampedModel):
    """
    An immutable ledger entry recording stock moving in or out of the
    warehouse for a given product. Saving a transaction automatically
    keeps `Product.quantity` in sync (see `save()` below).
    """

    class TransactionType(models.TextChoices):
        STOCK_IN = "IN", "Stock In"
        STOCK_OUT = "OUT", "Stock Out"

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=3, choices=TransactionType.choices
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    note = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()} - {self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs) -> None:
        """
        Persist the transaction and apply its effect to the related
        product's stock quantity. Only applied on first save (creation)
        so re-saving an existing transaction doesn't double-adjust stock.
        """
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            delta = self.quantity if self.transaction_type == self.TransactionType.STOCK_IN else -self.quantity
            self.product.adjust_stock(delta)
