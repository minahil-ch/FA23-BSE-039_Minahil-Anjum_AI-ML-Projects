"""Web views for dataset management."""

import json
import logging
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.exceptions import DatasetError
from datasets.forms import CleaningOperationsForm, DatasetUploadForm
from datasets.models import CleaningJob, Dataset, Report
from datasets.services.orchestrator import DatasetOrchestrator

logger = logging.getLogger(__name__)


@login_required
def dataset_list(request):
    """List all user datasets with pagination."""
    datasets = Dataset.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'datasets/list.html', {'datasets': datasets})


@login_required
def dataset_upload(request):
    """Upload a new dataset."""
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                dataset = DatasetOrchestrator.create_dataset(
                    user=request.user,
                    name=form.cleaned_data['name'],
                    uploaded_file=form.cleaned_data['original_file'],
                )
                messages.success(request, f'Dataset "{dataset.name}" uploaded successfully.')
                return redirect('datasets:detail', pk=dataset.pk)
            except DatasetError as exc:
                messages.error(request, exc.message)
    else:
        form = DatasetUploadForm()

    return render(request, 'datasets/upload.html', {'form': form})


@login_required
def dataset_detail(request, pk):
    """Dataset detail with analysis overview."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)

    if dataset.status == 'uploaded':
        try:
            DatasetOrchestrator.analyze(dataset)
            dataset.refresh_from_db()
            messages.info(request, 'Dataset analyzed automatically.')
        except DatasetError as exc:
            messages.warning(request, f'Analysis pending: {exc.message}')

    analysis = dataset.analysis_result or {}
    suggestions = analysis.get('suggestions', [])
    jobs = dataset.cleaning_jobs.order_by('-started_at')[:5]

    return render(request, 'datasets/detail.html', {
        'dataset': dataset,
        'analysis': analysis,
        'suggestions': suggestions,
        'jobs': jobs,
    })


@login_required
def dataset_analyze(request, pk):
    """Re-run dataset analysis."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)

    try:
        analysis = DatasetOrchestrator.analyze(dataset)
        messages.success(request, 'Analysis completed successfully.')
    except DatasetError as exc:
        messages.error(request, exc.message)
        return redirect('datasets:detail', pk=pk)

    return render(request, 'datasets/analyze.html', {
        'dataset': dataset,
        'analysis': analysis,
        'suggestions': analysis.get('suggestions', []),
    })


@login_required
def dataset_visualize(request, pk):
    """Display dataset visualizations."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
    use_cleaned = request.GET.get('cleaned') == '1' and bool(dataset.cleaned_file)

    try:
        charts = DatasetOrchestrator.get_visualizations(dataset, use_cleaned=use_cleaned)
    except DatasetError as exc:
        messages.error(request, exc.message)
        return redirect('datasets:detail', pk=pk)

    return render(request, 'datasets/visualize.html', {
        'dataset': dataset,
        'charts_json': json.dumps(charts),
        'use_cleaned': use_cleaned,
    })


@login_required
def dataset_clean(request, pk):
    """Configure and run cleaning operations."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
    analysis = dataset.analysis_result or {}
    suggestions = analysis.get('suggestions', [])

    if request.method == 'POST':
        form = CleaningOperationsForm(request.POST)
        if form.is_valid():
            operations = form.get_operations_list()
            use_suggestions = form.cleaned_data.get('use_ai_suggestions', False)

            try:
                job = DatasetOrchestrator.clean(
                    dataset=dataset,
                    user=request.user,
                    operations=operations,
                    use_suggestions=use_suggestions,
                )
                messages.success(request, f'Cleaning completed! {len(job.history.all())} operation(s) applied.')
                return redirect('datasets:report', pk=dataset.pk)
            except DatasetError as exc:
                messages.error(request, exc.message)
    else:
        form = CleaningOperationsForm()

    return render(request, 'datasets/clean.html', {
        'dataset': dataset,
        'form': form,
        'suggestions': suggestions,
    })


@login_required
def dataset_report(request, pk):
    """View cleaning report and download options."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
    job = dataset.cleaning_jobs.filter(status='completed').order_by('-started_at').first()
    report = dataset.reports.order_by('-created_at').first()

    if not report and job:
        try:
            report = DatasetOrchestrator.generate_report(dataset, request.user, job)
            messages.success(request, 'Report generated successfully.')
        except DatasetError as exc:
            messages.error(request, exc.message)

    return render(request, 'datasets/report.html', {
        'dataset': dataset,
        'job': job,
        'report': report,
    })


@login_required
@require_POST
def generate_report(request, pk):
    """Generate or regenerate report."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
    job = dataset.cleaning_jobs.filter(status='completed').order_by('-started_at').first()

    try:
        DatasetOrchestrator.generate_report(dataset, request.user, job)
        messages.success(request, 'Report generated successfully.')
    except DatasetError as exc:
        messages.error(request, exc.message)

    return redirect('datasets:report', pk=pk)


@login_required
def download_dataset(request, pk, file_type):
    """Download original or cleaned dataset."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
    variant = request.GET.get('variant', 'cleaned')

    if variant == 'cleaned' and dataset.cleaned_file:
        file_field = dataset.cleaned_file
    else:
        file_field = dataset.original_file

    if not file_field:
        raise Http404('File not found.')

    ext = file_type.lower()
    if ext == 'csv':
        content_type = 'text/csv'
    elif ext in ('xlsx', 'excel'):
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ext = 'xlsx'
    else:
        raise Http404('Invalid file type.')

    filename = f'{dataset.name}_{variant}.{ext}'
    return FileResponse(file_field.open('rb'), as_attachment=True, filename=filename, content_type=content_type)


@login_required
def download_report_pdf(request, pk):
    """Download report PDF."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
    report = dataset.reports.order_by('-created_at').first()

    if not report or not report.pdf_file:
        messages.error(request, 'No report available. Generate a report first.')
        return redirect('datasets:report', pk=pk)

    return FileResponse(
        report.pdf_file.open('rb'),
        as_attachment=True,
        filename=f'report_{dataset.name}.pdf',
        content_type='application/pdf',
    )


@login_required
@require_POST
def delete_dataset(request, pk):
    """Delete a dataset."""
    dataset = get_object_or_404(Dataset, pk=pk, user=request.user)
    name = dataset.name
    dataset.delete()
    messages.success(request, f'Dataset "{name}" deleted.')
    return redirect('datasets:list')
