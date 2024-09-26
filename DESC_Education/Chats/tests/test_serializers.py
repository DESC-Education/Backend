import random
from django.utils import timezone
from django.test import TestCase
from rest_framework import serializers
from django.http.request import HttpRequest
from Chats.serializers import (
    ChatSerializer
)
from Users.models import (
    CustomUser
)
from Tasks.models import (
    Task,
    TaskCategory,
    Solution
)

from Chats.models import (
    ChatMembers,
    Chat
)

class CreateChatSerializerTest(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)

        self.student2 = CustomUser.objects.create_user(
            email='example123@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)

        self.company = CustomUser.objects.create_user(
            email='example2@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.task = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Description",
            deadline=timezone.now() + timezone.timedelta(days=2),
            category=TaskCategory.objects.first(),)

        self.company2 = CustomUser.objects.create_user(
            email='example22@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.task2 = Task.objects.create(
            user=self.company2,
            title="Test Task2",
            description="Test Description2",
            deadline=timezone.now() + timezone.timedelta(days=2),
            category=TaskCategory.objects.first(), )

    def test_serializer_data(self):
        serializer = ChatSerializer(data={
            "companionId": str(self.student.id),
            "taskId": str(self.task.id)
        })
        req = HttpRequest()
        req.user = self.company
        serializer.context['request'] = req
        serializer.is_valid()
        instance = serializer.save(user=self.company)
        members = instance.chatmembers_set.all()

        self.assertEqual(len(members), len((ChatMembers.objects.filter(chat=instance))))
        self.assertEqual(dict(serializer.data), {
            "id": str(instance.id),
            "companion": {
                "id": str(self.student.id),
                "name": self.student.get_full_name(),
                "avatar": None
            },
            "task": {
                "id": str(self.task.id),
                "title": "Test Task",
            }
        })


    def test_validate_student_empty_task_field(self):
        serializer = ChatSerializer(data={
            "companionId": str(self.student2.id),
        })
        req = HttpRequest()
        req.user = self.student
        serializer.context['request'] = req
        serializer.is_valid()
        self.assertEqual(str(serializer.errors.get('taskId')[0]), 'Это поле обязательно!')

    def test_validate_student_wrong_taskId(self):
        serializer = ChatSerializer(data={
            "companionId": str(self.student2.id),
            'taskId': str(self.task.id)
        })
        req = HttpRequest()
        req.user = self.student
        serializer.context['request'] = req
        serializer.is_valid()
        self.assertEqual(str(serializer.errors.get('taskId')[0]), 'Это поле несоответствует вашему собеседнику!')

    def test_validate_company_to_company(self):
        serializer = ChatSerializer(data={
            "companionId": str(self.company2.id),
            'taskId': str(self.task.id)
        })
        req = HttpRequest()
        req.user = self.company
        serializer.context['request'] = req
        serializer.is_valid()
        self.assertEqual(str(serializer.errors.get('companionId')[0]), 'Вы не можете добавлять компанию в чат!')




