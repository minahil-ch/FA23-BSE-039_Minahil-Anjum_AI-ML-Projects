from rest_framework import viewsets, permissions
from departments.models import Department
from departments.serializers import DepartmentSerializer
from users.permissions import IsManager
from activity_logs.models import ActivityLog

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows departments to be viewed or edited.
    """
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    filterset_fields = ['name', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManager()]

    def perform_create(self, serializer):
        department = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="DEPARTMENT_CREATE",
            details={"message": f"Created department: {department.name}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

    def perform_update(self, serializer):
        department = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="DEPARTMENT_UPDATE",
            details={"message": f"Updated department: {department.name}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

    def perform_destroy(self, instance):
        name = instance.name
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action="DEPARTMENT_DELETE",
            details={"message": f"Deleted department: {name}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
