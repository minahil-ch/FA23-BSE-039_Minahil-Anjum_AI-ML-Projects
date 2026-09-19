from django.urls import path
from . import views

app_name = "candidates"

urlpatterns = [
    path("", views.CandidateListView.as_view(), name="list"),
    path("add/", views.CandidateCreateView.as_view(), name="add"),
    path("<int:pk>/", views.CandidateDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.CandidateUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.CandidateDeleteView.as_view(), name="delete"),
    path("<int:pk>/status/", views.update_status, name="update_status"),
]
