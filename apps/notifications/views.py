"""Notifications Views — BeautyMap Congo"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification


@login_required
def notifications_list(request):
    """Page liste des notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def list_notifs_json(request):
    """API JSON pour le badge nav"""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:30]
    return JsonResponse({'notifications': [
        {
            'id':         str(n.id),
            'title':      n.title,
            'message':    n.message,
            'type':       n.notif_type,
            'is_read':    n.is_read,
            'link':       n.link,
            'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
        }
        for n in notifs
    ]})


@login_required
def mark_read(request, notif_id):
    Notification.objects.filter(pk=notif_id, user=request.user).update(
        is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True})


@login_required
def mark_all_read(request):
    n = Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True, 'marked': n})
