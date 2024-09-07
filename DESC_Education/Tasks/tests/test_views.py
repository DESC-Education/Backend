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
from Profiles.models import (
    StudentProfile
)
from Tasks.models import (
    Task,
    TaskCategory,
    FilterCategory,
    Filter,
    Solution
)

from Tasks.serializers import (
    TaskSerializer,
    TaskCategorySerializer,
    TaskCategoryWithFiltersSerializer,
    SolutionSerializer,
    FilterCategorySerializer,
    CompanyTasksMySerializer,
    TaskListSerializer,
    StudentTasksMySerializer,
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
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.student_token = self.student.get_token()['accessToken']

        self.another_company = CustomUser.objects.create_user(
            email='exampl3e@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.another_company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.another_company_token = self.another_company.get_token()['accessToken']
        self.company = CustomUser.objects.create_user(
            email='exampl2e2@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.company_token = self.company.get_token()['accessToken']

        task_category = TaskCategory.objects.first()
        filter_category: FilterCategory = FilterCategory.objects.create(
            name="Языки прогрмирования",
        )
        task_category.filter_categories.add(filter_category)
        filter_python: Filter = Filter.objects.create(
            name="Python",
            filter_category=filter_category
        )

        self.example_data = {
            "title": "Test Task",
            "description": "Test Task Description",
            "deadline": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            'file': self.create_test_image(),
            'categoryId': task_category.id,
            'filters': [filter_python.id, ]

        }

    def test_student_403(self):
        res = self.client.post(reverse('task'),
                               self.example_data,
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token)

        self.assertEqual(json.loads(res.content),
                         {'detail': "Только для компаний!"})
        self.assertEqual(res.status_code, 403)

    def test_create_task_200(self):
        res = self.client.post(reverse('task'),
                               self.example_data,
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)
        task = Task.objects.first()

        expected_data = self.get_expected_data(task)

        res_data = json.loads(res.content)

        res_data['user'] = uuid.UUID(res_data.get('user'))

        self.assertEqual(res_data, expected_data)
        self.assertEqual(res.status_code, 200)

    def test_edit_task_another_user_400(self):
        self.test_create_task_200()
        task = Task.objects.first()

        another_company_put = self.client.patch(reverse('task_detail',
                                                        kwargs={'pk': task.id}),
                                                {'title': "new Title"},
                                                HTTP_AUTHORIZATION='Bearer ' + self.another_company_token)
        self.assertEqual(another_company_put.data.get('message'),
                         'К изменению доступны объекты созданые только вами')
        self.assertEqual(another_company_put.status_code, 400)

    def test_edit_task_200(self):
        self.test_create_task_200()
        task = Task.objects.first()

        test_put = self.client.patch(reverse('task_detail',
                                             kwargs={'pk': task.id}),
                                     {'title': "new Title"},
                                     HTTP_AUTHORIZATION='Bearer ' + self.company_token, )

        put_res = json.loads(test_put.content)
        put_res['user'] = uuid.UUID(put_res.get('user'))

        expected_data = self.get_expected_data(task)
        expected_data['title'] = 'new Title'
        self.assertEqual(put_res, expected_data)
        self.assertEqual(test_put.status_code, 200)


class TaskListViewTest(APITestCase):
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
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.student_token = self.student.get_token()['accessToken']

        self.another_company = CustomUser.objects.create_user(
            email='exampl3e@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.another_company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.another_company_token = self.another_company.get_token()['accessToken']
        self.company = CustomUser.objects.create_user(
            email='exampl2e2@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.company_token = self.company.get_token()['accessToken']

        task_category = TaskCategory.objects.first()
        filter_category: FilterCategory = FilterCategory.objects.create(
            name="Языки прогрмирования",
        )
        task_category.filter_categories.add(filter_category)
        filter_python: Filter = Filter.objects.create(
            name="Python",
            filter_category=filter_category
        )

        self.example_data = {
            "user": self.company,
            "title": "Test Task",
            "description": "Test Task Description",
            "deadline": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            'file': self.create_test_image(),
            'category': task_category,

        }

        self.task = Task.objects.create(**self.example_data)

    def test_get(self):
        res = self.client.get(reverse('get_tasks'))

        expected_data = TaskListSerializer(instance=self.task)

        self.assertEqual(dict(res.data).get('results')[0], dict(expected_data.data))

class TaskDetailViewTest(APITestCase):

    def get_expected_data(self, task):
        expected_data = TaskSerializer(data=self.example_data, instance=task)
        expected_data.user = str(self.company.id)
        expected_data.is_valid(raise_exception=True)
        expected_data = dict(expected_data.data)

        return expected_data

    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile(f"test_{random.randint(1, 25)}.jpg", bts.getvalue())

    def setUp(self):
        self.maxDiff = None
        self.company = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.company_token = self.company.get_token()['accessToken']

        self.example_data = {
            "title": "Test Task",
            "description": "Test Task Description",
            "deadline": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            'file': self.create_test_image(),
            "categoryId": TaskCategory.objects.first().id
        }
        self.task = Task.objects.create(
            user=self.company,
            title=self.example_data['title'],
            description=self.example_data['description'],
            deadline=self.example_data['deadline'],
            file=self.example_data['file'],
            category=TaskCategory.objects.first()
        )

    def test_get_200(self):
        res = self.client.get(reverse('task_detail', kwargs={'pk': self.task.id}),
                              HTTP_AUTHORIZATION=f'Bearer {self.company_token}')

        task = Task.objects.first()
        expected_data = self.get_expected_data(task)

        self.assertEqual(dict(res.data), expected_data)
        self.assertEqual(res.status_code, 200)

    def test_get_400(self):
        task_id = list(str(self.task.id))
        t = task_id[-1]
        task_id[-1] = task_id[0]
        task_id[0] = t
        task_id[1] = 0
        task_id[2] = 0
        task_id[3] = 0
        task_id = ''.join(task_id)

        res = self.client.get(reverse('task_detail', kwargs={'pk': task_id}),
                              HTTP_AUTHORIZATION=f'Bearer {self.company_token}')

        self.assertEqual(dict(res.data), {'detail': 'No Task matches the given query.'})
        self.assertEqual(res.status_code, 404)


class TestSolutionView(APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.company = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        self.task = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Task Description",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first()
        )

        self.student: CustomUser = CustomUser.objects.create_user(
            email='student@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )

        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.student_token = self.student.get_token()['accessToken']

        self.example_data = {
            'taskId': self.task.id,
            'description': "Test Task Description",
            'file': SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg")
        }

    def get_expected_data(self, solution):
        example_data = self.example_data.copy()
        expected_data = SolutionSerializer(instance=solution, data=example_data)
        expected_data.is_valid()

        return dict(expected_data.data)

    def test_create_solution(self):
        res = self.client.post(reverse('solution'),
                               self.example_data,
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token,
                               )
        solution = Solution.objects.first()
        profile: StudentProfile = StudentProfile.objects.get(user=self.student)

        expected_data = self.get_expected_data(solution)
        self.assertEqual(dict(res.data), expected_data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(profile.reply_count, profile.REPLY_MONTH_COUNT - 1)


class TaskCategoryListViewTest(APITestCase):
    def setUp(self):
        TaskCategory.objects.all().delete()
        self.category1: TaskCategory = TaskCategory.objects.create(name='Web')
        self.category2 = TaskCategory.objects.create(name='Phone')
        self.category3 = TaskCategory.objects.create(name='Node')
        self.category4 = TaskCategory.objects.create(name='Design')

        filter_category = FilterCategory.objects.create(name='FilterCategory')
        filter_category2 = FilterCategory.objects.create(name='FilterCategory2')
        self.category1.filter_categories.add(filter_category)
        self.category1.filter_categories.add(filter_category2)

        filter = Filter.objects.create(name='example_filter', filter_category=filter_category)

    def test_get_categories(self):
        res = self.client.get(reverse('task_category_list'))

        categories = TaskCategory.objects.all().prefetch_related('filter_categories__filters')
        expected_data = TaskCategoryWithFiltersSerializer(categories, many=True)
        self.assertEqual(dict(res.data).get('results'), expected_data.data)
        self.assertEqual(res.status_code, 200)

    def get_category_by_name(self):
        res = self.client.get(reverse('task_category_detail'), {'search': "pyt"})
        self.assertEqual(dict(res.data).get('results'), {'id': str(self.category2.id), 'name': self.category2.name})
        self.assertEqual(res.status_code, 200)

    def get_category_by_name2(self):
        res = self.client.get(reverse('task_category_detail'), {'search': "o"})
        self.assertEqual(dict(res.data).get('results'), [{'id': str(self.category2.id), 'name': self.category2.name},
                                                         {'id': str(self.category3.id), 'name': self.category3.name}])
        self.assertEqual(res.status_code, 200)


class CompanyTasksMyViewTest(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='example2@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.student_token = self.student.get_token()['accessToken']

        self.company = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()
        self.company_token = self.company.get_token()['accessToken']

        self.task_1 = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Task Description",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_1.filters.set([Filter.objects.first()])

        self.task_2: Task = Task.objects.create(
            user=self.company,
            title="Test Task2",
            description="Test Task Description",
            deadline=(timezone.now() + timezone.timedelta(days=2)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_2.filters.set([Filter.objects.first()])

        self.task_3 = Task.objects.create(
            user=self.company,
            title="Test Task3",
            description="Test Task Description",
            deadline=(timezone.now() - timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_3.filters.set([Filter.objects.first()])

        self.task_4 = Task.objects.create(
            user=self.company,
            title="Test Task4",
            description="Test Task Description",
            deadline=(timezone.now() - timezone.timedelta(days=2)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_2.filters.set([Filter.objects.first()])

    def test_get_200(self):
        res = self.client.get(reverse('company_tasks_my'),
                              HTTP_AUTHORIZATION=f'Bearer {self.company_token}')

        serializer = CompanyTasksMySerializer()
        self.assertEqual(dict(res.data),
                         serializer.to_representation(Task.objects.all()))
        self.assertEqual(res.status_code, 200)

    def test_get_student(self):
        res = self.client.get(reverse('company_tasks_my'),
                              HTTP_AUTHORIZATION=f'Bearer {self.student_token}')

        self.assertEqual(dict(res.data), {'detail': 'Только для компаний!'})
        self.assertEqual(res.status_code, 403)


class StudentTasksMyViewTest(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='example2@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.student_token = self.student.get_token()['accessToken']

        self.company = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.company_token = self.company.get_token()['accessToken']

        self.task_1 = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Task Description",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_1.filters.set([Filter.objects.first()])

        self.task_2: Task = Task.objects.create(
            user=self.company,
            title="Test Task2",
            description="Test Task Description",
            deadline=(timezone.now() + timezone.timedelta(days=2)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_2.filters.set([Filter.objects.first()])

        self.task_3 = Task.objects.create(
            user=self.company,
            title="Test Task3",
            description="Test Task Description",
            deadline=(timezone.now() - timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_3.filters.set([Filter.objects.first()])

        self.task_4 = Task.objects.create(
            user=self.company,
            title="Test Task4",
            description="Test Task Description",
            deadline=(timezone.now() - timezone.timedelta(days=2)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_4.filters.set([Filter.objects.first()])

        solution = Solution.objects.create(
            task=self.task_1,
            user=self.student,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            status=Solution.COMPLETED,
        )

        solution2 = Solution.objects.create(
            task=self.task_4,
            user=self.student,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            status=Solution.PENDING,
        )

        solution3 = Solution.objects.create(
            task=self.task_2,
            user=self.student,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            status=Solution.PENDING,
        )

    def test_get_200(self):
        res = self.client.get(reverse('student_tasks_my'),
                              HTTP_AUTHORIZATION=f'Bearer {self.student_token}')

        serializer = StudentTasksMySerializer()
        self.assertEqual(dict(res.data),
                         serializer.to_representation(Solution.objects.all()))
        self.assertEqual(res.status_code, 200)

    def test_get_company(self):
        res = self.client.get(reverse('student_tasks_my'),
                              HTTP_AUTHORIZATION=f'Bearer {self.company_token}')

        self.assertEqual(dict(res.data), {'detail': 'Только для студентов!'})
        self.assertEqual(res.status_code, 403)


class EvaluateSolutionViewTest(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='example2@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        profile = self.student.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.student_token = self.student.get_token()['accessToken']

        self.company = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.company_token = self.company.get_token()['accessToken']

        self.task_1 = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Task Description",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_1.filters.set([Filter.objects.first()])

        self.solution = Solution.objects.create(
            task=self.task_1,
            user=self.student,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            description="Test Solution Description",
        )

    def test_evaluate_solution(self):
        res = self.client.post((reverse('task_evaluate', kwargs={"pk": self.solution.id})),
                               {
                                   'status': "completed",
                                   'companyComment': "Test Comment",
                               },
                               HTTP_AUTHORIZATION=f'Bearer {self.company_token}')

        solution: Solution = Solution.objects.first()


        self.assertEqual(res.data, {'status': 'completed'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(solution.status, "completed")

