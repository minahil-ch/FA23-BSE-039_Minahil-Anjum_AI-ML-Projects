from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Candidate
from .forms import CandidateForm


class CandidateListView(LoginRequiredMixin, ListView):
    """List candidates with search + filter + pagination."""
    model = Candidate
    template_name = "candidates/candidate_list.html"
    context_object_name = "candidates"
    paginate_by = 10

    def get_queryset(self):
        qs = Candidate.objects.all()
        query = self.request.GET.get("q")
        status = self.request.GET.get("status")
        department = self.request.GET.get("department")

        if query:
            qs = qs.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query) |
                Q(email__icontains=query) | Q(phone_number__icontains=query) |
                Q(technical_skills__icontains=query) | Q(candidate_id__icontains=query)
            )
        if status:
            qs = qs.filter(status=status)
        if department:
            qs = qs.filter(preferred_department__icontains=department)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Candidate.Status.choices
        ctx["query"] = self.request.GET.get("q", "")
        ctx["selected_status"] = self.request.GET.get("status", "")
        return ctx


class CandidateDetailView(LoginRequiredMixin, DetailView):
    model = Candidate
    template_name = "candidates/candidate_detail.html"
    context_object_name = "candidate"


class CandidateCreateView(LoginRequiredMixin, CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = "candidates/candidate_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Candidate added successfully.")
        return super().form_valid(form)


class CandidateUpdateView(LoginRequiredMixin, UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = "candidates/candidate_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Candidate updated successfully.")
        return super().form_valid(form)


class CandidateDeleteView(LoginRequiredMixin, DeleteView):
    model = Candidate
    template_name = "candidates/candidate_confirm_delete.html"
    success_url = reverse_lazy("candidates:list")

    def form_valid(self, form):
        messages.success(self.request, "Candidate deleted.")
        return super().form_valid(form)


@login_required
def update_status(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in Candidate.Status.values:
            candidate.status = new_status
            candidate.save()
            messages.success(request, f"Status updated to {candidate.get_status_display()}.")
    return redirect("candidates:detail", pk=pk)
