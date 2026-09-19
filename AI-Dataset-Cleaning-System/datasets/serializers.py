"""REST API serializers for datasets."""

from rest_framework import serializers

from .models import CleaningHistory, CleaningJob, Dataset, Report


class DatasetSerializer(serializers.ModelSerializer):
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = (
            'id', 'name', 'file_type', 'file_size', 'file_size_display',
            'status', 'row_count', 'column_count', 'analysis_result',
            'uploaded_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'file_type', 'file_size', 'status', 'row_count',
            'column_count', 'analysis_result', 'uploaded_at', 'updated_at',
        )

    def get_file_size_display(self, obj):
        from core.utils import format_bytes
        return format_bytes(obj.file_size)


class DatasetUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ('name', 'original_file')

    def validate_original_file(self, value):
        from datasets.utils.file_handler import validate_uploaded_file
        validate_uploaded_file(value)
        return value


class CleaningHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningHistory
        fields = ('id', 'operation', 'parameters', 'rows_affected', 'description', 'applied_at')
        read_only_fields = fields


class CleaningJobSerializer(serializers.ModelSerializer):
    history = CleaningHistorySerializer(many=True, read_only=True)
    dataset_name = serializers.CharField(source='dataset.name', read_only=True)

    class Meta:
        model = CleaningJob
        fields = (
            'id', 'dataset', 'dataset_name', 'status', 'operations', 'progress',
            'suggestions', 'before_stats', 'after_stats', 'error_message',
            'started_at', 'completed_at', 'history',
        )
        read_only_fields = (
            'id', 'status', 'progress', 'suggestions', 'before_stats',
            'after_stats', 'error_message', 'started_at', 'completed_at', 'history',
        )


class CleanDatasetSerializer(serializers.Serializer):
    operations = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )
    use_suggestions = serializers.BooleanField(default=False)


class ReportSerializer(serializers.ModelSerializer):
    dataset_name = serializers.CharField(source='dataset.name', read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = (
            'id', 'title', 'dataset', 'dataset_name', 'job', 'summary',
            'comparison', 'pdf_url', 'created_at',
        )
        read_only_fields = fields

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None
