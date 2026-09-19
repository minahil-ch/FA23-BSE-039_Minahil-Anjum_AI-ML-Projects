"""
Core ML training pipeline: trains 6 classification algorithms on a
recruitment dataset, evaluates each with cross validation, picks the best
performer, and saves the best model + scaler + metadata with joblib.
"""
import os
import time
import joblib
import numpy as np
from django.conf import settings
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix,
)

from .preprocessing import build_training_matrix, FEATURE_COLUMNS
from . import services as ml_services


ALGORITHMS = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42),
    "Support Vector Machine": SVC(kernel="rbf", probability=True, random_state=42),
    "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
    "Naive Bayes": GaussianNB(),
}


def train_all_models(df, dataset_id, user, test_size=0.2):
    """
    Train every algorithm in ALGORITHMS on the given dataframe, evaluate
    each one, persist metrics to the database via ml_services, save the
    best model to disk with joblib, and return the list of results.
    """
    X, y, scaler = build_training_matrix(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y if len(set(y)) > 1 else None
    )

    results = []
    best_result = None

    for name, model in ALGORITHMS.items():
        start = time.time()
        model.fit(X_train, y_train)
        elapsed = time.time() - start

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        try:
            auc = roc_auc_score(y_test, y_proba) if len(set(y_test)) > 1 else None
        except ValueError:
            auc = None
        cm = confusion_matrix(y_test, y_pred).tolist()

        try:
            cv_scores = cross_val_score(model, X, y, cv=min(5, max(2, len(set(y)))))
            cv_mean = float(np.mean(cv_scores))
        except Exception:
            cv_mean = None

        feature_importance = None
        if hasattr(model, "feature_importances_"):
            feature_importance = dict(zip(FEATURE_COLUMNS, model.feature_importances_.tolist()))
        elif hasattr(model, "coef_"):
            feature_importance = dict(zip(FEATURE_COLUMNS, model.coef_[0].tolist()))

        result = {
            "algorithm_name": name,
            "model_object": model,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "roc_auc": auc,
            "cross_val_mean": cv_mean,
            "confusion_matrix": cm,
            "feature_importance": feature_importance,
            "training_time_seconds": elapsed,
        }
        results.append(result)

        if best_result is None or result["f1_score"] > best_result["f1_score"]:
            best_result = result

    # Persist all results + save the best model to disk
    saved_records = ml_services.save_training_results(
        results, best_result, scaler, dataset_id, user
    )
    return saved_records


def save_best_model_to_disk(model, scaler, dataset_id, algorithm_name):
    """Save the winning model + its scaler + feature list with joblib."""
    os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)
    safe_name = algorithm_name.replace(" ", "_").lower()
    model_path = os.path.join(settings.ML_MODELS_DIR, f"best_model_dataset{dataset_id}_{safe_name}.joblib")

    bundle = {
        "model": model,
        "scaler": scaler,
        "features": FEATURE_COLUMNS,
        "algorithm_name": algorithm_name,
    }
    joblib.dump(bundle, model_path)
    return model_path
