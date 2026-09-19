from rest_framework import serializers
from notifications.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'notification_type', 'created_at']
        read_only_fields = ['id', 'title', 'message', 'notification_type', 'created_at']
