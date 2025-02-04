import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from guardian.models import GroupObjectPermissionBase, UserObjectPermissionBase


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_conversations",
    )
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        # permissions = [
        #     ("view_own_conversation", "Can view own conversation"),
        #     ("delete_own_conversation", "Can delete own conversation"),
        # ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def get_last_message(self):
        return self.messages.last()


class ConversationUserObjectPermission(UserObjectPermissionBase):
    content_object = models.ForeignKey(Conversation, on_delete=models.CASCADE)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(
        max_length=10,
        choices=[("user", _("User")), ("assistant", _("Assistant"))],
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
