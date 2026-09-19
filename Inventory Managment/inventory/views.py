"""
Views for the inventory app.

Built entirely with Django's class-based generic views to demonstrate
OOP concepts in practice: each view class *inherits* shared behaviour
from Django's generics (ListView, DetailView, CreateView, ...) and only
overrides the small pieces that differ (querysets, success URLs, extra
context).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import CategoryForm, ProductForm, StockTransactionForm, SupplierForm
from .models import Category, Product, StockTransaction, Supplier


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardView(TemplateView):
    """Landing page with high-level warehouse stats and alerts."""

    template_name = "inventory/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        context["total_products"] = products.count()
        context["total_categories"] = Category.objects.count()
        context["total_suppliers"] = Supplier.objects.count()
        context["total_stock_value"] = sum(
            (p.total_stock_value for p in products), Decimal("0.00")
        )
        context["low_stock_products"] = products.filter(
            quantity__lte=F("reorder_level")
        )
        context["recent_transactions"] = StockTransaction.objects.select_related(
            "product"
        )[:8]
        return context


# ---------------------------------------------------------------------------
# Product views
# ---------------------------------------------------------------------------
class ProductListView(ListView):
    model = Product
    template_name = "inventory/product_list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Product]:
        queryset = Product.objects.select_related("category", "supplier")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(sku__icontains=query)
            )
        category_id = self.request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        # Build query string for pagination links (preserves filters)
        params = self.request.GET.copy()
        params.pop("page", None)
        context["filter_params"] = params.urlencode()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "inventory/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["transactions"] = self.object.transactions.all()[:20]
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"

    def form_valid(self, form: ProductForm):
        messages.success(self.request, f"Product '{form.instance.name}' created.")
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"

    def form_valid(self, form: ProductForm):
        messages.success(self.request, f"Product '{form.instance.name}' updated.")
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "inventory/product_confirm_delete.html"
    success_url = reverse_lazy("product-list")

    def form_valid(self, form):
        messages.success(self.request, "Product deleted.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Category views
# ---------------------------------------------------------------------------
class CategoryListView(ListView):
    model = Category
    template_name = "inventory/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("category-list")


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "inventory/category_form.html"
    success_url = reverse_lazy("category-list")


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "inventory/category_confirm_delete.html"
    success_url = reverse_lazy("category-list")


# ---------------------------------------------------------------------------
# Supplier views
# ---------------------------------------------------------------------------
class SupplierListView(ListView):
    model = Supplier
    template_name = "inventory/supplier_list.html"
    context_object_name = "suppliers"


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"
    success_url = reverse_lazy("supplier-list")


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "inventory/supplier_form.html"
    success_url = reverse_lazy("supplier-list")


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = "inventory/supplier_confirm_delete.html"
    success_url = reverse_lazy("supplier-list")


# ---------------------------------------------------------------------------
# Stock transactions (stock in / stock out)
# ---------------------------------------------------------------------------
class StockTransactionCreateView(LoginRequiredMixin, CreateView):
    model = StockTransaction
    form_class = StockTransactionForm
    template_name = "inventory/stocktransaction_form.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form: StockTransactionForm):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Recorded {form.instance.get_transaction_type_display()} "
            f"of {form.instance.quantity} x {form.instance.product.name}.",
        )
        return response


class StockTransactionListView(ListView):
    model = StockTransaction
    template_name = "inventory/stocktransaction_list.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[StockTransaction]:
        return StockTransaction.objects.select_related("product").all()
