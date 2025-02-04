from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

from chat.models import Conversation, Message

from .forms import CustomUserCreationForm, UserSettingsForm
from .tokens import account_activation_token


def landing_page(request):
    return render(request, "core/landing.html")


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("core:landing")
            else:
                messages.error(request, _("Invalid username or password."))
    else:
        form = AuthenticationForm()

    context = {
        "form": form,
        "social_auth_enabled": settings.SOCIAL_AUTH_ENABLED,
        "social_providers": settings.SOCIAL_AUTH_PROVIDERS,
    }
    return render(request, "core/login.html", context)


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = _("Please verify your email")
            message = render_to_string(
                "core/email/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()

            messages.success(
                request,
                _("A verification email has been sent. Please check your inbox."),
            )
            return redirect("core:login")
    else:
        form = CustomUserCreationForm()

    context = {
        "form": form,
        "social_auth_enabled": settings.SOCIAL_AUTH_ENABLED,
        "social_providers": settings.SOCIAL_AUTH_PROVIDERS,
    }
    return render(request, "core/register.html", context)


def logout_view(request):
    logout(request)
    return redirect("core:landing")


def set_theme(request, theme_name):
    if theme_name in settings.AVAILABLE_THEMES:
        request.session["theme"] = theme_name
    return redirect(request.META.get("HTTP_REFERER", "core:landing"))


@login_required
async def chat_view(request, conversation_id=None):
    conversations = (
        await Conversation.objects.filter(user=request.user)
        .order_by("-updated_at")
        .all()
    )
    current_conversation = None

    if conversation_id:
        current_conversation = await get_object_or_404(
            Conversation.objects.prefetch_related("messages"),
            id=conversation_id,
            user=request.user,
        )

    return render(
        request,
        "core/chat.html",
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

    return render(
        request,
        "core/chat.html",
        {
            "conversations": await Conversation.objects.filter(user=request.user)
            .order_by("-updated_at")
            .all(),
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

    return render(
        request,
        "core/chat.html",
        {
            "conversations": await Conversation.objects.filter(user=request.user)
            .order_by("-updated_at")
            .all(),
            "current_conversation": conversation,
        },
    )


@login_required
def settings_view(request):
    if request.method == "POST":
        form = UserSettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your profile has been updated."))
            return redirect("core:settings")
    else:
        form = UserSettingsForm(instance=request.user)

    return render(request, "core/settings.html", {"form": form})
