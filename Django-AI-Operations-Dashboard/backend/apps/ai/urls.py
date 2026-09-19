"""
AI app URL routing — mounted at /api/ai/ in config/urls.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ai.views import (
    ChatView,
    ChatSessionViewSet,
    ClassifyTicketView,
    SummarizeView,
    WeeklyReportViewSet,
    AgentRunViewSet,
    AIInteractionLogViewSet,
    DocumentAIViewSet,
)

router = DefaultRouter()
router.register(r'chat/sessions', ChatSessionViewSet, basename='chat-session')
router.register(r'reports', WeeklyReportViewSet, basename='weekly-report')
router.register(r'agent/runs', AgentRunViewSet, basename='agent-run')
router.register(r'interactions', AIInteractionLogViewSet, basename='ai-interaction')
router.register(r'documents', DocumentAIViewSet, basename='ai-document')

urlpatterns = [
    path('chat/', ChatView.as_view(), name='ai-chat'),
    path('classify-ticket/', ClassifyTicketView.as_view(), name='ai-classify-ticket'),
    path('summarize/', SummarizeView.as_view(), name='ai-summarize'),
    path('', include(router.urls)),
]
