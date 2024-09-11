import random
import uuid
import rest_framework.generics
from django.urls import reverse
import json
from django.utils import timezone
from rest_framework.test import APITestCase
from Profiles.models import (
    ProfileVerifyRequest
)
from Admins.serializers import ProfileVerifyRequestsListSerializer
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
        res = self.client.get(reverse('v_request_list'),
                              headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(len(res.data.get('results')), 1)
        self.assertEqual(dict(res.data).get('results')[0],
                         ProfileVerifyRequestsListSerializer(instance=self.v_request).data)
        self.assertEqual(res.status_code, 200)



