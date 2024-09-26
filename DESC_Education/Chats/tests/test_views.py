from django.utils import timezone
from rest_framework.test import APITestCase
from django.urls import reverse
from Tasks.models import TaskCategory, Task
from Users.models import CustomUser
from Profiles.models import StudentProfile
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
        res = self.client.get(reverse('chat_list'), HTTP_AUTHORIZATION=f'Bearer {self.student.get_token()["accessToken"]}')


        data = res.data.get('results')
        self.assertEqual(data[0].get('id'), str(self.chat2.id))
        self.assertEqual(data[0].get('companion').get('id'), str(self.company2.id))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 2)
