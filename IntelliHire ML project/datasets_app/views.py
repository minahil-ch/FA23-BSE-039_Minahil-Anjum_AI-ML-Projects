import os
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from .models import Dataset
from .forms import DatasetUploadForm
from . import services


@login_required
def dataset_list(request):
    datasets = Dataset.objects.all()
    return render(request, "datasets/dataset_list.html", {"datasets": datasets})


@login_required
def dataset_upload(request):
    if request.method == "POST":
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.uploaded_by = request.user
            dataset.save()

            # Run validation immediately after upload
            df = services.load_dataset(dataset.file.path)
            report = services.validate_dataset(df)
            dataset.rows_count = report["rows"]
            dataset.columns_count = report["columns"]
            dataset.missing_values_count = report["missing_values"]
            dataset.duplicate_rows_count = report["duplicate_rows"]
            dataset.validation_report = report
            dataset.status = Dataset.Status.VALIDATED if report["is_valid"] else Dataset.Status.INVALID
            dataset.save()

            messages.success(request, "Dataset uploaded and validated.")
            return redirect("datasets:preview", pk=dataset.pk)
    else:
        form = DatasetUploadForm()
    return render(request, "datasets/dataset_upload.html", {"form": form})


@login_required
def dataset_preview(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    df = services.load_dataset(dataset.file.path)
    preview_rows = df.head(15).to_html(classes="table table-striped table-sm", index=False, border=0)
    return render(request, "datasets/dataset_preview.html", {
        "dataset": dataset,
        "preview_table": preview_rows,
        "report": dataset.validation_report,
    })


@login_required
def dataset_clean(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    df = services.load_dataset(dataset.file.path)
    cleaned_df = services.clean_dataset(df)

    clean_dir = os.path.join(settings.MEDIA_ROOT, "datasets", "cleaned")
    os.makedirs(clean_dir, exist_ok=True)
    clean_filename = f"cleaned_{dataset.pk}_{dataset.name.replace(' ', '_')}.csv"
    clean_path = os.path.join(clean_dir, clean_filename)
    cleaned_df.to_csv(clean_path, index=False)

    dataset.cleaned_file.name = f"datasets/cleaned/{clean_filename}"
    dataset.status = Dataset.Status.CLEANED
    dataset.save()

    messages.success(request, f"Dataset cleaned: {len(df) - len(cleaned_df)} rows removed.")
    return redirect("datasets:preview", pk=pk)


@login_required
def dataset_download_clean(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    if not dataset.cleaned_file:
        raise Http404("Cleaned dataset not available. Please clean the dataset first.")
    return FileResponse(open(dataset.cleaned_file.path, "rb"), as_attachment=True,
                         filename=os.path.basename(dataset.cleaned_file.name))


@login_required
def dataset_delete(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    dataset.delete()
    messages.success(request, "Dataset deleted.")
    return redirect("datasets:list")
