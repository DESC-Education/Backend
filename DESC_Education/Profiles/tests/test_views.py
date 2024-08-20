from django.urls import reverse
import json
from django.utils import timezone
from rest_framework.test import APITestCase
from Users.models import (
    CustomUser
)
from tempfile import NamedTemporaryFile
from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    University,
    ProfileVerifyRequest
)
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile




class CreateProfileViewTest(APITestCase):

    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile("test.jpg", bts.getvalue())



    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="example@example.com",
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
        self.admin = CustomUser.objects.create_user(
            email="example3@example.com",
            password="test123",
            role=CustomUser.ADMIN_ROLE,
            is_verified=True
        )
        self.admin_token = self.admin.get_token()['accessToken']
        self.token = self.user.get_token()['accessToken']
        self.company_token = self.company.get_token()['accessToken']
        university = University.objects.first()
        self.student_example_data = {
            "firstName": "John",
            "lastName": "Doe",
            "description": "Student description",
            "phoneVisibility": True,
            "emailVisibility": True,
            "telegramLink": "https://t.me/john_doe",
            "vkLink": "https://vk.com/john_doe",
            "timezone": 3,
            "formOfEducation": StudentProfile.FULL_TIME_EDUCATION,
            "speciality": "it",
            "admissionYear": 2020,
            "university": str(university.id),
            "studentCard": self.create_test_image()
        }

        self.company_example_data = {
            "firstName": "John",
            "lastName": "Doe",
            "description": "Student description",
            "phoneVisibility": True,
            "emailVisibility": True,
            "telegramLink": "https://t.me/john_doe",
            "vkLink": "https://vk.com/john_doe",
            "timezone": 3,
            "companyName": "Test Company",
            'linkToCompany': "https://link.com/"
        }


    def test_create_student_profile_200(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.student_example_data,
                               headers={"Authorization": f"Bearer {self.token}"})

        profile = StudentProfile.objects.first()

        expected_data = self.student_example_data
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["phone"] = None
        expected_data["studentCard"] = profile.student_card.url

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content).get("data").get("studentProfile"), expected_data)

    def test_create_company_profile_200(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.company_example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"})

        profile = CompanyProfile.objects.first()

        expected_data = self.company_example_data
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["phone"] = None


        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content).get("data").get("companyProfile"), expected_data)

    def test_student_duplicate_405(self, ):
        example_data = self.student_example_data.copy()
        example_data['studentCard'] = self.create_test_image()

        self.test_create_student_profile_200()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )


        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль еще на проверке')


    def test_student_rejected_405(self, ):
        example_data = self.student_example_data.copy()
        example_data['firstName'] = "newFIrstName"
        example_data['studentCard'] = self.create_test_image()

        self.test_create_student_profile_200()
        ProfileVerifyRequest.objects.filter(object_id=StudentProfile.objects.first().id)\
            .update(status=ProfileVerifyRequest.REJECTED)

        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )

        profile = StudentProfile.objects.first()

        expected_data = example_data
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["phone"] = None
        expected_data["studentCard"] = profile.student_card.url


        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('message'), 'Профиль создан и отправлен на проверку!')
        self.assertEqual(json.loads(res.content).get("data").get("studentProfile"), expected_data)





    def test_company_not_verified_405(self, ):
        example_data = self.company_example_data.copy()

        self.test_create_company_profile_200()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               )


        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль еще на проверке')

    def test_company_verified_405(self, ):
        example_data = self.company_example_data.copy()
        self.test_create_company_profile_200()
        profile = CompanyProfile.objects.first()
        profile.is_verified = True
        profile.save()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               )


        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль уже подтвержден')

    def test_create_admin_profile_200(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.student_example_data,
                               headers={"Authorization": f"Bearer {self.admin_token}"})



        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data.get('message'), 'Вы можете создать профиль только для студента или компании!')

