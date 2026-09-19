from django.apps import AppConfig


class AiConfig(AppConfig):
    """Django app configuration for all AI features (RAG, agents, reports)."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai'
    verbose_name = 'AI Operations'
