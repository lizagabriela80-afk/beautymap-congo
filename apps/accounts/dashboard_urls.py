# apps/accounts/dashboard_urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pro/', views.pro_dashboard, name='pro_dashboard'),
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]
