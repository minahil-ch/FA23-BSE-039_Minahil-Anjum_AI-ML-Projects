from django.db import models
from django.conf import settings
from datasets_app.models import Dataset


class TrainedModel(models.Model):
    """Metadata record for a batch of models trained on a dataset."""

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="trainings")
    algorithm_name = models.CharField(max_length=50)
    is_best_model = models.BooleanField(default=False)

    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    roc_auc = models.FloatField(null=True, blank=True)
    cross_val_mean = models.FloatField(null=True, blank=True)

    confusion_matrix = models.JSONField(blank=True, null=True)
    feature_importance = models.JSONField(blank=True, null=True)

    model_file_path = models.CharField(max_length=500, blank=True)
    training_time_seconds = models.FloatField(default=0)

    trained_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    trained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-trained_at"]

    def __str__(self):
        return f"{self.algorithm_name} - Acc {self.accuracy:.2%}"


class Prediction(models.Model):
    """Stores every prediction made by HR through the web interface."""

    class Result(models.TextChoices):
        SELECTED = "SELECTED", "Selected"
        REJECTED = "REJECTED", "Rejected"

    candidate = models.ForeignKey("candidates.Candidate", on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="predictions")
    model_used = models.ForeignKey(TrainedModel, on_delete=models.SET_NULL, null=True)

    input_data = models.JSONField()
    result = models.CharField(max_length=10, choices=Result.choices)
    probability = models.FloatField(help_text="Probability of being selected (0-1)")
    explanation = models.TextField(blank=True)

    predicted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    predicted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-predicted_at"]

    def __str__(self):
        return f"Prediction #{self.pk} - {self.result} ({self.probability:.0%})"
