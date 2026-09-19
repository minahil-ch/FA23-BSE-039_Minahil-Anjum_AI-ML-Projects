from django.db import models
from django.conf import settings


def dataset_upload_path(instance, filename):
    return f"datasets/{filename}"


class Dataset(models.Model):
    """An uploaded CSV dataset used to train the ML models."""

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Uploaded"
        VALIDATED = "VALIDATED", "Validated"
        CLEANED = "CLEANED", "Cleaned"
        INVALID = "INVALID", "Invalid"

    name = models.CharField(max_length=150)
    file = models.FileField(upload_to=dataset_upload_path)
    cleaned_file = models.FileField(upload_to="datasets/cleaned/", blank=True, null=True)

    rows_count = models.PositiveIntegerField(default=0)
    columns_count = models.PositiveIntegerField(default=0)
    missing_values_count = models.PositiveIntegerField(default=0)
    duplicate_rows_count = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    validation_report = models.JSONField(blank=True, null=True)

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"
