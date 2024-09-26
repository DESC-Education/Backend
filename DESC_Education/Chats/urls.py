from django.urls import path

from Chats.views import (
    index,
    room,
    CreateChatView,

)


urlpatterns = [
    path("", index, name="index"),
    # path("<str:room_name>/", room, name="room"),



    path("chat/", CreateChatView.as_view(), name="chat_create"),
    # path('profile/requests', AdminProfileVerifyRequestListView.as_view(), name='admin_v_request_list'),


]
