import os
import django

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from users.models import CustomUser, UserRole
from departments.models import Department
from teams.models import Team
from tasks.models import Task, TaskStatus, TaskPriority
from tickets.models import Ticket, TicketStatus, TicketPriority
from notifications.models import Notification, NotificationType
from activity_logs.models import ActivityLog

def seed():
    # 1. Clear database
    print("Clearing existing data...")
    ActivityLog.objects.all().delete()
    Notification.objects.all().delete()
    Ticket.objects.all().delete()
    Task.objects.all().delete()
    Team.objects.all().delete()
    Department.objects.all().delete()
    CustomUser.objects.all().delete()
    
    # 2. Create users
    print("Creating users...")
    admin = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN
    )
    admin.set_password('admin123')
    admin.save()

    manager = CustomUser.objects.create_user(
        username='manager',
        email='manager@example.com',
        first_name='Sarah',
        last_name='Conner',
        role=UserRole.MANAGER
    )
    manager.set_password('manager123')
    manager.save()

    employee = CustomUser.objects.create_user(
        username='employee',
        email='employee@example.com',
        first_name='John',
        last_name='Doe',
        role=UserRole.EMPLOYEE
    )
    employee.set_password('employee123')
    employee.save()
    
    # 3. Create Departments
    print("Creating departments...")
    ai_dept = Department.objects.create(
        name="AI & Analytics",
        description="Department focused on ML models, RAG systems, and Agent workflows.",
        manager=manager
    )
    devops_dept = Department.objects.create(
        name="DevOps & Infrastructure",
        description="Responsible for CI/CD, Docker registry, Kubernetes, and Cloud Operations.",
        manager=admin
    )
    
    # Associate users to departments
    employee.department = ai_dept
    employee.save()
    
    manager.department = ai_dept
    manager.save()

    # 4. Create Teams
    print("Creating teams...")
    rag_team = Team.objects.create(
        name="RAG Systems Team",
        department=ai_dept,
        leader=manager
    )
    agent_team = Team.objects.create(
        name="AI Agents Team",
        department=ai_dept,
        leader=employee
    )
    
    employee.team = agent_team
    employee.save()
    manager.team = rag_team
    manager.save()

    # 5. Create Tasks
    print("Creating tasks...")
    Task.objects.create(
        title="Deploy Vector Database",
        description="Setup PGVector extension on production PostgreSQL instance.",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        assigned_to=employee,
        department=devops_dept,
        created_by=admin,
        due_date=timezone.now() + timezone.timedelta(days=3)
    )
    Task.objects.create(
        title="Optimize RAG Embeddings Cache",
        description="Implement Redis caching layer for quick embedding lookup.",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.CRITICAL,
        assigned_to=manager,
        department=ai_dept,
        created_by=admin,
        due_date=timezone.now() + timezone.timedelta(days=1)
    )
    Task.objects.create(
        title="Build LangGraph workflow",
        description="Design multi-agent orchestration for ticket routing.",
        status=TaskStatus.REVIEW,
        priority=TaskPriority.MEDIUM,
        assigned_to=employee,
        department=ai_dept,
        created_by=manager,
        due_date=timezone.now() + timezone.timedelta(days=5)
    )
    Task.objects.create(
        title="Write API Authentication Docs",
        description="Document JWT flow and RBAC controls for the front-end team.",
        status=TaskStatus.DONE,
        priority=TaskPriority.LOW,
        assigned_to=employee,
        department=ai_dept,
        created_by=manager,
        due_date=timezone.now() - timezone.timedelta(days=1)
    )

    # 6. Create Support Tickets
    print("Creating tickets...")
    Ticket.objects.create(
        subject="Redis connection timeout in Celery worker",
        description="Worker throws connection pool limits exceeded every 6 hours.",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        created_by=employee,
        assigned_to=admin
    )
    Ticket.objects.create(
        subject="Model latency increase",
        description="GPT-4o response times spiked to 8 seconds on routing queries.",
        status=TicketStatus.IN_PROGRESS,
        priority=TicketPriority.MEDIUM,
        created_by=manager,
        assigned_to=employee
    )

    # 7. Create Notifications
    print("Creating notifications...")
    Notification.objects.create(
        user=employee,
        title="Task Assigned",
        message="You have been assigned to 'Deploy Vector Database'.",
        notification_type=NotificationType.INFO
    )
    Notification.objects.create(
        user=employee,
        title="Task Overdue Warning",
        message="The task 'Optimize RAG Embeddings Cache' is approaching its deadline.",
        notification_type=NotificationType.WARNING
    )
    Notification.objects.create(
        user=manager,
        title="New Ticket Raised",
        message="A new ticket regarding model latency was submitted.",
        notification_type=NotificationType.ALERT
    )

    # 8. Create Activity Logs
    print("Creating activity logs...")
    ActivityLog.objects.create(
        user=admin,
        action="SYSTEM_INIT",
        details={"message": "System database seeded with mock data."},
        ip_address="127.0.0.1"
    )
    ActivityLog.objects.create(
        user=employee,
        action="TASK_UPDATE",
        details={"message": "Task 'Write API Authentication Docs' marked as DONE."},
        ip_address="127.0.0.1"
    )

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
