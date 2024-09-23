import random
from django.utils import timezone
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from Files.models import (
    File
)
from Profiles.models import (
    StudentProfile,
    CompanyProfile,
)
from rest_framework import serializers
from Users.models import (
    CustomUser
)
from Tasks.models import (
    Task,
    TaskCategory,
    Solution
)

from Files.serializers import (
    FileSerializer
)



class CustomFileSerializerTest(TestCase):

    def setUp(self):
        self.company = CustomUser.objects.create_user(
            email='example2@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        self.company_profile = self.company.get_profile()
        self.company_profile.verification = StudentProfile.VERIFIED
        self.company_profile.save()

        self.task = Task.objects.create(
            user=self.company,
            title="Test Task",
            description="Test Description",
            deadline=timezone.now(),
            category=TaskCategory.objects.first(),
        )

        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.student_profile = self.student.get_profile()
        self.student_profile.verification = StudentProfile.VERIFIED
        self.student_profile.save()

        self.solution = Solution.objects.create(
            user=self.student,
            task=self.task,
            description="Test Solution",
        )

    def test_file_create_verification_student_ok(self):
        serializer = FileSerializer(data={
            'file': SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(content_object=self.student_profile, type=File.VERIFICATION_FILE)

        self.assertEqual(dict(serializer.data), {
            'name': 'test',
            'extension': 'jpg',
            'path': f'users/{self.student.id}/verification_files/test.jpg'
        })

    def test_file_validate_available_extension(self):
        for ext in ('jpg', 'jpeg', 'png', 'pdf', 'docx'):
            serializer = FileSerializer(data={
                'file': SimpleUploadedFile(name=f"test.{ext}", content=b"file_content", content_type="image/jpeg")
            })
            serializer.is_valid()
            self.assertTrue(serializer.is_valid())



    def test_file_validate_not_available_extension(self):
        serializer_1 = FileSerializer(data={
            'file': SimpleUploadedFile(name="test.txt", content=b"file_content", content_type="image/jpeg")
        })

        self.assertFalse(serializer_1.is_valid())

    def test_file_validate_not_available_size(self):
        data = b'file_content' * 1024 * 500
        serializer = FileSerializer(data={
            'file': SimpleUploadedFile(name="test.docx", content=data, content_type="image/jpeg"),
        })

        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors.get('file')[0]), 'Размер файла не должен превышать 5 МБ.')


