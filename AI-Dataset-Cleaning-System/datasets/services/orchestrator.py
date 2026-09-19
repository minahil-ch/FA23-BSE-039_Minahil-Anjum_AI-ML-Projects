"""Business logic orchestration for dataset operations."""

import logging
import os
from datetime import datetime

from django.core.files.base import ContentFile
from django.utils import timezone

from core.utils import safe_filename
from datasets.models import CleaningHistory, CleaningJob, Dataset, Report
from datasets.services.analysis_service import AnalysisService
from datasets.services.cleaning_service import CleaningService
from datasets.services.report_service import ReportService
from datasets.services.suggestion_service import SuggestionService
from datasets.services.visualization_service import VisualizationService
from datasets.utils.file_handler import load_dataframe, save_dataframe, validate_uploaded_file

logger = logging.getLogger(__name__)


class DatasetOrchestrator:
    """Coordinate dataset upload, analysis, cleaning, and reporting."""

    @staticmethod
    def create_dataset(user, name, uploaded_file) -> Dataset:
        """Validate, store, and create dataset record."""
        file_type = validate_uploaded_file(uploaded_file)
        if not name:
            name = safe_filename(os.path.splitext(uploaded_file.name)[0])

        dataset = Dataset(
            user=user,
            name=name,
            file_type=file_type,
            file_size=uploaded_file.size,
        )
        dataset.original_file.save(uploaded_file.name, uploaded_file, save=False)
        dataset.save()
        logger.info('Dataset %s uploaded by %s', dataset.id, user.username)
        return dataset

    @staticmethod
    def get_dataframe(dataset: Dataset, use_cleaned: bool = False):
        """Load dataset as DataFrame."""
        if use_cleaned and dataset.cleaned_file:
            path = dataset.cleaned_file.path
            file_type = dataset.file_type
        else:
            path = dataset.original_file.path
            file_type = dataset.file_type
        return load_dataframe(path, file_type)

    @classmethod
    def analyze(cls, dataset: Dataset) -> dict:
        """Run analysis and persist results."""
        df = cls.get_dataframe(dataset)
        analysis = AnalysisService.analyze(df)
        suggestions = SuggestionService.generate_suggestions(df)

        dataset.row_count = analysis['row_count']
        dataset.column_count = analysis['column_count']
        dataset.analysis_result = {**analysis, 'suggestions': suggestions}
        dataset.status = 'analyzed'
        dataset.save(update_fields=['row_count', 'column_count', 'analysis_result', 'status', 'updated_at'])

        return dataset.analysis_result

    @classmethod
    def get_visualizations(cls, dataset: Dataset, use_cleaned: bool = False) -> dict:
        """Generate chart data for dataset."""
        df = cls.get_dataframe(dataset, use_cleaned=use_cleaned)
        return VisualizationService.generate_all(df)

    @classmethod
    def clean(cls, dataset: Dataset, user, operations: list = None, use_suggestions: bool = False) -> CleaningJob:
        """Execute cleaning job on dataset."""
        # 1. Load the dataset into a pandas DataFrame
        df = cls.get_dataframe(dataset)
        
        # 2. Get quick statistics before cleaning to compare later
        before_stats = AnalysisService.quick_stats(df)
        
        # 3. Generate AI suggestions based on the current dataset state
        suggestions = SuggestionService.generate_suggestions(df)

        # 4. Decide which operations to run: user-selected, AI-suggested, or both
        if use_suggestions:
            ops = CleaningService.operations_from_suggestions(suggestions)
            if operations:
                ops.extend(operations)
        else:
            ops = operations or []

        # 5. Create a CleaningJob record in the database with status 'running'
        job = CleaningJob.objects.create(
            user=user,
            dataset=dataset,
            status='running',
            operations=ops,
            suggestions=suggestions,
            before_stats=before_stats,
            progress=0,
        )

        try:
            # 6. Apply all selected operations on the DataFrame sequentially
            cleaned_df, history = CleaningService.apply_operations(df, ops)
            
            # 7. Get quick statistics after cleaning to calculate improvements
            after_stats = AnalysisService.quick_stats(cleaned_df)

            # 8. Save the cleaned DataFrame to a new file
            ext = 'csv' if dataset.file_type == 'csv' else 'xlsx'
            cleaned_name = f'{safe_filename(dataset.name)}_cleaned.{ext}'
            cleaned_path = os.path.join(
                os.path.dirname(dataset.original_file.path),
                cleaned_name,
            )
            save_dataframe(cleaned_df, cleaned_path, dataset.file_type)

            with open(cleaned_path, 'rb') as f:
                dataset.cleaned_file.save(cleaned_name, ContentFile(f.read()), save=False)

            dataset.row_count = after_stats['row_count']
            dataset.column_count = after_stats['column_count']
            dataset.status = 'cleaned'
            dataset.save()

            for entry in history:
                CleaningHistory.objects.create(
                    job=job,
                    operation=entry['operation'],
                    parameters=entry.get('parameters', {}),
                    rows_affected=entry.get('rows_affected', 0),
                    description=entry.get('description', ''),
                )

            job.status = 'completed'
            job.progress = 100
            job.after_stats = after_stats
            job.completed_at = timezone.now()
            job.save()

            logger.info('Cleaning job %s completed for dataset %s', job.id, dataset.id)
            return job

        except Exception as exc:
            job.status = 'failed'
            job.error_message = str(exc)
            job.completed_at = timezone.now()
            job.save()
            dataset.status = 'failed'
            dataset.save(update_fields=['status', 'updated_at'])
            raise

    @classmethod
    def generate_report(cls, dataset: Dataset, user, job: CleaningJob = None) -> Report:
        """Create report with PDF."""
        if job is None:
            job = dataset.cleaning_jobs.filter(status='completed').order_by('-started_at').first()

        before_stats = job.before_stats if job else AnalysisService.quick_stats(cls.get_dataframe(dataset))
        after_stats = job.after_stats if job else before_stats
        history = list(job.history.all()) if job else []

        summary = ReportService.build_summary(job or CleaningJob(dataset=dataset, status='N/A'), before_stats, after_stats, history)
        comparison = ReportService.build_comparison(before_stats, after_stats)

        report = Report.objects.create(
            user=user,
            dataset=dataset,
            job=job,
            title=f'Cleaning Report - {dataset.name}',
            summary=summary,
            comparison=comparison,
        )

        pdf_content = ReportService.generate_pdf(report, dataset, job)
        report.pdf_file.save(pdf_content.name, pdf_content, save=True)
        return report
