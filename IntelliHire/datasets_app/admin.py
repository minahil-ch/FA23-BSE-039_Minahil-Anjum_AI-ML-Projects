from django.contrib import admin
from .models import Dataset

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "rows_count", "columns_count", "uploaded_by", "uploaded_at")
    list_filter = ("status",)
