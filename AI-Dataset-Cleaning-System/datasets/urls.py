"""URL routes for datasets web views."""

from django.urls import path

from . import views

app_name = 'datasets'

urlpatterns = [
    path('', views.dataset_list, name='list'),
    path('upload/', views.dataset_upload, name='upload'),
    path('<uuid:pk>/', views.dataset_detail, name='detail'),
    path('<uuid:pk>/analyze/', views.dataset_analyze, name='analyze'),
    path('<uuid:pk>/visualize/', views.dataset_visualize, name='visualize'),
    path('<uuid:pk>/clean/', views.dataset_clean, name='clean'),
    path('<uuid:pk>/report/', views.dataset_report, name='report'),
    path('<uuid:pk>/report/generate/', views.generate_report, name='generate_report'),
    path('<uuid:pk>/download/<str:file_type>/', views.download_dataset, name='download'),
    path('<uuid:pk>/report/pdf/', views.download_report_pdf, name='download_report_pdf'),
    path('<uuid:pk>/delete/', views.delete_dataset, name='delete'),
]
