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
    Task,
    TaskCategory,
    FilterCategory,
    Filter
)

from Tasks.serializers import (
    TaskSerializer,
    TaskCategorySerializer
)


class TaskViewTest(APITestCase):
    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile(f"test_{random.randint(1, 25)}.jpg", bts.getvalue())

    def get_expected_data(self, task):
        expected_data = TaskSerializer(data=self.example_data, instance=task)
        expected_data.user = str(self.company.id)
        expected_data.is_valid()
        expected_data = dict(expected_data.data)

        return expected_data


    def setUp(self):
        self.maxDiff = None
        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE
        )
        self.student_token = self.student.get_token()['accessToken']


        self.another_company = CustomUser.objects.create_user(
            email='exampl3e@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE
        )
        self.another_company_token = self.another_company.get_token()['accessToken']
        self.company = CustomUser.objects.create_user(
            email='exampl2e2@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE
        )
        self.company_token = self.company.get_token()['accessToken']


        task_category = TaskCategory.objects.first()
        filter_category: FilterCategory = FilterCategory.objects.create(
            name="Языки прогрмирования",
        )
        filter_category.task_category.add(task_category)
        filter_python: Filter = Filter.objects.create(
            name="Python",
            filter_category=filter_category
        )

        self.example_data = {
            "title": "Test Task",
            "description": "Test Task Description",
            "deadline": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            'file': self.create_test_image(),
            'category': task_category.id,
            'filters': [filter_python.id, ]

        }

    def test_student_403(self):
        res = self.client.post(reverse('task'),
                               self.example_data,
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token)

        self.assertEqual(json.loads(res.content),
                         {'detail': "У вас недостаточно прав для выполнения данного действия."})
        self.assertEqual(res.status_code, 403)

    def test_create_task_200(self):
        res = self.client.post(reverse('task'),
                               self.example_data,
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)

        import pprint
        pprint.pprint(dict(res.data))

        task = Task.objects.first()

        expected_data = self.get_expected_data(task)

        res_data = json.loads(res.content)

        res_data['user'] = uuid.UUID(res_data.get('user'))

        self.assertEqual(res_data, expected_data)
        self.assertEqual(res.status_code, 200)

    def test_edit_task_another_user_400(self):
        self.test_create_task_200()
        task = Task.objects.first()

        another_company_put = self.client.patch(reverse('task_edit',
                                                        kwargs={'pk': task.id}),
                                                {'title': "new Title"},
                                                HTTP_AUTHORIZATION='Bearer ' + self.another_company_token)
        self.assertEqual(another_company_put.data.get('message'),
                         'У вас недостаточно прав для выполнения данного действия.')
        self.assertEqual(another_company_put.status_code, 400)



    def test_edit_task_200(self):
        self.test_create_task_200()
        task = Task.objects.first()


        test_put = self.client.patch(reverse('task_edit',
                                             kwargs={'pk': task.id}),
                                     {'title': "new Title"},
                                     HTTP_AUTHORIZATION='Bearer ' + self.company_token, )

        put_res = json.loads(test_put.content)
        put_res['user'] = uuid.UUID(put_res.get('user'))

        expected_data = self.get_expected_data(task)
        expected_data['title'] = 'new Title'
        self.assertEqual(put_res, expected_data)
        self.assertEqual(test_put.status_code, 200)


