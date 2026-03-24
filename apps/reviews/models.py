"""Reviews Models — BeautyMap Congo"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    client = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews_given')
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=120, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    owner_reply = models.TextField(blank=True)
    owner_reply_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']
        unique_together = ['client', 'shop']

    def __str__(self):
        return f"{self.client.get_full_name()} → {self.shop.name} ({self.rating}★)"

    def stars_display(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
