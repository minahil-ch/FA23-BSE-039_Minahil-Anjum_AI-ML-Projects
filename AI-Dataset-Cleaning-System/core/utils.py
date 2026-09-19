"""Shared utility functions."""

import re
from pathlib import Path

from django.conf import settings


def get_file_extension(filename: str) -> str:
    """Return lowercase file extension including dot."""
    return Path(filename).suffix.lower()


def is_allowed_dataset_file(filename: str) -> bool:
    """Check if file extension is allowed for dataset upload."""
    return get_file_extension(filename) in settings.ALLOWED_DATASET_EXTENSIONS


def format_bytes(size_bytes: int) -> str:
    """Human-readable byte size."""
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size_bytes < 1024:
            return f'{size_bytes:.2f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.2f} TB'


def safe_filename(name: str) -> str:
    """Sanitize filename for storage."""
    name = re.sub(r'[^\w\s\-.]', '', name)
    return name.replace(' ', '_')[:200]
