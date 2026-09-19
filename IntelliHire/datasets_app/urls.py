from django.urls import path
from . import views

app_name = "datasets"

urlpatterns = [
    path("", views.dataset_list, name="list"),
    path("upload/", views.dataset_upload, name="upload"),
    path("<int:pk>/preview/", views.dataset_preview, name="preview"),
    path("<int:pk>/clean/", views.dataset_clean, name="clean"),
    path("<int:pk>/download-clean/", views.dataset_download_clean, name="download_clean"),
    path("<int:pk>/delete/", views.dataset_delete, name="delete"),
]
