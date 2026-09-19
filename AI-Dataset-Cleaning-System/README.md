# 🤖 AI Dataset Cleaning System

> A full-stack Django web application that uses AI/ML techniques to automatically detect data quality issues, apply intelligent cleaning operations, generate visualizations, and export PDF reports — all through an intuitive browser interface.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Libraries Used](#-libraries-used)
- [Project Structure](#-project-structure)
- [Key Modules Explained](#-key-modules-explained)
- [Database Models](#-database-models)
- [API Endpoints](#-api-endpoints)
- [Setup & Run Instructions](#-setup--run-instructions)
- [Environment Variables](#-environment-variables)
- [Viva Guide — Common Questions](#-viva-guide--common-questions)

---

## 🌟 Project Overview

The **AI Dataset Cleaning System** is a Django-based web platform that allows data scientists, analysts, and students to:

1. **Upload** CSV or Excel datasets
2. **Analyze** them automatically (missing values, duplicates, data types, memory usage)
3. **Get AI suggestions** on what cleaning operations to apply
4. **Apply cleaning operations** (fill missing values, remove duplicates, detect outliers using ML, normalize text, encode categorical data, etc.)
5. **Visualize** data distributions and quality metrics using interactive Plotly charts
6. **Download** the cleaned dataset as CSV or Excel
7. **Generate PDF reports** comparing before vs. after cleaning statistics

The system exposes both a **Django Template-based web UI** and a **REST API** (built with Django REST Framework).

---

## 🔄 How It Works

```
User Uploads File (CSV/Excel)
          │
          ▼
  File Validation (extension, size, format)
          │
          ▼
  Dataset saved to DB + Media storage
          │
          ▼
  Auto-Analysis runs (AnalysisService)
  ├── Count rows, columns
  ├── Detect missing values per column
  ├── Count duplicate rows
  ├── Detect data types
  └── Compute memory usage
          │
          ▼
  AI Suggestion Engine (SuggestionService)
  ├── Detect missing value columns → suggest fill strategy
  ├── Detect duplicate rows → suggest remove_duplicates
  ├── Detect potential numeric columns stored as text
  ├── Run Isolation Forest on numeric columns → suggest outlier removal
  ├── Scan text columns for extra spaces / mixed case
  ├── Detect email columns → validate email format
  └── Detect phone columns → validate phone format
          │
          ▼
  User selects operations (or uses AI suggestions)
          │
          ▼
  CleaningService applies operations sequentially
  ├── remove_duplicates
  ├── fill_missing (mean / median / mode)
  ├── remove_missing rows/columns
  ├── convert_datatype (int, float, datetime, bool)
  ├── normalize_text (lower / upper / title case)
  ├── remove_extra_spaces
  ├── encode_categorical (LabelEncoder)
  ├── scale_numeric (StandardScaler / MinMaxScaler)
  ├── detect_outliers (IsolationForest → adds flag column)
  ├── remove_outliers (IsolationForest or IQR method)
  ├── remove_invalid_emails
  └── remove_invalid_phones
          │
          ▼
  Cleaned DataFrame saved back to disk
  History of each operation saved to DB
          │
          ▼
  Visualization (VisualizationService via Plotly)
          │
          ▼
  Report generation (ReportService via ReportLab)
  └── PDF with before/after comparison table
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | Django 5.x |
| **REST API** | Django REST Framework (DRF) |
| **Database (Dev)** | SQLite3 (default) |
| **Database (Prod)** | PostgreSQL |
| **Frontend** | Django Templates + Bootstrap 5 |
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | scikit-learn (IsolationForest, LabelEncoder, Scalers) |
| **Visualization** | Plotly |
| **PDF Generation** | ReportLab |
| **Excel Support** | openpyxl |
| **File Handling** | Pillow |
| **Static Files** | WhiteNoise |
| **Environment Config** | python-decouple |
| **CORS** | django-cors-headers |
| **Filtering** | django-filter |
| **WSGI Server (Prod)** | Gunicorn |
| **Auth** | Django built-in + DRF Token Auth |

---

## 📦 Libraries Used

### Core Django Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `Django` | ≥5.0 | Web framework — handles routing, ORM, templates, auth |
| `djangorestframework` | ≥3.15 | REST API — ViewSets, Serializers, Authentication |
| `django-cors-headers` | ≥4.3 | Allows cross-origin requests (important for API access) |
| `django-filter` | ≥24.0 | Adds filter capabilities to DRF querysets |

### Data Science Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `pandas` | ≥2.2 | Core data manipulation — DataFrames, reading CSV/Excel |
| `numpy` | ≥2.0 | Numerical operations, numeric type detection |
| `scikit-learn` | ≥1.5 | ML operations: IsolationForest (outliers), LabelEncoder, MinMaxScaler, StandardScaler |
| `openpyxl` | ≥3.1 | Read/write `.xlsx` Excel files |

### Visualization & Reporting

| Library | Version | Purpose |
|---------|---------|---------|
| `plotly` | ≥5.22 | Interactive charts (histograms, bar charts, box plots) |
| `reportlab` | ≥4.2 | Generate PDF cleaning reports |
| `Pillow` | ≥10.4 | Image handling for user avatars |

### Infrastructure Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `python-decouple` | ≥3.8 | Load settings from `.env` file cleanly |
| `psycopg2-binary` | ≥2.9 | PostgreSQL database adapter |
| `gunicorn` | ≥22.0 | Production WSGI server |
| `whitenoise` | ≥6.7 | Serve static files efficiently without a separate web server |

---

## 📁 Project Structure

```
AI-Dataset-Cleaning-System/
│
├── config/                        # Django project configuration
│   ├── settings.py                # All settings (DB, INSTALLED_APPS, REST_FRAMEWORK, logging)
│   ├── urls.py                    # Root URL routing
│   ├── wsgi.py                    # WSGI entry point
│   └── asgi.py                    # ASGI entry point
│
├── accounts/                      # User authentication app
│   ├── models.py                  # Custom User model (extends AbstractUser)
│   ├── views.py                   # Login, Signup, Dashboard, Profile views
│   ├── forms.py                   # SignUp and Profile update forms
│   ├── serializers.py             # DRF serializers for User API
│   ├── api_views.py               # REST API views for auth
│   ├── urls.py                    # Web URL patterns for accounts
│   └── api_urls.py                # API URL patterns for auth
│
├── datasets/                      # Core dataset management app
│   ├── models.py                  # Dataset, CleaningJob, CleaningHistory, Report models
│   ├── views.py                   # Web views (upload, detail, clean, report, download)
│   ├── api_views.py               # REST API ViewSets for datasets
│   ├── serializers.py             # DRF serializers for dataset models
│   ├── forms.py                   # Upload and cleaning operation forms
│   ├── urls.py                    # Web URL patterns
│   ├── api_urls.py                # API URL patterns (DRF routers)
│   │
│   ├── services/                  # Business logic layer (Service Pattern)
│   │   ├── orchestrator.py        # Main coordinator — ties all services together
│   │   ├── analysis_service.py    # Analyzes DataFrame statistics
│   │   ├── cleaning_service.py    # Applies all cleaning operations
│   │   ├── suggestion_service.py  # AI-driven cleaning suggestions
│   │   ├── visualization_service.py # Generates Plotly chart data
│   │   └── report_service.py      # Builds summary and generates PDF
│   │
│   └── utils/                     # Utility helpers
│       ├── file_handler.py        # Load/save DataFrames, validate uploads
│       └── validators.py          # Email/phone validation, helper functions
│
├── core/                          # Shared utilities app
│   ├── exceptions.py              # Custom exceptions + DRF exception handler
│   ├── pagination.py              # Standard pagination config for DRF
│   └── utils.py                   # General utility functions (e.g., safe_filename)
│
├── templates/                     # Django HTML templates
│   ├── base.html                  # Base layout with nav and Bootstrap
│   ├── accounts/                  # Login, signup, dashboard, profile templates
│   └── datasets/                  # Upload, detail, clean, visualize, report templates
│
├── static/                        # CSS, JS, images
├── media/                         # Uploaded and cleaned files (runtime)
├── logs/                          # Application log files (runtime)
├── sample_data/                   # Sample CSV/Excel files to test with
├── manage.py                      # Django management command entry point
├── requirements.txt               # All Python dependencies
└── .env.example                   # Template for environment variables
```

---

## 🧩 Key Modules Explained

### `DatasetOrchestrator` (orchestrator.py)

The **central coordinator** of the application. Every major operation flows through here:

```python
# Creates a new dataset record after validating the uploaded file
DatasetOrchestrator.create_dataset(user, name, uploaded_file)

# Runs AnalysisService + SuggestionService and saves results to DB
DatasetOrchestrator.analyze(dataset)

# Runs CleaningService, saves cleaned file, records job history
DatasetOrchestrator.clean(dataset, user, operations, use_suggestions)

# Generates Plotly chart data using VisualizationService
DatasetOrchestrator.get_visualizations(dataset, use_cleaned=False)

# Builds report summary and generates PDF via ReportService
DatasetOrchestrator.generate_report(dataset, user, job)
```

---

### `CleaningService` (cleaning_service.py)

Applies **12 cleaning operations** to a pandas DataFrame:

```python
# Each operation returns: (cleaned_df, description_string, rows_affected_count)

remove_duplicates   # df.drop_duplicates()
fill_missing        # fillna(mean / median / mode)
remove_missing      # dropna() on rows or columns
convert_datatype    # pd.to_numeric(), pd.to_datetime(), astype()
normalize_text      # str.lower() / str.upper() / str.title()
remove_extra_spaces # str.strip() + regex whitespace collapse
encode_categorical  # sklearn LabelEncoder
scale_numeric       # sklearn StandardScaler or MinMaxScaler
detect_outliers     # sklearn IsolationForest → adds '*_outlier' flag column
remove_outliers     # IsolationForest or IQR method to drop rows
remove_invalid_emails  # regex-based email validation
remove_invalid_phones  # regex-based phone validation
```

---

### `SuggestionService` (suggestion_service.py)

The **AI suggestion engine** — scans the raw DataFrame and generates a prioritized list of recommendations:

```python
# Priority order: high → medium → low
{
  'type': 'missing_values',        # Category of issue
  'priority': 'high',              # high / medium / low
  'column': 'email',               # Affected column (or None for whole-dataset)
  'count': 42,                     # Number of affected cells/rows
  'percentage': 12.5,              # Percentage of data affected
  'strategy': 'fill_mean',         # Recommended fix
  'message': 'Fill missing ...',   # Human-readable explanation
  'operation': {                   # Ready-to-execute operation dict
    'name': 'fill_missing',
    'params': {'column': 'email', 'method': 'mean'}
  }
}
```

**Detection logic:**
- **Missing values** — `df.isnull().sum()` per column, chooses fill strategy based on % missing
- **Duplicates** — `df.duplicated().sum()`
- **Wrong datatypes** — tries `pd.to_numeric()`, checks valid ratio
- **Outliers** — `IsolationForest(contamination=0.05)` on numeric columns
- **Text issues** — checks for leading/trailing spaces and mixed case
- **Invalid emails** — regex pattern matching on likely email columns
- **Invalid phones** — regex pattern matching on likely phone columns

---

### `AnalysisService` (analysis_service.py)

Produces a **comprehensive statistics dictionary** from a DataFrame:

```python
{
  'row_count': 1000,
  'column_count': 12,
  'missing_values': {'total': 45, 'by_column': {'age': 10}, 'percentage': 0.375},
  'duplicate_rows': 3,
  'data_types': {'name': 'object', 'age': 'float64'},
  'memory_usage_mb': 0.0987,
  'numeric_columns': ['age', 'salary'],
  'categorical_columns': ['name', 'city'],
  'numeric_stats': {'age': {'mean': 30.5, 'std': 8.2, ...}},
  'categorical_stats': {'city': {'unique_count': 15, 'top_values': {...}}},
  'sample_rows': [...]   # First 5 rows as list of lists
}
```

---

### `ReportService` (report_service.py)

Builds a **PDF report** using ReportLab with:
- Dataset metadata (name, user, date generated)
- Cleaning operations applied (table with rows affected)
- Before vs. After comparison table (row count, missing values, duplicates, memory usage)

---

### Custom Exception Hierarchy (core/exceptions.py)

```python
DatasetError          # Base exception for all dataset-related errors
  ├── FileValidationError   # Bad file extension, size exceeded, corrupt file
  ├── AnalysisError         # Failure during statistical analysis
  └── CleaningError         # Failure during a cleaning operation
```

The `custom_exception_handler` in DRF always returns a consistent JSON shape:
```json
{
  "success": false,
  "error": {
    "message": "Human-readable error",
    "code": "error_code_string"
  }
}
```

---

## 🗄 Database Models

### `User` (accounts app)
Extends Django's `AbstractUser` with:
- `email` (unique)
- `phone`, `organization`, `bio`
- `avatar` (image upload)

### `Dataset` (datasets app)
Stores uploaded file metadata:
- `id` — UUID primary key
- `user` — ForeignKey to User
- `original_file` / `cleaned_file` — FileField paths
- `file_type` — csv / xlsx / xls
- `status` — uploaded → analyzed → cleaned → failed
- `analysis_result` — JSONField with full analysis stats
- `row_count`, `column_count`

### `CleaningJob` (datasets app)
Represents one cleaning run:
- `dataset` — ForeignKey to Dataset
- `status` — pending → running → completed → failed
- `operations` — JSONField list of operations applied
- `suggestions` — JSONField of AI suggestions at time of cleaning
- `before_stats` / `after_stats` — Quick stats snapshots
- `progress` — 0–100 integer

### `CleaningHistory` (datasets app)
Per-operation log entries within a job:
- `job` — ForeignKey to CleaningJob
- `operation` — operation name string
- `parameters` — JSONField of params used
- `rows_affected` — integer count

### `Report` (datasets app)
Generated cleaning report:
- `title`, `summary` (JSON), `comparison` (JSON)
- `pdf_file` — FileField for the generated PDF

---

## 🔌 API Endpoints

### Authentication API (`/api/v1/auth/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Obtain auth token |
| POST | `/api/v1/auth/logout/` | Invalidate token |
| GET | `/api/v1/auth/profile/` | Get current user profile |

### Datasets API (`/api/v1/`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/datasets/` | List user's datasets |
| POST | `/api/v1/datasets/` | Upload new dataset |
| GET | `/api/v1/datasets/{id}/` | Dataset detail |
| DELETE | `/api/v1/datasets/{id}/` | Delete dataset |
| POST | `/api/v1/datasets/{id}/analyze/` | Run/re-run analysis |
| POST | `/api/v1/datasets/{id}/clean/` | Run cleaning job |
| GET | `/api/v1/datasets/{id}/visualizations/` | Get chart data |
| POST | `/api/v1/datasets/{id}/report/` | Generate report |
| GET | `/api/v1/datasets/{id}/download/csv/` | Download as CSV |
| GET | `/api/v1/datasets/{id}/download/xlsx/` | Download as Excel |
| GET | `/api/v1/datasets/{id}/report/download/` | Download PDF report |
| GET | `/api/v1/jobs/` | List cleaning jobs |
| GET | `/api/v1/reports/` | List reports |

### Web UI Routes
| Route | Description |
|-------|-------------|
| `/` → redirects to dashboard | |
| `/login/` | Login page |
| `/signup/` | Registration page |
| `/dashboard/` | User dashboard with stats |
| `/profile/` | Edit profile |
| `/datasets/` | Dataset list |
| `/datasets/upload/` | Upload new dataset |
| `/datasets/{id}/` | Dataset detail & analysis |
| `/datasets/{id}/analyze/` | Re-analyze dataset |
| `/datasets/{id}/clean/` | Configure & run cleaning |
| `/datasets/{id}/visualize/` | Interactive charts |
| `/datasets/{id}/report/` | View cleaning report |
| `/admin/` | Django admin panel |

---

## 🚀 Setup & Run Instructions

### Prerequisites

- Python 3.10 or higher
- pip
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/minahil-ch/AI-Dataset-Cleaning-System.git
cd AI-Dataset-Cleaning-System
```

### Step 2 — Create and activate virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment

```bash
# Copy the example env file
copy .env.example .env        # Windows
cp .env.example .env           # macOS/Linux

# Edit .env and set your values (see Environment Variables section below)
```

### Step 5 — Apply database migrations

```bash
python manage.py migrate
```

### Step 6 — Create a superuser (admin account)

```bash
python manage.py createsuperuser
# Follow prompts: username, email, password
```

### Step 7 — Collect static files (optional in dev)

```bash
python manage.py collectstatic
```

### Step 8 — Run the development server

```bash
python manage.py runserver
# App will be available at: http://127.0.0.1:8000/
```

### Step 9 — (Optional) Run with a specific port

```bash
python manage.py runserver 8080
# App available at: http://127.0.0.1:8080/
```

---

### ⚡ Quick Start (One-liners for Windows venv)

```powershell
# If already inside the project folder and venv is already created:
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py runserver 8080
```

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and fill in these values:

```env
# Django core settings
SECRET_KEY=your-secret-key-change-in-production   # Required in production
DEBUG=True                                          # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1                  # Add your domain in production

# Database — use 'sqlite' for local dev, 'postgresql' for production
DB_ENGINE=sqlite

# PostgreSQL settings (only needed when DB_ENGINE=postgresql)
DB_NAME=ai_dataset_cleaning
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# File uploads — max size in megabytes
MAX_UPLOAD_SIZE_MB=50

# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

---

## 🎓 Viva Guide — Common Questions

### Q1: What is the purpose of this project?
**A:** It is a web application that automates the process of cleaning messy datasets. Users upload CSV or Excel files, the system analyzes the data quality, suggests AI-driven fixes, applies cleaning operations, and generates downloadable PDF reports.

---

### Q2: What design pattern does this project follow?
**A:** It follows the **Service Layer Pattern** (also called Business Logic Layer). Instead of putting business logic in views, all logic is delegated to service classes:
- `AnalysisService` — data profiling
- `SuggestionService` — AI suggestions
- `CleaningService` — applying operations
- `VisualizationService` — chart generation
- `ReportService` — PDF creation
- `DatasetOrchestrator` — coordinates all services

---

### Q3: What is Django REST Framework (DRF)?
**A:** DRF is a toolkit built on top of Django that makes it easy to build Web APIs. In this project, it is used to:
- Create **ViewSets** (like `DatasetViewSet`) that automatically handle GET, POST, DELETE
- Write **Serializers** to convert Python objects to/from JSON
- Handle **Authentication** (Token-based)
- Add **Filtering, Searching, and Pagination** with minimal code

---

### Q4: What ML algorithm is used for outlier detection?
**A:** `IsolationForest` from scikit-learn. It is an unsupervised algorithm that isolates anomalies by randomly selecting a feature and then randomly selecting a split value. Outliers are easier to isolate (fewer splits needed), so they get lower anomaly scores. We use `contamination=0.05` meaning we expect ~5% of data to be outliers.

---

### Q5: How does the suggestion engine work?
**A:** The `SuggestionService` scans the raw DataFrame and:
1. Counts missing values per column — suggests fill or remove strategy
2. Counts duplicate rows — suggests remove_duplicates
3. Tries to parse object columns as numeric — suggests datatype conversion
4. Runs IsolationForest on numeric columns — suggests outlier removal
5. Checks text columns for whitespace/case issues — suggests text normalization
6. Detects email/phone columns by name patterns — validates format with regex

Each suggestion includes a ready-to-execute operation dict so it can be applied directly.

---

### Q6: What is the difference between `views.py` and `api_views.py`?
**A:**
- `views.py` — serves **HTML pages** using Django templates (server-side rendering, form submissions)
- `api_views.py` — serves **JSON responses** using DRF (for programmatic access, mobile apps, or JavaScript frontends)

Both enforce authentication — web views use Django session auth; API views use Token auth.

---

### Q7: Why use UUID as primary key instead of integer?
**A:** UUIDs prevent enumeration attacks (an attacker cannot guess `/datasets/1/`, `/datasets/2/`), make IDs safe to expose in URLs, and allow distributed systems to generate IDs without a central counter.

---

### Q8: What is WhiteNoise and why is it used?
**A:** WhiteNoise is a Python library that allows Django to serve its own static files efficiently in production without needing a separate Nginx/Apache web server. It compresses and caches files automatically.

---

### Q9: How does the PDF report get generated?
**A:** The `ReportService` uses **ReportLab** — a Python library for programmatic PDF creation. It builds a `SimpleDocTemplate` with `Paragraph`, `Table`, and `Spacer` elements, applies custom `TableStyle` (blue headers, alternating row colors), then writes the buffer to a `ContentFile` which is saved to the `Report.pdf_file` field.

---

### Q10: How is authentication handled?
**A:** Two mechanisms:
1. **Session Authentication** — for the web UI. Django's built-in login/logout sets a session cookie.
2. **Token Authentication** — for the REST API. After logging in via `/api/v1/auth/login/`, you receive a token and include it in requests as `Authorization: Token <your_token>`.

---

### Q11: What is `python-decouple` and why is it used?
**A:** `python-decouple` reads environment variables from a `.env` file and makes them available via `config('VARIABLE_NAME', default=..., cast=...)`. This separates configuration from code, following the **12-Factor App** principle — sensitive data like `SECRET_KEY` and database passwords are never hardcoded.

---

### Q12: Explain the CleaningJob lifecycle.
**A:**
1. Job created with `status='running'`
2. `CleaningService.apply_operations()` runs all selected operations sequentially on the DataFrame
3. Each operation produces a history entry (operation name, rows affected, description)
4. Cleaned DataFrame saved to disk
5. `CleaningHistory` records created in DB
6. Job updated to `status='completed'`, `progress=100`, `after_stats` recorded
7. If any operation fails → job marked `status='failed'`, error stored

---

### Q13: What kind of data quality issues can this system detect?
**A:** Missing values, duplicate rows, wrong data types, statistical outliers (using ML), text formatting issues (extra spaces, inconsistent casing), invalid email addresses, and invalid phone numbers.

---

### Q14: How are files stored and organized?
**A:**
- Original files → `media/datasets/original/`
- Cleaned files → `media/datasets/cleaned/`
- Reports → `media/reports/pdf/`
- User avatars → `media/avatars/`

The `MEDIA_ROOT` is `BASE_DIR/media` and files are served via the `MEDIA_URL = '/media/'` prefix during development.

---

## 👩‍💻 Author

**Minahil** — AI Dataset Cleaning System  
Built with Django 5, scikit-learn, Pandas, Plotly, and ReportLab.

---

*This project is intended for educational use and viva demonstration.*
