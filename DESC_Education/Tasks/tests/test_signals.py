import random

import rest_framework.generics
from django.urls import reverse
import json
from django.utils import timezone
from django.test import TestCase
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
    Filter,
    Solution
)
from Profiles.models import (
    StudentProfile
)


class check_student_profile_levelTest(TestCase):
    def setUp(self):
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

        self.company = CustomUser.objects.create_user(
            email='exampl2e@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

    def create_tasks(self, company, user, count):
        for _ in range(count):
            task = Task.objects.create(
                user=company,
                title=f"Test Task {random.randint(1, 100)}",
                description=f"Test Task Description {random.randint(1, 100)}",
                deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
                file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
                category=TaskCategory.objects.first(),
            )

            solution = Solution.objects.create(
                user=user,
                task=task,
                description=f"Test Solution Description {random.randint(1, 100)}",
                file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            )

            solution.status = Solution.COMPLETED
            solution.save()

    def test_signal(self):

        profile = self.student.get_profile()

        self.assertEqual(profile.level_id, 1)

        self.create_tasks(self.company, self.student, 15)

        self.assertEqual(profile.level_id, 2)

        self.create_tasks(self.company, self.student, 15)

        self.assertEqual(profile.level_id, 3)


