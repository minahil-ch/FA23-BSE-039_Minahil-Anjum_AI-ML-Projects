"""Chart and visualization generation service."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class VisualizationService:
    """Generate Chart.js-compatible chart data from DataFrames."""

    @staticmethod
    def generate_all(df: pd.DataFrame) -> dict:
        """Generate all visualization datasets."""
        return {
            'missing_values': VisualizationService.missing_values_chart(df),
            'correlation_heatmap': VisualizationService.correlation_heatmap(df),
            'histograms': VisualizationService.histograms(df),
            'box_plots': VisualizationService.box_plots(df),
            'bar_charts': VisualizationService.bar_charts(df),
            'pie_charts': VisualizationService.pie_charts(df),
        }

    @staticmethod
    def missing_values_chart(df: pd.DataFrame) -> dict:
        """Bar chart of missing values per column."""
        missing = df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False).head(15)

        if missing.empty:
            return {
                'type': 'bar',
                'title': 'Missing Values by Column',
                'labels': ['No missing values'],
                'datasets': [{'label': 'Missing Count', 'data': [0], 'backgroundColor': '#28a745'}],
            }

        colors = ['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#0d6efd']
        return {
            'type': 'bar',
            'title': 'Missing Values by Column',
            'labels': missing.index.tolist(),
            'datasets': [{
                'label': 'Missing Count',
                'data': [int(v) for v in missing.values],
                'backgroundColor': [colors[i % len(colors)] for i in range(len(missing))],
            }],
        }

    @staticmethod
    def correlation_heatmap(df: pd.DataFrame) -> dict:
        """Correlation matrix for numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return {
                'type': 'heatmap',
                'title': 'Correlation Heatmap',
                'labels': [],
                'matrix': [],
                'message': 'Need at least 2 numeric columns for correlation.',
            }

        cols = numeric_df.columns.tolist()[:10]
        corr = numeric_df[cols].corr().fillna(0).round(3)

        return {
            'type': 'heatmap',
            'title': 'Correlation Heatmap',
            'labels': cols,
            'matrix': corr.values.tolist(),
        }

    @staticmethod
    def histograms(df: pd.DataFrame, max_cols: int = 4) -> list:
        """Histogram data for numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:max_cols]
        charts = []

        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue

            counts, bin_edges = np.histogram(series, bins=min(20, max(5, len(series) // 10)))
            labels = [f'{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}' for i in range(len(counts))]

            charts.append({
                'type': 'bar',
                'title': f'Histogram: {col}',
                'column': col,
                'labels': labels,
                'datasets': [{
                    'label': col,
                    'data': counts.tolist(),
                    'backgroundColor': 'rgba(13, 110, 253, 0.6)',
                    'borderColor': '#0d6efd',
                    'borderWidth': 1,
                }],
            })

        return charts

    @staticmethod
    def box_plots(df: pd.DataFrame, max_cols: int = 4) -> list:
        """Box plot statistics for numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:max_cols]
        charts = []

        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue

            q1, median, q3 = series.quantile([0.25, 0.5, 0.75])
            iqr = q3 - q1
            lower = max(series.min(), q1 - 1.5 * iqr)
            upper = min(series.max(), q3 + 1.5 * iqr)

            charts.append({
                'type': 'boxplot',
                'title': f'Box Plot: {col}',
                'column': col,
                'stats': {
                    'min': float(series.min()),
                    'q1': float(q1),
                    'median': float(median),
                    'q3': float(q3),
                    'max': float(series.max()),
                    'lower_whisker': float(lower),
                    'upper_whisker': float(upper),
                    'outliers': int(((series < lower) | (series > upper)).sum()),
                },
            })

        return charts

    @staticmethod
    def bar_charts(df: pd.DataFrame, max_cols: int = 3) -> list:
        """Bar charts for top categorical value counts."""
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()[:max_cols]
        charts = []

        for col in cat_cols:
            counts = df[col].value_counts().head(10)
            if counts.empty:
                continue

            charts.append({
                'type': 'bar',
                'title': f'Top Values: {col}',
                'column': col,
                'labels': [str(k) for k in counts.index],
                'datasets': [{
                    'label': 'Count',
                    'data': [int(v) for v in counts.values],
                    'backgroundColor': 'rgba(32, 201, 151, 0.7)',
                }],
            })

        return charts

    @staticmethod
    def pie_charts(df: pd.DataFrame, max_cols: int = 3) -> list:
        """Pie charts for categorical distributions."""
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()[:max_cols]
        charts = []
        palette = ['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545',
                   '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0']

        for col in cat_cols:
            counts = df[col].value_counts().head(8)
            if counts.empty:
                continue

            charts.append({
                'type': 'pie',
                'title': f'Distribution: {col}',
                'column': col,
                'labels': [str(k) for k in counts.index],
                'datasets': [{
                    'data': [int(v) for v in counts.values],
                    'backgroundColor': palette[:len(counts)],
                }],
            })

        return charts
