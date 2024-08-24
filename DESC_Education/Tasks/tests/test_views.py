import random

import rest_framework.generics
from django.urls import reverse
import json
from django.utils import timezone
from rest_framework.test import APITestCase
import uuid
from Users.models import CustomUser
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from Tasks.models import (
    Task
)

from Tasks.serializers import (
    TaskSerializer
)



class TaskViewTest(APITestCase):
    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile(f"test_{random.randint(1, 25)}.jpg", bts.getvalue())

    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE
        )
        self.student_token = self.student.get_token()['accessToken']

        self.company = CustomUser.objects.create_user(
            email='exampl2e2@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE
        )
        self.company_token = self.company.get_token()['accessToken']


        self.example_data = {
            "title": "Test Task",
            "description": "Test Task Description",
            "deadline": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            'file': self.create_test_image()
        }



    def test_student_403(self):
        res = self.client.post(reverse('task'),
                               self.example_data,
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token)

        self.assertEqual(json.loads(res.content), {'detail': "У вас недостаточно прав для выполнения данного действия."})
        self.assertEqual(res.status_code, 403)


    def test_create_task_200(self):
        res = self.client.post(reverse('task'),
                               self.example_data,
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)


        expected_data = TaskSerializer(data=self.example_data, instance=Task.objects.first())
        expected_data.user = str(self.company.id)
        expected_data.is_valid()

        res_data = json.loads(res.content).get('data').get('task')
        res_data['user'] = uuid.UUID(res_data.get('user'))

        self.assertEqual(res_data, dict(expected_data.data))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('message'), 'Задача добавлена успешно')

