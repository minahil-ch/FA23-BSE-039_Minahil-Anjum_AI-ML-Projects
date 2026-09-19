"""REST API URL routes for datasets."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import CleaningJobViewSet, DatasetViewSet, ReportViewSet

router = DefaultRouter()
router.register('datasets', DatasetViewSet, basename='api-dataset')
router.register('jobs', CleaningJobViewSet, basename='api-job')
router.register('reports', ReportViewSet, basename='api-report')

urlpatterns = [
    path('', include(router.urls)),
]
