import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from Chats.models import Chat
from drf_spectacular_websocket.decorators import extend_ws_schema

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope.get('user')

        # if not await self._check_permissions():
        #     await self.close(code=4002, reason="Permission denied")


        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @extend_ws_schema(
        type='receive',
        summary='send_message_summary',
        description='send_message_description',
        request=None,

    )
    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, 'type': 'сообщение'}))

    @database_sync_to_async
    def _check_permissions(self):
        if isinstance(self.user, AnonymousUser):
            return False
        chat = Chat.objects.filter(pk=self.room_id, members=self.user).first()
        if chat:
            return True
        else:
            return False





