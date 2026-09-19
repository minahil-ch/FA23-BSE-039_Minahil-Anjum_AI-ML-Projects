from django.db.models import Q
from rest_framework import viewsets, permissions
from tickets.models import Ticket
from tickets.serializers import TicketSerializer
from users.permissions import IsOwnerOrAdminOrManager
from activity_logs.models import ActivityLog
from notifications.models import Notification, NotificationType

class TicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tickets to be viewed or edited.
    """
    serializer_class = TicketSerializer
    filterset_fields = ['status', 'priority', 'assigned_to', 'created_by']
    search_fields = ['subject', 'description']
    ordering_fields = ['created_at', 'priority', 'status']

    def get_queryset(self):
        user = self.request.user
        # Admins and Managers see all support tickets
        if user.is_superuser or user.role in ['ADMIN', 'MANAGER']:
            return Ticket.objects.all().order_by('-created_at')
        # Employees only see tickets they created or are assigned to
        return Ticket.objects.filter(Q(created_by=user) | Q(assigned_to=user)).distinct().order_by('-created_at')

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdminOrManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        ticket = serializer.save(created_by=self.request.user)
        ActivityLog.objects.create(
            user=self.request.user,
            action="TICKET_CREATE",
            details={"message": f"Created support ticket: {ticket.subject}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        # Notify managers or assignee if assigned_to is specified
        if ticket.assigned_to and ticket.assigned_to != self.request.user:
            Notification.objects.create(
                user=ticket.assigned_to,
                title="Ticket Assigned",
                message=f"Ticket '{ticket.subject}' has been assigned to you.",
                notification_type=NotificationType.INFO
            )

        # Queue AI classification in background (category, priority, department)
        from ai.tasks import classify_ticket_task
        try:
            classify_ticket_task.delay(ticket.id)
        except Exception:
            classify_ticket_task(ticket.id)

    def perform_update(self, serializer):
        old_ticket = self.get_object()
        old_assigned_to = old_ticket.assigned_to
        old_status = old_ticket.status
        
        ticket = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="TICKET_UPDATE",
            details={"message": f"Updated support ticket: {ticket.subject}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        # Notify assignee if changed
        if ticket.assigned_to and ticket.assigned_to != old_assigned_to and ticket.assigned_to != self.request.user:
            Notification.objects.create(
                user=ticket.assigned_to,
                title="Ticket Assigned to You",
                message=f"Ticket '{ticket.subject}' has been assigned to you.",
                notification_type=NotificationType.INFO
            )
            
        # Notify creator if ticket is resolved/closed
        if ticket.status in ['RESOLVED', 'CLOSED'] and old_status != ticket.status and ticket.created_by != self.request.user:
            Notification.objects.create(
                user=ticket.created_by,
                title=f"Ticket status changed to {ticket.get_status_display()}",
                message=f"Your ticket '{ticket.subject}' has been marked as {ticket.get_status_display()} by {self.request.user.username}.",
                notification_type=NotificationType.SUCCESS if ticket.status == 'RESOLVED' else NotificationType.INFO
            )

    def perform_destroy(self, instance):
        subject = instance.subject
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action="TICKET_DELETE",
            details={"message": f"Deleted support ticket: {subject}"},
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
