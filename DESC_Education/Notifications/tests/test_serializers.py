from django.test import TestCase
from Notifications.serializers import MessageNotificationSerializer
from Users.models import CustomUser
from Chats.models import Chat, ChatMembers, Message




class MessageNotificationSerializerTest(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)

        self.company = CustomUser.objects.create_user(
            email='example123@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student)
        ChatMembers.objects.create(chat=self.chat, user=self.company)
        self.mes = Message.objects.create(chat=self.chat, user=self.student, message='Первое')

        self.chat2 = Chat.objects.create()
        self.chat3 = Chat.objects.create()
        self.chat4 = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat2, user=self.company)
        ChatMembers.objects.create(chat=self.chat2, user=self.student)
        Message.objects.create(chat=self.chat2, user=self.company, message='Первое')
        Message.objects.create(chat=self.chat2, user=self.student, message='Первое')
        Message.objects.create(chat=self.chat2, user=self.student, message='Первое')
        Message.objects.create(chat=self.chat2, user=self.student, message='Первое')
        ChatMembers.objects.create(chat=self.chat3, user=self.company)
        Message.objects.create(chat=self.chat3, user=self.company, message='Первое')
        ChatMembers.objects.create(chat=self.chat4, user=self.company)
        Message.objects.create(chat=self.chat4, user=self.company, message='Первое')


    def test_serialization(self):
        serializer = MessageNotificationSerializer(self.mes, data={"user": self.company.id})
        self.assertTrue(serializer.is_valid())

        self.assertEqual(dict(serializer.data), {'chat': self.chat.id,
                                                 'message': 'Первое',
                                                 'createdAt': self.mes.created_at.isoformat(),
                                                 'unreadChatsCount': 2,
                                                 'unreadCount': 1})

