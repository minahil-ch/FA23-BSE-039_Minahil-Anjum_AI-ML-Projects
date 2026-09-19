"""Business logic that connects the ML pipeline to the database layer."""
from .models import TrainedModel


def save_training_results(results, best_result, scaler, dataset_id, user):
    """
    Persist every trained algorithm's metrics to the database and save the
    single best-performing model to disk via joblib. Returns the list of
    created TrainedModel records.
    """
    from .train import save_best_model_to_disk

    saved = []
    for result in results:
        is_best = result is best_result
        model_file_path = ""
        if is_best:
            model_file_path = save_best_model_to_disk(
                result["model_object"], scaler, dataset_id, result["algorithm_name"]
            )

        record = TrainedModel.objects.create(
            dataset_id=dataset_id,
            algorithm_name=result["algorithm_name"],
            is_best_model=is_best,
            accuracy=result["accuracy"],
            precision=result["precision"],
            recall=result["recall"],
            f1_score=result["f1_score"],
            roc_auc=result["roc_auc"],
            cross_val_mean=result["cross_val_mean"],
            confusion_matrix=result["confusion_matrix"],
            feature_importance=result["feature_importance"],
            model_file_path=str(model_file_path),
            training_time_seconds=result["training_time_seconds"],
            trained_by=user,
        )
        saved.append(record)
    return saved


def get_active_best_model():
    """Return the most recently trained best-performing model record."""
    return TrainedModel.objects.filter(is_best_model=True).order_by("-trained_at").first()
