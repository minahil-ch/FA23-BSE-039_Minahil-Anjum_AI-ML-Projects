from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from datasets_app.models import Dataset
from datasets_app import services as dataset_services
from .models import TrainedModel, Prediction
from .forms import PredictionForm
from . import train as train_module
from . import predict as predict_module


@login_required
def training_page(request):
    datasets = Dataset.objects.exclude(status=Dataset.Status.INVALID)
    trainings = TrainedModel.objects.select_related("dataset").all()[:30]
    return render(request, "ml_engine/training.html", {
        "datasets": datasets,
        "trainings": trainings,
    })


@login_required
def train_models(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    file_path = dataset.cleaned_file.path if dataset.cleaned_file else dataset.file.path
    df = dataset_services.load_dataset(file_path)

    try:
        results = train_module.train_all_models(df, dataset.pk, request.user)
        messages.success(request, f"Training complete. {len(results)} models trained and compared.")
    except Exception as exc:
        messages.error(request, f"Training failed: {exc}")

    return redirect("ml_engine:comparison")


@login_required
def model_comparison(request):
    latest_dataset = TrainedModel.objects.order_by("-trained_at").first()
    trainings = []
    if latest_dataset:
        trainings = TrainedModel.objects.filter(dataset=latest_dataset.dataset).order_by("-f1_score")
    return render(request, "ml_engine/comparison.html", {"trainings": trainings})


@login_required
def prediction_form_view(request):
    result = None
    if request.method == "POST":
        form = PredictionForm(request.POST)
        if form.is_valid():
            feature_dict = form.to_feature_dict()
            try:
                result = predict_module.predict_candidate(feature_dict)
                Prediction.objects.create(
                    model_used=result["model_record"],
                    input_data={**feature_dict,
                                "first_name": form.cleaned_data["first_name"],
                                "last_name": form.cleaned_data["last_name"]},
                    result=result["result"],
                    probability=result["probability"],
                    explanation=result["explanation"],
                    predicted_by=request.user,
                )
                messages.success(request, "Prediction generated successfully.")
            except predict_module.ModelNotFoundError as exc:
                messages.error(request, str(exc))
    else:
        form = PredictionForm()
    return render(request, "ml_engine/predict.html", {"form": form, "result": result})


@login_required
def prediction_history(request):
    predictions = Prediction.objects.select_related("model_used", "predicted_by").all()
    return render(request, "ml_engine/prediction_history.html", {"predictions": predictions})


@login_required
def prediction_detail(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)
    return render(request, "ml_engine/prediction_detail.html", {"prediction": prediction})


@login_required
def prediction_delete(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)
    prediction.delete()
    messages.success(request, "Prediction record deleted.")
    return redirect("ml_engine:prediction_history")
