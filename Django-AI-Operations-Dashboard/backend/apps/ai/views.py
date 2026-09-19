"""
REST API views for all AI features.

Endpoints:
  POST /api/ai/chat/              — RAG chatbot
  GET  /api/ai/chat/sessions/     — list chat sessions
  GET  /api/ai/chat/sessions/<id>/ — session with messages
  POST /api/ai/classify-ticket/   — classify ticket text
  POST /api/ai/summarize/         — summarize text or document
  POST /api/ai/reports/generate/  — trigger weekly report (Celery)
  GET  /api/ai/reports/           — list reports
  GET  /api/ai/reports/<id>/      — report detail
  POST /api/ai/agent/run/         — run AI agent
  GET  /api/ai/agent/runs/        — list agent runs
  POST /api/ai/agent/runs/<id>/approve/ — approve/reject agent action
  GET  /api/ai/interactions/      — AI interaction logs
  POST /api/ai/documents/<id>/reprocess/ — re-trigger document processing
  GET  /api/ai/documents/<id>/chunks/    — list document chunks
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from ai.models import (
    ChatSession, ChatMessage, WeeklyReport, AgentRun, AIInteractionLog, DocumentChunk,
)
from ai.serializers import (
    ChatSessionSerializer, ChatRequestSerializer, ClassifyTicketSerializer,
    SummarizeSerializer, GenerateReportSerializer, WeeklyReportSerializer,
    AgentRunSerializer, AgentRequestSerializer, AgentApprovalActionSerializer,
    AIInteractionLogSerializer, DocumentChunkSerializer,
)
from ai.services.rag import rag_answer
from ai.services.classifier import classify_ticket
from ai.services.summarizer import summarize_text
from ai.services.agent import run_agent, approve_agent_action
from ai.tasks import generate_report_task, process_document_task
from documents.models import Document
from users.permissions import IsManager


class ChatView(APIView):
    """RAG chatbot — answers only from uploaded documents with source citations."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']
        session_id = serializer.validated_data.get('session_id')

        # Get or create chat session
        if session_id:
            session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=question[:80],
            )

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=question)

        # Run RAG pipeline
        result = rag_answer(request.user, question)

        # Save assistant message with sources
        assistant_msg = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=result['answer'],
            sources=result['sources'],
        )
        session.updated_at = timezone.now()
        session.save(update_fields=['updated_at'])

        return Response({
            'session_id': session.id,
            'answer': result['answer'],
            'sources': result['sources'],
            'model_used': result['model_used'],
            'duration_ms': result['duration_ms'],
            'message_id': assistant_msg.id,
        })


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve user's chat sessions."""
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('messages')


class ClassifyTicketView(APIView):
    """AI ticket classification — category, priority, department."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ClassifyTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = classify_ticket(
            serializer.validated_data['subject'],
            serializer.validated_data['description'],
            user=request.user,
        )
        return Response(result)


class SummarizeView(APIView):
    """Generate AI summary for raw text or an uploaded document."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SummarizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data.get('text', '')
        document_id = serializer.validated_data.get('document_id')

        if document_id:
            doc = get_object_or_404(Document, pk=document_id)
            text = doc.extracted_text or doc.ai_summary or ''
            title = doc.title
        else:
            title = 'Custom Text'

        if not text:
            return Response(
                {'error': 'No text provided. Pass text or document_id of a processed document.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = summarize_text(text, title=title, user=request.user)
        return Response(result)


class WeeklyReportViewSet(viewsets.ModelViewSet):
    """Generate and list weekly AI reports."""

    serializer_class = WeeklyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER'] or user.is_superuser:
            return WeeklyReport.objects.all()
        return WeeklyReport.objects.filter(created_by=user)

    def create(self, request):
        """POST /api/ai/reports/ — queue report generation via Celery."""
        serializer = GenerateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        today = timezone.now().date()
        week_end = serializer.validated_data.get('week_end') or today
        week_start = serializer.validated_data.get('week_start') or (today - timedelta(days=7))

        report = WeeklyReport.objects.create(
            created_by=request.user,
            title=f'Weekly Report {week_start} — {week_end}',
            week_start=week_start,
            week_end=week_end,
            status='PENDING',
        )

        # Dispatch to Celery (falls back to sync if worker unavailable)
        try:
            generate_report_task.delay(report.id)
        except Exception:
            generate_report_task(report.id)

        return Response(
            WeeklyReportSerializer(report).data,
            status=status.HTTP_202_ACCEPTED,
        )


class AgentRunViewSet(viewsets.ReadOnlyModelViewSet):
    """AI Agent runs with human approval workflow."""

    serializer_class = AgentRunSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER'] or user.is_superuser:
            return AgentRun.objects.all().select_related('approval')
        return AgentRun.objects.filter(user=user).select_related('approval')

    @action(detail=False, methods=['post'])
    def run(self, request):
        """POST /api/ai/agent/runs/run/ — execute agent on user request."""
        serializer = AgentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agent_run = run_agent(request.user, serializer.validated_data['request'])
        return Response(AgentRunSerializer(agent_run).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """POST /api/ai/agent/runs/<id>/approve/ — human approval gate."""
        agent_run = self.get_object()
        if agent_run.status != 'AWAITING_APPROVAL':
            return Response(
                {'error': 'This agent run is not awaiting approval.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AgentApprovalActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agent_run = approve_agent_action(
            agent_run, request.user, serializer.validated_data['approved']
        )
        return Response(AgentRunSerializer(agent_run).data)


class AIInteractionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit log of every AI interaction — managers/admins see all."""

    serializer_class = AIInteractionLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['interaction_type', 'success']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER'] or user.is_superuser:
            return AIInteractionLog.objects.all()
        return AIInteractionLog.objects.filter(user=user)


class DocumentAIViewSet(viewsets.ViewSet):
    """Document processing endpoints: reprocess and list chunks."""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='reprocess')
    def reprocess(self, request, pk=None):
        """Re-trigger Celery document processing pipeline."""
        doc = get_object_or_404(Document, pk=pk)
        try:
            process_document_task.delay(doc.id)
        except Exception:
            process_document_task(doc.id)
        return Response({'message': f'Reprocessing queued for document {doc.id}.'})

    @action(detail=True, methods=['get'], url_path='chunks')
    def chunks(self, request, pk=None):
        """Return all text chunks for a document."""
        doc = get_object_or_404(Document, pk=pk)
        chunks = DocumentChunk.objects.filter(document=doc)
        return Response(DocumentChunkSerializer(chunks, many=True).data)
