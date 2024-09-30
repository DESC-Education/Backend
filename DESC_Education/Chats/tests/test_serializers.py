import random
from django.utils import timezone
from django.test import TestCase
from rest_framework import serializers
from django.http.request import HttpRequest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
from Chats.serializers import (
    ChatSerializer,
    ChatListSerializer,
    ChatDetailSerializer,
    SendFileSerializer,
    CompanionSerializer,
    MessageSerializer
)
from Files.models import File
import json
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
    Chat,
    Message
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
            category=TaskCategory.objects.first(), )

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

    def test_duplicate(self):
        serializer = ChatSerializer(data={
            "companionId": str(self.student.id),
            "taskId": str(self.task.id)
        })
        req = HttpRequest()
        req.user = self.company
        serializer.context['request'] = req
        serializer.is_valid()
        instance = serializer.save(user=self.company)
        instance2 = serializer.save(user=self.company)
        self.assertEqual(instance2.id, instance.id)
        self.assertEqual(len(Chat.objects.all()), 1)

    def test_duplicate_with_another_task(self):
        serializer = ChatSerializer(data={
            "companionId": str(self.student.id),
            "taskId": str(self.task.id)
        })
        req = HttpRequest()
        req.user = self.company
        serializer.context['request'] = req
        serializer.is_valid()
        instance = serializer.save(user=self.company)

        serializer2 = ChatSerializer(data={
            "companionId": str(self.student.id)
        })
        req = HttpRequest()
        req.user = self.company
        serializer2.context['request'] = req
        serializer2.is_valid()
        instance2 = serializer2.save(user=self.company)

        self.assertEqual(len(Chat.objects.all()), 2)

        serializer3 = ChatSerializer(data={
            "companionId": str(self.student.id)
        })
        req = HttpRequest()
        req.user = self.company
        serializer3.context['request'] = req
        serializer3.is_valid()
        instance3 = serializer3.save(user=self.company)

        self.assertEqual(instance3, instance2)
        self.assertEqual(len(Chat.objects.all()), 2)

        serializer4 = ChatSerializer(data={
            "companionId": str(self.company.id),
            "taskId": str(self.task.id)
        })
        req = HttpRequest()
        req.user = self.student
        serializer4.context['request'] = req
        serializer4.is_valid()
        instance4 = serializer4.save(user=self.company)

        self.assertEqual(instance, instance4)
        self.assertEqual(len(Chat.objects.all()), 2)








class ChatListSerializerTest(TestCase):
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
        Message.objects.create(chat=self.chat, user=self.student, message='Первое')
        self.mes1 = Message.objects.create(chat=self.chat, user=self.company, message='Последнее')

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

    def test_serializer_data(self):
        queryset = Chat.objects.all()
        req = HttpRequest()
        req.user = self.student
        context = {'request': req}
        serializer = ChatListSerializer(queryset, many=True, context=context)
        data = serializer.data
        data[0]['companion'] = dict(data[0]['companion'])
        data[0]['lastMessage'] = dict(data[0]['lastMessage'])
        data[1]['companion'] = dict(data[1]['companion'])
        data[1]['lastMessage'] = dict(data[1]['lastMessage'])

        self.assertEqual(list(serializer.data), [
            {
                'id': str(self.chat.id),
                'task': None,
                'companion': {'id': str(self.company.id), 'name': '', 'avatar': None},
                'lastMessage': {'message': 'Последнее', 'createdAt': self.mes1.created_at.isoformat(),
                                'isRead': False, 'user': {'id': str(self.company.id), 'name': '', 'avatar': None},
                                'id': str(self.mes1.id), 'files': []}},
            {
                'id': str(self.chat2.id),
                'task': None,
                'companion': {'id': str(self.company2.id), 'name': '', 'avatar': None},
                'lastMessage': {'message': 'Последнее второе', 'createdAt': self.mes2.created_at.isoformat(),
                                'isRead': False, 'user': {'id': str(self.student.id), 'name': ' ', 'avatar': None},
                                'id': str(self.mes2.id), 'files': []}}])


class ChatDetailSerializerTest(TestCase):
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

        self.mes_0 = Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')
        self.mes_1 = Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')
        self.mes = Message.objects.create(chat=self.chat, user=self.company, message='Третье')
        for mes in range(49):
            Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')
        self.mes1 = Message.objects.create(chat=self.chat, user=self.company, message='Пятидесятое')
        self.mes2 = Message.objects.create(chat=self.chat, user=self.company, message='пятдесят первое')
        for mes in range(49):
            Message.objects.create(chat=self.chat, user=self.student, message=f'{random.randint(1, 99999999)}')

    def test_serializer(self):
        req = HttpRequest()
        req.user = self.student
        req.query_params = {'messageId': str(self.mes.id)}
        # req.query_params = {}
        context = {'request': req}

        serializer = ChatDetailSerializer(self.chat, context=context)

        res = dict(serializer.data)
        res['messages'] = list(res['messages'])
        for i, k in enumerate(res['messages']):
            res['messages'][i] = dict(k)

        self.assertEqual(res, {
            'companion': {'id': str(self.company.id), 'name': '', 'avatar': None},
            'messages': [{'createdAt': self.mes_1.created_at.isoformat(),
                          'isRead': False,
                          'message': self.mes_1.message,
                          'files': [],
                          'user': {'avatar': None,
                                   'id': str(self.student.id),
                                   'name': ' '},
                          'id': str(self.mes_1.id)},
                         {'createdAt': self.mes_0.created_at.isoformat(),
                          'isRead': False,
                          'message': self.mes_0.message,
                          'files': [],
                          'user': {'avatar': None,
                                   'id': str(self.student.id),
                                   'name': ' '},
                          'id': str(self.mes_0.id)}],
            'task': None})


class SendFileSerializerTest(TestCase):
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

        self.company2 = CustomUser.objects.create_user(
            email='example1232@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student)
        ChatMembers.objects.create(chat=self.chat, user=self.company)

    def test_validation(self):
        req = HttpRequest()
        req.user = self.student
        context = {'request': req}
        serializer = SendFileSerializer(context=context, data={
            'file': SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            'chat': str(self.chat.id)
        })

        self.assertTrue(serializer.is_valid())
        instance = serializer.save(
            type=File.CHAT_FILE
        )
        file = File.objects.all().first()
        self.assertEqual(file, instance)
        self.assertEqual(str(instance), f'chats/{self.chat.id}/test.jpg')
        self.assertEqual(serializer.data, {
            'id': str(file.id),
            'size': file.file.size,
            'name': 'test',
            'extension': 'jpg',
            'path': f'/api/media/chats/{str(self.chat.id)}/test.jpg'})



class CompanionSerializerTest(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)

        self.profile = self.student.get_profile()
        self.profile.logo_img = SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg")
        self.profile.save()

    def test_serialize(self):
        res = CompanionSerializer(instance=self.student).data

        self.assertEqual(dict(res), {
            'id': str(self.student.id),
            'name': str(self.student.get_full_name()),
            'avatar': f'/api/media/{self.profile.logo_img.name}'
        })


class MessageSerializerTest(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)
        self.chat = Chat.objects.create()
        self.mes = Message.objects.create(
            chat_id=self.chat.id,
            user_id=self.student.id,
            message='123'
        )
        self.file = File.objects.create(
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            content_object=self.chat,
            type=File.CHAT_FILE
        )
        self.file2 = File.objects.create(
            file=SimpleUploadedFile(name="test2.jpg", content=b"file_content", content_type="image/jpeg"),
            content_object=self.chat,
            type=File.CHAT_FILE
        )


    def test_serialize(self):
        self.file.content_object = self.mes
        self.file.save()
        self.file2.content_object = self.mes
        self.file2.save()



        res = MessageSerializer(instance=self.mes).data

        self.assertEqual(dict(res),
                         {'id': str(self.mes.id),
                          'message': '123',
                          'user': {'id': str(self.student.id),
                                   'name': ' ',
                                   'avatar': None},
                          'createdAt': self.mes.created_at.isoformat(),
                          'isRead': False,
                          'files': [
                              {'id': str(self.file.id),
                               'size': 12,
                               'name': 'test',
                               'extension': 'jpg',
                               'path': f'/api/media/chats/{str(self.chat.id)}/test.jpg'},
                              {'id': str(self.file2.id),
                               'size': 12,
                               'name': 'test2',
                               'extension': 'jpg',
                               'path': f'/api/media/chats/{str(self.chat.id)}/test2.jpg'}]})




