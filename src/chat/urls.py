from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path("<uuid:conversation_id>/", views.chat_view, name="chat_detail"),
    path("<uuid:conversation_id>/message/", views.chat_message, name="chat_message"),
    path("new/", views.new_chat, name="new_chat"),
]
