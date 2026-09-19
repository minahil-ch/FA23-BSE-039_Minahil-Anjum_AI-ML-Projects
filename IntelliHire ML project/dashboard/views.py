import json
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from candidates.models import Candidate
from datasets_app.models import Dataset
from ml_engine.models import TrainedModel, Prediction


@login_required
def home(request):
    candidates = Candidate.objects.all()
    total_candidates = candidates.count()
    selected = candidates.filter(status=Candidate.Status.SELECTED).count()
    rejected = candidates.filter(status=Candidate.Status.REJECTED).count()
    hired = candidates.filter(status=Candidate.Status.HIRED).count()

    hiring_ratio = round((selected / total_candidates) * 100, 1) if total_candidates else 0
    avg_experience = candidates.aggregate(avg=Avg("experience_years"))["avg"] or 0
    avg_cgpa = candidates.aggregate(avg=Avg("cgpa"))["avg"] or 0

    best_model = TrainedModel.objects.filter(is_best_model=True).order_by("-trained_at").first()
    total_predictions = Prediction.objects.count()
    avg_confidence = Prediction.objects.aggregate(avg=Avg("probability"))["avg"] or 0

    # Monthly hiring trend (last 12 entries by month)
    monthly = (
        candidates.annotate(month=TruncMonth("application_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    monthly_labels = [m["month"].strftime("%b %Y") if m["month"] else "N/A" for m in monthly]
    monthly_counts = [m["count"] for m in monthly]

    # Status distribution for pie chart
    status_counts = candidates.values("status").annotate(count=Count("id"))
    status_labels = [dict(Candidate.Status.choices).get(s["status"], s["status"]) for s in status_counts]
    status_values = [s["count"] for s in status_counts]

    # Department distribution
    dept_counts = (
        candidates.exclude(preferred_department="")
        .values("preferred_department").annotate(count=Count("id")).order_by("-count")[:8]
    )

    # Model accuracy comparison (latest training batch)
    model_labels, model_scores = [], []
    if best_model:
        latest_batch = TrainedModel.objects.filter(dataset=best_model.dataset).order_by("-f1_score")
        model_labels = [m.algorithm_name for m in latest_batch]
        model_scores = [round(m.accuracy * 100, 2) for m in latest_batch]

    context = {
        "total_candidates": total_candidates,
        "selected": selected,
        "rejected": rejected,
        "hired": hired,
        "hiring_ratio": hiring_ratio,
        "avg_experience": round(avg_experience, 1),
        "avg_cgpa": round(avg_cgpa, 2) if avg_cgpa else 0,
        "total_datasets": Dataset.objects.count(),
        "best_model": best_model,
        "total_predictions": total_predictions,
        "avg_confidence": round(avg_confidence * 100, 1),
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_counts": json.dumps(monthly_counts),
        "status_labels": json.dumps(status_labels),
        "status_values": json.dumps(status_values),
        "dept_labels": json.dumps([d["preferred_department"] for d in dept_counts]),
        "dept_values": json.dumps([d["count"] for d in dept_counts]),
        "model_labels": json.dumps(model_labels),
        "model_scores": json.dumps(model_scores),
        "recent_candidates": candidates[:5],
        "recent_predictions": Prediction.objects.select_related("candidate")[:5],
    }
    return render(request, "dashboard/home.html", context)
