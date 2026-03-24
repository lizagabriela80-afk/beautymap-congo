# apps/accounts/api_urls.py
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .serializers import RegisterView, MeView, LogoutView

urlpatterns = [
    path('login/', obtain_auth_token, name='api_login'),
    path('register/', RegisterView.as_view(), name='api_register'),
    path('me/', MeView.as_view(), name='api_me'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
]
