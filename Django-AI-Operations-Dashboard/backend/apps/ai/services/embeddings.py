"""
Embedding generation using TF-IDF + L2 normalization.

Works offline without API keys. Vectors are stored as JSON in DocumentChunk.
For production you can swap this module to use OpenAI or sentence-transformers.
"""

import logging
import math
from collections import Counter

logger = logging.getLogger('ai')

# In-memory cache: document_id -> fitted vocabulary for that document's chunks
# Rebuilt on each search across all accessible chunks (simple but correct for dev)
_vocabulary_cache: dict[str, list[str]] = {}


def _tokenize(text: str) -> list[str]:
    """Simple word tokenizer — lowercase alphanumeric tokens."""
    import re
    return re.findall(r'\b[a-z0-9]+\b', text.lower())


def build_vocabulary(texts: list[str], max_features: int = 2000) -> list[str]:
    """
    Pick the most frequent tokens across all texts as vocabulary.
    TF-IDF is computed only over this fixed vocabulary.
    """
    counter: Counter = Counter()
    for text in texts:
        counter.update(_tokenize(text))
    # Keep top N tokens by frequency
    return [word for word, _ in counter.most_common(max_features)]


def text_to_tfidf_vector(text: str, vocabulary: list[str], idf_map: dict[str, float]) -> list[float]:
    """
    Convert one text into a TF-IDF vector aligned with vocabulary indices.
    idf_map: precomputed inverse document frequency per token.
    """
    tokens = _tokenize(text)
    if not tokens or not vocabulary:
        return [0.0] * len(vocabulary)

    tf = Counter(tokens)
    total = len(tokens)
    vec = []
    for term in vocabulary:
        term_freq = tf.get(term, 0) / total
        vec.append(term_freq * idf_map.get(term, 1.0))

    return _l2_normalize(vec)


def _l2_normalize(vec: list[float]) -> list[float]:
    """Unit-length vector for cosine similarity via dot product."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec
    return [x / norm for x in vec]


def compute_idf(corpus: list[str], vocabulary: list[str]) -> dict[str, float]:
    """Inverse document frequency: log(N / df) for each vocabulary term."""
    n_docs = len(corpus) or 1
    df: Counter = Counter()
    for doc in corpus:
        tokens = set(_tokenize(doc))
        for term in vocabulary:
            if term in tokens:
                df[term] += 1

    return {term: math.log((n_docs + 1) / (df.get(term, 0) + 1)) + 1 for term in vocabulary}


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a batch of texts with a shared vocabulary + IDF.
    Returns one vector per input text.
    """
    if not texts:
        return []

    vocabulary = build_vocabulary(texts)
    idf_map = compute_idf(texts, vocabulary)
    return [text_to_tfidf_vector(t, vocabulary, idf_map) for t in texts]


def embed_single(text: str, corpus: list[str] | None = None) -> list[float]:
    """
    Embed one query string using corpus vocabulary (all stored chunks).
    Pass corpus=all_chunk_texts so query lives in same vector space.
    """
    corpus = corpus or [text]
    vocabulary = build_vocabulary(corpus)
    idf_map = compute_idf(corpus, vocabulary)
    return text_to_tfidf_vector(text, vocabulary, idf_map)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Dot product of L2-normalized vectors equals cosine similarity."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    return sum(a * b for a, b in zip(vec_a, vec_b))
