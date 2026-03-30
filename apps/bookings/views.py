"""Bookings Views — BeautyMap Congo"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
import json
from .models import Booking, TimeSlot
from apps.shops.models import Shop, Service
from apps.notifications.models import Notification


@login_required
def book_service(request, shop_slug, service_id=None):
    """Booking form page"""
    shop = get_object_or_404(Shop, slug=shop_slug, is_active=True)
    services = shop.services.filter(is_active=True)
    service = None
    if service_id:
        service = get_object_or_404(Service, pk=service_id, shop=shop)

    if request.method == 'POST':
        service_id = request.POST.get('service')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        notes = request.POST.get('notes', '')

        try:
            service = get_object_or_404(Service, pk=service_id, shop=shop)
            from datetime import date, time
            booking_date = date.fromisoformat(date_str)
            booking_time = time.fromisoformat(time_str)

            booking = Booking.objects.create(
                client=request.user,
                shop=shop,
                service=service,
                date=booking_date,
                start_time=booking_time,
                notes=notes,
                total_price=service.price,
                client_phone=request.user.phone,
            )

            # Notify shop owner
            Notification.send(
                user=shop.owner,
                notif_type='booking_new',
                title='Nouvelle réservation',
                message=f"{request.user.get_full_name()} a réservé {service.name} pour le {booking_date}",
                link=f'/dashboard/?tab=bookings'
            )

            messages.success(request, f"Réservation confirmée ! Référence: {booking.get_booking_ref()}")
            return redirect('booking_confirm', pk=booking.pk)

        except Exception as e:
            messages.error(request, f"Erreur lors de la réservation: {str(e)}")

    today = timezone.now().date()
    return render(request, 'bookings/book.html', {
        'shop': shop,
        'services': services,
        'selected_service': service,
        'today': today.isoformat(),
    })


@login_required
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    return render(request, 'bookings/confirm.html', {'booking': booking})


@login_required
def get_available_slots(request):
    """Ajax: Get available time slots"""
    shop_id = request.GET.get('shop')
    service_id = request.GET.get('service')
    date_str = request.GET.get('date')

    if not all([shop_id, service_id, date_str]):
        return JsonResponse({'slots': []})

    try:
        from datetime import date, time, timedelta, datetime
        booking_date = date.fromisoformat(date_str)
        service = get_object_or_404(Service, pk=service_id)
        shop = get_object_or_404(Shop, pk=shop_id)

        # Get booked slots for that day
        booked_times = set(
            Booking.objects.filter(
                shop=shop, date=booking_date, status__in=['pending','confirmed']
            ).values_list('start_time', flat=True)
        )

        # Generate slots from 8:00 to 18:00 by 30-min intervals
        slots = []
        slot_time = time(8, 0)
        end_time = time(18, 0)
        while slot_time < end_time:
            is_taken = slot_time in booked_times
            now = timezone.localtime()
            slot_dt = datetime.combine(booking_date, slot_time)
            is_past = booking_date == now.date() and slot_time < now.time()
            slots.append({
                'time': slot_time.strftime('%H:%M'),
                'available': not is_taken and not is_past,
            })
            # Increment by 30 min
            slot_dt_inc = datetime.combine(booking_date, slot_time) + timedelta(minutes=30)
            slot_time = slot_dt_inc.time()

        return JsonResponse({'slots': slots})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_POST
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.client != request.user and booking.shop.owner != request.user:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    if not booking.can_cancel():
        return JsonResponse({'error': 'Impossible d\'annuler ce rendez-vous'}, status=400)
    booking.status = 'cancelled'
    booking.save()
    # Notify
    if request.user == booking.shop.owner:
        Notification.send(booking.client, 'booking_cancelled', 'RDV annulé',
            f"Votre rendez-vous du {booking.date} a été annulé par le salon.")
    else:
        Notification.send(booking.shop.owner, 'booking_cancelled', 'RDV annulé',
            f"{booking.client.get_full_name()} a annulé son RDV du {booking.date}.")
    return JsonResponse({'success': True})


@login_required
@require_POST
def confirm_booking(request, pk):
    """Pro confirms a booking"""
    booking = get_object_or_404(Booking, pk=pk, shop__owner=request.user)
    booking.status = 'confirmed'
    booking.save()
    Notification.send(booking.client, 'booking_confirmed', 'RDV confirmé !',
        f"Votre RDV chez {booking.shop.name} le {booking.date} à {booking.start_time.strftime('%H:%M')} est confirmé.")
    return JsonResponse({'success': True})

@login_required
def book_service(request, shop_slug):
    """
    Page de réservation d’un service pour une boutique
    """
    shop = get_object_or_404(Shop, slug=shop_slug, is_active=True)
    services = shop.services.filter(is_active=True)

    if request.method == 'POST':
        service_id = request.POST.get('service')
        date       = request.POST.get('date')
        time       = request.POST.get('time')
        notes      = request.POST.get('notes', '')

        if not service_id or not date or not time:
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('bookings:book_service', shop_slug=shop.slug)

        service = get_object_or_404(Service, id=service_id, shop=shop)

        booking = Booking.objects.create(
            client=request.user,
            shop=shop,
            service=service,
            date=date,
            time=time,
            notes=notes,
            status='pending'
        )

        messages.success(request, "🎉 Réservation envoyée avec succès !")
        return redirect('shops:shop_detail', slug=shop.slug)

    return render(request, 'bookings/book_service.html', {
        'shop': shop,
        'services': services,
    })