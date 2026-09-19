"""Dataset cleaning operations service."""

import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler

from core.exceptions import CleaningError
from datasets.utils.validators import is_valid_email, is_valid_phone, pd_notna

logger = logging.getLogger(__name__)


class CleaningService:
    """Apply cleaning operations to datasets."""

    OPERATIONS = {
        'remove_duplicates': 'Remove duplicate rows',
        'fill_missing': 'Fill missing values',
        'remove_missing': 'Remove rows/columns with missing values',
        'convert_datatype': 'Convert column datatype',
        'normalize_text': 'Normalize text formatting',
        'remove_extra_spaces': 'Remove extra whitespace',
        'encode_categorical': 'Encode categorical values',
        'scale_numeric': 'Scale numeric values',
        'detect_outliers': 'Detect outliers',
        'remove_outliers': 'Remove outliers',
        'remove_invalid_emails': 'Remove rows with invalid emails',
        'remove_invalid_phones': 'Remove rows with invalid phone numbers',
    }

    @classmethod
    def apply_operations(cls, df: pd.DataFrame, operations: list) -> tuple:
        """
        Apply a list of cleaning operations.
        Returns (cleaned_df, history_entries).
        """
        result = df.copy()
        history = []
        total = len(operations)

        for idx, op in enumerate(operations):
            name = op.get('name') or op.get('operation')
            params = op.get('params', {})
            if not name:
                continue

            try:
                before_rows = len(result)
                result, description, affected = cls._apply_single(result, name, params)
                history.append({
                    'operation': name,
                    'parameters': params,
                    'rows_affected': affected,
                    'description': description,
                    'progress': int((idx + 1) / total * 100) if total else 100,
                })
                logger.info('Applied %s: %s (rows: %d -> %d)', name, description, before_rows, len(result))
            except Exception as exc:
                logger.error('Cleaning operation %s failed: %s', name, exc)
                raise CleaningError(f'Operation "{name}" failed: {exc}') from exc

        return result, history

    @classmethod
    def _apply_single(cls, df: pd.DataFrame, name: str, params: dict) -> tuple:
        """Apply one operation. Returns (df, description, rows_affected)."""
        handlers = {
            'remove_duplicates': cls._remove_duplicates,
            'fill_missing': cls._fill_missing,
            'remove_missing': cls._remove_missing,
            'convert_datatype': cls._convert_datatype,
            'normalize_text': cls._normalize_text,
            'remove_extra_spaces': cls._remove_extra_spaces,
            'encode_categorical': cls._encode_categorical,
            'scale_numeric': cls._scale_numeric,
            'detect_outliers': cls._detect_outliers,
            'remove_outliers': cls._remove_outliers,
            'remove_invalid_emails': cls._remove_invalid_emails,
            'remove_invalid_phones': cls._remove_invalid_phones,
        }

        handler = handlers.get(name)
        if not handler:
            raise CleaningError(f'Unknown operation: {name}')

        return handler(df, params)

    @staticmethod
    def _remove_duplicates(df: pd.DataFrame, params: dict) -> tuple:
        before = len(df)
        subset = params.get('subset')
        keep = params.get('keep', 'first')
        result = df.drop_duplicates(subset=subset, keep=keep)
        removed = before - len(result)
        return result, f'Removed {removed} duplicate row(s)', removed

    @staticmethod
    def _fill_missing(df: pd.DataFrame, params: dict) -> tuple:
        method = params.get('method', 'mean')
        column = params.get('column')
        columns = [column] if column else df.columns.tolist()
        affected = 0

        for col in columns:
            if col not in df.columns:
                continue
            missing_count = int(df[col].isnull().sum())
            if missing_count == 0:
                continue

            if method == 'mean' and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            elif method == 'median' and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            elif method == 'mode':
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val.iloc[0])
            else:
                df[col] = df[col].fillna(df[col].median() if pd.api.types.is_numeric_dtype(df[col]) else '')
            affected += missing_count

        return df, f'Filled {affected} missing value(s) using {method}', affected

    @staticmethod
    def _remove_missing(df: pd.DataFrame, params: dict) -> tuple:
        column = params.get('column')
        axis = params.get('axis', 0)

        if column and column in df.columns:
            before = len(df)
            result = df.dropna(subset=[column])
            return result, f'Removed {before - len(result)} rows with missing "{column}"', before - len(result)

        if axis == 1:
            before_cols = len(df.columns)
            result = df.dropna(axis=1, thresh=max(1, len(df) // 2))
            return result, f'Removed {before_cols - len(result.columns)} column(s)', before_cols - len(result.columns)

        before = len(df)
        result = df.dropna()
        return result, f'Removed {before - len(result)} rows with any missing values', before - len(result)

    @staticmethod
    def _convert_datatype(df: pd.DataFrame, params: dict) -> tuple:
        column = params['column']
        dtype = params.get('dtype', 'float')

        if column not in df.columns:
            raise CleaningError(f'Column "{column}" not found')

        before_invalid = int(df[column].isnull().sum())
        if dtype in ('int', 'integer'):
            df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
        elif dtype in ('float', 'numeric'):
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif dtype in ('str', 'string', 'object'):
            df[column] = df[column].astype(str)
        elif dtype == 'datetime':
            df[column] = pd.to_datetime(df[column], errors='coerce')
        elif dtype == 'bool':
            df[column] = df[column].astype(bool)

        after_invalid = int(df[column].isnull().sum())
        converted = after_invalid - before_invalid
        return df, f'Converted "{column}" to {dtype}', max(converted, 0)

    @staticmethod
    def _normalize_text(df: pd.DataFrame, params: dict) -> tuple:
        column = params.get('column')
        case = params.get('case', 'lower')
        columns = [column] if column else df.select_dtypes(include=['object']).columns.tolist()
        affected = 0

        for col in columns:
            if col not in df.columns:
                continue
            mask = df[col].apply(pd_notna)
            if case == 'lower':
                df.loc[mask, col] = df.loc[mask, col].astype(str).str.lower()
            elif case == 'upper':
                df.loc[mask, col] = df.loc[mask, col].astype(str).str.upper()
            elif case == 'title':
                df.loc[mask, col] = df.loc[mask, col].astype(str).str.title()
            affected += int(mask.sum())

        return df, f'Normalized text in {len(columns)} column(s) ({case} case)', affected

    @staticmethod
    def _remove_extra_spaces(df: pd.DataFrame, params: dict) -> tuple:
        column = params.get('column')
        columns = [column] if column else df.select_dtypes(include=['object']).columns.tolist()
        affected = 0

        for col in columns:
            if col not in df.columns:
                continue
            mask = df[col].apply(lambda x: pd_notna(x) and str(x) != str(x).strip())
            df.loc[df[col].apply(pd_notna), col] = (
                df.loc[df[col].apply(pd_notna), col].astype(str).str.strip()
            )
            df.loc[df[col].apply(pd_notna), col] = (
                df.loc[df[col].apply(pd_notna), col].astype(str).str.replace(r'\s+', ' ', regex=True)
            )
            affected += int(mask.sum())

        return df, f'Trimmed whitespace in {len(columns)} column(s)', affected

    @staticmethod
    def _encode_categorical(df: pd.DataFrame, params: dict) -> tuple:
        column = params.get('column')
        method = params.get('method', 'label')
        columns = [column] if column else df.select_dtypes(include=['object', 'category']).columns.tolist()
        affected = 0

        for col in columns:
            if col not in df.columns:
                continue
            if method == 'label':
                le = LabelEncoder()
                mask = df[col].notna()
                df.loc[mask, col] = le.fit_transform(df.loc[mask, col].astype(str))
            affected += int(df[col].notna().sum())

        return df, f'Encoded {len(columns)} categorical column(s)', affected

    @staticmethod
    def _scale_numeric(df: pd.DataFrame, params: dict) -> tuple:
        method = params.get('method', 'standard')
        column = params.get('column')
        columns = [column] if column else df.select_dtypes(include=[np.number]).columns.tolist()

        if not columns:
            return df, 'No numeric columns to scale', 0

        # VIVA NOTE: Scaling brings all numeric columns to a common scale without distorting differences.
        # MinMaxScaler scales data between 0 and 1. Useful for Neural Networks or distance-based algorithms.
        if method == 'minmax':
            scaler = MinMaxScaler()
        # StandardScaler scales data so it has mean=0 and variance=1. Useful for models assuming normally distributed data.
        else:
            scaler = StandardScaler()

        # fillna(0) ensures the scaler doesn't fail on missing data
        df[columns] = scaler.fit_transform(df[columns].fillna(0))
        return df, f'Scaled {len(columns)} numeric column(s) using {method}', len(df)

    @staticmethod
    def _detect_outliers(df: pd.DataFrame, params: dict) -> tuple:
        column = params.get('column')
        columns = [column] if column else df.select_dtypes(include=[np.number]).columns.tolist()[:3]
        total_outliers = 0

        for col in columns:
            if col not in df.columns or df[col].dropna().shape[0] < 10:
                continue
            
            # VIVA NOTE: IsolationForest is an unsupervised machine learning algorithm for anomaly detection.
            # It isolates outliers by randomly selecting a feature and a split value. 
            # Outliers need fewer splits to be isolated compared to normal points.
            # contamination=0.05 means we assume about 5% of the data might be outliers.
            clf = IsolationForest(contamination=0.05, random_state=42)
            
            # fit_predict returns -1 for outliers and 1 for inliers
            preds = clf.fit_predict(df[[col]].fillna(df[col].median()).values)
            
            # Create a new boolean column flagging the outliers
            df[f'{col}_outlier'] = preds == -1
            total_outliers += int((preds == -1).sum())

        return df, f'Detected {total_outliers} outlier(s) in {len(columns)} column(s)', total_outliers

    @staticmethod
    def _remove_outliers(df: pd.DataFrame, params: dict) -> tuple:
        column = params.get('column')
        method = params.get('method', 'isolation_forest')
        columns = [column] if column else df.select_dtypes(include=[np.number]).columns.tolist()[:3]
        before = len(df)
        outlier_mask = pd.Series(False, index=df.index)

        for col in columns:
            if col not in df.columns:
                continue
            series = df[col].dropna()
            if len(series) < 10:
                continue

            if method == 'isolation_forest':
                clf = IsolationForest(contamination=0.05, random_state=42)
                preds = clf.fit_predict(df[[col]].fillna(df[col].median()).values)
                outlier_mask |= pd.Series(preds == -1, index=df.index)
            else:
                q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                iqr = q3 - q1
                outlier_mask |= (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)

        result = df[~outlier_mask]
        removed = before - len(result)
        return result, f'Removed {removed} outlier row(s)', removed

    @staticmethod
    def _remove_invalid_emails(df: pd.DataFrame, params: dict) -> tuple:
        column = params['column']
        if column not in df.columns:
            raise CleaningError(f'Column "{column}" not found')

        before = len(df)
        mask = df[column].apply(lambda x: is_valid_email(x) if pd_notna(x) else True)
        result = df[mask]
        removed = before - len(result)
        return result, f'Removed {removed} row(s) with invalid emails in "{column}"', removed

    @staticmethod
    def _remove_invalid_phones(df: pd.DataFrame, params: dict) -> tuple:
        column = params['column']
        if column not in df.columns:
            raise CleaningError(f'Column "{column}" not found')

        before = len(df)
        mask = df[column].apply(lambda x: is_valid_phone(x) if pd_notna(x) else True)
        result = df[mask]
        removed = before - len(result)
        return result, f'Removed {removed} row(s) with invalid phones in "{column}"', removed

    @classmethod
    def operations_from_suggestions(cls, suggestions: list) -> list:
        """Convert AI suggestions to executable operations."""
        return [s['operation'] for s in suggestions if s.get('operation')]
