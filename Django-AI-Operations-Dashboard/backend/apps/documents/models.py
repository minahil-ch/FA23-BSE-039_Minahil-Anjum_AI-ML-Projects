from django.db import models
from django.conf import settings
from departments.models import Department


class Document(models.Model):
    """
    Uploaded document with AI processing metadata.

    After upload, Celery task extracts text, chunks it, and stores embeddings.
    """

    # Processing status tracks the async ingestion pipeline
    PROCESSING_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    is_public = models.BooleanField(default=True)

    # AI processing fields
    processing_status = models.CharField(
        max_length=20, choices=PROCESSING_STATUS, default='PENDING',
        help_text='Status of text extraction and embedding pipeline.',
    )
    file_type = models.CharField(max_length=10, blank=True, help_text='e.g. .pdf, .docx, .txt')
    extracted_text = models.TextField(blank=True, help_text='Full text extracted from file.')
    chunk_count = models.PositiveIntegerField(default=0, help_text='Number of RAG chunks created.')
    ai_summary = models.TextField(blank=True, help_text='AI-generated document summary.')
    error_message = models.TextField(blank=True, help_text='Error details if processing failed.')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
