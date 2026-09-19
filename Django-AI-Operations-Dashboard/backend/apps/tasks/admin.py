from django.contrib import admin
from tasks.models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'assigned_to', 'department', 'due_date', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['status', 'priority', 'department', 'assigned_to', 'due_date', 'created_at']
    ordering = ['-created_at']
