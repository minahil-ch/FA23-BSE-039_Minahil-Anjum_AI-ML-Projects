from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "department", "is_active", "date_joined")
    list_filter = ("role", "is_active", "department")
    fieldsets = UserAdmin.fieldsets + (
        ("IntelliHire Profile", {"fields": ("role", "phone_number", "department",
                                             "employee_id", "profile_image", "joining_date")}),
    )
