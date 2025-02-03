from .settings import *

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Auto-login settings
AUTO_LOGIN_ENABLED = True
AUTO_LOGIN_USER = {
    "username": "dev_user",
    "password": "dev_password",
    "email": "dev@example.com",
}

# Email settings for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Social auth settings for development
SOCIAL_AUTH_ENABLED = True
SOCIAL_AUTH_PROVIDERS = {
    "google": True,
    "azure": True,
}


# Move user creation to a ready handler
def ready_handler(sender, **kwargs):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if (
        AUTO_LOGIN_ENABLED
        and not User.objects.filter(username=AUTO_LOGIN_USER["username"]).exists()
    ):
        User.objects.create_superuser(
            username=AUTO_LOGIN_USER["username"],
            email=AUTO_LOGIN_USER["email"],
            password=AUTO_LOGIN_USER["password"],
        )


# Connect the ready handler to the post_migrate signal
from django.db.models.signals import post_migrate

post_migrate.connect(ready_handler)
