"""
Loads the currently active best model bundle (model + scaler + feature
list) from disk, with a simple in-memory cache so we don't hit disk on
every prediction request.
"""
import joblib
from .services import get_active_best_model

_cache = {"path": None, "bundle": None}


def load_active_model_bundle():
    """Return (bundle_dict, TrainedModel record) or (None, None) if no model trained yet."""
    record = get_active_best_model()
    if record is None or not record.model_file_path:
        return None, None

    if _cache["path"] != record.model_file_path:
        try:
            _cache["bundle"] = joblib.load(record.model_file_path)
            _cache["path"] = record.model_file_path
        except FileNotFoundError:
            return None, None

    return _cache["bundle"], record
