from django.test import TestCase
from channels.testing import HttpCommunicator
from Chats.consumers import ChatConsumer


#
# class MyTests(TestCase):
#     async def test_my_consumer(self):
#         communicator = HttpCommunicator(ChatConsumer.as_asgi(), "GET", "/ws/chat/s/")
#         response = await communicator.get_response()
#         self.assertEqual(response["body"], b"test response")
#         self.assertEqual(response["status"], 200)