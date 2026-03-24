"""Messaging Models — BeautyMap Congo"""
from django.db import models
import uuid


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='conversations_as_client')
    pro = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='conversations_as_pro')
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['client', 'pro', 'shop']
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conv {self.client.get_full_name()} ↔ {self.pro.get_full_name()}"

    def get_unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='messages_sent')
    content = models.TextField()
    attachment = models.FileField(upload_to='messages/attachments/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}"
