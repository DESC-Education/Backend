from django.urls import re_path, path

from Chats.consumers import ChatConsumer

websocket_urlpatterns = [
    path(r"ws/chat/<uuid:room_id>/", ChatConsumer.as_asgi()),
]