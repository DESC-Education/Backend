from django.urls import path

from Chats.views import (
    index,
    room,
    CreateChatView,
    ChatListView,
    ChatDetailView,
    SendFileView,
    ChatChangeFavoriteView,

)


urlpatterns = [
    path("", index, name="index"),
    # path("c/<uuid:chat_id>/", room, name="room"),


    path("chats", ChatListView.as_view(), name="chat_list"),
    path("chat", CreateChatView.as_view(), name="chat_create"),
    path("chat/<uuid:pk>", ChatDetailView.as_view(), name="chat_detail"),
    path("send_file", SendFileView.as_view(), name="send_file"),
    path("chat/<uuid:pk>/favorite", ChatChangeFavoriteView.as_view(), name="chat_change_favorite"),


    # path('profile/requests', AdminProfileVerifyRequestListView.as_view(), name='admin_v_request_list'),


]
