import json
from uuid import UUID

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get conversation ID from URL route
        self.conversation_id = str(self.scope["url_route"]["kwargs"]["conversation_id"])
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if conversation exists and user has permission
        try:
            conversation = await self.get_conversation()
            if not await self.has_permission(conversation):
                await self.close()
                return
        except Exception:
            await self.close()
            return

        # Join conversation group
        await self.channel_layer.group_add(
            f"chat_{self.conversation_id}", self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave conversation group
        await self.channel_layer.group_discard(
            f"chat_{self.conversation_id}", self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("content", "").strip()

        if not content:
            return

        # Save user message
        message = await self.save_message("user", content)

        # Send message to group
        await self.channel_layer.group_send(
            f"chat_{self.conversation_id}",
            {
                "type": "chat.message",
                "message": {
                    "role": "user",
                    "content": content,
                },
            },
        )

        # Generate and save AI response
        response = (
            f"This is a sample response to: {content}"  # Replace with actual AI call
        )
        words = response.split()

        # Send response word by word
        for i, word in enumerate(words):
            await self.channel_layer.group_send(
                f"chat_{self.conversation_id}",
                {
                    "type": "chat.message",
                    "message": {
                        "role": "assistant",
                        "content": word + " ",
                        "done": i == len(words) - 1,
                    },
                },
            )

        # Save complete response
        await self.save_message("assistant", response)

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def get_conversation(self):
        return get_object_or_404(Conversation, id=UUID(self.conversation_id))

    @database_sync_to_async
    def has_permission(self, conversation):
        return self.user.has_perm("view_own_conversation", conversation)

    @database_sync_to_async
    def save_message(self, role, content):
        return Message.objects.create(
            conversation_id=UUID(self.conversation_id), role=role, content=content
        )
