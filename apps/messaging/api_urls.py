# ═══════════════════════════════════════════════════════════════
#  apps/messaging/api_urls.py  — API Messagerie (mobile)
# ═══════════════════════════════════════════════════════════════
from django.urls import path, include
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from django.utils import timezone
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name     = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_initials = serializers.CharField(source='sender.get_initials',  read_only=True)
    is_mine         = serializers.SerializerMethodField()
    attachment_url  = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ['id', 'sender_name', 'sender_initials', 'content',
                  'attachment', 'attachment_url', 'is_read', 'read_at',
                  'created_at', 'is_mine']
        read_only_fields = ['id', 'is_read', 'read_at', 'created_at']
        extra_kwargs = {'attachment': {'write_only': True, 'required': False}}

    def get_is_mine(self, obj):
        req = self.context.get('request')
        return req and obj.sender_id == req.user.id

    def get_attachment_url(self, obj):
        req = self.context.get('request')
        if obj.attachment and req:
            return req.build_absolute_uri(obj.attachment.url)
        return None


class ConversationSerializer(serializers.ModelSerializer):
    other_user   = serializers.SerializerMethodField()
    shop_name    = serializers.CharField(source='shop.name', read_only=True)
    shop_slug    = serializers.CharField(source='shop.slug', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ['id', 'other_user', 'shop', 'shop_name', 'shop_slug',
                  'last_message', 'unread_count', 'created_at', 'updated_at']

    def get_other_user(self, obj):
        req = self.context.get('request')
        if not req:
            return None
        other = obj.pro if req.user == obj.client else obj.client
        return {
            'id': other.pk,
            'full_name': other.get_full_name(),
            'initials':  other.get_initials(),
            'avatar':    req.build_absolute_uri(other.avatar.url) if other.avatar else None,
        }

    def get_last_message(self, obj):
        msg = obj.get_last_message()
        if not msg:
            return None
        return {
            'content':    msg.content[:80],
            'created_at': msg.created_at.strftime('%d/%m %H:%M'),
            'is_mine':    msg.sender_id == self.context['request'].user.id,
        }

    def get_unread_count(self, obj):
        req = self.context.get('request')
        return obj.get_unread_count(req.user) if req else 0


class ConversationViewSet(viewsets.ModelViewSet):
    """
    GET  /api/v1/messages/                      → Liste des conversations
    POST /api/v1/messages/start/                → Démarrer avec un salon
    GET  /api/v1/messages/{id}/messages/        → Messages paginés
    POST /api/v1/messages/{id}/send/            → Envoyer un message
    POST /api/v1/messages/{id}/mark_read/       → Marquer comme lus
    GET  /api/v1/messages/unread_count/         → Compteur non lus total
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names  = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        u = self.request.user
        qs = Conversation.objects.filter(pro=u) if u.is_pro else Conversation.objects.filter(client=u)
        return qs.select_related('client', 'pro', 'shop').order_by('-updated_at')

    def list(self, request, *args, **kwargs):
        serializer = ConversationSerializer(self.get_queryset(), many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def start(self, request):
        from apps.shops.models import Shop
        from django.shortcuts import get_object_or_404
        slug = request.data.get('shop_slug', '').strip()
        if not slug:
            return Response({'error': 'shop_slug requis.'}, status=400)
        shop = get_object_or_404(Shop, slug=slug, is_active=True)
        if request.user == shop.owner:
            return Response({'error': 'Vous ne pouvez pas vous envoyer un message.'}, status=400)
        conv, created = Conversation.objects.get_or_create(
            client=request.user, pro=shop.owner, shop=shop)
        initial = request.data.get('initial_message', '').strip()
        if initial:
            Message.objects.create(conversation=conv, sender=request.user, content=initial)
            conv.updated_at = timezone.now(); conv.save()
        return Response(ConversationSerializer(conv, context={'request': request}).data,
                        status=201 if created else 200)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conv = self.get_object()
        if request.user not in [conv.client, conv.pro]:
            return Response({'error': 'Non autorisé.'}, status=403)
        # Auto-mark as read
        conv.messages.filter(is_read=False).exclude(sender=request.user).update(
            is_read=True, read_at=timezone.now())
        msgs = conv.messages.select_related('sender').order_by('created_at')
        # Simple manual pagination
        page  = int(request.query_params.get('page', 1))
        size  = int(request.query_params.get('page_size', 30))
        start = (page - 1) * size
        total = msgs.count()
        serializer = MessageSerializer(msgs[start:start+size], many=True, context={'request': request})
        return Response({'count': total, 'page': page, 'results': serializer.data})

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        conv = self.get_object()
        if request.user not in [conv.client, conv.pro]:
            return Response({'error': 'Non autorisé.'}, status=403)
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': 'Le message ne peut pas être vide.'}, status=400)
        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        conv.updated_at = timezone.now(); conv.save()
        # Notification
        try:
            from apps.notifications.models import Notification
            other = conv.pro if request.user == conv.client else conv.client
            Notification.send(other, 'message_new', 'Nouveau message',
                f"{request.user.get_full_name()} vous a envoyé un message.",
                link=f'/messages/?conv={conv.pk}')
        except Exception:
            pass
        return Response(MessageSerializer(msg, context={'request': request}).data, status=201)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        conv = self.get_object()
        if request.user not in [conv.client, conv.pro]:
            return Response({'error': 'Non autorisé.'}, status=403)
        n = conv.messages.filter(is_read=False).exclude(sender=request.user).update(
            is_read=True, read_at=timezone.now())
        return Response({'marked_read': n})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        u = self.request.user
        convs = Conversation.objects.filter(pro=u) if u.is_pro else Conversation.objects.filter(client=u)
        total = sum(c.get_unread_count(u) for c in convs)
        return Response({'unread_count': total})


_router = DefaultRouter()
_router.register(r'', ConversationViewSet, basename='conversation')
urlpatterns = [path('', include(_router.urls))]
