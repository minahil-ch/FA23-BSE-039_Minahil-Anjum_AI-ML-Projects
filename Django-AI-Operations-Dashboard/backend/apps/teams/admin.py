from django.contrib import admin
from teams.models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'leader', 'created_at']
    search_fields = ['name']
    list_filter = ['department', 'leader', 'created_at']
    ordering = ['name']
