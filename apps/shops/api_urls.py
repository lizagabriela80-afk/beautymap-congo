# apps/shops/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ShopViewSet, ServiceViewSet

router = DefaultRouter()
router.register(r'', ShopViewSet, basename='shop')
router.register(r'services', ServiceViewSet, basename='service')

urlpatterns = [path('', include(router.urls))]
