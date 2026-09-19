from django.contrib import admin
from documents.models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'department', 'is_public', 'created_at']
    search_fields = ['title']
    list_filter = ['is_public', 'department', 'uploaded_by', 'created_at']
    ordering = ['-created_at']
