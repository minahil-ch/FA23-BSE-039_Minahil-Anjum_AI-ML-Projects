from django.contrib import admin
from departments.models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['manager', 'created_at']
    ordering = ['name']
