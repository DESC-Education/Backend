import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, Count
from Chats.models import Chat
from Chats.serializers import (WebSocketSerializer)
from Files.models import File
from Files.serializers import FileSerializer
from Chats.serializers import (
    MessageSerializer
)
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

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        serializer = WebSocketSerializer(data=json.loads(text_data))
        serializer.is_valid(raise_exception=True)

        payload = await self.create_message(serializer.data)
        if payload is None:
            return
        serializer.validated_data['payload'] = json.dumps(payload)

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
                message = payload.get('message', None)
                files = payload.get('files', None)

                if not files and not message:
                    return None

                mes = Message.objects.create(
                    chat_id=self.chat_id,
                    user_id=self.user.id,
                    message=message)

                if files:
                    query_files = File.objects.filter(id__in=files)
                    if str(query_files[0].content_object.id) == str(self.chat_id):
                        for file in query_files:
                            file.content_object = mes
                            file.save()

                return MessageSerializer(instance=mes).data

            case "viewed":
                mes = Message.objects.get(id=payload)

                if not (str(mes.user.id) != str(self.user) and str(mes.chat.id) == str(self.chat_id)):
                    return None
                queryset = Message.objects.filter(~Q(user=self.user) & Q(is_readed=False) & Q(chat__members=self.user))

                unread_chats_count = queryset.filter(Q(chat__members=self.user)) \
                    .aggregate(Count('chat', distinct=True)).get('chat__count')

                chats = queryset.values('chat')\
                    .annotate(unread_count=Count('id'))


                unreaded_message_count = chats.filter(Q(chat_id=self.chat_id))[0].get('unread_count')

                messages = queryset.filter(Q(created_at__lte=mes.created_at))
                readed_messages = messages.update(is_readed=True)
                mes.is_readed = True

                if readed_messages == unreaded_message_count:
                    unread_chats_count -= 1

                data = MessageSerializer(instance=mes).data
                data.update({'unreadChatsCount': unread_chats_count})

                return None


    @database_sync_to_async
    def _check_permissions(self):
        if isinstance(self.user, AnonymousUser):
            return False
        chat = Chat.objects.filter(pk=self.chat_id, members=self.user).first()
        if chat:
            return True
        else:
            return False
