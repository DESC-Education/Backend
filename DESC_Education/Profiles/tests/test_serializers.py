import random
import uuid

import rest_framework.generics
from django.urls import reverse
import json
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APITestCase
from Users.models import (
    CustomUser
)
from tempfile import NamedTemporaryFile
from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    University,
    ProfileVerifyRequest,
    File,
    Skill,
    City,
    Faculty,
    Specialty,
    PhoneVerificationCode
)
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from Profiles.serializers import (
    CreateCompanyProfileSerializer,
    StudentProfileSerializer,
    UniversitySerializer,
    SkillSerializer,
    FacultySerializer,
    SpecialtySerializer,
    GetStudentProfileSerializer,
    GetCompanyProfileSerializer,
    CitySerializer
)

from Tasks.models import (
    Task,
    Solution,
    TaskCategory,
    FilterCategory,
    Filter,
)




class GetStudentProfileSerializerTest(TestCase):

    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile(f"test_{random.randint(1, 25)}.jpg", bts.getvalue())

    @staticmethod
    def get_skils_ids():
        skills_ids = []

        skills = Skill.objects.all()[:3]

        for i in skills:
            skills_ids.append(i.id)

        return skills_ids, SkillSerializer(skills, many=True).data

    def setUp(self):
        self.maxDiff = None
        self.student = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        user_profile: StudentProfile = StudentProfile.objects.get(user=self.student)
        user_profile.phone = '+77777777777'
        user_profile.verification = StudentProfile.VERIFIED
        user_profile.save()

        self.company = CustomUser.objects.create_user(
            email='exampl2e@example.com',
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
        self.task_2 = Task.objects.create(
            user=self.company,
            title="Test Task2",
            description="Test Task Description2",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.first(),
        )
        self.task_2.filters.set([Filter.objects.first()])

        self.task_3 = Task.objects.create(
            user=self.company,
            title="Test Task3",
            description="Test Task Description2",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            category=TaskCategory.objects.get(id="848254a3-bad2-4e0c-be20-bedce1700301"),
        )
        self.task_3.filters.set([Filter.objects.first()])

        self.solution = Solution.objects.create(
            task=self.task_1,
            user=self.student,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            description="Test Solution Description",
            status=Solution.COMPLETED,
        )

        self.solution = Solution.objects.create(
            task=self.task_2,
            user=self.student,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            description="Test Solution Description",
            status=Solution.COMPLETED,
        )

        self.solution = Solution.objects.create(
            task=self.task_3,
            user=self.student,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
            description="Test Solution Description",
            status=Solution.COMPLETED,
        )
    def test_serialize(self):
        serializer = GetStudentProfileSerializer(instance=self.student.get_profile()).data

        # print(serializer.data)

