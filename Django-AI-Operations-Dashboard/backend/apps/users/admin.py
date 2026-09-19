from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'team', 'is_staff']
    list_filter = ['role', 'department', 'team', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Fields', {'fields': ('role', 'phone_number', 'department', 'team', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Fields', {
            'classes': ('wide',),
            'fields': ('role', 'phone_number', 'department', 'team', 'avatar')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
