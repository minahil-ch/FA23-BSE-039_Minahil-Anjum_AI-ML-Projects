from rest_framework import viewsets
from activity_logs.models import ActivityLog
from activity_logs.serializers import ActivityLogSerializer
from users.permissions import IsManager

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows admins and managers to view activity logs.
    """
    queryset = ActivityLog.objects.all().order_by('-created_at')
    serializer_class = ActivityLogSerializer
    permission_classes = [IsManager]
    filterset_fields = ['user', 'action']
    search_fields = ['action', 'details']
    ordering_fields = ['created_at']
