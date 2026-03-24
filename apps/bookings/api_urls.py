# apps/bookings/api_urls.py
from django.urls import path
from rest_framework import serializers, viewsets, permissions
from rest_framework.routers import DefaultRouter
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    booking_ref = serializers.CharField(source='get_booking_ref', read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'shop', 'shop_name', 'service', 'service_name', 'booking_ref',
                  'date', 'start_time', 'end_time', 'status', 'notes', 'total_price', 'created_at']
        read_only_fields = ['id', 'end_time', 'created_at']

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        u = self.request.user
        if u.is_pro:
            return Booking.objects.filter(shop__owner=u).order_by('-date', '-start_time')
        return Booking.objects.filter(client=u).order_by('-date', '-start_time')
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

router = DefaultRouter()
router.register(r'', BookingViewSet, basename='booking')
urlpatterns = router.urls
