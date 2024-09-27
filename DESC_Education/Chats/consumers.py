import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from Chats.models import Chat
from drf_spectacular_websocket.decorators import extend_ws_schema
from Chats.serializers import (WebSocketSerializer)
from Chats.models import (
    Message,

)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.chat_id}"
        self.user = self.scope.get('user')

        # if not await self._check_permissions():
        #     await self.close(code=4002, reason="Permission denied")

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @extend_ws_schema(
        type='receive',
        summary='send_message_summary',
        description='send_message_description',
        request=None,
    )
    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        serializer = WebSocketSerializer(data=json.loads(text_data))
        serializer.is_valid(raise_exception=True)

        payload = await self.create_message(serializer.data)
        serializer.validated_data['payload'] = payload

        await self.channel_layer.group_send(
            self.room_group_name, {'message': serializer.validated_data, 'type': 'chat.message'}
        )

    # Receive message from room group
    async def chat_message(self, event):
        serializer = WebSocketSerializer(data=event['message'])
        serializer.is_valid(raise_exception=True)

        # Send message to WebSocket
        await self.send(text_data=json.dumps(serializer.validated_data))

    @database_sync_to_async
    def create_message(self, data):
        type = data.get('type')
        payload = data.get('payload')

        match type:
            case 'message':
                mes = Message.objects.create(
                    chat_id=self.chat_id,
                    user_id=self.user.id,
                    message=payload, )
                return {'message': mes.message, 'id': mes.id}
            case "viewed":
                mes = Message.objects.get(id=payload)



    @database_sync_to_async
    def _check_permissions(self):
        if isinstance(self.user, AnonymousUser):
            return False
        chat = Chat.objects.filter(pk=self.chat_id, members=self.user).first()
        if chat:
            return True
        else:
            return False
