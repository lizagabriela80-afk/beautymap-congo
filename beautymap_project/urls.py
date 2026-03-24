"""BeautyMap Congo — URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Web views
    path('', include('apps.shops.urls')),
    path('auth/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.accounts.dashboard_urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('messages/', include('apps.messaging.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('payments/', include('apps.payments.urls')),
    # REST API
    path('api/v1/', include([
        path('auth/', include('apps.accounts.api_urls')),
        path('shops/', include('apps.shops.api_urls')),
        path('bookings/', include('apps.bookings.api_urls')),
        path('reviews/', include('apps.reviews.api_urls')),
        path('messages/', include('apps.messaging.api_urls')),
        path('notifications/', include('apps.notifications.api_urls')),
        path('payments/', include('apps.payments.api_urls')),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
