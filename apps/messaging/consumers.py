"""WebSocket Consumer for Real-Time Messaging"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conv_id = self.scope['url_route']['kwargs']['conv_id']
        self.room_group_name = f'chat_{self.conv_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Check user belongs to this conversation
        has_access = await self.check_access()
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            content = data.get('content', '').strip()
            if not content:
                return

            # Save to DB
            msg = await self.save_message(content)

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': str(msg['id']),
                        'content': msg['content'],
                        'sender_id': self.user.pk,
                        'sender_name': self.user.get_full_name(),
                        'sender_initials': self.user.get_initials(),
                        'created_at': msg['created_at'],
                    }
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_access(self):
        from apps.messaging.models import Conversation
        try:
            conv = Conversation.objects.get(pk=self.conv_id)
            return self.user in [conv.client, conv.pro]
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        from apps.messaging.models import Conversation, Message
        conv = Conversation.objects.get(pk=self.conv_id)
        msg = Message.objects.create(conversation=conv, sender=self.user, content=content)
        conv.updated_at = timezone.now()
        conv.save()
        return {
            'id': str(msg.id),
            'content': msg.content,
            'created_at': msg.created_at.strftime('%H:%M'),
        }
