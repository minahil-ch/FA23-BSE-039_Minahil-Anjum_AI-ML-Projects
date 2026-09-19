"""REST API URL routes for accounts."""

from django.urls import path

from .api_views import LoginAPIView, LogoutAPIView, ProfileAPIView, SignUpAPIView

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='api-signup'),
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('profile/', ProfileAPIView.as_view(), name='api-profile'),
]
