"""Bookings Models — BeautyMap Congo"""
from django.db import models
from django.utils import timezone
import uuid


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', '⏳ En attente'),
        ('confirmed', '✅ Confirmé'),
        ('cancelled', '❌ Annulé'),
        ('completed', '✔️ Terminé'),
        ('no_show', '🚫 Absent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bookings')
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey('shops.Service', on_delete=models.SET_NULL, null=True, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    promo_code = models.CharField(max_length=20, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"RDV {self.client.get_full_name()} @ {self.shop.name} — {self.date} {self.start_time}"

    def save(self, *args, **kwargs):
        if self.service and not self.end_time:
            from datetime import datetime, timedelta
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = start_dt + timedelta(minutes=self.service.duration_minutes)
            self.end_time = end_dt.time()
        if self.service and not self.total_price:
            self.total_price = self.service.price - self.discount_amount
        super().save(*args, **kwargs)

    def get_booking_ref(self):
        return f"BMC-{str(self.id)[:8].upper()}"

    def can_cancel(self):
        from datetime import datetime
        booking_dt = datetime.combine(self.date, self.start_time)
        now = timezone.localtime().replace(tzinfo=None)
        return self.status in ('pending', 'confirmed') and booking_dt > now

    def is_upcoming(self):
        from datetime import datetime
        booking_dt = datetime.combine(self.date, self.start_time)
        return booking_dt > timezone.localtime().replace(tzinfo=None)


class TimeSlot(models.Model):
    """Available time slots for a shop/service"""
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='time_slots')
    service = models.ForeignKey('shops.Service', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ['shop', 'date', 'start_time']
        ordering = ['date', 'start_time']
