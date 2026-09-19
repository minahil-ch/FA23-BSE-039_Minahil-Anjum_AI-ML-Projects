from rest_framework import serializers
from documents.models import Document
from users.serializers import CustomUserSerializer
from departments.serializers import DepartmentSerializer


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_detail = CustomUserSerializer(source='uploaded_by', read_only=True)
    department_detail = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'uploaded_by',
            'uploaded_by_detail', 'department', 'department_detail',
            'is_public', 'processing_status', 'file_type', 'chunk_count',
            'ai_summary', 'error_message', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'uploaded_by', 'processing_status', 'file_type',
            'chunk_count', 'ai_summary', 'error_message', 'created_at', 'updated_at',
        ]

    def validate_file(self, value):
        """Only allow PDF, DOCX, and TXT for AI processing."""
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.pdf', '.docx', '.txt']:
            raise serializers.ValidationError(
                'Only PDF, DOCX, and TXT files are supported for AI processing.'
            )
        return value
