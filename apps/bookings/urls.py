# apps/bookings/urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('reserver/<slug:shop_slug>/', views.book_service, name='book_service'),
    path('reserver/<slug:shop_slug>/<int:service_id>/', views.book_service, name='book_service_with_service'),
    path('confirmation/<uuid:pk>/', views.booking_confirm, name='booking_confirm'),
    path('creneaux/', views.get_available_slots, name='available_slots'),
    path('<uuid:pk>/annuler/', views.cancel_booking, name='cancel_booking'),
    path('<uuid:pk>/confirmer/', views.confirm_booking, name='confirm_booking'),
]
