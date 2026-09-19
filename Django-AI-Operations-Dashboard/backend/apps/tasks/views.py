from rest_framework import viewsets, permissions
from tasks.models import Task
from tasks.serializers import TaskSerializer
from users.permissions import IsOwnerOrAdminOrManager
from activity_logs.models import ActivityLog
from notifications.models import Notification, NotificationType

class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    filterset_fields = ['status', 'priority', 'assigned_to', 'department', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'status', 'created_at']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdminOrManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            action="TASK_CREATE",
            details={"message": f"Created task: {task.title}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        # Notify the assignee if set and is different from the creator
        if task.assigned_to and task.assigned_to != self.request.user:
            Notification.objects.create(
                user=task.assigned_to,
                title="New Task Assigned",
                message=f"You have been assigned a new task: {task.title}.",
                notification_type=NotificationType.INFO
            )

    def perform_update(self, serializer):
        # Retrieve the original state before updating
        old_task = self.get_object()
        old_assigned_to = old_task.assigned_to
        old_status = old_task.status
        
        task = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="TASK_UPDATE",
            details={"message": f"Updated task: {task.title}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        # Notify the assignee if it has changed
        if task.assigned_to and task.assigned_to != old_assigned_to and task.assigned_to != self.request.user:
            Notification.objects.create(
                user=task.assigned_to,
                title="Task Assigned to You",
                message=f"You have been assigned the task: {task.title}.",
                notification_type=NotificationType.INFO
            )
        
        # Notify creator if the task status was changed to DONE by someone else
        if task.status == 'DONE' and old_status != 'DONE' and task.created_by != self.request.user:
            Notification.objects.create(
                user=task.created_by,
                title="Task Completed",
                message=f"The task '{task.title}' has been marked as DONE by {self.request.user.username}.",
                notification_type=NotificationType.SUCCESS
            )

    def perform_destroy(self, instance):
        title = instance.title
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action="TASK_DELETE",
            details={"message": f"Deleted task: {title}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
