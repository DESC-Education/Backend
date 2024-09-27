from django.utils import timezone
from rest_framework.test import APITestCase
from django.urls import reverse
from Tasks.models import TaskCategory, Task
from Users.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile
from Profiles.models import StudentProfile
import random
from Chats.models import (
    Chat,
    Message,
    ChatMembers
)


class CreateChatViewTest(APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.student = CustomUser.objects.create_user(
            email="example1@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.company = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.company2 = CustomUser.objects.create_user(
            email="example22@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company2.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.student_token = self.student.get_token()['accessToken']
        self.company_token = self.company.get_token()['accessToken']

        self.task = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Description",
            deadline=timezone.now() + timezone.timedelta(days=2),
            category=TaskCategory.objects.first(), )

    def test_create_chat_student(self):
        res = self.client.post(reverse('chat_create'), {
            'companionId': str(self.company.id),
            'taskId': str(self.task.id)
        }, HTTP_AUTHORIZATION=f'Bearer {self.student_token}')

        self.assertEqual(res.status_code, 201)

    def test_create_chat_company(self):
        res = self.client.post(reverse('chat_create'), {
            'companionId': str(self.student.id),

        }, HTTP_AUTHORIZATION=f'Bearer {self.company_token}')

        self.assertEqual(res.status_code, 201)

    def test_create_chat_company_to_company(self):
        res = self.client.post(reverse('chat_create'), {
            'companionId': str(self.company2.id),

        }, HTTP_AUTHORIZATION=f'Bearer {self.company_token}')

        self.assertEqual(res.status_code, 400)

    def test_create_chat_student_without_task(self):
        res = self.client.post(reverse('chat_create'), {
            'companionId': str(self.company.id),

        }, HTTP_AUTHORIZATION=f'Bearer {self.student_token}')

        self.assertEqual(res.status_code, 400)

    def test_create_chat_student_wrong_task(self):
        res = self.client.post(reverse('chat_create'), {
            'companionId': str(self.company2.id),
            'taskId': str(self.task.id)

        }, HTTP_AUTHORIZATION=f'Bearer {self.student_token}')

        self.assertEqual(res.status_code, 400)


class ChatListViewTest(APITestCase):
    def setUp(self):
        self.maxDiff = None

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.company = CustomUser.objects.create_user(
            email='example123@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student)
        ChatMembers.objects.create(chat=self.chat, user=self.company)
        Message.objects.create(chat=self.chat, user=self.student, message='Первое')
        self.mes1 = Message.objects.create(chat=self.chat, user=self.student, message='Последнее')

        self.company2 = CustomUser.objects.create_user(
            email='123@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.chat2 = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat2, user=self.student)
        ChatMembers.objects.create(chat=self.chat2, user=self.company2)
        Message.objects.create(chat=self.chat2, user=self.student, message='Первое второе')
        self.mes2 = Message.objects.create(chat=self.chat2, user=self.student, message='Последнее второе')

    def test_200(self):
        res = self.client.get(reverse('chat_list'),
                              HTTP_AUTHORIZATION=f'Bearer {self.student.get_token()["accessToken"]}')

        data = res.data.get('results')
        self.assertEqual(data[0].get('id'), str(self.chat2.id))
        self.assertEqual(data[0].get('companion').get('id'), str(self.company2.id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 2)


class ChatDetailViewTest(APITestCase):
    def setUp(self):
        self.maxDiff = None

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.company = CustomUser.objects.create_user(
            email='example123@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student)
        ChatMembers.objects.create(chat=self.chat, user=self.company)

        self.mes_0 = Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')
        self.mes_1 = Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')
        self.mes = Message.objects.create(chat=self.chat, user=self.company, message='Третье')
        for mes in range(49):
            Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')
        self.mes1 = Message.objects.create(chat=self.chat, user=self.company, message='Пятидесятое')
        self.mes2 = Message.objects.create(chat=self.chat, user=self.company, message='пятдесят первое')
        for mes in range(48):
            Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')
        self.mes3 = Message.objects.create(chat=self.chat, user=self.company, message='последнее')

    def test_200(self):
        res = self.client.get(reverse('chat_detail', kwargs={'pk': self.chat.id}),
                              HTTP_AUTHORIZATION=f'Bearer {self.student.get_token()["accessToken"]}')

        data = res.data.get('messages')
        self.assertEqual(len(data), 50)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data[0].get('id'), str(self.mes3.id))
        self.assertEqual(data[49].get('id'), str(self.mes2.id))

    def test_offset_200(self):
        res = self.client.get(reverse('chat_detail', kwargs={'pk': self.chat.id}), {'messageId': str(self.mes.id)},
                               HTTP_AUTHORIZATION=f'Bearer {self.student.get_token()["accessToken"]}')

        data = res.data.get('messages')
        self.assertEqual(len(data), 2)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data[0].get('id'), str(self.mes_1.id))
        self.assertEqual(data[-1].get('id'), str(self.mes_0.id))

class SendFileViewTest(APITestCase):
    def setUp(self):
        self.maxDiff = None

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.company = CustomUser.objects.create_user(
            email='example123@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student)
        ChatMembers.objects.create(chat=self.chat, user=self.company)


    def test_200(self):
        res = self.client.post(reverse('send_file'), {
            "file": SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            'chat': str(self.chat.id)
        }, HTTP_AUTHORIZATION=f'Bearer {self.student.get_token()["accessToken"]}')

        self.assertEqual(dict(res.data), {'name': 'test', 'extension': 'jpg', 'path': f'chats/{str(self.chat.id)}/test.jpg'})
        self.assertEqual(res.status_code, 201)
