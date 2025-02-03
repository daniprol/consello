from django.conf import settings
from django.contrib.auth import authenticate, login


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.user.is_authenticated
            and hasattr(settings, "AUTO_LOGIN_ENABLED")
            and settings.AUTO_LOGIN_ENABLED
        ):
            user = authenticate(
                username=settings.AUTO_LOGIN_USER["username"],
                password=settings.AUTO_LOGIN_USER["password"],
            )
            if user:
                login(request, user)

        return self.get_response(request)
