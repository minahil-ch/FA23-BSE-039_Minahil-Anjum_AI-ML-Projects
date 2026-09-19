"""
Document text extraction and chunking.

Supports PDF (pypdf), DOCX (python-docx), and plain TXT files.
Chunks are ~500 characters with overlap for better RAG retrieval.
"""

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger('ai')

# Chunk size in characters — balance between context and retrieval precision
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


def get_file_extension(filename: str) -> str:
    """Return lowercase extension including the dot, e.g. '.pdf'."""
    return Path(filename).suffix.lower()


def validate_file_type(filename: str) -> bool:
    """Only PDF, DOCX, and TXT are accepted for AI processing."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path: str) -> str:
    """Read all pages from a PDF and concatenate their text."""
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return '\n\n'.join(pages)


def extract_text_from_docx(file_path: str) -> str:
    """Extract paragraph text from a Word document."""
    from docx import Document as DocxDocument

    doc = DocxDocument(file_path)
    return '\n\n'.join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_from_txt(file_path: str) -> str:
    """Read plain text with UTF-8 fallback to latin-1."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def extract_text(file_path: str) -> str:
    """
    Route to the correct extractor based on file extension.
    Raises ValueError for unsupported types.
    """
    ext = get_file_extension(file_path)
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    if ext == '.docx':
        return extract_text_from_docx(file_path)
    if ext == '.txt':
        return extract_text_from_txt(file_path)
    raise ValueError(f'Unsupported file type: {ext}. Allowed: PDF, DOCX, TXT.')


def clean_text(text: str) -> str:
    """Normalize whitespace so chunks are cleaner."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks for embedding.

    Overlap helps RAG retrieve context that spans chunk boundaries.
    """
    text = clean_text(text)
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
        if start >= len(text):
            break

    return chunks


def process_document_file(file_path: str) -> tuple[str, list[str]]:
    """
    Full pipeline: extract text then chunk it.
    Returns (full_text, list_of_chunks).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File not found: {file_path}')

    if not validate_file_type(file_path):
        raise ValueError(
            f'Unsupported file: {get_file_extension(file_path)}. Upload PDF, DOCX, or TXT only.'
        )

    raw_text = extract_text(file_path)
    cleaned = clean_text(raw_text)
    chunks = split_into_chunks(cleaned)
    logger.info('Extracted %d chars, %d chunks from %s', len(cleaned), len(chunks), file_path)
    return cleaned, chunks
