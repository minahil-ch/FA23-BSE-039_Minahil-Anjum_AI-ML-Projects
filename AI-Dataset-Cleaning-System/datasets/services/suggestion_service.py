"""AI-powered cleaning suggestions service."""

import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from datasets.utils.validators import (
    count_invalid_emails,
    count_invalid_phones,
    detect_email_columns,
    detect_phone_columns,
    pd_notna,
)

logger = logging.getLogger(__name__)


class SuggestionService:
    """Detect data quality issues and recommend cleaning strategies."""

    @staticmethod
    def generate_suggestions(df: pd.DataFrame) -> list:
        """Return prioritized list of cleaning suggestions."""
        suggestions = []

        suggestions.extend(SuggestionService._missing_value_suggestions(df))
        suggestions.extend(SuggestionService._duplicate_suggestions(df))
        suggestions.extend(SuggestionService._datatype_suggestions(df))
        suggestions.extend(SuggestionService._outlier_suggestions(df))
        suggestions.extend(SuggestionService._text_format_suggestions(df))
        suggestions.extend(SuggestionService._email_suggestions(df))
        suggestions.extend(SuggestionService._phone_suggestions(df))

        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda s: priority_order.get(s['priority'], 3))
        return suggestions

    @staticmethod
    def _missing_value_suggestions(df: pd.DataFrame) -> list:
        suggestions = []
        missing = df.isnull().sum()
        cols_with_missing = missing[missing > 0]

        if cols_with_missing.empty:
            return suggestions

        total_missing = int(missing.sum())
        pct = round(total_missing / (len(df) * len(df.columns)) * 100, 2)

        for col, count in cols_with_missing.items():
            col_pct = round(count / len(df) * 100, 2)
            is_numeric = pd.api.types.is_numeric_dtype(df[col])
            if col_pct > 50:
                strategy = 'remove_column'
                action = f'Consider removing column "{col}" ({col_pct}% missing)'
            elif col_pct > 20:
                strategy = 'fill_median' if is_numeric else 'fill_mode'
                action = f'Fill missing values in "{col}" using {strategy.replace("fill_", "")}'
            else:
                strategy = 'fill_mean' if is_numeric else 'fill_mode'
                action = f'Fill missing values in "{col}" using {strategy.replace("fill_", "")}'

            suggestions.append({
                'type': 'missing_values',
                'priority': 'high' if col_pct > 30 else 'medium',
                'column': col,
                'count': int(count),
                'percentage': col_pct,
                'strategy': strategy,
                'message': action,
                'operation': {
                    'name': 'fill_missing',
                    'params': {'column': col, 'method': strategy.replace('fill_', '')},
                } if strategy.startswith('fill_') else {
                    'name': 'remove_missing',
                    'params': {'column': col},
                },
            })

        if total_missing > 0 and len(cols_with_missing) > 3:
            suggestions.append({
                'type': 'missing_values',
                'priority': 'medium',
                'column': None,
                'count': total_missing,
                'percentage': pct,
                'strategy': 'remove_rows',
                'message': f'{total_missing} total missing values across {len(cols_with_missing)} columns',
                'operation': {'name': 'remove_missing', 'params': {}},
            })

        return suggestions

    @staticmethod
    def _duplicate_suggestions(df: pd.DataFrame) -> list:
        dup_count = int(df.duplicated().sum())
        if dup_count == 0:
            return []

        return [{
            'type': 'duplicate_rows',
            'priority': 'high',
            'column': None,
            'count': dup_count,
            'percentage': round(dup_count / len(df) * 100, 2),
            'strategy': 'remove_duplicates',
            'message': f'Remove {dup_count} duplicate row(s)',
            'operation': {'name': 'remove_duplicates', 'params': {}},
        }]

    @staticmethod
    def _datatype_suggestions(df: pd.DataFrame) -> list:
        suggestions = []
        for col in df.columns:
            if df[col].dtype == object:
                numeric_attempt = pd.to_numeric(df[col], errors='coerce')
                valid_ratio = numeric_attempt.notna().sum() / max(len(df), 1)
                if 0.5 < valid_ratio < 1.0:
                    invalid = int((~numeric_attempt.notna() & df[col].notna()).sum())
                    suggestions.append({
                        'type': 'invalid_datatype',
                        'priority': 'medium',
                        'column': col,
                        'count': invalid,
                        'percentage': round(invalid / len(df) * 100, 2),
                        'strategy': 'convert_numeric',
                        'message': f'Convert "{col}" to numeric ({invalid} invalid values)',
                        'operation': {
                            'name': 'convert_datatype',
                            'params': {'column': col, 'dtype': 'float'},
                        },
                    })
        return suggestions

    @staticmethod
    def _outlier_suggestions(df: pd.DataFrame) -> list:
        suggestions = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols[:5]:
            series = df[col].dropna()
            if len(series) < 10:
                continue

            try:
                clf = IsolationForest(contamination=0.05, random_state=42)
                preds = clf.fit_predict(series.values.reshape(-1, 1))
                outlier_count = int((preds == -1).sum())
            except Exception:
                q1, q3 = series.quantile(0.25), series.quantile(0.75)
                iqr = q3 - q1
                outlier_count = int(
                    ((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum()
                )

            if outlier_count > 0:
                suggestions.append({
                    'type': 'outliers',
                    'priority': 'medium',
                    'column': col,
                    'count': outlier_count,
                    'percentage': round(outlier_count / len(df) * 100, 2),
                    'strategy': 'remove_outliers',
                    'message': f'Remove {outlier_count} outlier(s) in "{col}" using Isolation Forest',
                    'operation': {
                        'name': 'remove_outliers',
                        'params': {'column': col, 'method': 'isolation_forest'},
                    },
                })

        return suggestions

    @staticmethod
    def _text_format_suggestions(df: pd.DataFrame) -> list:
        suggestions = []
        text_cols = df.select_dtypes(include=['object']).columns.tolist()

        for col in text_cols:
            extra_spaces = df[col].apply(
                lambda x: pd_notna(x) and str(x) != str(x).strip()
            ).sum()
            mixed_case = df[col].apply(
                lambda x: pd_notna(x) and str(x) != str(x).lower() and str(x) != str(x).upper()
            ).sum()

            if extra_spaces > 0:
                suggestions.append({
                    'type': 'text_formatting',
                    'priority': 'low',
                    'column': col,
                    'count': int(extra_spaces),
                    'percentage': round(extra_spaces / len(df) * 100, 2),
                    'strategy': 'trim_spaces',
                    'message': f'Remove extra spaces in "{col}" ({extra_spaces} cells)',
                    'operation': {
                        'name': 'remove_extra_spaces',
                        'params': {'column': col},
                    },
                })

            if mixed_case > len(df) * 0.3:
                suggestions.append({
                    'type': 'text_formatting',
                    'priority': 'low',
                    'column': col,
                    'count': int(mixed_case),
                    'percentage': round(mixed_case / len(df) * 100, 2),
                    'strategy': 'normalize_text',
                    'message': f'Normalize text case in "{col}"',
                    'operation': {
                        'name': 'normalize_text',
                        'params': {'column': col, 'case': 'lower'},
                    },
                })

        return suggestions

    @staticmethod
    def _email_suggestions(df: pd.DataFrame) -> list:
        email_cols = detect_email_columns(df)
        invalid = count_invalid_emails(df, email_cols)
        suggestions = []

        for col, count in invalid.items():
            suggestions.append({
                'type': 'invalid_emails',
                'priority': 'high',
                'column': col,
                'count': count,
                'percentage': round(count / len(df) * 100, 2),
                'strategy': 'flag_or_remove',
                'message': f'{count} invalid email(s) found in "{col}"',
                'operation': {
                    'name': 'remove_invalid_emails',
                    'params': {'column': col},
                },
            })

        return suggestions

    @staticmethod
    def _phone_suggestions(df: pd.DataFrame) -> list:
        phone_cols = detect_phone_columns(df)
        invalid = count_invalid_phones(df, phone_cols)
        suggestions = []

        for col, count in invalid.items():
            suggestions.append({
                'type': 'invalid_phones',
                'priority': 'medium',
                'column': col,
                'count': count,
                'percentage': round(count / len(df) * 100, 2),
                'strategy': 'flag_or_remove',
                'message': f'{count} invalid phone number(s) found in "{col}"',
                'operation': {
                    'name': 'remove_invalid_phones',
                    'params': {'column': col},
                },
            })

        return suggestions
