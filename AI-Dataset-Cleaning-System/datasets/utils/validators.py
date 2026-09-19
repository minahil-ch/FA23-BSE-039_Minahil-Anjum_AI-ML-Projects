"""Data validation utilities for emails, phones, and text."""

import re

EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)
PHONE_PATTERN = re.compile(
    r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$'
)


def is_valid_email(value) -> bool:
    """Check if value is a valid email address."""
    if value is None or (isinstance(value, float) and str(value) == 'nan'):
        return True
    return bool(EMAIL_PATTERN.match(str(value).strip()))


def is_valid_phone(value) -> bool:
    """Check if value is a valid phone number."""
    if value is None or (isinstance(value, float) and str(value) == 'nan'):
        return True
    cleaned = re.sub(r'[\s\-\(\)\.]', '', str(value))
    if len(cleaned) < 7 or len(cleaned) > 15:
        return False
    return bool(PHONE_PATTERN.match(str(value).strip()))


def detect_email_columns(df) -> list:
    """Detect columns likely containing email addresses."""
    email_cols = []
    for col in df.columns:
        col_lower = str(col).lower()
        if 'email' in col_lower or 'e-mail' in col_lower or 'mail' in col_lower:
            email_cols.append(col)
    return email_cols


def detect_phone_columns(df) -> list:
    """Detect columns likely containing phone numbers."""
    phone_cols = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(kw in col_lower for kw in ('phone', 'mobile', 'tel', 'contact')):
            phone_cols.append(col)
    return phone_cols


def count_invalid_emails(df, columns: list) -> dict:
    """Count invalid emails per column."""
    result = {}
    for col in columns:
        if col in df.columns:
            invalid = df[col].apply(lambda x: not is_valid_email(x) if pd_notna(x) else False)
            count = int(invalid.sum())
            if count > 0:
                result[col] = count
    return result


def count_invalid_phones(df, columns: list) -> dict:
    """Count invalid phone numbers per column."""
    result = {}
    for col in columns:
        if col in df.columns:
            invalid = df[col].apply(lambda x: not is_valid_phone(x) if pd_notna(x) else False)
            count = int(invalid.sum())
            if count > 0:
                result[col] = count
    return result


def pd_notna(value) -> bool:
    """Safe check for non-null values."""
    import pandas as pd
    return pd.notna(value) and str(value).strip() != ''
