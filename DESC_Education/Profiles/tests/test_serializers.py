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
from Files.models import File


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
            category=TaskCategory.objects.first(),
        )
        self.task_1.filters.set([Filter.objects.first()])
        file = File.objects.create(
            file=self.create_test_image(),
            type=File.TASK_FILE,
            content_object=self.task_1
        )
        self.task_1.files.add(file)
        self.task_2 = Task.objects.create(
            user=self.company,
            title="Test Task2",
            description="Test Task Description2",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            category=TaskCategory.objects.first(),
        )
        self.task_2.filters.set([Filter.objects.first()])
        file = File.objects.create(
            file=self.create_test_image(),
            type=File.TASK_FILE,
            content_object=self.task_2
        )
        self.task_2.files.add(file)

        self.task_3 = Task.objects.create(
            user=self.company,
            title="Test Task3",
            description="Test Task Description2",
            deadline=(timezone.now() + timezone.timedelta(days=1)).isoformat(),
            category=TaskCategory.objects.first(),
        )
        self.task_3.filters.set([Filter.objects.first()])
        file = File.objects.create(
            file=self.create_test_image(),
            type=File.TASK_FILE,
            content_object=self.task_3
        )
        self.task_3.files.add(file)

        self.solution = Solution.objects.create(
            task=self.task_1,
            user=self.student,
            description="Test Solution Description",
            status=Solution.COMPLETED,
        )
        file = File.objects.create(
            content_object=self.solution,
            type=File.SOLUTION_FILE,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
        )

        self.solution = Solution.objects.create(
            task=self.task_2,
            user=self.student,
            description="Test Solution Description",
            status=Solution.COMPLETED,
        )
        file = File.objects.create(
            content_object=self.solution,
            type=File.SOLUTION_FILE,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
        )

        self.solution = Solution.objects.create(
            task=self.task_3,
            user=self.student,
            description="Test Solution Description",
            status=Solution.COMPLETED,
        )
        file = File.objects.create(
            content_object=self.solution,
            type=File.SOLUTION_FILE,
            file=SimpleUploadedFile(name="solution.txt", content=b"solution_content", content_type="text/plain"),
        )

    def test_serialize_leadTaskCategories(self):
        serializer = GetStudentProfileSerializer(instance=self.student.get_profile()).data
        cat = TaskCategory.objects.first()
        self.assertEqual(serializer.get('leadTaskCategories'),
                         [{'id': str(cat.id), 'name': cat.name, 'percent': 1.0}])

    def test_company_serialize_leadTaskCategories(self):
        serializer = GetCompanyProfileSerializer(instance=self.company.get_profile()).data
        cat = TaskCategory.objects.first()
        self.assertEqual(serializer.get('leadTaskCategories'),
                         [{'id': str(cat.id), 'name': cat.name, 'percent': 1.0}])
