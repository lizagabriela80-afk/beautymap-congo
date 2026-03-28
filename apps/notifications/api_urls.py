# ═══════════════════════════════════════════════════════════════
#  apps/notifications/api_urls.py  — API Notifications (mobile)
# ═══════════════════════════════════════════════════════════════
from django.urls import path, include
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from django.utils import timezone
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'notif_type', 'title', 'message', 'link',
                  'is_read', 'read_at', 'created_at']
        read_only_fields = fields


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /api/v1/notifications/                → Toutes les notifications
    GET  /api/v1/notifications/unread/         → Non lues
    GET  /api/v1/notifications/count/          → Nombre de non lues
    POST /api/v1/notifications/{id}/mark_read/ → Marquer une comme lue
    POST /api/v1/notifications/mark_all_read/  → Tout marquer comme lu
    """
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')[:50]

    @action(detail=False, methods=['get'])
    def unread(self, request):
        qs = self.get_queryset().filter(is_read=False)
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def count(self, request):
        n = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': n})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=['is_read', 'read_at'])
        return Response({'success': True})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        n = self.get_queryset().filter(is_read=False).update(
            is_read=True, read_at=timezone.now())
        return Response({'marked_read': n})


_router = DefaultRouter()
_router.register(r'', NotificationViewSet, basename='notification')
urlpatterns = [path('', include(_router.urls))]
