"""
Document and text summarization service.

Generates concise summaries from extracted document text or arbitrary input.
"""

import logging
import time

from ai.services.llm import generate_completion, get_model_name
from ai.services.interaction_logger import log_interaction

logger = logging.getLogger('ai')

SUMMARY_SYSTEM = """You are a technical summarizer for an operations dashboard.
Produce a clear, structured summary with:
1. Key points (bullet list)
2. Main topics covered
3. Action items if any
Keep it under 300 words."""


def _extractive_summary(text: str, max_sentences: int = 5) -> str:
    """
    Offline summary: pick first N substantial sentences.
    Works without any LLM API.
    """
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    substantial = [s for s in sentences if len(s.split()) > 8]
    picked = substantial[:max_sentences] if substantial else sentences[:max_sentences]

    if not picked:
        return 'Document contains insufficient text for summarization.'

    bullets = '\n'.join(f'• {s.strip()}' for s in picked)
    return f"**Document Summary**\n\n{bullets}\n\n*(Generated in local extractive mode.)*"


def summarize_text(text: str, title: str = 'Document', user=None) -> dict:
    """
    Generate summary for given text (full document or excerpt).

    Returns dict with summary, model_used, word_count.
    """
    start = time.time()
    if not text or len(text.strip()) < 50:
        summary = 'Text too short to summarize. Upload a document with more content.'
        duration_ms = int((time.time() - start) * 1000)
        return {'summary': summary, 'model_used': get_model_name(), 'duration_ms': duration_ms}

    import os
    if os.getenv('OPENAI_API_KEY'):
        user_prompt = f"Summarize this document titled '{title}':\n\n{text[:6000]}"
        summary, tokens = generate_completion(SUMMARY_SYSTEM, user_prompt, max_tokens=400)
        model = get_model_name()
    else:
        summary = _extractive_summary(text)
        tokens = len(summary.split())
        model = 'local-extractive'

    duration_ms = int((time.time() - start) * 1000)

    if user:
        log_interaction(
            user=user,
            interaction_type='SUMMARIZE',
            input_data={'title': title, 'text_length': len(text)},
            output_data={'summary': summary[:500]},
            model_used=model,
            tokens_used=tokens,
            duration_ms=duration_ms,
        )

    return {'summary': summary, 'model_used': model, 'duration_ms': duration_ms}
