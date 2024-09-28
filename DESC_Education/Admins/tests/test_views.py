import random
import uuid
import rest_framework.generics
from django.urls import reverse
import json
from django.utils import timezone
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from Profiles.models import (
    ProfileVerifyRequest,
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
