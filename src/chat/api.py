from typing import List
from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from guardian.decorators import permission_required_or_403
from guardian.shortcuts import assign_perm
from ninja import File, NinjaAPI
from ninja.security import django_auth

from .models import Conversation, Message
from .schemas import (
    ConversationCreateSchema,
    ConversationSchema,
    MessageCreateSchema,
    MessageSchema,
    MessageStreamSchema,
)

api = NinjaAPI(auth=django_auth)


@api.get("/conversations", response=List[ConversationSchema])
async def list_conversations(request):
    return (
        await Conversation.objects.filter(user=request.user)
        .prefetch_related("messages")
        .all()
    )


@api.post("/conversations", response=ConversationSchema)
@transaction.atomic
async def create_conversation(request, payload: ConversationCreateSchema):
    conversation = await Conversation.objects.create(
        user=request.user, title=payload.title
    )

    return conversation


@api.get("/conversations/{conversation_id}", response=ConversationSchema)
async def get_conversation(request, conversation_id: UUID):
    conversation = await get_object_or_404(
        Conversation.objects.prefetch_related("messages"), id=conversation_id
    )

    # Check if the user is the creator of the conversation
    if conversation.user != request.user:
        raise PermissionDenied("You do not have permission to view this conversation.")

    return conversation
