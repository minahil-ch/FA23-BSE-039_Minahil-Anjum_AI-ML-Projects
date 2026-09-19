from rest_framework import viewsets, permissions
from teams.models import Team
from teams.serializers import TeamSerializer
from users.permissions import IsManager
from activity_logs.models import ActivityLog

class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows teams to be viewed or edited.
    """
    queryset = Team.objects.all().order_by('name')
    serializer_class = TeamSerializer
    filterset_fields = ['department', 'leader']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def perform_create(self, serializer):
        team = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="TEAM_CREATE",
            details={"message": f"Created team: {team.name} in department {team.department.name}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

    def perform_update(self, serializer):
        team = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="TEAM_UPDATE",
            details={"message": f"Updated team: {team.name}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

    def perform_destroy(self, instance):
        name = instance.name
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action="TEAM_DELETE",
            details={"message": f"Deleted team: {name}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
