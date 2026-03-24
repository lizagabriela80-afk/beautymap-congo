from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['get_booking_ref', 'client', 'shop', 'service', 'date', 'start_time', 'status', 'total_price']
    list_filter = ['status', 'date', 'shop__category']
    search_fields = ['client__email', 'shop__name', 'client__first_name']
    ordering = ['-date', '-start_time']
    list_editable = ['status']
    date_hierarchy = 'date'
