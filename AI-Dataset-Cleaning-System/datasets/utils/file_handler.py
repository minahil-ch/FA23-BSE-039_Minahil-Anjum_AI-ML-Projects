"""Data loading and file handling utilities."""

import logging
from pathlib import Path

import pandas as pd

from core.exceptions import FileValidationError
from core.utils import get_file_extension, is_allowed_dataset_file

logger = logging.getLogger(__name__)


def validate_uploaded_file(uploaded_file) -> str:
    """
    Validate uploaded file format and size.
    Returns detected file type (csv, xlsx, xls).
    """
    if not uploaded_file:
        raise FileValidationError('No file provided.')

    if not is_allowed_dataset_file(uploaded_file.name):
        raise FileValidationError(
            'Invalid file format. Only CSV and Excel (.xlsx, .xls) files are allowed.'
        )

    ext = get_file_extension(uploaded_file.name)
    type_map = {'.csv': 'csv', '.xlsx': 'xlsx', '.xls': 'xls'}
    return type_map[ext]


def load_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
    """Load dataset file into a pandas DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileValidationError(f'File not found: {file_path}')

    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        elif file_type in ('xlsx', 'xls'):
            df = pd.read_excel(file_path, engine='openpyxl')
        else:
            raise FileValidationError(f'Unsupported file type: {file_type}')
    except Exception as exc:
        logger.error('Failed to load file %s: %s', file_path, exc)
        raise FileValidationError(f'Failed to parse file: {exc}') from exc

    if df.empty:
        raise FileValidationError('The uploaded file contains no data.')

    return df


def save_dataframe(df: pd.DataFrame, file_path: str, file_type: str) -> None:
    """Save DataFrame to CSV or Excel."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if file_type == 'csv':
        df.to_csv(file_path, index=False)
    elif file_type in ('xlsx', 'xls'):
        df.to_excel(file_path, index=False, engine='openpyxl')
    else:
        raise FileValidationError(f'Cannot save as {file_type}')
