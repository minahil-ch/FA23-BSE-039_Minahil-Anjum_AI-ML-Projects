"""Web views for authentication and dashboard."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from datasets.models import CleaningJob, Dataset, Report

from .forms import ProfileUpdateForm, SignUpForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created successfully! Welcome aboard.')
        return response


@login_required
def dashboard(request):
    """User dashboard with statistics and recent activity."""
    user = request.user
    datasets = Dataset.objects.filter(user=user).order_by('-uploaded_at')[:5]
    recent_jobs = CleaningJob.objects.filter(user=user).select_related('dataset')[:5]
    reports = Report.objects.filter(user=user).select_related('dataset')[:5]

    stats = {
        'total_datasets': Dataset.objects.filter(user=user).count(),
        'total_jobs': CleaningJob.objects.filter(user=user).count(),
        'completed_jobs': CleaningJob.objects.filter(user=user, status='completed').count(),
        'total_reports': Report.objects.filter(user=user).count(),
    }

    return render(request, 'accounts/dashboard.html', {
        'stats': stats,
        'datasets': datasets,
        'recent_jobs': recent_jobs,
        'reports': reports,
    })


@login_required
def profile(request):
    """User profile view and update."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
