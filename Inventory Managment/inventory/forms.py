"""ModelForms used by the inventory app's create/update views."""

from __future__ import annotations

from django import forms

from .models import Category, Product, StockTransaction, Supplier


class BootstrapModelForm(forms.ModelForm):
    """
    Base form that adds the correct Bootstrap 5 CSS classes to every field
    widget automatically — `form-select` for dropdowns, `form-control` for
    all other inputs — so individual forms below stay short.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get("class", "")
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = f"{existing} form-select".strip()
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{existing} form-check-input".strip()
            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = f"{existing} form-control".strip()
                widget.attrs.setdefault("rows", 3)
            else:
                widget.attrs["class"] = f"{existing} form-control".strip()


class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class SupplierForm(BootstrapModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "email", "phone", "address"]


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "supplier",
            "description",
            "price",
            "quantity",
            "reorder_level",
            "image",
        ]


class StockTransactionForm(BootstrapModelForm):
    class Meta:
        model = StockTransaction
        fields = ["product", "transaction_type", "quantity", "note"]
