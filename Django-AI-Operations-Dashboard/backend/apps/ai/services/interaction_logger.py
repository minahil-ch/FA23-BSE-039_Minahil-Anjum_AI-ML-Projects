"""
Centralized AI interaction logging.

Every AI feature calls log_interaction() so Requirement #9 is satisfied.
"""

import logging

from ai.models import AIInteractionLog

logger = logging.getLogger('ai')


def log_interaction(
    user,
    interaction_type: str,
    input_data: dict,
    output_data: dict,
    model_used: str = 'local-fallback',
    tokens_used: int = 0,
    duration_ms: int = 0,
    success: bool = True,
    error_message: str = '',
) -> AIInteractionLog:
    """
    Persist one AI operation to the database and file logger.
    """
    record = AIInteractionLog.objects.create(
        user=user,
        interaction_type=interaction_type,
        input_data=input_data,
        output_data=output_data,
        model_used=model_used,
        tokens_used=tokens_used,
        duration_ms=duration_ms,
        success=success,
        error_message=error_message,
    )
    logger.info(
        'AI [%s] user=%s success=%s duration=%dms',
        interaction_type,
        getattr(user, 'username', 'anonymous'),
        success,
        duration_ms,
    )
    return record
