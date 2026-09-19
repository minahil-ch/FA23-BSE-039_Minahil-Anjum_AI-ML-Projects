"""
Shared preprocessing logic used by BOTH training and prediction, so that
candidate input is transformed in exactly the same way the training data
was transformed (this prevents train/serve skew).
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

FEATURE_COLUMNS = [
    "experience_years",
    "cgpa",
    "communication_score",
    "interview_score",
    "technical_skills_count",
    "expected_salary",
    "qualification_level",  # encoded
]

TARGET_COLUMN = "selected"

QUALIFICATION_MAP = {
    "matric": 1, "intermediate": 2, "bachelor": 3, "bachelors": 3,
    "master": 4, "masters": 4, "phd": 5, "diploma": 2,
}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive model-ready numeric features from the raw dataset columns."""
    df = df.copy()

    if "technical_skills" in df.columns and "technical_skills_count" not in df.columns:
        df["technical_skills_count"] = df["technical_skills"].fillna("").apply(
            lambda s: len([x for x in str(s).split(",") if x.strip()])
        )

    if "qualification_level" not in df.columns and "highest_qualification" in df.columns:
        df["qualification_level"] = (
            df["highest_qualification"].astype(str).str.lower().str.strip().map(QUALIFICATION_MAP).fillna(3)
        )

    if "expected_salary" not in df.columns:
        df["expected_salary"] = 0

    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """Map the target column to 0/1 if it isn't already numeric."""
    df = df.copy()
    if df[TARGET_COLUMN].dtype == object:
        mapping = {"selected": 1, "yes": 1, "1": 1, "hired": 1,
                   "rejected": 0, "no": 0, "0": 0}
        df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(str).str.lower().map(mapping)
    df[TARGET_COLUMN] = df[TARGET_COLUMN].fillna(0).astype(int)
    return df


def build_training_matrix(df: pd.DataFrame):
    """Return X, y, and the fitted scaler ready for train/test split."""
    df = engineer_features(df)
    df = encode_target(df)

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler


def build_prediction_vector(candidate_dict: dict, scaler: StandardScaler) -> np.ndarray:
    """Convert a single candidate's form input into a scaled feature vector."""
    row = pd.DataFrame([candidate_dict])
    row = engineer_features(row)
    X = row[FEATURE_COLUMNS].values
    return scaler.transform(X)
