# apps/notifications/urls.py
from django.urls import path
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.utils import timezone

@login_required
def list_notifs(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:30]
    return JsonResponse({'notifications': [
        {'id': str(n.id), 'title': n.title, 'message': n.message,
         'type': n.notif_type, 'is_read': n.is_read, 'created_at': n.created_at.strftime('%d/%m/%Y %H:%M')}
        for n in notifs
    ]})

@login_required
def mark_read(request, notif_id):
    Notification.objects.filter(pk=notif_id, user=request.user).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True})

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True})

urlpatterns = [
    path('', list_notifs, name='notifications'),
    path('<uuid:notif_id>/lue/', mark_read, name='mark_read'),
    path('tout-lire/', mark_all_read, name='mark_all_read'),
]
