from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for IntelliHire.
    Extends Django's built-in user with role-based access control (RBAC)
    and extra HR-relevant profile fields.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        HR_MANAGER = "HR_MANAGER", "HR Manager"
        RECRUITER = "RECRUITER", "Recruiter"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECRUITER)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    is_active_employee = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_hr_manager(self):
        return self.role == self.Role.HR_MANAGER

    @property
    def is_recruiter(self):
        return self.role == self.Role.RECRUITER
