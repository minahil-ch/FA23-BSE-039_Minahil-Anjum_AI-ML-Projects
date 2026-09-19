from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task, TaskStatus
from notifications.models import Notification, NotificationType

@shared_task
def cleanup_old_notifications():
    """
    Background task to clean up read notifications older than 14 days.
    """
    cutoff = timezone.now() - timedelta(days=14)
    deleted_count, _ = Notification.objects.filter(is_read=True, created_at__lt=cutoff).delete()
    return f"Cleaned up {deleted_count} old notifications."

@shared_task
def check_due_tasks_summary():
    """
    Background task to scan for incomplete tasks that are due within 24 hours 
    and notify their assignees.
    """
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_tasks = Task.objects.filter(
        status__in=[TaskStatus.TODO, TaskStatus.IN_PROGRESS],
        due_date__lte=tomorrow,
        due_date__gte=timezone.now()
    )
    
    notifications_sent = 0
    for task in upcoming_tasks:
        if task.assigned_to:
            Notification.objects.create(
                user=task.assigned_to,
                title="Task Deadline Approaching",
                message=f"The task '{task.title}' is due by {task.due_date.strftime('%Y-%m-%d %H:%M')}.",
                notification_type=NotificationType.WARNING
            )
            notifications_sent += 1
            
    return f"Alerted assignees for {notifications_sent} upcoming tasks."
