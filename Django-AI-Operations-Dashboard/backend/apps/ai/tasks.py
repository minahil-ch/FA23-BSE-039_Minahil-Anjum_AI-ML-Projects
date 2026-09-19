"""
Celery background tasks for AI operations.

These run asynchronously via Redis broker:
- process_document_task: extract text, chunk, embed
- classify_ticket_task: AI classification on new tickets
- generate_report_task: weekly report generation
- send_agent_email_task: email delivery
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('ai')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document_task(self, document_id: int):
    """
    Background pipeline after document upload:
    1. Extract text from PDF/DOCX/TXT
    2. Split into chunks
    3. Generate TF-IDF embeddings
    4. Store chunks in vector database (DocumentChunk model)
    """
    from documents.models import Document
    from ai.models import DocumentChunk, ProcessingStatus
    from ai.services.document_processor import process_document_file, get_file_extension
    from ai.services.embeddings import embed_texts
    from ai.services.summarizer import summarize_text
    from ai.services.interaction_logger import log_interaction

    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        return f'Document {document_id} not found'

    document.processing_status = ProcessingStatus.PROCESSING
    document.save(update_fields=['processing_status', 'updated_at'])

    try:
        file_path = document.file.path
        full_text, chunks = process_document_file(file_path)

        # Remove old chunks if reprocessing
        DocumentChunk.objects.filter(document=document).delete()

        if not chunks:
            document.processing_status = ProcessingStatus.FAILED
            document.error_message = 'No text could be extracted from this file.'
            document.save(update_fields=['processing_status', 'error_message', 'updated_at'])
            return 'No text extracted'

        # Batch embed all chunks
        vectors = embed_texts(chunks)
        for idx, (content, vector) in enumerate(zip(chunks, vectors)):
            DocumentChunk.objects.create(
                document=document,
                chunk_index=idx,
                content=content,
                embedding=vector,
                token_count=len(content.split()),
            )

        # Auto-generate summary
        summary_result = summarize_text(full_text, title=document.title, user=document.uploaded_by)

        document.extracted_text = full_text[:50000]  # cap storage size
        document.chunk_count = len(chunks)
        document.file_type = get_file_extension(document.file.name)
        document.ai_summary = summary_result.get('summary', '')
        document.processing_status = ProcessingStatus.COMPLETED
        document.error_message = ''
        document.save(update_fields=[
            'extracted_text', 'chunk_count', 'file_type', 'ai_summary',
            'processing_status', 'error_message', 'updated_at',
        ])

        log_interaction(
            user=document.uploaded_by,
            interaction_type='EMBED_DOCUMENT',
            input_data={'document_id': document_id, 'title': document.title},
            output_data={'chunks': len(chunks), 'status': 'COMPLETED'},
            duration_ms=0,
        )
        logger.info('Processed document %s: %d chunks', document_id, len(chunks))
        return f'Processed document {document_id}: {len(chunks)} chunks'

    except Exception as exc:
        logger.exception('Document processing failed for %s', document_id)
        document.processing_status = ProcessingStatus.FAILED
        document.error_message = str(exc)[:500]
        document.save(update_fields=['processing_status', 'error_message', 'updated_at'])
        raise self.retry(exc=exc)


@shared_task
def classify_ticket_task(ticket_id: int):
    """Run AI classification on a newly created ticket."""
    from tickets.models import Ticket
    from ai.services.classifier import classify_ticket

    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return f'Ticket {ticket_id} not found'

    result = classify_ticket(ticket.subject, ticket.description, user=ticket.created_by)
    ticket.ai_category = result['ai_category']
    ticket.ai_priority = result['ai_priority']
    ticket.ai_department = result['ai_department']
    ticket.ai_confidence = result['ai_confidence']
    ticket.save(update_fields=[
        'ai_category', 'ai_priority', 'ai_department', 'ai_confidence', 'updated_at',
    ])
    return f'Classified ticket {ticket_id}: {result["ai_category"]}'


@shared_task
def generate_report_task(report_id: int):
    """Generate weekly report content in background."""
    from ai.models import WeeklyReport
    from ai.services.report_generator import generate_weekly_report

    try:
        report = WeeklyReport.objects.get(pk=report_id)
    except WeeklyReport.DoesNotExist:
        return f'Report {report_id} not found'

    report.status = 'GENERATING'
    report.save(update_fields=['status'])

    try:
        result = generate_weekly_report(
            report.created_by,
            week_start=report.week_start,
            week_end=report.week_end,
        )
        report.title = result['title']
        report.content = result['content']
        report.status = 'COMPLETED'
        report.save(update_fields=['title', 'content', 'status'])
        return f'Report {report_id} generated'
    except Exception as exc:
        report.status = 'FAILED'
        report.error_message = str(exc)[:500]
        report.save(update_fields=['status', 'error_message'])
        raise


@shared_task
def send_email_task(subject: str, message: str, recipient_list: list):
    """Send email asynchronously (used by agent after approval)."""
    from django.core.mail import send_mail
    from django.conf import settings

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@aiops.local'),
        recipient_list=recipient_list,
        fail_silently=False,
    )
    return f'Email sent to {recipient_list}'
