from django.contrib import admin
from notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'notification_type', 'created_at']
    search_fields = ['title', 'message']
    list_filter = ['is_read', 'notification_type', 'created_at', 'user']
    ordering = ['-created_at']
