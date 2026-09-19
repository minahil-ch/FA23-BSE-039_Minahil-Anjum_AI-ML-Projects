# 📦 Inventory Management System (Django)

A full-featured **Inventory Management System** built with Django to bring
together everything from Python fundamentals to a real, multi-app web
application: Python basics → Git → virtualenv → OOP → typing → package
management → CLI mini project → GitHub → Django (apps, URLs, views,
templates, models, admin).

Track products, categories, suppliers, and stock-in/stock-out movements,
with a live dashboard, low-stock alerts, search/filtering, and a full
Django admin panel.

---

## ✨ Features

- **Dashboard** — total products, categories, suppliers, total stock value,
  low-stock alerts, and a feed of recent stock transactions.
- **Products** — full CRUD (create, read, update, delete), search by name/SKU,
  filter by category, pagination, product images.
- **Categories & Suppliers** — full CRUD with a linked product count per category.
- **Stock Transactions** — record "Stock In" / "Stock Out" movements; the
  related product's quantity is updated automatically and atomically.
- **Django Admin** — manage every model from `/admin/`, with inline stock
  transactions on the Product page, search, and filters.
- **Authentication** — login required to create/edit/delete data; browsing
  is open to everyone (adjust to taste).
- **Demo data seeding** — one command populates realistic sample data.
- **Automated tests** — model and view test coverage using Django's test framework.

---

## 🛠 Tech Stack

| Layer               | Technology                                          |
|----------------------|------------------------------------------------------|
| Language             | Python 3.11+                                         |
| Web framework        | Django 5.x                                            |
| Database             | SQLite (default, zero-config; swap for PostgreSQL in production) |
| Templating           | Django Template Language (DTL)                       |
| Frontend styling     | Bootstrap 5 (via CDN)                                 |
| Image handling       | Pillow (for `ImageField`)                             |
| Config               | `python-dotenv` + environment variables               |
| Package management   | `pip` + `requirements.txt` inside a `venv` virtual environment |
| Version control      | Git / GitHub                                          |
| Testing              | Django's built-in `TestCase` (unittest-based)         |

**Concepts demonstrated in this codebase:**

| Topic                     | Where to see it |
|----------------------------|------------------|
| Python basics               | Throughout — functions, classes, control flow |
| Git & GitHub                | `.gitignore`, project structured for a clean repo (see below) |
| Virtualenv                  | Setup instructions use `venv` |
| OOP                          | `TimeStampedModel` abstract base class, `Product.adjust_stock()`, class-based views inheriting from Django generics |
| Typing                       | Type hints on methods/properties in `models.py`, `views.py` |
| Package management (pip)    | `requirements.txt`, `.env.example` |
| CLI mini project             | `python manage.py seed_demo_data` custom management command |
| Django apps                  | Project (`config`) + app (`inventory`) split |
| URLs                          | `config/urls.py` (project) includes `inventory/urls.py` (app) |
| Views                         | Class-based views: `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, `TemplateView` |
| Templates                     | `templates/base.html` + app templates with template inheritance & includes |
| Models                        | `Category`, `Supplier`, `Product`, `StockTransaction` with relationships (FK), validators, properties |
| Admin                         | `admin.py` with `ModelAdmin`, `TabularInline`, search/filter/list_display |

---

## 📁 Project Structure

```
inventory_management_system/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/                    # Project package (settings, root URLs)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── inventory/                 # The Django app
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py              # Category, Supplier, Product, StockTransaction
│   ├── forms.py                # ModelForms (Bootstrap-styled)
│   ├── views.py                # Class-based views
│   ├── urls.py                 # App-level routes
│   ├── admin.py                 # Admin site configuration
│   ├── tests.py                 # Model + view tests
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo_data.py   # CLI command to load demo data
│   ├── static/inventory/css/style.css
│   └── templates/inventory/
│       ├── dashboard.html
│       ├── product_list.html / product_detail.html / product_form.html / product_confirm_delete.html
│       ├── category_list.html / category_form.html / category_confirm_delete.html
│       ├── supplier_list.html / supplier_form.html / supplier_confirm_delete.html
│       └── stocktransaction_list.html / stocktransaction_form.html
├── templates/
│   ├── base.html               # Shared layout (navbar, messages, footer)
│   └── registration/login.html
└── media/                       # Uploaded product images (created at runtime)
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11 or newer
- `pip` (comes with Python)
- Git (optional, for version control)

### 2. Clone or unzip the project
```bash
unzip inventory_management_system.zip
cd inventory_management_system
```

### 3. Create and activate a virtual environment
```bash
# Create
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment variables (optional but recommended)
```bash
cp .env.example .env
# then edit .env with your own SECRET_KEY, etc.
```
> The project runs out-of-the-box with sensible defaults even if you skip this step.

### 6. Apply database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create an admin (superuser) account
```bash
python manage.py createsuperuser
```

### 8. (Optional) Load demo data
```bash
python manage.py seed_demo_data
```

### 9. Run the development server
```bash
python manage.py runserver
```

Visit:
- **App:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/

### 10. Run the test suite
```bash
python manage.py test
```

---

## 🧭 Using the App

1. Log in (top-right "Login") using the superuser you created, so you can
   add/edit/delete records.
2. Visit **Categories** and **Suppliers** first to set up reference data
   (or just use the seeded demo data).
3. Add **Products**, assigning them a category, supplier, price, and
   starting quantity/reorder level.
4. Use **Transactions → Record Stock Movement** to log stock coming in or
   going out — the product's quantity updates automatically.
5. Watch the **Dashboard** for low-stock alerts and a live activity feed.

---

## 🌱 Suggested Next Steps / Extensions

- Switch `DATABASES` in `config/settings.py` to PostgreSQL for production.
- Add REST API endpoints with Django REST Framework.
- Add role-based permissions (e.g. staff vs. manager).
- Add CSV/Excel import-export for bulk product management.
- Deploy to a platform like Railway, Render, or a VPS with Gunicorn + Nginx.

---

## 📄 License

This project is provided as a learning/portfolio template — use and adapt
it freely.
