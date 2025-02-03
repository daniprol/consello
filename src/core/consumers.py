import json
import time

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils.translation import gettext as _

from .models import Conversation, Message


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if not self.scope["user"].is_authenticated:
            self.close()
            return

        self.accept()
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        async_to_sync(self.channel_layer.group_add)(
            f"chat_{self.conversation_id}", self.channel_name
        )

    def disconnect(self, close_code):
        if hasattr(self, "conversation_id"):
            async_to_sync(self.channel_layer.group_discard)(
                f"chat_{self.conversation_id}", self.channel_name
            )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        conversation = Conversation.objects.get(id=self.conversation_id)

        # Save user message
        Message.objects.create(conversation=conversation, role="user", content=message)

        # Echo back user message
        self.send(json.dumps({"role": "user", "content": message}))

        # Get mock response
        response = self.get_mock_response(message)

        # Save assistant message
        Message.objects.create(
            conversation=conversation, role="assistant", content=response
        )

        # Update conversation timestamp
        conversation.save()

        # Stream response
        words = response.split()
        partial_response = ""
        for word in words:
            partial_response += word + " "
            self.send(
                json.dumps({"role": "assistant", "content": partial_response.strip()})
            )
            time.sleep(0.1)

    def get_mock_response(self, message):
        # Mock responses based on message content
        if "festival" in message.lower():
            return _(
                "The most important festivals in Galicia include the Festival of San Xoán, celebrated on June 24th with bonfires and traditional music, and the Festival of the Apostle Santiago, celebrated in Santiago de Compostela in July."
            )
        elif "food" in message.lower() or "dish" in message.lower():
            return _(
                "Galician cuisine is famous for its seafood dishes like pulpo á feira (octopus), empanada gallega (savory pie), and caldo gallego (traditional soup). You can find these dishes in traditional restaurants called 'marisquerías'."
            )
        elif "beach" in message.lower():
            return _(
                "The Rías Baixas region offers beautiful beaches like Playa de Rodas in the Cíes Islands, often considered one of the best beaches in the world. The Costa da Morte also has spectacular wild beaches."
            )
        else:
            return _(
                "Galicia is a beautiful region with rich culture and history. You can explore the historic Santiago de Compostela, visit the Tower of Hercules in A Coruña, or discover the Roman walls of Lugo."
            )
