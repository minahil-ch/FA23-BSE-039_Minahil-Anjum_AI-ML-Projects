"""
Retrieval-Augmented Generation (RAG) chatbot pipeline.

Flow: user question → vector search → build prompt with sources → LLM answer.
Answers are restricted to uploaded document content only.
"""

import logging
import time

from ai.services.vector_store import search_similar_chunks
from ai.services.llm import generate_completion, get_model_name
from ai.services.interaction_logger import log_interaction

logger = logging.getLogger('ai')

RAG_SYSTEM_PROMPT = """You are a helpful assistant for an AI Operations Dashboard.
Answer questions ONLY using the provided document context.
If the context does not contain enough information, say so clearly.
Cite document titles when referencing specific information.
Do not invent facts outside the given context."""


def rag_answer(user, question: str, top_k: int = 5) -> dict:
    """
    Run full RAG pipeline for one user question.

    Returns dict with answer, sources list, model_used, duration_ms.
    """
    start = time.time()
    hits = search_similar_chunks(user, question, top_k=top_k)

    if not hits:
        answer = (
            'No indexed documents found. Upload PDF, DOCX, or TXT files '
            'and wait for background processing to finish before asking questions.'
        )
        duration_ms = int((time.time() - start) * 1000)
        log_interaction(
            user=user,
            interaction_type='RAG_CHAT',
            input_data={'question': question},
            output_data={'answer': answer, 'sources': []},
            model_used=get_model_name(),
            duration_ms=duration_ms,
        )
        return {'answer': answer, 'sources': [], 'model_used': get_model_name(), 'duration_ms': duration_ms}

    # Build context block from top chunks
    context_blocks = []
    sources = []
    for i, hit in enumerate(hits, 1):
        context_blocks.append(
            f"[Source {i}: {hit['document_title']}, chunk {hit['chunk_index']}]\n{hit['chunk'].content}"
        )
        sources.append({
            'document_id': hit['document_id'],
            'document_title': hit['document_title'],
            'chunk_index': hit['chunk_index'],
            'excerpt': hit['excerpt'],
            'relevance_score': round(hit['score'], 4),
        })

    context = '\n\n'.join(context_blocks)
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    answer, tokens = generate_completion(RAG_SYSTEM_PROMPT, user_prompt)
    duration_ms = int((time.time() - start) * 1000)

    log_interaction(
        user=user,
        interaction_type='RAG_CHAT',
        input_data={'question': question, 'top_k': top_k},
        output_data={'answer': answer, 'sources': sources},
        model_used=get_model_name(),
        tokens_used=tokens,
        duration_ms=duration_ms,
    )

    return {
        'answer': answer,
        'sources': sources,
        'model_used': get_model_name(),
        'duration_ms': duration_ms,
    }
