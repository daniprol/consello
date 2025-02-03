import random

from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def ask(self, request, pk=None):
        conversation = self.get_object()
        question = request.data.get("message", "")

        # Create user message
        Message.objects.create(conversation=conversation, role="user", content=question)

        # Generate mock response (for development)
        words = [
            _("Galicia"),
            _("culture"),
            _("history"),
            _("beaches"),
            _("food"),
            _("traditions"),
            _("festivals"),
            _("nature"),
            _("Santiago"),
            _("Compostela"),
            _("cathedral"),
            _("pilgrimage"),
            _("seafood"),
            _("octopus"),
            _("wine"),
            _("Celtic"),
        ]
        response = " ".join(random.choices(words, k=random.randint(10, 20)))

        # Create assistant message
        message = Message.objects.create(
            conversation=conversation, role="assistant", content=response
        )

        # Update conversation timestamp
        conversation.save()  # This updates the updated_at field

        return Response({"role": message.role, "content": message.content})
