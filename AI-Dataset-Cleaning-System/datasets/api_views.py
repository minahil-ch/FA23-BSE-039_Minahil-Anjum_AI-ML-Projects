"""REST API views for datasets."""

import logging

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.exceptions import DatasetError
from datasets.models import CleaningJob, Dataset, Report
from datasets.serializers import (
    CleanDatasetSerializer,
    CleaningJobSerializer,
    DatasetSerializer,
    DatasetUploadSerializer,
    ReportSerializer,
)
from datasets.services.orchestrator import DatasetOrchestrator

logger = logging.getLogger(__name__)


class DatasetFilter(filters.FilterSet):
    status = filters.CharFilter()
    file_type = filters.CharFilter()
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Dataset
        fields = ['status', 'file_type', 'name']


class DatasetViewSet(viewsets.ModelViewSet):
    """CRUD and operations for datasets."""

    permission_classes = [IsAuthenticated]
    filterset_class = DatasetFilter
    search_fields = ['name']
    ordering_fields = ['uploaded_at', 'name', 'row_count']
    ordering = ['-uploaded_at']
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return DatasetUploadSerializer
        return DatasetSerializer

    def perform_create(self, serializer):
        try:
            dataset = DatasetOrchestrator.create_dataset(
                user=self.request.user,
                name=serializer.validated_data.get('name', ''),
                uploaded_file=serializer.validated_data['original_file'],
            )
            serializer.instance = dataset
        except DatasetError as exc:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(exc.message) from exc

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'success': True,
            'dataset': DatasetSerializer(serializer.instance, context={'request': request}).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Analyze dataset and return statistics."""
        dataset = self.get_object()
        try:
            analysis = DatasetOrchestrator.analyze(dataset)
            return Response({
                'success': True,
                'analysis': analysis,
                'dataset': DatasetSerializer(dataset, context={'request': request}).data,
            })
        except DatasetError as exc:
            return Response({
                'success': False,
                'error': {'message': exc.message, 'code': exc.code},
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def clean(self, request, pk=None):
        """Run cleaning operations on dataset."""
        dataset = self.get_object()
        serializer = CleanDatasetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            job = DatasetOrchestrator.clean(
                dataset=dataset,
                user=request.user,
                operations=serializer.validated_data.get('operations', []),
                use_suggestions=serializer.validated_data.get('use_suggestions', False),
            )
            dataset.refresh_from_db()
            return Response({
                'success': True,
                'job': CleaningJobSerializer(job).data,
                'dataset': DatasetSerializer(dataset, context={'request': request}).data,
            })
        except DatasetError as exc:
            return Response({
                'success': False,
                'error': {'message': exc.message, 'code': exc.code},
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def visualizations(self, request, pk=None):
        """Get chart data for dataset."""
        dataset = self.get_object()
        use_cleaned = request.query_params.get('cleaned', 'false').lower() == 'true'

        try:
            charts = DatasetOrchestrator.get_visualizations(dataset, use_cleaned=use_cleaned)
            return Response({'success': True, 'charts': charts})
        except DatasetError as exc:
            return Response({
                'success': False,
                'error': {'message': exc.message, 'code': exc.code},
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Generate cleaning report."""
        dataset = self.get_object()
        job_id = request.data.get('job_id')
        job = None

        if job_id:
            job = get_object_or_404(CleaningJob, pk=job_id, user=request.user, dataset=dataset)
        else:
            job = dataset.cleaning_jobs.filter(status='completed').order_by('-started_at').first()

        try:
            report = DatasetOrchestrator.generate_report(dataset, request.user, job)
            return Response({
                'success': True,
                'report': ReportSerializer(report, context={'request': request}).data,
            }, status=status.HTTP_201_CREATED)
        except DatasetError as exc:
            return Response({
                'success': False,
                'error': {'message': exc.message, 'code': exc.code},
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='download/(?P<file_type>csv|xlsx)')
    def download(self, request, pk=None, file_type=None):
        """Download dataset file."""
        dataset = self.get_object()
        variant = request.query_params.get('variant', 'cleaned')

        if variant == 'cleaned' and dataset.cleaned_file:
            file_field = dataset.cleaned_file
        else:
            file_field = dataset.original_file

        ext = file_type
        content_type = 'text/csv' if ext == 'csv' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = f'{dataset.name}_{variant}.{ext}'

        return FileResponse(file_field.open('rb'), as_attachment=True, filename=filename, content_type=content_type)

    @action(detail=True, methods=['get'], url_path='report/download')
    def download_report(self, request, pk=None):
        """Download report PDF."""
        dataset = self.get_object()
        report = dataset.reports.order_by('-created_at').first()

        if not report or not report.pdf_file:
            return Response({
                'success': False,
                'error': {'message': 'No report available.', 'code': 'not_found'},
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            report.pdf_file.open('rb'),
            as_attachment=True,
            filename=f'report_{dataset.name}.pdf',
            content_type='application/pdf',
        )


class CleaningJobViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to cleaning jobs."""

    serializer_class = CleaningJobSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'dataset']
    ordering = ['-started_at']

    def get_queryset(self):
        return CleaningJob.objects.filter(user=self.request.user).select_related('dataset').prefetch_related('history')


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to reports."""

    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['dataset']
    ordering = ['-created_at']

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user).select_related('dataset', 'job')

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download report PDF."""
        report = self.get_object()
        if not report.pdf_file:
            return Response({
                'success': False,
                'error': {'message': 'PDF not available.', 'code': 'not_found'},
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            report.pdf_file.open('rb'),
            as_attachment=True,
            filename=f'report_{report.dataset.name}.pdf',
            content_type='application/pdf',
        )
