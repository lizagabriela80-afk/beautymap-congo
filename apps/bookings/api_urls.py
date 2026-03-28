# ═══════════════════════════════════════════════════════════════
#  apps/bookings/api_urls.py  — API Réservations (mobile)
# ═══════════════════════════════════════════════════════════════
from django.urls import path, include
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from django.utils import timezone
from .models import Booking, TimeSlot


class BookingSerializer(serializers.ModelSerializer):
    shop_name       = serializers.CharField(source='shop.name',           read_only=True)
    shop_slug       = serializers.CharField(source='shop.slug',           read_only=True)
    shop_address    = serializers.CharField(source='shop.address',        read_only=True)
    shop_phone      = serializers.CharField(source='shop.phone',          read_only=True)
    shop_whatsapp   = serializers.CharField(source='shop.whatsapp',       read_only=True)
    service_name    = serializers.CharField(source='service.name',        read_only=True)
    service_duration= serializers.IntegerField(source='service.duration_minutes', read_only=True)
    client_name     = serializers.CharField(source='client.get_full_name', read_only=True)
    booking_ref     = serializers.SerializerMethodField()
    can_cancel      = serializers.SerializerMethodField()
    is_upcoming     = serializers.SerializerMethodField()
    status_label    = serializers.CharField(source='get_status_display',  read_only=True)

    class Meta:
        model  = Booking
        fields = [
            'id', 'booking_ref',
            'client_name',
            'shop', 'shop_name', 'shop_slug', 'shop_address', 'shop_phone', 'shop_whatsapp',
            'service', 'service_name', 'service_duration',
            'date', 'start_time', 'end_time',
            'status', 'status_label', 'notes', 'client_phone',
            'total_price', 'promo_code', 'discount_amount',
            'can_cancel', 'is_upcoming',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'end_time', 'created_at', 'updated_at']

    def get_booking_ref(self, obj):  return obj.get_booking_ref()
    def get_can_cancel(self,  obj):  return obj.can_cancel()
    def get_is_upcoming(self, obj):  return obj.is_upcoming()


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Booking
        fields = ['shop', 'service', 'date', 'start_time', 'notes', 'client_phone', 'promo_code']

    def validate(self, data):
        if data.get('date') and data['date'] < timezone.now().date():
            raise serializers.ValidationError({'date': 'La date ne peut pas être dans le passé.'})
        if data.get('shop') and data.get('service') and data['service'].shop_id != data['shop'].pk:
            raise serializers.ValidationError({'service': "Ce service n'appartient pas à ce salon."})
        if data.get('shop') and data.get('date') and data.get('start_time'):
            conflict = Booking.objects.filter(
                shop=data['shop'], date=data['date'],
                start_time=data['start_time'], status__in=['pending', 'confirmed']
            ).exists()
            if conflict:
                raise serializers.ValidationError({'start_time': 'Ce créneau est déjà réservé.'})
        return data

    def create(self, validated_data):
        svc = validated_data.get('service')
        return Booking.objects.create(
            client=self.context['request'].user,
            total_price=svc.price if svc else None,
            **validated_data
        )


class BookingViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/bookings/                → Mes réservations
    POST   /api/v1/bookings/                → Créer une réservation
    GET    /api/v1/bookings/{id}/           → Détail
    PATCH  /api/v1/bookings/{id}/           → Modifier notes
    POST   /api/v1/bookings/{id}/cancel/    → Annuler
    POST   /api/v1/bookings/{id}/confirm/   → Confirmer (pro)
    POST   /api/v1/bookings/{id}/complete/  → Terminer (pro)
    GET    /api/v1/bookings/upcoming/       → Prochains RDV
    GET    /api/v1/bookings/history/        → Historique
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names  = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        u = self.request.user
        qs = Booking.objects.filter(shop__owner=u) if u.is_pro else Booking.objects.filter(client=u)
        return qs.select_related('client', 'shop', 'service').order_by('-date', '-start_time')

    def get_serializer_class(self):
        return BookingCreateSerializer if self.action == 'create' else BookingSerializer

    def create(self, request, *args, **kwargs):
        s = BookingCreateSerializer(data=request.data, context={'request': request})
        s.is_valid(raise_exception=True)
        booking = s.save()
        try:
            from apps.notifications.models import Notification
            Notification.send(
                booking.shop.owner, 'booking_new', 'Nouvelle réservation',
                f"{booking.client.get_full_name()} a réservé {booking.service.name} pour le {booking.date}",
                link='/dashboard/?tab=rdv')
        except Exception:
            pass
        return Response(BookingSerializer(booking, context={'request': request}).data, status=201)

    def _change_status(self, request, pk, new_status, allowed_roles='pro'):
        booking = self.get_object()
        if allowed_roles == 'pro' and getattr(booking.shop, 'owner', None) != request.user:
            return Response({'error': 'Réservé aux professionnels.'}, status=403)
        if allowed_roles == 'any' and booking.client != request.user and \
           getattr(booking.shop, 'owner', None) != request.user:
            return Response({'error': 'Non autorisé.'}, status=403)
        if new_status == 'cancelled' and not booking.can_cancel():
            return Response({'error': "Impossible d'annuler ce rendez-vous."}, status=400)
        booking.status = new_status
        booking.save(update_fields=['status'])
        return Response(BookingSerializer(booking, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        resp = self._change_status(request, pk, 'cancelled', allowed_roles='any')
        if resp.status_code == 200:
            b = self.get_object()
            try:
                from apps.notifications.models import Notification
                if request.user == b.shop.owner:
                    Notification.send(b.client, 'booking_cancelled', 'RDV annulé',
                        f"Votre RDV du {b.date} a été annulé par le salon.")
                else:
                    Notification.send(b.shop.owner, 'booking_cancelled', 'RDV annulé',
                        f"{b.client.get_full_name()} a annulé son RDV du {b.date}.")
            except Exception:
                pass
        return resp

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        resp = self._change_status(request, pk, 'confirmed')
        if resp.status_code == 200:
            b = self.get_object()
            try:
                from apps.notifications.models import Notification
                Notification.send(b.client, 'booking_confirmed', 'RDV confirmé !',
                    f"Votre RDV chez {b.shop.name} le {b.date} est confirmé.")
            except Exception:
                pass
        return resp

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        return self._change_status(request, pk, 'completed')

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        u  = request.user
        qs = Booking.objects.filter(
            **(dict(shop__owner=u) if u.is_pro else dict(client=u)),
            status__in=['pending', 'confirmed'],
            date__gte=timezone.now().date()
        ).select_related('client', 'shop', 'service').order_by('date', 'start_time')
        return Response(BookingSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        u  = request.user
        qs = Booking.objects.filter(
            **(dict(shop__owner=u) if u.is_pro else dict(client=u)),
            status__in=['completed', 'cancelled', 'no_show']
        ).select_related('client', 'shop', 'service').order_by('-date')[:50]
        return Response(BookingSerializer(qs, many=True, context={'request': request}).data)


class AvailableSlotsView(APIView):
    """
    GET /api/v1/bookings/slots/?shop=<uuid>&service=<id>&date=<YYYY-MM-DD>
    Retourne les créneaux disponibles.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from datetime import date, time, timedelta, datetime
        from apps.shops.models import Shop, Service
        from django.shortcuts import get_object_or_404

        shop_id    = request.query_params.get('shop')
        service_id = request.query_params.get('service')
        date_str   = request.query_params.get('date')

        if not all([shop_id, service_id, date_str]):
            return Response({'error': 'Paramètres shop, service et date requis.'}, status=400)

        try:
            booking_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Format de date invalide (YYYY-MM-DD attendu).'}, status=400)

        if booking_date < timezone.now().date():
            return Response({'error': 'La date ne peut pas être dans le passé.'}, status=400)

        shop    = get_object_or_404(Shop,    pk=shop_id)
        service = get_object_or_404(Service, pk=service_id, shop=shop)

        booked_times = set(Booking.objects.filter(
            shop=shop, date=booking_date, status__in=['pending', 'confirmed']
        ).values_list('start_time', flat=True))

        # Horaires du salon ce jour
        day_name = booking_date.strftime('%A').lower()
        schedule = shop.schedules.filter(day=day_name, is_closed=False).first()
        open_t   = schedule.open_time  if schedule else time(8, 0)
        close_t  = schedule.close_time if schedule else time(18, 0)

        slots      = []
        slot_time  = open_t
        now        = timezone.localtime()
        interval   = service.duration_minutes or 30

        while slot_time < close_t:
            is_taken = slot_time in booked_times
            is_past  = booking_date == now.date() and slot_time <= now.time()
            slots.append({
                'time':      slot_time.strftime('%H:%M'),
                'available': not is_taken and not is_past,
                'taken':     is_taken,
                'past':      is_past,
            })
            slot_dt   = datetime.combine(booking_date, slot_time) + timedelta(minutes=interval)
            slot_time = slot_dt.time()

        return Response({
            'date':              date_str,
            'shop_id':           str(shop_id),
            'service_id':        service_id,
            'service_name':      service.name,
            'duration_minutes':  service.duration_minutes,
            'slots':             slots,
            'total':             len(slots),
            'available':         sum(1 for s in slots if s['available']),
        })


_router = DefaultRouter()
_router.register(r'', BookingViewSet, basename='booking')
urlpatterns = [
    path('slots/', AvailableSlotsView.as_view(), name='api-slots'),
    path('', include(_router.urls)),
]
