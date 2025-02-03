from django.conf.urls.i18n import i18n_patterns
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("theme/<str:theme_name>/", views.set_theme, name="set_theme"),
]
