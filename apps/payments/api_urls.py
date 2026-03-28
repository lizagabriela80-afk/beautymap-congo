# ═══════════════════════════════════════════════════════════════
#  apps/payments/api_urls.py  — API Paiements (mobile)
# ═══════════════════════════════════════════════════════════════
from django.urls import path, include
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from django.utils import timezone
from .models import Payment, Subscription


class PaymentSerializer(serializers.ModelSerializer):
    booking_ref  = serializers.SerializerMethodField()
    shop_name    = serializers.CharField(source='booking.shop.name', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    method_label = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model  = Payment
        fields = ['id', 'booking', 'booking_ref', 'shop_name',
                  'amount', 'method', 'method_label', 'status', 'status_label',
                  'reference', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'reference', 'provider_ref', 'created_at', 'updated_at']

    def get_booking_ref(self, obj):
        return obj.booking.get_booking_ref()


class PaymentInitSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()
    method     = serializers.ChoiceField(choices=['mobile_money', 'cash', 'card'])
    phone      = serializers.CharField(required=False, allow_blank=True,
                                       help_text="Requis pour Mobile Money")

    def validate(self, data):
        from apps.bookings.models import Booking
        from django.shortcuts import get_object_or_404
        try:
            booking = Booking.objects.get(pk=data['booking_id'], client=self.context['request'].user)
        except Booking.DoesNotExist:
            raise serializers.ValidationError({'booking_id': 'Réservation introuvable.'})
        if Payment.objects.filter(booking=booking, status='success').exists():
            raise serializers.ValidationError('Cette réservation est déjà payée.')
        data['booking'] = booking
        if data['method'] == 'mobile_money' and not data.get('phone'):
            raise serializers.ValidationError({'phone': 'Le numéro de téléphone est requis pour Mobile Money.'})
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_label   = serializers.CharField(source='get_plan_display',   read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = Subscription
        fields = ['id', 'plan', 'plan_label', 'status', 'status_label',
                  'price', 'start_date', 'end_date', 'created_at']
        read_only_fields = fields


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /api/v1/payments/               → Historique des paiements
    POST /api/v1/payments/initiate/      → Initier un paiement
    POST /api/v1/payments/{id}/confirm/  → Confirmer (webhook / admin)
    GET  /api/v1/payments/subscription/  → Abonnement actif du pro
    """
    serializer_class   = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related(
            'booking', 'booking__shop').order_by('-created_at')

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """
        Initie un paiement. Pour Mobile Money (MTN/Airtel Congo),
        intégrer l'API CinetPay ou un agrégateur local ici.
        """
        serializer = PaymentInitSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data    = serializer.validated_data
        booking = data['booking']
        method  = data['method']

        # Créer ou récupérer le paiement
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'user':   request.user,
                'amount': booking.total_price or 0,
                'method': method,
                'status': 'pending',
            }
        )
        if not created:
            payment.method = method
            payment.save(update_fields=['method'])

        response = {
            'payment_id': str(payment.id),
            'amount':     int(payment.amount),
            'method':     method,
            'status':     'pending',
            'booking_ref': booking.get_booking_ref(),
        }

        # ── Mobile Money (CinetPay / agrégateur) ──────────────────────
        if method == 'mobile_money':
            # TODO: appeler l'API CinetPay ou Airtel/MTN Congo
            # Exemple CinetPay :
            # import requests
            # r = requests.post('https://api-checkout.cinetpay.com/v2/payment', json={
            #     'apikey': settings.CINETPAY_API_KEY,
            #     'site_id': settings.CINETPAY_SITE_ID,
            #     'transaction_id': str(payment.id),
            #     'amount': int(payment.amount),
            #     'currency': 'XAF',
            #     'description': f'BeautyMap - {booking.get_booking_ref()}',
            #     'customer_phone_number': data.get('phone'),
            #     'notify_url': 'https://votre-domaine.com/api/v1/payments/webhook/',
            # })
            # response['payment_url'] = r.json().get('data', {}).get('payment_url')
            response['instructions'] = (
                f"Envoyez {int(payment.amount):,} FCFA au +242 XX XXX XX XX "
                f"avec la référence {booking.get_booking_ref()}"
            )

        # ── Espèces ───────────────────────────────────────────────────
        elif method == 'cash':
            payment.status = 'success'
            payment.save(update_fields=['status'])
            response['status'] = 'success'
            response['message'] = 'Paiement en espèces enregistré. Réglez directement au salon.'

        return Response(response)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def confirm(self, request, pk=None):
        """Confirmer un paiement (webhook ou admin uniquement)"""
        payment = self.get_object()
        payment.status       = 'success'
        payment.provider_ref = request.data.get('provider_ref', '')
        payment.save(update_fields=['status', 'provider_ref'])
        # Confirmer automatiquement la réservation
        booking = payment.booking
        if booking.status == 'pending':
            booking.status = 'confirmed'
            booking.save(update_fields=['status'])
        return Response({'success': True, 'payment_id': str(payment.id)})

    @action(detail=False, methods=['get'])
    def subscription(self, request):
        """Abonnement actif du professionnel"""
        if not request.user.is_pro:
            return Response({'error': 'Réservé aux professionnels.'}, status=403)
        sub = Subscription.objects.filter(
            pro=request.user, status='active'
        ).order_by('-start_date').first()
        if not sub:
            return Response({'plan': 'free', 'status': 'none'})
        return Response(SubscriptionSerializer(sub).data)

    @action(detail=False, methods=['post'])
    def webhook(self, request):
        """
        Webhook pour les notifications de paiement (CinetPay, etc.)
        À sécuriser avec une validation de signature en production.
        """
        transaction_id = request.data.get('transaction_id')
        status         = request.data.get('status')  # 'ACCEPTED' ou 'REFUSED'
        if not transaction_id:
            return Response({'error': 'transaction_id requis'}, status=400)
        try:
            payment = Payment.objects.get(pk=transaction_id)
            payment.status = 'success' if status == 'ACCEPTED' else 'failed'
            payment.provider_ref = request.data.get('payment_token', '')
            payment.save(update_fields=['status', 'provider_ref'])
            if payment.status == 'success':
                booking = payment.booking
                booking.status = 'confirmed'
                booking.save(update_fields=['status'])
                from apps.notifications.models import Notification
                Notification.send(booking.client, 'booking_confirmed',
                    'Paiement confirmé !',
                    f"Votre RDV chez {booking.shop.name} est confirmé.")
        except Payment.DoesNotExist:
            return Response({'error': 'Paiement introuvable'}, status=404)
        return Response({'received': True})


_router = DefaultRouter()
_router.register(r'', PaymentViewSet, basename='payment')
urlpatterns = [path('', include(_router.urls))]
