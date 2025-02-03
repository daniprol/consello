from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Import and connect signals
        from django.conf import settings

        if hasattr(settings, "AUTO_LOGIN_ENABLED") and settings.AUTO_LOGIN_ENABLED:
            from django.contrib.auth import get_user_model

            User = get_user_model()

            if not User.objects.filter(
                username=settings.AUTO_LOGIN_USER["username"]
            ).exists():
                User.objects.create_superuser(
                    username=settings.AUTO_LOGIN_USER["username"],
                    email=settings.AUTO_LOGIN_USER["email"],
                    password=settings.AUTO_LOGIN_USER["password"],
                )
