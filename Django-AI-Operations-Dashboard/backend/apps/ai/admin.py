from django.contrib import admin
from ai.models import (
    DocumentChunk, ChatSession, ChatMessage, AIInteractionLog,
    WeeklyReport, AgentRun, AgentApproval,
)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'token_count', 'created_at']
    search_fields = ['document__title', 'content']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'updated_at']
    search_fields = ['title', 'user__username']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'created_at']
    list_filter = ['role']


@admin.register(AIInteractionLog)
class AIInteractionLogAdmin(admin.ModelAdmin):
    list_display = ['interaction_type', 'user', 'model_used', 'success', 'duration_ms', 'created_at']
    list_filter = ['interaction_type', 'success', 'model_used']
    readonly_fields = ['input_data', 'output_data']


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'status', 'week_start', 'week_end', 'created_at']
    list_filter = ['status']


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'selected_tool', 'status', 'requires_approval', 'created_at']
    list_filter = ['status', 'selected_tool']


@admin.register(AgentApproval)
class AgentApprovalAdmin(admin.ModelAdmin):
    list_display = ['agent_run', 'decision', 'decided_by', 'decided_at']
    list_filter = ['decision']
