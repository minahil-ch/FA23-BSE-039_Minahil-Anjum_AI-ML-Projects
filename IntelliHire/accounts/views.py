from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import User


class UserLoginView(LoginView):
    """Handles HR/Admin/Recruiter login."""
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class RegisterView(CreateView):
    """Self-service registration for new HR staff."""
    model = User
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully. Please log in.")
        return response


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"profile_user": request.user})


@login_required
def profile_edit_view(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})


class UserListView(ListView):
    """Admin-only view listing all system users."""
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 15

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Only Admins can view the user list.")
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)


@login_required
def toggle_user_status(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect("dashboard:home")
    user = User.objects.get(pk=pk)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"User {user.username} status updated.")
    return redirect("accounts:user_list")
