"""
URL configuration for AI Dataset Cleaning System.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('datasets/', include('datasets.urls')),
    path('api/v1/', include('datasets.api_urls')),
    path('api/v1/auth/', include('accounts.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'AI Dataset Cleaning System'
admin.site.site_title = 'Dataset Cleaning Admin'
admin.site.index_title = 'Administration Dashboard'
