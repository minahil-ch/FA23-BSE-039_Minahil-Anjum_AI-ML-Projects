"""
Business logic for dataset validation and cleaning.
Kept separate from views so it can be reused by the ML training pipeline
and unit tested independently.
"""
import pandas as pd


REQUIRED_COLUMNS = [
    "experience_years", "cgpa", "communication_score",
    "interview_score", "technical_skills_count", "selected",
]


def load_dataset(file_path):
    """Load a CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)


def validate_dataset(df: pd.DataFrame) -> dict:
    """
    Run a set of sanity checks on the raw uploaded dataset and return a
    validation report dictionary (used both for display and for deciding
    whether the dataset is safe to train on).
    """
    report = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_names": list(df.columns),
        "missing_by_column": {c: int(v) for c, v in df.isnull().sum().items() if v > 0},
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing_required_columns": [c for c in REQUIRED_COLUMNS if c not in df.columns],
    }
    report["is_valid"] = len(report["missing_required_columns"]) == 0 and report["rows"] > 10
    return report


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply standard data cleaning steps:
    - drop exact duplicate rows
    - trim whitespace from string columns
    - fill missing numeric values with column median
    - fill missing categorical values with the mode
    - drop rows still missing the target column
    """
    df = df.copy()
    df = df.drop_duplicates()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    for col in df.select_dtypes(include="object").columns:
        if df[col].isnull().any() and not df[col].mode().empty:
            df[col] = df[col].fillna(df[col].mode()[0])

    if "selected" in df.columns:
        df = df.dropna(subset=["selected"])

    return df.reset_index(drop=True)


def dataset_summary(df: pd.DataFrame) -> dict:
    """Generate an EDA-style statistical summary used on the dataset preview page."""
    numeric_df = df.select_dtypes(include=["float64", "int64"])
    return {
        "describe": numeric_df.describe().round(2).to_dict(),
        "correlation": numeric_df.corr().round(2).to_dict() if not numeric_df.empty else {},
        "target_distribution": df["selected"].value_counts().to_dict() if "selected" in df.columns else {},
    }
