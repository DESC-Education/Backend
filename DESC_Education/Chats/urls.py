from django.urls import path

from Chats.views import (
    index,
    room,
    CreateChatView,
    ChatListView,
    ChatDetailView

)


urlpatterns = [
    path("", index, name="index"),
    # path("c/<uuid:chat_id>/", room, name="room"),


    path("chats", ChatListView.as_view(), name="chat_list"),
    path("chat", CreateChatView.as_view(), name="chat_create"),
    path("chat/<uuid:pk>", ChatDetailView.as_view(), name="chat_detail"),

    # path('profile/requests', AdminProfileVerifyRequestListView.as_view(), name='admin_v_request_list'),


]
