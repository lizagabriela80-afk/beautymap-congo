"""Notifications Models"""
from django.db import models
import uuid


class Notification(models.Model):
    TYPES = [
        ('booking_new', '📅 Nouvelle réservation'),
        ('booking_confirmed', '✅ Réservation confirmée'),
        ('booking_cancelled', '❌ Réservation annulée'),
        ('booking_reminder', '⏰ Rappel de rendez-vous'),
        ('review_new', '⭐ Nouvel avis'),
        ('message_new', '💬 Nouveau message'),
        ('promo', '🎉 Promotion'),
        ('system', '🔔 Système'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=25, choices=TYPES)
    title = models.CharField(max_length=120)
    message = models.TextField()
    link = models.CharField(max_length=250, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.title}"

    @classmethod
    def send(cls, user, notif_type, title, message, link=''):
        return cls.objects.create(user=user, notif_type=notif_type, title=title, message=message, link=link)
