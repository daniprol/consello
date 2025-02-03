from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

from .forms import CustomUserCreationForm
from .models import Conversation
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
def chat_view(request, conversation_id=None):
    if conversation_id:
        conversation = get_object_or_404(
            Conversation, id=conversation_id, user=request.user
        )
    else:
        # Create new conversation
        conversation = Conversation.objects.create(
            user=request.user, title=_("New Conversation")
        )

    conversations = Conversation.objects.filter(user=request.user)

    quick_prompts = [
        {
            "title": _("Cultural Routes"),
            "description": _("Discover the best cultural routes in Galicia"),
            "text": _(
                "What are the most interesting cultural routes to explore in Galicia?"
            ),
        },
        {
            "title": _("Local Festivals"),
            "description": _("Find information about traditional festivals"),
            "text": _(
                "What are the main traditional festivals in Galicia and when do they take place?"
            ),
        },
        {
            "title": _("Gastronomy Guide"),
            "description": _("Learn about Galician cuisine"),
            "text": _(
                "What are the must-try traditional Galician dishes and where can I find them?"
            ),
        },
        {
            "title": _("Hidden Gems"),
            "description": _("Discover lesser-known places"),
            "text": _(
                "What are some hidden gems or off-the-beaten-path places to visit in Galicia?"
            ),
        },
        {
            "title": _("Coastal Experience"),
            "description": _("Explore the Galician coast"),
            "text": _(
                "What are the most beautiful beaches and coastal towns to visit in Galicia?"
            ),
        },
        {
            "title": _("Historical Sites"),
            "description": _("Visit historical landmarks"),
            "text": _(
                "What are the most important historical sites and monuments in Galicia?"
            ),
        },
    ]

    context = {
        "quick_prompts": quick_prompts,
        "conversations": conversations,
        "current_conversation": conversation,
    }
    return render(request, "core/chat.html", context)
