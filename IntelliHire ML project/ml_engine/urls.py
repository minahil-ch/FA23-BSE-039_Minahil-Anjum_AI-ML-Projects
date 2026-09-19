from django.urls import path
from . import views

app_name = "ml_engine"

urlpatterns = [
    path("training/", views.training_page, name="training"),
    path("training/run/<int:dataset_id>/", views.train_models, name="train"),
    path("comparison/", views.model_comparison, name="comparison"),
    path("predict/", views.prediction_form_view, name="predict"),
    path("predictions/", views.prediction_history, name="prediction_history"),
    path("predictions/<int:pk>/", views.prediction_detail, name="prediction_detail"),
    path("predictions/<int:pk>/delete/", views.prediction_delete, name="prediction_delete"),
]
