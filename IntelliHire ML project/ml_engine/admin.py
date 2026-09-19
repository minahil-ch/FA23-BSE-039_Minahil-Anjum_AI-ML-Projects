from django.contrib import admin
from .models import TrainedModel, Prediction

@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ("algorithm_name", "dataset", "accuracy", "f1_score", "is_best_model", "trained_at")
    list_filter = ("algorithm_name", "is_best_model")

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("id", "result", "probability", "model_used", "predicted_by", "predicted_at")
    list_filter = ("result",)
