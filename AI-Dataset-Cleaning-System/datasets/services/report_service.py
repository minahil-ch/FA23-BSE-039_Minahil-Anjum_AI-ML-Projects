"""Report generation service with PDF export."""

import io
import logging
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.exceptions import DatasetError

logger = logging.getLogger(__name__)


class ReportService:
    """Generate cleaning reports and PDF exports."""

    @staticmethod
    def build_summary(job, before_stats: dict, after_stats: dict, history: list) -> dict:
        """Build cleaning summary JSON."""
        operations_applied = []
        for h in history:
            if isinstance(h, dict):
                operations_applied.append({
                    'operation': h.get('operation', ''),
                    'rows_affected': h.get('rows_affected', 0),
                    'description': h.get('description', ''),
                })
            else:
                operations_applied.append({
                    'operation': h.operation,
                    'rows_affected': h.rows_affected,
                    'description': h.description,
                })

        return {
            'dataset_name': job.dataset.name,
            'job_id': str(job.id),
            'status': job.status,
            'operations_count': len(operations_applied),
            'operations': operations_applied,
            'generated_at': datetime.utcnow().isoformat(),
        }

    @staticmethod
    def build_comparison(before_stats: dict, after_stats: dict) -> dict:
        """Build before/after comparison metrics."""
        metrics = ['row_count', 'column_count', 'missing_values', 'duplicate_rows', 'memory_usage_mb']
        comparison = {}

        for metric in metrics:
            before_val = before_stats.get(metric, 0)
            after_val = after_stats.get(metric, 0)
            diff = after_val - before_val if isinstance(before_val, (int, float)) else None
            comparison[metric] = {
                'before': before_val,
                'after': after_val,
                'change': diff,
                'improved': (
                    (metric in ('missing_values', 'duplicate_rows', 'memory_usage_mb') and diff is not None and diff < 0)
                    or (metric == 'row_count' and diff is not None)
                ),
            }

        return comparison

    @classmethod
    def generate_pdf(cls, report, dataset, job=None) -> ContentFile:
        """Generate PDF report and return as ContentFile."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.HexColor('#0d6efd'),
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=16,
            spaceAfter=8,
        )

        elements = [
            Paragraph('AI Dataset Cleaning Report', title_style),
            Paragraph(f'Dataset: <b>{dataset.name}</b>', styles['Normal']),
            Paragraph(f'Generated: {report.created_at.strftime("%Y-%m-%d %H:%M UTC")}', styles['Normal']),
            Paragraph(f'User: {report.user.username}', styles['Normal']),
            Spacer(1, 0.25 * inch),
        ]

        # Summary section
        elements.append(Paragraph('Cleaning Summary', heading_style))
        summary = report.summary or {}
        summary_data = [
            ['Metric', 'Value'],
            ['Operations Applied', str(summary.get('operations_count', 0))],
            ['Job Status', summary.get('status', 'N/A')],
        ]
        elements.append(cls._make_table(summary_data))
        Spacer(1, 0.15 * inch)

        # Operations table
        operations = summary.get('operations', [])
        if operations:
            elements.append(Paragraph('Operations Detail', heading_style))
            op_data = [['Operation', 'Rows Affected', 'Description']]
            for op in operations:
                op_data.append([
                    op.get('operation', ''),
                    str(op.get('rows_affected', 0)),
                    op.get('description', '')[:60],
                ])
            elements.append(cls._make_table(op_data, col_widths=[1.5 * inch, 1.2 * inch, 3.5 * inch]))

        # Before vs After
        comparison = report.comparison or {}
        if comparison:
            elements.append(Spacer(1, 0.15 * inch))
            elements.append(Paragraph('Before vs After Comparison', heading_style))
            comp_data = [['Metric', 'Before', 'After', 'Change']]
            for metric, data in comparison.items():
                comp_data.append([
                    metric.replace('_', ' ').title(),
                    str(data.get('before', '')),
                    str(data.get('after', '')),
                    str(data.get('change', '')),
                ])
            elements.append(cls._make_table(comp_data))

        try:
            doc.build(elements)
        except Exception as exc:
            logger.error('PDF generation failed: %s', exc)
            raise DatasetError(f'PDF generation failed: {exc}') from exc

        buffer.seek(0)
        filename = f'report_{report.id}.pdf'
        return ContentFile(buffer.read(), name=filename)

    @staticmethod
    def _make_table(data, col_widths=None):
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        return table
