from django.test import TestCase, TransactionTestCase
from channels.testing import WebsocketCommunicator
from Chats.consumers import ChatConsumer
from Users.models import CustomUser
from Chats.models import Chat, ChatMembers, Message
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, include
from Settings.middlewares import JwtAuthMiddlewareStack
from channels.db import database_sync_to_async
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from Chats.serializers import MessageSerializer
from Files.models import File


class MyTests(TransactionTestCase):
    def setUp(self) -> None:
        self.student = CustomUser.objects.create_user(
            email='test@example.com',
            password='123',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True,
        )
        self.student_token = self.student.get_token()['accessToken']

        self.company = CustomUser.objects.create_user(
            email='test2@example.com',
            password='123',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True,
        )
        self.company_token = self.company.get_token()['accessToken']

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student)
        ChatMembers.objects.create(chat=self.chat, user=self.company)

        Message.objects.create(chat=self.chat, user=self.company, message="123")
        self.mes = Message.objects.create(chat=self.chat, user=self.company, message="123")


        self.file_1 = File.objects.create(
            content_object=self.chat,
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            type=File.CHAT_FILE,
        )
        self.file_2 = File.objects.create(
            content_object=self.chat,
            file=SimpleUploadedFile(name="test2.jpg", content=b"file_content", content_type="image/jpeg"),
            type=File.CHAT_FILE,
        )

    @database_sync_to_async
    def compare_message(self, res):
        mess = Message.objects.all().last()
        serializer = dict(MessageSerializer(instance=mess).data)

        self.assertEqual(serializer, dict(res))
        return mess

    async def test_send_message(self):
        application = JwtAuthMiddlewareStack(URLRouter([
            path("ws/chat/<room_id>/", ChatConsumer.as_asgi()),
        ]))
        communicator = WebsocketCommunicator(application, f"/ws/chat/{self.chat.id}/?token={self.student_token}")
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({"payload": {"message": "hello"},
                                         "type": "message"})
        message = json.loads(await communicator.receive_from())
        payload = json.loads(message.get('payload'))

        await self.compare_message(payload)
        self.assertEqual(payload.get('message'), 'hello')


        await communicator.send_json_to({"payload": {"message": "hello",
                                                     'files': [str(self.file_1.id), str(self.file_2.id)]},
                                         "type": "message"})
        message = json.loads(await communicator.receive_from())
        payload = json.loads(message.get('payload'))

        mes = await self.compare_message(payload)
        self.assertEqual(payload.get('message'), 'hello')
        self.assertEqual(len(payload.get('files')), 2)


        await communicator.send_json_to({"payload": str(self.mes.id),
                                         "type": "viewed"})
        message = json.loads(await communicator.receive_from())
        payload = json.loads(message.get('payload'))

        self.assertEqual(payload.get('unreadChatsCount'), 1)
        self.assertTrue(payload.get('isRead'))


        await communicator.disconnect()



