import importlib

from django.conf import settings


def theme(request):
    theme_name = request.session.get("theme", settings.DEFAULT_THEME)
    try:
        theme_module = importlib.import_module(f"core.themes.{theme_name}")
        colors = theme_module.COLORS
    except ImportError:
        theme_module = importlib.import_module("core.themes.default")
        colors = theme_module.COLORS

    return {
        "theme": colors,
        "available_themes": settings.AVAILABLE_THEMES,
    }
