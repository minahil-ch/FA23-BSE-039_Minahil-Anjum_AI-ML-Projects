"""Database models for datasets, cleaning jobs, history, and reports."""

import uuid

from django.conf import settings
from django.db import models


class Dataset(models.Model):
    """Uploaded dataset file and metadata."""

    FILE_TYPE_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('xls', 'Excel (Legacy)'),
    ]
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('analyzed', 'Analyzed'),
        ('cleaned', 'Cleaned'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='datasets',
    )
    name = models.CharField(max_length=255)
    original_file = models.FileField(upload_to='datasets/original/')
    cleaned_file = models.FileField(upload_to='datasets/cleaned/', blank=True, null=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file_size = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    row_count = models.PositiveIntegerField(default=0)
    column_count = models.PositiveIntegerField(default=0)
    analysis_result = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'

    def __str__(self):
        return f'{self.name} ({self.user.username})'


class CleaningJob(models.Model):
    """A cleaning operation job on a dataset."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cleaning_jobs',
    )
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='cleaning_jobs',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    operations = models.JSONField(default=list)
    progress = models.PositiveSmallIntegerField(default=0)
    suggestions = models.JSONField(default=list, blank=True)
    before_stats = models.JSONField(default=dict, blank=True)
    after_stats = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Cleaning Job'
        verbose_name_plural = 'Cleaning Jobs'

    def __str__(self):
        return f'Job {self.id} - {self.dataset.name}'


class CleaningHistory(models.Model):
    """Log of individual cleaning operations applied."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        CleaningJob,
        on_delete=models.CASCADE,
        related_name='history',
    )
    operation = models.CharField(max_length=100)
    parameters = models.JSONField(default=dict, blank=True)
    rows_affected = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['applied_at']
        verbose_name = 'Cleaning History'
        verbose_name_plural = 'Cleaning Histories'

    def __str__(self):
        return f'{self.operation} on {self.job_id}'


class Report(models.Model):
    """Generated cleaning report."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
    )
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='reports',
    )
    job = models.ForeignKey(
        CleaningJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
    )
    title = models.CharField(max_length=255)
    summary = models.JSONField(default=dict)
    comparison = models.JSONField(default=dict)
    pdf_file = models.FileField(upload_to='reports/pdf/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __str__(self):
        return self.title
