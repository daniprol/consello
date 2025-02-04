from datetime import datetime
from typing import List
from uuid import UUID

from ninja import ModelSchema, Schema

from .models import Conversation, Message


class MessageSchema(ModelSchema):
    class Config:
        model = Message
        model_fields = ["id", "role", "content", "created_at"]


class ConversationSchema(ModelSchema):
    messages: List[MessageSchema]

    class Config:
        model = Conversation
        model_fields = ["id", "title", "created_at", "updated_at"]


class ConversationCreateSchema(Schema):
    title: str


class MessageCreateSchema(Schema):
    content: str


class MessageStreamSchema(Schema):
    content: str
    done: bool
