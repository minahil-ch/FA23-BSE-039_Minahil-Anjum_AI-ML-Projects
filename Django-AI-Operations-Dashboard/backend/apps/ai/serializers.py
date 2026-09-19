"""
DRF serializers for all AI REST API endpoints.
"""

from rest_framework import serializers
from ai.models import (
    DocumentChunk,
    ChatSession,
    ChatMessage,
    AIInteractionLog,
    WeeklyReport,
    AgentRun,
    AgentApproval,
)


class DocumentChunkSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = DocumentChunk
        fields = ['id', 'document', 'document_title', 'chunk_index', 'content', 'token_count', 'created_at']
        read_only_fields = fields


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'sources', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'messages', 'message_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class ChatRequestSerializer(serializers.Serializer):
    """POST body for /api/ai/chat/"""
    question = serializers.CharField(max_length=2000)
    session_id = serializers.IntegerField(required=False, allow_null=True)


class ClassifyTicketSerializer(serializers.Serializer):
    """POST body for /api/ai/classify-ticket/"""
    subject = serializers.CharField(max_length=200)
    description = serializers.CharField()


class SummarizeSerializer(serializers.Serializer):
    """POST body for /api/ai/summarize/"""
    text = serializers.CharField(required=False, allow_blank=True)
    document_id = serializers.IntegerField(required=False, allow_null=True)


class GenerateReportSerializer(serializers.Serializer):
    """POST body for /api/ai/reports/generate/"""
    week_start = serializers.DateField(required=False)
    week_end = serializers.DateField(required=False)


class WeeklyReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = WeeklyReport
        fields = [
            'id', 'title', 'week_start', 'week_end', 'content',
            'status', 'error_message', 'created_by', 'created_by_name', 'created_at',
        ]
        read_only_fields = ['id', 'content', 'status', 'error_message', 'created_at']


class AgentRunSerializer(serializers.ModelSerializer):
    approval = serializers.SerializerMethodField()

    class Meta:
        model = AgentRun
        fields = [
            'id', 'user_request', 'selected_tool', 'tool_input', 'tool_output',
            'final_answer', 'status', 'requires_approval', 'approval',
            'created_at', 'completed_at',
        ]
        read_only_fields = fields

    def get_approval(self, obj):
        if hasattr(obj, 'approval'):
            return AgentApprovalSerializer(obj.approval).data
        return None


class AgentRequestSerializer(serializers.Serializer):
    """POST body for /api/ai/agent/run/"""
    request = serializers.CharField(max_length=2000)


class AgentApprovalSerializer(serializers.ModelSerializer):
    decided_by_name = serializers.CharField(source='decided_by.username', read_only=True)

    class Meta:
        model = AgentApproval
        fields = [
            'id', 'action_description', 'decision', 'decided_by',
            'decided_by_name', 'decided_at', 'created_at',
        ]
        read_only_fields = ['id', 'action_description', 'decided_by', 'decided_at', 'created_at']


class AgentApprovalActionSerializer(serializers.Serializer):
    """POST body for approve/reject agent action."""
    approved = serializers.BooleanField()


class AIInteractionLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AIInteractionLog
        fields = [
            'id', 'user', 'username', 'interaction_type', 'input_data',
            'output_data', 'model_used', 'tokens_used', 'duration_ms',
            'success', 'error_message', 'created_at',
        ]
        read_only_fields = fields
