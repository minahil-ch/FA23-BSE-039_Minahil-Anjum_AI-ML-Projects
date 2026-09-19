"""
Vector search over DocumentChunk records stored in the database.

This replaces an external vector DB (Chroma/Pinecone) for local development.
Each chunk has a precomputed embedding JSON field; we rank by cosine similarity.
"""

import logging
from django.db.models import Q

from ai.models import DocumentChunk
from ai.services.embeddings import embed_single, cosine_similarity, build_vocabulary, compute_idf, text_to_tfidf_vector

logger = logging.getLogger('ai')


def get_accessible_chunks(user):
    """
    Return chunks the user may search — same RBAC rules as DocumentViewSet.
    Public docs, user's department, or docs they uploaded.
    """
    from documents.models import Document

    if user.is_superuser or user.role == 'ADMIN':
        doc_ids = Document.objects.values_list('id', flat=True)
    else:
        q = Q(is_public=True) | Q(uploaded_by=user)
        if user.department_id:
            q |= Q(department_id=user.department_id)
        doc_ids = Document.objects.filter(q).values_list('id', flat=True)

    return DocumentChunk.objects.filter(
        document_id__in=doc_ids,
        embedding__isnull=False,
    ).exclude(embedding=[]).select_related('document')


def search_similar_chunks(user, query: str, top_k: int = 5) -> list[dict]:
    """
    Semantic search: embed query, score all accessible chunks, return top_k.

    Each result dict contains chunk object, score, and citation metadata.
    """
    chunks_qs = list(get_accessible_chunks(user))
    if not chunks_qs:
        return []

    # Build shared vocabulary from entire accessible corpus + query
    corpus = [c.content for c in chunks_qs] + [query]
    vocabulary = build_vocabulary(corpus)
    idf_map = compute_idf(corpus, vocabulary)
    query_vec = text_to_tfidf_vector(query, vocabulary, idf_map)

    scored = []
    for chunk in chunks_qs:
        # Re-embed chunk in same vocabulary space for fair comparison
        chunk_vec = text_to_tfidf_vector(chunk.content, vocabulary, idf_map)
        score = cosine_similarity(query_vec, chunk_vec)
        if score > 0.05:  # ignore very weak matches
            scored.append({
                'chunk': chunk,
                'score': score,
                'document_id': chunk.document_id,
                'document_title': chunk.document.title,
                'chunk_index': chunk.chunk_index,
                'excerpt': chunk.content[:300] + ('...' if len(chunk.content) > 300 else ''),
            })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_k]
