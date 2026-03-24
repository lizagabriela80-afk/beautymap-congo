"""Payments Models — BeautyMap Congo"""
from django.db import models
import uuid


class Payment(models.Model):
    STATUS = [
        ('pending', 'En attente'),
        ('success', 'Réussi'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    METHOD = [
        ('mobile_money', 'Mobile Money'),
        ('cash', 'Espèces'),
        ('card', 'Carte bancaire'),
        ('free', 'Gratuit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    method = models.CharField(max_length=20, choices=METHOD, default='cash')
    status = models.CharField(max_length=15, choices=STATUS, default='pending')
    reference = models.CharField(max_length=100, blank=True)
    provider_ref = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Paiement {self.amount} FCFA — {self.booking}"


class Subscription(models.Model):
    PLANS = [('free','Gratuit'),('premium','Premium'),('enterprise','Enterprise')]
    STATUS = [('active','Actif'),('expired','Expiré'),('cancelled','Annulé')]

    pro = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLANS)
    status = models.CharField(max_length=15, choices=STATUS, default='active')
    price = models.DecimalField(max_digits=10, decimal_places=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    payment_ref = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pro.get_full_name()} — Plan {self.plan}"
