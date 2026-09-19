"""Prediction engine: turns HR-entered candidate data into a prediction."""
from .model_loader import load_active_model_bundle
from .preprocessing import build_prediction_vector


class ModelNotFoundError(Exception):
    pass


def predict_candidate(candidate_dict: dict):
    """
    Run the active best model on a single candidate's data.
    Returns a dict with result, probability, algorithm name, and a
    human-readable explanation.
    """
    bundle, record = load_active_model_bundle()
    if bundle is None:
        raise ModelNotFoundError(
            "No trained model is available yet. Please train a model first."
        )

    model = bundle["model"]
    scaler = bundle["scaler"]

    X = build_prediction_vector(candidate_dict, scaler)

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0][1]
    else:
        proba = float(model.predict(X)[0])

    result = "SELECTED" if proba >= 0.5 else "REJECTED"
    explanation = build_explanation(candidate_dict, proba, result)

    return {
        "result": result,
        "probability": float(proba),
        "algorithm_name": bundle.get("algorithm_name", "Unknown"),
        "model_record": record,
        "explanation": explanation,
    }


def build_explanation(candidate_dict, proba, result):
    """Generate a short human-readable explanation of the prediction."""
    exp = candidate_dict.get("experience_years", 0)
    interview = candidate_dict.get("interview_score", 0)
    comm = candidate_dict.get("communication_score", 0)

    strengths = []
    if exp and float(exp) >= 3:
        strengths.append("solid experience")
    if interview and float(interview) >= 70:
        strengths.append("a strong interview score")
    if comm and float(comm) >= 70:
        strengths.append("strong communication skills")

    strength_text = ", ".join(strengths) if strengths else "an average overall profile"

    if result == "SELECTED":
        return (f"The candidate shows {strength_text}. The model predicts a "
                f"{proba:.0%} probability of being shortlisted.")
    return (f"The candidate's profile ({strength_text}) did not meet the model's "
            f"threshold. Predicted probability of selection: {proba:.0%}.")
