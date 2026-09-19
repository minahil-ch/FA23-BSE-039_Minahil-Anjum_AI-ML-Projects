from django.contrib import admin
from tickets.models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'priority', 'created_by', 'assigned_to', 'created_at']
    search_fields = ['subject', 'description']
    list_filter = ['status', 'priority', 'assigned_to', 'created_by', 'created_at']
    ordering = ['-created_at']
