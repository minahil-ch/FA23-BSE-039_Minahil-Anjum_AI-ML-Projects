"""
AI ticket classification — predicts category, priority, and department.

Uses keyword rules + optional LLM when OPENAI_API_KEY is set.
Triggered automatically on ticket creation via Celery.
"""

import logging
import re
import time

from ai.services.llm import generate_completion, get_model_name
from ai.services.interaction_logger import log_interaction

logger = logging.getLogger('ai')

# Keyword maps for offline classification (works without API key)
CATEGORY_KEYWORDS = {
    'Hardware': ['laptop', 'monitor', 'keyboard', 'printer', 'hardware', 'device', 'broken screen'],
    'Software': ['bug', 'crash', 'install', 'update', 'software', 'application', 'login error'],
    'Network': ['wifi', 'vpn', 'network', 'connection', 'internet', 'dns', 'firewall'],
    'Access': ['password', 'reset', 'permission', 'access', 'account', 'locked out'],
    'AI/ML': ['model', 'embedding', 'rag', 'vector', 'gpu', 'training', 'inference'],
}

PRIORITY_KEYWORDS = {
    'HIGH': ['urgent', 'critical', 'down', 'outage', 'emergency', 'asap', 'production'],
    'MEDIUM': ['issue', 'problem', 'slow', 'error', 'help'],
    'LOW': ['question', 'request', 'feature', 'enhancement', 'when possible'],
}

DEPARTMENT_KEYWORDS = {
    'IT Support': ['hardware', 'software', 'network', 'password', 'access'],
    'Engineering': ['bug', 'deploy', 'api', 'code', 'development'],
    'AI Operations': ['model', 'embedding', 'rag', 'vector', 'gpu', 'ml'],
    'HR': ['leave', 'payroll', 'benefits', 'onboarding'],
}


def _keyword_score(text: str, keywords: list[str]) -> int:
    """Count how many keywords appear in text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def _classify_by_keywords(text: str, keyword_map: dict) -> tuple[str, float]:
    """Pick category with highest keyword hit count; confidence = hits / total keywords checked."""
    best_cat = list(keyword_map.keys())[0]
    best_score = 0
    for cat, kws in keyword_map.items():
        score = _keyword_score(text, kws)
        if score > best_score:
            best_score = score
            best_cat = cat
    confidence = min(0.95, 0.5 + best_score * 0.15) if best_score else 0.4
    return best_cat, round(confidence, 2)


def classify_ticket(subject: str, description: str, user=None) -> dict:
    """
    Predict ticket category, priority, and suggested department.

    Returns dict with ai_category, ai_priority, ai_department, ai_confidence.
    """
    start = time.time()
    combined = f'{subject} {description}'

    # Offline keyword classification (always runs)
    category, cat_conf = _classify_by_keywords(combined, CATEGORY_KEYWORDS)
    priority, pri_conf = _classify_by_keywords(combined, PRIORITY_KEYWORDS)
    department, dept_conf = _classify_by_keywords(combined, DEPARTMENT_KEYWORDS)

    # Normalize priority to ticket model choices
    priority_map = {'HIGH': 'HIGH', 'MEDIUM': 'MEDIUM', 'LOW': 'LOW'}
    ai_priority = priority_map.get(priority, 'MEDIUM')
    confidence = round((cat_conf + pri_conf + dept_conf) / 3, 2)

    result = {
        'ai_category': category,
        'ai_priority': ai_priority,
        'ai_department': department,
        'ai_confidence': confidence,
        'model_used': 'keyword-classifier',
    }

    # Optional LLM refinement when API key available
    import os
    if os.getenv('OPENAI_API_KEY'):
        system = (
            'Classify support tickets. Reply in JSON only: '
            '{"category":"...", "priority":"LOW|MEDIUM|HIGH", "department":"...", "confidence":0.0-1.0}'
        )
        user_prompt = f'Subject: {subject}\nDescription: {description}'
        text, _ = generate_completion(system, user_prompt, max_tokens=150)
        try:
            import json
            match = re.search(r'\{[^}]+\}', text)
            if match:
                parsed = json.loads(match.group())
                result['ai_category'] = parsed.get('category', category)
                result['ai_priority'] = parsed.get('priority', ai_priority)
                result['ai_department'] = parsed.get('department', department)
                result['ai_confidence'] = float(parsed.get('confidence', confidence))
                result['model_used'] = get_model_name()
        except Exception as exc:
            logger.debug('LLM classification parse failed: %s', exc)

    duration_ms = int((time.time() - start) * 1000)
    if user:
        log_interaction(
            user=user,
            interaction_type='CLASSIFY_TICKET',
            input_data={'subject': subject, 'description': description[:500]},
            output_data=result,
            model_used=result['model_used'],
            duration_ms=duration_ms,
        )

    return result
