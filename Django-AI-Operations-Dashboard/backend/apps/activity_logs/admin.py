from django.contrib import admin
from activity_logs.models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'created_at']
    search_fields = ['action', 'details']
    list_filter = ['action', 'created_at', 'user']
    readonly_fields = ['user', 'action', 'details', 'ip_address', 'created_at']
    ordering = ['-created_at']
