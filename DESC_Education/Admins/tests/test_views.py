import random
import uuid
import rest_framework.generics
from django.urls import reverse
import json
from django.utils import timezone
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from Tasks.models import Task, Solution, TaskCategory
from Chats.models import Chat, ChatMembers, Message
from Profiles.models import (
    ProfileVerifyRequest,
    StudentProfile,
    CompanyProfile
)
from Files.models import (
    File
)
from Admins.serializers import (
    ProfileVerifyRequestsListSerializer,
    ProfileVerifyRequestDetailSerializer,
    CustomUserDetailSerializer
)

from Users.models import (
    CustomUser
)


class AdminProfileVerifyRequestsViewTest(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.ADMIN_ROLE,
            is_verified=True
        )
        self.admin_token = self.admin.get_token()['accessToken']

        self.student = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )

        self.v_request = ProfileVerifyRequest.objects.create(
            profile=self.student.get_profile()
        )

    def test_get_list(self):
        res = self.client.get(reverse('admin_v_request_list'),
                              headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(len(res.data.get('results')), 1)
        self.assertEqual(dict(res.data).get('results')[0],
                         ProfileVerifyRequestsListSerializer(instance=self.v_request).data)
        self.assertEqual(res.status_code, 200)


class AdminProfileVerifyRequestDetailViewTest(APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.admin = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.ADMIN_ROLE,
            is_verified=True
        )
        self.admin_token = self.admin.get_token()['accessToken']

        self.student = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )

        file = File.objects.create(
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            content_object=self.student.get_profile(),
            type=File.VERIFICATION_FILE
        )
        profile = self.student.get_profile()
        profile.reply_reload_date = timezone.now() + timezone.timedelta(minutes=10)
        profile.save()

        self.v_request = ProfileVerifyRequest.objects.create(
            profile=self.student.get_profile()
        )

    def test_get_detail(self):
        res = self.client.get(reverse('admin_v_request_detail', kwargs={'pk': str(self.v_request.id)}),
                              headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(dict(res.data),
                         dict(ProfileVerifyRequestDetailSerializer(instance=self.v_request).data))
        self.assertEqual(res.status_code, 200)

    def test_post_v_request_detail_error(self):
        res = self.client.post(reverse('admin_v_request_detail', kwargs={'pk': str(self.v_request.id)}),
                               data=json.dumps({"status": ProfileVerifyRequest.REJECTED,
                                                }),
                               content_type="application/json",
                               headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(dict(res.data).get('comment')[0], 'Требуется указать причину отказа!')

    def test_post_v_request_detail_approve(self):
        res = self.client.post(reverse('admin_v_request_detail', kwargs={'pk': str(self.v_request.id)}),
                               data=json.dumps({"status": ProfileVerifyRequest.APPROVED,
                                                }),
                               content_type="application/json",
                               headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(dict(res.data).get('status'), ProfileVerifyRequest.APPROVED)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('admin'), self.admin.id)

    def test_post_v_request_detail_rejected(self):
        res = self.client.post(reverse('admin_v_request_detail', kwargs={'pk': str(self.v_request.id)}),
                               data=json.dumps({"status": ProfileVerifyRequest.REJECTED,
                                                "comment": "Причина"
                                                }),
                               content_type="application/json",
                               headers={"Authorization": f"Bearer {self.admin_token}"})
        data = dict(res.data)
        self.assertEqual(data.get('status'), ProfileVerifyRequest.REJECTED)
        self.assertEqual(data.get('comment'), 'Причина')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data.get('admin'), self.admin.id)


class AdminCustomUserListViewTest(APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.admin = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.ADMIN_ROLE,
            is_verified=True,
        )
        self.admin_token = self.admin.get_token()['accessToken']

        self.student = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )

        self.company = CustomUser.objects.create_user(
            email="example22@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )

    def test_get_without_filters(self):
        res = self.client.get(reverse('admin_user_list'),
                              headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(len(res.data.get('results')), 2)
        self.assertEqual(res.status_code, 200)


class AdminCustomUserDetailViewTest(APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.admin = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.ADMIN_ROLE,
            is_verified=True,
        )
        self.admin_token = self.admin.get_token()['accessToken']

        self.student = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )

        self.company = CustomUser.objects.create_user(
            email="example22@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )

    def test_get_detail(self):
        res = self.client.get(reverse('admin_user_detail', args=(str(self.student.id),)),
                              headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(dict(res.data), dict(CustomUserDetailSerializer(instance=self.student).data))
        self.assertEqual(res.status_code, 200)


class StatisticsUserViewTest(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.student = CustomUser.objects.create_user(
            email="example1@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.company = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        self.company = CustomUser.objects.create_user(
            email="example3@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True,
        )
        self.company.created_at = (timezone.now() - timezone.timedelta(days=2))
        self.company.save()

    def test_stats_users_200(self):
        res = self.client.post(reverse('stats_users'))  # {'toDate': timezone.now().date(),
        # 'fromDate': (timezone.now().date() - timezone.timedelta(days=200))})

        self.assertEqual(len(res.data), 7)
        self.assertEqual(res.data[-1],
                         {'companies': 1, 'date': timezone.now().date().strftime('%Y-%m-%d'), 'students': 2})
        self.assertEqual(res.status_code, 200)

    def test_stats_users_fromDate_toDate_200(self):
        date_now = timezone.now().date()
        res = self.client.post(reverse('stats_users'), {'toDate': date_now,
                                                        'fromDate': (date_now - timezone.timedelta(days=2))})

        self.assertEqual(len(res.data), 3)
        self.assertEqual(res.data[0], {'companies': 1,
                                       'date': (date_now - timezone.timedelta(days=2)).strftime('%Y-%m-%d'),
                                       'students': 0})
        self.assertEqual(res.status_code, 200)


class StatisticsTasksViewTest(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.student = CustomUser.objects.create_user(
            email="example1@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.company = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        self.company = CustomUser.objects.create_user(
            email="example3@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True,
        )
        self.company.created_at = (timezone.now() - timezone.timedelta(days=2))
        self.company.save()

        self.task = Task.objects.create(
            user=self.company,
            title='Test task',
            description='Test task description',
            deadline=timezone.now() + timezone.timedelta(days=5),
            category=TaskCategory.objects.first()
        )

        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task
        )
        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task
        )
        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task,
            status=Solution.COMPLETED
        )
        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task,
            status=Solution.FAILED
        )

    def test_stats_tasks_200(self):
        res = self.client.post(reverse('stats_tasks'))  # {'toDate': timezone.now().date(),
        # 'fromDate': (timezone.now().date() - timezone.timedelta(days=200))})

        self.assertEqual(len(res.data), 7)
        self.assertEqual(res.data[-1],
                         {'date': timezone.now().date().strftime('%Y-%m-%d'),
                          'created': 1, 'completed': 1, 'pending': 2, 'failed': 1})
        self.assertEqual(res.status_code, 200)


class AdminUserChatsTest(APITestCase):
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

        self.student2 = CustomUser.objects.create_user(
            email='example222@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True)
        profile = self.student2.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.company = CustomUser.objects.create_user(
            email='example123@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student2)
        ChatMembers.objects.create(chat=self.chat, user=self.company)

        self.chat = Chat.objects.create()
        ChatMembers.objects.create(chat=self.chat, user=self.student)
        ChatMembers.objects.create(chat=self.chat, user=self.company)
        Message.objects.create(chat=self.chat, user=self.student, message='Первое')
        Message.objects.create(chat=self.chat, user=self.company, message='Первое')
        Message.objects.create(chat=self.chat, user=self.company, message='Первое')
        Message.objects.create(chat=self.chat, user=self.company, message='Первое')
        Message.objects.create(chat=self.chat, user=self.company, message='Первое')
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

    def test_get_chats_200(self):
        res = self.client.get(reverse('admin_user_chats', args=(str(self.student.id),)))

        self.assertEqual(dict(res.data.get('results')[0]),
                         {'companion':
                              {'id': str(self.company2.id), 'name': '', 'avatar': None},
                          'id': str(self.chat2.id),
                          'isFavorite': False,
                          'lastMessage': {'id': str(self.mes2.id),
                                          'message': 'Последнее второе',
                                          'user': {'id': str(self.student.id), 'name': ' ',
                                                   'avatar': None}, 'createdAt': self.mes2.created_at.isoformat(),
                                          'isRead': False, 'files': []},
                          'task': None,
                          'unreadCount': 0}
                         )
        self.assertEqual(res.status_code, 200)


class AdminCompanyTasksListViewTest(APITestCase):

    def setUp(self):
        self.maxDiff = None
        self.student = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.student = CustomUser.objects.create_user(
            email="example1@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.company = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        self.company = CustomUser.objects.create_user(
            email="example3@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True,
        )
        self.company.created_at = (timezone.now() - timezone.timedelta(days=2))
        self.company.save()

        self.task = Task.objects.create(
            user=self.company,
            title='Test task',
            description='Test task description',
            deadline=timezone.now() + timezone.timedelta(days=5),
            category=TaskCategory.objects.first()
        )
        self.task = Task.objects.create(
            user=self.company,
            title='Test task',
            description='Test task description',
            deadline=timezone.now() + timezone.timedelta(days=5),
            category=TaskCategory.objects.first()
        )

        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task
        )
        self.solution1 = Solution.objects.create(
            user=self.student,
            task=self.task
        )
        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task,
            status=Solution.COMPLETED
        )
        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task,
            status=Solution.FAILED
        )

    def test_get_company_200(self):
        res = self.client.get(reverse('admin_company_tasks', args=(str(self.company.id),)))

        self.assertEqual(dict(res.data.get('results')[0]), {
            'id': str(self.task.id),
            'title': 'Test task', 'user': self.company.id,
            'description': 'Test task description', 'deadline': self.task.deadline.isoformat(),
            'createdAt': self.task.created_at.isoformat(),
            'profile': {'companyName': '', 'logoImg': None, 'id': str(self.company.id)},
            'category': TaskCategory.objects.first().id}
                         )
        self.assertEqual(res.status_code, 200)

    def test_get_students_200(self):
        res = self.client.get(reverse('admin_student_solutions', args=(str(self.student.id),)))

        self.assertEqual(dict(res.data.get('results')[0]),
                         {'companyComment': None,
                          'createdAt': self.solution1.created_at.isoformat(),
                          'description': None,
                          'files': [],
                          'id': str(self.solution1.id),
                          'review': None,
                          'status': 'pending',
                          'studentProfile': {'firstName': '', 'lastName': '', 'logoImg': None},
                          'task': str(self.task.id),
                          'user': self.student.id}

                         )
        self.assertEqual(res.status_code, 200)
