"""
LLM interface with OpenAI optional fallback to local extractive generation.

Set OPENAI_API_KEY in .env to use GPT; otherwise answers are built from
retrieved document chunks (still valid RAG, no external dependency).
"""

import logging
import os
import time

logger = logging.getLogger('ai')


def get_model_name() -> str:
    """Report which model/provider is active."""
    if os.getenv('OPENAI_API_KEY'):
        return os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    return 'local-extractive-rag'


def generate_completion(system_prompt: str, user_prompt: str, max_tokens: int = 800) -> tuple[str, int]:
    """
    Generate text from system + user prompts.
    Returns (response_text, estimated_tokens_used).
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        return _openai_completion(system_prompt, user_prompt, max_tokens)
    return _local_completion(system_prompt, user_prompt)


def _openai_completion(system_prompt: str, user_prompt: str, max_tokens: int) -> tuple[str, int]:
    """Call OpenAI Chat Completions API."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        text = response.choices[0].message.content or ''
        tokens = response.usage.total_tokens if response.usage else len(text.split())
        logger.info('OpenAI response in %dms, ~%d tokens', int((time.time() - start) * 1000), tokens)
        return text, tokens
    except Exception as exc:
        logger.warning('OpenAI failed (%s), falling back to local', exc)
        return _local_completion(system_prompt, user_prompt)


def _local_completion(system_prompt: str, user_prompt: str) -> tuple[str, int]:
    """
    Offline fallback: synthesize answer from context embedded in user_prompt.
    Used when no API key is configured — still grounded in retrieved chunks.
    """
    # user_prompt typically contains "Context:" section from RAG
    context = ''
    question = user_prompt
    if 'Context:' in user_prompt and 'Question:' in user_prompt:
        parts = user_prompt.split('Question:')
        context = parts[0].replace('Context:', '').strip()
        question = parts[1].strip() if len(parts) > 1 else user_prompt

    if not context.strip():
        answer = (
            "I couldn't find relevant information in your uploaded documents. "
            "Please upload PDF, DOCX, or TXT files and wait for processing to complete."
        )
        return answer, len(answer.split())

    # Build extractive answer from context paragraphs
    paragraphs = [p.strip() for p in context.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [context[:800]]

    summary_parts = paragraphs[:3]
    answer = (
        f"Based on your uploaded documents, here is what I found regarding \"{question}\":\n\n"
        + '\n\n'.join(f"• {p[:400]}" for p in summary_parts)
        + "\n\n*(Local RAG mode — set OPENAI_API_KEY in .env for GPT-powered answers.)*"
    )
    return answer, len(answer.split())
