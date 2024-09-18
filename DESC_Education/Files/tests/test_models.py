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
from Users.models import (
    CustomUser
)
from Tasks.models import (
    Task,
    TaskCategory,
    Solution
)




class ProfileModelTest(TestCase):

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




    def test_file_create_verification_student(self):
        file: File = File.objects.create(
            content_object=self.student_profile,
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            type=File.VERIFICATION_FILE
        )

        self.assertEqual(file.file.url, f'/api/media/users/{self.student.id}/verification_files/test.jpg')

    def test_file_create_verification_company(self):
        file = File.objects.create(
            content_object=self.company_profile,
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            type=File.VERIFICATION_FILE
        )

        self.assertEqual(file.file.url, f'/api/media/users/{self.company.id}/verification_files/test.jpg')


    def test_file_create_task_files_company(self):
        file = File.objects.create(
            content_object=self.task,
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            type=File.TASK_FILE
        )

        self.assertEqual(file.file.url, f'/api/media/users/{self.company.id}/tasks/{self.task.id}/test.jpg')

    def test_file_create_solution_files_student(self):
        file = File.objects.create(
            content_object=self.solution,
            file=SimpleUploadedFile(name="test.jpg", content=b"file_content", content_type="image/jpeg"),
            type=File.SOLUTION_FILE
        )

        self.assertEqual(file.file.url, f'/api/media/users/{self.student.id}/solutions/{self.solution.id}/test.jpg')







