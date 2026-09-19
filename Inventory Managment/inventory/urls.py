"""URL routes for the inventory app."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Products
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/add/", views.ProductCreateView.as_view(), name="product-add"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product-edit"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product-delete"),
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category-add"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category-edit"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category-delete"),
    # Suppliers
    path("suppliers/", views.SupplierListView.as_view(), name="supplier-list"),
    path("suppliers/add/", views.SupplierCreateView.as_view(), name="supplier-add"),
    path("suppliers/<int:pk>/edit/", views.SupplierUpdateView.as_view(), name="supplier-edit"),
    path("suppliers/<int:pk>/delete/", views.SupplierDeleteView.as_view(), name="supplier-delete"),
    # Stock transactions
    path("transactions/", views.StockTransactionListView.as_view(), name="transaction-list"),
    path("transactions/add/", views.StockTransactionCreateView.as_view(), name="transaction-add"),
]
