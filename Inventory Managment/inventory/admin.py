"""Django admin configuration for the inventory app."""

from django.contrib import admin

from .models import Category, Product, StockTransaction, Supplier


class StockTransactionInline(admin.TabularInline):
    """Show recent stock movements directly on the Product admin page."""

    model = StockTransaction
    extra = 0
    readonly_fields = ("timestamp",)
    fields = ("transaction_type", "quantity", "note", "timestamp")
    ordering = ("-timestamp",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "product_count", "created_at")
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "email", "phone")
    search_fields = ("name", "contact_person", "email")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "supplier",
        "price",
        "quantity",
        "is_low_stock",
    )
    list_filter = ("category", "supplier")
    search_fields = ("name", "sku")
    inlines = [StockTransactionInline]

    @admin.display(boolean=True, description="Low stock?")
    def is_low_stock(self, obj: Product) -> bool:
        return obj.is_low_stock


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ("product", "transaction_type", "quantity", "timestamp")
    list_filter = ("transaction_type",)
    search_fields = ("product__name", "product__sku")
    date_hierarchy = "timestamp"
