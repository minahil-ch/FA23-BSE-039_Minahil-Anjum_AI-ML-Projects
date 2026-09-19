from rest_framework import serializers
from activity_logs.models import ActivityLog
from users.serializers import CustomUserSerializer

class ActivityLogSerializer(serializers.ModelSerializer):
    user_detail = CustomUserSerializer(source='user', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_detail', 'action', 'details', 'ip_address', 'created_at']
        read_only_fields = ['id', 'user', 'action', 'details', 'ip_address', 'created_at']
