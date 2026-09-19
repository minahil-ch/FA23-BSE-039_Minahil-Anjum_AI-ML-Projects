"""Dataset analysis service."""

import logging

import numpy as np
import pandas as pd

from core.exceptions import AnalysisError

logger = logging.getLogger(__name__)


class AnalysisService:
    """Analyze dataset and produce comprehensive statistics."""

    @staticmethod
    def analyze(df: pd.DataFrame) -> dict:
        """Run full analysis on a DataFrame."""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

            missing_by_column = df.isnull().sum().to_dict()
            missing_total = int(df.isnull().sum().sum())
            duplicate_count = int(df.duplicated().sum())

            dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}

            memory_bytes = int(df.memory_usage(deep=True).sum())

            return {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
                'missing_values': {
                    'total': missing_total,
                    'by_column': {k: int(v) for k, v in missing_by_column.items() if v > 0},
                    'percentage': round(missing_total / (len(df) * len(df.columns)) * 100, 2) if len(df) > 0 else 0,
                },
                'duplicate_rows': duplicate_count,
                'data_types': dtypes,
                'memory_usage_bytes': memory_bytes,
                'memory_usage_mb': round(memory_bytes / (1024 * 1024), 4),
                'numeric_columns': numeric_cols,
                'categorical_columns': categorical_cols,
                'numeric_stats': AnalysisService._numeric_stats(df, numeric_cols),
                'categorical_stats': AnalysisService._categorical_stats(df, categorical_cols),
                'sample_rows': [
                    [str(row[col]) if pd.notna(row[col]) else '' for col in df.columns]
                    for _, row in df.head(5).iterrows()
                ],
            }
        except Exception as exc:
            logger.error('Analysis failed: %s', exc)
            raise AnalysisError(f'Analysis failed: {exc}') from exc

    @staticmethod
    def _numeric_stats(df: pd.DataFrame, columns: list) -> dict:
        if not columns:
            return {}
        stats = df[columns].describe().fillna(0).to_dict()
        return {col: {k: float(v) if isinstance(v, (np.floating, float)) else v for k, v in vals.items()}
                for col, vals in stats.items()}

    @staticmethod
    def _categorical_stats(df: pd.DataFrame, columns: list) -> dict:
        result = {}
        for col in columns[:10]:
            value_counts = df[col].value_counts().head(10)
            result[col] = {
                'unique_count': int(df[col].nunique()),
                'top_values': {str(k): int(v) for k, v in value_counts.items()},
            }
        return result

    @staticmethod
    def quick_stats(df: pd.DataFrame) -> dict:
        """Lightweight stats for before/after comparison."""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'missing_values': int(df.isnull().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum()),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 4),
        }
