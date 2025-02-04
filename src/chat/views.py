from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Conversation, Message


@sync_to_async
def get_conversations(user):
    return list(
        Conversation.objects.filter(user=user).order_by("-updated_at")
    )  # Important: list()


@login_required
async def chat_view(request, conversation_id=None):
    conversations = await get_conversations(request.user)
    # queryset = MyModel.objects.all()

    # # Use async iteration to fetch results:
    # results = []
    # async for instance in queryset:
    #     results.append(instance)
    current_conversation = None

    if conversation_id:
        current_conversation = await get_object_or_404(
            Conversation.objects.prefetch_related("messages"),
            id=conversation_id,
            user=request.user,
        )

    return render(
        request,
        "chat/chat.html",
        {
            "conversations": conversations,
            "current_conversation": current_conversation,
        },
    )


@login_required
async def chat_message(request, conversation_id):
    if request.method != "POST":
        return HttpResponse(status=405)

    conversation = await get_object_or_404(
        Conversation.objects.prefetch_related("messages"),
        id=conversation_id,
        user=request.user,
    )

    # Create user message
    content = request.POST.get("content")
    await Message.objects.create(
        conversation=conversation, role="user", content=content
    )

    # Create AI response (dummy for now)
    response = "This is a sample response to: " + content
    await Message.objects.create(
        conversation=conversation, role="assistant", content=response
    )

    # Update conversation timestamp
    conversation.save()

    conversations = await get_conversations(request.user)
    return render(
        request,
        "chat/chat.html",
        {
            "conversations": conversations,
            "current_conversation": conversation,
        },
    )


@login_required
async def new_chat(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    # Create new conversation
    conversation = await Conversation.objects.create(
        user=request.user,
        title="New Chat",  # You might want to generate a better title
    )

    conversations = await get_conversations(request.user)
    return render(
        request,
        "chat/chat.html",
        {
            "conversations": conversations,
            "current_conversation": conversation,
        },
    )
