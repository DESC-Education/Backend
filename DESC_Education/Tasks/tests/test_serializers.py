import random
import uuid
import rest_framework.generics
from django.urls import reverse
import json
from django.utils import timezone
from django.test import TestCase
from Tasks.models import (Task, TaskCategory, Solution, Filter, FilterCategory)
from Files.models import File
from django.core.files.uploadedfile import SimpleUploadedFile
from Tasks.serializers import SolutionSerializer
from Users.models import CustomUser
from Profiles.models import StudentProfile


class SolutionSerializerTest(TestCase):
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

        self.company = CustomUser.objects.create_user(
            email='exampl2e@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        profile = self.company.get_profile()
        profile.verification = StudentProfile.VERIFIED
        profile.save()

        self.task = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Task Description",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            category=TaskCategory.objects.first(),
        )
        self.task.filters.set([Filter.objects.first()])
        file = File.objects.create(
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            type=File.TASK_FILE,
            content_object=self.task
        )

        self.solution = Solution.objects.create(
            task=self.task,
            user=self.student,
            status=Solution.COMPLETED,
        )
        self.file = File.objects.create(
            content_object=self.solution,
            type=File.SOLUTION_FILE,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
        )

    def test_serialize(self):
        serializer = SolutionSerializer(instance=self.solution)
        self.assertEqual(dict(serializer.data),
                         {'id': str(self.solution.id),
                          'user': self.student.id,
                          'description': None,
                          'files': [
                              {'id': str(self.file.id),
                               'size': 16, 'name': 'solution',
                               'extension': 'txt',
                               'path': f'/api/media/users/{str(self.student.id)}/solutions/{self.solution.id}/solution.txt'
                               }],
                          'userProfile': {'firstName': '',
                                          'lastName': '',
                                          'logoImg': None},
                          'companyComment': None,
                          'status': 'completed',
                          'createdAt': self.solution.created_at.isoformat()})

