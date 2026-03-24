"""Messaging Views — BeautyMap Congo"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from .models import Conversation, Message
from apps.accounts.models import User


@login_required
def inbox(request):
    user = request.user
    if user.is_pro:
        conversations = Conversation.objects.filter(pro=user).select_related('client', 'shop').order_by('-updated_at')
    else:
        conversations = Conversation.objects.filter(client=user).select_related('pro', 'shop').order_by('-updated_at')

    active_conv = None
    conv_id = request.GET.get('conv')
    if conv_id:
        try:
            active_conv = conversations.get(pk=conv_id)
            active_conv.messages.filter(is_read=False).exclude(sender=user).update(is_read=True, read_at=timezone.now())
        except Conversation.DoesNotExist:
            pass

    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
        'active_conv': active_conv,
    })


@login_required
def start_conversation(request, shop_slug):
    """Client starts a conversation with shop owner"""
    from apps.shops.models import Shop
    shop = get_object_or_404(Shop, slug=shop_slug)
    pro = shop.owner

    if request.user == pro:
        return redirect('inbox')

    conv, created = Conversation.objects.get_or_create(
        client=request.user, pro=pro, shop=shop
    )
    return redirect(f'/messages/?conv={conv.pk}')


@login_required
@require_POST
def send_message(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id)
    if request.user not in [conv.client, conv.pro]:
        return JsonResponse({'error': 'Non autorisé'}, status=403)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    content = data.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Message vide'}, status=400)

    msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
    conv.updated_at = timezone.now()
    conv.save()

    return JsonResponse({
        'success': True,
        'message': {
            'id': str(msg.id),
            'content': msg.content,
            'sender_name': request.user.get_full_name(),
            'sender_initials': request.user.get_initials(),
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_mine': True,
        }
    })
