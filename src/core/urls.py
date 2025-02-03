from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

app_name = "core"

router = DefaultRouter()
router.register(r"conversations", api.ConversationViewSet, basename="conversation")

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("theme/<str:theme_name>/", views.set_theme, name="set_theme"),
    path("chat/", views.chat_view, name="chat"),
    path("chat/<int:conversation_id>/", views.chat_view, name="chat_detail"),
    path("api/", include(router.urls)),
]
