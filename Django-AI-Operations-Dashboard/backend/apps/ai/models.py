"""
AI app database models.

Each model maps to one AI capability:
- DocumentChunk: text chunks + embedding vectors for RAG retrieval
- ChatSession / ChatMessage: RAG chatbot conversation history
- AIInteractionLog: audit trail for every AI API call
- WeeklyReport: generated operational reports
- AgentRun / AgentApproval: autonomous agent with human-in-the-loop
"""

from django.db import models
from django.conf import settings


class ProcessingStatus(models.TextChoices):
    """Document ingestion pipeline states."""
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'


class DocumentChunk(models.Model):
    """
    A single text chunk from an uploaded document with its embedding vector.
    Stored in SQLite as JSON so we avoid an external vector DB for local dev.
    """

    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    chunk_index = models.PositiveIntegerField(
        help_text='Order of this chunk inside the parent document.',
    )
    content = models.TextField(help_text='Raw text extracted for this chunk.')
    # Embedding stored as JSON list of floats — works with SQLite/PostgreSQL
    embedding = models.JSONField(default=list, blank=True)
    token_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document', 'chunk_index']
        unique_together = ['document', 'chunk_index']

    def __str__(self):
        return f'Chunk {self.chunk_index} of {self.document.title}'


class ChatSession(models.Model):
    """Groups related chat messages for one user conversation."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
    )
    title = models.CharField(max_length=200, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title} ({self.user.username})'


class ChatMessage(models.Model):
    """Single message in a RAG chat session (user question or AI answer)."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    # Source references returned by RAG — list of {document_id, title, chunk_index, excerpt}
    sources = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}...'


class AIInteractionLog(models.Model):
    """
    Persistent log of every AI operation for auditing and debugging.
    Requirement #9: store every AI interaction.
    """

    INTERACTION_TYPES = [
        ('RAG_CHAT', 'RAG Chat'),
        ('CLASSIFY_TICKET', 'Ticket Classification'),
        ('SUMMARIZE', 'Document Summary'),
        ('GENERATE_REPORT', 'Report Generation'),
        ('AGENT_RUN', 'Agent Run'),
        ('EMBED_DOCUMENT', 'Document Embedding'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_interactions',
    )
    interaction_type = models.CharField(max_length=30, choices=INTERACTION_TYPES)
    input_data = models.JSONField(default=dict, help_text='Request payload sent to AI.')
    output_data = models.JSONField(default=dict, help_text='Response returned by AI.')
    model_used = models.CharField(max_length=100, default='local-fallback')
    tokens_used = models.PositiveIntegerField(default=0)
    duration_ms = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.interaction_type} @ {self.created_at:%Y-%m-%d %H:%M}'


class WeeklyReport(models.Model):
    """AI-generated weekly operational report stored for download/review."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weekly_reports',
    )
    title = models.CharField(max_length=200)
    week_start = models.DateField()
    week_end = models.DateField()
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AgentRun(models.Model):
    """
    Record of an AI agent execution.
    The agent receives a user request, picks a tool, and may require approval.
    """

    STATUS_CHOICES = [
        ('RUNNING', 'Running'),
        ('AWAITING_APPROVAL', 'Awaiting Approval'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_runs',
    )
    user_request = models.TextField(help_text='Original natural-language request from user.')
    selected_tool = models.CharField(max_length=50, blank=True)
    tool_input = models.JSONField(default=dict, blank=True)
    tool_output = models.JSONField(default=dict, blank=True)
    final_answer = models.TextField(blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='RUNNING')
    requires_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'AgentRun #{self.pk} — {self.status}'


class AgentApproval(models.Model):
    """
    Human approval gate before the agent executes sensitive actions
    (e.g. assigning tickets, sending emails).
    """

    DECISION_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    agent_run = models.OneToOneField(
        AgentRun,
        on_delete=models.CASCADE,
        related_name='approval',
    )
    action_description = models.TextField(
        help_text='Plain-English description of what the agent wants to do.',
    )
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES, default='PENDING')
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_approvals',
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Approval for Run #{self.agent_run_id}: {self.decision}'
